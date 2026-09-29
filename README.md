# meeting-audio-minutes

Codex skill for converting Chinese expert interviews, user research sessions, and small meeting recordings into:

- a faithful Markdown transcript
- a staged information inventory and expert-logic outline
- a boss-facing, coverage-audited meeting-minutes Markdown
- a DOCX minutes document

The workflow is designed for sensitive interview material and emphasizes:

- no hallucinated completion of missing speech
- no normalization of spoken numbers
- traceable facts and source timestamps
- preservation of distinct times, objects, statuses, mechanisms, conditions, exceptions, and examples
- four-stage reconstruction instead of one-shot summarization
- explicit user confirmation before any external API call

## Included Files

- `SKILL.md`: skill behavior, guardrails, and workflow
- `scripts/run_meeting_workflow.py`: end-to-end entrypoint
- `scripts/doubao_tos_asr.py`: upload local audio to private TOS, submit to Doubao ASR, poll results, and write transcript artifacts
- `scripts/deepseek_minutes.py`: run extraction, logic reconstruction, drafting, coverage repair, and DOCX generation
- `references/`: transcript rules, minutes rules, metadata template, quality checks, and TOS/ASR flow notes
- `agents/openai.yaml`: display metadata for the skill

## Expected Inputs

- audio file path: `mp3`, `wav`, `m4a`, or `mp4`
- meeting topic
- meeting date
- participant roles
- industry/domain
- approval for external API processing for the specific recording

Optional inputs:

- interview outline: research context only; it never dictates the final structure
- user notes: emphasis and terminology aid only; they never override the transcript

## External Services

This skill is built around:

- Volcengine TOS for temporary private object storage and presigned URL delivery
- Doubao ASR for audio transcription
- DeepSeek for structured minutes generation

Do not run this workflow on confidential recordings unless the data path is approved by the user and acceptable for your environment.

## Environment Files

The workflow expects local env files in the workspace root:

- `doubaoyuyin.env`
- `豆包TOS配置.env`
- `deepseek_meeting.env`

Secrets should stay local and must not be committed.

## Example

```bash
python3 scripts/run_meeting_workflow.py --meta meeting_meta.md --yes
```

With optional context:

```bash
python3 scripts/run_meeting_workflow.py --meta meeting_meta.md \
  --outline 访谈提纲.md --notes 访谈速记.md --yes
```

Dry run:

```bash
python3 scripts/run_meeting_workflow.py --meta meeting_meta.md \
  --skip-asr --transcript existing_逐字稿.md --dry-run
```

## Notes

- The generated transcript preserves ASR wording unless a user glossary explicitly allows correction.
- The minutes pipeline normally makes four model calls: information extraction, logic reconstruction, formal drafting, and coverage audit/repair.
- Only the first call receives the full transcript. Later calls use the extracted information inventory, which controls token cost while retaining coverage.
- Intermediate `信息清单.md`, `逻辑结构.md`, `纪要初稿.md`, and `模型用量.json` files are retained for review.
