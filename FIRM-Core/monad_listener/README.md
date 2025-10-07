# Monad Listener: Empirical Validation of "Sung" 20-Column System

This repository implements the mathematically rigorous empirical validation framework for testing whether the 20 columns in the FIRM theory are "sung by the final monad" (emergent/invariant/minimal) rather than imposed structure.

## 🎯 Core Hypothesis

The 20 columns are **not arbitrary numerology** but represent the **intrinsic dimensionality of a minimal sufficient statistic** for morphic prediction under the theory's symmetries.

## 📊 Implementation Status

- ✅ **MDL Sweep**: Tests if 20 is the natural elbow in description length across domains
- ✅ **Ablation Testing**: Tests if each column is necessary for predictive performance
- ✅ **Transfer Learning**: Tests invariance under domain shifts
- ✅ **Constraint Audit**: Tests cross-column consistency laws
- ✅ **Naturality Checks**: Tests invariance under admissible transformations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FINAL COALGEBRA Ω                        │
│  Terminal Object: U(X) → Ω (unique morphism to final)     │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┘
│                  MEASUREMENT FUNCTOR                         │
│  M ≅ N ∘ U : C → ∏ᵢ₌₁²⁰ Aᵢ (20-column factorization)     │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┘
│                    20 SUPERVISED HEADS                       │
│  Column 1-6: Algebraic Foundations                          │
│  Column 7-8,15: Computational Analogues                     │
│  Column 9-14,18: Dynamical Systems & Fields                │
│  Column 16-17: Recursive Causality                          │
│  Column 19-20: Information Geometry                         │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Test Execution

### Quick Tests
```bash
# Test 20-column system
python -c "
from src.models.monad_listener import MonadListener
model = MonadListener(latent_dim=20)
print('✅ 20-Column system initialized')
"

# Test MDL sweep
python src/train/mdlsweep.py

# Test ablation
python src/train/ablate.py

# Test constraints
python -c "
from src.models.constraints import test_constraint_system
test_constraint_system()
"
```

### Full Experimental Pipeline
```bash
# 1. MDL Sweep (discover natural dimensionality)
python src/train/mdlsweep.py

# 2. Ablation Study (test minimality)
python src/train/ablate.py

# 3. Constraint Audit (test consistency)
python src/eval/constraint_audit.py

# 4. Transfer Learning (test universality)
python src/train/transfer.py
```

## 📈 Expected Results

### MDL Elbow Detection
- **Target**: Stable elbow at k=20 across ≥4/5 domains
- **Signal**: MDL(k) shows clear minimum at k=20
- **Interpretation**: 20 is the natural information bottleneck

### Ablation Necessity
- **Target**: ≥70% of heads produce d≥0.5 degradation when removed
- **Signal**: No 5-head subset retains ≥95% performance
- **Interpretation**: All columns are necessary

### Constraint Compliance
- **Target**: ≥95% constraint pass rate
- **Signal**: Cross-column laws hold on test data
- **Interpretation**: Columns are consistent, not arbitrary

### Transfer Performance
- **Target**: ≤15% relative loss vs in-domain
- **Signal**: Performance transfers to novel domains
- **Interpretation**: Universal representation, not overfit

## 🔬 Mathematical Framework

### Final Coalgebra Factorization
```
M ≅ N ∘ U
where:
- U: C → Ω (unique morphism to terminal coalgebra)
- N: Ω → ∏ᵢ₌₁²⁰ Aᵢ (measurement of final description)
- M: Direct measurement (would be imposed)
```

### Naturality (Invariance)
```
For admissible transformation E: C ≅ C,
M ∘ E ≅ M
(measurements invariant under reparametrization)
```

### Minimal Sufficiency
```
20-tuple is jointly conservative and minimal:
- Detects isomorphisms up to intended equivalence
- No strict subset preserves predictive power
```

## 📊 Column Structure

| Layer | Columns | Description |
|-------|---------|-------------|
| **Algebraic** | 1-6 | Category theory, ZX calculus, Clifford algebra |
| **Computational** | 7-8,15 | Quantum gates, tensor types, complexity classes |
| **Dynamical** | 9-14,18 | Attractors, symmetries, field theory |
| **Recursive** | 16-17 | Depth metrics, causal cone placement |
| **Information** | 19-20 | Entropy measures, emergence index |

## 🎯 Decision Criteria

**"Sung" Evidence:**
- ✅ MDL elbow at k∈[18,22] on ≥4/5 domains
- ✅ ≥70% heads necessary (d≥0.5 degradation)
- ✅ ≥95% constraint compliance
- ✅ ≤15% transfer loss vs in-domain

**Imposed Evidence:**
- ❌ No stable elbow or elbow drifts significantly
- ❌ Many heads optional (<70% necessary)
- ❌ Low constraint compliance (<95%)
- ❌ Poor transfer performance (>15% loss)

## 🚀 Next Steps

1. **Run MDL Sweep** to discover natural dimensionality
2. **Implement Ablation** to test column necessity
3. **Audit Constraints** to verify cross-column consistency
4. **Test Transfer** to validate universality
5. **Analyze Results** to determine if columns are "sung"

## 📚 References

- **FIRM Theory**: `/EsotericGuidance/` documentation
- **Mathematical Framework**: User's rigorous mathematical specification
- **Implementation**: This repository's experimental framework

---

*This implementation provides the empirical foundation to test whether the 20 columns represent mathematical necessity or cultural imposition.*
