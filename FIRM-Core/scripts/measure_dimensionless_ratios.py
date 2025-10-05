"""
Measure All Dimensionless Ratios: Search for fundamental constants.

This script measures every possible dimensionless ratio in the evolved graph
and checks for convergence to known physical constants:
- α (fine structure) ≈ 1/137.036
- φ (golden ratio) ≈ 1.618
- π ≈ 3.14159
- e ≈ 2.71828
- Mass ratios (m_μ/m_e ≈ 206.77, etc.)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import numpy as np
from collections import Counter
from FIRM_dsl.core import ObjectG, validate_object_g
from FIRM_dsl.coherence import compute_cycle_basis_signature


def measure_all_ratios(graph: ObjectG, grace_events: int, total_rewrites: int) -> dict:
    """
    Measure all dimensionless ratios in the graph.
    
    Returns dict with all ratios and their distances to known constants.
    """
    ratios = {}
    
    # Known constants
    constants = {
        "alpha": 1/137.036,  # Fine structure constant
        "phi": (1 + np.sqrt(5)) / 2,  # Golden ratio
        "pi": np.pi,
        "e": np.e,
        "sqrt2": np.sqrt(2),
        "sqrt3": np.sqrt(3),
        "mass_ratio_muon_electron": 206.768,
        "mass_ratio_tau_electron": 3477.23,
        "mass_ratio_proton_electron": 1836.15
    }
    
    # 1. Edge/Node ratio
    num_nodes = len(graph.nodes)
    num_edges = len(graph.edges)
    if num_nodes > 0:
        ratios["edge_node"] = num_edges / num_nodes
    
    # 2. Grace/Rewrite ratio
    if total_rewrites > 0:
        ratios["grace_rewrite"] = grace_events / total_rewrites
    
    # 3. Cycle-based ratios
    cycles = compute_cycle_basis_signature(graph)
    if cycles:
        cycle_lengths = [len(c) for c in cycles]
        
        # Longest / Mean
        if len(cycle_lengths) > 1:
            ratios["longest_cycle_over_mean"] = max(cycle_lengths) / np.mean(cycle_lengths)
        
        # Cycle length distribution
        length_counts = Counter(cycle_lengths)
        if len(length_counts) > 1:
            sorted_lengths = sorted(length_counts.keys())
            # Ratios between consecutive cycle lengths
            for i in range(len(sorted_lengths) - 1):
                l1, l2 = sorted_lengths[i], sorted_lengths[i+1]
                ratios[f"cycle_{l2}_over_{l1}"] = l2 / l1
    
    # 4. Degree distribution ratios
    degrees = []
    for node in graph.nodes:
        degree = sum(1 for u, v in graph.edges if u == node or v == node)
        degrees.append(degree)
    
    if degrees:
        max_degree = max(degrees)
        mean_degree = np.mean(degrees)
        if mean_degree > 0:
            ratios["max_degree_over_mean"] = max_degree / mean_degree
    
    # 5. Z/X spider ratio
    z_count = sum(1 for nid in graph.nodes if graph.labels[nid].kind == 'Z')
    x_count = sum(1 for nid in graph.nodes if graph.labels[nid].kind == 'X')
    if x_count > 0:
        ratios["z_over_x"] = z_count / x_count
    
    # Find best matches to known constants
    best_matches = {}
    for ratio_name, ratio_value in ratios.items():
        best_match = None
        best_distance = float('inf')
        
        for const_name, const_value in constants.items():
            distance = abs(ratio_value - const_value) / const_value
            if distance < best_distance:
                best_distance = distance
                best_match = const_name
        
        best_matches[ratio_name] = {
            "value": ratio_value,
            "best_match": best_match,
            "best_match_value": constants[best_match],
            "relative_error": best_distance
        }
    
    return {
        "ratios": ratios,
        "best_matches": best_matches,
        "constants": constants
    }


def find_alpha_candidates(ratios_data: dict, threshold: float = 0.01) -> list:
    """
    Find ratios that are within threshold of α = 1/137.036.
    
    Args:
        ratios_data: Output from measure_all_ratios
        threshold: Maximum relative error (1% = 0.01)
    
    Returns:
        List of ratio names that match α
    """
    alpha = 1/137.036
    candidates = []
    
    for ratio_name, match_data in ratios_data["best_matches"].items():
        if match_data["best_match"] == "alpha" and match_data["relative_error"] < threshold:
            candidates.append({
                "ratio_name": ratio_name,
                "value": match_data["value"],
                "alpha": alpha,
                "relative_error": match_data["relative_error"]
            })
    
    return candidates


def print_ratio_report(ratios_data: dict):
    """Print formatted report of all ratios and matches."""
    print("\n" + "="*80)
    print("DIMENSIONLESS RATIOS REPORT")
    print("="*80)
    
    print("\nAll measured ratios:")
    for ratio_name, ratio_value in ratios_data["ratios"].items():
        print(f"  {ratio_name}: {ratio_value:.6f}")
    
    print("\n" + "-"*80)
    print("Best matches to known constants:")
    print("-"*80)
    
    for ratio_name, match_data in ratios_data["best_matches"].items():
        error_pct = match_data["relative_error"] * 100
        match_symbol = "✓" if error_pct < 1.0 else "~" if error_pct < 5.0 else "✗"
        
        print(f"\n{match_symbol} {ratio_name}:")
        print(f"    Value: {match_data['value']:.6f}")
        print(f"    Best match: {match_data['best_match']} = {match_data['best_match_value']:.6f}")
        print(f"    Error: {error_pct:.2f}%")
    
    # Check for α
    alpha_candidates = find_alpha_candidates(ratios_data, threshold=0.01)
    
    print("\n" + "="*80)
    if alpha_candidates:
        print("🎯 FINE STRUCTURE CONSTANT (α) CANDIDATES FOUND!")
        print("="*80)
        for candidate in alpha_candidates:
            print(f"\n  {candidate['ratio_name']}:")
            print(f"    Value: {candidate['value']:.8f}")
            print(f"    α:     {candidate['alpha']:.8f}")
            print(f"    Error: {candidate['relative_error']*100:.4f}%")
        print("\n✓✓✓ THIS WOULD BE REVOLUTIONARY ✓✓✓")
    else:
        print("No α candidates found (< 1% error)")
        print("="*80)
        
        # Check for other interesting matches
        close_matches = []
        for ratio_name, match_data in ratios_data["best_matches"].items():
            if match_data["relative_error"] < 0.05:  # Within 5%
                close_matches.append((ratio_name, match_data))
        
        if close_matches:
            print("\nClose matches to known constants (< 5% error):")
            for ratio_name, match_data in close_matches:
                print(f"  {ratio_name} → {match_data['best_match']} ({match_data['relative_error']*100:.2f}% error)")


if __name__ == "__main__":
    # This is a utility module; use from long_run_evolution_simple.py
    print("Run this via: python scripts/long_run_evolution_simple.py --steps 10000")
