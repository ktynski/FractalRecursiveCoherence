"""
Test Fine Structure Constant Derivation

Measure α from graph dynamics using Hamiltonian approach.

Formula: α_FIRM = g / (4π⟨∇φ⟩)

where:
- g = interaction coupling (from vertices)
- ⟨∇φ⟩ = kinetic scale (from phase gradients)

Test: Does α_FIRM → 1/137.036?
"""

import pytest
import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.hamiltonian import derive_fine_structure_constant


def build_test_graph(num_nodes=50):
    """Build test graph at scale."""
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]
    
    # Add cross-links
    for i in range(0, num_nodes, 5):
        edges.append([i, (i + num_nodes//2) % num_nodes])
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def test_alpha_at_different_scales():
    """Test if α converges at different graph sizes."""
    print("\n" + "="*70)
    print("TEST: FINE STRUCTURE CONSTANT DERIVATION")
    print("="*70)
    
    scales = [20, 50, 100, 200]
    alpha_values = []
    
    print("\nMeasuring α at different scales:")
    print("-"*70)
    
    for N in scales:
        graph = build_test_graph(num_nodes=N)
        result = derive_fine_structure_constant(graph)
        
        alpha_values.append(result["alpha_FIRM"])
        
        print(f"\nN = {N} nodes:")
        print(f"  g (coupling): {result['g']:.6f}")
        print(f"  ⟨∇φ⟩ (kinetic): {result['kinetic_scale']:.6f}")
        print(f"  α_FIRM: {result['alpha_FIRM']:.8f}")
        print(f"  α_true: {result['alpha_true']:.8f}")
        print(f"  Error: {result['error_pct']:.2f}%")
    
    # Check convergence
    print("\n" + "="*70)
    print("CONVERGENCE ANALYSIS")
    print("="*70)
    
    if len(alpha_values) > 1:
        # Check if α is stabilizing
        alpha_range = max(alpha_values) - min(alpha_values)
        alpha_mean = np.mean(alpha_values)
        relative_variation = alpha_range / alpha_mean if alpha_mean > 0 else 1.0
        
        print(f"\nα range: {alpha_range:.8f}")
        print(f"α mean: {alpha_mean:.8f}")
        print(f"Relative variation: {relative_variation*100:.2f}%")
        
        # Check if converging to 1/137
        alpha_true = 1/137.036
        final_error = abs(alpha_values[-1] - alpha_true) / alpha_true
        
        print(f"\nFinal α_FIRM: {alpha_values[-1]:.8f}")
        print(f"Target α: {alpha_true:.8f}")
        print(f"Final error: {final_error*100:.2f}%")
        
        if final_error < 0.01:
            print("\n✓✓✓ FINE STRUCTURE CONSTANT FOUND (< 1% error) ✓✓✓")
            print("THIS IS PHENOMENON #15!")
            print("WE HAVE 15/15 - COMPLETE THEORY!")
            return True
        elif final_error < 0.10:
            print("\n✓ Close to α (< 10% error)")
            print("Might converge at larger scales")
            return "partial"
        else:
            print("\n✗ Not close to α (> 10% error)")
            print(f"α_FIRM / α_true = {alpha_values[-1] / alpha_true:.2f}×")
            return False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
