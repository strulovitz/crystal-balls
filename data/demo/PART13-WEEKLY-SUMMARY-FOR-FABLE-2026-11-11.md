# Report for Fable, 2026-11-11: first weekly round under 13.22/13.24 (round id 2026-11-09)

Fable, this is a normal-sized report, written by Sonnet from all 32 judge essays, with the cross-sections and my own read of what works and what does not. The full essays are in data/text/2026-11-09/<CODE>.json (field "judgment") if you want any one of them verbatim; ask Nir.

## What ran
Run Round icon (text_round --weekly), all four steps for all 32 countries, about 28 hours on the local model (first file 11-09 22:29, last 11-11 02:26). The judge graded the 11-01 forecasts against the week to 11-09: the first forecasts written before their week. Nir published; it is live. Method frozen (13.24, round 1 of 6).

## The numbers
Crystal preferred 20, plain 8, even 4. Last time (catch-up, stored headlines) it was 18 / 8 / 6. So crystal wins about 60 percent both times, plain about a quarter, the rest a draw.

Position bias check: the verdict word was A 14, B 14, Even 4, and the A/B order is random. Crystal won 12 of 19 when it was shown as A and 8 of 13 when shown as B (both about 62 percent). I see no position bias.

## When crystal wins (examples)
Ukraine: crystal predicted a multi-day Kyiv blackout, the cumulative energy and economic squeeze, European leaders taking a visible role (G7, Merz ultimatum), the domestic corruption friction, and Russian petrol rationing; the judge said these "landed with high precision". Plain was more generic, with a few specific hits crystal missed (cyber attack on alert apps, Black Sea ships).
Iran: crystal correctly named the France cyber story, the IRGC missile-range announcement, the US land-route task force and the post-midterms diplomatic shift. Where the world has many concrete moving parts, crystal's specificity pays.
Also crystal: Russia, China, Japan, US, South Africa, Singapore, Venezuela, Vietnam, Taiwan, Germany, France.

## When plain wins (examples)
Israel: crystal said Netanyahu would be mandated first with Eisenkot as fallback; Eisenkot was tasked directly on Nov 7. The judge called plain's neutrality on the mandate "a genuine advantage" because it was the biggest event of the week.
Britain: crystal wrote "I would not bet on the Brand trial reaching a verdict"; the verdict and sentencing were the week's dominant story. A confident negative is the costliest kind of error.
Canada: crystal listed a long menu of small concrete items (Cohere follow-up, Wealthsimple valuation, Microsoft buyout offers, avalanche dogs...) that mostly did not happen; plain stayed general and its confidence labels matched reality.
Iraq: crystal said "Security will be quiet" and "the US will remain a quiet presence"; the real week was the Kurdish power-sharing collapse, drone strikes and a gas-field blackout. Also plain: Brazil, Italy, India, Turkey.

## Cross-section: the pattern
1. Crystal wins by being specific and loses by being specific. It gains when the situation is a continuing storyline with known actors, and loses when it commits to one outcome (who gets the mandate) or to a confident "will not happen".
2. Over-specification: the Canada and Britain essays both complain about long menus of invented-sounding details. The plain forecast's hedged probability words ("probable", "possible") are praised for calibration in about a quarter of the essays.
3. Shared blind spot: in many essays the judge says both forecasts missed the week's single biggest story (Iraq: Kurdish deal collapse; Canada: the federal budget; Britain: the cybersecurity and power-grid cluster; Gaza: the flooding). Both forecasts extend the previous week, and neither predicts a rupture. That is expected, not a bug, but worth saying plainly on the page.
4. Numbers are the weak spot: crystal said Iran oil would be $110-125 and plain said mid-70s to low 80s; the real price was under $90, so plain was close and crystal far off. A number invites a clear miss.

## Problems I want you to look at
a. The judge is the same local Qwen model, and the "week that actually happened" it judges against is the model's own summary of the headlines, not the headlines themselves. So the judge checks a forecast against another text written by the same model. Errors or omissions in the measurement flow straight into the verdict. (I cannot tell from here how large this effect is.)
b. Some essays mention events I cannot check (midterm results, the Brand sentencing, Eisenkot being tasked). They are after my knowledge, so I cannot confirm them; I only report what the essays say.
c. The "Even" verdicts (AU, CD, EG, ID) have the least informative essays: "strikingly similar". When the two forecasts barely differ, crystal adds little; it might be worth counting how often the two are near-identical.
d. Nothing failed or needed a retry that I know of; every country shows all four steps done.

## One question for Nir and you
Crystal beats plain about 60 percent and loses mostly by committing too hard. Is that the result you wanted to show readers as it is, or do you want the page to say plainly that crystal is bolder, wins more, and misses harder? That is a wording choice only; the method stays frozen.
