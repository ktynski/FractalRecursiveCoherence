"""Tests for identity echo time τ from coherence time series and θ.

Covers single-run first passage, multi-run expectation over finite values,
and never-crossing behavior returning +inf.
"""
import importlib
import math


def test_tau_single_run_first_passage():
    coh = importlib.import_module('FIRM_dsl.coherence')
    theta = 0.5
    series = [0.9, 0.8, 0.7, 0.6, 0.49, 0.48]
    tau = coh.compute_identity_echo_time_tau({'coherence': series, 'theta': theta})
    assert tau == 4.0  # first index where C_t < θ is t=4


def test_tau_multiple_runs_mean_over_finite():
    coh = importlib.import_module('FIRM_dsl.coherence')
    theta = 0.3
    runs = [
        [0.9, 0.2],            # τ=1
        [0.5, 0.4, 0.29],      # τ=2
        [0.31, 0.3001, 0.3000] # τ=math.inf (never strictly below θ)
    ]
    tau = coh.compute_identity_echo_time_tau({'coherence_runs': runs, 'theta': theta})
    # Mean over finite {1, 2} = 1.5
    assert abs(tau - 1.5) < 1e-12


def test_tau_never_crossing_returns_inf():
    coh = importlib.import_module('FIRM_dsl.coherence')
    theta = 0.1
    series = [0.9, 0.8, 0.7]
    tau = coh.compute_identity_echo_time_tau({'coherence': series, 'theta': theta})
    assert tau == math.inf


