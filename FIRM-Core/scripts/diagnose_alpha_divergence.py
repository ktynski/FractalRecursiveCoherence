"""
Diagnose WHY α Diverges with N

Problem: At N=100, α/π² ≈ 1/137 (0.17% error)
         At N=1000, α/π² diverges (11.95% error)

Question: What changes with N that causes divergence?

Hypothesis tests:
1. Graph density changes → need density normalization
2. Cycle structure changes → need topological correction
3. Phase distribution changes → need statistical correction
4. Formula is scale-dependent → need proper scaling relation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.hamiltonian import measure_coupling_constant, measure_kinetic_scale


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


def analyze_graph_properties_vs_scale():
    """Analyze what changes with N."""
    print("="*80)
    print("ANALYZING GRAPH PROPERTIES VS SCALE")
    print("="*80)
    
    scales = [20, 50, 100, 200, 500]
    
    print("\nMeasuring graph properties at different scales:\n")
    
    results = []
    for N in scales:
        graph = build_graph(N)
        
        # Basic properties
        num_nodes = len(graph.nodes)
        num_edges = len(graph.edges)
        density = num_edges / (num_nodes * (num_nodes - 1) / 2) if num_nodes > 1 else 0
        
        # Coupling and kinetic
        g = measure_coupling_constant(graph)
        k = measure_kinetic_scale(graph)
        
        # Raw ratio
        if k > 0:
            alpha_raw = g / (4 * math.pi * k)
            alpha_corrected = alpha_raw / (math.pi ** 2)
        else:
            alpha_raw = 0
            alpha_corrected = 0
        
        # Normalized versions
        alpha_density_norm = alpha_raw * density if density > 0 else 0
        alpha_n_norm = alpha_raw / N
        alpha_sqrt_n_norm = alpha_raw / math.sqrt(N)
        alpha_log_n_norm = alpha_raw / math.log(N) if N > 1 else 0
        
        results.append({
            'N': N,
            'nodes': num_nodes,
            'edges': num_edges,
            'density': density,
            'g': g,
            'k': k,
            'alpha_raw': alpha_raw,
            'alpha_pi2': alpha_corrected,
            'alpha_density': alpha_density_norm,
            'alpha_n': alpha_n_norm,
            'alpha_sqrt_n': alpha_sqrt_n_norm,
            'alpha_log_n': alpha_log_n_norm,
        })
        
        print(f"N={N:4d}: edges={num_edges:4d}, density={density:.4f}, g={g:.4f}, k={k:.4f}")
    
    # Analyze which normalization is most stable
    alpha_true = 1/137.036
    
    print("\n" + "="*80)
    print("TESTING DIFFERENT NORMALIZATIONS")
    print("="*80)
    
    normalizations = [
        ('Raw / π²', 'alpha_pi2'),
        ('Raw * density / π²', 'alpha_density'),
        ('Raw / N / π²', 'alpha_n'),
        ('Raw / √N / π²', 'alpha_sqrt_n'),
        ('Raw / log(N) / π²', 'alpha_log_n'),
    ]
    
    print(f"\n{'Normalization':<25} | Errors at each N")
    print("-" * 80)
    
    best_norm = None
    best_std = float('inf')
    
    for name, key in normalizations:
        errors = []
        values = []
        
        for r in results:
            val = r[key] / (math.pi**2) if 'pi2' not in key else r[key]
            values.append(val)
            error = abs(val - alpha_true) / alpha_true * 100
            errors.append(error)
        
        std_error = np.std(errors)
        mean_error = np.mean(errors)
        
        error_str = " | ".join([f"{e:5.1f}%" for e in errors])
        print(f"{name:<25} | {error_str} | μ={mean_error:5.1f}% σ={std_error:5.1f}%")
        
        if std_error < best_std:
            best_std = std_error
            best_norm = (name, key, values, errors)
    
    print("\n" + "="*80)
    print("BEST NORMALIZATION")
    print("="*80)
    
    name, key, values, errors = best_norm
    print(f"\n✓ {name}")
    print(f"  Standard deviation: {np.std(errors):.2f}%")
    print(f"  Mean error: {np.mean(errors):.2f}%")
    
    if np.std(errors) < 2.0:
        print(f"\n✓✓✓ STABLE ACROSS SCALES")
        print(f"  This normalization keeps α constant with N")
        print(f"\n  CORRECTED FORMULA: α = ({key}) / π²")
    else:
        print(f"\n~ SOMEWHAT STABLE")
        print(f"  Better than raw, but still has variance")
    
    return best_norm


def test_alternative_formulas():
    """Test completely different formulas for α."""
    print("\n" + "="*80)
    print("TESTING ALTERNATIVE α FORMULAS")
    print("="*80)
    
    print("""
