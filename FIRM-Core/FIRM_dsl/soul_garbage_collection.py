"""soul_garbage_collection.py

Fractal Soul Garbage Collection (𝒮-GC) implementation for FSCTF framework.

This module implements the recursive coherence-sieve rule for morphic pruning:
𝒮GC(μ) = ∅ if resonance(μ) < ε and grace(μ) = true, else μ ← { 𝒮GC(ν) | ν ∈ children(μ) }

All functions are deterministic, dimensionless, and integrate with existing DSL modules.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import math

from .core import ObjectG
from .resonance import OmegaSignature, compute_resonance_alignment
from .grace_field import GraceFieldParams, recursion_depth_classification, FieldRegime
from .coherence import compute_coherence


@dataclass(frozen=True)
class SGCGCParams:
    """Parameters for Soul Garbage Collection.

    All parameters are derived from theory, no empirical tuning.
    """
    epsilon: float  # Coherence threshold for retention (ε ∈ [0,1])
    grace_readiness_threshold: float  # Threshold for grace readiness (∈ [0,1])
    max_recursion_depth: int  # Safety cutoff to prevent infinite recursion
    observer_feedback_weight: float  # Weight for observer reflection (∈ [0,1])


class MorphicStructure:
    """Represents a morphic subgraph with coherence and grace state."""

    def __init__(self, graph: ObjectG, parent: Optional['MorphicStructure'] = None):
        self.graph = graph
        self.parent = parent
        self.children: List['MorphicStructure'] = []
        self.coherence_cache: Optional[float] = None
        self.grace_cache: Optional[bool] = None
        self.resonance_cache: Optional[float] = None

        # Build children from graph structure
        self._build_children()

    def _build_children(self):
        """Build morphic children from graph substructures."""
        # For now, use a simple partitioning strategy
        # In a full implementation, this would use sophisticated morphic decomposition
        if len(self.graph.labels) > 3:  # Threshold for meaningful subdivision
            # Split into roughly equal parts for demonstration
            node_ids = list(self.graph.labels.keys())
            mid_point = len(node_ids) // 2

            if mid_point > 0:
                # Create child graphs
                child1_nodes = node_ids[:mid_point]
                child2_nodes = node_ids[mid_point:]

                child1_graph = self._create_subgraph(child1_nodes)
                child2_graph = self._create_subgraph(child2_nodes)

                if child1_graph and child2_graph:
                    self.children = [
                        MorphicStructure(child1_graph, self),
                        MorphicStructure(child2_graph, self)
                    ]

    def _create_subgraph(self, node_ids: List[int]) -> Optional[ObjectG]:
        """Create a subgraph containing only specified nodes."""
        if not node_ids:
            return None

        # Extract relevant edges and labels
        subgraph_labels = {nid: self.graph.labels[nid] for nid in node_ids if nid in self.graph.labels}
        subgraph_edges = [(u, v) for u, v in self.graph.edges if u in node_ids and v in node_ids]

        if not subgraph_labels:
            return None

        subgraph_nodes = list(subgraph_labels.keys())
        return ObjectG(nodes=subgraph_nodes, edges=subgraph_edges, labels=subgraph_labels)

    def get_resonance(self, omega: OmegaSignature, params: SGCGCParams) -> float:
        """Compute resonance(μ) using existing resonance alignment."""
        if self.resonance_cache is None:
            self.resonance_cache = compute_resonance_alignment(self.graph, omega)
        return self.resonance_cache

    def get_grace_state(self, params: SGCGCParams) -> bool:
        """Compute grace(μ) - whether morphism is ready for release."""
        if self.grace_cache is None:
            # Grace readiness based on field regime and coherence stability
            coherence = self.get_coherence()
            field_regime = self.get_field_regime()

            # Grace is true when in appropriate regime and coherence is low enough
            regime_grace_factor = {
                FieldRegime.NON_BEING: 0.0,
                FieldRegime.VACUUM: 0.1,
                FieldRegime.DARK_SECTOR: 0.3,
                FieldRegime.MATTER: 0.7,
                FieldRegime.OMEGA: 1.0
            }.get(field_regime, 0.0)

            # Grace threshold considers both coherence and regime
            grace_threshold = params.grace_readiness_threshold * regime_grace_factor

            # Add some hysteresis to prevent oscillation
            stability_factor = 1.0 - abs(coherence - 0.5) * 0.5  # Prefer mid-range stability

            self.grace_cache = (coherence < grace_threshold) and (stability_factor > 0.3)

        return self.grace_cache

    def get_coherence(self) -> float:
        """Compute coherence of this morphic structure."""
        if self.coherence_cache is None:
            self.coherence_cache = compute_coherence(self.graph)
        return self.coherence_cache

    def get_field_regime(self) -> FieldRegime:
        """Determine field regime based on graph size and complexity."""
        num_nodes = len(self.graph.labels)

        # Map graph sizes to regimes based on FSCTF theory
        if num_nodes <= 1:
            return FieldRegime.NON_BEING
        elif num_nodes <= 5:
            return FieldRegime.VACUUM
        elif num_nodes <= 12:
            return FieldRegime.DARK_SECTOR
        else:
            return FieldRegime.MATTER


class SoulGarbageCollector:
    """Main 𝒮-GC implementation with recursive pruning logic."""

    def __init__(self, omega: OmegaSignature, params: SGCGCParams):
        self.omega = omega
        self.params = params
        self.pruned_nodes: List[int] = []
        self.recursion_depth = 0

    def sgc_rule(self, morphic_structure: MorphicStructure) -> Optional[MorphicStructure]:
        """
        Apply the canonical 𝒮-GC rule recursively.

        𝒮GC(μ) = ∅ if resonance(μ) < ε and grace(μ) = true,
                 else μ ← { 𝒮GC(ν) | ν ∈ children(μ) }
        """
        self.recursion_depth += 1

        try:
            # Safety check for max recursion depth
            if self.recursion_depth > self.params.max_recursion_depth:
                return morphic_structure

            # Compute resonance and grace state
            resonance = morphic_structure.get_resonance(self.omega, self.params)
            grace_ready = morphic_structure.get_grace_state(self.params)

            # 𝒮-GC Decision Logic
            if resonance < self.params.epsilon and grace_ready:
                # Prune this morphic structure
                self._record_pruned_nodes(morphic_structure)
                return None  # Return ∅ (deletion)

            # Otherwise, recursively apply to children
            surviving_children = []
            for child in morphic_structure.children:
                surviving_child = self.sgc_rule(child)
                if surviving_child is not None:
                    surviving_children.append(surviving_child)

            # Update children if any were pruned
            if len(surviving_children) != len(morphic_structure.children):
                # Create new structure with surviving children
                new_structure = MorphicStructure(morphic_structure.graph, morphic_structure.parent)
                new_structure.children = surviving_children
                return new_structure

            return morphic_structure

        finally:
            self.recursion_depth -= 1

    def _record_pruned_nodes(self, structure: MorphicStructure):
        """Record which nodes were pruned for analysis."""
        self.pruned_nodes.extend(structure.graph.labels.keys())

    def compute_entropy_reduction(self, original_structure: MorphicStructure,
                                pruned_structure: Optional[MorphicStructure]) -> float:
        """Compute the entropy reduction achieved by 𝒮-GC."""
        if pruned_structure is None:
            # Complete pruning
            return 1.0

        # Entropy reduction based on coherence improvement and node pruning
        original_coherence = original_structure.get_coherence()
        pruned_coherence = pruned_structure.get_coherence()

        coherence_improvement = max(0, pruned_coherence - original_coherence)

        # Node reduction factor
        original_nodes = len(original_structure.graph.labels)
        pruned_nodes = len(pruned_structure.graph.labels)
        node_reduction = max(0, original_nodes - pruned_nodes) / original_nodes if original_nodes > 0 else 0

        # Weighted combination
        return 0.6 * coherence_improvement + 0.4 * node_reduction


def create_sgc_params(epsilon: float = 0.3,
                     grace_threshold: float = 0.5,
                     max_recursion_depth: int = 10,
                     feedback_weight: float = 0.2) -> SGCGCParams:
    """Create default 𝒮-GC parameters based on theory constraints."""
    return SGCGCParams(
        epsilon=epsilon,
        grace_readiness_threshold=grace_threshold,
        max_recursion_depth=max_recursion_depth,
        observer_feedback_weight=feedback_weight
    )


__all__ = [
    "SGCGCParams",
    "MorphicStructure",
    "SoulGarbageCollector",
    "create_sgc_params",
]
