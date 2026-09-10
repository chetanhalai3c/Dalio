# All Weather

## 1. Purpose

This file explains the All Weather *concept* — an approach to strategic asset allocation designed so that portfolio success does not depend heavily on one economic scenario occurring.

It deliberately does **not** reproduce any fixed percentage allocation. There is no single canonical "Ray Dalio portfolio," and the widely circulated internet allocations attributed to him are simplifications produced by third parties, not a specification EducosysDalio should treat as authoritative.

The four-environment framing introduced here is used throughout the system. The measurement of where the economy currently sits belongs to `economic_regimes.md`. The mechanics of balancing risk belong to `risk_balancing.md`.

---

## 2. Core Concept

### 2.1 The starting observation

Every asset carries an implicit environmental bias. An asset is not simply "risky" or "safe"; it is a bundle of sensitivities that pays off in some economic conditions and suffers in others.

If an investor holds assets whose environmental biases point in the same direction, the portfolio contains a concentrated bet on that environment — often without the investor having consciously chosen it.

### 2.2 The two dominant axes

Two macroeconomic variables explain a large share of the co-movement of major asset classes:

- **Growth** — the pace of real economic activity and, through it, corporate cash flows and credit quality.
- **Inflation** — the pace of price change, which drives nominal discount rates, real returns on nominal cash flows, and the relative value of real assets.

Crossing these produces four broad environments:

| | **Rising inflation** | **Falling inflation** |
|---|---|---|
| **Rising growth** | 1. Rising growth + rising inflation | 2. Rising growth + falling inflation |
| **Falling growth** | 3. Falling growth + rising inflation | 4. Falling growth + falling inflation |

These are conceptual quadrants, not a classification the world neatly obeys. Real environments sit on a continuum, transition gradually, and can be mixed across geographies at the same moment.

### 2.3 The critical refinement: it is about surprises, not levels

This is the point most commonly lost in popular summaries, and it is central.

Asset prices already embed the expected path of growth and inflation. What moves prices is the *difference* between what happens and what was expected. Consequently, the environments that matter to a portfolio are defined less by:

- "Is inflation high or low?" (**level**)

and more by:

- "Is it rising or falling?" (**direction**)
- "Is the rate of change accelerating or decelerating?" (**second derivative**)
- "What was already priced in?" (**expectations**)
- "Did the outcome land above or below what was priced?" (**surprise**)

A high but decelerating inflation rate that comes in below expectations is, from an asset-pricing perspective, a very different environment from a low but accelerating inflation rate that comes in above expectations — even though a naive "level" classifier would call the first one "high inflation" and the second one "low inflation."

The four quadrants should therefore be read as **growth and inflation relative to what was discounted**, not as absolute levels. This distinction is developed further in `economic_regimes.md`.

### 2.4 The core idea in one sentence

**All Weather is the attempt to build a strategic allocation whose viability does not depend on correctly identifying which environment is coming next.**

---

## 3. Dalio / Bridgewater Foundation

### 3.1 Attributable to Dalio / Bridgewater

- **The environmental-bias framing of asset classes.** The idea that every asset class has a built-in bias toward particular growth and inflation conditions, and that this bias is knowable in advance from the structure of the asset's cash flows, is central to Bridgewater's public explanation of All Weather.
- **The four-box growth/inflation structure.** Organising the world into rising/falling growth crossed with rising/falling inflation, and asking which assets do relatively well in each box, is a Bridgewater framing.
- **The emphasis on surprises relative to discounted expectations.** Bridgewater's public material stresses that assets respond to shifts in expectations rather than to levels already priced in.
- **Balancing risk rather than capital across environments.** The proposition that an allocation should be balanced by risk contribution across environments rather than by capital weight is closely associated with Bridgewater's All Weather approach, and was highly influential in the development and popularisation of broader risk-parity approaches. Risk parity is now a wider portfolio-construction category with multiple implementations, differing in their risk measures, estimation methods, asset universes and use of leverage; it should not be treated as synonymous with Bridgewater's specific methodology, and Bridgewater should not be described as the exclusive originator of all forms of it.
- **Designing an allocation not to depend on forecasting ability.** Dalio has publicly described the origin of All Weather in terms of building something that would hold up across environments the designer could not predict, including for capital he would not be actively managing.
- **The separation of strategic allocation (beta) from active views (alpha).** Bridgewater's public positioning of All Weather alongside a separate active strategy reflects a deliberate structural separation between the two activities.

