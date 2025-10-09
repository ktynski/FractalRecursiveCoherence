# ROOT CAUSE ANALYSIS AND SYSTEMATIC RESOLUTION

**Date**: October 9, 2025  
**Purpose**: Identify fundamental issues, not symptoms. Resolve properly, not ad-hoc.  
**Status**: Comprehensive investigation initiated

---

## EXECUTIVE SUMMARY

The criticism identified **4 core issues**:
1. Muon formula appears numerological (coefficient 10 not derived)
2. 12N-4=248 appears asserted (DOF structure not proven)
3. NS Clifford inequality only "sketched" (critical step incomplete)
4. Yang-Mills coercivity asserted (equivalence to standard YM unproven)

**Our finding**: These are symptoms of **3 deeper root causes**:

### ROOT CAUSE A: Group Theory Calculations Incomplete
- **Issue**: SU(5) Clebsch-Gordan coefficients exist in code but not computed rigorously
- **Files**: `compute_su5_clebsch_gordan.py` has framework, returns `NotImplementedError`
- **Impact**: Mass formulas (muon, tau, quarks) are patterns, not derivations

### ROOT CAUSE B: E8 Decomposition Not Uniquely Proven
- **Issue**: "12 DOF per node" comes from octonions+spinors (8+4), but not derived from E8
- **Files**: `N21_DERIVATION_INVESTIGATION.md` explicitly states "ASSUMED, not proven"
- **Impact**: 12N-4=248 is dimensional analysis, not unique derivation

### ROOT CAUSE C: Full Nonlinear NS Testing Never Performed
- **Issue**: Tests used diffusion-only (∂_t u = ν∇²u), not full NS with vortex stretching
- **Files**: `THE_GAP_EXPLAINED.md` documents this failure
- **Impact**: φ-convergence unvalidated, Clifford inequality untested

---

## PART 1: MUON FORMULA - ROOT CAUSE ANALYSIS

### Current Status

**Formula**: $m_\mu / m_e = 10N - 3 = 207$

**Justification given**:
- "10 from SU(5) 10-representation"
- "-3 from U(1) charge quantization"
- "N=21 from topology"

**Reality check**:
```python
# From compute_su5_clebsch_gordan.py:113-163
def clebsch_gordan_5bar_5_5bar(self, i: int, j: int) -> float:
    """
    Compute CG coefficient for 5̄_i × 5 × 5̄_j → 1.
    ...
    Returns:
        CG coefficient (pure number)
    """
    if i == j:
        return 1.0 / np.sqrt(5)  # = 0.447
    else:
        return 0.0
```

**The gap**: This gives $1/\sqrt{5} \approx 0.447$, NOT the coefficient 10!

### ROOT CAUSE: Missing Representation-Dependent Factors

The CG coefficient $1/\sqrt{5}$ is just the **group theory overlap**. The full Yukawa coupling includes:

1. **CG coefficient**: $C_{ij} = \delta_{ij}/\sqrt{5}$ ✓ (computed)
2. **Wave function overlap**: $\langle \psi_\mu | \psi_e \rangle$ (topology-dependent) ❌ (not computed)
3. **VEV insertion**: $v/\sqrt{2} = 246/\sqrt{2}$ GeV ✓ (known)
4. **Running**: RG evolution from GUT to EW scale ❌ (not computed)

**The coefficient 10 should come from**: 
$$\text{Yukawa}_\mu = \frac{1}{\sqrt{5}} \times \text{(wave function overlap)} \times \text{(RG running)} = 10 \times \text{Yukawa}_e$$

**What we need to derive**:
- Wave function overlap from N=21 node positions
- RG running factors from $M_{\text{GUT}}$ to $M_Z$

### RESOLUTION PATH 1: Rigorous SU(5) Calculation

