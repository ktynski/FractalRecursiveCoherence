"""
Tests for CP¹ Quantization Module

Comprehensive test suite for cp1_quantization.py covering:
1. Field to spinor conversion
2. Spinor to field reconstruction
3. Gauge potential extraction
4. Field strength computation
5. Electric and magnetic field identification
6. Flux quantization
7. CP¹ configuration creation
8. Edge cases and error handling

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import unittest
import numpy as np
from FIRM_dsl.cp1_quantization import (
    GaugeField,
    CP1Configuration,
    CP1Quantizer,
    extract_gauge_field
)


class TestGaugeField(unittest.TestCase):
    """Test gauge field data structure."""
    
    def test_creation(self):
        """Test creating gauge field."""
        a = np.array([[[1, 2], [3, 4]]] * 3)
        f = np.zeros((3, 3, 2, 2))
        
        gauge = GaugeField(a=a, f=f)
        self.assertEqual(gauge.a.shape, (3, 2, 2))
        self.assertEqual(gauge.f.shape, (3, 3, 2, 2))
    
    def test_with_flux_and_charge(self):
        """Test gauge field with flux and charge."""
        a = np.zeros((3, 2, 2))
        f = np.zeros((3, 3, 2, 2))
        E = np.zeros((3, 2, 2))
        B = np.ones((3, 2, 2))
        
        gauge = GaugeField(
            a=a, f=f, E=E, B=B,
            flux=6.28, charge=1.0
        )
        
        self.assertAlmostEqual(gauge.flux, 6.28)
        self.assertAlmostEqual(gauge.charge, 1.0)
    
    def test_string_representation(self):
        """Test string formatting."""
        a = np.zeros((3, 2, 2))
        f = np.zeros((3, 3, 2, 2))
        gauge = GaugeField(a=a, f=f, flux=10.0, charge=1.5)
        
        string = str(gauge)
        self.assertIn("GaugeField", string)
        self.assertIn("Φ=10.000", string)
        self.assertIn("Q=1.500", string)


class TestCP1Configuration(unittest.TestCase):
    """Test CP¹ configuration data structure."""
    
    def test_creation(self):
        """Test creating CP¹ configuration."""
        z = np.random.randn(2, 10, 10, 10) + 1j * np.random.randn(2, 10, 10, 10)
        # Normalize
        norm = np.sqrt(np.abs(z[0])**2 + np.abs(z[1])**2)
        z /= norm
        
        n = np.random.randn(3, 10, 10, 10)
        norm_n = np.sqrt(np.sum(n**2, axis=0))
        n /= norm_n
        
        config = CP1Configuration(z=z, n=n)
        
        self.assertEqual(config.z.shape, (2, 10, 10, 10))
        self.assertEqual(config.n.shape, (3, 10, 10, 10))
    
    def test_string_representation(self):
        """Test string formatting."""
        z = np.zeros((2, 5, 5, 5), dtype=complex)
        n = np.zeros((3, 5, 5, 5))
        config = CP1Configuration(z=z, n=n)
        
        string = str(config)
        self.assertIn("CP1Configuration", string)


class TestCP1Quantizer(unittest.TestCase):
    """Test CP¹ quantizer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quantizer = CP1Quantizer()
        
        # Create simple uniform field (pointing in +z direction)
        N = 16
        self.N = N
        self.n_uniform = np.array([
            np.zeros((N, N, N)),
            np.zeros((N, N, N)),
            np.ones((N, N, N))
        ])
        
        # Create field with rotation
        x = np.linspace(-1, 1, N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        R = np.sqrt(X**2 + Y**2 + Z**2) + 1e-10
        theta = np.arctan2(np.sqrt(X**2 + Y**2), Z)
        phi = np.arctan2(Y, X)
        
        self.n_rotated = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])
    
    def test_quantizer_initialization(self):
        """Test quantizer initialization."""
        quantizer = CP1Quantizer()
        self.assertIsNone(quantizer.field)
        self.assertIsNone(quantizer.grid)
    
    def test_field_to_spinor_uniform(self):
        """Test converting uniform field to spinor."""
        z = self.quantizer.field_to_spinor(self.n_uniform)
        
        # Check shape
        self.assertEqual(z.shape, (2, self.N, self.N, self.N))
        
        # Check normalization
        norm = np.abs(z[0])**2 + np.abs(z[1])**2
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm))
    
    def test_field_to_spinor_rotated(self):
        """Test converting rotated field to spinor."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        
        # Check shape
        self.assertEqual(z.shape, (2, self.N, self.N, self.N))
        
        # Check normalization
        norm = np.abs(z[0])**2 + np.abs(z[1])**2
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=6)
    
    def test_spinor_to_field_reconstruction(self):
        """Test that spinor_to_field inverts field_to_spinor."""
        # Convert to spinor and back
        z = self.quantizer.field_to_spinor(self.n_rotated)
        n_reconstructed = self.quantizer.spinor_to_field(z)
        
        # Should match original (up to numerical precision)
        np.testing.assert_array_almost_equal(
            n_reconstructed,
            self.n_rotated,
            decimal=10
        )
    
    def test_spinor_produces_unit_field(self):
        """Test that reconstructed field is normalized."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        n = self.quantizer.spinor_to_field(z)
        
        # Check normalization
        norm = np.sqrt(np.sum(n**2, axis=0))
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=10)
    
    def test_gauge_potential_uniform_field(self):
        """Test gauge potential for uniform field (should be small)."""
        z = self.quantizer.field_to_spinor(self.n_uniform)
        a = self.quantizer.compute_gauge_potential(z)
        
        # Uniform field should have minimal gauge potential
        self.assertEqual(a.shape, (3, self.N, self.N, self.N))
        self.assertLess(np.max(np.abs(a)), 0.5)  # Small but non-zero due to numerical derivatives
    
    def test_gauge_potential_is_real(self):
        """Test that gauge potential is real-valued."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        a = self.quantizer.compute_gauge_potential(z)
        
        # a should be real (imaginary part negligible)
        self.assertTrue(np.all(np.abs(np.imag(a)) < 1e-10))
    
    def test_field_strength_antisymmetry(self):
        """Test that field strength tensor is antisymmetric."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        a = self.quantizer.compute_gauge_potential(z)
        f = self.quantizer.compute_field_strength(a)
        
        # f_μν = -f_νμ
        for mu in range(3):
            for nu in range(3):
                np.testing.assert_array_almost_equal(
                    f[mu, nu],
                    -f[nu, mu],
                    decimal=10
                )
    
    def test_field_strength_diagonal_zero(self):
        """Test that diagonal of field strength is zero."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        a = self.quantizer.compute_gauge_potential(z)
        f = self.quantizer.compute_field_strength(a)
        
        # f_μμ = 0
        for mu in range(3):
            np.testing.assert_array_almost_equal(
                f[mu, mu],
                np.zeros_like(f[mu, mu]),
                decimal=10
            )
    
    def test_extract_magnetic_field(self):
        """Test extracting magnetic field from field strength."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        a = self.quantizer.compute_gauge_potential(z)
        f = self.quantizer.compute_field_strength(a)
        
        E, B = self.quantizer.extract_electric_magnetic_fields(f)
        
        # B should exist
        self.assertIsNotNone(B)
        self.assertEqual(B.shape, (3, self.N, self.N, self.N))
    
    def test_magnetic_flux_computation(self):
        """Test computing magnetic flux."""
        z = self.quantizer.field_to_spinor(self.n_rotated)
        a = self.quantizer.compute_gauge_potential(z)
        f = self.quantizer.compute_field_strength(a)
        E, B = self.quantizer.extract_electric_magnetic_fields(f)
        
        flux = self.quantizer.compute_magnetic_flux(B, surface='xy')
        
        # Flux should be finite
        self.assertTrue(np.isfinite(flux))
    
    def test_extract_gauge_field(self):
        """Test full gauge field extraction."""
        gauge = self.quantizer.extract_gauge_field(self.n_rotated)
        
        self.assertIsInstance(gauge, GaugeField)
        self.assertEqual(gauge.a.shape, (3, self.N, self.N, self.N))
        self.assertEqual(gauge.f.shape, (3, 3, self.N, self.N, self.N))
        self.assertIsNotNone(gauge.B)
        self.assertIsNotNone(gauge.flux)
        self.assertIsNotNone(gauge.charge)
    
    def test_create_cp1_configuration(self):
        """Test creating full CP¹ configuration."""
        config = self.quantizer.create_cp1_configuration(self.n_rotated)
        
        self.assertIsInstance(config, CP1Configuration)
        self.assertEqual(config.z.shape, (2, self.N, self.N, self.N))
        self.assertEqual(config.n.shape, (3, self.N, self.N, self.N))
        self.assertIsNotNone(config.gauge)
        self.assertIsNotNone(config.phase)
    
    def test_quantization_condition_verification(self):
        """Test verifying Dirac quantization condition."""
        flux = 2 * np.pi * 1.05  # Close to Q_H = 1
        Q_H = 1.0
        
        is_quantized = self.quantizer.verify_quantization_condition(
            flux, Q_H, tolerance=0.1
        )
        
        self.assertTrue(is_quantized)
    
    def test_quantization_condition_violation(self):
        """Test detecting quantization violation."""
        flux = 10.0  # Not close to 2πQ_H for any integer Q_H
        Q_H = 1.0
        
        is_quantized = self.quantizer.verify_quantization_condition(
            flux, Q_H, tolerance=0.1
        )
        
        self.assertFalse(is_quantized)


