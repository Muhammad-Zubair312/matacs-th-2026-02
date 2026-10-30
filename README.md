# MATACS-TH-2026-02: AI Proposal Triage Design

**Name:** Muhammad Zubair Arif
**Reference:** MATACS-TH-2026-02
**Time actually spent:** About 45 minutes

## Files

- [WRITEUP.md](WRITEUP.md): answers to the five questions
- [diagram/process-flow.png](diagram/process-flow.png): process flow from upload to ranked output
- [PROMPTS.md](PROMPTS.md): extraction, verification and reason prompts
- [ranking.json](ranking.json): expected ranking of proposals A to E
- [prototype/](prototype/): optional scoring script ([score.py](prototype/score.py)) that applies the scoring rules to hand-prepared extracted fields ([extracted.json](prototype/extracted.json)); [.env.example](prototype/.env.example) holds a placeholder only. It does not call an AI model.

## Summary

AI reads and structures the proposal text; plain code does eligibility, scoring and ranking; people review anything flagged and make the final award decision. Result on the sample set: A first, E second, C and D flagged, B ineligible.

## How I used AI tools

I used Claude to draft the design, the prompts and the scoring script, and I ran the script to check the numbers. I then reviewed its work critically and disagreed with two things. First, it scored Proposal C on its raw install count, but "since 2020" may fall outside the 5-year window, so I added a date-window rule that flags unclear ranges for a person. Second, it claimed every extracted fact has a supporting quote, but nothing enforced that, so I added a code check that each quote must appear word for word in the PDF text.