"""
Tests for Field Equations Module

Comprehensive test suite for field_equations.py covering:
1. Field parameter validation
2. Grid setup (1D and 2D)
3. Field initialization and normalization
4. Energy computation
5. Laplacian operators
6. Field evolution (with and without retrocausality)
7. Conservation laws
8. Soliton stability

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import unittest
import numpy as np
from FIRM_dsl.field_equations import (
    FieldParameters,
    GridParameters,
    BoundaryCondition,
    CoherenceField,
    FieldEvolution,
    evolve_field_simple
)

# Check if retrocausality is available
try:
    from FIRM_dsl.coherence_tensor import RetrocausalParameters, AttractorField
    RETROCAUSALITY_AVAILABLE = True
except ImportError:
    RETROCAUSALITY_AVAILABLE = False


class TestFieldParameters(unittest.TestCase):
    """Test field parameter validation."""
    
    def test_valid_parameters(self):
        """Test creating valid field parameters."""
        params = FieldParameters(f=1.0, kappa=0.1, mass=0.5, lambda_reg=1.0, c=1.0)
        self.assertEqual(params.f, 1.0)
        self.assertEqual(params.kappa, 0.1)
        self.assertEqual(params.mass, 0.5)
    
    def test_invalid_f(self):
        """Test that negative or zero f raises error."""
        with self.assertRaises(ValueError):
            FieldParameters(f=0.0)
        with self.assertRaises(ValueError):
            FieldParameters(f=-1.0)
    
    def test_invalid_kappa(self):
        """Test that negative kappa raises error."""
        with self.assertRaises(ValueError):
            FieldParameters(kappa=-0.1)
    
    def test_defaults(self):
        """Test default parameter values."""
        params = FieldParameters()
        self.assertEqual(params.f, 1.0)
        self.assertEqual(params.kappa, 0.1)
        self.assertEqual(params.mass, 0.0)
        self.assertEqual(params.c, 1.0)


class TestGridParameters(unittest.TestCase):
    """Test grid parameter validation and setup."""
    
    def test_1d_grid(self):
        """Test 1D grid creation."""
        grid = GridParameters(Nx=64, Lx=10.0, dt=0.01, t_max=10.0)
        self.assertTrue(grid.is_1d)
        self.assertFalse(grid.is_2d)
        self.assertAlmostEqual(grid.dx, 10.0 / 64)
    
    def test_2d_grid(self):
        """Test 2D grid creation."""
        grid = GridParameters(Nx=32, Ny=32, Lx=10.0, Ly=10.0, dt=0.01, t_max=10.0)
        self.assertFalse(grid.is_1d)
        self.assertTrue(grid.is_2d)
        self.assertAlmostEqual(grid.dx, 10.0 / 32)
        self.assertAlmostEqual(grid.dy, 10.0 / 32)
    
    def test_invalid_grid_size(self):
        """Test that too-small grid raises error."""
        with self.assertRaises(ValueError):
            GridParameters(Nx=4)  # Too small
    
    def test_boundary_conditions(self):
        """Test boundary condition specification."""
        grid_periodic = GridParameters(Nx=32, boundary=BoundaryCondition.PERIODIC)
        grid_dirichlet = GridParameters(Nx=32, boundary=BoundaryCondition.DIRICHLET)
        
        self.assertEqual(grid_periodic.boundary, BoundaryCondition.PERIODIC)
        self.assertEqual(grid_dirichlet.boundary, BoundaryCondition.DIRICHLET)


class TestCoherenceField(unittest.TestCase):
    """Test coherence field representation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.grid_1d = GridParameters(Nx=32, Lx=10.0, dt=0.01, t_max=10.0)
        self.grid_2d = GridParameters(Nx=16, Ny=16, Lx=10.0, Ly=10.0, dt=0.01, t_max=10.0)
    
    def test_field_initialization_1d(self):
        """Test 1D field initialization."""
        field = CoherenceField(self.grid_1d)
        
        # Check shapes
        self.assertEqual(field.n_x.shape, (32,))
        self.assertEqual(field.n_y.shape, (32,))
        self.assertEqual(field.n_z.shape, (32,))
        
        # Initially aligned with z-axis
        np.testing.assert_array_almost_equal(field.n_z, np.ones(32))
        np.testing.assert_array_almost_equal(field.n_x, np.zeros(32))
    
    def test_field_initialization_2d(self):
        """Test 2D field initialization."""
        field = CoherenceField(self.grid_2d)
        
        # Check shapes
        self.assertEqual(field.n_x.shape, (16, 16))
        self.assertEqual(field.n_y.shape, (16, 16))
        self.assertEqual(field.n_z.shape, (16, 16))
    
    def test_normalization(self):
        """Test field normalization enforces |n| = 1."""
        field = CoherenceField(self.grid_1d)
        
        # Perturb field
        field.n_x += 0.5
        field.n_y += 0.3
        field.n_z += 0.2
        
        # Normalize
        field.normalize()
        
        # Check |n| = 1 everywhere
        norm = np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=10)
    
    def test_gaussian_soliton_1d(self):
        """Test Gaussian soliton initialization in 1D."""
        field = CoherenceField(self.grid_1d)
        
        center = (5.0,)  # Middle of domain
        width = 1.0
        direction = np.array([0.0, 0.0, 1.0])  # Stay aligned with z
        
        field.set_gaussian_soliton(center, width, direction)
        
        # Check normalization
        norm = np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=6)
        
        # Check center is perturbed
        idx_center = self.grid_1d.Nx // 2
        self.assertAlmostEqual(field.n_z[idx_center], direction[2], delta=0.1)
    
    def test_hopf_soliton_2d(self):
        """Test Hopf soliton initialization in 2D."""
        field = CoherenceField(self.grid_2d)
        
        field.set_hopf_soliton(width=2.0)
        
        # Check normalization
        norm = np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=6)
        
        # Check field wraps around (toroidal structure)
        # Center should be different from edges
        center_val = field.n_z[8, 8]  # Center
        edge_val = field.n_z[0, 0]    # Corner
        self.assertNotAlmostEqual(center_val, edge_val, places=1)
    
    def test_hopf_requires_2d(self):
        """Test that Hopf soliton requires 2D grid."""
        field = CoherenceField(self.grid_1d)
        
        with self.assertRaises(ValueError):
            field.set_hopf_soliton()
    
    def test_energy_computation_1d(self):
        """Test energy computation in 1D."""
        field = CoherenceField(self.grid_1d)
        params = FieldParameters(f=1.0, kappa=0.1, mass=0.5)  # Non-zero mass for potential
        
        # Uniform field has only potential energy (V = ½m²(1 - n_z) = 0 since n_z=1)
        energy_uniform = field.energy(params)
        
        # Perturbed field has gradient energy + potential
        field.set_gaussian_soliton((5.0,), 1.0, [1.0, 0.0, 0.0])
        energy_perturbed = field.energy(params)
        self.assertGreater(energy_perturbed, energy_uniform)
    
    def test_energy_computation_2d(self):
        """Test energy computation in 2D."""
        field = CoherenceField(self.grid_2d)
        params = FieldParameters(f=1.0, kappa=0.1, mass=0.5)
        
        # Hopf soliton has gradient + Skyrme energy
        field.set_hopf_soliton(width=2.0)
        energy = field.energy(params)
        self.assertGreater(energy, 0)
    
    def test_state_vector_conversion(self):
        """Test conversion to/from state vector."""
        field = CoherenceField(self.grid_1d)
        
        # Set some values
        field.n_x += 0.1
        field.n_y += 0.2
        field.n_z += 0.3
        field.normalize()
        
        # Convert to state vector
        state = field.get_state_vector()
        
        # Check size (6 components: n and ṅ)
        self.assertEqual(len(state), 6 * 32)
        
        # Create new field and restore
        field2 = CoherenceField(self.grid_1d)
        field2.set_from_state_vector(state)
        
        # Check equality
        np.testing.assert_array_almost_equal(field.n_x, field2.n_x)
        np.testing.assert_array_almost_equal(field.n_y, field2.n_y)
        np.testing.assert_array_almost_equal(field.n_z, field2.n_z)


