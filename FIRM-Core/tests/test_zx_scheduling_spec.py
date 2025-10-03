"""Spec test verifying ZX scheduling by ΔC ordering."""
import importlib


def test_schedule_rewrites_by_delta_c_orders_descending():
    rules = importlib.import_module('FIRM_zx.rules')
    sched = rules.CoherenceDeltaScaffold()
    candidates = [
        {"type": "fusion", "delta_c": 0.1},
        {"type": "flip", "delta_c": 0.3},
        {"type": "fusion", "delta_c": 0.2},
        {"type": "invalid", "delta_c": None},
    ]
    ordered = sched.schedule_rewrites_by_delta_c(candidates)
    deltas = [c.get('delta_c') for c in ordered]
    assert deltas == [0.3, 0.2, 0.1]

