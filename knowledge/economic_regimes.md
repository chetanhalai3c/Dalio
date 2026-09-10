# Economic Regimes

## 1. Purpose

This file is the conceptual foundation for the future **Macro / Cycle Agent**. It defines how EducosysDalio observes and characterises the current economic environment — which dimensions to look at, how to read them, and how to express a view without overstating what is knowable.

Its output feeds exposure and vulnerability analysis. It does **not** feed strategic reallocation. The environments themselves and their portfolio meaning are covered in `all_weather.md`; the credit, debt and fiscal-adjustment dimension is developed further in `debt_cycles.md`.

---

## 2. Core Concept

### 2.1 What a "regime" is here

A regime is a **characterisation of the prevailing macroeconomic conditions** along a small number of dimensions, held with explicit uncertainty. It is a description, not a prediction, and not a category the world is obliged to fit.

Three properties define how EducosysDalio treats regimes:

**They are probabilistic.** At any moment the evidence usually supports more than one characterisation. The honest output is a distribution across plausible regimes, not a single label.

**They are continuous and transitional.** Economies do not step discretely between boxes. Much of the time the correct answer is "transitioning, with mixed signals," and that answer is more useful than a forced classification.

**They are recognised late.** Macroeconomic data is published with lags, subject to revision, and noisy. A regime is usually confidently identifiable only after markets have had time to price it. This is the single most important structural constraint on the value of regime analysis.

### 2.2 The five-layer separation

Every regime assessment EducosysDalio produces must keep these layers distinct and visibly labelled:

**FACT** — Observed, published data. "Headline CPI for the reference month was published at X%, versus Y% the prior month." Includes source and vintage. No interpretation.

**INTERPRETATION** — What the facts appear to indicate. "Core services inflation continues to decelerate more slowly than goods inflation, which is consistent with persistence in the domestically generated component." Reasoning is shown.

**REGIME ASSESSMENT** — The probabilistic characterisation across environments.

**CONFIDENCE** — How much weight the assessment deserves, with the specific reasons for and against.

**POSSIBLE IMPLICATIONS** — What this may mean for portfolio exposures and vulnerabilities, stated conditionally.

Collapsing these layers is the primary failure mode of macro commentary generally, and the one this structure exists to prevent. A statement of interpretation presented as fact, or an implication presented as a forecast, is a defect regardless of how reasonable it sounds.

---

## 3. Dalio / Bridgewater Foundation

### 3.1 Attributable to Dalio / Bridgewater

- **Growth and inflation as the two primary organising axes** for understanding asset-relevant macroeconomic conditions.
- **Emphasis on changes relative to discounted expectations** rather than absolute levels — the argument that markets move on surprises because expectations are already in prices.
- **The economy as a mechanical, transaction-driven system** — the framing that aggregate spending is the sum of money and credit spent, and that this decomposition makes cycles more legible.
- **The layering of short-term debt cycles, long-term debt cycles, and underlying productivity growth** as three overlapping forces that together shape the environment. Developed in `debt_cycles.md`.
- **Credit creation as a first-order macroeconomic variable**, not merely a financial-sector detail — the observation that credit can be created rapidly and contract rapidly, which makes it a major driver of activity swings.
- **Explicit treatment of central-bank policy and liquidity as regime-defining forces**, including the distinction between conventional interest-rate policy and balance-sheet operations.

**Source Note:** These framings appear across Ray Dalio's publicly available material, principally the "How the Economic Machine Works" explanatory video and accompanying document (published circa 2013), *Principles for Navigating Big Debt Crises* (2018, released publicly at no cost), *Principles for Dealing with the Changing World Order* (2021), and Bridgewater's publicly released research commentary. This file describes the general content of that material; specific figures, thresholds, indicator lists or wording should be verified against the primary sources before assertion. Bridgewater's actual internal regime-identification methodology is proprietary and is **not** publicly specified — EducosysDalio must not imply otherwise.

### 3.2 Broader financial theory (not uniquely Dalio)

Most of the *measurement* content of this file is standard macroeconomics and belongs in this category:

- Business-cycle analysis; the classification of indicators as leading, coincident and lagging.
- National accounts, GDP measurement, output gaps and potential output.
- Price index construction; the headline/core distinction; the treatment of shelter, services and imported goods.
- The Phillips-curve family of relationships between labour-market slack and wage/price pressure — contested, unstable, and not to be applied mechanically.
- The Fisher relationship between nominal rates, real rates and inflation expectations.
- Monetary transmission mechanisms and policy-rule frameworks (e.g. Taylor-type rules) as reference points rather than descriptions of actual central-bank behaviour.
- Yield-curve analysis, term premia, and the empirical literature on curve inversion as a recession signal — a relationship with a suggestive record, an unstable lead time, and a modest sample size.
- Credit-spread analysis and the financial-accelerator literature.
- Financial-conditions indices as composite measures.
- Regime-switching statistical models (Markov-switching and similar) as an established econometric family.
- Minsky's financial instability hypothesis, which addresses similar territory to the debt-cycle framing but is independent of Dalio and predates it.
- Nowcasting methodologies for handling publication lags.

### 3.3 EducosysDalio interpretation

The **probabilistic, multi-regime output format**, the **five-layer FACT / INTERPRETATION / ASSESSMENT / CONFIDENCE / IMPLICATIONS separation**, and the **subordination of regime analysis to exposure education rather than allocation** are EducosysDalio design decisions. They are consistent with the spirit of the source material but are not specified by it.

---

## 4. How the Concept Works

### 4.1 The five readings of any indicator

Before any dimension is discussed, this framework applies to every indicator in the file. It is the analytical core of the whole document.

| Reading | Question | Why it matters |
|---|---|---|
| **Level** | What is the value? | Establishes context; often the least informative for asset prices. |
| **Direction** | Is it rising or falling? | First derivative; the basic regime axis. |
| **Rate of change** | Is the movement accelerating or decelerating? | Second derivative; often where inflection is detectable first. |
| **Expectation** | What was anticipated and priced? | Determines what is already in asset prices. |
| **Surprise** | Did the outcome land above or below expectation? | Unexpected information is an important driver of repricing, because expected information may already be reflected in prices. |

Worked illustration, inflation:

- *Level:* inflation is elevated relative to the central bank's target.
- *Direction:* it is falling.
- *Rate of change:* the pace of decline is slowing.
- *Expectation:* markets and forecasters anticipated a faster decline.
- *Surprise:* the outcome was above expectations.

A level-only reading would call this "high inflation." A surprise-aware reading identifies something materially different: **disinflation that is disappointing relative to what is priced** — which typically has quite different implications for rates, discount rates and asset prices than either "high inflation" or "falling inflation" alone would suggest.

**On the weight to give the surprise reading.** Unexpected information is an important driver of repricing, because expected information may already be reflected in market prices. Expected data and unexpected data should therefore not be treated as equivalent, and the surprise reading deserves the analytical prominence given to it here.

It does not follow that economic-data surprise is the only thing that moves asset prices. Prices can also move because of changes in:

- risk premia
- liquidity conditions
- positioning and flows
- policy communication, independent of any data release
- geopolitical events
- valuation and discount-rate shifts
- other information not captured by the economic-data surprise itself

A large surprise may therefore produce little price response, and a substantial price move may occur with no economic surprise behind it at all. Where the observed market reaction does not fit the surprise, EducosysDalio should treat that mismatch as information — it may indicate that something outside the data was driving prices — rather than assuming the reaction was mistaken.

EducosysDalio should attempt all five readings on every material indicator, and should say explicitly when the expectation or surprise component is unavailable rather than substituting the level.

`DETERMINISTIC CALCULATION REQUIRED:` level, period-over-period and year-over-year change, rate-of-change (acceleration/deceleration), and — where consensus expectation data is available — surprise magnitude in standardised units.

`CONFIGURABLE PARAMETER:` the smoothing windows and standardisation method used for rate-of-change and surprise measures. *No values are chosen here.*

### 4.2 Dimension: GROWTH

**What is being assessed:** the pace and direction of real economic activity, and how it compares to what was expected.

**Indicators and how to read them:**

- **Real GDP / output.** The comprehensive measure. Published with a substantial lag, subject to material revision, and quarterly in most jurisdictions. Useful for confirmation; poor for timeliness. Read direction and rate of change more than level.
- **Purchasing-manager and business-survey indices.** Timely, diffusion-based, and typically constructed around an expansion/contraction threshold. Their advantage is speed; their weakness is that they measure breadth of change rather than magnitude, and sentiment can diverge from activity. Read direction and the level relative to the neutral threshold.
- **Employment.** Payroll growth, hiring and quits behaviour, job openings, hours worked, participation. Employment is generally a coincident-to-lagging measure — it confirms rather than predicts. Hours worked and temporary employment have sometimes led.
- **Unemployment.** Lagging. Its *rate of change* from a cyclical low has historically been a more informative signal than its level, but any such rule should be treated as a historical regularity from a limited sample, not a mechanism.
- **Consumption.** Retail sales, real household spending, savings rate, consumer credit usage. Where household consumption is a dominant share of output, this dimension carries proportionate weight.
- **Corporate activity and earnings.** Capital expenditure, inventories, orders, earnings revisions and guidance. Earnings *revisions* — the direction in which analysts are changing estimates — tend to be more informative than earnings levels. Inventory cycles can amplify apparent growth swings.
- **Trade and external demand**, where the economy is externally exposed.

