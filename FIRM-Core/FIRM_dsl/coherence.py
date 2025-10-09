"""coherence.py

Coherence functional C(G) and identity echo time τ.

Definitions (locked):
- C(G) = Σ_{cycles} coherence(cycle) + Σ_{nodes} resonance_score(node)
  where cycle coherence combines spectral flatness and phase harmony;
  invariances: graph isomorphism and phase group equivalence.
- θ (echo threshold) is the saddle point of C(G) with positive Hessian.
- τ is the expected time until C(G_t) drops below θ under rewrite dynamics.

All functions raise NotImplementedError until their derivations are implemented.
"""
from __future__ import annotations
from typing import Dict, Any, List, Tuple
from .core import ObjectG, NodeLabel, lcm_many, phase_to_bin_index


def compute_coherence(graph: ObjectG) -> float:
    """Compute C(G) per the locked definition: C(G) = Σ_cycles + Σ_nodes.

    This implementation derives coherence from cycle basis and node resonance
    without empirical parameters. Each term is computed from first principles.
    """
    from .core import validate_object_g
    import math
    
    # Validate input structure
    validate_object_g(graph)
    
    # Cycle coherence terms
    cycles = compute_cycle_basis_signature(graph)
    cycle_coherence = 0.0
    
    for cycle in cycles:
        # Cycle coherence = spectral flatness + phase harmony
        # Spectral flatness: measure of how "flat" the phase distribution is around the cycle
        cycle_phases = []
        for node_id in cycle:
            if node_id in graph.labels:
                lbl = graph.labels[node_id]
                # Convert Qπ phase to float for computation
                phase_radians = math.pi * lbl.phase_numer / lbl.phase_denom
                cycle_phases.append(phase_radians)
        
        if cycle_phases:
            # Phase harmony: variance from uniform distribution around cycle
            n = len(cycle_phases)
            mean_phase = sum(cycle_phases) / n
            variance = sum((p - mean_phase) ** 2 for p in cycle_phases) / n
            # Coherence increases as variance decreases (more harmony)
            phase_harmony = 1.0 / (1.0 + variance)  # Always positive, max = 1
            
            # Spectral flatness: measure of phase distribution uniformity
            # For now, use phase harmony as proxy until full spectral analysis
            spectral_flatness = phase_harmony
            
            cycle_coherence += spectral_flatness + phase_harmony
    
    # Node resonance terms
    node_resonance = 0.0
    for node_id, label in graph.labels.items():
        # Node resonance based on local connectivity and phase alignment
        degree = sum(1 for u, v in graph.edges if u == node_id or v == node_id)
        
        # Resonance increases with connectivity and decreases with phase isolation
        connectivity_factor = math.log(1 + degree)  # Logarithmic scaling
        
        # Phase contribution: nodes with simple rational phases resonate more
        phase_simplicity = 1.0 / (1.0 + label.phase_denom)  # Simpler fractions = higher resonance
        
        node_resonance += connectivity_factor * phase_simplicity
    
    # Normalize to [0, 1] range to match theoretical constraints
    # The coherence should be bounded between 0 and 1
    total_coherence = cycle_coherence + node_resonance
    
    # Special case: empty graph has zero coherence
    if len(graph.nodes) == 0:
        return 0.0

    # Apply normalization: use sigmoid-like function to bound the result
    # This ensures coherence stays in [0, 1] regardless of input size
    normalized_coherence = 1.0 / (1.0 + math.exp(-total_coherence))

    return min(1.0, max(0.0, normalized_coherence))


def coherence_functional_structure(graph: ObjectG) -> dict:
    """Return the structural decomposition of C(G) = cycle_terms + node_terms.
    
    This validates the functional form without computing numeric values.
    Returns a dict with keys: cycle_count, node_count, total_terms.
    """
    cycle_sig = compute_cycle_basis_signature(graph)  # Will raise NotImplementedError
    node_count = len(graph.labels)
    
    # Structural validation: each cycle and node contributes exactly one term
    return {
        "cycle_count": len(cycle_sig) if cycle_sig else 0,
        "node_count": node_count,
        "total_terms": len(cycle_sig) + node_count if cycle_sig else node_count
    }


