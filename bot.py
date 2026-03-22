# -*- coding: utf-8 -*-
"""
Telegram project board + voting bot (pyTelegramBotAPI / telebot).

Set BOT_TOKEN in the environment or in a .env file next to this script.
"""
from __future__ import annotations

import json
import os
import threading
from html import escape
from pathlib import Path

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

import tenders as tenders_store

from i18n import (
    DEFAULT_LOCALE,
    LOCALES,
    LOCALE_DISPLAY,
    normalize_locale,
    t,
    vote_panel_footer_html,
    vote_panel_footer_max_len,
)

DATA_FILE = Path(__file__).resolve().parent / "projects_data.json"
_ENV_FILE = Path(__file__).resolve().parent / ".env"
CONFIG_FILE = Path(__file__).resolve().parent / "config.json"
_lock = threading.Lock()

# 群内机器人消息在发送后多久删除（秒）；需管理员「删除消息」权限
GROUP_MESSAGE_TTL_SEC = 300


def _load_env_file() -> None:
    if not _ENV_FILE.is_file():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _load_data() -> dict:
    if not DATA_FILE.is_file():
        return {"next_id": 1, "projects": [], "user_lang": {}}
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if "next_id" not in raw or "projects" not in raw:
            return {"next_id": 1, "projects": [], "user_lang": {}}
        raw.setdefault("user_lang", {})
        _sync_next_id(raw)
        return raw
    except (json.JSONDecodeError, OSError):
        return {"next_id": 1, "projects": [], "user_lang": {}}


def _sync_next_id(data: dict) -> None:
    """Ensure next_id > max(existing ids). Never lower next_id — ids are not reused after delete."""
    projects = data.get("projects") or []
    ids: list[int] = []
    for p in projects:
        try:
            ids.append(int(p["id"]))
        except (TypeError, ValueError, KeyError):
            continue
    hi = max(ids) if ids else 0
    try:
        n = int(data["next_id"])
    except (TypeError, ValueError, KeyError):
        n = 1
    # Monotonic: never assign a next_id below what we already committed to.
    data["next_id"] = max(n, hi + 1)


def _project_index_by_id(data: dict, pid: int) -> int | None:
    for i, x in enumerate(data.get("projects") or []):
        try:
            if int(x["id"]) == pid:
                return i
        except (TypeError, ValueError, KeyError):
            continue
    return None


def _author_id_of(p: dict) -> int | None:
    try:
        v = p.get("author_id")
        if v is None:
            return None
        return int(v)
    except (TypeError, ValueError):
        return None


def _is_publisher(p: dict, user_id: int) -> bool:
    aid = _author_id_of(p)
    return aid is not None and aid == user_id


def _load_admin_ids() -> frozenset[int]:
    """从 config.json 读取管理员 Telegram 数字 ID；文件缺失或格式错误则视为无管理员。"""
    if not CONFIG_FILE.is_file():
        return frozenset()
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return frozenset()
    ids = raw.get("admin_ids")
    if not isinstance(ids, list):
        return frozenset()
    out: set[int] = set()
    for x in ids:
        try:
            out.add(int(x))
        except (TypeError, ValueError):
            continue
    return frozenset(out)


def _can_moderate_project(
    p: dict, user_id: int, admin_ids: frozenset[int]
) -> bool:
    """发布者或 config 中的管理员可编辑/删除该项目。"""
    return _is_publisher(p, user_id) or user_id in admin_ids


def _save_data(data: dict) -> None:
    _sync_next_id(data)
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_project(p: dict) -> dict:
    p = dict(p)
    p.setdefault("up", [])
    p.setdefault("down", [])
    p.setdefault("author_username", None)
    p.setdefault("budget", "")
    p["up"] = [int(x) for x in p["up"]]
    p["down"] = [int(x) for x in p["down"]]
    return p


def _parse_desc_and_budget(body: str) -> tuple[str, str]:
    """第一段为描述；第一个 | 后为预算（可空）。无 | 则预算为空字符串。"""
    body = body.strip()
    if "|" not in body:
        return body, ""
    desc, _, rest = body.partition("|")
    return desc.strip(), rest.strip()