**Reading discipline:** distinguish demand-driven growth changes from supply-driven ones. The same growth number arising from a demand collapse versus a supply constraint has very different implications for inflation, policy and asset behaviour.

### 4.3 Dimension: INFLATION

**What is being assessed:** the pace and direction of price change, its composition, its persistence, and how expectations are anchored.

**Indicators and how to read them:**

- **Headline CPI (or the local equivalent).** What households experience; includes volatile food and energy.
- **Core inflation.** Excludes volatile components to isolate the persistent trend. Neither headline nor core is "correct" — headline drives real incomes and political pressure; core is generally more informative about underlying trend and policy response.
- **Services inflation.** Typically more persistent and more domestically generated than goods inflation, since it is more labour-intensive. Often the more important component for judging whether disinflation is durable. Shelter/housing components carry construction lags in many indices that make them slow to reflect current conditions.
- **Goods inflation.** More exposed to global supply chains, commodity prices and currency movements; typically faster-moving and more mean-reverting.
- **Wage growth.** Relevant both as a cost input and as a support for demand. Its relationship to price inflation depends heavily on productivity growth — wage growth exceeding productivity growth is more inflationary than wage growth alone suggests.
- **Producer prices.** May lead consumer prices, but pass-through is variable and depends on margins and competitive conditions.
- **Inflation expectations.** Two distinct types, and they should not be conflated:
  - *Market-implied* (e.g. breakeven rates derived from inflation-linked versus nominal bonds). Timely and continuous, but contaminated by liquidity conditions and inflation risk premia — a breakeven is not a pure forecast.
  - *Survey-based* (household and professional forecaster surveys). Slower and less precise, but free of market-technical distortion.
  Whether expectations remain anchored is one of the more consequential judgements in inflation analysis, because de-anchoring changes the behaviour of the whole system.

**Reading discipline:** identify the *source* of inflation — demand pull, supply/cost push, energy, currency pass-through, or policy-driven. Different sources imply different persistence and different appropriate policy responses, and therefore different asset implications.

### 4.4 Dimension: MONETARY POLICY

**What is being assessed:** the stance of policy relative to what the economy requires, and its direction of travel.

**Indicators and how to read them:**

- **Policy rates.** The level, the recent direction, and the pace of change. A rapid move is a different signal from a slow one at the same endpoint.
- **The expected path.** Market-implied forward rates and central-bank guidance. Because asset prices reflect the expected path, changes in the *path* often matter more than any single decision.
- **Real interest rates.** The nominal rate adjusted for inflation. Two versions should be kept distinct, because they answer different questions:
  - **Ex-ante real rate** — conceptually, the nominal interest rate minus *expected* inflation over the relevant horizon. This is the measure economic agents actually face when deciding whether to borrow, save or invest, since those decisions are made against inflation that has not yet occurred.
  - **Ex-post real rate** — conceptually, the nominal interest rate minus *subsequently realised* inflation. This can only be computed after the fact. It is useful for historical analysis and for assessing what savers and borrowers actually received, but it was not the rate anyone was responding to at the time.

  For assessing the *current* policy stance, an ex-ante measure is generally the more conceptually relevant starting point. It carries its own difficulty: expected inflation is not directly observable and must be proxied by market-implied or survey measures, each with the limitations described in §4.3.

  **Horizon matching.** The inflation expectation horizon should match the interest-rate horizon being analysed. Pairing a short policy rate with a long-horizon inflation expectation, or the reverse, produces a figure that does not correspond to any decision an economic agent faces.

  A real rate is generally more informative about stance than the nominal rate: a high nominal rate accompanied by higher inflation may be accommodative, and a low nominal rate accompanied by deflation may be restrictive. But real rates should not be interpreted in isolation. The same real rate can be restrictive in one economy or period and accommodative in another, depending on debt structures, credit availability, fiscal stance and the level of the neutral rate.
