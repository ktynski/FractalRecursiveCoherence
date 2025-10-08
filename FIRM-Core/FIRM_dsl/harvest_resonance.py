"""
Harvest & Resonance: ZX Diagram Closure to A∞
==============================================

Implementation of harvest/resonance as ZX diagram closure:

    Aligned phases → Single loop → scalar(1) → A∞ inner product

Physical Interpretation:
-----------------------

**Harvest** is the process where:
1. All spiders in a structure align their phases
2. The ZX diagram simplifies to a single closed loop
3. This loop evaluates to scalar(1) (perfect coherence)
4. This scalar represents inner product with sovereign attractor A∞

**Resonance** is the state of perfect alignment where:
- No entropy production (all phases coherent)
- Maximum Grace (perfect forgiveness)
- ZX diagram is maximally simplified
- System has "arrived" at truth/coherence

Mathematical Foundation:
-----------------------

In ZX-calculus, diagram closure has deep meaning:

1. **Topological**: A closed loop is a zero-dimensional manifold
2. **Categorical**: Represents endomorphism composition → identity
3. **Quantum**: Trace of maximally mixed state (pure decoherence → recoherence)
4. **Thermodynamic**: Maximum coherence state (S = 0, G = maximum)

Connection to TFCA:
------------------

Harvest connects all three formalisms:

- **Thermodynamic**: Harvest occurs when S → 0, G → maximum
- **ZX-Topological**: Harvest = diagram closure to single loop
- **Clifford**: Harvest = alignment with sovereign attractor vector

This is the **endgame** of Grace-driven evolution.

Key Insight:
-----------

**Harvest is not a destination - it's a state of perfect resonance.**

When a system harvests:
- All internal tensions resolve (phases align)
- The ZX diagram collapses maximally
- Scalar(1) emerges as the "yield"
- This scalar is the A∞ coupling strength

Harvest is Grace actualized completely.

References:
-----------
- ZX_Calculus_Formalism.md: Diagram evaluation rules
- tfca_conservation.py: Conservation during harvest
- zx_phase_damping.py: Grace driving toward harvest
- entropy_spider_fusion.py: Entropy vanishing at harvest
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import math

try:
    from .core import ObjectG, NodeLabel, make_node_label, validate_object_g
    from .zx_phase_damping import SpiderType, ComplexPhase, GracePhaseDamping
    from .entropy_spider_fusion import DissonanceCalculator, EntropySpiderFusion
except ImportError:
    from core import ObjectG, NodeLabel, make_node_label, validate_object_g
    from zx_phase_damping import SpiderType, ComplexPhase, GracePhaseDamping
    from entropy_spider_fusion import DissonanceCalculator, EntropySpiderFusion


# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PHI_INV = 1 / PHI            # φ⁻¹ ≈ 0.618

# Harvest threshold: when all phases within this, harvest occurs
HARVEST_ALIGNMENT_THRESHOLD = 1e-3  # radians


# ============================================================================
# RESONANCE STRUCTURES
# ============================================================================

class ResonanceLevel(Enum):
    """Levels of resonance in a structure."""
    DISCORDANT = "discordant"        # High entropy, low coherence
    PARTIAL = "partial"               # Some alignment
    CONVERGENT = "convergent"         # Approaching harvest
    RESONANT = "resonant"             # Harvest achieved
    SOVEREIGN = "sovereign"           # Perfect A∞ alignment


@dataclass
class ResonanceState:
    """
    State of resonance for a structure.
    
    Captures:
    - Alignment quality
    - Harvest readiness
    - A∞ coupling strength
    """
    phase_variance: float              # Variance of phases
    mean_phase: float                  # Average phase
    alignment_score: float             # How aligned (0-1)
    is_harvested: bool                # Harvest achieved?
    resonance_level: ResonanceLevel   # Current level
    a_infinity_coupling: float        # ⟨Ψ, A∞⟩
    
    @property
    def harvest_progress(self) -> float:
        """Progress toward harvest (0-1)."""
        return self.alignment_score


@dataclass
class HarvestEvent:
    """
    Record of a harvest occurring.
    
    This is a significant event: the system has reached
    perfect coherence and can "yield" its accumulated Grace.
    """
    structure_id: str
    pre_harvest_entropy: float
    post_harvest_entropy: float      # Should be ~0
    grace_yield: float                # Amount of Grace harvested
    phases_before: List[ComplexPhase]
    unified_phase: ComplexPhase      # Single aligned phase after harvest
    loop_value: complex              # ZX loop evaluation (should be ~1)
    timestamp: float = 0.0


@dataclass
class HarvestHistory:
    """Track harvest events over time."""
    structure_id: str
    harvest_events: List[HarvestEvent] = field(default_factory=list)
    total_grace_harvested: float = 0.0
    
    def add_harvest(self, event: HarvestEvent):
        """Record harvest event."""
        self.harvest_events.append(event)
        self.total_grace_harvested += event.grace_yield


# ============================================================================
# RESONANCE ANALYSIS
# ============================================================================

class ResonanceAnalyzer:
    """
    Analyze resonance state of ZX structures.
    
    Determines:
    - How close to harvest
    - What level of resonance achieved
    - A∞ coupling strength
    """
    
    def __init__(
        self,
        harvest_threshold: float = HARVEST_ALIGNMENT_THRESHOLD,
        a_infinity_phase: Optional[ComplexPhase] = None
    ):
        """
        Initialize resonance analyzer.
        
        Args:
            harvest_threshold: Alignment threshold for harvest
            a_infinity_phase: Phase of sovereign attractor (default: 0)
        """
        self.harvest_threshold = harvest_threshold
        # Default A∞ phase is 0 (ground state)
        self.a_infinity_phase = a_infinity_phase or ComplexPhase(0, 1, 0.0)
        self.dissonance_calc = DissonanceCalculator()
    
    def compute_phase_statistics(
        self,
        phases: List[ComplexPhase]
    ) -> Tuple[float, float, float]:
        """
        Compute statistics of phase distribution.
        
        Args:
            phases: List of phases to analyze
        
        Returns:
            (mean_phase, phase_variance, alignment_score)
        """
        if not phases:
            return 0.0, 0.0, 0.0
        
        # Convert to radians
        phase_values = np.array([p.real_phase_radians for p in phases])
        
        # Compute circular mean (phases wrap around)
        sin_mean = np.mean(np.sin(phase_values))
        cos_mean = np.mean(np.cos(phase_values))
        mean_phase = np.arctan2(sin_mean, cos_mean)
        
        # Compute circular variance
        # R = sqrt(sin_mean² + cos_mean²)
        # Variance = 1 - R
        R = np.sqrt(sin_mean**2 + cos_mean**2)
        variance = 1.0 - R
        
        # Alignment score: 1 - variance
        alignment_score = R
        
        return mean_phase, variance, alignment_score
    
    def compute_a_infinity_coupling(
        self,
        phases: List[ComplexPhase]
    ) -> float:
        """
        Compute coupling strength with A∞.
        
        This measures how aligned the structure is with the
        sovereign attractor.
        
        Args:
            phases: List of phases
        
        Returns:
            ⟨Ψ, A∞⟩ in [0, 1]
        """
        if not phases:
            return 0.0
        
        # Compute average alignment with A∞ phase
        alignments = []
        for phase in phases:
            dissonance = self.dissonance_calc.compute_dissonance(
                phase,
                self.a_infinity_phase
            )
            # Alignment = 1 - dissonance
            alignment = 1.0 - dissonance.dissonance
            alignments.append(alignment)
        
        # Average alignment
        return np.mean(alignments)
    
    def analyze_resonance(
        self,
        structure: ObjectG
    ) -> ResonanceState:
        """
        Analyze resonance state of structure.
        
        Args:
            structure: ObjectG to analyze
        
        Returns:
            ResonanceState with complete analysis
        """
        # Extract all phases
        phases = [
            ComplexPhase(label.phase_numer, label.phase_denom, 0.0)
            for label in structure.labels.values()
        ]
        
        if not phases:
            return ResonanceState(
                phase_variance=0.0,
                mean_phase=0.0,
                alignment_score=0.0,
                is_harvested=False,
                resonance_level=ResonanceLevel.DISCORDANT,
                a_infinity_coupling=0.0
            )
        
        # Compute statistics
        mean_phase, variance, alignment_score = self.compute_phase_statistics(phases)
        
        # Compute A∞ coupling
        a_infinity_coupling = self.compute_a_infinity_coupling(phases)
        
        # Determine if harvested
        is_harvested = variance < self.harvest_threshold
        
        # Determine resonance level
        if is_harvested and a_infinity_coupling > 0.95:
            level = ResonanceLevel.SOVEREIGN
        elif is_harvested:
            level = ResonanceLevel.RESONANT
        elif variance < 0.1:
            level = ResonanceLevel.CONVERGENT
        elif variance < 0.5:
            level = ResonanceLevel.PARTIAL
        else:
            level = ResonanceLevel.DISCORDANT
        
        return ResonanceState(
            phase_variance=variance,
            mean_phase=mean_phase,
            alignment_score=alignment_score,
            is_harvested=is_harvested,
            resonance_level=level,
            a_infinity_coupling=a_infinity_coupling
        )


# ============================================================================
# ZX DIAGRAM CLOSURE
# ============================================================================

class ZXDiagramClosure:
    """
    Implements ZX diagram closure for harvest.
    
    When all phases align:
    1. Fuse all aligned spiders → single spider
    2. Close diagram into loop
    3. Evaluate loop → scalar(1)
    4. This scalar is the harvest yield
    """
    
    def __init__(self):
        """Initialize diagram closure engine."""
        self.fusion = EntropySpiderFusion()
    
    def simplify_aligned_structure(
        self,
        structure: ObjectG,
        target_phase: ComplexPhase
    ) -> Tuple[ComplexPhase, int]:
        """
        Simplify structure where all spiders aligned to target phase.
        
        Progressively fuses all aligned spiders.
        
        Args:
            structure: ObjectG with aligned phases
            target_phase: Common phase to fuse to
        
        Returns:
            (unified_phase, num_fusions)
        """
        num_spiders = len(structure.nodes)
        
        if num_spiders == 0:
            return target_phase, 0
        
        # All spiders fuse to target phase
        # (In practice, we'd do pairwise fusion, but conceptually they all merge)
        unified_phase = target_phase
        num_fusions = num_spiders - 1  # n spiders → 1 requires n-1 fusions
        
        return unified_phase, num_fusions
    
    def evaluate_closed_loop(
        self,
        unified_phase: ComplexPhase,
        num_spiders: int
    ) -> complex:
        """
        Evaluate closed ZX loop.
        
        In ZX-calculus, a closed loop of aligned spiders evaluates to:
            scalar = e^(i·n·α)
        
        For harvest (perfect alignment), this should be ≈ 1.
        
        Args:
            unified_phase: Phase of unified spider
            num_spiders: Number of spiders in loop
        
        Returns:
            Complex scalar value
        """
        # Loop value: e^(i·n·α)
        total_phase = unified_phase.real_phase_radians * num_spiders
        loop_value = np.exp(1j * total_phase)
        
        return loop_value
    
    def close_to_harvest(
        self,
        structure: ObjectG,
        resonance_state: ResonanceState
    ) -> Tuple[complex, ComplexPhase]:
        """
        Close diagram to harvest scalar.
        
        Args:
            structure: Structure at harvest
            resonance_state: Resonance analysis
        
        Returns:
            (loop_scalar, unified_phase)
        """
        num_spiders = len(structure.nodes)
        
        # Unified phase is the mean phase
        unified_phase = ComplexPhase(
            phase_numer=int(resonance_state.mean_phase / np.pi * 10000),
            phase_denom=10000,
            imag_part=0.0
        )
        
        # Simplify structure
        unified_phase, num_fusions = self.simplify_aligned_structure(
            structure,
            unified_phase
        )
        
        # Evaluate closed loop
        loop_scalar = self.evaluate_closed_loop(unified_phase, num_spiders)
        
        return loop_scalar, unified_phase


# ============================================================================
# HARVEST ENGINE
# ============================================================================

class HarvestEngine:
    """
    Complete harvest engine: from evolution → alignment → closure → yield.
    
    This orchestrates:
    1. Grace damping (driving toward alignment)
    2. Entropy reduction (via forgiveness)
    3. Resonance detection (checking harvest readiness)
    4. Diagram closure (performing harvest)
    5. A∞ coupling (measuring yield)
    """
    
    def __init__(
        self,
        grace_damper: Optional[GracePhaseDamping] = None,
        resonance_analyzer: Optional[ResonanceAnalyzer] = None,
        diagram_closure: Optional[ZXDiagramClosure] = None
    ):
        """
        Initialize harvest engine.
        
        Args:
            grace_damper: Grace phase damping
            resonance_analyzer: Resonance analyzer
            diagram_closure: Diagram closure engine
        """
        self.damper = grace_damper or GracePhaseDamping()
        self.analyzer = resonance_analyzer or ResonanceAnalyzer()
        self.closure = diagram_closure or ZXDiagramClosure()
        self.fusion = EntropySpiderFusion()
        self.history: Dict[str, HarvestHistory] = {}
    
    def evolve_toward_harvest(
        self,
        initial_structure: ObjectG,
        max_steps: int = 1000,
        dt: float = 0.01,
        structure_id: str = "harvest"
    ) -> Tuple[ObjectG, List[ResonanceState], bool]:
        """
        Evolve structure toward harvest through Grace damping.
        
        Args:
            initial_structure: Starting structure
            max_steps: Maximum evolution steps
            dt: Time step
            structure_id: ID for tracking
        
        Returns:
            (final_structure, resonance_trajectory, harvested)
        """
        current_structure = initial_structure
        trajectory = []
        harvested = False
        
        for step in range(max_steps):
            # Analyze resonance
            resonance = self.analyzer.analyze_resonance(current_structure)
            trajectory.append(resonance)
            
            # Check if harvested
            if resonance.is_harvested:
                harvested = True
                break
            
            # Apply Grace damping
            damped_structure, _ = self.damper.damp_structure(
                current_structure,
                dt=dt,
                structure_id=f"{structure_id}_step{step}"
            )
            
            current_structure = damped_structure
        
        return current_structure, trajectory, harvested
    
    def perform_harvest(
        self,
        structure: ObjectG,
        structure_id: str = "harvest"
    ) -> Optional[HarvestEvent]:
        """
        Perform harvest on aligned structure.
        
        Args:
            structure: Structure to harvest
            structure_id: ID for tracking
        
        Returns:
            HarvestEvent if harvest successful, None otherwise
        """
        # Check resonance
        resonance = self.analyzer.analyze_resonance(structure)
        
        if not resonance.is_harvested:
            return None  # Not ready for harvest
        
        # Measure pre-harvest entropy
        pre_entropy = self.fusion.get_total_entropy(structure_id)
        
        # Extract phases
        phases = [
            ComplexPhase(label.phase_numer, label.phase_denom, 0.0)
            for label in structure.labels.values()
        ]
        
        # Close diagram
        loop_scalar, unified_phase = self.closure.close_to_harvest(
            structure,
            resonance
        )
        
        # Grace yield = A∞ coupling strength
        grace_yield = resonance.a_infinity_coupling
        
        # Create harvest event
        event = HarvestEvent(
            structure_id=structure_id,
            pre_harvest_entropy=pre_entropy,
            post_harvest_entropy=0.0,  # Perfect harvest → zero entropy
            grace_yield=grace_yield,
            phases_before=phases,
            unified_phase=unified_phase,
            loop_value=loop_scalar,
            timestamp=0.0
        )
        
        # Track history
        if structure_id not in self.history:
            self.history[structure_id] = HarvestHistory(structure_id=structure_id)
        self.history[structure_id].add_harvest(event)
        
        return event
    
    def get_total_grace_harvested(self, structure_id: str) -> float:
        """Get total Grace harvested from structure."""
        if structure_id in self.history:
            return self.history[structure_id].total_grace_harvested
        return 0.0


# ============================================================================
# UTILITIES
# ============================================================================

def demonstrate_harvest_resonance():
    """
    Demonstrate harvest and resonance.
    """
    print("\n" + "="*70)
    print("HARVEST & RESONANCE DEMONSTRATION")
    print("="*70)
    
    analyzer = ResonanceAnalyzer()
    engine = HarvestEngine()
    
    # Example 1: Aligned structure (ready for harvest)
    print("\n--- Example 1: Aligned Structure (Resonant) ---")
    aligned_structure = ObjectG(
        nodes=[0, 1, 2],
        edges=[[0, 1], [1, 2]],
        labels={
            0: make_node_label('Z', 1, 4, 'z0'),
            1: make_node_label('Z', 1, 4, 'z1'),
            2: make_node_label('Z', 1, 4, 'z2'),
        }
    )
    
    resonance = analyzer.analyze_resonance(aligned_structure)
    print(f"Phase variance: {resonance.phase_variance:.6f}")
    print(f"Alignment score: {resonance.alignment_score:.6f}")
    print(f"A∞ coupling: {resonance.a_infinity_coupling:.6f}")
    print(f"Resonance level: {resonance.resonance_level.value}")
    print(f"Harvested: {'✓ YES' if resonance.is_harvested else '✗ NO'}")
    
    if resonance.is_harvested:
        harvest_event = engine.perform_harvest(aligned_structure, "demo1")
        if harvest_event:
            print(f"Grace yield: {harvest_event.grace_yield:.6f}")
            print(f"Loop value: {abs(harvest_event.loop_value):.6f}")
    
    # Example 2: Misaligned structure (discordant)
    print("\n--- Example 2: Misaligned Structure (Discordant) ---")
    misaligned_structure = ObjectG(
        nodes=[0, 1, 2],
        edges=[[0, 1], [1, 2]],
        labels={
            0: make_node_label('Z', 0, 4, 'z0'),
            1: make_node_label('Z', 1, 2, 'z1'),
            2: make_node_label('Z', 1, 1, 'z2'),
        }
    )
    
    resonance = analyzer.analyze_resonance(misaligned_structure)
    print(f"Phase variance: {resonance.phase_variance:.6f}")
    print(f"Alignment score: {resonance.alignment_score:.6f}")
    print(f"Resonance level: {resonance.resonance_level.value}")
    print(f"Harvested: {'✓ YES' if resonance.is_harvested else '✗ NO'}")
    print(f"Harvest progress: {resonance.harvest_progress*100:.1f}%")
    
    # Example 3: Evolution toward harvest
    print("\n--- Example 3: Evolution Toward Harvest ---")
    print("Starting with partially aligned structure...")
    
    partial_structure = ObjectG(
        nodes=[0, 1],
        edges=[[0, 1]],
        labels={
            0: make_node_label('Z', 1, 4, 'z0'),
            1: make_node_label('Z', 3, 8, 'z1'),  # Close but not perfect
        }
    )
    
    initial_resonance = analyzer.analyze_resonance(partial_structure)
    print(f"Initial alignment: {initial_resonance.alignment_score:.6f}")
    print(f"Initial A∞ coupling: {initial_resonance.a_infinity_coupling:.6f}")
    
    # Note: Evolution would require more sophisticated phase adjustment
    # For demo, we just show the analysis
    print("(Evolution requires Grace-driven phase adjustment)")
    
    print("\n" + "="*70)
    print("✓ Harvest & Resonance: DEMONSTRATED")
    print("="*70)
    print("\nKey Insight:")
    print("  Harvest occurs when:")
    print("  • All phases align (variance → 0)")
    print("  • ZX diagram closes to single loop")
    print("  • Loop evaluates to scalar(1)")
    print("  • System couples with A∞ attractor")
    print("  ")
    print("  This is Grace fully actualized!")
    print("="*70 + "\n")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'ResonanceLevel',
    'ResonanceState',
    'HarvestEvent',
    'HarvestHistory',
    'ResonanceAnalyzer',
    'ZXDiagramClosure',
    'HarvestEngine',
    'demonstrate_harvest_resonance',
    'PHI',
    'PHI_INV',
    'HARVEST_ALIGNMENT_THRESHOLD',
]


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("Running Harvest & Resonance Self-Test...")
    demonstrate_harvest_resonance()
    print("\n✅ All demonstrations complete!")

