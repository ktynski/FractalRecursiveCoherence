"""grace_field.py

Symbolic Grace field model interfaces (structure-only, no empirical tuning).

Implements:
- GraceFieldParams: potential parameters with sign validation
- potential_V(u): V = α u - β u^2 + γ u^3 where u = |G|^2
- dV_du(u): derivative w.r.t. u for stationary-point analysis
- recursion_depth_classification(r): maps discrete recursion depth to regimes
- coherence_density(grad_phi_sqr, amplitude_sqr): ρ_c = |∇φ|^2 + |G|^2
- resonant_source_term(omega, graph, λ): λ · Res(S, Ω) using DSL resonance

All functions are deterministic, dimensionless, and avoid numeric "tuning".
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import isfinite, inf
from typing import Union

from .core import ObjectG
from .resonance import OmegaSignature, compute_resonance_alignment


@dataclass(frozen=True)
class GraceFieldParams:
    """Parameters for symbolic potential V.

    Constraints:
        α > 0 (spontaneous emergence)
        β > 0 (prevents runaway collapse)
        γ ∈ ℝ (triune metastability coefficient)
    """

    alpha: float
    beta: float
    gamma: float = 0.0

    def __post_init__(self) -> None:
        if not (self.alpha > 0):
            raise ValueError("alpha must be > 0")
        if not (self.beta > 0):
            raise ValueError("beta must be > 0")
        # gamma unconstrained (can be 0 or any real)


def potential_V(u: float, p: GraceFieldParams) -> float:
    """Polynomial potential V(u) with u = |G|^2 ≥ 0.

    V(u) = α u - β u^2 + γ u^3
    """
    if u < 0:
        raise ValueError("u must be non-negative (|G|^2)")
    return p.alpha * u - p.beta * (u ** 2) + p.gamma * (u ** 3)


def dV_du(u: float, p: GraceFieldParams) -> float:
    """First derivative of V with respect to u.

    dV/du = α - 2β u + 3γ u^2
    """
    if u < 0:
        raise ValueError("u must be non-negative (|G|^2)")
    return p.alpha - 2.0 * p.beta * u + 3.0 * p.gamma * (u ** 2)


class FieldRegime(Enum):
    NON_BEING = "non_being"
    VACUUM = "vacuum"
    DARK_SECTOR = "dark_sector"
    MATTER = "ordinary_matter"
    OMEGA = "omega"


def recursion_depth_classification(r: Union[int, float]) -> FieldRegime:
    """Classify recursion depth into field regimes.

    Mapping (discrete by design, no thresholds):
      r = 0            → NON_BEING
      r = 1            → VACUUM
      r ∈ {2, 3}       → DARK_SECTOR
      r ∈ ℕ, r ≥ 4     → MATTER
      r = ∞            → OMEGA

    Any non-integer finite r raises to avoid numeric guessing.
    """
    if r == inf:
        return FieldRegime.OMEGA
    if not isfinite(r):
        raise ValueError("recursion depth must be finite integer or +∞")
    if int(r) != r:
        raise ValueError("recursion depth must be an integer or +∞")
    ri = int(r)
    if ri < 0:
        raise ValueError("recursion depth cannot be negative")
    if ri == 0:
        return FieldRegime.NON_BEING
    if ri == 1:
        return FieldRegime.VACUUM
    if ri in (2, 3):
        return FieldRegime.DARK_SECTOR
    return FieldRegime.MATTER


def coherence_density(grad_phi_sqr: float, amplitude_sqr: float) -> float:
    """ρ_c = |∇φ|^2 + |G|^2 with strict domain checks (no negative inputs)."""
    if grad_phi_sqr < 0:
        raise ValueError("|∇φ|^2 must be non-negative")
    if amplitude_sqr < 0:
        raise ValueError("|G|^2 must be non-negative")
    return grad_phi_sqr + amplitude_sqr


def resonant_source_term(omega: OmegaSignature, graph: ObjectG, lam: float) -> float:
    """Source term S_res = λ · Res(S, Ω), dimensionless scaling by λ.

    λ is a symbolic coupling constant provided by caller; this function
    introduces no numeric defaults or hidden scaling.
    """
    res = compute_resonance_alignment(graph, omega)
    return float(lam) * float(res)


__all__ = [
    "GraceFieldParams",
    "potential_V",
    "dV_du",
    "FieldRegime",
    "recursion_depth_classification",
    "coherence_density",
    "resonant_source_term",
]


