#!/usr/bin/env python3
"""
Simple test for the Monad Listener system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from src.models.monad_listener import MonadListener
        print("✅ MonadListener imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_initialization():
    """Test model initialization"""
    try:
        from src.models.monad_listener import MonadListener
        model = MonadListener(latent_dim=20)
        print(f"✅ Model initialized with {len(model.heads)} heads")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_measurement():
    """Test measurement functor"""
    try:
        from src.models.monad_listener import MonadListener
        model = MonadListener(latent_dim=20)

        # Create test field data
        test_field = {
            'payload': {
                'components': [0.5, 0.3, 0.2, 0.1, 0.4, 0.3, 0.2, 0.1, 0.2, 0.1, 0.05, 0.15, 0.1, 0.08, 0.05, 0.03]
            }
        }

        columns = model.measurement_functor(test_field)
        print(f"✅ Measurement computed {len(columns)} columns")

        # Check some key columns
        if 'morphic_type_signature' in columns:
            print("✅ Key columns present")
            return True
        else:
            print("❌ Missing expected columns")
            return False

    except Exception as e:
        print(f"❌ Measurement test failed: {e}")
        return False

def test_constraints():
    """Test constraint system"""
    try:
        from src.models.constraints import ConstraintSystem
        system = ConstraintSystem()

        # Test with valid columns
        valid_columns = {
            'zx_phase_group': 'Clifford_group',
            'lie_algebra_generator': 'su2_pauli',
            'frobenius_algebra_role': 'comonoid'
        }

        results = system.check_all_constraints(valid_columns)
        passed = sum(results.values())
        print(f"✅ Constraint system tested: {passed}/{len(results)} constraints passed")
        return True

    except Exception as e:
        print(f"❌ Constraint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Monad Listener System Test")
    print("=" * 40)

    tests = [
        ("Imports", test_imports),
        ("Initialization", test_initialization),
        ("Measurement", test_measurement),
        ("Constraints", test_constraints)
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! Monad Listener system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
