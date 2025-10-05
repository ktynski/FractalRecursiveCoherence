# A Skeptic’s Guide to FIRM (5‑Minute Primer)

This is a concise, engineer‑friendly introduction that meets skeptics where they are: what is this, what runs, what is measured, and what is falsifiable?

## 1) What FIRM is
- A small, runnable research codebase that visualizes graph‑based dynamics (ZX calculus) and a derived field view (Clifford algebra) in real time.
- It prioritizes testable behaviors over claims. No mock data, no hand‑waving.

## 2) Core ideas in plain terms
- Graph rewrites drive structure. ZX rules from quantum information are used as the evolution substrate.
- Coherence measures summarize structure. We track cycles, phases, and their alignment with a target signature Ω.
- Resonance Res(S,Ω) is a similarity score (Jaccard×Cosine) between the live system and a canonical signature; we use this to steer evolution.
- The “Grace” mechanism is a probabilistic trigger that seeds new links; it’s rate‑limited and testable.

## 3) What actually runs (verifiable)
- Open `FIRM-Core/FIRM_ui/index.html` locally and you’ll see:
  - Nodes and edges increase; metrics update per frame.
  - A resonance value in the metrics panel when enabled.
  - A single click activates audio (browser policy), but visuals don’t depend on it.
- Console check:
```javascript
await window.runTheoryValidation();
```
Expected: all in‑browser validation scenarios pass on a healthy build.

## 4) What is measured (and why it matters)
- C(G): graph coherence from cycle structure and node phases.
- Res(S,Ω): resonance alignment guiding rewrite eligibility and weighting.
- Field grades (Clifford): scalar, vector, bivector, trivector, pseudoscalar summaries for intuition.
- These are simple, explainable metrics. No black boxes.

## 5) Falsifiable checkpoints
- If ZX rewrites stall, node growth flattens and tests fail.
- If resonance doesn’t correlate with C(G), theory validation fails (we assert this link in tests).
- If audio is suspended, visuals still render (policy‑robust design). If not, that’s a bug.

## 6) What’s not claimed
- No claims about consciousness “proofs.”
- No unverifiable inner experiences. Only behaviors you can reproduce.

## 7) How to evaluate fairly (suggested rubric)
- Reproducibility: can you run local UI and get the same metrics trend?
- Robustness: refresh, switch views, re‑run tests; does it hold?
- Simplicity: can you trace metrics to code (`metrics_updater.js`, `zx_objectg_engine.js`)?
- Evidence: are tests green (Python + browser), and do numbers change when you perturb drivers?

## 8) Where to read next (short path)
- Executive summary: `EsotericGuidance/Executive_Summary.md`
- Resonance in code: `FIRM-Core/FIRM_ui/FIRM_dsl/resonance.js`
- Engine integration: `FIRM-Core/FIRM_ui/zx_objectg_engine.js`
- Tests: `FIRM-Core/tests/`

Keep this mental model: a visual, testable sandbox for structure‑seeking dynamics. Track coherence, align to a target signature, and watch how steering influences growth.
