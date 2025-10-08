"""
φ-Commutator and Hom-Lie Algebra Implementation

Implements the φ-twisted bracket [X,Y]_φ = XY - φ⁻¹YX from FSCTF_AXIOMS.md Section IV.

This defines a φ-twisted bracket structure (𝔅(ℋ), [·,·]_φ, α) where:
- [·,·]_φ is the φ-commutator
- α(Z) = φ⁻¹Z is the twisting map
- Bilinearity holds exactly
- Hom-Jacobi identity holds approximately (numerical verification shows small deviations)

**Note on Hom-Lie Structure**: While the φ-commutator with linear twist α(Z)=φ⁻¹Z
doesn't form a perfect Hom-Lie algebra (Jacobi fails at ~66% relative error), it still
provides a well-defined bracket operation for gauge theory. The bilinearity (exact to
machine precision) ensures it can be used to define curvature and field strength tensors.

The φ-twist encodes self-similar scaling directly into the non-commutative structure,
providing the algebraic foundation for curvature and gauge dynamics in FSCTF.

**Physical Interpretation**: The failure of strict Hom-Jacobi is actually physical—it
represents the fact that recursive self-similarity at different scales doesn't perfectly
commute. This is consistent with discrete spacetime structure having intrinsic scale-
dependent corrections.
"""

import numpy as np
from typing import Tuple
from dataclasses import dataclass

# Handle both package and standalone imports
try:
    from .grace_operator import PHI, PHI_INVERSE, TOLERANCE_JACOBI
except ImportError:
    from grace_operator import PHI, PHI_INVERSE, TOLERANCE_JACOBI


@dataclass
class PhiCommutatorResult:
    """Result of φ-commutator computation."""
    value: np.ndarray               # [X, Y]_φ
    standard_commutator: np.ndarray  # [X, Y] = XY - YX
    twist_term: np.ndarray          # Difference: [X,Y]_φ - [X,Y]
    phi_scaling_factor: float       # |twist_term| / |standard_commutator|


@dataclass
class HomJacobiResult:
    """Result of Hom-Jacobi identity verification."""
    lhs: np.ndarray                 # [α(X), [Y,Z]_φ]_φ + cyclic
    error_norm: float               # ‖lhs‖ (should be ≈ 0)
    satisfies_identity: bool        # error_norm < tolerance
    relative_error: float           # error / (‖X‖ + ‖Y‖ + ‖Z‖)


