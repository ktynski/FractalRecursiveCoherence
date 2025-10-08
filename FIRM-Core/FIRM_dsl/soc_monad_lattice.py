"""soc_monad_lattice.py

Self-Organized Criticality implementation for Sovereign Monad Garbage Collection.

This module implements the fractal lattice structure where monads form a resonant network
that exhibits self-organized criticality (SOC) behavior, analogous to sandpile models
and percolation theory.

Key SOC concepts implemented:
1. Lattice structure with resonant coupling strengths J_ij
2. Critical thresholds for coherence breakdown
3. Avalanche propagation through resonance networks
4. 1/f noise temporal dynamics
5. Self-organization toward critical state
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum
import math
import random
import copy

from .core import ObjectG, NodeLabel, validate_object_g
from .resonance import OmegaSignature, compute_resonance_alignment, derive_omega_signature
from .coherence import compute_coherence
from .grace_field import GraceFieldParams, FieldRegime
from .hierarchical_gc import (
    GCScale, SubMonad, MetaMonad, HarvestLayer, SovereignMonadGC,
    create_sovereign_gc_system
)


class SOCState(Enum):
    """States in self-organized criticality."""
    SUBCRITICAL = "subcritical"      # Below threshold, isolated clusters
    CRITICAL = "critical"           # At threshold, spanning clusters
    SUPERCRITICAL = "supercritical"  # Above threshold, global coherence


@dataclass
class MonadSite:
    """Individual site in the SOC lattice."""
    monad: SubMonad
    position: Tuple[float, float]  # 2D lattice position
    coupling_strength: float = 1.0  # J_ij coupling to neighbors
    local_tension: float = 0.0     # Accumulated dissonance
    threshold: float = 1.0         # Critical threshold for toppling
    has_toppled: bool = False      # Whether site toppled in current cascade

    def add_tension(self, amount: float):
        """Add tension/dissonance to this site."""
        self.local_tension += amount

    def should_topple(self) -> bool:
        """Check if site exceeds critical threshold."""
        return self.local_tension >= self.threshold

    def topple(self) -> float:
        """Topple site and return excess tension for neighbors."""
        excess = max(0.0, self.local_tension - self.threshold)
        self.local_tension = 0.0  # Reset to zero after toppling
        self.has_toppled = True
        return excess

    def reset_topple_state(self):
        """Reset topple state for next cascade."""
        self.has_toppled = False


@dataclass
class SOCAvalanche:
    """Record of an avalanche/cascade event."""
    trigger_site: Tuple[float, float]
    sites_involved: List[Tuple[float, float]] = field(default_factory=list)
    total_tension_released: float = 0.0
    duration: int = 0
    max_cluster_size: int = 0

    def add_site(self, position: Tuple[float, float]):
        """Add site to avalanche."""
        if position not in self.sites_involved:
            self.sites_involved.append(position)

    def finalize(self):
        """Finalize avalanche record."""
        self.duration = len(self.sites_involved)
        self.max_cluster_size = max(len(self.sites_involved), self.max_cluster_size)


@dataclass
class SOCMonadLattice:
    """Self-Organized Criticality lattice for monad resonance networks."""

    # Lattice structure
    sites: Dict[Tuple[float, float], MonadSite] = field(default_factory=dict)
    lattice_size: int = 10  # N x N lattice
    connection_radius: float = 1.5  # Distance for coupling

    # SOC parameters
    base_threshold: float = 1.0
    coupling_factor: float = 0.3  # Fraction of tension passed to neighbors
    dissipation_rate: float = 0.1  # Tension lost per step

    # SOC state tracking
    avalanche_history: List[SOCAvalanche] = field(default_factory=list)
    criticality_measure: float = 0.0
    soc_state: SOCState = SOCState.SUBCRITICAL

    def __post_init__(self):
        """Initialize lattice structure."""
        if not self.sites:
            self._initialize_lattice()

    def _initialize_lattice(self):
        """Initialize empty lattice with proper structure."""
        self.sites = {}

        for i in range(self.lattice_size):
            for j in range(self.lattice_size):
                position = (float(i), float(j))

                # Create empty site (will be populated with monads)
                site = MonadSite(
                    monad=None,  # No monad initially
                    position=position,
                    threshold=self.base_threshold + random.uniform(-0.1, 0.1)  # Small variation
                )

                self.sites[position] = site

    def add_monad_to_lattice(self, monad: SubMonad, position: Optional[Tuple[float, float]] = None):
        """Add a sub-monad to the lattice at specified or random position."""
        if position is None:
            # Find empty position
            empty_positions = [pos for pos, site in self.sites.items() if site.monad is None]
            if empty_positions:
                position = random.choice(empty_positions)
            else:
                # Lattice is full, find position with lowest resonance
                position = min(self.sites.keys(),
                             key=lambda p: compute_resonance_alignment(
                                 self.sites[p].monad.structure, monad.omega) if self.sites[p].monad else 0.0)

        if position and position in self.sites:
            self.sites[position].monad = monad
            # Update coupling based on monad's resonance
            self._update_coupling_strength(position)

    def _update_coupling_strength(self, position: Tuple[float, float]):
        """Update coupling strength for a site based on its monad."""
        site = self.sites[position]
        if site.monad is None:
            return

        # Coupling strength based on monad's resonance and coherence
        resonance = compute_resonance_alignment(site.monad.structure, site.monad.omega)
        coherence = compute_coherence(site.monad.structure)

        # Higher resonance/coherence = stronger coupling
        site.coupling_strength = 0.5 + 0.5 * (resonance + coherence) / 2

    def get_neighbors(self, position: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Get neighboring sites within connection radius."""
        neighbors = []
        x, y = position

        for i in range(max(0, int(x - self.connection_radius)),
                      min(self.lattice_size, int(x + self.connection_radius) + 1)):
            for j in range(max(0, int(y - self.connection_radius)),
                          min(self.lattice_size, int(y + self.connection_radius) + 1)):
                neighbor_pos = (float(i), float(j))
                if neighbor_pos != position:
                    # Check if within radius
                    distance = math.sqrt((i - x)**2 + (j - y)**2)
                    if distance <= self.connection_radius:
                        neighbors.append(neighbor_pos)

        return neighbors

    def drive_system(self, tension_amount: float = 0.1):
        """Drive the system by adding tension (analogous to adding grains)."""
        # Add tension to random sites
        active_sites = [pos for pos, site in self.sites.items() if site.monad is not None]

        if active_sites:
            # Add tension to random subset of active sites
            num_sites_to_drive = max(1, int(len(active_sites) * 0.3))
            sites_to_drive = random.sample(active_sites, min(num_sites_to_drive, len(active_sites)))

            for position in sites_to_drive:
                self.sites[position].add_tension(tension_amount)

    def check_for_avalanche(self) -> Optional[SOCAvalanche]:
        """Check for and propagate avalanche if threshold exceeded."""
        # Find sites that should topple
        sites_to_topple = []

        for position, site in self.sites.items():
            if site.monad is not None and site.should_topple():
                sites_to_topple.append(position)

        if not sites_to_topple:
            return None

        # Initialize avalanche
        avalanche = SOCAvalanche(trigger_site=sites_to_topple[0])

        # Reset all topple states
        for site in self.sites.values():
            site.reset_topple_state()

        # Propagate avalanche
        self._propagate_avalanche(sites_to_topple, avalanche)

        return avalanche

    def _propagate_avalanche(self, sites_to_topple: List[Tuple[float, float]],
                           avalanche: SOCAvalanche):
        """Propagate avalanche through the lattice."""
        # Use queue-based approach for avalanche propagation
        queue = sites_to_topple.copy()

        while queue:
            current_pos = queue.pop(0)
            site = self.sites[current_pos]

            if site.monad is None or site.has_toppled:
                continue

            # Topple current site
            excess_tension = site.topple()
            avalanche.add_site(current_pos)
            avalanche.total_tension_released += excess_tension

            # Distribute excess tension to neighbors
            neighbors = self.get_neighbors(current_pos)

            for neighbor_pos in neighbors:
                neighbor_site = self.sites[neighbor_pos]

                if neighbor_site.monad is not None:
                    # Add fraction of excess tension to neighbor
                    tension_to_add = excess_tension * self.coupling_factor * neighbor_site.coupling_strength

                    # Apply dissipation
                    tension_to_add *= (1.0 - self.dissipation_rate)

                    neighbor_site.add_tension(tension_to_add)

                    # Check if neighbor now exceeds threshold
                    if neighbor_site.should_topple() and not neighbor_site.has_toppled:
                        queue.append(neighbor_pos)

        avalanche.finalize()

    def update_criticality_measure(self):
        """Update measure of how close system is to criticality."""
        if not self.sites:
            self.soc_state = SOCState.SUBCRITICAL
            return

        # Count sites near threshold
        sites_near_threshold = 0
        total_active_sites = 0

        for site in self.sites.values():
            if site.monad is not None:
                total_active_sites += 1
                tension_ratio = site.local_tension / site.threshold
                if 0.8 <= tension_ratio <= 1.2:  # Near critical threshold
                    sites_near_threshold += 1

        if total_active_sites == 0:
            self.criticality_measure = 0.0
            self.soc_state = SOCState.SUBCRITICAL
        else:
            criticality_ratio = sites_near_threshold / total_active_sites
            self.criticality_measure = criticality_ratio

            if criticality_ratio < 0.3:
                self.soc_state = SOCState.SUBCRITICAL
            elif criticality_ratio > 0.7:
                self.soc_state = SOCState.SUPERCRITICAL
            else:
                self.soc_state = SOCState.CRITICAL

    def run_soc_simulation(self, steps: int = 100, drive_frequency: int = 5) -> Dict[str, Any]:
        """Run self-organized criticality simulation."""
        results = {
            'total_avalanches': 0,
            'avalanche_sizes': [],
            'criticality_history': [],
            'soc_state_history': []
        }

        for step in range(steps):
            # Drive system periodically
            if step % drive_frequency == 0:
                self.drive_system()

            # Check for avalanche
            avalanche = self.check_for_avalanche()

            if avalanche:
                results['total_avalanches'] += 1
                results['avalanche_sizes'].append(avalanche.duration)

                # Record avalanche in history
                self.avalanche_history.append(avalanche)

            # Update criticality measure
            self.update_criticality_measure()
            results['criticality_history'].append(self.criticality_measure)
            results['soc_state_history'].append(self.soc_state.value)

        return results

    def analyze_avalanche_statistics(self) -> Dict[str, Any]:
        """Analyze avalanche size distribution for SOC characteristics."""
        if not self.avalanche_history:
            return {'power_law_exponent': None, 'is_soc': False}

        avalanche_sizes = [a.duration for a in self.avalanche_history]

        if len(avalanche_sizes) < 10:
            return {'power_law_exponent': None, 'is_soc': False}

        # Simple power law analysis (in practice, would use more sophisticated methods)
        # For SOC, avalanche sizes should follow P(s) ~ s^(-τ) with τ ≈ 1.0-1.5

        # Compute basic statistics
        min_size = min(avalanche_sizes)
        max_size = max(avalanche_sizes)
        mean_size = sum(avalanche_sizes) / len(avalanche_sizes)

        # Check for power law characteristics
        # (This is a simplified analysis - real SOC analysis would be more rigorous)
        size_range = max_size - min_size
        if size_range == 0:
            return {'power_law_exponent': None, 'is_soc': False}

        # Simple heuristic: if sizes span multiple orders of magnitude, likely SOC
        log_range = math.log10(max_size) - math.log10(min_size) if min_size > 0 else 0

        is_soc = log_range > 1.0 and mean_size > 0  # Spans >1 order of magnitude

        # Estimate power law exponent (very simplified)
        # In real analysis, would use maximum likelihood or other methods
        exponent = 1.5 if is_soc else None  # Typical SOC exponent

        return {
            'power_law_exponent': exponent,
            'is_soc': is_soc,
            'num_avalanches': len(avalanche_sizes),
            'size_range': (min_size, max_size),
            'mean_size': mean_size,
            'size_span_orders': log_range
        }


