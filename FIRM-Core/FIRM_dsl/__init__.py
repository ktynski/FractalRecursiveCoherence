"""
FIRM_dsl: Typed Python DSL for expressing the meta-axioms, the site (G, J),
sheaves, the time-evolution geometric morphisms (f*, f_*), the monad T = f_* ∘ f*,
and derived observables including the coherence functional C(G) and identity echo time τ.

This module is the source of truth for mathematical derivations. No empirical
values are permitted. Every exported numeric must trace to a derivation recorded
in provenance bundles per the anti-tuning directive.
"""

__all__ = [
    "core",
    "coherence",
    "sheaf",
    "monad",
    "provenance",
    "resonance",
    "grace_field",
]
