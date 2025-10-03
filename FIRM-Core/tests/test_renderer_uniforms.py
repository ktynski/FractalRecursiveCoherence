"""Ensure renderer uses inverse matrices uniforms consistent with pipeline.
This is a static check over JS source strings.
"""
import os


def test_renderer_references_inverse_uniforms():
    path = os.path.join('FIRM_ui', 'renderer.js')
    assert os.path.exists(path)
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    # Check uniform names set in updateUniforms
    assert 'uInverseViewMatrix' in src
    assert 'uInverseProjectionMatrix' in src


