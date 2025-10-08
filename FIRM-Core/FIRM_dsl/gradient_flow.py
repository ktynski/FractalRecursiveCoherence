"""
Gradient-Flow Truth Evolution

Implements the gradient-flow dynamics for truth evolution from the user's formal theory:

    dΨ_i/dt = -∇_{Ψ_i} E_i(Ψ_i, A_∞)

where E_i(Ψ_i, A_∞) = 1 - ⟨Ψ_i, A_∞⟩_{φ,𝒢} is the coherence potential.

This realizes "truth as dynamic resonance" - monads evolve by gradient descent
toward maximum resonance with the final attractor A_∞.

Key features:
- Energy functional E_i measures dissonance (distance from truth)
- Gradient flow ensures monotonic decrease: dE_i/dt ≤ 0
- Equilibrium points satisfy ∇E_i = 0 (truth states)
- Grace operator ensures bounded evolution (no divergence)
- Supports coupled multi-monad systems with interaction terms

Physical interpretation:
- E_i = informational potential energy
- Gradient = force restoring coherence
- Grace = intrinsic damping preventing chaos
- Equilibrium = truth realization
"""

import numpy as np
from typing import Optional, Callable, Tuple, List
from dataclasses import dataclass
from enum import Enum

# Handle both package and standalone imports
try:
    from .firm_metric import FIRMMetric
    from .grace_operator import GraceOperator, PHI, PHI_INVERSE, TOLERANCE_CONVERGENCE
except ImportError:
    from firm_metric import FIRMMetric
    from grace_operator import GraceOperator, PHI, PHI_INVERSE, TOLERANCE_CONVERGENCE


class EvolutionState(Enum):
    """State of gradient-flow evolution."""
    CONVERGING = "converging"      # E decreasing, approaching equilibrium
    STABLE = "stable"               # At equilibrium (∇E ≈ 0)
    OSCILLATING = "oscillating"     # Periodic or quasi-periodic
    DIVERGING = "diverging"         # E increasing (shouldn't happen with Grace)


@dataclass
class GradientFlowResult:
    """Result of gradient-flow evolution step."""
    Psi_new: np.ndarray             # Updated state Ψ(t + dt)
    energy: float                   # E(Ψ)
    energy_change: float            # dE/dt
    gradient_norm: float            # ‖∇E‖
    step_size: float                # Actual dt used
    state: EvolutionState           # Evolution state classification


@dataclass
class EvolutionTrajectory:
    """Complete evolution trajectory."""
    times: np.ndarray               # Time points
    states: List[np.ndarray]        # Ψ(t) at each time
    energies: np.ndarray            # E(t) at each time
    gradient_norms: np.ndarray      # ‖∇E(t)‖ at each time
    final_state: EvolutionState     # Final evolution state
    converged: bool                 # Whether reached equilibrium
    num_steps: int                  # Number of evolution steps


