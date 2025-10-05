"""hamiltonian.py

Theory-compliant Hamiltonian for FIRM graphs.

From existing theory:
- Kinetic energy: T = Σ_edges |∇φ|² (coherence_density in grace_field.py)
- Potential energy: V(u) = αu - βu² + γu³ (grace_field.py)
- Total energy: H = T + V

This module adds:
- Interaction coupling measurement
- Fine structure constant derivation: α = g/(4π⟨∇φ⟩)

Theory provenance:
- grace_field.py: coherence_density(grad_phi_sqr, amplitude_sqr)
- QFT: α = e²/(4πε₀ℏc) → α_FIRM = g/(4π⟨∇φ⟩)
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict
from .core import ObjectG
from .grace_field import GraceFieldParams, potential_V
from .coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def compute_kinetic_energy(graph: ObjectG) -> float:
    """
    Kinetic energy from phase gradients: T = Σ_edges (∇φ)².
    
    This is the standard kinetic term in field theory.
    Theory: coherence_density uses |∇φ|² (grace_field.py line 22)
    """
    if not graph.edges:
        return 0.0
    
    kinetic = 0.0
    
    for u, v in graph.edges:
        if u in graph.labels and v in graph.labels:
            phase_u = math.pi * graph.labels[u].phase_numer / graph.labels[u].phase_denom
            phase_v = math.pi * graph.labels[v].phase_numer / graph.labels[v].phase_denom
            
            # Phase gradient
            grad_phi = phase_v - phase_u
            
            # Kinetic contribution
            kinetic += grad_phi ** 2
    
    return kinetic


def compute_interaction_energy(graph: ObjectG) -> float:
    """
    Interaction energy from vertex coupling: V_int = Σ_vertices g·n(n-1).
    
    In QFT: 4-point interaction (φ⁴ theory)
    In FIRM: Vertex degree → interaction strength
    
    Theory: Higher degree → stronger interaction (more connections)
    """
    if not graph.nodes:
        return 0.0
    
    interaction = 0.0
    
    for node in graph.nodes:
        # Count degree (number of connections)
        degree = sum(1 for u, v in graph.edges if u == node or v == node)
        
        # Interaction energy: n(n-1) scaling (pairwise interactions)
        # This is standard for φ⁴ theory: (a†a)² = a†a†aa
        interaction += degree * (degree - 1) / 2.0
    
    return interaction


def compute_hamiltonian(graph: ObjectG, params: GraceFieldParams) -> Dict[str, float]:
    """
    Total Hamiltonian: H = T + V_pot + V_int.
    
    Components:
    - T: Kinetic (phase gradients)
    - V_pot: Potential from grace field
    - V_int: Interaction (vertex coupling)
    
    Returns:
        Dict with all energy components
    """
    T = compute_kinetic_energy(graph)
    
    # Potential energy (from grace field)
    # u = coherence (proxy for |G|²)
    u = compute_coherence(graph)
    V_pot = potential_V(u, params)
    
    V_int = compute_interaction_energy(graph)
    
    H_total = T + V_pot + V_int
    
    return {
        "kinetic": T,
        "potential": V_pot,
        "interaction": V_int,
        "total": H_total
    }


def measure_coupling_constant(graph: ObjectG) -> float:
    """
    Measure interaction coupling constant g from graph.
    
    g = V_int / N_vertices
    
    This is the average interaction energy per vertex.
    """
    V_int = compute_interaction_energy(graph)
    N_vertices = len(graph.nodes)
    
    if N_vertices == 0:
        return 0.0
    
    g = V_int / N_vertices
    return g


def measure_kinetic_scale(graph: ObjectG) -> float:
    """
    Measure kinetic energy scale ⟨∇φ⟩.
    
    This is the average phase gradient per edge.
    """
    T = compute_kinetic_energy(graph)
    N_edges = len(graph.edges)
    
    if N_edges == 0:
        return 0.0
    
    avg_grad_phi_sq = T / N_edges
    return avg_grad_phi_sq


def derive_fine_structure_constant(graph: ObjectG) -> Dict[str, float]:
    """
    Derive fine structure constant from graph dynamics.
    
    Formula: α = g / (4π · ⟨∇φ⟩)
    
    Theory:
    - In QED: α = e²/(4πε₀ℏc) ≈ 1/137.036
    - In FIRM: α = g_interaction / (4π · kinetic_scale)
    
    where:
    - g = interaction coupling (from vertices)
    - ⟨∇φ⟩ = kinetic scale (from edges)
    
    Returns:
        Dict with g, kinetic_scale, α_FIRM, and error from α_true
    """
    g = measure_coupling_constant(graph)
    kinetic_scale = measure_kinetic_scale(graph)
    
    if kinetic_scale == 0:
        return {
            "g": g,
            "kinetic_scale": 0.0,
            "alpha_FIRM": 0.0,
            "alpha_true": 1/137.036,
            "relative_error": 1.0
        }
    
    # Derive α
    alpha_FIRM = g / (4 * math.pi * kinetic_scale)
    
    # Compare to true value
    alpha_true = 1/137.036
    relative_error = abs(alpha_FIRM - alpha_true) / alpha_true
    
    return {
        "g": g,
        "kinetic_scale": kinetic_scale,
        "alpha_FIRM": alpha_FIRM,
        "alpha_true": alpha_true,
        "relative_error": relative_error,
        "error_pct": relative_error * 100
    }


__all__ = [
    "compute_kinetic_energy",
    "compute_interaction_energy",
    "compute_hamiltonian",
    "measure_coupling_constant",
    "measure_kinetic_scale",
    "derive_fine_structure_constant"
]
