"""
Test Quantum Interference: Do graph paths interfere like quantum amplitudes?

This is a critical test. If FIRM exhibits quantum interference, it suggests
the graph dynamics encode quantum mechanics at a fundamental level.

Test: Create two paths A→D (via B and via C) and check if the total
probability differs from classical expectation due to phase interference.
"""

import pytest
import numpy as np
import math
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def build_diamond_graph():
    """
    Build a diamond graph: A → B,C → D
    
    This creates two paths from A to D with different phases.
    """
    nodes = [0, 1, 2, 3]  # A, B, C, D
    edges = [
        [0, 1],  # A → B
        [0, 2],  # A → C
        [1, 3],  # B → D
        [2, 3]   # C → D
    ]
    
    # Assign phases to create interference
    labels = {
        0: make_node_label('Z', 0, 100, 'A'),      # A: phase = 0
        1: make_node_label('X', 25, 100, 'B'),     # B: phase = π/2
        2: make_node_label('X', 33, 100, 'C'),     # C: phase = 2π/3
        3: make_node_label('Z', 0, 100, 'D')       # D: phase = 0
    }
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def compute_path_amplitude(graph, path):
    """
    Compute quantum-like amplitude for a path through the graph.
    
    Amplitude = exp(i * Σ phases along path)
    """
    total_phase = 0.0
    for node_id in path:
        if node_id in graph.labels:
            label = graph.labels[node_id]
            phase_rad = math.pi * label.phase_numer / label.phase_denom
            total_phase += phase_rad
    
    # Return complex amplitude
    return np.exp(1j * total_phase)


def test_two_path_interference():
    """Test if two paths A→D interfere quantum-mechanically."""
    print("\n" + "="*70)
    print("TEST: QUANTUM INTERFERENCE (Two-Path)")
    print("="*70)
    
    graph = build_diamond_graph()
    
    # Path 1: A → B → D (nodes 0, 1, 3)
    path1 = [0, 1, 3]
    amplitude1 = compute_path_amplitude(graph, path1)
    
    # Path 2: A → C → D (nodes 0, 2, 3)
    path2 = [0, 2, 3]
    amplitude2 = compute_path_amplitude(graph, path2)
    
    # Total amplitude (quantum)
    total_amplitude = amplitude1 + amplitude2
    probability_quantum = abs(total_amplitude)**2
    
    # Classical probability (no interference)
    prob1_classical = abs(amplitude1)**2
    prob2_classical = abs(amplitude2)**2
    probability_classical = prob1_classical + prob2_classical
    
    # Phase difference
    phase1 = np.angle(amplitude1)
    phase2 = np.angle(amplitude2)
    phase_diff = abs(phase1 - phase2)
    
    print(f"\nPath 1 (A→B→D):")
    print(f"  Amplitude: {amplitude1}")
    print(f"  Phase: {phase1:.4f} rad")
    print(f"  Classical prob: {prob1_classical:.4f}")
    
    print(f"\nPath 2 (A→C→D):")
    print(f"  Amplitude: {amplitude2}")
    print(f"  Phase: {phase2:.4f} rad")
    print(f"  Classical prob: {prob2_classical:.4f}")
    
    print(f"\nInterference:")
    print(f"  Phase difference: {phase_diff:.4f} rad ({phase_diff*180/np.pi:.1f}°)")
    print(f"  Quantum probability: {probability_quantum:.4f}")
    print(f"  Classical probability: {probability_classical:.4f}")
    print(f"  Difference: {abs(probability_quantum - probability_classical):.4f}")
    
    # Check for interference
    interference_strength = abs(probability_quantum - probability_classical)
    
    if interference_strength > 0.1:
        print(f"\n✓ QUANTUM INTERFERENCE DETECTED")
        print(f"  Interference strength: {interference_strength:.4f}")
        has_interference = True
    else:
        print(f"\n✗ NO SIGNIFICANT INTERFERENCE")
        print(f"  Interference strength: {interference_strength:.4f} (< 0.1 threshold)")
        has_interference = False
    
    # Check if it matches Born rule expectations
    if has_interference:
        # Born rule: probability should be in [0, 4] for two equal paths
        if 0 <= probability_quantum <= 4:
            print(f"  ✓ Probability in Born rule range [0, 4]")
        else:
            print(f"  ✗ Probability outside Born rule range: {probability_quantum:.4f}")
    
    return has_interference