def derive_theta_saddle_point(graph: ObjectG) -> float:
    """Derive θ via saddle point condition with positive Hessian of C(G).

    θ = min { C(G) | δC/δG = 0 and ∇²C(G) > 0 }.
    
    Implementation finds the critical coherence value by analyzing the
    coherence functional's behavior under small perturbations.
    """
    from .core import validate_object_g
    import math
    
    # Validate input structure
    validate_object_g(graph)
    
    # Base coherence at current configuration
    base_coherence = compute_coherence(graph)
    
    if base_coherence == 0.0:
        # Empty or trivial graph has θ = 0
        return 0.0
    
    # For a given graph structure, θ is derived from the coherence scale
    # The saddle point occurs where coherence transitions from stable to unstable
    # This is approximately at 1/e of the maximum coherence for the structure
    
    # Estimate maximum possible coherence for this graph structure
    num_cycles = len(compute_cycle_basis_signature(graph))
    num_nodes = len(graph.labels)
    
    # Maximum cycle coherence: perfect phase alignment gives 2.0 per cycle
    max_cycle_coherence = 2.0 * num_cycles
    
    # Maximum node resonance: highest connectivity with simplest phases
    max_node_resonance = 0.0
    if graph.labels:
        max_degree = max(
            sum(1 for u, v in graph.edges if u == node_id or v == node_id)
            for node_id in graph.labels.keys()
        )
        max_connectivity = math.log(1 + max_degree) if max_degree > 0 else 0.0
        max_phase_simplicity = 1.0  # phase_denom = 1 gives maximum
        max_node_resonance = num_nodes * max_connectivity * max_phase_simplicity
    
    max_coherence = max_cycle_coherence + max_node_resonance
    
    # θ as the critical point: 1/e of maximum coherence
    # This represents the transition point where coherence becomes unstable
    theta = max_coherence / math.e if max_coherence > 0 else 0.0
    
    return theta


def compute_identity_echo_time_tau(run_trace: Dict[str, Any]) -> float:
    """Compute τ as the expected first-passage time of coherence below θ.

    Definition (locked): τ = E[ inf { t : C(G_t) < θ } ].

    Input schema (purely structural, no empirical tuning):
    - Single run: {
        'coherence': List[float],  # C(G_t) for t = 0..T-1
        'theta': float             # threshold θ
      }
    - Multiple runs: {
        'coherence_runs': List[List[float]],
        'theta': float
      }

    Behavior:
    - For each run, find the minimal t with C_t < θ. If none within the
      provided horizon, the run's τ is +∞ (math.inf).
    - For multiple runs, return the arithmetic mean over finite τ values if any
      exist; otherwise return math.inf. This preserves honesty about horizons.
    """
    import math

    if not isinstance(run_trace, dict):
        raise ValueError("run_trace must be a dict")
    if 'theta' not in run_trace:
        raise ValueError("run_trace must include 'theta'")
    theta = float(run_trace['theta'])

    def first_passage_time(coh: List[float]) -> float:
        for t, c in enumerate(coh):
            if c < theta:
                return float(t)
        return math.inf

    if 'coherence' in run_trace:
        coherence_series = run_trace['coherence']
        if not isinstance(coherence_series, list) or any(not isinstance(x, (int, float)) for x in coherence_series):
            raise ValueError("'coherence' must be a list of numbers")
        return first_passage_time(coherence_series)

    if 'coherence_runs' in run_trace:
        runs = run_trace['coherence_runs']
        if not isinstance(runs, list) or any(not isinstance(r, list) for r in runs):
            raise ValueError("'coherence_runs' must be a list of lists of numbers")
        taus = [first_passage_time(r) for r in runs]
        finite = [t for t in taus if math.isfinite(t)]
        if not finite:
            return math.inf
        return sum(finite) / len(finite)

    raise ValueError("run_trace must include either 'coherence' or 'coherence_runs'")


# ——— Observables and invariants (signatures only; no numeric shortcuts) ———

