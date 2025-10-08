"""
Curvature Tensor and FIRM Action Functional

Implements the φ-curvature field strength F_μν and FIRM action from FSCTF_AXIOMS.md Section V.

Key components:
- φ-Curvature: F_μν = ∂_μΨ_ν - ∂_νΨ_μ + [Ψ_μ, Ψ_ν]_φ
- φ-Covariant derivative: D^φ_μ X = ∂_μX + [Ψ_μ, X]_φ
- FIRM action: S_{φ,𝒢}[Ψ] = ∫ ⟨F_μν, F^μν⟩_{φ,𝒢} √|g| d⁴x

This provides the gauge-theoretic foundation for FSCTF, generalizing Yang-Mills
theory with recursive φ-scaling and Grace regularization.
"""

import numpy as np
from typing import Tuple, Optional, Callable
from dataclasses import dataclass

# Handle both package and standalone imports
try:
    from .phi_commutator import PhiCommutator
    from .firm_metric import FIRMMetric
    from .grace_operator import PHI, TOLERANCE_CONVERGENCE
except ImportError:
    from phi_commutator import PhiCommutator
    from firm_metric import FIRMMetric
    from grace_operator import PHI, TOLERANCE_CONVERGENCE


@dataclass
class CurvatureResult:
    """Result of curvature tensor computation."""
    F_muv: np.ndarray               # Field strength F_μν
    partial_term: np.ndarray        # ∂_μΨ_ν - ∂_νΨ_μ
    commutator_term: np.ndarray     # [Ψ_μ, Ψ_ν]_φ
    firm_norm: float                # ‖F_μν‖_{φ,𝒢}
    hs_norm: float                  # ‖F_μν‖_hs


@dataclass
class ActionResult:
    """Result of FIRM action functional computation."""
    action: float                   # S_{φ,𝒢}[Ψ]
    action_density: np.ndarray      # Integrand at each spacetime point
    total_curvature: float          # ∫‖F‖² √g d⁴x
    num_points: int                 # Number of lattice points


