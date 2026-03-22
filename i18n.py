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
            "<code>/publish 描述 | 预算</code> — 发布项目（预算可省略；<code>|</code> 前为描述）\n"
            "<code>/projects</code> — 列出所有项目与票数\n"
            "<code>/vote 编号</code> — 对某项目投票（内联按钮）\n"
            "<code>/edit 编号 新描述 | 预算</code> — 发布者或管理员可改（不写 <code>|</code> 则只改描述、保留原预算）\n"
            "<code>/delete 编号</code> — 发布者或管理员可删除（编号不回收）\n\n"
            "<b>招标（公开需求与投标）</b>\n"
            "<code>/tender_add 需求正文</code> — 仅 <code>config.json</code> 管理员发布\n"
            "<code>/tenders</code> — 公开列表（每条招标下列出各投标摘要与 👍/👎 数）\n"
            "<code>/tender_view 编号</code> — 需求与全部投标（<b>每条投标</b>可 👍/👎）\n"
            "<code>/tender_bid 编号 团队说明 | 报价</code> — 任何人可投（第一个 <code>|</code> 后为报价）\n"
            "<code>/tender_close 编号</code> — 管理员截止投标\n\n"
            "<b>切换语言</b>\n"
            "<code>/lang cn</code> — 中文\n"
            "<code>/lang en</code> — English 英语（<i>首次使用默认</i>）\n"
            "<code>/lang ko</code> — 한국어（ISO 639-1）\n"
        ),
        "publish_need_desc": (
            "请填写<b>项目描述</b>；预算写在第一个 <code>|</code> 后面，可省略。\n"
            "例：<code>/publish 开源记账应用 | 预算 5000 元</code>\n"
            "或：<code>/publish 仅描述不要预算</code>"
        ),
        "publish_ok": (
            "✅ 已发布项目 <b>#{pid}</b>\n\n"
            "发送 <code>/projects</code> 查看列表，<code>/vote {pid}</code> 投票。\n"
            "可随时 <code>/edit {pid} …</code> 或 <code>/delete {pid}</code>。"
        ),
        "projects_empty": (
            "📭 还没有项目。\n"
            "使用 <code>/publish 描述 | 预算</code> 发布第一条（预算可省略）。"
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
        "budget_label": "预算",
        "budget_not_set": "<i>（未填写）</i>",
        "no_description": "（无描述）",
        "anonymous": "匿名",
        "single_vote_title": "🗳 <b>为项目 #{pid} 投票</b>\n",
        "btn_up": "👍 赞成 ({n})",
        "btn_down": "👎 反对 ({n})",
        "vote_need_id": "请指定项目编号，例如 <code>/vote 3</code>\n用 <code>/projects</code> 查看编号。",
        "vote_bad_id": "编号无效，请使用数字，例如 <code>/vote 3</code>。",
        "vote_no_such": "没有项目 <b>#{pid}</b>。用 <code>/projects</code> 查看编号。",
        "delete_usage": "用法：<code>/delete 编号</code> — 发布者或 <code>config.json</code> 中的管理员可删除。",
        "delete_bad_id": "编号无效。示例：<code>/delete 3</code>",
        "delete_no_such": "没有项目 <b>#{pid}</b>。用 <code>/projects</code> 查看编号。",
        "delete_not_pub": "只有<b>发布者</b>或<b>机器人管理员</b>（见 config.json）可以删除该项目。",
        "delete_ok": "🗑 已删除项目 <b>#{pid}</b>。之后新项目仍按下一个编号递增。",
        "edit_usage": (
            "用法（发布者或 config.json 管理员）：\n"
            "<code>/edit 编号 新描述</code> — 只改描述，预算不变\n"
            "<code>/edit 编号 新描述 | 新预算</code> — 同时改；<code>|</code> 后留空则清空预算"
        ),
        "edit_bad_id": "编号无效。示例：<code>/edit 3 新文字</code>",
        "edit_empty": "新描述不能为空。",
        "edit_no_such": "没有项目 <b>#{pid}</b>。用 <code>/projects</code> 查看编号。",
        "edit_not_pub": "只有<b>发布者</b>或<b>机器人管理员</b>（见 config.json）可以编辑该项目。",
        "edit_ok": "✏️ 已更新项目 <b>#{pid}</b>。",
        "hint_no_project": "未找到该项目。",
        "hint_up_off": "已取消赞成。",
        "hint_up_on": "已记录赞成。",
        "hint_down_off": "已取消反对。",
        "hint_down_on": "已记录反对。",
        "callback_invalid": "无效操作",
        "id_private_only": "此命令仅可在<b>私聊</b>中使用。请打开与本机器人的私聊发送 <code>/id</code>。",
        "id_reply": "你的 Telegram 用户 ID：<code>{uid}</code>\n用户名：{uname}",
        "id_no_username": "（未设置）",
        "lang_usage": (
            "用法：<code>/lang cn</code>、<code>/lang en</code> 或 <code>/lang ko</code>\n"
            "你当前语言：<b>{name}</b>"
        ),
        "lang_set": "界面语言已设为：<b>{name}</b>",
        "lang_bad": "不支持的语言。请使用：<code>cn</code>、<code>en</code>、<code>ko</code>（韩语，ISO 639-1）。",
        "tender_list_empty": "📭 暂无招标需求。管理员可用 <code>/tender_add …</code> 发布。",
        "tender_list_title": "📑 <b>招标列表</b>（公开）\n",
        "tender_list_continued": "📑 <b>招标列表</b> <i>（续）</i>\n",
        "tender_list_footer": "\n💡 发送 <code>/tender_view 编号</code> 查看详情（含每条投标的 👍/👎 按钮）。",
        "tender_list_bids_none": "暂无投标",
        "tender_list_bid_line": (
            "  └ <b>投标 #{bid_id}</b> {team} · <i>{quote}</i>\n"
            "    {up_l} <b>{up_n}</b> · {dn_l} <b>{dn_n}</b>\n"
        ),
        "tender_list_bids_more": (
            "  <i>…另有 <b>{n}</b> 份投标，请 <code>/tender_view {tid}</code></i>\n"
        ),
        "tender_bid_vote_footer": (
            "\n💡 每条<b>投标</b>下方按钮可 👍/👎（再点同一按钮可取消，规则同项目投票）。"
        ),
        "tender_bid_id_btn_hint": "此为投标编号；请点右侧 👍 / 👎。",
        "tender_bids_count": "份投标",
        "tender_no_text": "（无正文）",
        "tender_status_open": "征集中",
        "tender_status_closed": "已截止",
        "tender_view_header": "📑 <b>招标 #{tid}</b> · {status}\n\n",
        "tender_label_requirement": "需求",
        "tender_label_bids": "投标",
        "tender_no_bids_yet": "<i>尚无投标。</i>\n",
        "tender_bid_block": (
            "<b>投标 #{bid_id}</b>\n"
            "<b>团队：</b>{team}\n<b>报价：</b>{quote}\n<b>投标人：</b>{bidder}\n"
            "{up_l}: <b>{up_n}</b> · {dn_l}: <b>{dn_n}</b>\n"
            "— — —\n"
        ),
        "tender_view_footer": "",
        "tender_view_cont": "\n<i>（下一条消息续）</i>\n",
        "tender_view_continued": "📑 <b>招标 #{tid}</b> · <i>投标（续）</i>\n\n",
        "tender_add_need_admin": "只有 <code>config.json</code> 中的<b>机器人管理员</b>可以发布招标。",
        "tender_add_usage": "用法（仅管理员）：<code>/tender_add 需求正文</code>",
        "tender_add_ok": (
            "✅ 已发布招标 <b>#{tid}</b>。\n"
            "列表：<code>/tenders</code> · 投标：<code>/tender_bid {tid} 团队说明 | 报价</code>"
        ),
        "tender_view_not_found": "没有招标 <b>#{tid}</b>。发送 <code>/tenders</code> 查看编号。",
        "tender_view_bad_id": "编号无效。示例：<code>/tender_view 3</code>",
        "tender_bid_usage": (
            "用法：<code>/tender_bid 编号 团队说明 | 报价</code>\n"
            "第一个 <code>|</code> 后面为报价；前面为团队说明。"
        ),
        "tender_bid_bad_id": "编号无效。示例：<code>/tender_bid 3 我们团队 | 5000 元</code>",
        "tender_bid_need_pipe": "请使用第一个 <code>|</code> 分隔团队说明与报价。",
        "tender_bid_empty_team": "团队说明不能为空。",
        "tender_bid_empty_quote": "报价不能为空（可写「面议」等）。",
        "tender_bid_tender_missing": "没有招标 <b>#{tid}</b>。",
        "tender_bid_tender_closed": "招标 <b>#{tid}</b> 已截止，不再接受投标。",
        "tender_bid_ok": "✅ 已提交投标 <b>#{bid_id}</b>（招标 #{tid}）。详情：<code>/tender_view {tid}</code>",
        "tender_close_usage": "用法（仅管理员）：<code>/tender_close 编号</code>",
        "tender_close_bad_id": "编号无效。示例：<code>/tender_close 3</code>",
        "tender_close_not_found": "没有招标 <b>#{tid}</b>。",
        "tender_close_need_admin": "仅<b>管理员</b>可截止招标。",
        "tender_close_ok": "✅ 招标 <b>#{tid}</b> 已截止（仍可查看）。",
        "tender_close_already": "招标 <b>#{tid}</b> 已是截止状态。",
    },
    "en": {
        "help": (
            "Hi! I am a <b>project voting</b> bot.\n\n"
            "<b>Commands</b>\n"
            "<code>/lang cn|en|ko</code> — set your UI language\n"
            "<code>/publish description | budget</code> — publish (budget optional; "
            "auto number <code>#1</code>, <code>#2</code>, …)\n"
            "<code>/projects</code> — list all projects with vote counts\n"
            "<code>/vote id</code> — vote on project <code>#id</code> (inline buttons)\n"
            "<code>/edit id text | budget</code> — publisher or admin (omit <code>|</code> to only change text)\n"
            "<code>/delete id</code> — publisher or bot admin: remove project "
            "(numbers keep increasing; ids are not reused)\n\n"
            "<b>Tenders (public RFP &amp; bids)</b>\n"
            "<code>/tender_add text</code> — bot admins in <code>config.json</code> only\n"
            "<code>/tenders</code> — list (bids under each tender + vote counts)\n"
            "<code>/tender_view id</code> — requirement + bids (<b>👍/👎 per bid</b>)\n"
            "<code>/tender_bid id team notes | quote</code> — anyone; first <code>|</code> separates quote\n"
            "<code>/tender_close id</code> — admin closes bidding\n\n"
            "<b>Language</b> <i>(default on first use: English)</i>\n"
            "<code>/lang cn</code> — <b>中文</b> (Chinese UI)\n"
            "<code>/lang ko</code> — <b>한국어</b> (Korean, ISO 639-1 <code>ko</code>)\n"
            "<code>/lang en</code> — English UI\n"
        ),
        "publish_need_desc": (
            "Add a <b>project description</b>. Optional budget after the first <code>|</code>.\n"
            "e.g. <code>/publish Expense tracker | USD 5000</code>\n"
            "or <code>/publish Description only</code>"
        ),
        "publish_ok": (
            "✅ Published project <b>#{pid}</b>\n\n"
            "Use <code>/projects</code> to list and "
            "<code>/vote {pid}</code> to vote.\n"
            "You can <code>/edit {pid} …</code> or <code>/delete {pid}</code> anytime."
        ),
        "projects_empty": (
            "📭 No projects yet.\n"
            "Use <code>/publish description | budget</code> (budget optional)."
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
        "budget_label": "Budget",
        "budget_not_set": "<i>(not set)</i>",
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
        "delete_usage": "Usage: <code>/delete id</code> — publisher or admin (see <code>config.json</code>).",
        "delete_bad_id": "Invalid id. Example: <code>/delete 3</code>",
        "delete_no_such": "No project <b>#{pid}</b>. Use <code>/projects</code> for ids.",
        "delete_not_pub": "Only the <b>publisher</b> or a <b>bot admin</b> (see config.json) can delete this project.",
        "delete_ok": (
            "🗑 Project <b>#{pid}</b> removed. New publishes still get the next number."
        ),
        "edit_usage": (
            "Usage (publisher or admin):\n"
            "<code>/edit id new text</code> — description only, budget unchanged\n"
            "<code>/edit id text | budget</code> — both; empty after <code>|</code> clears budget"
        ),
        "edit_bad_id": "Invalid id. Example: <code>/edit 3 New text</code>",
        "edit_empty": "New description cannot be empty.",
        "edit_no_such": "No project <b>#{pid}</b>. Use <code>/projects</code> for ids.",
        "edit_not_pub": "Only the <b>publisher</b> or a <b>bot admin</b> (see config.json) can edit this project.",
        "edit_ok": "✏️ Project <b>#{pid}</b> updated.",
        "hint_no_project": "Project not found.",
        "hint_up_off": "Upvote removed.",
        "hint_up_on": "Upvote recorded.",
        "hint_down_off": "Downvote removed.",
        "hint_down_on": "Downvote recorded.",
        "callback_invalid": "Invalid action",
        "id_private_only": "This command only works in <b>private chat</b>. Open a DM with this bot and send <code>/id</code>.",
        "id_reply": "Your Telegram user ID: <code>{uid}</code>\nUsername: {uname}",
        "id_no_username": "(not set)",
        "lang_usage": (
            "Usage: <code>/lang cn</code>, <code>/lang en</code>, or <code>/lang ko</code>\n"
            "Your language: <b>{name}</b>"
        ),
        "lang_set": "UI language set to: <b>{name}</b>",
        "lang_bad": "Unknown language. Use: <code>cn</code>, <code>en</code>, or <code>ko</code> (Korean).",
        "tender_list_empty": "📭 No tenders yet. Admins: <code>/tender_add …</code>",
        "tender_list_title": "📑 <b>Tenders</b> (public)\n",
        "tender_list_continued": "📑 <b>Tenders</b> <i>(continued)</i>\n",
        "tender_list_footer": "\n💡 <code>/tender_view id</code> for full detail (👍/👎 per bid).",
        "tender_list_bids_none": "No bids yet",
        "tender_list_bid_line": (
            "  └ <b>Bid #{bid_id}</b> {team} · <i>{quote}</i>\n"
            "    {up_l} <b>{up_n}</b> · {dn_l} <b>{dn_n}</b>\n"
        ),
        "tender_list_bids_more": (
            "  <i>…<b>{n}</b> more bid(s): <code>/tender_view {tid}</code></i>\n"
        ),
        "tender_bid_vote_footer": (
            "\n💡 Use <b>👍/👎</b> under each <b>bid</b> (tap again to undo; same rules as project votes)."
        ),
        "tender_bid_id_btn_hint": "Bid id; use 👍 / 👎 on the right.",
        "tender_bids_count": "bids",
        "tender_no_text": "(no text)",
        "tender_status_open": "open",
        "tender_status_closed": "closed",
        "tender_view_header": "📑 <b>Tender #{tid}</b> · {status}\n\n",
        "tender_label_requirement": "Requirement",
        "tender_label_bids": "Bids",
        "tender_no_bids_yet": "<i>No bids yet.</i>\n",
        "tender_bid_block": (
            "<b>Bid #{bid_id}</b>\n"
            "<b>Team:</b> {team}\n<b>Quote:</b> {quote}\n<b>Bidder:</b> {bidder}\n"
            "{up_l}: <b>{up_n}</b> · {dn_l}: <b>{dn_n}</b>\n"
            "— — —\n"
        ),
        "tender_view_footer": "",
        "tender_view_cont": "\n<i>(continued in next message)</i>\n",
        "tender_view_continued": "📑 <b>Tender #{tid}</b> · <i>bids (cont.)</i>\n\n",
        "tender_add_need_admin": "Only <b>bot admins</b> in <code>config.json</code> can publish tenders.",
        "tender_add_usage": "Usage (admin): <code>/tender_add requirement text</code>",
        "tender_add_ok": (
            "✅ Tender <b>#{tid}</b> published.\n"
            "List: <code>/tenders</code> · bid: <code>/tender_bid {tid} team | quote</code>"
        ),
        "tender_view_not_found": "No tender <b>#{tid}</b>. Use <code>/tenders</code> for ids.",
        "tender_view_bad_id": "Invalid id. Example: <code>/tender_view 3</code>",
        "tender_bid_usage": (
            "Usage: <code>/tender_bid id team notes | quote</code>\n"
            "First <code>|</code> starts the quote."
        ),
        "tender_bid_bad_id": "Invalid id. Example: <code>/tender_bid 3 We | USD 100</code>",
        "tender_bid_need_pipe": "Use the first <code>|</code> to separate team notes and quote.",
        "tender_bid_empty_team": "Team notes cannot be empty.",
        "tender_bid_empty_quote": "Quote cannot be empty (e.g. write TBD).",
        "tender_bid_tender_missing": "No tender <b>#{tid}</b>.",
        "tender_bid_tender_closed": "Tender <b>#{tid}</b> is closed for bids.",
        "tender_bid_ok": "✅ Bid <b>#{bid_id}</b> recorded (tender #{tid}). <code>/tender_view {tid}</code>",
        "tender_close_usage": "Usage (admin): <code>/tender_close id</code>",
        "tender_close_bad_id": "Invalid id. Example: <code>/tender_close 3</code>",
        "tender_close_not_found": "No tender <b>#{tid}</b>.",
        "tender_close_need_admin": "Only <b>admins</b> can close a tender.",
        "tender_close_ok": "✅ Tender <b>#{tid}</b> closed (still viewable).",
        "tender_close_already": "Tender <b>#{tid}</b> is already closed.",
    },
    "ko": {
        "help": (
            "안녕하세요! <b>프로젝트 투표</b> 봇입니다.\n\n"
            "<b>명령</b>\n"
            "<code>/lang cn|en|ko</code> — 화면 언어 설정\n"
            "<code>/publish 설명 | 예산</code> — 프로젝트 등록 (예산 생략 가능, 자동 번호 <code>#1</code> …)\n"
            "<code>/projects</code> — 전체 목록과 표 수\n"
            "<code>/vote 번호</code> — 해당 프로젝트 투표 (인라인 버튼)\n"
            "<code>/edit 번호 새설명 | 예산</code> — 작성자·관리자 (<code>|</code> 없으면 설명만 변경)\n"
            "<code>/delete 번호</code> — 작성자 또는 관리자가 삭제 (번호는 재사용 안 됨)\n\n"
            "<b>입찰(공개 요청·투찰)</b>\n"
            "<code>/tender_add 본문</code> — <code>config.json</code> 관리자만\n"
            "<code>/tenders</code> — 공개 목록(공고별 투찰 요약·표 수)\n"
            "<code>/tender_view 번호</code> — 요청·전체 투찰(<b>투찰별</b> 👍/👎)\n"
            "<code>/tender_bid 번호 팀설명 | 견적</code> — 누구나 (첫 <code>|</code> 뒤가 견적)\n"
            "<code>/tender_close 번호</code> — 관리자 마감\n\n"
            "<b>언어 전환</b> <i>(첫 사용 시 기본: English)</i>\n"
            "<code>/lang cn</code> — 中文\n"
            "<code>/lang en</code> — English\n"
            "<code>/lang ko</code> — 한국어 (ISO 639-1)\n"
        ),
        "publish_need_desc": (
            "<b>프로젝트 설명</b>을 입력하세요. 첫 <code>|</code> 뒤에 예산(선택).\n"
            "예: <code>/publish 가계부 앱 | 500만원</code>\n"
            "또: <code>/publish 설명만</code>"
        ),
        "publish_ok": (
            "✅ 프로젝트 <b>#{pid}</b> 를 등록했습니다.\n\n"
            "<code>/projects</code> 로 목록을 보고 <code>/vote {pid}</code> 로 투표하세요.\n"
            "언제든 <code>/edit {pid} …</code> 또는 <code>/delete {pid}</code> 가능합니다."
        ),
        "projects_empty": (
            "📭 아직 프로젝트가 없습니다.\n"
            "<code>/publish 설명 | 예산</code> 으로 추가 (예산 생략 가능)."
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
        "budget_label": "예산",
        "budget_not_set": "<i>(없음)</i>",
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
        "delete_usage": "사용법: <code>/delete 번호</code> — 작성자 또는 <code>config.json</code> 관리자만 삭제 가능.",
        "delete_bad_id": "번호가 올바르지 않습니다. 예: <code>/delete 3</code>",
        "delete_no_such": "프로젝트 <b>#{pid}</b> 가 없습니다. <code>/projects</code> 를 확인하세요.",
        "delete_not_pub": "<b>작성자</b> 또는 <b>봇 관리자</b>(config.json)만 이 프로젝트를 삭제할 수 있습니다.",
        "delete_ok": (
            "🗑 프로젝트 <b>#{pid}</b> 를 삭제했습니다. 이후 새 글은 다음 번호를 씁니다."
        ),
        "edit_usage": (
            "사용법 (작성자 또는 config.json 관리자):\n"
            "<code>/edit 번호 새 설명</code> — 설명만, 예산 유지\n"
            "<code>/edit 번호 설명 | 예산</code> — 둘 다; <code>|</code> 뒤 비우면 예산 삭제"
        ),
        "edit_bad_id": "번호가 올바르지 않습니다. 예: <code>/edit 3 새 글</code>",
        "edit_empty": "새 설명은 비울 수 없습니다.",
        "edit_no_such": "프로젝트 <b>#{pid}</b> 가 없습니다. <code>/projects</code> 를 확인하세요.",
        "edit_not_pub": "<b>작성자</b> 또는 <b>봇 관리자</b>(config.json)만 이 프로젝트를 수정할 수 있습니다.",
        "edit_ok": "✏️ 프로젝트 <b>#{pid}</b> 를 수정했습니다.",
        "hint_no_project": "프로젝트를 찾을 수 없습니다.",
        "hint_up_off": "찬성을 취소했습니다.",
        "hint_up_on": "찬성했습니다.",
        "hint_down_off": "반대를 취소했습니다.",
        "hint_down_on": "반대했습니다.",
        "callback_invalid": "잘못된 동작입니다.",
        "id_private_only": "이 명령은 <b>개인 채팅</b>에서만 사용할 수 있습니다. 봇과의 DM에서 <code>/id</code> 를 보내세요.",
        "id_reply": "Telegram 사용자 ID: <code>{uid}</code>\n사용자명: {uname}",
        "id_no_username": "(없음)",
        "lang_usage": (
            "사용법: <code>/lang cn</code>, <code>/lang en</code>, <code>/lang ko</code>\n"
            "현재 언어: <b>{name}</b>"
        ),
        "lang_set": "화면 언어: <b>{name}</b>",
        "lang_bad": "지원하지 않는 언어입니다. <code>cn</code>, <code>en</code>, <code>ko</code>(ISO 639-1)를 사용하세요.",
        "tender_list_empty": "📭 입찰 공고가 없습니다. 관리자: <code>/tender_add …</code>",
        "tender_list_title": "📑 <b>입찰 목록</b> (공개)\n",
        "tender_list_continued": "📑 <b>입찰 목록</b> <i>(계속)</i>\n",
        "tender_list_footer": "\n💡 <code>/tender_view 번호</code> 로 상세(투찰별 👍/👎).",
        "tender_list_bids_none": "투찰 없음",
        "tender_list_bid_line": (
            "  └ <b>투찰 #{bid_id}</b> {team} · <i>{quote}</i>\n"
            "    {up_l} <b>{up_n}</b> · {dn_l} <b>{dn_n}</b>\n"
        ),
        "tender_list_bids_more": (
            "  <i>…투찰 <b>{n}</b>건 더 — <code>/tender_view {tid}</code></i>\n"
        ),
        "tender_bid_vote_footer": (
            "\n💡 각 <b>투찰</b> 아래 👍/👎 (다시 누르면 취소, 프로젝트 투표와 동일)."
        ),
        "tender_bid_id_btn_hint": "투찰 번호입니다. 오른쪽 👍 / 👎 를 누르세요.",
        "tender_bids_count": "건 투찰",
        "tender_no_text": "(내용 없음)",
        "tender_status_open": "접수중",
        "tender_status_closed": "마감",
        "tender_view_header": "📑 <b>입찰 #{tid}</b> · {status}\n\n",
        "tender_label_requirement": "요청",
        "tender_label_bids": "투찰",
        "tender_no_bids_yet": "<i>아직 투찰이 없습니다.</i>\n",
        "tender_bid_block": (
            "<b>투찰 #{bid_id}</b>\n"
            "<b>팀:</b> {team}\n<b>견적:</b> {quote}\n<b>투찰자:</b> {bidder}\n"
            "{up_l}: <b>{up_n}</b> · {dn_l}: <b>{dn_n}</b>\n"
            "— — —\n"
        ),
        "tender_view_footer": "",
        "tender_view_cont": "\n<i>(다음 메시지 계속)</i>\n",
        "tender_view_continued": "📑 <b>입찰 #{tid}</b> · <i>투찰(계속)</i>\n\n",
        "tender_add_need_admin": "<code>config.json</code>의 <b>봇 관리자</b>만 공고를 올릴 수 있습니다.",
        "tender_add_usage": "사용법(관리자): <code>/tender_add 요청 본문</code>",
        "tender_add_ok": (
            "✅ 입찰 공고 <b>#{tid}</b> 를 등록했습니다.\n"
            "목록: <code>/tenders</code> · 투찰: <code>/tender_bid {tid} 팀설명 | 견적</code>"
        ),
        "tender_view_not_found": "입찰 <b>#{tid}</b> 가 없습니다. <code>/tenders</code> 로 번호 확인.",
        "tender_view_bad_id": "번호가 올바르지 않습니다. 예: <code>/tender_view 3</code>",
        "tender_bid_usage": (
            "사용법: <code>/tender_bid 번호 팀설명 | 견적</code>\n"
            "첫 <code>|</code> 뒤가 견적입니다."
        ),
        "tender_bid_bad_id": "번호가 올바르지 않습니다. 예: <code>/tender_bid 3 팀A | 100만원</code>",
        "tender_bid_need_pipe": "팀 설명과 견적은 첫 <code>|</code> 로 구분하세요.",
        "tender_bid_empty_team": "팀 설명은 비울 수 없습니다.",
        "tender_bid_empty_quote": "견적은 비울 수 없습니다(「협의」 등 입력).",
        "tender_bid_tender_missing": "입찰 <b>#{tid}</b> 가 없습니다.",
        "tender_bid_tender_closed": "입찰 <b>#{tid}</b> 는 마감되어 투찰할 수 없습니다.",
        "tender_bid_ok": "✅ 투찰 <b>#{bid_id}</b> 등록(입찰 #{tid}). <code>/tender_view {tid}</code>",
        "tender_close_usage": "사용법(관리자): <code>/tender_close 번호</code>",
        "tender_close_bad_id": "번호가 올바르지 않습니다. 예: <code>/tender_close 3</code>",
        "tender_close_not_found": "입찰 <b>#{tid}</b> 가 없습니다.",
        "tender_close_need_admin": "<b>관리자</b>만 마감할 수 있습니다.",
        "tender_close_ok": "✅ 입찰 <b>#{tid}</b> 를 마감했습니다(조회 가능).",
        "tender_close_already": "입찰 <b>#{tid}</b> 는 이미 마감 상태입니다.",
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


def tender_panel_footer_html(locale: str, part: int, total: int) -> str:
    lines = ["\n", t(locale, "tender_list_footer")]
    if total > 1:
        lines.append(t(locale, "part_footer", part=part, total=total))
    lines.append("\n")
    return "".join(lines)


def tender_panel_footer_max_len() -> int:
    return max(len(tender_panel_footer_html(loc, 99, 99)) for loc in LOCALES)