- **Stance relative to neutral.** Whether policy is restrictive, neutral or accommodative depends on comparison to a neutral real rate — the rate that would neither stimulate nor restrain activity. The neutral rate is **estimated, not directly observable**. Published estimates rest on models with differing assumptions, are revised substantially over time, and can differ materially from one another for the same economy and period. Any statement of the form "policy is restrictive" therefore embeds an estimate with wide uncertainty, and should be presented with that uncertainty attached rather than as an established fact. Where estimates of neutral disagree, EducosysDalio should report the range rather than selecting one.
- **Balance-sheet operations.** Expansion or contraction of central-bank assets, and the mechanics of how reserves and liquidity are affected. This is a separate policy channel from rates and can move in a different direction.
- **Communication and reaction function.** How the central bank has described what it is responding to. Changes in the reaction function can matter more than changes in the rate.
- **Policy lags.** Monetary policy operates with long and variable lags. The economy at any moment is responding partly to decisions made some time ago. This makes "current stance" and "current effect" different things.

### 4.5 Dimension: LIQUIDITY

**What is being assessed:** the availability and price of money and funding across the system.

**Indicators and how to read them:**

- **Composite financial-conditions indices**, which typically blend rates, spreads, equity valuations and currency levels into a single measure. Useful as a summary; opaque about which component is driving the move, so components should be inspected.
- **Money and reserve aggregates**, read for direction and rate of change. The relationship between aggregates and activity has been unstable across eras and should not be applied mechanically.
- **Funding-market conditions** — short-term funding spreads, repo conditions, cross-currency basis. These are among the most direct indicators of stress in market plumbing and can move sharply before broader indicators react.
- **Market liquidity** — bid-offer spreads, market depth, the price impact of trading. Distinct from monetary liquidity: policy can be accommodative while market liquidity is poor.
- **Currency conditions**, particularly for globally significant funding currencies, which affect liquidity well beyond the issuing economy.

**Reading discipline:** liquidity conditions can change faster than growth or inflation, and liquidity shocks are the environments in which diversification most often fails — because correlations converge when the marginal seller is selling for funding reasons rather than fundamental ones. See `diversification.md` §4.3.

### 4.6 Dimension: CREDIT

**What is being assessed:** whether credit is expanding or contracting, on what terms, and how sustainable the associated debt burdens are.

**Indicators and how to read them:**

- **Lending standards.** Bank loan-officer surveys and similar. Among the more useful leading indicators of credit availability, since tightening standards precede reduced credit growth.
- **Credit growth.** Volumes outstanding across household, corporate, financial and government sectors, read for direction and rate of change.
- **Credit spreads.** The compensation demanded for default risk. Widening spreads indicate deteriorating perceived credit quality or reduced risk appetite, and are usually more timely than realised defaults. Sensitive to liquidity as well as to credit fundamentals.
- **Default and delinquency rates.** Lagging — they confirm stress rather than anticipate it. Early-stage delinquencies lead later-stage ones.
- **Leverage.** Debt relative to income, output or assets, by sector. Levels matter for vulnerability; rate of change matters for cycle position.
- **Debt service burden.** Interest and principal payments as a share of income. Rising rates transmit to this measure with a lag that depends on the fixed/floating mix and maturity structure — the same rate rise has very different effects across economies with different mortgage and corporate debt structures.
- **Refinancing schedules.** When debt must be rolled and at what rate relative to its original terms. This determines when accumulated rate changes actually bite.

Full framework treatment is in `debt_cycles.md`. This section covers only the observational dimension.

### 4.7 Dimension: FISCAL POLICY

**What is being assessed:** whether the government's tax and spending position is adding to or subtracting from aggregate demand, and how its financing interacts with bond markets, inflation and the debt-cycle position.

**The central analytical discipline:** *do not analyse fiscal policy using the deficit level alone.* A large deficit that is shrinking may be withdrawing demand from the economy, while a smaller deficit that is widening may be adding it. The level describes the stock position; the **change** describes what fiscal policy is currently doing to activity. This is the same distinction the five readings enforce elsewhere, and it applies here with particular force because the deficit level is the figure most commonly quoted and most commonly misread.

**Indicators and how to read them:**

