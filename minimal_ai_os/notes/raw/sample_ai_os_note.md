# Karpathy LLM Wiki + Thin Harness / Fat Skills 測試筆記

這份筆記用來測試一人公司的 Minimal AI OS。

核心想法：不要一開始就做複雜 RAG、向量資料庫、多 agent 編排。先把原文保留下來，建立可回源的 LLM Wiki，再用 Skills 固定工作流程與決策框架。

Thin harness 的責任應該很少：讀檔、寫檔、搜尋、路由、呼叫工具、留下 log。不要把商業判斷與大量流程邏輯塞進 harness。

Fat skills 的責任比較重：定義任務 SOP、判斷標準、輸出格式、風險檢查、驗收條件。這讓 Claude Code、Codex、ChatGPT 或地端 LLM 都可以用同一套工作規格。

Memory 不應該變成垃圾桶。只保存長期穩定、未來會重複使用、能降低決策成本的資訊。短期資料留在 raw 或 artifacts，不要污染核心記憶。

對一人公司來說，第一個有效場景不是全自動公司，而是：研究輸入、知識整理、決策紀錄、內容產出、流程 SOP 化。

高風險假設：
- 以為向量資料庫一開始就必要。
- 以為多 agent 一定比單 agent 好。
- 以為模型可以自動判斷所有記憶是否值得保存。
- 以為沒有驗收規格也能穩定產出。

最小驗證方式：
1. 每天丟 3 篇 raw notes。
2. 每週整理 5 個 concepts。
3. 用 ask 找回來源。
4. 用 skills 產生固定格式的分析。
5. 一週後檢查是否真的降低重複整理成本。