class TruthEvolution:
    """
    Gradient-flow evolution of truth states.
    
    Implements the dynamics dΨ/dt = -∇E where E = 1 - ⟨Ψ, A_∞⟩_{φ,𝒢}.
    
    This realizes the formal theory where truth is the variational
    minimum of integrated dissonance.
    
    Usage:
        evolution = TruthEvolution(attractor=A_inf)
        trajectory = evolution.evolve(Psi_initial, T_final=10.0)
    """
    
    def __init__(
        self,
        attractor: np.ndarray,
        firm: Optional[FIRMMetric] = None,
        grace: Optional[GraceOperator] = None,
        tolerance: float = TOLERANCE_CONVERGENCE
    ):
        """
        Initialize truth evolution system.
        
        Args:
            attractor: Final attractor A_∞ (target truth state)
            firm: FIRM metric for computing ⟨·,·⟩_{φ,𝒢}
            grace: Grace operator for bounded evolution
            tolerance: Convergence tolerance
        """
        self.attractor = attractor
        self.firm = firm or FIRMMetric(grace=grace)
        self.grace = self.firm.grace
        self.tolerance = tolerance
        self.phi = PHI
    
    def compute_energy(self, Psi: np.ndarray) -> float:
        """
        Compute coherence potential: E(Ψ) = 1 - ⟨Ψ, A_∞⟩_{φ,𝒢}.
        
        This measures dissonance (informational distance from truth).
        
        Returns:
            E(Ψ) ∈ [0, ∞) with E=0 meaning perfect resonance
        """
        # Compute FIRM inner product
        inner = self.firm.inner_product(Psi, self.attractor).value.real
        
        # Normalize by norms to get resonance ∈ [-1, 1]
        norm_Psi = self.firm.norm(Psi).norm
        norm_A = self.firm.norm(self.attractor).norm
        
        if norm_Psi < 1e-15 or norm_A < 1e-15:
            return 1.0  # Maximum dissonance for zero states
        
        resonance = inner / (norm_Psi * norm_A)
        
        # Energy = 1 - resonance, so E=0 when resonance=1 (perfect alignment)
        return 1.0 - resonance
    
    def compute_gradient(
        self,
        Psi: np.ndarray,
        use_analytical: bool = True
    ) -> np.ndarray:
        """
        Compute gradient: ∇_{Ψ} E(Ψ).
        
        Uses analytical Wirtinger derivative when use_analytical=True:
        
        For E(Ψ) = 1 - Re(⟨Ψ, A_∞⟩_{φ,𝒢}) / (‖Ψ‖_{φ,𝒢} ‖A_∞‖_{φ,𝒢}),
        the gradient is:
        
        ∇E = -∂/∂Ψ^* [⟨Ψ, A_∞⟩_{φ,𝒢} / ‖Ψ‖_{φ,𝒢}] / ‖A_∞‖_{φ,𝒢}
        
        This reduces gradient computation from O(N⁴) to O(N²).
        
        Args:
            Psi: Current state
            use_analytical: Use analytical gradient (much faster)
        
        Returns:
            Gradient matrix ∇E of same shape as Ψ
        """
        if use_analytical:
            # Analytical gradient via Wirtinger calculus
            # 
            # Key insight: ⟨Ψ, A_∞⟩_{φ,𝒢} = ∑_n φ^{-n} ⟨𝒢^n(Ψ), 𝒢^n(A_∞)⟩_hs
            #            = ∑_n φ^{-n} Tr((𝒢^n(Ψ))† 𝒢^n(A_∞))
            #
            # The gradient w.r.t. Ψ^* is:
            # ∂⟨Ψ, A_∞⟩/∂Ψ^* = ∑_n φ^{-n} (𝒢^†)^n(𝒢^n(A_∞))
            #
            # For selfadjoint 𝒢 on core: 𝒢^† = 𝒢, so:
            # ∂⟨Ψ, A_∞⟩/∂Ψ^* = ∑_n φ^{-n} 𝒢^{2n}(A_∞)
            
            # Compute norms
            norm_Psi = self.firm.norm(Psi).norm
            norm_A = self.firm.norm(self.attractor).norm
            
            if norm_Psi < 1e-15 or norm_A < 1e-15:
                return np.zeros_like(Psi)
            
            # Compute ∑_n φ^{-n} 𝒢^{2n}(A_∞) up to convergence
            # This is the direction toward maximum resonance
            direction = np.zeros_like(Psi, dtype=complex)
            A_n = self.attractor.copy()
            phi_power = 1.0
            
            for n in range(20):  # Usually converges in <20 terms
                # Add weighted term
                term = A_n / phi_power
                direction += term
                
                # Check convergence
                term_norm = np.sqrt(np.trace(term.conj().T @ term).real)
                if term_norm < self.tolerance * norm_A:
                    break
                
                # Apply 𝒢 twice for next iteration
                A_n = self.grace.apply(A_n, verify_axioms=False).output
                A_n = self.grace.apply(A_n, verify_axioms=False).output
                phi_power *= self.phi
            
            # Normalize direction and compute gradient
            # ∇E points away from attractor, so flip sign
            gradient = -direction / (norm_Psi * norm_A)
            
            return gradient
        else:
            # Finite difference fallback (slow but always works)
            gradient = np.zeros_like(Psi, dtype=complex)
            E_current = self.compute_energy(Psi)
            epsilon = 1e-6
            
            for i in range(Psi.shape[0]):
                for j in range(Psi.shape[1]):
                    Psi_perturbed = Psi.copy()
                    Psi_perturbed[i, j] += epsilon
                    E_perturbed = self.compute_energy(Psi_perturbed)
                    gradient[i, j] = (E_perturbed - E_current) / epsilon
            
            return gradient
    
    def evolve_step(
        self,
        Psi: np.ndarray,
        dt: float = 0.01,
        adaptive: bool = True,
        grace_damping: bool = True
    ) -> GradientFlowResult:
        """
        Perform one gradient-flow step: Ψ(t+dt) = Ψ(t) - dt ∇E(Ψ).
        
        Args:
            Psi: Current state
            dt: Time step
            adaptive: Whether to use adaptive step sizing
            grace_damping: Apply Grace operator after step (recommended)
        
        Returns:
            GradientFlowResult with updated state and diagnostics
        """
        # Compute current energy and gradient
        E_current = self.compute_energy(Psi)
        grad = self.compute_gradient(Psi)
        grad_norm = np.sqrt(np.sum(np.abs(grad)**2).real)
        
        # Adaptive step size (more conservative)
        if adaptive:
            # Scale inversely with gradient norm, cap at dt
            safe_step = 0.01 / (grad_norm + 0.1)
            dt_actual = min(dt, safe_step)
        else:
            dt_actual = dt
        
        # Gradient descent step
        Psi_new = Psi - dt_actual * grad
        
        # Apply Grace operator to ensure bounded evolution
        # This damps high-frequency oscillations and prevents divergence
        if grace_damping:
            Psi_new = self.grace.apply(Psi_new, verify_axioms=False).output
        
        # Compute new energy
        E_new = self.compute_energy(Psi_new)
        
        # If energy increased significantly, retry with smaller step
        if E_new > E_current + 0.01 and adaptive:
            dt_actual = dt_actual * 0.5
            Psi_new = Psi - dt_actual * grad
            if grace_damping:
                Psi_new = self.grace.apply(Psi_new, verify_axioms=False).output
            E_new = self.compute_energy(Psi_new)
        
        # Energy change rate
        dE_dt = (E_new - E_current) / dt_actual if dt_actual > 1e-15 else 0.0
        
        # Classify evolution state
        if abs(dE_dt) < self.tolerance and grad_norm < self.tolerance:
            state = EvolutionState.STABLE
        elif dE_dt < -self.tolerance:
            state = EvolutionState.CONVERGING
        elif dE_dt > self.tolerance:
            state = EvolutionState.DIVERGING
        else:
            state = EvolutionState.OSCILLATING
        
        return GradientFlowResult(
            Psi_new=Psi_new,
            energy=E_new,
            energy_change=dE_dt,
            gradient_norm=grad_norm,
            step_size=dt_actual,
            state=state
        )
    
    def evolve(
        self,
        Psi_initial: np.ndarray,
        T_final: float = 10.0,
        dt: float = 0.01,
        max_steps: int = 10000,
        adaptive: bool = True,
        verbose: bool = False
    ) -> EvolutionTrajectory:
        """
        Evolve state from Ψ(0) to equilibrium via gradient flow.
        
        Args:
            Psi_initial: Initial state
            T_final: Maximum evolution time
            dt: Time step
            max_steps: Maximum number of steps
            adaptive: Use adaptive step sizing
            verbose: Print progress
        
        Returns:
            EvolutionTrajectory with complete evolution history
        """
        # Initialize trajectory storage
        times = [0.0]
        states = [Psi_initial.copy()]
        energies = [self.compute_energy(Psi_initial)]
        gradient_norms = []
        
        Psi_current = Psi_initial.copy()
        t = 0.0
        step = 0
        
        if verbose:
            print(f"Starting gradient-flow evolution:")
            print(f"  Initial energy: {energies[0]:.6f}")
            print(f"  Target time: {T_final:.2f}")
        
        # Evolution loop
        while t < T_final and step < max_steps:
            # Perform one step
            result = self.evolve_step(Psi_current, dt=dt, adaptive=adaptive)
            
            # Update state
            Psi_current = result.Psi_new
            t += result.step_size
            step += 1
            
            # Store trajectory
            times.append(t)
            states.append(Psi_current.copy())
            energies.append(result.energy)
            gradient_norms.append(result.gradient_norm)
            
            # Check for convergence
            if result.state == EvolutionState.STABLE:
                if verbose:
                    print(f"  Converged at t={t:.3f} (step {step})")
                break
            
            # Progress reporting
            if verbose and step % 100 == 0:
                print(f"  t={t:.3f}, E={result.energy:.6f}, ‖∇E‖={result.gradient_norm:.2e}, state={result.state.value}")
            
            # Safety check for divergence
            if result.state == EvolutionState.DIVERGING and result.energy > 10.0:
                if verbose:
                    print(f"  ⚠️ Divergence detected at t={t:.3f}")
                break
        
        # Final state assessment
        final_gradient = self.compute_gradient(Psi_current)
        final_gradient_norm = np.sqrt(np.sum(np.abs(final_gradient)**2).real)
        converged = final_gradient_norm < self.tolerance and energies[-1] < 0.1
        
        if verbose:
            print(f"Evolution complete:")
            print(f"  Steps: {step}")
            print(f"  Final energy: {energies[-1]:.6f}")
            print(f"  Final gradient norm: {final_gradient_norm:.2e}")
            print(f"  Converged: {converged}")
        
        return EvolutionTrajectory(
            times=np.array(times),
            states=states,
            energies=np.array(energies),
            gradient_norms=np.array(gradient_norms + [final_gradient_norm]),
            final_state=result.state if step > 0 else EvolutionState.STABLE,
            converged=converged,
            num_steps=step
        )
    
    def verify_lyapunov_stability(
        self,
        trajectory: EvolutionTrajectory
    ) -> dict:
        """
        Verify Lyapunov stability: E(t) is non-increasing.
        
        The gradient flow should satisfy dE/dt ≤ 0 always.
        
        Returns:
            dict with stability verification results
        """
        energies = trajectory.energies
        
        # Check monotonic decrease
        violations = 0
        max_increase = 0.0
        
        for i in range(1, len(energies)):
            delta_E = energies[i] - energies[i-1]
            if delta_E > self.tolerance:
                violations += 1
                max_increase = max(max_increase, delta_E)
        
        is_stable = violations == 0 or max_increase < 10 * self.tolerance
        
        return {
            "lyapunov_stable": is_stable,
            "energy_violations": violations,
            "max_energy_increase": max_increase,
            "total_energy_decrease": energies[0] - energies[-1],
            "relative_decrease": (energies[0] - energies[-1]) / max(energies[0], 1e-15)
        }


