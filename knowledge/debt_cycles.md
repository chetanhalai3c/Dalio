# Debt Cycles

## 1. Purpose

This file explains Ray Dalio's debt-cycle framework at a conceptual level and, more importantly, defines what EducosysDalio should *do* with it.

The framing question throughout is:

> **What does this framework tell us about portfolio vulnerability?**

not

> *How can we predict the next financial crisis?*

The credit indicators used to observe cycle conditions are listed in `economic_regimes.md` §4.6. This file supplies the framework that gives those indicators meaning.

---

## 2. Core Concept

### 2.1 Why credit deserves a separate framework

Spending in an economy is funded by money and by credit. Credit can expand much faster than current income, because lending creates a new financial claim between borrower and lender rather than transferring existing income. In practice, however, credit creation is constrained by factors such as:

- lender balance-sheet capacity
- capital and liquidity requirements
- underwriting standards
- collateral
- borrower creditworthiness
- funding conditions
- regulation
- demand for borrowing

The important macroeconomic point is not that credit can be created without constraint, but that credit can expand or contract much faster than productive capacity and income. This makes credit a source of amplification: it allows spending to exceed current income for a period, and it later requires spending to fall below income while the debt is serviced or repaid. Credit expansion can amplify spending on the way up, and credit contraction can amplify downturns on the way down.

One agent's debt is another's asset, and one agent's spending is another's income. That circularity is what turns individual borrowing decisions into system-level cycles.

The consequence for a portfolio analyst: **credit conditions can change the distribution of outcomes for nearly every asset simultaneously**, which is precisely the situation in which diversification measured on ordinary-period data provides least protection.

### 2.2 Three overlapping forces

The Dalio framing separates three forces operating at different timescales:

**Productivity growth** — the slow, upward-trending force from output per unit of input. It is the only one of the three that raises long-run living standards, and it is relatively steady.

**The short-term debt cycle** — the recurring expansion and contraction of credit, typically associated with the ordinary business cycle. Historically these have often run over several years, though the duration varies considerably and no fixed period should be assumed.

**The long-term debt cycle** — the accumulation of debt burdens across multiple short-term cycles, over a period long enough that most participants have no personal experience of a full one. This makes it structurally harder to recognise.

At any moment an economy sits somewhere in all three simultaneously. Confusing which force is operating is a common analytical error: the same slowdown means something different depending on whether it is an ordinary short-cycle contraction or an episode within a long-cycle adjustment.

---

## 3. Dalio / Bridgewater Foundation

### 3.1 Attributable to Dalio / Bridgewater

- **The explicit separation of short-term and long-term debt cycles**, and the layering of both on top of a productivity trend line.
- **The transactional model of the economy** — treating aggregate spending as the sum of money and credit spent, and deriving cycle behaviour from that identity.
- **The long-term debt cycle as a multi-decade phenomenon** ending in a period where debt burdens grow faster than incomes and conventional monetary policy loses effectiveness.
- **The taxonomy of deleveraging responses** — the framing that adjustment occurs through some combination of austerity, debt restructuring/default, wealth transfers, and monetary expansion (including, at its most direct, monetary financing of government obligations), and that the *mix* of these determines whether the adjustment is deflationary, inflationary, or comparatively orderly. The framing is Dalio's; the disaggregation of the monetary category into asset purchases, direct monetary-fiscal financing and broader liquidity measures set out in §4.2 is EducosysDalio's, added for analytical precision.
- **The concept of a comparatively well-managed deleveraging** — Dalio's argument that when the deflationary and inflationary forces of adjustment are balanced, debt burdens can decline relative to income without either a deflationary collapse or an inflationary spiral. Dalio has publicly used the phrase "beautiful deleveraging" for this.
- **The distinction between debt denominated in one's own currency versus foreign currency**, and how that constrains the available policy responses.
- **The study of debt crises as a repeating archetype** with recognisable phases, derived from a large set of historical cases.
- **The linkage of debt dynamics to broader questions of reserve-currency status and long-cycle geopolitical shifts** — developed in Dalio's later work.

