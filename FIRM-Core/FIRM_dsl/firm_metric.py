"""
FIRM Inner Product Implementation

Implements the φ-Fractal Informational Resonance Metric (FIRM) inner product
from FSCTF_AXIOMS.md Section III.

The FIRM extends the Hilbert-Schmidt inner product to capture recursive
self-similarity at all scales via the Grace operator:

    ⟨A, B⟩_{φ,𝒢} := ∑_{n=0}^∞ φ⁻ⁿ ⟨𝒢ⁿ(A), 𝒢ⁿ(B)⟩_hs

Key theorems:
- Convergence (Theorem 3.1): Series converges absolutely under G2
- Norm equivalence (Theorem 3.3): ‖A‖_hs² ≤ ‖A‖_{φ,𝒢}² ≤ U‖A‖_hs²
- Coercivity on core (Theorem 3.4): ‖A‖_{φ,𝒢}² ≥ C_V‖A‖_hs² for A ∈ V
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

# Handle both package and standalone imports
try:
    from .grace_operator import (
        GraceOperator,
        create_default_grace_operator,
        PHI,
        PHI_INVERSE,
        TOLERANCE_CONVERGENCE,
        MAX_ITERATIONS
    )
except ImportError:
    from grace_operator import (
        GraceOperator,
        create_default_grace_operator,
        PHI,
        PHI_INVERSE,
        TOLERANCE_CONVERGENCE,
        MAX_ITERATIONS
    )


@dataclass
class FIRMResult:
    """Result of FIRM inner product computation."""
    value: complex                  # ⟨A, B⟩_{φ,𝒢}
    terms_computed: int             # Number of series terms
    converged: bool                 # Whether series converged
    truncation_error_bound: float   # Upper bound on truncation error
    hs_value: complex               # ⟨A, B⟩_hs for comparison


@dataclass
class FIRMNormResult:
    """Result of FIRM norm computation."""
    norm: float                     # ‖A‖_{φ,𝒢}
    hs_norm: float                  # ‖A‖_hs
    ratio: float                    # ‖A‖_{φ,𝒢} / ‖A‖_hs
    satisfies_lower_bound: bool     # ‖A‖_{φ,𝒢} ≥ ‖A‖_hs
    satisfies_upper_bound: bool     # ‖A‖_{φ,𝒢} ≤ U‖A‖_hs
    coercivity_constant: float      # Actual C_V if in core


class FIRMMetric:
    """
    φ-Fractal Informational Resonance Metric (FIRM).
    
    Provides inner product and norm on operator spaces with recursive
    self-similarity encoded via Grace operator iterations.
    
    Usage:
        firm = FIRMMetric(grace_operator)
        result = firm.inner_product(A, B)
        norm_result = firm.norm(A)
    """
    
    def __init__(
        self,
        grace: Optional[GraceOperator] = None,
        tolerance: float = TOLERANCE_CONVERGENCE,
        max_terms: int = MAX_ITERATIONS
    ):
        self.grace = grace or create_default_grace_operator()
        self.tolerance = tolerance
        self.max_terms = max_terms
        
        # Precompute theoretical bounds (from FSCTF_AXIOMS.md Theorem 3.3)
        kappa = self.grace.params.kappa
        self.upper_bound_constant = 1.0 / (1.0 - kappa**2 / PHI)
    
    def inner_product(
        self,
        A: np.ndarray,
        B: np.ndarray,
        in_core: bool = False
    ) -> FIRMResult:
        """
        Compute FIRM inner product: ⟨A, B⟩_{φ,𝒢}.
        
        Args:
            A, B: Input operators (N×N complex matrices)
            in_core: Whether A, B are in coherence core V
        
        Returns:
            FIRMResult with value and convergence diagnostics
        """
        if A.shape != B.shape or A.shape[0] != A.shape[1]:
            raise ValueError(f"A and B must be square and same size, got {A.shape}, {B.shape}")
        
        # Initialize accumulators
        result_sum = 0.0 + 0.0j
        phi_power = 1.0
        A_n, B_n = A.copy(), B.copy()
        
        # Compute HS inner product for comparison
        hs_value = self._hs_inner_product(A, B)
        
        # Iterate φ-weighted Grace series
        for n in range(self.max_terms):
            # Current term: φ⁻ⁿ ⟨𝒢ⁿ(A), 𝒢ⁿ(B)⟩_hs
            term = self._hs_inner_product(A_n, B_n) / phi_power
            result_sum += term
            
            # Check convergence
            term_magnitude = abs(term)
            if term_magnitude < self.tolerance:
                # Estimate truncation error bound
                # Remaining series: ∑_{k=n+1}^∞ φ⁻ᵏ κ²ᵏ ‖A‖‖B‖
                # ≤ (φ⁻ⁿ⁺¹ κ²⁽ⁿ⁺¹⁾) / (1 - κ²/φ) ‖A‖‖B‖
                error_bound = term_magnitude * self.grace.params.kappa**2 / (1.0 - self.grace.params.kappa**2 / PHI)
                
                return FIRMResult(
                    value=result_sum,
                    terms_computed=n + 1,
                    converged=True,
                    truncation_error_bound=error_bound,
                    hs_value=hs_value
                )
            
            # Apply Grace operator for next iteration
            A_n = self.grace.apply(A_n, in_core=in_core, verify_axioms=False).output
            B_n = self.grace.apply(B_n, in_core=in_core, verify_axioms=False).output
            phi_power *= PHI
        
        # Did not converge
        print(f"⚠️  FIRM series did not converge in {self.max_terms} terms")
        return FIRMResult(
            value=result_sum,
            terms_computed=self.max_terms,
            converged=False,
            truncation_error_bound=float('inf'),
            hs_value=hs_value
        )
    
    def norm(
        self,
        A: np.ndarray,
        in_core: bool = False
    ) -> FIRMNormResult:
        """
        Compute FIRM norm: ‖A‖_{φ,𝒢} = √⟨A, A⟩_{φ,𝒢}.
        
        Args:
            A: Input operator
            in_core: Whether A is in coherence core V
        
        Returns:
            FIRMNormResult with norm and bound verification
        """
        # Compute FIRM inner product with self
        inner_result = self.inner_product(A, A, in_core=in_core)
        firm_norm_squared = inner_result.value.real
        
        if firm_norm_squared < 0:
            raise ValueError(f"FIRM norm squared is negative: {firm_norm_squared:.6e}")
        
        firm_norm = np.sqrt(firm_norm_squared)
        hs_norm = np.sqrt(self._hs_inner_product(A, A).real)
        
        # Check norm equivalence bounds (Theorem 3.3)
        ratio = firm_norm / hs_norm if hs_norm > 1e-15 else 0.0
        
        satisfies_lower = firm_norm >= hs_norm - self.tolerance
        satisfies_upper = firm_norm <= self.upper_bound_constant * hs_norm + self.tolerance
        
        # Compute actual coercivity constant if in core
        coercivity_constant = 1.0
        if in_core:
            mu = self.grace.params.mu
            coercivity_constant = 1.0 / (1.0 - mu**2 / PHI)
        
        return FIRMNormResult(
            norm=firm_norm,
            hs_norm=hs_norm,
            ratio=ratio,
            satisfies_lower_bound=satisfies_lower,
            satisfies_upper_bound=satisfies_upper,
            coercivity_constant=coercivity_constant
        )
    
    def verify_inner_product_axioms(
        self,
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray,
        alpha: complex = 1.0 + 1.0j,
        beta: complex = 2.0 - 0.5j
    ) -> dict:
        """
        Verify FIRM satisfies inner product axioms:
        1. Conjugate symmetry: ⟨A, B⟩ = ⟨B, A⟩*
        2. Linearity: ⟨αA + βB, C⟩ = α⟨A,C⟩ + β⟨B,C⟩
        3. Positive-definiteness: ⟨A, A⟩ ≥ 0, with equality iff A=0
        
        Returns:
            dict with verification results
        """
        # 1. Conjugate symmetry
        AB = self.inner_product(A, B).value
        BA = self.inner_product(B, A).value
        sym_error = abs(AB - BA.conjugate())
        
        # 2. Linearity
        lin_combo = alpha * A + beta * B
        lhs = self.inner_product(lin_combo, C).value
        rhs = alpha * self.inner_product(A, C).value + beta * self.inner_product(B, C).value
        lin_error = abs(lhs - rhs)
        
        # 3. Positive-definiteness
        AA = self.inner_product(A, A).value.real
        pos_def = AA >= -self.tolerance
        
        return {
            "conjugate_symmetry": sym_error < self.tolerance,
            "conjugate_symmetry_error": sym_error,
            "linearity": lin_error < self.tolerance,
            "linearity_error": lin_error,
            "positive_definite": pos_def,
            "self_inner_product": AA
        }
    
    @staticmethod
    def _hs_inner_product(A: np.ndarray, B: np.ndarray) -> complex:
        """Hilbert-Schmidt inner product: ⟨A, B⟩_hs = Tr(A†B)."""
        return np.trace(A.conj().T @ B)


# ============================================================================
# Utility Functions
# ============================================================================

def compute_firm_distance(
    A: np.ndarray,
    B: np.ndarray,
    firm: Optional[FIRMMetric] = None
) -> float:
    """
    Compute FIRM distance: d(A, B) = ‖A - B‖_{φ,𝒢}.
    
    This defines a metric on operator space compatible with Grace flow.
    """
    firm = firm or FIRMMetric()
    diff = A - B
    return firm.norm(diff).norm


def compute_firm_angle(
    A: np.ndarray,
    B: np.ndarray,
    firm: Optional[FIRMMetric] = None
) -> float:
    """
    Compute angle between operators in FIRM geometry:
    
        cos(θ) = Re(⟨A, B⟩_{φ,𝒢}) / (‖A‖_{φ,𝒢} ‖B‖_{φ,𝒢})
    
    Returns angle in radians [0, π].
    """
    firm = firm or FIRMMetric()
    
    inner = firm.inner_product(A, B).value.real
    norm_A = firm.norm(A).norm
    norm_B = firm.norm(B).norm
    
    if norm_A < 1e-15 or norm_B < 1e-15:
        return 0.0
    
    cos_theta = inner / (norm_A * norm_B)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)  # Numerical safety
    
    return np.arccos(cos_theta)


def compute_coercivity_constant(kappa: float, mu: float) -> float:
    """
    Compute theoretical coercivity constant C_V from FSCTF_AXIOMS.md Theorem 3.4:
    
        C_V = (1 - μ²/φ)⁻¹
    
    This gives the lower bound ‖A‖_{φ,𝒢}² ≥ C_V ‖A‖_hs² for A ∈ V.
    """
    if mu > kappa:
        raise ValueError(f"μ ({mu}) cannot exceed κ ({kappa})")
    return 1.0 / (1.0 - mu**2 / PHI)


# ============================================================================
# Main (Self-Test)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FIRM Inner Product Self-Test")
    print("=" * 70)
    
    # Create test matrices
    N = 4
    np.random.seed(42)
    A = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    A = (A + A.conj().T) / 2  # Hermitian
    B = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    B = (B + B.conj().T) / 2
    C = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    C = (C + C.conj().T) / 2
    
    print(f"\nTest matrices: A, B, C ({N}×{N} Hermitian)")
    
    # Create FIRM metric
    firm = FIRMMetric()
    print(f"\n📐 FIRM Configuration:")
    print(f"   κ = {firm.grace.params.kappa:.6f}")
    print(f"   μ = {firm.grace.params.mu:.6f}")
    print(f"   Upper bound constant U = {firm.upper_bound_constant:.6f}")
    
    # Test inner product
    print(f"\n🔢 Inner Product Test:")
    result_AB = firm.inner_product(A, B)
    print(f"   ⟨A, B⟩_{{φ,𝒢}} = {result_AB.value:.6f}")
    print(f"   ⟨A, B⟩_hs = {result_AB.hs_value:.6f}")
    print(f"   Terms computed: {result_AB.terms_computed}")
    print(f"   Converged: {result_AB.converged}")
    print(f"   Truncation error bound: {result_AB.truncation_error_bound:.2e}")
    
    # Test norm
    print(f"\n📏 Norm Test:")
    norm_A = firm.norm(A)
    print(f"   ‖A‖_{{φ,𝒢}} = {norm_A.norm:.6f}")
    print(f"   ‖A‖_hs = {norm_A.hs_norm:.6f}")
    print(f"   Ratio = {norm_A.ratio:.6f}")
    print(f"   Lower bound satisfied: {norm_A.satisfies_lower_bound}")
    print(f"   Upper bound satisfied: {norm_A.satisfies_upper_bound}")
    
    # Verify axioms
    print(f"\n✅ Axiom Verification:")
    axioms = firm.verify_inner_product_axioms(A, B, C)
    print(f"   Conjugate symmetry: {axioms['conjugate_symmetry']}")
    print(f"      Error: {axioms['conjugate_symmetry_error']:.2e}")
    print(f"   Linearity: {axioms['linearity']}")
    print(f"      Error: {axioms['linearity_error']:.2e}")
    print(f"   Positive-definite: {axioms['positive_definite']}")
    print(f"      ⟨A,A⟩ = {axioms['self_inner_product']:.6f}")
    
    # Test geometric operations
    print(f"\n📐 Geometric Operations:")
    distance = compute_firm_distance(A, B, firm)
    angle = compute_firm_angle(A, B, firm)
    print(f"   d(A, B) = {distance:.6f}")
    print(f"   ∠(A, B) = {np.degrees(angle):.2f}°")
    
    # Test coercivity
    print(f"\n🎯 Coercivity Analysis:")
    C_V = compute_coercivity_constant(firm.grace.params.kappa, firm.grace.params.mu)
    print(f"   Theoretical C_V = {C_V:.6f}")
    print(f"   Actual ‖A‖²_{{φ,𝒢}} / ‖A‖²_hs = {(norm_A.norm / norm_A.hs_norm)**2:.6f}")
    
    print("\n" + "=" * 70)
    print("✅ FIRM Inner Product Self-Test Complete")
    print("=" * 70)

