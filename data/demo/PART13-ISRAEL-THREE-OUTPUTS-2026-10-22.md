# Part 13: the three real Israel demonstration outputs, verbatim (2026-10-22)

Produced by scripts/part13_israel_demo.py on the local Qwen model (Ollama). The log of the six real calls is below, then the three outputs exactly as printed.

## Log of the six real calls

```
19:20:56   [IL legacy_reader] attempt 1: 1010.1s, prompt_tokens=4342, completion_tokens=7479
19:20:56 Imported Israel 2026-09-15 from text in 1010s (unscorable: horizon not covered by any collection)
19:20:56 PROGRESS call 1 of 6 done (16%): import 2026-09-15. Started 19:04, elapsed 16 min, estimated remaining 84 min.
19:33:43   [IL legacy_reader] attempt 1: 767.0s, prompt_tokens=4894, completion_tokens=5229
19:33:43 Imported Israel 2026-10-02 from text in 767s (unscorable: horizon not covered by any collection)
19:33:43 PROGRESS call 2 of 6 done (33%): import 2026-10-02. Started 19:04, elapsed 29 min, estimated remaining 59 min.
19:44:25   [IL legacy_reader] attempt 1: 642.0s, prompt_tokens=5440, completion_tokens=4412
19:44:25 Imported Israel 2026-10-22 from text in 642s (scorable)
19:44:25 PROGRESS call 3 of 6 done (50%): import 2026-10-22. Started 19:04, elapsed 40 min, estimated remaining 40 min.
19:58:13   [IL reader] attempt 1: 826.9s, prompt_tokens=3456, completion_tokens=5926
19:58:13 PROGRESS call 4 of 6 done (66%): reader Israel 10-17, 826s. Started 19:04, elapsed 54 min, estimated remaining 27 min.
20:08:29   [IL crystal_forecast] attempt 1: 616.1s, prompt_tokens=5891, completion_tokens=3485
20:08:29   [IL crystal_forecast] attempt 1 rejected: Bulletin validation failed:
  - lead.sign: expected a sentence of 4 to 40 words
  - second.sign: expected a sentence of 4 to 40 words
  - third.expected: expected a sentence of 4 to 40 words
20:14:17   [IL crystal_forecast] attempt 2: 348.1s, prompt_tokens=7287, completion_tokens=2975
20:14:17 PROGRESS call 5 of 6 done (83%): crystal Israel 10-17, 964s. Started 19:04, elapsed 70 min, estimated remaining 14 min.
20:23:09   [IL judge] attempt 1: 531.8s, prompt_tokens=4262, completion_tokens=3473
20:23:09 PROGRESS call 6 of 6 done (100%): judge dry run, 531s. Started 19:04, elapsed 79 min, estimated remaining 0 min.
```

## 1. Reader on the 2026-10-17 Israel headlines