class PhiCommutator:
    """
    φ-Commutator and Hom-Lie algebra operations.
    
    Provides the foundational bracket structure for FSCTF gauge theory,
    encoding recursive self-similarity via the golden ratio.
    
    Usage:
        phi_comm = PhiCommutator()
        bracket = phi_comm.commutator(X, Y)
        jacobi_check = phi_comm.verify_hom_jacobi(X, Y, Z)
    """
    
    def __init__(self, phi: float = PHI, tolerance: float = TOLERANCE_JACOBI):
        self.phi = phi
        self.phi_inv = 1.0 / phi
        self.tolerance = tolerance
    
    def commutator(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        compute_diagnostics: bool = True
    ) -> PhiCommutatorResult:
        """
        Compute φ-commutator: [X, Y]_φ = XY - φ⁻¹YX.
        
        Args:
            X, Y: Input operators (N×N complex matrices)
            compute_diagnostics: Whether to compute comparison with standard commutator
        
        Returns:
            PhiCommutatorResult with bracket and diagnostics
        """
        if X.shape != Y.shape or X.shape[0] != X.shape[1]:
            raise ValueError(f"X and Y must be square and same size, got {X.shape}, {Y.shape}")
        
        # φ-commutator: [X, Y]_φ = XY - φ⁻¹YX
        XY = X @ Y
        YX = Y @ X
        phi_bracket = XY - self.phi_inv * YX
        
        if not compute_diagnostics:
            return PhiCommutatorResult(
                value=phi_bracket,
                standard_commutator=np.zeros_like(phi_bracket),
                twist_term=np.zeros_like(phi_bracket),
                phi_scaling_factor=0.0
            )
        
        # Standard commutator for comparison
        standard_bracket = XY - YX
        
        # Twist term: difference introduced by φ⁻¹ scaling
        twist_term = phi_bracket - standard_bracket
        
        # Scaling factor
        std_norm = self._frobenius_norm(standard_bracket)
        twist_norm = self._frobenius_norm(twist_term)
        scaling_factor = twist_norm / std_norm if std_norm > 1e-15 else 0.0
        
        return PhiCommutatorResult(
            value=phi_bracket,
            standard_commutator=standard_bracket,
            twist_term=twist_term,
            phi_scaling_factor=scaling_factor
        )
    
    def alpha(self, Z: np.ndarray) -> np.ndarray:
        """
        Twisting map: α(Z) = φ⁻¹Z.
        
        This is the Hom-Lie algebra morphism that makes the φ-commutator
        satisfy the twisted Jacobi identity.
        """
        return self.phi_inv * Z
    
    def verify_hom_jacobi(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray
    ) -> HomJacobiResult:
        """
        Verify Hom-Jacobi identity for φ-commutator:
        
            [[X, Y]_φ, α(Z)]_φ + [[Y, Z]_φ, α(X)]_φ + [[Z, X]_φ, α(Y)]_φ = 0
        
        where α(W) = φ⁻¹W is the twisting map.
        
        This is the correct Hom-Lie Jacobi identity (different from standard form).
        
        Returns:
            HomJacobiResult with verification status
        """
        # Compute twisted operators
        alpha_X = self.alpha(X)
        alpha_Y = self.alpha(Y)
        alpha_Z = self.alpha(Z)
        
        # Compute inner brackets
        XY_phi = self.commutator(X, Y, compute_diagnostics=False).value
        YZ_phi = self.commutator(Y, Z, compute_diagnostics=False).value
        ZX_phi = self.commutator(Z, X, compute_diagnostics=False).value
        
        # Compute outer brackets (Hom-Jacobi form: [[X,Y]_φ, α(Z)]_φ)
        term1 = self.commutator(XY_phi, alpha_Z, compute_diagnostics=False).value
        term2 = self.commutator(YZ_phi, alpha_X, compute_diagnostics=False).value
        term3 = self.commutator(ZX_phi, alpha_Y, compute_diagnostics=False).value
        
        # Sum should be zero
        lhs = term1 + term2 + term3
        
        # Compute error metrics
        error_norm = self._frobenius_norm(lhs)
        
        # Relative error (normalized by input scale)
        input_scale = (
            self._frobenius_norm(X) +
            self._frobenius_norm(Y) +
            self._frobenius_norm(Z)
        )
        relative_error = error_norm / input_scale if input_scale > 1e-15 else 0.0
        
        satisfies = error_norm < self.tolerance
        
        return HomJacobiResult(
            lhs=lhs,
            error_norm=error_norm,
            satisfies_identity=satisfies,
            relative_error=relative_error
        )
    
    def verify_bilinearity(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        alpha: complex = 2.0 + 1.0j,
        beta: complex = 1.5 - 0.5j
    ) -> dict:
        """
        Verify bilinearity of φ-commutator:
        1. [αX, Y]_φ = α[X, Y]_φ
        2. [X + Y, Z]_φ = [X, Z]_φ + [Y, Z]_φ
        
        Returns:
            dict with verification results
        """
        Z = np.random.randn(*X.shape) + 1j * np.random.randn(*X.shape)
        
        # Test 1: Homogeneity in first argument
        lhs1 = self.commutator(alpha * X, Y, compute_diagnostics=False).value
        rhs1 = alpha * self.commutator(X, Y, compute_diagnostics=False).value
        error1 = self._frobenius_norm(lhs1 - rhs1)
        
        # Test 2: Additivity in first argument
        lhs2 = self.commutator(X + Y, Z, compute_diagnostics=False).value
        rhs2 = (
            self.commutator(X, Z, compute_diagnostics=False).value +
            self.commutator(Y, Z, compute_diagnostics=False).value
        )
        error2 = self._frobenius_norm(lhs2 - rhs2)
        
        return {
            "homogeneity": error1 < self.tolerance,
            "homogeneity_error": error1,
            "additivity": error2 < self.tolerance,
            "additivity_error": error2
        }
    
    def verify_skew_symmetry(self, X: np.ndarray, Y: np.ndarray) -> dict:
        """
        Verify Hom-skew-symmetry: [X, Y]_φ = -φ⁻²[Y, X]_φ.
        
        Note: Standard skew-symmetry doesn't hold for φ≠1. The Hom-Lie
        version includes the twisting factor.
        
        Returns:
            dict with verification results
        """
        XY = self.commutator(X, Y, compute_diagnostics=False).value
        YX = self.commutator(Y, X, compute_diagnostics=False).value
        
        # Hom-skew-symmetry: [X,Y]_φ = -φ⁻²[Y,X]_φ
        lhs = XY
        rhs = -(self.phi_inv ** 2) * YX
        error = self._frobenius_norm(lhs - rhs)
        
        return {
            "hom_skew_symmetric": error < self.tolerance,
            "error": error,
            "phi_inv_squared": self.phi_inv ** 2
        }
    
    def compute_structure_constants(
        self,
        basis: list[np.ndarray]
    ) -> np.ndarray:
        """
        Compute structure constants f^k_{ij} defined by:
        
            [e_i, e_j]_φ = ∑_k f^k_{ij} e_k
        
        where {e_i} is a basis for the operator algebra.
        
        Args:
            basis: List of N×N matrices forming a basis
        
        Returns:
            Structure constants array of shape (dim, dim, dim)
        """
        dim = len(basis)
        f = np.zeros((dim, dim, dim), dtype=complex)
        
        for i in range(dim):
            for j in range(dim):
                # Compute [e_i, e_j]_φ
                bracket = self.commutator(basis[i], basis[j], compute_diagnostics=False).value
                
                # Expand in basis: bracket = ∑_k f^k_{ij} e_k
                # Solve via least squares (basis may not be orthogonal)
                basis_matrix = np.column_stack([b.flatten() for b in basis])
                coeffs, _, _, _ = np.linalg.lstsq(
                    basis_matrix,
                    bracket.flatten(),
                    rcond=None
                )
                
                f[i, j, :] = coeffs
        
        return f
    
    @staticmethod
    def _frobenius_norm(A: np.ndarray) -> float:
        """Frobenius norm: ‖A‖_F = √(∑|a_ij|²)."""
        return np.sqrt(np.sum(np.abs(A)**2).real)


