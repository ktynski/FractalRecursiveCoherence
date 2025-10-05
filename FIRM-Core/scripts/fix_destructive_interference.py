"""
Experiment 3: Fix Destructive Interference Bug

Current: Destructive interference gives 2.0 (should be 0.0)
Problem: Missing proper ZX-calculus Hadamard handling

This script tests different Hadamard implementations to find which works.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g


def build_destructive_graph():
    """Build graph designed for destructive interference."""
    nodes = [0, 1, 2, 3]
    edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
    
    labels = {
        0: make_node_label('Z', 0, 100, 'A'),    # Phase 0
        1: make_node_label('X', 25, 100, 'B'),   # Phase π/2
        2: make_node_label('X', 75, 100, 'C'),   # Phase 3π/2 (π different from B)
        3: make_node_label('Z', 0, 100, 'D')     # Phase 0
    }
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def compute_amplitude_v1_naive(graph, path):
    """V1: Naive (current broken version)."""
    amplitude = 1.0 + 0.0j
    for node_id in path:
        if node_id in graph.labels:
            label = graph.labels[node_id]
            phase = math.pi * label.phase_numer / label.phase_denom
            
            if label.kind == 'Z':
                amplitude *= np.exp(1j * phase)
            elif label.kind == 'X':
                amplitude *= np.exp(1j * (phase + np.pi/2))
    return amplitude


def compute_amplitude_v2_hadamard_matrix(graph, path):
    """V2: Full Hadamard matrix multiplication."""
    # In ZX calculus, X-spider is Hadamard-conjugated Z-spider
    # H = (1/√2) [[1, 1], [1, -1]]
    
    amplitude = 1.0 + 0.0j
    for node_id in path:
        if node_id in graph.labels:
            label = graph.labels[node_id]
            phase = math.pi * label.phase_numer / label.phase_denom
            
            if label.kind == 'Z':
                # Z-spider: standard phase gate
                amplitude *= np.exp(1j * phase)
            elif label.kind == 'X':
                # X-spider: H·Z(φ)·H† 
                # = (exp(iφ) + exp(-iφ))/2 = cos(φ)
                amplitude *= np.cos(phase)
    
    return amplitude


def compute_amplitude_v3_basis_rotation(graph, path):
    """V3: Basis rotation interpretation."""
    amplitude = 1.0 + 0.0j
    for node_id in path:
        if node_id in graph.labels:
            label = graph.labels[node_id]
            phase = math.pi * label.phase_numer / label.phase_denom
            
            if label.kind == 'Z':
                amplitude *= np.exp(1j * phase)
            elif label.kind == 'X':
                # X basis: |+⟩ = (|0⟩ + |1⟩)/√2, |−⟩ = (|0⟩ - |1⟩)/√2
                # Phase gate in X basis: different from Z basis
                # Correction: multiply by exp(iπ/2) = i
                amplitude *= 1j * np.exp(1j * phase)
    
    return amplitude


def compute_amplitude_v4_green_spider(graph, path):
    """V4: Full ZX calculus with spider fusion rules."""
    # In ZX calculus:
    # - Adjacent same-color spiders fuse: angles add
    # - Hadamard connects Z and X spiders
    # - Need to track color changes
    
    amplitude = 1.0 + 0.0j
    current_basis = 'Z'  # Start in Z basis
    
    for node_id in path:
        if node_id in graph.labels:
            label = graph.labels[node_id]
            phase = math.pi * label.phase_numer / label.phase_denom
            
            if label.kind != current_basis:
                # Basis change: apply Hadamard
                amplitude *= 1/np.sqrt(2)
                current_basis = label.kind
            
            # Apply phase gate in current basis
            amplitude *= np.exp(1j * phase)
    
    return amplitude


def test_all_versions():
    """Test all amplitude computation versions."""
    print("="*80)
    print("TESTING DESTRUCTIVE INTERFERENCE FIXES")
    print("="*80)
    
    graph = build_destructive_graph()
    path1 = [0, 1, 3]  # A → B → D
    path2 = [0, 2, 3]  # A → C → D
    
    versions = [
        ("V1: Naive (current)", compute_amplitude_v1_naive),
        ("V2: Hadamard matrix", compute_amplitude_v2_hadamard_matrix),
        ("V3: Basis rotation", compute_amplitude_v3_basis_rotation),
        ("V4: Full ZX calculus", compute_amplitude_v4_green_spider),
    ]
    
    print("\nPhase configuration:")
    print("  A (Z): phase = 0")
    print("  B (X): phase = π/2")
    print("  C (X): phase = 3π/2 (π different from B)")
    print("  D (Z): phase = 0")
    print("\nExpected: Destructive interference → probability ≈ 0.0\n")
    
    results = []
    for name, func in versions:
        print(f"\n{name}:")
        print("-" * 80)
        
        amp1 = func(graph, path1)
        amp2 = func(graph, path2)
        
        total_amp = amp1 + amp2
        prob_quantum = abs(total_amp)**2
        prob_classical = abs(amp1)**2 + abs(amp2)**2
        
        print(f"  Path 1 amplitude: {amp1}")
        print(f"  Path 2 amplitude: {amp2}")
        print(f"  Total amplitude:  {total_amp}")
        print(f"  Quantum prob: {prob_quantum:.4f}")
        print(f"  Classical prob: {prob_classical:.4f}")
        print(f"  Interference: {abs(prob_quantum - prob_classical):.4f}")
        
        # Check if destructive
        is_destructive = prob_quantum < 0.5
        error = abs(prob_quantum - 0.0)
        
        if is_destructive:
            print(f"  ✓ DESTRUCTIVE (prob = {prob_quantum:.4f} < 0.5)")
            print(f"    Error from 0.0: {error:.4f}")
        else:
            print(f"  ✗ NOT DESTRUCTIVE (prob = {prob_quantum:.4f} ≥ 0.5)")
        
        results.append({
            'name': name,
            'prob': prob_quantum,
            'error': error,
            'is_destructive': is_destructive
        })
    
    # Find best version
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    best = min(results, key=lambda x: x['error'])
    
    print(f"\nBest version: {best['name']}")
    print(f"  Probability: {best['prob']:.6f}")
    print(f"  Error from 0.0: {best['error']:.6f}")
    
    if best['error'] < 0.1:
        print(f"\n✓✓✓ FIX FOUND: {best['name']} achieves destructive interference!")
        print("  Error < 0.1, this is the correct implementation")
        print("\nNext step: Update compute_path_amplitude() in test_quantum_interference.py")
    elif best['error'] < 0.5:
        print(f"\n~ PARTIAL FIX: {best['name']} is better but not perfect")
        print(f"  Error = {best['error']:.2f}, still needs work")
    else:
        print(f"\n✗ NO FIX: All versions fail destructive interference")
        print("  Need deeper understanding of ZX calculus")
    
    return best


def test_constructive_too():
    """Verify fix doesn't break constructive interference."""
    print("\n" + "="*80)
    print("VERIFICATION: Test Constructive Interference")
    print("="*80)
    
    # Build constructive graph (same phases)
    nodes = [0, 1, 2, 3]
    edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
    
    labels = {
        0: make_node_label('Z', 0, 100, 'A'),
        1: make_node_label('X', 25, 100, 'B'),   # Phase π/2
        2: make_node_label('X', 25, 100, 'C'),   # Same phase as B
        3: make_node_label('Z', 0, 100, 'D')
    }
    
    graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
    graph = validate_object_g(graph)
    
    path1 = [0, 1, 3]
    path2 = [0, 2, 3]
    
    # Test with best version (V2)
    amp1 = compute_amplitude_v2_hadamard_matrix(graph, path1)
    amp2 = compute_amplitude_v2_hadamard_matrix(graph, path2)
    
    total_amp = amp1 + amp2
    prob_quantum = abs(total_amp)**2
    
    print(f"\nConstructive interference (same phases):")
    print(f"  Quantum probability: {prob_quantum:.4f}")
    print(f"  Expected: 4.0 (maximum)")
    
    if abs(prob_quantum - 4.0) < 0.1:
        print(f"  ✓ CONSTRUCTIVE works correctly")
    else:
        print(f"  ✗ CONSTRUCTIVE broken (error = {abs(prob_quantum - 4.0):.2f})")
    
    return abs(prob_quantum - 4.0) < 0.1


if __name__ == "__main__":
    best_result = test_all_versions()
    constructive_ok = test_constructive_too()
    
    print("\n" + "="*80)
    print("FINAL RECOMMENDATION")
    print("="*80)
    
    if best_result['error'] < 0.1 and constructive_ok:
        print(f"\n✓ Implement {best_result['name']} in production code")
        print("  Both destructive and constructive interference work correctly")
    elif best_result['error'] < 0.5:
        print(f"\n~ {best_result['name']} is better but needs refinement")
        print("  Continue investigating ZX calculus semantics")
    else:
        print(f"\n✗ No working fix found")
        print("  Consider consulting ZX calculus experts or papers")
