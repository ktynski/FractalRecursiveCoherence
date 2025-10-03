"""UI pipeline consistency between Python and JS implementations.

Enforce that the Python raymarching pipeline uses precomputed inverse matrices
(`uInverseViewMatrix`, `uInverseProjectionMatrix`) matching the JS renderer,
and avoids in-shader inverse() usage.
"""
import importlib


def test_python_raymarching_uniforms_match_js_renderer_strategy():
    ray = importlib.import_module('FIRM_ui.raymarching')
    validator = ray.RaymarchingValidator()
    pipeline = validator.create_raymarching_pipeline(None, {
        'position': [0, 0, 5], 'target': [0, 0, 0], 'up': [0, 1, 0],
        'fov': 45, 'aspect_ratio': 16/9
    })

    # Uniforms must include precomputed inverse matrices
    uniforms = pipeline.uniforms
    assert 'uInverseViewMatrix' in uniforms
    assert 'uInverseProjectionMatrix' in uniforms

    # Vertex shader should not call inverse(); rely on uInverse* instead
    vsrc = pipeline.vertex_shader_source
    assert 'inverse(' not in vsrc
    assert 'uInverseViewMatrix' in vsrc and 'uInverseProjectionMatrix' in vsrc

    # Fragment shader should be consistent with JS (uses uMinDistance/uMaxDistance)
    fsrc = pipeline.fragment_shader_source
    assert 'uMinDistance' in fsrc and 'uMaxDistance' in fsrc