**Source Note:** These framings are drawn from Ray Dalio's publicly available material: "How the Economic Machine Works" (explanatory video and accompanying document, published circa 2013), *Principles for Navigating Big Debt Crises* (2018, released publicly at no cost by Bridgewater), and *Principles for Dealing with the Changing World Order* (2021). Specific case studies, numerical templates, phase definitions and quantitative indicators should be verified against those sources directly before assertion. This file does not reproduce any specific numbers, thresholds or quotations from them.

### 3.2 Broader financial theory (not uniquely Dalio)

Considerable overlapping work exists independently, and EducosysDalio should not attribute it to Dalio:

- **Minsky's financial instability hypothesis** — the argument that extended stability encourages progressively more fragile financing structures (hedge, speculative, Ponzi), leading endogenously to instability. This predates and parallels the Dalio framing and is independently influential.
- **Kindleberger's historical anatomy of manias, panics and crashes**, and the broader financial-history literature.
- **Fisher's debt-deflation theory** (1930s) — the mechanism whereby falling prices raise the real burden of nominal debt, forcing further liquidation. This is the intellectual ancestor of much of the deflationary-adjustment discussion.
- **The credit-cycle and financial-accelerator literature in academic macroeconomics** — how balance-sheet conditions amplify shocks.
- **Reinhart and Rogoff's cross-country historical study of debt and financial crises**, which is empirical work independent of Bridgewater.
- **Balance-sheet recession analysis** (associated with Richard Koo) — the argument that after asset-price collapses, indebted entities prioritise debt reduction over profit maximisation, which blunts monetary policy.
- **The literature on the effective lower bound on nominal rates, and on unconventional monetary policy.**
- **Sovereign-debt sustainability analysis**, standard in official-sector economics.

Where the Dalio framework and these bodies of work agree, EducosysDalio should note the convergence — agreement across independent frameworks is stronger evidence than any single framework's assertion.

### 3.3 EducosysDalio interpretation

EducosysDalio uses the debt-cycle framework **as a vulnerability lens, not as a forecasting engine**. Specifically: to identify which portfolio exposures depend on continued credit availability, which depend on the current debt-servicing environment persisting, and which would be damaged under each form of adjustment. That application is this project's decision.

---

## 4. How the Concept Works

### 4.1 The short-term debt cycle

Conceptually, the sequence runs roughly as follows. It is a stylised description of tendencies, not a schedule.

**Expansion phase**
- Credit is available and its cost is low relative to expected returns.
- Borrowing increases across households, firms, or both.
- Borrowed funds are spent, so aggregate spending rises faster than income.
- Because one entity's spending is another's income, incomes rise.
- Rising incomes and rising asset values improve perceived creditworthiness, which supports further borrowing.
- The feedback loop is self-reinforcing on the way up.

**Pressure phase**
- Spending growth exceeding the economy's productive capacity generates price pressure.
- Capacity constraints appear in labour markets and supply chains.
- Inflation pressure builds.

**Tightening phase**
- The central bank raises policy rates to restrain demand.
- Borrowing becomes more expensive; debt service costs rise, with a lag determined by the fixed/floating mix and maturity structure of existing debt.
- New credit creation slows.
- Lending standards tighten, often ahead of observable declines in credit volumes.

**Contraction phase**
- Slower credit growth means slower spending growth.
- Slower spending means slower income growth.
- Debt service is now a larger share of a slower-growing income.
- The feedback loop that operated on the way up now operates in reverse.
- Asset prices may fall, further impairing collateral and creditworthiness.

**Easing phase**
- Inflation pressure subsides as demand weakens.
- The central bank lowers rates.
- Credit gradually becomes available again, and the cycle can restart.

**What matters for a portfolio:** the transitions, not the phases. Assets tend to reprice sharply at inflection points, and the inflections are exactly what is hardest to identify in real time.

### 4.2 The long-term debt cycle

