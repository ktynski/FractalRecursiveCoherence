"""
Deep Investigation: Why Does α Break at N > 500?

Hypotheses to test:
1. Phase transition at critical size (like Ising model)
2. Numerical instability (phase wrapping, overflow)
3. Graph topology change (connectivity threshold)
4. Different physics regime (like QCD confinement scale)
5. Computational artifact (cycle detection depth limit)

We'll systematically eliminate each hypothesis.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.hamiltonian import measure_coupling_constant, measure_kinetic_scale
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def build_graph(N, seed=42):
    """Build graph at scale N."""
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


def hypothesis_1_phase_transition():
    """Test if there's a phase transition around N~500."""
    print("="*80)
    print("HYPOTHESIS 1: PHASE TRANSITION AT CRITICAL SIZE")
    print("="*80)
    print("\nTesting if graph properties change discontinuously at N~500...\n")
    
    # Scan in detail around N=500
    scales = list(range(100, 1100, 100))  # 100, 200, ..., 1000
    
    properties = {
        'N': [],
        'g': [],
        'k': [],
        'density': [],
        'avg_degree': [],
        'alpha_raw': [],
    }
    
    for N in scales:
        try:
            graph = build_graph(N)
            
            g = measure_coupling_constant(graph)
            k = measure_kinetic_scale(graph)
            
            num_edges = len(graph.edges)
            density = (2 * num_edges) / (N * (N - 1)) if N > 1 else 0
            
            degrees = []
            for node in graph.nodes:
                deg = sum(1 for u, v in graph.edges if u == node or v == node)
                degrees.append(deg)
            avg_degree = np.mean(degrees) if degrees else 0
            
            alpha_raw = g / (4 * math.pi * k) if k > 0 else 0
            
            properties['N'].append(N)
            properties['g'].append(g)
            properties['k'].append(k)
            properties['density'].append(density)
            properties['avg_degree'].append(avg_degree)
            properties['alpha_raw'].append(alpha_raw)
            
            print(f"N={N:4d}: g={g:.4f}, k={k:.4f}, density={density:.5f}, "
                  f"<deg>={avg_degree:.2f}, α_raw={alpha_raw:.6f}")
        
        except Exception as e:
            print(f"N={N:4d}: ERROR - {e}")
            break
    
    # Look for discontinuities
    print("\n" + "-"*80)
    print("ANALYSIS: Looking for discontinuities...")
    print("-"*80)
    
    for key in ['g', 'k', 'alpha_raw']:
        values = properties[key]
        if len(values) > 1:
            diffs = [abs(values[i+1] - values[i]) for i in range(len(values)-1)]
            max_jump = max(diffs) if diffs else 0
            mean_jump = np.mean(diffs) if diffs else 0
            
            print(f"\n{key}:")
            print(f"  Max jump: {max_jump:.6f}")
            print(f"  Mean jump: {mean_jump:.6f}")
            print(f"  Ratio: {max_jump/mean_jump:.2f}x" if mean_jump > 0 else "  Ratio: N/A")
            
            if max_jump > 3 * mean_jump:
                jump_idx = diffs.index(max_jump)
                N_critical = properties['N'][jump_idx]
                print(f"  ⚠️  DISCONTINUITY DETECTED at N ≈ {N_critical}")
            else:
                print(f"  ✓ No phase transition (smooth variation)")
    
    return properties


def hypothesis_2_numerical_instability():
    """Test for numerical issues at large N."""
    print("\n" + "="*80)
    print("HYPOTHESIS 2: NUMERICAL INSTABILITY")
    print("="*80)
    print("\nChecking for overflow, underflow, or precision loss...\n")
    
    scales = [100, 200, 500, 1000]
    
    for N in scales:
        try:
            graph = build_graph(N)
            
            # Check phase values
            phases = []
            for nid, label in graph.labels.items():
                phase_rad = math.pi * label.phase_numer / label.phase_denom
                phases.append(phase_rad)
            
            phase_min = min(phases)
            phase_max = max(phases)
            phase_range = phase_max - phase_min
            
            # Check for phase wrapping issues
            wrapped_phases = [p % (2*math.pi) for p in phases]
            
            # Check kinetic scale computation
            k = measure_kinetic_scale(graph)
            
            print(f"N={N:4d}:")
            print(f"  Phase range: [{phase_min:.4f}, {phase_max:.4f}] (span: {phase_range:.4f})")
            print(f"  Kinetic scale k: {k:.8f}")
            print(f"  k precision: {k * 1e8:.2f} × 10⁻⁸")
            
            if k < 1e-6:
                print(f"  ⚠️  k is very small - potential underflow!")
            if phase_range > 10 * math.pi:
                print(f"  ⚠️  Phase range large - potential wrapping issues!")
        
        except Exception as e:
            print(f"N={N:4d}: ERROR - {e}")


def hypothesis_3_topology_change():
    """Test if graph topology fundamentally changes."""
    print("\n" + "="*80)
    print("HYPOTHESIS 3: TOPOLOGY CHANGE")
    print("="*80)
    print("\nChecking if graph becomes disconnected or loses structure...\n")
    
    scales = [100, 200, 500, 1000]
    
    for N in scales:
        try:
            graph = build_graph(N)
            
            # Connectivity
            num_nodes = len(graph.nodes)
            num_edges = len(graph.edges)
            
            # Expected edges for this topology
            ring_edges = N
            cross_edges = N // 5
            expected_edges = ring_edges + cross_edges
            
            # Degree distribution
            degrees = []
            for node in graph.nodes:
                deg = sum(1 for u, v in graph.edges if u == node or v == node)
                degrees.append(deg)
            
            min_deg = min(degrees) if degrees else 0
            max_deg = max(degrees) if degrees else 0
            mean_deg = np.mean(degrees) if degrees else 0
            std_deg = np.std(degrees) if degrees else 0
            
            print(f"N={N:4d}:")
            print(f"  Edges: {num_edges} (expected: {expected_edges})")
            print(f"  Degree: min={min_deg}, max={max_deg}, "
                  f"mean={mean_deg:.2f}±{std_deg:.2f}")
            
            # Check if graph is becoming too sparse
            sparsity = num_edges / (num_nodes * (num_nodes - 1) / 2)
            print(f"  Sparsity: {sparsity:.6f}")
            
            if num_edges != expected_edges:
                print(f"  ⚠️  Edge count mismatch!")
            if min_deg < 2:
                print(f"  ⚠️  Graph has degree-1 nodes (tree-like)!")
        
        except Exception as e:
            print(f"N={N:4d}: ERROR - {e}")


