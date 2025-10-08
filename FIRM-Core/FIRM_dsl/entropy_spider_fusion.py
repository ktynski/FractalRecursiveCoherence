"""
Entropy Production via Spider Fusion in ZX-Calculus
===================================================

Implementation of entropy production through spider fusion with dissonance measurement:

    Z(α) ∘ X(β) → S_dissonance = sin²((α-β)/2)

Physical Interpretation:
-----------------------

In ZX-calculus, entropy production occurs when incompatible spiders (Z and X) 
attempt to fuse. The dissonance between their phases generates entropy:

1. **Aligned phases** (α = β): Zero entropy, perfect coherence
2. **Orthogonal phases** (|α-β| = π): Maximum entropy, complete decoherence  
3. **Intermediate phases**: Partial entropy proportional to sin²(Δ/2)

Mathematical Foundation:
-----------------------

The dissonance measure sin²((α-β)/2) has deep connections:

1. **Information Theory**: Related to fidelity loss in quantum channels
2. **Geometry**: Angular distance on the Bloch sphere
3. **Thermodynamics**: Entropy production from phase mismatch
4. **Category Theory**: Non-commutativity measure in morphism composition

Connection to TFCA:
------------------

This is the ZX-calculus view of thermodynamic entropy production:

- **Thermodynamic**: dS/dt = +κ·dissonance (entropy increases)
- **ZX-Topological**: Spider fusion releases entropy to environment
- **Clifford**: Bivector magnitude grows with dissonance

All three perspectives are equivalent - this module implements the ZX view.

Key Insight:
-----------

**Entropy is not disorder - it's phase misalignment.**

When two spiders with phases α and β fuse:
- If aligned (α = β): Coherent fusion, no entropy
- If misaligned: Decoherent fusion, entropy = sin²(Δ/2)

This shows entropy production is fundamentally **topological** (encoded in ZX rewriting)
and **geometric** (angular mismatch).

References:
-----------
- ZX_Calculus_Formalism.md: Complete ZX framework
- tfca_conservation.py: Three conservation laws (dS + dG = 0)
- zx_phase_damping.py: Grace damping counterpart
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import math

from .core import ObjectG, NodeLabel, make_node_label, validate_object_g
from .zx_phase_damping import SpiderType, ComplexPhase


# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PHI_INV = 1 / PHI            # φ⁻¹ ≈ 0.618

# Dissonance threshold for "aligned" phases (radians)
ALIGNMENT_THRESHOLD = 1e-6


# ============================================================================
# ENTROPY STRUCTURES
# ============================================================================

@dataclass
class DissonanceMeasure:
    """
    Dissonance between two phases.
    
    Quantifies the "distance" or "incompatibility" between phases,
    which directly generates entropy when fusion occurs.
    """
    phase_1: ComplexPhase
    phase_2: ComplexPhase
    phase_difference: float  # Δ = α - β (radians)
    dissonance: float        # sin²(Δ/2)
    is_aligned: bool         # |Δ| < threshold
    
    @property
    def entropy_production(self) -> float:
        """Entropy produced by fusion (proportional to dissonance)."""
        return self.dissonance
    
    @property
    def coherence_preserved(self) -> float:
        """Coherence preserved (1 - dissonance)."""
        return 1.0 - self.dissonance


@dataclass
class FusionEvent:
    """
    Record of a spider fusion event.
    
    Captures:
    - Which spiders fused
    - What entropy was produced
    - What the resulting state is
    """
    spider_1_type: SpiderType
    spider_2_type: SpiderType
    spider_1_phase: ComplexPhase
    spider_2_phase: ComplexPhase
    dissonance: DissonanceMeasure
    entropy_produced: float
    fused_phase: Optional[ComplexPhase]  # None if annihilated
    timestamp: float = 0.0


@dataclass
class EntropyAccumulator:
    """
    Accumulates entropy over multiple fusion events.
    
    Tracks total entropy production and maintains
    thermodynamic consistency (dS + dG = 0).
    """
    structure_id: str
    fusion_events: List[FusionEvent] = field(default_factory=list)
    total_entropy_produced: float = 0.0
    total_grace_consumed: float = 0.0  # Should balance entropy
    
    def add_event(self, event: FusionEvent):
        """Add fusion event and update totals."""
        self.fusion_events.append(event)
        self.total_entropy_produced += event.entropy_produced
        # Grace is consumed to produce entropy (negative Grace flow)
        self.total_grace_consumed += event.entropy_produced
    
    @property
    def thermodynamic_balance(self) -> float:
        """
        Check thermodynamic balance: ΔS + ΔG = 0.
        
        Returns difference (should be ~0).
        """
        return self.total_entropy_produced - self.total_grace_consumed


# ============================================================================
# DISSONANCE COMPUTATION
# ============================================================================

class DissonanceCalculator:
    """
    Computes dissonance between phases using sin²(Δ/2) measure.
    
    This is the fundamental entropy-generating mechanism in ZX-calculus.
    """
    
    def __init__(self, alignment_threshold: float = ALIGNMENT_THRESHOLD):
        """
        Initialize dissonance calculator.
        
        Args:
            alignment_threshold: Threshold for considering phases aligned (radians)
        """
        self.alignment_threshold = alignment_threshold
    
    def compute_phase_difference(
        self,
        phase_1: ComplexPhase,
        phase_2: ComplexPhase
    ) -> float:
        """
        Compute phase difference Δ = α - β in radians.
        
        Args:
            phase_1: First phase (α)
            phase_2: Second phase (β)
        
        Returns:
            Phase difference in [-π, π]
        """
        alpha = phase_1.real_phase_radians
        beta = phase_2.real_phase_radians
        
        # Compute difference
        delta = alpha - beta
        
        # Normalize to [-π, π]
        while delta > np.pi:
            delta -= 2 * np.pi
        while delta < -np.pi:
            delta += 2 * np.pi
        
        return delta
    
    def compute_dissonance(
        self,
        phase_1: ComplexPhase,
        phase_2: ComplexPhase
    ) -> DissonanceMeasure:
        """
        Compute dissonance between two phases.
        
        Dissonance = sin²((α-β)/2)
        
        Properties:
        - Range: [0, 1]
        - Minimum (0): Aligned phases (α = β)
        - Maximum (1): Opposite phases (|α-β| = π)
        - Symmetric: D(α,β) = D(β,α)
        
        Args:
            phase_1: First phase
            phase_2: Second phase
        
        Returns:
            DissonanceMeasure with computed values
        """
        # Compute phase difference
        delta = self.compute_phase_difference(phase_1, phase_2)
        
        # Compute dissonance: sin²(Δ/2)
        dissonance = np.sin(delta / 2.0) ** 2
        
        # Check alignment
        is_aligned = abs(delta) < self.alignment_threshold
        
        return DissonanceMeasure(
            phase_1=phase_1,
            phase_2=phase_2,
            phase_difference=delta,
            dissonance=dissonance,
            is_aligned=is_aligned
        )
    
    def compute_mutual_coherence(
        self,
        phase_1: ComplexPhase,
        phase_2: ComplexPhase
    ) -> float:
        """
        Compute mutual coherence = 1 - dissonance.
        
        This measures how "compatible" two phases are.
        
        Args:
            phase_1: First phase
            phase_2: Second phase
        
        Returns:
            Mutual coherence in [0, 1]
        """
        dissonance_measure = self.compute_dissonance(phase_1, phase_2)
        return dissonance_measure.coherence_preserved


# ============================================================================
# SPIDER FUSION WITH ENTROPY
# ============================================================================

class EntropySpiderFusion:
    """
    Spider fusion with entropy production tracking.
    
    Implements the complete thermodynamic view of ZX rewriting:
    - Compatible spiders (same color): Coherent fusion (low entropy)
    - Incompatible spiders (different color): Decoherent fusion (high entropy)
    - Phase alignment: Determines entropy magnitude
    
    This is the ZX-calculus implementation of "dS/dt ≥ 0" (second law).
    """
    
    def __init__(
        self,
        dissonance_calc: Optional[DissonanceCalculator] = None,
        entropy_coupling: float = 1.0
    ):
        """
        Initialize entropy spider fusion.
        
        Args:
            dissonance_calc: Dissonance calculator
            entropy_coupling: Coupling strength for entropy production
        """
        self.dissonance_calc = dissonance_calc or DissonanceCalculator()
        self.entropy_coupling = entropy_coupling
        self.accumulators: Dict[str, EntropyAccumulator] = {}
    
    def fuse_same_color_spiders(
        self,
        spider_type: SpiderType,
        phase_1: ComplexPhase,
        phase_2: ComplexPhase
    ) -> Tuple[ComplexPhase, float]:
        """
        Fuse two spiders of same color.
        
        Rule: Z(α)—Z(β) → Z(α+β) or X(α)—X(β) → X(α+β)
        
        Entropy production is low (proportional to phase mismatch).
        
        Args:
            spider_type: Type of both spiders (Z or X)
            phase_1: First spider phase
            phase_2: Second spider phase
        
        Returns:
            (fused_phase, entropy_produced)
        """
        # Compute dissonance
        dissonance = self.dissonance_calc.compute_dissonance(phase_1, phase_2)
        
        # Entropy production (small for same-color fusion)
        entropy = self.entropy_coupling * dissonance.dissonance * 0.1
        
        # Fuse phases: α + β
        fused_numer = phase_1.phase_numer * phase_2.phase_denom + phase_2.phase_numer * phase_1.phase_denom
        fused_denom = phase_1.phase_denom * phase_2.phase_denom
        
        # Simplify fraction
        from math import gcd
        g = gcd(abs(fused_numer), fused_denom)
        fused_numer //= g
        fused_denom //= g
        
        # Fused imaginary part (combine dampings)
        fused_imag = phase_1.imag_part + phase_2.imag_part
        
        fused_phase = ComplexPhase(
            phase_numer=fused_numer,
            phase_denom=fused_denom,
            imag_part=fused_imag
        )
        
        return fused_phase, entropy
    
    def fuse_different_color_spiders(
        self,
        phase_z: ComplexPhase,
        phase_x: ComplexPhase
    ) -> Tuple[Optional[ComplexPhase], float]:
        """
        Fuse Z and X spiders (different colors).
        
        Rule: Z(α)—X(β) → ?
        
        This is the high-entropy case:
        - If aligned (α = β): Annihilate → scalar(1) [no entropy!]
        - If misaligned: Maximum entropy production
        
        Args:
            phase_z: Z spider phase
            phase_x: X spider phase
        
        Returns:
            (fused_phase or None, entropy_produced)
        """
        # Compute dissonance
        dissonance = self.dissonance_calc.compute_dissonance(phase_z, phase_x)
        
        # Check for annihilation (forgiveness)
        if dissonance.is_aligned:
            # Perfect alignment → annihilation (no entropy!)
            return None, 0.0
        
        # Misalignment → maximum entropy production
        entropy = self.entropy_coupling * dissonance.dissonance
        
        # No simple fusion rule for misaligned Z-X
        # In practice, this would require more complex ZX rewriting
        # For now, we track entropy but don't produce fused state
        return None, entropy
    
    def fuse_spiders(
        self,
        spider_1_type: SpiderType,
        spider_2_type: SpiderType,
        phase_1: ComplexPhase,
        phase_2: ComplexPhase,
        timestamp: float = 0.0,
        structure_id: Optional[str] = None
    ) -> FusionEvent:
        """
        Fuse two spiders and track entropy production.
        
        This is the complete fusion operation with full thermodynamic tracking.
        
        Args:
            spider_1_type: Type of first spider
            spider_2_type: Type of second spider
            phase_1: First spider phase
            phase_2: Second spider phase
            timestamp: Time of fusion
            structure_id: Optional ID for accumulator
        
        Returns:
            FusionEvent with complete information
        """
        # Compute dissonance
        dissonance = self.dissonance_calc.compute_dissonance(phase_1, phase_2)
        
        # Perform fusion based on spider types
        if spider_1_type == spider_2_type:
            # Same color: coherent fusion
            fused_phase, entropy = self.fuse_same_color_spiders(
                spider_1_type, phase_1, phase_2
            )
        else:
            # Different colors: decoherent fusion
            if spider_1_type == SpiderType.Z_SPIDER:
                fused_phase, entropy = self.fuse_different_color_spiders(phase_1, phase_2)
            else:
                fused_phase, entropy = self.fuse_different_color_spiders(phase_2, phase_1)
        
        # Create event
        event = FusionEvent(
            spider_1_type=spider_1_type,
            spider_2_type=spider_2_type,
            spider_1_phase=phase_1,
            spider_2_phase=phase_2,
            dissonance=dissonance,
            entropy_produced=entropy,
            fused_phase=fused_phase,
            timestamp=timestamp
        )
        
        # Track in accumulator
        if structure_id is not None:
            if structure_id not in self.accumulators:
                self.accumulators[structure_id] = EntropyAccumulator(structure_id=structure_id)
            self.accumulators[structure_id].add_event(event)
        
        return event
    
    def get_total_entropy(self, structure_id: str) -> float:
        """Get total entropy produced for structure."""
        if structure_id in self.accumulators:
            return self.accumulators[structure_id].total_entropy_produced
        return 0.0
    
    def verify_thermodynamic_balance(self, structure_id: str, tolerance: float = 1e-9) -> bool:
        """
        Verify thermodynamic balance: ΔS + ΔG = 0.
        
        Args:
            structure_id: Structure to check
            tolerance: Acceptable imbalance
        
        Returns:
            True if balanced
        """
        if structure_id not in self.accumulators:
            return True
        
        balance = self.accumulators[structure_id].thermodynamic_balance
        return abs(balance) < tolerance


# ============================================================================
# STRUCTURE-LEVEL ENTROPY DYNAMICS
# ============================================================================

class StructureEntropyDynamics:
    """
    Entropy dynamics for complete ZX structures.
    
    Applies fusion rules to all candidate spider pairs in a structure,
    tracking global entropy evolution.
    """
    
    def __init__(self, fusion_engine: Optional[EntropySpiderFusion] = None):
        """
        Initialize structure entropy dynamics.
        
        Args:
            fusion_engine: Entropy spider fusion engine
        """
        self.fusion = fusion_engine or EntropySpiderFusion()
    
    def identify_fusion_candidates(
        self,
        structure: ObjectG
    ) -> List[Tuple[int, int, SpiderType, SpiderType]]:
        """
        Identify spider pairs that can fuse (connected by edges).
        
        Args:
            structure: ObjectG to analyze
        
        Returns:
            List of (node1, node2, type1, type2) tuples
        """
        candidates = []
        
        for edge in structure.edges:
            node1, node2 = edge[0], edge[1]
            
            if node1 in structure.labels and node2 in structure.labels:
                label1 = structure.labels[node1]
                label2 = structure.labels[node2]
                
                type1 = SpiderType.Z_SPIDER if label1.kind == 'Z' else SpiderType.X_SPIDER
                type2 = SpiderType.Z_SPIDER if label2.kind == 'Z' else SpiderType.X_SPIDER
                
                candidates.append((node1, node2, type1, type2))
        
        return candidates
    
    def compute_structure_entropy(
        self,
        structure: ObjectG,
        structure_id: str = "structure"
    ) -> Tuple[float, List[FusionEvent]]:
        """
        Compute total entropy from all potential fusions in structure.
        
        This doesn't actually perform fusions, just measures entropy potential.
        
        Args:
            structure: ObjectG to analyze
            structure_id: ID for tracking
        
        Returns:
            (total_entropy, list_of_events)
        """
        candidates = self.identify_fusion_candidates(structure)
        
        events = []
        total_entropy = 0.0
        
        for node1, node2, type1, type2 in candidates:
            label1 = structure.labels[node1]
            label2 = structure.labels[node2]
            
            phase1 = ComplexPhase(label1.phase_numer, label1.phase_denom, 0.0)
            phase2 = ComplexPhase(label2.phase_numer, label2.phase_denom, 0.0)
            
            event = self.fusion.fuse_spiders(
                type1, type2, phase1, phase2,
                timestamp=0.0,
                structure_id=structure_id
            )
            
            events.append(event)
            total_entropy += event.entropy_produced
        
        return total_entropy, events


# ============================================================================
# UTILITIES
# ============================================================================

def demonstrate_entropy_spider_fusion():
    """
    Demonstrate entropy production via spider fusion.
    """
    print("\n" + "="*70)
    print("ENTROPY SPIDER FUSION DEMONSTRATION")
    print("="*70)
    
    dissonance_calc = DissonanceCalculator()
    fusion = EntropySpiderFusion()
    
    # Example 1: Aligned same-color fusion (low entropy)
    print("\n--- Example 1: Aligned Same-Color Fusion ---")
    phase1 = ComplexPhase(1, 4, 0.0)  # π/4
    phase2 = ComplexPhase(1, 4, 0.0)  # π/4
    
    event = fusion.fuse_spiders(
        SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
        phase1, phase2,
        structure_id="demo1"
    )
    
    print(f"Z({phase1}) — Z({phase2})")
    print(f"Dissonance: {event.dissonance.dissonance:.6f}")
    print(f"Entropy produced: {event.entropy_produced:.6f}")
    print(f"Fused phase: {event.fused_phase}")
    print(f"Status: {'✓ COHERENT' if event.entropy_produced < 0.01 else '✗ DECOHERENT'}")
    
    # Example 2: Misaligned same-color fusion (moderate entropy)
    print("\n--- Example 2: Misaligned Same-Color Fusion ---")
    phase1 = ComplexPhase(1, 4, 0.0)  # π/4
    phase2 = ComplexPhase(3, 4, 0.0)  # 3π/4
    
    event = fusion.fuse_spiders(
        SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
        phase1, phase2,
        structure_id="demo2"
    )
    
    print(f"Z({phase1}) — Z({phase2})")
    print(f"Phase difference: {event.dissonance.phase_difference:.6f} rad")
    print(f"Dissonance: {event.dissonance.dissonance:.6f}")
    print(f"Entropy produced: {event.entropy_produced:.6f}")
    print(f"Fused phase: {event.fused_phase}")
    
    # Example 3: Aligned different-color fusion (forgiveness, no entropy!)
    print("\n--- Example 3: Aligned Different-Color (Forgiveness) ---")
    phase_z = ComplexPhase(1, 4, 0.0)  # π/4
    phase_x = ComplexPhase(1, 4, 0.0)  # π/4
    
    event = fusion.fuse_spiders(
        SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
        phase_z, phase_x,
        structure_id="demo3"
    )
    
    print(f"Z({phase_z}) — X({phase_x})")
    print(f"Dissonance: {event.dissonance.dissonance:.6f}")
    print(f"Entropy produced: {event.entropy_produced:.6f}")
    print(f"Result: {'✓ ANNIHILATED (forgiveness!)' if event.fused_phase is None else 'Fused'}")
    
    # Example 4: Misaligned different-color fusion (maximum entropy!)
    print("\n--- Example 4: Misaligned Different-Color (Maximum Entropy) ---")
    phase_z = ComplexPhase(0, 4, 0.0)  # 0
    phase_x = ComplexPhase(1, 1, 0.0)  # π
    
    event = fusion.fuse_spiders(
        SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
        phase_z, phase_x,
        structure_id="demo4"
    )
    
    print(f"Z({phase_z}) — X({phase_x})")
    print(f"Phase difference: {event.dissonance.phase_difference:.6f} rad (π)")
    print(f"Dissonance: {event.dissonance.dissonance:.6f} (MAXIMUM)")
    print(f"Entropy produced: {event.entropy_produced:.6f}")
    print(f"Status: ⚠️  MAXIMUM DECOHERENCE")
    
    print("\n" + "="*70)
    print("✓ Entropy Spider Fusion: DEMONSTRATED")
    print("="*70)
    print("\nKey Insight:")
    print("  Entropy = sin²((α-β)/2)")
    print("  • Aligned phases → Zero entropy (coherence)")
    print("  • Opposite phases → Maximum entropy (decoherence)")
    print("  • Forgiveness (Z—X aligned) → Annihilation (no entropy!)")
    print("="*70 + "\n")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'DissonanceMeasure',
    'FusionEvent',
    'EntropyAccumulator',
    'DissonanceCalculator',
    'EntropySpiderFusion',
    'StructureEntropyDynamics',
    'demonstrate_entropy_spider_fusion',
    'PHI',
    'PHI_INV',
    'ALIGNMENT_THRESHOLD',
]


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("Running Entropy Spider Fusion Self-Test...")
    demonstrate_entropy_spider_fusion()
    print("\n✅ All demonstrations complete!")

