#!/usr/bin/env python3
"""
Minimal AI OS Harness
- Thin harness: file IO, routing, simple search, simple extraction.
- Fat skills: domain logic lives in skills/*.md.
- No external dependency. Python stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from textwrap import shorten

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "notes" / "raw"
SOURCE_DIR = ROOT / "wiki" / "sources"
CONCEPT_DIR = ROOT / "wiki" / "concepts"
SKILL_DIR = ROOT / "skills"
MEMORY_FILE = ROOT / "memory" / "memory.md"
LOG_FILE = ROOT / "logs" / "run.log"

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "was",
    "可以", "以及", "這個", "那個", "如果", "不是", "沒有", "因為", "所以", "一個", "我們", "你要", "要把", "就是", "對於",
}

KEY_TERMS = [
    "thin harness", "fat skills", "memory", "llm wiki", "codex", "claude code",
    "skill", "skills", "agent", "agentic", "obsidian", "一人公司", "知識庫", "記憶",
    "決策", "流程", "治理", "評估", "自動化", "wiki", "harness",
]


def now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dirs() -> None:
    for d in [RAW_DIR, SOURCE_DIR, CONCEPT_DIR, SKILL_DIR, MEMORY_FILE.parent, LOG_FILE.parent]:
        d.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text("# Memory Index\n\n", encoding="utf-8")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    return text.strip("-")[:80] or "untitled"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_log(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{now()}] {message}\n")


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip() or fallback
    for line in text.splitlines():
        line = line.strip()
        if line:
            return shorten(line, width=60, placeholder="…")
    return fallback


def extract_bullets(text: str, max_items: int = 8) -> list[str]:
    candidates: list[str] = []
    for raw in text.splitlines():
        line = raw.strip(" \t-•0123456789.、")
        if len(line) >= 12:
            candidates.append(line)
    # Prefer lines with known terms
    scored = sorted(
        set(candidates),
        key=lambda s: sum(term.lower() in s.lower() for term in KEY_TERMS),
        reverse=True,
    )
    return scored[:max_items]


def extract_concepts(text: str) -> list[str]:
    lower = text.lower()

    # Priority 1: explicit architecture terms. Keep phrase-level concepts first.
    concepts: list[str] = [term for term in KEY_TERMS if term.lower() in lower]

    # Priority 2: repeated tokens as lightweight fallback.
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,8}", text)
    freq: dict[str, int] = {}
    for t in tokens:
        tl = t.lower()
        if tl in STOPWORDS or len(tl) < 2:
            continue
        freq[t] = freq.get(t, 0) + 1

    for token, count in sorted(freq.items(), key=lambda x: x[1], reverse=True):
        if count >= 2 and token not in concepts and token.lower() not in [c.lower() for c in concepts]:
            concepts.append(token)
        if len(concepts) >= 12:
            break

    return concepts[:12]


def _relative_to_root(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def ingest(file_path: str) -> None:
    ensure_dirs()
    path = Path(file_path)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = read_file(path)
    title = extract_title(text, path.stem)
    source_slug = slugify(path.stem)
    bullets = extract_bullets(text)
    concepts = extract_concepts(text)
    created = now()

    source_md = SOURCE_DIR / f"{source_slug}.md"
    source_md.write_text(
        "\n".join([
            f"# {title}",
            "",
            f"- Source: `{_relative_to_root(path)}`",
            f"- Ingested: {created}",
            f"- Concepts: {', '.join(concepts) if concepts else 'None'}",
            "",
            "## Extracted Points",
            *(f"- {b}" for b in bullets),
            "",
            "## Verbatim Anchor",
            "```text",
            text[:2500],
            "```",
            "",
            "## Open Questions",
            "- 待補。",
            "",
        ]),
        encoding="utf-8",
    )

    for concept in concepts:
        cslug = slugify(concept)
        cpath = CONCEPT_DIR / f"{cslug}.md"
        if cpath.exists():
            existing = read_file(cpath)
        else:
            existing = f"# {concept}\n\n## Definition\n\n待補。\n\n## Linked Sources\n\n"
        link_line = f"- [[../sources/{source_slug}|{title}]] — {created}\n"
        if link_line not in existing:
            existing += link_line
        cpath.write_text(existing, encoding="utf-8")

    memory_text = read_file(MEMORY_FILE) if MEMORY_FILE.exists() else ""
    source_marker = f"- Source summary: `wiki/sources/{source_slug}.md`"
    if source_marker not in memory_text:
        with MEMORY_FILE.open("a", encoding="utf-8") as f:
            f.write(f"\n## {created} — {title}\n")
            f.write(f"{source_marker}\n")
            if concepts:
                f.write(f"- Concepts: {', '.join(concepts)}\n")
            if bullets:
                f.write(f"- Decision-useful note: {bullets[0]}\n")

    write_log(f"ingest: {path} -> {source_md}")
    print(f"OK: ingested '{title}'")
    print(f"SOURCE: {source_md.relative_to(ROOT)}")
    print(f"CONCEPTS: {', '.join(concepts) if concepts else 'None'}")


def iter_knowledge_files() -> list[Path]:
    ensure_dirs()
    files = []
    for d in [RAW_DIR, SOURCE_DIR, CONCEPT_DIR, MEMORY_FILE.parent, SKILL_DIR]:
        files.extend(sorted(d.glob("**/*.md")))
    return [f for f in files if f.is_file()]


def score_text(query: str, text: str) -> int:
    q_tokens = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]{2,8}", query.lower())
    text_lower = text.lower()
    score = 0
    for t in q_tokens:
        if t in STOPWORDS:
            continue
        score += text_lower.count(t.lower()) * max(1, len(t) // 2)
    return score


def best_snippet(query: str, text: str, size: int = 420) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return ""
    ranked = sorted(lines, key=lambda l: score_text(query, l), reverse=True)
    snippet = " / ".join(ranked[:3])
    return shorten(snippet, width=size, placeholder="…")


def ask(query: str) -> None:
    ensure_dirs()
    results = []
    for f in iter_knowledge_files():
        text = read_file(f)
        s = score_text(query, text)
        if s > 0:
            results.append((s, f, best_snippet(query, text)))
    results.sort(reverse=True, key=lambda x: x[0])

    print(f"# Query: {query}\n")
    if not results:
        print("找不到直接命中的資料。建議先 ingest 更多 raw notes，或改用更明確關鍵字。")
        return

    print("## Best Matches")
    for s, f, snip in results[:5]:
        print(f"\n### {f.relative_to(ROOT)}")
        print(f"- Score: {s}")
        print(f"- Snippet: {snip}")

    print("\n## 判斷")
    print("這是關鍵字式最小檢索，不是語意搜尋；適合驗證資料結構與引用回源，不適合當最終問答品質。")


def run_skill(skill_name: str, task: str) -> None:
    ensure_dirs()
    skill_path = SKILL_DIR / f"{skill_name}.md"
    if not skill_path.exists():
        available = ", ".join(p.stem for p in SKILL_DIR.glob("*.md")) or "None"
        print(f"ERROR: skill not found: {skill_name}", file=sys.stderr)
        print(f"Available skills: {available}", file=sys.stderr)
        sys.exit(1)

    skill = read_file(skill_path)
    memory = read_file(MEMORY_FILE) if MEMORY_FILE.exists() else ""
    print(f"# Skill Run: {skill_name}\n")
    print("## Task")
    print(task)
    print("\n## Skill Contract")
    print(shorten(skill.replace("\n", " "), width=900, placeholder="…"))
    print("\n## Context From Memory")
    print(shorten(memory.replace("\n", " "), width=900, placeholder="…"))
    print("\n## Output Template")
    print("- 結論：")
    print("- 原因：")
    print("- 已知事實：")
    print("- 合理推論：")
    print("- 待驗證資訊：")
    print("- 高風險假設：")
    print("- 最大失敗原因：")
    print("- 對一人公司的價值：")
    print("- 成本與執行難度：")
    print("- 風險與限制：")
    print("- 最小可行測試：")
    print("- 下一步：")
    print("\nNOTE: 這個 MVP 只組裝上下文與輸出框架；正式版可在這一步接 LLM。")
    write_log(f"run-skill: {skill_name} task={task[:80]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal AI OS Harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="ingest a raw markdown/text file")
    p_ingest.add_argument("file")

    p_ask = sub.add_parser("ask", help="search local wiki/memory/skills")
    p_ask.add_argument("query")

    p_skill = sub.add_parser("run-skill", help="run a markdown skill contract")
    p_skill.add_argument("skill_name")
    p_skill.add_argument("task")

    args = parser.parse_args()
    if args.cmd == "ingest":
        ingest(args.file)
    elif args.cmd == "ask":
        ask(args.query)
    elif args.cmd == "run-skill":
        run_skill(args.skill_name, args.task)


if __name__ == "__main__":
    main()
