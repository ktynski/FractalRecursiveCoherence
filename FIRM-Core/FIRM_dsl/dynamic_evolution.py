"""dynamic_evolution.py

Dynamic phase evolution framework for Soul Garbage Collection.

Implements the theoretical equation:
dΦ_i/dt = -α_i ∇_Φ D_i + β_i Transmute(D_i) + γ_i Grace(Φ_i)

This bridges the gap between static analysis and dynamic evolution in the 𝒮-GC system.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import math
import time

from .core import ObjectG, NodeLabel, normalize_phase_qpi
from .resonance import OmegaSignature, compute_resonance_alignment, derive_omega_signature
from .coherence import compute_coherence
from .grace_field import GraceFieldParams, potential_V, dV_du, FieldRegime


class EvolutionState(Enum):
    """States of dynamic evolution process."""
    STABLE = "stable"
    EVOLVING = "evolving"
    CONVERGING = "converging"
    DIVERGING = "diverging"
    OSCILLATING = "oscillating"


@dataclass
class EvolutionMetrics:
    """Metrics for tracking evolution progress."""
    coherence_history: List[float] = field(default_factory=list)
    resonance_history: List[float] = field(default_factory=list)
    phase_history: List[Dict[str, float]] = field(default_factory=list)
    evolution_rate: float = 0.0
    convergence_rate: float = 0.0
    oscillation_amplitude: float = 0.0
    state: EvolutionState = EvolutionState.STABLE


@dataclass
class DynamicPhaseEvolution:
    """Implements dynamic phase evolution for 𝒮-GC.

    Theoretical foundation:
    dΦ_i/dt = -α_i ∇_Φ D_i + β_i Transmute(D_i) + γ_i Grace(Φ_i)

    Where:
    - Φ_i: Phase of structure i
    - D_i: Dissonance measure |Φ_i - Ω|
    - ∇_Φ D_i: Gradient of dissonance w.r.t. phase
    - Transmute(D_i): Cross-monad resonance mediation term
    - Grace(Φ_i): Grace field contribution
    """

    alpha_i: float  # Resonance gradient coefficient
    beta_i: float   # Transmutation coefficient
    gamma_i: float  # Grace field coefficient
    dt: float = 0.01  # Time step for evolution
    max_iterations: int = 1000
    convergence_threshold: float = 1e-6
    oscillation_threshold: float = 0.1

    def __post_init__(self):
        """Validate coefficients."""
        if not all(c >= 0 for c in [self.alpha_i, self.beta_i, self.gamma_i]):
            raise ValueError("All evolution coefficients must be non-negative")

    def compute_dissonance_gradient(self, phi_i: float, omega: OmegaSignature,
                                 structure: ObjectG) -> float:
        """Compute ∇_Φ D_i - gradient of dissonance with respect to phase.

        Theory: Dissonance D_i = |Φ_i - Ω| where Ω is the attractor phase.
        The gradient ∇_Φ D_i = sign(Φ_i - Ω) for the phase component.
        """
        # Get current structure resonance (which measures dissonance)
        current_resonance = compute_resonance_alignment(structure, omega)

        # For gradient computation, we need to consider how resonance changes
        # with phase perturbations. This is a simplified gradient estimate.
        dissonance = 1.0 - current_resonance  # Convert resonance to dissonance

        # Estimate gradient by perturbing phase slightly
        epsilon = 1e-6
        perturbed_structure = self._perturb_phase(structure, epsilon)
        perturbed_resonance = compute_resonance_alignment(perturbed_structure, omega)
        perturbed_dissonance = 1.0 - perturbed_resonance

        gradient = (perturbed_dissonance - dissonance) / epsilon
        return gradient

    def compute_transmutation(self, phi_i: float, omega: OmegaSignature,
                            structure: ObjectG) -> float:
        """Compute Transmute(D_i) - cross-monad resonance mediation.

        This implements the transmutative mediation between different
        monadic structures to enhance overall coherence.
        """
        # For now, implement a simplified transmutation based on
        # structure connectivity and phase diversity
        coherence = compute_coherence(structure)

        # Transmutation factor based on phase diversity within structure
        phase_diversity = self._compute_phase_diversity(structure)

        # Transmutation promotes structures with balanced phase diversity
        # Optimal diversity around 0.5-0.7 for good mediation
        optimal_diversity = 0.6
        transmutation_factor = 1.0 - abs(phase_diversity - optimal_diversity)

        return coherence * transmutation_factor

    def compute_grace_field(self, phi_i: float, field_regime: FieldRegime) -> float:
        """Compute Grace(Φ_i) - grace field contribution to evolution.

        The grace field provides the potential landscape that guides
        structures toward more coherent configurations.
        """
        # Grace field strength varies by regime
        regime_multipliers = {
            FieldRegime.NON_BEING: 0.1,
            FieldRegime.VACUUM: 0.3,
            FieldRegime.DARK_SECTOR: 0.6,
            FieldRegime.MATTER: 0.8,
            FieldRegime.OMEGA: 1.0
        }

        base_grace = regime_multipliers.get(field_regime, 0.5)

        # Grace field also depends on current phase coherence
        # More coherent phases receive stronger grace field guidance
        # Canonical baseline: φ⁻¹ ≈ 0.618 represents natural vacuum potential
        PHI_INVERSE = 1 / 1.618033988749  # ≈ 0.618
        phase_coherence_factor = min(1.0, phi_i / PHI_INVERSE)  # Normalize relative to golden baseline

        return base_grace * phase_coherence_factor

    def evolve_structure(self, structure: ObjectG, omega: OmegaSignature,
                        field_regime: FieldRegime,
                        max_steps: int = None) -> Tuple[ObjectG, EvolutionMetrics]:
        """Evolve a structure according to the dynamic equation.

        Returns the evolved structure and evolution metrics.
        """
        current_structure = structure.copy() if hasattr(structure, 'copy') else structure
        metrics = EvolutionMetrics()
        max_steps = max_steps or self.max_iterations

        for step in range(max_steps):
            # Compute current state
            current_coherence = compute_coherence(current_structure)
            current_resonance = compute_resonance_alignment(current_structure, omega)

            # Extract representative phase for evolution (simplified)
            phi_i = self._extract_representative_phase(current_structure)

            # Compute evolution terms
            dissonance_gradient = self.compute_dissonance_gradient(
                phi_i, omega, current_structure
            )
            transmutation_term = self.compute_transmutation(
                phi_i, omega, current_structure
            )
            grace_term = self.compute_grace_field(phi_i, field_regime)

            # Apply evolution equation: dΦ_i/dt = -α ∇_Φ D_i + β Transmute + γ Grace
            phase_derivative = (
                -self.alpha_i * dissonance_gradient +
                self.beta_i * transmutation_term +
                self.gamma_i * grace_term
            )

            # Update phase (simplified - in full implementation would update node phases)
            new_phi_i = phi_i + phase_derivative * self.dt

            # Apply phase update to structure
            evolved_structure = self._apply_phase_evolution(
                current_structure, phi_i, new_phi_i, omega
            )

            # Update metrics
            evolved_coherence = compute_coherence(evolved_structure)
            evolved_resonance = compute_resonance_alignment(evolved_structure, omega)

            metrics.coherence_history.append(evolved_coherence)
            metrics.resonance_history.append(evolved_resonance)
            metrics.phase_history.append({'step': step, 'phase': new_phi_i})

            # Check convergence
            if self._check_convergence(metrics, step):
                metrics.state = EvolutionState.CONVERGING
                break

            # Check oscillation
            if self._check_oscillation(metrics, step):
                metrics.state = EvolutionState.OSCILLATING
                break

            current_structure = evolved_structure

            # Safety check for divergence
            if self._check_divergence(metrics, step):
                metrics.state = EvolutionState.DIVERGING
                break

        # Final metrics computation
        self._compute_final_metrics(metrics)

        return evolved_structure, metrics

    def _perturb_phase(self, structure: ObjectG, epsilon: float) -> ObjectG:
        """Create a perturbed version of the structure for gradient computation."""
        # Simplified perturbation - in full implementation would modify node phases
        perturbed_structure = ObjectG(
            nodes=structure.nodes.copy(),
            edges=structure.edges.copy(),
            labels=structure.labels.copy()
        )

        # Perturb a representative node's phase
        if perturbed_structure.labels:
            first_node_id = next(iter(perturbed_structure.labels.keys()))
            original_label = perturbed_structure.labels[first_node_id]

            # Add small phase perturbation
            new_numer = original_label.phase_numer + epsilon
            new_denom = original_label.phase_denom

            perturbed_label = NodeLabel(
                original_label.kind,
                int(new_numer),
                new_denom,
                original_label.monadic_id
            )

            perturbed_structure.labels[first_node_id] = perturbed_label

        return perturbed_structure

    def _compute_phase_diversity(self, structure: ObjectG) -> float:
        """Compute phase diversity within a structure."""
        if not structure.labels:
            return 0.0

        phases = []
        for label in structure.labels.values():
            phase_angle = 2 * math.pi * label.phase_numer / label.phase_denom
            phases.append(phase_angle)

        if len(phases) <= 1:
            return 0.0

        # Compute standard deviation of phases normalized to [0,1]
        mean_phase = sum(phases) / len(phases)
        variance = sum((p - mean_phase) ** 2 for p in phases) / len(phases)
        std_dev = math.sqrt(variance)

        # Normalize to [0,1] range (max possible std dev is π)
        return min(1.0, std_dev / math.pi)

    def _extract_representative_phase(self, structure: ObjectG) -> float:
        """Extract a representative phase value from the structure."""
        if not structure.labels:
            return 0.0

        # Use average phase as representative
        total_phase = 0.0
        count = 0

        for label in structure.labels.values():
            phase_angle = 2 * math.pi * label.phase_numer / label.phase_denom
            total_phase += phase_angle
            count += 1

        return total_phase / count if count > 0 else 0.0

    def _apply_phase_evolution(self, structure: ObjectG, old_phi: float,
                             new_phi: float, omega: OmegaSignature) -> ObjectG:
        """Apply phase evolution to structure nodes."""
        evolved_structure = ObjectG(
            nodes=structure.nodes.copy(),
            edges=structure.edges.copy(),
            labels=structure.labels.copy()
        )

        # Apply phase evolution to all nodes (simplified approach)
        phase_shift = new_phi - old_phi

        for node_id, label in evolved_structure.labels.items():
            # Convert phase shift back to rational representation
            old_phase_angle = 2 * math.pi * label.phase_numer / label.phase_denom
            new_phase_angle = old_phase_angle + phase_shift

            # Clamp to valid range [0, 2π)
            new_phase_angle = new_phase_angle % (2 * math.pi)

            # Convert back to rational (simplified)
            new_numer = int(round(new_phase_angle * label.phase_denom / (2 * math.pi)))
            new_numer = max(0, min(new_numer, 2 * label.phase_denom - 1))  # Ensure valid range

            evolved_label = NodeLabel(
                label.kind,
                new_numer,
                label.phase_denom,
                label.monadic_id
            )

            evolved_structure.labels[node_id] = evolved_label

        return evolved_structure

    def _check_convergence(self, metrics: EvolutionMetrics, step: int) -> bool:
        """Check if evolution is converging."""
        if len(metrics.coherence_history) < 10:
            return False

        recent_coherence = metrics.coherence_history[-10:]
        coherence_range = max(recent_coherence) - min(recent_coherence)

        return coherence_range < self.convergence_threshold

    def _check_oscillation(self, metrics: EvolutionMetrics, step: int) -> bool:
        """Check if evolution is oscillating."""
        if len(metrics.coherence_history) < 20:
            return False

        recent_coherence = metrics.coherence_history[-20:]
        oscillations = 0

        for i in range(1, len(recent_coherence) - 1):
            if (recent_coherence[i] - recent_coherence[i-1]) * (recent_coherence[i+1] - recent_coherence[i]) < 0:
                oscillations += 1

        oscillation_ratio = oscillations / (len(recent_coherence) - 2)
        return oscillation_ratio > 0.3  # More than 30% of steps are oscillation points

    def _check_divergence(self, metrics: EvolutionMetrics, step: int) -> bool:
        """Check if evolution is diverging."""
        if len(metrics.coherence_history) < 10:
            return False

        # Check if coherence is consistently decreasing over a longer window
        recent_coherence = metrics.coherence_history[-10:]

        # Only consider it divergence if coherence is decreasing significantly
        # and consistently over multiple steps
        coherence_changes = [
            recent_coherence[i+1] - recent_coherence[i]
            for i in range(len(recent_coherence) - 1)
        ]

        negative_changes = [c for c in coherence_changes if c < -0.01]  # Small threshold
        negative_ratio = len(negative_changes) / len(coherence_changes)

        # Divergence if more than 70% of recent changes are negative
        # and the trend is significantly downward
        trend = sum(coherence_changes) / len(coherence_changes)
        return negative_ratio > 0.7 and trend < -0.05

    def _compute_final_metrics(self, metrics: EvolutionMetrics):
        """Compute final evolution metrics."""
        if len(metrics.coherence_history) < 2:
            return

        # Evolution rate (change per step)
        coherence_changes = [
            metrics.coherence_history[i+1] - metrics.coherence_history[i]
            for i in range(len(metrics.coherence_history) - 1)
        ]
        metrics.evolution_rate = sum(coherence_changes) / len(coherence_changes)

        # Convergence rate (how quickly approaching final state)
        if len(metrics.coherence_history) >= 10:
            final_coherence = metrics.coherence_history[-1]
            initial_coherence = metrics.coherence_history[0]

            if abs(final_coherence - initial_coherence) > 1e-6:
                total_change = final_coherence - initial_coherence
                steps_needed = len(metrics.coherence_history)
                metrics.convergence_rate = total_change / steps_needed

        # Oscillation amplitude
        if len(metrics.coherence_history) >= 20:
            recent_coherence = metrics.coherence_history[-20:]
            metrics.oscillation_amplitude = max(recent_coherence) - min(recent_coherence)


@dataclass
class ModeCoefficients:
    """Dynamic mode coefficient management based on field regime."""

    coefficient_sets: Dict[FieldRegime, Tuple[float, float, float]] = field(default_factory=lambda: {
        FieldRegime.NON_BEING: (0.1, 0.1, 0.1),
        FieldRegime.VACUUM: (0.3, 0.2, 0.4),
        FieldRegime.DARK_SECTOR: (0.5, 0.4, 0.6),
        FieldRegime.MATTER: (0.7, 0.6, 0.8),
        FieldRegime.OMEGA: (1.0, 1.0, 1.0)
    })

    def get_coefficients(self, field_regime: FieldRegime) -> Tuple[float, float, float]:
        """Get evolution coefficients for a field regime."""
        return self.coefficient_sets.get(field_regime, (0.5, 0.5, 0.5))

    def adapt_coefficients(self, field_regime: FieldRegime,
                          evolution_metrics: EvolutionMetrics) -> Tuple[float, float, float]:
        """Adapt coefficients based on evolution performance."""
        base_coeffs = self.get_coefficients(field_regime)

        # Adjust based on evolution state
        if evolution_metrics.state == EvolutionState.DIVERGING:
            # Reduce coefficients to slow down evolution
            adaptation_factor = 0.7
        elif evolution_metrics.state == EvolutionState.OSCILLATING:
            # Reduce alpha (resonance gradient) to dampen oscillations
            alpha_factor = 0.6
            return (base_coeffs[0] * alpha_factor, base_coeffs[1], base_coeffs[2])
        elif evolution_metrics.state == EvolutionState.CONVERGING:
            # Slightly increase coefficients for faster convergence
            adaptation_factor = 1.2
        else:
            adaptation_factor = 1.0

        return tuple(c * adaptation_factor for c in base_coeffs)


# Factory functions for easy creation
def create_dynamic_evolution(alpha: float = 0.5, beta: float = 0.3,
                           gamma: float = 0.4, dt: float = 0.01) -> DynamicPhaseEvolution:
    """Create a dynamic evolution system with specified coefficients."""
    return DynamicPhaseEvolution(alpha_i=alpha, beta_i=beta, gamma_i=gamma, dt=dt)


def create_mode_coefficients() -> ModeCoefficients:
    """Create default mode coefficient manager."""
    return ModeCoefficients()


__all__ = [
    "DynamicPhaseEvolution",
    "ModeCoefficients",
    "EvolutionState",
    "EvolutionMetrics",
    "create_dynamic_evolution",
    "create_mode_coefficients",
]