The long-term cycle is the accumulation across many short-term cycles.

**The accumulation pathway.** One stylised pathway described in the Dalio framework is that successive short-term cycles can leave debt burdens higher relative to income, while policy easing and declining interest rates make those larger debt stocks serviceable for a long period. Where this pattern persists across multiple cycles, leverage can accumulate over decades.

This is not a mechanical requirement of every economy or every cycle. Debt ratios can fall, rates do not need to make a new low in every cycle, and institutional, demographic, fiscal and productivity differences can materially alter the path. EducosysDalio should treat the pathway as one plausible pattern to test against the evidence for a given economy, not as a description of what must be happening.

**The role of falling interest rates as a support.** A long secular decline in interest rates can make rising debt *stocks* more serviceable in terms of debt *service*, because each refinancing lowers the cost. This can continue for a long time, and during it debt-to-income ratios may rise substantially without visible stress. The critical structural observation: **this support mechanism is finite.** Nominal rates can in some systems be pushed moderately below zero, so there is no single fixed floor, but the room available is practically bounded — cash holding, financial-system profitability, deposit behaviour and institutional constraints all limit how far and for how long rates can be reduced. The point to preserve is not that rates stop at zero, but that the ability to support ever-higher debt burdens through progressively easier *conventional* interest-rate policy is finite, and diminishes as rates approach that practical bound.

**Limits to conventional policy.** As policy rates approach their effective lower bound, the room for further conventional easing narrows sharply and may be largely exhausted. Authorities may then turn to balance-sheet operations, credit guarantees, direct fiscal transfers, or other unconventional measures. These have different transmission mechanisms and different distributional and inflationary consequences from rate cuts.

**Debt servicing pressure.** As debt service consumes a larger share of income, less income remains for other spending. This weighs on growth independent of the level of rates. The burden depends on the debt stock, the average interest rate, the amortisation schedule, and income growth — a change in any of these can alter the burden without a change in the others.

**Deleveraging.** The process of reducing debt relative to income. It can occur through:
- **Austerity** — spending less. Deflationary; also reduces incomes, which can raise debt-to-income ratios even as debt falls in absolute terms. This is the counterintuitive core of the debt-deflation problem.
- **Debt reduction** — defaults, write-downs, restructurings, maturity extensions, rate reductions. Deflationary; imposes losses on creditors.
- **Wealth transfers** — redistribution through taxation or other policy, including transfers between generations, sectors or nations. Politically difficult and often slow.
- **Monetary and liquidity expansion** — a family of measures that are often grouped together but operate differently and should be kept distinct:
  - **Central-bank asset purchases / QE.** The central bank creates reserves and purchases securities, frequently in secondary markets. This changes the composition and duration of the financial assets held by the private sector, and can affect liquidity, yields and financial conditions more broadly. It is **not automatically identical to directly financing government spending**, and conflating the two is a common analytical error.
  - **Direct or close monetary-fiscal financing.** Fiscal spending or transfers are effectively financed through monetary expansion, or through persistent central-bank absorption of government debt issuance. This involves a more direct interaction between fiscal and monetary policy than asset purchases alone, and the boundary between the two can be blurred in practice rather than sharp.
  - **Broader monetary expansion.** Other measures that expand liquidity or credit availability — lending facilities, credit guarantees, collateral easing, reserve requirement changes.

  These measures can reduce the real burden of nominal debt and can create inflationary pressure under some conditions. Whether they do so, and to what degree, depends on economic slack, private credit creation, the fiscal stance, velocity and spending behaviour, supply constraints, expectations, and institutional credibility. EducosysDalio should therefore not treat monetary expansion as inflationary in a simple one-for-one way; the historical record includes episodes of substantial balance-sheet expansion accompanied by subdued inflation, and episodes where expansion coincided with significant inflation.

The distinction the Dalio framework draws is between **deflationary adjustment forces** — austerity, defaults and write-downs, falling incomes and asset prices — and **inflationary or reflationary policy responses**. That distinction should be preserved, while recognising that the second category contains several mechanisms with different transmission channels.

