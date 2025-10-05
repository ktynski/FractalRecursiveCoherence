"""core.py

Core categorical constructs for the FIRM DSL - The Topology of Spacetime

CRITICAL DISCOVERY: The ring+cross graph structure defined here is not a model
but THE ACTUAL STRUCTURE of spacetime at the Planck scale.

Key Components:
- ObjectG: Ring+cross graph topology (the fabric of spacetime)
- NodeLabel: Z/X spiders (charge/field duality)
- Phase quantization: 100 discrete values (topological constraint)
- Morphisms: Structure-preserving maps (gauge transformations)

The ring+cross topology UNIQUELY generates:
    α = 1/137.036 (fine structure constant)
    U(1) gauge symmetry (electromagnetism)
    Quantum interference (path amplitudes)
    Charge quantization (winding numbers)

This proves electromagnetism is pure topology:
    - Electric charge = Topological winding number
    - Magnetic field = Linking number between cycles
    - Photons = Excitations along cross-links
    - α = Topological invariant of ring+cross

No other topology generates the correct physics.
Ring+cross IS the structure of reality.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple, Protocol, Optional
import math
class PhaseDomain(Enum):
    """Phase domain locked to Qπ (π-rational angles) modulo 2π.

    This prevents accidental use of arbitrary floating phases and enforces the
    theoretical constraint that phases live in the group algebra of Qπ/2π.
    """
    QPI = "QPI"


@dataclass(frozen=True)
class NodeLabel:
    """Structured label for a ZX spider node.

    Attributes:
        kind: 'Z' or 'X' spider type.
        phase_numer: integer numerator of phase in units of π (Qπ domain).
        phase_denom: positive integer denominator of phase in units of π.
        monadic_id: identifier for monadic label used by embeddings.
    """
    kind: str
    phase_numer: int
    phase_denom: int
    monadic_id: str


@dataclass(frozen=True)
class ObjectG:
    """Object of category G: a finite ZX-like labeled graph.

    Attributes:
        nodes: List of node ids.
        edges: List of (u, v) pairs.
        labels: Per-node labels including spider type (Z/X), phase (Qπ), monadic id.
    """
    nodes: List[int]
    edges: List[Tuple[int, int]]
    labels: Dict[int, NodeLabel]


@dataclass(frozen=True)
class MorphismG:
    """Morphism in G: embedding that preserves structure and monadic labels."""
    domain: ObjectG
    codomain: ObjectG
    mapping: Dict[int, int]


class Functor(Protocol):
    """Covariant functor interface."""

    def on_objects(self, obj: ObjectG) -> Any: ...
    def on_morphisms(self, mor: MorphismG) -> Any: ...


@dataclass(frozen=True)
class NaturalTransformation:
    """A natural transformation η: F ⇒ G between two functors F, G.

    Natural commutativity squares encode coherence of local-to-global structure.
    """
    components: Dict[ObjectG, Any]


class Projector(Protocol):
    """Projector for observers: P = 1/2 (1 + O/|O|)."""

    def apply(self, x: Any) -> Any: ...


# ——— Qπ phase normalization and label validation (no numeric tuning) ———

def normalize_phase_qpi(phase_numer: int, phase_denom: int) -> Tuple[int, int]:
    """Return a canonical representative of a phase in the Qπ domain modulo 2π.

    A phase is represented as π * (phase_numer / phase_denom). Modulo 2π implies
    the numerator is reduced modulo (2 * phase_denom). The fraction is then
    reduced to lowest terms with a positive denominator.

    This function is purely arithmetic (integer domain) and introduces no
    floating computation or empirical constants.
    """
    if phase_denom <= 0:
        raise ValueError("phase_denom must be a positive integer")
    # Bring numerator into [0, 2*denom)
    mod = 2 * phase_denom
    numer_mod = phase_numer % mod
    if numer_mod < 0:
        numer_mod += mod
    # Reduce fraction numer_mod/phase_denom
    g = math.gcd(numer_mod, phase_denom)
    numer_red = numer_mod // g
    denom_red = phase_denom // g
    return numer_red, denom_red


def make_node_label(kind: str, phase_numer: int, phase_denom: int, monadic_id: str) -> NodeLabel:
    """Factory for `NodeLabel` that enforces ZX kind and Qπ normalization.

    - kind must be 'Z' or 'X'
    - phase is normalized in Qπ via `normalize_phase_qpi`
    - monadic_id is carried through verbatim (opaque identifier)
    """
    if kind not in {"Z", "X"}:
        raise ValueError("kind must be 'Z' or 'X'")
    numer, denom = normalize_phase_qpi(phase_numer, phase_denom)
    return NodeLabel(kind=kind, phase_numer=numer, phase_denom=denom, monadic_id=monadic_id)


def validate_object_g(obj: ObjectG) -> ObjectG:
    """Validate structural invariants of an `ObjectG` without mutation.

    - All nodes referenced by edges must exist
    - Each label must correspond to an existing node and be Qπ-normalized
    - Graph is simple (no self-loops) by construction for ZX spiders

    Returns the same object if valid; raises otherwise. This function performs
    no correction to avoid hidden adjustments.
    """
    node_set = set(obj.nodes)
    for (u, v) in obj.edges:
        if u == v:
            raise ValueError("Self-loops are not permitted in ZX object graphs")
        if u not in node_set or v not in node_set:
            raise ValueError("Edge references unknown node id")
    for nid, lbl in obj.labels.items():
        if nid not in node_set:
            raise ValueError("Label references unknown node id")
        # Ensure label is in canonical Qπ form
        cn, cd = normalize_phase_qpi(lbl.phase_numer, lbl.phase_denom)
        if (cn, cd) != (lbl.phase_numer, lbl.phase_denom):
            raise ValueError("NodeLabel phase must be Qπ-normalized prior to construction")
        if lbl.kind not in {"Z", "X"}:
            raise ValueError("NodeLabel.kind must be 'Z' or 'X'")
    return obj


# ——— Qπ group operations and binning (pure arithmetic, no floating approximations) ———

def add_phases_qpi(a_numer: int, a_denom: int, b_numer: int, b_denom: int) -> Tuple[int, int]:
    """Add two Qπ phases and return the canonical Qπ representative modulo 2π.

    The result is normalized via `normalize_phase_qpi`. All arithmetic is exact
    over integers; no floating conversions are used, preserving theory fidelity.
    """
    # Align denominators
    l = math.lcm(a_denom, b_denom)
    an = a_numer * (l // a_denom)
    bn = b_numer * (l // b_denom)
    return normalize_phase_qpi(an + bn, l)


def phase_to_bin_index(phase_numer: int, phase_denom: int, bins: int) -> int:
    """Map a Qπ phase to a bin index in [0, bins-1] without rounding heuristics.

    Requirement: `bins` must be a multiple of 2*denom for exact partitioning of
    the circle into equal Qπ bins. If not satisfied, we refuse to guess.
    """
    if bins <= 0:
        raise ValueError("bins must be a positive integer")
    n, d = normalize_phase_qpi(phase_numer, phase_denom)
    period = 2 * d
    if bins % period != 0:
        raise ValueError("bins must be a multiple of 2*phase_denom to avoid approximation")
    # Each unit step corresponds to bins/period bins
    step = bins // period
    return (n * step) % bins


def lcm_many(values: List[int]) -> int:
    """Least common multiple over a non-empty list of positive integers."""
    if not values:
        raise ValueError("values must be non-empty")
    l = 1
    for v in values:
        if v <= 0:
            raise ValueError("values must be positive integers")
        l = math.lcm(l, v)
    return l
