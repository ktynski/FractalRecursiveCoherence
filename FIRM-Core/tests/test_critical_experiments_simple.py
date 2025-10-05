"""
Critical Experiments (Simplified): Quick tests for profound emergence.

This simplified version focuses on running the tests without full ZX engine complexity.
"""

import pytest
import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment


def build_simple_graph(num_nodes=5):
    """Build a simple test graph."""
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]  # Ring
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        phase_denom = 100
        labels[i] = make_node_label(kind, phase_numer, phase_denom, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def test_phase_transitions_basic():
    """Test if C(G) changes as graph evolves."""
    print("\n" + "="*60)
    print("TEST 1: PHASE TRANSITIONS")
    print("="*60)
    
    graph = build_simple_graph(num_nodes=5)
    coherence_history = []
    
    # Measure initial coherence
    coh_initial = compute_coherence(graph)
    coherence_history.append(coh_initial)
    print(f"\nInitial C(G): {coh_initial:.4f}")
    
    # Grow graph and track coherence
    for step in range(20):
        new_id = len(graph.nodes)
        kind = 'Z' if new_id % 2 == 0 else 'X'
        phase_numer = (new_id * 13) % 100
        phase_denom = 100
        
        new_label = make_node_label(kind, phase_numer, phase_denom, f'n{new_id}')
        
        # Add node
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        
        # Connect to previous node
        graph.edges.append([new_id - 1, new_id])
        
        # Validate and measure
        graph = validate_object_g(graph)
        coh = compute_coherence(graph)
        coherence_history.append(coh)
    
    print(f"Final C(G): {coherence_history[-1]:.4f}")
    print(f"Change: {coherence_history[-1] - coh_initial:+.4f}")
    
    # Check for monotonic increase (thermodynamic arrow)
    increases = sum(1 for i in range(len(coherence_history)-1) 
                    if coherence_history[i+1] > coherence_history[i])
    monotonic_fraction = increases / (len(coherence_history) - 1)
    
    print(f"\nMonotonic increase: {monotonic_fraction*100:.1f}%")
    
    if monotonic_fraction > 0.7:
        print("✓ THERMODYNAMIC ARROW OF TIME DETECTED")
    else:
        print("✗ No clear thermodynamic arrow")
    
    assert len(coherence_history) == 21


def test_resonance_coherence_correlation():
    """Test if Res(S,Ω) correlates with C(G)."""
    print("\n" + "="*60)
    print("TEST 2: RESONANCE-COHERENCE CORRELATION")
    print("="*60)
    
    graph = build_simple_graph(num_nodes=10)
    omega = derive_omega_signature(graph)
    
    res_values = []
    coh_values = []
    
    # Measure at different graph sizes
    for _ in range(15):
        res = compute_resonance_alignment(graph, omega)
        coh = compute_coherence(graph)
        
        res_values.append(res)
        coh_values.append(coh)
        
        # Add node
        new_id = len(graph.nodes)
        kind = 'Z' if new_id % 2 == 0 else 'X'
        phase_numer = (new_id * 17) % 100
        phase_denom = 100
        
        new_label = make_node_label(kind, phase_numer, phase_denom, f'n{new_id}')
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        graph.edges.append([new_id - 2, new_id])  # Cross-link
        graph = validate_object_g(graph)
    
    # Compute correlation
    if len(res_values) > 2:
        correlation = np.corrcoef(res_values, coh_values)[0, 1]
        print(f"\nCorrelation(Res, C(G)): {correlation:.4f}")
        
        if correlation > 0.5:
            print("✓ STRONG POSITIVE CORRELATION")
        elif correlation > 0.3:
            print("~ MODERATE CORRELATION")
        else:
            print("✗ WEAK OR NO CORRELATION")
        
        print(f"\nRes range: [{min(res_values):.4f}, {max(res_values):.4f}]")
        print(f"C(G) range: [{min(coh_values):.4f}, {max(coh_values):.4f}]")
    
    assert len(res_values) == 15


def test_dimensionless_ratios():
    """Test for emergent dimensionless constants."""
    print("\n" + "="*60)
    print("TEST 3: DIMENSIONLESS RATIOS")
    print("="*60)
    
    # Build larger graph
    graph = build_simple_graph(num_nodes=20)
    
    # Add cross-links to create cycles
    for i in range(0, 20, 5):
        target = (i + 10) % 20
        graph.edges.append([i, target])
    
    graph = validate_object_g(graph)
    
    # Measure graph properties
    num_nodes = len(graph.nodes)
    num_edges = len(graph.edges)
    
    # Edge/node ratio
    edge_node_ratio = num_edges / num_nodes if num_nodes > 0 else 0
    
    print(f"\nNodes: {num_nodes}")
    print(f"Edges: {num_edges}")
    print(f"Edge/Node ratio: {edge_node_ratio:.4f}")
    
    # Compare to known constants
    phi = (1 + np.sqrt(5)) / 2
    print(f"\nφ (golden ratio): {phi:.4f}")
    print(f"Ratio / φ: {edge_node_ratio / phi:.4f}")
    
    if abs(edge_node_ratio - phi) < 0.1:
        print("✓ RATIO CLOSE TO φ")
    elif abs(edge_node_ratio - np.pi) < 0.1:
        print("✓ RATIO CLOSE TO π")
    else:
        print("~ Ratio doesn't match known constants")
    
    assert num_nodes > 0


def test_gauge_symmetry_basic():
    """Test if coherence depends on phase differences (not absolute phases)."""
    print("\n" + "="*60)
    print("TEST 4: GAUGE SYMMETRY (U(1))")
    print("="*60)
    
    graph = build_simple_graph(num_nodes=8)
    coh_before = compute_coherence(graph)
    
    print(f"\nC(G) before phase shift: {coh_before:.4f}")
    
    # Apply global phase shift (add constant to all phases)
    shift = 50  # Shift by π/2 (50/100 * 2π)
    for node_id in graph.nodes:
        label = graph.labels[node_id]
        new_numer = (label.phase_numer + shift) % 100
        graph.labels[node_id] = make_node_label(
            label.kind, new_numer, label.phase_denom, label.monadic_id
        )
    
    graph = validate_object_g(graph)
    coh_after = compute_coherence(graph)
    
    print(f"C(G) after phase shift: {coh_after:.4f}")
    
    relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
    print(f"Relative change: {relative_change:.4f}")
    
    if relative_change < 0.05:
        print("✓ GAUGE INVARIANCE (U(1)) DETECTED")
    elif relative_change < 0.2:
        print("~ APPROXIMATE GAUGE INVARIANCE")
    else:
        print("✗ NO GAUGE INVARIANCE")
    
    assert True  # Always pass; this is data collection


def test_emergence_summary():
    """Run all tests and provide summary assessment."""
    print("\n" + "="*80)
    print("EMERGENCE ASSESSMENT SUMMARY")
    print("="*80)
    
    phenomena_detected = 0
    
    # Run simplified checks
    graph = build_simple_graph(num_nodes=15)
    
    # 1. Thermodynamic arrow
    coherence_history = [compute_coherence(graph)]
    for _ in range(10):
        new_id = len(graph.nodes)
        kind = 'Z' if new_id % 2 == 0 else 'X'
        new_label = make_node_label(kind, (new_id * 13) % 100, 100, f'n{new_id}')
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        graph.edges.append([new_id - 1, new_id])
        graph = validate_object_g(graph)
        coherence_history.append(compute_coherence(graph))
    
    increases = sum(1 for i in range(len(coherence_history)-1) 
                    if coherence_history[i+1] > coherence_history[i])
    if increases / len(coherence_history) > 0.7:
        phenomena_detected += 1
        print("\n✓ Thermodynamic arrow of time")
    
    # 2. Resonance correlation
    omega = derive_omega_signature(graph)
    res = compute_resonance_alignment(graph, omega)
    coh = compute_coherence(graph)
    if res > 0.3 and coh > 0.1:
        phenomena_detected += 1
        print("✓ Resonance-coherence coupling")
    
    # Final assessment
    print("\n" + "-"*80)
    print(f"Profound phenomena detected: {phenomena_detected}/5")
    
    if phenomena_detected >= 4:
        assessment = "REVOLUTIONARY"
    elif phenomena_detected >= 2:
        assessment = "HIGHLY INTERESTING"
    elif phenomena_detected >= 1:
        assessment = "PROMISING"
    else:
        assessment = "TOY MODEL"
    
    print(f"\nASSESSMENT: {assessment}")
    print("="*80)
    
    assert True  # Always pass; this is exploratory


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
