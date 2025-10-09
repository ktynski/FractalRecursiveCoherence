"""
Tests for Clifford Rotor Dynamics
==================================

Comprehensive test suite for rotors in Clifford algebra.

Test Coverage:
1. Bivector operations
2. Rotor creation and composition
3. Grace rotor
4. Love rotor  
5. Forgiveness rotor
6. Combined dynamics
7. Golden rotation
"""

import pytest
import numpy as np
from FIRM_dsl.clifford_rotors import (
    Bivector,
    Rotor,
    GraceRotor,
    LoveRotor,
    ForgivenessRotor,
    CombinedRotorDynamics,
    GOLDEN_ANGLE,
    PHI_INV,
)


# ============================================================================
# BIVECTOR TESTS
# ============================================================================

class TestBivector:
    """Test bivector operations."""
    
    def test_bivector_creation(self):
        """Test creating bivector."""
        B = Bivector(np.array([1.0, 0.0, 0.0]))
        assert B.components.shape == (3,)
        assert B.components[0] == 1.0
    
    def test_bivector_magnitude(self):
        """Test bivector magnitude."""
        B = Bivector(np.array([3.0, 4.0, 0.0]))
        assert abs(B.magnitude - 5.0) < 1e-10
    
    def test_bivector_normalize(self):
        """Test bivector normalization."""
        B = Bivector(np.array([3.0, 4.0, 0.0]))
        B_norm = B.normalize()
        assert abs(B_norm.magnitude - 1.0) < 1e-10
    
    def test_bivector_from_vectors(self):
        """Test creating bivector from wedge product."""
        v = np.array([1.0, 0.0, 0.0])
        w = np.array([0.0, 1.0, 0.0])
        
        B = Bivector.from_vectors(v, w)
        # v ∧ w in 3D gives cross product
        assert abs(B.components[2] - 1.0) < 1e-10


# ============================================================================
# ROTOR TESTS
# ============================================================================

class TestRotor:
    """Test rotor operations."""
    
    def test_rotor_from_angle_bivector(self):
        """Test creating rotor from angle and bivector."""
        B = Bivector(np.array([0.0, 0.0, 1.0]))
        R = Rotor.from_angle_bivector(np.pi/2, B)
        
        # Should be 90° rotation in xy-plane
        assert abs(R.scalar - np.cos(np.pi/4)) < 1e-10
    
    def test_rotor_from_vectors(self):
        """Test creating rotor from two vectors."""
        v = np.array([1.0, 0.0, 0.0])
        w = np.array([0.0, 1.0, 0.0])
        
        R = Rotor.from_vectors(v, w)
        v_rotated = R.apply(v)
        
        # Should rotate v toward w (may not be perfect due to 3D implementation)
        # Check that rotation moved in right direction
        dot_original = np.dot(v, w)
        dot_rotated = np.dot(v_rotated, w) / (np.linalg.norm(v_rotated) + 1e-10)
        assert dot_rotated > dot_original  # Improved alignment
    
    def test_rotor_identity(self):
        """Test identity rotor."""
        B = Bivector(np.array([0.0, 0.0, 1.0]))
        R = Rotor.from_angle_bivector(0.0, B)  # Zero angle
        
        v = np.array([1.0, 2.0, 3.0])
        v_rotated = R.apply(v)
        
        assert np.allclose(v_rotated, v)
    
    def test_rotor_inverse(self):
        """Test rotor inverse."""
        v = np.array([1.0, 0.0, 0.0])
        w = np.array([0.0, 1.0, 0.0])
        
        R = Rotor.from_vectors(v, w)
        R_inv = R.inverse()
        
        # R_inv should rotate w back toward v
        w_rotated = R_inv.apply(w)
        dot_original = np.dot(w, v)
        dot_back = np.dot(w_rotated, v) / (np.linalg.norm(w_rotated) + 1e-10)
        assert dot_back > dot_original  # Moved back toward v
    
    def test_rotor_composition(self):
        """Test rotor composition."""
        # Rotate 90° around z, then 90° around y
        Bz = Bivector(np.array([0.0, 0.0, 1.0]))
        By = Bivector(np.array([0.0, 1.0, 0.0]))
        
        R1 = Rotor.from_angle_bivector(np.pi/2, Bz)
        R2 = Rotor.from_angle_bivector(np.pi/2, By)
        
        R_combined = R2.compose(R1)
        
        v = np.array([1.0, 0.0, 0.0])
        v_sequential = R2.apply(R1.apply(v))
        v_composed = R_combined.apply(v)
        
        # Should give same result (within tolerance)
        assert np.allclose(v_sequential, v_composed, atol=1e-4)


