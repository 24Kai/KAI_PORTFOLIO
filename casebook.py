"""Public case-study export and synthetic calculations; no external services."""
from urllib.parse import urlencode

PUBLIC_URL = 'https://krtqdtupujerpksubdpac2.streamlit.app/'


def case_url(identifier):
    return PUBLIC_URL + '?' + urlencode({'case': identifier})


def delivery_preview(failure='無'):
    """Explain stop-on-failure, never execute a workflow or send a message."""
    stages = ['到時啟動', '來源檢核', '整理報表', '確認附件', '寄送']
    failed = False
    result = []
    for stage in stages:
        state = '未執行' if failed else '通過'
        if not failed and stage == failure:
            state = '失敗'
            failed = True
        result.append({'步驟': stage, '示範結果': state})
    return result


def credited_totals(orders):
    """Credit each order before aggregating; excess cannot fill another order."""
    return {
        'planned': sum(plan for plan, actual in orders),
        'actual': sum(actual for plan, actual in orders),
        'credited': sum(min(plan, actual) for plan, actual in orders),
        'remaining': sum(max(plan-actual, 0) for plan, actual in orders),
        'excess': sum(max(actual-plan, 0) for plan, actual in orders),
    }


def case_markdown(project):
    p = project
    lines = [f'# {p["title"]}', '', p['summary'], '', f'閱讀與體驗：{p["reading_minutes"]}｜專案狀態：{p["status"]}',
             '', f'適合：{p["audience"]}', '', '## 0:00 — 先理解問題', '', p['problem'],
             '', '## 0:30 — 原來怎麼做，後來怎麼做', '', '**原本的情境**', '', p['before'],
             '', '**設計後的做法**', '', p['after'], '', '**我負責的設計**', '', p['role'],
             '', '## 1:15 — 為什麼需要串接', '', ' → '.join(p['flow']), '',
             *['- '+line for line in p['connections']], '',
             '## 2:15 — 換一個情境看看', '',
             '以下為合成情境解說，不會連線公司系統或執行正式作業。', '']
    for title, outcome in p['scenarios']:
        lines += [f'**{title}**', '', outcome, '']
    lines += ['## 3:00 — 關鍵取捨', '', *['- '+line for line in p['decisions']], '',
              '## 4:00 — 成果與界線', '', *['- '+line for line in p['outcomes']], '',
              '**實作依據**：'+p['evidence'], '', '**目前界線**：'+p['limitation'], '',
              '**技術**：'+'、'.join(p['technology']), '',
              '## 面試時，我會這樣介紹', '',
              p['problem']+' '+p['role']+' '+p['after']+' 最後，'+'；'.join(p['outcomes'])+' '+p['limitation'], '',
              f'[開啟此作品與互動]({case_url(p["id"])})', '']
    return '\n'.join(lines)


def full_casebook(content):
    return '# KAI｜流程、資料與自動化作品集\n\n每個作品以 3～5 分鐘的閱讀與體驗為目標。所有數字情境為合成資料；功能狀態依實作與留存驗證說明，不宣稱未量測的節省工時或營運效益。\n\n' + '\n\n---\n\n'.join(case_markdown(p) for p in content['projects'])
