# Crystal Balls

Crystal Balls is a free, open, run-at-home system that forecasts the
news of the coming week for 32 influential countries and shows the
result as three transparent globes nested inside each other, like
matryoshka dolls: the inner globe is the situation two rounds ago, the
middle globe is the previous round, and the outer bright globe is the
forecast for the coming week. Every forecast comes with concrete,
scoreable yes/no statements, so the page can show honestly whether
Crystal Balls actually beats a naive forecast, round after round.

Live page: https://www.strulovitz.org/crystal-balls/

Read the Bible in `BIBLE/`, starting with `BIBLE/part-00-mission.md`.

## Run it yourself

```
git clone https://github.com/strulovitz/crystal-balls.git
cd crystal-balls && bash scripts/install.sh
```

Set your model's URL and name in `config/settings.env`, then double-click
the "Crystal Balls — Run Round" desktop icon it creates.

Author and owner: Nir Strulovitz.

License: the code is MIT (see `LICENSE`). The data and written texts
(forecasts, summaries, explanations) are CC BY 4.0. Everything in this
project is free; nothing is ever paywalled.

A forecaster who always says 50 percent scores a Brier score of 0.25;
lower is better. See [`data/scorecard.json`](data/scorecard.json) for how
Crystal Balls is actually doing, round after round.