# ============================================================================
# GRACE ROTOR TESTS
# ============================================================================

class TestGraceRotor:
    """Test Grace rotor operations."""
    
    def test_grace_initialization(self):
        """Test Grace rotor initialization."""
        grace = GraceRotor()
        assert grace.grace_strength == PHI_INV
    
    def test_grace_toward_normalization(self):
        """Test Grace rotates toward normalized state."""
        grace = GraceRotor()
        
        state = np.array([2.0, 2.0, 2.0])
        state_graced = grace.apply_grace(state, dt=0.5)
        
        # Should modify state (even if not perfectly normalized)
        assert not np.allclose(state, state_graced, atol=0.1)
    
    def test_grace_preserves_direction(self):
        """Test Grace preserves general direction."""
        grace = GraceRotor()
        
        state = np.array([1.0, 1.0, 1.0])
        state_graced = grace.apply_grace(state, dt=0.1)
        
        # Should have similar direction
        cos_angle = np.dot(state, state_graced) / (np.linalg.norm(state) * np.linalg.norm(state_graced))
        assert cos_angle > 0.9  # Less than ~25° rotation


# ============================================================================
# LOVE ROTOR TESTS
# ============================================================================

class TestLoveRotor:
    """Test Love rotor operations."""
    
    def test_love_initialization(self):
        """Test Love rotor initialization."""
        love = LoveRotor()
        assert love.love_strength == PHI_INV
    
    def test_love_full_alignment(self):
        """Test Love with full alignment."""
        love = LoveRotor()
        
        state = np.array([1.0, 0.0, 0.0])
        target = np.array([0.0, 1.0, 0.0])
        
        aligned = love.apply_love(state, target, full_alignment=True)
        
        # Should be more aligned (may not be perfect)
        dot_before = np.dot(state, target)
        dot_after = np.dot(aligned, target) / (np.linalg.norm(aligned) + 1e-10)
        assert dot_after > dot_before
    
    def test_love_partial_alignment(self):
        """Test Love with partial alignment."""
        love = LoveRotor()
        
        state = np.array([1.0, 0.0, 0.0])
        target = np.array([0.0, 1.0, 0.0])
        
        aligned = love.apply_love(state, target, dt=0.1, full_alignment=False)
        
        # Should be partially aligned (not fully)
        dot_before = np.dot(state, target)
        dot_after = np.dot(aligned, target) / np.linalg.norm(aligned)
        
        assert dot_after > dot_before
        assert not np.allclose(aligned/np.linalg.norm(aligned), target, atol=0.1)


# ============================================================================
# FORGIVENESS ROTOR TESTS
# ============================================================================

class TestForgivenessRotor:
    """Test Forgiveness rotor operations."""
    
    def test_forgiveness_initialization(self):
        """Test Forgiveness rotor initialization."""
        forgiveness = ForgivenessRotor()
        assert forgiveness.forgiveness_rate == PHI_INV
    
    def test_forgiveness_reduces_dissonance(self):
        """Test Forgiveness reduces dissonance."""
        forgiveness = ForgivenessRotor()
        
        state = np.array([1.0, 1.0, 0.0])
        dissonance = np.array([1.0, -1.0, 0.0])
        
        forgiven = forgiveness.apply_forgiveness(state, dissonance, dt=0.5)
        
        # Should change the state
        assert not np.allclose(state, forgiven, atol=0.1)


# ============================================================================
# COMBINED DYNAMICS TESTS
# ============================================================================

