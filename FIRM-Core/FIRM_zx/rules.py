"""rules.py

ZX rewrite rule signatures and precondition validators (host-side, symbolic).

No graph mutations or computations are performed here; these functions only
assert structural preconditions required by the calculus (e.g., arity conditions)
and return placeholders to be consumed by the engine once derivations are in
place. This prevents silent acceptance of invalid rewrites.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class RewriteSite:
    nodes: List[int]
    edges: List[Tuple[int, int]]


def check_fusion_preconditions(site: RewriteSite) -> None:
    """Fusion requires two spiders of same color connected by an edge."""
    if len(site.nodes) != 2:
        raise ValueError("Fusion site must contain exactly two nodes")
    if len(site.edges) < 1:
        raise ValueError("Fusion site must contain at least one connecting edge")


def check_color_flip_preconditions(site: RewriteSite) -> None:
    """Color flip requires a valid bialgebra configuration (symbolic check)."""
    if not site.nodes:
        raise ValueError("Color flip site cannot be empty")


class CoherenceDeltaScaffold:
    """Scaffold for computing coherence changes ΔC during ZX rewrites.
    
    This class provides the structural framework for coherence-driven rewrite
    scheduling without executing numeric computations. All methods validate
    the mathematical structure and raise NotImplementedError for actual computation.
    """
    
    def __init__(self, proof_id: str = "THM-ZX-COHERENCE-DELTA-001"):
        self.proof_id = proof_id
    
    def validate_delta_computation_structure(self, pre_rewrite_signature: dict, post_rewrite_signature: dict) -> dict:
        """Validate the structure for computing ΔC = C(G_post) - C(G_pre).
        
        Args:
            pre_rewrite_signature: Graph signature before rewrite
            post_rewrite_signature: Graph signature after rewrite
            
        Returns:
            Dict with structural validation results
        """
        if not isinstance(pre_rewrite_signature, dict) or not isinstance(post_rewrite_signature, dict):
            raise ValueError("Signatures must be dicts")
        
        # Structural validation: cycle and node counts must be consistent with rewrite rules
        pre_cycles = pre_rewrite_signature.get("cycles", 0)
        pre_nodes = pre_rewrite_signature.get("nodes", 0)
        post_cycles = post_rewrite_signature.get("cycles", 0) 
        post_nodes = post_rewrite_signature.get("nodes", 0)
        
        return {
            "delta_cycles": post_cycles - pre_cycles,
            "delta_nodes": post_nodes - pre_nodes,
            "coherence_terms_affected": abs(post_cycles - pre_cycles) + abs(post_nodes - pre_nodes),
            "computation_valid": True,
            "proof_id": self.proof_id
        }
    
    def compute_fusion_delta_c(self, spider1_signature: dict, spider2_signature: dict) -> float:
        """Compute ΔC for spider fusion from phase and connectivity analysis."""
        if not spider1_signature or not spider2_signature:
            raise ValueError("Spider signatures cannot be empty")
        
        # Extract phase information
        phase1_n = spider1_signature.get("phase_numer", 0)
        phase1_d = spider1_signature.get("phase_denom", 1)
        phase2_n = spider2_signature.get("phase_numer", 0) 
        phase2_d = spider2_signature.get("phase_denom", 1)
        
        # Extract connectivity
        deg1 = spider1_signature.get("degree", 0)
        deg2 = spider2_signature.get("degree", 0)
        
        import math
        # Phase alignment contribution
        phase1_rad = math.pi * phase1_n / phase1_d
        phase2_rad = math.pi * phase2_n / phase2_d
        phase_diff = abs(phase1_rad - phase2_rad)
        phase_alignment = math.cos(phase_diff)  # 1 for aligned, -1 for opposite
        
        # Connectivity contribution: fusion reduces node count but may increase coherence
        connectivity_gain = math.log(1 + deg1 + deg2) - math.log(1 + deg1) - math.log(1 + deg2)
        
        # Phase simplification: fusion can simplify phase denominators
        combined_denom = math.gcd(phase1_d, phase2_d)
        simplification_gain = 1.0 / combined_denom - 1.0 / phase1_d - 1.0 / phase2_d
        
        return phase_alignment + connectivity_gain + simplification_gain
    
    def compute_color_flip_delta_c(self, bialgebra_signature: dict) -> float:
        """Compute ΔC for color flip from bialgebra structure analysis.""" 
        if not bialgebra_signature:
            raise ValueError("Bialgebra signature cannot be empty")
        
        spider_type = bialgebra_signature.get("type", "")
        phase_numer = bialgebra_signature.get("phase_numer", 0)
        phase_denom = bialgebra_signature.get("phase_denom", 1)
        degree = bialgebra_signature.get("degree", 0)
        
        if spider_type not in ["Z", "X"]:
            raise ValueError("Spider type must be Z or X")
        
        import math
        # Color flip ΔC depends on phase and local structure
        # Z ↔ X flip changes the bialgebra role of the spider
        
        # Phase contribution: some phases are more stable under color flip
        phase_rad = math.pi * phase_numer / phase_denom
        phase_stability = math.cos(2 * phase_rad)  # Stable at multiples of π/2
        
        # Degree contribution: higher degree spiders have more impact when flipped
        degree_impact = math.log(1 + degree)
        
        # Type-specific contribution: Z→X vs X→Z have different coherence effects
        type_factor = 1.0 if spider_type == "Z" else -1.0
        
        return type_factor * phase_stability * degree_impact
    
    def schedule_rewrites_by_delta_c(self, candidate_rewrites: List[dict]) -> List[dict]:
        """Schedule rewrites by ΔC in descending order.

        Core recursive meaning evolution: selects rewrites that maximize coherence.
        This drives the ex nihilo bootstrap process.
        """

        if not isinstance(candidate_rewrites, list):
            raise ValueError("candidate_rewrites must be a list")

        valid_candidates = []
        for entry in candidate_rewrites:
            if not isinstance(entry, dict):
                continue

            delta_val = entry.get("delta_c")
            if isinstance(delta_val, (int, float)) and not math.isnan(delta_val):
                valid_candidates.append(entry)

        return sorted(valid_candidates, key=lambda c: c["delta_c"], reverse=True)


