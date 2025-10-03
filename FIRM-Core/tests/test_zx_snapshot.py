import importlib
import pytest

try:
    engine_mod = importlib.import_module('FIRM_ui.zx_objectg_engine')
except ModuleNotFoundError:
    pytest.skip('ZXObjectGraphEngine JS module not importable in Python environment', allow_module_level=True)


def test_zx_snapshot_matches_clifford_mapping():
    zx_engine = engine_mod.ZXObjectGraphEngine()

    # Seed graph and evolve once to populate histories
    zx_engine.reset()
    zx_engine.evolve(audioCoherence=0.25)

    snapshot = zx_engine.getSnapshot()
    direct = zx_engine.mapToCliffordField()

    assert 'graph' in snapshot and 'cliffordField' in snapshot
    assert snapshot['graph'] == zx_engine.getCurrentGraph()

    assert snapshot['cliffordField'].payload['algebra'] == 'Cl(1,3)'
    assert len(snapshot['cliffordField'].payload['components']) == 16
    assert snapshot['cliffordField'].payload == direct.payload