def _parse_edit_payload(s: str) -> tuple[str, str | None]:
    """有 | 时：(描述, 预算或空)；无 | 时：(整段描述, None 表示不改预算)。"""
    s = s.strip()
    if "|" not in s:
        return s, None
    desc, _, rest = s.partition("|")
    return desc.strip(), rest.strip()


def _user_lang(data: dict, user_id: int) -> str:
    v = (data.get("user_lang") or {}).get(str(user_id))
    return v if v in LOCALES else DEFAULT_LOCALE


def _publisher_display_html(p: dict, locale: str) -> str:
    """Publisher line: display name plus <code>@username</code> when available."""
    name = (p.get("author_name") or "").strip() or t(locale, "anonymous")
    raw_u = p.get("author_username")
    un = str(raw_u).strip().lstrip("@") if raw_u else ""
    safe_name = escape(name)
    if not un:
        return safe_name
    return f"{safe_name} <code>@{escape(un)}</code>"


def _get_projects(data: dict) -> list[dict]:
    items = [_normalize_project(p) for p in data.get("projects", [])]
    items.sort(key=lambda p: int(p["id"]))
    return items


# Telegram 单条消息 HTML 上限 4096
_MAX_VOTE_PANEL_MSG = 4096


def _budget_line_html(p: dict, locale: str) -> str:
    b = (p.get("budget") or "").strip()
    bud_l = t(locale, "budget_label")
    if b:
        return f"💰 <b>{bud_l}:</b> {escape(b)}\n"
    return f"💰 <b>{bud_l}:</b> {t(locale, 'budget_not_set')}\n"


def _project_block_html(p: dict, locale: str) -> str:
    pid = int(p["id"])
    text = (p.get("text") or "").strip() or t(locale, "no_description")
    if len(text) > 400:
        text = text[:397] + "..."
    up_n = len(p["up"])
    down_n = len(p["down"])
    pub = _publisher_display_html(p, locale)
    safe_body = escape(text)
    pub_l = t(locale, "publisher")
    up_l = t(locale, "upvotes")
    dn_l = t(locale, "downvotes")
    return (
        f"<b>#{pid}</b>\n{safe_body}\n"
        f"{_budget_line_html(p, locale)}"
        f"👤 <b>{pub_l}:</b> {pub}\n"
        f"{up_l}: <b>{up_n}</b> · {dn_l}: <b>{down_n}</b>\n"
        f"— — —\n"
    )


