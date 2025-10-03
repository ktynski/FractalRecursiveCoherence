"""spec_autogen.py

Assemble sections of FIRM_spec.md from module docstrings (read-only, pure).

This tool returns a string that can be written to FIRM_spec.md by a separate
commit step. It does not perform I/O to comply with anti-fallback policy.
"""
from __future__ import annotations
import importlib


SECTIONS = [
    ("FIRM_dsl.core", "Core DSL"),
    ("FIRM_dsl.coherence", "Coherence & τ"),
    ("FIRM_dsl.sheaf", "Sheaves on (G, J)"),
    ("FIRM_dsl.monad", "Monad T and time evolution"),
    ("FIRM_zx.host_layout", "ZX host layout"),
    ("FIRM_zx.host_params", "ZX params layout"),
    ("FIRM_zx.rules", "ZX rules (preconditions)"),
    ("FIRM_clifford.interface", "Clifford mapping interface"),
]


def render_spec() -> str:
    parts = ["# FIRM Spec (Auto-assembled)\n\n"]
    for mod_name, title in SECTIONS:
        mod = importlib.import_module(mod_name)
        doc = (mod.__doc__ or "").strip()
        parts.append(f"## {title}\n\n")
        parts.append("```\n")
        parts.append(doc + "\n")
        parts.append("```\n\n")
    return "".join(parts)