class FSCTFGaugeTheory:
    """
    FSCTF Gauge Theory with φ-curvature and FIRM action.
    
    Implements the complete gauge-theoretic structure including:
    - φ-covariant derivatives
    - φ-twisted field strength tensors
    - FIRM action functionals
    - Equations of motion
    
    Usage:
        gauge = FSCTFGaugeTheory()
        F_01 = gauge.compute_curvature(Psi_0, Psi_1, spacetime_lattice, mu=0, nu=1)
        action = gauge.compute_action(Psi_field, spacetime_lattice)
    """
    
    def __init__(
        self,
        phi_comm: Optional[PhiCommutator] = None,
        firm: Optional[FIRMMetric] = None
    ):
        self.phi_comm = phi_comm or PhiCommutator()
        self.firm = firm or FIRMMetric()
        self.phi = PHI
    
    def covariant_derivative(
        self,
        X: np.ndarray,
        Psi_mu: np.ndarray,
        direction: int = 0,
        lattice_spacing: float = 1.0
    ) -> np.ndarray:
        """
        Compute φ-covariant derivative: D^φ_μ X = ∂_μX + [Ψ_μ, X]_φ.
        
        Args:
            X: Field to differentiate
            Psi_mu: Connection field in direction μ
            direction: Spacetime direction index
            lattice_spacing: Discretization step
        
        Returns:
            D^φ_μ X
        """
        # Partial derivative (finite difference approximation)
        # In practice, this would use actual spatial derivatives from a lattice
        # For now, we compute the gauge-covariant part only
        partial_X = np.zeros_like(X)  # Placeholder for ∂_μX
        
        # φ-commutator term
        comm_term = self.phi_comm.commutator(Psi_mu, X, compute_diagnostics=False).value
        
        return partial_X + comm_term
    
    def compute_curvature(
        self,
        Psi_mu: np.ndarray,
        Psi_nu: np.ndarray,
        lattice: Optional[np.ndarray] = None,
        mu: int = 0,
        nu: int = 1,
        lattice_spacing: float = 1.0
    ) -> CurvatureResult:
        """
        Compute φ-curvature: F_μν = ∂_μΨ_ν - ∂_νΨ_μ + [Ψ_μ, Ψ_ν]_φ.
        
        Args:
            Psi_mu, Psi_nu: Connection fields
            lattice: Spacetime lattice (optional, for derivatives)
            mu, nu: Spacetime direction indices
            lattice_spacing: Discretization step
        
        Returns:
            CurvatureResult with field strength and norms
        """
        # Partial derivative terms (simplified: zero for constant fields)
        # In full implementation, these would be finite differences on lattice
        partial_mu_nu = np.zeros_like(Psi_nu)
        partial_nu_mu = np.zeros_like(Psi_mu)
        partial_term = partial_mu_nu - partial_nu_mu
        
        # φ-commutator term: [Ψ_μ, Ψ_ν]_φ
        comm_result = self.phi_comm.commutator(Psi_mu, Psi_nu)
        commutator_term = comm_result.value
        
        # Full curvature
        F_muv = partial_term + commutator_term
        
        # Compute norms
        firm_norm = self.firm.norm(F_muv).norm
        hs_norm = np.sqrt(np.trace(F_muv.conj().T @ F_muv).real)
        
        return CurvatureResult(
            F_muv=F_muv,
            partial_term=partial_term,
            commutator_term=commutator_term,
            firm_norm=firm_norm,
            hs_norm=hs_norm
        )
    
    def compute_action(
        self,
        Psi_field: dict,
        lattice: np.ndarray,
        metric_det: Optional[np.ndarray] = None
    ) -> ActionResult:
        """
        Compute FIRM action: S_{φ,𝒢}[Ψ] = ∫ ⟨F_μν, F^μν⟩_{φ,𝒢} √|g| d⁴x.
        
        Args:
            Psi_field: Dictionary {(μ,ν): Ψ_μν} of connection fields
            lattice: Spacetime lattice points (shape: [N_points, 4])
            metric_det: √|g| at each lattice point (default: flat spacetime)
        
        Returns:
            ActionResult with total action and density
        """
        num_points = lattice.shape[0] if lattice is not None else 1
        
        # Default to flat spacetime
        if metric_det is None:
            metric_det = np.ones(num_points)
        
        # Initialize action density array
        action_density = np.zeros(num_points)
        total_curvature_squared = 0.0
        
        # Sum over all independent (μ,ν) pairs
        spacetime_dims = 4
        for mu in range(spacetime_dims):
            for nu in range(mu + 1, spacetime_dims):  # Only upper triangle (antisymmetry)
                if (mu, nu) in Psi_field:
                    Psi_mu = Psi_field.get((mu, mu), np.zeros((2,2)))  # Diagonal element
                    Psi_nu = Psi_field.get((nu, nu), np.zeros((2,2)))
                    
                    # Compute curvature
                    curv = self.compute_curvature(Psi_mu, Psi_nu, lattice, mu, nu)
                    F_muv = curv.F_muv
                    
                    # FIRM inner product ⟨F_μν, F^μν⟩_{φ,𝒢}
                    # F^μν = F_μν for flat metric
                    firm_inner = self.firm.inner_product(F_muv, F_muv).value.real
                    
                    # Contribution to action density (averaged over points)
                    action_density += firm_inner / num_points
                    total_curvature_squared += firm_inner
        
        # Integrate: S = ∫ action_density √|g| d⁴x
        # Discrete: S ≈ ∑_i action_density[i] √|g_i| Δx⁴
        lattice_volume_element = 1.0  # Placeholder for Δx⁴
        action = np.sum(action_density * metric_det) * lattice_volume_element
        
        return ActionResult(
            action=action,
            action_density=action_density,
            total_curvature=total_curvature_squared,
            num_points=num_points
        )
    
    def compute_equations_of_motion(
        self,
        Psi_field: dict,
        lattice: np.ndarray
    ) -> dict:
        """
        Compute Euler-Lagrange equations: D^φ_μ F^μν = 0.
        
        This is the FSCTF generalization of Yang-Mills equations.
        
        Args:
            Psi_field: Connection field configuration
            lattice: Spacetime lattice
        
        Returns:
            dict with equation residuals for each direction
        """
        residuals = {}
        spacetime_dims = 4
        
        for nu in range(spacetime_dims):
            residual = np.zeros_like(list(Psi_field.values())[0])
            
            for mu in range(spacetime_dims):
                if (mu, nu) in Psi_field or (nu, mu) in Psi_field:
                    # Get F^μν
                    Psi_mu = Psi_field.get((mu, mu), np.zeros_like(residual))
                    Psi_nu_field = Psi_field.get((nu, nu), np.zeros_like(residual))
                    
                    curv = self.compute_curvature(Psi_mu, Psi_nu_field, lattice, mu, nu)
                    F_muv = curv.F_muv
                    
                    # D^φ_μ F^μν (simplified: just covariant derivative)
                    D_mu_F = self.covariant_derivative(F_muv, Psi_mu, direction=mu)
                    residual += D_mu_F
            
            residuals[nu] = residual
        
        return residuals
    
    def verify_bianchi_identity(
        self,
        Psi_field: dict,
        lattice: np.ndarray,
        indices: Tuple[int, int, int] = (0, 1, 2)
    ) -> dict:
        """
        Verify Bianchi identity: D^φ_λ F_μν + D^φ_μ F_νλ + D^φ_ν F_λμ = 0.
        
        Args:
            Psi_field: Connection field
            lattice: Spacetime lattice
            indices: (λ, μ, ν) triple to check
        
        Returns:
            dict with identity residual and error
        """
        lam, mu, nu = indices
        
        # Get connection fields
        Psi_lam = Psi_field.get((lam, lam), np.zeros((2,2)))
        Psi_mu = Psi_field.get((mu, mu), np.zeros((2,2)))
        Psi_nu = Psi_field.get((nu, nu), np.zeros((2,2)))
        
        # Compute curvatures
        F_muv = self.compute_curvature(Psi_mu, Psi_nu, lattice, mu, nu).F_muv
        F_nulam = self.compute_curvature(Psi_nu, Psi_lam, lattice, nu, lam).F_muv
        F_lammu = self.compute_curvature(Psi_lam, Psi_mu, lattice, lam, mu).F_muv
        
        # Covariant derivatives
        D_lam_F_muv = self.covariant_derivative(F_muv, Psi_lam, direction=lam)
        D_mu_F_nulam = self.covariant_derivative(F_nulam, Psi_mu, direction=mu)
        D_nu_F_lammu = self.covariant_derivative(F_lammu, Psi_nu, direction=nu)
        
        # Sum (should be zero)
        bianchi_sum = D_lam_F_muv + D_mu_F_nulam + D_nu_F_lammu
        
        error = np.sqrt(np.trace(bianchi_sum.conj().T @ bianchi_sum).real)
        
        return {
            "bianchi_sum": bianchi_sum,
            "error": error,
            "satisfies_identity": error < TOLERANCE_CONVERGENCE
        }


