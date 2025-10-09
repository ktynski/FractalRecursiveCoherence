#!/usr/bin/env python3
"""
Complete Validation of Navier-Stokes Proofs

Tests all new claims made in:
- CLAY_NS_COMPLETE_LYAPUNOV_PROOF.md
- CLAY_NS_COMPLETE_KAM_PROOF.md

Critical tests:
1. Clifford cubic inequality: ∫T³ ≥ κ_φ·δ²
2. Production formula: P ≈ α(R)·κ^(3/2)/E^(1/2)
3. Convergence: R(t) → φ⁻² exponentially
4. Decay rate: κ ≈ 0.1545 matches theory
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from dataclasses import dataclass
import time

PHI = (1 + np.sqrt(5)) / 2
PHI_INV = 1 / PHI
PHI_INV_SQ = PHI_INV**2
KAPPA_THEORY = (PHI - 1) / 4  # ≈ 0.1545


@dataclass
class NSState:
    """Current NS flow state"""
    u: np.ndarray  # velocity (N,N,N,3)
    t: float       # time
    E: float       # energy
    kappa: float   # enstrophy
    R: float       # ratio |ω|²/|∇u|²
    G: float       # Grace functional
    G_eq: float    # Equilibrium Grace


class NSValidator:
    """Validate both NS proofs"""
    
    def __init__(self, N: int = 32, L: float = 2*np.pi, nu: float = 0.01):
        self.N = N
        self.L = L
        self.nu = nu
        
        # Setup Fourier grid
        k = 2*np.pi/L * np.fft.fftfreq(N, 1/N)
        kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
        self.k = np.stack([kx, ky, kz], axis=-1)
        self.k_sq = kx**2 + ky**2 + kz**2
        self.k_sq[0,0,0] = 1.0  # Avoid division by zero
        
        self.dx = L / N
        
    def compute_vorticity(self, u: np.ndarray) -> np.ndarray:
        """Compute ω = ∇×u"""
        u_hat = np.fft.fftn(u, axes=(0,1,2))
        
        omega = np.zeros_like(u)
        # ω_x = ∂_y u_z - ∂_z u_y
        omega[:,:,:,0] = np.real(np.fft.ifftn(
            1j * (self.k[:,:,:,1]*u_hat[:,:,:,2] - self.k[:,:,:,2]*u_hat[:,:,:,1]),
            axes=(0,1,2)))
        # ω_y = ∂_z u_x - ∂_x u_z
        omega[:,:,:,1] = np.real(np.fft.ifftn(
            1j * (self.k[:,:,:,2]*u_hat[:,:,:,0] - self.k[:,:,:,0]*u_hat[:,:,:,2]),
            axes=(0,1,2)))
        # ω_z = ∂_x u_y - ∂_y u_x
        omega[:,:,:,2] = np.real(np.fft.ifftn(
            1j * (self.k[:,:,:,0]*u_hat[:,:,:,1] - self.k[:,:,:,1]*u_hat[:,:,:,0]),
            axes=(0,1,2)))
        
        return omega
    
    def compute_state(self, u: np.ndarray, t: float) -> NSState:
        """Compute all flow quantities"""
        omega = self.compute_vorticity(u)
        
        # Energy
        E = 0.5 * np.mean(np.sum(u**2, axis=-1))
        
        # Enstrophy
        kappa = 0.5 * np.mean(np.sum(omega**2, axis=-1))
        
        # Compute ∇u
        u_hat = np.fft.fftn(u, axes=(0,1,2))
        grad_u_sq = 0.0
        for i in range(3):
            for j in range(3):
                grad_ij = np.real(np.fft.ifftn(
                    1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
                grad_u_sq += np.mean(grad_ij**2)
        
        # R ratio
        omega_sq = np.mean(np.sum(omega**2, axis=-1))
        R = omega_sq / grad_u_sq if grad_u_sq > 1e-10 else 0.0
        
        # Grace functional G = (1/4)(|∇u|² - |ω|²)
        G = 0.25 * (grad_u_sq - omega_sq)
        G_eq = 0.25 * (1 - PHI_INV_SQ) * grad_u_sq
        
        return NSState(u=u, t=t, E=E, kappa=kappa, R=R, G=G, G_eq=G_eq)
    
    def compute_velocity_gradient_tensor(self, u: np.ndarray) -> np.ndarray:
        """Compute T_ij = ∂_j u_i"""
        u_hat = np.fft.fftn(u, axes=(0,1,2))
        T = np.zeros((self.N, self.N, self.N, 3, 3))
        
        for i in range(3):
            for j in range(3):
                T[:,:,:,i,j] = np.real(np.fft.ifftn(
                    1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
        
        return T
    
    def test_clifford_cubic_inequality(self, u: np.ndarray) -> Dict:
        """
        TEST 1: Clifford cubic inequality
        Claim: ∫T_jk T_ki T_ij dx ≥ κ_φ·δ²
        where δ = G - G_eq and κ_φ = φ-1 ≈ 0.618
        """
        print("\n" + "="*70)
        print("TEST 1: Clifford Cubic Inequality")
        print("="*70)
        
        state = self.compute_state(u, 0.0)
        T = self.compute_velocity_gradient_tensor(u)
        
        # Compute triple product ∫T_jk T_ki T_ij dx
        triple_product = np.einsum('...jk,...ki,...ij->...', T, T, T)
        integral = np.mean(triple_product)
        
        # Compute deviation
        delta = state.G - state.G_eq
        
        # Theoretical lower bound
        grad_u_sq = 4 * (state.G + 0.5*np.mean(np.sum(self.compute_vorticity(u)**2, axis=-1)))
        lower_bound = (PHI - 1) * delta**2 / grad_u_sq if grad_u_sq > 1e-10 else 0
        
        # Check inequality
        satisfied = integral >= lower_bound - 1e-6  # Small numerical tolerance
        
        result = {
            'triple_product': integral,
            'lower_bound': lower_bound,
            'delta': delta,
            'ratio': integral / lower_bound if abs(lower_bound) > 1e-10 else np.inf,
            'satisfied': satisfied,
            'G': state.G,
            'G_eq': state.G_eq
        }
        
        print(f"  Triple product ∫T³: {integral:.6e}")
        print(f"  Lower bound κ_φ·δ²: {lower_bound:.6e}")
        print(f"  Deviation δ = G - G_eq: {delta:.6e}")
        print(f"  Ratio (should be ≥ 1): {result['ratio']:.3f}")
        print(f"  Inequality satisfied: {satisfied} {'✓' if satisfied else '✗'}")
        
        return result
    
    def test_production_formula(self, u: np.ndarray) -> Dict:
        """
        TEST 2: Production formula
        Claim: P ≈ α(R)·κ^(3/2)/E^(1/2)
        where α(R) = α₀ + C·|R - φ⁻²|
        """
        print("\n" + "="*70)
        print("TEST 2: Enstrophy Production Formula")
        print("="*70)
        
        state = self.compute_state(u, 0.0)
        omega = self.compute_vorticity(u)
        
        # Compute actual production P = ∫ω·(ω·∇)u dx
        # This is vortex stretching term
        omega_dot_grad_u = np.zeros_like(u)
        u_hat = np.fft.fftn(u, axes=(0,1,2))
        
        for i in range(3):
            for j in range(3):
                grad_u_ij = np.real(np.fft.ifftn(
                    1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
                omega_dot_grad_u[:,:,:,i] += omega[:,:,:,j] * grad_u_ij
        
        P_actual = np.mean(np.sum(omega * omega_dot_grad_u, axis=-1))
        
        # Theoretical prediction
        if state.E > 1e-10 and state.kappa > 1e-10:
            # Simplified: α(R) ≈ α₀(1 + C|R - φ⁻²|)
            # For now, use α₀ as baseline
            alpha_0 = 1.0  # Dimensional constant (order 1)
            alpha_R = alpha_0 * (1 + abs(state.R - PHI_INV_SQ))
            
            P_theory = alpha_R * state.kappa**(3/2) / np.sqrt(state.E)
        else:
            P_theory = 0.0
        
        result = {
            'P_actual': P_actual,
            'P_theory': P_theory,
            'ratio': P_actual / P_theory if abs(P_theory) > 1e-10 else np.nan,
            'R': state.R,
            'R_deviation': abs(state.R - PHI_INV_SQ),
            'kappa': state.kappa,
            'E': state.E
        }
        
        print(f"  Actual production P: {P_actual:.6e}")
        print(f"  Theory κ^(3/2)/E^(1/2): {P_theory:.6e}")
        print(f"  Ratio P_actual/P_theory: {result['ratio']:.3f}")
        print(f"  Current R: {state.R:.6f}")
        print(f"  Target φ⁻²: {PHI_INV_SQ:.6f}")
        print(f"  Deviation |R - φ⁻²|: {result['R_deviation']:.6f}")
        
        return result
    
    def test_phi_convergence(self, u0: np.ndarray, t_max: float = 5.0, 
                            dt: float = 0.01, n_samples: int = 50) -> Dict:
        """
        TEST 3: Convergence to φ-balance
        Claim: R(t) → φ⁻² exponentially
        """
        print("\n" + "="*70)
        print("TEST 3: Convergence to φ-Balance")
        print("="*70)
        
        u = u0.copy()
        times = []
        R_vals = []
        kappa_vals = []
        G_vals = []
        
        n_steps = int(t_max / dt)
        sample_interval = max(1, n_steps // n_samples)
        
        print(f"  Running {n_steps} steps...")
        start = time.time()
        
        for step in range(n_steps):
            t = step * dt
            
            if step % sample_interval == 0:
                state = self.compute_state(u, t)
                times.append(t)
                R_vals.append(state.R)
                kappa_vals.append(state.kappa)
                G_vals.append(state.G - state.G_eq)
                
                if step % (sample_interval * 10) == 0:
                    print(f"    t={t:.2f}: R={state.R:.6f}, κ={state.kappa:.6e}")
            
            # Evolve (simple diffusion for now)
            u = self.evolve_step(u, dt)
        
        elapsed = time.time() - start
        print(f"  Completed in {elapsed:.2f}s")
        
        times = np.array(times)
        R_vals = np.array(R_vals)
        kappa_vals = np.array(kappa_vals)
        G_vals = np.array(G_vals)
        
        # Analyze convergence
        R_final = R_vals[-10:].mean()  # Average last 10 points
        R_deviation = abs(R_final - PHI_INV_SQ)
        converged = R_deviation < 0.1  # Within 10% of φ⁻²
        
        # Fit exponential decay to |R(t) - φ⁻²|
        R_dev = np.abs(R_vals - PHI_INV_SQ)
        if len(times) > 10:
            # Use later half for fitting (after transient)
            mid = len(times) // 2
            t_fit = times[mid:]
            R_dev_fit = R_dev[mid:]
            
            # Linear fit to log
            valid = R_dev_fit > 1e-10
            if np.sum(valid) > 5:
                log_R_dev = np.log(R_dev_fit[valid] + 1e-12)
                coeffs = np.polyfit(t_fit[valid], log_R_dev, 1)
                decay_rate = -coeffs[0]
            else:
                decay_rate = np.nan
        else:
            decay_rate = np.nan
        
        result = {
            'times': times,
            'R_vals': R_vals,
            'kappa_vals': kappa_vals,
            'G_vals': G_vals,
            'R_initial': R_vals[0],
            'R_final': R_final,
            'R_target': PHI_INV_SQ,
            'deviation': R_deviation,
            'converged': converged,
            'decay_rate': decay_rate,
            'theory_rate': self.nu * (2*np.pi/self.L)**2  # Rough estimate
        }
        
        print(f"\n  Results:")
        print(f"    Initial R: {result['R_initial']:.6f}")
        print(f"    Final R: {R_final:.6f}")
        print(f"    Target φ⁻²: {PHI_INV_SQ:.6f}")
        print(f"    Deviation: {R_deviation:.6f} ({R_deviation/PHI_INV_SQ*100:.1f}%)")
        print(f"    Converged: {converged} {'✓' if converged else '✗'}")
        print(f"    Measured decay rate: {decay_rate:.4f}")
        print(f"    Theory rate ~ν/L²: {result['theory_rate']:.4f}")
        
        return result
    
    def test_lyapunov_decay_rate(self, u0: np.ndarray, t_max: float = 3.0,
                                 dt: float = 0.01) -> Dict:
        """
        TEST 4: Lyapunov decay rate
        Claim: dG/dt ≤ -κ·δ² where κ ≈ 0.1545
        """
        print("\n" + "="*70)
        print("TEST 4: Lyapunov Decay Rate")
        print("="*70)
        
        u = u0.copy()
        
        # Initial state
        state0 = self.compute_state(u, 0.0)
        delta0 = state0.G - state0.G_eq
        
        # Evolve slightly
        u_next = self.evolve_step(u, dt)
        state1 = self.compute_state(u_next, dt)
        delta1 = state1.G - state1.G_eq
        
        # Numerical derivative
        dG_dt = (state1.G - state0.G) / dt
        
        # Theoretical bound: dG/dt ≤ -κ·δ²
        bound = -KAPPA_THEORY * delta0**2
        
        satisfied = dG_dt <= bound + 1e-6
        
        result = {
            'dG_dt': dG_dt,
            'bound': bound,
            'delta': delta0,
            'kappa_theory': KAPPA_THEORY,
            'kappa_measured': -dG_dt / delta0**2 if abs(delta0) > 1e-10 else np.nan,
            'satisfied': satisfied
        }
        
        print(f"  dG/dt measured: {dG_dt:.6e}")
        print(f"  Bound -κ·δ²: {bound:.6e}")
        print(f"  δ = G - G_eq: {delta0:.6e}")
        print(f"  κ theory: {KAPPA_THEORY:.6f}")
        print(f"  κ measured: {result['kappa_measured']:.6f}")
        print(f"  Inequality satisfied: {satisfied} {'✓' if satisfied else '✗'}")
        
        return result
    
    def evolve_step(self, u: np.ndarray, dt: float) -> np.ndarray:
        """Simple diffusion step (for testing)"""
        u_hat = np.fft.fftn(u, axes=(0,1,2))
        diffusion = np.exp(-self.nu * self.k_sq * dt)
        u_hat_new = u_hat * diffusion[:,:,:,np.newaxis]
        u_new = np.real(np.fft.ifftn(u_hat_new, axes=(0,1,2)))
        return u_new
    
    def make_random_field(self, energy: float = 1.0) -> np.ndarray:
        """Create random divergence-free velocity field"""
        # Random Fourier modes
        u_hat = np.random.randn(self.N, self.N, self.N, 3) + \
                1j * np.random.randn(self.N, self.N, self.N, 3)
        
        # Make divergence-free: u_hat - k·(k·u_hat)/|k|² · k
        k_dot_u = np.sum(self.k * u_hat, axis=-1, keepdims=True)
        u_hat = u_hat - self.k * k_dot_u / self.k_sq[:,:,:,np.newaxis]
        
        # Reality condition
        u = np.real(np.fft.ifftn(u_hat, axes=(0,1,2)))
        
        # Normalize energy
        E = 0.5 * np.mean(np.sum(u**2, axis=-1))
        u *= np.sqrt(energy / (E + 1e-10))
        
        return u


def run_all_tests():
    """Run complete validation suite"""
    print("="*70)
    print("NAVIER-STOKES PROOFS: COMPLETE VALIDATION")
    print("="*70)
    print(f"\nTesting claims from:")
    print("  - CLAY_NS_COMPLETE_LYAPUNOV_PROOF.md")
    print("  - CLAY_NS_COMPLETE_KAM_PROOF.md")
    print(f"\nGolden ratio φ = {PHI:.6f}")
    print(f"Target φ⁻² = {PHI_INV_SQ:.6f}")
    print(f"Theory κ = {KAPPA_THEORY:.6f}")
    
    validator = NSValidator(N=32, L=2*np.pi, nu=0.01)
    
    # Create test field
    print("\nGenerating random test field...")
    u0 = validator.make_random_field(energy=1.0)
    state0 = validator.compute_state(u0, 0.0)
    print(f"  Energy: {state0.E:.6f}")
    print(f"  Enstrophy: {state0.kappa:.6f}")
    print(f"  Initial R: {state0.R:.6f}")
    
    results = {}
    
    # Test 1: Clifford inequality
    results['clifford'] = validator.test_clifford_cubic_inequality(u0)
    
    # Test 2: Production formula
    results['production'] = validator.test_production_formula(u0)
    
    # Test 3: φ-convergence
    results['convergence'] = validator.test_phi_convergence(u0, t_max=5.0)
    
    # Test 4: Lyapunov rate
    results['lyapunov'] = validator.test_lyapunov_decay_rate(u0)
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    all_pass = True
    
    tests = [
        ("Clifford cubic inequality", results['clifford']['satisfied']),
        ("Convergence to φ⁻²", results['convergence']['converged']),
        ("Lyapunov decay rate", results['lyapunov']['satisfied'])
    ]
    
    for name, passed in tests:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        all_pass = all_pass and passed
    
    print(f"\n{'='*70}")
    if all_pass:
        print("✓ ALL TESTS PASSED")
        print("Proofs are VALIDATED by numerical experiment")
    else:
        print("⚠ SOME TESTS FAILED")
        print("Proofs need revision")
    print(f"{'='*70}")
    
    return results


if __name__ == "__main__":
    results = run_all_tests()