def _markup_for_projects(group: list[dict], locale: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for p in group:
        pid = int(p["id"])
        up_n = len(p["up"])
        down_n = len(p["down"])
        markup.row(
            types.InlineKeyboardButton(
                t(locale, "btn_up", n=up_n), callback_data=f"v:{pid}:u"
            ),
            types.InlineKeyboardButton(
                t(locale, "btn_down", n=down_n), callback_data=f"v:{pid}:d"
            ),
        )
    return markup


def _shrink_project_description(p: dict, max_chars: int, locale: str) -> dict:
    """返回副本，描述截断到至多 max_chars（用于单条过长时塞进一条消息）。"""
    out = dict(p)
    raw = (out.get("text") or "").strip() or t(locale, "no_description")
    if len(raw) > max_chars:
        out["text"] = raw[: max(1, max_chars - 3)] + "..."
    return out


def _split_projects_html_batches(projects: list[dict], locale: str) -> list[list[dict]]:
    """按消息长度上限拆成多批项目（header + 各项目块，不含页脚）。"""
    if not projects:
        return []
    header_first = t(locale, "projects_title")
    header_cont = t(locale, "projects_continued")
    reserve = vote_panel_footer_max_len()
    max_body = _MAX_VOTE_PANEL_MSG - reserve

    batches: list[list[dict]] = []
    cur: list[dict] = []
    batch_hdr = ""

    for p in projects:
        p_work = dict(p)
        while True:
            block = _project_block_html(p_work, locale)
            if not cur:
                batch_hdr = header_first if not batches else header_cont
            trial = batch_hdr + "".join(
                _project_block_html(x, locale) for x in cur
            ) + block

            if len(trial) <= max_body:
                cur.append(p_work)
                break

            if cur:
                batches.append(cur)
                cur = []
                continue

            raw_t = (p_work.get("text") or "").strip() or t(locale, "no_description")
            if len(raw_t) > 15:
                p_work = _shrink_project_description(
                    p_work, max(15, len(raw_t) - 100), locale
                )
                continue

            cur.append(p_work)
            break

    if cur:
        batches.append(cur)
    return batches


def _format_vote_panel_batches(
    data: dict, locale: str
) -> list[tuple[str, types.InlineKeyboardMarkup]]:
    """仅当单条超过 Telegram 长度上限时才拆成多批；否则一条发完。每批末尾都有 /vote 说明；多批时带 Part n/m。"""
    projects = _get_projects(data)
    if not projects:
        empty = t(locale, "projects_empty")
        return [(empty, types.InlineKeyboardMarkup())]

    header_first = t(locale, "projects_title")
    body_all = header_first + "".join(
        _project_block_html(p, locale) for p in projects
    )
    footer_single = vote_panel_footer_html(locale, 1, 1)
    one_msg = body_all.rstrip() + footer_single
    if len(one_msg) <= _MAX_VOTE_PANEL_MSG:
        return [(one_msg, _markup_for_projects(projects, locale))]

    groups = _split_projects_html_batches(projects, locale)
    n = len(groups)
    header_cont = t(locale, "projects_continued")
    out: list[tuple[str, types.InlineKeyboardMarkup]] = []
    for i, group in enumerate(groups):
        head = header_first if i == 0 else header_cont
        body = head + "".join(_project_block_html(p, locale) for p in group)
        footer = vote_panel_footer_html(locale, i + 1, n)
        text = body.rstrip() + footer
        out.append((text, _markup_for_projects(group, locale)))
    return out


def _format_vote_panel(
    data: dict, locale: str
) -> tuple[str, types.InlineKeyboardMarkup]:
    """单条消息用的总览（用于内联回调刷新）；多批时仅返回第一批并提示 /projects。"""
    batches = _format_vote_panel_batches(data, locale)
    text, markup = batches[0]
    if len(batches) > 1:
        note = t(locale, "vote_panel_more", n=len(batches))
        if len(text) + len(note) <= _MAX_VOTE_PANEL_MSG:
            text = text.rstrip() + note
        else:
            text = text.rstrip() + t(locale, "vote_panel_more_short")
            if len(text) > _MAX_VOTE_PANEL_MSG:
                text = text[: _MAX_VOTE_PANEL_MSG - 1] + "…"
    return text, markup


def _format_single_project_vote_panel(
    data: dict, pid: int, locale: str
) -> tuple[str, types.InlineKeyboardMarkup] | None:
    """One project with counts + upvote/downvote row. None if id missing."""
    p = None
    for x in data["projects"]:
        if int(x["id"]) == pid:
            p = _normalize_project(x)
            break
    if not p:
        return None

    text = (p.get("text") or "").strip() or t(locale, "no_description")
    if len(text) > 800:
        text = text[:797] + "..."
    up_n = len(p["up"])
    down_n = len(p["down"])
    pub = _publisher_display_html(p, locale)
    safe_body = escape(text)
    pub_l = t(locale, "publisher")
    up_l = t(locale, "upvotes")
    dn_l = t(locale, "downvotes")
    body = (
        t(locale, "single_vote_title", pid=pid)
        + f"<b>#{pid}</b>\n{safe_body}\n"
        f"{_budget_line_html(p, locale)}"
        f"👤 <b>{pub_l}:</b> {pub}\n"
        f"{up_l}: <b>{up_n}</b> · {dn_l}: <b>{down_n}</b>"
    )
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            t(locale, "btn_up", n=up_n), callback_data=f"vs:{pid}:u"
        ),
        types.InlineKeyboardButton(
            t(locale, "btn_down", n=down_n), callback_data=f"vs:{pid}:d"
        ),
    )
    return body, markup