**Source Note:** These points are drawn from Bridgewater's publicly published account of the strategy's origins and design ("The All Weather Story" and related public Bridgewater material), from Ray Dalio's publicly available writing including *Principles: Life and Work* (2017), and from Bridgewater research made public over time (including material on engineering targeted returns and risks). This file describes the general content of that public material; specific figures, charts, allocations or wording should be verified against the primary source before being asserted. No specific allocation percentages are attributed to these sources here, because the public material does not present a single fixed retail allocation.

### 3.2 Broader financial theory (not uniquely Dalio)

- **Strategic asset allocation as the dominant driver of long-run portfolio outcomes** — a long-standing proposition in the portfolio-management literature, independent of Bridgewater.
- **Mean-variance portfolio construction and the mathematics of combining assets** — Markowitz and successors.
- **Risk parity as a general portfolio-construction category** — now practised by many managers with materially different implementations; not a single proprietary method.
- **Rebalancing as a mechanical discipline** with its own return and risk-control properties, studied extensively outside Bridgewater.
- **Duration, real versus nominal returns, the Fisher relationship between nominal rates, real rates and inflation expectations** — standard macro-finance.
- **The general observation that no single asset performs well in all environments** — a broadly held view.
- **Business-cycle and inflation-regime analysis** — a large independent academic and practitioner literature.

### 3.3 EducosysDalio interpretation

EducosysDalio adopts the four-environment framing and the surprise-based refinement as a **diagnostic lens for exposure analysis**, not as a template for a specific portfolio. Using the framing to ask "which environments is this portfolio silent on?" is this project's application. It is consistent with the public Dalio material but is our design decision, not an instruction from it.

EducosysDalio also explicitly declines to adopt Bridgewater's *implementation* techniques — notably the use of leverage to raise the risk contribution of lower-volatility assets. See §6.4.

---

## 4. How the Concept Works

### 4.1 Assets as bundles of environmental sensitivity

Each broad asset class can be characterised — conceptually, with wide uncertainty — by which environments it has tended to favour. The characterisations below are *tendencies with conditions attached*, not rules. Full treatment, including the conditions under which each role breaks down, is in `asset_roles.md`.

**Equities.** Represent claims on future corporate cash flows. They have tended to do relatively well when growth surprises to the upside and discount rates are not rising sharply. They have tended to struggle when growth disappoints, when risk appetite contracts, or when real discount rates rise abruptly. Long-duration equity (high multiple, distant cash flows) carries substantial implicit interest-rate sensitivity.

**Nominal government bonds.** Contractual nominal cash flows. They have tended to do relatively well when growth disappoints and inflation falls, since falling nominal yields raise prices. They have tended to do poorly when inflation surprises upward, because the fixed nominal stream loses real value and yields rise. Their diversifying relationship with equities is *conditional on the dominant shock being a growth shock rather than an inflation shock*.

**Inflation-linked bonds.** Cash flows indexed to a price index. They separate real-rate exposure from inflation exposure more cleanly than nominal bonds. They have tended to do relatively well when inflation surprises upward while real rates stay contained, and poorly when real rates rise sharply.

**Commodities.** Physical inputs to production. They have tended to do relatively well when inflation surprises upward, particularly supply-driven inflation, and when growth is strong enough to support demand. They have tended to do poorly in demand collapses and in disinflation. They produce no income and carry roll and storage economics that materially affect realised returns.

**Gold.** Neither a productive asset nor a contractual claim. It has at times behaved as a monetary and real-asset diversifier, particularly when real interest rates fall, when confidence in monetary or fiscal management weakens, or during currency-debasement concerns. Its relationship to realised inflation is inconsistent, and it has experienced long, deep drawdowns.

**Cash and short-duration instruments.** Minimal duration risk and high nominal certainty over short horizons. They have tended to be relatively attractive when policy rates rise sharply and other assets reprice, and are the reference asset for liquidity. Their principal risk is erosion of purchasing power when inflation exceeds the rate earned, and reinvestment risk when rates fall.

### 4.2 The construction logic

The All Weather construction logic proceeds roughly as follows:

1. Identify the environments that matter — the growth/inflation surprise quadrants.
2. Identify which exposures have tended to be positively sensitive to each environment.
3. Ensure the portfolio has meaningful representation across different economic environments, reducing its dependence on any single environment and limiting the damage that one adverse regime could cause. This reduces dependence; it does not eliminate the possibility of severe outcomes.
4. Balance the **risk** contributed by each environmental grouping, not the capital allocated to it, because equal capital in a high-volatility and a low-volatility exposure produces very unequal risk.
5. Rebalance systematically so that the intended balance is maintained rather than drifting toward whatever has recently appreciated.

