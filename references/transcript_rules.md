# Transcript Rules

## Goal

Produce a faithful Markdown transcript from ASR output. This is not a cleaned article, not a summary, and not a polished reconstruction.

## Allowed Edits

- Add paragraph breaks for readability.
- Add punctuation when it does not change meaning.
- Map speaker labels to roles when supported by metadata or obvious turn-taking.
- Remove only pure filler that has no semantic content and does not affect tone or meaning, such as an isolated "嗯" between turns.
- Correct terms only when the user glossary explicitly supports the correction.

## Forbidden Edits

- Do not complete unfinished sentences.
- Do not infer missing logic from later context.
- Do not normalize numbers, units, percentages, dates, or currencies.
- Do not change colloquial expressions into formal numbers or business wording.
- Do not silently correct homophones outside the glossary.
- Do not merge answers across different questions.
- Do not reorder turns.
- Do not add fact/opinion labels.

## Uncertainty Markers

Use these exact markers:

- `【发言中断】`: speaker was interrupted or the sentence visibly breaks off.
- `【听不清】`: audio or ASR is unclear.
- `【重叠发言】`: multiple speakers overlap.
- `【未知发言人-Speaker X】`: role cannot be mapped.
- `【存疑：ASR原文为"..."】`: likely term issue but not supported by glossary.

Prefer preserving the original ASR text over a confident-looking correction.

## Role Mapping

For expert interviews and user research:

- Use `【访谈者】`, `【受访者】`, and `【其他】`.
- If there are two interviewers, use `【访谈者1】` and `【访谈者2】` only when separable.
- If not separable, keep a shared `【访谈者】` role and mention the limitation in `待确认事项`.

For internal meetings:

- Use `【角色-姓名】` when metadata provides it.
- Otherwise use `【未知发言人-Speaker X】`.

## Q/A Formatting

For interviews, use Q/A blocks when the conversation is question-led:

```markdown
## 问题 1：问题原文或最贴近原话的短标题

【访谈者】...

【受访者】...
```

The question heading may be a short label, but the dialogue text underneath must preserve the speaker's wording.

## Dialogue Formatting

For less structured meetings:

```markdown
## 片段 1

【角色】...

【角色】...
```

## Header Template

```markdown
# 会议逐字稿

**会议主题**：
**会议日期**：
**会议类型**：
**行业/领域**：
**参会角色**：
**转写说明**：本文保留原话措辞；未补全中断发言；数字未做归一化。

---
```
