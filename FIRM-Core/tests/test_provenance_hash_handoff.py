"""Test provenance hash handoff from machine info to BLAKE3 function.

Ensures compute_blake3_hex is used via build_machine_fingerprint without fallbacks.
"""
import importlib


def test_build_machine_fingerprint_uses_blake3_vendor_function():
    prov = importlib.import_module('FIRM_dsl.provenance')
    blake3_vendor = importlib.import_module('FIRM_dsl.blake3_vendor')

    # Use test blake3 function to ensure deterministic result
    test_fn = blake3_vendor.create_test_blake3_function()

    # Monkeypatch compute_blake3_hex to use the test function
    # without changing the production code path (simulate injection point)
    original = prov.compute_blake3_hex

    try:
        def patched_compute_blake3_hex(data: bytes) -> str:
            return test_fn(data)

        prov.compute_blake3_hex = patched_compute_blake3_hex
        info_bytes = b'{"cpu_model":"x","cpu_arch":"arm","os_name":"darwin","os_version":"24","node_id":"uuid"}'
        fp = prov.build_machine_fingerprint(info_bytes)
        assert isinstance(fp, str)
        assert fp.startswith('TEST-')
    finally:
        prov.compute_blake3_hex = original


