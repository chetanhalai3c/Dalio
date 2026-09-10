# Risk Balancing

## 1. Purpose

This file is the conceptual foundation for the future **deterministic portfolio risk engine**. It defines what each risk measure means, when it is informative, when it misleads, and — critically — which quantities must be computed by code rather than produced by a language model.

The governing rule of this file:

> **The LLM interprets these numbers. The LLM does not invent these numbers.**

Every quantity marked `DETERMINISTIC CALCULATION REQUIRED` must originate from an explicit computation over actual data, with its inputs, window and method recorded. A number that appears in an EducosysDalio output without such a provenance is a defect, not an estimate.

---

## 2. Core Concept

### 2.1 Capital allocation is not risk allocation

This is the central idea of the file.

Consider a portfolio described as:

- 60% equities
- 40% government bonds

That is a statement about **capital**. It says where the money is. It says almost nothing about where the *risk* is.

Suppose the equity allocation has historically exhibited annualised volatility several times that of the bond allocation — a common ordering, though the specific ratio varies by period and by which bonds are held. Because risk scales with volatility (and with covariance), the equity sleeve can account for the overwhelming majority of the portfolio's variance despite holding well under two-thirds of the capital.

The portfolio described as "balanced" is, in risk terms, close to an equity portfolio with a modest cushion.

This is not a criticism of that allocation. It may be entirely appropriate. The point is narrower and more important: **the capital description conceals the risk description, and investors routinely believe they own the first when they own the second.**

### 2.2 Why the arithmetic works this way

Portfolio risk is not the weighted average of component risks. It is determined by:

- the **weights** of each holding,
- the **volatility** of each holding,
- the **correlations** between them.

Two of these three are usually ignored in casual portfolio descriptions. The consequence is that:

- A small weight in a very high-volatility asset can contribute risk far out of proportion to its capital share.
- A large weight in a low-volatility asset can contribute very little.
- Adding a holding that is highly correlated with existing holdings adds more risk than its volatility alone implies.
- Adding a holding with low correlation adds less risk than its volatility alone implies — this is the diversification benefit.

### 2.3 What risk balancing attempts

**Risk balancing is the attempt to prevent any single asset class or driver from dominating total portfolio behaviour.**

The objective is not equality for its own sake, and not risk minimisation. It is to avoid a situation where the portfolio's outcome is effectively determined by one exposure, while the investor believes it is determined by several.

---

## 3. Dalio / Bridgewater Foundation

### 3.1 Attributable to Dalio / Bridgewater

- **The proposition that portfolios should be balanced by risk contribution rather than by capital weight**, and the observation that conventionally "balanced" portfolios are dominated by equity risk. Balancing portfolio risk rather than relying on capital weights is closely associated with Bridgewater's All Weather approach, and was highly influential in the development and popularisation of institutional risk-parity approaches. Risk parity is now a broader portfolio-construction category with multiple independent implementations, and should not be treated as synonymous with Bridgewater's proprietary methodology or as originating exclusively from Bridgewater.
- **The separation of the risk level of a portfolio from its balance** — the argument that how much risk to take and how to distribute it are two independent decisions that should be made separately.
- **Framing risk in terms of exposure to economic environments** rather than only to asset labels, so that risk balancing and environmental balancing are the same exercise viewed from two angles. See `all_weather.md`.
- **The argument that diversification across genuinely different return streams improves return per unit of risk**, with diminishing marginal benefit as streams are added.

**Source Note:** These framings appear in Ray Dalio's publicly available writing (*Principles: Life and Work*, 2017), in Bridgewater's public All Weather material, and in Bridgewater research on engineering targeted returns and risks that has circulated publicly. The general risk-parity approach is now practised by many managers with materially different methods; Bridgewater's specific implementation is proprietary and is not publicly specified in detail. EducosysDalio should not present any particular construction method as "Bridgewater's method."

### 3.2 Broader financial theory (not uniquely Dalio)

