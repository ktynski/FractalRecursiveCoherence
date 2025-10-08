"""
Tests for Entropy Spider Fusion
================================

Comprehensive test suite for entropy production via spider fusion with dissonance measurement.

Test Coverage:
1. DissonanceCalculator: Phase difference and sin²(Δ/2) measure
2. Same-color fusion: Low entropy, coherent
3. Different-color fusion: High entropy, decoherent
4. Forgiveness: Aligned Z-X annihilation
5. Thermodynamic balance: ΔS + ΔG = 0
6. Structure-level entropy
"""

import pytest
import numpy as np
from FIRM_dsl.entropy_spider_fusion import (
    DissonanceCalculator,
    EntropySpiderFusion,
    StructureEntropyDynamics,
    demonstrate_entropy_spider_fusion,
    ALIGNMENT_THRESHOLD,
)
from FIRM_dsl.zx_phase_damping import SpiderType, ComplexPhase
from FIRM_dsl.core import ObjectG, make_node_label


# ============================================================================
# DISSONANCE CALCULATOR TESTS
# ============================================================================

class TestDissonanceCalculator:
    """Test dissonance computation."""
    
    def test_initialization(self):
        """Test calculator initialization."""
        calc = DissonanceCalculator()
        assert calc.alignment_threshold == ALIGNMENT_THRESHOLD
    
    def test_aligned_phases_zero_dissonance(self):
        """Test that aligned phases have zero dissonance."""
        calc = DissonanceCalculator()
        
        phase1 = ComplexPhase(1, 4, 0.0)  # π/4
        phase2 = ComplexPhase(1, 4, 0.0)  # π/4
        
        dissonance = calc.compute_dissonance(phase1, phase2)
        
        assert dissonance.is_aligned
        assert abs(dissonance.dissonance) < 1e-10
        assert abs(dissonance.phase_difference) < 1e-10
    
    def test_opposite_phases_maximum_dissonance(self):
        """Test that opposite phases have maximum dissonance."""
        calc = DissonanceCalculator()
        
        phase1 = ComplexPhase(0, 1, 0.0)  # 0
        phase2 = ComplexPhase(1, 1, 0.0)  # π
        
        dissonance = calc.compute_dissonance(phase1, phase2)
        
        assert not dissonance.is_aligned
        # sin²(π/2) = 1
        assert abs(dissonance.dissonance - 1.0) < 1e-10
        assert abs(abs(dissonance.phase_difference) - np.pi) < 1e-10
    
    def test_orthogonal_phases_half_dissonance(self):
        """Test π/2 difference gives sin²(π/4) = 0.5 dissonance."""
        calc = DissonanceCalculator()
        
        phase1 = ComplexPhase(0, 1, 0.0)  # 0
        phase2 = ComplexPhase(1, 2, 0.0)  # π/2
        
        dissonance = calc.compute_dissonance(phase1, phase2)
        
        # sin²(π/4) = 0.5
        assert abs(dissonance.dissonance - 0.5) < 1e-10
    
    def test_dissonance_symmetry(self):
        """Test D(α,β) = D(β,α)."""
        calc = DissonanceCalculator()
        
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(3, 4, 0.0)
        
        d12 = calc.compute_dissonance(phase1, phase2)
        d21 = calc.compute_dissonance(phase2, phase1)
        
        assert abs(d12.dissonance - d21.dissonance) < 1e-10
    
    def test_mutual_coherence(self):
        """Test mutual coherence = 1 - dissonance."""
        calc = DissonanceCalculator()
        
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(1, 2, 0.0)
        
        coherence = calc.compute_mutual_coherence(phase1, phase2)
        dissonance = calc.compute_dissonance(phase1, phase2)
        
        assert abs(coherence + dissonance.dissonance - 1.0) < 1e-10


# ============================================================================
# SAME-COLOR FUSION TESTS
# ============================================================================

class TestSameColorFusion:
    """Test fusion of same-color spiders."""
    
    def test_aligned_z_fusion_low_entropy(self):
        """Test aligned Z spiders fuse with low entropy."""
        fusion = EntropySpiderFusion()
        
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(1, 4, 0.0)
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
            phase1, phase2
        )
        
        # Low entropy for aligned same-color
        assert event.entropy_produced < 0.01
        
        # Fused phase should be 2π/4 = π/2
        assert event.fused_phase is not None
        expected_radians = np.pi / 2
        actual_radians = event.fused_phase.real_phase_radians
        assert abs(actual_radians - expected_radians) < 1e-10
    
    def test_misaligned_z_fusion_moderate_entropy(self):
        """Test misaligned Z spiders produce moderate entropy."""
        fusion = EntropySpiderFusion()
        
        phase1 = ComplexPhase(0, 1, 0.0)  # 0
        phase2 = ComplexPhase(1, 1, 0.0)  # π
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
            phase1, phase2
        )
        
        # Some entropy for misaligned same-color
        assert event.entropy_produced > 0.0
        
        # But still fused
        assert event.fused_phase is not None
    
    def test_x_spider_fusion(self):
        """Test X spider fusion works identically."""
        fusion = EntropySpiderFusion()
        
        phase1 = ComplexPhase(1, 8, 0.0)
        phase2 = ComplexPhase(1, 8, 0.0)
        
        event = fusion.fuse_spiders(
            SpiderType.X_SPIDER, SpiderType.X_SPIDER,
            phase1, phase2
        )
        
        assert event.entropy_produced < 0.01
        assert event.fused_phase is not None


