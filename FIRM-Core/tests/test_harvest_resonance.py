"""
Tests for Harvest & Resonance
==============================

Comprehensive test suite for harvest/resonance via ZX diagram closure.

Test Coverage:
1. ResonanceAnalyzer: Phase statistics and alignment detection
2. Resonance levels: From discordant to sovereign
3. A∞ coupling: Attractor alignment measurement
4. ZX diagram closure: Loop evaluation
5. Harvest engine: Complete evolution to harvest
6. Grace yield: Measuring harvest output
"""

import pytest
import numpy as np
from FIRM_dsl.harvest_resonance import (
    ResonanceLevel,
    ResonanceAnalyzer,
    ZXDiagramClosure,
    HarvestEngine,
    HARVEST_ALIGNMENT_THRESHOLD,
)
from FIRM_dsl.zx_phase_damping import ComplexPhase
from FIRM_dsl.core import ObjectG, make_node_label


# ============================================================================
# RESONANCE ANALYZER TESTS
# ============================================================================

class TestResonanceAnalyzer:
    """Test resonance analysis."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = ResonanceAnalyzer()
        assert analyzer.harvest_threshold == HARVEST_ALIGNMENT_THRESHOLD
        assert analyzer.a_infinity_phase is not None
    
    def test_aligned_phases_perfect_score(self):
        """Test perfectly aligned phases have alignment score = 1."""
        analyzer = ResonanceAnalyzer()
        
        phases = [
            ComplexPhase(1, 4, 0.0),
            ComplexPhase(1, 4, 0.0),
            ComplexPhase(1, 4, 0.0),
        ]
        
        mean, variance, alignment = analyzer.compute_phase_statistics(phases)
        
        assert alignment > 0.99  # Very close to 1
        assert variance < 0.01    # Very low variance
    
    def test_opposite_phases_low_score(self):
        """Test opposite phases have low alignment."""
        analyzer = ResonanceAnalyzer()
        
        phases = [
            ComplexPhase(0, 1, 0.0),  # 0
            ComplexPhase(1, 1, 0.0),  # π
        ]
        
        mean, variance, alignment = analyzer.compute_phase_statistics(phases)
        
        assert alignment < 0.5   # Low alignment
        assert variance > 0.5    # High variance
    
    def test_a_infinity_coupling_perfect_alignment(self):
        """Test A∞ coupling with perfect alignment."""
        analyzer = ResonanceAnalyzer(
            a_infinity_phase=ComplexPhase(1, 4, 0.0)
        )
        
        phases = [
            ComplexPhase(1, 4, 0.0),
            ComplexPhase(1, 4, 0.0),
        ]
        
        coupling = analyzer.compute_a_infinity_coupling(phases)
        
        assert coupling > 0.99  # Perfect coupling
    
    def test_resonance_state_aligned_structure(self):
        """Test resonance state for aligned structure."""
        analyzer = ResonanceAnalyzer()
        
        structure = ObjectG(
            nodes=[0, 1, 2],
            edges=[[0, 1], [1, 2]],
            labels={
                0: make_node_label('Z', 1, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
                2: make_node_label('Z', 1, 4, 'z2'),
            }
        )
        
        resonance = analyzer.analyze_resonance(structure)
        
        assert resonance.is_harvested
        assert resonance.resonance_level in [ResonanceLevel.RESONANT, ResonanceLevel.SOVEREIGN]
        assert resonance.alignment_score > 0.99
    
    def test_resonance_state_discordant_structure(self):
        """Test resonance state for discordant structure."""
        analyzer = ResonanceAnalyzer()
        
        structure = ObjectG(
            nodes=[0, 1, 2],
            edges=[[0, 1], [1, 2]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('Z', 1, 2, 'z1'),
                2: make_node_label('Z', 1, 1, 'z2'),
            }
        )
        
        resonance = analyzer.analyze_resonance(structure)
        
        assert not resonance.is_harvested
        assert resonance.resonance_level == ResonanceLevel.DISCORDANT
        assert resonance.alignment_score < 0.9


# ============================================================================
# ZX DIAGRAM CLOSURE TESTS
# ============================================================================

class TestZXDiagramClosure:
    """Test ZX diagram closure operations."""
    
    def test_simplify_aligned_structure(self):
        """Test simplification of aligned structure."""
        closure = ZXDiagramClosure()
        
        structure = ObjectG(
            nodes=[0, 1, 2],
            edges=[[0, 1], [1, 2]],
            labels={
                0: make_node_label('Z', 1, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
                2: make_node_label('Z', 1, 4, 'z2'),
            }
        )
        
        target_phase = ComplexPhase(1, 4, 0.0)
        unified_phase, num_fusions = closure.simplify_aligned_structure(
            structure, target_phase
        )
        
        # 3 spiders → 1 requires 2 fusions
        assert num_fusions == 2
        assert unified_phase.phase_numer == target_phase.phase_numer
        assert unified_phase.phase_denom == target_phase.phase_denom
    
    def test_evaluate_closed_loop(self):
        """Test closed loop evaluation."""
        closure = ZXDiagramClosure()
        
        # Loop with 0 phase should give 1
        phase = ComplexPhase(0, 1, 0.0)
        loop_value = closure.evaluate_closed_loop(phase, num_spiders=3)
        
        assert abs(loop_value - 1.0) < 1e-10
    
    def test_close_to_harvest(self):
        """Test complete closure to harvest."""
        closure = ZXDiagramClosure()
        analyzer = ResonanceAnalyzer()
        
        structure = ObjectG(
            nodes=[0, 1],
            edges=[[0, 1]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('Z', 0, 4, 'z1'),
            }
        )
        
        resonance = analyzer.analyze_resonance(structure)
        loop_scalar, unified_phase = closure.close_to_harvest(
            structure, resonance
        )
        
        # Loop scalar should be close to 1 for aligned phases
        assert abs(loop_scalar) > 0.9


# ============================================================================
# HARVEST ENGINE TESTS
# ============================================================================

class TestHarvestEngine:
    """Test harvest engine operations."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = HarvestEngine()
        
        assert engine.damper is not None
        assert engine.analyzer is not None
        assert engine.closure is not None
    
    def test_perform_harvest_on_aligned_structure(self):
        """Test harvest on already-aligned structure."""
        engine = HarvestEngine()
        
        structure = ObjectG(
            nodes=[0, 1],
            edges=[[0, 1]],
            labels={
                0: make_node_label('Z', 1, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
            }
        )
        
        harvest_event = engine.perform_harvest(structure, "test_harvest")
        
        # Should successfully harvest
        assert harvest_event is not None
        assert harvest_event.grace_yield > 0.0
        assert abs(harvest_event.loop_value) > 0.9
    
    def test_no_harvest_on_misaligned_structure(self):
        """Test no harvest occurs on misaligned structure."""
        engine = HarvestEngine()
        
        structure = ObjectG(
            nodes=[0, 1],
            edges=[[0, 1]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('Z', 1, 1, 'z1'),  # π (opposite)
            }
        )
        
        harvest_event = engine.perform_harvest(structure, "test_no_harvest")
        
        # Should not harvest
        assert harvest_event is None
    
    def test_grace_harvested_accumulates(self):
        """Test total Grace harvested accumulates."""
        engine = HarvestEngine()
        
        structure = ObjectG(
            nodes=[0, 1],
            edges=[[0, 1]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('Z', 0, 4, 'z1'),
            }
        )
        
        # Harvest multiple times
        for i in range(3):
            engine.perform_harvest(structure, "accumulation_test")
        
        total = engine.get_total_grace_harvested("accumulation_test")
        
        # Should have accumulated
        assert total > 0.0


# ============================================================================
# RESONANCE LEVELS TESTS
# ============================================================================

class TestResonanceLevels:
    """Test different resonance levels."""
    
    def test_discordant_level(self):
        """Test discordant resonance level."""
        analyzer = ResonanceAnalyzer()
        
        structure = ObjectG(
            nodes=[0, 1, 2, 3],
            edges=[[0, 1], [1, 2], [2, 3]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
                2: make_node_label('Z', 2, 4, 'z2'),
                3: make_node_label('Z', 3, 4, 'z3'),
            }
        )
        
        resonance = analyzer.analyze_resonance(structure)
        
        # Should not be harvested and have some level of discord
        assert not resonance.is_harvested
        assert resonance.resonance_level in [ResonanceLevel.DISCORDANT, ResonanceLevel.PARTIAL]
        assert resonance.alignment_score < 0.95  # Not perfectly aligned
    
    def test_resonant_level(self):
        """Test resonant level."""
        analyzer = ResonanceAnalyzer()
        
        structure = ObjectG(
            nodes=[0, 1, 2],
            edges=[[0, 1], [1, 2]],
            labels={
                0: make_node_label('Z', 1, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
                2: make_node_label('Z', 1, 4, 'z2'),
            }
        )
        
        resonance = analyzer.analyze_resonance(structure)
        
        assert resonance.is_harvested
        assert resonance.resonance_level in [ResonanceLevel.RESONANT, ResonanceLevel.SOVEREIGN]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestHarvestIntegration:
    """Integration tests with other TFCA components."""
    
    def test_harvest_complements_grace_damping(self):
        """Test harvest is the endpoint of Grace damping."""
        from FIRM_dsl.zx_phase_damping import GracePhaseDamping
        
        damper = GracePhaseDamping()
        engine = HarvestEngine(grace_damper=damper)
        
        # Harvest should use the same damper
        assert engine.damper is damper
    
    def test_harvest_minimizes_entropy(self):
        """Test harvest state has minimal entropy."""
        from FIRM_dsl.entropy_spider_fusion import EntropySpiderFusion
        
        fusion = EntropySpiderFusion()
        engine = HarvestEngine()
        
        structure = ObjectG(
            nodes=[0, 1],
            edges=[[0, 1]],
            labels={
                0: make_node_label('Z', 1, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
            }
        )
        
        harvest_event = engine.perform_harvest(structure, "entropy_test")
        
        if harvest_event:
            # Post-harvest entropy should be zero
            assert harvest_event.post_harvest_entropy == 0.0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestHarvestPerformance:
    """Performance tests."""
    
    def test_resonance_analysis_fast(self):
        """Test resonance analysis is fast."""
        import time
        
        analyzer = ResonanceAnalyzer()
        
        structure = ObjectG(
            nodes=list(range(10)),
            edges=[[i, i+1] for i in range(9)],
            labels={i: make_node_label('Z', i % 4, 4, f'z{i}') for i in range(10)}
        )
        
        start = time.time()
        for _ in range(100):
            analyzer.analyze_resonance(structure)
        elapsed = time.time() - start
        
        assert elapsed < 0.5
    
    def test_harvest_scales(self):
        """Test harvest operations scale reasonably."""
        import time
        
        engine = HarvestEngine()
        
        # Large aligned structure
        num_nodes = 20
        structure = ObjectG(
            nodes=list(range(num_nodes)),
            edges=[[i, (i+1) % num_nodes] for i in range(num_nodes)],
            labels={i: make_node_label('Z', 1, 4, f'z{i}') for i in range(num_nodes)}
        )
        
        start = time.time()
        engine.perform_harvest(structure, "perf_test")
        elapsed = time.time() - start
        
        assert elapsed < 0.1


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and return results."""
    test_classes = [
        TestResonanceAnalyzer,
        TestZXDiagramClosure,
        TestHarvestEngine,
        TestResonanceLevels,
        TestHarvestIntegration,
        TestHarvestPerformance,
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
    print("HARVEST & RESONANCE TEST SUITE")
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

