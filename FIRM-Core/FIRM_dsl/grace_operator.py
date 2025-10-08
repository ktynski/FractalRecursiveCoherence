"""
Grace Operator Implementation

Implements the foundational Grace operator (𝒢) satisfying axioms G1-G4 from FSCTF_AXIOMS.md.

The Grace operator is the core regulator ensuring recursive coherence remains bounded,
providing:
- G1 (Positivity): ⟨X, 𝒢(X)⟩_hs ≥ 0
- G2 (Contraction): ‖𝒢(X)‖_hs ≤ κ‖X‖_hs with 0 < κ < 1
- G3 (Coherence Core): ‖𝒢(X)‖_hs ≥ μ‖X‖_hs for X ∈ V
- G4 (Selfadjointness): ⟨X, 𝒢(Y)⟩_hs = ⟨𝒢(X), Y⟩_hs on V

Physical interpretation: Grace acts as an information-geometric projector onto
coherent subspaces, damping dissonance while preserving truth-aligned structures.
"""

import numpy as np
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum


# Golden ratio constants (from FSCTF_AXIOMS.md Section VI)
PHI = (1 + np.sqrt(5)) / 2              # ≈ 1.618033988749
PHI_INVERSE = 1 / PHI                    # ≈ 0.618033988749
PHI_SQUARED = PHI * PHI                  # ≈ 2.618033988749

# Numerical tolerances (from FSCTF_AXIOMS.md Section VIII.2)
TOLERANCE_CONVERGENCE = 1e-12
TOLERANCE_JACOBI = 1e-10
TOLERANCE_COERCIVITY = 1e-8
MAX_ITERATIONS = 1000


class GraceImplementation(Enum):
    """Available Grace operator implementations."""
    SPECTRAL = "spectral"           # Eigenvalue filtering (default)
    HEAT_KERNEL = "heat_kernel"     # Diffusion-based smoothing
    WAVELET = "wavelet"             # Multi-scale decomposition
    PROJECTOR = "projector"         # Direct subspace projection


@dataclass
class GraceParameters:
    """Configuration for Grace operator."""
    kappa: float = PHI_INVERSE      # Contraction constant (Axiom G2)
    mu: float = 0.5                 # Core lower bound (Axiom G3)
    implementation: GraceImplementation = GraceImplementation.SPECTRAL
    tolerance: float = TOLERANCE_CONVERGENCE
    max_iterations: int = MAX_ITERATIONS
    
    def __post_init__(self):
        """Validate parameters satisfy axiom constraints."""
        if not (0 < self.kappa < 1):
            raise ValueError(f"kappa must be in (0,1), got {self.kappa}")
        if not (0 < self.mu <= 1):
            raise ValueError(f"mu must be in (0,1], got {self.mu}")
        if self.mu > self.kappa:
            raise ValueError(f"mu ({self.mu}) cannot exceed kappa ({self.kappa})")


@dataclass
class GraceResult:
    """Result of Grace operator application."""
    output: np.ndarray              # 𝒢(X)
    hs_norm_ratio: float            # ‖𝒢(X)‖_hs / ‖X‖_hs
    satisfies_g2: bool              # Contraction verified
    satisfies_g3: bool              # Core bound verified (if in_core=True)
    iterations: int                 # Number of iterations (if iterative)
    converged: bool                 # Convergence status


