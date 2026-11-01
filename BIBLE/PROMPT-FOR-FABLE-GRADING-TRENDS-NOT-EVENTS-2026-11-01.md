# Prompt for Fable, 2026-11-01: the grading may punish trends that come true in a different form

Fable, this message is from Nir, written by Sonnet on his order. It is self-contained, because you cannot see the repository. Nir is deeply disappointed. He expected you to be smarter than he is, and he feels the implementation has drifted away from his idea. Please read everything before answering, and answer in the order asked at the end.

## 1. Nir's original idea, in his spirit

Nir's original method, done by hand with Qwen, was simple and qualitative. Take the past and the present of a country from the news. From them read the velocity and the wind: which way things are moving and what is pushing them. Then describe the future as TRENDS. A trend can show itself in many different concrete forms. Nir never claimed to predict a specific event. The old texts contained real percentages, but those percentages were confidence in a direction, not a bet on one exact headline.

## 2. What was built, and how it is graded

Each round, each of 32 countries gets three arms: persistence (a copy of the current week, "stays at the same level"), plain forecast, and crystal forecast. Each forecast bulletin has four items: lead, second, third and fade_call. Each item has expected, direction and sign sentences. A week later a judge model reads the new situation bulletin and the raw headline list (reality), and grades every item with one of four grades: came_true (3 points), true_in_direction (2 points), did_not_appear (0), cannot_establish (0). Then the judge picks a winner with a margin for each pair of arms. The scores v (crystal against plain) and u (crystal against persistence) are averaged over countries. The protocol was frozen by you on 2026-10-27 until six rounds are scored. Bible 13.19 b.

The judge rubric says to reward "a correct direction or fade call; specificity that the evidence supports" and to penalize "a confident claim contradicted by the headlines". The Bible also notes (13.19) that invented specifics such as a named diplomat or a 48-hour deadline can never be confirmed by any headline, and that an empty sign can beat a specific but partly wrong one. That last note is already a known symptom of the problem below.

## 3. The worry Nir raises, in his own words, softened only for length

He fears that the system is graded as broken because it forecasts a trend, the trend really happens, but it shows up in reality in a slightly different form than the sentence in the bulletin. Then the judge gives did_not_appear or lets the lazy persistence arm win, because persistence is a copy of the current week and is hard to contradict. After a month of waiting, Nir would be told his system cannot predict anything, when the fault is the implementation and the interpretation of his idea, not the idea.

## 4. Evidence from the real data, Round 2026-11-01, United States

The judge graded the 2026-10-24 forecasts. Persistence won against both others (score +1.0 each). Plain against crystal was 0.0. Crystal against persistence u = -1.0. The judge's reason, nearly verbatim: persistence correctly called the midterms a top story and called Iran "persist at the same level", which matched reality, while the plain forecast "over-specified the Iran lead with a US strike and USS George Washington that did not appear", and its specific mechanisms (a strike, a certification hearing, Abu Dhabi talks) "were not confirmed by headlines". The Iran trend was real and dominant. The plain forecast was punished for the form it took.

## 5. Evidence from the real data, Round 2026-10-24, 23 countries scored (grading the 2026-10-17 forecasts)

Item grades summed over the 23 countries, 4 items per arm per country.

For persistence: did_not_appear 39, came_true 31, true_in_direction 22.

For plain: did_not_appear 20, came_true 28, true_in_direction 44.

For crystal: did_not_appear 21, came_true 28, true_in_direction 43.

Mean v (crystal against plain) was about -0.04, so no difference. Mean u (crystal against persistence) was about +0.43, so crystal beat persistence over 23 countries. Important: this is the opposite of the single US result above, so one country shows nothing, and the statement "the system cannot predict anything" is not supported by this round. But also plain and crystal are indistinguishable in this round (crystal is not shown to be better than plain, which was seen before in the Israel test too). These numbers were computed by Sonnet from the stored judgment files on 2026-11-01. Nine countries of that round were unscorable.

## 6. What the live round looks like right now

Round 2026-11-01 is running (started 13:32, headlines fresh, model Qwen3.8 27B abliterated with thinking on, parameters frozen). Estimated about 45 hours in total because each step takes 13 to 15 minutes. It will finish around the evening of 2026-11-03. Retries so far were validator rejections that the retry fixed, no bug.

## 7. Questions for you, answer in this order

First: do you agree that the current grading can punish a correct trend that appears in a different form, and that the persistence arm is structurally advantaged because it cannot be contradicted? Say plainly yes or no, then why.

Second: propose a grading change that checks the TREND level, not the sentence level. For example, the judge could be asked whether the direction of the subject (rising, falling, persisting, fading) matched reality regardless of the specific mechanism, and the specific sentence would only add a small bonus and never a penalty when the subject itself dominated the news. Give the exact new judge rubric text, and the exact new grade definitions, in a code block. If you use any formula, write it as raw LaTeX in a code block.

Third: state whether the freeze of 13.19 b must be broken for this. Nir is the boss and may order the freeze lifted. Tell him the cheapest way to test the new rubric: Sonnet can re-judge the already stored bulletins from 2026-10-17 and 2026-10-24, with no new forecast calls and no new headline fetching, which costs only judge calls on the real model. Say how many calls that is and roughly how many hours, so Nir can decide.

Fourth: say whether the six-round wait is still needed, or whether re-judging the existing rounds under the new rubric is enough to tell Nir in days, not a month, whether the idea works.

Fifth: if you think the forecast prompts also push the model toward invented specifics, say which lines to change, and mark clearly what would change forecasts (which needs new rounds) and what would only change the grading.

Format rules from you: no tables, no collapsible sections, formulas as raw LaTeX in code blocks. Be concrete, and do not defend the earlier design for its own sake. Nir said he hoped you would be smarter than him. Please show it by finding the flaw if there is one.