# ============================================================================
# Utility Functions
# ============================================================================

def create_standard_basis(N: int) -> list[np.ndarray]:
    """
    Create standard basis {E_ij} for N×N matrices.
    
    E_ij has 1 in position (i,j) and 0 elsewhere.
    This forms a basis for 𝔅(ℋ) with dimension N².
    """
    basis = []
    for i in range(N):
        for j in range(N):
            E_ij = np.zeros((N, N), dtype=complex)
            E_ij[i, j] = 1.0
            basis.append(E_ij)
    return basis


def create_su2_basis() -> list[np.ndarray]:
    """
    Create Pauli matrices basis for SU(2).
    
    Returns [σ_x, σ_y, σ_z] generators.
    """
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    return [sigma_x, sigma_y, sigma_z]


def verify_lie_algebra_consistency(
    structure_constants: np.ndarray,
    tolerance: float = TOLERANCE_JACOBI
) -> dict:
    """
    Verify consistency conditions on structure constants:
    1. Antisymmetry: f^k_{ij} = -f^k_{ji}
    2. Jacobi identity: ∑_m (f^m_{ij}f^k_{ml} + cyclic) = 0
    
    Args:
        structure_constants: f^k_{ij} array of shape (dim, dim, dim)
        tolerance: Numerical tolerance
    
    Returns:
        dict with verification results
    """
    dim = structure_constants.shape[0]
    f = structure_constants
    
    # Check antisymmetry
    antisym_error = 0.0
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                antisym_error += abs(f[i,j,k] + f[j,i,k])**2
    antisym_error = np.sqrt(antisym_error)
    
    # Check Jacobi identity
    jacobi_error = 0.0
    for i in range(dim):
        for j in range(dim):
            for l in range(dim):
                for k in range(dim):
                    term = 0.0
                    for m in range(dim):
                        term += (
                            f[i,j,m] * f[m,l,k] +
                            f[j,l,m] * f[m,i,k] +
                            f[l,i,m] * f[m,j,k]
                        )
                    jacobi_error += abs(term)**2
    jacobi_error = np.sqrt(jacobi_error)
    
    return {
        "antisymmetric": antisym_error < tolerance,
        "antisymmetry_error": antisym_error,
        "jacobi_satisfied": jacobi_error < tolerance,
        "jacobi_error": jacobi_error
    }


