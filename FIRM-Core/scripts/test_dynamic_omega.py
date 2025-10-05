"""
Test Dynamic Ω: Does correlation flip if we update Ω during evolution?

Current: Ω derived once, correlation is -0.96 (negative)
Hypothesis: If we update Ω every N steps, correlation becomes positive

This tests whether negative correlation is:
- A bug (static Ω) → correlation should be positive
- A feature (phase transition) → correlation stays negative
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment


def initialize_graph(num_nodes=10):
    """Create initial graph."""
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def evolve_step(graph):
    """Simple evolution step."""
    new_id = len(graph.nodes)
    phi = (1 + np.sqrt(5)) / 2
    
    kind = 'Z' if np.random.random() > 0.5 else 'X'
    phase_numer = int((new_id * 100 / phi)) % 100
    
    new_label = make_node_label(kind, phase_numer, 100, f'n{new_id}')
    graph.nodes.append(new_id)
    graph.labels[new_id] = new_label
    
    # Connect to random existing node
    if graph.nodes[:-1]:
        target = np.random.choice(graph.nodes[:-1])
        graph.edges.append([new_id, target])
    
    # Occasionally add cross-link
    if len(graph.nodes) > 5 and np.random.random() < 0.3:
        n1, n2 = np.random.choice(graph.nodes, 2, replace=False)
        if [n1, n2] not in graph.edges and [n2, n1] not in graph.edges:
            graph.edges.append([n1, n2])
    
    return validate_object_g(graph)


def test_static_omega():
    """Test with static Ω (current implementation)."""
    print("="*80)
    print("TEST 1: STATIC Ω (Current Implementation)")
    print("="*80)
    
    graph = initialize_graph(num_nodes=10)
    omega = derive_omega_signature(graph)  # Derive once
    
    res_values = []
    coh_values = []
    
    for step in range(50):
        res = compute_resonance_alignment(graph, omega)  # Same Ω throughout
        coh = compute_coherence(graph)
        
        res_values.append(res)
        coh_values.append(coh)
        
        graph = evolve_step(graph)
    
    # Compute correlation
    correlation = np.corrcoef(res_values, coh_values)[0, 1]
    
    print(f"\nResults:")
    print(f"  Steps: {len(res_values)}")
    print(f"  Res range: [{min(res_values):.4f}, {max(res_values):.4f}]")
    print(f"  C(G) range: [{min(coh_values):.4f}, {max(coh_values):.4f}]")
    print(f"  Correlation: {correlation:.4f}")
    
    if correlation < -0.5:
        print("  ✓ Strong NEGATIVE correlation (as expected)")
    elif correlation > 0.5:
        print("  ✓ Strong POSITIVE correlation")
    else:
        print("  ~ Weak correlation")
    
    return correlation


def test_dynamic_omega(update_interval=10):
    """Test with dynamic Ω (updated every N steps)."""
    print("\n" + "="*80)
    print(f"TEST 2: DYNAMIC Ω (Updated Every {update_interval} Steps)")
    print("="*80)
    
    graph = initialize_graph(num_nodes=10)
    omega = derive_omega_signature(graph)  # Initial Ω
    
    res_values = []
    coh_values = []
    omega_updates = []
    
    for step in range(50):
        # Update Ω periodically
        if step % update_interval == 0 and step > 0:
            omega = derive_omega_signature(graph)  # Re-derive Ω
            omega_updates.append(step)
            print(f"  Ω updated at step {step}")
        
        res = compute_resonance_alignment(graph, omega)  # Dynamic Ω
        coh = compute_coherence(graph)
        
        res_values.append(res)
        coh_values.append(coh)
        
        graph = evolve_step(graph)
    
    # Compute correlation
    correlation = np.corrcoef(res_values, coh_values)[0, 1]
    
    print(f"\nResults:")
    print(f"  Steps: {len(res_values)}")
    print(f"  Ω updates: {len(omega_updates)}")
    print(f"  Res range: [{min(res_values):.4f}, {max(res_values):.4f}]")
    print(f"  C(G) range: [{min(coh_values):.4f}, {max(coh_values):.4f}]")
    print(f"  Correlation: {correlation:.4f}")
    
    if correlation < -0.5:
        print("  ✗ Still NEGATIVE (phase transition confirmed)")
    elif correlation > 0.5:
        print("  ✓ Now POSITIVE (static Ω was the issue)")
    else:
        print("  ~ Weak correlation (inconclusive)")
    
    return correlation


def compare_static_vs_dynamic():
    """Compare static and dynamic Ω correlations."""
    print("\n" + "="*80)
    print("COMPARISON: Static vs Dynamic Ω")
    print("="*80)
    
    # Run multiple trials
    static_correlations = []
    dynamic_correlations = []
    
    for trial in range(5):
        np.random.seed(trial)  # Reproducible
        
        corr_static = test_static_omega()
        corr_dynamic = test_dynamic_omega(update_interval=10)
        
        static_correlations.append(corr_static)
        dynamic_correlations.append(corr_dynamic)
        
        print(f"\nTrial {trial+1}:")
        print(f"  Static Ω:  {corr_static:+.4f}")
        print(f"  Dynamic Ω: {corr_dynamic:+.4f}")
        print(f"  Difference: {corr_dynamic - corr_static:+.4f}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    mean_static = np.mean(static_correlations)
    mean_dynamic = np.mean(dynamic_correlations)
    
    print(f"\nMean correlations:")
    print(f"  Static Ω:  {mean_static:+.4f}")
    print(f"  Dynamic Ω: {mean_dynamic:+.4f}")
    print(f"  Difference: {mean_dynamic - mean_static:+.4f}")
    
    # Interpretation
    print("\n" + "-"*80)
    print("INTERPRETATION:")
    print("-"*80)
    
    if mean_dynamic > 0.3 and mean_static < -0.3:
        print("\n✓ CORRELATION FLIPS POSITIVE with dynamic Ω")
        print("  Conclusion: Static Ω was a BUG")
        print("  Fix: Use dynamic Ω in production")
        interpretation = "BUG_FIXED"
    
    elif mean_dynamic < -0.3 and mean_static < -0.3:
        print("\n✓ CORRELATION STAYS NEGATIVE with dynamic Ω")
        print("  Conclusion: Negative correlation is a FEATURE")
        print("  Interpretation: Phase transition (vacuum → matter)")
        print("  Ω represents vacuum; evolution moves away")
        interpretation = "PHASE_TRANSITION"
    
    elif abs(mean_dynamic) < 0.3 and abs(mean_static) < 0.3:
        print("\n~ CORRELATION BECOMES WEAK with dynamic Ω")
        print("  Conclusion: Ω tracking removes correlation")
        print("  Interpretation: Res measures distance from initial state")
        interpretation = "TRACKING_ARTIFACT"
    
    else:
        print("\n? INCONCLUSIVE")
        interpretation = "UNCLEAR"
    
    return {
        "static_mean": mean_static,
        "dynamic_mean": mean_dynamic,
        "interpretation": interpretation
    }


if __name__ == "__main__":
    result = compare_static_vs_dynamic()
    
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    if result["interpretation"] == "BUG_FIXED":
        print("\n✓ Use dynamic Ω in production")
        print("  This will improve Res-C(G) coupling phenomenon")
    elif result["interpretation"] == "PHASE_TRANSITION":
        print("\n✓ Negative correlation is CORRECT")
        print("  This is a profound signature of phase transition")
        print("  Ω = vacuum state, evolution = matter formation")
    else:
        print(f"\n~ Result: {result['interpretation']}")
    
    print("="*80)