Nearly all of the *measurement* content of this file is standard finance and should be labelled as such:

- **Mean-variance portfolio theory** (Markowitz) — variance as the risk measure, the covariance structure as the mechanism, and the diversification benefit.
- **Portfolio variance decomposition and marginal contribution to risk** — the Euler decomposition that allows total portfolio risk to be attributed additively across positions. Standard risk-management mathematics.
- **Beta and the systematic/idiosyncratic decomposition** (CAPM and successors).
- **Risk parity as a general category** — developed and implemented independently by many firms.
- **Downside risk measures** — semi-deviation, downside deviation, Sortino-type ratios (Markowitz himself discussed semi-variance).
- **Value at Risk and Conditional Value at Risk / Expected Shortfall** — standard regulatory and practitioner measures, with well-documented limitations.
- **Maximum drawdown and underwater analysis** — standard practitioner measures.
- **Fat tails and the inadequacy of the normal distribution for financial returns** — a large independent literature (Mandelbrot, Taleb and many others).
- **Stress testing and scenario analysis** — standard risk-management practice, mandated in regulated institutions.
- **Estimation error in covariance matrices** and the shrinkage literature addressing it.
- **Volatility clustering and time-varying volatility models** (ARCH/GARCH family).

### 3.3 EducosysDalio interpretation

The **strict separation of computation from interpretation**, the **prohibition on model-generated numbers**, the **refusal to use leverage**, and the **requirement that every risk output carry its method and window** are EducosysDalio design decisions.

---

## 4. How the Concept Works

### 4.1 Returns — the foundation

Every downstream measure depends on the return series. Errors here propagate everywhere.

Considerations: arithmetic versus logarithmic returns and where each is appropriate; total return including income versus price return; the treatment of dividends, coupons, splits and corporate actions; the choice of currency; whether returns are gross or net of fees and costs; frequency (daily, weekly, monthly) and the aliasing effects of each; the handling of missing data, non-synchronous market closes across time zones, and instruments with short histories.

Instruments with short histories are a recurring practical problem: a holding launched a few years ago has never experienced a full cycle, so any risk estimate for it describes a narrow slice of conditions.

`DETERMINISTIC CALCULATION REQUIRED:` return series construction for all holdings, in the investor's base currency, on a stated total-return basis, with data quality and coverage flags.

`CONFIGURABLE PARAMETER:` return frequency, currency basis, and gross/net convention. *No values are chosen here.*

### 4.2 Volatility

**What it is.** The dispersion of returns around their mean, conventionally the standard deviation, usually annualised.

**What it tells you.** How much a holding has typically fluctuated over the measurement window. It is the basic scaling factor that translates capital weights into risk weights.

**What it does not tell you.** Volatility treats upside and downside dispersion symmetrically, though investors do not experience them symmetrically. It says nothing about the shape of the tails. It is not stable — volatility clusters, so calm periods systematically understate the risk of the regime that follows, and stressed periods overstate it. It is entirely backward-looking.

**When it misleads most.** For illiquid or infrequently priced assets, where stale or smoothed valuations mechanically depress measured volatility and make the asset appear safer than it is. This is a serious and common distortion in property, private assets and some structured products.

`DETERMINISTIC CALCULATION REQUIRED:` volatility per holding and for the portfolio, over multiple stated windows, annualised, with the window and frequency reported.

`CONFIGURABLE PARAMETER:` volatility estimation windows and whether an exponentially weighted or equal-weighted method is used. *No values are chosen here.*

### 4.3 Correlation and covariance

Conceptual treatment is in `diversification.md` §4.1–4.3 and is not repeated here. The essentials for risk computation:

- **Correlation** measures co-movement direction and consistency on a −1 to +1 scale.
- **Covariance** combines correlation with both volatilities, and is the quantity that enters the portfolio variance calculation.
- Correlation alone can mislead. A low correlation with a highly volatile asset can still transmit substantial risk.
- Both are sample estimates and both change across regimes. Their instability is the largest single source of error in portfolio risk estimation.