**Step 1.1**: Implement wave function overlap from node geometry
```python
def topology_wave_function_overlap(gen_i: int, gen_j: int, N: int = 21) -> float:
    """
    Compute overlap of fermion wave functions on Ring+Cross graph.
    
    For muon (gen 1) vs electron (gen 0):
    - Electron: nodes 0-6 (sector 1)
    - Muon: nodes 7-13 (sector 2)
    - Overlap: integral over graph edges
    
    Returns:
        Dimensionless overlap coefficient
    """
    # Node positions on ring
    theta_i = 2 * np.pi * gen_i * 7 / N  # 7 nodes per generation
    theta_j = 2 * np.pi * gen_j * 7 / N
    
    # Wave function is Gaussian on graph
    # Width determined by N
    sigma = 2 * np.pi / (3 * np.sqrt(N))  # 3 generations
    
    # Overlap integral
    delta_theta = abs(theta_i - theta_j)
    overlap = np.exp(-delta_theta**2 / (2 * sigma**2))
    
    # THIS IS THE DERIVATION WE NEED, NOT GUESSWORK
    # Must come from actual graph Laplacian eigenfunctions
    
    return overlap
```

**Step 1.2**: Implement RG running
```python
def rg_running_yukawa(y_GUT: float, m_GUT: float, m_EW: float) -> float:
    """
    Run Yukawa coupling from GUT to EW scale.
    
    Uses 1-loop beta function:
    dy/dt = y/(16π²) * [Tr(Y² gauge) - 6y²_top - ...]
    
    Returns:
        y(m_EW) / y(m_GUT) ratio
    """
    # This is standard SM RG, well-defined
    # Need to implement 2-loop for <1% precision
    pass
```

**Step 1.3**: Combine to derive coefficient
```python
def derive_muon_coefficient():
    # CG coefficient
    cg = 1.0 / np.sqrt(5)  # 0.447
    
    # Wave function overlap (to be derived)
    wf_overlap = topology_wave_function_overlap(1, 0, N=21)
    
    # RG running (standard calculation)
    rg_factor = rg_running_yukawa(y_GUT, M_GUT, M_Z)
    
    # Combined
    coeff = cg * wf_overlap * rg_factor
    
    # Verify: should equal ~10
    print(f"Derived coefficient: {coeff}")
    print(f"Target: 10")
    print(f"Match: {abs(coeff - 10) / 10 * 100:.1f}% error")
```

**Acceptance criteria**:
- [ ] Wave function overlap derived from graph Laplacian eigenfunctions
- [ ] RG running computed to 2-loop precision
- [ ] Combined coefficient within 5% of 10 (not fitted!)
- [ ] Works for tau (coefficient 14) and quarks without adjustment

---

## PART 2: 12N-4 FORMULA - ROOT CAUSE ANALYSIS

### Current Status

**Formula**: $\dim(E8) = 248 = 12N - 4$ with $N=21$

**Justification given**:
```
Each node: 8 (octonions) + 4 (spinors) = 12 DOF
Constraints: 1 (phase) + 3 (momentum) = 4
Result: 12×21 - 4 = 248
```

**From N21_DERIVATION_INVESTIGATION.md lines 88-99**:
> "**Problem**: This is ad-hoc. Why octonions? Why not quaternions (4D)?  
> **Deeper question**: Does E8 decompose naturally into 21 copies of something 12D?"

### ROOT CAUSE: No Unique E8 Decomposition Proven

The formula 12N-4=248 is **arithmetic**, not **derivation**. Many other decompositions exist:

| Formula | N | DOF | Constraints | Notes |
|---------|---|-----|-------------|-------|
| 12N - 4 = 248 | 21 | 12 | 4 | Our choice (octonions) |
| 10N + 48 = 248 | 20 | 10 | -48 | SU(5) 10-rep basis |
| 16N - 16 = 248 | 16.5 | 16 | 16 | SO(10) spinors (non-integer!) |
| 8N + 80 = 248 | 21 | 8 | -80 | Pure octonions |
| 31N - 403 = 248 | 21 | 31 | 403 | Arbitrary fit |

**All give N≈21, but for different reasons!**

### What Would Constitute a Derivation

**Option A: E8 Cartan Decomposition**

E8 has a Cartan decomposition into root spaces. If we can show:
1. E8 Cartan subalgebra naturally decomposes into 21 sectors
2. Each sector has exactly 12 generators
3. Constraints arise from Lie bracket relations

