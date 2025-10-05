"""symmetry_breaking.py

Theory-compliant spontaneous symmetry breaking using existing grace_field potential.

From Resonance_Field_Model.md:
- Potential V(u) = α u − β u² + γ u³, u = |G|²
- This potential has critical points that can drive symmetry breaking

For Z/X symmetry breaking, we map:
- u = |G|² → S² where S = (N_Z - N_X) / N_total (order parameter)
- V(S²) creates Mexican hat if γ < 0 and β > 0

Theory provenance:
- grace_field.py: potential_V(u, params)
- Standard Higgs mechanism: V(φ) with degenerate minima
- Metropolis algorithm: energy-based evolution
"""

from __future__ import annotations
import numpy as np
from typing import Tuple
from .core import ObjectG, make_node_label, validate_object_g
from .grace_field import GraceFieldParams, potential_V, dV_du
from .coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def compute_order_parameter(graph: ObjectG) -> float:
    """
    Compute Z/X order parameter S = (N_Z - N_X) / N_total.
    
    S ∈ [-1, 1]:
    - S = +1: all Z-spiders (broken to Z)
    - S = 0: equal Z/X (symmetric)
    - S = -1: all X-spiders (broken to X)
    """
    if not graph.nodes:
        return 0.0
    
    z_count = sum(1 for nid in graph.nodes if graph.labels[nid].kind == 'Z')
    x_count = len(graph.nodes) - z_count
    total = len(graph.nodes)
    
    S = (z_count - x_count) / total if total > 0 else 0.0
    return S


def compute_potential_energy(graph: ObjectG, params: GraceFieldParams) -> float:
    """
    Compute potential energy using grace field potential.
    
    From theory:
    - V(u) = α u − β u² + γ u³ where u = |G|²
    - For symmetry breaking, map: u = S² (order parameter squared)
    
    Mexican hat requires:
    - α > 0 (drives away from S=0)
    - β > 0 (creates minima)
    - γ < 0 (stabilizes at finite S)
    
    Returns:
        V(S²) where S = (N_Z - N_X) / N_total
    """
    S = compute_order_parameter(graph)
    u = S ** 2  # u = |G|² → S²
    
    return potential_V(u, params)


def compute_kinetic_energy(graph: ObjectG) -> float:
    """
    Compute kinetic energy from phase gradients.
    
    T = Σ_edges |∇φ|² = Σ_edges (φ_j - φ_i)²
    
    This is the standard kinetic term in field theory.
    """
    import math
    
    kinetic = 0.0
    
    for u, v in graph.edges:
        if u in graph.labels and v in graph.labels:
            phase_u = math.pi * graph.labels[u].phase_numer / graph.labels[u].phase_denom
            phase_v = math.pi * graph.labels[v].phase_numer / graph.labels[v].phase_denom
            
            grad_phi = phase_v - phase_u
            kinetic += grad_phi ** 2
    
    return kinetic


def compute_total_energy(graph: ObjectG, params: GraceFieldParams) -> float:
    """
    Total energy E = T + V (kinetic + potential).
    
    This is the standard Hamiltonian for a scalar field.
    """
    T = compute_kinetic_energy(graph)
    V = compute_potential_energy(graph, params)
    
    return T + V


def evolve_with_metropolis(graph: ObjectG, 
                            params: GraceFieldParams,
                            temperature: float,
                            num_steps: int = 1) -> ObjectG:
    """
    Evolve graph using Metropolis algorithm (energy minimization).
    
    Algorithm:
    1. Propose move (add node with random type)
    2. Compute ΔE = E_new - E_old
    3. Accept if ΔE < 0 (always)
    4. Accept if ΔE > 0 with probability exp(-ΔE/T)
    
    This is standard statistical mechanics (Metropolis et al., 1953).
    
    Args:
        graph: Current graph state
        params: Potential parameters (α, β, γ)
        temperature: T for Boltzmann factor
        num_steps: Number of Metropolis steps
    
    Returns:
        Evolved graph
    """
    phi = (1 + np.sqrt(5)) / 2
    
    for step in range(num_steps):
        # Compute energy before
        E_old = compute_total_energy(graph, params)
        
        # Propose move: add node
        new_id = len(graph.nodes)
        
        # Random type (unbiased proposal)
        kind_proposed = 'Z' if np.random.random() > 0.5 else 'X'
        phase_numer = int((new_id * 100 / phi)) % 100
        
        new_label = make_node_label(kind_proposed, phase_numer, 100, f'n{new_id}')
        
        # Create trial graph
        trial_nodes = graph.nodes + [new_id]
        trial_labels = dict(graph.labels)
        trial_labels[new_id] = new_label
        trial_edges = list(graph.edges)
        
        # Connect to random existing node
        if graph.nodes:
            target = np.random.choice(graph.nodes)
            trial_edges.append([new_id, target])
        
        trial_graph = ObjectG(nodes=trial_nodes, edges=trial_edges, labels=trial_labels)
        trial_graph = validate_object_g(trial_graph)
        
        # Compute energy after
        E_new = compute_total_energy(trial_graph, params)
        
        # Metropolis acceptance
        delta_E = E_new - E_old
        
        if delta_E < 0:
            # Lower energy: always accept
            graph = trial_graph
        else:
            # Higher energy: accept with Boltzmann probability
            if temperature > 0:
                prob_accept = np.exp(-delta_E / temperature)
                if np.random.random() < prob_accept:
                    graph = trial_graph
            # else: reject (keep old graph)
    
    return graph


def test_symmetry_breaking_with_potential(
    params: GraceFieldParams,
    initial_temperature: float = 10.0,
    final_temperature: float = 0.01,
    cooling_steps: int = 100
) -> Tuple[list, list]:
    """
    Test symmetry breaking by cooling system with potential energy.
    
    Protocol:
    1. Start at high T (symmetric, S ≈ 0)
    2. Cool gradually (T → 0)
    3. Measure S at each step
    4. Check if |S| > 0.15 at T → 0 (broken symmetry)
    
    Args:
        params: Potential parameters (α, β, γ)
        initial_temperature: Starting T (hot)
        final_temperature: Ending T (cold)
        cooling_steps: Number of cooling stages
    
    Returns:
        (temperatures, order_parameters) for plotting
    """
    # Initialize symmetric graph
    nodes = list(range(20))
    edges = [[i, (i+1) % 20] for i in range(20)]
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(20):
        # Start 50/50 Z/X
        kind = 'Z' if i < 10 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    graph = ObjectG(nodes=nodes, edges=edges, labels=labels)
    graph = validate_object_g(graph)
    
    # Cooling schedule
    temperatures = []
    order_parameters = []
    
    # Logarithmic cooling
    for step in range(cooling_steps):
        # Temperature schedule: exponential decay
        T = initial_temperature * (final_temperature / initial_temperature) ** (step / cooling_steps)
        
        # Evolve at this temperature
        graph = evolve_with_metropolis(graph, params, T, num_steps=10)
        
        # Measure order parameter
        S = compute_order_parameter(graph)
        
        temperatures.append(T)
        order_parameters.append(S)
    
    return temperatures, order_parameters


__all__ = [
    "compute_order_parameter",
    "compute_potential_energy",
    "compute_kinetic_energy",
    "compute_total_energy",
    "evolve_with_metropolis",
    "test_symmetry_breaking_with_potential"
]
