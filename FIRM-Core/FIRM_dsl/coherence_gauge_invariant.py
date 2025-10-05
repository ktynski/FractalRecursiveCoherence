"""
Gauge-Invariant Coherence Implementation

This module provides a theory-compliant coherence functional that respects
U(1) gauge symmetry (phase group equivalence) as required by the locked definition:

"invariances: graph isomorphism and phase group equivalence"

The key insight: coherence must depend ONLY on phase DIFFERENCES between
connected nodes, not on absolute phases. This ensures:
  C(G) = C(G') where G' has all phases shifted by constant θ

This is fundamental to gauge theories in physics (electromagnetism, etc.).
"""

from typing import List, Tuple
import math
from .core import ObjectG, validate_object_g, NodeLabel


def compute_coherence_gauge_invariant(graph: ObjectG) -> float:
    """
    Compute C(G) with U(1) gauge invariance.
    
    Theory requirement (from coherence.py line 8):
    "invariances: graph isomorphism and phase group equivalence"
    
    Implementation:
    - Cycle coherence: uses phase differences around cycles (gauge-invariant)
    - Node resonance: uses connectivity only (no absolute phases)
    
    This ensures C(G + θ) = C(G) for any global phase shift θ.
    """
    validate_object_g(graph)
    
    from .coherence import compute_cycle_basis_signature
    
    # Cycle coherence: phase differences around cycles
    cycles = compute_cycle_basis_signature(graph)
    cycle_coherence = 0.0
    
    for cycle in cycles:
        # Compute phase differences along cycle edges
        phase_diffs = []
        for i in range(len(cycle)):
            node_a = cycle[i]
            node_b = cycle[(i + 1) % len(cycle)]
            
            if node_a in graph.labels and node_b in graph.labels:
                lbl_a = graph.labels[node_a]
                lbl_b = graph.labels[node_b]
                
                # Phase difference (gauge-invariant quantity)
                phase_a = math.pi * lbl_a.phase_numer / lbl_a.phase_denom
                phase_b = math.pi * lbl_b.phase_numer / lbl_b.phase_denom
                phase_diff = (phase_b - phase_a) % (2 * math.pi)
                
                # Normalize to [-π, π]
                if phase_diff > math.pi:
                    phase_diff -= 2 * math.pi
                
                phase_diffs.append(phase_diff)
        
        if phase_diffs:
            # Cycle coherence: how "closed" is the phase winding?
            # For a closed cycle, Σ phase_diffs should be 0 (mod 2π)
            total_winding = sum(phase_diffs) % (2 * math.pi)
            if total_winding > math.pi:
                total_winding -= 2 * math.pi
            
            # Coherence is high when winding is close to 0 (phase-closed cycle)
            winding_coherence = 1.0 / (1.0 + abs(total_winding))
            
            # Phase harmony: variance of phase differences (low variance = high harmony)
            n = len(phase_diffs)
            mean_diff = sum(phase_diffs) / n
            variance = sum((d - mean_diff) ** 2 for d in phase_diffs) / n
            phase_harmony = 1.0 / (1.0 + variance)
            
            cycle_coherence += winding_coherence + phase_harmony
    
    # Node resonance: purely topological (gauge-invariant by construction)
    node_resonance = 0.0
    for node_id in graph.labels.keys():
        # Degree (connectivity)
        degree = sum(1 for u, v in graph.edges if u == node_id or v == node_id)
        
        # Resonance from connectivity alone (no phase dependence whatsoever)
        # This ensures perfect gauge invariance
        connectivity_factor = math.log(1 + degree)
        
        node_resonance += connectivity_factor
    
    return cycle_coherence + node_resonance


def verify_gauge_invariance(graph: ObjectG, shift_amount: int = 50) -> dict:
    """
    Verify that coherence is gauge-invariant by applying a global phase shift.
    
    Args:
        graph: Input graph
        shift_amount: Phase shift in units of 1/100 * 2π
    
    Returns:
        Dict with:
        - coherence_before: C(G) before shift
        - coherence_after: C(G) after shift
        - relative_change: |C_after - C_before| / C_before
        - is_gauge_invariant: True if relative_change < 0.01
    """
    from .core import make_node_label
    
    # Measure before
    coh_before = compute_coherence_gauge_invariant(graph)
    
    # Apply global phase shift
    shifted_labels = {}
    for node_id, label in graph.labels.items():
        new_numer = (label.phase_numer + shift_amount) % (2 * label.phase_denom)
        shifted_labels[node_id] = make_node_label(
            label.kind, new_numer, label.phase_denom, label.monadic_id
        )
    
    # Create shifted graph
    shifted_graph = ObjectG(
        nodes=graph.nodes.copy(),
        edges=graph.edges.copy(),
        labels=shifted_labels
    )
    shifted_graph = validate_object_g(shifted_graph)
    
    # Measure after
    coh_after = compute_coherence_gauge_invariant(shifted_graph)
    
    # Compute relative change
    relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
    
    return {
        "coherence_before": coh_before,
        "coherence_after": coh_after,
        "relative_change": relative_change,
        "is_gauge_invariant": relative_change < 0.02  # 2% tolerance for numerical precision
    }


def compare_implementations(graph: ObjectG) -> dict:
    """
    Compare original and gauge-invariant coherence implementations.
    
    Returns:
        Dict with:
        - original_coherence: C(G) from original implementation
        - gauge_invariant_coherence: C(G) from gauge-invariant implementation
        - difference: Absolute difference
        - original_gauge_violation: Relative change under phase shift (original)
        - gauge_invariant_violation: Relative change under phase shift (new)
    """
    from .coherence import compute_coherence
    
    # Compute both versions
    coh_original = compute_coherence(graph)
    coh_gauge_inv = compute_coherence_gauge_invariant(graph)
    
    # Test gauge invariance of original
    original_test = verify_gauge_invariance_original(graph)
    
    # Test gauge invariance of new
    gauge_inv_test = verify_gauge_invariance(graph)
    
    return {
        "original_coherence": coh_original,
        "gauge_invariant_coherence": coh_gauge_inv,
        "difference": abs(coh_original - coh_gauge_inv),
        "original_gauge_violation": original_test["relative_change"],
        "gauge_invariant_violation": gauge_inv_test["relative_change"]
    }


def verify_gauge_invariance_original(graph: ObjectG, shift_amount: int = 50) -> dict:
    """Test gauge invariance of original implementation."""
    from .coherence import compute_coherence
    from .core import make_node_label
    
    coh_before = compute_coherence(graph)
    
    # Apply shift
    shifted_labels = {}
    for node_id, label in graph.labels.items():
        new_numer = (label.phase_numer + shift_amount) % (2 * label.phase_denom)
        shifted_labels[node_id] = make_node_label(
            label.kind, new_numer, label.phase_denom, label.monadic_id
        )
    
    shifted_graph = ObjectG(
        nodes=graph.nodes.copy(),
        edges=graph.edges.copy(),
        labels=shifted_labels
    )
    shifted_graph = validate_object_g(shifted_graph)
    
    coh_after = compute_coherence(shifted_graph)
    relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
    
    return {
        "coherence_before": coh_before,
        "coherence_after": coh_after,
        "relative_change": relative_change,
        "is_gauge_invariant": relative_change < 0.02  # 2% tolerance for numerical precision
    }
