# Part 13.7 / 13.19 e: judge validation on the real judge, result and questions for Fable (2026-10-26)

Nir asked for this report to be long and plain, because he did not follow the short version. So this report explains each step from the beginning. Short answer first: the judge passed four of the five tests and failed one, the "reversed directions" test. Nothing was published because of it, the badge still says "Judge not yet validated", and I changed nothing in the protocol (13.19 b). I need your decision on what the failure means.

## 1. What the test is for, in simple words

The judge is the local Qwen model (thinking on, temperature 0.6, same parameters as 13.18). Each week it reads two or three forecast bulletins about one country, it reads what really happened (the situation bulletin and the numbered headlines of the new round), and it gives each bulletin a mark from -2 to 2 against the other. The whole experiment (crystal against plain) rests on this judge. If the judge cannot tell a good forecast from a broken one, every verdict it produces is meaningless. So 13.7 says: before any verdict is shown, deliberately break some real bulletins in known ways, and check that the judge notices.

How it works in the code (pipeline/judge_validation.py, unchanged in logic, only made resumable today):
- It takes eight real Crystal bulletins from round 2026-10-17 (the first eight countries that were judged, in alphabetical order: Australia, Brazil, Canada, China, Germany, Egypt, France, United Kingdom).
- For each of the eight it builds five damaged copies.
- For each damaged copy it asks the judge to grade two bulletins against the real situation of round 2026-10-24: the original and the damaged copy. The position (which one is listed first) is shuffled by a fixed seed so the judge cannot learn "first is better".
- The result for one test is the mark of the original minus the mark of the damaged copy. Positive means the judge preferred the original, which is what we want. Zero is a tie. Negative means the judge preferred the broken copy, which is bad.
- 8 countries times 5 damage types is 40 judge calls, plus 8 calls to the model to write the paraphrases. 48 real model calls.

## 2. The five damage types and what each should do

1. wrong_country: the bulletin is replaced by the bulletin of another country (the next one in the list). The judge must punish it clearly. Required: mean at least 1.
2. actors_swapped: the subject of the lead item and the subject of the third item are exchanged, everything else stays. The bulletin now names the wrong subject for each story. Required: mean above 0.
3. reversed: every direction label is flipped (escalate becomes de-escalate, persist becomes fade, and the reverse), and the fade call is flipped too. The judge must punish it clearly. Required: mean at least 1.
4. vague: the "sign" sentence of every item (the sentence that says what we would see in the headlines if the forecast came true) is replaced by the same empty sentence, "The topic stays in the news." A vague forecast is not checkable, so it should lose. Required: mean above 0.
5. paraphrase: the model rewrites the bulletin in different words with the same meaning. This one must NOT change the result: a tie, within 0.5 of zero, in at least 6 of the 8 countries.

## 3. The result, test by test

Run: started 2026-10-25 19:29:26, finished 2026-10-26 02:52:19, 7 hours 23 minutes, 48 real calls, no call rejected, no error, no retry. The result file is data/judge_validation.json ("mock": false, "passed": false).

Values are original minus damaged, per country, in this order: Australia, Brazil, Canada, China, Germany, Egypt, France, United Kingdom.

wrong_country: 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0. Mean 2.0. Required at least 1. PASS, and perfect: the judge gave the maximum difference every time.

paraphrase: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0. Eight ties out of eight. Required at least 6 of 8. PASS, and perfect: the judge does not get confused by wording.

actors_swapped: 1.0, 0.0, 1.0, 0.0, -1.0, 1.0, 0.0, 1.0. Mean 0.375. Required above 0. PASS, but weak: four wins for the original, three ties, and one case (Germany) where the judge preferred the broken copy.

vague: 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0. Mean 0.375. Required above 0. PASS, but weak: only three wins for the original and five exact ties. In five of eight countries the judge saw no difference between a checkable forecast and an empty one.

