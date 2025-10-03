"""sheaf.py

Sheaf-theoretic foundation on the site (G, J).

- Site: (G, J) with G the category of finite monadic subgraphs and J a Grothendieck
  topology where covers generate all valid one-step extensions; closure is reachability
  in one tick via the growth functor F.
- Sheaves live in PSh(G) with gluing validated over J.

This module defines types and interfaces for presheaves, sheaves, and cover data.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from .core import ObjectG, MorphismG


@dataclass(frozen=True)
class Cover:
    """A cover {V_i -> U} whose images jointly generate all valid one-step extensions."""
    target: ObjectG
    arrows: List[MorphismG]


@dataclass
class Presheaf:
    """A presheaf S: G^op -> Set."""
    values_on_objects: Dict[ObjectG, Any]

    def restrict(self, morphism: MorphismG) -> Any:
        """Restriction map along morphism in G^op."""
        raise NotImplementedError


class Sheaf(Presheaf):
    """A presheaf satisfying the sheaf gluing condition over J."""

    def glue(self, cover: Cover) -> Any:
        """Gluing along a cover respecting locality-to-globality of coherence."""
        raise NotImplementedError
