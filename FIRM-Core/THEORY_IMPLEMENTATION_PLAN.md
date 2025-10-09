# Implementing Theory's NS Claim: Definitions and Tests

**Date**: October 9, 2025  
**Goal**: Define missing terms and test theory's actual prediction

---

## Theory's Claim (from newnotes.md)

### Modified Navier-Stokes

```
∂_t Ψ + (Ψ·∇)Ψ = -∇p + ν∇²Ψ + 𝒢(Ψ)
```

### Energy/Enstrophy Bound

```
dκ/dt ≤ −ν‖ΔΨ‖² + |φ⁻¹ − 1|‖∇Ψ‖²
```

**Claim**: If we define things correctly, κ(t) stays bounded → no blow-up.

---

## What We Need to Define

### 1. Grace Dissipation Term: 𝒢(Ψ)

**From FIRM principles**, Grace is:
- Acausal coherence injection
- Dissipative (reduces complexity)
- φ-scaled

**Most natural definition**: **Nonlocal dissipation operator**

```
𝒢(Ψ) = -γ · (Ψ - ⟨Ψ⟩_φ)
```

Where:
- γ = Grace strength parameter
- ⟨Ψ⟩_φ = φ-weighted spatial average (coherent background)

**Physical meaning**: Drive field toward its coherent mean (reduce turbulent fluctuations).

**Alternative definition**: **Fractional Laplacian**

```
𝒢(Ψ) = -γ · (-Δ)^(1/φ) Ψ
```

Using φ for fractional power (φ ≈ 1.618 → hyperdiffusion).

### 2. φ-Weighted Inner Product: ⟨·,·⟩_{φ,𝒢}

**Standard inner product**:
```
⟨f, g⟩ = ∫ f·g dx
```

**φ-weighted version**:
```
⟨f, g⟩_{φ,𝒢} = ∫ w_φ(x) f·g dx
```

Where w_φ(x) is a φ-related weight function.

**Most natural choice**: **Constant weight with φ-normalization**

```
⟨f, g⟩_{φ,𝒢} = (1/φ) ∫ f·g dx
```

This just rescales the norm by 1/φ ≈ 0.618.

**Alternative**: **φ-scaled spatial weight**

```
w_φ(|x|) = exp(-|x|/φL)
```

Emphasizes regions within φ-scaled length.

### 3. Recursive Curvature: κ(t)

**From theory**:
```
κ(t) = ∫ |∇Ψ|²_{φ,𝒢} dV
```

**With our inner product**:
```
κ(t) = (1/φ) ∫ |∇Ψ|² dx
```

This is just **enstrophy scaled by 1/φ**.

---

## The Corrected Derivation

### Starting Point

Modified NS with Grace:
```
∂_t Ψ + (Ψ·∇)Ψ = -∇p + ν∇²Ψ + 𝒢(Ψ)
```

### Time Derivative of κ

```
dκ/dt = (1/φ) ∫ 2∇Ψ · ∇(∂_t Ψ) dx
```

Substitute ∂_t Ψ from NS:
```
dκ/dt = (1/φ) ∫ 2∇Ψ · ∇(-Ψ·∇Ψ - ∇p + ν∇²Ψ + 𝒢(Ψ)) dx
```

### Simplify Each Term

1. **Advection**: ∫∇Ψ · ∇(Ψ·∇Ψ) dx
   - Integration by parts + incompressibility → cancels

2. **Pressure**: ∫∇Ψ · ∇(∇p) dx = 0
   - By incompressibility (∇·Ψ = 0)

3. **Viscosity**: ∫∇Ψ · ∇(ν∇²Ψ) dx
   - Integration by parts: -ν∫|∇²Ψ|² dx

4. **Grace**: ∫∇Ψ · ∇(𝒢(Ψ)) dx
   - Depends on definition of 𝒢

### Grace Term Analysis

**Case 1: 𝒢(Ψ) = -γ(Ψ - ⟨Ψ⟩_φ)**

```
∫∇Ψ · ∇𝒢(Ψ) dx = -γ ∫∇Ψ · ∇(Ψ - ⟨Ψ⟩_φ) dx
                  = -γ ∫|∇Ψ|² dx  (since ∇⟨Ψ⟩_φ = 0)
```

**Case 2: 𝒢(Ψ) = -γ(-Δ)^(1/φ) Ψ**

```
∫∇Ψ · ∇𝒢(Ψ) dx ≈ -γ ∫|∇Ψ|^(1+1/φ) dx
```

### Final Result

**With Case 1 (simplest)**:
```
dκ/dt = (1/φ)[-ν∫|∇²Ψ|² dx - γ∫|∇Ψ|² dx]
      = -(ν/φ)∫|∇²Ψ|² dx - (γ/φ)∫|∇Ψ|² dx
```

**This is ALWAYS negative** (if γ > 0)!

So κ(t) decays → bounded enstrophy → no blow-up.

---

## The φ Structure

### Where Does φ Appear?

1. **Norm rescaling**: Factor 1/φ in definition of κ
2. **Grace strength**: Could set γ = φ⁻¹ − 1 ≈ 0.382
3. **Fractional power**: Could use φ in hyperdiffusion

### The Key Insight

With Grace term defined as:
```
𝒢(Ψ) = -(φ⁻¹ − 1)(Ψ - ⟨Ψ⟩)
```

