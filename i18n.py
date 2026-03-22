# -*- coding: utf-8 -*-
"""UI strings: locales cn / en / ko (ISO 639-1 style; cn kept for Chinese UI code)."""

from __future__ import annotations

LOCALES = frozenset({"cn", "en", "ko"})
DEFAULT_LOCALE = "en"

# /lang 参数别名 -> 标准码（韩语用国际通用 ISO 639-1：ko）
LANG_ALIASES: dict[str, str] = {
    "cn": "cn",
    "zh": "cn",
    "zh-cn": "cn",
    "chs": "cn",
    "en": "en",
    "eng": "en",
    "ko": "ko",
}

STRINGS: dict[str, dict[str, str]] = {
    "cn": {
        "help": (
            "你好！我是<b>项目投票</b>机器人。\n\n"
            "<b>命令</b>\n"
            "<code>/lang cn|en|ko</code> — 设置你的界面语言\n"
            "<code>/publish 描述</code> — 发布项目（自动编号 <code>#1</code>、<code>#2</code>…）\n"
            "<code>/projects</code> — 列出所有项目与票数\n"
            "<code>/vote 编号</code> — 对某项目投票（内联按钮）\n"
            "<code>/edit 编号 新描述</code> — 仅发布者可改描述\n"
            "<code>/delete 编号</code> — 仅发布者可删除（编号不回收）\n\n"
            "<b>切换语言</b>\n"
            "<code>/lang cn</code> — 中文\n"
            "<code>/lang en</code> — English 英语（<i>首次使用默认</i>）\n"
            "<code>/lang ko</code> — 한국어（ISO 639-1）\n"
        ),
        "publish_need_desc": "请加上描述，例如：\n<code>/publish 开源记账应用</code>",
        "publish_ok": (
            "✅ 已发布项目 <b>#{pid}</b>\n\n"
            "发送 <code>/projects</code> 查看列表，<code>/vote {pid}</code> 投票。\n"
            "可随时 <code>/edit {pid} …</code> 或 <code>/delete {pid}</code>。"
        ),
        "projects_empty": (
            "📭 还没有项目。\n"
            "使用 <code>/publish 描述</code> 发布第一条。"
        ),
        "projects_title": "📋 <b>项目与投票</b>\n",
        "projects_continued": "📋 <b>项目与投票</b> <i>（续）</i>\n",
        "vote_footer": (
            "💡 <b>如何投票：</b>发送 <code>/vote</code> 加项目编号，例如 "
            "<code>/vote 3</code>，即可显示 👍/👎 按钮。"
        ),
        "part_footer": "\n📄 <i>第 {part}/{total} 部分</i>",
        "vote_panel_more": "\n\n<i>第 1 部分，共 {n} 部分 — 发送 /projects 查看完整列表。</i>",
        "vote_panel_more_short": "\n\n<i>更多请用 /projects</i>",
        "publisher": "发布者",
        "upvotes": "👍 赞成",
        "downvotes": "👎 反对",
        "no_description": "（无描述）",
        "anonymous": "匿名",
        "single_vote_title": "🗳 <b>为项目 #{pid} 投票</b>\n",
        "btn_up": "👍 赞成 ({n})",
        "btn_down": "👎 反对 ({n})",
        "vote_need_id": "请指定项目编号，例如 <code>/vote 3</code>\n用 <code>/projects</code> 查看编号。",
        "vote_bad_id": "编号无效，请使用数字，例如 <code>/vote 3</code>。",
        "vote_no_such": "没有项目 <b>#{pid}</b>。用 <code>/projects</code> 查看编号。",
        "delete_usage": "用法：<code>/delete 编号</code> — 仅发布者可删除。",
        "delete_bad_id": "编号无效。示例：<code>/delete 3</code>",
        "delete_no_such": "没有项目 <b>#{pid}</b>。用 <code>/projects</code> 查看编号。",
        "delete_not_pub": "只有<b>发布者</b>可以删除该项目。",
        "delete_ok": "🗑 已删除项目 <b>#{pid}</b>。之后新项目仍按下一个编号递增。",
        "edit_usage": (
            "用法：<code>/edit 编号 新描述</code>\n"
            "示例：<code>/edit 3 更新后的说明文字</code>"
        ),
        "edit_bad_id": "编号无效。示例：<code>/edit 3 新文字</code>",
        "edit_empty": "新描述不能为空。",
        "edit_no_such": "没有项目 <b>#{pid}</b>。用 <code>/projects</code> 查看编号。",
        "edit_not_pub": "只有<b>发布者</b>可以编辑该项目。",
        "edit_ok": "✏️ 已更新项目 <b>#{pid}</b>。",
        "hint_no_project": "未找到该项目。",
        "hint_up_off": "已取消赞成。",
        "hint_up_on": "已记录赞成。",
        "hint_down_off": "已取消反对。",
        "hint_down_on": "已记录反对。",
        "callback_invalid": "无效操作",
        "lang_usage": (
            "用法：<code>/lang cn</code>、<code>/lang en</code> 或 <code>/lang ko</code>\n"
            "你当前语言：<b>{name}</b>"
        ),
        "lang_set": "界面语言已设为：<b>{name}</b>",
        "lang_bad": "不支持的语言。请使用：<code>cn</code>、<code>en</code>、<code>ko</code>（韩语，ISO 639-1）。",
    },
    "en": {
        "help": (
            "Hi! I am a <b>project voting</b> bot.\n\n"
            "<b>Commands</b>\n"
            "<code>/lang cn|en|ko</code> — set your UI language\n"
            "<code>/publish description</code> — publish a project "
            "(auto number <code>#1</code>, <code>#2</code>, …)\n"
            "<code>/projects</code> — list all projects with vote counts\n"
            "<code>/vote id</code> — vote on project <code>#id</code> (inline buttons)\n"
            "<code>/edit id new text</code> — publisher only: update description\n"
            "<code>/delete id</code> — publisher only: remove project "
            "(numbers keep increasing; ids are not reused)\n\n"
            "<b>Language</b> <i>(default on first use: English)</i>\n"
            "<code>/lang cn</code> — <b>中文</b> (Chinese UI)\n"
            "<code>/lang ko</code> — <b>한국어</b> (Korean, ISO 639-1 <code>ko</code>)\n"
            "<code>/lang en</code> — English UI\n"
        ),
        "publish_need_desc": (
            "Add a description, e.g.\n"
            "<code>/publish Open-source expense tracker app</code>"
        ),
        "publish_ok": (
            "✅ Published project <b>#{pid}</b>\n\n"
            "Use <code>/projects</code> to list and "
            "<code>/vote {pid}</code> to vote.\n"
            "You can <code>/edit {pid} …</code> or <code>/delete {pid}</code> anytime."
        ),
        "projects_empty": (
            "📭 No projects yet.\n"
            "Use <code>/publish description</code> to add the first one."
        ),
        "projects_title": "📋 <b>Projects &amp; votes</b>\n",
        "projects_continued": "📋 <b>Projects &amp; votes</b> <i>(continued)</i>\n",
        "vote_footer": (
            "💡 <b>How to vote:</b> send <code>/vote</code> with the project number — "
            "e.g. <code>/vote 3</code> — to get 👍/👎 buttons for that project."
        ),
        "part_footer": "\n📄 <i>Part {part}/{total}</i>",
        "vote_panel_more": (
            "\n\n<i>Part 1 of {n} — send /projects for the full list.</i>"
        ),
        "vote_panel_more_short": "\n\n<i>More: /projects</i>",
        "publisher": "Publisher",
        "upvotes": "👍 Upvotes",
        "downvotes": "👎 Downvotes",
        "no_description": "(no description)",
        "anonymous": "Anonymous",
        "single_vote_title": "🗳 <b>Vote on project #{pid}</b>\n",
        "btn_up": "👍 Upvote ({n})",
        "btn_down": "👎 Downvote ({n})",
        "vote_need_id": (
            "Specify a project number, e.g. <code>/vote 3</code>\n"
            "Use <code>/projects</code> to see IDs."
        ),
        "vote_bad_id": "Invalid project id. Use a number, e.g. <code>/vote 3</code>.",
        "vote_no_such": "No project <b>#{pid}</b>. Use <code>/projects</code> to list IDs.",
        "delete_usage": "Usage: <code>/delete id</code> — only the publisher can delete.",
        "delete_bad_id": "Invalid id. Example: <code>/delete 3</code>",
        "delete_no_such": "No project <b>#{pid}</b>. Use <code>/projects</code> for ids.",
        "delete_not_pub": "Only the <b>publisher</b> can delete this project.",
        "delete_ok": (
            "🗑 Project <b>#{pid}</b> removed. New publishes still get the next number."
        ),
        "edit_usage": (
            "Usage: <code>/edit id new description</code>\n"
            "Example: <code>/edit 3 Updated pitch text here</code>"
        ),
        "edit_bad_id": "Invalid id. Example: <code>/edit 3 New text</code>",
        "edit_empty": "New description cannot be empty.",
        "edit_no_such": "No project <b>#{pid}</b>. Use <code>/projects</code> for ids.",
        "edit_not_pub": "Only the <b>publisher</b> can edit this project.",
        "edit_ok": "✏️ Project <b>#{pid}</b> updated.",
        "hint_no_project": "Project not found.",
        "hint_up_off": "Upvote removed.",
        "hint_up_on": "Upvote recorded.",
        "hint_down_off": "Downvote removed.",
        "hint_down_on": "Downvote recorded.",
        "callback_invalid": "Invalid action",
        "lang_usage": (
            "Usage: <code>/lang cn</code>, <code>/lang en</code>, or <code>/lang ko</code>\n"
            "Your language: <b>{name}</b>"
        ),
        "lang_set": "UI language set to: <b>{name}</b>",
        "lang_bad": "Unknown language. Use: <code>cn</code>, <code>en</code>, or <code>ko</code> (Korean).",
    },
    "ko": {
        "help": (
            "안녕하세요! <b>프로젝트 투표</b> 봇입니다.\n\n"
            "<b>명령</b>\n"
            "<code>/lang cn|en|ko</code> — 화면 언어 설정\n"
            "<code>/publish 설명</code> — 프로젝트 등록 (자동 번호 <code>#1</code>, <code>#2</code> …)\n"
            "<code>/projects</code> — 전체 목록과 표 수\n"
            "<code>/vote 번호</code> — 해당 프로젝트 투표 (인라인 버튼)\n"
            "<code>/edit 번호 새설명</code> — 작성자만 설명 수정\n"
            "<code>/delete 번호</code> — 작성자만 삭제 (번호는 재사용 안 됨)\n\n"
            "<b>언어 전환</b> <i>(첫 사용 시 기본: English)</i>\n"
            "<code>/lang cn</code> — 中文\n"
            "<code>/lang en</code> — English\n"
            "<code>/lang ko</code> — 한국어 (ISO 639-1)\n"
        ),
        "publish_need_desc": "설명을 입력하세요. 예:\n<code>/publish 오픈소스 가계부 앱</code>",
        "publish_ok": (
            "✅ 프로젝트 <b>#{pid}</b> 를 등록했습니다.\n\n"
            "<code>/projects</code> 로 목록을 보고 <code>/vote {pid}</code> 로 투표하세요.\n"
            "언제든 <code>/edit {pid} …</code> 또는 <code>/delete {pid}</code> 가능합니다."
        ),
        "projects_empty": (
            "📭 아직 프로젝트가 없습니다.\n"
            "<code>/publish 설명</code> 으로 첫 항목을 추가하세요."
        ),
        "projects_title": "📋 <b>프로젝트 및 투표</b>\n",
        "projects_continued": "📋 <b>프로젝트 및 투표</b> <i>(계속)</i>\n",
        "vote_footer": (
            "💡 <b>투표 방법:</b> <code>/vote</code> 와 프로젝트 번호를 보내세요. "
            "예: <code>/vote 3</code> — 👍/👎 버튼이 표시됩니다."
        ),
        "part_footer": "\n📄 <i>{part}/{total} 부분</i>",
        "vote_panel_more": (
            "\n\n<i>전체 {n}부 중 1부 — 전체 목록은 /projects</i>"
        ),
        "vote_panel_more_short": "\n\n<i>더 보기: /projects</i>",
        "publisher": "작성자",
        "upvotes": "👍 찬성",
        "downvotes": "👎 반대",
        "no_description": "(설명 없음)",
        "anonymous": "익명",
        "single_vote_title": "🗳 <b>프로젝트 #{pid} 투표</b>\n",
        "btn_up": "👍 찬성 ({n})",
        "btn_down": "👎 반대 ({n})",
        "vote_need_id": (
            "프로젝트 번호를 지정하세요. 예: <code>/vote 3</code>\n"
            "번호는 <code>/projects</code> 에서 확인하세요."
        ),
        "vote_bad_id": "번호가 올바르지 않습니다. 예: <code>/vote 3</code>",
        "vote_no_such": "프로젝트 <b>#{pid}</b> 가 없습니다. <code>/projects</code> 로 확인하세요.",
        "delete_usage": "사용법: <code>/delete 번호</code> — 작성자만 삭제할 수 있습니다.",
        "delete_bad_id": "번호가 올바르지 않습니다. 예: <code>/delete 3</code>",
        "delete_no_such": "프로젝트 <b>#{pid}</b> 가 없습니다. <code>/projects</code> 를 확인하세요.",
        "delete_not_pub": "<b>작성자</b>만 이 프로젝트를 삭제할 수 있습니다.",
        "delete_ok": (
            "🗑 프로젝트 <b>#{pid}</b> 를 삭제했습니다. 이후 새 글은 다음 번호를 씁니다."
        ),
        "edit_usage": (
            "사용법: <code>/edit 번호 새 설명</code>\n"
            "예: <code>/edit 3 수정된 설명</code>"
        ),
        "edit_bad_id": "번호가 올바르지 않습니다. 예: <code>/edit 3 새 글</code>",
        "edit_empty": "새 설명은 비울 수 없습니다.",
        "edit_no_such": "프로젝트 <b>#{pid}</b> 가 없습니다. <code>/projects</code> 를 확인하세요.",
        "edit_not_pub": "<b>작성자</b>만 이 프로젝트를 수정할 수 있습니다.",
        "edit_ok": "✏️ 프로젝트 <b>#{pid}</b> 를 수정했습니다.",
        "hint_no_project": "프로젝트를 찾을 수 없습니다.",
        "hint_up_off": "찬성을 취소했습니다.",
        "hint_up_on": "찬성했습니다.",
        "hint_down_off": "반대를 취소했습니다.",
        "hint_down_on": "반대했습니다.",
        "callback_invalid": "잘못된 동작입니다.",
        "lang_usage": (
            "사용법: <code>/lang cn</code>, <code>/lang en</code>, <code>/lang ko</code>\n"
            "현재 언어: <b>{name}</b>"
        ),
        "lang_set": "화면 언어: <b>{name}</b>",
        "lang_bad": "지원하지 않는 언어입니다. <code>cn</code>, <code>en</code>, <code>ko</code>(ISO 639-1)를 사용하세요.",
    },
}

LOCALE_DISPLAY: dict[str, str] = {
    "cn": "中文",
    "en": "English",
    "ko": "한국어",
}


def normalize_locale(code: str) -> str | None:
    c = code.strip().lower()
    return LANG_ALIASES.get(c)


def t(locale: str, key: str, **kwargs: object) -> str:
    loc = locale if locale in LOCALES else DEFAULT_LOCALE
    s = STRINGS.get(loc, STRINGS[DEFAULT_LOCALE]).get(
        key, STRINGS[DEFAULT_LOCALE][key]
    )
    if kwargs:
        return s.format(**kwargs)
    return s


def vote_panel_footer_html(locale: str, part: int, total: int) -> str:
    base = t(locale, "vote_footer")
    lines = ["\n", base]
    if total > 1:
        lines.append(t(locale, "part_footer", part=part, total=total))
    lines.append("\n")
    return "".join(lines)


def vote_panel_footer_max_len() -> int:
    """各语言页脚最大可能长度（用于拆批预留）。"""
    return max(len(vote_panel_footer_html(loc, 99, 99)) for loc in LOCALES)
