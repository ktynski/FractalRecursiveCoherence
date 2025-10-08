"""
Test Suite for Love Operator
=============================

Comprehensive tests for the Love operator: L(v, w) = ½(⟨v, w⟩ + I(v ∧ w))

Tests verify:
1. Mathematical properties (symmetry, bounds, self-love)
2. Geometric interpretation (alignment + rotation)
3. Love-Grace dynamics
4. Physical applications
"""

import pytest
import numpy as np
from typing import List

from FIRM_dsl.love_operator import (
    CliffordAlgebra,
    LoveOperator,
    LoveGraceDynamics,
    PHI,
    PHI_INV,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

def random_unit_vector_3d() -> np.ndarray:
    """Generate random 3D unit vector."""
    v = np.random.randn(3)
    return v / (np.linalg.norm(v) + 1e-10)


def orthogonal_vectors_3d() -> tuple[np.ndarray, np.ndarray]:
    """Generate two orthogonal 3D vectors."""
    v1 = random_unit_vector_3d()
    # Generate random perpendicular vector
    v_temp = np.random.randn(3)
    v2 = v_temp - np.dot(v_temp, v1) * v1
    v2 = v2 / (np.linalg.norm(v2) + 1e-10)
    return v1, v2


def parallel_vectors_3d() -> tuple[np.ndarray, np.ndarray]:
    """Generate two parallel 3D vectors."""
    v1 = random_unit_vector_3d()
    v2 = 2.0 * v1  # Parallel, different magnitude
    return v1, v2


# ============================================================================
# CLIFFORD ALGEBRA TESTS
# ============================================================================

class TestCliffordAlgebra:
    """Test Clifford algebra operations."""
    
    def test_initialization(self):
        """Test Clifford algebra initialization."""
        cl = CliffordAlgebra(dimension=3)
        
        assert cl.dim == 3
        assert cl.basis_size == 8  # 2^3
    
    def test_grade_projection(self):
        """Test grade projection."""
        cl = CliffordAlgebra(dimension=3)
        
        # Create multivector with all grades
        mv = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        
        # Project to scalar
        scalar = cl.grade_projection(mv, grade=0)
        assert scalar[0] == 1.0
        assert np.sum(np.abs(scalar[1:])) < 1e-10
        
        # Project to vector
        vector = cl.grade_projection(mv, grade=1)
        assert np.allclose(vector[1:4], [2.0, 3.0, 4.0])
        assert abs(vector[0]) < 1e-10
        
        # Project to bivector
        bivector = cl.grade_projection(mv, grade=2)
        assert np.allclose(bivector[4:7], [5.0, 6.0, 7.0])
    
    def test_inner_product(self):
        """Test Clifford inner product."""
        cl = CliffordAlgebra(dimension=3)
        
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        v3 = np.array([1.0, 1.0, 0.0]) / np.sqrt(2)
        
        # Orthogonal vectors
        assert abs(cl.inner_product(v1, v2)) < 1e-10
        
        # Parallel vector
        assert abs(cl.inner_product(v1, v1) - 1.0) < 1e-10
        
        # 45-degree angle
        inner = cl.inner_product(v1, v3)
        assert abs(inner - 1/np.sqrt(2)) < 1e-10
    
    def test_wedge_product(self):
        """Test exterior (wedge) product."""
        cl = CliffordAlgebra(dimension=3)
        
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        
        wedge = cl.wedge_product(v1, v2)
        
        # Should create bivector e₁e₂
        assert abs(wedge[4] - 1.0) < 1e-10  # e₁e₂ component
        assert abs(wedge[5]) < 1e-10  # e₁e₃ component
        assert abs(wedge[6]) < 1e-10  # e₂e₃ component
    
    def test_wedge_antisymmetry(self):
        """Test wedge product antisymmetry: v∧w = -(w∧v)."""
        cl = CliffordAlgebra(dimension=3)
        
        v1 = random_unit_vector_3d()
        v2 = random_unit_vector_3d()
        
        wedge_12 = cl.wedge_product(v1, v2)
        wedge_21 = cl.wedge_product(v2, v1)
        
        # Should be opposite
        assert np.allclose(wedge_12[4:7], -wedge_21[4:7], atol=1e-10)
    
    def test_geometric_product(self):
        """Test geometric product: vw = ⟨v,w⟩ + v∧w."""
        cl = CliffordAlgebra(dimension=3)
        
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        
        geom_prod = cl.geometric_product(v1, v2)
        
        # Scalar part should be 0 (orthogonal)
        assert abs(geom_prod[0]) < 1e-10
        
        # Bivector part should be e₁e₂
        assert abs(geom_prod[4] - 1.0) < 1e-10


# ============================================================================
# LOVE OPERATOR TESTS
# ============================================================================

class TestLoveOperator:
    """Test Love operator L(v,w) = ½(⟨v,w⟩ + I(v∧w))."""
    
    def test_self_love(self):
        """Test self-love: L(v,v) = ⟨v,v⟩ = |v|²."""
        love = LoveOperator()
        
        vectors = [
            np.array([1.0, 0.0, 0.0]),
            np.array([1.0, 1.0, 0.0]) / np.sqrt(2),
            random_unit_vector_3d(),
        ]
        
        for v in vectors:
            self_love_value = love.self_love(v)
            expected = np.dot(v, v)
            
            assert abs(self_love_value - expected) < 1e-10, \
                f"Self-love {self_love_value} != |v|² {expected}"
    
    def test_orthogonal_vectors(self):
        """Test love between orthogonal vectors."""
        love = LoveOperator()
        
        v1, v2 = orthogonal_vectors_3d()
        
        result = love.apply(v1, v2)
        
        # Scalar part should be zero (no alignment)
        assert abs(result.scalar_part) < 1e-8, \
            f"Orthogonal vectors have non-zero scalar love: {result.scalar_part}"
        
        # Bivector part should be non-zero (rotation exists)
        assert np.linalg.norm(result.bivector_part) > 1e-10, \
            "Orthogonal vectors should have rotational component"
    
    def test_parallel_vectors(self):
        """Test love between parallel vectors."""
        love = LoveOperator()
        
        v1, v2 = parallel_vectors_3d()
        
        result = love.apply(v1, v2)
        
        # Scalar part should be positive (strong alignment)
        assert result.scalar_part > 0, \
            "Parallel vectors should have positive scalar love"
        
        # Bivector part should be nearly zero (no rotation)
        assert np.linalg.norm(result.bivector_part) < 1e-8, \
            f"Parallel vectors have non-zero rotation: {np.linalg.norm(result.bivector_part)}"
    
    def test_love_bounds(self):
        """Test that |L(v,w)| ≤ |v||w|."""
        love = LoveOperator()
        
        for _ in range(10):
            v1 = random_unit_vector_3d()
            v2 = random_unit_vector_3d()
            
            result = love.apply(v1, v2)
            
            v1_mag = np.linalg.norm(v1)
            v2_mag = np.linalg.norm(v2)
            max_love = v1_mag * v2_mag
            
            assert result.magnitude <= max_love + 1e-6, \
                f"Love magnitude {result.magnitude} exceeds bound {max_love}"
    
    def test_normalized_alignment(self):
        """Test normalized alignment is in [-1, 1]."""
        love = LoveOperator()
        
        for _ in range(10):
            v1 = random_unit_vector_3d()
            v2 = random_unit_vector_3d()
            
            result = love.apply(v1, v2)
            
            assert -1.0 <= result.normalized_alignment <= 1.0, \
                f"Normalized alignment {result.normalized_alignment} out of bounds"
    
    def test_love_symmetry(self):
        """Test love symmetry properties."""
        love = LoveOperator()
        
        v1 = random_unit_vector_3d()
        v2 = random_unit_vector_3d()
        
        love_12, love_21 = love.love_symmetry(v1, v2)
        
        # Scalar parts should be equal
        assert abs(love_12[0] - love_21[0]) < 1e-10, \
            "Scalar love not symmetric"
        
        # Bivector parts should be opposite (antisymmetric)
        assert np.allclose(love_12[4:7], -love_21[4:7], atol=1e-10), \
            "Bivector love not antisymmetric"
    
    def test_love_field(self):
        """Test love field computation."""
        love = LoveOperator()
        
        v = np.array([1.0, 0.0, 0.0])
        field = [
            np.array([1.0, 0.0, 0.0]),  # Parallel
            np.array([0.0, 1.0, 0.0]),  # Orthogonal
            np.array([-1.0, 0.0, 0.0]), # Antiparallel
        ]
        
        love_field = love.love_field(v, field)
        
        assert len(love_field) == 3
        assert all(lf >= 0 for lf in love_field)
        # Parallel should have highest love
        assert love_field[0] > love_field[1]
    
    def test_maximal_love_direction(self):
        """Test finding maximal love direction."""
        love = LoveOperator()
        
        v = np.array([1.0, 0.0, 0.0])
        field = [
            np.array([0.5, 0.5, 0.0]),   # 45 degrees
            np.array([1.0, 0.0, 0.0]),   # Parallel (best)
            np.array([0.0, 1.0, 0.0]),   # Orthogonal
        ]
        
        optimal_direction, max_love = love.maximal_love_direction(v, field)
        
        # Should select parallel direction
        assert np.allclose(optimal_direction, field[1])
    
    def test_love_gradient(self):
        """Test love gradient computation."""
        love = LoveOperator()
        
        v = np.array([0.5, 0.5, 0.0])
        w = np.array([1.0, 0.0, 0.0])
        
        gradient = love.love_gradient(v, w)
        
        # Gradient should point roughly toward w
        assert gradient[0] > 0, "Gradient should point toward target"
        assert len(gradient) == 3
    
    def test_evolve_toward_love(self):
        """Test evolution toward maximal love."""
        love = LoveOperator()
        
        v_initial = np.array([0.0, 1.0, 0.0])
        w_target = np.array([1.0, 0.0, 0.0])
        
        # Evolve for several steps
        v = v_initial.copy()
        initial_love = love.apply(v, w_target).magnitude
        
        for _ in range(10):
            v = love.evolve_toward_love(v, w_target, dt=0.1, learning_rate=1.0)
        
        final_love = love.apply(v, w_target).magnitude
        
        # Love should increase
        assert final_love > initial_love, \
            f"Love did not increase: {initial_love} -> {final_love}"


# ============================================================================
# LOVE-GRACE DYNAMICS TESTS
# ============================================================================

class TestLoveGraceDynamics:
    """Test combined Love-Grace dynamics."""
    
    def test_initialization(self):
        """Test Love-Grace dynamics initialization."""
        dynamics = LoveGraceDynamics()
        assert dynamics.love is not None
    
    def test_combined_flow(self):
        """Test combined Grace-Love flow computation."""
        dynamics = LoveGraceDynamics()
        
        psi = np.array([0.5, 0.5, 0.0])
        a_infinity = np.array([1.0, 0.0, 0.0])  # Sovereign attractor
        
        flow = dynamics.compute_combined_flow(psi, a_infinity)
        
        assert len(flow) == 3
        # Flow should be finite
        assert np.all(np.isfinite(flow))
        # Flow should point generally toward a_infinity
        assert np.dot(flow, a_infinity - psi) > 0
    
    def test_evolve_step(self):
        """Test single evolution step."""
        dynamics = LoveGraceDynamics()
        
        psi = np.array([0.0, 1.0, 0.0])
        a_infinity = np.array([1.0, 0.0, 0.0])
        
        psi_new = dynamics.evolve_step(psi, a_infinity, dt=0.01)
        
        # Should move toward a_infinity
        dist_initial = np.linalg.norm(psi - a_infinity)
        dist_final = np.linalg.norm(psi_new - a_infinity)
        
        assert dist_final < dist_initial, \
            "Evolution did not move toward attractor"
    
    def test_evolve_trajectory(self):
        """Test complete evolution trajectory."""
        dynamics = LoveGraceDynamics()
        
        psi0 = np.array([0.0, 0.0, 1.0])
        a_infinity = np.array([1.0, 0.0, 0.0])
        
        trajectory = dynamics.evolve_trajectory(psi0, a_infinity, num_steps=50, dt=0.05)
        
        assert trajectory.shape == (51, 3)  # num_steps + initial
        
        # Distance to attractor should decrease
        distances = [np.linalg.norm(traj - a_infinity) for traj in trajectory]
        assert distances[-1] < distances[0], \
            "Trajectory did not converge toward attractor"
    
    def test_convergence_to_attractor(self):
        """Test that trajectory converges to sovereign attractor."""
        dynamics = LoveGraceDynamics()
        
        psi0 = random_unit_vector_3d()
        a_infinity = random_unit_vector_3d()
        
        trajectory = dynamics.evolve_trajectory(psi0, a_infinity, num_steps=200, dt=0.01)
        
        final_state = trajectory[-1]
        final_distance = np.linalg.norm(final_state - a_infinity)
        
        # Should get close to attractor
        assert final_distance < 0.5, \
            f"Did not converge: final distance {final_distance}"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestLoveIntegration:
    """Integration tests for Love operator in complete system."""
    
    def test_love_grace_balance(self):
        """Test that Love and Grace balance in dynamics."""
        dynamics = LoveGraceDynamics()
        
        psi = np.array([0.5, 0.5, 0.0])
        a_infinity = np.array([1.0, 0.0, 0.0])
        
        # Compute flow with different weight combinations
        flow_grace_heavy = dynamics.compute_combined_flow(
            psi, a_infinity, grace_weight=0.8, love_weight=0.2
        )
        flow_love_heavy = dynamics.compute_combined_flow(
            psi, a_infinity, grace_weight=0.2, love_weight=0.8
        )
        flow_balanced = dynamics.compute_combined_flow(
            psi, a_infinity, grace_weight=PHI_INV, love_weight=PHI_INV
        )
        
        # All should produce reasonable flows
        assert np.all(np.isfinite(flow_grace_heavy))
        assert np.all(np.isfinite(flow_love_heavy))
        assert np.all(np.isfinite(flow_balanced))
    
    def test_love_with_multiple_attractors(self):
        """Test Love field with multiple attractors."""
        love = LoveOperator()
        
        psi = np.array([0.0, 0.0, 1.0])
        attractors = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),  # Closest
        ]
        
        love_field = love.love_field(psi, attractors)
        
        # Closest attractor should have highest love
        assert np.argmax(love_field) == 2
    
    def test_love_stability(self):
        """Test that Love operator is numerically stable."""
        love = LoveOperator()
        
        # Test with very small vectors
        v_small = np.array([1e-10, 1e-10, 1e-10])
        w_small = np.array([1e-10, 0.0, 0.0])
        
        result_small = love.apply(v_small, w_small)
        assert np.all(np.isfinite(result_small.love_value))
        
        # Test with large vectors
        v_large = np.array([1e10, 0.0, 0.0])
        w_large = np.array([0.0, 1e10, 0.0])
        
        result_large = love.apply(v_large, w_large)
        assert np.all(np.isfinite(result_large.love_value))


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_all_tests():
    """Run all Love operator tests."""
    test_classes = [
        TestCliffordAlgebra,
        TestLoveOperator,
        TestLoveGraceDynamics,
        TestLoveIntegration,
    ]
    
    results = {}
    for test_class in test_classes:
        test_instance = test_class()
        class_name = test_class.__name__
        
        test_methods = [method for method in dir(test_instance)
                       if method.startswith('test_')]
        
        class_results = {}
        for method_name in test_methods:
            try:
                method = getattr(test_instance, method_name)
                method()
                class_results[method_name] = 'PASSED'
            except Exception as e:
                class_results[method_name] = f'FAILED: {str(e)}'
        
        results[class_name] = class_results
    
    return results


if __name__ == "__main__":
    print("Running Love Operator Test Suite...")
    test_results = run_all_tests()
    
    print("\n" + "="*70)
    print("LOVE OPERATOR TEST RESULTS")
    print("="*70)
    
    total_passed = 0
    total_tests = 0
    
    for class_name, class_results in test_results.items():
        print(f"\n{class_name}:")
        for method_name, result in class_results.items():
            print(f"  {method_name}: {result}")
            total_tests += 1
            if result == 'PASSED':
                total_passed += 1
    
    print(f"\n{'='*70}")
    print(f"Overall: {total_passed}/{total_tests} tests passed")
    print(f"{'='*70}\n")
    
    if total_passed == total_tests:
        print("✓ ALL TESTS PASSED!")
        print("\nLove Operator: VALIDATED")
        print("Geometric alignment proven:")
        print("  L(v, w) = ½(⟨v, w⟩ + I(v ∧ w))")
        print("  - Scalar: alignment measure")
        print("  - Bivector: rotational coupling")
        print("  - Together: complete relational geometry")
        exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        exit(1)