Then 12N-4 would be **derived**, not assumed.

**Option B: E8 Weight Lattice Projection**

E8 weight lattice in 8D contains 240 roots. If:
1. Roots organize into 21 equivalence classes (orbits under some subgroup)
2. Each class has 11-12 representatives
3. The 4 constraints come from Weyl group quotient

Then N=21 would be **unique**, not chosen.

**Option C: Variational Principle**

If we can prove:
1. Among all decompositions $pN + q = 248$
2. The action functional $S[N, p, q]$ is minimized
3. Minimum occurs at $(N, p, q) = (21, 12, -4)$

Then 12N-4 would be **inevitable**, not arbitrary.

### RESOLUTION PATH 2: Rigorous E8 Analysis

**Step 2.1**: E8 root system decomposition
```python
def decompose_e8_roots_into_sectors(n_sectors: int = 21) -> List[List]:
    """
    Decompose 240 E8 roots into n_sectors equivalence classes.
    
    Method:
    1. Load E8 root system from standard tables
    2. Define equivalence relation (e.g., Weyl orbit under rank-7 subalgebra)
    3. Partition into classes
    4. Verify: sum of class sizes = 240
    
    Returns:
        List of root vectors per sector
    """
    # E8 roots (from Lie algebra tables)
    e8_roots = load_e8_root_system()  # 240 vectors in 8D
    
    # Define equivalence: project onto 7D subspace, quantize
    projection_map = define_e8_to_rank7_projection()
    
    # Partition
    sectors = partition_by_equivalence(e8_roots, projection_map, n_sectors)
    
    # Verify
    assert len(sectors) == n_sectors
    assert sum(len(s) for s in sectors) == 240
    
    # Check if decomposition is natural (not forced)
    verify_natural_decomposition(sectors)
    
    return sectors
```

**Step 2.2**: Derive DOF per sector
```python
def derive_dof_per_sector(sectors: List) -> int:
    """
    From E8 root decomposition, derive DOF per sector.
    
    Each root generates a 1D Lie algebra element.
    Sectors group related roots.
    DOF = number of independent generators per sector.
    
    Returns:
        DOF per sector (should be ≈12)
    """
    # Count generators in first sector (by symmetry, all equal)
    sector_0_roots = sectors[0]
    
    # Dimension = rank of span of roots + Cartan contribution
    rank_span = np.linalg.matrix_rank(np.array(sector_0_roots))
    cartan_contrib = 8 / len(sectors)  # Share of Cartan subalgebra
    
    dof = rank_span + cartan_contrib
    
    print(f"Derived DOF per sector: {dof}")
    print(f"Target: 12")
    
    return dof
```

**Step 2.3**: Derive constraints
```python
def derive_e8_constraints(sectors: List) -> int:
    """
    Constraints arise from Lie bracket consistency.
    
    For E8: [H_i, E_α] = α_i E_α (Cartan-root relation)
    
    When decomposing into sectors, some relations become constraints.
    
    Returns:
        Number of independent constraints
    """
    n_sectors = len(sectors)
    
    # Cartan subalgebra (8D) must be shared across sectors
    # Each sector "sees" 8/n_sectors of Cartan → coupling
    # This creates n_sectors constraints... no wait, that's too many
    
    # Actually: constraints come from cross-sector Lie brackets
    # [E_α (sector i), E_β (sector j)] = ... (structure constants)
    
    # Count independent constraints
    # This is the HARD part - needs actual E8 representation theory
    
    return 4  # Placeholder - need real calculation
```

**Acceptance criteria**:
- [ ] E8 roots decompose naturally into 21 sectors (not forced partition)
- [ ] Each sector has 11-12 roots/generators (within ±1)
- [ ] Constraints arise from Lie bracket relations (not ad-hoc)
- [ ] Alternative N values (20, 22, 24) fail natural decomposition test
- [ ] Fibonaccni F(8)=21 emerges from φ-structure in E8 roots

---

## PART 3: NAVIER-STOKES - ROOT CAUSE ANALYSIS

### Current Status

**Claim**: Clifford cubic inequality proves global convergence  
**Reality**: Inequality fails numerical tests

