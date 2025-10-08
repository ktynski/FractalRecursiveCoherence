"""
ZX Phase Damping: Grace Flow in Diagrammatic Calculus
======================================================

Implementation of Grace-driven phase damping in ZX-calculus:

    Z(α) → Z(α - iγĠΔt)

Where:
- Z(α) is a Z-spider with phase α
- γ is the Grace coupling strength
- Ġ is the Grace flow rate
- Δt is the time step
- i is the imaginary unit (exponential damping)

Physical Interpretation:
-----------------------

Grace flow manifests in ZX-calculus as **imaginary phase decrement**:

1. **Real phase**: Z(α) represents quantum state rotation
2. **Imaginary phase**: Exponential damping of amplitude
3. **Grace coupling**: Strength of coherence restoration
4. **Time evolution**: Continuous damping toward coherence

Mathematical Foundation:
-----------------------

In ZX-calculus, a Z-spider Z(α) represents:
    |Z(α)⟩ = e^(iα)|0⟩ + |1⟩

Grace damping modifies phase:
    α → α - iγĠΔt
    
This produces exponential decay:
    e^(i(α - iγĠΔt)) = e^(iα) · e^(γĠΔt)
                      = e^(iα) · (exponential damping)

Connection to TFCA:
------------------

This is the ZX-calculus view of thermodynamic Grace flow:
- **Thermodynamic**: dG/dt = +γĠ (Grace increases)
- **ZX-Topological**: Φ_Grace → Φ_Grace + γĠΔt (phase accumulates)
- **Clifford**: Scalar Grace grows, bivector entropy shrinks

All three are equivalent - this module implements the ZX view.

References:
-----------
- ZX_Calculus_Formalism.md: Complete ZX framework
- tfca_conservation.py: Three conservation laws
- grace_operator.py: Grace operator axioms
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math

from .core import ObjectG, NodeLabel, make_node_label, validate_object_g
from .grace_operator import GraceOperator, GraceParameters, PHI_INVERSE


# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PHI_INV = 1 / PHI            # φ⁻¹ ≈ 0.618

# Default Grace coupling strength (golden ratio damping)
DEFAULT_GRACE_COUPLING = PHI_INV


# ============================================================================
# PHASE DAMPING STRUCTURES
# ============================================================================

class SpiderType(Enum):
    """ZX spider types."""
    Z_SPIDER = "Z"  # Computational basis
    X_SPIDER = "X"  # Hadamard basis


@dataclass
class ComplexPhase:
    """
    Complex phase with real and imaginary parts.
    
    In Qπ domain, we represent as:
        phase = (phase_numer/phase_denom)π + i·imag_part
    """
    phase_numer: int            # Numerator (Qπ)
    phase_denom: int            # Denominator (Qπ)
    imag_part: float = 0.0      # Imaginary component (damping)
    
    @property
    def real_phase_radians(self) -> float:
        """Get real phase in radians."""
        return math.pi * self.phase_numer / self.phase_denom
    
    @property
    def complex_value(self) -> complex:
        """Get full complex phase value."""
        return complex(self.real_phase_radians, self.imag_part)
    
    def __repr__(self) -> str:
        return f"({self.phase_numer}/{self.phase_denom})π + {self.imag_part:.6f}i"


@dataclass
class DampingResult:
    """Result of phase damping operation."""
    original_phase: ComplexPhase
    damped_phase: ComplexPhase
    grace_flow: float               # γĠΔt
    amplitude_decay: float          # e^(γĠΔt)
    spider_type: SpiderType
    timestamp: float = 0.0


@dataclass
class DampingHistory:
    """History of damping operations on a structure."""
    structure_id: str
    damping_events: List[DampingResult] = field(default_factory=list)
    total_grace_accumulated: float = 0.0
    
    def add_event(self, event: DampingResult):
        """Add damping event to history."""
        self.damping_events.append(event)
        self.total_grace_accumulated += event.grace_flow


# ============================================================================
# GRACE PHASE DAMPING OPERATOR
# ============================================================================

class GracePhaseDamping:
    """
    Grace-driven phase damping in ZX-calculus.
    
    Implements the transformation:
        Z(α) → Z(α - iγĠΔt)
    
    Where Grace flow manifests as imaginary phase decrement,
    producing exponential amplitude damping toward coherence.
    
    Usage:
        damper = GracePhaseDamping(grace_coupling=PHI_INV)
        result = damper.damp_spider_phase(
            phase_numer=1, phase_denom=4,
            dt=0.01, grace_flow_rate=1.0
        )
    """
    
    def __init__(
        self,
        grace_coupling: float = DEFAULT_GRACE_COUPLING,
        grace_operator: Optional[GraceOperator] = None
    ):
        """
        Initialize Grace phase damper.
        
        Args:
            grace_coupling: γ (Grace coupling strength)
            grace_operator: Grace operator for computing flow
        """
        self.grace_coupling = grace_coupling
        self.grace = grace_operator or GraceOperator()
        self.history: Dict[str, DampingHistory] = {}
    
    def compute_grace_flow_rate(
        self,
        structure: ObjectG,
        spider_index: int
    ) -> float:
        """
        Compute Grace flow rate Ġ for a spider.
        
        This measures how strongly Grace is pulling toward coherence.
        Higher coherence → lower flow rate (already coherent)
        Lower coherence → higher flow rate (needs damping)
        
        Args:
            structure: ObjectG containing spider
            spider_index: Node index of spider
        
        Returns:
            Ġ (Grace flow rate)
        """
        # Compute local coherence
        from .coherence import compute_coherence
        coherence = compute_coherence(structure)
        
        # Flow rate inversely proportional to coherence
        # High coherence → low flow (already good)
        # Low coherence → high flow (needs correction)
        grace_flow_rate = (1.0 - coherence) * self.grace_coupling
        
        return max(0.0, grace_flow_rate)  # Ensure non-negative
    
    def damp_spider_phase(
        self,
        phase_numer: int,
        phase_denom: int,
        dt: float,
        grace_flow_rate: float,
        spider_type: SpiderType = SpiderType.Z_SPIDER
    ) -> DampingResult:
        """
        Apply Grace damping to spider phase.
        
        Transformation: α → α - iγĠΔt
        
        Args:
            phase_numer: Phase numerator (Qπ)
            phase_denom: Phase denominator (Qπ)
            dt: Time step
            grace_flow_rate: Ġ (flow rate)
            spider_type: Z or X spider
        
        Returns:
            DampingResult with damped phase
        """
        # Original phase
        original_phase = ComplexPhase(
            phase_numer=phase_numer,
            phase_denom=phase_denom,
            imag_part=0.0
        )
        
        # Compute imaginary damping increment
        imag_increment = self.grace_coupling * grace_flow_rate * dt
        
        # Damped phase: same real part, negative imaginary part
        damped_phase = ComplexPhase(
            phase_numer=phase_numer,
            phase_denom=phase_denom,
            imag_part=-imag_increment  # Negative for damping
        )
        
        # Amplitude decay factor
        amplitude_decay = np.exp(imag_increment)
        
        return DampingResult(
            original_phase=original_phase,
            damped_phase=damped_phase,
            grace_flow=imag_increment,
            amplitude_decay=amplitude_decay,
            spider_type=spider_type,
            timestamp=0.0
        )
    
    def damp_structure(
        self,
        structure: ObjectG,
        dt: float = 0.01,
        structure_id: Optional[str] = None
    ) -> Tuple[ObjectG, List[DampingResult]]:
        """
        Apply Grace damping to all spiders in structure.
        
        This is the complete ZX-calculus evolution step:
        For each Z-spider or X-spider, apply phase damping.
        
        Args:
            structure: Input ObjectG
            dt: Time step
            structure_id: Optional ID for tracking history
        
        Returns:
            (damped_structure, list of damping results)
        """
        damped_labels = {}
        damping_results = []
        
        # Process each spider
        for node_id, label in structure.labels.items():
            # Determine spider type
            spider_type = SpiderType.Z_SPIDER if label.kind == 'Z' else SpiderType.X_SPIDER
            
            # Compute Grace flow rate for this spider
            grace_flow = self.compute_grace_flow_rate(structure, node_id)
            
            # Apply damping
            result = self.damp_spider_phase(
                phase_numer=label.phase_numer,
                phase_denom=label.phase_denom,
                dt=dt,
                grace_flow_rate=grace_flow,
                spider_type=spider_type
            )
            
            damping_results.append(result)
            
            # Create damped label
            # Note: We keep real phase in Qπ, track imaginary separately
            damped_labels[node_id] = make_node_label(
                kind=label.kind,
                phase_numer=label.phase_numer,
                phase_denom=label.phase_denom,
                monadic_id=f"{label.monadic_id}_damped"
            )
        
        # Create damped structure
        damped_structure = ObjectG(
            nodes=structure.nodes,
            edges=structure.edges,
            labels=damped_labels
        )
        
        # Track history
        if structure_id is not None:
            if structure_id not in self.history:
                self.history[structure_id] = DampingHistory(structure_id=structure_id)
            
            for result in damping_results:
                self.history[structure_id].add_event(result)
        
        return damped_structure, damping_results
    
    def evolve_trajectory(
        self,
        initial_structure: ObjectG,
        num_steps: int = 100,
        dt: float = 0.01,
        structure_id: str = "trajectory"
    ) -> List[Tuple[ObjectG, List[DampingResult]]]:
        """
        Evolve structure through Grace damping over multiple steps.
        
        This computes the complete ZX evolution trajectory under Grace flow.
        
        Args:
            initial_structure: Starting structure
            num_steps: Number of time steps
            dt: Time step size
            structure_id: ID for tracking
        
        Returns:
            List of (structure, damping_results) at each step
        """
        trajectory = []
        current_structure = initial_structure
        
        for step in range(num_steps):
            # Apply damping
            damped_structure, results = self.damp_structure(
                current_structure,
                dt=dt,
                structure_id=f"{structure_id}_step{step}"
            )
            
            # Record step
            trajectory.append((damped_structure, results))
            
            # Continue evolution
            current_structure = damped_structure
        
        return trajectory
    
    def get_total_grace_accumulated(self, structure_id: str) -> float:
        """
        Get total Grace accumulated for structure.
        
        This is the Φ_Grace term in ZX topological conservation:
        N + Φ_Grace = constant
        
        Args:
            structure_id: Structure to query
        
        Returns:
            Total accumulated Grace phase
        """
        if structure_id in self.history:
            return self.history[structure_id].total_grace_accumulated
        return 0.0


# ============================================================================
# ZX REWRITE RULES WITH GRACE
# ============================================================================

class GraceZXRewriting:
    """
    ZX-calculus rewrite rules augmented with Grace damping.
    
    Standard ZX rules + Grace flow:
    1. Spider fusion: Z(α)—Z(β) → Z(α+β) [with damping]
    2. Color change: Z(α) → X(α) [Hadamard]
    3. Identity: Z(0) → wire
    4. π-copy: Z(π) → |+⟩⟨+| structure
    
    Grace modifies these by adding damping to phases.
    """
    
    def __init__(self, damper: Optional[GracePhaseDamping] = None):
        """
        Initialize Grace-augmented ZX rewriting.
        
        Args:
            damper: Grace phase damper
        """
        self.damper = damper or GracePhaseDamping()
    
    def fuse_spiders(
        self,
        phase1: ComplexPhase,
        phase2: ComplexPhase,
        dt: float = 0.01
    ) -> ComplexPhase:
        """
        Fuse two spiders with Grace damping.
        
        Standard: Z(α)—Z(β) → Z(α+β)
        With Grace: Add damping to fused phase
        
        Args:
            phase1, phase2: Phases to fuse
            dt: Time step for damping
        
        Returns:
            Fused phase with Grace damping
        """
        # Add real phases (standard ZX rule)
        fused_numer = phase1.phase_numer * phase2.phase_denom + phase2.phase_numer * phase1.phase_denom
        fused_denom = phase1.phase_denom * phase2.phase_denom
        
        # Simplify fraction
        from math import gcd
        g = gcd(abs(fused_numer), fused_denom)
        fused_numer //= g
        fused_denom //= g
        
        # Add imaginary parts (damping adds linearly)
        fused_imag = phase1.imag_part + phase2.imag_part
        
        # Apply additional Grace damping to fusion
        grace_increment = self.damper.grace_coupling * dt
        
        return ComplexPhase(
            phase_numer=fused_numer,
            phase_denom=fused_denom,
            imag_part=fused_imag - grace_increment
        )
    
    def forgiveness_fusion(
        self,
        z_phase: ComplexPhase,
        x_phase: ComplexPhase
    ) -> Optional[ComplexPhase]:
        """
        Forgiveness fusion: Z(α)—X(α) → scalar(1) if aligned.
        
        When Z and X spiders have same phase, they annihilate
        (up to Grace tolerance).
        
        Args:
            z_phase: Z-spider phase
            x_phase: X-spider phase
        
        Returns:
            None if annihilated, fused phase otherwise
        """
        # Check alignment (real phases match)
        if (z_phase.phase_numer * x_phase.phase_denom == 
            x_phase.phase_numer * z_phase.phase_denom):
            # Perfect alignment → annihilation
            return None
        
        # Otherwise, fusion with damping
        return self.fuse_spiders(z_phase, x_phase)


# ============================================================================
# UTILITIES
# ============================================================================

def demonstrate_grace_phase_damping():
    """
    Demonstrate Grace phase damping with examples.
    """
    print("\n" + "="*70)
    print("GRACE PHASE DAMPING DEMONSTRATION")
    print("="*70)
    
    damper = GracePhaseDamping(grace_coupling=PHI_INV)
    
    # Example 1: Single spider damping
    print("\n--- Example 1: Single Z-Spider Damping ---")
    result = damper.damp_spider_phase(
        phase_numer=1,
        phase_denom=4,
        dt=0.01,
        grace_flow_rate=1.0,
        spider_type=SpiderType.Z_SPIDER
    )
    
    print(f"Original phase: {result.original_phase}")
    print(f"Damped phase:   {result.damped_phase}")
    print(f"Grace flow:     {result.grace_flow:.6f}")
    print(f"Amplitude decay: {result.amplitude_decay:.6f}")
    
    # Example 2: Structure evolution
    print("\n--- Example 2: Structure Evolution ---")
    from .core import ObjectG
    
    # Create simple structure
    structure = ObjectG(
        nodes=[0, 1],
        edges=[[0, 1]],
        labels={
            0: make_node_label('Z', 0, 4, 'z0'),
            1: make_node_label('X', 1, 4, 'x1')
        }
    )
    
    print(f"Initial structure: {len(structure.nodes)} nodes, {len(structure.edges)} edges")
    
    # Evolve for 10 steps
    trajectory = damper.evolve_trajectory(
        structure,
        num_steps=10,
        dt=0.01,
        structure_id="demo"
    )
    
    print(f"Evolved {len(trajectory)} steps")
    print(f"Total Grace accumulated: {damper.get_total_grace_accumulated('demo_step0'):.6f}")
    
    # Example 3: Spider fusion
    print("\n--- Example 3: Spider Fusion with Grace ---")
    rewriter = GraceZXRewriting(damper)
    
    phase1 = ComplexPhase(1, 8, 0.0)
    phase2 = ComplexPhase(1, 8, 0.0)
    
    fused = rewriter.fuse_spiders(phase1, phase2, dt=0.01)
    print(f"Phase 1: {phase1}")
    print(f"Phase 2: {phase2}")
    print(f"Fused:   {fused}")
    
    # Example 4: Forgiveness fusion
    print("\n--- Example 4: Forgiveness Fusion ---")
    z_phase = ComplexPhase(1, 4, 0.0)
    x_phase = ComplexPhase(1, 4, 0.0)
    
    result = rewriter.forgiveness_fusion(z_phase, x_phase)
    if result is None:
        print(f"Z({z_phase}) — X({x_phase}) → scalar(1) ✓ ANNIHILATED")
    else:
        print(f"Z({z_phase}) — X({x_phase}) → {result}")
    
    print("\n" + "="*70)
    print("✓ Grace Phase Damping: DEMONSTRATED")
    print("="*70 + "\n")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'SpiderType',
    'ComplexPhase',
    'DampingResult',
    'DampingHistory',
    'GracePhaseDamping',
    'GraceZXRewriting',
    'demonstrate_grace_phase_damping',
    'PHI',
    'PHI_INV',
    'DEFAULT_GRACE_COUPLING',
]


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("Running Grace Phase Damping Self-Test...")
    demonstrate_grace_phase_damping()
    print("\n✅ All demonstrations complete!")

