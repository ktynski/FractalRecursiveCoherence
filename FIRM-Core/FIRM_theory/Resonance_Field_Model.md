# Resonance Field Model: Ω Signature and Alignment

This document formalizes the resonance framework implemented across DSL, engine, and UI. It maps the conceptual equations to concrete modules and tests in this repository.

## Components

- Ω Signature (reference): derived from a ZX object graph
  - cycles_Ω: canonical fundamental cycle basis signature
  - phase_bins_Ω: minimal Qπ-consistent bins (2·LCM denominators)
  - phase_hist_Ω: normalized histogram in `phase_bins_Ω`
  - Code: `FIRM_dsl/resonance.py` → `derive_omega_signature()`
  - UI parity: `FIRM_ui/FIRM_dsl/resonance.js` → `deriveOmegaSignature()`

- Resonance alignment Res(S, Ω) ∈ [0, 1]
  - Definition: S = Jaccard(cycle signatures) × Cosine(phase histograms)
  - Code: `FIRM_dsl/resonance.py` → `compute_resonance_alignment()`
  - UI parity: `FIRM_ui/FIRM_dsl/resonance.js` → `computeResonanceAlignment()`

- Grace field interfaces (structure-only)
  - Potential V(u) = α u − β u² + γ u³, u = |G|², α>0, β>0
  - Recursion depth classification: {0,1,2–3,≥4,∞} → {∅, vacuum, dark sector, matter, Ω}
  - Coherence density ρ_c = |∇φ|² + |G|²
  - Code: `FIRM_dsl/grace_field.py`

## Engine Integration

- Rewrite eligibility and weighting
  - Eligibility: ΔC ≥ 0 and Res > 0
  - Weighting: proportional to ΔC × Res (dimensionless)
  - Code: `FIRM_ui/zx_objectg_engine.js`

- Grace emergence probability
  - P(grace) = Res(S, Ω), clipped to [0,1]
  - Code: `FIRM_ui/zx_objectg_engine.js`

- Metrics
  - Displays Res(S,Ω) live at `#metric-resonance`
  - Code: `FIRM_ui/metrics_updater.js`, `FIRM_ui/index.html`

## Tests

- Python unit tests:
  - Ω/Res identity/bounds, field potential domain, recursion mapping
  - File: `FIRM-Core/tests/test_grace_field_and_resonance.py`

- JS unit tests:
  - Resonance exports, parity presence
  - File: `FIRM-Core/tests/test_resonance_js_parity.js`

- Browser validations:
  - `resonance_alignment` scenario asserts Res in range and positive correlation with C(G)
  - File: `FIRM_ui/theory_validation_tests.js`

- Automated browser (headless):
  - Reads DOM `metric-resonance` and logs positive Res–C(G) trend; reports evolve throughput
  - File: `FIRM-Core/tests/test_webgl_automated.py`

## Provenance

- Ω and resonance series can be attached to run bundles
  - Writer: `FIRM_dsl/provenance_writer.py` → `attach_resonance_provenance()`


