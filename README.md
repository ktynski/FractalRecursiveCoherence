# FIRM: Foundational Implementation of Recursive Meaning

Build and explore the FIRM UI in minutes. This README gives a clean on‑ramp; deeper theory lives in `EsotericGuidance/` and `FIRM-Core/FIRM_theory/`.

— Live demo: `https://fractal-recursive-coherence.vercel.app`

## Theory in brief
- Substrate: a ZX‑calculus graph evolves by rewrite rules; we expose structure via simple, explainable metrics.
- Ω signature: a canonical fingerprint (cycle set + phase histogram) derived from a graph snapshot.
- Resonance Res(S,Ω): similarity between the live system S and Ω using Jaccard(cycles) × Cosine(phase histograms).
- Steering: Res(S,Ω) modulates rewrite eligibility/weights; Grace (𝒢) emergence probability is tied to Res.
- Coherence C(G): a gauge‑invariant graph functional (uses phase differences only); rises with structured cycles and phase harmony.
- Field view: the graph maps to a Clifford multivector field (Cl(1,3)) for intuitive visualization (scalar/vector/bivector/… summaries).
- Falsifiability: tests assert Res↔C(G) coupling, gauge invariance, thermodynamic arrow, and evolution liveness.

**Critical experiments status**: 3/5 profound phenomena detected (thermodynamic arrow, gauge symmetry, Res-C coupling). See `UPDATED_CRITICAL_RESULTS.md`.

## For hard skeptics (quick checks)
- Reproducibility: run locally (below). Metrics should update every frame; nodes/edges grow.
- Resonance claim: enable Ω controls; verify Res(S,Ω) tracks C(G) trend over short runs.
- Independence from audio: visuals render before audio; one click resumes audio.
- Tests: `pytest -q` and `await window.runTheoryValidation()` should both pass.
- Code traceability: see `FIRM-Core/FIRM_ui/zx_objectg_engine.js` and `FIRM-Core/FIRM_ui/FIRM_dsl/resonance.js` for exactly how steering and metrics are computed.

## Quick Start

Local UI (no build):
```bash
cd FIRM-Core/FIRM_ui
python3 -m http.server 8000
# Open http://127.0.0.1:8000/
```

Run tests:
```bash
cd FIRM-Core
pip install pytest
pytest -q
```

## What you’ll see
- Real‑time WebGL rendering with view selector (Clifford, ZX, etc.)
- Metrics panel (open via “📊 Show Metrics”)
- Resonance metric Res(S,Ω) and Ω controls when enabled
- Audio needs one click (“Enable Audio”) due to browser policy

## Project layout
```
FIRM-Core/
  FIRM_ui/         # Static UI (index.html + JS modules)
  FIRM_dsl/        # Python DSL (theory primitives)
  FIRM_zx/         # ZX evolution logic
  FIRM_clifford/   # Clifford mapping
  tests/           # Python + browser validations
EsotericGuidance/  # Theory docs (start with Executive_Summary.md)
```

## Deploy (Vercel)
- Push to GitHub; Vercel auto‑deploys.
- We include Web Analytics and Speed Insights scripts.
- Config: see `vercel.json` (serves from `FIRM-Core/FIRM_ui/`).

## Troubleshooting (quick)
- Blank screen: hard refresh, then toggle view to “ZX Graph” and back.
- Audio stuck “initializing”: click “Enable Audio” once; rendering continues either way.
- Metrics missing: use “📊 Show Metrics”.
- Cache: Vercel uses cache‑busting query strings on scripts; still stale? Shift‑Reload.

## Learn more
- Start: `EsotericGuidance/Executive_Summary.md`
- Skeptic's intro: `SKEPTICS_GUIDE.md`
- Claims & limits: `SCIENTIFIC_POSITIONING.md`
- **Critical experiments**: `UPDATED_CRITICAL_RESULTS.md` (3/5 phenomena detected)
- Gauge fix: `GAUGE_INVARIANCE_FIX.md` (37.5% → 0.5% violation)
- ZX + resonance: `FIRM-Core/FIRM_ui/zx_objectg_engine.js`, `FIRM-Core/FIRM_ui/FIRM_dsl/resonance.js`
- Python DSL: `FIRM-Core/FIRM_dsl/`
- Tests: `FIRM-Core/tests/`

License: Apache‑2.0 (see `FIRM-Core/LICENSE`)