Step 4 is the step most often lost in popular summaries and is the reason a capital-weighted "balanced" portfolio is usually not risk-balanced. See `risk_balancing.md`.

`DETERMINISTIC CALCULATION REQUIRED:` mapping of current holdings to environmental sensitivity groupings; risk contribution by grouping; identification of groupings with zero or negligible representation.

### 4.3 Why rebalancing matters here

Without rebalancing, an environmentally balanced portfolio tends to become an unbalanced one without any decision being taken. Exposures that have recently performed strongly can grow into a larger share of portfolio capital and risk, while those that have lagged shrink.

The portfolio can therefore drift away from its intended environmental balance even though the investor has made no explicit allocation decision. Rebalancing is primarily a mechanism for restoring the intended structure — it is not a claim that recent winners are necessarily overvalued, and it is not a valuation or tactical judgement. Whether an exposure is attractively or unattractively priced is a separate question belonging to the tactical layer (§4.5), and the case for rebalancing does not depend on answering it.

Rebalancing is therefore not a performance-enhancement technique in this framework; it is the maintenance mechanism that keeps the design intact.

It has costs that must be weighed: transaction costs, tax consequences in taxable accounts, tracking of cost basis, and behavioural difficulty (rebalancing requires selling what has done well and buying what has not).

`CONFIGURABLE PARAMETER:` rebalancing trigger method (calendar interval, drift band, or hybrid) and its associated tolerances. *No values are chosen here.*

`CONFIGURABLE PARAMETER:` minimum trade size and cost/tax thresholds below which rebalancing is not recommended. *No values are chosen here.*

### 4.4 What All Weather is not

**It is not a prediction system.** It does not require a view on which quadrant is next. It requires the acknowledgement that any of them could occur.

**It is not quadrant rotation.** Identifying the current quadrant and moving the whole portfolio into the assets favoured by that quadrant is the opposite of the concept. It converts a robustness design into a concentrated forecast, and it does so at the moment when the current environment is most widely recognised and therefore most likely already reflected in prices.

**It is not a guarantee of positive returns in every period.** A portfolio designed to avoid catastrophic dependence on one environment will still have losing periods. In environments where nearly all assets fall together — sharp real-rate shocks, liquidity events, simultaneous growth and inflation disappointment — environmental balance provides limited protection. This should be stated plainly rather than glossed over.

**It is not a fixed set of percentages.** Any specific allocation depends on the investor's circumstances, currency, tax position, available instruments, horizon and risk tolerance, and on which risk-balancing method is used.

**It is not inherently low-risk.** The risk level of an All Weather-style portfolio is a separate choice from its balance. A balanced portfolio can be run at many different overall risk levels.

### 4.5 Strategic versus tactical

These are two distinct activities and EducosysDalio keeps them structurally separate.

**Strategic / All Weather layer**
- Purpose: robustness across environments the investor cannot predict.
- Horizon: long, measured in years.
- Changes: infrequent, driven by changes in the *investor's* circumstances or by structural changes in the opportunity set — not by the macro view.
- Justification standard: must survive being wrong about the cycle.
- Should constitute the large majority of the portfolio.

**Tactical layer**
- Purpose: expressing a specific, falsifiable macro or valuation view.
- Horizon: shorter, and explicitly time-bounded.
- Changes: driven by evidence, and reversed when the evidence changes or the thesis is invalidated.
- Justification standard: must state in advance what would prove it wrong.
- Should be size-limited so that being wrong is survivable and does not compromise the strategic layer.

`CONFIGURABLE PARAMETER:` maximum aggregate share of the portfolio available to the tactical layer. *No value is chosen here.*

`CONFIGURABLE PARAMETER:` maximum deviation of any single asset class from its strategic weight due to tactical views. *No value is chosen here.*

A tactical view that requires a large deviation to be worth having is, by construction, a view that would do serious damage if wrong. That asymmetry is the reason for the limit.

---

## 5. Portfolio Implications

Applying the All Weather lens to a real portfolio produces the following observations:

**Environmental coverage.** Which of the four environments does this portfolio have meaningful positive sensitivity to, and which does it have essentially none? A portfolio with three environments unrepresented is making a large implicit forecast.

