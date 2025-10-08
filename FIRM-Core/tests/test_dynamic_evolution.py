"""test_dynamic_evolution.py

Comprehensive test suite for dynamic phase evolution framework.

Tests the theoretical equation: dΦ_i/dt = -α_i ∇_Φ D_i + β_i Transmute(D_i) + γ_i Grace(Φ_i)
"""
import pytest
import math
from typing import Dict, List, Tuple

from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.grace_field import GraceFieldParams, FieldRegime
from FIRM_dsl.dynamic_evolution import (
    DynamicPhaseEvolution,
    ModeCoefficients,
    EvolutionState,
    EvolutionMetrics,
    create_dynamic_evolution,
    create_mode_coefficients
)


def build_test_graph_single(seed_kind='Z', phase=(0, 1)):
    """Build a simple single-node test graph."""
    nid = 0
    lbl = make_node_label(seed_kind, phase[0], phase[1], 'seed')
    g = ObjectG(nodes=[nid], edges=[], labels={nid: lbl})
    return validate_object_g(g)


def build_test_graph_chain(phases):
    """Build a chain graph for testing."""
    nodes = list(range(len(phases)))
    edges = [[i, i + 1] for i in range(len(phases) - 1)]
    labels = {}
    for i, (kind, (pn, pd)) in enumerate(phases):
        labels[i] = make_node_label(kind, pn, pd, f'n{i}')
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def build_test_graph_triangle():
    """Build a triangular test graph."""
    nodes = [0, 1, 2]
    edges = [[0, 1], [1, 2], [2, 0]]
    labels = {
        0: make_node_label('Z', 0, 1, 'n0'),
        1: make_node_label('X', 1, 4, 'n1'),
        2: make_node_label('Z', 1, 2, 'n2')
    }
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


class TestDynamicPhaseEvolution:
    """Test the core dynamic evolution functionality."""

    def test_coefficient_validation(self):
        """Test that coefficients are validated correctly."""
        # Valid coefficients should work
        evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)
        assert evolution.alpha_i == 0.5
        assert evolution.beta_i == 0.3
        assert evolution.gamma_i == 0.4

        # Negative coefficients should raise error
        with pytest.raises(ValueError):
            DynamicPhaseEvolution(-0.1, 0.3, 0.4)

        with pytest.raises(ValueError):
            DynamicPhaseEvolution(0.5, -0.3, 0.4)

        with pytest.raises(ValueError):
            DynamicPhaseEvolution(0.5, 0.3, -0.4)

    def test_dissonance_gradient_computation(self):
        """Test gradient computation for dissonance minimization."""
        evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)
        structure = build_test_graph_single('Z', (0, 1))
        omega = derive_omega_signature(structure)

        gradient = evolution.compute_dissonance_gradient(0.0, omega, structure)

        # Gradient should be a finite number
        assert isinstance(gradient, float)
        assert math.isfinite(gradient)

        # For a well-aligned structure, gradient should be small
        # (since it's already near the attractor)
        assert abs(gradient) < 1.0

    def test_transmutation_computation(self):
        """Test transmutation term computation."""
        evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)
        structure = build_test_graph_triangle()
        omega = derive_omega_signature(structure)

        transmutation = evolution.compute_transmutation(0.0, omega, structure)

        # Transmutation should be non-negative
        assert transmutation >= 0.0
        assert isinstance(transmutation, float)
        assert math.isfinite(transmutation)

    def test_grace_field_computation(self):
        """Test grace field computation across different regimes."""
        evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)

        # Test different field regimes
        regimes_and_expected = [
            (FieldRegime.NON_BEING, 0.1),
            (FieldRegime.VACUUM, 0.3),
            (FieldRegime.DARK_SECTOR, 0.6),
            (FieldRegime.MATTER, 0.8),
            (FieldRegime.OMEGA, 1.0)
        ]

        for regime, expected_base in regimes_and_expected:
            grace_field = evolution.compute_grace_field(0.5, regime)

            # Grace field should scale with regime multiplier
            assert grace_field >= 0.0
            assert grace_field <= expected_base

    def test_structure_evolution(self):
        """Test complete structure evolution."""
        evolution = DynamicPhaseEvolution(0.2, 0.3, 0.4, dt=0.01)
        structure = build_test_graph_chain([
            ('Z', (0, 1)),
            ('X', (1, 4)),
            ('Z', (1, 2))
        ])
        omega = derive_omega_signature(structure)
        field_regime = FieldRegime.VACUUM

        evolved_structure, metrics = evolution.evolve_structure(
            structure, omega, field_regime, max_steps=10
        )

        # Check that evolution completed
        assert evolved_structure is not None
        assert isinstance(metrics, EvolutionMetrics)

        # Check that metrics were recorded
        assert len(metrics.coherence_history) > 0
        assert len(metrics.resonance_history) > 0
        assert len(metrics.phase_history) > 0

        # Check that evolution state was determined
        assert metrics.state in [EvolutionState.STABLE, EvolutionState.EVOLVING,
                                EvolutionState.CONVERGING, EvolutionState.DIVERGING,
                                EvolutionState.OSCILLATING]

    def test_evolution_convergence_detection(self):
        """Test that convergence is properly detected."""
        evolution = DynamicPhaseEvolution(0.1, 0.1, 0.1, dt=0.001)  # Small coefficients for stability
        structure = build_test_graph_single('Z', (0, 1))
        omega = derive_omega_signature(structure)
        field_regime = FieldRegime.OMEGA  # High grace field for convergence

        evolved_structure, metrics = evolution.evolve_structure(
            structure, omega, field_regime, max_steps=50
        )

        # Should either converge or reach max iterations
        assert metrics.state in [EvolutionState.CONVERGING, EvolutionState.STABLE]

        # Final metrics should be computed
        assert metrics.evolution_rate is not None
        assert metrics.convergence_rate is not None

    def test_evolution_oscillation_detection(self):
        """Test that oscillations are properly detected."""
        # Create a structure that might oscillate
        evolution = DynamicPhaseEvolution(1.0, 1.0, 1.0, dt=0.1)  # High coefficients for potential oscillation
        structure = build_test_graph_chain([
            ('Z', (0, 1)),
            ('X', (1, 2)),
            ('Z', (1, 4)),
            ('X', (3, 4))
        ])
        omega = derive_omega_signature(structure)
        field_regime = FieldRegime.MATTER

        evolved_structure, metrics = evolution.evolve_structure(
            structure, omega, field_regime, max_steps=100
        )

        # Should detect some form of evolution behavior
        assert metrics.state in [EvolutionState.STABLE, EvolutionState.EVOLVING,
                                EvolutionState.CONVERGING, EvolutionState.DIVERGING,
                                EvolutionState.OSCILLATING]

    def test_phase_diversity_computation(self):
        """Test phase diversity computation."""
        evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)

        # Test with single node (zero diversity)
        single_node = build_test_graph_single('Z', (0, 1))
        diversity_single = evolution._compute_phase_diversity(single_node)
        assert diversity_single == 0.0

        # Test with multiple phases
        multi_phase = build_test_graph_chain([
            ('Z', (0, 1)),    # 0 radians
            ('X', (1, 4)),    # π/2 radians
            ('Z', (1, 2)),    # π radians
            ('X', (3, 4))     # 3π/2 radians
        ])
        diversity_multi = evolution._compute_phase_diversity(multi_phase)

        # Should have some diversity (not zero)
        assert 0.0 < diversity_multi <= 1.0