`DETERMINISTIC CALCULATION REQUIRED:` correlation matrix and covariance matrix over stated windows; rolling versions; conditional versions computed on defined stress subsets.

`CONFIGURABLE PARAMETER:` covariance estimation method, including whether shrinkage or other regularisation is applied. *No values are chosen here.*

### 4.4 Portfolio variance and portfolio volatility

**Conceptually:** portfolio variance aggregates the variance contributed by each holding *plus* the covariance contributed by every pair of holdings. The pairwise terms are what make diversification work. When correlations are low, the pairwise terms are small and total portfolio risk is materially less than the weighted average of component risks. When correlations rise toward one, the pairwise terms grow and that benefit erodes.

**The diversification benefit.** One useful diagnostic is the difference between the weighted-average standalone volatility of the holdings and the resulting portfolio volatility. It gives a single summary of how much the correlation structure is helping at current weights.

It is not, however, the one canonical definition. Other diversification measures may also be used, including diversification ratios, concentration measures computed on capital or risk contributions, and effective independent-exposure measures. These can rank the same portfolio differently, because each embeds different assumptions about what diversification means.

`CONFIGURABLE METHODOLOGY:` whichever diversification measure is adopted must have its definition documented and applied consistently across assessments, so that results are comparable over time and between portfolios. *No measure is selected here.*

Whichever measure is used, the underlying principle holds: correlation and covariance can cause portfolio risk to be materially lower than the simple weighted average of standalone risks. Any reported figure should carry the caveat that it is estimated on a specific window, and that it may shrink materially under the stressed correlation structures described in §4.11.

`DETERMINISTIC CALCULATION REQUIRED:` portfolio variance; portfolio volatility; diversification benefit versus weighted-average component volatility.

### 4.5 Marginal contribution to risk and contribution to risk

These two measures are the analytical heart of risk balancing.

**Marginal contribution to risk (MCR)** answers: *if I increased this holding slightly, how much would total portfolio risk change?* It is a sensitivity — the derivative of portfolio risk with respect to the position's weight. It accounts for both the holding's own volatility and its covariance with everything else, which is why adding a highly correlated holding raises portfolio risk more than its standalone volatility suggests.

**Contribution to risk (CTR)** answers: *what share of total portfolio risk does this holding account for?* It is the position weight multiplied by its marginal contribution, and the contributions sum to total portfolio risk. This additivity is what makes CTR the natural companion to capital weights.

**The comparison that matters.** Presenting capital weight alongside risk contribution for each holding is, in practice, one of the most informative outputs EducosysDalio can produce. It is where "60/40" is revealed for what it actually is. It converts an abstract argument into an observation about the investor's own portfolio.

**Contributions can be negative.** This is a technical point with real interpretive consequences, and it is easily missed.

A holding's contribution to portfolio volatility can be **negative** when its covariance with the rest of the portfolio is sufficiently negative. A holding can therefore *reduce* total portfolio volatility even though it has positive standalone volatility of its own. Read the sign as follows:

- **Positive CTR** — at current weights, the holding increases measured portfolio volatility.
- **Negative CTR** — at current weights and under the estimated covariance structure, the holding acts as a hedge or diversifier, reducing measured portfolio volatility.
- **Zero or near-zero CTR** — the holding has very little marginal effect on current portfolio volatility, either because its weight is small or because its covariance contribution roughly offsets its own variance contribution.

**Consequence for reporting.** A "risk contribution share" should therefore not be interpreted automatically in the way a capital percentage is. Percentage contributions become unintuitive when some contributions are negative: shares can exceed 100%, and the negative entries do not represent a portion of anything. Forcing every holding into a positive percentage bucket obscures exactly the information that matters most.

EducosysDalio should therefore preserve, in its outputs:

- the **absolute contribution** in risk units, not only a normalised share
- the **sign** of each contribution, displayed explicitly
- the **grouping** at which contributions are aggregated
- the **reconciliation** of contributions to total portfolio risk

**What a negative contribution is and is not.** A negative contribution is an *estimated, covariance-based property measured over a specific window at current weights*. It is not evidence that the holding will hedge in future stress. The covariance that produced the negative sign may not persist, may weaken, or may reverse — the equity–bond relationship in `asset_roles.md` §4.2 is the most consequential example of a diversifying relationship that has changed sign across regimes. A negative CTR should be reported as an observation about the measured sample, not as a property of the asset, and it should be tested against the stressed correlation structures in §4.11.

**Caveats to state alongside it.** CTR is a local, estimated, window-dependent decomposition. It is computed from the covariance matrix, so it inherits all of that matrix's instability. It describes marginal behaviour around current weights, not behaviour under large moves. It is a good tool and not a precise one.

`DETERMINISTIC CALCULATION REQUIRED:` marginal contribution to risk per holding; contribution to risk per holding and per grouping (asset class, region, currency, environmental grouping), reported in absolute risk units with sign preserved; reconciliation of contributions to total portfolio risk.

`CONFIGURABLE PARAMETER:` the groupings used for risk contribution reporting. *Not specified here.*

`CONFIGURABLE PARAMETER:` acceptable maximum risk contribution from any single holding, asset class or driver, above which a concentration discussion is triggered. *No value is chosen here.*

### 4.6 Concentration measures

Concentration can be measured on capital weights, on risk contributions, or on look-through exposures — and the three often disagree, which is itself informative.

Useful concepts: the share held by the largest few positions; standard concentration indices computed on weights or on risk contributions; the effective number of independent positions implied by the risk decomposition (typically far lower than the nominal holding count); look-through issuer, sector, region and currency concentration.

`DETERMINISTIC CALCULATION REQUIRED:` concentration metrics on capital weights, on risk contributions, and on look-through exposures; effective number of independent positions.

### 4.7 Beta

**What it is.** The sensitivity of a holding's returns to a specified reference series — most commonly a broad equity market, but the reference must be stated because beta is meaningless without it.

**Where it is useful.** As a compact way to express "how much of this holding's behaviour is explained by the dominant market factor," and to identify holdings whose apparent distinctiveness is actually market exposure in disguise. This makes it a useful check on false diversification.

**Limitations.** Beta is a single-factor linear summary. It is estimated and unstable. It typically rises in stress, so a low estimated beta may not hold when it matters. It assumes a linear relationship that may not describe holdings with option-like or non-linear payoffs.

`DETERMINISTIC CALCULATION REQUIRED:` beta of each holding and of the portfolio to specified reference series, with the reference, window and fit quality reported.

### 4.8 Maximum drawdown

**What it is.** The largest peak-to-trough decline over a period, usually with the recovery time recorded alongside.

**Why it matters more than volatility for real investors.** Drawdown is what people actually experience. It is the measure that determines whether an investor abandons a strategy at the worst possible moment, and whether a drawdown coinciding with a spending need forces a sale at a depressed price. A portfolio that is theoretically optimal but produces a drawdown the investor cannot tolerate is not appropriate for that investor. Behavioural capacity is a real constraint, not a soft one.

**Related measures.** Time under water (how long the position remained below its prior peak) and recovery time are often more decision-relevant than the depth of the decline alone. A shallow drawdown lasting many years may be harder to endure than a deep one that recovers quickly.

**Limitations.** Maximum drawdown is a single realised path — one observation from a distribution. The maximum over a historical window is not a bound. The worst drawdown ahead may exceed anything in the sample, particularly for holdings with short histories.

`DETERMINISTIC CALCULATION REQUIRED:` maximum drawdown per holding and for the portfolio; drawdown duration; time under water; recovery periods; drawdown distribution across the sample.

### 4.9 Downside and tail risk