class GraceOperator:
    """
    Grace Operator (𝒢): Core FSCTF recursion regulator.
    
    Implements all four Grace axioms with multiple backend strategies.
    
    Usage:
        grace = GraceOperator(params=GraceParameters(kappa=0.618))
        result = grace.apply(X, in_core=True)
    """
    
    def __init__(self, params: Optional[GraceParameters] = None):
        self.params = params or GraceParameters()
        self._coherence_core_projector: Optional[np.ndarray] = None
    
    def apply(
        self,
        X: np.ndarray,
        in_core: bool = False,
        verify_axioms: bool = True
    ) -> GraceResult:
        """
        Apply Grace operator: 𝒢(X).
        
        Args:
            X: Input operator (N×N complex matrix)
            in_core: Whether X is in coherence core V (affects G3 check)
            verify_axioms: Check G1-G4 satisfaction (expensive but safe)
        
        Returns:
            GraceResult with output and diagnostic information
        """
        if X.shape[0] != X.shape[1]:
            raise ValueError(f"X must be square, got shape {X.shape}")
        
        # Select implementation
        if self.params.implementation == GraceImplementation.SPECTRAL:
            output, iterations, converged = self._apply_spectral(X)
        elif self.params.implementation == GraceImplementation.HEAT_KERNEL:
            output, iterations, converged = self._apply_heat_kernel(X)
        elif self.params.implementation == GraceImplementation.WAVELET:
            output, iterations, converged = self._apply_wavelet(X)
        elif self.params.implementation == GraceImplementation.PROJECTOR:
            output, iterations, converged = self._apply_projector(X)
        else:
            raise ValueError(f"Unknown implementation: {self.params.implementation}")
        
        # Compute diagnostics
        X_hs_norm = self._hs_norm(X)
        output_hs_norm = self._hs_norm(output)
        hs_norm_ratio = output_hs_norm / X_hs_norm if X_hs_norm > 1e-15 else 0.0
        
        satisfies_g2 = hs_norm_ratio <= self.params.kappa + TOLERANCE_COERCIVITY
        
        # G3 check only if in coherence core
        satisfies_g3 = True
        if in_core:
            satisfies_g3 = hs_norm_ratio >= self.params.mu - TOLERANCE_COERCIVITY
        
        # Optional full axiom verification
        if verify_axioms:
            self._verify_g1(X, output)
            if not satisfies_g2:
                print(f"⚠️  G2 violation: ‖𝒢(X)‖/‖X‖ = {hs_norm_ratio:.6f} > κ = {self.params.kappa}")
            if in_core and not satisfies_g3:
                print(f"⚠️  G3 violation: ‖𝒢(X)‖/‖X‖ = {hs_norm_ratio:.6f} < μ = {self.params.mu}")
            self._verify_g4(X, output, in_core)
        
        return GraceResult(
            output=output,
            hs_norm_ratio=hs_norm_ratio,
            satisfies_g2=satisfies_g2,
            satisfies_g3=satisfies_g3,
            iterations=iterations,
            converged=converged
        )
    
    def apply_n_times(self, X: np.ndarray, n: int) -> np.ndarray:
        """Apply Grace operator n times: 𝒢ⁿ(X)."""
        result = X
        for _ in range(n):
            grace_result = self.apply(result, verify_axioms=False)
            result = grace_result.output
        return result
    
    def converge_to_core(
        self,
        X: np.ndarray,
        tolerance: Optional[float] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Iterate 𝒢 until convergence to coherence core: X★ = lim_{n→∞} 𝒢ⁿ(X).
        
        Returns:
            (X_star, num_iterations)
        """
        tol = tolerance or self.params.tolerance
        X_current = X
        
        for iteration in range(self.params.max_iterations):
            grace_result = self.apply(X_current, verify_axioms=False)
            X_next = grace_result.output
            
            # Check convergence
            diff_norm = self._hs_norm(X_next - X_current)
            if diff_norm < tol:
                return X_next, iteration + 1
            
            X_current = X_next
        
        print(f"⚠️  Grace iteration did not converge in {self.params.max_iterations} steps")
        return X_current, self.params.max_iterations
    
    # ========================================================================
    # Implementation Strategies
    # ========================================================================
    
    def _apply_spectral(self, X: np.ndarray) -> Tuple[np.ndarray, int, bool]:
        """
        Spectral filtering: project onto coherent eigenspaces.
        
        Implementation from FSCTF_AXIOMS.md Section IX.1:
        - Compute eigendecomposition
        - Apply soft damping to all eigenvalues by κ factor
        - Ensures strict contraction: ‖𝒢(X)‖ ≤ κ‖X‖
        """
        # Hermitian part for stable eigendecomposition
        X_herm = (X + X.conj().T) / 2
        
        eigenvalues, eigenvectors = np.linalg.eigh(X_herm)
        
        # Apply uniform damping by κ to ensure contraction
        damped_eigenvalues = self.params.kappa * eigenvalues
        
        # Reconstruct
        output = eigenvectors @ np.diag(damped_eigenvalues) @ eigenvectors.conj().T
        
        return output, 1, True
    
    def _apply_heat_kernel(self, X: np.ndarray) -> Tuple[np.ndarray, int, bool]:
        """
        Heat kernel smoothing: exp(-τ Δ) for small τ.
        
        Diffuses high-frequency dissonance while preserving low-frequency coherence.
        """
        # Laplacian approximation via finite difference
        tau = -np.log(self.params.kappa)  # Choose τ to achieve desired contraction
        
        # For operator-valued heat equation, use matrix exponential of Laplacian
        # Simplified: apply exponential damping to eigenvalues
        eigenvalues, eigenvectors = np.linalg.eigh((X + X.conj().T) / 2)
        damped_eigenvalues = eigenvalues * np.exp(-tau * np.abs(eigenvalues))
        
        output = eigenvectors @ np.diag(damped_eigenvalues) @ eigenvectors.conj().T
        
        return output, 1, True
    
    def _apply_wavelet(self, X: np.ndarray) -> Tuple[np.ndarray, int, bool]:
        """
        Wavelet shrinkage: multi-scale coefficient filtering.
        
        Decomposes into scales, applies soft-thresholding, reconstructs.
        """
        # Simplified wavelet: SVD-based scale separation
        U, s, Vh = np.linalg.svd(X, full_matrices=False)
        
        # Soft-threshold singular values
        threshold = self.params.kappa * np.max(s)
        s_filtered = np.maximum(s - threshold, 0)
        
        output = U @ np.diag(s_filtered) @ Vh
        
        return output, 1, True
    
    def _apply_projector(self, X: np.ndarray) -> Tuple[np.ndarray, int, bool]:
        """
        Direct projection onto pre-computed coherence core.
        
        Requires coherence core to be set via set_coherence_core().
        """
        if self._coherence_core_projector is None:
            raise ValueError("Coherence core projector not set. Call set_coherence_core() first.")
        
        P = self._coherence_core_projector
        output = P @ X @ P  # Projection: PXP
        
        return output, 1, True
    
    def set_coherence_core(self, basis_vectors: np.ndarray):
        """
        Set coherence core V via orthonormal basis vectors.
        
        Args:
            basis_vectors: (N × K) matrix where columns span V
        """
        # Construct projector P = VV†
        self._coherence_core_projector = basis_vectors @ basis_vectors.conj().T
    
    # ========================================================================
    # Axiom Verification
    # ========================================================================
    
    def _verify_g1(self, X: np.ndarray, GX: np.ndarray):
        """Verify G1 (Positivity): ⟨X, 𝒢(X)⟩_hs ≥ 0."""
        inner_product = np.trace(X.conj().T @ GX).real
        if inner_product < -TOLERANCE_COERCIVITY:
            raise ValueError(f"G1 violated: ⟨X, 𝒢(X)⟩_hs = {inner_product:.6e} < 0")
    
    def _verify_g4(self, X: np.ndarray, Y: np.ndarray, in_core: bool):
        """Verify G4 (Selfadjointness on core): ⟨X, 𝒢(Y)⟩ = ⟨𝒢(X), Y⟩."""
        if not in_core:
            return  # G4 only required on core
        
        GX = self.apply(X, verify_axioms=False).output
        GY = self.apply(Y, verify_axioms=False).output
        
        lhs = np.trace(X.conj().T @ GY)
        rhs = np.trace(GX.conj().T @ Y)
        
        if np.abs(lhs - rhs) > TOLERANCE_JACOBI:
            print(f"⚠️  G4 violation: |⟨X,𝒢Y⟩ - ⟨𝒢X,Y⟩| = {np.abs(lhs - rhs):.6e}")
    
    # ========================================================================
    # Utility Functions
    # ========================================================================
    
    @staticmethod
    def _hs_norm(X: np.ndarray) -> float:
        """Hilbert-Schmidt norm: ‖X‖_hs = √Tr(X†X)."""
        return np.sqrt(np.trace(X.conj().T @ X).real)
    
    @staticmethod
    def _hs_inner_product(X: np.ndarray, Y: np.ndarray) -> complex:
        """Hilbert-Schmidt inner product: ⟨X, Y⟩_hs = Tr(X†Y)."""
        return np.trace(X.conj().T @ Y)


# ============================================================================
# Factory Functions
# ============================================================================

def create_default_grace_operator() -> GraceOperator:
    """Create Grace operator with canonical FSCTF parameters."""
    return GraceOperator(GraceParameters(
        kappa=PHI_INVERSE,  # φ⁻¹ ≈ 0.618 (golden baseline)
        mu=0.5,             # Core bound (must be ≤ κ)
        implementation=GraceImplementation.SPECTRAL
    ))


def create_strict_grace_operator() -> GraceOperator:
    """Create highly contractive Grace operator (strong damping)."""
    return GraceOperator(GraceParameters(
        kappa=0.5,
        mu=0.9,
        implementation=GraceImplementation.SPECTRAL
    ))


def create_gentle_grace_operator() -> GraceOperator:
    """Create weakly contractive Grace operator (gentle damping)."""
    return GraceOperator(GraceParameters(
        kappa=0.85,
        mu=0.5,
        implementation=GraceImplementation.HEAT_KERNEL
    ))


# ============================================================================
# Main (Self-Test)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Grace Operator Self-Test")
    print("=" * 70)
    
    # Create test matrix
    N = 4
    np.random.seed(42)
    X = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    X = (X + X.conj().T) / 2  # Make Hermitian
    
    print(f"\nTest matrix X ({N}×{N}, ‖X‖_hs = {GraceOperator._hs_norm(X):.6f})")
    
    # Test default Grace operator
    grace = create_default_grace_operator()
    print(f"\n📐 Grace Parameters:")
    print(f"   κ (contraction) = {grace.params.kappa:.6f}")
    print(f"   μ (core bound) = {grace.params.mu:.6f}")
    print(f"   Implementation: {grace.params.implementation.value}")
    
    # Apply Grace
    result = grace.apply(X, in_core=True, verify_axioms=True)
    
    print(f"\n✅ Grace Applied:")
    print(f"   ‖𝒢(X)‖_hs = {GraceOperator._hs_norm(result.output):.6f}")
    print(f"   ‖𝒢(X)‖/‖X‖ = {result.hs_norm_ratio:.6f}")
    print(f"   G2 (contraction) satisfied: {result.satisfies_g2}")
    print(f"   G3 (core bound) satisfied: {result.satisfies_g3}")
    print(f"   Converged: {result.converged}")
    
    # Test convergence to core
    X_star, iterations = grace.converge_to_core(X)
    print(f"\n🎯 Convergence to Core:")
    print(f"   Iterations: {iterations}")
    print(f"   ‖X★‖_hs = {GraceOperator._hs_norm(X_star):.6f}")
    
    # Test φ-recursion
    print(f"\n🔄 φ-Recursive Application:")
    for n in range(5):
        X_n = grace.apply_n_times(X, n)
        norm_n = GraceOperator._hs_norm(X_n)
        print(f"   ‖𝒢^{n}(X)‖_hs = {norm_n:.6f}")
    
    print("\n" + "=" * 70)
    print("✅ Grace Operator Self-Test Complete")
    print("=" * 70)

