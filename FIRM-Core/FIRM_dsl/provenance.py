"""provenance.py

Provenance ledger structures and helpers. No network access. No PII.

- Required fields: axioms_hash, graph_seed, version_hash, machine_fingerprint,
  compile_time, render_tick, τ_distribution, active_macros.
- machine_fingerprint = Blake3(serialized(cpu_model, cpu_arch, os_name, os_version, node_id))
  with node_id = UUIDv4 generated at first run.
- In CI, use machine_fingerprint := "CI_CANONICAL" for deterministic seeds.

Note: Blake3 is not in the Python stdlib; to remain honest, we do not silently
substitute another hash. Instead, we expose a function that raises until Blake3
is available or vendored.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Callable
import uuid
import json
import os


@dataclass
class RunLedger:
    axioms_hash: str
    graph_seed: str
    version_hash: str
    machine_fingerprint: str
    compile_time: str
    render_tick: int
    tau_distribution: List[float]
    active_macros: List[str]


def generate_node_id() -> str:
    """Generate a UUIDv4 node id (non-PII)."""
    return str(uuid.uuid4())


def compute_blake3_hex(data: bytes) -> str:
    """Compute BLAKE3 hex digest of bytes.

    This intentionally raises until BLAKE3 is available. No fake fallback.
    """
    from .blake3_vendor import blake3_hex
    return blake3_hex(data)


def canonical_ci_fingerprint() -> str:
    """Return the canonical CI fingerprint string used to fix seeds in CI."""
    return "CI_CANONICAL"


@dataclass
class MachineInfo:
    """Opaque machine info for non-PII fingerprinting.

    Fields mirror the locked spec; values must be collected locally and serialized
    to JSON for hashing. No network calls; no hardware serials.
    """
    cpu_model: str
    cpu_arch: str
    os_name: str
    os_version: str
    node_id: str


def build_machine_fingerprint(info_json_bytes: bytes) -> str:
    """Hash serialized machine info using BLAKE3.

    This function enforces the anti-tuning directive by refusing to proceed
    without the exact hash algorithm specified in the spec.
    """
    return compute_blake3_hex(info_json_bytes)


def provenance_bundle_path(root: str, hash_hex: str) -> str:
    """Return content-addressed provenance subdirectory path.

    Layout: root/<2-hex>/<hash>/
    No filesystem writes are performed here.
    """
    if len(hash_hex) < 2:
        raise ValueError("hash_hex must have at least 2 hex characters")
    return os.path.join(root, hash_hex[:2], hash_hex)


def write_run_json(path: str, run: RunLedger, json_dumps: Callable[..., str] = None) -> bytes:
    """Serialize run ledger to JSON bytes for hashing and storage.

    The serializer is dependency-injected to avoid hidden defaults; by default
    we use json.dumps with separators set for stability.
    """
    if json_dumps is None:
        json_dumps = lambda obj: json.dumps(obj, sort_keys=True, separators=(",", ":"))
    as_dict = {
        "axioms_hash": run.axioms_hash,
        "graph_seed": run.graph_seed,
        "version_hash": run.version_hash,
        "machine_fingerprint": run.machine_fingerprint,
        "compile_time": run.compile_time,
        "render_tick": run.render_tick,
        "tau_distribution": run.tau_distribution,
        "active_macros": run.active_macros,
    }
    return json_dumps(as_dict).encode("utf-8")


def compute_content_hash(json_bytes: bytes, hash_hex_fn: Callable[[bytes], str]) -> str:
    """Compute a content hash using a provided hex-digest function.

    This avoids hidden dependencies. In production, pass BLAKE3; in tests, pass a
    deterministic stub. No fallback is performed inside this function.
    """
    if not callable(hash_hex_fn):
        raise TypeError("hash_hex_fn must be callable and accept bytes -> hex str")
    return hash_hex_fn(json_bytes)


def compose_run_bundle(root: str, run: RunLedger, hash_hex_fn: Callable[[bytes], str]) -> dict:
    """Compose a content-addressed run bundle description (pure, no I/O).

    Returns a dict with keys:
      - path: content-addressed directory path under `root`
      - run_json_bytes: serialized run.json bytes
      - hash_hex: content hash used in addressing
    """
    run_bytes = write_run_json("/dev/null", run)
    hh = compute_content_hash(run_bytes, hash_hex_fn)
    path = provenance_bundle_path(root, hh)
    return {"path": path, "run_json_bytes": run_bytes, "hash_hex": hh}
