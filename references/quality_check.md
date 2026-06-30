# Quality Check

Run this check before final delivery.

## Transcript Check

- No inferred completion appears after interrupted speech.
- All interruptions are marked `【发言中断】`.
- Spoken numbers remain in original wording.
- No fact/opinion labels appear in the transcript.
- Homophone corrections are supported by the glossary, or uncertainty is marked.
- Unknown speakers are not overconfidently assigned.

## Minutes Check

- Each number in the minutes appears in the transcript in the same spoken wording.
- Each key factual claim has a source pointer.
- Opinion, prediction, and interpretation are labeled `【观点】`.
- Unverified or unclear statements are labeled `【待确认】`.
- Summary does not introduce facts absent from the transcript.
- Tables preserve original numeric wording.

## Data Safety Check

Before any external call, confirm:

- Exact audio or transcript file path.
- Target provider and endpoint.
- Whether the user approves sending this specific content.
- Whether `doubaoyuyin.env` and `豆包TOS配置.env` are present. Do not read, print, or expose secret values during this check.
- Whether the audio is available through a controlled URL if using Doubao standard recording API.

Do not print API keys or secrets in responses.

## Delivery Check

Final response should include:

- Paths to generated files.
- Which model/provider was used, if any.
- Any limitations, such as unclear speakers or missing API docs.
- Whether quality checks passed.
