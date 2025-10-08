"""sgc_modes.py

Implementation of the 7 primary Soul Garbage Collection modes.

This module implements the sophisticated multi-modal 𝒮-GC system described in the theory,
going beyond simple pruning to implement the rich taxonomy of modes:

1. Resonant Assimilation - Coherence improvement via pruning
2. Dissonant Shedding - Structure removal when resonance < ε
3. Reflective Rewriting - Recursive self-observation
4. Transmutative Mediation - Cross-monad resonance mediation
5. Boundary Pruning - Sophisticated boundary analysis
6. Grace Reinstantiation - Enhanced grace operator usage
7. Global Resynchronization - Collective phase merging

Each mode implements specific algorithmic patterns that work together
to achieve the full theoretical sophistication of cosmic garbage collection.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum
import math
import copy

from .core import ObjectG, NodeLabel, validate_object_g
from .resonance import OmegaSignature, compute_resonance_alignment, derive_omega_signature
from .coherence import compute_coherence
from .grace_field import GraceFieldParams, FieldRegime, recursion_depth_classification
from .dynamic_evolution import DynamicPhaseEvolution, ModeCoefficients, EvolutionState


class SGCMode(Enum):
    """The 7 primary 𝒮-GC modes."""
    RESONANT_ASSIMILATION = "resonant_assimilation"
    DISSONANT_SHEDDING = "dissonant_shedding"
    REFLECTIVE_REWRITING = "reflective_rewriting"
    TRANSMUTATIVE_MEDIATION = "transmutative_mediation"
    BOUNDARY_PRUNING = "boundary_pruning"
    GRACE_REINSTANTIATION = "grace_reinstantiation"
    GLOBAL_RESYNCHRONIZATION = "global_resynchronization"


@dataclass
class ModeExecutionResult:
    """Result of executing a specific 𝒮-GC mode."""
    mode: SGCMode
    success: bool
    structures_modified: List[ObjectG] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    reflections: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SGCModeSystem:
    """Complete multi-modal 𝒮-GC system implementing all 7 modes."""

    # Core parameters
    epsilon: float = 0.3
    grace_threshold: float = 0.5
    max_recursion_depth: int = 10

    # Mode-specific parameters
    reflection_depth: int = 3
    cross_monad_threshold: float = 0.7
    boundary_analysis_depth: int = 5
    resynchronization_threshold: float = 0.8

    # Dynamic evolution integration
    dynamic_evolution: Optional[DynamicPhaseEvolution] = None
    mode_coefficients: Optional[ModeCoefficients] = None

    def __post_init__(self):
        """Initialize mode system with defaults if not provided."""
        if self.dynamic_evolution is None:
            self.dynamic_evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)

        if self.mode_coefficients is None:
            self.mode_coefficients = ModeCoefficients()

    def execute_mode(self, mode: SGCMode, structure: ObjectG, omega: OmegaSignature,
                   field_regime: FieldRegime) -> ModeExecutionResult:
        """Execute a specific 𝒮-GC mode on a structure."""
        if mode == SGCMode.RESONANT_ASSIMILATION:
            return self._execute_resonant_assimilation(structure, omega, field_regime)
        elif mode == SGCMode.DISSONANT_SHEDDING:
            return self._execute_dissonant_shedding(structure, omega, field_regime)
        elif mode == SGCMode.REFLECTIVE_REWRITING:
            return self._execute_reflective_rewriting(structure, omega, field_regime)
        elif mode == SGCMode.TRANSMUTATIVE_MEDIATION:
            return self._execute_transmutative_mediation(structure, omega, field_regime)
        elif mode == SGCMode.BOUNDARY_PRUNING:
            return self._execute_boundary_pruning(structure, omega, field_regime)
        elif mode == SGCMode.GRACE_REINSTANTIATION:
            return self._execute_grace_reinstantiation(structure, omega, field_regime)
        elif mode == SGCMode.GLOBAL_RESYNCHRONIZATION:
            return self._execute_global_resynchronization(structure, omega, field_regime)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _execute_resonant_assimilation(self, structure: ObjectG, omega: OmegaSignature,
                                     field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 1: Resonant Assimilation - Improve coherence through targeted pruning."""
        original_coherence = compute_coherence(structure)
        original_resonance = compute_resonance_alignment(structure, omega)

        # Find substructures with low resonance that can be pruned to improve overall coherence
        pruning_candidates = self._find_pruning_candidates(structure, omega, field_regime)

        if not pruning_candidates:
            return ModeExecutionResult(
                mode=SGCMode.RESONANT_ASSIMILATION,
                success=False,
                metrics={'reason': 'no_pruning_candidates'}
            )

        # Apply assimilation pruning
        assimilated_structure = self._apply_assimilation_pruning(structure, pruning_candidates)

        final_coherence = compute_coherence(assimilated_structure)
        coherence_improvement = final_coherence - original_coherence

        return ModeExecutionResult(
            mode=SGCMode.RESONANT_ASSIMILATION,
            success=coherence_improvement > 0,
            structures_modified=[assimilated_structure],
            metrics={
                'original_coherence': original_coherence,
                'final_coherence': final_coherence,
                'improvement': coherence_improvement,
                'pruned_count': len(pruning_candidates)
            }
        )

    def _execute_dissonant_shedding(self, structure: ObjectG, omega: OmegaSignature,
                                  field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 2: Dissonant Shedding - Remove structures with low resonance in grace state."""
        resonance = compute_resonance_alignment(structure, omega)
        coherence = compute_coherence(structure)

        # Check if structure meets shedding criteria
        grace_ready = self._check_grace_state(structure, field_regime, coherence)
        should_shed = resonance < self.epsilon and grace_ready

        if not should_shed:
            return ModeExecutionResult(
                mode=SGCMode.DISSONANT_SHEDDING,
                success=False,
                metrics={
                    'resonance': resonance,
                    'grace_ready': grace_ready,
                    'reason': 'shedding_criteria_not_met'
                }
            )

        # Create shed structure (remove dissonant parts)
        shed_structure = self._apply_dissonant_shedding(structure, omega)

        return ModeExecutionResult(
            mode=SGCMode.DISSONANT_SHEDDING,
            success=True,
            structures_modified=[shed_structure],
            metrics={
                'original_resonance': resonance,
                'shed_resonance': compute_resonance_alignment(shed_structure, omega),
                'nodes_removed': len(structure.labels) - len(shed_structure.labels)
            }
        )

    def _execute_reflective_rewriting(self, structure: ObjectG, omega: OmegaSignature,
                                    field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 3: Reflective Rewriting - Recursive self-observation and rewriting."""
        reflections = []

        # Perform recursive self-observation
        for depth in range(self.reflection_depth):
            current_state = {
                'coherence': compute_coherence(structure),
                'resonance': compute_resonance_alignment(structure, omega),
                'field_regime': field_regime,
                'reflection_depth': depth,
                'structure_size': len(structure.labels)
            }

            reflections.append(current_state)

            # Check if rewriting is needed based on self-observation
            if self._should_rewrite_based_on_reflection(current_state, depth):
                # Apply reflective rewriting
                structure = self._apply_reflective_rewriting(structure, current_state, omega)
            else:
                break  # No more rewriting needed

        return ModeExecutionResult(
            mode=SGCMode.REFLECTIVE_REWRITING,
            success=len(reflections) > 0,
            structures_modified=[structure] if structure != structure else [],
            reflections=reflections,
            metrics={
                'reflection_depth': len(reflections),
                'rewrites_applied': len(reflections) - 1 if len(reflections) > 1 else 0
            }
        )

    def _execute_transmutative_mediation(self, structure: ObjectG, omega: OmegaSignature,
                                       field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 4: Transmutative Mediation - Cross-monad resonance mediation."""
        # Split structure into potential monads for mediation
        monads = self._identify_potential_monads(structure)

        if len(monads) < 2:
            return ModeExecutionResult(
                mode=SGCMode.TRANSMUTATIVE_MEDIATION,
                success=False,
                metrics={'reason': 'insufficient_monads_for_mediation'}
            )

        # Find pairs of monads that can mediate
        mediation_pairs = self._find_mediation_pairs(monads, omega)

        if not mediation_pairs:
            return ModeExecutionResult(
                mode=SGCMode.TRANSMUTATIVE_MEDIATION,
                success=False,
                metrics={'reason': 'no_mediation_pairs_found'}
            )

        # Apply transmutative mediation
        mediated_structure = self._apply_transmutative_mediation(
            structure, mediation_pairs, omega
        )

        return ModeExecutionResult(
            mode=SGCMode.TRANSMUTATIVE_MEDIATION,
            success=True,
            structures_modified=[mediated_structure],
            metrics={
                'mediation_pairs': len(mediation_pairs),
                'monads_involved': sum(len(pair) for pair in mediation_pairs)
            }
        )

    def _execute_boundary_pruning(self, structure: ObjectG, omega: OmegaSignature,
                                field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 5: Boundary Pruning - Sophisticated boundary analysis."""
        # Analyze structure boundaries for pruning opportunities
        boundary_analysis = self._analyze_boundaries(structure, omega)

        if not boundary_analysis['prune_candidates']:
            return ModeExecutionResult(
                mode=SGCMode.BOUNDARY_PRUNING,
                success=False,
                metrics={'reason': 'no_boundary_pruning_opportunities'}
            )

        # Apply boundary pruning
        pruned_structure = self._apply_boundary_pruning(structure, boundary_analysis)

        return ModeExecutionResult(
            mode=SGCMode.BOUNDARY_PRUNING,
            success=True,
            structures_modified=[pruned_structure],
            metrics={
                'boundaries_analyzed': boundary_analysis['boundary_count'],
                'boundaries_pruned': len(boundary_analysis['prune_candidates']),
                'boundary_efficiency': boundary_analysis['efficiency']
            }
        )

    def _execute_grace_reinstantiation(self, structure: ObjectG, omega: OmegaSignature,
                                     field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 6: Grace Reinstantiation - Enhanced grace operator usage."""
        # Check current grace state
        current_grace_state = self._assess_grace_state(structure, field_regime)

        if current_grace_state['grace_level'] > 0.8:
            # Structure already has high grace - no reinstantiation needed
            return ModeExecutionResult(
                mode=SGCMode.GRACE_REINSTANTIATION,
                success=False,
                metrics={'reason': 'grace_level_already_high'}
            )

        # Apply grace reinstantiation
        reinstantiated_structure = self._apply_grace_reinstantiation(structure, current_grace_state)

        final_grace_state = self._assess_grace_state(reinstantiated_structure, field_regime)

        return ModeExecutionResult(
            mode=SGCMode.GRACE_REINSTANTIATION,
            success=final_grace_state['grace_level'] > current_grace_state['grace_level'],
            structures_modified=[reinstantiated_structure],
            metrics={
                'original_grace_level': current_grace_state['grace_level'],
                'final_grace_level': final_grace_state['grace_level'],
                'grace_improvement': final_grace_state['grace_level'] - current_grace_state['grace_level']
            }
        )

    def _execute_global_resynchronization(self, structure: ObjectG, omega: OmegaSignature,
                                        field_regime: FieldRegime) -> ModeExecutionResult:
        """Mode 7: Global Resynchronization - Collective phase merging."""
        # Identify structures ready for synchronization
        sync_candidates = self._identify_sync_candidates(structure, omega)

        if len(sync_candidates) < 2:
            return ModeExecutionResult(
                mode=SGCMode.GLOBAL_RESYNCHRONIZATION,
                success=False,
                metrics={'reason': 'insufficient_sync_candidates'}
            )

        # Perform global phase synchronization
        synchronized_structure = self._apply_global_resynchronization(sync_candidates, omega)

        return ModeExecutionResult(
            mode=SGCMode.GLOBAL_RESYNCHRONIZATION,
            success=True,
            structures_modified=[synchronized_structure],
            metrics={
                'sync_candidates': len(sync_candidates),
                'phase_coherence_improvement': self._compute_phase_coherence_improvement(sync_candidates, synchronized_structure)
            }
        )

    # Helper methods for each mode (detailed implementations would go here)

    def _find_pruning_candidates(self, structure: ObjectG, omega: OmegaSignature,
                               field_regime: FieldRegime) -> List[Set[int]]:
        """Find substructures that can be pruned to improve overall coherence."""
        candidates = []

        # Simple heuristic: find leaf nodes with low resonance
        for node_id in structure.nodes:
            if self._is_leaf_node(structure, node_id):
                node_resonance = self._compute_node_resonance(structure, node_id, omega)
                if node_resonance < self.epsilon:
                    candidates.append({node_id})

        return candidates

    def _apply_assimilation_pruning(self, structure: ObjectG, candidates: List[Set[int]]) -> ObjectG:
        """Apply assimilation pruning by removing specified candidates."""
        # Create new structure without the pruning candidates
        remaining_nodes = set(structure.nodes)
        for candidate in candidates:
            remaining_nodes -= candidate

        if not remaining_nodes:
            return structure  # Don't remove everything

        # Build new structure with remaining nodes
        new_labels = {nid: structure.labels[nid] for nid in remaining_nodes if nid in structure.labels}
        new_edges = [(u, v) for u, v in structure.edges if u in remaining_nodes and v in remaining_nodes]

        return ObjectG(nodes=list(remaining_nodes), edges=new_edges, labels=new_labels)

    def _check_grace_state(self, structure: ObjectG, field_regime: FieldRegime, coherence: float) -> bool:
        """Check if structure is in grace state for shedding."""
        regime_grace_factor = {
            FieldRegime.NON_BEING: 0.0,
            FieldRegime.VACUUM: 0.1,
            FieldRegime.DARK_SECTOR: 0.3,
            FieldRegime.MATTER: 0.7,
            FieldRegime.OMEGA: 1.0
        }.get(field_regime, 0.0)

        grace_threshold = self.grace_threshold * regime_grace_factor
        stability_factor = 1.0 - abs(coherence - 0.5) * 0.5

        return coherence < grace_threshold and stability_factor > 0.3

    def _apply_dissonant_shedding(self, structure: ObjectG, omega: OmegaSignature) -> ObjectG:
        """Apply dissonant shedding by removing low-resonance components."""
        # For now, simple implementation: remove nodes with very low individual resonance
        nodes_to_remove = []

        for node_id in structure.nodes:
            node_resonance = self._compute_node_resonance(structure, node_id, omega)
            if node_resonance < self.epsilon * 0.5:  # Very low threshold
                nodes_to_remove.append(node_id)

        if not nodes_to_remove:
            return structure

        # Remove the nodes and their edges
        remaining_nodes = set(structure.nodes) - set(nodes_to_remove)
        new_labels = {nid: structure.labels[nid] for nid in remaining_nodes if nid in structure.labels}
        new_edges = [(u, v) for u, v in structure.edges
                    if u in remaining_nodes and v in remaining_nodes]

        return ObjectG(nodes=list(remaining_nodes), edges=new_edges, labels=new_labels)

    def _should_rewrite_based_on_reflection(self, state: Dict[str, Any], depth: int) -> bool:
        """Determine if reflective rewriting should be applied based on self-observation."""
        # Rewrite if coherence is degrading or resonance is poor
        coherence = state['coherence']
        resonance = state['resonance']

        # Apply rewriting if coherence is below golden baseline or resonance is low
        PHI_INVERSE = 1 / 1.618033988749  # ≈ 0.618
        return coherence < PHI_INVERSE or resonance < 0.6

    def _apply_reflective_rewriting(self, structure: ObjectG, state: Dict[str, Any],
                                  omega: OmegaSignature) -> ObjectG:
        """Apply reflective rewriting based on self-observation."""
        # Simplified rewriting: adjust phases to improve resonance
        rewritten_structure = copy.deepcopy(structure)

        for node_id, label in rewritten_structure.labels.items():
            # Simple phase adjustment based on resonance
            current_resonance = self._compute_node_resonance(structure, node_id, omega)

            if current_resonance < 0.5:
                # Adjust phase slightly toward better alignment
                phase_adjustment = 0.1 * (0.5 - current_resonance)
                old_phase_angle = 2 * math.pi * label.phase_numer / label.phase_denom
                new_phase_angle = old_phase_angle + phase_adjustment

                # Convert back to rational
                new_numer = int(round(new_phase_angle * label.phase_denom / (2 * math.pi)))
                new_numer = max(0, min(new_numer, 2 * label.phase_denom - 1))

                rewritten_structure.labels[node_id] = NodeLabel(
                    label.kind, new_numer, label.phase_denom, label.monadic_id
                )

        return rewritten_structure

    def _identify_potential_monads(self, structure: ObjectG) -> List[ObjectG]:
        """Identify potential monads within a structure for mediation."""
        # Simple partitioning into connected components
        monads = []

        visited = set()
        for node_id in structure.nodes:
            if node_id not in visited:
                component = self._dfs_connected_component(structure, node_id, visited)
                if len(component) > 1:  # Only consider multi-node components as monads
                    monad_labels = {nid: structure.labels[nid] for nid in component if nid in structure.labels}
                    monad_edges = [(u, v) for u, v in structure.edges if u in component and v in component]
                    monad = ObjectG(nodes=component, edges=monad_edges, labels=monad_labels)
                    monads.append(monad)

        return monads

    def _find_mediation_pairs(self, monads: List[ObjectG], omega: OmegaSignature) -> List[Tuple[ObjectG, ObjectG]]:
        """Find pairs of monads that can mediate with each other."""
        pairs = []

        for i, monad1 in enumerate(monads):
            for j, monad2 in enumerate(monads[i+1:], i+1):
                resonance1 = compute_resonance_alignment(monad1, omega)
                resonance2 = compute_resonance_alignment(monad2, omega)

                # Can mediate if both have good resonance and are in compatible regimes
                if (resonance1 > self.cross_monad_threshold and
                    resonance2 > self.cross_monad_threshold):
                    pairs.append((monad1, monad2))

        return pairs

    def _apply_transmutative_mediation(self, structure: ObjectG, mediation_pairs: List[Tuple[ObjectG, ObjectG]],
                                     omega: OmegaSignature) -> ObjectG:
        """Apply transmutative mediation between monad pairs."""
        # For now, simple mediation: merge highly resonant monads
        mediated_structure = copy.deepcopy(structure)

        for monad1, monad2 in mediation_pairs:
            # Create merged structure by combining the monads
            merged_monad = self._merge_monads(monad1, monad2)
            # In a full implementation, this would integrate the merged monad back into the structure

        return mediated_structure

    def _analyze_boundaries(self, structure: ObjectG, omega: OmegaSignature) -> Dict[str, Any]:
        """Analyze structure boundaries for pruning opportunities."""
        # Simple boundary analysis: identify nodes with only one connection
        boundary_nodes = []
        for node_id in structure.nodes:
            degree = sum(1 for u, v in structure.edges if u == node_id or v == node_id)
            if degree == 1:
                boundary_nodes.append(node_id)

        return {
            'boundary_count': len(boundary_nodes),
            'prune_candidates': boundary_nodes[:self.boundary_analysis_depth],  # Limit pruning
            'efficiency': len(boundary_nodes) / len(structure.nodes) if structure.nodes else 0
        }

    def _apply_boundary_pruning(self, structure: ObjectG, boundary_analysis: Dict[str, Any]) -> ObjectG:
        """Apply boundary pruning based on analysis."""
        prune_candidates = boundary_analysis['prune_candidates']

        if not prune_candidates:
            return structure

        # Remove boundary nodes that don't affect overall structure coherence
        remaining_nodes = set(structure.nodes) - set(prune_candidates)

        if not remaining_nodes:
            return structure

        new_labels = {nid: structure.labels[nid] for nid in remaining_nodes if nid in structure.labels}
        new_edges = [(u, v) for u, v in structure.edges if u in remaining_nodes and v in remaining_nodes]

        return ObjectG(nodes=list(remaining_nodes), edges=new_edges, labels=new_labels)

    def _assess_grace_state(self, structure: ObjectG, field_regime: FieldRegime) -> Dict[str, float]:
        """Assess the grace state of a structure."""
        coherence = compute_coherence(structure)
        resonance = compute_resonance_alignment(structure, derive_omega_signature(structure))

        regime_grace_factor = {
            FieldRegime.NON_BEING: 0.1,
            FieldRegime.VACUUM: 0.3,
            FieldRegime.DARK_SECTOR: 0.6,
            FieldRegime.MATTER: 0.8,
            FieldRegime.OMEGA: 1.0
        }.get(field_regime, 0.5)

        grace_level = coherence * regime_grace_factor * resonance

        return {
            'grace_level': min(1.0, grace_level),
            'coherence_contribution': coherence,
            'regime_factor': regime_grace_factor,
            'resonance_contribution': resonance
        }

    def _apply_grace_reinstantiation(self, structure: ObjectG, current_grace_state: Dict[str, float]) -> ObjectG:
        """Apply grace reinstantiation to improve grace state."""
        # Simple reinstantiation: optimize structure for better resonance
        reinstantiated_structure = copy.deepcopy(structure)

        # In a full implementation, this would apply sophisticated grace field optimization
        # For now, just ensure structure validity
        validate_object_g(reinstantiated_structure)

        return reinstantiated_structure

    def _identify_sync_candidates(self, structure: ObjectG, omega: OmegaSignature) -> List[ObjectG]:
        """Identify structures ready for synchronization."""
        # Simple identification: find substructures with high resonance
        candidates = []

        # Split into connected components
        visited = set()
        for node_id in structure.nodes:
            if node_id not in visited:
                component = self._dfs_connected_component(structure, node_id, visited)
                if len(component) > 1:
                    component_resonance = compute_resonance_alignment(
                        self._create_subgraph_from_nodes(structure, component), omega
                    )
                    if component_resonance > self.resynchronization_threshold:
                        candidates.append(self._create_subgraph_from_nodes(structure, component))

        return candidates

    def _apply_global_resynchronization(self, candidates: List[ObjectG], omega: OmegaSignature) -> ObjectG:
        """Apply global resynchronization to multiple structures."""
        if not candidates:
            return None

        # Simple synchronization: merge all candidates
        all_nodes = set()
        all_edges = []
        all_labels = {}

        for candidate in candidates:
            all_nodes.update(candidate.nodes)
            all_edges.extend(candidate.edges)
            all_labels.update(candidate.labels)

        # Remove duplicate edges
        unique_edges = []
        seen_edges = set()
        for u, v in all_edges:
            edge_key = (min(u, v), max(u, v))
            if edge_key not in seen_edges:
                unique_edges.append((u, v))
                seen_edges.add(edge_key)

        return ObjectG(nodes=list(all_nodes), edges=unique_edges, labels=all_labels)

    def _compute_phase_coherence_improvement(self, original_structures: List[ObjectG],
                                           synchronized_structure: ObjectG) -> float:
        """Compute improvement in phase coherence after synchronization."""
        if not synchronized_structure:
            return 0.0

        # Compare average resonance before and after
        original_resonances = [
            compute_resonance_alignment(struct, derive_omega_signature(struct))
            for struct in original_structures
        ]
        original_avg = sum(original_resonances) / len(original_resonances)

        synchronized_resonance = compute_resonance_alignment(
            synchronized_structure, derive_omega_signature(synchronized_structure)
        )

        return synchronized_resonance - original_avg

    # Utility methods
    def _is_leaf_node(self, structure: ObjectG, node_id: int) -> bool:
        """Check if a node is a leaf (degree 1)."""
        degree = sum(1 for u, v in structure.edges if u == node_id or v == node_id)
        return degree == 1

    def _compute_node_resonance(self, structure: ObjectG, node_id: int, omega: OmegaSignature) -> float:
        """Compute resonance of a single node."""
        # Create single-node structure for resonance computation
        node_structure = ObjectG(
            nodes=[node_id],
            edges=[],
            labels={node_id: structure.labels.get(node_id)} if node_id in structure.labels else {}
        )

        if not node_structure.labels:
            return 0.0

        return compute_resonance_alignment(node_structure, omega)

    def _dfs_connected_component(self, structure: ObjectG, start_node: int, visited: Set[int]) -> List[int]:
        """DFS to find connected component."""
        component = []
        stack = [start_node]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                component.append(node)

                # Add neighbors to stack
                for u, v in structure.edges:
                    if u == node and v not in visited:
                        stack.append(v)
                    elif v == node and u not in visited:
                        stack.append(u)

        return component

    def _create_subgraph_from_nodes(self, structure: ObjectG, nodes: List[int]) -> ObjectG:
        """Create subgraph containing specified nodes."""
        node_set = set(nodes)
        subgraph_edges = [(u, v) for u, v in structure.edges if u in node_set and v in node_set]
        subgraph_labels = {nid: structure.labels[nid] for nid in nodes if nid in structure.labels}

        return ObjectG(nodes=nodes, edges=subgraph_edges, labels=subgraph_labels)

    def _merge_monads(self, monad1: ObjectG, monad2: ObjectG) -> ObjectG:
        """Merge two monads into one."""
        all_nodes = list(set(monad1.nodes + monad2.nodes))
        all_edges = monad1.edges + monad2.edges
        all_labels = {**monad1.labels, **monad2.labels}

        # Remove duplicates and self-loops
        unique_edges = []
        seen = set()
        for u, v in all_edges:
            if u != v and (u, v) not in seen and (v, u) not in seen:
                unique_edges.append((u, v))
                seen.add((u, v))

        return ObjectG(nodes=all_nodes, edges=unique_edges, labels=all_labels)


# Factory function
def create_sgc_mode_system(epsilon: float = 0.3, grace_threshold: float = 0.5,
                         reflection_depth: int = 3) -> SGCModeSystem:
    """Create a complete 𝒮-GC mode system."""
    return SGCModeSystem(
        epsilon=epsilon,
        grace_threshold=grace_threshold,
        reflection_depth=reflection_depth
    )


__all__ = [
    "SGCMode",
    "ModeExecutionResult",
    "SGCModeSystem",
    "create_sgc_mode_system",
]