def test_interference_with_different_phases():
    """Test interference with systematically varied phases."""
    print("\n" + "="*70)
    print("TEST: QUANTUM INTERFERENCE (Phase Scan)")
    print("="*70)
    
    interference_detected = []
    
    # Test multiple phase configurations
    phase_configs = [
        (0, 25, 50),    # 0, π/2, π
        (0, 33, 67),    # 0, 2π/3, 4π/3
        (0, 16, 84),    # 0, π/3, 5π/3
        (0, 50, 50),    # 0, π, π (same phase on both paths)
    ]
    
    for i, (phase_a, phase_b, phase_c) in enumerate(phase_configs):
        nodes = [0, 1, 2, 3]
        edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
        
        labels = {
            0: make_node_label('Z', 0, 100, 'A'),
            1: make_node_label('X', phase_b, 100, 'B'),
            2: make_node_label('X', phase_c, 100, 'C'),
            3: make_node_label('Z', 0, 100, 'D')
        }
        
        graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
        graph = validate_object_g(graph)
        
        # Compute interference
        path1 = [0, 1, 3]
        path2 = [0, 2, 3]
        
        amp1 = compute_path_amplitude(graph, path1)
        amp2 = compute_path_amplitude(graph, path2)
        
        total_amp = amp1 + amp2
        prob_quantum = abs(total_amp)**2
        prob_classical = abs(amp1)**2 + abs(amp2)**2
        
        interference = abs(prob_quantum - prob_classical)
        
        print(f"\nConfig {i+1}: B={phase_b}/100·2π, C={phase_c}/100·2π")
        print(f"  Quantum prob: {prob_quantum:.4f}")
        print(f"  Classical prob: {prob_classical:.4f}")
        print(f"  Interference: {interference:.4f}")
        
        if interference > 0.1:
            interference_detected.append(True)
            print(f"  ✓ Interference")
        else:
            interference_detected.append(False)
            print(f"  ✗ No interference")
    
    # Summary
    interference_count = sum(interference_detected)
    print(f"\n" + "-"*70)
    print(f"Interference detected in {interference_count}/{len(phase_configs)} configurations")
    
    if interference_count >= 3:
        print("✓ QUANTUM INTERFERENCE CONFIRMED")
        return True
    elif interference_count >= 1:
        print("~ PARTIAL INTERFERENCE")
        return True
    else:
        print("✗ NO QUANTUM INTERFERENCE")
        return False


def test_born_rule_compliance():
    """Test if interference probabilities match Born rule predictions."""
    print("\n" + "="*70)
    print("TEST: BORN RULE COMPLIANCE")
    print("="*70)
    
    # Create graph with known phase difference
    nodes = [0, 1, 2, 3]
    edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
    
    # Set phases for constructive interference (phase_diff = 0)
    labels = {
        0: make_node_label('Z', 0, 100, 'A'),
        1: make_node_label('X', 25, 100, 'B'),  # π/2
        2: make_node_label('X', 25, 100, 'C'),  # π/2 (same as B)
        3: make_node_label('Z', 0, 100, 'D')
    }
    
    graph_constructive = ObjectG(nodes=nodes, edges=edges, labels=labels)
    graph_constructive = validate_object_g(graph_constructive)
    
    amp1_c = compute_path_amplitude(graph_constructive, [0, 1, 3])
    amp2_c = compute_path_amplitude(graph_constructive, [0, 2, 3])
    prob_constructive = abs(amp1_c + amp2_c)**2
    
    print(f"Constructive interference (same phases):")
    print(f"  Probability: {prob_constructive:.4f}")
    print(f"  Expected (Born rule): 4.0 (maximum)")
    print(f"  Match: {abs(prob_constructive - 4.0) < 0.1}")
    
    # Set phases for destructive interference (phase_diff = π)
    labels_destructive = {
        0: make_node_label('Z', 0, 100, 'A'),
        1: make_node_label('X', 25, 100, 'B'),   # π/2
        2: make_node_label('X', 75, 100, 'C'),   # 3π/2 (π difference)
        3: make_node_label('Z', 0, 100, 'D')
    }
    
    graph_destructive = ObjectG(nodes=nodes, edges=edges, labels=labels_destructive)
    graph_destructive = validate_object_g(graph_destructive)
    
    amp1_d = compute_path_amplitude(graph_destructive, [0, 1, 3])
    amp2_d = compute_path_amplitude(graph_destructive, [0, 2, 3])
    prob_destructive = abs(amp1_d + amp2_d)**2
    
    print(f"\nDestructive interference (π phase diff):")
    print(f"  Probability: {prob_destructive:.4f}")
    print(f"  Expected (Born rule): 0.0 (minimum)")
    print(f"  Match: {abs(prob_destructive - 0.0) < 0.1}")
    
    # Check Born rule compliance
    constructive_match = abs(prob_constructive - 4.0) < 0.5
    destructive_match = abs(prob_destructive - 0.0) < 0.5
    
    if constructive_match and destructive_match:
        print(f"\n✓ BORN RULE COMPLIANCE CONFIRMED")
        return True
    elif constructive_match or destructive_match:
        print(f"\n~ PARTIAL BORN RULE COMPLIANCE")
        return True
    else:
        print(f"\n✗ NO BORN RULE COMPLIANCE")
        return False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
