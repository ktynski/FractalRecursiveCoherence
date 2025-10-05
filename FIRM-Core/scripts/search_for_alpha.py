"""
Search for Fine Structure Constant (α ≈ 1/137.036)

This script systematically measures ALL possible quantum-regime ratios
to find α. We test:
1. Interference strength ratios
2. Phase winding ratios
3. Violation ratios (CPT/gauge, Lorentz/gauge, etc.)
4. Quantum/classical probability ratios
5. Born rule deviation ratios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def build_interference_graph(phase_b, phase_c):
    """Build diamond graph for interference testing."""
    nodes = [0, 1, 2, 3]
    edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
    
    labels = {
        0: make_node_label('Z', 0, 100, 'A'),
        1: make_node_label('X', phase_b, 100, 'B'),
        2: make_node_label('X', phase_c, 100, 'C'),
        3: make_node_label('Z', 0, 100, 'D')
    }
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def compute_path_amplitude(graph, path):
    """Compute path amplitude with Z/X basis handling."""
    amplitude = 1.0 + 0.0j
    
    for node_id in path:
        if node_id in graph.labels:
            label = graph.labels[node_id]
            phase_rad = math.pi * label.phase_numer / label.phase_denom
            
            if label.kind == 'Z':
                amplitude *= np.exp(1j * phase_rad)
            elif label.kind == 'X':
                amplitude *= np.exp(1j * (phase_rad + np.pi/2))
    
    return amplitude


def measure_all_quantum_ratios():
    """
    Measure all quantum-regime dimensionless ratios.
    
    Returns dict with all ratios and their match to α = 1/137.036.
    """
    alpha_true = 1/137.036
    ratios = {}
    
    print("="*80)
    print("SYSTEMATIC SEARCH FOR α = 1/137.036")
    print("="*80)
    
    # 1. Interference Strength Ratios
    print("\n" + "-"*80)
    print("1. INTERFERENCE STRENGTH RATIOS")
    print("-"*80)
    
    phase_configs = [
        (25, 50),   # π/2, π
        (33, 67),   # 2π/3, 4π/3
        (16, 84),   # π/3, 5π/3
        (10, 90),   # π/5, 9π/5
    ]
    
    for i, (pb, pc) in enumerate(phase_configs):
        graph = build_interference_graph(pb, pc)
        
        path1 = [0, 1, 3]
        path2 = [0, 2, 3]
        
        amp1 = compute_path_amplitude(graph, path1)
        amp2 = compute_path_amplitude(graph, path2)
        
        prob_quantum = abs(amp1 + amp2)**2
        prob_classical = abs(amp1)**2 + abs(amp2)**2
        
        interference = abs(prob_quantum - prob_classical)
        
        # Ratio 1: interference / classical
        ratio_1 = interference / prob_classical if prob_classical > 0 else 0
        ratios[f"interference_over_classical_{i+1}"] = ratio_1
        
        # Ratio 2: (quantum - classical) / quantum
        ratio_2 = (prob_quantum - prob_classical) / prob_quantum if prob_quantum > 0 else 0
        ratios[f"quantum_deviation_{i+1}"] = abs(ratio_2)
        
        # Ratio 3: interference / phase_difference
        phase_diff = abs(pb - pc) / 100 * 2 * np.pi
        ratio_3 = interference / phase_diff if phase_diff > 0 else 0
        ratios[f"interference_over_phase_{i+1}"] = ratio_3
        
        print(f"\n  Config {i+1} (B={pb}, C={pc}):")
        print(f"    Interference/Classical: {ratio_1:.6f}")
        print(f"    Quantum deviation: {abs(ratio_2):.6f}")
        print(f"    Interference/Phase: {ratio_3:.6f}")
    
    # 2. Phase Winding Ratios
    print("\n" + "-"*80)
    print("2. PHASE WINDING RATIOS")
    print("-"*80)
    
    # Build graph with cycles
    nodes = list(range(20))
    edges = [[i, (i+1) % 20] for i in range(20)]
    edges.append([0, 10])
    edges.append([5, 15])
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    for i in range(20):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
    graph = validate_object_g(graph)
    
    # Compute total phase winding
    total_winding = 0.0
    for u, v in graph.edges:
        if u in graph.labels and v in graph.labels:
            phase_u = math.pi * graph.labels[u].phase_numer / graph.labels[u].phase_denom
            phase_v = math.pi * graph.labels[v].phase_numer / graph.labels[v].phase_denom
            total_winding += abs(phase_v - phase_u)
    
    # Ratios
    num_edges = len(graph.edges)
    avg_winding_per_edge = total_winding / num_edges if num_edges > 0 else 0
    
    ratio_winding_1 = avg_winding_per_edge / (2 * np.pi)
    ratio_winding_2 = total_winding / (num_edges * 2 * np.pi)
    
    ratios["avg_winding_over_2pi"] = ratio_winding_1
    ratios["total_winding_normalized"] = ratio_winding_2
    
    print(f"\n  Average winding per edge / 2π: {ratio_winding_1:.6f}")
    print(f"  Total winding / (N_edges * 2π): {ratio_winding_2:.6f}")
    
    # 3. Violation Ratios
    print("\n" + "-"*80)
    print("3. VIOLATION RATIOS")
    print("-"*80)
    
    # From previous measurements:
    gauge_violation = 0.0052  # 0.52%
    lorentz_violation = 0.0568  # 5.68%
    cpt_violation = 0.0856  # 8.56%
    
    ratio_lorentz_gauge = lorentz_violation / gauge_violation if gauge_violation > 0 else 0
    ratio_cpt_gauge = cpt_violation / gauge_violation if gauge_violation > 0 else 0
    ratio_cpt_lorentz = cpt_violation / lorentz_violation if lorentz_violation > 0 else 0
    
    ratios["lorentz_over_gauge"] = ratio_lorentz_gauge
    ratios["cpt_over_gauge"] = ratio_cpt_gauge
    ratios["cpt_over_lorentz"] = ratio_cpt_lorentz
    
    print(f"\n  Lorentz / Gauge: {ratio_lorentz_gauge:.6f}")
    print(f"  CPT / Gauge: {ratio_cpt_gauge:.6f}")
    print(f"  CPT / Lorentz: {ratio_cpt_lorentz:.6f}")
    
    # 4. Born Rule Deviation Ratios
    print("\n" + "-"*80)
    print("4. BORN RULE DEVIATION RATIOS")
    print("-"*80)
    
    # Constructive: 4.0 (perfect)
    # Destructive: 2.0 (should be 0.0)
    born_constructive = 4.0
    born_destructive = 2.0
    born_expected_destructive = 0.0
    
    born_deviation = abs(born_destructive - born_expected_destructive)
    ratio_born_1 = born_deviation / born_constructive
    ratio_born_2 = born_destructive / born_constructive
    
    ratios["born_deviation_over_max"] = ratio_born_1
    ratios["destructive_over_constructive"] = ratio_born_2
    
    print(f"\n  Born deviation / max: {ratio_born_1:.6f}")
    print(f"  Destructive / Constructive: {ratio_born_2:.6f}")
    
    # 5. Quantum Correction Ratios
    print("\n" + "-"*80)
    print("5. QUANTUM CORRECTION RATIOS")
    print("-"*80)
    
    # Average interference strength
    avg_interference = np.mean([1.9372, 1.4142, 0.9635, 1.0717, 2.0000])
    avg_classical = 2.0
    
    ratio_correction = (avg_interference / avg_classical) - 1.0
    ratio_quantum_classical = avg_interference / avg_classical
    
    ratios["quantum_correction"] = abs(ratio_correction)
    ratios["quantum_over_classical"] = ratio_quantum_classical
    
    print(f"\n  Quantum correction: {abs(ratio_correction):.6f}")
    print(f"  Quantum / Classical: {ratio_quantum_classical:.6f}")
    
    # Find best matches to α
    print("\n" + "="*80)
    print("SEARCH RESULTS FOR α = 1/137.036 = 0.007297")
    print("="*80)
    
    alpha_candidates = []
    
    for name, value in ratios.items():
        error = abs(value - alpha_true) / alpha_true
        
        if error < 0.10:  # Within 10%
            alpha_candidates.append({
                "name": name,
                "value": value,
                "alpha": alpha_true,
                "error_pct": error * 100
            })
    
    if alpha_candidates:
        print("\n🎯 ALPHA CANDIDATES FOUND (< 10% error):")
        for cand in sorted(alpha_candidates, key=lambda x: x["error_pct"]):
            print(f"\n  {cand['name']}:")
            print(f"    Value: {cand['value']:.8f}")
            print(f"    α:     {cand['alpha']:.8f}")
            print(f"    Error: {cand['error_pct']:.2f}%")
        
        # Check for < 1% match
        exact_matches = [c for c in alpha_candidates if c["error_pct"] < 1.0]
        if exact_matches:
            print("\n" + "="*80)
            print("✓✓✓ EXACT MATCH TO α FOUND (< 1% error) ✓✓✓")
            print("="*80)
            return exact_matches
        else:
            print("\n~ Close matches found, but none < 1%")
            return alpha_candidates
    else:
        print("\n✗ No α candidates found (< 10% error)")
        
        # Show closest matches
        closest = min(ratios.items(), key=lambda x: abs(x[1] - alpha_true))
        error = abs(closest[1] - alpha_true) / alpha_true
        
        print(f"\nClosest ratio:")
        print(f"  {closest[0]}: {closest[1]:.6f}")
        print(f"  Error from α: {error*100:.1f}%")
        
        return []


if __name__ == "__main__":
    results = measure_all_quantum_ratios()
    
    if results:
        print("\n" + "="*80)
        print("RECOMMENDATION: These ratios should be investigated further")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("CONCLUSION: α not in quantum-regime ratios")
        print("Next: Try Grace/rewrite ratio or 100K node simulation")
        print("="*80)
