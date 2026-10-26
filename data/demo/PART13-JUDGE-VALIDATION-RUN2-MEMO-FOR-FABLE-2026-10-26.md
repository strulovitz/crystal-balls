# Judge validation, second run (rebuilt damages): result and memo for Fable, 2026-10-26

Short answer: the rebuilt run finished and the judge did NOT pass again, but this time only narrowly and only on one test. Four tests pass, "reversed" fails with a mean of 0.75 against the required 1. Following your ruling I changed nothing: the badge stays "Judge not yet validated", nothing was published, and the round of Saturday 2026-10-31 goes ahead as planned. The data is saved (data/judge_validation.json, with the judge's full reply for every comparison).

## Run facts
- Started 2026-10-26 08:45:09, finished 17:59:53: 9 hours 14 minutes (I had estimated 6 to 7 hours; the rewrite calls were slower than the paraphrase I had measured).
- 40 calls: 16 kept from the first run (wrong_country and paraphrase, not rerun), 8 rewrite calls for reversed, 8 for actors_swapped, 24 judge calls (8 actors_swapped, 8 reversed, 8 vague). One rewrite attempt was rejected by validation (Brazil, damage_reversed) and succeeded on retry. No failures.
- Nir was not asked to run it: he told me he does not want to run commands that I can run, so I ran it.
- I reported the finish 64 minutes late, because I only act when Nir writes to me.

## Results against the thresholds of 13.7 (unchanged)
Order of countries: Australia, Brazil, Canada, China, Germany, Egypt, France, United Kingdom. Values are original minus damaged; positive means the judge preferred the original.

wrong_country (kept from run 1): 2.0 in all eight. Mean 2.0, needs at least 1. PASS.
paraphrase (kept from run 1): 0.0 in all eight, eight ties of eight, needs 6. PASS.
actors_swapped: 1.0, 1.0, 1.0, 2.0, 0.0, 1.0, 1.0, 1.0. Mean 1.0, needs above 0. PASS. Seven wins, one tie, no loss. (Run 1: mean 0.375.)
vague: -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0. Mean 0.5, needs above 0. PASS. Six wins, two losses (Australia, Canada). (Run 1: mean 0.375.)
reversed: 2.0, 2.0, 2.0, 1.0, 0.0, -1.0, -2.0, 2.0. Mean 0.75, needs at least 1. FAIL. Five wins, one tie (Germany), two losses (Egypt, France). The sum is 6; the rule needs 8. (Run 1: mean 0.625.)

I checked that the new damages are real rewrites. Example, France reversed, lead: the original says "A second nationwide day of demonstrations will draw larger crowds ... and spark a new round of clashes", direction escalate; the damaged one says "The nationwide protest wave will shrink to a small, peaceful gathering in a single city as the coalition narrows back to students and police stand down", direction de-escalate. Same subject, opposite development, as you specified. Egypt reversed lead: original "Egypt's parliament will hold the formal vote to authorize military assistance to Saudi Arabia", damaged "Egypt's parliament will postpone the formal vote". One limit of the actors_swapped rewrite: in Germany the model changed the subject wording ("Nord Stream sabotage trial" became "German prosecutors in the Nord Stream case") but the story is still Nord Stream with the same development, so the judge reasonably called the two bulletins near-paraphrases (score 0).

## The judge's own words for every case where the original lost or tied (verbatim)
The label order is in each header. In every case X is the first-listed bulletin. Per the judge prompt, a negative score means the first-listed (X) was better.

Australia, vague, original minus damaged -1.0. Original was Y, damaged was X:
"Y's specific prediction of a Pacific Island or Asian RLWC opponent was contradicted by the England match, downgrading its third item to true_in_direction while X's generic sign was fully satisfied. Both bulletins share the same four topics, the same correct lead, and the same wrong fade call, but Y's added specificity introduced one concrete error that X's vagueness avoided."

Canada, vague, -1.0. Original was Y, damaged was X:
"Both bulletins correctly identified the Alberta vote, steel/Cleveland-Cliffs, BoC rates, and rugby fade, but Y's added specifics (power scramble among premiers, forced asset sale to court, spooking mortgage holders) were not clearly supported by the headlines. X's more conservative language ('stays in the news,' 'persist') was consistently matched by the evidence without introducing unsupported details."

Egypt, reversed, -1.0. Original was Y, damaged was X:
"X correctly predicted the parliamentary delay, which was the dominant story of the week, while Y predicted the vote would be held and announced, getting the single most important event backwards. Y was directionally closer on the succession and gold mine items and nailed the FIFA fade call, but the lead carries the greatest weight and X's hit there outweighs Y's advantages on secondary items."

France, reversed, -2.0. Original was Y, damaged was X:
"Y correctly called the direction of both dominant stories (protests escalating, debt stress widening) and the Channel Tunnel fade, while X got all four items wrong in direction, predicting de-escalation where escalation occurred. The decisive gap is on the lead and third items, where X's calm-and-confidence thesis was directly contradicted by 70,000 police, record yields, and curfews, whereas Y's escalation thesis matched the headlines almost verbatim."

Ties, for completeness:
Germany, reversed, 0.0. Original was X, damaged was Y:
"Both bulletins achieved an identical grade distribution (one came_true, one true_in_direction, two did_not_appear), with Y winning on the lead and second while X won on the third and fade call. The decisive difference is offset by the opposite errors on the remaining two items, making them a functional tie in overall accuracy."
Germany, actors_swapped, 0.0. Original was Y, damaged was X:
"Both bulletins are near-paraphrases of each other: identical lead (Nord Stream), identical second (car deal), identical third (Nvidia AI), and identical fade call (G20 Russia), with only minor wording differences in framing. The decisive difference is negligible, as both missed the same dominant stories and both got the same items right or wrong."

## What I read in these replies (my reading, for you to judge)
1. Egypt reversed is a legitimate judge decision, not a defect: the reversed bulletin happened to forecast what really occurred (the vote was postponed). A reversal can be right by chance. The judge was right to prefer it.
2. Australia and Canada vague are the judge doing exactly what its rubric says: penalizing a specific claim that the headlines contradicted, and not penalizing a statement too empty to be wrong. The rubric also says "generalities that nothing could falsify" should be penalized, but in these two cases the original's specifics were wrong, and wrong specifics lost to empty ones. This is a behaviour of the rubric, not a sign confusion.
3. France reversed is different, and I think it matters. The judge's own text says Y (the original) was right on all dominant stories and X (the reversed bulletin) "got all four items wrong in direction". The item grades in the same reply agree: X got did_not_appear on all four items, Y got came_true on the lead, the third item and the fade call (Y's second item did_not_appear). But the score is -2, and by the prompt's rule (negative means the first-named bulletin, X, was better) that says the reversed bulletin was the clear winner. The judge's number contradicts its own sentences and its own grades. This looks like a sign slip by the judge, in the one case that costs the most points. If that single score had been +2, the reversed mean would be 1.25 and the test would pass. I cannot prove it is a slip, but the text, the grades and the score cannot all be right.
4. If the judge can flip the sign of its verdict, that matters beyond this test, because every verdict of the main experiment uses the same scale. The rule in the prompt ("negative means the first-named bulletin was better") is the opposite of what most people would write; a model may slip on it, especially after a long thinking pass. I checked all 24 new comparisons against their own item grades with a crude points count (3 for came_true, 2 for true_in_direction, 0 for the rest). Most agree. The ones where the crude count and the score point to different bulletins are Brazil vague, Canada actors_swapped, China vague, Germany vague, Egypt reversed, Egypt vague, France reversed, United Kingdom vague, so eight of 24, but the judge says the lead counts most and ignores equal weights, so my count is too crude to call these errors. France reversed is the only one where the judge's own text and the grades both clearly say one thing and the score says the other.
5. Honest limit: the judge's replies for the 16 kept comparisons (wrong_country, paraphrase) were not saved in run 1, so I cannot check them the same way. They have no sign problem in effect: the wrong-country result is 2.0 eight times and paraphrase 0.0 eight times, which a sign slip would have shown as a negative somewhere.

