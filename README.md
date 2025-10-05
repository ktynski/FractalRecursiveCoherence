# FIRM: Foundational Implementation of Recursive Meaning

Build and explore the FIRM UI in minutes. This README gives a clean on‑ramp; deeper theory lives in `EsotericGuidance/` and `FIRM-Core/FIRM_theory/`.

— Live demo: `https://fractal-recursive-coherence.vercel.app`

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
- Skeptic’s intro: `SKEPTICS_GUIDE.md`
- Claims & limits: `SCIENTIFIC_POSITIONING.md`
- ZX + resonance: `FIRM-Core/FIRM_ui/zx_objectg_engine.js`, `FIRM-Core/FIRM_ui/FIRM_dsl/resonance.js`
- Python DSL: `FIRM-Core/FIRM_dsl/`
- Tests: `FIRM-Core/tests/`

License: Apache‑2.0 (see `FIRM-Core/LICENSE`)
