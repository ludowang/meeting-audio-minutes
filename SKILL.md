---
name: meeting-audio-minutes
description: Convert Chinese expert interview, user research, or small-group meeting recordings into a faithful transcript and high-coverage executive minutes through staged information extraction, logic reconstruction, drafting, and coverage repair. Use when the user provides or references mp3, wav, m4a, or mp4 recordings and needs transcript-backed minutes without losing business distinctions.
---

# Meeting Audio Minutes

Use this skill for Chinese-first expert interviews, user research, and small meetings, typically 30 minutes to 2 hours with 2-3 participants.

## Non-Negotiable Rules

These rules override any older prompt, template, or user-provided draft unless the user explicitly changes the safety policy.

1. Do not infer, complete, or invent missing speech. If speech is interrupted or lost, mark `【发言中断】`, `【听不清】`, or `【重叠发言】`.
2. Do not normalize numbers. Preserve spoken wording such as "大概两百多个亿"; do not rewrite it as "约200亿元".
3. Do not correct homophones unless the correction appears in the user-provided glossary. If uncertain, preserve ASR text and mark `【存疑：...】`.
4. Do not add fact/opinion labels in the transcript. In minutes, prefer natural qualifiers and use explicit labels only when they materially clarify uncertainty.
5. Every number, amount, ratio, time, ranking, company name, product name, and key factual claim in the minutes must be traceable to the transcript.
6. Do not send audio, transcript, or minutes to an external service without confirming with the user immediately before the call.
7. Prefer controlled or enterprise environments for sensitive recordings. Do not route confidential content to an uncontrolled public hosted model by default.

## Inputs To Collect Before Running

Ask the user for missing required items before processing:

- Audio file path: mp3, wav, m4a, or mp4.
- Meeting topic.
- Meeting date.
- Participant roles: for example `访谈者：...；受访者：...`.
- Industry/domain.
- Whether external API processing is allowed for this specific file.

Optional but helpful:

- Glossary: one term per line, optionally `误识别=正确术语` or `简称=全称`.
- Meeting purpose.
- Focus questions.
- Interview outline file: optional context for research intent; never use it as the final minutes structure.
- User notes file: optional emphasis and terminology aid; never let it override fuller transcript wording.
- Preferred output folder.

Use `references/meeting_meta_template.md` when the user wants a fillable metadata file.

## Model Selection

Audio transcription:

- Preferred ASR provider: Volcengine/Doubao ASR when the user wants a domestic, lower-cost, multilingual transcription service.
- Current Doubao identifier provided by user: `d0e49403-cda1-45fd-8998-160c1edfcd69`. Treat this as an app/resource/model identifier candidate, not as a secret and not as full authentication.
- Env file lookup: use `doubaoyuyin.env` for Doubao ASR secrets and `豆包TOS配置.env` for non-secret TOS settings. Do not read, print, or expose secret values; only verify that the env files exist before execution.
- Doubao standard recording API uses two phases: submit task, then query result.
- Enable speaker clustering when using Doubao ASR: set `enable_speaker_info: true`; for Chinese or unspecified language, also set `ssd_version: "200"` when supported.
- Submit endpoint: `https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit`.
- Query endpoint: `https://openspeech.bytedance.com/api/v3/auc/bigmodel/query`.
- Required resource id for Doubao recording recognition model 2.0: `volc.seedasr.auc`.
- Standard API expects `audio.url`; if the user only has a local file, first decide on a controlled upload/presigned URL path before submitting.
- Preferred local-file URL path: upload the recording to a private Volcengine TOS bucket, generate a short-lived presigned GET URL, submit that URL to Doubao ASR, then delete the object after successful transcription.
- Required TOS env variables for local-file processing: `VOLC_ACCESS_KEY_ID`, `VOLC_SECRET_ACCESS_KEY`, `VOLC_TOS_ENDPOINT`, `VOLC_TOS_REGION`, `VOLC_TOS_BUCKET`.
- Required Doubao ASR env variables: `DOUBAO_APP_KEY` and `DOUBAO_ACCESS_KEY`. Accept aliases only if the user confirms the env naming.
- Before any API call, confirm the target endpoint, file path, and data-safety approval with the user.