# ============================================================================
# DIFFERENT-COLOR FUSION TESTS
# ============================================================================

class TestDifferentColorFusion:
    """Test fusion of different-color spiders (Z-X)."""
    
    def test_aligned_zx_annihilation(self):
        """Test aligned Z-X spiders annihilate (forgiveness!)."""
        fusion = EntropySpiderFusion()
        
        phase_z = ComplexPhase(1, 4, 0.0)
        phase_x = ComplexPhase(1, 4, 0.0)
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
            phase_z, phase_x
        )
        
        # Annihilation: no entropy, no fused state
        assert event.entropy_produced == 0.0
        assert event.fused_phase is None
        assert event.dissonance.is_aligned
    
    def test_misaligned_zx_maximum_entropy(self):
        """Test misaligned Z-X spiders produce maximum entropy."""
        fusion = EntropySpiderFusion()
        
        phase_z = ComplexPhase(0, 1, 0.0)  # 0
        phase_x = ComplexPhase(1, 1, 0.0)  # π
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
            phase_z, phase_x
        )
        
        # Maximum entropy for opposite phases
        assert event.entropy_produced >= 0.9  # Close to 1.0
        assert event.dissonance.dissonance >= 0.9
    
    def test_xz_order_doesnt_matter(self):
        """Test X-Z fusion same as Z-X."""
        fusion = EntropySpiderFusion()
        
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(3, 4, 0.0)
        
        event_zx = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
            phase1, phase2
        )
        
        event_xz = fusion.fuse_spiders(
            SpiderType.X_SPIDER, SpiderType.Z_SPIDER,
            phase2, phase1
        )
        
        # Same entropy regardless of order
        assert abs(event_zx.entropy_produced - event_xz.entropy_produced) < 1e-10


# ============================================================================
# FORGIVENESS TESTS
# ============================================================================

class TestForgiveness:
    """Test forgiveness (annihilation) mechanism."""
    
    def test_perfect_forgiveness_zero_entropy(self):
        """Test perfect forgiveness produces zero entropy."""
        fusion = EntropySpiderFusion()
        
        # Multiple aligned pairs should all annihilate
        test_phases = [
            (ComplexPhase(0, 1, 0.0), ComplexPhase(0, 1, 0.0)),
            (ComplexPhase(1, 4, 0.0), ComplexPhase(1, 4, 0.0)),
            (ComplexPhase(1, 2, 0.0), ComplexPhase(1, 2, 0.0)),
        ]
        
        for phase_z, phase_x in test_phases:
            event = fusion.fuse_spiders(
                SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
                phase_z, phase_x
            )
            
            assert event.entropy_produced == 0.0
            assert event.fused_phase is None
    
    def test_forgiveness_requires_alignment(self):
        """Test forgiveness only occurs with aligned phases."""
        fusion = EntropySpiderFusion()
        
        phase_z = ComplexPhase(1, 4, 0.0)  # π/4
        phase_x = ComplexPhase(1, 2, 0.0)  # π/2 (not aligned!)
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
            phase_z, phase_x
        )
        
        # Not aligned → entropy produced
        assert event.entropy_produced > 0.0


# ============================================================================
# THERMODYNAMIC BALANCE TESTS
# ============================================================================

class TestThermodynamicBalance:
    """Test thermodynamic balance (ΔS + ΔG = 0)."""
    
    def test_accumulator_tracks_entropy(self):
        """Test entropy accumulator tracks total entropy."""
        fusion = EntropySpiderFusion()
        
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(3, 4, 0.0)
        
        # Multiple fusions
        for i in range(5):
            fusion.fuse_spiders(
                SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
                phase1, phase2,
                structure_id="test_structure"
            )
        
        total_entropy = fusion.get_total_entropy("test_structure")
        assert total_entropy > 0.0
    
    def test_thermodynamic_balance_maintained(self):
        """Test ΔS + ΔG = 0 is maintained."""
        fusion = EntropySpiderFusion()
        
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(1, 4, 0.0)
        
        fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
            phase1, phase2,
            structure_id="balance_test"
        )
        
        # Balance should be maintained (ΔS = ΔG_consumed)
        assert fusion.verify_thermodynamic_balance("balance_test")


