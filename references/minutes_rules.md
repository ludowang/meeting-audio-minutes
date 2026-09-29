# Minutes Rules

## Goal

Create executive-ready minutes by faithfully reconstructing the transcript, not by summarizing it.

The governing sequence is:

> 先保全信息，再重建逻辑，最后才压缩表达。

Conciseness may come only from removing filler and meaningless repetition, merging truly identical information, improving syntax, and improving hierarchy. Never delete or merge distinct numbers, time periods, objects, mechanisms, reasons, strategies, conditions, exceptions, examples, rankings, or priorities merely to shorten the document.

## Source Roles

- **逐字稿**：事实底座。事实、数字、机制和专家观点必须可回溯至逐字稿。
- **访谈提纲（optional）**：只解释研究目的和原始关注点，不决定纪要结构；提纲中未被回答的问题不得补写答案。
- **用户速记（optional）**：提示重要性、时间口径、细节和可能的 ASR 术语问题，不得覆盖逐字稿。速记更简略时，保留逐字稿中的完整限定条件。

## Four-Stage Workflow

### Step 1: Extract Valuable Information

Do not write minutes and do not optimize for brevity. Extract every research-relevant item, even if some temporary repetition remains.

An item is valuable if removing it changes understanding of what happened, why, how much, for whom, during which period, in what status, under what condition or exception, what happens next, or what is more important.

Use a simple Markdown inventory. Each item contains:

- 来源 / timestamp
- 主题
- 时间
- 对象
- 状态
- 内容
- 关系（only when useful）

Useful status values include `已发生`, `当前实际`, `当前目标`, `计划`, `申请中`, `尚未批准`, and `专家个人预计`. Useful relation values include `结论`, `原因`, `结果`, `并列原因`, `条件`, `例外`, `对比`, and `举例`.

Split one passage into multiple items whenever it contains distinct times, objects, states, mechanisms, or relations. Preserve the transcript's original numeric wording and source pointer.

### Step 2: Reconstruct the Expert's Logic

Build a global outline from the complete information inventory. Ask what business logic the expert actually explained; do not reproduce the interview guide or Q1/Q2/Q3 order.

Cross-question material may be grouped under one theme, but two items may be merged only when their time, object, status, and meaning all match. Otherwise keep them as separate branches under the same theme.

Prefer a decision-useful logic such as:

`结果 → 原因/机制 → 应对措施 → 资源变化 → 未来战略与计划`

Use another logic when the expert's actual answer requires it.

### Step 3: Write Formal Minutes

Only now optimize for boss-facing readability. Use headings and bullets by default:

- **主结论：** one clear sentence.
  - Supporting bullets preserve necessary numbers, time periods, mechanisms, strategies, conditions, exceptions, examples, and source pointers.

Do not force Q&A, fact/opinion labels on every sentence, or tables. Use a table only when a true horizontal comparison, numeric comparison, or multi-object comparison becomes materially clearer.

State uncertainty naturally: `专家个人预计`, `当前尚未最终确定`, `计划于 H2`, `截至 7 月实际`, or `该说法仍需确认`. Never turn a forecast into a target, a plan into an actual result, or an application into an approval.

### Step 4: Coverage Audit And Repair

Audit the draft against the information inventory, then output a corrected final version rather than a QA report. Check every item in `quality_check.md` and repair omissions or distortions before delivery.

## Merge Guards

Never collapse distinctions across:

- different periods, including year, half-year, current actual, full-year target, and future forecast;
- different objects, such as mid-tier creators, KOC/long-tail creators, and top creators;
- different mechanisms or parallel reasons;
- different states, such as actual, target, planned, pending approval, and expert forecast;
- different strategies, conditions, exceptions, or business examples.

Do not rewrite parallel causes as a causal chain. When later speech corrects or clarifies earlier speech, use the final clarified position and retain the change when it has business significance.

## Source References

Keep source pointers at the claim or bullet level. Prefer transcript timestamps. If timestamps are unavailable, use the closest stable transcript heading or segment marker. A source pointer supports traceability; it does not replace natural uncertainty wording.

## DOCX Expectations

- Clear heading hierarchy and short paragraphs.
- Bullets for conclusion-plus-support logic.
- Tables only where comparison benefits.
- No decorative prose.
- The final document must be usable without rereading the entire transcript to recover important independent information.