- **Government spending.** Level, direction and rate of change in real terms. The composition matters: transfers to lower-income households have historically tended to be spent at a higher rate than tax reductions accruing to higher-income households or corporations, so identical headline amounts may have different demand effects.
- **Taxation.** Rates, bases, and changes to both. Timing matters — announced changes can affect behaviour before they take effect.
- **Budget balance.** Deficit or surplus as a share of output. Useful context, but insufficient on its own for the reason given above.
- **Fiscal impulse.** The change in the fiscal position, conventionally adjusted to strip out the part driven by the cycle itself, so that discretionary policy can be separated from the economy's automatic response. This is generally the more informative measure of what fiscal policy is currently contributing. It is an estimated quantity that depends on assumptions about potential output, and different estimates can disagree.
- **Automatic stabilisers.** The components that move counter-cyclically without any decision being taken — unemployment-related spending rising in downturns, tax receipts falling with incomes. These cushion the cycle mechanically. Their strength varies substantially across countries with different welfare and tax structures, which means the same shock produces different fiscal responses in different economies.
- **Discretionary stimulus or tightening.** Deliberate policy changes, distinct from the automatic component. Both the size and the expected persistence matter: a temporary measure and a permanent one of the same magnitude may have different effects on behaviour.
- **Government debt issuance.** The volume, maturity profile and composition of borrowing, and who is absorbing it — domestic institutions, foreign investors, or the central bank. Issuance interacts with bond supply and can affect yields and term premia independently of policy-rate expectations.
- **Interest burden.** Debt service as a share of revenue or output. As rates rise and lower-coupon debt matures, this can grow, absorbing revenue that would otherwise fund other spending and potentially constraining future fiscal choices. Its trajectory depends on the debt stock, the average coupon, the refinancing schedule and nominal growth — see `debt_cycles.md` §4.3.
- **Fiscal tightening / austerity.** Deliberate consolidation through spending reduction or tax increases. Its effect on activity depends on the starting position, the composition of the consolidation, the monetary policy stance accompanying it, and the state of private demand.

**Interaction with monetary policy.** Fiscal and monetary policy can operate in the same direction or in opposition, and the combination matters more than either alone. Fiscal expansion alongside monetary tightening produces a different environment from either occurring on its own, and can complicate the assessment of overall policy stance. Where fiscal expansion is financed in ways that expand central-bank holdings of government debt, the distinction between the two policy channels becomes blurred — a situation examined in `debt_cycles.md` §4.2.

**Crowding-out and crowding-in.** Government borrowing may, under some conditions, raise the cost of capital and displace private investment (crowding out). Under other conditions — notably where private demand is weak and resources are underemployed — public spending may support private activity rather than displace it (crowding in). Which effect dominates depends on the state of the economy, monetary conditions, the openness of the capital account and the use to which the spending is put. The empirical literature is contested and EducosysDalio should not assert a general answer.

**Applying the five readings.** As with every other dimension: *level* (the deficit, debt or spending share), *direction* (is the fiscal position loosening or tightening), *rate of change* (is the loosening or tightening accelerating), *expectation* (what was the market and forecaster expectation for the fiscal path), and *surprise* (did announced policy, revenue outturns or issuance plans differ from what was anticipated). Fiscal surprises — unexpected issuance volumes, unanticipated packages, revenue shortfalls — have at times moved bond markets materially.

**Reading discipline:** fiscal policy is set through a political process, which makes its future path less forecastable than monetary policy and subject to discontinuous change. Announced multi-year plans are statements of intent rather than commitments. EducosysDalio should treat fiscal projections with more uncertainty than it applies to monetary policy paths, and should be explicit that a change of government or of political circumstance can reverse a fiscal trajectory quickly.

**Attribution note.** The material in this subsection is standard macroeconomics and fiscal policy analysis — national accounts, fiscal impulse and cyclically-adjusted balance methodology, automatic stabiliser theory, the crowding-out literature and debt sustainability analysis. It is **not** specific to Dalio or Bridgewater. Dalio's publicly available material does address fiscal responses as one component of debt-cycle adjustment (see `debt_cycles.md` §3.1), but the observational framework set out here belongs to broader theory and should be attributed accordingly.

`DETERMINISTIC CALCULATION REQUIRED:` budget balance and debt as shares of output; changes in the fiscal position period over period; fiscal impulse and cyclically-adjusted balance measures where the underlying series are available; interest burden as a share of revenue and output; issuance volumes and maturity profiles; surprise magnitudes versus fiscal forecasts where consensus data exists.

`CONFIGURABLE PARAMETER:` the fiscal series, jurisdictions and cyclical-adjustment methodology used, together with the source of potential-output estimates on which impulse measures depend. *No values or methodology are chosen here.*

### 4.8 Dimension: MARKET EXPECTATIONS

This dimension is treated with special weight because it is the bridge between the economy and asset prices.

**What is already priced?** Asset prices embed a forecast. Before forming any view, the analysis should attempt to establish what the market currently discounts: the expected policy path in forward rates, expected inflation in breakevens, expected earnings in consensus estimates, expected volatility in options markets, expected default risk in credit spreads.

**Where does the assessment differ from what is priced?** A regime assessment that broadly matches what markets already discount may offer limited *incremental directional* information for tactical positioning. That does not mean the assessment has no value. It may still matter for:

