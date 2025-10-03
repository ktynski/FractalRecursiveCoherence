"""
Test suite for metamirror bireflection operator.

Validates implementation against FIRM_theory/metamirror_bireflection_derivation.md.
"""

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
JS_MODULE_ROOT = Path("FIRM_ui")


def _run_node(script: str) -> dict:
    """Execute Node.js script and return parsed JSON output."""
    env = dict(**os.environ, NODE_PATH=str(JS_MODULE_ROOT))
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


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_metamirror_involution_property():
    """
    Verify β(β(G)) = G (involution property).
    
    From metamirror_bireflection_derivation.md Section 1.1:
    Bireflection is self-inverse: β ∘ β = 1_A.
    """
    script = textwrap.dedent(
        """
        import { CoherenceDeltaScaffold } from './FIRM_zx/rules.js';
        
        const scaffold = new CoherenceDeltaScaffold();
        
        // Create test graph
        const graph = {
          nodes: [0, 1, 2],
          edges: [[0, 1], [1, 2]],
          labels: {
            0: { kind: 'Z', phase_numer: 1, phase_denom: 2, monadic_id: 'test_z' },
            1: { kind: 'X', phase_numer: 0, phase_denom: 1, monadic_id: 'test_x' },
            2: { kind: 'Z', phase_numer: 3, phase_denom: 4, monadic_id: 'test_z2' }
          }
        };
        
        // Apply metamirror twice
        const mirror1 = scaffold.compute_metamirror_state(null, graph);
        const mirror2 = scaffold.compute_metamirror_state(null, mirror1);
        
        // Extract labels for comparison
        const originalLabels = Object.entries(graph.labels).map(([id, l]) => ({
          id, kind: l.kind, phase_numer: l.phase_numer, phase_denom: l.phase_denom
        }));
        
        const mirror2Labels = Object.entries(mirror2.labels).map(([id, l]) => ({
          id, kind: l.kind, phase_numer: l.phase_numer, phase_denom: l.phase_denom
        }));
        
        console.log(JSON.stringify({
          original: originalLabels,
          mirror2: mirror2Labels
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # After two bireflections, should return to original
    orig = data["original"]
    mir2 = data["mirror2"]
    
    assert len(orig) == len(mir2), "Node count should be preserved"
    
    for i in range(len(orig)):
        assert orig[i]["kind"] == mir2[i]["kind"], \
            f"Node {i}: kind mismatch after double reflection"
        assert orig[i]["phase_numer"] == mir2[i]["phase_numer"], \
            f"Node {i}: phase_numer should be preserved"
        assert orig[i]["phase_denom"] == mir2[i]["phase_denom"], \
            f"Node {i}: phase_denom should be preserved"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_metamirror_color_flip():
    """
    Verify metamirror flips spider colors: Z ↔ X.
    
    From metamirror_bireflection_derivation.md Section 2.2:
    β(Z) = X and β(X) = Z.
    """
    script = textwrap.dedent(
        """
        import { CoherenceDeltaScaffold } from './FIRM_zx/rules.js';
        
        const scaffold = new CoherenceDeltaScaffold();
        
        const graph = {
          nodes: [0, 1],
          edges: [[0, 1]],
          labels: {
            0: { kind: 'Z', phase_numer: 0, phase_denom: 1, monadic_id: 'z_node' },
            1: { kind: 'X', phase_numer: 1, phase_denom: 4, monadic_id: 'x_node' }
          }
        };
        
        const mirror = scaffold.compute_metamirror_state(null, graph);
        
        console.log(JSON.stringify({
          original_z_kind: graph.labels[0].kind,
          original_x_kind: graph.labels[1].kind,
          mirror_z_kind: mirror.labels[0].kind,
          mirror_x_kind: mirror.labels[1].kind
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Z should flip to X
    assert data["original_z_kind"] == "Z"
    assert data["mirror_z_kind"] == "X"
    
    # X should flip to Z
    assert data["original_x_kind"] == "X"
    assert data["mirror_x_kind"] == "Z"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_metamirror_phase_preservation():
    """
    Verify metamirror preserves phases (involution property).
    
    From metamirror_bireflection_derivation.md Section 2.2:
    Phases unchanged under bireflection.
    """
    script = textwrap.dedent(
        """
        import { CoherenceDeltaScaffold } from './FIRM_zx/rules.js';
        
        const scaffold = new CoherenceDeltaScaffold();
        
        const graph = {
          nodes: [0, 1, 2],
          edges: [[0, 1], [1, 2]],
          labels: {
            0: { kind: 'Z', phase_numer: 1, phase_denom: 8, monadic_id: 'a' },
            1: { kind: 'X', phase_numer: 3, phase_denom: 8, monadic_id: 'b' },
            2: { kind: 'Z', phase_numer: 5, phase_denom: 8, monadic_id: 'c' }
          }
        };
        
        const mirror = scaffold.compute_metamirror_state(null, graph);
        
        const phases = [];
        for (const nodeId of [0, 1, 2]) {
          phases.push({
            original: graph.labels[nodeId].phase_numer / graph.labels[nodeId].phase_denom,
            mirror: mirror.labels[nodeId].phase_numer / mirror.labels[nodeId].phase_denom
          });
        }
        
        console.log(JSON.stringify({ phases }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # All phases should be preserved
    for i, phase_pair in enumerate(data["phases"]):
        assert abs(phase_pair["original"] - phase_pair["mirror"]) < 1e-9, \
            f"Node {i}: phase should be preserved under bireflection"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_metamirror_structure_preservation():
    """
    Verify metamirror preserves graph structure (nodes and edges).
    
    From metamirror_bireflection_derivation.md Section 2.2:
    Nodes and edges unchanged, only labels transformed.
    """
    script = textwrap.dedent(
        """
        import { CoherenceDeltaScaffold } from './FIRM_zx/rules.js';
        
        const scaffold = new CoherenceDeltaScaffold();
        
        const graph = {
          nodes: [0, 1, 2, 3],
          edges: [[0, 1], [1, 2], [2, 3], [3, 0]],
          labels: {
            0: { kind: 'Z', phase_numer: 0, phase_denom: 1, monadic_id: 'a' },
            1: { kind: 'X', phase_numer: 1, phase_denom: 2, monadic_id: 'b' },
            2: { kind: 'Z', phase_numer: 1, phase_denom: 4, monadic_id: 'c' },
            3: { kind: 'X', phase_numer: 3, phase_denom: 4, monadic_id: 'd' }
          }
        };
        
        const mirror = scaffold.compute_metamirror_state(null, graph);
        
        console.log(JSON.stringify({
          original_nodes: graph.nodes,
          mirror_nodes: mirror.nodes,
          original_edges: graph.edges,
          mirror_edges: mirror.edges
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Nodes should be identical
    assert data["original_nodes"] == data["mirror_nodes"], \
        "Metamirror should preserve nodes"
    
    # Edges should be identical
    assert len(data["original_edges"]) == len(data["mirror_edges"]), \
        "Metamirror should preserve edge count"
    
    for i in range(len(data["original_edges"])):
        assert data["original_edges"][i] == data["mirror_edges"][i], \
            f"Edge {i} should be preserved"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_metamirror_color_count_swap():
    """
    Verify Z-count and X-count swap under bireflection.
    
    From metamirror_bireflection_derivation.md Section 9.1:
    Z-count(G) = X-count(β(G)) and vice versa.
    """
    script = textwrap.dedent(
        """
        import { CoherenceDeltaScaffold } from './FIRM_zx/rules.js';
        
        const scaffold = new CoherenceDeltaScaffold();
        
        const graph = {
          nodes: [0, 1, 2, 3, 4],
          edges: [[0, 1], [1, 2], [2, 3], [3, 4]],
          labels: {
            0: { kind: 'Z', phase_numer: 0, phase_denom: 1, monadic_id: 'a' },
            1: { kind: 'Z', phase_numer: 0, phase_denom: 1, monadic_id: 'b' },
            2: { kind: 'X', phase_numer: 0, phase_denom: 1, monadic_id: 'c' },
            3: { kind: 'Z', phase_numer: 0, phase_denom: 1, monadic_id: 'd' },
            4: { kind: 'X', phase_numer: 0, phase_denom: 1, monadic_id: 'e' }
          }
        };
        
        const mirror = scaffold.compute_metamirror_state(null, graph);
        
        const countKinds = (labels) => {
          const counts = { Z: 0, X: 0 };
          for (const label of Object.values(labels)) {
            counts[label.kind]++;
          }
          return counts;
        };
        
        const originalCounts = countKinds(graph.labels);
        const mirrorCounts = countKinds(mirror.labels);
        
        console.log(JSON.stringify({
          original: originalCounts,
          mirror: mirrorCounts
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Z and X counts should swap
    assert data["original"]["Z"] == data["mirror"]["X"], \
        "Original Z-count should equal mirror X-count"
    assert data["original"]["X"] == data["mirror"]["Z"], \
        "Original X-count should equal mirror Z-count"

