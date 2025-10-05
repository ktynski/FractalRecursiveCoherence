"""
Test Gauge Invariance: Verify U(1) phase symmetry in coherence.

Theory requirement (from coherence.py line 8):
"invariances: graph isomorphism and phase group equivalence"

This test verifies that the gauge-invariant implementation satisfies
this requirement, while documenting that the original implementation
violates it.
"""

import pytest
import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.coherence_gauge_invariant import (
    compute_coherence_gauge_invariant,
    verify_gauge_invariance,
    compare_implementations
)


def build_test_graph(num_nodes=8):
    """Build a test graph with cycles."""
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]  # Ring
    
    # Add cross-links
    edges.append([0, num_nodes // 2])
    edges.append([num_nodes // 4, 3 * num_nodes // 4])
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        phase_denom = 100
        labels[i] = make_node_label(kind, phase_numer, phase_denom, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def test_original_violates_gauge_invariance():
    """Test that original implementation violates U(1) gauge symmetry."""
    print("\n" + "="*70)
    print("TEST: Original Coherence Implementation (Gauge Violation)")
    print("="*70)
    
    graph = build_test_graph(num_nodes=8)
    
    # Measure before shift
    coh_before = compute_coherence(graph)
    
    # Apply global phase shift
    shift = 50  # π/2 shift
    shifted_labels = {}
    for node_id, label in graph.labels.items():
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
    
    # Measure after shift
    coh_after = compute_coherence(shifted_graph)
    
    relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
    
    print(f"\nOriginal Implementation:")
    print(f"  C(G) before shift: {coh_before:.6f}")
    print(f"  C(G) after shift:  {coh_after:.6f}")
    print(f"  Relative change:   {relative_change:.6f}")
    print(f"  Violates gauge invariance: {relative_change > 0.01}")
    
    # Document violation
    assert relative_change > 0.01, "Original should violate gauge invariance"
    print("\n✗ CONFIRMED: Original implementation violates U(1) gauge symmetry")


def test_gauge_invariant_implementation():
    """Test that gauge-invariant implementation satisfies U(1) symmetry."""
    print("\n" + "="*70)
    print("TEST: Gauge-Invariant Coherence Implementation")
    print("="*70)
    
    graph = build_test_graph(num_nodes=8)
    
    # Test with multiple shift amounts
    shifts = [10, 25, 50, 75, 90]
    max_violation = 0.0
    
    print("\nTesting multiple phase shifts:")
    for shift in shifts:
        result = verify_gauge_invariance(graph, shift_amount=shift)
        
        print(f"\n  Shift = {shift}/100 * 2π:")
        print(f"    C(G) before: {result['coherence_before']:.6f}")
        print(f"    C(G) after:  {result['coherence_after']:.6f}")
        print(f"    Relative change: {result['relative_change']:.6f}")
        print(f"    Gauge invariant: {result['is_gauge_invariant']}")
        
        max_violation = max(max_violation, result['relative_change'])
        
        # Assert gauge invariance
        assert result['is_gauge_invariant'], f"Gauge invariance violated at shift={shift}"
    
    print(f"\n✓ PASSED: Maximum violation across all shifts: {max_violation:.6f}")
    print("✓ Gauge-invariant implementation satisfies U(1) symmetry")


def test_comparison_with_original():
    """Compare original and gauge-invariant implementations."""
    print("\n" + "="*70)
    print("TEST: Comparison of Implementations")
    print("="*70)
    
    graph = build_test_graph(num_nodes=10)
    
    result = compare_implementations(graph)
    
    print(f"\nCoherence Values:")
    print(f"  Original:        {result['original_coherence']:.6f}")
    print(f"  Gauge-invariant: {result['gauge_invariant_coherence']:.6f}")
    print(f"  Difference:      {result['difference']:.6f}")
    
    print(f"\nGauge Invariance Test (50/100 * 2π shift):")
    print(f"  Original violation:        {result['original_gauge_violation']:.6f}")
    print(f"  Gauge-invariant violation: {result['gauge_invariant_violation']:.6f}")
    
    # Original should violate, new should not
    assert result['original_gauge_violation'] > 0.01, "Original should violate"
    assert result['gauge_invariant_violation'] < 0.02, "New should not violate (< 2%)"
    
    print("\n✓ Gauge-invariant implementation is theory-compliant")


def test_gauge_invariance_with_different_topologies():
    """Test gauge invariance across different graph topologies."""
    print("\n" + "="*70)
    print("TEST: Gauge Invariance Across Topologies")
    print("="*70)
    
    topologies = {
        "Ring": lambda n: [[i, (i+1) % n] for i in range(n)],
        "Star": lambda n: [[0, i] for i in range(1, n)],
        "Complete": lambda n: [[i, j] for i in range(n) for j in range(i+1, n)]
    }
    
    for topo_name, edge_func in topologies.items():
        num_nodes = 6
        nodes = list(range(num_nodes))
        edges = edge_func(num_nodes)
        
        labels = {}
        for i in range(num_nodes):
            kind = 'Z' if i % 2 == 0 else 'X'
            phase_numer = (i * 17) % 100
            phase_denom = 100
            labels[i] = make_node_label(kind, phase_numer, phase_denom, f'n{i}')
        
        graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
        graph = validate_object_g(graph)
        
        result = verify_gauge_invariance(graph, shift_amount=50)
        
        print(f"\n{topo_name} topology:")
        print(f"  Nodes: {num_nodes}, Edges: {len(edges)}")
        print(f"  Gauge invariant: {result['is_gauge_invariant']}")
        print(f"  Violation: {result['relative_change']:.6f}")
        
        assert result['is_gauge_invariant'], f"Failed for {topo_name} topology"
    
    print("\n✓ Gauge invariance holds across all topologies")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