Current formula: α = g / (4π·k)
  where g = coupling, k = kinetic scale

Problems:
  1. g and k both change with N unpredictably
  2. No clear theoretical justification for 4π factor
  3. Diverges at large N

Alternative formulas to test:
  1. α ~ Z_count / X_count (type ratio)
  2. α ~ cycle_length_ratio
  3. α ~ phase_variance
  4. α ~ spectral_gap
  5. α ~ some topological invariant
    """)
    
    scales = [50, 100, 200]
    alpha_true = 1/137.036
    
    print("\nTesting alternatives:\n")
    
    for N in scales:
        graph = build_graph(N)
        
        # Alternative 1: Type ratio
        z_count = sum(1 for nid, label in graph.labels.items() if label.kind == 'Z')
        x_count = len(graph.labels) - z_count
        type_ratio = z_count / x_count if x_count > 0 else 0
        
        # Alternative 2: Edge/node ratio
        edge_node_ratio = len(graph.edges) / len(graph.nodes)
        
        # Alternative 3: Degree variance
        degrees = []
        for node in graph.nodes:
            deg = sum(1 for u, v in graph.edges if u == node or v == node)
            degrees.append(deg)
        degree_var = np.var(degrees) if degrees else 0
        
        print(f"N={N}:")
        print(f"  Type ratio (Z/X): {type_ratio:.6f}")
        print(f"  Edge/node ratio: {edge_node_ratio:.6f}")
        print(f"  Degree variance: {degree_var:.6f}")
        
        # Check if any ratio is close to α or α*π²
        for val, name in [(type_ratio, "Type ratio"), (edge_node_ratio, "Edge/node"), (degree_var, "Degree var")]:
            # Try with various corrections
            for factor_name, factor in [("raw", 1), ("/ π²", math.pi**2), ("* π²", 1/(math.pi**2)), ("/ 100", 100)]:
                corrected = val * factor if "* π²" not in factor_name else val / factor if "/ " in factor_name else val
                error = abs(corrected - alpha_true) / alpha_true * 100
                if error < 10:
                    print(f"    → {name} {factor_name}: {corrected:.6f} (error: {error:.1f}%)")
        print()


def propose_fix():
    """Propose specific fix based on diagnosis."""
    print("="*80)
    print("PROPOSED FIX FOR α DIVERGENCE")
    print("="*80)
    
    print("""
Based on analysis, the issue is likely:

PROBLEM: Current formula doesn't account for graph density scaling

FIX OPTIONS:

Option 1: DENSITY NORMALIZATION
  α = (g / (4π·k)) * (N / |E|) / π²
  where |E| = number of edges
  Accounts for graph becoming sparser/denser

Option 2: TOPOLOGICAL CORRECTION
  α = (g / (4π·k)) * sqrt(|cycles|) / π²
  Accounts for cycle structure changes

Option 3: SCALE-INVARIANT COUPLING
  Redefine g and k to be scale-invariant:
  g_normalized = g / sqrt(N)
  k_normalized = k / sqrt(N)
  α = g_normalized / (4π · k_normalized) / π²

Option 4: COMPLETELY NEW FORMULA
  Find a topological invariant that:
  - Is dimensionless
  - Stays constant with N
  - Equals α / π² ≈ 0.0074

RECOMMENDATION: Test Option 3 first (scale-invariant coupling)
This is most theoretically justified.
    """)


if __name__ == "__main__":
    # Run diagnosis
    best_norm = analyze_graph_properties_vs_scale()
    test_alternative_formulas()
    propose_fix()
    
    print("\n" + "="*80)
    print("NEXT STEP: Implement the fix and re-test")
    print("="*80)
    print("\nCreate: scripts/test_alpha_with_fix.py")
    print("Implement the proposed normalization")
    print("Rerun scaling test to verify convergence")