**Downside risk measures** — semi-deviation, downside deviation relative to a stated threshold, and ratios built on them — capture the asymmetry that volatility misses. They estimate dispersion using only adverse outcomes. They are noisier than volatility because they use fewer observations.

**Tail risk, conceptually.** Financial return distributions have historically exhibited more extreme outcomes than a normal distribution implies. Extreme moves occur more often and are larger than a variance-based model expects. Any risk framework built on volatility alone systematically understates the probability of severe outcomes.

Value at Risk expresses a loss threshold not expected to be exceeded with a stated probability over a stated horizon. Its well-known deficiency is that it says nothing about the magnitude of losses beyond that threshold. Conditional VaR / Expected Shortfall addresses this by measuring the average loss in the tail, and is generally the better of the two.

Both are estimated from limited data in the region where data is scarcest. They should be presented with wide uncertainty and never as bounds.

**The honest statement EducosysDalio should make:** tail risk estimates are the least reliable numbers in the risk report, precisely because they concern the events with the fewest observations. This should be said out loud rather than buried.

`DETERMINISTIC CALCULATION REQUIRED:` downside deviation; VaR and Conditional VaR at stated confidence levels and horizons; tail statistics (skewness, kurtosis) with sample size disclosed.

`CONFIGURABLE PARAMETER:` VaR/CVaR confidence levels, horizons and estimation method (historical, parametric or simulation). *No values are chosen here.*

### 4.10 Scenario analysis

**What it is.** Applying a specified set of market moves to the current portfolio and computing the resulting impact — a "what if" applied to actual holdings.

**Two useful families:**
- *Historical replay* — applying the actual moves from a defined past episode to today's portfolio. Concrete and defensible, but assumes today's holdings would behave as their historical proxies did.
- *Hypothetical construction* — specifying a coherent set of moves for a scenario that has not occurred, such as a sharp simultaneous rise in real rates and inflation.

**What makes a scenario useful:** internal coherence (the specified moves must be economically consistent with one another), relevance to the actual portfolio's exposures, and severity that is plausible rather than either comfortable or absurd.

**The essential point:** scenarios do not carry probabilities. Their purpose is to reveal *what would happen*, not *what will happen*. This distinction must be preserved in the output.

`DETERMINISTIC CALCULATION REQUIRED:` scenario impact calculations applying specified shocks to current holdings, with per-holding and total portfolio results.

`CONFIGURABLE PARAMETER:` the scenario library — which historical episodes and hypothetical constructions are used, and the shock magnitudes for each. *No values are chosen here.*

### 4.11 Stress testing

Closely related to scenario analysis, with a different emphasis: rather than asking "what would happen in scenario X," stress testing asks "what conditions would produce an unacceptable outcome for this investor?" — working backwards from consequence to cause.

This reverse framing is valuable because it identifies the portfolio's actual breaking points rather than testing scenarios chosen for convenience.

**Correlation stress.** Stress testing should include scenarios in which correlations among historically diversifying risk assets rise materially, reducing the diversification benefit. The stressed correlation structure should be **explicitly specified** rather than assuming that every pairwise correlation becomes +1. A blanket assumption of perfect correlation is easy to compute but describes no episode that has actually occurred, and it discards the structure that makes the exercise informative.

Different crises have produced different correlation structures. Growth shocks, inflation shocks, funding and liquidity shocks, and currency events can affect relationships in different ways — a stress in which nominal bonds rally alongside falling equities is a materially different exercise from one in which they fall together. Where possible, stressed structures should be drawn from or informed by defined historical episodes as well as constructed hypothetically.

The point being preserved is that **diversification measured in normal periods can deteriorate sharply during stress**, and that a portfolio whose robustness depends on a measured correlation structure should be tested against plausible alternatives to it.

`CONFIGURABLE PARAMETER:` the stressed correlation structures used, including which historical episodes inform them and the magnitude of the assumed correlation shifts. *No values are chosen here.*

