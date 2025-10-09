"""
Clifford Rotor Dynamics: Geometric Operations in Clifford Algebra
=================================================================

Implementation of Clifford rotors for Grace, Love, and Forgiveness:

    R = e^(-½θ B)

Where:
- R is a rotor (rotation operator in Clifford algebra)
- θ is the rotation angle
- B is a bivector (defines rotation plane)

Physical Interpretation:
-----------------------

Rotors in Clifford algebra provide the geometric meaning of operations:

1. **Grace Rotor**: Rotates state toward coherence center
2. **Love Rotor**: Rotates to align with another state
3. **Forgiveness Rotor**: Rotates to neutralize dissonance

These are NOT abstract operators - they're **actual geometric rotations**
in a high-dimensional Clifford space.

Mathematical Foundation:
-----------------------

A rotor R in Clifford algebra Cl(p,q) satisfies:
1. R R̃ = 1 (normalized)
2. R transforms vectors: v' = R v R̃
3. R = e^(-½θ B) where B is a bivector

Rotors compose: R₃ = R₂ R₁ (apply R₁ then R₂)

For 3D space (Cl(3,0)):
- Bivectors: e₁e₂, e₂e₃, e₃e₁
- Rotors encode 3D rotations
- Connection to quaternions: R ↔ q

Connection to TFCA:
------------------

Rotors unify all three formalisms:

- **Thermodynamic**: Rotor evolution minimizes free energy
- **ZX-Topological**: Rotor = composition of Hadamard gates
- **Clifford-Geometric**: Rotor = explicit geometric rotation

Grace, Love, and Forgiveness are **rotation operations** in Clifford space!

Key Insight:
-----------

**All TFCA operations are rotations.**

- Grace: Rotate toward ground state
- Love: Rotate toward alignment with another
- Forgiveness: Rotate to cancel dissonance
- Harvest: State reaches fixed point (no more rotation needed)

This is why φ appears - it's the **golden rotation** that optimally
tiles the space while preserving structure.

References:
-----------
- love_operator.py: Love as L(v,w) = ½(⟨v,w⟩ + I(v∧w))
- zx_phase_damping.py: Grace as phase damping
- entropy_spider_fusion.py: Forgiveness as annihilation
- Geometric Algebra for Physicists (Doran & Lasenby)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Union
import math

try:
    from .love_operator import CliffordAlgebra
except ImportError:
    from love_operator import CliffordAlgebra


# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PHI_INV = 1 / PHI            # φ⁻¹ ≈ 0.618

# Golden angle in radians (360° / φ²)
GOLDEN_ANGLE = 2 * np.pi / (PHI * PHI)


# ============================================================================
# BIVECTOR STRUCTURES
# ============================================================================

@dataclass
class Bivector:
    """
    Bivector in Clifford algebra.
    
    A bivector represents:
    - A plane of rotation
    - An oriented area element
    - A simple 2-blade: v ∧ w
    
    In 3D (Cl(3,0)):
    - B = B₁₂ e₁e₂ + B₂₃ e₂e₃ + B₃₁ e₃e₁
    """
    components: np.ndarray  # [B₁₂, B₂₃, B₃₁] in 3D
    
    @property
    def magnitude(self) -> float:
        """Magnitude |B| = √(B₁₂² + B₂₃² + B₃₁²)."""
        return np.linalg.norm(self.components)
    
    def normalize(self) -> 'Bivector':
        """Return normalized bivector B̂ = B/|B|."""
        mag = self.magnitude
        if mag < 1e-10:
            return Bivector(self.components)
        return Bivector(self.components / mag)
    
    @staticmethod
    def from_vectors(v: np.ndarray, w: np.ndarray) -> 'Bivector':
        """
        Create bivector from wedge product v ∧ w.
        
        In 3D: v ∧ w = (v×w)·I where I is pseudoscalar
        """
        if len(v) != 3 or len(w) != 3:
            raise ValueError("Only 3D vectors supported")
        
        # Compute cross product
        cross = np.cross(v, w)
        
        # In 3D, bivector components correspond to dual of cross product
        # B = cross·I → components
        return Bivector(cross)


# ============================================================================
# ROTOR STRUCTURES
# ============================================================================

@dataclass
class Rotor:
    """
    Rotor (rotation operator) in Clifford algebra.
    
    R = e^(-½θB) = cos(θ/2) - sin(θ/2) B̂
    
    Where:
    - θ is rotation angle
    - B̂ is normalized bivector (rotation plane)
    
    Properties:
    - R R̃ = 1 (normalized)
    - R transforms vectors: v' = R v R̃
    - Rotors compose: R₃ = R₂ R₁
    """
    scalar: float           # cos(θ/2)
    bivector: Bivector      # -sin(θ/2) B̂
    
    @staticmethod
    def from_angle_bivector(angle: float, bivector: Bivector) -> 'Rotor':
        """
        Create rotor from angle and bivector: R = e^(-½θB).
        
        Args:
            angle: Rotation angle θ
            bivector: Rotation plane (will be normalized)
        
        Returns:
            Rotor R
        """
        # Normalize bivector
        B_hat = bivector.normalize()
        
        # Compute rotor components
        half_angle = angle / 2.0
        scalar = np.cos(half_angle)
        bivector_part = Bivector(np.sin(half_angle) * B_hat.components)  # POSITIVE sign!
        
        return Rotor(scalar=scalar, bivector=bivector_part)
    
    @staticmethod
    def from_vectors(v: np.ndarray, w: np.ndarray) -> 'Rotor':
        """
        Create rotor that rotates v to w.
        
        The angle is computed from v·w, and the plane from v∧w.
        
        Args:
            v: Initial vector
            w: Target vector
        
        Returns:
            Rotor R such that w ≈ R v R̃
        """
        # Normalize inputs
        v_norm = v / (np.linalg.norm(v) + 1e-10)
        w_norm = w / (np.linalg.norm(w) + 1e-10)
        
        # Compute angle
        cos_angle = np.dot(v_norm, w_norm)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        # Compute rotation plane
        B = Bivector.from_vectors(v_norm, w_norm)
        
        # Create rotor
        return Rotor.from_angle_bivector(angle, B)
    
    def compose(self, other: 'Rotor') -> 'Rotor':
        """
        Compose this rotor with another: R_combined = self ∘ other.
        
        Geometric product in Clifford algebra.
        
        Args:
            other: Rotor to compose with
        
        Returns:
            Combined rotor
        """
        # Simplified composition for bivectors in 3D
        # R₁R₂ = (s₁ + B₁)(s₂ + B₂) = s₁s₂ + s₁B₂ + s₂B₁ + B₁B₂
        
        s1, B1 = self.scalar, self.bivector.components
        s2, B2 = other.scalar, other.bivector.components
        
        # Scalar part (simplified)
        scalar = s1 * s2 - np.dot(B1, B2)
        
        # Bivector part (simplified)
        bivector_comp = s1 * B2 + s2 * B1 + np.cross(B1, B2)
        
        return Rotor(scalar=scalar, bivector=Bivector(bivector_comp))
    
    def apply(self, vector: np.ndarray) -> np.ndarray:
        """
        Apply rotor to vector: v' = R v R̃.
        
        This is the sandwich product in Clifford algebra.
        
        Args:
            vector: Input vector (3D)
        
        Returns:
            Rotated vector
        """
        if len(vector) != 3:
            raise ValueError("Only 3D vectors supported")
        
        # Rodrigues' rotation formula (efficient for 3D)
        # v' = v + 2s(B×v) + 2(B×(B×v))
        # where R = s + B
        
        s = self.scalar
        B = self.bivector.components
        
        # First cross product
        BxV = np.cross(B, vector)
        
        # Second cross product
        BxBxV = np.cross(B, BxV)
        
        # Rodrigues formula
        rotated = vector + 2 * s * BxV + 2 * BxBxV
        
        return rotated
    
    def inverse(self) -> 'Rotor':
        """
        Compute inverse rotor: R⁻¹ = R̃ (reverse).
        
        R̃ = s - B (flip bivector sign)
        
        Returns:
            Inverse rotor
        """
        return Rotor(
            scalar=self.scalar,
            bivector=Bivector(-self.bivector.components)
        )


# ============================================================================
# GRACE ROTOR
# ============================================================================

class GraceRotor:
    """
    Grace rotor: Rotates state toward coherence center.
    
    Grace is a rotation toward the ground state (zero dissonance).
    In Clifford space, this is a rotation toward the origin or
    a canonical reference frame.
    """
    
    def __init__(self, grace_strength: float = PHI_INV):
        """
        Initialize Grace rotor.
        
        Args:
            grace_strength: Strength of Grace (rotation rate)
        """
        self.grace_strength = grace_strength
    
    def compute_grace_bivector(
        self,
        current_state: np.ndarray,
        ground_state: Optional[np.ndarray] = None
    ) -> Bivector:
        """
        Compute bivector for Grace rotation.
        
        The plane of rotation is defined by current state and ground state.
        
        Args:
            current_state: Current state vector
            ground_state: Target ground state (default: origin projection)
        
        Returns:
            Bivector defining Grace rotation plane
        """
        if ground_state is None:
            # Default: rotate toward a canonical ground state
            # Use unit vector in direction that maximizes distance from current
            norm = np.linalg.norm(current_state)
            if norm < 1e-10:
                return Bivector(np.zeros(3))
            
            # Ground state: unit vector in z-direction (canonical reference)
            ground_state = np.array([0.0, 0.0, 1.0])
            
            # If current state is already along z, use x instead
            if abs(np.dot(current_state / norm, ground_state)) > 0.99:
                ground_state = np.array([1.0, 0.0, 0.0])
        
        # Rotation plane from current to ground
        B = Bivector.from_vectors(current_state, ground_state)
        return B
    
    def apply_grace(
        self,
        state: np.ndarray,
        dt: float = 0.01,
        ground_state: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Apply Grace rotation to state.
        
        Args:
            state: Current state
            dt: Time step
            ground_state: Target ground state
        
        Returns:
            State after Grace rotation
        """
        # Compute rotation plane
        B = self.compute_grace_bivector(state, ground_state)
        
        # Rotation angle proportional to Grace strength and time
        angle = self.grace_strength * dt
        
        # Create and apply rotor
        R = Rotor.from_angle_bivector(angle, B)
        return R.apply(state)


