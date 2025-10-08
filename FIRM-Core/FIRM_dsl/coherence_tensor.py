"""
Coherence Tensor: Structure Tensor for TFCA Field Theory with Grace Retrocausality

This module implements the coherence tensor C_ijk that governs how geometric 
(Love–Grace), logical (Scale–Phase), and vibrational (Real–Imaginary) coherence couple.

The tensor decomposes into three independent planes:
1. Love-Grace (LG): λ - Antisymmetric rotation (preserves coherence)
2. Scale-Phase (SP): β - Symmetric dilation (drives adaptation)
3. Real-Imaginary (RI): ω - Antisymmetric oscillation (vibrational persistence)

Mathematical Foundation:
    C = λ B₁₂ + β B₀₃ + ω B₁₃
    
    Where B_ij are Clifford bivectors in signature (3,1).
    
    Invariant: I = λ² + β² + ω²

Grace Retrocausality Extension:
    𝒢(x,t) = ∫ K_adv(t,t') A∞(x',t') d³x' dt'  where t' > t
    
    Where:
    - K_adv: Advanced Green's function (future → past coupling)
    - A∞: Future attractor field configuration
    - α_adv: Retrocausal coupling strength
    
Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.1.0 (Grace Retrocausality added)
"""

import numpy as np
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

# Optional: Import existing Clifford algebra if available
try:
    from clifford_rotors import CliffordAlgebra, CliffordRotor
    CLIFFORD_AVAILABLE = True
except ImportError:
    CLIFFORD_AVAILABLE = False


class CoherencePlane(Enum):
    """Three fundamental planes of the coherence tensor."""
    LOVE_GRACE = "LG"      # λ - Rotational coherence (antisymmetric)
    SCALE_PHASE = "SP"     # β - Adaptive dilation (symmetric)
    REAL_IMAGINARY = "RI"  # ω - Vibrational persistence (antisymmetric)


@dataclass
class CoherenceParameters:
    """Parameters for the three coherence planes."""
    lambda_lg: float  # Love-Grace coefficient (rotation)
    beta_sp: float    # Scale-Phase coefficient (dilation)
    omega_ri: float   # Real-Imaginary coefficient (oscillation)
    
    def __post_init__(self):
        """Validate parameters."""
        # All parameters should be real numbers
        if not all(isinstance(x, (int, float)) for x in [self.lambda_lg, self.beta_sp, self.omega_ri]):
            raise ValueError("All coherence parameters must be real numbers")
    
    @property
    def invariant(self) -> float:
        """Compute the scalar invariant I = λ² + β² + ω²."""
        return self.lambda_lg**2 + self.beta_sp**2 + self.omega_ri**2
    
    def normalize(self) -> 'CoherenceParameters':
        """Return normalized parameters with I = 1."""
        norm = np.sqrt(self.invariant)
        if norm < 1e-10:
            raise ValueError("Cannot normalize zero vector")
        return CoherenceParameters(
            lambda_lg=self.lambda_lg / norm,
            beta_sp=self.beta_sp / norm,
            omega_ri=self.omega_ri / norm
        )


@dataclass
class StructureTensor:
    """
    Structure tensor C_ijk with antisymmetric and symmetric decomposition.
    
    C_ijk = S_ijk + A_ijk
    
    Where:
        S_ijk = ½(C_ijk + C_ikj): Symmetric part (information-like flows)
        A_ijk = ½(C_ijk - C_ikj): Antisymmetric part (energy-like rotations)
    """
    antisymmetric: np.ndarray  # A_ijk - rotations
    symmetric: np.ndarray      # S_ijk - flows
    
    def __post_init__(self):
        """Validate tensor shapes."""
        if self.antisymmetric.shape != self.symmetric.shape:
            raise ValueError("Antisymmetric and symmetric parts must have same shape")
        if len(self.antisymmetric.shape) != 3:
            raise ValueError("Structure tensor must be rank-3")
    
    @property
    def full(self) -> np.ndarray:
        """Return full tensor C_ijk = S_ijk + A_ijk."""
        return self.symmetric + self.antisymmetric
    
    def __getitem__(self, indices: Tuple[int, int, int]) -> float:
        """Access tensor component C_ijk."""
        return self.full[indices]