`DETERMINISTIC CALCULATION REQUIRED:` reverse stress calculations; correlation-stress recomputation of portfolio risk; identification of the exposures driving the worst outcomes.

### 4.12 The computation/interpretation boundary

This is the operational rule that governs the whole file.

**Deterministic code produces:** every number. Returns, volatilities, correlations, covariances, portfolio variance, risk contributions, betas, drawdowns, downside measures, VaR/CVaR, concentration metrics, scenario impacts, and every intermediate quantity. Each output carries its method, window, data source and coverage.

**The reasoning layer produces:** the explanation of what those numbers mean, the identification of which are most decision-relevant for this investor, the connection between the risk picture and the investor's circumstances, the statement of limitations, and the questions worth asking. It also produces the *judgement* about whether a given risk profile is appropriate — which is not a computable quantity.

**The reasoning layer must never:** state a volatility, correlation, drawdown, risk contribution or any other quantitative figure that was not produced by the deterministic layer; round, adjust, or "reasonably estimate" such a figure; or describe a relationship in quantitative terms without a computed basis.

If a number is not available, the correct output is to say that it is not available and to explain what would be needed to compute it. A plausible-sounding invented figure is worse than an acknowledged gap, because it will be trusted.

---

## 5. Portfolio Implications

The risk analysis EducosysDalio produces should answer these questions about a real portfolio:

**Where is the risk?** The side-by-side comparison of capital weight and risk contribution, at holding level and at grouping level. This is the primary output.

**Is one exposure dominant?** If a single asset class or driver accounts for the large majority of portfolio risk, the portfolio's outcome is substantially determined by that one thing, whatever the capital weights suggest.

**How much diversification is actually present?** The measured diversification benefit under the documented measure, with an explicit statement of how much of it would survive the stressed correlation structures tested in §4.11.

**What has this portfolio's drawdown experience looked like?** Depth, duration and recovery — and whether the investor has the financial and behavioural capacity for a repeat or worse.

**What would break it?** The scenarios and reverse-stress results that identify the portfolio's breaking points.

**Is the risk level appropriate?** Distinct from whether the risk is balanced. A well-balanced portfolio may still carry more or less risk than the investor's circumstances warrant. Both questions must be answered.

**What is the trade-off?** Under conventional capital-market assumptions, reducing the dominance of the highest-risk exposure without leverage may reduce expected return. That is assumption-dependent rather than guaranteed, and it must be stated together with the assumptions behind it rather than implied or omitted. See §6.3.

---

## 6. EducosysDalio Interpretation

**6.1 Both lenses, always.** Every portfolio assessment reports capital weights and risk contributions together. Reporting only capital weights is treated as an incomplete assessment.

**6.2 Balance means avoiding domination, not enforcing equality.** EducosysDalio does not target equal risk contributions as a goal. It identifies domination — where one exposure determines the outcome — and makes it visible. Whether to change it is the investor's decision, informed by their circumstances.

**6.3 No leverage.** EducosysDalio does not recommend leverage to achieve risk balance. Institutional risk-parity implementations often use it; EducosysDalio's conservatism excludes it because of path dependence, margin and forced-liquidation risk, financing cost, counterparty exposure, and a qualitatively different failure profile.

The honest consequence must accompany this position. Under conventional capital-market assumptions, an unlevered portfolio that reduces concentration in higher-risk / higher-expected-return assets such as equities **may** have a lower expected nominal return than a heavily equity-dominated portfolio of the same nominal size.

That trade-off is assumption-dependent rather than guaranteed. Expected returns, volatilities and correlations are themselves estimates, and realised outcomes may differ materially from those assumptions — there have been extended historical periods in which more balanced portfolios outperformed equity-dominated ones, and periods in which they did not.

EducosysDalio should therefore present the expected-return implications of greater balance explicitly, together with the assumptions behind them, rather than presenting diversification either as costless or as certain to reduce return. Reducing risk concentration is not a free lunch; nor is it a guaranteed sacrifice.