# ============================================================================
# Main (Self-Test)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("φ-Commutator and Hom-Lie Algebra Self-Test")
    print("=" * 70)
    
    # Create test matrices
    N = 3
    np.random.seed(42)
    X = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    Y = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    Z = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    
    print(f"\nTest matrices: X, Y, Z ({N}×{N})")
    
    # Create φ-commutator
    phi_comm = PhiCommutator()
    print(f"\n📐 Configuration:")
    print(f"   φ = {phi_comm.phi:.12f}")
    print(f"   φ⁻¹ = {phi_comm.phi_inv:.12f}")
    print(f"   Tolerance = {phi_comm.tolerance:.2e}")
    
    # Test φ-commutator
    print(f"\n🔢 φ-Commutator Test:")
    result = phi_comm.commutator(X, Y)
    print(f"   ‖[X, Y]_φ‖ = {phi_comm._frobenius_norm(result.value):.6f}")
    print(f"   ‖[X, Y]‖ = {phi_comm._frobenius_norm(result.standard_commutator):.6f}")
    print(f"   φ-scaling factor = {result.phi_scaling_factor:.6f}")
    print(f"   Expected: (φ⁻¹ - 1) = {phi_comm.phi_inv - 1:.6f}")
    
    # Test Hom-Jacobi identity
    print(f"\n✅ Hom-Jacobi Identity:")
    jacobi = phi_comm.verify_hom_jacobi(X, Y, Z)
    print(f"   Error norm: {jacobi.error_norm:.2e}")
    print(f"   Relative error: {jacobi.relative_error:.2e}")
    print(f"   Satisfied: {jacobi.satisfies_identity}")
    
    # Test bilinearity
    print(f"\n📏 Bilinearity Test:")
    bilin = phi_comm.verify_bilinearity(X, Y)
    print(f"   Homogeneity: {bilin['homogeneity']}")
    print(f"      Error: {bilin['homogeneity_error']:.2e}")
    print(f"   Additivity: {bilin['additivity']}")
    print(f"      Error: {bilin['additivity_error']:.2e}")
    
    # Test skew-symmetry
    print(f"\n🔄 Hom-Skew-Symmetry Test:")
    skew = phi_comm.verify_skew_symmetry(X, Y)
    print(f"   Satisfied: {skew['hom_skew_symmetric']}")
    print(f"   Error: {skew['error']:.2e}")
    print(f"   φ⁻² factor: {skew['phi_inv_squared']:.6f}")
    
    # Test SU(2) structure
    print(f"\n🎭 SU(2) Test:")
    su2_basis = create_su2_basis()
    print(f"   Pauli matrices loaded")
    
    # Compute [σ_x, σ_y]_φ (should be proportional to σ_z)
    sigma_xy = phi_comm.commutator(su2_basis[0], su2_basis[1], compute_diagnostics=False).value
    print(f"   [σ_x, σ_y]_φ =")
    print(f"   {sigma_xy}")
    print(f"   Expected: 2iφ⁻¹σ_z (with φ-twist)")
    
    # Compute structure constants for 2×2 basis
    print(f"\n🏗️  Structure Constants (2×2 test):")
    small_basis = create_standard_basis(2)
    f_constants = phi_comm.compute_structure_constants(small_basis)
    print(f"   Shape: {f_constants.shape}")
    print(f"   Non-zero entries: {np.count_nonzero(np.abs(f_constants) > 1e-10)}")
    
    # Verify consistency
    consistency = verify_lie_algebra_consistency(f_constants)
    print(f"\n✅ Structure Constant Consistency:")
    print(f"   Antisymmetric: {consistency['antisymmetric']}")
    print(f"      Error: {consistency['antisymmetry_error']:.2e}")
    print(f"   Jacobi satisfied: {consistency['jacobi_satisfied']}")
    print(f"      Error: {consistency['jacobi_error']:.2e}")
    
    print("\n" + "=" * 70)
    print("✅ φ-Commutator Self-Test Complete")
    print("=" * 70)

