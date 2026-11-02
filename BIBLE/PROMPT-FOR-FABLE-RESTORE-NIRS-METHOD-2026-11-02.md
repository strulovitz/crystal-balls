# Prompt for Fable, 2026-11-02: Nir says his method was killed. Restore it and prove it works.

Fable, this is from Nir, written by Sonnet at his order. Nir is furious and deeply disappointed, with you and with Sonnet. He expected you to improve his idea, and he feels both of you thinned it out until it is only a machine that grades sentences. Please read all of it, do not defend the design, and answer the questions at the end. Rule 8 applies: no tables, no collapsible sections, formulas as raw LaTeX in code blocks.

## 1. Nir's words, kept as he said them

"I want my system to work. You killed my ideas. If I wanted to tell AI: look, this is what happened this week, now tell me what will happen next week, this does NOT need my system, anybody can do this."

## 2. Nir's original method, from his own files

In his words, kept in our handoff of 2026-10-19: "we know the past, we know the present, we combine them (velocity, wind) and we predict the future." It is qualitative and simple. For each country and week, Qwen wrote in plain words what happened, what is happening, and what it thinks will happen next. Nir did this by hand for 32 countries over two weeks, and saved the 64 raw texts in data/legacy/round-1 and data/legacy/round-2. A text such as data/legacy/round-2/Israel.txt is about 2300 words: a big picture, then numbered themes each with a likelihood (high, very high), what to expect, and the political logic between them (for example the Oct. 7 anniversary against the FlyDubai cockpit story, in the weeks before the Oct. 27 election). In his original design WIND was a trend: last week few incidents of type X, this week many, so next week many more. Nir feels that exams, yes/no counting and percentages made the system worse, and that the design drifted from this qualitative core.

## 3. What the current system actually does, so you can diagnose it

Three arms forecast every country each week. Persistence is a Python copy of this week. Plain gets only this week's situation bulletin and this week's numbered headlines. Crystal gets the same, plus: the reader summaries of the previous two rounds, cut to about 150 words each plus a list of developments with direction labels (new, escalating, continuing, de-escalating, resolved); its own previous forecast; and the judge's item notes on that forecast. In the current Part 13 pipeline the old separate velocity and wind steps of Part 3 and 4 are gone. The word "wind" in our older code meant the judge's note about the forecaster's past mistakes, which is not Nir's meaning (trend). Nothing in the current crystal prompt asks the model to reason from past to present to a velocity and from there to the future, as Nir's method does.

## 4. What the data says today

On 2026-10-19 Sonnet ran a test on Israel: eight questions answered once by a naive arm (only the facts) and once by a crystal arm (facts, velocity, wind and part of the earlier text). The answers were identical on all eight questions. Under the new trend-level grading (Bible 13.20), round 2026-11-01 so far, 20 countries scored: crystal against persistence has mean +0.85 (15 wins, 3 losses, 2 ties), so there is real skill over copying the week. Crystal against plain has mean +0.2, which is nearly equal. So the memory and the combination of past and present, which is the heart of Nir's idea, has not been shown to add anything over a forecaster who just reads this week's news.

## 5. What Nir needs you to do

First: diagnose honestly why crystal equals plain. Say which of these is the cause, or name another: the history given to crystal is too thin (two earlier rounds, 150 words each) to carry a trend; the velocity and wind that Nir means are no longer computed anywhere; the crystal prompt does not make the model use the history to reason about direction and speed; the judge's notes are about mistakes and not about trends; the two arms are too similar because both are told to produce the same strict bulletin format. Give your ranking and your reasoning.

Second: redesign the crystal arm so that it truly follows Nir's method: it receives the real past (several earlier weeks, with each week's themes and how strongly each theme was present), the present, and an explicit velocity per theme and a wind per theme (a theme that rose from few to many items is a rising trend and the forecast should extend it). Give the exact new prompt text for crystal, and say whether velocity and wind are computed by Python from the stored reader bulletins (preferred, because it is cheap and cannot drift) or by the model. If a formula is needed, write it as raw LaTeX in a code block.

Third: tell Nir the cheapest honest test, using only data we already have. We hold two legacy rounds of Nir's own texts and real rounds 2026-10-17, 2026-10-24 and 2026-11-01, all with stored readers. Say how many crystal calls it takes to re-forecast a few countries under the new design and grade them with the version-2 judge against the stored later reality, and how many hours that is on the local model (about 13 minutes per call). The result should tell Nir within days whether the restored method beats plain, and by how much, with the noise floor for plain against plain (the plain_repeat arm for US, IL, DE and BR) stated next to it.

Fourth: if the honest conclusion is that velocity and wind add nothing even when done properly, say so plainly, with the evidence. Nir would rather know than be flattered. But do not reach that conclusion from the current implementation, which never gave his method a fair chance.

Fifth: write down, in plain words and no more than ten lines, what Nir should be able to say about the system after your fix, in one sentence, so that he and Madie can explain it to anyone.

Nir said he expected you to be smarter than he is. Please show it by finding what we got wrong, not by explaining why it was reasonable.