**From THE_GAP_EXPLAINED.md**:
```
Test: Clifford Cubic Inequality | ∫T³ ≥ κ_φ·δ² | Ratio: -2.830 | ✗ FAIL
Test: φ-Convergence | R(t) → 0.382 | R(t) = 1.000 | ✗ FAIL
```

### ROOT CAUSE: Wrong Test Setup

**From THE_GAP_EXPLAINED.md lines 41-45**:
> "With pure diffusion (no nonlinear term), flows don't converge to φ-balance. They lose all strain and become pure rotation. This is **OPPOSITE** of what the theory predicts."

**The test used**:
```python
# WRONG TEST
∂_t u = ν∇²u  # Diffusion only
```

**Should have used**:
```python
# CORRECT TEST
∂_t u = -(u·∇)u - ∇p + ν∇²u  # Full nonlinear NS
∇·u = 0
```

**Why this matters**: The vortex stretching term $(u·\nabla)u$ is **essential** for φ-balance!

From NS_ACTUAL_PROBLEM.md:
> "For isotropic turbulence (no preferred direction):
> - By symmetry: Tr(S²) ≈ Tr(A²)
> - Therefore: **R ≈ 2/3 ≈ 0.667**
>
> To reach R = φ⁻² ≈ 0.382:
> - Need Tr(S²) > Tr(A²) (strain-dominated)
> - Requires Tr(S²)/Tr(A²) ≈ 3.24"

**The vortex stretching term creates strain!** Without it, pure diffusion only creates rotation.

### RESOLUTION PATH 3: Proper NS Testing

**We have the code**: `test_full_ns_convergence.py`, `test_grace_vs_devourer.py`

**Step 3.1**: Run full nonlinear NS
```python
# From test_full_ns_convergence.py:19-108
solver = PseudospectralNS(N=64, nu=0.001, L=2*np.pi)

# Initialize with random field
u0_hat = solver.random_field(energy=1.0, k_peak=4)

# Evolve with FULL nonlinear term
results = solver.run_simulation(
    u0_hat,
    t_max=100.0,  # Long time!
    dt=0.01,
    compute_R=True,  # Track R(t)
    verbose=True
)

# Check convergence
R_final = results['R'][-1]
phi_inv_sq = 1.618**(-2)  # 0.382

print(f"Final R: {R_final:.3f}")
print(f"Target φ⁻²: {phi_inv_sq:.3f}")
print(f"Converged: {abs(R_final - phi_inv_sq) < 0.05}")
```

**Step 3.2**: Vary initial conditions
```python
initial_conditions = [
    "TaylorGreen",  # Smooth vortex
    "RandomIsotropic",  # Turbulent
    "StrainDominated",  # R < 0.5
    "VorticityDominated",  # R > 0.8
]

for ic in initial_conditions:
    u0 = generate_initial_condition(ic)
    results = run_full_ns(u0, t_max=100)
    
    # Check if ALL converge to φ⁻²
    assert converged_to_phi(results['R'])
```

**Step 3.3**: Measure Clifford inequality on real NS data
```python
def test_clifford_inequality_on_ns_flow():
    """
    Test inequality using ACTUAL NS evolution, not toy models.
    """
    solver = PseudospectralNS(N=64, nu=0.001)
    u_hat = solver.random_field()
    
    for step in range(1000):
        u_hat = solver.step_rk4(u_hat, dt=0.01)
        
        # Compute T³ integral (triple tensor product)
        T_cubic = compute_triple_tensor_product(u_hat)
        
        # Compute δ² (distance from φ-balance)
        R = compute_vorticity_strain_ratio(u_hat)
        delta_sq = (R - PHI_INV_SQ)**2
        
        # Test inequality
        ratio = T_cubic / (KAPPA_PHI * delta_sq)
        
        print(f"Step {step}: T³/κδ² = {ratio:.3f} (should be ≥ 1)")
        
        if ratio < 1:
            print(f"INEQUALITY VIOLATED at step {step}")
            # But is this because:
            # A) Inequality is wrong (theory error)
            # B) Flow converged to φ-balance (δ→0, ratio→∞ or NaN)
            # C) Numerical error
            
            investigate_failure(u_hat, ratio, delta_sq)
```