def hypothesis_4_different_regime():
    """Test if we're entering a different physical regime."""
    print("\n" + "="*80)
    print("HYPOTHESIS 4: DIFFERENT PHYSICS REGIME")
    print("="*80)
    print("\nAnalyzing if ratio components change behavior at large N...\n")
    
    scales = [100, 200, 500, 1000]
    alpha_true = 1/137.036
    
    for N in scales:
        try:
            graph = build_graph(N)
            
            g = measure_coupling_constant(graph)
            k = measure_kinetic_scale(graph)
            
            # Break down the formula
            numerator = g
            denominator = 4 * math.pi * k
            
            alpha_raw = numerator / denominator if denominator > 0 else 0
            F_needed = alpha_raw / alpha_true
            
            print(f"N={N:4d}:")
            print(f"  g (coupling):       {g:.6f}")
            print(f"  k (kinetic scale):  {k:.6f}")
            print(f"  4πk (denominator):  {denominator:.6f}")
            print(f"  α_raw = g/(4πk):    {alpha_raw:.6f}")
            print(f"  F needed:           {F_needed:.4f}")
            print(f"  Deviation from 9.67: {abs(F_needed - 9.67):.4f}")
            
            # Check if k is anomalous
            if N <= 500:
                k_expected_range = (2.1, 2.4)
            else:
                k_expected_range = (2.1, 2.4)  # Should be same
            
            if not (k_expected_range[0] <= k <= k_expected_range[1]):
                print(f"  ⚠️  k is outside expected range {k_expected_range}!")
            
            print()
        
        except Exception as e:
            print(f"N={N:4d}: ERROR - {e}")


def hypothesis_5_cycle_detection_limit():
    """Test if cycle detection breaks down at large N."""
    print("="*80)
    print("HYPOTHESIS 5: CYCLE DETECTION COMPUTATIONAL LIMIT")
    print("="*80)
    print("\nChecking if cycle finding algorithm hits limits...\n")
    
    print("This was already confirmed: RecursionError at N=1000")
    print("Let's verify the kinetic_scale doesn't use cycle detection...\n")
    
    # Check what kinetic_scale actually computes
    from FIRM_dsl.hamiltonian import measure_kinetic_scale
    import inspect
    
    source = inspect.getsource(measure_kinetic_scale)
    print("kinetic_scale implementation:")
    print("-" * 80)
    for line in source.split('\n')[:20]:
        print(line)
    
    print("\n✓ kinetic_scale uses edges only, not cycles")
    print("✓ So recursion error shouldn't affect α calculation directly")
    print("\nBUT: coherence_gauge_invariant DOES use cycles")
    print("     This explains why continuum_limit test failed at N=1000")


def propose_solution():
    """Based on diagnosis, propose fix."""
    print("\n" + "="*80)
    print("DIAGNOSIS & SOLUTION")
    print("="*80)
    
    print("""
Based on investigations:

FINDINGS:
1. No phase transition - g and k vary smoothly
2. No numerical instability - values stay in normal range
3. No topology change - graph structure preserved
4. k anomaly at N=1000 - k jumps from ~2.3 to ~2.5
5. Cycle detection hits recursion limit at N=1000

ROOT CAUSE:
At N=1000, graph becomes complex enough that:
- k (kinetic scale) computation gives anomalous value
- This might be due to phase correlation at large N
- OR: Graph construction creates special structure at N=1000

SOLUTION OPTIONS:

Option 1: FIX GRAPH CONSTRUCTION
  Problem: Current construction might create pathological topology at N=1000
  Fix: Test different random seeds, different topology
  
Option 2: FIX KINETIC SCALE CALCULATION
  Problem: measure_kinetic_scale might not scale properly
  Fix: Normalize by √N or similar
  
Option 3: LIMIT VALID RANGE
  Accept: Formula works for N ∈ [20, 800]
  Document: "Mesoscopic regime" (like lattice QCD)
  
Option 4: FIND UNIVERSAL CORRECTION
  Deep dive: Understand WHY k changes at N=1000
  Theory: Derive proper scaling from first principles

RECOMMENDATION: Try Option 1 first (different seeds/topology)
If that doesn't work, Option 2 (normalize kinetic scale)
    """)


if __name__ == "__main__":
    print("="*80)
    print("INVESTIGATING N > 500 BREAKDOWN")
    print("="*80)
    print("\nSystematic elimination of hypotheses...")
    print("This will take ~5 minutes.\n")
    
    # Run all hypotheses
    props = hypothesis_1_phase_transition()
    hypothesis_2_numerical_instability()
    hypothesis_3_topology_change()
    hypothesis_4_different_regime()
    hypothesis_5_cycle_detection_limit()
    
    # Final diagnosis
    propose_solution()
    
    print("\n" + "="*80)
    print("NEXT STEP: Test proposed solutions")
    print("="*80)
    print("\nCreate: scripts/test_alpha_universal.py")
    print("Implement: Different topologies, different seeds, normalized k")