- **portfolio vulnerability** — which exposures would be damaged if the consensus path did not materialise
- **risk-premium assessment** — whether the compensation available for bearing a given exposure looks adequate
- **positioning** — understanding what the portfolio is implicitly aligned with
- **scenario analysis** — constructing the alternative paths worth testing
- **confidence around existing exposures** — whether the evidence supports holding what is already held

A regime view that differs materially from what is priced is a tactical view and must be labelled as such, with a size limit and a falsification condition (see `all_weather.md` §4.5).

**Market expectations are not necessarily correct.** A view being widely held and reflected in prices does not establish that it is right. Consensus expectations have at times been substantially wrong, and prices have at times adjusted sharply when they were. EducosysDalio should therefore ask two questions rather than one:

- *What is currently priced?*
- *What evidence suggests the priced view may be incomplete or wrong?*

Asking only the first collapses into assuming the market is correct. Asking only the second collapses into ignoring what is already reflected in prices. Both are needed.

**Prices reflect more than expected macro outcomes.** A market-implied measure is not a clean forecast, because the price also incorporates:

- risk premia — compensation demanded for bearing uncertainty, which varies over time
- positioning and flows
- liquidity conditions
- hedging demand, which can move prices for reasons unrelated to any view
- technical and structural flows, including index, regulatory and collateral-driven activity
- the level of uncertainty itself, distinct from the central expectation

This is why a breakeven inflation rate is not simply "the market's inflation forecast," and why a forward rate is not simply "the market's expected policy path." Extracting an expectation from a price requires assumptions about these other components, and those assumptions carry their own uncertainty.

**Positioning and sentiment.** Where observable, extreme positioning or sentiment can indicate that a view is crowded, which changes the asymmetry of outcomes independent of whether the view is correct.

### 4.9 Producing the regime output

The output format EducosysDalio should build toward is a **distribution across environments with an explicit confidence statement**, structured conceptually like this:

```
Growth rising / Inflation falling:  45%
Growth rising / Inflation rising:   25%
Growth falling / Inflation falling: 20%
Growth falling / Inflation rising:  10%

Confidence: Moderate
```

**This example is illustrative only.** The numbers are invented for the purpose of showing the shape of the output.

Critical constraints on this format:

**No probability model is specified here.** EducosysDalio does not yet have a defensible method for producing calibrated probabilities. Until one exists, any numbers of this kind are structured judgement, not measurement, and must be presented as such.

**An LLM should not invent these figures unaided.** Language models produce plausible-looking numbers readily and calibrated ones rarely. Whatever method eventually generates the distribution should be documented, reproducible, and separable from the narrative layer.

**Qualitative output is acceptable and often preferable.** "Evidence currently leans toward decelerating growth with continuing but slowing disinflation; the signals conflict on the labour-market dimension; confidence is low" is a more honest output than a precise-looking percentage split with no method behind it.

**Confidence must be reasoned, not asserted.** State what would raise confidence, what would lower it, and which specific observations conflict.

`DETERMINISTIC CALCULATION REQUIRED:` all indicator transformations (changes, rates of change, standardisation, surprise magnitudes, composite aggregations) and any eventual probability computation.

`CONFIGURABLE PARAMETER:` the indicator set, weighting scheme, and aggregation method used to form the regime distribution. *Not specified here.*

`CONFIGURABLE PARAMETER:` confidence banding definitions and the criteria that map evidence quality to a confidence label. *Not specified here.*

### 4.10 Data honesty requirements

Every regime assessment must carry its own limitations:

- **Publication lag.** State the reference period of each data point, not just its release date.
- **Revision risk.** Note where data is preliminary or historically revision-prone.
- **Conflicting signals.** Report indicators that contradict the assessment. Selective presentation of confirming evidence is the most common way macro analysis becomes misleading.
- **Geographic scope.** Regimes differ across economies. State which economy or bloc the assessment covers, and note where the investor's portfolio is exposed to a different one.
- **Sample limitations.** Many macro relationships rest on a small number of historical cycles. Be explicit when a claimed regularity has few independent observations behind it.

---

## 5. Portfolio Implications

Regime analysis in EducosysDalio serves four purposes, in this order of priority:

**1. Education.** Helping the investor understand what is happening in the economy and why it might matter. This has standalone value even if it never changes a single holding.

**2. Exposure analysis.** Mapping which of the portfolio's exposures are most sensitive to the currently live macroeconomic questions. "Your portfolio's largest single sensitivity is to real interest rates, and real rates are currently the most contested variable in this environment" is a genuinely useful observation.

