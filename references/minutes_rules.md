# Minutes Rules

## Goal

Create an executive-ready DOCX meeting minutes document from the transcript. The document should reduce reading difficulty while preserving traceability.

## Default Structure

1. 标题与会议信息
2. 摘要
3. 核心结论
4. 问题 1：问题标题
   - 回答摘要
   - 关键依据
   - 事实/观点标注
5. 问题 2：问题标题
6. 分主题纪要
7. 关键数据表
8. 风险、分歧与不确定点
9. 待确认事项
10. 出处索引

For expert interviews, the question-answer sequence is the primary structure. Use thematic sections only when they help merge repeated discussion.

## Writing Style

- Boss-facing: concise, decision-useful, and scannable.
- Preserve uncertainty. Use wording such as `受访者认为`, `据受访者描述`, `需进一步确认`.
- Avoid over-polished claims.
- Do not convert spoken numbers into normalized figures.
- Do not present unsupported inferences as facts.

## Fact And Opinion Labels

Only label in the minutes, not in the transcript.

Use:

- `【事实】`: stated as concrete factual information in the transcript.
- `【观点】`: speaker's judgment, prediction, interpretation, or preference.
- `【待确认】`: unclear, disputed, unsupported, or requiring follow-up evidence.

Example:

```markdown
【观点】受访者认为该竞品的优势主要在于渠道覆盖和响应速度。
【事实】受访者提到相关规模是“大概两百多个亿”。出处：逐字稿 Q3。
```

## Tables

Use tables when they reduce reading burden:

- Key data points
- Competitor comparison
- Product or feature comparison
- User needs and pain points
- Risks and uncertainties
- Follow-up questions

Key data table columns:

| 主题 | 原话数据 | 含义 | 类型 | 出处 |
|---|---|---|---|---|

Risk table columns:

| 风险/不确定点 | 说明 | 类型 | 建议跟进 |
|---|---|---|---|

## Source References

Every specific number or factual claim must include a source pointer such as:

- `出处：逐字稿 问题 2`
- `出处：逐字稿 片段 4`
- `出处：逐字稿 00:12:30-00:13:10` if timestamps exist

If no source can be found, remove the claim or mark it `【待确认】` without treating it as fact.

## DOCX Expectations

- Use clear heading hierarchy.
- Use tables for dense information.
- Keep paragraphs short.
- Do not include decorative language.
- Optional one-page summary may be created as `摘要.md` or as the first section of the DOCX.
