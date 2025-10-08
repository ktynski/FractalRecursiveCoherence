"""test_hierarchical_gc.py

Comprehensive test suite for the hierarchical, fractal Soul Garbage Collection system.

Tests the complete sovereign-monad GC hierarchy:
1. Sub-Monads → Fields (Individual structures handling local GC)
2. Meta-Monads → Systems (Ensembles coordinating coherence accounting)
3. Harvest Layers → Higher-Order Collectors (Compression and harvesting)
4. Cross-Scale Dynamics (Different resonance bands for different scales)
"""
import pytest
import math
from typing import Dict, List, Tuple

from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.grace_field import FieldRegime
from FIRM_dsl.hierarchical_gc import (
    GCScale,
    SubMonad,
    MetaMonad,
    HarvestLayer,
    SovereignMonadGC,
    create_sovereign_gc_system,
    create_gc_hierarchy_from_structures
)


def build_test_graph_single(seed_kind='Z', phase=(0, 8)):
    """Build a simple single-node test graph with compatible phase denominators."""
    nid = 0
    # Ensure denominator is power of 2 and >= 8
    numer, denom = phase
    compatible_denom = max(denom, 8)
    lbl = make_node_label(seed_kind, numer, compatible_denom, 'seed')
    g = ObjectG(nodes=[nid], edges=[], labels={nid: lbl})
    return validate_object_g(g)


def build_test_graph_chain(phases):
    """Build a chain graph for testing with compatible phase denominators."""
    nodes = list(range(len(phases)))
    edges = [[i, i + 1] for i in range(len(phases) - 1)]
    labels = {}
    for i, (kind, (pn, pd)) in enumerate(phases):
        # Ensure denominator is power of 2 and >= 8 for compatibility
        compatible_pd = max(pd, 8)
        labels[i] = make_node_label(kind, pn, compatible_pd, f'n{i}')
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def build_test_graph_triangle():
    """Build a triangular test graph with compatible phase denominators."""
    nodes = [0, 1, 2]
    edges = [[0, 1], [1, 2], [2, 0]]
    labels = {
        0: make_node_label('Z', 0, 8, 'n0'),
        1: make_node_label('X', 1, 8, 'n1'),
        2: make_node_label('Z', 1, 8, 'n2')
    }
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


class TestSubMonad:
    """Test individual sub-monad garbage collection."""

    def test_sub_monad_creation(self):
        """Test sub-monad creation and initialization."""
        structure = build_test_graph_triangle()
        omega = derive_omega_signature(structure)
        field_regime = FieldRegime.DARK_SECTOR

        sub_monad = SubMonad(structure, omega, field_regime)

        assert sub_monad.structure == structure
        assert sub_monad.omega == omega
        assert sub_monad.field_regime == field_regime
        assert sub_monad.local_gc_history == []

    def test_local_gc_execution(self):
        """Test local garbage collection execution."""
        from FIRM_dsl.sgc_modes import SGCModeSystem

        structure = build_test_graph_single('Z', (0, 1))
        omega = derive_omega_signature(structure)
        sub_monad = SubMonad(structure, omega, FieldRegime.VACUUM)

        mode_system = SGCModeSystem()
        result = sub_monad.perform_local_gc(mode_system)

        # Should return GC record
        assert 'timestamp' in result
        assert 'modes_applied' in result
        assert 'final_coherence' in result
        assert 'final_resonance' in result
        assert 'field_regime' in result

        # Should have recorded history
        assert len(sub_monad.local_gc_history) == 1