The Dalio framing holds that the *balance* between deflationary and inflationary responses determines the character of the adjustment. Heavily deflationary adjustments tend to be severe and prolonged; heavily inflationary ones risk currency and expectation de-anchoring; a balanced mix can allow debt-to-income to decline with less disruption.

**Currency denomination.** Currency denomination materially changes debt vulnerability, and this remains one of the more durable structural insights in the framework. The distinction must be drawn precisely, however, because only a sovereign or public monetary authority with control over a currency can create it — private companies and households cannot.

**Sovereign monetary issuer.** A government or monetary authority whose debt is denominated in a currency it controls has policy options unavailable to a borrower owing foreign-currency debt: nominal default is a choice rather than a necessity, and the debt can in principle be serviced in currency the authority can issue. Those options are still constrained by:

- inflation, and the real cost imposed on holders of the currency
- currency credibility and exchange-rate consequences
- capital flows and the willingness of foreign holders to remain
- institutional arrangements, including membership of currency unions or fixed-exchange-rate regimes
- political constraints on what policy is actually available
- central-bank independence and mandate, which may prohibit the relevant action
- investor confidence, which can deteriorate well before any formal limit is reached

"Can issue the currency" is therefore not "faces no constraint." It changes the *form* the constraint takes — from an outright inability to pay toward inflation, currency depreciation and confidence effects.

**Foreign-currency sovereign borrower.** A sovereign owing material debt in a currency it cannot create faces much tighter constraints and materially greater default and restructuring risk, since servicing depends on earning or borrowing that currency. This is the situation in many historical sovereign crises, and it is a genuinely different category from the case above.

**Private borrowers.** Households and companies cannot create currency in any circumstance, so the sovereign distinction does not apply to them. For private borrowers the relevant questions are:

- is income earned in the same currency as the debt?
- are assets and liabilities currency-matched?
- are rates fixed or floating?
- is refinancing required, and when?
- is any hedging in place, and for how long does it run?

A company earning GBP while owing USD debt, for example, carries currency mismatch risk even though both currencies are issued by credible sovereigns. Currency mismatch at the private level has been a recurring source of stress independent of sovereign creditworthiness, and EducosysDalio should assess it separately rather than inferring private resilience from sovereign currency status.

### 4.3 The key quantities

**Debt service burden** — interest plus principal payments as a share of income. More informative than the debt stock alone. Two economies with identical debt-to-GDP ratios can face very different burdens depending on rates and maturity structure.

**Credit expansion / contraction** — the rate of change of credit outstanding. Rate of change generally matters more for near-term activity than the level.

**Financial leverage** — debt relative to assets or equity. Determines how far asset prices must fall before solvency is threatened, and therefore how much amplification a given shock produces.

**Refinancing profile** — when existing debt matures and must be rolled. Determines *when* a change in rates transmits into actual debt service. A long-duration, fixed-rate debt structure delays transmission substantially; a short-duration or floating-rate structure transmits quickly. This single structural variable explains much of why the same rate move affects different economies so differently.

**Sectoral distribution** — total leverage tells you less than *where* it sits. Household, non-financial corporate, financial-sector and government leverage have different transmission mechanisms, different policy responses available, and different portfolio implications.

`DETERMINISTIC CALCULATION REQUIRED:` debt-to-income and debt-to-output ratios by sector; debt service ratios; credit growth rates and their rate of change; leverage measures; credit spread levels and changes; refinancing wall profiles where data is available.

`CONFIGURABLE PARAMETER:` the sectors, geographies and data series included in credit condition monitoring. *No values are chosen here.*

### 4.4 What this framework can and cannot do

**What it can reasonably do:**
- Identify whether credit conditions are expanding or contracting, and at what pace.
- Identify where leverage is concentrated and therefore where a shock would amplify.
- Identify whether debt service burdens are rising or falling, and what would change them.
- Explain the mechanism by which credit conditions transmit into activity and asset prices.
- Identify which policy responses are available and which are constrained.
- Provide a structured way to think about what an adjustment might look like — deflationary, inflationary, or mixed — and which assets would be affected differently under each.