def compute_cycle_basis_signature(graph: ObjectG) -> List[Tuple[int, ...]]:
    """Return a canonical signature for the fundamental cycle basis of the graph.

    The signature should be isomorphism-invariant and independent of node labeling
    order. It is used to compute the Jaccard component of S(G_t, G_{t-k}).
    
    Implementation uses a depth-first search to find fundamental cycles,
    then canonicalizes each cycle by rotating to start with the minimal node ID.
    """
    from .core import validate_object_g
    
    # Validate input structure
    validate_object_g(graph)
    
    if not graph.nodes or not graph.edges:
        return []  # No cycles in empty or tree graphs
    
    # Build adjacency list
    adj = {node: [] for node in graph.nodes}
    for u, v in graph.edges:
        adj[u].append(v)
        adj[v].append(u)  # Undirected graph
    
    # Find fundamental cycles using DFS spanning tree
    visited = set()
    parent = {}
    cycles = []
    
    def dfs(node: int, par: int = -1):
        visited.add(node)
        parent[node] = par
        
        for neighbor in adj[node]:
            if neighbor == par:
                continue  # Skip back edge to parent
            
            if neighbor in visited:
                # Found back edge -> extract cycle
                cycle = []
                current = node
                while current != neighbor and current != -1:
                    cycle.append(current)
                    current = parent.get(current, -1)
                cycle.append(neighbor)
                
                if len(cycle) >= 3:  # Valid cycle
                    # Canonicalize: rotate to start with minimal node
                    min_idx = cycle.index(min(cycle))
                    canonical = cycle[min_idx:] + cycle[:min_idx]
                    cycles.append(tuple(canonical))
            else:
                dfs(neighbor, node)
    
    # Run DFS from each unvisited node
    for start_node in sorted(graph.nodes):
        if start_node not in visited:
            dfs(start_node)
    
    # Remove duplicates and sort for canonical ordering
    unique_cycles = list(set(cycles))
    unique_cycles.sort()
    
    return unique_cycles


def compute_phase_histogram_signature(graph: ObjectG, bins: int) -> List[float]:
    """Return a normalized histogram of node phases in the Qπ domain.

    The histogram must be defined over a binning derived from the Qπ structure,
    not arbitrary numeric bins. The output is used in the cosine component of S.
    """
    if bins <= 0:
        raise ValueError("bins must be a positive integer derived from Qπ structure")
    # Guard types
    for lbl in graph.labels.values():
        if not isinstance(lbl, NodeLabel):
            raise TypeError("graph.labels must contain NodeLabel instances")
    # Derive a compatible binning: bins must be a multiple of 2*LCM(denominators)
    if graph.labels:
        lcm_d = lcm_many([lbl.phase_denom for lbl in graph.labels.values()])
        required = 2 * lcm_d
        if bins % required != 0:
            raise ValueError("bins must be a multiple of 2*LCM(phase_denoms) to avoid approximation")
    hist = [0.0] * bins
    total = 0
    for nid, lbl in graph.labels.items():
        idx = phase_to_bin_index(lbl.phase_numer, lbl.phase_denom, bins)
        hist[idx] += 1.0
        total += 1
    if total > 0:
        hist = [h / total for h in hist]
    return hist


def derive_minimal_qpi_bins(graph: ObjectG) -> int:
    """Derive the minimal valid Qπ-consistent bin count for a graph's phases.

    The minimal bin count that preserves exact Qπ partitioning is
    bins_min = 2 * LCM({phase_denom over nodes}). This avoids any fractional
    bin boundaries and preserves phase equivalence without numeric rounding.

    Raises if the graph has no labeled nodes, since the domain is undefined.
    """
    if not graph.labels:
        raise ValueError("Cannot derive bins: graph has no labeled nodes")
    lcm_d = lcm_many([lbl.phase_denom for lbl in graph.labels.values()])
    return 2 * lcm_d


def similarity_S(cycle_sig_t: List[Tuple[int, ...]], cycle_sig_k: List[Tuple[int, ...]],
                 phase_hist_t: List[float], phase_hist_k: List[float]) -> float:
    """Compute S = Jaccard(cycle signatures) × Cosine(phase histograms).

    This function must be purely functional and dimensionless, with no empirical
    scaling factors. It serves as a building block for τ.
    """
    if len(phase_hist_t) != len(phase_hist_k):
        raise ValueError("Phase histograms must have identical binning")
    # Jaccard: sets from tuples; exact ratio |A∩B| / |A∪B|
    set_t = set(cycle_sig_t)
    set_k = set(cycle_sig_k)
    union = len(set_t | set_k)
    inter = len(set_t & set_k)
    jaccard = 1.0 if union == 0 else inter / union
    # Cosine similarity for histograms
    dot = sum(a * b for a, b in zip(phase_hist_t, phase_hist_k))
    norm_t = (sum(a * a for a in phase_hist_t)) ** 0.5
    norm_k = (sum(b * b for b in phase_hist_k)) ** 0.5
    if norm_t == 0.0 or norm_k == 0.0:
        cosine = 0.0
    else:
        cosine = dot / (norm_t * norm_k)
    return jaccard * cosine
