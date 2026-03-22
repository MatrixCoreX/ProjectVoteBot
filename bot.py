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
_lock = threading.Lock()


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
    p["up"] = [int(x) for x in p["up"]]
    p["down"] = [int(x) for x in p["down"]]
    return p


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
                "author_id": p.get("author_id"),
                "author_name": p.get("author_name", ""),
                "author_username": p.get("author_username"),
                "up": p["up"],
                "down": p["down"],
            }
            break
    return hint


def main() -> None:
    _load_env_file()
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Set BOT_TOKEN in the environment or in .env (BOT_TOKEN=your_token)."
        )

    bot = telebot.TeleBot(token, parse_mode="HTML")

    def send_chat(message: types.Message, text: str, **kwargs) -> None:
        """发到当前聊天，不引用用户那条命令（非 reply）。"""
        bot.send_message(message.chat.id, text, **kwargs)

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

    @bot.message_handler(commands=["publish"])
    def cmd_publish(message: types.Message):
        uid, uname, uname_at = publisher_from_message(message)
        parts = (message.text or "").split(maxsplit=1)
        desc = parts[1].strip() if len(parts) > 1 else ""
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
                if not _is_publisher(p, uid):
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

        new_text = parts[2].strip()
        if not new_text:
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
                if not _is_publisher(p, uid):
                    err = t(lang, "edit_not_pub")
                else:
                    p["text"] = new_text
                    data["projects"][idx] = {
                        "id": p["id"],
                        "text": p["text"],
                        "author_id": p.get("author_id"),
                        "author_name": pub_name,
                        "author_username": pub_username,
                        "up": p["up"],
                        "down": p["down"],
                    }
                    _save_data(data)

        if err:
            send_chat(message, err)
            return

        send_chat(message, t(lang, "edit_ok", pid=pid))

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
        except telebot.apihelper.ApiTelegramException:
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
