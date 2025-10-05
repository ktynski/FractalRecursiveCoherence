"""
Test Emergent Quantization

Measure coherence spectrum (cycle energy levels) to check for quantization.

In QM: Energy levels are discrete and evenly spaced
In FIRM: Cycle coherences might be quantized
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from collections import Counter
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence import compute_cycle_basis_signature
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def compute_cycle_coherence(graph, cycle):
    """Compute coherence for a single cycle."""
    phase_diffs = []
    
    for i in range(len(cycle)):
        node_a = cycle[i]
        node_b = cycle[(i + 1) % len(cycle)]
        
        if node_a in graph.labels and node_b in graph.labels:
            lbl_a = graph.labels[node_a]
            lbl_b = graph.labels[node_b]
            
            phase_a = math.pi * lbl_a.phase_numer / lbl_a.phase_denom
            phase_b = math.pi * lbl_b.phase_numer / lbl_b.phase_denom
            phase_diff = (phase_b - phase_a) % (2 * math.pi)
            
            if phase_diff > math.pi:
                phase_diff -= 2 * math.pi
            
            phase_diffs.append(phase_diff)
    
    if not phase_diffs:
        return 0.0
    
    # Cycle coherence
    total_winding = sum(phase_diffs) % (2 * math.pi)
    if total_winding > math.pi:
        total_winding -= 2 * math.pi
    
    winding_coherence = 1.0 / (1.0 + abs(total_winding))
    
    n = len(phase_diffs)
    mean_diff = sum(phase_diffs) / n
    variance = sum((d - mean_diff) ** 2 for d in phase_diffs) / n
    phase_harmony = 1.0 / (1.0 + variance)
    
    return winding_coherence + phase_harmony


def test_coherence_spectrum():
    """Test if cycle coherences are quantized."""
    print("="*80)
    print("EMERGENT QUANTIZATION TEST (Coherence Spectrum)")
    print("="*80)
    
    # Build large graph with many cycles
    nodes = list(range(50))
    edges = [[i, (i+1) % 50] for i in range(50)]  # Ring
    
    # Add cross-links to create diverse cycles
    for i in range(0, 50, 5):
        edges.append([i, (i + 25) % 50])
    for i in range(0, 50, 7):
        edges.append([i, (i + 17) % 50])
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(50):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
    graph = validate_object_g(graph)
    
    # Find cycles
    cycles = compute_cycle_basis_signature(graph)
    
    print(f"\nGraph structure:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"  Cycles: {len(cycles)}")
    
    # Compute coherence for each cycle
    cycle_coherences = []
    for cycle in cycles:
        coh = compute_cycle_coherence(graph, cycle)
        cycle_coherences.append(coh)
    
    if not cycle_coherences:
        print("\n✗ No cycles to analyze")
        return False
    
    print(f"\nCoherence spectrum:")
    print(f"  Min: {min(cycle_coherences):.4f}")
    print(f"  Max: {max(cycle_coherences):.4f}")
    print(f"  Mean: {np.mean(cycle_coherences):.4f}")
    print(f"  Std: {np.std(cycle_coherences):.4f}")
    
    # Check for quantization (discrete peaks)
    hist, bin_edges = np.histogram(cycle_coherences, bins=15)
    
    # Quantization signature: high peaks with low valleys
    peak_threshold = np.mean(hist) + 0.5 * np.std(hist)
    num_peaks = sum(1 for h in hist if h > peak_threshold)
    
    print(f"\nHistogram analysis:")
    print(f"  Bins: 15")
    print(f"  Peaks detected: {num_peaks}")
    print(f"  Mean count: {np.mean(hist):.2f}")
    
    # Check for evenly-spaced levels
    if num_peaks >= 3:
        # Find peak positions
        peak_indices = [i for i, h in enumerate(hist) if h > peak_threshold]
        peak_positions = [bin_edges[i] for i in peak_indices]
        
        if len(peak_positions) > 1:
            # Measure spacing
            spacings = [peak_positions[i+1] - peak_positions[i] 
                       for i in range(len(peak_positions)-1)]
            
            mean_spacing = np.mean(spacings)
            spacing_std = np.std(spacings)
            spacing_uniformity = spacing_std / mean_spacing if mean_spacing > 0 else 1.0
            
            print(f"\nPeak spacing:")
            print(f"  Mean: {mean_spacing:.4f}")
            print(f"  Std: {spacing_std:.4f}")
            print(f"  Uniformity: {1 - spacing_uniformity:.2f} (1.0 = perfect)")
            
            # Quantization if peaks are evenly spaced
            if spacing_uniformity < 0.3:
                print("\n✓ EMERGENT QUANTIZATION (evenly-spaced levels)")
                return True
            else:
                print("\n~ Peaks present but not evenly spaced")
                return False
    
    print("\n✗ No clear quantization (< 3 peaks)")
    return False


if __name__ == "__main__":
    has_quantization = test_coherence_spectrum()
    
    print("\n" + "="*80)
    if has_quantization:
        print("This is phenomenon #14!")
    else:
        print("Quantization not detected")
        print("Likely requires: Hamiltonian operator (theory extension)")
    print("="*80)
