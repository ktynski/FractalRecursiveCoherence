# Scientific Positioning: Claims, Limits, and Falsifiability

This document states, plainly, what this project claims, what it does not claim, and how it can be falsified. It is designed to address reasonable skepticism and to avoid "AI slop."

## What this project IS
- A testable sandbox for structure‑seeking dynamics on ZX graphs with a derived Clifford‑field visualization.
- A resonance‑guided evolution engine: Res(S,Ω) steers rewrite eligibility/weights; Grace is a probabilistic source.
- A set of measurable observables (C(G), Res(S,Ω), grade summaries) exposed in a live UI and tests.

## What this project is NOT
- Not a claim of new fundamental physics or a replacement of established laws.
- Not a proof of consciousness; not metaphysical certitude.
- Not a product of LLM “conversation” alone; code and tests are primary artifacts.

## Core, checkable claims
1) Under default drivers, ZX rewrites produce sustained growth and increasing C(G).
2) When Ω steering is enabled, Res(S,Ω) correlates with C(G) and biases rewrite selection.
3) Visuals render independent of audio initialization; audio resumes with one user action.
4) Tests (Python + browser) pass on a healthy build without mocks or hidden shortcuts.

## Falsification routes (how we could be wrong)
- If Res(S,Ω) fails to correlate with C(G) across controlled perturbations → reject resonance steering claim.
- If growth/rewrites stall on fresh runs (sans errors) → reject sustained‑evolution claim.
- If UI depends on audio for rendering → reject policy‑robust design claim.
- If tests fail on a clean environment without modification → reject reproducibility claims.

## Evidence and provenance
- Code paths: `FIRM-Core/FIRM_ui/zx_objectg_engine.js`, `FIRM-Core/FIRM_ui/FIRM_dsl/resonance.js`.
- Metrics: `FIRM-Core/FIRM_ui/metrics_updater.js` (reads/writes DOM metrics).
- Tests: `FIRM-Core/tests/` (unit + Selenium; in‑browser scenarios).

## On AI and theory
- We do not assert that an LLM “derived” new laws.
- We use conventional, transparent metrics and simple similarity measures (Jaccard × Cosine).
- All claims are limited to behaviors in this sandbox and are evaluated by code‑level tests.

## How to evaluate fairly
- Reproduce locally (no build), run tests, toggle Ω mode, inspect metrics and logs.
- Perturb drivers and verify trends; review code mapping metrics to behavior.
- Check that claims above continue to hold across sessions (robustness).

Short version: this is a reproducible, instrumented simulator exploring resonance‑guided structure formation. It stands or falls on observable behaviors, not on vibes.