class CoherenceTensor:
    """
    Main class for coherence tensor operations.
    
    Implements the structure tensor C_ijk and provides methods for:
    - Tensor construction from parameters
    - Parametric geometry (helical trajectories)
    - Curvature and torsion calculations
    - Integration with Clifford algebra
    """
    
    def __init__(self, params: CoherenceParameters):
        """
        Initialize coherence tensor with given parameters.
        
        Args:
            params: CoherenceParameters specifying λ, β, ω
        """
        self.params = params
        self._structure_tensor: Optional[StructureTensor] = None
        
        # Initialize Clifford algebra if available
        if CLIFFORD_AVAILABLE:
            self.clifford = CliffordAlgebra(dimension=4, signature=(3, 1))
        else:
            self.clifford = None
    
    def compute_structure_tensor(self, dimension: int = 3) -> StructureTensor:
        """
        Compute the structure tensor C_ijk for given dimension.
        
        Args:
            dimension: Spatial dimension (default 3)
            
        Returns:
            StructureTensor with antisymmetric and symmetric components
        """
        # Initialize tensors
        antisymmetric = np.zeros((dimension, dimension, dimension))
        symmetric = np.zeros((dimension, dimension, dimension))
        
        # Love-Grace plane: antisymmetric rotation in (1,2) plane
        # [R, e₁] = λ e₂, [R, e₂] = -λ e₁
        antisymmetric[0, 0, 1] = self.params.lambda_lg
        antisymmetric[0, 1, 0] = -self.params.lambda_lg
        
        # Scale-Phase plane: symmetric dilation
        # [R, Φ] = β
        symmetric[0, 1, 1] = self.params.beta_sp
        symmetric[0, 1, 1] = self.params.beta_sp
        
        # Real-Imaginary plane: antisymmetric oscillation in (1,3) or time-space
        if dimension >= 3:
            antisymmetric[0, 0, 2] = self.params.omega_ri
            antisymmetric[0, 2, 0] = -self.params.omega_ri
        
        self._structure_tensor = StructureTensor(
            antisymmetric=antisymmetric,
            symmetric=symmetric
        )
        
        return self._structure_tensor
    
    def parametric_trajectory(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute parametric trajectory under rotor evolution.
        
        Evolution equations:
            x(t) = e^(βt) cos(λt) cos(ωt)
            y(t) = e^(βt) sin(λt) cos(ωt)
            z(t) = e^(βt) sin(ωt)
        
        Args:
            t: Time array
            
        Returns:
            Tuple of (x, y, z) trajectory arrays
        """
        λ = self.params.lambda_lg
        β = self.params.beta_sp
        ω = self.params.omega_ri
        
        # Radial scaling
        r = np.exp(β * t)
        
        # Coordinates
        x = r * np.cos(λ * t) * np.cos(ω * t)
        y = r * np.sin(λ * t) * np.cos(ω * t)
        z = r * np.sin(ω * t)
        
        return x, y, z
    
    def differential_invariants(self, t: float) -> Tuple[float, float]:
        """
        Compute curvature κ and torsion τ at time t.
        
        κ = √(λ² + ω²) / e^(βt)  (curvature)
        τ = λω / (λ² + ω²)        (torsion)
        
        Args:
            t: Time point
            
        Returns:
            Tuple of (curvature, torsion)
        """
        λ = self.params.lambda_lg
        β = self.params.beta_sp
        ω = self.params.omega_ri
        
        # Curvature (time-dependent)
        λω_sum_sq = λ**2 + ω**2
        if λω_sum_sq < 1e-10:
            κ = 0.0
        else:
            κ = np.sqrt(λω_sum_sq) / np.exp(β * t)
        
        # Torsion (time-independent ratio)
        if λω_sum_sq < 1e-10:
            τ = 0.0
        else:
            τ = λ * ω / λω_sum_sq
        
        return κ, τ
    
    def classify_geometry(self) -> str:
        """
        Classify the geometric type based on parameters.
        
        Returns:
            String description of geometry type
        """
        λ = abs(self.params.lambda_lg)
        β = abs(self.params.beta_sp)
        ω = abs(self.params.omega_ri)
        
        tol = 1e-6
        
        if β < tol and λ > tol and ω > tol:
            if abs(λ - ω) < tol:
                return "Toroid (stable attractor)"
            else:
                return "Pure helix (constant radius)"
        elif λ < tol and β > tol:
            return "Exponential curve (pure dilation)"
        elif ω < tol and β > tol and λ > tol:
            return "Spiral in plane (rotational scaling)"
        elif β < tol and λ < tol and ω > tol:
            return "Oscillation (vertical only)"
        elif β > tol and λ > tol and ω > tol:
            return "Helical torus (general case)"
        else:
            return "Trivial (near-zero motion)"
    
    def jacobi_closure(self) -> bool:
        """
        Verify Jacobi identity for closure: C_[ij|m C_|k]m^n = 0
        
        This ensures the structure tensor forms a consistent algebra.
        
        Returns:
            True if Jacobi identity holds (within numerical tolerance)
        """
        if self._structure_tensor is None:
            self.compute_structure_tensor()
        
        C = self._structure_tensor.full
        n = C.shape[0]
        
        # Check Jacobi identity for all index combinations
        max_violation = 0.0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    # Compute C_[ij|m C_|k]m^n (antisymmetrized product)
                    jacobi_sum = 0.0
                    for m in range(n):
                        for p in range(n):
                            # Antisymmetrize over [ij...k]
                            jacobi_sum += (
                                C[i, j, m] * C[k, m, p]
                                - C[j, k, m] * C[i, m, p]
                                + C[k, i, m] * C[j, m, p]
                            )
                    max_violation = max(max_violation, abs(jacobi_sum))
        
        # Tolerance for numerical closure
        return bool(max_violation < 1e-6)  # Convert to Python bool
    
    def to_clifford_bivector(self) -> Optional[np.ndarray]:
        """
        Convert coherence parameters to Clifford bivector representation.
        
        C = λ B₁₂ + β B₀₃ + ω B₁₃
        
        Returns:
            Bivector coefficients if Clifford algebra available, else None
        """
        if not CLIFFORD_AVAILABLE:
            return None
        
        # In Cl(3,1), bivectors have 6 components
        # B_μν for μ < ν: (01, 02, 03, 12, 13, 23)
        bivector = np.zeros(6)
        
        # Map our coherence parameters to bivector components
        # Love-Grace (λ): B₁₂ (spatial rotation) → index 3
        bivector[3] = self.params.lambda_lg
        
        # Scale-Phase (β): B₀₃ (time-space) → index 2
        bivector[2] = self.params.beta_sp
        
        # Real-Imaginary (ω): B₁₃ (mixed) → index 4
        bivector[4] = self.params.omega_ri
        
        return bivector
    
    def energy_flow_decomposition(self) -> Dict[str, float]:
        """
        Decompose tensor into energy-like (antisymmetric) and 
        information-like (symmetric) flows.
        
        Returns:
            Dictionary with 'energy_flow' and 'information_flow' magnitudes
        """
        if self._structure_tensor is None:
            self.compute_structure_tensor()
        
        energy_flow = np.linalg.norm(self._structure_tensor.antisymmetric)
        information_flow = np.linalg.norm(self._structure_tensor.symmetric)
        
        return {
            'energy_flow': energy_flow,
            'information_flow': information_flow,
            'total': np.sqrt(energy_flow**2 + information_flow**2),
            'ratio': information_flow / (energy_flow + 1e-10)
        }


def create_love_grace_tensor(lambda_lg: float) -> CoherenceTensor:
    """
    Create a pure Love-Grace coherence tensor (rotation only).
    
    Args:
        lambda_lg: Rotation coefficient
        
    Returns:
        CoherenceTensor with only LG plane active
    """
    params = CoherenceParameters(lambda_lg=lambda_lg, beta_sp=0.0, omega_ri=0.0)
    return CoherenceTensor(params)


def create_scale_phase_tensor(beta_sp: float) -> CoherenceTensor:
    """
    Create a pure Scale-Phase coherence tensor (dilation only).
    
    Args:
        beta_sp: Dilation coefficient
        
    Returns:
        CoherenceTensor with only SP plane active
    """
    params = CoherenceParameters(lambda_lg=0.0, beta_sp=beta_sp, omega_ri=0.0)
    return CoherenceTensor(params)


def create_real_imaginary_tensor(omega_ri: float) -> CoherenceTensor:
    """
    Create a pure Real-Imaginary coherence tensor (oscillation only).
    
    Args:
        omega_ri: Oscillation coefficient
        
    Returns:
        CoherenceTensor with only RI plane active
    """
    params = CoherenceParameters(lambda_lg=0.0, beta_sp=0.0, omega_ri=omega_ri)
    return CoherenceTensor(params)


def golden_ratio_tensor() -> CoherenceTensor:
    """
    Create a coherence tensor with golden ratio relationships.
    
    Uses φ = (1 + √5)/2 ≈ 1.618 and φ⁻¹ ≈ 0.618
    
    Returns:
        CoherenceTensor with golden ratio proportions
    """
    φ = (1 + np.sqrt(5)) / 2  # Golden ratio
    φ_inv = 1 / φ             # Inverse golden ratio
    
    # Set λ = 1, β = φ⁻¹, ω = φ⁻² for harmonic proportions
    params = CoherenceParameters(
        lambda_lg=1.0,
        beta_sp=φ_inv,
        omega_ri=φ_inv**2
    )
    return CoherenceTensor(params)


# ============================================================================
# GRACE RETROCAUSALITY EXTENSION (v1.1.0)
# ============================================================================

@dataclass
class RetrocausalParameters:
    """
    Parameters for Grace retrocausality.
    
    Attributes:
        alpha_adv: Retrocausal coupling strength (0 = no retrocausality)
        tau_future: Time window for future influence (how far ahead A∞ acts)
        mass: Effective mass for Green's function (controls decay rate)
        c: Effective speed (controls propagation rate)
    """
    alpha_adv: float = 0.0     # Retrocausal coupling (0 = disabled)
    tau_future: float = 10.0   # Future time window
    mass: float = 1.0          # Effective mass
    c: float = 1.0             # Effective speed
    
    def __post_init__(self):
        """Validate retrocausal parameters."""
        if self.alpha_adv < 0:
            raise ValueError("alpha_adv must be non-negative")
        if self.tau_future <= 0:
            raise ValueError("tau_future must be positive")
        if self.mass <= 0:
            raise ValueError("mass must be positive")
        if self.c <= 0:
            raise ValueError("c must be positive")


class AdvancedGreensFunction:
    """
    Advanced Green's function for retrocausal coupling.
    
    K_adv(t, t', x, x') for t' > t (future influencing past)
    
    For simplicity, we use a relativistic form:
        K_adv(t, t', r) = (1/4πr) δ(t' - t - r/c) θ(t' - t)
    
    Where θ is the Heaviside step function ensuring t' > t.
    
    In practice, we use a regularized Gaussian form:
        K_adv(t, t', r) ∝ exp(-(r - c(t'-t))²/σ²) / r  for t' > t
    """
    
    def __init__(self, params: RetrocausalParameters):
        """
        Initialize advanced Green's function.
        
        Args:
            params: RetrocausalParameters
        """
        self.params = params
        self.mass = params.mass
        self.c = params.c
        # Regularization width (makes delta function Gaussian)
        self.sigma = 0.1 * params.c  # 10% of light cone width
    
    def evaluate(
        self,
        t: float,
        t_prime: float,
        x: np.ndarray,
        x_prime: np.ndarray
    ) -> float:
        """
        Evaluate K_adv(t, t', x, x').
        
        Args:
            t: Present time
            t_prime: Future time
            x: Present position (3D)
            x_prime: Future position (3D)
            
        Returns:
            Green's function value
        """
        # Causality check: only future influences past
        if t_prime <= t:
            return 0.0
        
        # Spatial separation
        r = np.linalg.norm(x_prime - x)
        if r < 1e-10:
            r = 1e-10  # Avoid singularity
        
        # Time delay
        dt = t_prime - t
        
        # Light cone distance
        r_cone = self.c * dt
        
        # Regularized delta function (Gaussian)
        # Peak when r = r_cone (on light cone)
        delta_reg = np.exp(-((r - r_cone)**2) / (2 * self.sigma**2))
        
        # Green's function with 1/r falloff and mass decay
        K = (delta_reg / (4 * np.pi * r)) * np.exp(-self.mass * r)
        
        return K
    
    def integrate_over_future(
        self,
        t: float,
        x: np.ndarray,
        attractor_field: callable,
        t_max: Optional[float] = None
    ) -> float:
        """
        Integrate K_adv over future times and positions.
        
        𝒢(x,t) = ∫∫ K_adv(t,t',x,x') A∞(x',t') d³x' dt'
        
        Args:
            t: Present time
            x: Present position
            attractor_field: Function A∞(x', t') returning attractor value
            t_max: Maximum future time (default: t + tau_future)
            
        Returns:
            Integrated Grace field value at (x,t)
        """
        if t_max is None:
            t_max = t + self.params.tau_future
        
        # Simple Monte Carlo integration
        # (In production, use more sophisticated quadrature)
        num_samples = 100
        
        # Sample future times
        t_samples = np.linspace(t + 0.1, t_max, num_samples)
        
        # Sample spatial positions (in a sphere around x)
        # For simplicity, sample on a grid
        r_max = self.c * self.params.tau_future
        num_spatial = 10
        x_range = np.linspace(-r_max, r_max, num_spatial)
        
        total = 0.0
        count = 0
        
        for t_prime in t_samples:
            for dx in x_range:
                for dy in x_range:
                    for dz in x_range:
                        x_prime = x + np.array([dx, dy, dz])
                        
                        # Evaluate Green's function
                        K = self.evaluate(t, t_prime, x, x_prime)
                        
                        # Evaluate attractor field
                        A = attractor_field(x_prime, t_prime)
                        
                        # Accumulate
                        total += K * A
                        count += 1
        
        # Volume element (crude approximation)
        dt_step = (t_max - t) / num_samples
        dx_step = (2 * r_max) / num_spatial
        dV = dt_step * dx_step**3
        
        return total * dV


@dataclass
class AttractorField:
    """
    Represents the future attractor field A∞(x,t).
    
    This can be:
    1. Static attractor (time-independent)
    2. Evolving attractor (following gradient flow)
    3. Known future state (from simulation/prediction)
    """
    field_values: Dict[Tuple[float, float, float, float], float]  # (x,y,z,t) → value
    default_value: float = 1.0  # Default for unseen points
    
    def __call__(self, x: np.ndarray, t: float) -> float:
        """
        Evaluate A∞(x,t).
        
        Args:
            x: Position (3D array)
            t: Time
            
        Returns:
            Attractor field value
        """
        # Round to nearest grid point
        key = (round(x[0], 2), round(x[1], 2), round(x[2], 2), round(t, 2))
        
        return self.field_values.get(key, self.default_value)
    
    @classmethod
    def gaussian_attractor(cls, center: np.ndarray, width: float = 1.0) -> 'AttractorField':
        """
        Create a Gaussian attractor centered at given position.
        
        Args:
            center: Center position (3D)
            width: Gaussian width
            
        Returns:
            AttractorField instance
        """
        # Create field values for a grid
        field_values = {}
        
        r_max = 5 * width
        num_points = 20
        t_points = 10
        
        for t in np.linspace(0, 10, t_points):
            for x in np.linspace(center[0] - r_max, center[0] + r_max, num_points):
                for y in np.linspace(center[1] - r_max, center[1] + r_max, num_points):
                    for z in np.linspace(center[2] - r_max, center[2] + r_max, num_points):
                        pos = np.array([x, y, z])
                        r = np.linalg.norm(pos - center)
                        value = np.exp(-r**2 / (2 * width**2))
                        
                        key = (round(x, 2), round(y, 2), round(z, 2), round(t, 2))
                        field_values[key] = value
        
        return cls(field_values=field_values, default_value=0.0)


class RetrocausalCoherenceTensor(CoherenceTensor):
    """
    Extended coherence tensor with Grace retrocausality.
    
    Adds retrocausal coupling to the standard coherence tensor evolution.
    
    Modified evolution equation:
        dΨ/dt = C·Ψ + α_adv·𝒢_adv[Ψ; A∞]
    
    Where 𝒢_adv is the retrocausal Grace field from future attractor.
    """
    
    def __init__(
        self,
        params: CoherenceParameters,
        retrocausal_params: Optional[RetrocausalParameters] = None,
        attractor: Optional[AttractorField] = None
    ):
        """
        Initialize retrocausal coherence tensor.
        
        Args:
            params: Standard CoherenceParameters
            retrocausal_params: RetrocausalParameters (if None, no retrocausality)
            attractor: AttractorField A∞ (if None, use default)
        """
        super().__init__(params)
        
        self.retrocausal_params = retrocausal_params or RetrocausalParameters(alpha_adv=0.0)
        self.attractor = attractor
        
        # Initialize advanced Green's function
        if self.retrocausal_params.alpha_adv > 0:
            self.greens_function = AdvancedGreensFunction(self.retrocausal_params)
        else:
            self.greens_function = None
    
    def compute_grace_field(
        self,
        x: np.ndarray,
        t: float,
        t_max: Optional[float] = None
    ) -> float:
        """
        Compute retrocausal Grace field 𝒢(x,t) at given position and time.
        
        𝒢(x,t) = α_adv ∫∫ K_adv(t,t',x,x') A∞(x',t') d³x' dt'
        
        Args:
            x: Position (3D)
            t: Time
            t_max: Maximum future time
            
        Returns:
            Grace field value
        """
        if self.greens_function is None or self.attractor is None:
            return 0.0
        
        # Integrate over future
        grace = self.greens_function.integrate_over_future(
            t, x, self.attractor, t_max
        )
        
        # Apply coupling strength
        return self.retrocausal_params.alpha_adv * grace
    
    def retrocausal_trajectory(
        self,
        t: np.ndarray,
        include_retrocausality: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute trajectory with optional retrocausal correction.
        
        Standard: Ψ(t) = exp(tC) Ψ₀
        With retrocausality: Ψ(t) = exp(tC) Ψ₀ + ∫₀ᵗ exp((t-s)C) 𝒢(s) ds
        
        Args:
            t: Time array
            include_retrocausality: Whether to include 𝒢_adv term
            
        Returns:
            Tuple of (x, y, z) trajectory arrays
        """
        # Get standard trajectory
        x_std, y_std, z_std = self.parametric_trajectory(t)
        
        if not include_retrocausality or self.greens_function is None:
            return x_std, y_std, z_std
        
        # Add retrocausal corrections
        x_retro = np.zeros_like(x_std)
        y_retro = np.zeros_like(y_std)
        z_retro = np.zeros_like(z_std)
        
        for i, t_val in enumerate(t):
            pos = np.array([x_std[i], y_std[i], z_std[i]])
            grace = self.compute_grace_field(pos, t_val)
            
            # Simple correction: Grace pulls toward attractor center
            # (In full theory, this would be gradient of Grace potential)
            if hasattr(self.attractor, 'field_values') and len(self.attractor.field_values) > 0:
                # Find attractor center (crude approximation)
                x_retro[i] = grace * 0.1  # Small perturbation
                y_retro[i] = grace * 0.1
                z_retro[i] = grace * 0.1
        
        return x_std + x_retro, y_std + y_retro, z_std + z_retro
    
    def temporal_fixed_point_check(self, t_values: np.ndarray, tolerance: float = 1e-3) -> bool:
        """
        Verify temporal fixed point theorem:
        𝒢(Ψ(t)) should be constant along the flow.
        
        Args:
            t_values: Array of times to check
            tolerance: Maximum allowed variation
            
        Returns:
            True if fixed point condition is satisfied
        """
        if self.greens_function is None or self.attractor is None:
            return True  # Trivially satisfied if no retrocausality
        
        # Compute trajectory
        x, y, z = self.retrocausal_trajectory(t_values, include_retrocausality=True)
        
        # Compute Grace field at each point
        grace_values = []
        for i, t in enumerate(t_values):
            pos = np.array([x[i], y[i], z[i]])
            grace = self.compute_grace_field(pos, t)
            grace_values.append(grace)
        
        # Check if variance is small
        grace_std = np.std(grace_values)
        grace_mean = np.mean(grace_values)
        
        if grace_mean < 1e-10:
            return True  # Trivial case
        
        relative_variation = grace_std / abs(grace_mean)
        
        return relative_variation < tolerance


