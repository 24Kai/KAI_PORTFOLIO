"""Readable public portfolio stories and isolated, synthetic explanations."""
from html import escape
import streamlit as st

from casebook import case_url, case_markdown, full_casebook, delivery_preview, credited_totals

CASE_PAGE = '3～5 分鐘看作品'

STYLE = '''<style>
.case-intro{font-size:1.05rem;color:#c6d9e8;line-height:1.85;max-width:920px}
.case-meta{display:flex;gap:.55rem;flex-wrap:wrap;margin:.8rem 0 1.4rem}
.case-meta span{background:#152b36;border:1px solid #335764;padding:.35rem .7rem;border-radius:7px;color:#adede1;font-size:.8rem}
.project-card .case-link{display:block;color:#9cf8e8;margin-top:1.3rem;text-decoration:none;font-weight:650;line-height:1.6}
.case-link:hover{text-decoration:underline}
.case-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.65rem;margin:1.3rem 0}
.case-flow .flow-step{background:#122a37;border:1px solid #37606c;border-radius:12px;padding:1rem;min-width:0;line-height:1.65;color:#e0eef5;overflow-wrap:anywhere}
.flow-step small{display:block;color:#72dace;margin-bottom:.4rem}
.chapter{margin:2rem 0 .8rem;display:flex;align-items:baseline;gap:.7rem;flex-wrap:wrap}
.chapter > span{font-size:.8rem;color:#64d7c4;font-variant-numeric:tabular-nums}
.chapter h2{font-size:1.45rem;line-height:1.6;margin:0;padding:0;color:#eef7fc}
.outcome-box{padding:1.2rem 1.4rem;border:1px solid #376258;background:#112c2b;border-radius:12px;color:#d0eee5;line-height:1.9;margin:1rem 0}
.status-box{padding:1rem 1.3rem;border-left:3px solid #e8bc65;background:#26261f;color:#e2d6b8;line-height:1.85;margin:1rem 0}
.route-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.85rem;margin:1rem 0 1.6rem}
.route-card{padding:1.25rem;background:#112c34;border:1px solid #315b64;border-radius:14px;color:#e7f6fa;text-decoration:none;line-height:1.7;min-width:0}
.route-card small{display:block;color:#89baC7;margin-top:.5rem}
[data-testid="stMarkdownContainer"] a.route-card{color:#e7f6fa;text-decoration:none}
[data-testid="stMarkdownContainer"] a.case-link{color:#9cf8e8;text-decoration:none}
a.route-card:focus-visible,a.case-link:focus-visible{outline:2px solid #87efd9;outline-offset:4px}
.route-card:hover{border-color:#6ad9c8}
.reading-nav{display:flex;flex-wrap:wrap;gap:.5rem;color:#93b0c6;line-height:1.8;margin:1rem 0 1.4rem;font-size:.85rem}
.reading-nav span{background:#152234;border-radius:6px;padding:.25rem .7rem}
@media(max-width:1100px){.case-flow{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.case-flow{grid-template-columns:repeat(2,minmax(0,1fr))}.route-grid{grid-template-columns:1fr}.chapter h2{font-size:1.2rem}}
</style>'''


def html(value):
    st.markdown(value, unsafe_allow_html=True)


def sync_route(content):
    ids = {p['id'] for p in content['projects']}
    previous = st.session_state.get('case')
    if isinstance(previous, dict):
        st.session_state['case'] = previous.get('id', 'n8n')
    requested = st.query_params.get('case')
    if requested in ids and requested != st.session_state.get('_case_route'):
        st.session_state['page'] = CASE_PAGE
        st.session_state['case'] = requested
    st.session_state['_case_route'] = requested


def nav_changed():
    if st.session_state['page'] != CASE_PAGE:
        st.query_params.pop('case', None)
        st.session_state['_case_route'] = None
    else:
        selected = st.session_state.get('case', 'n8n')
        st.query_params['case'] = selected
        st.session_state['_case_route'] = selected


def case_changed():
    selected = st.session_state['case']
    st.query_params['case'] = selected
    st.session_state['_case_route'] = selected


def goto_demo(name):
    st.session_state['page'] = '互動體驗'
    st.session_state['demo_mode'] = name
    st.query_params.pop('case', None)
    st.session_state['_case_route'] = None


def overview(content):
    html(STYLE)
    st.subheader('先選一個你想了解的方向')
    html('<div class="route-grid">'+''.join(
        f'<a class="route-card" href="?case={identifier}" target="_self"><strong>{escape(title)}</strong><small>{escape(copy)}</small></a>'
        for identifier,title,copy in [('production','現場的人怎麼用','看派工、掃碼、收工怎麼接在一起'),('n8n','系統為什麼要串','看排程如何帶動程式與結果回報'),('bi','數字為什麼可信','看超產為什麼不能抵銷另一張欠單')])+'</div>')
    st.subheader(f'{len(content["projects"])} 個作品，各有一個要解決的問題')
    st.caption('每篇都有 3～5 分鐘導覽、串接圖、情境解說與實作界線。可直接分享單一作品連結。')
    category = st.selectbox('依領域找作品', ['全部']+list(dict.fromkeys(p['category'] for p in content['projects'])), key='case_category')
    selected = [p for p in content['projects'] if category == '全部' or p['category'] == category]
    cards = []
    for p in selected:
        tags = ''.join(f'<span>{escape(tag)}</span>' for tag in p['technology'])
        cards.append(f'<article class="project-card"><div class="project-meta"><span>{escape(p["category"])}</span><b>{p["number"]}</b></div>'
                     f'<h3>{escape(p["title"])}</h3><p>{escape(p["summary"])}</p>'
                     f'<div class="case-meta"><span>{escape(p["status"])}</span><span>3～5 分鐘</span></div>'
                     f'<div class="tech">{tags}</div><a class="case-link" href="?case={p["id"]}" target="_self">看這個作品 →</a></article>')
    html('<div class="project-grid">'+''.join(cards)+'</div>')
    st.download_button('下載完整作品集文字版', full_casebook(content), 'KAI_CASEBOOK.md', 'text/markdown', key='download_casebook')


