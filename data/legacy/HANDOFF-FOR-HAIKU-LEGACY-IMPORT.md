# Handoff: collecting the legacy forecast texts (for Claude Haiku)

Nir is pasting 32 old, hand-made forecast texts (one per country) for
**round 1**, then 32 more for **round 2**. He already gave the first one
(Israel, round 1) directly to Sonnet; it is already saved. Start from the
**second** country of round 1.

Your job is narrow and mechanical: ask Nir for each text one at a time,
in a fixed format, save it EXACTLY as pasted, record a one-line note
about it, and commit+push after every single file. Never summarize,
never paraphrase, never "clean up" the text. Never skip ahead without
being given the text.

## The 32 country names, in this exact order (use these exact names as
filenames — a few short aliases also work, but prefer the exact name)

United States, Russia, China, DR Congo, Iran, Israel, Ukraine, North
Korea, Venezuela, Canada, Iraq, Saudi Arabia, Japan, South Korea, Taiwan,
Germany, Netherlands, Switzerland, Singapore, Brazil, Australia,
Indonesia, Chile, Peru, Vietnam, France, United Kingdom, Italy, India,
Egypt, Turkey, South Africa

Nir does them in his own order (Israel first, because he's Israeli), not
necessarily the order above. That's fine — just ask him which country is
next; don't assume the list order.

## What Nir already told Sonnet about these two rounds

- Round 1: first file was "Israel 15-09-2026 Qwen" (DD-MM-YYYY, so
  September 15, 2026), last file was "South Africa 01-10-2026 Qwen".
- Round 2: first file was "Israel 02-10-2026 Qwen", last file was
  "South Africa 14-10-2026 Qwen".
- ALL of these texts, in both rounds, were written by the same model:
  Qwen 3.8 27B abliterated (Nir's own local model). He said so explicitly
  — you do not need to ask about the model again unless a file is
  different.
- Each text is in free-form prose, different format every time (headers,
  percentages, bullet lists, whatever the model felt like that day).
  This is expected. Do not try to normalize the format.

## Exactly what to ask Nir, one country at a time

For each remaining country (31 left in round 1, then all 32 in round 2),
ask in this style, one question, wait for the answer:

> "Round 1, country N of 32: which country is next?"

Then:

> "What date did [Country]'s round 1 text get written? (DD-MM-YYYY is
> fine, that's how Nir writes dates — September 15 2026 = 15-09-2026.)
> And is it still Qwen 3.8 27B abliterated, or a different model this
> time?"

Then:

> "Please paste the full text now."

## Saving the file

1. Save the pasted text **exactly as given** — same line breaks, same
   punctuation, same em-dashes/smart quotes if present, same everything.
   Do not add a summary line at the top. Do not fix typos. Do not reformat
   bullet lists into paragraphs or vice versa. If Nir's paste includes a
   stray greeting like "hello :-)" at the very top, keep it — it doesn't
   hurt anything and preserving the original is more important than
   tidiness.
2. Save it as `data/legacy/round-1/<CountryName>.txt` (round 2 goes in
   `data/legacy/round-2/<CountryName>.txt`), using the exact country name
   from the list above as the filename (e.g. `data/legacy/round-1/Iran.txt`).
3. Append one row to `data/legacy/round-1/MANIFEST.md` (or round-2's own
   MANIFEST.md): `| Country | Written on (YYYY-MM-DD) | Model |`
4. Commit and push IMMEDIATELY after every single file — never batch
   multiple countries into one commit. If OpenCode or the terminal
   crashes between files, nothing is lost beyond the one file in
   progress. Use a plain `git add -A && git commit -m "Legacy round 1:
   <Country>" && git push` each time.
5. Tell Nir the running count ("That's 5 of 32 for round 1 saved.") so he
   can track progress and knows it's safe to take breaks.

## When round 1 is fully done (32 of 32)

Say so clearly to Nir, then start round 2 the same way, using
`data/legacy/round-2/` and asking "Round 2, country N of 32: which
country is next?"

## When BOTH rounds are fully done (64 files total)

1. Do a final check: `ls data/legacy/round-1/*.txt | wc -l` should say 32,
   same for round-2. If either is short, tell Nir which countries are
   missing (compare against the 32-name list above) before declaring done.
2. Open `HANDOFF-FOR-SONNET-LEGACY-IMPORT.md` (same folder as this file)
   and confirm its two round dates (2026-10-01 for round 1, 2026-10-14
   for round 2) still match what Nir told Sonnet. If Nir corrects either
   date while you're working, update that file's two `--round` dates to
   match and say so in your final message.
3. Tell Nir plainly: "Both legacy rounds are fully saved and pushed to
   GitHub (64 files, 32 per round). Please restart OpenCode and switch
   back to Claude Sonnet 5, then say: 'read
   HANDOFF-FOR-SONNET-LEGACY-IMPORT.md and continue.'"

## Rules, no exceptions

- Never invent, guess, or fill in a country's text yourself. If Nir
  hasn't given you one yet, it does not exist yet.
- Never reorder, skip, or batch-request multiple countries at once — one
  at a time, in the order Nir wants to give them.
- Never edit a saved .txt file after the fact unless Nir explicitly says
  a paste was wrong and gives you the correction.
- Commit and push after every file. This is the most important rule —
  it is what makes a mid-session crash harmless.