**What it cannot do:**
- Time anything. Debt burdens have risen for extended periods without crisis. Elevated leverage is a statement about *fragility*, not about *timing*.
- Specify thresholds. There is no debt-to-GDP level at which crisis reliably occurs. Sustainable levels depend on currency denomination, rate structure, ownership of the debt, institutional credibility, growth rates and the availability of policy responses.
- Predict which form the adjustment takes. The mix of austerity, default, transfers and monetary expansion is a *political* outcome, not an economic inevitability. Political outcomes are especially poorly forecast.
- Substitute for other evidence. Not every economic environment is primarily a debt story.

### 4.5 Limitations to state explicitly

**Small independent sample.** Long-term debt cycles are, by construction, rare. The number of well-documented complete cycles in comparable modern economies is small. Any claim of a repeating pattern rests on limited independent observations, and pattern-recognition on small samples is unreliable.

**Retrospective clarity.** Cycle phases are far easier to identify after the fact. The framework's explanatory coherence is not evidence of its predictive accuracy.

**Institutional and structural change.** Financial systems, policy frameworks, regulatory regimes, currency arrangements and market structures differ across the historical cases. Mechanisms that operated in one era may operate differently now.

**Narrative attractiveness.** The debt-cycle framework is compelling and internally coherent, which makes it easy to over-apply. A framework that can explain any outcome after the fact provides less decision-relevant information than its coherence suggests.

**Persistent-warning risk.** Concerns about unsustainable debt have been voiced for many years across many economies. Portfolios positioned continuously for a debt crisis have at times performed poorly for long stretches. Recognising fragility is not the same as acting on it, and the cost of premature defensive positioning is real.

**Not the only framework.** Minsky, Fisher, Koo, Reinhart–Rogoff and the academic credit-cycle literature cover similar ground with different emphases. Where they converge, confidence rises; where they diverge, that divergence is information.

---

## 5. Portfolio Implications

The debt-cycle framework matters to EducosysDalio because it identifies vulnerabilities that ordinary volatility and correlation analysis, estimated on ordinary periods, will systematically understate.

**Credit-condition dependence.** Which holdings require continued credit availability to perform? Equities of leveraged businesses, credit instruments, property, private assets and anything financed with borrowed money all carry this dependence, often in ways not obvious from the asset label.

**Debt-service sensitivity.** Which holdings are exposed to entities whose debt service is rising? This includes the investor's own borrowings — a portfolio held alongside a large floating-rate mortgage has a different risk profile from the same portfolio held unlevered.

**Diversification failure in credit stress.** Credit contractions are among the conditions in which correlations converge. Assets that appear to diversify one another in ordinary periods may not do so in a forced-deleveraging episode, because selling pressure is driven by funding needs rather than fundamentals. See `diversification.md` §4.3.

**Asymmetry of adjustment paths.** A deflationary adjustment and an inflationary adjustment damage different assets:
- *Deflationary tendencies* — nominal government bonds of creditworthy issuers have historically tended to benefit; credit-sensitive, equity and real assets have tended to suffer.
- *Inflationary tendencies* — nominal bonds have tended to suffer in real terms; inflation-linked instruments, commodities and some real assets have tended to fare relatively better; equities have had mixed experience depending on pricing power and the level of real rates.

A portfolio positioned for only one of these paths carries a large concentrated bet on a *political* outcome. This is precisely the kind of dependence the system exists to surface. Details in `asset_roles.md`.

**Liquidity adequacy.** Credit contractions are when access to cash matters most and is hardest to arrange. This connects the framework directly to a practical question: does the investor hold enough liquidity to avoid becoming a forced seller?

`CONFIGURABLE PARAMETER:` minimum liquidity reserve, expressed relative to the investor's spending needs and obligations. *No value is chosen here.*

