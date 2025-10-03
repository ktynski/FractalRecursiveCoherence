"""Validate Python-generated raymarching shaders using the WebGL shader validator.

This avoids real GPU compilation; it checks structure and required qualifiers.
"""
import importlib


def test_python_raymarching_shaders_validate_with_webgl_validator():
    ray = importlib.import_module('FIRM_ui.raymarching')
    shader_val = importlib.import_module('FIRM_ui.shader_validator')

    validator = ray.RaymarchingValidator()
    pipeline = validator.create_raymarching_pipeline(None, {
        'position': [0, 0, 5], 'target': [0, 0, 0], 'up': [0, 1, 0],
        'fov': 45, 'aspect_ratio': 16/9
    })

    sv = shader_val.WebGLShaderValidator()
    vres = sv.validate_vertex_shader(pipeline.vertex_shader_source)
    fres = sv.validate_fragment_shader(pipeline.fragment_shader_source)

    assert vres.is_valid is True
    assert fres.is_valid is True


