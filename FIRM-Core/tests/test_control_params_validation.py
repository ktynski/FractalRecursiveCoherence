"""
Test suite for control parameters validation and provenance.

Validates implementation against FIRM_theory/control_parameters_specification.md.
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
def test_control_params_defaults():
    """
    Verify default control parameters match specification.
    
    From control_parameters_specification.md Section 2.1.
    """
    script = textwrap.dedent(
        """
        import { ControlParamsValidator } from './FIRM_ui/control_params.js';
        
        const { validated, provenance } = ControlParamsValidator.create();
        
        console.log(JSON.stringify({
          params: validated,
          provenance: provenance
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Check defaults
    assert data["params"]["graceScale"] == 1.0
    assert data["params"]["bootstrapEnergy"] == 1.0
    assert data["params"]["emergenceRate"] == 1.0
    assert data["params"]["metamirrorStrength"] == 0.0
    
    # Check provenance exists
    assert "graceScale" in data["provenance"]
    assert "reference" in data["provenance"]["graceScale"]
    assert "grace_emergence_derivation.md" in data["provenance"]["graceScale"]["reference"]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_control_params_bounds_enforcement():
    """
    Verify bounds checking rejects out-of-range values.
    
    From control_parameters_specification.md Section 1 (all bounds).
    """
    script = textwrap.dedent(
        """
        import { ControlParamsValidator } from './FIRM_ui/control_params.js';
        
        const testCases = [
          { param: 'graceScale', value: 0.05, shouldFail: true },  // Below min
          { param: 'graceScale', value: 6.0, shouldFail: true },   // Above max
          { param: 'graceScale', value: 2.5, shouldFail: false },  // Valid
          { param: 'bootstrapEnergy', value: 0.0, shouldFail: true },
          { param: 'bootstrapEnergy', value: 3.0, shouldFail: false },
          { param: 'emergenceRate', value: 4.0, shouldFail: true },
          { param: 'emergenceRate', value: 1.5, shouldFail: false },
          { param: 'metamirrorStrength', value: -0.1, shouldFail: true },
          { param: 'metamirrorStrength', value: 1.5, shouldFail: true },
          { param: 'metamirrorStrength', value: 0.5, shouldFail: false }
        ];
        
        const results = [];
        
        for (const testCase of testCases) {
          try {
            ControlParamsValidator.create({ [testCase.param]: testCase.value });
            results.push({ ...testCase, actuallyFailed: false });
          } catch (error) {
            results.push({ ...testCase, actuallyFailed: true, error: error.message });
          }
        }
        
        console.log(JSON.stringify({ results }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Verify all test cases behaved as expected
    for result in data["results"]:
        assert result["actuallyFailed"] == result["shouldFail"], \
            f"{result['param']}={result['value']}: expected fail={result['shouldFail']}, got fail={result['actuallyFailed']}"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_control_params_zx_engine_integration():
    """
    Verify ZXObjectGraphEngine uses validated control params.
    
    From control_parameters_specification.md Section 3.2.
    """
    script = textwrap.dedent(
        """
        import { ZXObjectGraphEngine } from './FIRM_ui/zx_objectg_engine.js';
        
        const engine = new ZXObjectGraphEngine();
        
        // Get initial params
        const initialParams = engine._controlParams;
        const initialProvenance = engine.getControlParamsProvenance();
        
        // Update with valid value
        const updated = engine.updateControlParams({ graceScale: 2.5 });
        const updatedProvenance = engine.getControlParamsProvenance();
        
        // Try to update with invalid value
        let invalidFailed = false;
        try {
          engine.updateControlParams({ graceScale: 10.0 });
        } catch (error) {
          invalidFailed = true;
        }
        
        console.log(JSON.stringify({
          initialParams: initialParams,
          hasInitialProvenance: !!initialProvenance,
          updated: updated,
          updatedProvenance: updatedProvenance.graceScale,
          invalidFailed: invalidFailed
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    # Initial params should be defaults
    assert data["initialParams"]["graceScale"] == 1.0
    assert data["hasInitialProvenance"], "Should have provenance from construction"
    
    # Update should work
    assert data["updated"]["graceScale"] == 2.5, "Valid update should apply"
    
    # Provenance should be updated
    assert data["updatedProvenance"]["value"] == 2.5
    assert "reference" in data["updatedProvenance"]
    
    # Invalid update should fail
    assert data["invalidFailed"], "Out-of-bounds update should throw error"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime required")
def test_control_params_provenance_tracking():
    """
    Verify provenance includes timestamps and references.
    
    From control_parameters_specification.md Section 5.2.
    """
    script = textwrap.dedent(
        """
        import { ZXObjectGraphEngine } from './FIRM_ui/zx_objectg_engine.js';
        
        const engine = new ZXObjectGraphEngine();
        
        // Update multiple params
        engine.updateControlParams({
          graceScale: 1.5,
          emergenceRate: 2.0
        });
        
        const provenance = engine.getControlParamsProvenance();
        
        const hasMandatoryFields = Object.values(provenance).every(p => 
          typeof p.value === 'number' &&
          typeof p.timestamp === 'number' &&
          typeof p.reference === 'string' &&
          typeof p.symbol === 'string' &&
          typeof p.bounds === 'object'
        );
        
        console.log(JSON.stringify({
          provenance: provenance,
          hasMandatoryFields: hasMandatoryFields
        }));
        """
    ).strip()
    
    data = _run_node(script)
    
    assert data["hasMandatoryFields"], "All provenance entries must have mandatory fields"
    
    # Check specific fields
    grace_prov = data["provenance"]["graceScale"]
    assert grace_prov["value"] == 1.5
    assert grace_prov["symbol"] == "ξ_grace"
    assert "grace_emergence_derivation.md" in grace_prov["reference"]
    assert grace_prov["bounds"]["min"] == 0.1
    assert grace_prov["bounds"]["max"] == 5.0

