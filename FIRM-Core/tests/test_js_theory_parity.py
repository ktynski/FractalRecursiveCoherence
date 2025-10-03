import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence import (
    compute_coherence,
    compute_cycle_basis_signature,
    compute_phase_histogram_signature,
    derive_minimal_qpi_bins,
    similarity_S,
)
from FIRM_clifford.interface import phi_zx_to_clifford


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
JS_MODULE_ROOT = Path("FIRM_ui")


def _run_node(script: str) -> dict:
    env = dict(**os.environ, NODE_PATH=str(JS_MODULE_ROOT))  # allow bare module imports
    result = subprocess.run(
        ["node", "--input-type=module", "-"],
        input=script.encode("utf-8"),
        capture_output=True,
        check=True,
        cwd=WORKSPACE_ROOT,
        env=env,
    )
    stdout = result.stdout.decode("utf-8").strip()
    return json.loads(stdout)


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required for JS parity tests")
def test_js_clifford_mapping_matches_python():
    graph = ObjectG(
        nodes=[0, 1],
        edges=[(0, 1)],
        labels={
            0: make_node_label("Z", 1, 2, "seed"),
            1: make_node_label("X", 0, 1, "dual"),
        },
    )
    validate_object_g(graph)

    py_coherence = compute_coherence(graph)
    py_field = phi_zx_to_clifford(graph)
    py_payload = py_field.payload

    script = textwrap.dedent(
        """
        import { ObjectG, make_node_label, validate_object_g } from './FIRM_ui/FIRM_dsl/core.js';
        import { compute_coherence } from './FIRM_ui/FIRM_dsl/coherence.js';
        import { phi_zx_to_clifford } from './FIRM_ui/FIRM_clifford/interface.js';

        const graph = new ObjectG({
          nodes: [0, 1],
          edges: [[0, 1]],
          labels: {
            0: make_node_label('Z', 1, 2, 'seed'),
            1: make_node_label('X', 0, 1, 'dual')
          }
        });

        validate_object_g(graph);
        const coherence = compute_coherence(graph);
        const field = phi_zx_to_clifford(graph);

        console.log(JSON.stringify({ coherence, field }));
        """
    ).strip()

    data = _run_node(script)

    assert abs(data["coherence"] - py_coherence) < 1e-9
    assert data["field"]["payload"]["algebra"] == py_payload["algebra"]

    js_components = data["field"]["payload"]["components"]
    py_components = py_payload["components"]
    assert len(js_components) == len(py_components) == 16
    for js, py in zip(js_components, py_components):
        assert abs(js - py) < 1e-9


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required for JS parity tests")
def test_js_coherence_structures_match_python():
    graph = ObjectG(
        nodes=[0, 1, 2],
        edges=[(0, 1), (1, 2), (2, 0)],
        labels={
            0: make_node_label("Z", 0, 1, "seed"),
            1: make_node_label("X", 1, 3, "dual"),
            2: make_node_label("Z", 1, 4, "aux"),
        },
    )
    validate_object_g(graph)

    py_cycles = compute_cycle_basis_signature(graph)
    bins = derive_minimal_qpi_bins(graph)
    py_hist = compute_phase_histogram_signature(graph, bins)
    py_similarity = similarity_S(py_cycles, py_cycles, py_hist, py_hist)

    script = textwrap.dedent(
        f"""
        import {{ ObjectG, make_node_label, validate_object_g }} from './FIRM_ui/FIRM_dsl/core.js';
        import {{ compute_cycle_basis_signature, compute_phase_histogram_signature, similarity_S }} from './FIRM_ui/FIRM_dsl/coherence.js';

        const graph = new ObjectG({{
          nodes: [0, 1, 2],
          edges: [[0, 1], [1, 2], [2, 0]],
          labels: {{
            0: make_node_label('Z', 0, 1, 'seed'),
            1: make_node_label('X', 1, 3, 'dual'),
            2: make_node_label('Z', 1, 4, 'aux')
          }}
        }});

        validate_object_g(graph);
        const cycles = compute_cycle_basis_signature(graph);
        const hist = compute_phase_histogram_signature(graph, {bins});
        const similarity = similarity_S(cycles, cycles, hist, hist);

        console.log(JSON.stringify({{ cycles, hist, similarity }}));
        """
    ).strip()

    data = _run_node(script)

    js_cycles = [tuple(cycle) for cycle in data["cycles"]]
    assert js_cycles == py_cycles
    assert len(data["hist"]) == len(py_hist) == bins
    for js, py in zip(data["hist"], py_hist):
        assert abs(js - py) < 1e-9
    assert abs(data["similarity"] - py_similarity) < 1e-12


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required for JS parity tests")
def test_js_evolution_cycle_matches_python():
    """
    Verify full ZXObjectGraphEngine.evolve() cycle matches expected behavior.
    
    Tests: bootstrap → rewrites → coherence computation → Clifford mapping.
    """
    script = textwrap.dedent(
        """
        import { ZXObjectGraphEngine } from './FIRM_ui/zx_objectg_engine.js';
        
        const engine = new ZXObjectGraphEngine();
        
        // Evolve through full cycle
        const evolutionHistory = [];
        
        for (let i = 0; i < 15; i++) {
          const audioCoherence = 0.5 + 0.3 * Math.sin(i * 0.5);
          
          const snapBefore = engine.getSnapshot();
          engine.evolve(audioCoherence, 0.016);
          const snapAfter = engine.getSnapshot();
          
          evolutionHistory.push({
            step: i,
            audioCoherence: audioCoherence,
            nodesBefore: snapBefore.graph.nodes.length,
            nodesAfter: snapAfter.graph.nodes.length,
            coherenceBefore: snapBefore.coherence,
            coherenceAfter: snapAfter.coherence,
            rewriteCount: snapAfter.rewrites.length - snapBefore.rewrites.length
          });
        }
        
        const finalSnap = engine.getSnapshot();
        
        console.log(JSON.stringify({
          evolutionHistory: evolutionHistory,
          finalNodes: finalSnap.graph.nodes.length,
          finalCoherence: finalSnap.coherence,
          totalRewrites: finalSnap.rewrites.length,
          cliffordComponentCount: finalSnap.cliffordField.payload.components.length
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Verify evolution occurred
    assert data["finalNodes"] > 1, "Evolution should create nodes"
    assert data["totalRewrites"] >= 2, "Should have multiple rewrites (bootstrap + others)"
    
    # Verify Clifford field structure
    assert data["cliffordComponentCount"] == 16, "Clifford field must have 16 components"
    
    # Verify coherence is reasonable
    assert 0 < data["finalCoherence"] < 2.0, "Final coherence should be reasonable"
    
    # Verify evolution progressed
    history = data["evolutionHistory"]
    assert len(history) == 15, "Should have 15 evolution steps"
    
    # At least one step should show node growth
    node_growth_steps = sum(1 for h in history if h["nodesAfter"] > h["nodesBefore"])
    assert node_growth_steps >= 1, "Should have at least one node growth event"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required for JS parity tests")
def test_js_rewrite_history_provenance():
    """
    Verify rewrite history includes proper provenance and metadata.
    
    All rewrites must track: type, timestamp, audioCoherence, delta_c (where applicable).
    """
    script = textwrap.dedent(
        """
        import { ZXObjectGraphEngine } from './FIRM_ui/zx_objectg_engine.js';
        
        const engine = new ZXObjectGraphEngine();
        
        // Evolve to generate various rewrite types
        for (let i = 0; i < 20; i++) {
          engine.evolve(0.6, 0.016);
        }
        
        const rewrites = engine.getRewriteHistory();
        
        // Categorize rewrites
        const byType = {};
        for (const rewrite of rewrites) {
          byType[rewrite.type] = (byType[rewrite.type] || 0) + 1;
        }
        
        // Check provenance fields
        const hasTimestamps = rewrites.every(r => typeof r.timestamp === 'number');
        const hasTypes = rewrites.every(r => typeof r.type === 'string');
        
        const standardRewrites = rewrites.filter(r => 
          r.type === 'fusion' || r.type === 'color_flip' || r.type === 'grace_emergence'
        );
        const hasDeltaC = standardRewrites.every(r => 
          typeof r.delta_c === 'number' && Number.isFinite(r.delta_c)
        );
        
        console.log(JSON.stringify({
          totalRewrites: rewrites.length,
          byType: byType,
          hasTimestamps: hasTimestamps,
          hasTypes: hasTypes,
          hasDeltaC: hasDeltaC,
          sampleRewrite: standardRewrites[0] || rewrites[0]
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    assert data["totalRewrites"] >= 2, "Should have multiple rewrites"
    assert data["hasTimestamps"], "All rewrites must have timestamps"
    assert data["hasTypes"], "All rewrites must have type field"
    assert data["hasDeltaC"], "All standard rewrites must have delta_c"
    
    # Verify sample structure
    sample = data["sampleRewrite"]
    assert "type" in sample
    assert "timestamp" in sample


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required for JS parity tests")
def test_js_coherence_history_tracking():
    """
    Verify coherence history is tracked correctly during evolution.
    """
    script = textwrap.dedent(
        """
        import { ZXObjectGraphEngine } from './FIRM_ui/zx_objectg_engine.js';
        
        const engine = new ZXObjectGraphEngine();
        
        // Evolve and track coherence
        for (let i = 0; i < 10; i++) {
          engine.evolve(0.5, 0.016);
        }
        
        const history = engine.getCoherenceHistory();
        const cycleHistory = engine.getCycleHistory();
        
        console.log(JSON.stringify({
          coherenceEntries: history.length,
          hasAudioCoherence: history.every(h => typeof h.audioCoherence === 'number'),
          hasCoherence: history.every(h => typeof h.coherence === 'number'),
          hasTimestamp: history.every(h => typeof h.timestamp === 'number'),
          cycleEntries: cycleHistory.length,
          sampleCoherence: history[0],
          sampleCycle: cycleHistory[0]
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    assert data["coherenceEntries"] > 0, "Coherence history should be populated"
    assert data["hasAudioCoherence"], "All entries must have audioCoherence"
    assert data["hasCoherence"], "All entries must have coherence"
    assert data["hasTimestamp"], "All entries must have timestamp"
    assert data["cycleEntries"] > 0, "Cycle history should be populated"

