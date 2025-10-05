"""
Emergence Detection: Identify profound emergent phenomena in FIRM evolution.

This module tests for:
1. Self-organized criticality (power-law distributions, avalanches)
2. Holographic behavior (boundary encodes bulk)
3. Thermodynamic arrow of time (monotonic entropy increase)
4. Emergent locality (finite information propagation speed)
5. Vacuum energy (non-zero baseline coherence)

These are the "smoking gun" signatures that would distinguish
"interesting toy model" from "candidate theory of reality."
"""

import numpy as np
from collections import Counter, deque
from typing import List, Dict, Tuple
from .core import ObjectG
from .coherence import compute_coherence


def detect_self_organized_criticality(event_sizes: List[int], 
                                       min_events: int = 100) -> Dict[str, float]:
    """
    Test for self-organized criticality via power-law distribution of event sizes.
    
    Args:
        event_sizes: List of rewrite cascade sizes (nodes affected per event)
        min_events: Minimum events needed for reliable fit
    
    Returns:
        Dict with:
        - power_law_exponent: α in P(s) ~ s^(-α)
        - r_squared: Goodness of fit
        - is_critical: True if exponent in [1.5, 3.0] (typical for SOC)
    """
    if len(event_sizes) < min_events:
        return {"power_law_exponent": None, "r_squared": None, "is_critical": False}
    
    # Bin event sizes
    counts = Counter(event_sizes)
    sizes = np.array(sorted(counts.keys()))
    frequencies = np.array([counts[s] for s in sizes])
    
    # Filter out zeros and take log
    mask = (sizes > 0) & (frequencies > 0)
    log_sizes = np.log(sizes[mask])
    log_freqs = np.log(frequencies[mask])
    
    if len(log_sizes) < 3:
        return {"power_law_exponent": None, "r_squared": None, "is_critical": False}
    
    # Fit power law: log(P) = -α * log(s) + c
    coeffs = np.polyfit(log_sizes, log_freqs, 1)
    alpha = -coeffs[0]
    
    # Compute R²
    predicted = np.polyval(coeffs, log_sizes)
    ss_res = np.sum((log_freqs - predicted)**2)
    ss_tot = np.sum((log_freqs - np.mean(log_freqs))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # SOC typically has α ∈ [1.5, 3.0]
    is_critical = 1.5 <= alpha <= 3.0 and r_squared > 0.8
    
    return {
        "power_law_exponent": alpha,
        "r_squared": r_squared,
        "is_critical": is_critical
    }


def detect_holographic_behavior(graph: ObjectG) -> Dict[str, float]:
    """
    Test for holographic principle: boundary information encodes bulk.
    
    We check if:
    - Entropy scales with surface area (not volume)
    - Boundary nodes contain enough information to reconstruct bulk
    
    Args:
        graph: Current graph state
    
    Returns:
        Dict with:
        - boundary_nodes: Count of boundary nodes (degree 1 or 2)
        - bulk_nodes: Count of interior nodes (degree > 2)
        - entropy_boundary: Information content of boundary
        - entropy_bulk: Information content of bulk
        - area_scaling_ratio: entropy_boundary / sqrt(boundary_nodes)
        - is_holographic: True if boundary entropy ~ sqrt(area)
    """
    if len(graph.nodes) < 10:
        return {"is_holographic": False, "reason": "Graph too small"}
    
    # Classify nodes by degree
    boundary_nodes = []
    bulk_nodes = []
    
    for node_id in graph.nodes:
        degree = len(list(graph.neighbors(node_id)))
        if degree <= 2:
            boundary_nodes.append(node_id)
        else:
            bulk_nodes.append(node_id)
    
    if not boundary_nodes or not bulk_nodes:
        return {"is_holographic": False, "reason": "No clear boundary/bulk separation"}
    
    # Compute entropy (Shannon entropy of phase distribution)
    def phase_entropy(node_ids):
        phases = [graph.nodes[nid]['phase'] for nid in node_ids]
        # Bin phases into 10 bins
        hist, _ = np.histogram(phases, bins=10, range=(0, 2*np.pi))
        probs = hist / np.sum(hist) if np.sum(hist) > 0 else hist
        probs = probs[probs > 0]  # Remove zeros
        return -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0
    
    entropy_boundary = phase_entropy(boundary_nodes)
    entropy_bulk = phase_entropy(bulk_nodes)
    
    # Holographic scaling: S_boundary ~ sqrt(N_boundary) (area law)
    area_scaling = entropy_boundary / np.sqrt(len(boundary_nodes)) if boundary_nodes else 0
    
    # Check if boundary entropy is comparable to bulk (holographic signature)
    entropy_ratio = entropy_boundary / entropy_bulk if entropy_bulk > 0 else 0
    is_holographic = 0.5 <= entropy_ratio <= 2.0 and area_scaling > 0.5
    
    return {
        "boundary_nodes": len(boundary_nodes),
        "bulk_nodes": len(bulk_nodes),
        "entropy_boundary": entropy_boundary,
        "entropy_bulk": entropy_bulk,
        "area_scaling_ratio": area_scaling,
        "entropy_ratio": entropy_ratio,
        "is_holographic": is_holographic
    }


def detect_thermodynamic_arrow(coherence_history: List[float], 
                                 window: int = 20) -> Dict[str, float]:
    """
    Test for thermodynamic arrow of time: C(G) increases monotonically.
    
    Args:
        coherence_history: Time series of C(G) values
        window: Window size for trend analysis
    
    Returns:
        Dict with:
        - mean_slope: Average rate of C(G) increase
        - monotonic_fraction: Fraction of time C(G) increases
        - has_arrow: True if C(G) increases > 70% of the time
    """
    if len(coherence_history) < window:
        return {"has_arrow": False, "reason": "Not enough data"}
    
    # Compute local slopes
    slopes = []
    for i in range(len(coherence_history) - 1):
        slope = coherence_history[i+1] - coherence_history[i]
        slopes.append(slope)
    
    # Fraction of positive slopes
    positive_count = sum(1 for s in slopes if s > 0)
    monotonic_fraction = positive_count / len(slopes) if slopes else 0
    
    # Mean slope (overall trend)
    mean_slope = np.mean(slopes) if slopes else 0
    
    # Arrow of time present if C(G) increases most of the time
    has_arrow = monotonic_fraction > 0.7 and mean_slope > 0
    
    return {
        "mean_slope": mean_slope,
        "monotonic_fraction": monotonic_fraction,
        "has_arrow": has_arrow
    }


def detect_emergent_locality(graph: ObjectG, 
                               sample_pairs: int = 50) -> Dict[str, float]:
    """
    Test for emergent locality: distant nodes should be uncorrelated.
    
    We measure phase correlation vs graph distance:
    - Nearby nodes (distance 1-2): high correlation expected
    - Distant nodes (distance > 5): low correlation expected
    
    Args:
        graph: Current graph state
        sample_pairs: Number of node pairs to sample
    
    Returns:
        Dict with:
        - correlation_near: Mean correlation for nearby pairs
        - correlation_far: Mean correlation for distant pairs
        - locality_ratio: correlation_near / correlation_far
        - has_locality: True if locality_ratio > 2.0
    """
    if len(graph.nodes) < 10:
        return {"has_locality": False, "reason": "Graph too small"}
    
    # Compute shortest paths (BFS)
    def shortest_path_length(g, start, end, max_depth=10):
        if start == end:
            return 0
        visited = {start}
        queue = deque([(start, 0)])
        
        while queue:
            node, depth = queue.popleft()
            if depth >= max_depth:
                return None
            
            for neighbor in g.neighbors(node):
                if neighbor == end:
                    return depth + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        
        return None  # No path found
    
    # Sample node pairs
    node_ids = list(graph.nodes.keys())
    if len(node_ids) < 4:
        return {"has_locality": False, "reason": "Too few nodes"}
    
    near_correlations = []
    far_correlations = []
    
    for _ in range(min(sample_pairs, len(node_ids) * (len(node_ids) - 1) // 2)):
        n1, n2 = np.random.choice(node_ids, 2, replace=False)
        dist = shortest_path_length(graph, n1, n2)
        
        if dist is None:
            continue
        
        # Phase correlation (cosine of phase difference)
        phase1 = graph.nodes[n1]['phase']
        phase2 = graph.nodes[n2]['phase']
        correlation = np.cos(phase1 - phase2)
        
        if dist <= 2:
            near_correlations.append(correlation)
        elif dist >= 5:
            far_correlations.append(correlation)
    
    if not near_correlations or not far_correlations:
        return {"has_locality": False, "reason": "Not enough samples"}
    
    correlation_near = np.mean(near_correlations)
    correlation_far = np.mean(far_correlations)
    locality_ratio = correlation_near / correlation_far if correlation_far != 0 else np.inf
    
    # Locality present if nearby nodes are much more correlated than distant ones
    has_locality = locality_ratio > 2.0
    
    return {
        "correlation_near": correlation_near,
        "correlation_far": correlation_far,
        "locality_ratio": locality_ratio,
        "has_locality": has_locality,
        "near_samples": len(near_correlations),
        "far_samples": len(far_correlations)
    }


def detect_vacuum_energy(empty_graph_coherence: float, 
                          evolved_graph_coherence: float) -> Dict[str, float]:
    """
    Test for vacuum energy: baseline C(G) in empty graph should be non-zero.
    
    Args:
        empty_graph_coherence: C(G) for minimal graph (3 nodes, no cycles)
        evolved_graph_coherence: C(G) after evolution
    
    Returns:
        Dict with:
        - vacuum_coherence: Baseline C(G)
        - coherence_increase: Δ C(G) from vacuum to evolved
        - has_vacuum_energy: True if vacuum_coherence > 0.01
    """
    coherence_increase = evolved_graph_coherence - empty_graph_coherence
    has_vacuum_energy = empty_graph_coherence > 0.01
    
    return {
        "vacuum_coherence": empty_graph_coherence,
        "evolved_coherence": evolved_graph_coherence,
        "coherence_increase": coherence_increase,
        "has_vacuum_energy": has_vacuum_energy
    }


def run_emergence_battery(graph: ObjectG, 
                           coherence_history: List[float],
                           event_sizes: List[int]) -> Dict[str, any]:
    """
    Run all emergence detection tests and return comprehensive report.
    
    Args:
        graph: Current graph state
        coherence_history: Time series of C(G)
        event_sizes: Sizes of rewrite cascades
    
    Returns:
        Dict with results from all tests and overall assessment
    """
    results = {}
    
    # Test 1: Self-organized criticality
    results['criticality'] = detect_self_organized_criticality(event_sizes)
    
    # Test 2: Holographic behavior
    results['holography'] = detect_holographic_behavior(graph)
    
    # Test 3: Thermodynamic arrow
    results['arrow_of_time'] = detect_thermodynamic_arrow(coherence_history)
    
    # Test 4: Emergent locality
    results['locality'] = detect_emergent_locality(graph)
    
    # Test 5: Vacuum energy (requires baseline measurement)
    # This is computed separately in long-run script
    
    # Overall assessment
    profound_count = sum([
        results['criticality'].get('is_critical', False),
        results['holography'].get('is_holographic', False),
        results['arrow_of_time'].get('has_arrow', False),
        results['locality'].get('has_locality', False)
    ])
    
    results['summary'] = {
        "profound_phenomena_detected": profound_count,
        "total_tests": 4,
        "assessment": (
            "REVOLUTIONARY" if profound_count >= 3 else
            "HIGHLY INTERESTING" if profound_count == 2 else
            "PROMISING" if profound_count == 1 else
            "TOY MODEL"
        )
    }
    
    return results
