"""KAI public portfolio; all interactive data lives in each visitor's session."""
import json
from html import escape
from pathlib import Path
from uuid import uuid4

import streamlit as st
import casebook_ui

from demo_logic import (Counter, MINUS_QR, PLUS_QR, metrics, now_taipei,
                        progress_palette, sample_orders, validate_report_columns)

ROOT = Path(__file__).resolve().parent
CONTENT = json.loads((ROOT / "portfolio_content.json").read_text(encoding="utf-8-sig"))

st.set_page_config(page_title="KAI | 流程・資料・自動化", page_icon="◈", layout="wide")

CSS = """
<style>
* {box-sizing:border-box}
.stApp {background:#0b111b}
.stMainBlockContainer {max-width:1440px;padding:3.5rem 2.4rem 3rem}
[data-testid="stHeader"] {background:#0b111be8}
[data-testid="stToolbar"] {right:.7rem}
.brand {display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.6rem;color:#a8bbcf;font-size:.8rem;letter-spacing:.09em;flex-wrap:wrap}
.brand strong {font-size:1.15rem;color:#eef6fc;letter-spacing:.18em}
.hero {background:linear-gradient(112deg,#13263c,#133c51 62%,#155854);border:1px solid #2b5464;border-radius:24px;padding:clamp(1.5rem,4vw,3.5rem);margin-bottom:1.6rem}
.eyebrow {color:#78e7d6;font-size:.76rem;letter-spacing:.18em;font-weight:700;margin:0 0 1.2rem}
.hero h1 {text-wrap:balance;font-size:clamp(2rem,3.7vw,3.35rem);line-height:1.45;max-width:950px;color:#fff;letter-spacing:.01em;margin:0 0 1.1rem;overflow-wrap:anywhere}
.hero p {color:#cad9e6;max-width:780px;line-height:1.85;margin:0;font-size:1.03rem}
.chips {display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.4rem}
.chip {border:1px solid #487078;border-radius:999px;padding:.28rem .8rem;color:#d2f8f1;font-size:.8rem}
.section-label {color:#6ee5d1;font-size:.74rem;letter-spacing:.13em;font-weight:700;margin:1.7rem 0 .6rem}
.section-title {font-size:1.6rem;font-weight:700;line-height:1.5;margin:0 0 .65rem;color:#f0f5fa}
.section-copy {color:#a6b9cc;line-height:1.8;margin:0 0 1.2rem}
.project-grid,.principle-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-auto-rows:1fr;gap:1.05rem;margin:1.2rem 0 1.7rem}
.project-card {border:1px solid #2a3b4e;border-radius:19px;background:linear-gradient(140deg,#152233,#101b29);padding:1.65rem;display:flex;flex-direction:column;min-width:0}
.project-meta {display:flex;justify-content:space-between;gap:.7rem;color:#83a0b8;font-size:.78rem;margin-bottom:1.15rem}
.project-meta b {color:#6de4d1;font-size:1.15rem;font-weight:500}
.project-card h3 {font-size:1.3rem;line-height:1.5;color:#eef4fa;margin:0 0 .7rem;overflow-wrap:anywhere}
.project-card p {color:#a9bfd1;line-height:1.8;margin:0 0 1.2rem}
.tech {display:flex;gap:.45rem;flex-wrap:wrap;margin-top:auto}
.tech span {background:#1b2e40;border:1px solid #2c4358;border-radius:6px;color:#b6cddd;padding:.18rem .5rem;font-size:.7rem}
.detail-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.1rem;margin:.7rem 0 1.2rem}
.detail-panel {border-left:2px solid #53caba;padding:.25rem 1.2rem;color:#b4c5d6;line-height:1.8;min-width:0}
.detail-panel b {display:block;color:#edf6fb;margin-bottom:.4rem}
.demo-note {border:1px solid #27545a;background:#112a32;color:#b1e9df;border-radius:12px;padding:.85rem 1.1rem;line-height:1.65;margin:1rem 0}
.demo-banner {display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;background:linear-gradient(110deg,#152a43,#155855);border-radius:17px;padding:1.4rem 1.6rem;margin:1rem 0}
.demo-banner h3 {margin:0;line-height:1.6;color:#fff;font-size:1.35rem}
.demo-time {color:#c5ebe8;text-align:right;font-variant-numeric:tabular-nums;font-size:.92rem;line-height:1.6}
.kpi-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-auto-rows:1fr;gap:.8rem;margin:1rem 0 1.5rem;align-items:stretch}
.kpi {border:1px solid #304152;border-radius:15px;background:#151f2d;padding:1.15rem;min-width:0;display:flex;flex-direction:column;justify-content:space-between;gap:1rem;container-type:inline-size}
.kpi-label {font-size:1rem;color:#b8cbdd;font-weight:600;line-height:1.6;overflow-wrap:anywhere}
.kpi-value {font-size:clamp(1.35rem,13cqi,3.3rem);font-weight:750;color:#fff;line-height:1.3;font-variant-numeric:tabular-nums;letter-spacing:-.02em;overflow-wrap:anywhere}
.track {height:8px;background:#30303e;border-radius:99px;margin-top:.5rem}
.fill {height:100%;border-radius:99px}
.kpi-spacer {height:8px;margin-top:.5rem}

.order-table-wrap {overflow-x:auto;border:1px solid #2c3b4c;border-radius:13px;margin:1rem 0}
.order-table {width:100%;border-collapse:collapse;min-width:830px;font-size:.85rem}
.order-table th {background:#1b2939;color:#b4c8da;font-weight:500;text-align:left;padding:.85rem .7rem;white-space:nowrap}
.order-table td {padding:.9rem .7rem;border-top:1px solid #293848;color:#e6f0f6;white-space:nowrap}
.order-table tr.current td {background:#133338}
.order-table th:first-child,.order-table td:first-child {width:44px;text-align:center;padding-left:.4rem;padding-right:.4rem}
.order-rate {display:flex;align-items:center;gap:.5rem;width:150px}
.order-rate .track {flex:1;margin:0;min-width:70px}
.order-rate span {min-width:3.2rem;text-align:right;font-variant-numeric:tabular-nums}
.status-dot {display:inline-block;width:13px;height:13px;border-radius:50%;box-shadow:0 0 9px #ffffff12}
.principle {background:#121e2c;border:1px solid #283d50;border-radius:15px;padding:1.4rem;min-width:0}
.principle b {font-size:1.1rem;color:#e2f1f8;display:block;margin-bottom:.6rem}
.principle p {color:#abc0d2;line-height:1.8;margin:0}
.footer {border-top:1px solid #26394b;margin-top:2.5rem;padding-top:1.3rem;display:flex;justify-content:space-between;gap:.9rem;flex-wrap:wrap;font-size:.78rem;color:#8199af;line-height:1.8}
.footer a {color:#81ded0;text-decoration:none}
[data-testid="stBaseButton-primary"] {color:#082c29;font-weight:700}
@media(max-width:1100px){.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.stMainBlockContainer{padding-left:1.6rem;padding-right:1.6rem}}
@media(max-width:640px){.stMainBlockContainer{padding:3.5rem 1rem 2rem}.project-grid,.principle-grid,.detail-grid{grid-template-columns:1fr}.hero{border-radius:18px}.project-card{padding:1.25rem}.kpi{padding:.9rem}.kpi-value{font-size:clamp(1.2rem,14cqi,2.5rem)}.demo-time{text-align:left}}
@media(prefers-reduced-motion:no-preference){.project-card{transition:border-color .2s}.project-card:hover{border-color:#4d999b}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def html(value):
    st.markdown(value, unsafe_allow_html=True)


def section(eyebrow, title, text=""):
    html(f'<div class="section-label">{escape(eyebrow)}</div><div class="section-title">{escape(title)}</div>'
         f'<p class="section-copy">{escape(text)}</p>')


def show_metrics(target, completed):
    values = metrics(target, completed)
    start, end, label = progress_palette(values["rate"])
    cards = []
    for name, text in (("今日派工", f"{target:,}"), ("完成數量", f"{completed:,}"),
                       ("達成率", f'{values["rate"]:.1f}%'), ("尚欠", f'{values["remaining"]:,}')):
        bar = (f'<div class="track" role="progressbar" aria-label="達成率：{values["rate"]:.1f}%，{label}" '
               f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{min(values["rate"],100):.1f}">'
               f'<div class="fill" style="width:{min(values["rate"],100):.2f}%;background:linear-gradient(90deg,{start},{end})"></div></div>') if name == "達成率" else '<div class="kpi-spacer"></div>'
        cards.append(f'<div class="kpi"><div class="kpi-label">{name}</div><div class="kpi-value">{text}</div>{bar}</div>')
    html('<div class="kpi-grid">' + ''.join(cards) + '</div>')


def banner(title):
    now = now_taipei()
    html(f'<div class="demo-banner"><h3>{escape(title)}</h3><div class="demo-time">'
         f'{now:%Y/%m/%d}<br>{now:%H:%M:%S} · 台北時間</div></div>')


def overview():
    casebook_ui.overview(CONTENT)


def counter_action(token):
    st.session_state.counter = st.session_state.counter.scan(token, uuid4().hex)
    st.session_state.counter_notice = "已完成 +1" if token == PLUS_QR else "已撤銷；完成量最低為 0"


def counter_target_changed():
    st.session_state.counter = st.session_state.counter.set_target(st.session_state.counter_target)


def counter_demo():
    if "counter" not in st.session_state:
        st.session_state.counter = Counter()
    st.number_input("今日目標", min_value=1, max_value=999999999, value=st.session_state.counter.target, step=1,
                    key="counter_target", on_change=counter_target_changed)
    st.caption("修改目標會保留已完成數量。這個簡易模式達標後仍可繼續記錄實際產量。")
    left, right = st.columns(2)
    left.button("模擬完成 QR · +1", type="primary", width="stretch",
                key="counter_plus", on_click=counter_action, args=(PLUS_QR,))
    right.button("模擬撤銷 QR · −1", width="stretch",
                 key="counter_minus", on_click=counter_action, args=(MINUS_QR,))
    counter = st.session_state.counter
    banner("產線簡易計數 · DEMO")
    show_metrics(counter.target, counter.completed)
    if st.session_state.get("counter_notice"):
        st.success(st.session_state.counter_notice)
    with st.expander("看看事件如何計數"):
        st.write("同一張 QR 可以一直掃；不同掃描事件都會計數。同一事件若因傳輸重送，則只會處理一次。")
        st.code(f"完成：{PLUS_QR}\n撤銷：{MINUS_QR}", language=None)
        st.caption("這兩個代碼僅供公開示範，與現場正式程式的條碼分開。")
    record = {"data_kind": "synthetic_demo", "date": now_taipei().date().isoformat(),
              **metrics(counter.target, counter.completed)}
    st.download_button("下載本次示範紀錄", json.dumps(record, ensure_ascii=False, indent=2),
                       "kai_counter_demo.json", "application/json")


def order_action(undo=False):
    orders = st.session_state.orders
    index = st.session_state.order_index
    try:
        order = orders[index]
        orders[index] = order.undo() if undo else order.scan(st.session_state.order_barcode)
        st.session_state.order_notice = ("success", "已撤銷最後一張示範條碼。" if undo else
                                         f"條碼已記錄：已完成 {orders[index].completed} 台，本台待續 {orders[index].pending}/{order.required} 張。")
    except ValueError as exc:
        st.session_state.order_notice = ("warning", str(exc))


def order_demo():
    if "orders" not in st.session_state:
        st.session_state.orders = sample_orders()
    orders = st.session_state.orders
    st.selectbox("目前工單", list(range(len(orders))), key="order_index",
                 format_func=lambda i: f"{orders[i].order_id} · {orders[i].model}")
    order = orders[st.session_state.order_index]
    st.caption(f"訂單 {order.quantity} − 已交貨 {order.delivered} ＝ 今日派工 {order.target}；每台需要 {order.required} 張條碼。")
    st.text_input("示範條碼內容", value="DEMO-BARCODE-A", max_chars=120, key="order_barcode")
    left, right = st.columns(2)
    left.button("模擬掃一張條碼", type="primary", width="stretch",
                key="order_scan", on_click=order_action)
    right.button("撤銷最後一張", width="stretch", key="order_undo", on_click=order_action, args=(True,),
                 disabled=not order.barcodes)
    banner(f"產線生產看板 · {order.model}")
    show_metrics(sum(p.target for p in orders), sum(p.completed for p in orders))
    if "order_notice" in st.session_state:
        kind, message = st.session_state.order_notice
        getattr(st, kind)(message)
    rows = []
    for p in sorted(orders, key=lambda item: item.order_id != order.order_id):
        rate = metrics(p.target, p.completed)["rate"]
        start, end, status = progress_palette(rate)
        lamp = f'<span class="status-dot" role="img" aria-label="{status}" title="{status}" style="background:linear-gradient(135deg,{end},{start})"></span>'
        bar = f'<div class="order-rate"><div class="track"><div class="fill" style="width:{min(rate,100):.2f}%;background:linear-gradient(90deg,{start},{end})"></div></div><span>{rate:.1f}%</span></div>'
        cells = [lamp, bar, escape(p.order_id), escape(p.sales_order), escape(p.item),
                 str(p.target), str(p.completed), f"本台 {p.pending}/{p.required} 張"]
        current_class = ' class="current"' if p.order_id == order.order_id else ''
        rows.append(f'<tr{current_class}>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
    headings = ''.join(f'<th scope="col">{name}</th>' for name in ["狀態", "達成率", "工單", "訂單", "項次", "今日派工", "完成數量", "條碼進度"])
    html('<div class="order-table-wrap"><table class="order-table"><thead><tr>' + headings + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
    st.caption("可重複送出相同條碼內容；掃齊一組才完成一台。工單達標後會阻擋新增，撤銷後可以補掃。")
    with st.expander("檢視目前工單的示範條碼"):
        st.write(list(order.barcodes) or "尚未掃描")


def report_demo():
    section("VALIDATE BEFORE UPDATE", "來源變了，先找出缺少什麼", "示範資料先經欄位檢核，通過後才提供下載。")
    changed = st.toggle("模擬來源漏掉「完成數量」欄", key="invalid_schema")
    columns = ["訂單", "項次", "預排數量"] + ([] if changed else ["完成數量"])
    row = {"訂單": "DEMO-SO-A", "項次": "000010", "預排數量": 20}
    if not changed:
        row["完成數量"] = 14
    st.dataframe([row], hide_index=True, width="stretch")
    missing = validate_report_columns(columns)
    if missing:
        st.error("檢核未通過：缺少「" + "、".join(missing) + "」。後續輸出已停止。")
    else:
        st.success("欄位檢核通過，可以輸出這筆示範資料。")
    st.download_button("下載檢核後的示範資料", json.dumps(row, ensure_ascii=False, indent=2),
                       "kai_report_demo.json", "application/json", disabled=bool(missing))
    st.caption("這是簡化機制展示；沒有 SAP 連線、資料庫更新或自動寄送。")


def demos():
    section("INTERACTIVE DEMO", "親手試一次，就能理解設計", "選一個情境，觀察操作如何改變結果。")
    html('<div class="demo-note">所有訂單、產品與數量均為合成示範資料。操作只保留於你的本次瀏覽工作階段，重新連線可能重置。</div>')
    mode = st.radio("選擇互動情境", ("QR 簡易計數", "工單派工看板", "報表資料檢核"), horizontal=True, key="demo_mode")
    if mode == "QR 簡易計數":
        counter_demo()
    elif mode == "工單派工看板":
        order_demo()
    else:
        report_demo()


def methods():
    section("HOW I BUILD", "工具背後，是處理問題的方式", "把需求、資料、程式與驗證接在一起，讓每一次調整都有清楚的理由。")
    cards = ''.join(f'<div class="principle"><b>{escape(p["title"])}</b><p>{escape(p["text"])}</p></div>'
                    for p in CONTENT["principles"])
    html('<div class="principle-grid">' + cards + '</div>')
    st.markdown("**一次改動的工作路徑**")
    st.markdown("釐清現場需求 → 確认現行行為 → 定義資料口徑 → 隔離實作與測試 → 記錄結果 → 現場驗收")
    st.markdown("**AI 在協作中的位置**")
    st.write("用 AI 協助整理需求、閱讀程式、比較方案與建立測試；保留來源及決策紀錄，並以實際程式行為和操作結果確認是否完成。")


casebook_ui.sync_route(CONTENT)
profile = CONTENT["profile"]
html(f'<div class="brand"><strong>{escape(profile["name"])} / PORTFOLIO</strong><span>流程・資料・自動化</span></div>')
if st.session_state.get("page", "作品總覽") != casebook_ui.CASE_PAGE:
    html(f'<div class="hero"><div class="eyebrow">{escape(profile["eyebrow"])}</div><h1>{escape(profile["headline"])}</h1>'
         f'<p>{escape(profile["intro"])}</p><div class="chips">' + ''.join(f'<span class="chip">{escape(tag)}</span>' for tag in profile["focus"]) + '</div></div>')
page = st.radio("作品集導覽", ("作品總覽", casebook_ui.CASE_PAGE, "互動體驗", "設計方法"), horizontal=True, key="page", label_visibility="collapsed", on_change=casebook_ui.nav_changed)
if page == casebook_ui.CASE_PAGE:
    casebook_ui.detail(CONTENT)
else:
    {"作品總覽": overview, "互動體驗": demos, "設計方法": methods}[page]()
github_url = profile.get("github_url", "")
link = f'<a href="{escape(github_url, quote=True)}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>' if github_url.startswith("https://github.com/") else ""
html(f'<div class="footer"><span>KAI · 流程、資料與自動化作品集<br>互動展示使用合成資料</span>{link}</div>')
