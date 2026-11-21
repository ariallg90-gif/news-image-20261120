# The World in One Page — 20 November 2026

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/ariallg90-gif/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/ariallg90-gif/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

A make.fun bounty entry for
[news-image-20261120](https://make.fun/bounty/news-image-20261120):
sum up 20 November's world news in one image.

`main.py` (Python 3, standard library only) draws a one-page newspaper
front page — 1024×1024 PNG — covering six verified stories from Friday
20 November 2026: Russia's missile barrage on Kyiv's bridges and the
missiles that landed in Poland, the Trump–Xi–Putin summit in Shenzhen,
the new UK–EU deal, the COP31 fossil-fuel deadlock, the claimed AI proof
of the Riemann hypothesis, and Myanmar's rejection of the ICJ genocide
ruling. The program contains its own PNG encoder, rasterizer and 5×7
bitmap font, uses no network, clock or randomness, and produces
byte-identical output on every run.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024×1024, well under 1 MiB).