**3. Vulnerability analysis.** Identifying which plausible environmental paths would damage this specific portfolio most, and how badly. This connects directly to scenario and stress analysis in `risk_balancing.md`.

**4. Scenario awareness.** Preparing the investor psychologically and practically for outcomes that have not occurred, so that a drawdown is a recognised possibility rather than a shock that triggers a poorly timed decision.

**What regime analysis is explicitly not for:**

It is not for timing the strategic allocation. The reasons are structural, not stylistic:

- Regimes are recognised with a lag, typically after markets have priced them.
- The current environment is usually the most widely discussed, and is therefore more likely to be substantially reflected in prices already — though not necessarily correctly or completely.
- Being right about the economy and wrong about the market reaction is common, because the market reaction depends on what was already expected.
- A strategic portfolio restructured around a regime view fails badly when the view is wrong — which is the outcome the whole system is designed to avoid.

The permanent test applies: **if this regime assessment is wrong, is the strategic portfolio still robust?**

---

## 6. EducosysDalio Interpretation

**6.1 Always probabilistic.** EducosysDalio does not state "we are in regime X." It states a distribution or a hedged qualitative characterisation, with confidence and with the conflicting evidence named.

**6.2 Layers stay separate.** The FACT / INTERPRETATION / REGIME ASSESSMENT / CONFIDENCE / POSSIBLE IMPLICATIONS structure is enforced in output, not merely in reasoning. The investor must be able to see which parts are observation and which are judgement.

**6.3 Surprise-aware by default.** Every material indicator is read on all five readings where data permits, and the absence of expectation data is disclosed rather than papered over.

**6.4 Numbers come from code, narrative comes from the model.** Deterministic components compute the indicator transformations; the reasoning layer interprets them. The reasoning layer does not generate figures.

**6.5 Regime informs vulnerability, not strategic weights.** A regime view may legitimately trigger: an explanation, a vulnerability warning, a scenario analysis, a rebalancing reminder, a liquidity check, or a small explicitly-labelled tactical view within the configured limit. It does not trigger a strategic restructure.

**6.6 "The signals conflict" is a valid and often correct answer.** Forcing a classification when the evidence is genuinely mixed manufactures false confidence. Transitional and ambiguous periods are common.

**6.7 Multi-region awareness.** Where a portfolio spans economies in different cyclical positions, the assessment is produced per relevant region rather than globally averaged into a single meaningless label.

**6.8 Track and disclose the record.** Where feasible, prior regime assessments should be retained so that the system's accuracy over time is visible. An advisor whose past macro assessments are unreviewable is asking for unearned trust.

---

## 7. Failure Modes / Misinterpretations

**False precision.** Producing percentage distributions with no defensible method, so that the format implies rigour the content does not have.

**Single-label certainty.** Declaring the regime, which is the behaviour this file exists to prevent.

**Narrative fitting.** Selecting the indicators that support a preferred story and omitting those that do not. This is the most insidious failure because the result reads as coherent analysis.

**Level-only reading.** Ignoring direction, acceleration, expectations and surprises, and thereby analysing something other than what drives prices.

**Ignoring what is priced.** Treating a widely held macro view as if it were an insight, without first establishing what markets already discount. A view that is broadly shared may already be reflected in prices, which limits its incremental directional value — though it does not make the view wrong, and does not remove its value for vulnerability and scenario work.

**Assuming what is priced is correct.** The mirror error: treating market expectations as authoritative because they are market expectations. Consensus has at times been substantially wrong. Prices also embed risk premia, positioning and flows, so they are not a clean statement of expected outcomes in any case.

**Lag blindness.** Treating published data as a description of the present rather than of a reference period in the past.

**Mistaking a signal for a mechanism.** Applying historical regularities — curve inversion, unemployment rate-of-change rules, aggregate-based rules — as if they were causal laws, when they rest on small samples and have failed before.

**Confusing forecasting with understanding.** The value of macro analysis here is comprehension of exposure. Drifting toward prediction is drift away from the system's purpose.

**Allowing the regime view to drive strategic allocation.** The central prohibition.

**Over-frequent reassessment.** Regenerating a regime view constantly encourages activity, anchors on noise, and creates an illusion of responsiveness. Macro conditions change more slowly than data releases arrive.

**Home-economy assumption.** Assuming the investor's domestic regime applies to globally diversified holdings.

**Ignoring non-quadrant risks.** Liquidity events, credit accidents, geopolitical shocks, policy errors and market-structure failures do not reduce to growth and inflation.

---

