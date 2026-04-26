# Minimal AI OS：Thin Harness / Fat Skills / Memory / Wiki 測試版

這是一個最小可測版本，用來驗證：

1. **Thin Harness**：`ai_os.py` 只負責讀寫檔案、路由、搜尋與產出，不塞太多商業邏輯。
2. **Fat Skills**：SOP、判斷標準、工作方法放在 `skills/*.md`。
3. **Memory Policy**：長期可重用資訊放 `memory/memory.md`，避免每次把所有資料塞進上下文。
4. **LLM Wiki**：原文先進 `notes/raw/`，萃取後進 `wiki/sources/` 與 `wiki/concepts/`。
5. **Model-agnostic**：不綁 Claude Code、Codex、ChatGPT；任何 agent 都能讀這個資料夾工作。

---

## 目錄結構

```text
minimal_ai_os/
├── ai_os.py                 # 最小 harness
├── notes/raw/               # 原始資料，保留原文
├── wiki/sources/            # 每份原文的來源摘要
├── wiki/concepts/           # 概念頁
├── skills/                  # Fat skills：SOP / 評估框架 / 任務方法
├── memory/memory.md         # 長期記憶索引
├── artifacts/               # 對外輸出成果
└── logs/                    # 執行紀錄
```

---

## 快速測試

### 1. 進入資料夾

```bash
cd minimal_ai_os
```

### 2. 放一份原文到 `notes/raw/`

已附一份測試資料：

```text
notes/raw/sample_ai_os_note.md
```

### 3. 匯入資料

```bash
python3 ai_os.py ingest notes/raw/sample_ai_os_note.md
```

會產生：

- `wiki/sources/sample-ai-os-note.md`
- `wiki/concepts/*.md`
- 更新 `memory/memory.md`
- 更新 `logs/run.log`

### 4. 查詢知識庫

```bash
python3 ai_os.py ask "Thin harness 跟 Fat skills 差在哪？"
```

### 5. 跑一個 skill

```bash
python3 ai_os.py run-skill one_person_company_review "我要把 AI OS 用在一人公司的內容研究、自動化與決策紀錄"
```

---

## 設計原則

### 這版刻意不做的事

- 不接 API。
- 不做向量資料庫。
- 不做複雜 UI。
- 不做多 agent 編排。
- 不做自動寫入外部服務。

原因：第一版只驗證資料結構、流程邊界、技能規格與記憶策略。

### 可以接上的下一步

1. 把 `ask()` 換成 OpenAI / Claude / local LLM。
2. 把 `skills/*.md` 交給 Claude Code 或 Codex 執行。
3. 增加 `memory_policy.md`，定義哪些資訊可寫入 memory。
4. 增加 `evals/`，用固定問題測試是否回答穩定。
5. 增加 `jobs/`，做每日研究、自動摘要、內容草稿。

---

## 一人公司測試重點

這個 MVP 適合先測三件事：

1. **輸入成本**：你每天丟 3–5 篇文章進 raw，系統是否能整理出可查資料。
2. **回收價值**：一週後是否能用 `ask` 找回概念、來源與判斷。
3. **治理能力**：skills 是否能把你的決策框架固定下來，而不是每次重新 prompt。

若這三件事成立，再往 API、agent、自動排程、Obsidian 整合擴充。

---

## 已知限制

- 同一份 raw 檔案重複 ingest 時，`memory/memory.md` 會依 source path 去重，但 `logs/run.log` 仍會持續追加執行紀錄。
