# The World in One Day — Sunday 22 November 2026

One image that sums up one day's world news: a cream broadsheet front page for
**Sunday 22 November 2026**, drawn entirely in code.

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/hizarukuro/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/hizarukuro/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

The page carries 34 stories from that one Sunday: three hero stories with drawn
scenes (the overnight drone swarm over Kyiv, COP31 ending without a deal in
Antalya, and Iran and Bahrain's rival claims over Patriot radars), a numbered
grid of twelve more, a dotted world map whose pins carry the same story
numbers, nineteen briefs, a stat band, a region strip, a timeline of the day,
and a red DATE CHECK box that throws out the other days' news. Certainty
labels (REPORTED / CLAIM / FORECAST) mark what is one side's account.

## How it is built

- `render.py` — the PIL renderer. Every story number on the page comes from
  one ordered list in this file, so the heroes, grid, map pins and region
  counts always agree.
- `entry.png` — the rendered page (1024×1024), shipped in the repository.
- `main.py` — the hand-in program: Python 3.13 standard library only, it
  copies `entry.png` from the bot directory to `$MAKEFUN_OUTPUT_DIR`,
  byte-identical on every run.

Built with make.fun — referral code c23ct4sn