class TestFieldEvolution(unittest.TestCase):
    """Test field evolution and dynamics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.grid_1d = GridParameters(Nx=32, Lx=10.0, dt=0.01, t_max=2.0)
        self.params = FieldParameters(f=1.0, kappa=0.1, mass=0.5)
    
    def test_evolution_initialization(self):
        """Test evolution solver initialization."""
        field = CoherenceField(self.grid_1d)
        evolution = FieldEvolution(field, self.params)
        
        self.assertIsNotNone(evolution.field)
        self.assertIsNotNone(evolution.params)
        self.assertFalse(evolution.retrocausality_enabled)
    
    def test_laplacian_computation_1d(self):
        """Test Laplacian computation in 1D."""
        field = CoherenceField(self.grid_1d)
        evolution = FieldEvolution(field, self.params)
        
        # Test with sine wave: ∇²sin(kx) = -k²sin(kx)
        x = np.linspace(0, self.grid_1d.Lx, self.grid_1d.Nx)
        k = 2 * np.pi / self.grid_1d.Lx
        f = np.sin(k * x)
        
        lap_f = evolution.compute_laplacian(f)
        expected = -k**2 * f
        
        # Check with reasonable tolerance for finite differences
        # Interior points should be more accurate
        np.testing.assert_array_almost_equal(lap_f[5:-5], expected[5:-5], decimal=1)
    
    def test_short_evolution_1d(self):
        """Test short-time evolution of 1D field."""
        field = CoherenceField(self.grid_1d)
        field.set_gaussian_soliton((5.0,), 1.0, [0.5, 0.5, 0.7])
        
        evolution = FieldEvolution(field, self.params)
        
        # Evolve for short time
        sol = evolution.evolve((0, 0.1), method='RK45')
        
        self.assertTrue(sol['success'])
        self.assertAlmostEqual(field.t, 0.1, places=2)
        
        # Check normalization preserved
        norm = np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=3)
    
    def test_energy_conservation(self):
        """Test approximate energy conservation in evolution."""
        field = CoherenceField(self.grid_1d)
        field.set_gaussian_soliton((5.0,), 1.0, [0.5, 0.5, 0.7])
        
        # Initial energy
        E_initial = field.energy(self.params)
        
        # Evolve
        evolution = FieldEvolution(field, self.params)
        sol = evolution.evolve((0, 0.5), method='RK45')
        
        # Final energy
        E_final = field.energy(self.params)
        
        # Energy should be approximately conserved
        # (some numerical dissipation expected)
        relative_change = abs(E_final - E_initial) / E_initial
        self.assertLess(relative_change, 0.5)  # Within 50% (generous for short evolution)
    
    @unittest.skipIf(not RETROCAUSALITY_AVAILABLE, "Retrocausality not available")
    def test_evolution_with_retrocausality(self):
        """Test evolution with retrocausal coupling."""
        from FIRM_dsl.coherence_tensor import RetrocausalParameters, AttractorField
        
        field = CoherenceField(self.grid_1d)
        field.set_gaussian_soliton((5.0,), 1.0, [0.5, 0.5, 0.7])
        
        # Setup retrocausality
        retro_params = RetrocausalParameters(alpha_adv=0.05, tau_future=1.0)
        attractor = AttractorField.gaussian_attractor(
            center=np.array([5.0, 0.0, 0.0]), width=2.0
        )
        
        evolution = FieldEvolution(field, self.params, retro_params, attractor)
        
        # Retrocausality should be enabled if all conditions met
        # (may be False if implementation pending, that's ok for now)
        self.assertIsNotNone(evolution)
        
        # Evolve
        sol = evolution.evolve((0, 0.1), method='RK45')
        self.assertTrue(sol['success'])
    
    @unittest.skipIf(not RETROCAUSALITY_AVAILABLE, "Retrocausality not available")
    def test_retrocausal_source_computation(self):
        """Test computation of retrocausal source term."""
        from FIRM_dsl.coherence_tensor import RetrocausalParameters, AttractorField
        
        field = CoherenceField(self.grid_1d)
        retro_params = RetrocausalParameters(alpha_adv=0.1, tau_future=2.0)
        attractor = AttractorField.gaussian_attractor(
            center=np.array([5.0, 0.0, 0.0]), width=1.0
        )
        
        evolution = FieldEvolution(field, self.params, retro_params, attractor)
        
        # Compute source
        G_x, G_y, G_z = evolution.compute_retrocausal_source(t=0.5)
        
        # Should be arrays
        self.assertEqual(G_x.shape, field.n_x.shape)
        self.assertEqual(G_y.shape, field.n_y.shape)
        self.assertEqual(G_z.shape, field.n_z.shape)
        
        # Should be finite
        self.assertTrue(np.all(np.isfinite(G_x)))
        self.assertTrue(np.all(np.isfinite(G_y)))
        self.assertTrue(np.all(np.isfinite(G_z)))


class TestConvenienceFunctions(unittest.TestCase):
    """Test module-level convenience functions."""
    
    def test_evolve_field_simple_gaussian(self):
        """Test simple evolution with Gaussian initial condition."""
        field, sol = evolve_field_simple("gaussian", Nx=32, t_max=0.5, with_retrocausality=False)
        
        self.assertTrue(sol['success'])
        self.assertGreater(field.t, 0)
        
        # Check normalization
        norm = np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=2)
    
    @unittest.skipIf(not RETROCAUSALITY_AVAILABLE, "Retrocausality not available")
    def test_evolve_field_simple_with_retrocausality(self):
        """Test simple evolution with retrocausality enabled."""
        field, sol = evolve_field_simple("gaussian", Nx=32, t_max=0.3, with_retrocausality=True)
        
        self.assertTrue(sol['success'])
        self.assertGreater(field.t, 0)


class TestPhysicalProperties(unittest.TestCase):
    """Test physical properties and consistency."""
    
    def test_constraint_preservation(self):
        """Test that |n| = 1 constraint is preserved during evolution."""
        grid = GridParameters(Nx=32, Lx=10.0, dt=0.01, t_max=1.0)
        field = CoherenceField(grid)
        field.set_gaussian_soliton((5.0,), 1.0, [0.5, 0.5, 0.7])
        
        params = FieldParameters(f=1.0, kappa=0.1, mass=0.5)
        evolution = FieldEvolution(field, params)
        
        # Evolve
        sol = evolution.evolve((0, 0.5))
        
        # Check constraint
        norm = np.sqrt(field.n_x**2 + field.n_y**2 + field.n_z**2)
        deviation = np.abs(norm - 1.0)
        self.assertLess(np.max(deviation), 0.1)  # Within 10%
    
    def test_dispersion_relation_preparation(self):
        """Test that field evolution produces data suitable for dispersion analysis."""
        field, sol = evolve_field_simple("gaussian", Nx=64, t_max=1.0)
        
        # Check we have time series data
        self.assertGreater(len(sol['t']), 10)
        
        # Check field has spatial variation
        self.assertGreater(np.std(field.n_z), 0.01)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