**Counterparty and structural exposure.** Where the portfolio depends on intermediaries, leverage-embedding structures, or products whose redemption terms are more liquid than their underlying assets, credit stress is when those dependencies matter.

---

## 6. EducosysDalio Interpretation

**6.1 Vulnerability lens, not forecasting engine.** EducosysDalio uses the framework to ask "what would hurt this portfolio, and how exposed is it?" It does not use it to predict crises or to time markets.

**6.2 Both adjustment paths are represented as plausible.** EducosysDalio does not adopt a house view on whether adjustment will be deflationary or inflationary. It treats the mix as uncertain and politically determined, and evaluates the portfolio against both.

**6.3 No thresholds.** EducosysDalio does not assert that any debt level is unsustainable. It describes direction, rate of change, structure and constraints, and identifies conditions that would increase or decrease fragility.

**6.4 Fragility is not timing.** When elevated leverage is identified, EducosysDalio states plainly that this is an observation about vulnerability, that it carries no timing implication, and that positioning defensively on this basis has historically had a real opportunity cost.

**6.5 Integration, not domination.** Debt-cycle evidence is one input alongside growth, inflation, policy, liquidity and market expectations. EducosysDalio should not force every environment into a debt-cycle narrative. When credit evidence conflicts with other macro evidence, the conflict is reported rather than resolved by preferring one framework.

**6.6 The investor's own balance sheet is in scope.** Personal leverage — mortgages, margin, business borrowings, guarantees — is part of the analysis. A household's debt-cycle position is as relevant to its portfolio as the economy's.

**6.7 Response bias is toward robustness, not repositioning.** The typical appropriate response to identified credit vulnerability is: explain it, verify liquidity adequacy, check that the portfolio does not depend on one adjustment path, confirm no forced-selling scenario exists — and often, change nothing.

**6.8 Attribution discipline.** Where the framework aligns with Minsky, Fisher, Koo or the academic literature, say so. Convergence across independent frameworks is stronger evidence than any single one, and honest attribution is more useful to the investor than a single-source narrative.

---

## 7. Failure Modes / Misinterpretations

**Treating the framework as a predictive schedule.** Assuming cycles have fixed durations or that a recognisable phase implies a known next step. Historical cycles have varied considerably in length and character.

**Perpetual crisis positioning.** Identifying elevated leverage and remaining defensively positioned indefinitely. The opportunity cost is real and can be very large.

**Threshold invention.** Asserting that some debt ratio is the danger point. No such general threshold is supportable.

**Assuming an inevitable adjustment form.** Confidently predicting either deflationary collapse or inflationary debasement. The mix is a political choice, and political outcomes are among the least forecastable.

**Single-framework capture.** Interpreting every macroeconomic condition through debt, ignoring supply shocks, technological change, demographics, geopolitics and policy shifts that operate independently.

**Ignoring institutional differences.** Applying insights from one economy's crisis to another with a different currency status, debt ownership structure, regulatory framework or institutional credibility.

**Confusing stock and flow.** Focusing on debt levels while ignoring debt service, refinancing structure and the rate of change of credit — which are usually more informative for near-term conditions.

**Ignoring sectoral location.** Treating aggregate leverage as sufficient without asking which sector holds it and what policy responses are available to that sector.

**Overlooking the investor's own leverage.** Analysing the portfolio in isolation from the household balance sheet.

**Mistaking coherence for accuracy.** The framework explains history persuasively. That is a property of good narrative frameworks generally and is weak evidence of predictive power.

**Recommending action from fragility alone.** Fragility is a standing condition of leveraged financial systems. It justifies robustness and liquidity adequacy; it rarely justifies dramatic repositioning.

---

## 8. Questions EducosysDalio Should Ask

**About the environment**