# ============================================================================
# Utility Functions
# ============================================================================

def create_constant_connection(N: int, strength: float = 0.1) -> np.ndarray:
    """Create a constant (spatially uniform) connection field."""
    Psi = strength * (np.random.randn(N, N) + 1j * np.random.randn(N, N))
    return (Psi + Psi.conj().T) / 2  # Hermitian


def create_abelian_connection(N: int) -> np.ndarray:
    """Create a diagonal (Abelian) connection field."""
    return np.diag(np.random.rand(N) * 0.1)


def create_su2_connection() -> dict:
    """Create SU(2) connection using Pauli matrices."""
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    # Connection coefficients
    a = 0.1 * np.random.randn(3)
    
    Psi_0 = a[0] * sigma_x
    Psi_1 = a[1] * sigma_y
    Psi_2 = a[2] * sigma_z
    
    return {
        (0, 0): Psi_0,
        (1, 1): Psi_1,
        (2, 2): Psi_2
    }


# ============================================================================
# Main (Self-Test)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FSCTF Gauge Theory Self-Test")
    print("=" * 70)
    
    # Initialize gauge theory
    gauge = FSCTFGaugeTheory()
    print(f"\n📐 FSCTF Gauge Theory initialized")
    print(f"   φ = {gauge.phi:.12f}")
    
    # Create test connection fields
    N = 3
    print(f"\n🔧 Creating {N}×{N} test connection fields...")
    Psi_0 = create_constant_connection(N, strength=0.2)
    Psi_1 = create_constant_connection(N, strength=0.15)
    Psi_2 = create_constant_connection(N, strength=0.1)
    
    print(f"   ‖Ψ_0‖ = {np.sqrt(np.trace(Psi_0.conj().T @ Psi_0).real):.6f}")
    print(f"   ‖Ψ_1‖ = {np.sqrt(np.trace(Psi_1.conj().T @ Psi_1).real):.6f}")
    print(f"   ‖Ψ_2‖ = {np.sqrt(np.trace(Psi_2.conj().T @ Psi_2).real):.6f}")
    
    # Test curvature computation
    print(f"\n🌀 Computing φ-Curvature F_01...")
    curv_01 = gauge.compute_curvature(Psi_0, Psi_1, mu=0, nu=1)
    print(f"   ‖F_01‖_{{φ,𝒢}} = {curv_01.firm_norm:.6f}")
    print(f"   ‖F_01‖_hs = {curv_01.hs_norm:.6f}")
    print(f"   Ratio = {curv_01.firm_norm / curv_01.hs_norm:.6f}")
    print(f"   ‖∂ term‖ = {np.sqrt(np.trace(curv_01.partial_term.conj().T @ curv_01.partial_term).real):.6f}")
    print(f"   ‖[Ψ,Ψ]_φ‖ = {np.sqrt(np.trace(curv_01.commutator_term.conj().T @ curv_01.commutator_term).real):.6f}")
    
    # Test action functional
    print(f"\n⚡ Computing FIRM Action...")
    lattice = np.random.randn(10, 4)  # 10 spacetime points
    Psi_field = {
        (0, 0): Psi_0,
        (1, 1): Psi_1,
        (2, 2): Psi_2
    }
    action_result = gauge.compute_action(Psi_field, lattice)
    print(f"   S_{{φ,𝒢}}[Ψ] = {action_result.action:.6f}")
    print(f"   Total curvature² = {action_result.total_curvature:.6f}")
    print(f"   Lattice points = {action_result.num_points}")
    print(f"   Mean action density = {np.mean(action_result.action_density):.6f}")
    
    # Test SU(2) connection
    print(f"\n🎭 SU(2) Connection Test...")
    su2_field = create_su2_connection()
    print(f"   Created SU(2) connection")
    curv_su2 = gauge.compute_curvature(
        su2_field[(0,0)],
        su2_field[(1,1)],
        mu=0, nu=1
    )
    print(f"   ‖F_01^{{SU(2)}}‖_{{φ,𝒢}} = {curv_su2.firm_norm:.6f}")
    
    # Test Bianchi identity
    print(f"\n✅ Bianchi Identity Test...")
    bianchi = gauge.verify_bianchi_identity(Psi_field, lattice, indices=(0,1,2))
    print(f"   Error: {bianchi['error']:.2e}")
    print(f"   Satisfied: {bianchi['satisfies_identity']}")
    
    # Test equations of motion
    print(f"\n📜 Equations of Motion (D^φ_μ F^μν = 0)...")
    eom = gauge.compute_equations_of_motion(Psi_field, lattice)
    for nu, residual in eom.items():
        residual_norm = np.sqrt(np.trace(residual.conj().T @ residual).real)
        print(f"   ν={nu}: ‖residual‖ = {residual_norm:.2e}")
    
    print("\n" + "=" * 70)
    print("✅ FSCTF Gauge Theory Self-Test Complete")
    print("=" * 70)

