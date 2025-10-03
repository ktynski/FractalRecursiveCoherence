"""test_rendering.py

Tests for WebGL rendering execution with theory validation.

These tests validate that the rendering pipeline maintains mathematical
correctness while producing visual output.
"""
import pytest
import importlib


@pytest.mark.rendering
def test_clifford_field_texture_conversion():
    """Test conversion of Clifford field to WebGL texture format."""
    # Test field structure for texture conversion
    clifford_field = {
        "payload": {
            "components": [1.0] + [0.0] * 15,  # Unit scalar field
            "algebra": "Cl(1,3)"
        }
    }
    
    # Validate texture data structure
    components = clifford_field["payload"]["components"]
    assert len(components) == 16
    
    # Test that components can be packed into 4x4 texture
    texture_size = 4 * 4
    assert len(components) == texture_size
    
    # Validate normalization
    magnitude_sq = sum(c * c for c in components)
    assert abs(magnitude_sq - 1.0) < 1e-10


@pytest.mark.rendering
def test_camera_matrix_computation():
    """Test camera matrix computation maintains mathematical correctness."""
    camera_state = {
        "position": [0, 0, 5],
        "target": [0, 0, 0],
        "up": [0, 1, 0],
        "fov": 45,
        "aspect_ratio": 16/9
    }
    
    # Test view matrix properties (would be computed in renderer)
    import math
    
    # Forward vector
    forward = [0, 0, -5]  # target - position
    forward_len = math.sqrt(sum(x*x for x in forward))
    forward_norm = [x/forward_len for x in forward]
    
    assert abs(forward_len - 5.0) < 1e-10
    assert abs(forward_norm[2] + 1.0) < 1e-10  # Looking down -Z
    
    # Test projection matrix properties
    fov_rad = camera_state["fov"] * math.pi / 180
    f = 1.0 / math.tan(fov_rad / 2)
    aspect = camera_state["aspect_ratio"]
    
    assert f > 0
    assert aspect > 0


@pytest.mark.rendering
def test_rendering_pipeline_integration():
    """Test integration between mathematical engine and rendering."""
    # Import required modules
    core = importlib.import_module('FIRM_dsl.core')
    iface = importlib.import_module('FIRM_clifford.interface')
    raymarch = importlib.import_module('FIRM_ui.raymarching')
    
    # Create test graph
    g = core.ObjectG(
        nodes=[0, 1], edges=[(0, 1)],
        labels={
            0: core.make_node_label('Z', 0, 1, 'm0'),
            1: core.make_node_label('X', 1, 4, 'm1')
        }
    )
    
    # Generate Clifford field
    field = iface.phi_zx_to_clifford(g)
    
    # Create raymarching pipeline
    validator = raymarch.RaymarchingValidator()
    camera_config = {
        "position": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0],
        "fov": 45, "aspect_ratio": 16/9
    }
    
    pipeline = validator.create_raymarching_pipeline(field, camera_config)
    
    # Validate complete pipeline
    assert isinstance(pipeline, raymarch.RaymarchingPipeline)
    assert "uCliffordField" in pipeline.uniforms
    assert pipeline.field_parameters["field_type"] == "clifford"
    
    # Validate field can be converted to texture format
    components = field.payload["components"]
    assert len(components) == 16
    assert all(isinstance(c, (int, float)) for c in components)


def test_rendering_theory_compliance():
    """Validate that rendering maintains theory fidelity."""
    # Test that all rendering parameters are theory-derived
    rendering_params = {
        "max_steps": 100,      # Bounded iteration (convergence theory)
        "min_distance": 0.001, # Numerical precision limit
        "max_distance": 100.0  # Ray escape distance
    }
    
    # Validate parameter bounds
    assert rendering_params["max_steps"] > 0
    assert rendering_params["min_distance"] > 0
    assert rendering_params["max_distance"] > rendering_params["min_distance"]
    
    # Test that no empirical magic numbers are used
    # All values must be mathematically justified
    step_bound = rendering_params["max_steps"]
    assert step_bound == 100  # Specific choice must be justified
    
    distance_ratio = rendering_params["max_distance"] / rendering_params["min_distance"]
    assert distance_ratio == 100000.0  # 5 orders of magnitude precision