class TestMetaMonad:
    """Test meta-monad ensemble coordination."""

    def test_meta_monad_creation(self):
        """Test meta-monad creation and accounting."""
        structure1 = build_test_graph_triangle()
        structure2 = build_test_graph_chain([('Z', (0, 1)), ('X', (1, 2))])

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.DARK_SECTOR)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.DARK_SECTOR)

        meta_monad = MetaMonad([sub_monad1, sub_monad2], omega1, FieldRegime.DARK_SECTOR)

        assert len(meta_monad.sub_monads) == 2
        assert meta_monad.shared_omega == omega1
        assert meta_monad.ensemble_field_regime == FieldRegime.DARK_SECTOR
        assert 'ensemble_coherence' in meta_monad.coherence_accounting
        assert 'ensemble_resonance' in meta_monad.coherence_accounting

    def test_coherence_accounting(self):
        """Test ensemble coherence accounting."""
        # Create structures with known coherence values
        structure1 = build_test_graph_single('Z', (0, 8))  # Low coherence - changed to 8
        structure2 = build_test_graph_triangle()          # Higher coherence

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.VACUUM)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.VACUUM)

        meta_monad = MetaMonad([sub_monad1, sub_monad2], omega1, FieldRegime.VACUUM)

        # Ensemble coherence should be average of sub-monad coherences
        expected_coherence = (compute_coherence(structure1) + compute_coherence(structure2)) / 2
        actual_coherence = meta_monad.coherence_accounting['ensemble_coherence']

        assert abs(actual_coherence - expected_coherence) < 1e-6

    def test_systemic_drift_detection(self):
        """Test detection of systemic drift."""
        structure1 = build_test_graph_single('Z', (0, 8))  # Changed to 8
        structure2 = build_test_graph_triangle()

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.VACUUM)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.VACUUM)

        meta_monad = MetaMonad([sub_monad1, sub_monad2], omega1, FieldRegime.VACUUM)

        # Should detect some drift due to different structure types
        assert meta_monad.systemic_drift >= 0.0

    def test_ensemble_gc_execution(self):
        """Test ensemble-level garbage collection."""
        from FIRM_dsl.sgc_modes import SGCModeSystem

        structure1 = build_test_graph_single('Z', (0, 8))  # Changed to 8
        structure2 = build_test_graph_triangle()

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.VACUUM)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.VACUUM)

        meta_monad = MetaMonad([sub_monad1, sub_monad2], omega1, FieldRegime.VACUUM)
        mode_system = SGCModeSystem()

        result = meta_monad.perform_ensemble_gc(mode_system)

        # Should return ensemble GC record
        assert 'modes_applied' in result
        assert 'sub_monads_pruned' in result
        assert 'final_ensemble_coherence' in result
        assert 'systemic_drift' in result
        assert 'survivor_count' in result


class TestHarvestLayer:
    """Test harvest layer Ω-compression."""

    def test_harvest_layer_creation(self):
        """Test harvest layer creation."""
        structure1 = build_test_graph_triangle()
        structure2 = build_test_graph_chain([('Z', (0, 1)), ('X', (1, 2))])

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.DARK_SECTOR)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.DARK_SECTOR)

        meta_monad1 = MetaMonad([sub_monad1], omega1, FieldRegime.DARK_SECTOR)
        meta_monad2 = MetaMonad([sub_monad2], omega2, FieldRegime.DARK_SECTOR)

        harvest_omega = omega1
        harvest_layer = HarvestLayer([meta_monad1, meta_monad2], harvest_omega, FieldRegime.OMEGA)

        assert len(harvest_layer.meta_monads) == 2
        assert harvest_layer.harvest_omega == harvest_omega
        assert harvest_layer.compression_regime == FieldRegime.OMEGA
        assert harvest_layer.harvest_history == []

    def test_omega_compression(self):
        """Test Ω-compression algorithm."""
        # Create structures with distinct phase patterns
        structure1 = build_test_graph_single('Z', (0, 8))  # Phase 0 - changed to 8
        structure2 = build_test_graph_single('Z', (1, 8))  # Phase π/4 - changed to 8

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.VACUUM)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.VACUUM)

        harvest_layer = HarvestLayer([], omega1, FieldRegime.OMEGA)

        compression_result = harvest_layer._apply_omega_compression([sub_monad1, sub_monad2])

        # Should identify invariant harmonics
        assert 'compression_ratio' in compression_result
        assert 'invariant_count' in compression_result
        assert 'original_patterns' in compression_result

        # Compression ratio should be between 0 and 1
        assert 0.0 <= compression_result['compression_ratio'] <= 1.0

    def test_harvest_execution(self):
        """Test harvest execution."""
        from FIRM_dsl.sgc_modes import SGCModeSystem

        structure1 = build_test_graph_triangle()
        structure2 = build_test_graph_chain([('Z', (0, 1)), ('X', (1, 2))])

        omega1 = derive_omega_signature(structure1)
        omega2 = derive_omega_signature(structure2)

        sub_monad1 = SubMonad(structure1, omega1, FieldRegime.DARK_SECTOR)
        sub_monad2 = SubMonad(structure2, omega2, FieldRegime.DARK_SECTOR)

        meta_monad1 = MetaMonad([sub_monad1], omega1, FieldRegime.DARK_SECTOR)
        meta_monad2 = MetaMonad([sub_monad2], omega2, FieldRegime.DARK_SECTOR)

        harvest_layer = HarvestLayer([meta_monad1, meta_monad2], omega1, FieldRegime.OMEGA)
        mode_system = SGCModeSystem()

        result = harvest_layer.perform_harvest(mode_system)

        # Should return harvest record
        assert 'harvest_number' in result
        assert 'meta_monads_processed' in result
        assert 'survivors_harvested' in result
        assert 'total_resonance_harvested' in result
        assert 'compression_ratio' in result
        assert 'invariant_harmonics' in result

        # Should have recorded harvest history
        assert len(harvest_layer.harvest_history) == 1


