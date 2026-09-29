# Quality Check

Run these checks before final delivery. The coverage audit must repair the minutes; do not deliver a separate QA report unless the user asks for one.

## Transcript Check

- No inferred completion appears after interrupted speech.
- All interruptions are marked `【发言中断】`.
- Spoken numbers remain in original wording.
- No fact/opinion labels appear in the transcript.
- Homophone corrections are supported by the glossary, or uncertainty is marked.
- Unknown speakers are not overconfidently assigned.

## Information Inventory Check

- Important conclusions, numbers, time periods, objects, mechanisms, results, measures, conditions, exceptions, examples, comparisons, rankings, priorities, and uncertainty are represented.
- One item does not mix different times, objects, states, mechanisms, or relations.
- Actual, target, plan, pending approval, and expert forecast are separately identified.
- Parallel reasons remain parallel; they are not converted into cause-and-effect.
- Every item has the best available timestamp or stable source pointer.
- The interview outline has not supplied an answer absent from the transcript.
- User notes have only influenced emphasis or interpretation where the transcript supports them.

## Coverage Audit And Automatic Repair

Before final output, compare the draft with the complete information inventory and repair it until all checks pass:

1. No important transcript-backed number is omitted.
2. No important time period is omitted or mixed with another period.
3. Different objects are not incorrectly merged.
4. Parallel relations are not rewritten as causal relations.
5. Actual, target, plan, pending approval, and expert forecast are not confused.
6. Explicit rankings and priorities are retained.
7. Concrete measures within an important strategy are not over-abstracted.
8. Business-meaningful examples are retained.
9. Later corrections or clarifications use the final clear wording.
10. User-note emphases supported by the transcript appear in the minutes.
11. No independent business information was deleted merely for conciseness.

Acceptance question: **Would the user still need to reread the whole transcript to discover an important omission or a materially changed distinction?** If yes, repair the minutes before delivery.

## Data Safety Check

Before any external call, confirm:

- Exact audio or transcript file path.
- Target provider and endpoint.
- Whether the user approves sending this specific content.
- Whether `doubaoyuyin.env` and `豆包TOS配置.env` are present. Do not print or expose secret values.
- Whether the audio is available through a controlled URL if using Doubao standard recording API.

Do not print API keys or secrets in responses.

## Delivery Check

Final response should include:

- Paths to generated final and intermediate files.
- Which model/provider was used, if any.
- Any limitations, such as unclear speakers or unavailable render QA.
- Whether code and coverage checks passed.