def _apply_vote(
    data: dict, pid: int, user_id: int, choice: str, locale: str
) -> str:
    """choice: 'u' (upvote) or 'd' (downvote). Returns a short toast for the user."""
    p = None
    for x in data["projects"]:
        if int(x["id"]) == pid:
            p = _normalize_project(x)
            break
    if not p:
        return t(locale, "hint_no_project")

    ups = set(p["up"])
    downs = set(p["down"])
    if choice == "u":
        if user_id in downs:
            downs.discard(user_id)
        if user_id in ups:
            ups.discard(user_id)
            hint = t(locale, "hint_up_off")
        else:
            ups.add(user_id)
            hint = t(locale, "hint_up_on")
    else:
        if user_id in ups:
            ups.discard(user_id)
        if user_id in downs:
            downs.discard(user_id)
            hint = t(locale, "hint_down_off")
        else:
            downs.add(user_id)
            hint = t(locale, "hint_down_on")

    p["up"] = list(ups)
    p["down"] = list(downs)
    for i, x in enumerate(data["projects"]):
        if int(x["id"]) == pid:
            data["projects"][i] = {
                "id": p["id"],
                "text": p.get("text", ""),
                "budget": (p.get("budget") or "").strip(),
                "author_id": p.get("author_id"),
                "author_name": p.get("author_name", ""),
                "author_username": p.get("author_username"),
                "up": p["up"],
                "down": p["down"],
            }
            break
    return hint


def _apply_bid_vote(
    td: dict, bid_id: int, user_id: int, choice: str, locale: str
) -> str:
    """单条投标 👍/👎，规则与项目投票相同。"""
    tenders_store._ensure_bid_votes_inplace(td)
    b = tenders_store.bid_ref_by_id(td, bid_id)
    if not b:
        return t(locale, "callback_invalid")

    ups = set(b["up"])
    downs = set(b["down"])
    if choice == "u":
        if user_id in downs:
            downs.discard(user_id)
        if user_id in ups:
            ups.discard(user_id)
            hint = t(locale, "hint_up_off")
        else:
            ups.add(user_id)
            hint = t(locale, "hint_up_on")
    else:
        if user_id in ups:
            ups.discard(user_id)
        if user_id in downs:
            downs.discard(user_id)
            hint = t(locale, "hint_down_off")
        else:
            downs.add(user_id)
            hint = t(locale, "hint_down_on")

    b["up"] = list(ups)
    b["down"] = list(downs)
    return hint


def _parse_bid_vote_callback(data: str) -> tuple[int, int, str] | None:
    """be:{part_idx}:{bid_id}:u|d → (part_idx, bid_id, choice)。"""
    if not data.startswith("be:"):
        return None
    parts = data.split(":")
    if len(parts) != 4:
        return None
    _, part_s, bid_s, c = parts
    if c not in ("u", "d"):
        return None
    try:
        return int(part_s), int(bid_s), c
    except ValueError:
        return None


def _markup_bid_vote_rows(
    td: dict, locale: str, bid_ids: list[int], part_idx: int
) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for bid_id in bid_ids:
        b = tenders_store.bid_ref_by_id(td, bid_id)
        if not b:
            continue
        up_n = len(b.get("up") or [])
        dn_n = len(b.get("down") or [])
        markup.row(
            types.InlineKeyboardButton(
                f"#{bid_id}",
                callback_data=f"bel:{bid_id}",
            ),
            types.InlineKeyboardButton(
                t(locale, "btn_up", n=up_n),
                callback_data=f"be:{part_idx}:{bid_id}:u",
            ),
            types.InlineKeyboardButton(
                t(locale, "btn_down", n=dn_n),
                callback_data=f"be:{part_idx}:{bid_id}:d",
            ),
        )
    return markup