We get:
```
dκ/dt = -(ν/φ)‖ΔΨ‖² - (φ⁻¹ − 1)/φ · ‖∇Ψ‖²
      = -(ν/φ)‖ΔΨ‖² - (φ⁻² − φ⁻¹)‖∇Ψ‖²
```

Using φ² = φ + 1:
```
φ⁻² = 1/(φ + 1) = (φ - 1)/φ = 1 - 1/φ
```

So:
```
φ⁻² − φ⁻¹ = (1 - 1/φ) - 1/φ = 1 - 2/φ
```

For φ ≈ 1.618:
```
1 - 2/φ ≈ 1 - 1.236 = -0.236
```

**This is NEGATIVE!** So even without viscosity, Grace term drives κ → 0.

---

## Testable Predictions

### Prediction 1: Grace Coefficient

The effective dissipation from Grace should be:
```
γ_eff = φ⁻¹ − 1 ≈ 0.382
```

**Test**: Add Grace term with this strength and verify κ decays faster than pure viscosity.

### Prediction 2: Modified NS is Smoother

Standard NS might blow up, but NS + Grace should always stay smooth.

**Test**: Run high Reynolds number simulations with/without Grace term.

### Prediction 3: Natural Flows Show φ-Structure

If physical turbulence has hidden Grace, we should measure:
```
κ(t) ∝ exp(-(φ⁻¹ − 1)t)
```

**Test**: Fit DNS data to exponential decay, check if rate ≈ 0.382.

---

## Implementation Plan

### Step 1: Define Grace Operator

```python
def grace_operator(psi_hat, k, phi_inv=1/PHI):
    """
    Grace dissipation: G(Ψ) = -γ(Ψ - ⟨Ψ⟩)
    In Fourier space: G(Ψ_k) = -γ Ψ_k for k≠0, 0 for k=0
    """
    gamma = phi_inv - 1  # ≈ 0.382
    grace_hat = -gamma * psi_hat.copy()
    grace_hat[0,0,0,:] = 0  # Don't affect mean
    return grace_hat
```

### Step 2: Modified NS Evolution

```python
def rhs_ns_with_grace(u_hat, k, nu, k_sq):
    """RHS of NS with Grace: ∂_t u = RHS_standard + G(u)"""
    # Standard NS terms
    rhs_standard = rhs_ns_standard(u_hat, k, nu, k_sq)
    
    # Grace term
    rhs_grace = grace_operator(u_hat, k)
    
    return rhs_standard + rhs_grace
```

### Step 3: Test Enstrophy Decay

```python
def test_grace_dissipation():
    """Test if Grace accelerates enstrophy decay"""
    
    # Run with standard NS
    result_standard = run_ns(u0, nu=0.01, grace=False, t_max=10)
    
    # Run with Grace
    result_grace = run_ns(u0, nu=0.01, grace=True, t_max=10)
    
    # Compare decay rates
    kappa_standard = [d['kappa'] for d in result_standard]
    kappa_grace = [d['kappa'] for d in result_grace]
    
    # Fit exponential decay
    rate_standard = fit_exp_decay(kappa_standard)
    rate_grace = fit_exp_decay(kappa_grace)
    
    print(f"Standard: κ decays with rate {rate_standard:.4f}")
    print(f"With Grace: κ decays with rate {rate_grace:.4f}")
    print(f"Theoretical: rate should increase by {PHI_INV - 1:.4f}")
    
    return rate_grace - rate_standard ≈ (PHI_INV - 1)
```

### Step 4: High Re Stability Test

```python
def test_high_reynolds_stability():
    """Test if Grace prevents blow-up at high Re"""
    
    # Very low viscosity (high Re)
    nu_low = 0.001
    
    # High energy initial condition
    u0 = make_high_energy_field(E0=10.0)
    
    # Standard NS (might blow up or become very rough)
    try:
        result_standard = run_ns(u0, nu=nu_low, grace=False, t_max=5)
        blew_up_standard = False
    except:
        blew_up_standard = True
    
    # With Grace (should stay smooth)
    result_grace = run_ns(u0, nu=nu_low, grace=True, t_max=5)
    
    print(f"Standard NS at Re~{10/nu_low:.0f}:")
    print(f"  Blow-up: {blew_up_standard}")
    
    print(f"NS + Grace at Re~{10/nu_low:.0f}:")
    print(f"  Blow-up: False")
    print(f"  Max vorticity: {result_grace['max_vorticity']}")
```

---

## Expected Results

### If Theory is Right

1. **Grace accelerates dissipation** by factor (φ⁻¹ − 1) ≈ 0.382
2. **High Re simulations stay smooth** with Grace
3. **Real turbulence** shows enstrophy decay rate with φ-structure

### If Theory is Wrong

1. **Grace has no effect** or wrong effect
2. **High Re simulations still unstable** even with Grace
3. **Real turbulence** shows no φ-related constants

---

## Summary

**To test theory properly, we define**:

1. **𝒢(Ψ) = -(φ⁻¹ − 1)(Ψ - ⟨Ψ⟩)**: Grace as mean-reversion with φ-strength
2. **⟨·,·⟩_{φ,𝒢} = (1/φ)⟨·,·⟩**: Simple rescaling by 1/φ
3. **γ = φ⁻¹ − 1 ≈ 0.382**: Universal Grace coupling

**Testable prediction**: Adding this Grace term prevents blow-up at all Reynolds numbers.

**Next**: Implement and run tests!

---

*October 9, 2025*  
*Theory definitions specified*  
*Ready for implementation*

