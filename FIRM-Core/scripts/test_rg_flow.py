"""
Test Renormalization Group Flow

Measure if coupling constants "run" with scale (graph size).

In QFT: β(g) = dg/d(log μ) where μ is energy scale
In FIRM: β(g) = dg/d(log N) where N is graph size (proxy for energy)

We measure dynamical couplings (rewrite rates) not structural (edge density).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def measure_rewrite_rates_at_scale(num_nodes, num_steps=100):
    """
    Measure rewrite rates at a given scale.
    
    Returns:
        Dict with rates for different rewrite types
    """
    # Initialize graph
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
    graph = validate_object_g(graph)
    
    # Count events
    grace_events = 0
    crosslink_events = 0
    total_steps = 0
    
    for step in range(num_steps):
        total_steps += 1
        
        # Grace emergence (probabilistic)
        if np.random.random() < 0.1:
            new_id = len(graph.nodes)
            kind = 'Z' if np.random.random() > 0.5 else 'X'
            phase_numer = int((new_id * 100 / phi)) % 100
            
            new_label = make_node_label(kind, phase_numer, 100, f'n{new_id}')
            graph.nodes.append(new_id)
            graph.labels[new_id] = new_label
            
            if graph.nodes[:-1]:
                target = np.random.choice(graph.nodes[:-1])
                graph.edges.append([new_id, target])
            
            grace_events += 1
        
        # Cross-link formation
        if len(graph.nodes) > 5 and np.random.random() < 0.2:
            n1, n2 = np.random.choice(graph.nodes, 2, replace=False)
            if [n1, n2] not in graph.edges and [n2, n1] not in graph.edges:
                graph.edges.append([n1, n2])
                crosslink_events += 1
        
        graph = validate_object_g(graph)
    
    # Compute rates
    grace_rate = grace_events / total_steps
    crosslink_rate = crosslink_events / total_steps
    total_rate = (grace_events + crosslink_events) / total_steps
    
    return {
        "num_nodes": len(graph.nodes),
        "grace_rate": grace_rate,
        "crosslink_rate": crosslink_rate,
        "total_rate": total_rate,
        "grace_events": grace_events,
        "crosslink_events": crosslink_events
    }


def test_rg_flow():
    """Test if couplings run with scale."""
    print("="*80)
    print("RENORMALIZATION GROUP FLOW TEST")
    print("="*80)
    
    # Test at multiple scales
    scales = [10, 20, 40, 80]
    results = []
    
    print("\nMeasuring coupling constants at different scales:")
    print("-"*80)
    
    for N in scales:
        print(f"\nScale N = {N}:")
        result = measure_rewrite_rates_at_scale(N, num_steps=100)
        results.append(result)
        
        print(f"  Final nodes: {result['num_nodes']}")
        print(f"  Grace rate g_G: {result['grace_rate']:.6f}")
        print(f"  Crosslink rate g_C: {result['crosslink_rate']:.6f}")
        print(f"  Total rate g_total: {result['total_rate']:.6f}")
    
    # Analyze running
    print("\n" + "="*80)
    print("RUNNING ANALYSIS")
    print("="*80)
    
    grace_rates = [r['grace_rate'] for r in results]
    crosslink_rates = [r['crosslink_rate'] for r in results]
    log_scales = [np.log(r['num_nodes']) for r in results]
    
    # Compute β-functions (dg/d(log N))
    if len(grace_rates) > 1:
        # Linear fit: g vs log(N)
        beta_grace = np.polyfit(log_scales, grace_rates, 1)[0]
        beta_crosslink = np.polyfit(log_scales, crosslink_rates, 1)[0]
        
        print(f"\nβ-functions:")
        print(f"  β_grace = dg_G/d(log N) = {beta_grace:.6f}")
        print(f"  β_crosslink = dg_C/d(log N) = {beta_crosslink:.6f}")
        
        # Check for significant running
        grace_range = max(grace_rates) - min(grace_rates)
        crosslink_range = max(crosslink_rates) - min(crosslink_rates)
        
        grace_relative = grace_range / np.mean(grace_rates) if np.mean(grace_rates) > 0 else 0
        crosslink_relative = crosslink_range / np.mean(crosslink_rates) if np.mean(crosslink_rates) > 0 else 0
        
        print(f"\nRelative running:")
        print(f"  Grace: {grace_relative*100:.1f}%")
        print(f"  Crosslink: {crosslink_relative*100:.1f}%")
        
        # RG flow detected if relative running > 10%
        if grace_relative > 0.10 or crosslink_relative > 0.10:
            print("\n✓ RENORMALIZATION GROUP FLOW DETECTED")
            has_rg = True
        else:
            print("\n✗ No significant RG flow (< 10% running)")
            has_rg = False
        
        # Check for asymptotic freedom (β < 0)
        if beta_grace < -0.001 or beta_crosslink < -0.001:
            print("  ✓ ASYMPTOTIC FREEDOM (coupling decreases at high energy)")
        elif beta_grace > 0.001 or beta_crosslink > 0.001:
            print("  ~ Coupling increases at high energy (like QED)")
        
        return has_rg
    
    return False


if __name__ == "__main__":
    has_rg_flow = test_rg_flow()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if has_rg_flow:
        print("\n✓ RG flow detected in dynamical couplings")
        print("  This is phenomenon #16!")
    else:
        print("\n✗ No RG flow in current implementation")
        print("  Possible reasons:")
        print("  1. Need larger scale range (10 → 10,000)")
        print("  2. Need loop-based rewrites (theory extension)")
        print("  3. Couplings are truly scale-independent (feature)")
    
    print("="*80)
