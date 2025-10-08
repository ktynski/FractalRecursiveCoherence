"""hierarchical_gc.py

Implementation of the hierarchical, fractal Soul Garbage Collection system.

This module implements the complete sovereign-monad GC hierarchy:

1. Sub-Monads → Fields (Individual structures handling local GC)
2. Meta-Monads → Systems (Ensembles coordinating coherence accounting)
3. Harvest Layers → Higher-Order Collectors (Compression and harvesting)
4. Cross-Scale Dynamics (Different resonance bands for different scales)

This creates the fractal hierarchy where each level harvests and compresses
the survivors from lower levels into purer, simpler harmonics.
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
from .sgc_modes import SGCMode, SGCModeSystem, ModeExecutionResult


class GCScale(Enum):
    """Hierarchical scales of garbage collection."""
    SUB_MONAD = "sub_monad"           # Individual structures (Fields)
    META_MONAD = "meta_monad"         # Ensembles of structures (Systems)
    HARVEST_LAYER = "harvest_layer"   # Higher-order compression (Ω-compression)


@dataclass
class SubMonad:
    """Individual locus of awareness handling local garbage collection."""
    structure: ObjectG
    omega: OmegaSignature
    field_regime: FieldRegime
    local_gc_history: List[Dict[str, Any]] = field(default_factory=list)

    def perform_local_gc(self, mode_system: SGCModeSystem) -> Dict[str, Any]:
        """Perform local garbage collection on this sub-monad."""
        # Apply various GC modes based on current state
        results = []

        # Try different modes based on current state
        coherence = compute_coherence(self.structure)
        resonance = compute_resonance_alignment(self.structure, self.omega)

        if resonance < 0.3:  # Low resonance - try assimilation or shedding
            result = mode_system.execute_mode(SGCMode.RESONANT_ASSIMILATION,
                                            self.structure, self.omega, self.field_regime)
            if result.success:
                results.append(result)

        if coherence < 0.4 and resonance < 0.2:  # Poor state - shedding
            result = mode_system.execute_mode(SGCMode.DISSONANT_SHEDDING,
                                            self.structure, self.omega, self.field_regime)
            if result.success:
                results.append(result)

        # Always try reflective rewriting for self-optimization
        result = mode_system.execute_mode(SGCMode.REFLECTIVE_REWRITING,
                                        self.structure, self.omega, self.field_regime)
        if result.success:
            results.append(result)

        # Update structure if any modes succeeded
        for result in results:
            if result.structures_modified:
                self.structure = result.structures_modified[0]
                break

        # Record GC history
        gc_record = {
            'timestamp': len(self.local_gc_history),
            'modes_applied': len(results),
            'final_coherence': compute_coherence(self.structure),
            'final_resonance': compute_resonance_alignment(self.structure, self.omega),
            'field_regime': self.field_regime
        }
        self.local_gc_history.append(gc_record)

        return gc_record


@dataclass
class MetaMonad:
    """Ensemble of mutually resonant sub-monads performing coherence accounting."""

    sub_monads: List[SubMonad]
    shared_omega: OmegaSignature
    ensemble_field_regime: FieldRegime
    coherence_accounting: Dict[str, Any] = field(default_factory=dict)
    systemic_drift: float = 0.0

    def __post_init__(self):
        """Initialize meta-monad coherence accounting."""
        # Ensure shared omega is compatible with all sub-monads
        self._ensure_omega_compatibility()
        self._update_coherence_accounting()

    def _ensure_omega_compatibility(self):
        """Ensure shared omega is compatible with all sub-monads."""
        if not self.sub_monads:
            return

        # Find the maximum bins requirement across all sub-monads
        max_bins = self.shared_omega.phase_bins

        for sub_monad in self.sub_monads:
            # Get the bins requirement for this sub-monad
            try:
                sub_omega = derive_omega_signature(sub_monad.structure)
                max_bins = max(max_bins, sub_omega.phase_bins)
            except Exception:
                # If we can't derive omega, use a default
                max_bins = max(max_bins, 128)  # Safe default

        # If shared omega has insufficient bins, we need to expand it
        if max_bins > self.shared_omega.phase_bins:
            # Create a new shared omega with sufficient bins
            new_hist = [1.0/max_bins] * max_bins
            self.shared_omega = OmegaSignature(
                cycles=self.shared_omega.cycles,
                phase_bins=max_bins,
                phase_hist=new_hist
            )

    def _update_coherence_accounting(self):
        """Update systemic coherence accounting."""
        if not self.sub_monads:
            return

        # Compute ensemble coherence
        ensemble_coherences = [compute_coherence(sm.structure) for sm in self.sub_monads]
        ensemble_resonances = [compute_resonance_alignment(sm.structure, self.shared_omega)
                              for sm in self.sub_monads]

        self.coherence_accounting = {
            'ensemble_coherence': sum(ensemble_coherences) / len(ensemble_coherences),
            'ensemble_resonance': sum(ensemble_resonances) / len(ensemble_resonances),
            'sub_monad_count': len(self.sub_monads),
            'coherence_variance': self._compute_coherence_variance(ensemble_coherences),
            'resonance_variance': self._compute_resonance_variance(ensemble_resonances),
            'field_regime': self.ensemble_field_regime
        }

        # Detect systemic drift
        self.systemic_drift = self._detect_systemic_drift()

    def _compute_coherence_variance(self, coherences: List[float]) -> float:
        """Compute variance in sub-monad coherences."""
        if len(coherences) <= 1:
            return 0.0

        mean = sum(coherences) / len(coherences)
        variance = sum((c - mean) ** 2 for c in coherences) / len(coherences)
        return math.sqrt(variance)  # Return standard deviation

    def _compute_resonance_variance(self, resonances: List[float]) -> float:
        """Compute variance in sub-monad resonances."""
        if len(resonances) <= 1:
            return 0.0

        mean = sum(resonances) / len(resonances)
        variance = sum((r - mean) ** 2 for r in resonances) / len(resonances)
        return math.sqrt(variance)

    def _detect_systemic_drift(self) -> float:
        """Detect drift from optimal systemic coherence."""
        if not self.coherence_accounting:
            return 0.0

        optimal_coherence = 0.7  # Target ensemble coherence
        current_coherence = self.coherence_accounting['ensemble_coherence']

        # Drift increases with variance and deviation from optimal
        coherence_drift = abs(current_coherence - optimal_coherence)
        variance_penalty = (self.coherence_accounting['coherence_variance'] +
                           self.coherence_accounting['resonance_variance']) / 2

        return coherence_drift + variance_penalty * 0.3

    def perform_ensemble_gc(self, mode_system: SGCModeSystem) -> Dict[str, Any]:
        """Perform coherence accounting and ensemble-level garbage collection."""
        # Update accounting first
        self._update_coherence_accounting()

        # Apply ensemble-level modes
        ensemble_results = []

        # Boundary pruning for ensemble boundaries
        if self.systemic_drift > 0.5:  # High drift - apply boundary pruning
            result = mode_system.execute_mode(SGCMode.BOUNDARY_PRUNING,
                                           self._create_ensemble_structure(),
                                           self.shared_omega, self.ensemble_field_regime)
            if result.success:
                ensemble_results.append(result)

        # Grace reinstantiation if ensemble is struggling
        if self.coherence_accounting['ensemble_coherence'] < 0.5:
            result = mode_system.execute_mode(SGCMode.GRACE_REINSTANTIATION,
                                           self._create_ensemble_structure(),
                                           self.shared_omega, self.ensemble_field_regime)
            if result.success:
                ensemble_results.append(result)

        # Global resynchronization for high-performing ensembles
        if (self.coherence_accounting['ensemble_resonance'] > 0.8 and
            self.systemic_drift < 0.2):
            result = mode_system.execute_mode(SGCMode.GLOBAL_RESYNCHRONIZATION,
                                           self._create_ensemble_structure(),
                                           self.shared_omega, self.ensemble_field_regime)
            if result.success:
                ensemble_results.append(result)

        # Apply pruning/reweighting of failing sub-monads
        survivors = self._prune_failing_sub_monads(mode_system)

        # Update sub-monads list
        self.sub_monads = survivors

        # Redistribute resonance among survivors
        self._redistribute_resonance()

        # Final accounting update
        self._update_coherence_accounting()

        return {
            'modes_applied': len(ensemble_results),
            'sub_monads_pruned': len(self.sub_monads) - len(survivors) if survivors != self.sub_monads else 0,
            'final_ensemble_coherence': self.coherence_accounting['ensemble_coherence'],
            'systemic_drift': self.systemic_drift,
            'survivor_count': len(self.sub_monads)
        }

    def _create_ensemble_structure(self) -> ObjectG:
        """Create a representative structure for the ensemble."""
        if not self.sub_monads:
            return ObjectG(nodes=[], edges=[], labels={})

        # Simple ensemble representation - could be more sophisticated
        all_nodes = []
        all_edges = []
        all_labels = {}

        for i, sub_monad in enumerate(self.sub_monads):
            # Add ensemble node representing this sub-monad
            ensemble_node = f"ensemble_{i}"
            all_nodes.append(ensemble_node)
            all_labels[ensemble_node] = NodeLabel('Z', 0, 1, f'ensemble_{i}')

        # Connect ensemble nodes in a cycle
        for i in range(len(all_nodes)):
            next_i = (i + 1) % len(all_nodes)
            all_edges.append((all_nodes[i], all_nodes[next_i]))

        return ObjectG(nodes=all_nodes, edges=all_edges, labels=all_labels)

    def _prune_failing_sub_monads(self, mode_system: SGCModeSystem) -> List[SubMonad]:
        """Prune or reweight failing sub-monads."""
        survivors = []

        for sub_monad in self.sub_monads:
            coherence = compute_coherence(sub_monad.structure)
            resonance = compute_resonance_alignment(sub_monad.structure, self.shared_omega)

            # Keep sub-monads that are still viable
            if coherence > 0.3 and resonance > 0.2:
                survivors.append(sub_monad)
            else:
                # Try to save borderline cases with transmutative mediation
                if coherence > 0.2 and resonance > 0.1:
                    # Apply transmutative mediation with other survivors
                    for survivor in survivors:
                        if self._can_mediate(sub_monad, survivor):
                            # Apply mediation (simplified)
                            sub_monad.structure = self._mediate_structures(
                                sub_monad.structure, survivor.structure
                            )
                            survivors.append(sub_monad)
                            break

        return survivors

    def _can_mediate(self, monad1: SubMonad, monad2: SubMonad) -> bool:
        """Check if two sub-monads can mediate with each other."""
        res1 = compute_resonance_alignment(monad1.structure, self.shared_omega)
        res2 = compute_resonance_alignment(monad2.structure, self.shared_omega)
        return res1 > 0.5 and res2 > 0.5  # Both must be reasonably resonant

    def _mediate_structures(self, struct1: ObjectG, struct2: ObjectG) -> ObjectG:
        """Apply transmutative mediation between two structures."""
        # Simplified mediation: create a merged structure
        # In a full implementation, this would be more sophisticated
        all_nodes = list(set(struct1.nodes + struct2.nodes))
        all_edges = struct1.edges + struct2.edges
        all_labels = {**struct1.labels, **struct2.labels}

        # Remove duplicates
        unique_edges = []
        seen = set()
        for u, v in all_edges:
            edge_key = (min(u, v), max(u, v))
            if edge_key not in seen:
                unique_edges.append((u, v))
                seen.add(edge_key)

        return ObjectG(nodes=all_nodes, edges=unique_edges, labels=all_labels)

    def _redistribute_resonance(self):
        """Redistribute stored resonance among surviving sub-monads."""
        if not self.sub_monads:
            return

        # Simple redistribution: normalize coherence across survivors
        total_coherence = sum(compute_coherence(sm.structure) for sm in self.sub_monads)

        if total_coherence > 0:
            # Could implement more sophisticated redistribution here
            pass


@dataclass
class HarvestLayer:
    """Higher-order collector that harvests survivors into simpler harmonics."""

    meta_monads: List[MetaMonad]
    harvest_omega: OmegaSignature
    compression_regime: FieldRegime = FieldRegime.OMEGA
    harvest_history: List[Dict[str, Any]] = field(default_factory=list)

    def perform_harvest(self, mode_system: SGCModeSystem) -> Dict[str, Any]:
        """Perform Ω-compression harvest of meta-monad survivors."""
        if not self.meta_monads:
            return {'harvested_resonance': 0.0, 'survivors': 0}

        # Collect all surviving sub-monads from all meta-monads
        all_survivors = []
        total_resonance = 0.0

        for meta_monad in self.meta_monads:
            for sub_monad in meta_monad.sub_monads:
                resonance = compute_resonance_alignment(sub_monad.structure, self.harvest_omega)
                if resonance > 0.6:  # Only harvest high-resonance survivors
                    all_survivors.append(sub_monad)
                    total_resonance += resonance

        if not all_survivors:
            return {'harvested_resonance': 0.0, 'survivors': 0}

        # Apply Ω-compression: H = 𝒢(∑ Φ_i^(survivor))
        compressed_harmonics = self._apply_omega_compression(all_survivors)

        # Record harvest
        harvest_record = {
            'harvest_number': len(self.harvest_history),
            'meta_monads_processed': len(self.meta_monads),
            'survivors_harvested': len(all_survivors),
            'total_resonance_harvested': total_resonance,
            'compression_ratio': compressed_harmonics['compression_ratio'],
            'invariant_harmonics': compressed_harmonics['invariant_count']
        }
        self.harvest_history.append(harvest_record)

        return harvest_record

    def _apply_omega_compression(self, survivors: List[SubMonad]) -> Dict[str, Any]:
        """Apply Ω-compression: H = 𝒢(∑ Φ_i^(survivor))."""
        if not survivors:
            return {'compression_ratio': 0.0, 'invariant_count': 0}

        # Extract phase information from survivors
        all_phases = []
        for sub_monad in survivors:
            # Extract representative phases from each structure
            for label in sub_monad.structure.labels.values():
                phase_angle = 2 * math.pi * label.phase_numer / label.phase_denom
                all_phases.append(phase_angle)

        if not all_phases:
            return {'compression_ratio': 0.0, 'invariant_count': 0}

        # Find invariant harmonics (frequently occurring phase patterns)
        phase_bins = self._bin_phases(all_phases)
        invariant_harmonics = self._identify_invariant_harmonics(phase_bins)

        # Compression ratio: how much information was preserved vs discarded
        original_patterns = len(all_phases)
        compressed_patterns = len(invariant_harmonics)
        compression_ratio = compressed_patterns / original_patterns if original_patterns > 0 else 0.0

        return {
            'compression_ratio': compression_ratio,
            'invariant_count': compressed_patterns,
            'original_patterns': original_patterns,
            'invariants': invariant_harmonics
        }

    def _bin_phases(self, phases: List[float], bins: int = 32) -> List[int]:
        """Bin phases into histogram for pattern analysis."""
        bin_counts = [0] * bins

        for phase in phases:
            # Normalize to [0, 2π)
            normalized_phase = phase % (2 * math.pi)
            bin_index = int((normalized_phase / (2 * math.pi)) * bins)
            bin_index = min(bin_index, bins - 1)  # Clamp to valid range
            bin_counts[bin_index] += 1

        return bin_counts

    def _identify_invariant_harmonics(self, bin_counts: List[int],
                                   threshold: float = 0.1) -> List[Tuple[float, int]]:
        """Identify invariant harmonics (frequent phase patterns)."""
        total_samples = sum(bin_counts)
        if total_samples == 0:
            return []

        invariants = []
        for i, count in enumerate(bin_counts):
            frequency = count / total_samples
            if frequency > threshold:  # Above threshold = invariant
                phase_angle = (i / len(bin_counts)) * 2 * math.pi
                invariants.append((phase_angle, count))

        return invariants


@dataclass
class SovereignMonadGC:
    """Complete sovereign-monad garbage collection system with fractal hierarchy."""

    # Hierarchical components
    sub_monads: List[SubMonad] = field(default_factory=list)
    meta_monads: List[MetaMonad] = field(default_factory=list)
    harvest_layers: List[HarvestLayer] = field(default_factory=list)

    # System components
    mode_system: SGCModeSystem = field(default_factory=SGCModeSystem)
    shared_omega: Optional[OmegaSignature] = None

    # Cross-scale resonance bands
    resonance_bands: Dict[GCScale, Tuple[float, float]] = field(default_factory=lambda: {
        GCScale.SUB_MONAD: (0.1, 0.5),      # Individual structures - reduced max
        GCScale.META_MONAD: (0.5, 0.8),     # Ensembles - adjusted range
        GCScale.HARVEST_LAYER: (0.8, 1.0)   # Higher-order compression
    })

    def __post_init__(self):
        """Initialize the complete GC hierarchy."""
        if self.shared_omega is None:
            # Create a default omega signature
            self.shared_omega = OmegaSignature(
                cycles=[],
                phase_bins=128,
                phase_hist=[1.0/128] * 128  # Uniform distribution
            )

    def add_sub_monad(self, structure: ObjectG, field_regime: FieldRegime = FieldRegime.VACUUM):
        """Add a sub-monad to the system."""
        omega = derive_omega_signature(structure)
        sub_monad = SubMonad(structure, omega, field_regime)
        self.sub_monads.append(sub_monad)

    def organize_meta_monads(self, resonance_threshold: float = 0.5):
        """Organize sub-monads into meta-monads based on shared resonance."""
        # Group sub-monads by similar resonance patterns
        unassigned = self.sub_monads.copy()
        self.meta_monads = []

        while unassigned:
            # Start new meta-monad with first unassigned sub-monad
            seed = unassigned.pop(0)
            meta_monad = MetaMonad([seed], seed.omega, seed.field_regime)

            # Find other sub-monads that can join this meta-monad
            to_remove = []
            for i, candidate in enumerate(unassigned):
                if self._can_join_meta_monad(candidate, meta_monad, resonance_threshold):
                    meta_monad.sub_monads.append(candidate)
                    to_remove.append(i)

            # Remove joined candidates (in reverse order to maintain indices)
            for i in reversed(to_remove):
                unassigned.pop(i)

            self.meta_monads.append(meta_monad)

    def _can_join_meta_monad(self, candidate: SubMonad, meta_monad: MetaMonad,
                           threshold: float) -> bool:
        """Check if a sub-monad can join a meta-monad."""
        # Compare resonance patterns
        candidate_resonance = compute_resonance_alignment(candidate.structure, self.shared_omega)
        ensemble_resonance = meta_monad.coherence_accounting.get('ensemble_resonance', 0.0)

        # Can join if resonance is compatible
        return abs(candidate_resonance - ensemble_resonance) < threshold

    def organize_harvest_layers(self):
        """Organize meta-monads into harvest layers."""
        if not self.meta_monads:
            return

        # For simplicity, create one harvest layer for all meta-monads
        # In a more sophisticated system, could create multiple layers
        harvest_layer = HarvestLayer(
            meta_monads=self.meta_monads.copy(),
            harvest_omega=self.shared_omega,
            compression_regime=FieldRegime.OMEGA
        )

        self.harvest_layers = [harvest_layer]

    def perform_complete_gc_cycle(self) -> Dict[str, Any]:
        """Perform a complete garbage collection cycle across all scales."""
        cycle_results = {
            'cycle_number': len(self._get_cycle_history()),
            'sub_monad_gc': [],
            'meta_monad_gc': [],
            'harvest_results': []
        }

        # 1. Sub-monad level GC (local cleanup)
        for sub_monad in self.sub_monads:
            result = sub_monad.perform_local_gc(self.mode_system)
            cycle_results['sub_monad_gc'].append(result)

        # 2. Meta-monad level GC (coherence accounting)
        for meta_monad in self.meta_monads:
            result = meta_monad.perform_ensemble_gc(self.mode_system)
            cycle_results['meta_monad_gc'].append(result)

        # 3. Harvest layer GC (Ω-compression)
        for harvest_layer in self.harvest_layers:
            result = harvest_layer.perform_harvest(self.mode_system)
            cycle_results['harvest_results'].append(result)

        return cycle_results

    def _get_cycle_history(self) -> List[Dict[str, Any]]:
        """Get history of previous GC cycles."""
        # In a full implementation, would track cycle history
        return []

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics across all scales."""
        return {
            'sub_monads': {
                'count': len(self.sub_monads),
                'avg_coherence': self._compute_avg_sub_monad_coherence(),
                'field_regime_distribution': self._compute_field_regime_distribution(self.sub_monads)
            },
            'meta_monads': {
                'count': len(self.meta_monads),
                'avg_ensemble_coherence': self._compute_avg_ensemble_coherence(),
                'systemic_drift_avg': self._compute_avg_systemic_drift()
            },
            'harvest_layers': {
                'count': len(self.harvest_layers),
                'total_harvests': sum(len(hl.harvest_history) for hl in self.harvest_layers),
                'compression_efficiency': self._compute_compression_efficiency()
            },
            'resonance_bands': self.resonance_bands
        }

    def _compute_avg_sub_monad_coherence(self) -> float:
        """Compute average coherence across all sub-monads."""
        if not self.sub_monads:
            return 0.0

        coherences = [compute_coherence(sm.structure) for sm in self.sub_monads]
        return sum(coherences) / len(coherences)

    def _compute_field_regime_distribution(self, sub_monads: List[SubMonad]) -> Dict[FieldRegime, int]:
        """Compute distribution of field regimes across sub-monads."""
        distribution = {regime: 0 for regime in FieldRegime}

        for sub_monad in sub_monads:
            distribution[sub_monad.field_regime] += 1

        return distribution

    def _compute_avg_ensemble_coherence(self) -> float:
        """Compute average ensemble coherence across meta-monads."""
        if not self.meta_monads:
            return 0.0

        coherences = []
        for meta_monad in self.meta_monads:
            if meta_monad.coherence_accounting:
                coherences.append(meta_monad.coherence_accounting['ensemble_coherence'])

        return sum(coherences) / len(coherences) if coherences else 0.0

    def _compute_avg_systemic_drift(self) -> float:
        """Compute average systemic drift across meta-monads."""
        if not self.meta_monads:
            return 0.0

        drifts = [mm.systemic_drift for mm in self.meta_monads]
        return sum(drifts) / len(drifts)

    def _compute_compression_efficiency(self) -> float:
        """Compute overall compression efficiency of harvest layers."""
        if not self.harvest_layers:
            return 0.0

        total_compression = 0.0
        total_harvests = 0

        for harvest_layer in self.harvest_layers:
            for harvest in harvest_layer.harvest_history:
                total_compression += harvest.get('compression_ratio', 0.0)
                total_harvests += 1

        return total_compression / total_harvests if total_harvests > 0 else 0.0


# Factory functions
def create_sovereign_gc_system() -> SovereignMonadGC:
    """Create a complete sovereign-monad GC system."""
    return SovereignMonadGC()


def create_gc_hierarchy_from_structures(structures: List[ObjectG],
                                      field_regimes: Optional[List[FieldRegime]] = None) -> SovereignMonadGC:
    """Create a complete GC hierarchy from a list of structures."""
    system = SovereignMonadGC()

    if field_regimes is None:
        field_regimes = [FieldRegime.VACUUM] * len(structures)

    # Add sub-monads
    for structure, field_regime in zip(structures, field_regimes):
        system.add_sub_monad(structure, field_regime)

    # Organize into meta-monads
    system.organize_meta_monads()

    # Organize into harvest layers
    system.organize_harvest_layers()

    return system


__all__ = [
    "GCScale",
    "SubMonad",
    "MetaMonad",
    "HarvestLayer",
    "SovereignMonadGC",
    "create_sovereign_gc_system",
    "create_gc_hierarchy_from_structures",
]