```
READER (10-17 Israel):
{
 "summary": "This week in Israel was dominated by a sharp escalation in West Bank settler violence during the annual olive harvest. Masked settlers attacked European diplomats, a US journalist, and Palestinian farmers across multiple villages, burning olive trees, torching cars, and setting fire to a mosque. The United States, China, and Belgium all called on Israel to crack down, while the US envoy demanded a formal probe into the journalist's injury. In Gaza, Israel halted commercial goods from entering the territory, prompting warnings of catastrophic malnutrition as food supplies thinned and the UN flagged fragile gains against starvation. Ahead of the parliamentary election in roughly two weeks, polls show a tight contest between Netanyahu and Gaby Eizenkot, with Israeli voters described as tired rather than engaged; a former security chief sued Netanyahu over October 7 defamation claims. Internationally, Italy opened a probe naming Defense Minister Katz over the Gaza flotilla incident, Colombia inaugurated its embassy in Jerusalem and restored a free trade deal, and a research team revealed that an Israeli ad-tech firm had used zero-click malware to compromise Al Jazeera devices. The IDF's pattern of closing investigations into Palestinian killings without public findings also drew renewed scrutiny.",
 "mood": "escalating",
 "intensity": 7,
 "developments": [
  {
   "subject": "West Bank settler violence (olive harvest)",
   "what_happened": "Masked settlers attacked European diplomats, a US journalist, and Palestinian farmers across multiple villages, burning trees, torching cars, and setting fire to a mosque, prompting US, Chinese, and Belgian calls for Israel to act.",
   "coverage": "dominant",
   "direction": "escalating",
   "headline_ids": [
    5,
    6,
    7,
    9,
    15,
    16,
    18,
    20,
    21,
    22,
    26,
    31,
    33,
    40,
    41,
    46,
    47,
    48,
    62,
    89,
    91
   ]
  },
  {
   "subject": "Gaza commercial goods halt and food crisis",
   "what_happened": "Israel stopped commercial goods from entering Gaza after merchants suspended coordination, and the health ministry and UN warned of catastrophic malnutrition as supplies thinned.",
   "coverage": "dominant",
   "direction": "escalating",
   "headline_ids": [
    32,
    45,
    59,
    66,
    67,
    68,
    75
   ]
  },
  {
   "subject": "Israeli parliamentary election",
   "what_happened": "Polls two weeks before the vote show a tight race between Netanyahu and Eizenkot, with voters described as fatigued; a former security chief sued Netanyahu over October 7 defamation, and Arab-led parties are positioned as potential kingmakers.",
   "coverage": "dominant",
   "direction": "continuing",
   "headline_ids": [
    3,
    12,
    23,
    27,
    30,
    35,
    42,
    65,
    70,
    77,
    79,
    86,
    88
   ]
  },
  {
   "subject": "International diplomatic pressure",
   "what_happened": "The US, China, Belgium, and Italy each issued public calls for Israel to address settler violence or the flotilla incident, while Colombia opened its Jerusalem embassy and restored a free trade deal, showing a mixed but active diplomatic front.",
   "coverage": "dominant",
   "direction": "escalating",
   "headline_ids": [
    1,
    4,
    24,
    34,
    39,
    43,
    49,
    55,
    57,
    63,
    64,
    69,
    81,
    87
   ]
  },
  {
   "subject": "Gaza ceasefire and military strikes",
   "what_happened": "Despite the ceasefire arrangement, Israeli drone and air strikes killed at least seven Palestinians in Gaza City over the week, raising questions about the deal's durability.",
   "coverage": "regular",
   "direction": "continuing",
   "headline_ids": [
    14,
    52,
    84
   ]
  },
  {
   "subject": "Israeli spyware and ad-tech espionage",
   "what_happened": "Researchers revealed that an Israeli ad-tech firm used a zero-click malware technique to plant spyware on Al Jazeera's devices, and suspected Israeli online operations raised alarm in Iran and Lebanon.",
   "coverage": "regular",
   "direction": "new",
   "headline_ids": [
    56,
    60,
    73,
    83,
    85
   ]
  },
  {
   "subject": "Lebanon border and Hezbollah",
   "what_happened": "Lebanon sent a military delegation to US talks to press for a halt to Israeli attacks, Hezbollah claimed ownership of confiscated explosives meant for Israel, and Israel's Yellow Line in southern Lebanon continued to reshape the border area.",
   "coverage": "regular",
   "direction": "continuing",
   "headline_ids": [
    11,
    61,
    72,
    90
   ]
  },
  {
   "subject": "IDF investigation transparency",
   "what_happened": "A BBC Verify review found hundreds of IDF investigations into Palestinian killings had been closed without any public outcome, and Israeli rights groups reported a surge of rubber-bullet injuries among Palestinian detainees.",
   "coverage": "regular",
   "direction": "continuing",
   "headline_ids": [
    51,
    53,
    54,
    58,
    74
   ]
  },
  {
   "subject": "Syria and Druze community",
   "what_happened": "Netanyahu said he spoke with Syria's leader about the Druze community's plight, and Israeli raids and arrests in southern Syria pushed the local population to the brink.",
   "coverage": "occasional",
   "direction": "continuing",
   "headline_ids": [
    28,
    38
   ]
  },
  {
   "subject": "Colombia-Israel diplomatic thaw",
   "what_happened": "Colombia inaugurated its embassy in Jerusalem and restored a free trade agreement with Israel, marking a significant re-engagement after a period of strained relations.",
   "coverage": "occasional",
   "direction": "new",
   "headline_ids": [
    57,
    63,
    87
   ]
  },
  {
   "subject": "West Bank settlement and PA funding",
   "what_happened": "Israel blocked Palestinian Authority funding, straining the West Bank's healthcare system, while a hardline rabbi's ruling on seized Palestinian olives sparked controversy and a plan to reopen settler Route 463 threatens to isolate Ramallah.",
   "coverage": "occasional",
   "direction": "continuing",
   "headline_ids": [
    21,
    44,
    91
   ]
  }
 ],
 "gone": [
  "FlyDubai cockpit attack",
  "Oct. 7 warning leaks",
  "Gulf coordination",
  "Arab-party legal fight",
  "Shipping and economy",
  "Sports friction",
  "Security alert level"
 ],
 "collection_quality": {
  "rating": "adequate",
  "note": "The headlines cover the main Israeli stories—West Bank settler violence, Gaza food crisis, elections, and international diplomacy—thoroughly, though internal cabinet dynamics and the economy beyond the Gaza goods halt are lightly represented."
 },
 "relevant_headlines": 91,
 "unscorable": false,
 "unscorable_reason": null
}
```

