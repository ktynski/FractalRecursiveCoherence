"""Export Parseval-based audio normalization to JSON for UI consumption.

This writes a small JSON file (normalization.json) under FIRM_ui/ derived from
FIRM_audio.derivations without any empirical tuning.
"""
from __future__ import annotations
import json
import os
import sys
from typing import Dict, Any


def build_normalization_payload(fft_size: int = 2048, sample_rate: float = 44100.0) -> Dict[str, Any]:
    # Ensure repository root is on sys.path for local imports
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from FIRM_audio.derivations import derive_parseval_normalization

    norm = derive_parseval_normalization(fft_size, sample_rate)
    return {
        "window_function": norm.window_function,
        "correction_factor": norm.correction_factor,
        "max_energy_bound": norm.max_energy_bound,
        "proof_id": norm.proof_id,
        "fft_size": fft_size,
        "sample_rate": sample_rate,
    }


def write_normalization_json(ui_dir: str = "FIRM_ui", filename: str = "normalization.json") -> str:
    payload = build_normalization_payload()
    os.makedirs(ui_dir, exist_ok=True)
    target = os.path.join(ui_dir, filename)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return target


if __name__ == "__main__":
    path = write_normalization_json()
    print(f"✓ Wrote normalization to {path}")