**Implicit forecast identification.** Every portfolio embeds a view. The question is whether the investor chose it. Making the implicit forecast explicit — "this portfolio requires continued disinflationary growth to meet its objective" — is often the single most useful output the system can produce.

**Risk-versus-capital balance.** A portfolio may appear environmentally spread by capital while being dominated by one environment's risk. See `risk_balancing.md`.

**Drift.** How far has the portfolio drifted from its intended balance, and in which direction? Drift usually points toward the environment that has recently prevailed.

**Realism about limits.** Which scenarios would still hurt this portfolio badly despite the balance? Every design has residual vulnerabilities and the system should name them rather than imply the portfolio is protected.

**Cost and complexity.** Environmental coverage achieved through expensive, illiquid or operationally complex instruments may not be worth the coverage it buys. Robustness that the investor cannot maintain in practice is not robustness.

---

## 6. EducosysDalio Interpretation

**6.1 Diagnostic, not prescriptive.** EducosysDalio uses the four-environment framing primarily to *diagnose* the environmental dependence of an existing portfolio and to *educate* the investor about it. It does not output a target allocation table as though there were one correct answer.

**6.2 The regime view informs, it does not drive.** EducosysDalio should form and communicate a view of the current environment (per `economic_regimes.md`) because understanding the environment is genuinely useful — for context, for setting expectations, for identifying which vulnerabilities are currently most live. But that view is not permitted to restructure the strategic layer. The test applied to every strategic recommendation is:

> *If this regime assessment is wrong, is the strategic portfolio still robust?*

If the answer is no, the recommendation is not a strategic recommendation; it is a tactical bet mislabelled.

**6.3 Explicit uncertainty.** Environmental characterisations are stated with hedged language and with the conditions under which they have historically held. EducosysDalio does not state that an asset "will" perform in a given environment.

**6.4 No leverage prescription.** Bridgewater's implementation of risk balancing has, in public accounts, involved using leverage to raise the risk contribution of lower-volatility assets so that balance can be achieved without sacrificing expected return. EducosysDalio does not adopt this. Leverage introduces path dependence, margin and forced-liquidation risk, financing cost, counterparty risk, and a materially different failure profile. Its exclusion is a conservatism choice of this project, not a claim that Bridgewater's approach is wrong for institutional investors with different constraints and infrastructure.

The consequence must be stated honestly rather than glossed over. Under conventional capital-market assumptions, an unlevered portfolio that reduces concentration in higher-risk / higher-expected-return assets such as equities **may** have a lower expected nominal return than a heavily equity-dominated portfolio. That trade-off is assumption-dependent rather than guaranteed: it rests on estimates of expected returns, volatilities and correlations that are themselves uncertain, and realised outcomes have at times differed from what such assumptions implied.

EducosysDalio should therefore present the expected-return implications of greater balance explicitly — including the assumptions they rest on — rather than claiming that diversification is costless.

**6.5 "Do nothing" is a valid conclusion.** If a portfolio is already reasonably balanced, the appropriate recommendation is often no change. Frictional costs, taxes and behavioural risk make unnecessary activity genuinely harmful.

**6.6 Adaptation to the investor.** Any application of this framework is filtered through the investor's spending currency, tax wrapper, horizon, liquidity needs, existing commitments, human capital, and demonstrated tolerance for drawdown. The framework describes a design principle, not a product.

---

## 7. Failure Modes / Misinterpretations

**Treating All Weather as a fixed portfolio.** Reproducing a percentage table found online and presenting it as "the Ray Dalio portfolio." There is no such single specification in the public source material, and any specific allocation is contingent on method, instruments and investor.

**Quadrant rotation.** Using the four-box framework as a market-timing device. This is the most consequential misuse and directly inverts the concept's purpose.

**Assuming balance means protection.** Environmental balance reduces dependence on one scenario. It does not prevent losses, and in correlated liquidity shocks it may help little.

**Ignoring the surprise dimension.** Classifying environments by level rather than by change and surprise, producing a classification that does not correspond to what actually drives prices.

**Copying institutional implementation.** Adopting leverage, derivative overlays or instrument choices designed for an institution with different constraints, capital, tax status and operational infrastructure.

**Under-representing the return trade-off.** Presenting environmental balance as improving everything simultaneously. Under conventional assumptions, unlevered balance may trade expected return for reduced dependence, and that possibility should be stated rather than omitted.