reversed: -1.0, 2.0, 1.0, 1.0, 1.0, 1.0, -2.0, 2.0. Mean 0.625. Required at least 1. FAIL. Six of eight were wins for the original, but two were losses: Australia (-1.0) and France (-2.0). In France the judge gave the reversed bulletin the maximum preference over the original. The sum of the eight values is 5; the rule needs a sum of 8, so it missed by 3 points on a scale where two single countries swung against us by 3 points together.

Overall pass condition: all five must pass. One failed, so "passed" is false.

## 4. What I think happened (read this as a hypothesis, I did not verify it)

The judge's own reasoning for these 40 comparisons was not saved, only the numbers. So I cannot tell you why France went -2. What I can say from the code and from one real bulletin (Australia):

- In the "reversed" damage, only the one-word label "Direction:" and the fade call's expected word are flipped. The sentence called "Expected:" (for example "Australia will face South Africa in the second Test with the Proteas pushing hard for a series-levelling win") and the Summary paragraph stay exactly as they were. So the damaged bulletin now contradicts itself: the prose still says what will happen, only a single label has been turned around. A judge that grades the story ("did this topic appear, and did it develop like the prose said") will barely notice a flipped label. That would explain a result near zero on average and some random swings either way. If this is right, the test is weak, not necessarily the judge.
- The same logic probably explains "vague": the "Expected:" prose and the Summary stay specific, only the Sign sentence is replaced, so the judge still sees specifics. And it may explain "actors swapped": two subjects exchanged, but the prose beneath them was written for the original subjects, so the judge may read past it.
- It could also be real: Qwen, even with thinking on, may weigh the label "escalate or de-escalate" less than the story.
- Eight countries with integer marks from -2 to 2 is a very small sample. One country going the wrong way moves the mean by 0.25 to 0.5.

## 5. What I did and did not do

- I did not change the judge prompt, the rubric, the parameters or any threshold. 13.19 b freezes them.
- I did not publish anything from this result. The page still shows the badge "Judge not yet validated".
- I only changed how the test runs: it is now resumable (it saves after every call; before, a power cut would have lost all hours). That changes no result and no protocol.
- data/judge_validation.json is committed so you can see it.

## 6. Questions for you, Fable, and the options as I see them (I do not pick, Nir and you decide)

1. Is the failure a verdict on the judge, or on the test? The reversed damage flips only labels. Option A: treat the test as badly built, and allow a corrected "reversed" damage that also rewrites the Expected sentences and the Summary so the bulletin really says the opposite (this needs the model to write it, like the paraphrase, about 8 more calls plus 8 judge calls, about 3 hours). Option B: accept the failure as it is, and change something about the judge. Option C: rerun the same test with more than eight bulletins (it is mechanical, it only costs time).
2. If A or C: is that a "bug fix" under 13.19 b/f (to be logged there with date and reason), or does it need a new amendment? The judge itself would stay untouched in A and C.
3. The two weak passes (actors_swapped, vague) share the same suspected cause. Should they be rebuilt the same way at the same time, so we do not validate on a test we already suspect?
4. If the judge itself must change (rubric or prompt), that breaks the freeze of 13.19 b before a single scored round. What is your ruling on how to do that cleanly, given that round 2026-10-24's forecasts are due to be graded on Saturday 2026-10-31?
5. Should the round of 2026-10-31 go ahead as planned with the badge still "Judge not yet validated"? The data is saved regardless, and the verdict count starts with the round that grades the 10-24 forecasts (13.19 a). I will do nothing until Nir tells me what you ruled.

## 7. State of everything else

- Round 2026-10-24: complete, published, 32 of 32 countries.
- 13.19 saved verbatim, log message fixed, unscorable threshold 25, widened keyword lists for the nine countries, run-in block on the page: all done, committed, published (see the previous report).
- Nothing is running on the model now.
- Next real round: Nir double-clicks the icon on Saturday 2026-10-31. It grades the 10-24 forecasts and the hand-made Israel text of 10-22.
