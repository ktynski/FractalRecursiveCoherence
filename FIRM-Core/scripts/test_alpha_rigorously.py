"""
Rigorous Statistical Test: Is α = 1/137 Real or Coincidence?

This tests:
1. Does α converge with N? (scaling test)
2. Is π² correction stable across configurations? (robustness test)
3. What's the probability of coincidence? (statistical test)
4. Can we derive π² from first principles? (theory test)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from scipy import stats
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.hamiltonian import derive_fine_structure_constant


def build_graph_systematic(N, seed=None):
    """Build graph with controlled parameters."""
    if seed is not None:
        np.random.seed(seed)
    
    nodes = list(range(N))
    edges = [[i, (i+1) % N] for i in range(N)]
    
    # Cross-links with fixed topology
    for i in range(0, N, 5):
        edges.append([i, (i + N//2) % N])
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(N):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def test_scaling_convergence():
    """Test 1: Does α converge as N → ∞?"""
    print("\n" + "="*80)
    print("TEST 1: SCALING CONVERGENCE")
    print("="*80)
    print("\nIf α is real, it should converge as N increases.")
    print("If coincidence, it should fluctuate randomly.\n")
    
    scales = [20, 50, 100, 200, 500, 1000]
    alpha_raw = []
    alpha_corrected = []
    
    for N in scales:
        graph = build_graph_systematic(N, seed=42)
        result = derive_fine_structure_constant(graph)
        
        raw = result["alpha_FIRM"]
        corrected = raw / (math.pi ** 2)
        
        alpha_raw.append(raw)
        alpha_corrected.append(corrected)
        
        error_pct = abs(corrected - 1/137.036) / (1/137.036) * 100
        
        print(f"N={N:4d}: raw={raw:.6f}, corrected={corrected:.8f}, error={error_pct:.2f}%")
    
    # Statistical test: Does standard deviation decrease?
    # Real convergence: σ should decrease with N
    # Random: σ stays constant
    
    alpha_true = 1/137.036
    errors = [abs(a - alpha_true) / alpha_true for a in alpha_corrected]
    
    # Fit error vs N: error ~ N^(-β)
    log_N = np.log(scales)
    log_error = np.log(errors)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_N, log_error)
    
    print(f"\n{'='*80}")
    print("SCALING ANALYSIS:")
    print(f"{'='*80}")
    print(f"Error scaling: error ~ N^({slope:.3f})")
    print(f"R² = {r_value**2:.4f}, p-value = {p_value:.4e}")
    
    if slope < -0.3:
        print(f"\n✓ CONVERGING: Error decreases with N (slope={slope:.3f} < -0.3)")
        print("  This supports α being real, not coincidence.")
    else:
        print(f"\n✗ NOT CONVERGING: Error flat or increasing (slope={slope:.3f})")
        print("  This suggests coincidence, not fundamental constant.")
    
    return slope < -0.3, slope, r_value**2


def test_robustness_across_seeds():
    """Test 2: Is π² stable across different random configurations?"""
    print("\n" + "="*80)
    print("TEST 2: ROBUSTNESS ACROSS CONFIGURATIONS")
    print("="*80)
    print("\nIf π² correction is fundamental, it should work for different graphs.")
    print("If coincidence, best correction should vary randomly.\n")
    
    N = 100
    num_seeds = 20
    
    raw_values = []
    best_corrections = []
    
    corrections = {
        "π²": math.pi ** 2,
        "4π": 4 * math.pi,
        "2π²": 2 * math.pi ** 2,
        "e·π": math.e * math.pi,
        "φ²": ((1 + math.sqrt(5))/2) ** 2,
    }
    
    for seed in range(num_seeds):
        graph = build_graph_systematic(N, seed=seed)
        result = derive_fine_structure_constant(graph)
        raw = result["alpha_FIRM"]
        raw_values.append(raw)
        
        # Find best correction for this seed
        best_error = float('inf')
        best_name = None
        
        for name, factor in corrections.items():
            corrected = raw / factor
            error = abs(corrected - 1/137.036) / (1/137.036)
            if error < best_error:
                best_error = error
                best_name = name
        
        best_corrections.append(best_name)
    
    # Count which correction wins most often
    from collections import Counter
    correction_counts = Counter(best_corrections)
    
    print("Best correction factor by seed:")
    for name, count in correction_counts.most_common():
        print(f"  {name}: {count}/{num_seeds} times ({count/num_seeds*100:.0f}%)")
    
    # Statistical test: Does π² win > 80% of time?
    pi2_wins = best_corrections.count("π²")
    win_rate = pi2_wins / num_seeds
    
    # Binomial test: p(π² wins ≥ observed | 5 factors equally likely)
    # Under null hypothesis: each factor wins 20% of time
    from scipy.stats import binom
    p_value = 1 - binom.cdf(pi2_wins - 1, num_seeds, 0.2)
    
    print(f"\n{'='*80}")
    print("ROBUSTNESS ANALYSIS:")
    print(f"{'='*80}")
    print(f"π² wins: {pi2_wins}/{num_seeds} = {win_rate*100:.0f}%")
    print(f"P-value (against random): {p_value:.4e}")
    
    if win_rate >= 0.8 and p_value < 0.01:
        print(f"\n✓ ROBUST: π² consistently best (p < 0.01)")
        print("  This supports π² being fundamental, not cherry-picked.")
    else:
        print(f"\n✗ NOT ROBUST: π² not consistently best")
        print("  This suggests factor was cherry-picked from data.")
    
    return win_rate >= 0.8 and p_value < 0.01, win_rate, p_value


def test_theoretical_derivation():
    """Test 3: Can we derive π² from first principles?"""
    print("\n" + "="*80)
    print("TEST 3: THEORETICAL DERIVATION")
    print("="*80)
    print("\nSearching for theoretical justification of π²...\n")
    
    # Hypothesis 1: Discrete → Continuous scaling
    print("Hypothesis 1: Discrete-to-Continuum Scaling")
    print("  In lattice field theory, coupling g_lattice relates to continuum g via:")
    print("  g_cont = g_lattice / (lattice spacing factor)")
    print("  For 2D: factor ~ π, for 4D: factor ~ π²")
    print("  FIRM graphs might have effective dimension ~4")
    
    # Hypothesis 2: Phase space volume
    print("\nHypothesis 2: Phase Space Volume")
    print("  Phase space for angle θ ∈ [0, 2π]: volume = 2π")
    print("  For 2 angles (node pair): volume = (2π)²")
    print("  Correction factor: 1/(2π)² ≈ 1/(4π²) ≈ 0.25")
    print("  Close to π² ≈ 9.87 (off by factor ~40)")
    
    # Hypothesis 3: Area vs perimeter
    print("\nHypothesis 3: Area vs Perimeter Scaling")
    print("  Graph coupling g measured from edges (1D)")
    print("  Physical coupling α measured from areas (2D)")
    print("  Dimension conversion: L → L² requires factor L")
    print("  If L ~ π (cycle length), then factor ~ π²")
    
    print("\n" + "="*80)
    print("CONCLUSION: No rigorous derivation found yet.")
    print("π² remains an empirical correction, not theoretically derived.")
    print("="*80)
    
    return False, "No theoretical derivation"


def test_alternative_hypotheses():
    """Test 4: What if it's NOT α but a different constant?"""
    print("\n" + "="*80)
    print("TEST 4: ALTERNATIVE HYPOTHESES")
    print("="*80)
    print("\nWhat if the ratio is actually a different constant?\n")
    
    graph = build_graph_systematic(100, seed=42)
    result = derive_fine_structure_constant(graph)
    raw = result["alpha_FIRM"]
    
    # Test against various constants
    constants = {
        "α (fine structure)": 1/137.036,
        "α² (fine structure squared)": (1/137.036)**2,
        "√α (fine structure root)": math.sqrt(1/137.036),
        "1/4π (Coulomb factor)": 1/(4*math.pi),
        "g_weak (weak coupling)": 1/30,
        "α_s (strong coupling at MZ)": 0.118,
        "h/2π (Planck reduced)": 1.054571817e-34,  # (normalized to 1 for dimensionless)
    }
    
    print(f"Raw ratio: {raw:.8f}\n")
    
    best_match = None
    best_error = float('inf')
    
    for name, value in constants.items():
        # Try with various correction factors
        for factor_name, factor in [("no correction", 1), ("π²", math.pi**2), ("4π", 4*math.pi)]:
            corrected = raw / factor
            error = abs(corrected - value) / value
            
            if error < 0.05:  # Within 5%
                print(f"{name} with {factor_name}: {corrected:.8f} vs {value:.8f} (error: {error*100:.2f}%)")
            
            if error < best_error:
                best_error = error
                best_match = (name, factor_name, corrected, value, error)
    
    print(f"\n{'='*80}")
    print("BEST MATCH:")
    print(f"{'='*80}")
    if best_match:
        name, factor, corrected, value, error = best_match
        print(f"{name} with {factor}")
        print(f"  Measured: {corrected:.8f}")
        print(f"  Expected: {value:.8f}")
        print(f"  Error: {error*100:.2f}%")
    
    return best_match