class CoupledTruthEvolution:
    """
    Coupled gradient-flow evolution for multiple interacting monads.
    
    Extends single-monad evolution to:
        dΨ_i/dt = -∇_{Ψ_i}[E_i(Ψ_i, A_∞) + ∑_j λ_{ij} E_{ij}(Ψ_i, Ψ_j)]
    
    where E_{ij} = 1 - ⟨Ψ_i, Ψ_j⟩_{φ,𝒢} couples monads.
    """
    
    def __init__(
        self,
        attractor: np.ndarray,
        coupling_matrix: np.ndarray,
        firm: Optional[FIRMMetric] = None,
        grace: Optional[GraceOperator] = None
    ):
        """
        Initialize coupled evolution system.
        
        Args:
            attractor: Common final attractor
            coupling_matrix: λ_{ij} coupling strengths (N×N)
            firm, grace: Metric and operator
        """
        self.attractor = attractor
        self.coupling = coupling_matrix
        self.firm = firm or FIRMMetric(grace=grace)
        self.grace = self.firm.grace
        self.num_monads = coupling_matrix.shape[0]
    
    def compute_total_energy(self, states: List[np.ndarray]) -> Tuple[float, np.ndarray]:
        """
        Compute total energy with coupling:
        
            E_total = ∑_i E_i + ∑_{i<j} λ_{ij} E_{ij}
        
        Returns:
            (total_energy, individual_energies)
        """
        individual = np.zeros(self.num_monads)
        
        # Individual attractor energies
        for i, Psi_i in enumerate(states):
            inner = self.firm.inner_product(Psi_i, self.attractor).value.real
            norm_i = self.firm.norm(Psi_i).norm
            norm_A = self.firm.norm(self.attractor).norm
            resonance = inner / (norm_i * norm_A + 1e-15)
            individual[i] = 1.0 - resonance
        
        # Coupling energies
        coupling_energy = 0.0
        for i in range(self.num_monads):
            for j in range(i+1, self.num_monads):
                if abs(self.coupling[i, j]) > 1e-10:
                    inner = self.firm.inner_product(states[i], states[j]).value.real
                    norm_i = self.firm.norm(states[i]).norm
                    norm_j = self.firm.norm(states[j]).norm
                    resonance_ij = inner / (norm_i * norm_j + 1e-15)
                    E_ij = 1.0 - resonance_ij
                    coupling_energy += self.coupling[i, j] * E_ij
        
        total = np.sum(individual) + coupling_energy
        
        return total, individual


