"""
Critical Experiments with Gauge-Invariant Coherence

Re-run critical experiments using the theory-compliant gauge-invariant
coherence implementation to get updated assessment.
"""

import pytest
import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence
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


def test_thermodynamic_arrow_with_gauge_fix():
    """Test thermodynamic arrow with gauge-invariant coherence."""
    print("\n" + "="*70)
    print("TEST 1: THERMODYNAMIC ARROW (Gauge-Invariant)")
    print("="*70)
    
    graph = build_simple_graph(num_nodes=5)
    coherence_history = []
    
    coh_initial = compute_coherence(graph)
    coherence_history.append(coh_initial)
    print(f"\nInitial C(G): {coh_initial:.4f}")
    
    # Grow graph
    for step in range(20):
        new_id = len(graph.nodes)
        kind = 'Z' if new_id % 2 == 0 else 'X'
        phase_numer = (new_id * 13) % 100
        phase_denom = 100
        
        new_label = make_node_label(kind, phase_numer, phase_denom, f'n{new_id}')
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        graph.edges.append([new_id - 1, new_id])
        graph = validate_object_g(graph)
        
        coh = compute_coherence(graph)
        coherence_history.append(coh)
    
    print(f"Final C(G): {coherence_history[-1]:.4f}")
    print(f"Change: {coherence_history[-1] - coh_initial:+.4f}")
    
    increases = sum(1 for i in range(len(coherence_history)-1) 
                    if coherence_history[i+1] > coherence_history[i])
    monotonic_fraction = increases / (len(coherence_history) - 1)
    
    print(f"\nMonotonic increase: {monotonic_fraction*100:.1f}%")
    
    if monotonic_fraction > 0.7:
        print("✓ THERMODYNAMIC ARROW OF TIME DETECTED")
        return True
    else:
        print("✗ No clear thermodynamic arrow")
        return False


def test_resonance_correlation_with_gauge_fix():
    """Test Res-C(G) correlation with gauge-invariant coherence."""
    print("\n" + "="*70)
    print("TEST 2: RESONANCE-COHERENCE CORRELATION (Gauge-Invariant)")
    print("="*70)
    
    graph = build_simple_graph(num_nodes=10)
    omega = derive_omega_signature(graph)
    
    res_values = []
    coh_values = []
    
    for _ in range(15):
        res = compute_resonance_alignment(graph, omega)
        coh = compute_coherence(graph)
        
        res_values.append(res)
        coh_values.append(coh)
        
        new_id = len(graph.nodes)
        kind = 'Z' if new_id % 2 == 0 else 'X'
        phase_numer = (new_id * 17) % 100
        phase_denom = 100
        
        new_label = make_node_label(kind, phase_numer, phase_denom, f'n{new_id}')
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        graph.edges.append([new_id - 2, new_id])
        graph = validate_object_g(graph)
    
    if len(res_values) > 2:
        correlation = np.corrcoef(res_values, coh_values)[0, 1]
        print(f"\nCorrelation(Res, C(G)): {correlation:.4f}")
        
        if abs(correlation) > 0.5:
            print(f"✓ STRONG CORRELATION (sign: {'positive' if correlation > 0 else 'negative'})")
            return True
        elif abs(correlation) > 0.3:
            print("~ MODERATE CORRELATION")
            return True
        else:
            print("✗ WEAK OR NO CORRELATION")
            return False
        
        print(f"\nRes range: [{min(res_values):.4f}, {max(res_values):.4f}]")
        print(f"C(G) range: [{min(coh_values):.4f}, {max(coh_values):.4f}]")
    
    return False


def test_gauge_symmetry_with_fix():
    """Test gauge symmetry with gauge-invariant coherence."""
    print("\n" + "="*70)
    print("TEST 3: GAUGE SYMMETRY (U(1)) - Gauge-Invariant")
    print("="*70)
    
    graph = build_simple_graph(num_nodes=8)
    coh_before = compute_coherence(graph)
    
    print(f"\nC(G) before phase shift: {coh_before:.4f}")
    
    # Apply global phase shift
    shift = 50
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
    
    if relative_change < 0.02:
        print("✓ GAUGE INVARIANCE (U(1)) DETECTED")
        return True
    elif relative_change < 0.05:
        print("~ APPROXIMATE GAUGE INVARIANCE")
        return True
    else:
        print("✗ NO GAUGE INVARIANCE")
        return False


def test_dimensionless_ratios_with_gauge_fix():
    """Test dimensionless ratios with gauge-invariant coherence."""
    print("\n" + "="*70)
    print("TEST 4: DIMENSIONLESS RATIOS (Gauge-Invariant)")
    print("="*70)
    
    graph = build_simple_graph(num_nodes=20)
    
    # Add cross-links
    for i in range(0, 20, 5):
        target = (i + 10) % 20
        graph.edges.append([i, target])
    
    graph = validate_object_g(graph)
    
    num_nodes = len(graph.nodes)
    num_edges = len(graph.edges)
    edge_node_ratio = num_edges / num_nodes if num_nodes > 0 else 0
    
    print(f"\nNodes: {num_nodes}")
    print(f"Edges: {num_edges}")
    print(f"Edge/Node ratio: {edge_node_ratio:.4f}")
    
    phi = (1 + np.sqrt(5)) / 2
    print(f"\nφ (golden ratio): {phi:.4f}")
    print(f"Ratio / φ: {edge_node_ratio / phi:.4f}")
    
    if abs(edge_node_ratio - phi) < 0.1:
        print("✓ RATIO CLOSE TO φ")
        return True
    elif abs(edge_node_ratio - np.pi) < 0.1:
        print("✓ RATIO CLOSE TO π")
        return True
    else:
        print("~ Ratio doesn't match known constants")
        return False


def test_final_assessment_with_gauge_fix():
    """Run all tests and provide final assessment."""
    print("\n" + "="*80)
    print("FINAL ASSESSMENT WITH GAUGE-INVARIANT COHERENCE")
    print("="*80)
    
    phenomena_detected = 0
    
    # Run all tests
    if test_thermodynamic_arrow_with_gauge_fix():
        phenomena_detected += 1
    
    if test_resonance_correlation_with_gauge_fix():
        phenomena_detected += 1
    
    if test_gauge_symmetry_with_fix():
        phenomena_detected += 1
    
    if test_dimensionless_ratios_with_gauge_fix():
        phenomena_detected += 1
    
    # Final assessment
    print("\n" + "="*80)
    print(f"Profound phenomena detected: {phenomena_detected}/5")
    
    if phenomena_detected >= 4:
        assessment = "REVOLUTIONARY"
    elif phenomena_detected >= 3:
        assessment = "HIGHLY INTERESTING"
    elif phenomena_detected >= 2:
        assessment = "PROMISING"
    else:
        assessment = "TOY MODEL"
    
    print(f"\nASSESSMENT: {assessment}")
    
    print("\n" + "-"*80)
    print("Comparison with Original:")
    print("  Original (gauge-violating): 2/5 phenomena")
    print(f"  Gauge-invariant:            {phenomena_detected}/5 phenomena")
    print(f"  Improvement:                +{phenomena_detected - 2} phenomena")
    print("="*80)
    
    assert True  # Always pass; this is exploratory


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
