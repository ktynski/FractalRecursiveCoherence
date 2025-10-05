# Critical Experiments Guide

This document explains the tests designed to determine if FIRM exhibits profound emergent phenomena that would distinguish it from a "toy model" and suggest it could be a candidate theory of reality.

## Overview

We've implemented 5 critical experiments and 5 emergence detection tests. Each is designed to be:
- **Falsifiable**: Clear pass/fail criteria
- **Reproducible**: Run locally with deterministic seeds
- **Interpretable**: Results map to known physics concepts

## The Central Question

**Could FIRM be what reality actually is?**

To answer this, we need to see if the graph dynamics spontaneously produce phenomena that match fundamental physics, WITHOUT hand-tuning parameters to fit observations.

---

## Critical Experiments

### 1. Phase Transitions (Test for Spontaneous Organization)

**File**: `FIRM-Core/tests/test_critical_experiments.py::TestPhaseTransitions`

**What it tests**:
- Does C(G) exhibit plateaus (distinct phases)?
- Does Res(S,Ω) vs C(G) show hysteresis (path-dependence)?

**Why it matters**:
- Real physics has phase transitions (ice→water→steam)
- If FIRM spontaneously organizes into vacuum→dark→ordinary matter phases, that's profound

**How to run**:
```bash
cd FIRM-Core
pytest tests/test_critical_experiments.py::TestPhaseTransitions -v -s
```

**What to look for**:
- Low-variance windows in C(G) time series (plateaus)
- Different Res values for same C(G) depending on history (hysteresis)

**Interpretation**:
- **Profound**: Multiple distinct plateaus with sharp transitions
- **Interesting**: Some plateaus, gradual transitions
- **Toy model**: Smooth monotonic increase, no structure

---

### 2. Dimensionless Ratios (Test for Physical Constants)

**File**: `FIRM-Core/tests/test_critical_experiments.py::TestDimensionlessRatios`

**What it tests**:
- Do cycle length ratios converge to constants?
- Does Grace/rewrite ratio match φ or other fundamental constants?

**Why it matters**:
- Physical constants (α ≈ 1/137, mass ratios) are dimensionless
- If graph topology produces these ratios, FIRM could encode physics

**How to run**:
```bash
cd FIRM-Core
pytest tests/test_critical_experiments.py::TestDimensionlessRatios -v -s
```

**What to look for**:
- (Longest cycle) / (Mean cycle) converging to a value
- Ratios matching known constants (φ, α, π, e, etc.)

**Interpretation**:
- **Revolutionary**: Ratio matches α = 1/137.036 to 3+ decimal places
- **Profound**: Ratio matches φ, π, or e consistently
- **Interesting**: Ratio converges but doesn't match known constants
- **Toy model**: Ratio varies randomly

---

### 3. Lorentz Invariance (Test for Relativistic Structure)

**File**: `FIRM-Core/tests/test_critical_experiments.py::TestLorentzInvariance`

**What it tests**:
- Is C(G) invariant under "boost" (phase rescaling by γ)?
- Does graph structure preserve Lorentz symmetry?

**Why it matters**:
- Spacetime has Lorentz symmetry (special relativity)
- If graph rewrites preserve this, FIRM could be spacetime substrate

**How to run**:
```bash
cd FIRM-Core
pytest tests/test_critical_experiments.py::TestLorentzInvariance -v -s
```

**What to look for**:
- Relative change in C(G) after boost should be ≈ 0

**Interpretation**:
- **Revolutionary**: C(G) invariant to < 1% under boosts
- **Profound**: C(G) approximately invariant (< 10% change)
- **Toy model**: C(G) changes significantly (> 20%)

---

### 4. Quantum Interference (Test for Path Integral Behavior)

**File**: `FIRM-Core/tests/test_critical_experiments.py::TestQuantumInterference`

**What it tests**:
- Do two paths A→B interfere based on phase differences?
- Does interference probability match quantum mechanics?

