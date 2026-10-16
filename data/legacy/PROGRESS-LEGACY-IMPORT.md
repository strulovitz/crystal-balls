# Legacy forecast import: progress and resume point

Last updated: end of Nir's session (Haiku 5.5). Resume from here.

## Round 1 (dates 2026-09-15 to 2026-10-01): 21 of 32 saved

Saved (all Qwen 3.8 27B abliterated), in data/legacy/round-1/ with MANIFEST.md:
1. Israel (2026-09-15)
2. United States (2026-09-15)
3. Russia (2026-09-16)
4. China (2026-09-16)
5. DR Congo (2026-09-16)
6. Iran (2026-09-16)
7. Ukraine (2026-09-20)
8. North Korea (2026-09-20)
9. Venezuela (2026-09-20)
10. Canada (2026-09-21)
11. Iraq (2026-09-21)
12. Saudi Arabia (2026-09-21)
13. Indonesia (2026-09-26)
14. Chile (2026-09-26)
15. Peru (2026-09-26)
16. Vietnam (2026-09-26)
17. France (2026-09-26)
18. India (2026-09-30)
19. Egypt (2026-10-01)
20. Turkey (2026-10-01)
21. South Africa (2026-10-01)

Still MISSING from round 1 (11 countries, text not yet given by Nir):
- Japan
- South Korea
- Taiwan
- Germany
- Netherlands
- Switzerland
- Singapore
- Brazil
- Australia
- United Kingdom
- Italy

Dates for these 11 are not known yet. Ask Nir for each country's date and model, then the full text.

## Round 2 (dates 2026-10-02 to 2026-10-14): 0 of 32 saved

Round 2 has not started. Nir said round 2 starts with Israel 02-10-2026. A round-2 Canada (07-10-2026) was mentioned once, then Nir said he would check; it is NOT saved. Ask Nir before saving anything for round 2.

## Rules to keep

- Save the text exactly as pasted. Never edit or summarize.
- One country at a time. Ask for the text, then save, add the MANIFEST row, commit, and push after every file.
- Use the exact country name from the list as the filename.
- Ask Nir before saving any country whose date or round is unclear.
- Keep messages short, with emojis.

## Resume steps for next session

1. git -C /home/nir/crystal-balls pull
2. Read this file and data/legacy/round-1/MANIFEST.md
3. Confirm the count: ls data/legacy/round-1/*.txt | wc -l (should be 21)
4. Ask Nir for the next missing country, its date, and its text
