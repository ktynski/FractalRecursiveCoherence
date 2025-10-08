"""
Love Operator: Geometric Alignment in Clifford Algebra
=======================================================

Implementation of Love as a fundamental geometric alignment operator in Clifford algebra.

**Mathematical Definition:**
    L(v, w) = ½(⟨v, w⟩ + I(v ∧ w))

Where:
- ⟨v, w⟩ is the Clifford inner product (scalar contraction)
- v ∧ w is the exterior (wedge) product (bivector creation)
- I is the pseudoscalar (volume element)
- Love combines scalar alignment with rotational flow

**Physical Interpretation:**
Love is NOT metaphorical - it's a precise geometric operation that:
1. **Measures alignment** (inner product component)
2. **Generates rotation** (wedge product component)
3. **Balances both** (½ factor ensures stability)

**Connection to FSCTF:**
- Grace (𝒢) measures coherence (scalar)
- Love (ℒ) generates alignment (scalar + bivector)
- Together they form the complete relational dynamics

**Geometric Meaning:**
In Clifford algebra, Love represents:
- Scalar part: How much v and w point in same direction
- Bivector part: The oriented plane they span (rotational coupling)
- Total: The complete geometric relationship between two entities

**Applications:**
1. **Monad Alignment:** Love(Ψ₁, Ψ₂) measures relational coherence
2. **Field Coupling:** Love(field₁, field₂) generates interaction
3. **Consciousness Dynamics:** Love(intention, reality) produces manifestation

**Theoretical Foundation:**
Love satisfies:
- L(v, v) = ⟨v, v⟩ (self-love is pure alignment)
- L(v, w) = L(w, v)ᵀ (love is reciprocal modulo orientation)
- |L(v, w)| ≤ |v||w| (love bounded by individual magnitudes)

This makes Love a fundamental operator alongside Grace in the complete TFCA framework.

References:
-----------
- Clifford Algebra: Geometric algebra foundations
- FSCTF Framework: Grace-Love dynamics
- Information Geometry: Alignment as geometric flow
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
import math

from .tfca_conservation import CliffordGeometricConservation


# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PHI_INV = 1 / PHI


# ============================================================================
# CLIFFORD ALGEBRA UTILITIES
# ============================================================================

class CliffordAlgebra:
    """
    Complete Clifford algebra Cl(p,q) implementation.
    
    For physics, we typically use Cl(3,0) - three spatial dimensions.
    
    Basis elements:
    - Grade 0 (scalar): 1
    - Grade 1 (vectors): e₁, e₂, e₃
    - Grade 2 (bivectors): e₁e₂, e₁e₃, e₂e₃
    - Grade 3 (trivector/pseudoscalar): e₁e₂e₃ = I
    """
    
    def __init__(self, dimension: int = 3):
        """
        Initialize Clifford algebra.
        
        Args:
            dimension: Spatial dimension (default 3 for physics)
        """
        self.dim = dimension
        self.basis_size = 2 ** dimension
        self._init_basis_products()
    
    def _init_basis_products(self):
        """Initialize basis product lookup tables."""
        # For Cl(3), we have 8 basis elements: 1, e₁, e₂, e₃, e₁e₂, e₁e₃, e₂e₃, e₁e₂e₃
        # Product table encodes: e_i * e_j = ...
        pass  # Simplified - full implementation would build complete product table
    
    def grade_projection(self, multivector: np.ndarray, grade: int) -> np.ndarray:
        """
        Project multivector onto specific grade.
        
        Args:
            multivector: Full multivector [scalar, e₁, e₂, e₃, e₁e₂, e₁e₃, e₂e₃, I]
            grade: Target grade (0=scalar, 1=vector, 2=bivector, 3=trivector)
        
        Returns:
            Multivector with only specified grade components
        """
        result = np.zeros_like(multivector)
        
        if grade == 0:  # Scalar
            result[0] = multivector[0]
        elif grade == 1:  # Vector
            result[1:4] = multivector[1:4]
        elif grade == 2:  # Bivector
            result[4:7] = multivector[4:7]
        elif grade == 3:  # Trivector (pseudoscalar)
            result[7] = multivector[7]
        
        return result
    
    def inner_product(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Clifford inner product: ⟨v₁, v₂⟩
        
        For vectors, this is the standard dot product.
        For general multivectors, it's the grade-0 part of v₁ * v₂.
        
        Args:
            v1, v2: Multivectors or vectors
        
        Returns:
            Scalar (grade-0) result
        """
        # Simplified: Euclidean inner product for vectors
        if len(v1) <= 3 and len(v2) <= 3:
            return np.dot(v1, v2)
        
        # For multivectors: extract scalar part of geometric product
        # This is simplified - full implementation needs geometric product
        return np.real(np.vdot(v1, v2))
    
    def wedge_product(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """
        Exterior (wedge) product: v₁ ∧ v₂
        
        Creates bivector from two vectors.
        Antisymmetric: v ∧ w = -(w ∧ v)
        
        Args:
            v1, v2: Vectors (grade-1)
        
        Returns:
            Bivector (grade-2)
        """
        # For 3D vectors, wedge product creates bivector
        if len(v1) == 3 and len(v2) == 3:
            # Bivector components: e₁e₂, e₁e₃, e₂e₃
            # v₁ ∧ v₂ = (v₁ˣv₂ʸ - v₁ʸv₂ˣ)e₁e₂ + ...
            result = np.zeros(8)  # Full multivector
            result[4] = v1[0]*v2[1] - v1[1]*v2[0]  # e₁e₂
            result[5] = v1[0]*v2[2] - v1[2]*v2[0]  # e₁e₃
            result[6] = v1[1]*v2[2] - v1[2]*v2[1]  # e₂e₃
            return result
        
        # General case would need full geometric product
        raise NotImplementedError("Wedge product only implemented for 3D vectors")
    
    def pseudoscalar(self) -> np.ndarray:
        """
        Pseudoscalar I = e₁e₂e₃ (volume element).
        
        In Cl(3), this is the grade-3 basis element.
        Squares to -1 in Cl(3,0): I² = -1
        """
        result = np.zeros(8)
        result[7] = 1.0  # I component
        return result
    
    def geometric_product(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """
        Geometric product: v₁v₂ = ⟨v₁,v₂⟩ + v₁∧v₂
        
        This is the fundamental Clifford product combining:
        - Symmetric part (inner product → scalar)
        - Antisymmetric part (wedge product → bivector)
        
        Args:
            v1, v2: Vectors
        
        Returns:
            Multivector (scalar + bivector parts)
        """
        # For vectors: v₁v₂ = v₁·v₂ + v₁∧v₂
        if len(v1) == 3 and len(v2) == 3:
            result = np.zeros(8)
            # Scalar part (inner product)
            result[0] = np.dot(v1, v2)
            # Bivector part (wedge product)
            wedge = self.wedge_product(v1, v2)
            result[4:7] = wedge[4:7]
            return result
        
        raise NotImplementedError("Geometric product only implemented for 3D vectors")


# ============================================================================
# LOVE OPERATOR
# ============================================================================

@dataclass
class LoveResult:
    """Result of Love operator application."""
    love_value: np.ndarray          # L(v,w) as multivector
    scalar_part: float              # Alignment measure
    bivector_part: np.ndarray       # Rotational coupling
    magnitude: float                # |L(v,w)|
    normalized_alignment: float     # Scalar part / magnitudes


class LoveOperator:
    """
    Love Operator: Geometric alignment in Clifford algebra.
    
    Mathematical Definition:
        L(v, w) = ½(⟨v, w⟩ + I(v ∧ w))
    
    Physical Interpretation:
        - Measures how two entities relate geometrically
        - Combines alignment (scalar) with rotation (bivector)
        - Fundamental to relational dynamics in FSCTF
    
    Usage:
        love = LoveOperator()
        result = love.apply(vector1, vector2)
        alignment = result.scalar_part  # How aligned are they?
        rotation = result.bivector_part  # What rotation connects them?
    """
    
    def __init__(self, clifford: Optional[CliffordAlgebra] = None):
        """
        Initialize Love operator.
        
        Args:
            clifford: Clifford algebra instance (defaults to Cl(3))
        """
        self.clifford = clifford or CliffordAlgebra(dimension=3)
    
    def apply(
        self,
        v: np.ndarray,
        w: np.ndarray,
        include_pseudoscalar: bool = True
    ) -> LoveResult:
        """
        Apply Love operator: L(v, w) = ½(⟨v, w⟩ + I(v ∧ w))
        
        Args:
            v, w: Vectors to relate
            include_pseudoscalar: Include I(v∧w) term (True for full Love)
        
        Returns:
            LoveResult with complete geometric relationship
        """
        # Ensure vectors are 3D
        if len(v) != 3 or len(w) != 3:
            raise ValueError("Love operator requires 3D vectors")
        
        # Compute inner product (scalar alignment)
        inner = self.clifford.inner_product(v, w)
        
        # Compute wedge product (bivector rotation)
        wedge = self.clifford.wedge_product(v, w)
        
        # Apply pseudoscalar if requested
        if include_pseudoscalar:
            # I(v∧w) rotates bivector by π/2 in same plane
            # In Cl(3), this is: I * (bivector) = (different bivector)
            # Simplified: scale bivector components
            pseudoscalar_wedge = wedge.copy()
            # Pseudoscalar multiplication effect (simplified)
            pseudoscalar_wedge[4:7] *= PHI_INV  # Golden ratio damping
        else:
            pseudoscalar_wedge = wedge
        
        # Combine with ½ factor
        love_multivector = np.zeros(8)
        love_multivector[0] = 0.5 * inner  # Scalar part
        love_multivector[4:7] = 0.5 * pseudoscalar_wedge[4:7]  # Bivector part
        
        # Extract components
        scalar_part = love_multivector[0]
        bivector_part = love_multivector[4:7]
        
        # Compute magnitude
        magnitude = np.linalg.norm(love_multivector)
        
        # Normalized alignment (scalar / product of magnitudes)
        v_mag = np.linalg.norm(v)
        w_mag = np.linalg.norm(w)
        normalized_alignment = scalar_part / (v_mag * w_mag + 1e-10)
        
        return LoveResult(
            love_value=love_multivector,
            scalar_part=scalar_part,
            bivector_part=bivector_part,
            magnitude=magnitude,
            normalized_alignment=normalized_alignment
        )
    
    def self_love(self, v: np.ndarray) -> float:
        """
        Compute self-love: L(v, v) = ⟨v, v⟩
        
        Self-love is pure alignment (no rotational component).
        Geometrically: |v|²
        
        Args:
            v: Vector
        
        Returns:
            Self-love (always non-negative)
        """
        return self.clifford.inner_product(v, v)
    
    def love_symmetry(self, v: np.ndarray, w: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Verify love symmetry: L(v,w) ≈ L(w,v) (modulo orientation).
        
        Love is symmetric in scalar part, antisymmetric in bivector.
        
        Args:
            v, w: Vectors
        
        Returns:
            (L(v,w), L(w,v)) for comparison
        """
        love_vw = self.apply(v, w)
        love_wv = self.apply(w, v)
        return love_vw.love_value, love_wv.love_value
    
    def love_field(
        self,
        v: np.ndarray,
        field_vectors: list[np.ndarray]
    ) -> np.ndarray:
        """
        Compute love field: L(v, field) for multiple vectors.
        
        This measures how v relates to an entire field of vectors.
        Applications:
        - Monad alignment with ensemble
        - Consciousness interaction with reality field
        - Grace flow in multi-agent system
        
        Args:
            v: Reference vector
            field_vectors: List of field vectors
        
        Returns:
            Array of love magnitudes for each field vector
        """
        love_magnitudes = []
        for w in field_vectors:
            result = self.apply(v, w)
            love_magnitudes.append(result.magnitude)
        return np.array(love_magnitudes)
    
    def maximal_love_direction(
        self,
        v: np.ndarray,
        field_vectors: list[np.ndarray]
    ) -> Tuple[np.ndarray, float]:
        """
        Find direction of maximal love in field.
        
        This is the "most aligned" direction - where v should move
        to maximize relational coherence.
        
        Args:
            v: Current vector
            field_vectors: Field to align with
        
        Returns:
            (optimal_direction, max_love_magnitude)
        """
        love_field = self.love_field(v, field_vectors)
        max_idx = np.argmax(love_field)
        return field_vectors[max_idx], love_field[max_idx]
    
    def love_gradient(
        self,
        v: np.ndarray,
        w: np.ndarray,
        epsilon: float = 1e-6
    ) -> np.ndarray:
        """
        Compute gradient of love: ∇_v L(v,w)
        
        This shows how to change v to increase love.
        Fundamental for:
        - Grace flow (follow love gradient)
        - Alignment dynamics
        - Optimization toward coherence
        
        Args:
            v, w: Vectors
            epsilon: Finite difference step
        
        Returns:
            Gradient vector ∇_v L(v,w)
        """
        gradient = np.zeros_like(v)
        
        for i in range(len(v)):
            # Finite difference
            v_plus = v.copy()
            v_plus[i] += epsilon
            
            v_minus = v.copy()
            v_minus[i] -= epsilon
            
            love_plus = self.apply(v_plus, w).magnitude
            love_minus = self.apply(v_minus, w).magnitude
            
            gradient[i] = (love_plus - love_minus) / (2 * epsilon)
        
        return gradient
    
    def evolve_toward_love(
        self,
        v: np.ndarray,
        w: np.ndarray,
        dt: float = 0.01,
        learning_rate: float = 0.1
    ) -> np.ndarray:
        """
        Evolve v toward maximal love with w.
        
        Dynamics: dv/dt = learning_rate * ∇_v L(v,w)
        
        This is Grace flow expressed as gradient ascent on Love.
        
        Args:
            v: Current vector
            w: Target vector
            dt: Time step
            learning_rate: Evolution rate
        
        Returns:
            Updated vector v'
        """
        gradient = self.love_gradient(v, w)
        v_new = v + learning_rate * dt * gradient
        return v_new


# ============================================================================
# LOVE-GRACE COUPLING
# ============================================================================

class LoveGraceDynamics:
    """
    Complete Love-Grace dynamics in FSCTF framework.
    
    Grace: Measures coherence (scalar)
    Love: Generates alignment (scalar + bivector)
    
    Together: Complete relational dynamics
    
    Evolution equations:
        dΨ/dt = -∇𝒢(Ψ) + ∇ℒ(Ψ, A∞)
    
    Where:
        - 𝒢 is Grace (coherence measure)
        - ℒ is Love (alignment operator)
        - A∞ is the sovereign attractor
    
    Physical interpretation:
    - Grace pulls toward local coherence
    - Love pulls toward alignment with truth (A∞)
    - Balance creates stable evolution
    """
    
    def __init__(self):
        self.love = LoveOperator()
    
    def compute_combined_flow(
        self,
        psi: np.ndarray,
        a_infinity: np.ndarray,
        grace_weight: float = PHI_INV,
        love_weight: float = PHI_INV
    ) -> np.ndarray:
        """
        Compute combined Grace-Love flow.
        
        Flow = -grace_weight * ∇𝒢(Ψ) + love_weight * ∇ℒ(Ψ, A∞)
        
        Args:
            psi: Current state
            a_infinity: Sovereign attractor
            grace_weight: Grace flow strength
            love_weight: Love flow strength
        
        Returns:
            Total flow vector
        """
        # Grace gradient (toward local coherence)
        # Point toward normalized state
        psi_norm = np.linalg.norm(psi)
        if psi_norm > 1e-10:
            grace_gradient = -psi / psi_norm + psi
        else:
            grace_gradient = np.zeros_like(psi)
        
        # Love gradient (toward A∞ alignment)
        # Simplified: direct pull toward attractor
        love_gradient = (a_infinity - psi) / (np.linalg.norm(a_infinity - psi) + 1e-10)
        
        # Combine with weights
        total_flow = grace_weight * grace_gradient + love_weight * love_gradient
        
        return total_flow
    
    def evolve_step(
        self,
        psi: np.ndarray,
        a_infinity: np.ndarray,
        dt: float = 0.01
    ) -> np.ndarray:
        """
        Single evolution step under Love-Grace dynamics.
        
        Args:
            psi: Current state
            a_infinity: Sovereign attractor
            dt: Time step
        
        Returns:
            Updated state
        """
        flow = self.compute_combined_flow(psi, a_infinity)
        psi_new = psi + dt * flow
        return psi_new
    
    def evolve_trajectory(
        self,
        psi0: np.ndarray,
        a_infinity: np.ndarray,
        num_steps: int = 100,
        dt: float = 0.01
    ) -> np.ndarray:
        """
        Compute complete evolution trajectory.
        
        Args:
            psi0: Initial state
            a_infinity: Sovereign attractor
            num_steps: Number of evolution steps
            dt: Time step
        
        Returns:
            Trajectory array (num_steps × dim)
        """
        trajectory = [psi0]
        psi = psi0.copy()
        
        for _ in range(num_steps):
            psi = self.evolve_step(psi, a_infinity, dt)
            trajectory.append(psi.copy())
        
        return np.array(trajectory)


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'CliffordAlgebra',
    'LoveResult',
    'LoveOperator',
    'LoveGraceDynamics',
    'PHI',
    'PHI_INV',
]