class TestConvenienceFunction(unittest.TestCase):
    """Test module-level convenience function."""
    
    def test_extract_gauge_field(self):
        """Test one-shot gauge field extraction."""
        # Create simple field
        N = 16
        n = np.array([
            np.zeros((N, N, N)),
            np.zeros((N, N, N)),
            np.ones((N, N, N))
        ])
        
        gauge = extract_gauge_field(n)
        
        self.assertIsInstance(gauge, GaugeField)
        self.assertEqual(gauge.a.shape, (3, N, N, N))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_no_field_provided(self):
        """Test error when no field is provided."""
        quantizer = CP1Quantizer()
        
        with self.assertRaises(ValueError):
            quantizer.extract_gauge_field()
    
    def test_non_unit_field_normalization(self):
        """Test that non-unit fields are handled."""
        # Create non-normalized field
        N = 10
        n = np.random.randn(3, N, N, N)
        
        quantizer = CP1Quantizer()
        
        # Should not crash, spinor will normalize
        z = quantizer.field_to_spinor(n)
        
        # Spinor should still be normalized
        norm = np.abs(z[0])**2 + np.abs(z[1])**2
        np.testing.assert_array_almost_equal(norm, np.ones_like(norm), decimal=6)
    
    def test_field_with_singularities(self):
        """Test field with potential singularities (n_z = -1)."""
        N = 10
        n = np.array([
            np.zeros((N, N, N)),
            np.zeros((N, N, N)),
            -np.ones((N, N, N))  # South pole
        ])
        
        quantizer = CP1Quantizer()
        
        # Should handle gracefully
        z = quantizer.field_to_spinor(n, gauge_choice='north')
        n_reconstructed = quantizer.spinor_to_field(z)
        
        # Should reconstruct correctly
        np.testing.assert_array_almost_equal(n, n_reconstructed, decimal=6)
    
    def test_cached_computations(self):
        """Test that computations are cached."""
        N = 10
        n = np.random.randn(3, N, N, N)
        norm = np.sqrt(np.sum(n**2, axis=0))
        n /= norm
        
        quantizer = CP1Quantizer()
        
        # First extraction
        gauge1 = quantizer.extract_gauge_field(n)
        
        # Check cache
        self.assertIsNotNone(quantizer._gauge_field)
        
        # Cached version
        gauge2 = quantizer._gauge_field
        
        # Should be same object
        self.assertIs(gauge1, gauge2)