**Acceptance criteria**:
- [ ] Full nonlinear NS solver runs stably for t=100+ eddy turnovers
- [ ] R(t) measured accurately (test with energy/enstrophy conservation)
- [ ] Multiple IC types tested (at least 5 different flows)
- [ ] φ-convergence observed for ≥80% of ICs, or alternative attractor identified
- [ ] Clifford inequality tested on converged flows (δ small), not arbitrary states
- [ ] If inequality still fails, identify WHERE (which term) and WHY

---

## PART 4: YANG-MILLS - ROOT CAUSE ANALYSIS

### Current Status

**Claim**: Grace operator has coercivity C > 1, implying mass gap  
**Question**: Does standard Yang-Mills satisfy Grace axioms?

**From FSCTF_COMPLETE_INTEGRATION_SUMMARY.md lines 245-249**:
> **What remains to prove:**  
> - ⚠️ Equivalence FSCTF ↔ standard Yang-Mills

### ROOT CAUSE: Equivalence Assumed, Not Proven

**What we proved**: Within FSCTF framework (which assumes Grace axioms), mass gap follows rigorously.

**What we didn't prove**: Standard Yang-Mills Hamiltonian satisfies Grace axioms.

**The gap**:
```
Standard YM:  H = ∫ d³x [½E² + ¼F²]
FSCTF-YM:     H_FSCTF = ∫ d³x [Grace-modified action]

Question: H ≡ H_FSCTF?
```

### RESOLUTION PATH 4: Prove or Disprove Equivalence

**Step 4.1**: Formulate precise equivalence criterion
```python
def test_ym_grace_equivalence():
    """
    Test if standard YM gauge-fixing satisfies Grace axioms.
    
    Standard YM uses gauge-fixing:
    - Coulomb gauge: ∇·A = 0
    - Axial gauge: A_3 = 0
    - Lorenz gauge: ∂_μ A^μ = 0
    
    Grace operator 𝒢 requires:
    - G1: Positivity
    - G2: Contraction (κ = φ⁻¹)
    - G3: Coherence core
    - G4: Self-adjoint
    
    Question: Does gauge-fixing operator act as Grace?
    """
    
    # Test on toy SU(2) gauge field
    gauge_field = generate_random_su2_field()
    
    # Apply Coulomb gauge projection
    coulomb_projected = apply_coulomb_gauge(gauge_field)
    
    # Measure contraction
    norm_before = field_norm(gauge_field)
    norm_after = field_norm(coulomb_projected)
    kappa_measured = norm_after / norm_before
    
    print(f"Contraction constant: {kappa_measured:.3f}")
    print(f"Target κ = φ⁻¹: {PHI_INV:.3f}")
    print(f"Match: {abs(kappa_measured - PHI_INV) < 0.1}")
    
    # Test other axioms...
```

**Step 4.2**: Lattice simulation measurement
```python
def measure_grace_constant_from_lattice_ym():
    """
    Use existing lattice QCD data to extract κ.
    
    If YM naturally has Grace structure, κ should emerge from data.
    """
    # Load lattice gauge configurations (public datasets exist)
    configs = load_lattice_configs("SU3_beta6.0_L32")
    
    kappas = []
    for config in configs:
        # Measure effective damping
        # From temporal correlation: ⟨A(t)A(0)⟩ ~ exp(-κt)
        kappa = fit_exponential_decay(config)
        kappas.append(kappa)
    
    kappa_mean = np.mean(kappas)
    kappa_std = np.std(kappas)
    
    print(f"Measured κ from lattice: {kappa_mean:.3f} ± {kappa_std:.3f}")
    print(f"Theory predicts κ = φ⁻¹: {PHI_INV:.3f}")
    
    # If match within error: Evidence FOR equivalence
    # If no match: Evidence AGAINST equivalence
```

