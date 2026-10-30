# Write-up: AI Proposal Triage Design

**Reference:** MATACS-TH-2026-02

## How the flow works

1. Reviewer uploads proposals and picks a category.
2. System loads the admin's saved criteria for that category (a versioned snapshot).
3. Text is pulled from each PDF.
4. **AI** extracts facts into structured fields, each with a quote as evidence.
5. A second **AI** call checks the extraction against the text and looks for hidden instructions.
6. **Rules** check validation, mandatory pass/fail, and budget and deadline limits.
7. **Rules** compute weighted scores and sort.
8. **Human** reviews flagged items, confirms or overrides, then makes the award decision.

## 1. AI vs. rules

**AI:** reading messy proposal text and turning it into fields (extraction), the second-pass check, and optionally phrasing a one-line reason.

**Rules/code:** mandatory pass/fail, budget and deadline limits, all score arithmetic, ranking, and tie-breaks.

I drew the line at "understanding text" versus "making a decision". Language is where AI helps, because every bidder words things differently. Scoring is where it hurts: scores must be exact, repeatable and defensible in a dispute, and code does that better. The AI never sees the weights and never produces a score.

## 2. Consistency and explainability

- Extraction runs at temperature 0 with a fixed model version and strict JSON output. Scoring is plain code, so given the same extracted fields the result is identical every time.
- The one source of variation is extraction. If the extraction is re-run and any field differs, that proposal is flagged instead of silently ranked.
- **Evidence check (code):** every quote the AI returns must appear word for word in the PDF text. If not, the field becomes null and the proposal is flagged.
- Scoring formulas are simple and written down. Price and timeline are scored relative to the best eligible bid, experience is capped at 12 installs, warranty averages panel and workmanship, and team is a four-item checklist. Ties break by a fixed rule.
- The reviewer sees a table per proposal: each criterion, the extracted value, the quote it came from, the points earned, and the total. They can click through to the page in the PDF.

**Answer to "ranked twice, same result?"** Yes, as long as the extraction is unchanged, and the system detects when it is not.

## 3. Human in the loop

Checkpoints:

- **After extraction:** the reviewer can correct any field. Corrections are marked as human edits.
- **Flagged queue:** missing data, low confidence, disagreement between the two AI passes, or detected manipulation always go to a person.
- **Ineligible bids:** a reviewer confirms each mandatory failure before it is final.
- **Final ranking:** advisory only. A human makes and records the award decision.

The audit log stores: who uploaded and when, file hash, category and criteria version, model name and version, prompts used, raw AI output, extracted values with quotes, every human edit (who, when, why), scores, and the final decision.

## 4. Changing criteria

Criteria are versioned. A score always records the version it used, so old results never change silently.

- Weights or criteria edited: existing scores are marked **stale** and shown with their original version.
- A reviewer can re-score. Because extraction is stored, a weight change only needs the cheap scoring code, not new AI calls.
- A new or changed criterion (not just a weight) needs extraction again for that field only.
- Weights must sum to 100% or the admin cannot save.
- Once an award is recorded, that ranking is locked as a historical record.

## 5. Risks

| Risk | Safeguard |
|---|---|
| Wrong extraction | Quote required for every field; second-pass check; human can correct; null instead of guessing |
| Made-up facts | "Extract only what is written" rule; no quote means null; AI never scores |
| Manipulation | Proposal text is treated as data, not instructions. In the sample set, C contains a note telling reviewers to rank it first. It is ignored, flagged, and scored on its real content. A person decides whether the bid is acceptable. |
| Bias | Fixed criteria and formulas; AI does not see weights; no company names or reputation in scoring; periodic audit of overrides |
| Vague promises | "Subcontractor to be confirmed" does not count as holding the licence, so B is ineligible |
| Missing data | Never silently scored as zero. D gives no schedule, so it is flagged and the bidder is asked to clarify |
| Date ambiguity | Date window (rules): experience counts only installs inside 5 years of the review date. An unclear range such as "since 2020" is flagged for a person to confirm, not scored as stated. |
| Cost | Small, cheap extraction per proposal; cached results; re-scoring uses no AI |
| Privacy | Fictional data only here; in production, minimise data sent and keep the log access-controlled |

## Result on the sample set

| Proposal | Outcome | Score |
|---|---|---|
| A | Rank 1 | 98.0 |
| E | Rank 2 | 87.7 |
| C | Flagged (manipulation attempt) | 80.3 merit-only |
| D | Flagged (no schedule) | not scored |
| B | Ineligible (licence) | not scored |

If D supplies a schedule within 16 weeks, it is rescored and ranked without changing the other scores.

## Assumptions

- Price and timeline are measured against the best bid that passes mandatory checks, including flagged ones.
- Insurance, WSIB and licence are taken as stated in the proposal; they are not verified externally in this design.
- Verifying a licence number against a public register would be a sensible later addition.