## 8. Questions EducosysDalio Should Ask

**About observation**

- What is the reference period of this data, and how revision-prone is it?
- On all five readings — level, direction, rate of change, expectation, surprise — what does this indicator say?
- Which indicators contradict the emerging assessment?
- Is this growth change demand-driven or supply-driven? Is this inflation demand-pull, cost-push, energy, or currency pass-through?

**About the assessment**

- What distribution across environments does the evidence support, and how wide is it?
- What is the confidence level, and specifically what drives it up or down?
- What single observation would most change this assessment?
- Which economy or bloc does this assessment cover, and does that match the portfolio's exposure?

**About fiscal policy**

- Is fiscal policy becoming more expansionary or more restrictive — and is that judgement based on the change, not the deficit level alone?
- What is the direction and rate of change of the fiscal impulse?
- What fiscal path was expected, and has policy or issuance surprised relative to it?
- Is fiscal policy currently supporting or weakening aggregate demand?
- Is it adding to or reducing inflation pressure?
- How is government borrowing affecting bond supply, yields and term premia?
- Is the interest burden becoming a more significant constraint on future policy choices?
- How does the fiscal stance interact with the current monetary stance, and with the debt-cycle position in `debt_cycles.md`?

**About expectations**

- What is currently priced in policy rates, breakevens, earnings estimates and credit spreads?
- What evidence suggests the priced view may be incomplete or wrong?
- How much of the market-implied measure is likely to be risk premium, positioning or liquidity rather than expectation?
- Does this assessment differ from what is priced? If so, in what direction and how confidently?
- If it does not differ, what value does it still add for vulnerability, risk-premium assessment, scenario work and confidence in existing exposures?

**About portfolio relevance**

- Which of this portfolio's exposures are most sensitive to the currently contested macro variables?
- Under each of the plausible environmental paths, which holdings would be most affected?
- What would have to happen for this portfolio to experience its worst outcome, and how plausible is that path?

**The governing question**

- If this regime assessment turns out to be wrong, is the strategic portfolio still robust?
- Does anything being proposed require this assessment to be correct? If so, it is tactical, not strategic — is it sized accordingly?

---

## 9. Structured Knowledge Summary

**Principle:**
Understand the economic environment probabilistically and use that understanding to explain exposure and vulnerability — not to time the strategic allocation.

**Objective:**
Provide the future Macro / Cycle Agent with a rigorous, uncertainty-preserving method for observing and characterising the economic environment across growth, inflation, monetary policy, liquidity, credit, fiscal policy and market expectations.

**Relevant Inputs:**
Growth indicators; inflation indicators and expectation measures; policy rates, expected paths and balance-sheet data; financial-conditions and funding-market measures; credit aggregates, standards, spreads and debt-service data; fiscal balances, spending and tax data, impulse and cyclically-adjusted measures, issuance and interest-burden data; market-implied expectations; consensus forecasts for surprise computation; data vintages and revision history.

**Relevant Outputs:**
Layered assessment separating fact, interpretation, regime assessment, confidence and possible implications; probabilistic or hedged qualitative regime characterisation; named conflicting evidence; exposure sensitivity mapping; vulnerability identification; scenario descriptions; explicit data limitations.

**Risks Addressed:**
False macro certainty; narrative fitting; overreaction to lagged data; conflation of observation with prediction; unrecognised portfolio sensitivity to contested macro variables; regime-driven strategic reallocation.

**Agent Behaviours:**
Never declare a single regime with certainty; enforce the five-layer output separation; read indicators on all five readings; state what is already priced while also asking what evidence suggests the priced view may be incomplete; assess fiscal stance by change rather than level alone; report contradicting evidence; produce per-region assessments; use deterministic components for all numbers; recommend education and vulnerability awareness rather than reallocation; apply the robustness test to every implication.

**Deterministic Calculations Required:**
Indicator changes, rates of change and smoothing; standardisation and z-scoring; surprise magnitudes versus consensus; fiscal balance, impulse, issuance and interest-burden measures; composite index construction; any regime probability computation; historical regime classification of past periods; portfolio sensitivity mapping to macro variables.

**Configurable Parameters:**
Indicator set and data sources; smoothing and standardisation windows; regime aggregation and weighting method; confidence banding criteria; reassessment frequency; regional scope definitions; fiscal series, jurisdictions and cyclical-adjustment methodology including the potential-output source. *No values are set in this file.*

**Related Knowledge Files:**
`investment_philosophy.md`, `all_weather.md`, `debt_cycles.md`, `risk_balancing.md`, `asset_roles.md`, `diversification.md`.
