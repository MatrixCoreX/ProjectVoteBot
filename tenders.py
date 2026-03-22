# -*- coding: utf-8 -*-
"""招标/投标独立数据与展示（与项目投票 projects_data 分离）。"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from i18n import t, tender_panel_footer_html, tender_panel_footer_max_len

TENDER_FILE = Path(__file__).resolve().parent / "tenders_data.json"

# Telegram 单条 HTML 上限 4096，预留页脚
_MAX_TENDER_MSG = 4000


def load_tenders() -> dict:
    if not TENDER_FILE.is_file():
        return {"next_tender_id": 1, "next_bid_id": 1, "tenders": [], "bids": []}
    try:
        raw = json.loads(TENDER_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"next_tender_id": 1, "next_bid_id": 1, "tenders": [], "bids": []}
    raw.setdefault("tenders", [])
    raw.setdefault("bids", [])
    raw.setdefault("next_tender_id", 1)
    raw.setdefault("next_bid_id", 1)
    _strip_tender_votes_inplace(raw)
    _ensure_bid_votes_inplace(raw)
    _sync_ids(raw)
    return raw


def _strip_tender_votes_inplace(data: dict) -> None:
    """招标不再使用 up/down，去掉旧字段以免混淆。"""
    for x in data.get("tenders") or []:
        x.pop("up", None)
        x.pop("down", None)


def _ensure_bid_votes_inplace(data: dict) -> None:
    for x in data.get("bids") or []:
        x.setdefault("up", [])
        x.setdefault("down", [])
        try:
            x["up"] = [int(i) for i in x["up"]]
            x["down"] = [int(i) for i in x["down"]]
        except (TypeError, ValueError):
            x["up"], x["down"] = [], []


def _sync_ids(data: dict) -> None:
    tenders = data.get("tenders") or []
    bids = data.get("bids") or []
    max_t = 0
    for x in tenders:
        try:
            max_t = max(max_t, int(x["id"]))
        except (TypeError, ValueError, KeyError):
            continue
    max_b = 0
    for x in bids:
        try:
            max_b = max(max_b, int(x["id"]))
        except (TypeError, ValueError, KeyError):
            continue
    try:
        nt = int(data["next_tender_id"])
    except (TypeError, ValueError):
        nt = 1
    try:
        nb = int(data["next_bid_id"])
    except (TypeError, ValueError):
        nb = 1
    data["next_tender_id"] = max(nt, max_t + 1)
    data["next_bid_id"] = max(nb, max_b + 1)


def save_tenders(data: dict) -> None:
    _sync_ids(data)
    TENDER_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def tender_by_id(data: dict, tid: int) -> dict | None:
    for x in data.get("tenders") or []:
        try:
            if int(x["id"]) == tid:
                return dict(x)
        except (TypeError, ValueError, KeyError):
            continue
    return None


def tender_ref_by_id(data: dict, tid: int) -> dict | None:
    for x in data.get("tenders") or []:
        try:
            if int(x["id"]) == tid:
                return x
        except (TypeError, ValueError, KeyError):
            continue
    return None


def bid_ref_by_id(data: dict, bid_id: int) -> dict | None:
    for x in data.get("bids") or []:
        try:
            if int(x["id"]) == bid_id:
                return x
        except (TypeError, ValueError, KeyError):
            continue
    return None


def get_tenders_sorted(data: dict) -> list[dict]:
    items = list(data.get("tenders") or [])
    items.sort(key=lambda z: int(z["id"]))
    return items


def bids_for_tender(data: dict, tid: int) -> list[dict]:
    out: list[dict] = []
    for b in data.get("bids") or []:
        try:
            if int(b["tender_id"]) == tid:
                out.append(dict(b))
        except (TypeError, ValueError, KeyError):
            continue
    out.sort(key=lambda x: int(x["id"]))
    return out


def _truncate_plain(s: str, max_len: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    if max_len <= 1:
        return "…"
    return s[: max_len - 1] + "…"


_MAX_BIDS_IN_TENDER_LIST = 18


def _tender_list_bids_under_tender(data: dict, tid: int, locale: str) -> str:
    """招标块内：逐条列出投标（摘要 + 票数）。"""
    bids = bids_for_tender(data, tid)
    if not bids:
        return f"  <i>{t(locale, 'tender_list_bids_none')}</i>\n"
    up_l = t(locale, "upvotes")
    dn_l = t(locale, "downvotes")
    lines: list[str] = []
    shown = bids[:_MAX_BIDS_IN_TENDER_LIST]
    for b in shown:
        try:
            bid_id = int(b["id"])
        except (TypeError, ValueError, KeyError):
            continue
        team = escape(_truncate_plain(b.get("team_text") or "", 56))
        quote = escape(_truncate_plain(b.get("quote") or "", 36))
        up_n = len(b.get("up") or [])
        dn_n = len(b.get("down") or [])
        lines.append(
            t(
                locale,
                "tender_list_bid_line",
                bid_id=bid_id,
                team=team or "—",
                quote=quote or "—",
                up_l=up_l,
                up_n=up_n,
                dn_l=dn_l,
                dn_n=dn_n,
            )
        )
    rest = len(bids) - len(shown)
    if rest > 0:
        lines.append(
            t(locale, "tender_list_bids_more", tid=tid, n=rest)
        )
    return "".join(lines)


def bids_for_tender_refs(data: dict, tid: int) -> list[dict]:
    """同一招标下的 bid 字典引用（可改 up/down）。"""
    _ensure_bid_votes_inplace(data)
    out: list[dict] = []
    for b in data.get("bids") or []:
        try:
            if int(b["tender_id"]) == tid:
                out.append(b)
        except (TypeError, ValueError, KeyError):
            continue
    out.sort(key=lambda x: int(x["id"]))
    return out


def _tender_list_item_html(data: dict, x: dict, locale: str) -> str:
    try:
        tid = int(x["id"])
    except (TypeError, ValueError, KeyError):
        return ""
    body = (x.get("text") or "").strip() or t(locale, "tender_no_text")
    if len(body) > 120:
        body = body[:117] + "..."
    st = (x.get("status") or "open").strip().lower()
    st_l = (
        t(locale, "tender_status_closed")
        if st == "closed"
        else t(locale, "tender_status_open")
    )
    n_bids = len(bids_for_tender(data, tid))
    bids_block = _tender_list_bids_under_tender(data, tid, locale)
    return (
        f"<b>#{tid}</b> [{st_l}] · {n_bids} {t(locale, 'tender_bids_count')}\n"
        f"{escape(body)}\n"
        f"{bids_block}"
        f"— — —\n"
    )


def split_tender_list_groups(data: dict, locale: str) -> list[list[dict]]:
    """按单条消息长度拆成多批招标（不含页脚），元素为 data 内 tender 引用。"""
    tenders = get_tenders_sorted(data)
    if not tenders:
        return []
    header_first = t(locale, "tender_list_title")
    header_cont = t(locale, "tender_list_continued")
    reserve = tender_panel_footer_max_len()
    max_body = _MAX_TENDER_MSG - reserve
    batches: list[list[dict]] = []
    cur: list[dict] = []

    for ten in tenders:
        while True:
            block = _tender_list_item_html(data, ten, locale)
            if not cur:
                batch_hdr = header_first if not batches else header_cont
            trial = batch_hdr + "".join(
                _tender_list_item_html(data, x, locale) for x in cur
            ) + block
            if len(trial) <= max_body:
                cur.append(ten)
                break
            if cur:
                batches.append(cur)
                cur = []
                continue
            cur.append(ten)
            break
    if cur:
        batches.append(cur)
    return batches


def format_tender_list_batches(data: dict, locale: str) -> list[str]:
    """纯文本列表（招标无赞踩）。"""
    groups = split_tender_list_groups(data, locale)
    if not groups:
        return [t(locale, "tender_list_empty")]
    n = len(groups)
    out: list[str] = []
    for i, group in enumerate(groups):
        head = t(locale, "tender_list_title") if i == 0 else t(
            locale, "tender_list_continued"
        )
        body = head + "".join(_tender_list_item_html(data, x, locale) for x in group)
        footer = tender_panel_footer_html(locale, i + 1, n)
        out.append(body.rstrip() + footer)
    return out


def _bid_block_html(b: dict, locale: str) -> str:
    try:
        bid_id = int(b["id"])
    except (TypeError, ValueError, KeyError):
        return ""
    team = (b.get("team_text") or "").strip() or "—"
    quote = (b.get("quote") or "").strip() or "—"
    bn = (b.get("bidder_name") or "").strip() or t(locale, "anonymous")
    bu = b.get("bidder_username")
    if bu:
        bidder = f"{escape(bn)} <code>@{escape(str(bu).strip().lstrip('@'))}</code>"
    else:
        bidder = escape(bn)
    up_n = len(b.get("up") or [])
    dn_n = len(b.get("down") or [])
    up_l = t(locale, "upvotes")
    dn_l = t(locale, "downvotes")
    return t(
        locale,
        "tender_bid_block",
        bid_id=bid_id,
        team=escape(team),
        quote=escape(quote),
        bidder=bidder,
        up_l=up_l,
        dn_l=dn_l,
        up_n=up_n,
        dn_n=dn_n,
    )


def format_tender_detail_batches(
    data: dict, tid: int, locale: str
) -> list[tuple[str, list[int], int]]:
    """(HTML, 本条消息内的投标编号列表, 分段序号 part_idx)。键盘一行对应一个 bid。"""
    ten = tender_ref_by_id(data, tid)
    if not ten:
        return []
    body_full = (ten.get("text") or "").strip() or t(locale, "tender_no_text")
    body = body_full
    st = (ten.get("status") or "open").strip().lower()
    st_l = (
        t(locale, "tender_status_closed")
        if st == "closed"
        else t(locale, "tender_status_open")
    )
    footer = t(locale, "tender_view_footer")
    cont_end = t(locale, "tender_view_cont")
    cont_hdr = t(locale, "tender_view_continued", tid=tid)

    def make_header(req_text: str) -> str:
        return (
            t(locale, "tender_view_header", tid=tid, status=st_l)
            + f"<b>{t(locale, 'tender_label_requirement')}</b>\n{escape(req_text)}\n"
            + f"<b>{t(locale, 'tender_label_bids')}</b>\n"
        )

    header = make_header(body)
    if len(header) + len(footer) > _MAX_TENDER_MSG:
        room = _MAX_TENDER_MSG - len(make_header("")) - len(footer) - 10
        body = body_full[: max(30, room)] + "…"
        header = make_header(body)

    bids = bids_for_tender_refs(data, tid)
    bid_vote_hint = t(locale, "tender_bid_vote_footer")

    if not bids:
        one = header + t(locale, "tender_no_bids_yet") + footer
        text = one[:_MAX_TENDER_MSG] if len(one) > _MAX_TENDER_MSG else one
        return [(text, [], 0)]

    msg_parts: list[tuple[str, list[int]]] = []
    cur = header
    cur_bids: list[int] = []

    for b in bids:
        try:
            bid_id = int(b["id"])
        except (TypeError, ValueError, KeyError):
            continue
        block = _bid_block_html(b, locale)
        if not block:
            continue
        if len(cur) + len(block) + len(footer) > _MAX_TENDER_MSG:
            if cur_bids:
                msg_parts.append((cur + cont_end, cur_bids))
                cur = cont_hdr + block
                cur_bids = [bid_id]
            else:
                room = _MAX_TENDER_MSG - len(cur) - len(footer) - 20
                short = block[: max(80, room)] + "…\n"
                cur += short
                cur_bids.append(bid_id)
        else:
            cur += block
            cur_bids.append(bid_id)
    msg_parts.append((cur + footer, cur_bids))

    out: list[tuple[str, list[int], int]] = []
    for part_idx, (text, bid_ids) in enumerate(msg_parts):
        if part_idx == 0 and bid_ids:
            text = text + bid_vote_hint
        out.append((text, bid_ids, part_idx))
    return out