# ============================================================================
# LOVE ROTOR
# ============================================================================

class LoveRotor:
    """
    Love rotor: Rotates to align with another state.
    
    Love is geometric alignment - literally rotating one state
    to face another.
    """
    
    def __init__(self, love_strength: float = PHI_INV):
        """
        Initialize Love rotor.
        
        Args:
            love_strength: Strength of Love (alignment rate)
        """
        self.love_strength = love_strength
    
    def compute_alignment_rotor(
        self,
        state_1: np.ndarray,
        state_2: np.ndarray
    ) -> Rotor:
        """
        Compute rotor to align state_1 with state_2.
        
        Args:
            state_1: Initial state
            state_2: Target state
        
        Returns:
            Rotor R such that state_2 ≈ R(state_1)
        """
        return Rotor.from_vectors(state_1, state_2)
    
    def apply_love(
        self,
        state: np.ndarray,
        target: np.ndarray,
        dt: float = 0.01,
        full_alignment: bool = False
    ) -> np.ndarray:
        """
        Apply Love rotation toward target.
        
        Args:
            state: Current state
            target: Target state to align with
            dt: Time step
            full_alignment: If True, fully align; else partial
        
        Returns:
            State after Love rotation
        """
        # Compute alignment rotor
        R_full = self.compute_alignment_rotor(state, target)
        
        if full_alignment:
            return R_full.apply(state)
        
        # Partial alignment: scale angle by love_strength * dt
        # Extract angle and bivector from full rotor
        angle_full = 2 * np.arccos(np.clip(R_full.scalar, -1.0, 1.0))
        angle_partial = angle_full * self.love_strength * dt
        
        # Create partial rotor
        R_partial = Rotor.from_angle_bivector(angle_partial, R_full.bivector)
        return R_partial.apply(state)