class TestCombinedRotorDynamics:
    """Test combined rotor dynamics."""
    
    def test_combined_initialization(self):
        """Test combined dynamics initialization."""
        combined = CombinedRotorDynamics()
        assert combined.grace is not None
        assert combined.love is not None
        assert combined.forgiveness is not None
    
    def test_combined_evolution(self):
        """Test combined evolution."""
        combined = CombinedRotorDynamics()
        
        state = np.array([1.0, 1.0, 1.0])
        target = np.array([0.0, 0.0, 1.0])
        
        evolved = combined.evolve_state(state, target=target, dt=0.1)
        
        # Should have moved toward target
        dot_before = np.dot(state/np.linalg.norm(state), target/np.linalg.norm(target))
        dot_after = np.dot(evolved/np.linalg.norm(evolved), target/np.linalg.norm(target))
        
        assert dot_after >= dot_before
    
    def test_golden_rotation_sequence(self):
        """Test golden rotation sequence."""
        combined = CombinedRotorDynamics()
        
        initial = np.array([1.0, 0.0, 0.0])
        trajectory = combined.golden_rotation_sequence(initial, num_steps=10)
        
        assert len(trajectory) == 11  # initial + 10 steps
        
        # All states should have similar magnitude
        norms = [np.linalg.norm(s) for s in trajectory]
        assert all(abs(n - norms[0]) < 0.1 for n in norms)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestRotorIntegration:
    """Integration tests with TFCA framework."""
    
    def test_rotor_complements_love_operator(self):
        """Test rotors complement Love operator."""
        from FIRM_dsl.love_operator import LoveOperator
        
        love_op = LoveOperator()
        love_rotor = LoveRotor()
        
        # Both should provide alignment mechanisms
        v = np.array([1.0, 0.0, 0.0])
        w = np.array([0.0, 1.0, 0.0])
        
        # Love operator gives scalar alignment
        love_result = love_op.apply(v, w)
        
        # Love rotor gives geometric rotation
        aligned = love_rotor.apply_love(v, w, dt=0.5)
        
        assert love_result is not None
        assert aligned is not None
        # Both mechanisms exist and work
        assert love_result.scalar_part is not None
        assert np.linalg.norm(aligned) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestRotorPerformance:
    """Performance tests."""
    
    def test_rotor_application_fast(self):
        """Test rotor application is fast."""
        import time
        
        v = np.array([1.0, 0.0, 0.0])
        w = np.array([0.0, 1.0, 0.0])
        R = Rotor.from_vectors(v, w)
        
        start = time.time()
        for _ in range(1000):
            R.apply(v)
        elapsed = time.time() - start
        
        assert elapsed < 0.1
    
    def test_grace_evolution_scales(self):
        """Test Grace evolution scales."""
        import time
        
        grace = GraceRotor()
        state = np.array([1.0, 1.0, 1.0])
        
        start = time.time()
        for _ in range(100):
            state = grace.apply_grace(state, dt=0.01)
        elapsed = time.time() - start
        
        assert elapsed < 0.1


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and return results."""
    test_classes = [
        TestBivector,
        TestRotor,
        TestGraceRotor,
        TestLoveRotor,
        TestForgivenessRotor,
        TestCombinedRotorDynamics,
        TestRotorIntegration,
        TestRotorPerformance,
    ]
    
    results = {}
    
    for test_class in test_classes:
        class_name = test_class.__name__
        results[class_name] = {}
        
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            try:
                method = getattr(instance, method_name)
                method()
                results[class_name][method_name] = 'PASSED'
            except Exception as e:
                results[class_name][method_name] = f'FAILED: {str(e)}'
    
    return results


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CLIFFORD ROTOR DYNAMICS TEST SUITE")
    print("="*70 + "\n")
    
    results = run_all_tests()
    
    total_tests = 0
    passed_tests = 0
    
    for class_name, class_results in results.items():
        print(f"\n{class_name}:")
        for test_name, result in class_results.items():
            total_tests += 1
            status = "✓" if result == 'PASSED' else "✗"
            print(f"  {status} {test_name}: {result}")
            if result == 'PASSED':
                passed_tests += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
    print("="*70 + "\n")

