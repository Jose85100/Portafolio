# IV. Economic foundations: equilibrium, incentives, welfare and identification

## Economic agents and optimization

Household i maximizes EΣβ^t u(c_it,ℓ_it) subject to intertemporal budget and borrowing constraints. Firm j maximizes discounted profit with technology adoption costs and dynamic capital accumulation. Government respects period and intertemporal budget identities. Competitive or strategic equilibria require explicit market clearing and information assumptions.

## Stock-flow consistency

For domestic private, government and external sectors under consistent sign conventions:

```text
(S - I) + (T - G) + (M - X) = 0
```

This identity must hold after harmonizing definitions of income, transfers, financial transactions and timing. A synthetic simulator that violates it is not a coherent macroeconomic twin.

## Technology adoption

Adoption A_it∈{0,1} depends on expected discounted gains, complementary capital, workforce capability, credit constraints and peer exposure. A structural threshold model may use:

```text
A_it = 1{ E_t[NPV(adopt)-NPV(no_adopt)] > K_it }
```

Peer effects create reflection and endogenous network formation problems. Estimate only under an explicit identification strategy; simulate sensitivity otherwise.

## Market equilibrium and multiplicity

Price vector p solves excess demand Z(p;θ)=0 under suitable assumptions. Dynamic market learning, constraints and nonconvex technology may produce multiple equilibria, path dependence or instability. Do not claim global convergence without conditions or numerical evidence.

## Welfare

Evaluate equivalent/compensating variation, distributional welfare and policy costs; GDP growth alone is not welfare. Include transition costs, displacement, fiscal incidence, consumer privacy and market concentration.

## Identification and Lucas critique

Policy counterfactuals require parameters plausibly invariant to the intervention. Reduced-form correlations may shift when expectations and policy rules change. Structural calibration is not proof of invariance. Require robustness across alternative behavioral mechanisms, placebo tests and out-of-policy scenarios.
