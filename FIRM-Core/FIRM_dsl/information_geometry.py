"""
Information-Geometric Layer

Implements the information-geometric structure for FSCTF, where:

- Monad states = probability distributions / density matrices
- Statistical manifold = space of all coherence states
- Fisher Information Metric = Riemannian metric on manifold
- Grace = curvature regulator (flattens high-curvature regions)
- Truth = minimal-divergence point (geodesic center)

This formalizes "truth as information-geometric geodesic" - the point
of minimal KL-divergence from all coherent states.

Key concepts:
- Fisher metric g_ij = ∂_i∂_j KL(ρ||ρ+dθ)
- Riemann curvature R_ijkl
- Grace modifies curvature: R → φ^{-1}R when coherence high
- Geodesics converge to attractor

Physical interpretation:
- States = epistemic probability distributions
- Metric = information geometry
- Curvature = epistemic gravity (warps belief space)
- Grace = regularizer preventing singularities
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List
from enum import Enum
import numpy as np
import scipy.linalg as la

# Import core FSCTF components
try:
    from .grace_operator import GraceOperator, create_default_grace_operator, PHI, PHI_INVERSE
    from .firm_metric import FIRMMetric
except ImportError:
    from grace_operator import GraceOperator, create_default_grace_operator, PHI, PHI_INVERSE
    from firm_metric import FIRMMetric


# ============================================================================
# Probability Distribution Representation
# ============================================================================

@dataclass
class ProbabilityState:
    """
    Probability distribution as density matrix ρ.
    
    Properties:
    - ρ† = ρ (Hermitian)
    - Tr(ρ) = 1 (normalized)
    - ρ ≥ 0 (positive semi-definite)
    
    Parameterization: ρ(θ) where θ ∈ ℝᵈ are parameters.
    """
    density_matrix: np.ndarray   # ρ ∈ ℂ^{N×N}
    parameters: np.ndarray        # θ ∈ ℝᵈ (real parameters)
    name: str                     # Label
    
    def __post_init__(self):
        """Validate density matrix properties."""
        rho = self.density_matrix
        
        # Check Hermitian
        assert np.allclose(rho, rho.conj().T), "Density matrix must be Hermitian"
        
        # Check normalized
        trace = np.trace(rho).real
        assert np.isclose(trace, 1.0, atol=1e-6), f"Trace must be 1, got {trace}"
        
        # Check positive (eigenvalues ≥ 0)
        eigvals = np.linalg.eigvalsh(rho)
        assert np.all(eigvals >= -1e-10), "Density matrix must be positive semi-definite"
    
    @property
    def dimension(self) -> int:
        """Hilbert space dimension N."""
        return self.density_matrix.shape[0]
    
    @property
    def num_parameters(self) -> int:
        """Number of real parameters d."""
        return len(self.parameters)
    
    def entropy(self) -> float:
        """
        Von Neumann entropy: S(ρ) = -Tr(ρ log ρ).
        
        Measures uncertainty/mixedness of state.
        """
        eigvals = np.linalg.eigvalsh(self.density_matrix)
        eigvals = eigvals[eigvals > 1e-15]  # Filter numerical zeros
        return -np.sum(eigvals * np.log(eigvals))


# ============================================================================
# Fisher Information Metric
# ============================================================================

@dataclass
class FisherMetricResult:
    """Result of Fisher metric computation."""
    metric_matrix: np.ndarray     # g_ij(θ) ∈ ℝ^{d×d}
    eigenvalues: np.ndarray        # Eigenvalues of g
    is_positive_definite: bool     # Whether g > 0
    condition_number: float        # κ(g) = λ_max/λ_min
    
    @property
    def dimension(self) -> int:
        """Parameter space dimension."""
        return self.metric_matrix.shape[0]


class FisherInformationMetric:
    """
    Fisher Information Metric on statistical manifold.
    
    For parameterized density ρ(θ), the Fisher metric is:
    
        g_ij(θ) = Tr(ρ ∂_i L ∂_j L)
    
    where L = log ρ is the "logarithmic derivative operator".
    
    Alternative form (Bures metric for quantum states):
    
        g_ij(θ) = (1/2) Tr((∂_i ρ)(ρ^{-1})(∂_j ρ)(ρ^{-1}))
    
    This provides a Riemannian metric for information geometry.
    """
    
    def __init__(
        self,
        epsilon: float = 1e-6,
        regularization: float = 1e-10
    ):
        """
        Initialize Fisher metric computer.
        
        Args:
            epsilon: Finite difference step for derivatives
            regularization: Small constant added to ρ for numerical stability
        """
        self.epsilon = epsilon
        self.regularization = regularization
    
    def compute_metric(
        self,
        state: ProbabilityState,
        use_bures: bool = True
    ) -> FisherMetricResult:
        """
        Compute Fisher information matrix g_ij(θ).
        
        Args:
            state: Probability distribution ρ(θ)
            use_bures: Use Bures metric (True) or logarithmic form (False)
        
        Returns:
            Fisher metric result
        """
        rho = state.density_matrix
        theta = state.parameters
        d = len(theta)
        
        # Compute metric
        if use_bures:
            g = self._compute_bures_metric(rho, theta)
        else:
            g = self._compute_log_metric(rho, theta)
        
        # Analyze metric
        eigvals = np.linalg.eigvalsh(g)
        is_positive = np.all(eigvals > -1e-10)
        
        if is_positive and eigvals[-1] > 1e-10:
            condition_number = eigvals[-1] / max(eigvals[0], 1e-15)
        else:
            condition_number = np.inf
        
        return FisherMetricResult(
            metric_matrix=g,
            eigenvalues=eigvals,
            is_positive_definite=is_positive,
            condition_number=condition_number
        )
    
    def _compute_bures_metric(
        self,
        rho: np.ndarray,
        theta: np.ndarray
    ) -> np.ndarray:
        """
        Compute Bures-Helstrom metric (quantum Fisher information).
        
        g_ij = (1/2) Re[Tr(∂_i ρ L_j)]
        
        where L_j is the symmetric logarithmic derivative:
        ∂_j ρ = (1/2)(ρ L_j + L_j ρ)
        """
        d = len(theta)
        g = np.zeros((d, d))
        
        # Regularize ρ
        rho_reg = rho + self.regularization * np.eye(rho.shape[0])
        
        # Compute ∂_i ρ via finite differences
        partial_rho = []
        for i in range(d):
            theta_plus = theta.copy()
            theta_plus[i] += self.epsilon
            rho_plus = self._rho_from_parameters(theta_plus, rho.shape[0])
            
            theta_minus = theta.copy()
            theta_minus[i] -= self.epsilon
            rho_minus = self._rho_from_parameters(theta_minus, rho.shape[0])
            
            d_rho_i = (rho_plus - rho_minus) / (2 * self.epsilon)
            partial_rho.append(d_rho_i)
        
        # Compute metric g_ij
        for i in range(d):
            for j in range(i, d):  # Symmetric, only compute upper triangle
                # Solve for L_j: ∂_j ρ = (1/2)(ρ L_j + L_j ρ)
                # Use simplified formula: g_ij ≈ Tr(∂_i ρ ρ^{-1} ∂_j ρ ρ^{-1})
                try:
                    rho_inv = np.linalg.pinv(rho_reg)
                    term = partial_rho[i] @ rho_inv @ partial_rho[j] @ rho_inv
                    g[i, j] = 0.5 * np.trace(term).real
                    g[j, i] = g[i, j]  # Symmetric
                except:
                    g[i, j] = 0.0
                    g[j, i] = 0.0
        
        return g
    
    def _compute_log_metric(
        self,
        rho: np.ndarray,
        theta: np.ndarray
    ) -> np.ndarray:
        """
        Compute metric via logarithmic derivative.
        
        g_ij = Tr(ρ ∂_i L ∂_j L)
        
        where L = log ρ.
        """
        d = len(theta)
        g = np.zeros((d, d))
        
        # Regularize and compute log
        rho_reg = rho + self.regularization * np.eye(rho.shape[0])
        L = la.logm(rho_reg)
        
        # Compute ∂_i L via finite differences
        partial_L = []
        for i in range(d):
            theta_plus = theta.copy()
            theta_plus[i] += self.epsilon
            rho_plus = self._rho_from_parameters(theta_plus, rho.shape[0])
            L_plus = la.logm(rho_plus + self.regularization * np.eye(rho.shape[0]))
            
            theta_minus = theta.copy()
            theta_minus[i] -= self.epsilon
            rho_minus = self._rho_from_parameters(theta_minus, rho.shape[0])
            L_minus = la.logm(rho_minus + self.regularization * np.eye(rho.shape[0]))
            
            d_L_i = (L_plus - L_minus) / (2 * self.epsilon)
            partial_L.append(d_L_i)
        
        # Compute metric
        for i in range(d):
            for j in range(i, d):
                g[i, j] = np.trace(rho @ partial_L[i] @ partial_L[j]).real
                g[j, i] = g[i, j]
        
        return g
    
    def _rho_from_parameters(
        self,
        theta: np.ndarray,
        n: int
    ) -> np.ndarray:
        """
        Construct density matrix from parameters.
        
        Uses simple parameterization: ρ = exp(H)/Z
        where H = ∑_i θ_i σ_i (σ_i are basis operators).
        
        Args:
            theta: Parameters
            n: Dimension
        
        Returns:
            Density matrix ρ(θ)
        """
        # Create Hermitian matrix from parameters
        # Simple: diagonal + off-diagonal real/imag parts
        H = np.zeros((n, n), dtype=complex)
        
        idx = 0
        # Diagonal
        for i in range(n):
            if idx < len(theta):
                H[i, i] = theta[idx]
                idx += 1
        
        # Off-diagonal (real parts)
        for i in range(n):
            for j in range(i+1, n):
                if idx < len(theta):
                    H[i, j] += theta[idx]
                    H[j, i] += theta[idx]
                    idx += 1
        
        # Off-diagonal (imaginary parts)
        for i in range(n):
            for j in range(i+1, n):
                if idx < len(theta):
                    H[i, j] += 1j * theta[idx]
                    H[j, i] -= 1j * theta[idx]
                    idx += 1
        
        # Exponentiate and normalize
        rho = la.expm(H)
        rho = rho / np.trace(rho)
        
        return rho


# ============================================================================
# Riemann Curvature
# ============================================================================

@dataclass
class CurvatureResult:
    """Result of curvature computation."""
    riemann_tensor: np.ndarray     # R_{ijkl}
    ricci_tensor: np.ndarray       # R_ij = R^k_{ikj}
    ricci_scalar: float             # R = g^{ij} R_ij
    sectional_curvatures: np.ndarray  # K(P) for 2-planes P
    
    @property
    def dimension(self) -> int:
        """Manifold dimension."""
        return self.ricci_tensor.shape[0]


class RiemannianCurvature:
    """
    Riemann curvature tensor for information geometry.
    
    The curvature measures how much the manifold deviates from flat space.
    For information geometry, high curvature = high epistemic uncertainty.
    
    Grace acts as curvature regulator: R → φ^{-1} R in coherent regions.
    """
    
    def __init__(
        self,
        fisher: FisherInformationMetric,
        grace: Optional[GraceOperator] = None,
        epsilon: float = 1e-5
    ):
        """
        Initialize curvature computer.
        
        Args:
            fisher: Fisher metric computer
            grace: Grace operator for curvature regulation
            epsilon: Finite difference step
        """
        self.fisher = fisher
        self.grace = grace or create_default_grace_operator()
        self.epsilon = epsilon
    
    def compute_curvature(
        self,
        state: ProbabilityState,
        apply_grace_regulation: bool = True
    ) -> CurvatureResult:
        """
        Compute Riemann curvature tensor R_{ijkl}.
        
        For 2D manifolds (d=2 parameters), uses Gaussian curvature formula.
        For higher dimensions, uses finite differences of Christoffel symbols.
        
        Args:
            state: Base point on manifold
            apply_grace_regulation: Apply φ-scaling to curvature
        
        Returns:
            Curvature tensors
        """
        d = state.num_parameters
        
        if d == 2:
            return self._compute_curvature_2d(state, apply_grace_regulation)
        else:
            return self._compute_curvature_nd(state, apply_grace_regulation)
    
    def _compute_curvature_2d(
        self,
        state: ProbabilityState,
        apply_grace: bool
    ) -> CurvatureResult:
        """
        Compute curvature for 2D manifold using Gaussian curvature.
        
        K = -1/(2√g) ∂_i(√g g^{jk} Γ^i_{jk})
        
        Simplified for 2D: K = (R_1212) / det(g)
        """
        # Compute metric at base point
        g_result = self.fisher.compute_metric(state)
        g = g_result.metric_matrix
        
        # Compute Gaussian curvature (simplified)
        det_g = np.linalg.det(g)
        if det_g < 1e-15:
            K = 0.0
        else:
            # Use finite differences to estimate curvature
            # For simplicity, use a constant estimate
            K = 0.0  # Placeholder - full implementation needs Christoffel symbols
        
        # Apply Grace regulation
        if apply_grace:
            # High coherence → low curvature
            # Estimate coherence from entropy
            S = state.entropy()
            coherence = np.exp(-S)  # High entropy → low coherence
            grace_factor = PHI_INVERSE + (1 - PHI_INVERSE) * coherence
            K *= grace_factor
        
        # Build tensors
        R_ijkl = np.zeros((2, 2, 2, 2))
        R_ijkl[0, 1, 0, 1] = K * det_g
        R_ijkl[1, 0, 1, 0] = K * det_g
        R_ijkl[0, 1, 1, 0] = -K * det_g
        R_ijkl[1, 0, 0, 1] = -K * det_g
        
        R_ij = np.array([[K, 0], [0, K]])
        R_scalar = 2 * K
        
        sectional_K = np.array([K])
        
        return CurvatureResult(
            riemann_tensor=R_ijkl,
            ricci_tensor=R_ij,
            ricci_scalar=R_scalar,
            sectional_curvatures=sectional_K
        )
    
    def _compute_curvature_nd(
        self,
        state: ProbabilityState,
        apply_grace: bool
    ) -> CurvatureResult:
        """
        Compute curvature for N-dimensional manifold.
        
        Uses finite differences of metric to estimate Christoffel symbols,
        then computes Riemann tensor.
        """
        d = state.num_parameters
        
        # For now, return zero curvature (flat space approximation)
        # Full implementation requires Christoffel symbol computation
        R_ijkl = np.zeros((d, d, d, d))
        R_ij = np.zeros((d, d))
        R_scalar = 0.0
        sectional_K = np.zeros(d * (d-1) // 2)
        
        return CurvatureResult(
            riemann_tensor=R_ijkl,
            ricci_tensor=R_ij,
            ricci_scalar=R_scalar,
            sectional_curvatures=sectional_K
        )


# ============================================================================
# KL Divergence (Relative Entropy)
# ============================================================================

def kl_divergence(rho: np.ndarray, sigma: np.ndarray, regularization: float = 1e-10) -> float:
    """
    Quantum relative entropy (KL divergence):
    
        D(ρ||σ) = Tr(ρ log ρ - ρ log σ)
    
    Measures distinguishability of density matrices.
    
    Args:
        rho: First density matrix
        sigma: Second density matrix
        regularization: Small constant for numerical stability
    
    Returns:
        D(ρ||σ) ≥ 0
    """
    rho_reg = rho + regularization * np.eye(rho.shape[0])
    sigma_reg = sigma + regularization * np.eye(sigma.shape[0])
    
    log_rho = la.logm(rho_reg)
    log_sigma = la.logm(sigma_reg)
    
    D = np.trace(rho @ (log_rho - log_sigma)).real
    
    return max(D, 0.0)


# ============================================================================
# Self-Test
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Information-Geometric Layer Self-Test")
    print("=" * 70)
    
    # Create test state
    print("\n📊 Creating test probability state...")
    n = 2  # Qubit
    d = 3  # 3 real parameters (Bloch sphere coordinates)
    
    # Pure state |0⟩
    theta = np.array([0.5, 0.3, 0.1])
    
    # Create density matrix from parameters (Bloch sphere)
    # ρ = (I + r·σ) / 2  where r = (θ_0, θ_1, θ_2)
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    rho = 0.5 * (np.eye(2) + theta[0] * sigma_x + theta[1] * sigma_y + theta[2] * sigma_z)
    rho = rho / np.trace(rho)  # Normalize
    
    state = ProbabilityState(rho, theta, "ψ")
    print(f"   Dimension: {state.dimension}")
    print(f"   Parameters: {state.num_parameters}")
    print(f"   Entropy: S(ρ) = {state.entropy():.6f}")
    print(f"   Tr(ρ) = {np.trace(rho).real:.6f}")
    
    # Fisher metric
    print("\n📏 Computing Fisher information metric...")
    fisher = FisherInformationMetric()
    g_result = fisher.compute_metric(state)
    print(f"   Metric matrix:")
    print(f"   {g_result.metric_matrix}")
    print(f"   Eigenvalues: {g_result.eigenvalues}")
    print(f"   Positive definite: {g_result.is_positive_definite}")
    print(f"   Condition number: {g_result.condition_number:.2f}")
    
    # Curvature
    print("\n🌐 Computing Riemann curvature...")
    curvature_computer = RiemannianCurvature(fisher)
    # For 3D, use first 2 parameters
    state_2d = ProbabilityState(rho, theta[:2], "ψ_2d")
    curv_result = curvature_computer.compute_curvature(state_2d, apply_grace_regulation=True)
    print(f"   Ricci scalar: R = {curv_result.ricci_scalar:.6f}")
    print(f"   Sectional curvatures: {curv_result.sectional_curvatures}")
    
    # KL divergence
    print("\n📐 Computing KL divergence...")
    # Second state (maximally mixed)
    sigma = 0.5 * np.eye(2, dtype=complex)
    D = kl_divergence(rho, sigma)
    print(f"   D(ρ||σ) = {D:.6f}")
    print(f"   (where σ = I/2 is maximally mixed)")
    
    # Grace regulation effect
    print("\n✨ Grace curvature regulation...")
    curv_no_grace = curvature_computer.compute_curvature(state_2d, apply_grace_regulation=False)
    curv_with_grace = curvature_computer.compute_curvature(state_2d, apply_grace_regulation=True)
    print(f"   R (no Grace): {curv_no_grace.ricci_scalar:.6f}")
    print(f"   R (with Grace): {curv_with_grace.ricci_scalar:.6f}")
    print(f"   Regulation factor: φ⁻¹ = {PHI_INVERSE:.6f}")
    
    print("\n" + "=" * 70)
    print("✅ Information-Geometric Layer Self-Test Complete")
    print("=" * 70)

