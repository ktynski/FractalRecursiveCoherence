"""resonance.py

Canonical Ω signature and morphic resonance functional Res(S, Ω).

Implementation uses only existing DSL observables:
- Cycle basis signature (topological component)
- Qπ-consistent phase histogram (phase component)
- Similarity S = Jaccard(cycles) × Cosine(phase histograms)

No empirical gates or constants are introduced. All computations are pure,
dimensionless, and derived from the DSL primitives in coherence.py.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from .core import ObjectG
from .coherence import (
    compute_cycle_basis_signature,
    compute_phase_histogram_signature,
    derive_minimal_qpi_bins,
    similarity_S,
)


@dataclass(frozen=True)
class OmegaSignature:
    """Canonical Ω signature comprising structure and phase domain.

    Attributes:
        cycles: Canonical fundamental cycle basis signature of Ω.
        phase_bins: Minimal valid Qπ-consistent bin count for Ω.
        phase_hist: Normalized phase histogram of Ω in `phase_bins`.
    """

    cycles: List[Tuple[int, ...]]
    phase_bins: int
    phase_hist: List[float]


def derive_omega_signature(graph: ObjectG) -> OmegaSignature:
    """Derive a canonical Ω signature from a reference object graph.

    The Ω signature fixes a structural and phase reference without numeric tuning:
    - cycles = canonical cycle basis signature (isomorphism-invariant)
    - phase_bins = 2*LCM(denominators) (minimal exact Qπ partition)
    - phase_hist = normalized histogram at `phase_bins`
    """
    cycles = compute_cycle_basis_signature(graph)
    bins = derive_minimal_qpi_bins(graph)
    hist = compute_phase_histogram_signature(graph, bins)
    return OmegaSignature(cycles=cycles, phase_bins=bins, phase_hist=hist)


def compute_resonance_alignment(graph: ObjectG, omega: OmegaSignature) -> float:
    """Compute morphic resonance alignment Res(S, Ω) in [0, 1].

    Definition (pure, dimensionless):
        Res(S, Ω) = S(cycles_S, cycles_Ω; phase_hist_S, phase_hist_Ω)
    where S = Jaccard(cycle signatures) × Cosine(phase histograms)

    Phase histogram for S is computed using Ω's `phase_bins` to ensure identical
    binning, per Qπ domain requirements.
    """
    cycles_s = compute_cycle_basis_signature(graph)
    hist_s = compute_phase_histogram_signature(graph, omega.phase_bins)
    return float(similarity_S(cycles_s, omega.cycles, hist_s, omega.phase_hist))


__all__ = [
    "OmegaSignature",
    "derive_omega_signature",
    "compute_resonance_alignment",
]