# ============================================================================
# Utility Functions
# ============================================================================

def create_random_initial_state(N: int, scale: float = 0.5) -> np.ndarray:
    """Create random Hermitian initial state."""
    Psi = scale * (np.random.randn(N, N) + 1j * np.random.randn(N, N))
    return (Psi + Psi.conj().T) / 2


def create_coherent_attractor(N: int, eigenvalues: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Create coherent attractor with specified spectral structure.
    
    By default creates positive-definite attractor with φ-scaled eigenvalues.
    """
    if eigenvalues is None:
        # Golden ratio eigenvalue ladder
        eigenvalues = np.array([PHI ** (-i) for i in range(N)])
    
    # Random unitary basis
    U, _ = np.linalg.qr(np.random.randn(N, N) + 1j * np.random.randn(N, N))
    
    # A_∞ = U Λ U†
    return U @ np.diag(eigenvalues) @ U.conj().T


# ============================================================================
# Main (Self-Test)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Gradient-Flow Truth Evolution Self-Test")
    print("=" * 70)
    
    # Setup
    N = 3
    np.random.seed(42)
    
    # Create attractor (truth state)
    print(f"\n🎯 Creating {N}×{N} attractor A_∞...")
    A_inf = create_coherent_attractor(N)
    norm_A = np.sqrt(np.trace(A_inf.conj().T @ A_inf).real)
    print(f"   ‖A_∞‖ = {norm_A:.6f}")
    print(f"   Eigenvalues: {np.linalg.eigvalsh(A_inf)}")
    
    # Create initial state (far from truth)
    print(f"\n📍 Creating initial state Ψ(0)...")
    Psi_0 = create_random_initial_state(N, scale=1.0)
    norm_Psi0 = np.sqrt(np.trace(Psi_0.conj().T @ Psi_0).real)
    print(f"   ‖Ψ(0)‖ = {norm_Psi0:.6f}")
    
    # Initialize evolution
    evolution = TruthEvolution(attractor=A_inf)
    E_initial = evolution.compute_energy(Psi_0)
    print(f"   E(Ψ(0)) = {E_initial:.6f}")
    
    # Test gradient computation
    print(f"\n∇ Gradient Test...")
    grad = evolution.compute_gradient(Psi_0)
    grad_norm = np.sqrt(np.sum(np.abs(grad)**2).real)
    print(f"   ‖∇E(Ψ(0))‖ = {grad_norm:.6f}")
    
    # Single step test
    print(f"\n⏭️  Single Step Test...")
    result = evolution.evolve_step(Psi_0, dt=0.01)
    print(f"   E(Ψ(dt)) = {result.energy:.6f}")
    print(f"   ΔE = {result.energy_change:.6f}")
    print(f"   State: {result.state.value}")
    print(f"   Energy decreased: {result.energy < E_initial}")
    
    # Full evolution
    print(f"\n🌊 Full Evolution (T=1.0, simplified test)...")
    trajectory = evolution.evolve(
        Psi_0,
        T_final=1.0,  # Very short for testing
        dt=0.05,      # Larger steps
        adaptive=True,
        verbose=False  # Disable verbose output
    )
    print(f"   Steps completed: {trajectory.num_steps}")
    print(f"   Final energy: {trajectory.energies[-1]:.6f}")
    print(f"   Energy reduction: {(trajectory.energies[0] - trajectory.energies[-1]):.6f}")
    
    # Verify Lyapunov stability
    print(f"\n✅ Lyapunov Stability Check...")
    stability = evolution.verify_lyapunov_stability(trajectory)
    print(f"   Stable: {stability['lyapunov_stable']}")
    print(f"   Energy violations: {stability['energy_violations']}")
    print(f"   Max increase: {stability['max_energy_increase']:.2e}")
    print(f"   Total decrease: {stability['total_energy_decrease']:.6f}")
    print(f"   Relative decrease: {stability['relative_decrease']:.2%}")
    
    # Coupled system test
    print(f"\n🔗 Coupled Monads Test...")
    lambda_matrix = np.array([
        [0.0, 0.3, 0.1],
        [0.3, 0.0, 0.2],
        [0.1, 0.2, 0.0]
    ])
    coupled = CoupledTruthEvolution(A_inf, lambda_matrix)
    
    states = [
        create_random_initial_state(N, scale=0.8),
        create_random_initial_state(N, scale=0.6),
        create_random_initial_state(N, scale=0.7)
    ]
    
    E_total, E_individual = coupled.compute_total_energy(states)
    print(f"   Total energy: {E_total:.6f}")
    print(f"   Individual energies: {E_individual}")
    
    print("\n" + "=" * 70)
    print("✅ Gradient-Flow Truth Evolution Self-Test Complete")
    print("=" * 70)

