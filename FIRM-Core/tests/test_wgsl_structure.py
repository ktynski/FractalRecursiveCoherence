"""WGSL shader structure checks for FIRM_ZX.wgsl.

Lightweight assertions to ensure required structs and bindings exist.
"""
import os


def test_firm_zx_wgsl_contains_params_and_spider_structs():
    path = os.path.join('FIRM_zx', 'FIRM_ZX.wgsl')
    assert os.path.exists(path)
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    assert 'struct Params' in src
    assert 'var<uniform> params' in src
    assert 'struct Spider' in src
    assert 'var<storage, read_write> spiders' in src
    assert '@compute' in src
    assert '@workgroup_size' in src