## 2. Crystal forecast with the legacy history (the display fields follow)

```
CRYSTAL FORECAST (10-17 Israel):
{
 "lead": {
  "subject": "Israeli parliamentary election – final week",
  "expected": "The last days before the October 27 vote will feature a prime-time debate between Netanyahu and Eizenkot, a flood of same-day polls, and both camps scrambling for the undecided middle as the tight race enters its closing stretch.",
  "direction": "escalate",
  "sign": "Headlines will carry a nationally televised debate, a wall of last-minute polls, and both leaders on separate late-night talk shows the same night."
 },
 "second": {
  "subject": "West Bank settler violence during olive harvest",
  "expected": "Masked settler groups will carry out at least one new high-profile attack on farmers, a journalist, or a foreign delegation, and the government will announce a formal crackdown and 48-hour investigation deadline before polls close.",
  "direction": "escalate",
  "sign": "Headlines will name a specific village and a named diplomat as the latest victim, show settlers torching trees, and quote a minister promising arrests within 48 hours."
 },
 "third": {
  "subject": "Gaza food crisis from commercial goods halt",
  "expected": "The suspension of commercial imports will push malnutrition admissions to a new weekly high, trigger a UN emergency appeal, and force both Netanyahu and Eizenkot to announce competing food-aid pledges before the vote.",
  "direction": "escalate",
  "sign": "Headlines will cite a specific malnutrition figure from UNRWA, name the Kerem Shalom crossing where convoys are queued, and quote a minister pledging a food-aid package within 72 hours."
 },
 "fade_call": {
  "subject": "Israeli ad-tech spyware on Al Jazeera",
  "expected": "fade",
  "sign": "The zero-click malware story will appear only in a technology column rather than front-page leads, and no parliamentary committee or follow-up forensic report will be announced before the election."
 },
 "surprise": {
  "subject": "Last-minute Eizenkot–Arab-party coalition pact",
  "expected": "Eizenkot's camp will announce a formal coalition agreement with one or more Arab-led parties within 48 hours of the vote, reframing the election as a two-bloc contest and triggering a late polling surge for the centrist ticket.",
  "chance": "medium"
 },
 "summary": "Israel enters its final pre-election week with a razor-thin contest between Netanyahu and Eizenkot, and the stakes feel existential to voters on both sides. The olive-harvest season will keep producing settler-violence headlines as masked groups attack farmers, journalists, and diplomats, and the government will be pressed to announce a crackdown before polls close. In Gaza, the halt of commercial goods will push malnutrition into crisis territory, and the UN will issue its strongest language yet about starvation. A wave of international statements from Washington, Beijing, and Brussels will frame the election as a choice for the Middle East. The spyware revelation and the Colombia embassy opening will register as notable but secondary. The most probable surprise is a last-minute coalition announcement that redraws the contest in the final 48 hours. The overall mood will be tense, fatigued, and volatile."
}
```

## 2b. Crystal display fields

```
CRYSTAL DISPLAY:
{
 "headline": "Israel Votes as Settlers Burn Olives and Gaza Starves",
 "emojis": [
  "🗳️",
  "🔥",
  "🌾"
 ],
 "emoji_reasons": [
  "The October 27 parliamentary election is the single dominant story of the week, with Netanyahu and Eizenkot locked in a dead heat.",
  "West Bank settler attacks on diplomats, journalists, and farmers will keep producing flare-ups and government responses throughout the campaign.",
  "The olive harvest is both the seasonal backdrop for settler violence and the symbol of Gaza's deepening food crisis as commercial goods stop flowing in."
 ],
 "tldr": "Israel's Oct 27 vote will dominate the week, with a heated final debate and a wall of polls. Settler violence in the West Bank and Gaza's food crisis will escalate into campaign flashpoints. A surprise coalition deal between Eizenkot and Arab parties is the wildcard.",
 "eli5": "Israel is about to hold a really close election between two leaders, Netanyahu and Eizenkot, and everyone is fighting hard in the last few days before people vote. At the same time, in the West Bank, groups of settlers keep attacking Palestinian farmers and even diplomats during the olive-harvest season, which is making a big mess right before the vote. In Gaza, food trucks stopped crossing the border, so hospitals are reporting more children with severe malnutrition, and the UN is sounding the alarm.\n\nWhy is all of this happening at once? Because the olive harvest is a yearly event that always stirs up tension, and the food halt in Gaza landed in the worst possible week for the ruling government. The election is the main event, and everything else is being pulled into the campaign.\n\nWhat will probably happen next? Expect the televised debate, a storm of last-minute polls, at least one more dramatic settler attack, and both candidates announcing food-aid plans to compete with each other. International leaders in the US, China, and Europe will keep issuing statements, but the vote itself is the story.\n\nWhat would be a surprise? If Eizenkot suddenly announces a formal alliance with the Arab-led parties just a day or two before the vote, it would flip the whole frame of the race and could shift the result. That is not the most expected outcome, but the polls are tight enough that a last-minute deal could change everything."
}
```