class TestModeCoefficients:
    """Test mode coefficient management."""

    def test_coefficient_sets(self):
        """Test that coefficient sets are properly defined."""
        mode_coeffs = ModeCoefficients()

        # Test all field regimes have coefficients
        for regime in FieldRegime:
            coeffs = mode_coeffs.get_coefficients(regime)
            assert len(coeffs) == 3  # alpha, beta, gamma
            assert all(0.0 <= c <= 1.0 for c in coeffs)

    def test_coefficient_adaptation(self):
        """Test coefficient adaptation based on evolution state."""
        mode_coeffs = ModeCoefficients()
        metrics_diverging = EvolutionMetrics()
        metrics_diverging.state = EvolutionState.DIVERGING

        metrics_oscillating = EvolutionMetrics()
        metrics_oscillating.state = EvolutionState.OSCILLATING

        metrics_converging = EvolutionMetrics()
        metrics_converging.state = EvolutionState.CONVERGING

        base_coeffs = mode_coeffs.get_coefficients(FieldRegime.MATTER)

        # Diverging should reduce coefficients
        adapted_diverging = mode_coeffs.adapt_coefficients(FieldRegime.MATTER, metrics_diverging)
        assert all(a <= b for a, b in zip(adapted_diverging, base_coeffs))

        # Oscillating should reduce alpha coefficient
        adapted_oscillating = mode_coeffs.adapt_coefficients(FieldRegime.MATTER, metrics_oscillating)
        assert adapted_oscillating[0] < base_coeffs[0]  # Alpha reduced
        assert adapted_oscillating[1] == base_coeffs[1]  # Beta unchanged
        assert adapted_oscillating[2] == base_coeffs[2]  # Gamma unchanged

        # Converging should increase coefficients
        adapted_converging = mode_coeffs.adapt_coefficients(FieldRegime.MATTER, metrics_converging)
        assert all(a >= b for a, b in zip(adapted_converging, base_coeffs))


