# KAI 個人作品集

可獨立部署至 Streamlit Community Cloud 的繁體中文作品集。公開內容只有專案方法與合成示範資料，不讀取私人中控、SAP、公司資料庫或本機工作檔。

## 內容

- 作品總覽：產線生產看板、QR 簡易計數、SAP 報表自動化、AI 工作中控。
- 案例詳情：問題、做法、設計取捨與技術。
- 互動體驗：QR 加減計數、工單多碼計數、來源欄位檢核。
- 設計方法：需求、資料、驗證與紀錄的工作路徑。

公開示範只保留在各訪客的 Streamlit session。重新連線或伺服器重啟可能重置；示範不是正式生產系統，不具備 Windows 背景接收、現場匯入、正式歸檔與公司連線。

## 日後調整

一般文案編輯 `portfolio_content.json`：

- `profile`：姓名、介紹、標語、領域、GitHub 連結。
- `projects`：案例摘要、問題、做法、設計取捨、技術。
- `principles`：工作方法。

尚未確認的個人職稱、年資、公司、聯絡方式或成效數字不預填。請先確認內容可以公開，再補進作品集。私人資料不要放入此儲存庫，包含 Git 歷史。

## 執行

Python 3.11 以上：

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 部署

1. 將本目錄作為獨立 GitHub 儲存庫。
2. Streamlit Community Cloud 選擇該儲存庫、發布分支與 `app.py`。
3. Python 選擇 3.13；本 app 不需要 secrets 或外部資料庫。
4. 完成後檢查 Share 設定，作品集設為公開；私人中控另用私人應用程式。

修改文案後 commit / push，Cloud 依發布分支更新。可透過 GitHub 網頁編輯 JSON，不需要下載整個專案。

## 驗證

```sh
python -m unittest discover -s tests -v
```

測試涵蓋數量、同碼多事件、重送去重、多碼分組、上限、撤銷、來源欄位、時區與 Streamlit AppTest 操作。AppTest 不代表瀏覽器版面驗收。上線前仍須實際檢視 1920、1600、1366、1024 與手機寬度，以及放大文字時是否溢出。

數量與進度日期使用 Asia/Taipei（UTC+08:00）。示範只還原說明所需的核心行為，未直接搬入正式 SAP 或 Windows 程式。