**Step 4.3**: Derive mass gap from gauge-fixing
```python
def derive_mass_gap_from_standard_ym():
    """
    Attempt alternative derivation not assuming FSCTF.
    
    Use only standard YM + gauge-fixing + known results.
    """
    # Gauge-fixing adds Faddeev-Popov determinant
    # This modifies the measure: ∫ DA → ∫ DA det(∂·D)
    
    # Question: Does det(∂·D) provide mass gap?
    # Answer: In Coulomb gauge, yes! (Gribov copies)
    
    # Gribov horizon: |A| ≤ A_Gribov ~ 1/g² (mass scale!)
    
    # Is A_Gribov related to our Δm = 0.899?
    A_gribov = estimate_gribov_horizon(g=1.0)
    
    print(f"Gribov horizon scale: {A_gribov:.3f}")
    print(f"Our mass gap: {MASS_GAP:.3f}")
    
    # If related: Provides alternative path to mass gap
    # Strengthens our result
```

**Acceptance criteria**:
- [ ] Grace axioms tested numerically on YM gauge-fixing
- [ ] κ measured from lattice data (if available)
- [ ] Either: κ ≈ φ⁻¹ (supports equivalence), or κ ≠ φ⁻¹ (requires modified claim)
- [ ] Alternative mass gap derivation attempted (Gribov, instantons, etc.)
- [ ] Honest statement: "Proven within FSCTF; equivalence to standard YM conjectured with evidence X"

---

## PART 5: VEV FORMULA - ADDITIONAL ROOT CAUSE

### Current Status

**Formula**: $v = \sqrt{3} M_P \alpha \pi^3 / (\phi^{21} N^9)$

**Result**: 0.026% error (excellent!)

**But**: Why these specific exponents? Currently dimensional analysis.

### ROOT CAUSE: Exponents Not Derived from Symmetry Breaking

**From VEV_DERIVATION_SUCCESS.md**:
> **Why These Specific Powers?**
> - φ²¹: "21 = N = F(8) = E8 rank → Fibonacci"
> - N⁹: "9 = 3² (three generations squared, 3D space)" OR "9 = rank(E8) + 1"
> - π³: "π³ ≈ 31.0 (volume element in 3D space?)"
> - √3: "3 generations / 3 spatial dimensions / SU(3)"

**These are plausible but not rigorous derivations.**

### RESOLUTION PATH 5: Derive Exponents from Symmetry Breaking

**The E8 breaking chain**:
```
E8 → E7 × SU(2) → E6 × U(1) × SU(2) → SO(10) × U(1) → SU(5) × U(1) → SM → EWSB
```

**Each step should contribute to the suppression**:

**Step 5.1**: φ exponent from E8 → E7 × SU(2)
```python
def derive_phi_exponent_from_breaking():
    """
    Each symmetry breaking step involves φ if KAM stable.
    
    E8 rank = 8, so 8 independent breaking steps.
    
    But we have 7 steps in the chain above.
    
    Question: Why φ²¹ and not φ⁷ or φ⁸?
    
    Answer: Multiple φ factors per step?
    - E8 → E7: φ (one breaking)
    - E7 → E6: φ (another breaking)
    - ...
    
    But 21 ≠ 7 or 8. Where do the other φ's come from?
    
    Alternative: φ²¹ because N=21 nodes, and each node contributes φ to VEV?
    
    NEED RIGOROUS DERIVATION
    """
    n_breaking_steps = 7
    phi_per_step = estimate_phi_contribution_per_breaking()
    
    total_phi_exponent = n_breaking_steps * phi_per_step
    
    print(f"Derived φ exponent: {total_phi_exponent}")
    print(f"Target: 21")
    
    return total_phi_exponent
```

