"""
Test 2: Continuum Limit

Do violations → 0 as N → ∞?

For FIRM to be a valid discrete approximation to continuous physics:
- Gauge violation should scale as ~ 1/N or better
- Lorentz violation should scale as ~ 1/N^β where β > 0
- CPT violation should also decrease

If violations stay constant or increase, FIRM is fundamentally discrete
and cannot be a substrate for continuous physics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from scipy import stats
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def build_graph(N, seed=42):
    """Build test graph at scale N."""
    np.random.seed(seed)
    nodes = list(range(N))
    edges = [[i, (i+1) % N] for i in range(N)]
    
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


def measure_gauge_violation(graph, shift=50):
    """Measure U(1) gauge violation."""
    coh_before = compute_coherence(graph)
    
    # Shift phases
    shifted_labels = {}
    for node_id, label in graph.labels.items():
        from FIRM_dsl.core import make_node_label
        new_numer = (label.phase_numer + shift) % (2 * label.phase_denom)
        shifted_labels[node_id] = make_node_label(
            label.kind, new_numer, label.phase_denom, label.monadic_id
        )
    
    shifted_graph = ObjectG(
        nodes=graph.nodes.copy(),
        edges=graph.edges.copy(),
        labels=shifted_labels
    )
    shifted_graph = validate_object_g(shifted_graph)
    coh_after = compute_coherence(shifted_graph)
    
    return abs(coh_after - coh_before) / (coh_before + 1e-10)


def measure_lorentz_violation(graph, gamma=1.5):
    """Measure Lorentz violation under boost."""
    coh_before = compute_coherence(graph)
    
    # Apply "boost" (phase rescaling)
    boosted_labels = {}
    for node_id, label in graph.labels.items():
        from FIRM_dsl.core import make_node_label
        # Scale phase by gamma, wrap to [0, 2*denom)
        new_numer = int((label.phase_numer * gamma)) % (2 * label.phase_denom)
        boosted_labels[node_id] = make_node_label(
            label.kind, new_numer, label.phase_denom, label.monadic_id
        )
    
    boosted_graph = ObjectG(
        nodes=graph.nodes.copy(),
        edges=graph.edges.copy(),
        labels=boosted_labels
    )
    boosted_graph = validate_object_g(boosted_graph)
    coh_after = compute_coherence(boosted_graph)
    
    return abs(coh_after - coh_before) / (coh_before + 1e-10)


def test_continuum_scaling():
    """Test if violations → 0 as N → ∞."""
    print("="*80)
    print("CONTINUUM LIMIT TEST")
    print("="*80)
    print("\nTesting if violations decrease with system size N...\n")
    
    scales = [20, 50, 100, 200, 500, 1000]
    gauge_violations = []
    lorentz_violations = []
    
    for N in scales:
        print(f"N = {N}...")
        graph = build_graph(N)
        
        gauge_viol = measure_gauge_violation(graph)
        lorentz_viol = measure_lorentz_violation(graph)
        
        gauge_violations.append(gauge_viol)
        lorentz_violations.append(lorentz_viol)
        
        print(f"  Gauge violation: {gauge_viol*100:.3f}%")
        print(f"  Lorentz violation: {lorentz_viol*100:.3f}%")
    
    # Fit: violation ~ N^(-β)
    log_N = np.log(scales)
    
    log_gauge = np.log(gauge_violations)
    slope_gauge, _, r2_gauge, p_gauge, _ = stats.linregress(log_N, log_gauge)
    
    log_lorentz = np.log(lorentz_violations)
    slope_lorentz, _, r2_lorentz, p_lorentz, _ = stats.linregress(log_N, log_lorentz)
    
    print("\n" + "="*80)
    print("SCALING ANALYSIS")
    print("="*80)
    
    print(f"\nGauge violation scaling:")
    print(f"  violation ~ N^({slope_gauge:.3f})")
    print(f"  R² = {r2_gauge:.4f}, p = {p_gauge:.4e}")
    
    if slope_gauge < -0.3:
        print(f"  ✓ CONVERGING to gauge symmetry (slope < -0.3)")
    else:
        print(f"  ✗ NOT CONVERGING (slope ≥ -0.3)")
    
    print(f"\nLorentz violation scaling:")
    print(f"  violation ~ N^({slope_lorentz:.3f})")
    print(f"  R² = {r2_lorentz:.4f}, p = {p_lorentz:.4e}")
    
    if slope_lorentz < -0.3:
        print(f"  ✓ CONVERGING to Lorentz invariance (slope < -0.3)")
    else:
        print(f"  ✗ NOT CONVERGING (slope ≥ -0.3)")
    
    # Extrapolate to N → ∞
    print(f"\n{'='*80}")
    print("EXTRAPOLATION TO N → ∞")
    print("="*80)
    
    N_large = 10000
    gauge_extrap = gauge_violations[-1] * (N_large / scales[-1]) ** slope_gauge
    lorentz_extrap = lorentz_violations[-1] * (N_large / scales[-1]) ** slope_lorentz
    
    print(f"\nExtrapolated to N = {N_large}:")
    print(f"  Gauge violation: {gauge_extrap*100:.4f}%")
    print(f"  Lorentz violation: {lorentz_extrap*100:.4f}%")
    
    if gauge_extrap < 0.001 and lorentz_extrap < 0.01:
        print(f"\n✓✓✓ CONTINUUM LIMIT EXISTS")
        print("FIRM can approximate continuous physics at large N")
    elif gauge_extrap < 0.01 and lorentz_extrap < 0.05:
        print(f"\n~ APPROXIMATE CONTINUUM")
        print("FIRM approaches continuous physics, but slowly")
    else:
        print(f"\n✗✗✗ NO CONTINUUM LIMIT")
        print("FIRM is fundamentally discrete, not an approximation to continuous physics")
    
    return {
        'gauge_slope': slope_gauge,
        'lorentz_slope': slope_lorentz,
        'gauge_extrap': gauge_extrap,
        'lorentz_extrap': lorentz_extrap
    }


if __name__ == "__main__":
    results = test_continuum_scaling()
    
    print("\n" + "="*80)
    print("VERDICT")
    print("="*80)
    
    if results['gauge_slope'] < -0.5 and results['lorentz_slope'] < -0.5:
        print("\n✓ FIRM has a continuum limit")
        print("  Violations decrease faster than 1/√N")
        print("  → Valid discrete approximation to continuous physics")
    elif results['gauge_slope'] < -0.3 and results['lorentz_slope'] < -0.3:
        print("\n~ FIRM approaches continuum (slowly)")
        print("  Violations decrease, but not rapidly")
        print("  → Possibly valid, needs larger N to confirm")
    else:
        print("\n✗ FIRM is fundamentally discrete")
        print("  Violations do NOT decrease with N")
        print("  → Not an approximation to continuous physics")
        print("  → Claims about QM/relativity need reinterpretation")