**Why it matters**:
- Quantum mechanics has path interference (double-slit experiment)
- If graph paths interfere like quantum amplitudes, FIRM could be QM substrate

**How to run**:
```bash
cd FIRM-Core
pytest tests/test_critical_experiments.py::TestQuantumInterference -v -s
```

**What to look for**:
- Interference probability ≠ 2.0 (classical expectation)
- Probability in [0, 4] range (quantum range)

**Interpretation**:
- **Revolutionary**: Interference matches Born rule predictions
- **Profound**: Clear interference pattern (probability ≠ 2)
- **Toy model**: No interference (probability ≈ 2)

---

### 5. Gauge Symmetry (Test for U(1) Invariance)

**File**: `FIRM-Core/tests/test_critical_experiments.py::TestGaugeSymmetry`

**What it tests**:
- Is C(G) invariant under global phase rotation?
- Does coherence depend on phase differences (not absolute phases)?

**Why it matters**:
- Electromagnetism has U(1) gauge symmetry
- If graph has this symmetry, FIRM could encode gauge theories

**How to run**:
```bash
cd FIRM-Core
pytest tests/test_critical_experiments.py::TestGaugeSymmetry -v -s
```

**What to look for**:
- Relative change in C(G) after rotation should be ≈ 0

**Interpretation**:
- **Revolutionary**: C(G) exactly invariant under U(1)
- **Profound**: C(G) approximately invariant (< 5% change)
- **Toy model**: C(G) changes significantly

---

## Emergence Detection Tests

### 1. Self-Organized Criticality

**File**: `FIRM-Core/FIRM_dsl/emergence_detection.py::detect_self_organized_criticality`

**What it detects**:
- Power-law distribution of event sizes: P(s) ~ s^(-α)
- Avalanches and scale-free behavior

**Why it matters**:
- Real systems at criticality (earthquakes, brain activity) show power laws
- SOC is a hallmark of complex systems at edge of chaos

**Expected signature**:
- α ∈ [1.5, 3.0] with R² > 0.8

---

### 2. Holographic Behavior

**File**: `FIRM-Core/FIRM_dsl/emergence_detection.py::detect_holographic_behavior`

**What it detects**:
- Boundary entropy ~ sqrt(boundary nodes) (area law)
- Boundary information encodes bulk

**Why it matters**:
- Holographic principle (AdS/CFT) is central to quantum gravity
- If FIRM is holographic, it could be a quantum gravity substrate

**Expected signature**:
- Entropy ratio (boundary/bulk) ∈ [0.5, 2.0]
- Area scaling ratio > 0.5

---

### 3. Thermodynamic Arrow of Time

**File**: `FIRM-Core/FIRM_dsl/emergence_detection.py::detect_thermodynamic_arrow`

**What it detects**:
- C(G) increases monotonically (like entropy)
- Time asymmetry without external input

**Why it matters**:
- Second law of thermodynamics defines arrow of time
- If FIRM has intrinsic arrow, time emerges from graph dynamics

**Expected signature**:
- Monotonic fraction > 0.7 (C(G) increases 70%+ of time)
- Positive mean slope

---

### 4. Emergent Locality

**File**: `FIRM-Core/FIRM_dsl/emergence_detection.py::detect_emergent_locality`

**What it detects**:
- Nearby nodes correlated, distant nodes uncorrelated
- Finite "speed of light" (information propagation rate)

**Why it matters**:
- Locality is fundamental to relativity and QFT
- If FIRM develops locality, it could have speed-of-light analogue

**Expected signature**:
- Locality ratio (near/far correlation) > 2.0

---

### 5. Vacuum Energy

**File**: `FIRM-Core/FIRM_dsl/emergence_detection.py::detect_vacuum_energy`

**What it detects**:
- Non-zero baseline C(G) in minimal graph
- Residual coherence drives expansion

**Why it matters**:
- Dark energy / cosmological constant is vacuum energy
- If FIRM has non-zero vacuum coherence, it could explain dark energy

**Expected signature**:
- Vacuum coherence > 0.01

---

## Long-Run Evolution Script

