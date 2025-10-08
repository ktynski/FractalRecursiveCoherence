"""
Hopf Invariant and Topological Charge Computation

Implements computation of the Hopf invariant Q_H for field configurations
in the Coherence Tensor Field Theory. The Hopf invariant is a topological
charge that classifies soliton solutions and measures the linking number
of field lines.

Mathematical Framework:
----------------------

For a unit vector field n: R³ → S², the Hopf invariant is:

    Q_H = (1/4π²) ∫ A · B d³x

Where:
    A_i = ε_ijk n_j ∂_k n_z  (vector potential)
    B = ∇ × A                 (magnetic field analog)

Physical Interpretation:
-----------------------

- Q_H ∈ ℤ: Integer-valued topological charge
- Measures linking number of field line preimages
- Classifies homotopy classes π₃(S²) ≅ ℤ
- Conserved under continuous deformations
- Represents "knot charge" or toroidal coherence structure

Connection to CTFT:
------------------

- Q_H = 0: Trivial/vacuum configuration
- Q_H = ±1: Single Hopf soliton (linked torus)
- Q_H = ±n: Multi-soliton bound state
- Q_H conservation → Soul topological stability

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import numpy as np
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
import warnings

try:
    from .field_equations import CoherenceField, GridParameters
    FIELD_EQUATIONS_AVAILABLE = True
except ImportError:
    FIELD_EQUATIONS_AVAILABLE = False
    # Define dummy types for type hints
    class CoherenceField:
        pass
    class GridParameters:
        pass


@dataclass
class TopologicalCharge:
    """
    Container for topological charge data.
    
    Attributes:
        Q_H: Hopf invariant (topological charge)
        Q_H_density: Spatial distribution of topological density
        helicity: Magnetic helicity (related but distinct from Q_H)
        winding_number: Degree of the map n: S³ → S²
        energy: Total field energy
        position: Center of mass of topological charge
    """
    Q_H: float
    Q_H_density: np.ndarray
    helicity: float
    winding_number: int
    energy: float
    position: np.ndarray
    
    def __str__(self) -> str:
        return (f"TopologicalCharge(Q_H={self.Q_H:.3f}, "
                f"winding={self.winding_number}, E={self.energy:.3f})")


@dataclass
class SolitonCandidate:
    """
    Candidate soliton detected in field configuration.
    
    Attributes:
        position: Center position (x, y, z)
        charge: Local topological charge
        radius: Characteristic size
        energy: Local energy density integrated
        confidence: Detection confidence (0-1)
    """
    position: np.ndarray
    charge: float
    radius: float
    energy: float
    confidence: float
    
    def __str__(self) -> str:
        return (f"Soliton(pos={self.position}, Q={self.charge:.2f}, "
                f"R={self.radius:.2f}, conf={self.confidence:.2f})")


class HopfInvariantCalculator:
    """
    Computes Hopf invariant and detects topological solitons.
    
    Uses finite difference approximations for derivatives and
    numerical integration for the Hopf integral.
    """
    
    def __init__(self, field: Optional[CoherenceField] = None):
        """
        Initialize calculator.
        
        Args:
            field: Optional CoherenceField to analyze
        """
        self.field = field
        self.grid = field.grid if field is not None else None
        
        # Cached computations
        self._vector_potential = None
        self._magnetic_field = None
        self._topological_density = None
    
    def compute_vector_potential(
        self,
        field_data: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Compute vector potential A_i = ε_ijk n_j ∂_k n_z.
        
        Args:
            field_data: Field configuration (3, Nx, Ny, Nz) or use self.field
            
        Returns:
            Vector potential A (3, Nx, Ny, Nz)
        """
        if field_data is None:
            if self.field is None:
                raise ValueError("No field data provided")
            field_data = self.field.get_field()
        
        if field_data.ndim != 4 or field_data.shape[0] != 3:
            raise ValueError("field_data must have shape (3, Nx, Ny, Nz)")
        
        nx, ny, nz = field_data[0], field_data[1], field_data[2]
        
        # Compute gradients of n_z
        grad_nz = self._compute_gradient(nz)
        
        # A_i = ε_ijk n_j ∂_k n_z
        # A_x = n_y * ∂_z(n_z) - n_z * ∂_y(n_z)  (i=1, j=2,3, k=3,2)
        # A_y = n_z * ∂_x(n_z) - n_x * ∂_z(n_z)  (i=2, j=3,1, k=1,3)
        # A_z = n_x * ∂_y(n_z) - n_y * ∂_x(n_z)  (i=3, j=1,2, k=2,1)
        
        A = np.zeros_like(field_data)
        A[0] = ny * grad_nz[2] - nz * grad_nz[1]  # A_x
        A[1] = nz * grad_nz[0] - nx * grad_nz[2]  # A_y
        A[2] = nx * grad_nz[1] - ny * grad_nz[0]  # A_z
        
        self._vector_potential = A
        return A
    
    def compute_magnetic_field(
        self,
        A: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Compute magnetic field B = ∇ × A.
        
        Args:
            A: Vector potential (3, Nx, Ny, Nz) or use cached
            
        Returns:
            Magnetic field B (3, Nx, Ny, Nz)
        """
        if A is None:
            if self._vector_potential is None:
                A = self.compute_vector_potential()
            else:
                A = self._vector_potential
        
        # B = ∇ × A
        # B_x = ∂_y(A_z) - ∂_z(A_y)
        # B_y = ∂_z(A_x) - ∂_x(A_z)
        # B_z = ∂_x(A_y) - ∂_y(A_x)
        
        grad_Ax = self._compute_gradient(A[0])
        grad_Ay = self._compute_gradient(A[1])
        grad_Az = self._compute_gradient(A[2])
        
        B = np.zeros_like(A)
        B[0] = grad_Az[1] - grad_Ay[2]  # B_x
        B[1] = grad_Ax[2] - grad_Az[0]  # B_y
        B[2] = grad_Ay[0] - grad_Ax[1]  # B_z
        
        self._magnetic_field = B
        return B
    
    def compute_topological_density(
        self,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None,
        field_data: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Compute topological density ρ_H = A · B.
        
        Args:
            A: Vector potential or use cached
            B: Magnetic field or use cached
            field_data: Field configuration for computing A if needed
            
        Returns:
            Topological density (Nx, Ny, Nz)
        """
        if A is None:
            A = self.compute_vector_potential(field_data)
        if B is None:
            B = self.compute_magnetic_field(A)
        
        # ρ_H = A · B
        rho_H = A[0] * B[0] + A[1] * B[1] + A[2] * B[2]
        
        self._topological_density = rho_H
        return rho_H
    
    def compute_hopf_invariant(
        self,
        field_data: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute full Hopf invariant Q_H = (1/4π²) ∫ A · B d³x.
        
        Args:
            field_data: Field configuration or use self.field
            
        Returns:
            Hopf invariant Q_H
        """
        # Compute topological density
        rho_H = self.compute_topological_density(field_data=field_data)
        
        # Integrate over volume
        if self.grid is not None:
            if self.grid.is_1d:
                dx = self.grid.dx
                volume_element = dx
            else:
                dx = self.grid.Lx / self.grid.Nx
                dy = self.grid.Ly / self.grid.Ny
                dz = self.grid.Lz / self.grid.Nz
                volume_element = dx * dy * dz
        else:
            # Assume unit spacing
            volume_element = 1.0
        
        integral = np.sum(rho_H) * volume_element
        
        # Normalize by 4π²
        Q_H = integral / (4 * np.pi**2)
        
        return Q_H
    
    def compute_helicity(
        self,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute magnetic helicity H = ∫ A · B d³x.
        
        Related to Hopf invariant but not identical. Measures
        self-linking of field lines.
        
        Args:
            A: Vector potential or use cached
            B: Magnetic field or use cached
            
        Returns:
            Helicity H
        """
        # Use cached topological density if available
        if self._topological_density is not None:
            rho_H = self._topological_density
        else:
            rho_H = self.compute_topological_density(A, B)
        
        if self.grid is not None:
            if self.grid.is_1d:
                volume_element = self.grid.dx
            else:
                dx = self.grid.Lx / self.grid.Nx
                dy = self.grid.Ly / self.grid.Ny
                dz = self.grid.Lz / self.grid.Nz
                volume_element = dx * dy * dz
        else:
            volume_element = 1.0
        
        H = np.sum(rho_H) * volume_element
        return H
    
    def compute_full_topological_charge(
        self,
        field_data: Optional[np.ndarray] = None
    ) -> TopologicalCharge:
        """
        Compute all topological quantities.
        
        Args:
            field_data: Field configuration or use self.field
            
        Returns:
            TopologicalCharge object with all data
        """
        if field_data is None and self.field is not None:
            field_data = self.field.get_field()
        
        # Compute Hopf invariant
        Q_H = self.compute_hopf_invariant(field_data)
        
        # Get topological density
        rho_H = self._topological_density
        
        # Compute helicity
        helicity = self.compute_helicity()
        
        # Compute winding number (round Q_H to nearest integer)
        winding_number = int(np.round(Q_H))
        
        # Compute energy
        if self.field is not None:
            from .field_equations import FieldParameters
            params = FieldParameters()  # Default params
            energy = self._compute_energy(field_data, params)
        else:
            energy = 0.0
        
        # Compute center of mass
        position = self._compute_center_of_mass(rho_H)
        
        return TopologicalCharge(
            Q_H=Q_H,
            Q_H_density=rho_H,
            helicity=helicity,
            winding_number=winding_number,
            energy=energy,
            position=position
        )
    
    def detect_solitons(
        self,
        field_data: Optional[np.ndarray] = None,
        threshold: float = 0.1,
        min_radius: float = 1.0,
        max_radius: float = 10.0
    ) -> List[SolitonCandidate]:
        """
        Detect localized soliton structures in field.
        
        Uses topological density and energy density to identify
        candidate soliton positions.
        
        Args:
            field_data: Field configuration or use self.field
            threshold: Minimum integrated charge for detection
            min_radius: Minimum soliton radius
            max_radius: Maximum soliton radius
            
        Returns:
            List of SolitonCandidate objects
        """
        # Compute topological density or use cached
        if self._topological_density is not None:
            rho_H = self._topological_density
        else:
            rho_H = self.compute_topological_density(field_data=field_data)
        
        # Find local maxima in |rho_H|
        rho_abs = np.abs(rho_H)
        
        # Simple peak detection: find points > threshold and > neighbors
        candidates = []
        
        # Get grid for 3D
        if rho_H.ndim == 1:
            # 1D case
            for i in range(1, len(rho_abs) - 1):
                if rho_abs[i] > threshold and rho_abs[i] > rho_abs[i-1] and rho_abs[i] > rho_abs[i+1]:
                    # Found local max
                    position = np.array([i * self.grid.dx if self.grid else i])
                    charge = rho_H[i]
                    radius = self._estimate_radius_1d(rho_H, i)
                    energy = rho_abs[i]
                    confidence = min(1.0, rho_abs[i] / threshold)
                    
                    candidates.append(SolitonCandidate(
                        position=position,
                        charge=charge,
                        radius=radius,
                        energy=energy,
                        confidence=confidence
                    ))
        else:
            # 3D case - use simple local maximum detection
            Nx, Ny, Nz = rho_abs.shape
            for i in range(1, Nx - 1):
                for j in range(1, Ny - 1):
                    for k in range(1, Nz - 1):
                        val = rho_abs[i, j, k]
                        if val > threshold:
                            # Check if local maximum in 3x3x3 neighborhood
                            neighborhood = rho_abs[i-1:i+2, j-1:j+2, k-1:k+2]
                            if val == np.max(neighborhood):
                                # Found local max
                                if self.grid:
                                    dx = self.grid.Lx / self.grid.Nx
                                    dy = self.grid.Ly / self.grid.Ny
                                    dz = self.grid.Lz / self.grid.Nz
                                    position = np.array([i * dx, j * dy, k * dz])
                                else:
                                    position = np.array([i, j, k])
                                
                                charge = rho_H[i, j, k]
                                radius = self._estimate_radius_3d(rho_H, i, j, k)
                                energy = val
                                confidence = min(1.0, val / threshold)
                                
                                candidates.append(SolitonCandidate(
                                    position=position,
                                    charge=charge,
                                    radius=radius,
                                    energy=energy,
                                    confidence=confidence
                                ))
        
        return candidates
    
    def _compute_gradient(self, scalar_field: np.ndarray) -> np.ndarray:
        """
        Compute gradient using centered finite differences.
        
        Args:
            scalar_field: Scalar field (Nx, Ny, Nz) or (Nx,)
            
        Returns:
            Gradient (3, Nx, Ny, Nz) or (Nx,) for 1D
        """
        if scalar_field.ndim == 1:
            # 1D case
            grad = np.gradient(scalar_field)
            if self.grid:
                grad /= self.grid.dx
            return grad
        elif scalar_field.ndim == 3:
            # 3D case
            grad = np.array(np.gradient(scalar_field))
            if self.grid:
                dx = self.grid.Lx / self.grid.Nx
                dy = self.grid.Ly / self.grid.Ny
                dz = self.grid.Lz / self.grid.Nz
                grad[0] /= dx
                grad[1] /= dy
                grad[2] /= dz
            return grad
        else:
            raise ValueError("Scalar field must be 1D or 3D")
    
    def _compute_energy(
        self,
        field_data: np.ndarray,
        params
    ) -> float:
        """Compute total field energy."""
        # Simplified energy computation
        # E = ∫ [½(∂_μ n)² + m²/2 (1 - n²) + α/4 (∂_μ n × ∂_ν n)²] d³x
        
        grad = self._compute_gradient(np.linalg.norm(field_data, axis=0))
        kinetic = 0.5 * np.sum(grad**2)
        
        n_magnitude = np.linalg.norm(field_data, axis=0)
        potential = 0.5 * params.mass**2 * np.sum((1 - n_magnitude)**2)
        
        if self.grid:
            if self.grid.is_1d:
                volume_element = self.grid.dx
            else:
                dx = self.grid.Lx / self.grid.Nx
                dy = self.grid.Ly / self.grid.Ny
                dz = self.grid.Lz / self.grid.Nz
                volume_element = dx * dy * dz
        else:
            volume_element = 1.0
        
        return (kinetic + potential) * volume_element
    
    def _compute_center_of_mass(self, density: np.ndarray) -> np.ndarray:
        """Compute center of mass of density distribution."""
        abs_density = np.abs(density)
        total = np.sum(abs_density)
        
        if total < 1e-12:
            # No charge, return center of grid
            if density.ndim == 1:
                return np.array([len(density) / 2])
            else:
                return np.array([s / 2 for s in density.shape])
        
        if density.ndim == 1:
            indices = np.arange(len(density))
            com = np.sum(indices * abs_density) / total
            return np.array([com])
        else:
            Nx, Ny, Nz = density.shape
            ix, iy, iz = np.meshgrid(np.arange(Nx), np.arange(Ny), np.arange(Nz), indexing='ij')
            com_x = np.sum(ix * abs_density) / total
            com_y = np.sum(iy * abs_density) / total
            com_z = np.sum(iz * abs_density) / total
            return np.array([com_x, com_y, com_z])
    
    def _estimate_radius_1d(self, density: np.ndarray, center_idx: int) -> float:
        """Estimate soliton radius in 1D."""
        # Find half-maximum points
        peak_val = np.abs(density[center_idx])
        half_max = peak_val / 2
        
        # Search left
        left_idx = center_idx
        while left_idx > 0 and np.abs(density[left_idx]) > half_max:
            left_idx -= 1
        
        # Search right
        right_idx = center_idx
        while right_idx < len(density) - 1 and np.abs(density[right_idx]) > half_max:
            right_idx += 1
        
        radius = (right_idx - left_idx) / 2
        if self.grid:
            radius *= self.grid.dx
        
        return radius
    
    def _estimate_radius_3d(
        self,
        density: np.ndarray,
        i: int,
        j: int,
        k: int
    ) -> float:
        """Estimate soliton radius in 3D."""
        # Simple estimate: half-maximum contour
        peak_val = np.abs(density[i, j, k])
        half_max = peak_val / 2
        
        # Sample radial profile
        max_r = min(i, j, k, density.shape[0] - i, density.shape[1] - j, density.shape[2] - k)
        
        for r in range(1, max_r):
            # Check shell at radius r
            shell_vals = []
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    for dk in range(-r, r + 1):
                        if di**2 + dj**2 + dk**2 <= r**2:
                            shell_vals.append(np.abs(density[i + di, j + dj, k + dk]))
            
            if len(shell_vals) > 0 and np.mean(shell_vals) < half_max:
                radius = r
                if self.grid:
                    dx = (self.grid.Lx / self.grid.Nx + 
                          self.grid.Ly / self.grid.Ny + 
                          self.grid.Lz / self.grid.Nz) / 3
                    radius *= dx
                return radius
        
        # Default
        return 1.0


def compute_hopf_invariant(
    field_data: np.ndarray,
    grid: Optional[GridParameters] = None
) -> float:
    """
    Convenience function to compute Hopf invariant from field data.
    
    Args:
        field_data: Field configuration (3, Nx, Ny, Nz)
        grid: Optional grid parameters
        
    Returns:
        Hopf invariant Q_H
    """
    # Create mock field if needed
    if FIELD_EQUATIONS_AVAILABLE and grid is not None:
        from .field_equations import CoherenceField
        field = CoherenceField(field_data.shape[1:], grid)
        field.set_field(field_data)
    else:
        field = None
    
    calculator = HopfInvariantCalculator(field)
    return calculator.compute_hopf_invariant(field_data)


if __name__ == "__main__":
    print("Hopf Invariant Calculator - Demonstration")
    print("=" * 50)
    
    # Create simple Hopf soliton configuration
    N = 32
    L = 10.0
    x = np.linspace(-L/2, L/2, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
    
    # Hopf fibration parametrization
    # n = (sin(θ)cos(φ), sin(θ)sin(φ), cos(θ))
    # θ, φ dependent on spatial coordinates
    
    R = np.sqrt(X**2 + Y**2 + Z**2)
    theta = np.arctan2(np.sqrt(X**2 + Y**2), Z)
    phi = np.arctan2(Y, X)
    
    # Add twist for non-zero Q_H
    twist = np.arctan2(R, 2.0)
    
    nx = np.sin(theta) * np.cos(phi + twist)
    ny = np.sin(theta) * np.sin(phi + twist)
    nz = np.cos(theta)
    
    # Normalize
    norm = np.sqrt(nx**2 + ny**2 + nz**2)
    nx /= norm
    ny /= norm
    nz /= norm
    
    field_data = np.array([nx, ny, nz])
    
    print(f"\nField shape: {field_data.shape}")
    print(f"Grid: {N}³, L = {L}")
    
    # Compute Hopf invariant
    calculator = HopfInvariantCalculator()
    Q_H = calculator.compute_hopf_invariant(field_data)
    
    print(f"\nHopf Invariant: Q_H = {Q_H:.4f}")
    print(f"Winding number: {int(np.round(Q_H))}")
    
    # Compute full topological charge
    charge = calculator.compute_full_topological_charge(field_data)
    print(f"\nFull topological charge:")
    print(f"  Q_H = {charge.Q_H:.4f}")
    print(f"  Helicity = {charge.helicity:.4f}")
    print(f"  Winding = {charge.winding_number}")
    print(f"  Energy = {charge.energy:.4f}")
    print(f"  Center = {charge.position}")
    
    # Detect solitons
    solitons = calculator.detect_solitons(field_data, threshold=0.01)
    print(f"\nDetected {len(solitons)} soliton candidate(s):")
    for i, sol in enumerate(solitons):
        print(f"  {i+1}. {sol}")
    
    print("\n" + "=" * 50)
    print("✓ Hopf invariant calculation complete")