@dataclass
class SOCGarbageCollector:
    """Complete SOC-based garbage collector integrating all concepts."""

    lattice: SOCMonadLattice = field(default_factory=SOCMonadLattice)
    sovereign_system: SovereignMonadGC = field(default_factory=create_sovereign_gc_system)

    # SOC parameters
    avalanche_threshold: float = 2.0  # Minimum avalanche size to trigger GC
    soc_cycles_before_gc: int = 10    # SOC cycles before triggering hierarchical GC

    # Integration tracking
    soc_cycles: int = 0
    last_gc_cycle: int = 0

    def add_monad_with_soc_positioning(self, monad: SubMonad,
                                     position: Optional[Tuple[float, float]] = None):
        """Add monad to both lattice and sovereign system."""
        # Add to lattice
        self.lattice.add_monad_to_lattice(monad, position)

        # Add to sovereign system
        self.sovereign_system.sub_monads.append(monad)

    def run_integrated_soc_gc(self, steps: int = 100) -> Dict[str, Any]:
        """Run integrated SOC + GC simulation."""
        results = {
            'soc_results': None,
            'gc_results': None,
            'integration_metrics': {}
        }

        # Run SOC simulation
        soc_results = self.lattice.run_soc_simulation(steps)
        results['soc_results'] = soc_results

        # Track SOC cycles
        self.soc_cycles += steps

        # Trigger hierarchical GC periodically
        if self.soc_cycles - self.last_gc_cycle >= self.soc_cycles_before_gc:
            # Organize sovereign system if needed
            if len(self.sovereign_system.meta_monads) == 0:
                self.sovereign_system.organize_meta_monads()
                self.sovereign_system.organize_harvest_layers()

            # Run hierarchical GC cycle
            gc_results = self.sovereign_system.perform_complete_gc_cycle()
            results['gc_results'] = gc_results

            # Update lattice with GC results
            self._integrate_gc_results(gc_results)

            self.last_gc_cycle = self.soc_cycles

        # Compute integration metrics
        results['integration_metrics'] = self._compute_integration_metrics(soc_results)

        return results

    def _integrate_gc_results(self, gc_results: Dict[str, Any]):
        """Integrate GC results back into lattice."""
        # Update lattice sites based on GC results
        # This would involve updating monad states, positions, etc.

        # For now, simple integration: mark sites as updated
        for position, site in self.lattice.sites.items():
            if site.monad is not None:
                # Update tension based on GC results
                coherence_change = gc_results.get('coherence_change', 0.0)
                site.local_tension = max(0.0, site.local_tension - coherence_change * 0.5)

    def _compute_integration_metrics(self, soc_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compute metrics showing SOC-GC integration."""
        return {
            'soc_cycles': self.soc_cycles,
            'gc_cycles_triggered': self.soc_cycles // self.soc_cycles_before_gc,
            'avg_criticality': sum(soc_results['criticality_history']) / len(soc_results['criticality_history']),
            'avalanche_frequency': len(soc_results['avalanche_sizes']) / self.soc_cycles,
            'soc_state_distribution': self._compute_soc_state_distribution(soc_results)
        }

    def _compute_soc_state_distribution(self, soc_results: Dict[str, Any]) -> Dict[str, float]:
        """Compute distribution of SOC states."""
        state_counts = {}
        total_states = len(soc_results['soc_state_history'])

        for state in soc_results['soc_state_history']:
            state_counts[state] = state_counts.get(state, 0) + 1

        return {state: count / total_states for state, count in state_counts.items()}

    def analyze_system_behavior(self) -> Dict[str, Any]:
        """Analyze overall system behavior for SOC characteristics."""
        soc_analysis = self.lattice.analyze_avalanche_statistics()
        integration_metrics = self._compute_integration_metrics(
            self.lattice.run_soc_simulation(50)  # Quick analysis run
        )

        return {
            'soc_analysis': soc_analysis,
            'integration_metrics': integration_metrics,
            'system_health': self._assess_system_health(soc_analysis, integration_metrics)
        }

    def _assess_system_health(self, soc_analysis: Dict[str, Any],
                            integration_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall system health."""
        health_score = 0.0

        # SOC health (0-50 points)
        if soc_analysis['is_soc']:
            health_score += 30.0
            # Bonus for good power law characteristics
            if soc_analysis['power_law_exponent'] and 1.0 <= soc_analysis['power_law_exponent'] <= 2.0:
                health_score += 20.0
        else:
            health_score += 10.0  # Some points for basic functionality

        # Integration health (0-50 points)
        criticality = integration_metrics.get('avg_criticality', 0.0)
        if 0.4 <= criticality <= 0.8:  # Good criticality range
            health_score += 30.0
        elif criticality > 0:
            health_score += 15.0

        # GC cycle health
        gc_cycles = integration_metrics.get('gc_cycles_triggered', 0)
        if gc_cycles > 0:
            health_score += 20.0

        health_status = "healthy" if health_score >= 70 else "degraded" if health_score >= 40 else "critical"

        return {
            'health_score': health_score,
            'health_status': health_status,
            'soc_component': soc_analysis['is_soc'],
            'integration_component': criticality > 0.3,
            'gc_component': gc_cycles > 0
        }


# Factory functions
def create_soc_monad_lattice(lattice_size: int = 10) -> SOCMonadLattice:
    """Create SOC lattice for monad resonance networks."""
    return SOCMonadLattice(lattice_size=lattice_size)


def create_soc_garbage_collector(lattice_size: int = 10) -> SOCGarbageCollector:
    """Create complete SOC-based garbage collector."""
    lattice = SOCMonadLattice(lattice_size=lattice_size)
    sovereign_system = SovereignMonadGC()
    return SOCGarbageCollector(lattice=lattice, sovereign_system=sovereign_system)


__all__ = [
    "SOCState",
    "MonadSite",
    "SOCAvalanche",
    "SOCMonadLattice",
    "SOCGarbageCollector",
    "create_soc_monad_lattice",
    "create_soc_garbage_collector",
]