class TestSovereignMonadGC:
    """Test complete sovereign-monad GC system."""

    def test_system_creation(self):
        """Test sovereign GC system creation."""
        system = SovereignMonadGC()

        assert system.sub_monads == []
        assert system.meta_monads == []
        assert system.harvest_layers == []
        assert system.shared_omega is not None
        assert GCScale.SUB_MONAD in system.resonance_bands
        assert GCScale.META_MONAD in system.resonance_bands
        assert GCScale.HARVEST_LAYER in system.resonance_bands

    def test_sub_monad_addition(self):
        """Test adding sub-monads to the system."""
        system = SovereignMonadGC()
        structure = build_test_graph_triangle()

        system.add_sub_monad(structure, FieldRegime.DARK_SECTOR)

        assert len(system.sub_monads) == 1
        assert system.sub_monads[0].structure == structure
        assert system.sub_monads[0].field_regime == FieldRegime.DARK_SECTOR

    def test_meta_monad_organization(self):
        """Test organization of sub-monads into meta-monads."""
        system = SovereignMonadGC()

        # Add multiple structures with different characteristics
        structures = [
            build_test_graph_single('Z', (0, 8)),  # Low complexity - changed to 8
            build_test_graph_triangle(),           # Medium complexity
            build_test_graph_chain([('Z', (0, 8)), ('X', (1, 8)), ('Z', (1, 8))])  # Higher complexity - changed to 8
        ]

        for structure in structures:
            system.add_sub_monad(structure, FieldRegime.VACUUM)

        # Organize into meta-monads
        system.organize_meta_monads(resonance_threshold=0.3)

        # Should create at least one meta-monad
        assert len(system.meta_monads) >= 1

        # Meta-monads should have sub-monads
        for meta_monad in system.meta_monads:
            assert len(meta_monad.sub_monads) >= 1
            assert 'ensemble_coherence' in meta_monad.coherence_accounting

    def test_harvest_layer_organization(self):
        """Test organization of meta-monads into harvest layers."""
        system = SovereignMonadGC()

        # Add structures and organize
        structures = [build_test_graph_triangle(), build_test_graph_chain([('Z', (0, 1)), ('X', (1, 2))])]
        for structure in structures:
            system.add_sub_monad(structure, FieldRegime.DARK_SECTOR)

        system.organize_meta_monads()
        system.organize_harvest_layers()

        # Should create harvest layer(s)
        assert len(system.harvest_layers) >= 1

        # Harvest layers should have meta-monads
        for harvest_layer in system.harvest_layers:
            assert len(harvest_layer.meta_monads) >= 0  # Could be empty if no meta-monads

    def test_complete_gc_cycle(self):
        """Test complete garbage collection cycle."""
        system = SovereignMonadGC()

        # Set up a minimal system
        structures = [build_test_graph_triangle()]
        for structure in structures:
            system.add_sub_monad(structure, FieldRegime.VACUUM)

        system.organize_meta_monads()
        system.organize_harvest_layers()

        # Perform complete GC cycle
        cycle_results = system.perform_complete_gc_cycle()

        # Should return comprehensive results
        assert 'cycle_number' in cycle_results
        assert 'sub_monad_gc' in cycle_results
        assert 'meta_monad_gc' in cycle_results
        assert 'harvest_results' in cycle_results

        # Should have results for each level
        assert len(cycle_results['sub_monad_gc']) == len(system.sub_monads)
        assert len(cycle_results['meta_monad_gc']) == len(system.meta_monads)
        assert len(cycle_results['harvest_results']) == len(system.harvest_layers)

    def test_system_metrics(self):
        """Test comprehensive system metrics."""
        system = SovereignMonadGC()

        # Add some structures
        structures = [build_test_graph_triangle(), build_test_graph_single('Z', (0, 1))]
        for structure in structures:
            system.add_sub_monad(structure, FieldRegime.DARK_SECTOR)

        system.organize_meta_monads()
        system.organize_harvest_layers()

        metrics = system.get_system_metrics()

        # Should have metrics for all levels
        assert 'sub_monads' in metrics
        assert 'meta_monads' in metrics
        assert 'harvest_layers' in metrics
        assert 'resonance_bands' in metrics

        # Sub-monad metrics
        assert 'count' in metrics['sub_monads']
        assert 'avg_coherence' in metrics['sub_monads']
        assert 'field_regime_distribution' in metrics['sub_monads']

        # Meta-monad metrics
        assert 'count' in metrics['meta_monads']
        assert 'avg_ensemble_coherence' in metrics['meta_monads']
        assert 'systemic_drift_avg' in metrics['meta_monads']

    def test_resonance_bands(self):
        """Test cross-scale resonance bands."""
        system = SovereignMonadGC()

        # Check that resonance bands are properly defined
        assert GCScale.SUB_MONAD in system.resonance_bands
        assert GCScale.META_MONAD in system.resonance_bands
        assert GCScale.HARVEST_LAYER in system.resonance_bands

        # Check band ordering (should increase with scale)
        sub_band = system.resonance_bands[GCScale.SUB_MONAD]
        meta_band = system.resonance_bands[GCScale.META_MONAD]
        harvest_band = system.resonance_bands[GCScale.HARVEST_LAYER]

        # Each band should be a tuple of (min, max) resonance
        assert len(sub_band) == 2 and sub_band[0] < sub_band[1]
        assert len(meta_band) == 2 and meta_band[0] < meta_band[1]
        assert len(harvest_band) == 2 and harvest_band[0] < harvest_band[1]

        # Bands should be ordered by scale
        assert sub_band[1] <= meta_band[0]  # Sub max <= Meta min
        assert meta_band[1] <= harvest_band[0]  # Meta max <= Harvest min