**File**: `FIRM-Core/scripts/long_run_evolution.py`

**Purpose**: Run extended simulation (5000+ steps) to collect data for all tests

**Usage**:
```bash
cd FIRM-Core
python scripts/long_run_evolution.py --steps 5000 --checkpoint 100 --output evolution_data.json
```

**What it does**:
1. Initializes graph with φ-modulated phases
2. Evolves for N steps with resonance-guided selection
3. Logs C(G), Res(S,Ω), event sizes, node/edge counts
4. Runs emergence battery every checkpoint
5. Saves all data to JSON for analysis

**Output**:
- `evolution_data.json`: Complete time series
- Console: Real-time emergence assessment

---

## Interpretation Guide

### Scoring System

Each test returns a verdict:
- **Revolutionary**: 4-5 profound phenomena detected
- **Highly Interesting**: 2-3 profound phenomena detected
- **Promising**: 1 profound phenomenon detected
- **Toy Model**: 0 profound phenomena detected

### What Each Level Means

**Revolutionary (4-5/5)**:
- FIRM exhibits multiple physics-like emergent behaviors
- Strong candidate for "what reality actually is"
- **Next step**: Make quantitative predictions, test experimentally

**Highly Interesting (2-3/5)**:
- FIRM shows some profound emergence
- Could be a useful model of reality, may not be reality itself
- **Next step**: Investigate why some tests fail, refine model

**Promising (1/5)**:
- FIRM has one interesting emergent property
- Useful computational framework, unlikely to be fundamental
- **Next step**: Explore what makes that one property emerge

**Toy Model (0/5)**:
- FIRM is a well-implemented simulator
- No profound emergence detected
- **Next step**: Accept it as a useful tool, not a theory of reality

---

## How to Use This Suite

### Quick Check (5 minutes)
```bash
cd FIRM-Core
pytest tests/test_critical_experiments.py -v -s
```

### Full Analysis (30-60 minutes)
```bash
cd FIRM-Core
python scripts/long_run_evolution.py --steps 5000
```

### Deep Dive (hours to days)
1. Run long evolution with different seeds
2. Vary initial conditions (node count, topology)
3. Test parameter sensitivity
4. Look for convergence across runs

---

## Current Status

**As of implementation**: Tests are in place, data collection ready.

**Expected first results**: Run `long_run_evolution.py` to see initial assessment.

**What we're looking for**:
- If we see 3+ profound phenomena → publish immediately
- If we see 1-2 → investigate further, refine tests
- If we see 0 → FIRM is a good simulator, not a theory of reality

---

## Next Steps After Results

### If Revolutionary:
1. Write paper: "Emergent Physics from Graph Dynamics"
2. Make falsifiable predictions (new particle masses, coupling constants)
3. Submit to arXiv, seek experimental collaboration

### If Highly Interesting:
1. Identify which phenomena are robust, which are fragile
2. Refine model to strengthen emergent behaviors
3. Compare to other discrete approaches (causal sets, spin networks)

### If Promising or Toy Model:
1. Document what works, what doesn't
2. Use as computational tool for exploring structure formation
3. Be honest about limitations in papers/presentations

---

## Falsification Criteria

**FIRM is falsified as a theory of reality if**:
1. No profound phenomena emerge after 10K+ steps
2. Dimensionless ratios don't converge
3. Lorentz invariance is violated by > 50%
4. No quantum interference detected
5. No gauge symmetry present

**FIRM is supported as a candidate theory if**:
1. 3+ profound phenomena emerge consistently
2. Dimensionless ratios match known constants
3. Lorentz invariance holds to < 10%
4. Quantum interference matches Born rule
5. U(1) gauge symmetry present

---

## Contact & Collaboration

If you run these tests and find revolutionary results, please:
1. Re-run with different seeds to confirm
2. Document your setup (OS, Python version, random seed)
3. Share `evolution_data.json` for independent verification
4. Consider co-authoring a paper if results are profound

This is open science. If FIRM is reality, we'll know together.
