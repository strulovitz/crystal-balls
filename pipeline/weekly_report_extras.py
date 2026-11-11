#!/usr/bin/env python3
"""Report-only extras for the weekly report to Fable (Fable's answers 2026-11-11, item 3). No method change.
(a) how many country pairs the judge called near-identical ("strikingly similar" and the like), plus the Even verdicts;
(b) per arm (plain / crystal), the confident negatives ("I would not bet on", "unlikely", "will not") that the judge
    says came true that week: the judge sentences that mention a negative and say it was right/held/none happened.
Usage: weekly_report_extras.py ROUND_ID   (reads data/text/ROUND_ID/*.json)"""
import glob, json, re, sys
rid = sys.argv[1]
SIM = re.compile(r"strikingly similar|remarkably similar|nearly identical|near-identical|almost identical|virtually identical|largely overlapping|same (?:core |structural |basic )?(?:skeleton|architecture|structure|threads)", re.I)
NEG = re.compile(r"would not bet on|not bet on|less likely|unlikely|did not happen|none of (?:these|them) happened|ruled out|correctly ruled", re.I)
OK = re.compile(r"correct|right|held|accurate|none (?:of (?:these|them) )?happened|did not happen", re.I)
sim, even, neg = [], [], {"plain": [], "crystal": []}
for f in sorted(glob.glob(f"data/text/{rid}/*.json")):
    d = json.load(open(f)); j = d["judgment"]; o = j["order"]; c = d["code"]
    allt = " ".join([j["reading_a"], j["reading_b"], j["comparison"]])
    if SIM.search(j["comparison"]) or j["verdict_word"] == "Even":
        sim.append(c)
    if j["verdict_word"] == "Even":
        even.append(c)
    for letter, key in (("A", "reading_a"), ("B", "reading_b")):
        arm = o[letter]
        for s in re.split(r"(?<=[.!?])\s+", j[key]):
            if NEG.search(s) and OK.search(s):
                neg[arm].append((c, " ".join(s.split())[:300]))
print(f"(a) near-identical or Even: {len(sim)} of 32 pairs: {', '.join(sim)}")
print(f"    of which verdict Even: {len(even)}: {', '.join(even)}")
for arm in ("plain", "crystal"):
    print(f"\n(b) {arm}: {len(neg[arm])} judge sentences saying a confident negative held")
    for c, s in neg[arm]:
        print(f"  {c}: {s}")
