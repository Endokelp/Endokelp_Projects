#set page(
  paper: "us-letter",
  margin: (x: 0.55in, y: 0.55in),
  fill: rgb("#faf8f3"),
)
#set text(
  font: "New Computer Modern",
  size: 10pt,
  fill: rgb("#1a1a1a"),
)
#set par(justify: true, leading: 0.58em)

#let ink = rgb("#1a1a1a")
#let charcoal = rgb("#3a3a38")
#let sage = rgb("#5b6b58")
#let rule-line = line(length: 100%, stroke: 1pt + ink)
#let thin-rule = line(length: 100%, stroke: 0.5pt + charcoal)

// ---------- Header ----------
#text(size: 25pt, weight: 700, fill: ink)[Overfit-Aware Signals]
#v(-1pt)
#text(size: 12.5pt, style: "italic", fill: charcoal)[
  Evaluating cross-sectional equity factors with DSR and PBO
]
#v(3pt)
#text(size: 9.6pt, fill: sage)[
  Anish Venkatesan #h(4pt) endokelp.com #h(4pt) Python research package
]
#v(6pt)
#rule-line
#v(9pt)

// ---------- What it is ----------
#grid(
  columns: (1fr,),
  row-gutter: 6pt,
)[
  #text(weight: 700, size: 10.6pt)[What it is]
  #v(3pt)
  Most backtests report one Sharpe ratio and stop. Under multiple testing that number is easy to inflate. This package runs three real cross-sectional signals, 12-1 momentum, one-month reversal, and low-vol, through purged CV, combinatorial purged CV, Deflated Sharpe Ratio (Bailey and Lopez de Prado, 2014), and Probability of Backtest Overfitting via CSCV. The product is a per-signal PASS or FAIL verdict under fixed thresholds, not a vanity Sharpe chart.
]

#v(12pt)

// ---------- Results ----------
#text(weight: 700, size: 10.6pt)[Results]
#text(size: 8.6pt, fill: charcoal)[  (live panel demo - non-claim / survivorship-biased)]
#v(4pt)
#text(size: 9pt)[
  50 liquid US equities, monthly rebalance, 2005-01 to 2026-06, long-only top-5, 10 bps one-way costs. DSR threshold \u{2265} 0.95, PBO threshold \u{2264} 0.05. PBO is set-level. Table uses n\_trials = 3; research log = 9. Absolute Sharpes are optimistic illustration, not a deployment claim. Prefer `synth` offline.
]
#v(7pt)

#table(
  columns: (1fr, auto, auto, auto, auto, auto, auto),
  align: (left, right, right, right, right, right, center),
  stroke: none,
  inset: (x: 7pt, y: 7pt),
  table.hline(stroke: 1pt + ink),
  table.header(
    text(weight: 700)[signal],
    text(weight: 700)[Sharpe],
    text(weight: 700)[CAGR],
    text(weight: 700)[median block Sharpe],
    text(weight: 700)[DSR],
    text(weight: 700)[PBO],
    text(weight: 700)[verdict],
  ),
  table.hline(stroke: 0.6pt + charcoal),
  [momentum], [0.921], [0.183], [0.925], [0.999], [0.041], text(weight: 700, fill: ink)[PASS],
  [reversal], [0.453], [0.081], [0.526], [0.860], [0.041], text(weight: 700, fill: ink)[FAIL],
  [lowvol],   [0.798], [0.100], [0.831], [0.994], [0.041], text(weight: 700, fill: ink)[PASS],
  table.hline(stroke: 1pt + ink),
)

#v(12pt)

// ---------- Methods + Caveat side by side ----------
#grid(
  columns: (1.15fr, 1fr),
  gutter: 18pt,
)[
  #text(weight: 700, size: 10.6pt)[Methods]
  #v(4pt)
  #set list(marker: [--], indent: 2pt, spacing: 7pt)
  - Purged K-Fold with embargo (AFML ch. 7): purge on lookback-window overlap, not only on labels
  - CPCV: S = 8, k = 2 → 28 combinatorial block Sharpes; φ = 7 paths (collapse for fixed rules)
  - DSR = PSR(SR0) using non-excess kurtosis (pandas kurt + 3); CSCV ranks by Sharpe
  - PBO via CSCV, reject if PBO \> 0.05
][
  #block(
    width: 100%,
    inset: 11pt,
    stroke: 0.7pt + charcoal,
    radius: 2pt,
    fill: rgb("#f1efe6"),
  )[
    #text(weight: 700, size: 9.4pt)[Non-claim]
    #v(3pt)
    #text(size: 8.9pt)[
      Universe uses current constituents, not a point-in-time survivorship-free panel. Absolute Sharpes are optimistic demo numbers, not a deployment claim. Prefer `synth` offline. DSR/PBO only correct multiple testing within the supplied panel. Not trading advice.
    ]
  ]
]

#v(12pt)
#thin-rule
#v(9pt)

// ---------- Reproduce ----------
#grid(
  columns: (1fr, 1fr),
  gutter: 18pt,
)[
  #text(weight: 700, size: 9.8pt)[Reproduce]
  #v(3pt)
  #text(size: 8.9pt, font: "DejaVu Sans Mono")[
    pip install -e ".[dev]" \
    python -m overfit\_aware\_signals synth
  ]
][
  #text(weight: 700, size: 9.8pt)[Repo]
  #v(3pt)
  #text(size: 8.9pt)[Endokelp\_Projects / PythonProjects / overfit-aware-signals]
]

#v(1fr)
#rule-line
#v(4pt)

// ---------- Footer ----------
#text(size: 7.3pt, fill: charcoal)[
  Primary sources: Bailey and Lopez de Prado (2014), Deflated Sharpe Ratio; Bailey et al., Probability of Backtest Overfitting and CSCV; Lopez de Prado, Advances in Financial Machine Learning, ch. 7. Positioned as claim-filtering tooling, the same class of checks used in 2026 LLM strategy-to-code benchmarks, not an AFML tutorial clone.
]
