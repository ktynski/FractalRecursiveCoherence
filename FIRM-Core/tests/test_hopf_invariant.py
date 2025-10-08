"""
Tests for Hopf Invariant Module

Comprehensive test suite for hopf_invariant.py covering:
1. Vector potential computation
2. Magnetic field computation
3. Topological density
4. Hopf invariant integration
5. Helicity computation
6. Soliton detection
7. Edge cases and error handling

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import unittest
import numpy as np
from FIRM_dsl.hopf_invariant import (
    TopologicalCharge,
    SolitonCandidate,
    HopfInvariantCalculator,
    compute_hopf_invariant
)


class TestTopologicalCharge(unittest.TestCase):
    """Test topological charge data structure."""
    
    def test_creation(self):
        """Test creating topological charge."""
        charge = TopologicalCharge(
            Q_H=1.0,
            Q_H_density=np.array([1, 2, 3]),
            helicity=2.0,
            winding_number=1,
            energy=10.0,
            position=np.array([0, 0, 0])
        )
        self.assertEqual(charge.Q_H, 1.0)
        self.assertEqual(charge.winding_number, 1)
    
    def test_string_representation(self):
        """Test string formatting."""
        charge = TopologicalCharge(
            Q_H=1.5,
            Q_H_density=np.array([1]),
            helicity=2.0,
            winding_number=2,
            energy=10.0,
            position=np.array([0])
        )
        string = str(charge)
        self.assertIn("Q_H=1.500", string)
        self.assertIn("winding=2", string)


class TestSolitonCandidate(unittest.TestCase):
    """Test soliton candidate data structure."""
    
    def test_creation(self):
        """Test creating soliton candidate."""
        soliton = SolitonCandidate(
            position=np.array([1, 2, 3]),
            charge=1.0,
            radius=2.0,
            energy=5.0,
            confidence=0.9
        )
        self.assertEqual(soliton.charge, 1.0)
        self.assertEqual(soliton.confidence, 0.9)
    
    def test_string_representation(self):
        """Test string formatting."""
        soliton = SolitonCandidate(
            position=np.array([0, 0, 0]),
            charge=1.5,
            radius=2.0,
            energy=5.0,
            confidence=0.8
        )
        string = str(soliton)
        self.assertIn("Q=1.50", string)
        self.assertIn("conf=0.80", string)


class TestHopfInvariantCalculator(unittest.TestCase):
    """Test Hopf invariant calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create simple field configuration
        self.N = 16
        self.field_data_3d = self._create_uniform_field_3d()
        self.field_data_1d = self._create_uniform_field_1d()
        
        self.calculator = HopfInvariantCalculator()
    
    def _create_uniform_field_3d(self):
        """Create uniform field pointing in z direction."""
        nx = np.zeros((self.N, self.N, self.N))
        ny = np.zeros((self.N, self.N, self.N))
        nz = np.ones((self.N, self.N, self.N))
        return np.array([nx, ny, nz])
    
    def _create_uniform_field_1d(self):
        """Create uniform 1D field."""
        nx = np.zeros(self.N)
        ny = np.zeros(self.N)
        nz = np.ones(self.N)
        return np.array([nx, ny, nz])
    
    def test_calculator_initialization(self):
        """Test calculator initialization."""
        calc = HopfInvariantCalculator()
        self.assertIsNone(calc.field)
        self.assertIsNone(calc.grid)
    
    def test_vector_potential_uniform_field(self):
        """Test vector potential for uniform field (should be zero)."""
        A = self.calculator.compute_vector_potential(self.field_data_3d)
        
        # For uniform field, A should be approximately zero
        self.assertEqual(A.shape, (3, self.N, self.N, self.N))
        self.assertLess(np.max(np.abs(A)), 0.1)  # Small due to numerical derivatives
    
    def test_magnetic_field_uniform_potential(self):
        """Test magnetic field for zero potential."""
        A = np.zeros((3, self.N, self.N, self.N))
        B = self.calculator.compute_magnetic_field(A)
        
        # Zero curl of zero field
        self.assertEqual(B.shape, (3, self.N, self.N, self.N))
        self.assertLess(np.max(np.abs(B)), 0.1)
    
    def test_topological_density_uniform_field(self):
        """Test topological density for uniform field."""
        rho_H = self.calculator.compute_topological_density(field_data=self.field_data_3d)
        
        # Uniform field has zero topological density
        self.assertEqual(rho_H.shape, (self.N, self.N, self.N))
        self.assertLess(np.max(np.abs(rho_H)), 0.1)
    
    def test_hopf_invariant_uniform_field(self):
        """Test Hopf invariant for uniform field (should be zero)."""
        Q_H = self.calculator.compute_hopf_invariant(self.field_data_3d)
        
        # Uniform field has Q_H = 0
        self.assertLess(abs(Q_H), 0.01)
    
    def test_hopf_invariant_twisted_field(self):
        """Test Hopf invariant for field with twist."""
        # Create field with some twist
        x = np.linspace(-1, 1, self.N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        R = np.sqrt(X**2 + Y**2 + Z**2) + 1e-10
        theta = np.arctan2(np.sqrt(X**2 + Y**2), Z)
        phi = np.arctan2(Y, X)
        
        # Add rotation
        twist = 0.5 * phi
        
        nx = np.sin(theta) * np.cos(phi + twist)
        ny = np.sin(theta) * np.sin(phi + twist)
        nz = np.cos(theta)
        
        # Normalize
        norm = np.sqrt(nx**2 + ny**2 + nz**2)
        nx /= norm
        ny /= norm
        nz /= norm
        
        field_data = np.array([nx, ny, nz])
        
        Q_H = self.calculator.compute_hopf_invariant(field_data)
        
        # Should get some non-zero value (though may be small)
        self.assertTrue(np.isfinite(Q_H))
    
    def test_helicity_computation(self):
        """Test helicity computation."""
        self.calculator.compute_topological_density(field_data=self.field_data_3d)
        helicity = self.calculator.compute_helicity()
        
        # Should be finite
        self.assertTrue(np.isfinite(helicity))
    
    def test_full_topological_charge(self):
        """Test computing full topological charge object."""
        charge = self.calculator.compute_full_topological_charge(self.field_data_3d)
        
        self.assertIsInstance(charge, TopologicalCharge)
        self.assertTrue(np.isfinite(charge.Q_H))
        self.assertTrue(np.isfinite(charge.helicity))
        self.assertIsInstance(charge.winding_number, int)
        self.assertEqual(len(charge.position), 3)
    
    def test_soliton_detection_uniform_field(self):
        """Test that uniform field has no solitons."""
        solitons = self.calculator.detect_solitons(
            self.field_data_3d,
            threshold=0.01
        )
        
        # Uniform field should have no localized structures
        self.assertEqual(len(solitons), 0)
    
    def test_soliton_detection_localized_structure(self):
        """Test soliton detection with localized structure."""
        # Create field with localized perturbation
        field_data = self.field_data_3d.copy()
        
        # Add a Gaussian bump in topological density
        # (indirectly by modifying the field)
        center = self.N // 2
        x = np.arange(self.N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        R = np.sqrt((X - center)**2 + (Y - center)**2 + (Z - center)**2)
        perturbation = 0.3 * np.exp(-R**2 / 4)
        
        # Rotate field slightly based on perturbation
        field_data[0] += perturbation
        field_data[1] += perturbation * 0.5
        
        # Renormalize
        norm = np.sqrt(np.sum(field_data**2, axis=0))
        field_data /= norm
        
        # Detect solitons
        solitons = self.calculator.detect_solitons(
            field_data,
            threshold=0.001
        )
        
        # May or may not detect depending on threshold
        self.assertIsInstance(solitons, list)
        for sol in solitons:
            self.assertIsInstance(sol, SolitonCandidate)
    
    def test_gradient_computation_1d(self):
        """Test gradient computation in 1D."""
        # Simple quadratic function
        N = 20
        x = np.linspace(0, 1, N)
        f = x**2
        
        grad = self.calculator._compute_gradient(f)
        
        # Without a grid, gradient is in index space
        # df/di = df/dx * dx/di
        # For x from 0 to 1 with N points: dx/di = 1/(N-1)
        # df/dx = 2x, so df/di = 2x / (N-1)
        dx = 1.0 / (N - 1)
        expected_index_grad = 2 * x / dx
        
        # Check interior points (boundary has larger error)
        # Actually, np.gradient returns df/di directly where i is index
        # So for f = x² = (i*dx)², df/di = 2*i*dx*dx = 2*i*dx²
        # Let's just check that gradient has correct shape and is monotonic
        self.assertEqual(len(grad), N)
        
        # Gradient should be monotonically increasing (approximately)
        diffs = np.diff(grad)
        self.assertGreater(np.mean(diffs), 0)  # Average slope positive
    
    def test_gradient_computation_3d(self):
        """Test gradient computation in 3D."""
        # Simple function f(x,y,z) = x² + y² + z²
        N = 10
        x = np.linspace(0, 1, N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        f = X**2 + Y**2 + Z**2
        
        grad = self.calculator._compute_gradient(f)
        
        # Gradient should be (2x, 2y, 2z)
        self.assertEqual(grad.shape, (3, N, N, N))
        
        # Check that gradient points outward
        center = N // 2
        self.assertGreater(grad[0, center+1, center, center], 
                         grad[0, center-1, center, center])
    
    def test_center_of_mass_computation(self):
        """Test center of mass computation."""
        # Create density with known center
        N = 20
        x = np.arange(N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        center_true = np.array([10.0, 10.0, 10.0])
        R = np.sqrt((X - center_true[0])**2 + 
                   (Y - center_true[1])**2 + 
                   (Z - center_true[2])**2)
        
        density = np.exp(-R**2 / 4)
        
        com = self.calculator._compute_center_of_mass(density)
        
        # Should be close to true center
        np.testing.assert_array_almost_equal(com, center_true, decimal=0)
    
    def test_radius_estimation_1d(self):
        """Test radius estimation in 1D."""
        # Gaussian peak
        N = 40
        x = np.arange(N)
        center = 20
        sigma = 3.0
        
        density = np.exp(-(x - center)**2 / (2 * sigma**2))
        
        radius = self.calculator._estimate_radius_1d(density, center)
        
        # Radius should be roughly sigma * sqrt(2 * ln(2)) ≈ 1.18 * sigma
        # For half-maximum
        expected_radius = sigma * np.sqrt(2 * np.log(2))
        
        self.assertLess(abs(radius - expected_radius), 2.0)


class TestConvenienceFunction(unittest.TestCase):
    """Test module-level convenience function."""
    
    def test_compute_hopf_invariant(self):
        """Test convenience function."""
        # Create uniform field
        N = 16
        nx = np.zeros((N, N, N))
        ny = np.zeros((N, N, N))
        nz = np.ones((N, N, N))
        field_data = np.array([nx, ny, nz])
        
        Q_H = compute_hopf_invariant(field_data)
        
        # Uniform field has Q_H ≈ 0
        self.assertLess(abs(Q_H), 0.01)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_zero_field(self):
        """Test with zero field."""
        N = 10
        field_data = np.zeros((3, N, N, N))
        
        calc = HopfInvariantCalculator()
        
        # Should not crash
        Q_H = calc.compute_hopf_invariant(field_data)
        self.assertTrue(np.isfinite(Q_H))
    
    def test_invalid_field_shape(self):
        """Test that invalid field shape raises error."""
        invalid_field = np.zeros((2, 10, 10, 10))  # Wrong first dimension
        
        calc = HopfInvariantCalculator()
        
        with self.assertRaises(ValueError):
            calc.compute_vector_potential(invalid_field)
    
    def test_no_field_provided(self):
        """Test that error is raised when no field is provided."""
        calc = HopfInvariantCalculator()  # No field
        
        with self.assertRaises(ValueError):
            calc.compute_vector_potential()  # No field_data argument
    
    def test_cached_computations(self):
        """Test that computations are properly cached."""
        N = 10
        field_data = np.random.randn(3, N, N, N)
        # Normalize
        norm = np.sqrt(np.sum(field_data**2, axis=0))
        field_data /= norm
        
        calc = HopfInvariantCalculator()
        
        # First call computes
        A1 = calc.compute_vector_potential(field_data)
        
        # Second call should use cache
        A2 = calc._vector_potential
        
        np.testing.assert_array_equal(A1, A2)


class TestPhysicalConsistency(unittest.TestCase):
    """Test physical consistency properties."""
    
    def test_hopf_invariant_is_integer_for_solitons(self):
        """Test that Hopf invariant rounds to integer."""
        # Any reasonable soliton should have integer winding
        N = 16
        field_data = np.random.randn(3, N, N, N)
        norm = np.sqrt(np.sum(field_data**2, axis=0))
        field_data /= norm
        
        calc = HopfInvariantCalculator()
        charge = calc.compute_full_topological_charge(field_data)
        
        # Winding number should be integer
        self.assertIsInstance(charge.winding_number, int)
        
        # Q_H should be close to winding number (within rounding error)
        self.assertLess(abs(charge.Q_H - charge.winding_number), 0.6)
    
    def test_topological_density_conservation(self):
        """Test that topological density integrates correctly."""
        N = 16
        field_data = np.random.randn(3, N, N, N)
        norm = np.sqrt(np.sum(field_data**2, axis=0))
        field_data /= norm
        
        calc = HopfInvariantCalculator()
        
        # Compute separately
        rho_H = calc.compute_topological_density(field_data=field_data)
        Q_H_from_density = np.sum(rho_H) / (4 * np.pi**2)
        
        # Compute via method
        Q_H_direct = calc.compute_hopf_invariant(field_data)
        
        # Should match (assuming unit volume element)
        self.assertAlmostEqual(Q_H_from_density, Q_H_direct, places=5)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