**Step 5.2**: N exponent from dimensional reduction
```python
def derive_N_exponent_from_compactification():
    """
    E8 is 248D → compactifies to 4D spacetime.
    
    Compactification: 248 → 21 nodes × 12D → 4D observed
    
    KK reduction: v ~ M_P / (R₁ R₂ ... R_n)
    where R_i are compactification radii.
    
    If all R_i ~ N (21 nodes set the scale):
    v ~ M_P / N^n
    
    What is n?
    
    From string theory: n = number of compact dimensions
    
    Our case: 248D → 4D means 244D compactified
    If organized as 21 nodes × 12D: 244 / 21 ≈ 11.6
    
    But we have N⁹, not N¹² or N²¹.
    
    9 = rank(E8) + 1? Or 9 = 3²?
    
    NEED DERIVATION, not dimensional analysis
    """
    compact_dimensions = 244  # 248 - 4
    n_nodes = 21
    dof_per_node = compact_dimensions / n_nodes  # 11.6
    
    # VEV suppression should be N^(something)
    # Dimensional analysis: [v] = mass
    # [M_P / N^x] = mass if x = 0 (dimensionless N)
    # But N is number of nodes (dimensionless), so any x works!
    
    # Need PHYSICS reason for x=9
    
    return 9  # Placeholder
```

**Acceptance criteria**:
- [ ] φ²¹ derived from 7-step breaking chain (3 φ factors per step?)
- [ ] N⁹ derived from compactification geometry (not dimensional analysis)
- [ ] π³ derived from 3D spatial integration (volume element in action)
- [ ] √3 derived from SU(3) normalization or 3 generations (group theory)
- [ ] All exponents predicted before fitting (not adjusted to match 246 GeV)

---

## SUMMARY OF RESOLUTION PATHS

### Path 1: SU(5) Yukawa (Muon Formula)
**Estimated time**: 2-3 weeks  
**Difficulty**: Medium (standard group theory + RG running)  
**Impact**: Resolves 40% of mass formula issues  
**Status**: Partially implemented (CG framework exists)

### Path 2: E8 Decomposition (12N-4 Formula)
**Estimated time**: 4-6 weeks  
**Difficulty**: High (requires deep E8 representation theory)  
**Impact**: Strengthens entire theoretical foundation  
**Status**: Not started (investigation doc exists)

### Path 3: Full NS Testing (φ-Convergence)
**Estimated time**: 1-2 weeks  
**Difficulty**: Medium (code exists, needs long runs)  
**Impact**: Validates or invalidates core NS claim  
**Status**: Code ready, tests not run

### Path 4: YM Equivalence (Grace Axioms)
**Estimated time**: 3-4 weeks  
**Difficulty**: High (may require lattice data)  
**Impact**: Determines if YM result is Clay-worthy  
**Status**: Conceptual only

### Path 5: VEV Exponents (Symmetry Breaking)
**Estimated time**: 2-3 weeks  
**Difficulty**: Medium-High (KK reduction + group theory)  
**Impact**: Strengthens VEV derivation claim  
**Status**: Dimensional analysis only

---

## PRIORITY RANKING

**Immediate (Week 1-2)**:
1. **Path 3** (NS Testing) - Code ready, just needs compute time
2. **Path 1** (Yukawa) - Framework exists, fill in calculations

**Near-term (Week 3-6)**:
3. **Path 5** (VEV) - Strengthens our best result
4. **Path 4** (YM) - Determines Clay Prize viability

**Long-term (Month 2-3)**:
5. **Path 2** (E8) - Foundational but hardest

---

## ACCEPTANCE CRITERIA FOR "RESOLVED"

Each root cause is considered **RESOLVED** when:

1. ✅ Rigorous mathematical derivation (not dimensional analysis)
2. ✅ Numerical validation (tests pass, not assumed)
3. ✅ Independent verification possible (documented method)
4. ✅ Peer-review ready (no "sketches" or "placeholders")
5. ✅ Honest documentation (limitations clearly stated)

---

## NEXT ACTIONS

**User decision required**: Which path to prioritize?

**Recommendation**: Start with Path 3 (NS Testing) because:
- Code is ready
- Results will determine if we have 85% or 95% solution
- Fast turnaround (1-2 weeks)
- If fails: Saves time on premature paper writing
- If succeeds: Strong Clay Prize candidate

**Then** proceed to Path 1 (Yukawa) to strengthen mass formulas.

**Question for user**: Proceed with Path 3, or prefer different priority?

---

**Document Status**: Root cause analysis complete  
**Resolution paths**: 5 identified with concrete steps  
**Estimated time to full resolution**: 3-6 months  
**Honesty level**: Maximum (no hiding of gaps)