def main() -> None:
    _load_env_file()
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Set BOT_TOKEN in the environment or in .env (BOT_TOKEN=your_token)."
        )

    bot = telebot.TeleBot(token, parse_mode="HTML")

    _group_msg_timers: dict[tuple[int, int], threading.Timer] = {}
    _group_msg_timer_lock = threading.Lock()

    def schedule_group_message_delete(
        chat_id: int, message_id: int, chat_type: str | None
    ) -> None:
        """群组/超级群：在 GROUP_MESSAGE_TTL_SEC 后删除该条机器人消息；重复调用会重置计时。"""
        if chat_type not in ("group", "supergroup"):
            return
        key = (chat_id, message_id)

        def do_delete() -> None:
            try:
                bot.delete_message(chat_id, message_id)
            except ApiTelegramException:
                pass
            finally:
                with _group_msg_timer_lock:
                    _group_msg_timers.pop(key, None)

        with _group_msg_timer_lock:
            old = _group_msg_timers.pop(key, None)
            if old is not None:
                old.cancel()
            timer = threading.Timer(GROUP_MESSAGE_TTL_SEC, do_delete)
            timer.daemon = True
            _group_msg_timers[key] = timer
            timer.start()

    def send_chat(message: types.Message, text: str, **kwargs) -> None:
        """发到当前聊天，不引用用户那条命令（非 reply）。"""
        sent = bot.send_message(message.chat.id, text, **kwargs)
        schedule_group_message_delete(
            sent.chat.id, sent.message_id, getattr(sent.chat, "type", None)
        )

    def publisher_from_message(message: types.Message) -> tuple[int, str, str | None]:
        u = message.from_user
        if not u:
            return 0, "Anonymous", None
        uid = u.id
        name = (u.full_name or "").strip() or (u.username or str(uid))
        username = (u.username or "").strip() or None
        return uid, name, username

    @bot.message_handler(commands=["start", "help"])
    def cmd_start(message: types.Message):
        uid = message.from_user.id if message.from_user else 0
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        send_chat(message, t(lang, "help"))

    @bot.message_handler(commands=["lang"])
    def cmd_lang(message: types.Message):
        uid = message.from_user.id if message.from_user else 0
        parts = (message.text or "").split()
        with _lock:
            data = _load_data()
            cur = _user_lang(data, uid)
        if len(parts) < 2:
            send_chat(
                message,
                t(cur, "lang_usage", name=LOCALE_DISPLAY[cur]),
            )
            return
        loc = normalize_locale(parts[1])
        if not loc:
            send_chat(message, t(cur, "lang_bad"))
            return
        with _lock:
            data = _load_data()
            data.setdefault("user_lang", {})
            data["user_lang"][str(uid)] = loc
            _save_data(data)
        send_chat(
            message,
            t(loc, "lang_set", name=LOCALE_DISPLAY[loc]),
        )

    @bot.message_handler(commands=["id"])
    def cmd_id(message: types.Message):
        """私聊返回当前用户 Telegram 数字 ID（不写入 /help）。"""
        uid_op = message.from_user.id if message.from_user else 0
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid_op)
        if getattr(message.chat, "type", None) != "private":
            send_chat(message, t(lang, "id_private_only"))
            return
        u = message.from_user
        if not u:
            send_chat(
                message,
                t(lang, "id_reply", uid="—", uname=t(lang, "id_no_username")),
            )
            return
        uname = (
            f"@{escape(u.username)}" if u.username else t(lang, "id_no_username")
        )
        send_chat(message, t(lang, "id_reply", uid=u.id, uname=uname))

    @bot.message_handler(commands=["publish"])
    def cmd_publish(message: types.Message):
        uid, uname, uname_at = publisher_from_message(message)
        parts = (message.text or "").split(maxsplit=1)
        raw_body = parts[1].strip() if len(parts) > 1 else ""
        desc, budget = _parse_desc_and_budget(raw_body)
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        if not desc:
            send_chat(message, t(lang, "publish_need_desc"))
            return

        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            pid = int(data["next_id"])
            data["next_id"] = pid + 1
            data["projects"].append(
                {
                    "id": pid,
                    "text": desc,
                    "budget": budget,
                    "author_id": uid,
                    "author_name": uname,
                    "author_username": uname_at,
                    "up": [],
                    "down": [],
                }
            )
            _save_data(data)

        send_chat(message, t(lang, "publish_ok", pid=pid))

    @bot.message_handler(commands=["projects"])
    def cmd_projects(message: types.Message):
        uid = message.from_user.id if message.from_user else 0
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        batches = _format_vote_panel_batches(data, lang)
        for chunk, _ in batches:
            send_chat(message, chunk)

    @bot.message_handler(commands=["vote"])
    def cmd_vote(message: types.Message):
        uid = message.from_user.id if message.from_user else 0
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        parts = (message.text or "").split()
        if len(parts) < 2:
            send_chat(message, t(lang, "vote_need_id"))
            return
        try:
            pid = int(parts[1])
        except ValueError:
            send_chat(message, t(lang, "vote_bad_id"))
            return

        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            single = _format_single_project_vote_panel(data, pid, lang)

        if not single:
            send_chat(message, t(lang, "vote_no_such", pid=pid))
            return

        text, markup = single
        send_chat(message, text, reply_markup=markup)

    @bot.message_handler(commands=["delete"])
    def cmd_delete(message: types.Message):
        uid, _, _ = publisher_from_message(message)
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        parts = (message.text or "").split()
        if len(parts) < 2:
            send_chat(message, t(lang, "delete_usage"))
            return
        try:
            pid = int(parts[1])
        except ValueError:
            send_chat(message, t(lang, "delete_bad_id"))
            return

        err: str | None = None
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            idx = _project_index_by_id(data, pid)
            if idx is None:
                err = t(lang, "delete_no_such", pid=pid)
            else:
                p = _normalize_project(data["projects"][idx])
                admins = _load_admin_ids()
                if not _can_moderate_project(p, uid, admins):
                    err = t(lang, "delete_not_pub")
                else:
                    data["projects"].pop(idx)
                    _save_data(data)

        if err:
            send_chat(message, err)
            return

        send_chat(message, t(lang, "delete_ok", pid=pid))

    @bot.message_handler(commands=["edit"])
    def cmd_edit(message: types.Message):
        uid, pub_name, pub_username = publisher_from_message(message)
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        raw = message.text or ""
        parts = raw.split(maxsplit=2)
        if len(parts) < 3:
            send_chat(message, t(lang, "edit_usage"))
            return
        try:
            pid = int(parts[1])
        except ValueError:
            send_chat(message, t(lang, "edit_bad_id"))
            return

        new_desc, new_budget = _parse_edit_payload(parts[2])
        if not new_desc:
            send_chat(message, t(lang, "edit_empty"))
            return

        err: str | None = None
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            idx = _project_index_by_id(data, pid)
            if idx is None:
                err = t(lang, "edit_no_such", pid=pid)
            else:
                p = _normalize_project(data["projects"][idx])
                admins = _load_admin_ids()
                if not _can_moderate_project(p, uid, admins):
                    err = t(lang, "edit_not_pub")
                else:
                    p["text"] = new_desc
                    if new_budget is not None:
                        p["budget"] = new_budget
                    is_pub = _is_publisher(p, uid)
                    aname = (
                        pub_name if is_pub else (p.get("author_name") or "").strip()
                    )
                    au = pub_username if is_pub else p.get("author_username")
                    data["projects"][idx] = {
                        "id": p["id"],
                        "text": p["text"],
                        "budget": (p.get("budget") or "").strip(),
                        "author_id": p.get("author_id"),
                        "author_name": aname,
                        "author_username": au,
                        "up": p["up"],
                        "down": p["down"],
                    }
                    _save_data(data)

        if err:
            send_chat(message, err)
            return

        send_chat(message, t(lang, "edit_ok", pid=pid))

    @bot.message_handler(commands=["tender_add"])
    def cmd_tender_add(message: types.Message):
        uid, name, username = publisher_from_message(message)
        admins = _load_admin_ids()
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        if uid not in admins:
            send_chat(message, t(lang, "tender_add_need_admin"))
            return
        parts = (message.text or "").split(maxsplit=1)
        body = parts[1].strip() if len(parts) > 1 else ""
        if not body:
            send_chat(message, t(lang, "tender_add_usage"))
            return
        with _lock:
            td = tenders_store.load_tenders()
            tid = int(td["next_tender_id"])
            td["next_tender_id"] = tid + 1
            td["tenders"].append(
                {
                    "id": tid,
                    "text": body,
                    "status": "open",
                    "author_id": uid,
                    "author_name": name,
                    "author_username": username,
                }
            )
            tenders_store.save_tenders(td)
        send_chat(message, t(lang, "tender_add_ok", tid=tid))

    @bot.message_handler(commands=["tenders"])
    def cmd_tenders(message: types.Message):
        uid = message.from_user.id if message.from_user else 0
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            td = tenders_store.load_tenders()
        for chunk in tenders_store.format_tender_list_batches(td, lang):
            send_chat(message, chunk)

    @bot.message_handler(commands=["tender_view"])
    def cmd_tender_view(message: types.Message):
        uid = message.from_user.id if message.from_user else 0
        parts = (message.text or "").split()
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        if len(parts) < 2:
            send_chat(message, t(lang, "tender_view_bad_id"))
            return
        try:
            tid = int(parts[1])
        except ValueError:
            send_chat(message, t(lang, "tender_view_bad_id"))
            return
        with _lock:
            td = tenders_store.load_tenders()
        batches = tenders_store.format_tender_detail_batches(td, tid, lang)
        if not batches:
            send_chat(message, t(lang, "tender_view_not_found", tid=tid))
            return
        for chunk, bid_ids, part_idx in batches:
            mk = (
                _markup_bid_vote_rows(td, lang, bid_ids, part_idx)
                if bid_ids
                else None
            )
            send_chat(message, chunk, reply_markup=mk)

    @bot.message_handler(commands=["tender_bid"])
    def cmd_tender_bid(message: types.Message):
        uid, name, username = publisher_from_message(message)
        raw = message.text or ""
        parts = raw.split(maxsplit=2)
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        if len(parts) < 3:
            send_chat(message, t(lang, "tender_bid_usage"))
            return
        try:
            tid = int(parts[1])
        except ValueError:
            send_chat(message, t(lang, "tender_bid_bad_id"))
            return
        rest = parts[2].strip()
        if "|" not in rest:
            send_chat(message, t(lang, "tender_bid_need_pipe"))
            return
        team, _, quote = rest.partition("|")
        team, quote = team.strip(), quote.strip()
        if not team:
            send_chat(message, t(lang, "tender_bid_empty_team"))
            return
        if not quote:
            send_chat(message, t(lang, "tender_bid_empty_quote"))
            return
        err: str | None = None
        bid_id: int | None = None
        with _lock:
            td = tenders_store.load_tenders()
            ten = tenders_store.tender_by_id(td, tid)
            if not ten:
                err = t(lang, "tender_bid_tender_missing", tid=tid)
            elif (ten.get("status") or "open").strip().lower() == "closed":
                err = t(lang, "tender_bid_tender_closed", tid=tid)
            else:
                bid_id = int(td["next_bid_id"])
                td["next_bid_id"] = bid_id + 1
                td["bids"].append(
                    {
                        "id": bid_id,
                        "tender_id": tid,
                        "team_text": team,
                        "quote": quote,
                        "bidder_id": uid,
                        "bidder_name": name,
                        "bidder_username": username,
                        "up": [],
                        "down": [],
                    }
                )
                tenders_store.save_tenders(td)
        if err:
            send_chat(message, err)
            return
        assert bid_id is not None
        send_chat(message, t(lang, "tender_bid_ok", bid_id=bid_id, tid=tid))

    @bot.message_handler(commands=["tender_close"])
    def cmd_tender_close(message: types.Message):
        uid, _, _ = publisher_from_message(message)
        admins = _load_admin_ids()
        parts = (message.text or "").split()
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
        if len(parts) < 2:
            send_chat(message, t(lang, "tender_close_usage"))
            return
        try:
            tid = int(parts[1])
        except ValueError:
            send_chat(message, t(lang, "tender_close_bad_id"))
            return
        if uid not in admins:
            send_chat(message, t(lang, "tender_close_need_admin"))
            return
        err: str | None = None
        with _lock:
            td = tenders_store.load_tenders()
            idx = None
            for i, x in enumerate(td.get("tenders") or []):
                try:
                    if int(x["id"]) == tid:
                        idx = i
                        break
                except (TypeError, ValueError, KeyError):
                    continue
            if idx is None:
                err = t(lang, "tender_close_not_found", tid=tid)
            else:
                cur = (td["tenders"][idx].get("status") or "open").strip().lower()
                if cur == "closed":
                    err = t(lang, "tender_close_already", tid=tid)
                else:
                    td["tenders"][idx]["status"] = "closed"
                    tenders_store.save_tenders(td)
        if err:
            send_chat(message, err)
            return
        send_chat(message, t(lang, "tender_close_ok", tid=tid))

    def _cb_vote_parse(data: str) -> tuple[int, str, str] | None:
        """Returns (pid, choice, mode) where mode is 'single' or 'all', or None."""
        if not data or ":" not in data:
            return None
        prefix, rest = data.split(":", 1)
        if prefix == "vs":
            mode = "single"
        elif prefix == "v":
            mode = "all"
        else:
            return None
        try:
            pid_s, choice = rest.split(":", 1)
            pid = int(pid_s)
        except ValueError:
            return None
        if choice not in ("u", "d"):
            return None
        return pid, choice, mode

    @bot.callback_query_handler(
        func=lambda c: c.data and (c.data.startswith("v:") or c.data.startswith("vs:"))
    )
    def on_vote(call: types.CallbackQuery):
        parsed = _cb_vote_parse(call.data)
        uid_cb = call.from_user.id if call.from_user else 0
        if not parsed:
            with _lock:
                data = _load_data()
                lang_cb = _user_lang(data, uid_cb)
            bot.answer_callback_query(call.id, t(lang_cb, "callback_invalid"))
            return

        pid, choice, mode = parsed
        uid = uid_cb
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            hint = _apply_vote(data, pid, uid, choice, lang)
            _save_data(data)
            if mode == "single":
                single = _format_single_project_vote_panel(data, pid, lang)
                if not single:
                    text, markup = _format_vote_panel(data, lang)
                else:
                    text, markup = single
            else:
                text, markup = _format_vote_panel(data, lang)

        try:
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
            )
            schedule_group_message_delete(
                call.message.chat.id,
                call.message.message_id,
                getattr(call.message.chat, "type", None),
            )
        except telebot.apihelper.ApiTelegramException:
            pass

        bot.answer_callback_query(call.id, hint, show_alert=False)

    @bot.callback_query_handler(
        func=lambda c: c.data and c.data.startswith("bel:")
    )
    def on_bid_label_click(call: types.CallbackQuery):
        uid_cb = call.from_user.id if call.from_user else 0
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid_cb)
        bot.answer_callback_query(
            call.id, t(lang, "tender_bid_id_btn_hint"), show_alert=False
        )

    @bot.callback_query_handler(
        func=lambda c: c.data and c.data.startswith("be:")
    )
    def on_bid_vote(call: types.CallbackQuery):
        parsed = _parse_bid_vote_callback(call.data or "")
        uid_cb = call.from_user.id if call.from_user else 0
        if not parsed:
            with _lock:
                data = _load_data()
                lang_cb = _user_lang(data, uid_cb)
            bot.answer_callback_query(call.id, t(lang_cb, "callback_invalid"))
            return

        part_idx, bid_id, choice = parsed
        uid = uid_cb
        with _lock:
            data = _load_data()
            lang = _user_lang(data, uid)
            td = tenders_store.load_tenders()
            hint = _apply_bid_vote(td, bid_id, uid, choice, lang)
            tenders_store.save_tenders(td)

            b = tenders_store.bid_ref_by_id(td, bid_id)
            if not b:
                bot.answer_callback_query(call.id, t(lang, "callback_invalid"))
                return
            tid = int(b["tender_id"])
            batches = tenders_store.format_tender_detail_batches(td, tid, lang)
            if not batches:
                bot.answer_callback_query(call.id, t(lang, "callback_invalid"))
                return
            if part_idx >= len(batches):
                part_idx = len(batches) - 1
            if part_idx < 0:
                part_idx = 0
            text, bid_ids, _ = batches[part_idx]
            markup = (
                _markup_bid_vote_rows(td, lang, bid_ids, part_idx)
                if bid_ids
                else types.InlineKeyboardMarkup()
            )

        try:
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
            )
            schedule_group_message_delete(
                call.message.chat.id,
                call.message.message_id,
                getattr(call.message.chat, "type", None),
            )
        except ApiTelegramException:
            pass

        bot.answer_callback_query(call.id, hint, show_alert=False)

    print("Bot is running. Press Ctrl+C to stop.")
    try:
        bot.infinity_polling(
            skip_pending=True, allowed_updates=["message", "callback_query"]
        )
    except ApiTelegramException as e:
        if getattr(e, "error_code", None) == 409:
            raise SystemExit(
                "Telegram 409 Conflict：同一 BOT_TOKEN 上已有其它进程在调用 getUpdates（长轮询）。\n"
                "请只保留一个实例：在项目目录执行 ./stop.sh；检查其它终端、服务器或 systemd 里是否还在跑本 bot；\n"
                "若该 Bot 在别处配置了 Webhook，需先删掉 webhook 或停用网页端拉取，再启动本程序。"
            ) from e
        raise


if __name__ == "__main__":
    main()
