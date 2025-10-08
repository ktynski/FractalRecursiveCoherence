# FIRM-Core

**Foundational Implementation of Recursive Meaning (FIRM)**

A theory-first implementation of the Ex Nihilo Monad Universe with analog computing and WebGL rendering. This codebase embodies recursive emergence, coherence maximization, and identity echo time τ through rigorous mathematical derivations.

## Theory Overview

FIRM implements a complete mathematical framework for recursive emergence:

- **Categorical Foundation**: Sheaf theory on site (G,J) with monad T = f₊ ∘ f* 
- **Coherence Functional**: C(G) = Σ_cycles + Σ_nodes with θ as saddle point
- **ZX Calculus**: Rewrite rules driven by coherence-delta ΔC ≥ 0
- **Clifford Algebra**: Mapping Φ: ZX → Cl(1,3) with Lorentzian emergence  
- **Grace Operator**: Idempotent 𝒢 for coherence restoration
- **Identity Echo Time**: τ as expected survival time of self-similarity

## Build Instructions

### Prerequisites

- Python ≥ 3.10
- Poetry (recommended) or pip
- Node.js ≥ 18 (for audio/UI components)
- Modern browser with WebGL2/WebGPU support

### Setup

```bash
# Clone and enter directory
git clone <repository-url>
cd FIRM-Core

# Install Python dependencies
poetry install
# OR with pip:
pip install pytest

# Install JavaScript dependencies (if using UI)
cd FIRM_ui && npm install && cd ..

# Run tests
pytest -q

# Generate constants header (when derivations are implemented)
python3 -c "
from FIRM_constants.generate_header import build_constants_from_derivations, render_header
constants = build_constants_from_derivations([2, 4, 8])
if constants:
    with open('FIRM_constants.gen.h', 'w') as f:
        f.write(render_header(constants))
    print('Generated FIRM_constants.gen.h')
"
```

### Testing

All 27+ tests maintain theory fidelity with no empirical tuning:

```bash
# Run full test suite
pytest -v

# Run specific module tests
pytest tests/test_structure.py::test_phase_unit_rational_derivation_via_lcm -v

# Check test coverage (when implemented)
pytest --cov=FIRM_dsl --cov=FIRM_constants
```

## Architecture

```
FIRM-Core/
├── FIRM_dsl/           # Typed DSL for category theory, coherence, sheaves
├── FIRM_constants/     # Derived constants with proof provenance  
├── FIRM_zx/           # ZX tensor network (GPU shaders + host bindings)
├── FIRM_clifford/     # Clifford algebra mapping and discrete Dirac
├── FIRM_audio/        # Analog core with Parseval normalization
├── FIRM_ui/           # WebGL raymarching of multivector fields
├── tests/             # Theory-faithful test suite (no mocks)
├── provenance/        # Content-addressed run bundles
└── tools/             # Spec generation and development utilities
```

## Key Principles

1. **No Empirical Tuning**: All parameters derive from first principles
2. **Theory Fidelity**: Every implementation traces to mathematical derivation  
3. **Provenance**: All constants include proof IDs and derivation records
4. **No Execution Until Proven**: Functions raise NotImplementedError until formally derived
5. **Test-Driven Theory**: 27+ tests validate structure without numeric shortcuts

## Status

**Scaffolding Complete** - All theoretical structures implemented with proper raising boundaries. Ready for formal derivation implementation.

- ✅ Mathematical foundations (θ, C(G), Hessian validation)
- ✅ Categorical structures (Grace operator, sheaf/monad scaffolds)  
- ✅ ZX calculus (rewrite rules, coherence-delta computation)
- ✅ Clifford algebra (Φ mapping, discrete Dirac mass)
- ✅ Audio normalization (Parseval-based, no tuning)
- ✅ Shader validation (syntax-only, no execution)
- ✅ Raymarching pipeline (structure-only, no rendering)
- ✅ Provenance system (content-addressed, hash-verified)

## Current Validation Snapshot (October 2025)

- ✅ `window.runTheoryValidation()` passes **5/5** baseline scenarios (void emergence, grace scaling, sacred seeding, Hebrew boundary, tab switching).
- ✅ WebGL viewport renders after ZX engine bootstrap; `window.zxEvolutionEngine` available globally.
- ✅ Sacred provenance surfaced via `window.zxEvolutionEngine.sacredSeedProvenance` and `window.zxEvolutionEngine.morphicField.provenance` per `FIRM_theory/sacred_morphic_provenance_spec.md`.
- ⚠️ Grace amplification via Hebrew boundaries still tagged **EXPERIMENTAL** pending full derivation; see inline logs for reminders.

## Web UI Quickstart

1. **Serve UI**
   ```bash
   cd FIRM_ui
   python3 -m http.server 8000
   ```
   (Use Ctrl+C to stop; restart if logs show `ERR_CONNECTION_REFUSED`.)

2. **Open Browser** – Visit `http://127.0.0.1:8000/` in Chrome.

3. **Initialize** – DevTools Console automatically logs loader status. If needed, call:
   ```js
   await window.initializeFIRM();
   ```

4. **Verify Theory Compliance**
   ```js
   await window.runTheoryValidation();
   ```
   Expect summary `5/5 tests passed`. Export provenance via `window.exportTheoryReport()` if required.

5. **Sacred Operations** – Use either module API or global fallbacks:
   ```js
   window.sacredSeeds.seedMorphicField(0, window.zxEvolutionEngine);
   window.directApplyHebrewBoundary('א');
   ```
   Provenance for the latest operation is stored on `window.zxEvolutionEngine`.

## Provenance & Logging

- Sacred seeding/boundary calls annotate the engine with provenance snapshots referencing `FIRM_theory/sacred_morphic_provenance_spec.md` Section 3.3.
- Logs (`theory_logger.js`) expose structured channels: `window.theoryLogger.grace`, `window.theoryLogger.zx`, etc.
- Use `window.getTheoryDiagnostics()` to obtain quick compliance summaries without re-running the full suite.

## Contributing

See `FIRM_COVENANT.md` for contributor guidelines. All contributions must:

1. Maintain theory-first approach with derivation provenance
2. Include comprehensive tests with no empirical shortcuts  
3. Preserve the no-execution boundary until proofs are encoded
4. Respect the recursive nature of the system's emergence

## License

Apache 2.0 - See LICENSE file