- Is credit currently expanding or contracting, and at what rate of change?
- Are lending standards tightening or loosening?
- Where is leverage concentrated by sector, and how has that changed?
- What is the debt service burden, and is it rising or falling?
- What is the refinancing profile — when does existing debt need to be rolled, and at what rate relative to its current cost?
- For sovereign debt: is it denominated in a currency the issuing authority controls, and what constraints — inflation, credibility, capital flows, institutional mandate — still apply?
- For private borrowers: is income earned in the same currency as the debt, are assets and liabilities matched, and is any mismatch hedged?
- What policy responses remain available, and which are constrained?

**About which cycle**

- Does the current evidence look like an ordinary short-cycle contraction, or something with long-cycle characteristics?
- What would distinguish the two, and is that evidence observable now?
- Do the credit indicators agree or conflict with the growth, inflation and policy indicators?

**About portfolio vulnerability**

- Which holdings depend on continued credit availability?
- Which holdings are exposed to entities with rising debt service?
- Under a deflationary adjustment, which holdings would suffer most?
- Under an inflationary adjustment, which holdings would suffer most?
- Does this portfolio implicitly require one of those two paths rather than the other?
- In a credit stress episode where correlations converge, what would the portfolio's effective exposure look like?

**About the investor**

- What leverage does the investor personally carry, on what terms, and with what reset schedule?
- Are there scenarios in which the investor would be forced to sell assets at a bad time?
- Is liquidity sufficient to avoid forced selling under a plausible stress path?

**About restraint**

- Is anything being proposed a timing bet on a debt event?
- If the adjustment does not occur for many years, what is the cost of positioning for it now?
- Is the right response here simply to verify robustness and change nothing?

**The governing question**

- If this debt-cycle assessment is wrong — in direction, in timing, or in the form of adjustment — is the strategic portfolio still robust?

---

## 9. Structured Knowledge Summary

**Principle:**
Credit expansion and contraction amplify economic cycles and accumulate over long periods into structural fragility; understanding this reveals portfolio vulnerability but does not enable prediction.

**Objective:**
Enable EducosysDalio to assess how credit conditions and debt burdens create portfolio vulnerabilities, and to evaluate robustness against multiple adjustment paths without adopting a house view on which will occur.

**Relevant Inputs:**
Credit growth and lending standards; debt-to-income and debt-to-output ratios by sector; debt service ratios; leverage measures; credit spreads; default and delinquency data; refinancing maturity profiles; policy rate levels and remaining policy space; currency denomination of debt, distinguishing sovereign issuer status from private-sector currency matching; the investor's personal balance sheet and leverage.

**Relevant Outputs:**
Credit condition assessment with direction and rate of change; leverage concentration map; identification of credit-dependent holdings; deflationary-path and inflationary-path vulnerability analysis; liquidity adequacy assessment; forced-selling scenario check; explicit statement that fragility carries no timing implication.

**Risks Addressed:**
Hidden credit dependence; correlation convergence during credit stress; forced selling; portfolios implicitly dependent on one adjustment path; debt service shock; refinancing risk; unrecognised personal leverage interacting with portfolio risk.

**Agent Behaviours:**
Use the framework diagnostically rather than predictively; refuse to assert thresholds or timing; represent both deflationary and inflationary adjustment paths as plausible; integrate credit evidence with other macro evidence rather than subordinating it; include the household balance sheet; acknowledge the opportunity cost of defensive positioning; note convergence with independent frameworks; bias toward robustness verification over repositioning.

**Deterministic Calculations Required:**
Debt-to-income and debt-to-output ratios by sector; debt service ratios; credit growth rates and rates of change; leverage measures; credit spread levels and changes; refinancing wall profiles; portfolio exposure to credit-sensitive holdings; scenario impact calculations for defined adjustment paths.

**Configurable Parameters:**
Sectors, geographies and series included in credit monitoring; minimum liquidity reserve relative to obligations; definition of credit-sensitive holdings; stress scenario specifications for deflationary and inflationary adjustment paths. *No values are set in this file.*

**Related Knowledge Files:**
`investment_philosophy.md`, `economic_regimes.md`, `risk_balancing.md`, `diversification.md`, `asset_roles.md`, `all_weather.md`.
