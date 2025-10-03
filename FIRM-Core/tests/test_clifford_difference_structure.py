"""Structural tests for Clifford difference operator and spectral gap preconditions.

Focus on validators present in FIRM_clifford.interface without executing unimplemented ops.
"""
import importlib


def test_difference_operator_and_spectral_gap_structure():
    iface = importlib.import_module('FIRM_clifford.interface')
    validator = iface.DiscreteDiracMassValidator()

    prev_sig = {"algebra": "Cl(1,3)", "dimension": 16}
    curr_sig = {"algebra": "Cl(1,3)", "dimension": 16}

    diff_val = validator.validate_difference_operator_structure(prev_sig, curr_sig)
    assert diff_val["difference_operator_valid"] is True
    assert diff_val["preserves_clifford_structure"] is True

    spec_val = validator.validate_spectral_gap_structure({"difference_operator_valid": True, "algebra": "Cl(1,3)"})
    assert spec_val["has_discrete_spectrum"] is True
    assert spec_val["first_eigenvalue_is_mass"] is True


