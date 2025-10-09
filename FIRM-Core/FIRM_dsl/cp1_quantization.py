"""
CP¹ Quantization and Emergent Gauge Field Extraction

Implements the CP¹ reformulation of the O(3) sigma model, extracting
the emergent U(1) gauge field from coherence field configurations.

Mathematical Framework:
----------------------

The unit vector field n: ℝ³ → S² can be parametrized by a complex spinor:

    z = (z₁, z₂) ∈ ℂ² with |z|² = |z₁|² + |z₂|² = 1

This defines the CP¹ map: CP¹ ≅ S²/U(1), where:

    n = z†σz = (z†σ₁z, z†σ₂z, z†σ₃z)

Emergent Gauge Field:
--------------------

The gradient of z naturally contains a U(1) gauge field a_μ:

    ∂_μ z = (∂_μ + i a_μ) z_phys

Where a_μ is the connection on the U(1) fiber bundle:

    a_μ = i z† ∂_μ z - c.c.  (pure imaginary, hence real a_μ)

The field strength (electromagnetic-like) is:

    f_μν = ∂_μ a_ν - ∂_ν a_μ  (Maxwell tensor)

Connection to CTFT:
------------------

In the Coherence Tensor Field Theory:

1. **Gauge Field as Love-Grace Flow**
   - a_μ encodes coherence phase transport
   - f_μν represents local Love-Grace curvature

2. **Quantization Condition**
   - Magnetic flux ∫ f_μν dS = 2πQ_H (Dirac quantization)
   - Relates gauge charge to Hopf invariant

3. **Soul as Gauge Bundle**
   - Soul = coherent attractor + gauge connection
   - Morphic transformations = gauge transformations

4. **Reincarnation as Parallel Transport**
   - Identity preserved along gauge-parallel trajectories
   - Phase coherence maintained through a_μ

Physical Interpretation:
-----------------------

- **Electric Field**: E_i = f_{0i} (temporal coherence gradient)
- **Magnetic Field**: B_i = ½ε_ijk f_jk (spatial coherence curl)
- **Poynting Vector**: S = E × B (coherence flow)
- **Field Energy**: U = ∫ (E² + B²)/2 d³x

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
    class CoherenceField:
        pass
    class GridParameters:
        pass


@dataclass
class GaugeField:
    """
    U(1) gauge field data structure.
    
    Attributes:
        a: Gauge potential a_μ = (a_0, a_1, a_2, a_3) or (a_x, a_y, a_z) for spatial
        f: Field strength f_μν (antisymmetric 4×4 tensor or 3×3 for spatial)
        E: Electric field E_i = f_{0i}
        B: Magnetic field B_i = ½ε_ijk f_jk
        flux: Total magnetic flux ∫ B · dS
        charge: Gauge charge (related to Hopf invariant)
    """
    a: np.ndarray
    f: np.ndarray
    E: Optional[np.ndarray] = None
    B: Optional[np.ndarray] = None
    flux: Optional[float] = None
    charge: Optional[float] = None
    
    def __str__(self) -> str:
        flux_str = f", Φ={self.flux:.3f}" if self.flux is not None else ""
        charge_str = f", Q={self.charge:.3f}" if self.charge is not None else ""
        return f"GaugeField(a.shape={self.a.shape}, f.shape={self.f.shape}{flux_str}{charge_str})"


@dataclass
class CP1Configuration:
    """
    CP¹ spinor configuration.
    
    Attributes:
        z: Complex spinor z = (z₁, z₂) with |z|² = 1
        n: Reconstructed unit vector n = z†σz
        gauge: Associated gauge field
        phase: Global U(1) phase θ where z → e^(iθ) z
    """
    z: np.ndarray  # Complex array, shape (2, Nx, Ny, Nz) or (2, Nx)
    n: np.ndarray  # Real array, shape (3, Nx, Ny, Nz) or (3, Nx)
    gauge: Optional[GaugeField] = None
    phase: Optional[np.ndarray] = None
    
    def __str__(self) -> str:
        return f"CP1Configuration(z.shape={self.z.shape}, n.shape={self.n.shape})"


class CP1Quantizer:
    """
    Extracts CP¹ structure and U(1) gauge field from coherence fields.
    
    Implements:
    1. n → z conversion (stereographic projection)
    2. Gauge potential extraction a_μ = i z† ∂_μ z
    3. Field strength computation f_μν = ∂_μ a_ν - ∂_ν a_μ
    4. Electric and magnetic field identification
    5. Flux and charge quantization
    """
    
    def __init__(
        self,
        field: Optional[CoherenceField] = None,
        grid: Optional[GridParameters] = None
    ):
        """
        Initialize CP¹ quantizer.
        
        Args:
            field: Optional CoherenceField
            grid: Optional grid parameters
        """
        self.field = field
        self.grid = grid if grid is not None else (field.grid if field else None)
        
        # Cached computations
        self._cp1_config = None
        self._gauge_field = None
    
    def field_to_spinor(
        self,
        n: np.ndarray,
        gauge_choice: str = 'north'
    ) -> np.ndarray:
        """
        Convert unit vector field n to CP¹ spinor z.
        
        Uses stereographic projection from S² to CP¹.
        
        Args:
            n: Unit vector field (3, Nx, ...) with n² = 1
            gauge_choice: Projection choice ('north' or 'south' pole)
            
        Returns:
            Complex spinor z (2, Nx, ...)
        """
        nx, ny, nz = n[0], n[1], n[2]
        
        # Stereographic projection from north pole
        # z₁ = (n_x + i n_y) / (1 + n_z)
        # z₂ = (1 - n_z) / (1 + n_z) * exp(-iφ)  where φ = atan2(n_y, n_x)
        
        # Simpler parametrization: z₁ = cos(θ/2) e^(iφ), z₂ = sin(θ/2)
        # where θ = acos(n_z), φ = atan2(n_y, n_x)
        
        # Avoid singularities by using numerically stable form
        theta = np.arccos(np.clip(nz, -1, 1))
        phi = np.arctan2(ny, nx)
        
        z1 = np.cos(theta / 2) * np.exp(1j * phi)
        z2 = np.sin(theta / 2)
        
        z = np.array([z1, z2])
        
        # Normalize (should already be normalized if n was normalized)
        norm = np.sqrt(np.abs(z[0])**2 + np.abs(z[1])**2)
        z /= norm
        
        return z
    
    def spinor_to_field(self, z: np.ndarray) -> np.ndarray:
        """
        Convert CP¹ spinor z to unit vector field n.
        
        Uses n = z†σz where σ are Pauli matrices.
        
        Args:
            z: Complex spinor (2, Nx, ...)
            
        Returns:
            Unit vector field n (3, Nx, ...)
        """
        z1, z2 = z[0], z[1]
        
        # Pauli matrices: σ₁ = [[0,1],[1,0]], σ₂ = [[0,-i],[i,0]], σ₃ = [[1,0],[0,-1]]
        # n_x = z†σ₁z = z₁*z₂ + z₂*z₁ = 2 Re(z₁*z₂)
        # n_y = z†σ₂z = i(z₂*z₁ - z₁*z₂) = 2 Im(z₁*z₂)
        # n_z = z†σ₃z = |z₁|² - |z₂|²
        
        nx = 2 * np.real(z1 * np.conj(z2))
        ny = 2 * np.imag(z1 * np.conj(z2))
        nz = np.abs(z1)**2 - np.abs(z2)**2
        
        n = np.array([nx, ny, nz])
        
        return n
    
    def compute_gauge_potential(
        self,
        z: np.ndarray,
        temporal: bool = False
    ) -> np.ndarray:
        """
        Compute gauge potential a_μ = i(z† ∂_μ z - ∂_μ z† z).
        
        Args:
            z: Complex spinor (2, Nx, Ny, Nz) or (2, Nx)
            temporal: If True, include temporal component a_0
            
        Returns:
            Gauge potential a (3,) or (4,) if temporal, shape (..., Nx, Ny, Nz)
        """
        # Compute spatial gradients
        spatial_dims = z.ndim - 1  # Minus 1 for spinor index
        
        a_components = []
        
        if spatial_dims == 1:
            # 1D case
            dz = np.gradient(z, axis=1)
            
            # a_x = i(z† ∂_x z - ∂_x z† z)
            # Since z† ∂_x z is complex, we want the imaginary part × 2
            # a_x = 2 Im(z† ∂_x z)
            a_x = 2 * np.imag(np.sum(np.conj(z) * dz, axis=0))
            
            if self.grid and not self.grid.is_1d:
                a_x /= self.grid.dx
            
            a_components = [a_x]
            
        elif spatial_dims == 3:
            # 3D case
            grad_z = np.array([
                np.gradient(z, axis=1),  # ∂_x z
                np.gradient(z, axis=2),  # ∂_y z
                np.gradient(z, axis=3)   # ∂_z z
            ])  # Shape: (3, 2, Nx, Ny, Nz)
            
            # For each direction μ
            for mu in range(3):
                # a_μ = 2 Im(z† ∂_μ z)
                a_mu = 2 * np.imag(np.sum(np.conj(z) * grad_z[mu], axis=0))
                
                if self.grid:
                    dx = [self.grid.Lx / self.grid.Nx,
                          self.grid.Ly / self.grid.Ny,
                          self.grid.Lz / self.grid.Nz][mu]
                    a_mu /= dx
                
                a_components.append(a_mu)
        
        else:
            raise ValueError(f"Unsupported spatial dimensions: {spatial_dims}")
        
        a = np.array(a_components)
        
        return a
    
    def compute_field_strength(
        self,
        a: np.ndarray
    ) -> np.ndarray:
        """
        Compute field strength tensor f_μν = ∂_μ a_ν - ∂_ν a_μ.
        
        Args:
            a: Gauge potential (3, Nx, Ny, Nz) or (Nx,)
            
        Returns:
            Field strength f (3, 3, Nx, Ny, Nz) antisymmetric in first two indices
        """
        spatial_dims = a.ndim - 1  # Minus 1 for component index
        
        if spatial_dims == 0:
            # 1D case: only one component a_x, no curl
            # f_xy, f_xz, f_yz all undefined
            # Return empty
            return np.zeros((3, 3, len(a[0])))
        
        elif spatial_dims == 3:
            # 3D case
            Nx, Ny, Nz = a.shape[1:]
            f = np.zeros((3, 3, Nx, Ny, Nz))
            
            # Compute gradients of each a component
            # a has shape (3, Nx, Ny, Nz), so axes are (component, x, y, z) = (0, 1, 2, 3)
            # We want ∂_x, ∂_y, ∂_z which correspond to axes 1, 2, 3 (relative to a's indexing)
            # But we need to take gradient of a[i] which is (Nx, Ny, Nz), so axes are 0, 1, 2
            grad_a = []
            for i in range(3):
                grad_a_i = []
                for axis_idx in range(3):  # x, y, z directions
                    grad = np.gradient(a[i], axis=axis_idx)
                    grad_a_i.append(grad)
                grad_a.append(grad_a_i)
            grad_a = np.array(grad_a)  # Shape: (3, 3, Nx, Ny, Nz) where [i, j] = ∂_j a_i
            
            # Apply grid scaling
            if self.grid:
                dx = [self.grid.Lx / self.grid.Nx,
                      self.grid.Ly / self.grid.Ny,
                      self.grid.Lz / self.grid.Nz]
                for i in range(3):
                    for j in range(3):
                        grad_a[i, j] /= dx[j]
            
            # f_μν = ∂_μ a_ν - ∂_ν a_μ
            for mu in range(3):
                for nu in range(3):
                    f[mu, nu] = grad_a[nu, mu] - grad_a[mu, nu]
            
            return f
        
        else:
            raise ValueError(f"Unsupported spatial dimensions: {spatial_dims}")
    
    def extract_electric_magnetic_fields(
        self,
        f: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract electric and magnetic fields from field strength tensor.
        
        Args:
            f: Field strength (3, 3, Nx, Ny, Nz)
            
        Returns:
            Tuple of (E, B) where E_i = f_{0i}, B_i = ½ε_ijk f_jk
        """
        # In purely spatial formulation, we interpret:
        # f_xy as B_z component, f_xz as -B_y, f_yz as B_x
        
        # Magnetic field: B_i = ½ε_ijk f_jk
        # B_x = ½(f_yz - f_zy) = f_yz  (since f antisymmetric)
        # B_y = ½(f_zx - f_xz) = f_zx = -f_xz
        # B_z = ½(f_xy - f_yx) = f_xy
        
        Bx = f[1, 2]  # f_yz
        By = f[2, 0]  # f_zx
        Bz = f[0, 1]  # f_xy
        
        B = np.array([Bx, By, Bz])
        
        # Electric field would need temporal component
        # For now, set to None or zero
        E = None
        
        return E, B
    
    def compute_magnetic_flux(
        self,
        B: np.ndarray,
        surface: Optional[str] = 'xy'
    ) -> float:
        """
        Compute magnetic flux through a surface.
        
        Args:
            B: Magnetic field (3, Nx, Ny, Nz)
            surface: Which plane to integrate over ('xy', 'xz', 'yz')
            
        Returns:
            Total flux Φ = ∫ B · dS
        """
        if surface == 'xy':
            # Integrate B_z over xy plane
            flux_density = B[2]
            if self.grid:
                dx = self.grid.Lx / self.grid.Nx
                dy = self.grid.Ly / self.grid.Ny
                dS = dx * dy
            else:
                dS = 1.0
            
            # Sum over x, y (integrate z)
            flux = np.sum(flux_density) * dS
            
        elif surface == 'xz':
            flux_density = B[1]
            if self.grid:
                dx = self.grid.Lx / self.grid.Nx
                dz = self.grid.Lz / self.grid.Nz
                dS = dx * dz
            else:
                dS = 1.0
            flux = np.sum(flux_density) * dS
            
        elif surface == 'yz':
            flux_density = B[0]
            if self.grid:
                dy = self.grid.Ly / self.grid.Ny
                dz = self.grid.Lz / self.grid.Nz
                dS = dy * dz
            else:
                dS = 1.0
            flux = np.sum(flux_density) * dS
        
        else:
            raise ValueError(f"Unknown surface: {surface}")
        
        return flux
    
    def extract_gauge_field(
        self,
        n: Optional[np.ndarray] = None,
        compute_flux: bool = True
    ) -> GaugeField:
        """
        Extract complete gauge field structure from vector field.
        
        Args:
            n: Unit vector field (3, Nx, ...) or use self.field
            compute_flux: Whether to compute magnetic flux
            
        Returns:
            GaugeField object with all data
        """
        if n is None:
            if self.field is None:
                raise ValueError("No field provided")
            n = self.field.get_field()
        
        # Convert to spinor
        z = self.field_to_spinor(n)
        
        # Compute gauge potential
        a = self.compute_gauge_potential(z)
        
        # Compute field strength
        f = self.compute_field_strength(a)
        
        # Extract E and B
        E, B = self.extract_electric_magnetic_fields(f)
        
        # Compute flux if requested
        flux = None
        charge = None
        if compute_flux and B is not None:
            try:
                flux = self.compute_magnetic_flux(B, surface='xy')
                # Gauge charge from Dirac quantization: Φ = 2πQ
                charge = flux / (2 * np.pi)
            except:
                pass
        
        gauge = GaugeField(
            a=a,
            f=f,
            E=E,
            B=B,
            flux=flux,
            charge=charge
        )
        
        self._gauge_field = gauge
        return gauge
    
    def create_cp1_configuration(
        self,
        n: Optional[np.ndarray] = None
    ) -> CP1Configuration:
        """
        Create full CP¹ configuration from vector field.
        
        Args:
            n: Unit vector field or use self.field
            
        Returns:
            CP1Configuration with spinor, field, and gauge data
        """
        if n is None:
            if self.field is None:
                raise ValueError("No field provided")
            n = self.field.get_field()
        
        # Convert to spinor
        z = self.field_to_spinor(n)
        
        # Reconstruct n (should match original)
        n_reconstructed = self.spinor_to_field(z)
        
        # Extract gauge field
        gauge = self.extract_gauge_field(n)
        
        # Compute global phase
        phase = np.angle(z[0])  # Use phase of z₁
        
        config = CP1Configuration(
            z=z,
            n=n_reconstructed,
            gauge=gauge,
            phase=phase
        )
        
        self._cp1_config = config
        return config
    
    def verify_quantization_condition(
        self,
        flux: float,
        Q_H: float,
        tolerance: float = 0.1
    ) -> bool:
        """
        Verify Dirac quantization condition: Φ = 2πQ_H.
        
        Args:
            flux: Magnetic flux
            Q_H: Hopf invariant
            tolerance: Allowed deviation
            
        Returns:
            True if quantization condition satisfied
        """
        expected_flux = 2 * np.pi * Q_H
        deviation = abs(flux - expected_flux)
        
        return deviation < tolerance * (2 * np.pi)


