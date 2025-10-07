#!/usr/bin/env python3
"""
Quick test script for the Monad Listener system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.models.monad_listener import MonadListener
from src.models.constraints import ConstraintSystem, ConstraintAuditor
from src.loaders.dataset_generators import DomainLoader

def test_monad_listener():
    """Test the core Monad Listener system"""
    print("🧪 Testing Monad Listener System...")

    # Test initialization
    model = MonadListener(latent_dim=20)
    print(f"✅ Model initialized with {len(model.heads)} heads")

    # Test measurement functor
    loader = DomainLoader()
    datasets = loader.load_all_datasets(10)  # Small test set

    # Test with sample field data
    test_field = {
        'payload': {
            'components': [0.5, 0.3, 0.2, 0.1, 0.4, 0.3, 0.2, 0.1, 0.2, 0.1, 0.05, 0.15, 0.1, 0.08, 0.05, 0.03]
        }
    }

    columns = model.measurement_functor(test_field)
    print(f"✅ Measurement functor computed {len(columns)} columns")

    # Test final description
    final_desc = model.compute_final_description(test_field)
    print(f"✅ Final description: coherence={final_desc.get('coherence', 0):.".3f"")

    return True

def test_constraint_system():
    """Test the constraint system"""
    print("\n🔍 Testing Constraint System...")

    # Test constraint system
    constraint_system = ConstraintSystem()
    print(f"✅ Constraint system initialized with {len(constraint_system.constraints)} constraints")

    # Test with sample columns
    sample_columns = {
        'zx_phase_group': 'Clifford_group',
        'lie_algebra_generator': 'su2_pauli',
        'frobenius_algebra_role': 'comonoid',
        'tensor_rank_type': '(1,1)_tensor',
        'field_theory_analog': 'electromagnetic_field'
    }

    results = constraint_system.check_all_constraints(sample_columns)
    print(f"✅ Constraint check completed: {sum(results.values())}/{len(results)} passed")

    return True

def test_datasets():
    """Test dataset generation"""
    print("\n📊 Testing Dataset Generators...")

    loader = DomainLoader()

    # Test quantum dataset
    quantum_data = loader.load_dataset('quantum', 5)
    print(f"✅ Quantum dataset: {len(quantum_data)} samples")

    # Test CA dataset
    ca_data = loader.load_dataset('ca', 5)
    print(f"✅ CA dataset: {len(ca_data)} samples")

    return True

def main():
    """Run all tests"""
    print("🎯 Monad Listener System Test Suite")
    print("=" * 50)

    try:
        test_monad_listener()
        test_constraint_system()
        test_datasets()

        print("\n🎉 All tests passed!")
        print("✅ Monad Listener system is ready for empirical validation")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