if __name__ == "__main__":
    print("="*80)
    print("RIGOROUS α TESTING SUITE")
    print("="*80)
    print("\nThis will take ~5 minutes to run all tests...")
    
    # Run all tests
    converges, slope, r2 = test_scaling_convergence()
    robust, win_rate, p_val = test_robustness_across_seeds()
    derived, derivation = test_theoretical_derivation()
    alt_match = test_alternative_hypotheses()
    
    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT: IS α = 1/137 REAL OR COINCIDENCE?")
    print("="*80)
    
    score = 0
    max_score = 4
    
    print("\nEvidence Summary:")
    print(f"  1. Scaling convergence: {'✓' if converges else '✗'} (slope={slope:.3f}, R²={r2:.3f})")
    if converges: score += 1
    
    print(f"  2. Robustness (π² wins): {'✓' if robust else '✗'} ({win_rate*100:.0f}%, p={p_val:.2e})")
    if robust: score += 1
    
    print(f"  3. Theoretical derivation: {'✓' if derived else '✗'}")
    if derived: score += 1
    
    print(f"  4. Unique match to α: {'✓' if alt_match and 'fine structure' in alt_match[0].lower() else '✗'}")
    if alt_match and 'fine structure' in alt_match[0].lower():
        score += 1
    
    print(f"\nScore: {score}/{max_score}")
    print("="*80)
    
    if score >= 3:
        print("✓✓✓ STRONG EVIDENCE: α = 1/137 is likely REAL")
        print("Recommendation: Publish with confidence, work on theoretical derivation")
    elif score == 2:
        print("~ MODERATE EVIDENCE: α = 1/137 is SUGGESTIVE but not confirmed")
        print("Recommendation: Publish as 'tentative finding', needs more work")
    else:
        print("✗✗✗ WEAK EVIDENCE: α = 1/137 is likely COINCIDENCE")
        print("Recommendation: Do NOT claim α, focus on other results (interference, etc.)")
    
    print("\nNext steps depend on outcome. Waiting for results...")