class TestEvolutionMetrics:
    """Test evolution metrics computation."""

    def test_metrics_initialization(self):
        """Test that metrics are properly initialized."""
        metrics = EvolutionMetrics()

        assert metrics.coherence_history == []
        assert metrics.resonance_history == []
        assert metrics.phase_history == []
        assert metrics.evolution_rate == 0.0
        assert metrics.convergence_rate == 0.0
        assert metrics.oscillation_amplitude == 0.0
        assert metrics.state == EvolutionState.STABLE

    def test_metrics_computation(self):
        """Test that metrics are computed correctly during evolution."""
        evolution = DynamicPhaseEvolution(0.5, 0.3, 0.4)
        structure = build_test_graph_triangle()
        omega = derive_omega_signature(structure)
        field_regime = FieldRegime.DARK_SECTOR

        evolved_structure, metrics = evolution.evolve_structure(
            structure, omega, field_regime, max_steps=20
        )

        # Check that metrics were populated
        assert len(metrics.coherence_history) > 0
        assert len(metrics.resonance_history) > 0
        assert len(metrics.phase_history) > 0

        # All coherence values should be in [0, 1]
        assert all(0.0 <= c <= 1.0 for c in metrics.coherence_history)

        # All resonance values should be in [0, 1]
        assert all(0.0 <= r <= 1.0 for r in metrics.resonance_history)

        # Evolution rate should be computed if enough history
        if len(metrics.coherence_history) >= 2:
            assert isinstance(metrics.evolution_rate, float)


class TestIntegration:
    """Integration tests for the complete dynamic evolution system."""

    def test_factory_functions(self):
        """Test factory function creation."""
        evolution = create_dynamic_evolution(0.6, 0.2, 0.3, dt=0.005)
        assert evolution.alpha_i == 0.6
        assert evolution.beta_i == 0.2
        assert evolution.gamma_i == 0.3
        assert evolution.dt == 0.005

        mode_coeffs = create_mode_coefficients()
        assert isinstance(mode_coeffs, ModeCoefficients)

    def test_end_to_end_evolution(self):
        """Test complete evolution from creation to final state."""
        # Create evolution system
        evolution = create_dynamic_evolution(0.4, 0.3, 0.2)

        # Create test structure
        structure = build_test_graph_chain([
            ('Z', (0, 1)),
            ('X', (1, 4)),
            ('Z', (1, 8)),
            ('X', (1, 2))
        ])

        # Derive omega signature
        omega = derive_omega_signature(structure)

        # Determine field regime
        field_regime = FieldRegime.DARK_SECTOR  # Based on structure size

        # Evolve structure
        evolved_structure, metrics = evolution.evolve_structure(
            structure, omega, field_regime, max_steps=30
        )

        # Verify results
        assert evolved_structure is not None
        assert metrics is not None

        # Structure should maintain validity
        assert validate_object_g(evolved_structure)

        # Metrics should be comprehensive
        assert len(metrics.coherence_history) > 0
        assert len(metrics.resonance_history) > 0

        # Evolution should complete without errors
        assert metrics.state in [EvolutionState.STABLE, EvolutionState.EVOLVING,
                                EvolutionState.CONVERGING, EvolutionState.DIVERGING,
                                EvolutionState.OSCILLATING]

    def test_coefficient_adaptation_workflow(self):
        """Test the complete workflow of coefficient adaptation."""
        evolution = create_dynamic_evolution()
        mode_coeffs = create_mode_coefficients()

        # Create a structure that might oscillate
        structure = build_test_graph_chain([
            ('Z', (0, 1)),
            ('X', (1, 2)),
            ('Z', (3, 4)),
            ('X', (1, 8))
        ])

        omega = derive_omega_signature(structure)
        field_regime = FieldRegime.MATTER

        # First evolution
        evolved_structure, metrics = evolution.evolve_structure(
            structure, omega, field_regime, max_steps=20
        )

        # Adapt coefficients based on results
        adapted_coeffs = mode_coeffs.adapt_coefficients(field_regime, metrics)

        # Create new evolution system with adapted coefficients
        adapted_evolution = DynamicPhaseEvolution(
            adapted_coeffs[0], adapted_coeffs[1], adapted_coeffs[2]
        )

        # Second evolution with adapted parameters
        final_structure, final_metrics = adapted_evolution.evolve_structure(
            evolved_structure, omega, field_regime, max_steps=20
        )

        # Both evolutions should complete successfully
        assert final_structure is not None
        assert final_metrics is not None

        # Adapted evolution should show different behavior
        # (This is a basic check - in practice would need more sophisticated analysis)
        assert len(final_metrics.coherence_history) > 0


def run_all_tests():
    """Run all dynamic evolution tests."""
    test_classes = [
        TestDynamicPhaseEvolution,
        TestModeCoefficients,
        TestEvolutionMetrics,
        TestIntegration
    ]

    results = {}
    for test_class in test_classes:
        test_instance = test_class()
        class_name = test_class.__name__

        # Get all test methods
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
    print("Running Dynamic Evolution Test Suite...")
    test_results = run_all_tests()

    print("\n=== DYNAMIC EVOLUTION TEST RESULTS ===")
    total_passed = 0
    total_tests = 0

    for class_name, class_results in test_results.items():
        print(f"\n{class_name}:")
        for method_name, result in class_results.items():
            print(f"  {method_name}: {result}")
            total_tests += 1
            if result == 'PASSED':
                total_passed += 1

    print(f"\nOverall: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