def extract_gauge_field(
    field_data: np.ndarray,
    grid: Optional[GridParameters] = None
) -> GaugeField:
    """
    Convenience function to extract gauge field from field data.
    
    Args:
        field_data: Unit vector field (3, Nx, Ny, Nz)
        grid: Optional grid parameters
        
    Returns:
        GaugeField object
    """
    quantizer = CP1Quantizer(grid=grid)
    return quantizer.extract_gauge_field(field_data)


if __name__ == "__main__":
    print("CP¹ Quantization - Demonstration")
    print("=" * 50)
    
    # Create simple field configuration
    N = 32
    L = 10.0
    x = np.linspace(-L/2, L/2, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
    
    # Create field with twist (hopf-like)
    R = np.sqrt(X**2 + Y**2 + Z**2) + 1e-10
    theta = np.arctan2(np.sqrt(X**2 + Y**2), Z)
    phi = np.arctan2(Y, X)
    
    # Add twist
    twist = 0.5 * phi
    
    nx = np.sin(theta) * np.cos(phi + twist)
    ny = np.sin(theta) * np.sin(phi + twist)
    nz = np.cos(theta)
    
    # Normalize
    norm = np.sqrt(nx**2 + ny**2 + nz**2)
    nx /= norm
    ny /= norm
    nz /= norm
    
    n = np.array([nx, ny, nz])
    
    print(f"\nField shape: {n.shape}")
    print(f"Grid: {N}³, L = {L}")
    
    # Create quantizer
    quantizer = CP1Quantizer()
    
    # Convert to spinor
    print("\n1. Converting to CP¹ spinor...")
    z = quantizer.field_to_spinor(n)
    print(f"   Spinor shape: {z.shape}")
    print(f"   |z|² = {np.mean(np.abs(z[0])**2 + np.abs(z[1])**2):.6f} (should be 1)")
    
    # Reconstruct field
    print("\n2. Reconstructing vector field...")
    n_reconstructed = quantizer.spinor_to_field(z)
    error = np.max(np.abs(n - n_reconstructed))
    print(f"   Reconstruction error: {error:.6e}")
    
    # Extract gauge field
    print("\n3. Extracting gauge field...")
    gauge = quantizer.extract_gauge_field(n)
    print(f"   {gauge}")
    print(f"   Gauge potential range: [{np.min(gauge.a):.3f}, {np.max(gauge.a):.3f}]")
    print(f"   Field strength range: [{np.min(gauge.f):.3f}, {np.max(gauge.f):.3f}]")
    
    if gauge.B is not None:
        print(f"   |B| max: {np.max(np.sqrt(np.sum(gauge.B**2, axis=0))):.3f}")
    
    if gauge.flux is not None:
        print(f"   Magnetic flux: Φ = {gauge.flux:.4f}")
        print(f"   Gauge charge: Q = {gauge.charge:.4f}")
    
    # Create full CP¹ configuration
    print("\n4. Creating full CP¹ configuration...")
    config = quantizer.create_cp1_configuration(n)
    print(f"   {config}")
    print(f"   Phase range: [{np.min(config.phase):.3f}, {np.max(config.phase):.3f}]")
    
    print("\n" + "=" * 50)
    print("✓ CP¹ quantization complete")

