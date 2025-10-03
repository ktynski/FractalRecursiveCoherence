"""DSL error-path coverage for Qπ arithmetic, graph validation, and utilities.

Systematic negative tests ensure explicit failures instead of silent fallbacks.
"""
import importlib
import pytest


def test_validate_object_g_rejects_self_loops_and_unknown_nodes():
    core = importlib.import_module('FIRM_dsl.core')
    # Self-loop
    g_self = core.ObjectG(nodes=[0], edges=[(0, 0)], labels={0: core.make_node_label('Z', 0, 1, 'm0')})
    with pytest.raises(ValueError):
        core.validate_object_g(g_self)

    # Unknown node in edge
    g_unknown_edge = core.ObjectG(nodes=[0], edges=[(0, 1)], labels={0: core.make_node_label('Z', 0, 1, 'm0')})
    with pytest.raises(ValueError):
        core.validate_object_g(g_unknown_edge)

    # Unknown node in label
    g_unknown_label = core.ObjectG(nodes=[0], edges=[], labels={1: core.make_node_label('Z', 0, 1, 'm1')})
    with pytest.raises(ValueError):
        core.validate_object_g(g_unknown_label)


def test_validate_object_g_rejects_non_normalized_phases():
    core = importlib.import_module('FIRM_dsl.core')
    # Create a label with non-normalized phase then bypass factory to simulate invalid input
    NodeLabel = core.NodeLabel
    lbl = NodeLabel(kind='Z', phase_numer=2, phase_denom=4, monadic_id='m0')  # should normalize to 1/2
    g = core.ObjectG(nodes=[0], edges=[], labels={0: lbl})
    with pytest.raises(ValueError):
        core.validate_object_g(g)


def test_phase_to_bin_index_requires_exact_qpi_partition():
    core = importlib.import_module('FIRM_dsl.core')
    # denom = 4 → bins must be multiple of 8
    with pytest.raises(ValueError):
        core.phase_to_bin_index(1, 4, 6)
    # valid case does not raise
    idx = core.phase_to_bin_index(1, 4, 8)
    assert isinstance(idx, int)


def test_compute_phase_histogram_signature_requires_lcm_multiple():
    core = importlib.import_module('FIRM_dsl.core')
    coh = importlib.import_module('FIRM_dsl.coherence')
    g = core.ObjectG(
        nodes=[0, 1],
        edges=[(0, 1)],
        labels={
            0: core.make_node_label('Z', 1, 4, 'm0'),
            1: core.make_node_label('X', 1, 2, 'm1'),
        },
    )
    # LCM(4,2) = 4 → bins must be multiple of 8
    with pytest.raises(ValueError):
        coh.compute_phase_histogram_signature(g, 6)
    hist = coh.compute_phase_histogram_signature(g, 8)
    assert len(hist) == 8
    assert abs(sum(hist) - 1.0) < 1e-12


def test_lcm_many_negative_inputs_and_empty_raise():
    core = importlib.import_module('FIRM_dsl.core')
    with pytest.raises(ValueError):
        core.lcm_many([])
    with pytest.raises(ValueError):
        core.lcm_many([2, 0])
    with pytest.raises(ValueError):
        core.lcm_many([-1, 2])