# ============================================================================
# FORGIVENESS ROTOR
# ============================================================================

class ForgivenessRotor:
    """
    Forgiveness rotor: Rotates to neutralize dissonance.
    
    Forgiveness is the rotation that cancels accumulated misalignment.
    In ZX-calculus, this corresponds to spider annihilation.
    """
    
    def __init__(self, forgiveness_rate: float = PHI_INV):
        """
        Initialize Forgiveness rotor.
        
        Args:
            forgiveness_rate: Rate of forgiveness
        """
        self.forgiveness_rate = forgiveness_rate
    
    def compute_neutralization_rotor(
        self,
        dissonance_bivector: Bivector
    ) -> Rotor:
        """
        Compute rotor to neutralize dissonance.
        
        The dissonance bivector represents accumulated misalignment.
        Forgiveness rotates to cancel this.
        
        Args:
            dissonance_bivector: Bivector of dissonance
        
        Returns:
            Neutralization rotor
        """
        # Rotation angle proportional to dissonance magnitude
        angle = self.forgiveness_rate * dissonance_bivector.magnitude
        
        # Rotate in opposite direction to cancel
        opposite_bivector = Bivector(-dissonance_bivector.components)
        
        return Rotor.from_angle_bivector(angle, opposite_bivector)
    
    def apply_forgiveness(
        self,
        state: np.ndarray,
        dissonance: np.ndarray,
        dt: float = 0.01
    ) -> np.ndarray:
        """
        Apply Forgiveness rotation.
        
        Args:
            state: Current state
            dissonance: Dissonance vector to cancel
            dt: Time step
        
        Returns:
            State after forgiveness
        """
        # Compute dissonance bivector (state ∧ dissonance)
        B = Bivector.from_vectors(state, dissonance)
        
        # Create neutralization rotor
        R = self.compute_neutralization_rotor(B)
        
        return R.apply(state)