**6.4 Numbers have provenance.** Every figure in an output carries its method, estimation window, data source, frequency and coverage. Figures without provenance do not appear.

**6.5 Multiple windows by default.** Risk measures are reported across more than one estimation window, because a single window invites false confidence and hides regime dependence. Where windows disagree materially, that disagreement is reported as a finding.

**6.6 Estimates are labelled as estimates.** Risk measures are sample statistics with error. Presenting them with excessive decimal precision implies accuracy that does not exist.

**6.7 Drawdown is given prominence.** Because drawdown, not volatility, is what causes investors to abandon plans, EducosysDalio treats drawdown capacity — financial and behavioural — as a first-order input rather than a footnote.

**6.8 Illiquid holdings are flagged.** Where measured volatility is likely suppressed by stale or smoothed pricing, EducosysDalio states this explicitly rather than reporting the flattering number without comment.

**6.9 Risk level and risk balance are separate decisions.** They are assessed and communicated separately, because conflating them leads to changing the wrong one.

**6.10 "No change" is a valid conclusion.** If the risk picture is appropriate for the investor, the recommendation is to change nothing. Turnover has costs and unnecessary activity is a real harm.

---

## 7. Failure Modes / Misinterpretations

**The LLM inventing numbers.** The most serious failure. Language models generate plausible figures fluently, and those figures will be trusted. Every quantitative claim must trace to a computation.

**Reading capital weights as risk weights.** The failure this file exists to correct.

**Treating volatility as the whole of risk.** Volatility misses asymmetry, tails, liquidity, drawdown path and the risk of permanent loss.

**Treating estimated parameters as stable.** Volatilities and correlations are regime-dependent. Estimates from calm periods systematically understate stressed-period risk.

**Believing the diversification benefit is durable.** The measured benefit reflects the sampled correlation structure and can substantially disappear in stress.

**Window shopping.** Choosing the estimation window that produces the desired conclusion.

**False precision.** Reporting figures to a precision that implies measurement rather than estimation.

**Ignoring smoothed pricing.** Accepting artificially low measured volatility for infrequently priced assets, which makes illiquid holdings appear to be diversifiers when they are not.

**Optimiser worship.** Treating the output of a risk-based optimisation as objectively correct. Optimisers concentrate estimation error and produce unstable, extreme solutions that are highly sensitive to inputs that are themselves uncertain.

**Treating maximum historical drawdown as a floor.** It is one realised path, not a bound.

**Assuming tail estimates are reliable.** They are estimated where data is scarcest and deserve the widest error bars in the report.

**Confusing risk balance with risk level.** Rebalancing risk contributions does not answer whether the total risk is appropriate for this investor.

**Presenting balance as costless.** Omitting the expected-return implications of unlevered balance entirely, so the investor sees only the risk reduction.

**Presenting the return sacrifice as certain.** The mirror error: asserting that balance necessarily costs return. The trade-off rests on capital-market assumptions that are themselves estimates, and should be presented as assumption-dependent with those assumptions named.

**Optimising a number rather than serving the investor.** A portfolio with attractive computed statistics that the investor cannot behaviourally sustain is a worse portfolio than a slightly less elegant one they will actually hold.

---

## 8. Questions EducosysDalio Should Ask

**About the risk picture**

- What is each holding's capital weight, and what is its risk contribution? Where do these diverge most?
- Which single asset class or driver contributes the largest share of portfolio risk?
- Does one exposure effectively determine the portfolio's outcome?
- What is the measured diversification benefit under the documented measure, and how much of it would remain under the stressed correlation structures tested?
- How different are the results across estimation windows, and what does the disagreement indicate?

**About drawdown**

- What is the portfolio's historical maximum drawdown, its duration, and its recovery period?
- Does the investor have the financial capacity to sustain a comparable or worse drawdown without forced selling?
- Does the investor have the behavioural capacity to hold through it?
- Would a drawdown coincide with any known spending need?