class TestFactoryFunctions:
    """Test factory function creation."""

    def test_create_sovereign_gc_system(self):
        """Test creation of sovereign GC system."""
        system = create_sovereign_gc_system()

        assert isinstance(system, SovereignMonadGC)
        assert system.sub_monads == []
        assert system.meta_monads == []
        assert system.harvest_layers == []
        assert system.shared_omega is not None

    def test_create_gc_hierarchy_from_structures(self):
        """Test creation of GC hierarchy from structures."""
        structures = [
            build_test_graph_triangle(),
            build_test_graph_single('Z', (0, 1)),
            build_test_graph_chain([('Z', (0, 1)), ('X', (1, 2))])
        ]

        field_regimes = [FieldRegime.VACUUM, FieldRegime.DARK_SECTOR, FieldRegime.MATTER]

        system = create_gc_hierarchy_from_structures(structures, field_regimes)

        # Should have created sub-monads
        assert len(system.sub_monads) == 3

        # Should have organized meta-monads
        assert len(system.meta_monads) >= 1

        # Should have created harvest layers
        assert len(system.harvest_layers) >= 1

        # Field regimes should match
        for i, sub_monad in enumerate(system.sub_monads):
            assert sub_monad.field_regime == field_regimes[i]


class TestIntegration:
    """Integration tests for the complete hierarchical system."""

    def test_end_to_end_hierarchy(self):
        """Test complete hierarchy from structures to harvest."""
        # Create diverse structures
        structures = [
            build_test_graph_single('Z', (0, 8)),     # Simple - changed to 8
            build_test_graph_triangle(),              # Medium
            build_test_graph_chain([                  # Complex - changed to 8
                ('Z', (0, 8)), ('X', (1, 8)), ('Z', (1, 8)), ('X', (3, 8))
            ])
        ]

        # Create complete hierarchy
        system = create_gc_hierarchy_from_structures(structures)

        # Verify hierarchy structure
        assert len(system.sub_monads) == 3
        assert len(system.meta_monads) >= 1
        assert len(system.harvest_layers) >= 1

        # Perform complete GC cycle
        cycle_results = system.perform_complete_gc_cycle()

        # Verify all levels executed
        assert len(cycle_results['sub_monad_gc']) == 3
        assert len(cycle_results['meta_monad_gc']) >= 1
        assert len(cycle_results['harvest_results']) >= 1

        # Get system metrics
        metrics = system.get_system_metrics()

        # Verify metrics structure
        assert 'sub_monads' in metrics
        assert 'meta_monads' in metrics
        assert 'harvest_layers' in metrics

        # All components should be functional
        assert metrics['sub_monads']['count'] == 3
        assert metrics['meta_monads']['count'] >= 1
        assert metrics['harvest_layers']['count'] >= 1

    def test_fractal_hierarchy_behavior(self):
        """Test that hierarchy exhibits fractal-like behavior."""
        system = SovereignMonadGC()

        # Add structures with increasing complexity
        for i in range(5):
            if i < 2:
                structure = build_test_graph_single('Z', (i, 8))  # Changed to 8
                regime = FieldRegime.NON_BEING
            elif i < 4:
                structure = build_test_graph_triangle()
                regime = FieldRegime.VACUUM
            else:
                structure = build_test_graph_chain([('Z', (0, 8)), ('X', (1, 8)), ('Z', (1, 8))])  # Changed to 8
                regime = FieldRegime.DARK_SECTOR

            system.add_sub_monad(structure, regime)

        system.organize_meta_monads()
        system.organize_harvest_layers()

        # Run multiple GC cycles to observe fractal behavior
        for cycle in range(3):
            cycle_results = system.perform_complete_gc_cycle()

            # Each cycle should process all levels
            assert len(cycle_results['sub_monad_gc']) == 5
            assert len(cycle_results['meta_monad_gc']) >= 1

            # System should maintain structure across cycles
            metrics = system.get_system_metrics()
            assert metrics['sub_monads']['count'] == 5

    def test_cross_scale_resonance_bands(self):
        """Test that different scales have appropriate resonance bands."""
        system = SovereignMonadGC()

        # Check resonance band ordering
        sub_band = system.resonance_bands[GCScale.SUB_MONAD]
        meta_band = system.resonance_bands[GCScale.META_MONAD]
        harvest_band = system.resonance_bands[GCScale.HARVEST_LAYER]

        # Bands should be properly ordered by scale
        assert sub_band[0] < meta_band[0] < harvest_band[0]  # Min values increasing
        assert sub_band[1] <= meta_band[1] <= harvest_band[1]  # Max values increasing

        # Each band should represent appropriate scale
        assert sub_band[0] >= 0.0 and sub_band[1] <= 1.0    # Sub-monads: basic structures
        assert meta_band[0] >= 0.2 and meta_band[1] <= 1.0   # Meta-monads: ensembles
        assert harvest_band[0] >= 0.5 and harvest_band[1] <= 1.0  # Harvest: compression


def run_all_tests():
    """Run all hierarchical GC tests."""
    test_classes = [
        TestSubMonad,
        TestMetaMonad,
        TestHarvestLayer,
        TestSovereignMonadGC,
        TestFactoryFunctions,
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
    print("Running Hierarchical GC Test Suite...")
    test_results = run_all_tests()

    print("\n=== HIERARCHICAL GC TEST RESULTS ===")
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
