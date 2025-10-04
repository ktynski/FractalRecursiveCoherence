import math

import pytest

from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.grace_field import (
    GraceFieldParams,
    potential_V,
    dV_du,
    FieldRegime,
    recursion_depth_classification,
    coherence_density,
    resonant_source_term,
)
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment


def build_graph_single(seed_kind='Z', phase=(0, 1)):
    nid = 0
    lbl = make_node_label(seed_kind, phase[0], phase[1], 'seed')
    g = ObjectG(nodes=[nid], edges=[], labels={nid: lbl})
    return validate_object_g(g)


def build_graph_chain(phases):
    nodes = list(range(len(phases)))
    edges = [[i, i + 1] for i in range(len(phases) - 1)]
    labels = {}
    for i, (kind, (pn, pd)) in enumerate(phases):
        labels[i] = make_node_label(kind, pn, pd, f'n{i}')
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def test_grace_params_sign_constraints():
    with pytest.raises(ValueError):
        GraceFieldParams(alpha=0.0, beta=1.0, gamma=0.0)
    with pytest.raises(ValueError):
        GraceFieldParams(alpha=1.0, beta=0.0, gamma=0.0)
    p = GraceFieldParams(alpha=1.0, beta=2.0, gamma=0.5)
    assert p.alpha > 0 and p.beta > 0


def test_potential_and_derivative_domain_and_forms():
    p = GraceFieldParams(alpha=1.0, beta=2.0, gamma=0.5)
    with pytest.raises(ValueError):
        potential_V(-1e-6, p)
    with pytest.raises(ValueError):
        dV_du(-1e-6, p)
    # Simple value checks
    u = 0.0
    assert potential_V(u, p) == 0.0
    assert dV_du(u, p) == pytest.approx(p.alpha)
    u = 1.0
    V = potential_V(u, p)
    dV = dV_du(u, p)
    assert isinstance(V, float) and isinstance(dV, float)


def test_recursion_depth_classification():
    assert recursion_depth_classification(0) == FieldRegime.NON_BEING
    assert recursion_depth_classification(1) == FieldRegime.VACUUM
    assert recursion_depth_classification(2) == FieldRegime.DARK_SECTOR
    assert recursion_depth_classification(3) == FieldRegime.DARK_SECTOR
    assert recursion_depth_classification(4) == FieldRegime.MATTER
    assert recursion_depth_classification(100) == FieldRegime.MATTER
    assert recursion_depth_classification(math.inf) == FieldRegime.OMEGA
    with pytest.raises(ValueError):
        recursion_depth_classification(-1)
    with pytest.raises(ValueError):
        recursion_depth_classification(1.5)


def test_coherence_density_non_negative_and_additive():
    assert coherence_density(0.0, 0.0) == 0.0
    assert coherence_density(1.0, 2.0) == 3.0
    with pytest.raises(ValueError):
        coherence_density(-1.0, 0.0)
    with pytest.raises(ValueError):
        coherence_density(0.0, -1.0)


def test_resonance_alignment_bounds_and_identity():
    g1 = build_graph_chain([
        ('Z', (0, 1)),
        ('X', (1, 4)),
        ('Z', (1, 8)),
    ])
    omega = derive_omega_signature(g1)
    r11 = compute_resonance_alignment(g1, omega)
    assert 0.0 <= r11 <= 1.0
    assert r11 == pytest.approx(1.0, rel=1e-12, abs=1e-12)

    # A different graph should have resonance ≤ 1 and typically < 1
    g2 = build_graph_chain([
        ('Z', (1, 8)),
        ('X', (1, 8)),
        ('Z', (3, 8)),
    ])
    r21 = compute_resonance_alignment(g2, omega)
    assert 0.0 <= r21 <= 1.0
    # Not asserting strictly < 1 to allow degenerate equal signatures


def test_resonant_source_term_linear_in_lambda():
    g = build_graph_single('Z', (0, 1))
    omega = derive_omega_signature(g)
    r = compute_resonance_alignment(g, omega)
    s1 = resonant_source_term(omega, g, lam=1.0)
    s2 = resonant_source_term(omega, g, lam=2.0)
    assert s1 == pytest.approx(r)
    assert s2 == pytest.approx(2.0 * r)