Transcript-to-minutes:

- Preferred model for the current project: DeepSeek using `deepseek_meeting.env`, with quality-first model `deepseek-v4-pro` when configured by the user.
- Do not default to OpenAI or another public API for confidential transcripts unless the user explicitly approves that data path.
- If no approved text model is available, generate a prompt package and wait for user confirmation rather than silently choosing another hosted provider.

## Workflow

1. Gather meeting metadata and glossary using `references/meeting_meta_template.md`.
2. Confirm data path before any external model call:
   - audio -> Volcengine TOS private bucket -> presigned URL -> Doubao ASR
   - transcript -> DeepSeek meeting-minutes model
3. Run `scripts/run_meeting_workflow.py` only after the user explicitly approves external API processing for that specific recording.
4. Transcribe audio with Doubao speaker separation. Preserve time ranges for traceability.
5. Convert ASR output into faithful transcript Markdown using `references/transcript_rules.md`.
6. Generate minutes with the four-stage fidelity reconstruction in `references/minutes_rules.md`:
   - extract a complete information inventory from the transcript;
   - reconstruct the expert's actual business logic;
   - write formal boss-facing minutes;
   - audit coverage and automatically repair the final minutes.
7. Run quality checks from `references/quality_check.md`. The full transcript is sent mainly in stage 1; later stages use the information inventory instead of repeatedly sending the transcript.
8. Create final outputs:
   - `逐字稿.md`
   - `信息清单.md`
   - `逻辑结构.md`
   - `纪要初稿.md`
   - `会议纪要.md`
   - `会议纪要.docx`
   - `模型用量.json`

Default output location:

- Put all artifacts for one meeting in one folder under the workspace.
- Folder naming: `{会议主题}-{会议日期}`.
- Do not scatter generated artifacts in the workspace root unless the user explicitly asks.

Example command after approval:

```bash
python3 .codex/skills/meeting-audio-minutes/scripts/run_meeting_workflow.py --meta meeting_meta.md --yes
```

Optional outline and notes may be supplied either in metadata or on the command line:

```bash
python3 .codex/skills/meeting-audio-minutes/scripts/run_meeting_workflow.py \
  --meta meeting_meta.md --outline 访谈提纲.md --notes 访谈速记.md --yes
```

Dry-run path check without API calls:

```bash
python3 .codex/skills/meeting-audio-minutes/scripts/run_meeting_workflow.py \
  --meta meeting_meta.md --skip-asr --transcript existing_逐字稿.md --dry-run
```

When the user asks to process a recording, first ask them to fill or confirm `meeting_meta.md`. Do not run the workflow from only an audio path unless the user explicitly says it is a technical test.

## Output Style

Transcript:

- Markdown.
- Q/A format for interviews, or role-dialogue format for less structured meetings.
- Preserve original wording, sequence, uncertainty markers, and speaker uncertainty.

Minutes:

- DOCX.
- Boss-facing, concise, structured, and easy to scan only after information is preserved and logic is reconstructed.
- Organize by the expert's actual business logic, not by the interview outline or mechanical Q&A order.
- Prefer headings plus conclusion/supporting bullets. Use tables only when true horizontal comparison becomes clearer.
- Preserve distinctions across time, object, status, mechanism, conditions, exceptions, examples, rankings, and priorities.
- Use natural qualifiers for actuals, targets, plans, pending approval, and expert forecasts instead of labeling every sentence.

## Reference Files

- Read `references/transcript_rules.md` before transforming ASR into transcript Markdown.
- Read `references/minutes_rules.md` before creating the DOCX minutes or summary.
- Read `references/quality_check.md` before final delivery.
- Read `references/meeting_meta_template.md` when collecting or writing meeting metadata.
- Read `references/doubao_tos_flow.md` before using Doubao ASR with a local audio file.