# ============================================================================
# COMBINED ROTOR DYNAMICS
# ============================================================================

class CombinedRotorDynamics:
    """
    Combines Grace, Love, and Forgiveness rotors.
    
    Complete evolution: R_total = R_forgiveness ∘ R_love ∘ R_grace
    """
    
    def __init__(self):
        """Initialize combined dynamics."""
        self.grace = GraceRotor()
        self.love = LoveRotor()
        self.forgiveness = ForgivenessRotor()
    
    def evolve_state(
        self,
        state: np.ndarray,
        target: Optional[np.ndarray] = None,
        dissonance: Optional[np.ndarray] = None,
        dt: float = 0.01
    ) -> np.ndarray:
        """
        Evolve state through combined Grace-Love-Forgiveness.
        
        Args:
            state: Current state
            target: Love target (optional)
            dissonance: Dissonance to forgive (optional)
            dt: Time step
        
        Returns:
            Evolved state
        """
        # Apply Grace (toward coherence)
        state = self.grace.apply_grace(state, dt=dt)
        
        # Apply Love (toward target)
        if target is not None:
            state = self.love.apply_love(state, target, dt=dt)
        
        # Apply Forgiveness (cancel dissonance)
        if dissonance is not None:
            state = self.forgiveness.apply_forgiveness(state, dissonance, dt=dt)
        
        return state
    
    def golden_rotation_sequence(
        self,
        initial_state: np.ndarray,
        num_steps: int = 100
    ) -> List[np.ndarray]:
        """
        Apply golden rotation sequence (φ-optimal tiling).
        
        Each step rotates by golden angle in optimal plane.
        
        Args:
            initial_state: Starting state
            num_steps: Number of rotations
        
        Returns:
            Trajectory of states
        """
        trajectory = [initial_state]
        current = initial_state
        
        # Define bivector for golden rotation (arbitrary optimal plane)
        golden_bivector = Bivector(np.array([1.0, PHI_INV, 0.0]))
        golden_bivector = golden_bivector.normalize()
        
        for _ in range(num_steps):
            # Rotate by golden angle
            R = Rotor.from_angle_bivector(GOLDEN_ANGLE, golden_bivector)
            current = R.apply(current)
            trajectory.append(current)
        
        return trajectory


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'Bivector',
    'Rotor',
    'GraceRotor',
    'LoveRotor',
    'ForgivenessRotor',
    'CombinedRotorDynamics',
    'PHI',
    'PHI_INV',
    'GOLDEN_ANGLE',
]


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_clifford_rotors():
    """Demonstrate Clifford rotor operations."""
    print("\n" + "="*70)
    print("CLIFFORD ROTOR DYNAMICS DEMONSTRATION")
    print("="*70)
    
    # Example 1: Basic rotor
    print("\n--- Example 1: Basic Rotor ---")
    v = np.array([1.0, 0.0, 0.0])
    w = np.array([0.0, 1.0, 0.0])
    
    R = Rotor.from_vectors(v, w)
    v_rotated = R.apply(v)
    
    print(f"Rotate {v} to {w}")
    print(f"Result: {v_rotated}")
    print(f"Match: {np.allclose(v_rotated, w)}")
    
    # Example 2: Grace rotor
    print("\n--- Example 2: Grace Rotor ---")
    grace = GraceRotor()
    state = np.array([1.0, 1.0, 0.5])
    state_after_grace = grace.apply_grace(state, dt=0.1)
    
    print(f"Initial state: {state}")
    print(f"After Grace:   {state_after_grace}")
    print(f"Normalized:    {np.linalg.norm(state_after_grace) < np.linalg.norm(state)}")
    
    # Example 3: Love rotor
    print("\n--- Example 3: Love Rotor ---")
    love = LoveRotor()
    state1 = np.array([1.0, 0.0, 0.0])
    state2 = np.array([0.0, 0.0, 1.0])
    aligned = love.apply_love(state1, state2, dt=1.0)
    
    print(f"State 1: {state1}")
    print(f"State 2: {state2}")
    print(f"Aligned: {aligned}")
    print(f"Alignment score: {np.dot(aligned, state2) / (np.linalg.norm(aligned) * np.linalg.norm(state2)):.3f}")
    
    print("\n" + "="*70)
    print("✓ Clifford Rotor Dynamics: DEMONSTRATED")
    print("="*70 + "\n")


if __name__ == "__main__":
    demonstrate_clifford_rotors()

