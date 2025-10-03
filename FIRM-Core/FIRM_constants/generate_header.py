"""generate_header.py

Generate a derived constants header `FIRM_constants.gen.h` from proven derivations.

This script exposes a pure function `render_header` that accepts a mapping from
names to DerivationResult and returns the header text. No I/O is performed here
to preserve testability and avoid side effects.
"""
from __future__ import annotations
from typing import Dict
from .FIRM_derivations import DerivationResult


HEADER_PREAMBLE = """// FIRM_constants.gen.h (auto-generated)
// All values in this header are derived from first principles and accompanied
// by proof identifiers. Do not edit manually.

#ifndef FIRM_CONSTANTS_GEN_H
#define FIRM_CONSTANTS_GEN_H

"""

HEADER_EPILOGUE = """
#endif // FIRM_CONSTANTS_GEN_H
"""


def render_define(name: str, res: DerivationResult) -> str:
    """Render a single #define with provenance comment."""
    if not name.startswith("FIRM_"):
        raise ValueError("constant names must start with FIRM_")
    return f"#define {name} {res.value} /* proof: {res.proof_id} */\n"


def render_header(constants: Dict[str, DerivationResult]) -> str:
    """Render the complete header as a string."""
    lines = [HEADER_PREAMBLE]
    for name in sorted(constants.keys()):
        lines.append(render_define(name, constants[name]))
    lines.append(HEADER_EPILOGUE)
    return "".join(lines)


def rational_to_float(r) -> float:
    """Convert RationalUnit to float for header generation."""
    # Import here to avoid circular dependency
    from .FIRM_derivations import RationalUnit
    if isinstance(r, RationalUnit):
        return r.numer / r.denom
    return float(r)


def build_constants_from_derivations(phase_denominators=None) -> Dict[str, DerivationResult]:
    """Build constants dict from available derivations (non-raising only)."""
    from .FIRM_derivations import derive_phase_unit_rational, DerivationResult
    
    constants = {}
    
    # Add rational phase unit if denominators provided
    if phase_denominators:
        try:
            proof_id, rational = derive_phase_unit_rational(phase_denominators)
            value = rational_to_float(rational)
            constants["FIRM_PHASE_UNIT"] = DerivationResult(proof_id, value)
        except Exception:
            pass  # Skip if derivation fails
    
    return constants


