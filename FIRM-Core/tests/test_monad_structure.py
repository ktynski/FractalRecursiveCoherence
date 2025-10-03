"""Monad identity and Grace operator structural tests.

These tests are structure-only and align with current raising boundaries.
"""
import importlib


def test_f_pullback_and_pushforward_identity_on_sheaf_instances():
    monad = importlib.import_module('FIRM_dsl.monad')
    sheaf_mod = importlib.import_module('FIRM_dsl.sheaf')

    s = sheaf_mod.Sheaf(values_on_objects={})
    s_pull = monad.f_pullback(s)
    s_push = monad.f_pushforward(s)

    assert isinstance(s_pull, sheaf_mod.Sheaf)
    assert isinstance(s_push, sheaf_mod.Sheaf)

    # MonadT composition preserves type
    T = monad.MonadT()
    s_T = T(s)
    assert isinstance(s_T, sheaf_mod.Sheaf)


def test_grace_operator_structure_and_application_returns_sheaf():
    monad = importlib.import_module('FIRM_dsl.monad')
    sheaf_mod = importlib.import_module('FIRM_dsl.sheaf')

    grace = monad.GraceOperatorStructure()

    idem = grace.validate_idempotent_structure(3)
    assert idem['is_idempotent'] is True and idem['domain_size'] == 3 and idem['codomain_size'] == 3

    adj = grace.validate_left_adjoint_structure(2)
    assert adj['has_left_adjoint_structure'] is True

    incoherent = {'coherence_level': 0.0}
    rest = grace.validate_coherence_restoration(incoherent)
    assert rest['can_restore'] is True and rest['preserves_history'] is True

    s = sheaf_mod.Sheaf(values_on_objects={})
    s_restored = grace.apply_grace_operator(s)
    assert isinstance(s_restored, sheaf_mod.Sheaf)


