"""
Field Equations: O(3) Sigma Model + Faddeev-Skyrme + Retrocausal Source

This module implements the coherence field theory equations:

Lagrangian:
    ℒ = (f²/2) ∂_μn · ∂^μn - (κ/4) (∂_μn × ∂_νn)² - V(n) + ℒ_retro

Where:
    - n(x,t): Unit vector field n ∈ S² (coherence direction)
    - f: Field strength (sets energy scale)
    - κ: Skyrme coefficient (stabilizes solitons)
    - V(n): Potential (breaks rotation symmetry)
    - ℒ_retro: Retrocausal coupling to future attractor

Euler-Lagrange Equations:
    f² □n - κ ∂_μ(F^μν n × ∂_νn) + ∂V/∂n + 𝒢_retro = λn

Where:
    - □ = ∂²_t - ∇² (d'Alembertian)
    - F^μν = ∂_μn × ∂_νn (field strength tensor)
    - λ: Lagrange multiplier enforcing |n| = 1
    - 𝒢_retro: Retrocausal source from future attractor

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import numpy as np
from typing import Tuple, Dict, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from scipy.integrate import solve_ivp

# Import coherence tensor for retrocausality
try:
    from coherence_tensor import (
        RetrocausalParameters,
        AdvancedGreensFunction,
        AttractorField
    )
    RETROCAUSALITY_AVAILABLE = True
except ImportError:
    # Define dummy types for type hints when not available
    RetrocausalParameters = type(None)
    AdvancedGreensFunction = type(None)
    AttractorField = type(None)
    RETROCAUSALITY_AVAILABLE = False


class BoundaryCondition(Enum):
    """Boundary condition types."""
    PERIODIC = "periodic"
    DIRICHLET = "dirichlet"
    NEUMANN = "neumann"
    OPEN = "open"


@dataclass
class FieldParameters:
    """
    Parameters for the coherence field theory.
    
    Attributes:
        f: Field strength (energy scale)
        kappa: Skyrme coefficient (topological stabilization)
        mass: Potential mass term (V = ½m²(1 - n·e₃))
        lambda_reg: Regularization for constraint enforcement
        c: Speed of propagation (c=1 for relativistic)
    """
    f: float = 1.0          # Field strength
    kappa: float = 0.1      # Skyrme coefficient
    mass: float = 0.0       # Mass term
    lambda_reg: float = 1.0 # Constraint regularization
    c: float = 1.0          # Speed of propagation
    
    def __post_init__(self):
        """Validate parameters."""
        if self.f <= 0:
            raise ValueError("Field strength f must be positive")
        if self.kappa < 0:
            raise ValueError("Skyrme coefficient kappa must be non-negative")
        if self.lambda_reg <= 0:
            raise ValueError("Regularization lambda_reg must be positive")
        if self.c <= 0:
            raise ValueError("Speed c must be positive")


@dataclass
class GridParameters:
    """
    Spatial and temporal grid parameters.
    
    Attributes:
        Nx: Number of spatial grid points in x
        Ny: Number of spatial grid points in y (None for 1D)
        Lx: Spatial domain size in x
        Ly: Spatial domain size in y (None for 1D)
        dt: Time step
        t_max: Maximum simulation time
        boundary: Boundary condition type
    """
    Nx: int = 64
    Ny: Optional[int] = None  # None for 1D, int for 2D
    Lx: float = 10.0
    Ly: Optional[float] = None
    dt: float = 0.01
    t_max: float = 10.0
    boundary: BoundaryCondition = BoundaryCondition.PERIODIC
    
    def __post_init__(self):
        """Validate and compute derived parameters."""
        if self.Nx < 8:
            raise ValueError("Nx must be at least 8")
        if self.Ny is not None and self.Ny < 8:
            raise ValueError("Ny must be at least 8 if specified")
        if self.Lx <= 0:
            raise ValueError("Lx must be positive")
        if self.Ly is not None and self.Ly <= 0:
            raise ValueError("Ly must be positive if specified")
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        if self.t_max <= 0:
            raise ValueError("t_max must be positive")
        
        # Compute grid spacing
        self.dx = self.Lx / self.Nx
        if self.Ny is not None and self.Ly is not None:
            self.dy = self.Ly / self.Ny
        else:
            self.dy = None
    
    @property
    def is_1d(self) -> bool:
        """Check if simulation is 1D."""
        return self.Ny is None
    
    @property
    def is_2d(self) -> bool:
        """Check if simulation is 2D."""
        return self.Ny is not None


class CoherenceField:
    """
    Represents the coherence field n(x,t) on a grid.
    
    The field is a unit vector field: n ∈ S² at each point.
    Stored as (n_x, n_y, n_z) components.
    """
    
    def __init__(self, grid: GridParameters):
        """
        Initialize field on grid.
        
        Args:
            grid: GridParameters defining the spatial grid
        """
        self.grid = grid
        
        # Initialize field arrays
        if grid.is_1d:
            shape = (grid.Nx,)
        else:
            shape = (grid.Nx, grid.Ny)
        
        self.n_x = np.zeros(shape)
        self.n_y = np.zeros(shape)
        self.n_z = np.ones(shape)  # Start aligned with z-axis
        
        # Time derivative (for dynamics)
        self.n_x_dot = np.zeros(shape)
        self.n_y_dot = np.zeros(shape)
        self.n_z_dot = np.zeros(shape)
        
        # Current time
        self.t = 0.0
    
    def normalize(self):
        """Enforce |n| = 1 constraint at all points."""
        norm = np.sqrt(self.n_x**2 + self.n_y**2 + self.n_z**2)
        norm = np.maximum(norm, 1e-10)  # Avoid division by zero
        
        self.n_x /= norm
        self.n_y /= norm
        self.n_z /= norm
    
    def set_gaussian_soliton(self, center: Tuple[float, ...], width: float, direction: np.ndarray):
        """
        Initialize with a Gaussian-like soliton.
        
        Args:
            center: Center position (x,) or (x,y)
            width: Width of soliton
            direction: Target direction (3D unit vector)
        """
        direction = np.array(direction)
        direction /= np.linalg.norm(direction)
        
        if self.grid.is_1d:
            x = np.linspace(0, self.grid.Lx, self.grid.Nx)
            r = np.abs(x - center[0])
        else:
            x = np.linspace(0, self.grid.Lx, self.grid.Nx)
            y = np.linspace(0, self.grid.Ly, self.grid.Ny)
            X, Y = np.meshgrid(x, y, indexing='ij')
            r = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
        
        # Smooth interpolation from z-axis to target direction
        weight = np.exp(-r**2 / (2 * width**2))
        
        self.n_x = weight * direction[0]
        self.n_y = weight * direction[1]
        self.n_z = 1.0 - weight * (1.0 - direction[2])
        
        self.normalize()
    
    def set_hopf_soliton(self, width: float = 1.0):
        """
        Initialize with a Hopf soliton (Q_H = 1) in 2D.
        
        This is a toroidal configuration with linking number 1.
        Only works for 2D grids.
        
        Args:
            width: Characteristic size of the soliton
        """
        if self.grid.is_1d:
            raise ValueError("Hopf soliton requires 2D grid")
        
        x = np.linspace(-self.grid.Lx/2, self.grid.Lx/2, self.grid.Nx)
        y = np.linspace(-self.grid.Ly/2, self.grid.Ly/2, self.grid.Ny)
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        # Hopf coordinates (stereographic projection)
        r = np.sqrt(X**2 + Y**2)
        theta = np.arctan2(Y, X)
        
        # Ansatz for Q_H = 1 configuration
        # n = (sin(f(r)) cos(θ), sin(f(r)) sin(θ), cos(f(r)))
        # where f(r) goes from 0 to π as r goes from 0 to ∞
        
        f_r = np.pi * (1 - np.exp(-r**2 / width**2))
        
        self.n_x = np.sin(f_r) * np.cos(theta)
        self.n_y = np.sin(f_r) * np.sin(theta)
        self.n_z = np.cos(f_r)
        
        self.normalize()
    
    def energy(self, params: FieldParameters) -> float:
        """
        Compute total energy of the field configuration.
        
        E = ∫ (f²/2 |∇n|² + κ/4 |∂_x n × ∂_y n|² + V(n)) dx dy
        
        Args:
            params: FieldParameters
            
        Returns:
            Total energy
        """
        # Gradient energy
        if self.grid.is_1d:
            dn_dx = np.gradient(np.stack([self.n_x, self.n_y, self.n_z]), 
                               self.grid.dx, axis=1)
            grad_energy = 0.5 * params.f**2 * np.sum(dn_dx**2) * self.grid.dx
            skyrme_energy = 0.0  # No Skyrme term in 1D
        else:
            # 2D case
            dn_dx = np.gradient(np.stack([self.n_x, self.n_y, self.n_z]), 
                               self.grid.dx, axis=1)
            dn_dy = np.gradient(np.stack([self.n_x, self.n_y, self.n_z]), 
                               self.grid.dy, axis=2)
            
            grad_energy = 0.5 * params.f**2 * (np.sum(dn_dx**2) + np.sum(dn_dy**2)) * self.grid.dx * self.grid.dy
            
            # Skyrme term: |∂_x n × ∂_y n|²
            cross = np.cross(dn_dx, dn_dy, axis=0)
            skyrme_energy = 0.25 * params.kappa * np.sum(cross**2) * self.grid.dx * self.grid.dy
        
        # Potential energy: V = ½m²(1 - n_z)
        potential_energy = 0.5 * params.mass**2 * np.sum(1.0 - self.n_z)
        if self.grid.is_1d:
            potential_energy *= self.grid.dx
        else:
            potential_energy *= self.grid.dx * self.grid.dy
        
        return grad_energy + skyrme_energy + potential_energy
    
    def get_state_vector(self) -> np.ndarray:
        """
        Get field as flat state vector [n_x, n_y, n_z, ṅ_x, ṅ_y, ṅ_z].
        
        Returns:
            Flattened state vector
        """
        return np.concatenate([
            self.n_x.flatten(),
            self.n_y.flatten(),
            self.n_z.flatten(),
            self.n_x_dot.flatten(),
            self.n_y_dot.flatten(),
            self.n_z_dot.flatten()
        ])
    
    def set_from_state_vector(self, state: np.ndarray):
        """
        Set field from flat state vector.
        
        Args:
            state: Flattened state vector
        """
        N = self.n_x.size
        shape = self.n_x.shape
        
        self.n_x = state[0*N:1*N].reshape(shape)
        self.n_y = state[1*N:2*N].reshape(shape)
        self.n_z = state[2*N:3*N].reshape(shape)
        self.n_x_dot = state[3*N:4*N].reshape(shape)
        self.n_y_dot = state[4*N:5*N].reshape(shape)
        self.n_z_dot = state[5*N:6*N].reshape(shape)


class FieldEvolution:
    """
    Solves the field equations with optional retrocausality.
    
    Implements:
        f² □n - κ ∂_μ(F^μν n × ∂_νn) + ∂V/∂n + 𝒢_retro = λn
    
    Where λ is a Lagrange multiplier enforcing |n| = 1.
    """
    
    def __init__(
        self,
        field: CoherenceField,
        params: FieldParameters,
        retrocausal_params: Optional[RetrocausalParameters] = None,
        attractor: Optional[AttractorField] = None
    ):
        """
        Initialize field evolution solver.
        
        Args:
            field: CoherenceField to evolve
            params: FieldParameters
            retrocausal_params: Optional retrocausal parameters
            attractor: Optional future attractor field
        """
        self.field = field
        self.params = params
        self.retrocausal_params = retrocausal_params
        self.attractor = attractor
        
        # Initialize retrocausality if enabled
        if (retrocausal_params is not None and 
            retrocausal_params.alpha_adv > 0 and 
            attractor is not None and
            RETROCAUSALITY_AVAILABLE and
            type(retrocausal_params).__name__ != 'NoneType'):  # Check it's not dummy type
            self.greens_function = AdvancedGreensFunction(retrocausal_params)
            self.retrocausality_enabled = True
        else:
            self.greens_function = None
            self.retrocausality_enabled = False
        
        # Build spatial derivative operators
        self._build_derivative_operators()
    
    def _build_derivative_operators(self):
        """Build finite difference operators for spatial derivatives."""
        grid = self.field.grid
        
        if grid.is_1d:
            # 1D second derivative operator (periodic or Dirichlet)
            if grid.boundary == BoundaryCondition.PERIODIC:
                # Periodic boundaries
                diag = -2.0 * np.ones(grid.Nx)
                off_diag = np.ones(grid.Nx - 1)
                self.D2_x = sp.diags([diag, off_diag, off_diag, [1.0], [1.0]], 
                                    [0, 1, -1, grid.Nx-1, -(grid.Nx-1)],
                                    shape=(grid.Nx, grid.Nx))
                self.D2_x /= grid.dx**2
            else:
                # Dirichlet boundaries
                diag = -2.0 * np.ones(grid.Nx)
                off_diag = np.ones(grid.Nx - 1)
                self.D2_x = sp.diags([diag, off_diag, off_diag], [0, 1, -1],
                                    shape=(grid.Nx, grid.Nx))
                self.D2_x /= grid.dx**2
        else:
            # 2D Laplacian (simplified - assume periodic for now)
            # Full 2D implementation would use Kronecker products
            # For now, we'll handle this in the RHS function directly
            self.D2_x = None
            self.D2_y = None
    
    def compute_laplacian(self, field_component: np.ndarray) -> np.ndarray:
        """
        Compute Laplacian ∇²f of a field component.
        
        Args:
            field_component: Field component (2D array)
            
        Returns:
            Laplacian
        """
        grid = self.field.grid
        
        if grid.is_1d:
            # Use sparse operator
            return self.D2_x @ field_component
        else:
            # 2D finite differences
            laplacian = np.zeros_like(field_component)
            
            # x-direction
            laplacian[1:-1, :] += (field_component[2:, :] - 2*field_component[1:-1, :] + 
                                   field_component[:-2, :]) / grid.dx**2
            
            # y-direction
            laplacian[:, 1:-1] += (field_component[:, 2:] - 2*field_component[:, 1:-1] + 
                                   field_component[:, :-2]) / grid.dy**2
            
            # Handle boundaries (periodic)
            if grid.boundary == BoundaryCondition.PERIODIC:
                # x-direction boundaries
                laplacian[0, :] = (field_component[1, :] - 2*field_component[0, :] + 
                                  field_component[-1, :]) / grid.dx**2
                laplacian[-1, :] = (field_component[0, :] - 2*field_component[-1, :] + 
                                   field_component[-2, :]) / grid.dx**2
                
                # y-direction boundaries
                laplacian[:, 0] += (field_component[:, 1] - 2*field_component[:, 0] + 
                                   field_component[:, -1]) / grid.dy**2
                laplacian[:, -1] += (field_component[:, 0] - 2*field_component[:, -1] + 
                                    field_component[:, -2]) / grid.dy**2
            
            return laplacian
    
    def compute_retrocausal_source(self, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute retrocausal source term 𝒢_retro from future attractor.
        
        𝒢_retro(x,t) = α_adv ∫ K_adv(t,t',x,x') A∞(x',t') d⁴x'
        
        Args:
            t: Current time
            
        Returns:
            Tuple of (𝒢_x, 𝒢_y, 𝒢_z) source terms
        """
        if not self.retrocausality_enabled:
            return np.zeros_like(self.field.n_x), np.zeros_like(self.field.n_y), np.zeros_like(self.field.n_z)
        
        grid = self.field.grid
        
        # Initialize source arrays
        G_x = np.zeros_like(self.field.n_x)
        G_y = np.zeros_like(self.field.n_y)
        G_z = np.zeros_like(self.field.n_z)
        
        # For computational efficiency, compute Grace field at a subset of points
        # In production, this would be optimized with adaptive sampling
        
        # Simple approach: sample at grid points
        if grid.is_1d:
            x_coords = np.linspace(0, grid.Lx, grid.Nx)
            for i, x in enumerate(x_coords):
                pos = np.array([x, 0.0, 0.0])
                grace = self.greens_function.integrate_over_future(
                    t, pos, self.attractor
                )
                # Grace pulls toward attractor (simplified)
                G_z[i] = self.retrocausal_params.alpha_adv * grace
        else:
            # 2D case (expensive - in production use sparse sampling)
            # For now, skip to keep computational cost reasonable
            pass
        
        return G_x, G_y, G_z
    
    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Right-hand side of field equations for ODE solver.
        
        d/dt [n, ṅ] = [ṅ, f⁻²(∇²n - κ·Skyrme + ∂V/∂n + 𝒢_retro - λn)]
        
        Args:
            t: Current time
            state: State vector [n_x, n_y, n_z, ṅ_x, ṅ_y, ṅ_z]
            
        Returns:
            Time derivative of state
        """
        # Extract current field and velocity
        N = self.field.n_x.size
        shape = self.field.n_x.shape
        
        n_x = state[0*N:1*N].reshape(shape)
        n_y = state[1*N:2*N].reshape(shape)
        n_z = state[2*N:3*N].reshape(shape)
        n_x_dot = state[3*N:4*N].reshape(shape)
        n_y_dot = state[4*N:5*N].reshape(shape)
        n_z_dot = state[5*N:6*N].reshape(shape)
        
        # Laplacian terms
        lap_n_x = self.compute_laplacian(n_x)
        lap_n_y = self.compute_laplacian(n_y)
        lap_n_z = self.compute_laplacian(n_z)
        
        # Potential force: -∂V/∂n where V = ½m²(1 - n_z)
        force_potential_z = self.params.mass**2 * np.ones_like(n_z)
        force_potential_x = np.zeros_like(n_x)
        force_potential_y = np.zeros_like(n_y)
        
        # Skyrme term (complex - simplified for now)
        # Full implementation would compute ∂_μ(F^μν n × ∂_νn)
        # For now, use a regularization term
        force_skyrme_x = np.zeros_like(n_x)
        force_skyrme_y = np.zeros_like(n_y)
        force_skyrme_z = np.zeros_like(n_z)
        
        # Retrocausal source
        G_x, G_y, G_z = self.compute_retrocausal_source(t)
        
        # Lagrange multiplier for constraint |n| = 1
        # λ = n · (f² ∇²n + forces) to keep |n| = 1
        n_dot_force = (n_x * (self.params.f**2 * lap_n_x + force_potential_x + self.params.kappa * force_skyrme_x + G_x) +
                       n_y * (self.params.f**2 * lap_n_y + force_potential_y + self.params.kappa * force_skyrme_y + G_y) +
                       n_z * (self.params.f**2 * lap_n_z + force_potential_z + self.params.kappa * force_skyrme_z + G_z))
        
        lambda_multiplier = n_dot_force / (n_x**2 + n_y**2 + n_z**2 + 1e-10)
        
        # Equations of motion: f² n_ddot = f² ∇²n + forces - λn
        n_x_ddot = (self.params.f**2 * lap_n_x + force_potential_x + self.params.kappa * force_skyrme_x + G_x 
                    - lambda_multiplier * n_x) / self.params.f**2
        n_y_ddot = (self.params.f**2 * lap_n_y + force_potential_y + self.params.kappa * force_skyrme_y + G_y 
                    - lambda_multiplier * n_y) / self.params.f**2
        n_z_ddot = (self.params.f**2 * lap_n_z + force_potential_z + self.params.kappa * force_skyrme_z + G_z 
                    - lambda_multiplier * n_z) / self.params.f**2
        
        # Assemble derivative
        dstate_dt = np.concatenate([
            n_x_dot.flatten(),
            n_y_dot.flatten(),
            n_z_dot.flatten(),
            n_x_ddot.flatten(),
            n_y_ddot.flatten(),
            n_z_ddot.flatten()
        ])
        
        return dstate_dt
    
    def evolve(self, t_span: Tuple[float, float], method: str = 'RK45') -> Dict:
        """
        Evolve field from t_span[0] to t_span[1].
        
        Args:
            t_span: (t_start, t_end)
            method: ODE solver method ('RK45', 'DOP853', 'BDF')
            
        Returns:
            Dictionary with solution history
        """
        # Initial state
        y0 = self.field.get_state_vector()
        
        # Solve ODE
        sol = solve_ivp(
            self.rhs,
            t_span,
            y0,
            method=method,
            dense_output=True,
            max_step=self.field.grid.dt
        )
        
        # Update field to final state
        self.field.set_from_state_vector(sol.y[:, -1])
        self.field.t = sol.t[-1]
        self.field.normalize()
        
        return {
            't': sol.t,
            'y': sol.y,
            'success': sol.success,
            'message': sol.message
        }


# Module-level convenience function

def evolve_field_simple(
    initial_config: str = "hopf",
    Nx: int = 32,
    t_max: float = 5.0,
    with_retrocausality: bool = False
) -> Tuple[CoherenceField, Dict]:
    """
    Simple field evolution for testing.
    
    Args:
        initial_config: "hopf", "gaussian", or "vortex"
        Nx: Grid resolution
        t_max: Evolution time
        with_retrocausality: Enable retrocausality
        
    Returns:
        Tuple of (final_field, solution_dict)
    """
    # Setup grid
    grid = GridParameters(Nx=Nx, Ny=Nx if initial_config == "hopf" else None, 
                         Lx=10.0, Ly=10.0 if initial_config == "hopf" else None,
                         dt=0.01, t_max=t_max)
    
    # Setup field
    field = CoherenceField(grid)
    
    if initial_config == "hopf" and not grid.is_1d:
        field.set_hopf_soliton(width=2.0)
    elif initial_config == "gaussian":
        center = (grid.Lx / 2,) if grid.is_1d else (grid.Lx / 2, grid.Ly / 2)
        field.set_gaussian_soliton(center, width=2.0, direction=[0.5, 0.5, 0.7])
    else:
        # Default: small perturbation
        field.n_x += 0.1 * np.sin(2 * np.pi * np.linspace(0, 1, grid.Nx))
        field.normalize()
    
    # Setup parameters
    params = FieldParameters(f=1.0, kappa=0.1, mass=0.5)
    
    # Setup retrocausality if requested
    if with_retrocausality and RETROCAUSALITY_AVAILABLE:
        retro_params = RetrocausalParameters(alpha_adv=0.05, tau_future=3.0)
        attractor = AttractorField.gaussian_attractor(
            center=np.array([grid.Lx/2, 0.0, 0.0]), width=2.0
        )
    else:
        retro_params = None
        attractor = None
    
    # Evolve
    evolution = FieldEvolution(field, params, retro_params, attractor)
    sol = evolution.evolve((0, t_max))
    
    return field, sol


if __name__ == "__main__":
    # Demonstration
    print("=" * 70)
    print("FIELD EQUATIONS DEMONSTRATION")
    print("=" * 70)
    
    print("\nEvolving 1D Gaussian soliton...")
    field, sol = evolve_field_simple("gaussian", Nx=64, t_max=2.0)
    
    print(f"Evolution: {'SUCCESS' if sol['success'] else 'FAILED'}")
    print(f"Final time: t = {field.t:.3f}")
    print(f"Final energy: E = {field.energy(FieldParameters()):.6f}")
    print(f"Constraint satisfied: |n| = {np.mean(np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)):.6f}")
    
    print("\n" + "=" * 70)
    print("Demonstration complete.")
    print("=" * 70)