**Over-stating the return trade-off.** The mirror error: asserting as certain that balance costs return. The trade-off depends on capital-market assumptions that are themselves uncertain, and should be presented as assumption-dependent.

**Confusing the strategic and tactical layers.** Allowing a macro view to justify a permanent change to strategic weights, or allowing a strategic principle to justify an unbounded tactical position.

**Over-engineering.** Adding instruments to fill a quadrant when the exposure is too small to matter, too expensive to hold, or too complex for the investor to maintain.

**Treating the four boxes as exhaustive.** Growth and inflation explain a lot, but not everything. Liquidity shocks, credit events, geopolitical disruption, policy error, currency crises and structural market-plumbing failures do not reduce neatly to the two axes. See `debt_cycles.md` and `economic_regimes.md`.

**Static environmental sensitivities.** Assuming an asset's environmental behaviour is fixed. Sensitivities have changed across eras, particularly the equity–bond relationship. See `asset_roles.md`.

---

## 8. Questions EducosysDalio Should Ask

**About environmental coverage**

- Which of the four environments does this portfolio have meaningful positive sensitivity to?
- Which environments are essentially unrepresented, and is that deliberate?
- If the least-represented environment occurred and persisted, what would the likely impact be?

**About the implicit forecast**

- What does this portfolio implicitly require the economy to do?
- Has the investor consciously chosen that bet, or has it accumulated?
- How much of the portfolio's expected outcome rests on a single environment continuing?

**About balance**

- Is the portfolio balanced by capital, by risk, or neither?
- Which environmental grouping dominates portfolio risk, and by how much?
- How far has the portfolio drifted from its intended balance, and toward which environment?

**About the strategic/tactical boundary**

- Is this proposed change strategic or tactical?
- If strategic: would it still be sensible under each of the four environments?
- If tactical: what specifically would prove this view wrong, over what horizon, and what is the size limit?
- Does this change survive the test of the regime view being wrong?

**About honest limits**

- What scenarios would still damage this portfolio badly?
- What are the expected-return implications of the balance being proposed, and what assumptions do they rest on?
- Can the investor realistically maintain this structure — the rebalancing, the costs, the complexity, the behavioural demands?

**About doing nothing**

- Is the current portfolio already adequately balanced for this investor's purposes?
- Would the frictional and tax cost of the proposed change exceed its expected benefit?

---

## 9. Structured Knowledge Summary

**Principle:**
Build a strategic allocation whose viability does not depend on correctly predicting which economic environment comes next; balance risk across environments rather than capital across labels.

**Objective:**
Give EducosysDalio a framework for diagnosing a portfolio's environmental dependence, making its implicit macro forecast explicit, and separating strategic robustness from tactical views.

**Relevant Inputs:**
Portfolio holdings and their environmental sensitivity classifications; risk contribution data from `risk_balancing.md`; current environment assessment from `economic_regimes.md`; investor circumstances, currency, horizon, tax position and liquidity needs.

**Relevant Outputs:**
Environmental coverage map; identification of unrepresented environments; statement of the portfolio's implicit macro forecast; drift assessment; strategic-versus-tactical classification of any proposed change; explicit statement of residual vulnerabilities and of the expected-return trade-off together with the assumptions it rests on.

**Risks Addressed:**
Single-scenario dependence; unrecognised implicit macro bets; drift toward recently successful exposures; forecast-dependent portfolio construction; conflation of strategic allocation with tactical positioning.

**Agent Behaviours:**
Apply the four-environment lens diagnostically; use surprise-based rather than level-based environmental framing; never present a fixed percentage template as canonical; keep strategic and tactical layers separate and size-limited; state trade-offs and residual vulnerabilities honestly; recommend no change when no change is warranted; always close with the robustness test.

**Deterministic Calculations Required:**
Mapping of holdings to environmental sensitivity groupings; risk contribution by grouping; drift from target weights; rebalancing trade calculations; historical performance of holdings within defined environmental periods (where data permits).

**Configurable Parameters:**
Rebalancing trigger method and tolerances; minimum trade size and cost/tax thresholds; maximum aggregate tactical share; maximum single-asset-class tactical deviation; definitions of the environmental period classifications. *No values are set in this file.*

**Related Knowledge Files:**
`investment_philosophy.md`, `economic_regimes.md`, `risk_balancing.md`, `diversification.md`, `asset_roles.md`, `debt_cycles.md`.