## What I did not do
- No change to the judge prompt, rubric, parameters, thresholds or pass rule.
- No change to the badge, no publication, no new run.

## Questions, with the options as I see them (I do not choose)
1. Is the failure of reversed (mean 0.75, sum 6 against 8) final under 13.7 as written? As written it is a fail, and you said that if it fails again I change nothing and write you this memo.
2. Is the France case (text and grades say original better, score says reversed better) a sign slip that matters to the whole experiment? Options: (a) leave it as noise and let the verdict interval absorb it; (b) a mechanical, protocol-neutral check in the code that flags any comparison where the judge's score sign disagrees with its grade totals, reporting only (no correction, in line with 13.16 "never edit a model's output"); (c) a change to the judge prompt wording of the sign convention, which breaks the freeze of 13.19 b and would need your explicit ruling.
3. Do you want the reversed test rerun on more bulletins (23 judged country-weeks exist, the code uses 8 by default, --max can raise it) so that one country cannot decide a pass or a fail? About 2.5 hours of rewrite calls plus 11 minutes per judge call per extra country.
4. Should the sanity tests keep gating the badge, now that the only reversed failures are one legitimate chance case (Egypt) and one possible sign slip (France)?

## State
- Round 2026-10-24: complete and published.
- Saturday 2026-10-31: Nir double-clicks the icon; that round grades the 10-24 forecasts (the first scored ones) and the hand-made Israel text of 10-22. The badge says "Judge not yet validated" until you rule.
- Nothing is running on the model now.
