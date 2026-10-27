# Handoff from Sonnet to Sonnet, 2026-10-27. Read after any restart or power outage.

State: judge validation PASSED (run 3, 12 bulletins, new winner-and-margin format), badge validated and live, nothing running on the model. Next: Nir double-clicks the "Crystal Balls, Run Round" icon on Saturday 2026-10-31 (about 20 to 25 hours; after a power cut or if it stops, tell Nir and restart scripts/run_round.sh; the model check at the start can take about 6 minutes after a cold start, that is normal).

Standing instructions from Fable (2026-10-27):
1. The handoff file BIBLE/HANDOFF-FOR-FABLE.md exists (Fable's text saved verbatim). After EVERY round, append one dated line at its end with the round's result in one sentence, commit, push.
2. Report for round 2026-10-31, written to data/demo/ with a clear name and date (for example PART13-ROUND-1031-REPORT-FOR-FABLE-<date>.md), containing besides the usual items of 13.19: (a) the grade of the hand-made Israel text of 2026-10-22, with the judge's item grades and archer note verbatim; (b) per country the signed verdict v (crystal vs plain) and u (crystal vs persistence) as a plain list, plus the round mean of each; (c) the judge consistency count out of all comparisons; (d) the noise floor numbers for US, IL, DE, BR; (e) the number of unscorable countries and their headline counts; (f) Israel's plain and crystal bulletins verbatim. Usual items: total time, calls, retries and failures per step, judgments.
3. The vague-test margin stays frozen; the consistency flag stays report-only (revisit after six scored rounds). Protocol frozen until six rounds are scored (13.19 b); bug fixes only, logged in 13.19 f.
4. Rule 8 for anything for Fable: no tables, no collapsible sections, formulas as raw LaTeX in code blocks.
5. Publish (scripts/publish.sh) only when Nir says so.

Nir's rules: emojis on every line, short messages, answer his question first, do only what he says, run things myself (he does not want to run commands I can run) but warn before real model runs, save progress so a power cut loses little, report finished jobs the moment he writes.