# Module-level convenience functions

def compute_trajectory(
    lambda_lg: float,
    beta_sp: float,
    omega_ri: float,
    t_max: float = 10.0,
    num_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute complete trajectory for given parameters.
    
    Args:
        lambda_lg: Love-Grace coefficient
        beta_sp: Scale-Phase coefficient
        omega_ri: Real-Imaginary coefficient
        t_max: Maximum time
        num_points: Number of points
        
    Returns:
        Tuple of (t, x, y, z) arrays
    """
    params = CoherenceParameters(lambda_lg, beta_sp, omega_ri)
    tensor = CoherenceTensor(params)
    
    t = np.linspace(0, t_max, num_points)
    x, y, z = tensor.parametric_trajectory(t)
    
    return t, x, y, z


if __name__ == "__main__":
    # Demonstration
    print("=" * 70)
    print("COHERENCE TENSOR DEMONSTRATION")
    print("=" * 70)
    
    # Create a general coherence tensor
    params = CoherenceParameters(lambda_lg=1.0, beta_sp=0.1, omega_ri=0.8)
    tensor = CoherenceTensor(params)
    
    print(f"\nParameters:")
    print(f"  λ (Love-Grace):    {params.lambda_lg}")
    print(f"  β (Scale-Phase):   {params.beta_sp}")
    print(f"  ω (Real-Imaginary): {params.omega_ri}")
    print(f"  Invariant I:       {params.invariant:.6f}")
    
    print(f"\nGeometry: {tensor.classify_geometry()}")
    
    # Differential invariants
    κ, τ = tensor.differential_invariants(t=1.0)
    print(f"\nDifferential Invariants (t=1):")
    print(f"  Curvature κ: {κ:.6f}")
    print(f"  Torsion τ:   {τ:.6f}")
    
    # Energy/information decomposition
    flows = tensor.energy_flow_decomposition()
    print(f"\nFlow Decomposition:")
    print(f"  Energy flow:       {flows['energy_flow']:.6f}")
    print(f"  Information flow:  {flows['information_flow']:.6f}")
    print(f"  Ratio (I/E):       {flows['ratio']:.6f}")
    
    # Jacobi closure
    is_closed = tensor.jacobi_closure()
    print(f"\nJacobi Closure: {'✓ SATISFIED' if is_closed else '✗ VIOLATED'}")
    
    print("\n" + "=" * 70)
    print("Demonstration complete.")
    print("=" * 70)

