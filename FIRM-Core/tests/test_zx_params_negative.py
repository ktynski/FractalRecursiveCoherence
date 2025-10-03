"""Negative validation tests for ZX host params.
"""
import importlib
import pytest


def test_params_validation_rejects_non_positive_values():
    hp = importlib.import_module('FIRM_zx.host_params')
    # max_spiders <= 0
    with pytest.raises(ValueError):
        hp.validate_params(hp.Params(max_spiders=0, bins_qpi=8))
    # bins_qpi <= 0
    with pytest.raises(ValueError):
        hp.validate_params(hp.Params(max_spiders=1, bins_qpi=0))