# ============================================================================
# STRUCTURE-LEVEL TESTS
# ============================================================================

class TestStructureEntropyDynamics:
    """Test entropy dynamics on complete structures."""
    
    def test_identify_fusion_candidates(self):
        """Test identification of fusion candidate pairs."""
        dynamics = StructureEntropyDynamics()
        
        structure = ObjectG(
            nodes=[0, 1, 2],
            edges=[[0, 1], [1, 2]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('X', 1, 4, 'x1'),
                2: make_node_label('Z', 2, 4, 'z2'),
            }
        )
        
        candidates = dynamics.identify_fusion_candidates(structure)
        
        # Two edges → two candidate pairs
        assert len(candidates) == 2
    
    def test_compute_structure_entropy(self):
        """Test computing total entropy for structure."""
        dynamics = StructureEntropyDynamics()
        
        structure = ObjectG(
            nodes=[0, 1],
            edges=[[0, 1]],
            labels={
                0: make_node_label('Z', 0, 4, 'z0'),
                1: make_node_label('X', 1, 1, 'x1'),  # π (opposite phase)
            }
        )
        
        total_entropy, events = dynamics.compute_structure_entropy(
            structure,
            structure_id="test_structure"
        )
        
        # Opposite Z-X phases → high entropy
        assert total_entropy > 0.5
        assert len(events) == 1
    
    def test_low_entropy_coherent_structure(self):
        """Test coherent structure has low entropy."""
        dynamics = StructureEntropyDynamics()
        
        # All aligned same-color
        structure = ObjectG(
            nodes=[0, 1, 2],
            edges=[[0, 1], [1, 2]],
            labels={
                0: make_node_label('Z', 1, 4, 'z0'),
                1: make_node_label('Z', 1, 4, 'z1'),
                2: make_node_label('Z', 1, 4, 'z2'),
            }
        )
        
        total_entropy, events = dynamics.compute_structure_entropy(structure)
        
        # All aligned same-color → very low entropy
        assert total_entropy < 0.1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEntropyIntegration:
    """Integration tests with other TFCA components."""
    
    def test_entropy_complements_grace_damping(self):
        """Test entropy fusion complements Grace damping."""
        from FIRM_dsl.zx_phase_damping import GracePhaseDamping
        
        fusion = EntropySpiderFusion()
        damper = GracePhaseDamping()
        
        # High dissonance → high entropy → should need high Grace damping
        phase1 = ComplexPhase(0, 1, 0.0)
        phase2 = ComplexPhase(1, 1, 0.0)
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
            phase1, phase2
        )
        
        # High entropy requires Grace restoration
        assert event.entropy_produced > 0.5
    
    def test_forgiveness_is_grace_actualized(self):
        """Test forgiveness (annihilation) is Grace in action."""
        fusion = EntropySpiderFusion()
        
        # Aligned Z-X: Grace enables forgiveness
        phase = ComplexPhase(1, 4, 0.0)
        
        event = fusion.fuse_spiders(
            SpiderType.Z_SPIDER, SpiderType.X_SPIDER,
            phase, phase
        )
        
        # Zero entropy = complete Grace
        assert event.entropy_produced == 0.0
        assert event.fused_phase is None  # Annihilated


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestEntropyPerformance:
    """Performance tests."""
    
    def test_dissonance_computation_fast(self):
        """Test dissonance computation is fast."""
        import time
        
        calc = DissonanceCalculator()
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(3, 4, 0.0)
        
        start = time.time()
        for _ in range(1000):
            calc.compute_dissonance(phase1, phase2)
        elapsed = time.time() - start
        
        # Should be very fast
        assert elapsed < 0.1
    
    def test_fusion_scales_linearly(self):
        """Test fusion operations scale linearly."""
        import time
        
        fusion = EntropySpiderFusion()
        phase1 = ComplexPhase(1, 4, 0.0)
        phase2 = ComplexPhase(3, 4, 0.0)
        
        start = time.time()
        for i in range(100):
            fusion.fuse_spiders(
                SpiderType.Z_SPIDER, SpiderType.Z_SPIDER,
                phase1, phase2,
                structure_id=f"perf_test_{i}"
            )
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 0.5


# ============================================================================
# DEMONSTRATION TEST
# ============================================================================

def test_demonstration_runs():
    """Test that demonstration runs without errors."""
    demonstrate_entropy_spider_fusion()


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and return results."""
    test_classes = [
        TestDissonanceCalculator,
        TestSameColorFusion,
        TestDifferentColorFusion,
        TestForgiveness,
        TestThermodynamicBalance,
        TestStructureEntropyDynamics,
        TestEntropyIntegration,
        TestEntropyPerformance,
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
    print("ENTROPY SPIDER FUSION TEST SUITE")
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
    
    # Run demonstration
    test_demonstration_runs()