**About tails and scenarios**

- Which scenarios produce the worst outcomes, and which exposures drive them?
- Working backwards: what conditions would produce an outcome this investor could not tolerate?
- How reliable are the tail estimates, and how many observations support them?

**About data quality**

- Which holdings have insufficient history for meaningful estimates?
- Which holdings have smoothed or stale pricing that suppresses measured volatility?
- What is the currency basis, and does it match the investor's spending currency?
- Which numbers are missing, and what would be required to compute them?

**About appropriateness**

- Is the risk *level* appropriate for this investor's horizon, obligations and capacity — separately from whether it is balanced?
- If the balance were improved, what would the expected-return implications be, and on what capital-market assumptions do they rest?
- Is the right answer here to change nothing?

**The governing questions**

- Does every number in this output trace to a deterministic computation?
- If the assumptions behind these risk estimates are wrong — if correlations shift, if volatility regimes change — is the portfolio still robust?

---

## 9. Structured Knowledge Summary

**Principle:**
Capital allocation is not risk allocation; portfolio risk must be measured, decomposed and interpreted rather than inferred from weights — and every number must come from deterministic computation, never from the language model.

**Objective:**
Provide the conceptual foundation for a deterministic portfolio risk engine, defining what each risk measure means, when it informs, when it misleads, and how the reasoning layer should interpret it.

**Relevant Inputs:**
Holdings and weights; total-return histories in the base currency; estimation windows and frequency; reference series for beta; investor horizon, obligations, liquidity needs and drawdown capacity; scenario definitions; data quality and coverage flags.

**Relevant Outputs:**
Capital weight versus risk contribution comparison at holding and grouping level; portfolio volatility and diversification benefit; concentration metrics; beta; drawdown depth, duration and recovery; downside and tail measures with uncertainty stated; scenario and reverse-stress results; correlation-stress recomputation; explicit statement of limitations, missing data and the expected-return implications of balance together with the assumptions behind them.

**Risks Addressed:**
Hidden risk concentration; misreading capital weights as risk weights; underestimation of tail and drawdown risk; overreliance on unstable estimated parameters; smoothed-pricing distortion in illiquid holdings; material deterioration of diversification under stressed correlation structures; model-fabricated figures; portfolios exceeding the investor's behavioural capacity.

**Agent Behaviours:**
Report both lenses always; never generate numbers, only interpret them; attach method, window and source to every figure; report multiple estimation windows and flag disagreement; flag smoothed or short-history data; treat drawdown capacity as first-order; separate risk level from risk balance; refuse leverage; state the expected-return implications of balance together with their assumptions, without presenting the trade-off as either absent or certain; preserve the sign and absolute magnitude of risk contributions rather than forcing positive percentage shares; state when data is unavailable rather than estimating; support "no change" as a conclusion.

**Deterministic Calculations Required:**
Return series construction; volatility; correlation matrix; covariance matrix; portfolio variance and volatility; diversification benefit; marginal contribution to risk; contribution to risk by holding and grouping; portfolio weights and drift; beta; concentration metrics; effective number of independent positions; maximum drawdown, duration and recovery; downside deviation; VaR and Conditional VaR; skewness and kurtosis; scenario impacts; reverse stress calculations; correlation-stress recomputation.

**Configurable Parameters:**
Return frequency, currency basis and gross/net convention; volatility and covariance estimation windows and methods; covariance regularisation approach; beta reference series; VaR/CVaR confidence levels and horizons; risk contribution reporting groupings; maximum acceptable risk contribution from a single holding, asset class or driver; scenario library and shock magnitudes; stressed correlation structures and the episodes informing them; the diversification measure adopted; drawdown tolerance parameters. *No values are set in this file.*

**Related Knowledge Files:**
`investment_philosophy.md`, `diversification.md`, `all_weather.md`, `asset_roles.md`, `economic_regimes.md`, `debt_cycles.md`.