def chapter(time, title):
    html(f'<div class="chapter"><span>{time}</span><h2>{escape(title)}</h2></div>')


def detail(content):
    html(STYLE)
    by_id = {p['id']: p for p in content['projects']}
    if st.session_state.get('case') not in by_id:
        st.session_state['case'] = 'n8n'
    selected = st.selectbox('選擇作品', list(by_id), format_func=lambda identifier: by_id[identifier]['title'], key='case', on_change=case_changed)
    p = by_id[selected]
    st.title(p['title'], anchor=False)
    html(f'<p class="case-intro">{escape(p["summary"])}</p><div class="case-meta"><span>{escape(p["category"])}</span><span>{escape(p["status"])}</span><span>導覽約 3～5 分鐘</span></div>')
    st.caption('適合：'+p['audience'])
    html('<div class="reading-nav">'+''.join(f'<span>{label}</span>' for label in ['理解問題','原本與後來','串接理由','換個情境','成果與界線'])+'</div>')
    chapter('0:00', '先理解，為什麼值得做')
    st.write(p['problem'])
    chapter('0:30', '原來怎麼做，後來怎麼做')
    html(f'<div class="detail-grid"><div class="detail-panel"><b>原本的情境</b>{escape(p["before"])}</div><div class="detail-panel"><b>設計後的做法</b>{escape(p["after"])}</div></div>')
    st.markdown('**我負責的設計**')
    st.write(p['role'])
    chapter('1:15', '為什麼需要串接這些系統')
    html('<div class="case-flow">'+''.join(f'<div class="flow-step"><small>{i:02} →</small>{escape(name)}</div>' for i,name in enumerate(p['flow'],1))+'</div>')
    for connection in p['connections']:
        st.markdown('- '+connection)
    if selected == 'n8n':
        st.caption('這是系統分工圖。既有週報由 n8n 排程與啟動，報表內部步驟在 Python 執行。')
    chapter('2:15', '換一個情境，看看結果')
    st.caption('互動解說使用合成情境；所有操作只在這個展示中發生。')
    if selected in {'n8n','weekly'}:
        failure = st.radio('假設流程在哪一步遇到問題？', ['無','來源檢核','寄送'], horizontal=True, key='failure_'+selected)
        rows = delivery_preview(failure)
        st.dataframe(rows, hide_index=True, width='stretch')
        if failure == '來源檢核':
            st.warning('來源檢核失敗：整理報表、確認附件與寄送都不執行。')
        elif failure == '寄送':
            st.warning('報表已準備好，但寄送失敗；不能把「產生檔案」當成「已送達」。')
        else:
            st.success('示範：各階段都通過，整個流程才可標成完成。')
        st.caption('這是執行邏輯示範，不會觸發真正的 n8n、SAP 或郵件。')
    elif selected == 'bi':
        a = st.slider('合成訂單 A 完成量（計畫 10）', 0, 20, 15, key='bi_a')
        b = st.slider('合成訂單 B 完成量（計畫 10）', 0, 20, 5, key='bi_b')
        totals = credited_totals([(10,a),(10,b)])
        st.dataframe([{'計畫':20,'實際產出':totals['actual'],'可認列完成':totals['credited'],'尚欠':totals['remaining'],'超產':totals['excess'],'達成率':f'{totals["credited"]/20:.0%}'}],hide_index=True,width='stretch')
        st.info('先算每筆訂單，再合計：A 的超產不能抵銷 B 的欠數。')
    choice = st.radio('再看一個現場情境', list(range(len(p['scenarios']))), format_func=lambda i:p['scenarios'][i][0], key='scenario_'+selected)
    html('<div class="outcome-box">'+escape(p['scenarios'][choice][1])+'</div>')
    if p.get('demo'):
        st.button('親手操作：'+p['demo'], type='primary', on_click=goto_demo,args=(p['demo'],),key='try_'+selected)
    chapter('3:00', '我做了哪些取捨')
    for decision in p['decisions']:
        st.markdown('- '+decision)
    chapter('4:00', '最後解決什麼，做到哪裡')
    for outcome in p['outcomes']:
        st.markdown('- '+outcome)
    st.markdown('**實作依據**')
    st.write(p['evidence'])
    html('<div class="status-box"><strong>目前界線</strong><br>'+escape(p['limitation'])+'</div>')
    st.caption('上述成果描述已具備的行為；未提供未量測的節省工時、金額或效益百分比。')
    with st.expander('面試時，我會這樣介紹'):
        st.write(p['problem']+' '+p['role']+' '+p['after'])
        st.write('最後，'+'；'.join(p['outcomes']))
        st.caption(p['limitation'])
    st.markdown('**分享這一個作品**')
    st.code(case_url(selected), language=None)
    st.download_button('下載這個作品的介紹', case_markdown(p), f'KAI_{selected}.md','text/markdown', key='download_'+selected)