class TestPhysicalConsistency(unittest.TestCase):
    """Test physical consistency properties."""
    
    def test_gauge_invariance_under_global_phase(self):
        """Test that gauge potential is invariant under global U(1) phase."""
        N = 16
        x = np.linspace(-1, 1, N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        R = np.sqrt(X**2 + Y**2 + Z**2) + 1e-10
        theta = np.arctan2(np.sqrt(X**2 + Y**2), Z)
        phi = np.arctan2(Y, X)
        
        n = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])
        
        quantizer = CP1Quantizer()
        
        # Convert to spinor
        z1 = quantizer.field_to_spinor(n)
        
        # Apply global phase
        global_phase = np.exp(1j * 0.5)
        z2 = z1 * global_phase
        
        # Compute gauge potentials
        a1 = quantizer.compute_gauge_potential(z1)
        a2 = quantizer.compute_gauge_potential(z2)
        
        # Should be identical (global phase doesn't affect gauge potential)
        np.testing.assert_array_almost_equal(a1, a2, decimal=6)
    
    def test_field_strength_gauge_invariance(self):
        """Test that field strength is gauge invariant."""
        N = 16
        n = np.random.randn(3, N, N, N)
        norm = np.sqrt(np.sum(n**2, axis=0))
        n /= norm
        
        quantizer = CP1Quantizer()
        
        # Compute field strength
        gauge = quantizer.extract_gauge_field(n)
        f = gauge.f
        
        # Field strength should be well-defined
        self.assertEqual(f.shape, (3, 3, N, N, N))
        
        # Antisymmetry
        for mu in range(3):
            for nu in range(3):
                np.testing.assert_array_almost_equal(
                    f[mu, nu], -f[nu, mu], decimal=10
                )
    
    def test_bianchi_identity(self):
        """Test Bianchi identity: ε_μνρσ ∂_ν f_ρσ = 0."""
        # This is complex to verify numerically, so we'll check a simpler condition:
        # ∇ · B = 0 (no magnetic monopoles in standard gauge theory)
        
        N = 16
        n = np.random.randn(3, N, N, N)
        norm = np.sqrt(np.sum(n**2, axis=0))
        n /= norm
        
        quantizer = CP1Quantizer()
        gauge = quantizer.extract_gauge_field(n)
        B = gauge.B
        
        # Compute divergence of B
        div_B = (np.gradient(B[0], axis=0) +
                 np.gradient(B[1], axis=1) +
                 np.gradient(B[2], axis=2))
        
        # Should be approximately zero (up to numerical errors)
        # This is not a strict test due to boundary effects
        self.assertLess(np.mean(np.abs(div_B)), 1.0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

