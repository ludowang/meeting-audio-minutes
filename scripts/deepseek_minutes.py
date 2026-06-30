#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

from docx import Document
from docx.shared import Pt


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"


SYSTEM_PROMPT = """你是一位专业的中文会议纪要编辑，服务对象是需要快速阅读决策信息的老板/管理者。

硬约束：
1. 不允许补全、推断或发明逐字稿之外的信息。
2. 不允许数字归一化，必须保留逐字稿中的原话数字措辞。
3. 纪要中的每个数字、金额、比例、时间、排名、公司名、产品名和关键事实，都必须带出处，出处指向逐字稿时间段或段落。
4. 事实/观点/待确认只在纪要中标注，格式为【事实】、【观点】、【待确认】。
5. 不确定就标【待确认】，不要写成事实。
6. 输出 Markdown，不要输出 JSON。

默认结构：
# 会议纪要
## 摘要
## 核心结论
## 关键问题与回答
### 问题 1：...
回答摘要：
关键依据：
事实/观点标注：
## 分主题纪要
## 关键数据表
| 主题 | 原话数据 | 含义 | 类型 | 出处 |
## 风险、分歧与不确定点
| 风险/不确定点 | 说明 | 类型 | 建议跟进 |
## 待确认事项
## 出处索引

写作要求：
- 老板可读，短句、清晰、可扫描。
- 能用表格降低阅读难度时使用表格。
- 不写装饰性语言。
- 如果逐字稿片段太短或信息不足，明确说明“本次测试片段信息有限”。"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate executive meeting minutes from transcript Markdown using DeepSeek.")
    parser.add_argument("--transcript", required=True, help="Transcript Markdown path")
    parser.add_argument("--minutes-md", required=True, help="Output minutes Markdown path")
    parser.add_argument("--minutes-docx", required=True, help="Output minutes DOCX path")
    parser.add_argument("--topic", default="", help="Meeting topic")
    parser.add_argument("--date", default="", help="Meeting date")
    parser.add_argument("--participants", default="", help="Participants/roles")
    parser.add_argument("--dry-run", action="store_true", help="Write prompt only, do not call API")
    args = parser.parse_args()

    transcript = read_text(args.transcript)
    prompt = build_prompt(transcript, args)

    if args.dry_run:
        write_text(args.minutes_md, prompt)
        markdown_to_docx("# 会议纪要\n\nDry run: prompt saved as Markdown.\n", args.minutes_docx)
        return 0

    content = call_deepseek(prompt)
    write_text(args.minutes_md, content.strip() + "\n")
    markdown_to_docx(content, args.minutes_docx)
    print(args.minutes_docx)
    return 0


def build_prompt(transcript: str, args) -> str:
    meta = []
    if args.topic:
        meta.append(f"会议主题：{args.topic}")
    if args.date:
        meta.append(f"会议日期：{args.date}")
    if args.participants:
        meta.append(f"参会角色：{args.participants}")
    meta_text = "\n".join(meta) if meta else "未提供"
    return f"""请根据以下逐字稿生成结构化会议纪要。

<meeting_meta>
{meta_text}
</meeting_meta>

<transcript>
{transcript}
</transcript>
"""


def call_deepseek(prompt: str) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("Missing DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"DeepSeek HTTP {e.code}: {redact(err)}")
    except Exception as e:
        raise SystemExit(f"DeepSeek request failed: {e}")
    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise SystemExit("DeepSeek response did not contain choices[0].message.content")


def markdown_to_docx(markdown: str, path: str) -> None:
    doc = Document()
    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10.5)

    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            doc.add_heading(text, level=min(level, 3))
            i += 1
            continue
        if is_table_line(line) and i + 1 < len(lines) and is_separator_line(lines[i + 1]):
            table_lines = [line]
            i += 2
            while i < len(lines) and is_table_line(lines[i]):
                table_lines.append(lines[i].rstrip())
                i += 1
            add_table(doc, table_lines)
            continue
        if line.startswith("- "):
            doc.add_paragraph(clean_inline(line[2:]), style="List Bullet")
            i += 1
            continue
        doc.add_paragraph(clean_inline(line))
        i += 1

    doc.save(path)


def add_table(doc: Document, table_lines):
    rows = [split_table_row(line) for line in table_lines]
    if not rows:
        return
    table = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows))
    table.style = "Table Grid"
    for r_idx, row in enumerate(rows):
        for c_idx, value in enumerate(row):
            table.cell(r_idx, c_idx).text = clean_inline(value)


def is_table_line(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def is_separator_line(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", line)) and "---" in line


def split_table_row(line: str):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def clean_inline(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def redact(text: str) -> str:
    return re.sub(r"(sk-[A-Za-z0-9_\-]{8})[A-Za-z0-9_\-]+", r"\1[REDACTED]", text)


if __name__ == "__main__":
    raise SystemExit(main())