## 3. Judge dry run: legacy 2 (2026-10-02 hand-made forecast) and its persistence opponent, graded against the 10-17 reader bulletin

```
JUDGE DRY RUN:
{
 "graded_round": "2026-10-02",
 "elapsed_days": 15,
 "label_order": {
  "X": "crystal",
  "Y": "persistence"
 },
 "per_arm": {
  "crystal": {
   "items": {
    "lead": {
     "grade": "did_not_appear",
     "evidence": "The reality section explicitly lists 'Oct. 7 warning leaks' under 'No longer in the headlines,' and while the Oct. 7 anniversary (Oct 7) predates this round, no headline describes state commemorations or opposition rallies over Egyptian warning leaks."
    },
    "second": {
     "grade": "did_not_appear",
     "evidence": "The reality section explicitly lists 'FlyDubai cockpit attack' under 'No longer in the headlines,' and no headline in the collection references cockpit-security rules, a hero-pilot award, or a Gulf diplomatic tug-of-war over the Omani copilot."
    },
    "third": {
     "grade": "true_in_direction",
     "evidence": "Headlines [27], [42], [77], and [70] confirm a tight Netanyahu-versus-Eizenkot election campaign dominates, but the specific predicted signs—hero-pilot campaign ads, a Ben-Gvir Al-Aqsa visit, and a Smotrich fuel-subsidy announcement—appear in none of the 91 headlines."
    },
    "fade_call": {
     "grade": "did_not_appear",
     "evidence": "The reality section explicitly lists 'Sports friction' under 'No longer in the headlines,' contradicting the prediction that Europa League boycott debates would persist."
    }
   },
   "archer_note": "The bulletin completely missed the West Bank olive-harvest settler violence that dominated nearly a quarter of all headlines and the Gaza commercial-goods halt that triggered a food-crisis narrative. It also missed the international diplomatic pressure cluster (US, China, Belgium, Italy) and the Colombia embassy opening, which were prominent new stories. Its main thesis—that the Oct. 7 anniversary and FlyDubai aftermath would drive the week—was wrong on both anchor events; the election was correctly identified as central but was mis-framed as a reaction to the anniversary rather than a standalone contest."
  },
  "persistence": {
   "items": {
    "lead": {
     "grade": "did_not_appear",
     "evidence": "The reality section explicitly lists 'FlyDubai cockpit attack' under 'No longer in the headlines,' directly contradicting the prediction that it would persist at the same volume."
    },
    "second": {
     "grade": "did_not_appear",
     "evidence": "The reality section explicitly lists 'Oct. 7 warning leaks' under 'No longer in the headlines,' directly contradicting the prediction that it would persist at the same volume."
    },
    "third": {
     "grade": "came_true",
     "evidence": "Headlines [14], [52], [59], [66], and [84] all confirm the Gaza war and ceasefire remain a dominant, continuing story with strikes, supply halts, and malnutrition warnings."
    },
    "fade_call": {
     "grade": "did_not_appear",
     "evidence": "The reality section explicitly lists 'FlyDubai cockpit attack' under 'No longer in the headlines,' contradicting the fade call that it would still be reported at the next collection."
    }
   },
   "archer_note": "The bulletin missed the West Bank settler violence and olive-harvest attacks, the Gaza commercial-goods halt and food crisis, and the parliamentary election as the dominant political story. It also missed the international diplomatic cluster and the spyware/ad-tech espionage revelation, both of which were significant new developments. Its main thesis of 'more of the same' was structurally wrong because both of its two anchor stories (FlyDubai and Oct. 7 warnings) faded out entirely while three new dominant stories emerged."
  }
 },
 "verdicts": [
  [
   {
    "first": "crystal",
    "second": "persistence",
    "score": -1.0,
    "reason": "Bulletin X at least identified the election as the central political story in its third item, pointing toward the actual dominant narrative even though its specific mechanisms were wrong, whereas Bulletin Y only correctly predicted that Gaza would persist, which is the least informative default call. The decisive difference is that X's framework, despite its errors, gestured toward the forward-looking political contest that actually dominated, while Y's 'more of the same' thesis was falsified by the fading of both its anchor stories."
   }
  ]
 ],
 "scores": {
  "crystal_vs_persistence": 1.0
 }
}
```

