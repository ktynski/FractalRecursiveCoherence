#!/usr/bin/env python3
"""
Comprehensive NS Testing: Grace vs. Devourer

Tests the CORRECT predictions from FIRM esoteric theory:
1. Stability of φ-balance (is φ⁻² a stable attractor?)
2. Basin of attraction (which initial R converge to φ⁻²?)
3. Forcing effects (does stationary turbulence reach φ⁻²?)
4. Devourer strength (how does Re affect convergence?)

NO SHORTCUTS - Real full nonlinear NS with proper initial conditions.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fftn, ifftn
from typing import Dict, List, Tuple
import time

PHI = (1 + np.sqrt(5)) / 2
PHI_INV_SQ = 1 / PHI**2  # ≈ 0.382


class FullNS3D:
    """Full 3D incompressible Navier-Stokes with spectral method."""
    
    def __init__(self, N: int = 32, L: float = 2*np.pi, nu: float = 0.01):
        self.N = N
        self.L = L
        self.nu = nu
        self.dx = L / N
        
        # Wavenumbers (with dealiasing)
        k1d = np.fft.fftfreq(N, d=1/N) * (2*np.pi/L)
        kx, ky, kz = np.meshgrid(k1d, k1d, k1d, indexing='ij')
        self.k = np.stack([kx, ky, kz], axis=-1)
        self.k_sq = np.sum(self.k**2, axis=-1)
        
        # Dealiasing (2/3 rule)
        k_max = N // 3
        self.dealias_mask = (np.abs(kx) <= k_max) & (np.abs(ky) <= k_max) & (np.abs(kz) <= k_max)
        
        print(f"Initialized NS: {N}³ grid, ν={nu}, L={L:.3f}")
        print(f"  Dealias cutoff: k_max={k_max}")
    
    def make_field_with_target_R(self, R_target: float, E0: float = 1.0, k_peak: int = 3) -> np.ndarray:
        """
        Create divergence-free field with specific target R = |ω|²/|∇u|².
        
        Strategy: 
        - Random solenoidal field has R ≈ 0.5-0.7 naturally
        - To get R < 0.5: Add more strain (compress vorticity spectrum)
        - To get R > 0.7: Add more rotation (compress strain spectrum)
        """
        N = self.N
        
        # Start with random field
        u_hat = np.zeros((N, N, N, 3), dtype=complex)
        
        # Random phases and amplitudes
        np.random.seed(int(R_target * 1000))  # Reproducible
        for i in range(3):
            phases = np.random.uniform(0, 2*np.pi, (N, N, N))
            amplitudes = np.exp(-((np.sqrt(self.k_sq) - k_peak) / 2)**2)
            u_hat[:,:,:,i] = amplitudes * np.exp(1j * phases)
        
        # Project to divergence-free
        u_hat = self.project_divergence_free(u_hat)
        
        # Adjust to target R by modifying spectral distribution
        # If R_target is low, we need more STRAIN (low-k)
        # If R_target is high, we need more VORTICITY (high-k)
        
        k_mag = np.sqrt(self.k_sq)
        k_mag[k_mag == 0] = 1  # Avoid division by zero
        
        if R_target < 0.5:
            # Want more strain → boost low k (large-scale shearing)
            weight = np.exp(-k_mag / 2)
        elif R_target > 0.7:
            # Want more vorticity → boost high k (small-scale rotation)
            weight = np.exp(-1.0 / (k_mag + 0.5))
        else:
            weight = np.ones_like(k_mag)
        
        for i in range(3):
            u_hat[:,:,:,i] *= weight
        
        u_hat = self.project_divergence_free(u_hat)
        
        # Normalize energy
        u = np.real(ifftn(u_hat, axes=(0,1,2)))
        E_current = np.mean(np.sum(u**2, axis=-1))
        u_hat *= np.sqrt(E0 / E_current)
        
        return u_hat
    
    def project_divergence_free(self, u_hat: np.ndarray) -> np.ndarray:
        """Project velocity field to divergence-free subspace."""
        k_sq = self.k_sq.copy()
        k_sq[k_sq == 0] = 1  # Avoid division by zero
        
        u_hat_proj = u_hat.copy()
        
        # Compute k·u (sum over velocity components)
        k_dot_u = np.zeros((self.N, self.N, self.N), dtype=complex)
        for j in range(3):
            k_dot_u += self.k[:,:,:,j] * u_hat[:,:,:,j]
        
        # Project: u_proj = u - k(k·u)/|k|²
        for i in range(3):
            u_hat_proj[:,:,:,i] -= self.k[:,:,:,i] * k_dot_u / k_sq
        
        # Zero out k=0 mode
        u_hat_proj[0,0,0,:] = 0
        
        return u_hat_proj
    
    def add_forcing(self, u_hat: np.ndarray, f_amplitude: float = 0.1, k_force: int = 2) -> np.ndarray:
        """Add forcing at low wavenumbers to maintain energy."""
        N = self.N
        f_hat = np.zeros_like(u_hat)
        
        k_mag = np.sqrt(self.k_sq)
        force_mask = (k_mag >= k_force - 0.5) & (k_mag <= k_force + 0.5)
        
        # Random forcing at target wavenumber
        phases = np.random.uniform(0, 2*np.pi, (N, N, N))
        for i in range(3):
            f_hat[:,:,:,i] = force_mask * f_amplitude * np.exp(1j * phases)
        
        f_hat = self.project_divergence_free(f_hat)
        return f_hat
    
    def compute_diagnostics(self, u_hat: np.ndarray) -> Dict:
        """Compute E, κ, R, etc."""
        N = self.N
        
        # Real-space velocity
        u = np.real(ifftn(u_hat, axes=(0,1,2)))
        
        # Energy
        E = 0.5 * np.mean(np.sum(u**2, axis=-1))
        
        # Vorticity ω = ∇×u
        omega_hat = np.zeros_like(u_hat)
        omega_hat[:,:,:,0] = 1j * (self.k[:,:,:,1]*u_hat[:,:,:,2] - self.k[:,:,:,2]*u_hat[:,:,:,1])
        omega_hat[:,:,:,1] = 1j * (self.k[:,:,:,2]*u_hat[:,:,:,0] - self.k[:,:,:,0]*u_hat[:,:,:,2])
        omega_hat[:,:,:,2] = 1j * (self.k[:,:,:,0]*u_hat[:,:,:,1] - self.k[:,:,:,1]*u_hat[:,:,:,0])
        
        omega = np.real(ifftn(omega_hat, axes=(0,1,2)))
        kappa = 0.5 * np.mean(np.sum(omega**2, axis=-1))
        
        # Velocity gradient squared
        grad_u_sq = 0
        for i in range(3):
            for j in range(3):
                grad_ij = np.real(ifftn(1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
                grad_u_sq += np.mean(grad_ij**2)
        
        # R ratio
        R = (2 * kappa) / grad_u_sq if grad_u_sq > 0 else np.nan
        
        # Deviation from φ⁻²
        delta_phi = abs(R - PHI_INV_SQ) / PHI_INV_SQ
        
        return {
            'E': E,
            'kappa': kappa,
            'grad_u_sq': grad_u_sq,
            'R': R,
            'delta_phi': delta_phi
        }
    
    def rhs_nonlinear(self, u_hat: np.ndarray) -> np.ndarray:
        """Compute nonlinear term (u·∇)u in Fourier space."""
        N = self.N
        
        # Transform to real space
        u = np.real(ifftn(u_hat, axes=(0,1,2)))
        
        # Compute u·∇u component by component
        convection = np.zeros_like(u)
        for i in range(3):
            for j in range(3):
                # ∂_j u_i
                du_ij = np.real(ifftn(1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
                # u_j * ∂_j u_i
                convection[:,:,:,i] += u[:,:,:,j] * du_ij
        
        # Transform back to Fourier space
        convection_hat = fftn(convection, axes=(0,1,2))
        
        # Apply dealiasing
        convection_hat *= self.dealias_mask[:,:,:,np.newaxis]
        
        return -convection_hat
    
    def step_rk4(self, u_hat: np.ndarray, dt: float, forcing: np.ndarray = None) -> np.ndarray:
        """RK4 time step for full nonlinear NS."""
        
        def dudt(u_h):
            # Nonlinear term
            nl = self.rhs_nonlinear(u_h)
            # Viscous term
            visc = -self.nu * self.k_sq[:,:,:,np.newaxis] * u_h
            # Forcing (if present)
            f = forcing if forcing is not None else 0
            # Project to divergence-free
            rhs = self.project_divergence_free(nl + visc + f)
            return rhs
        
        k1 = dudt(u_hat)
        k2 = dudt(u_hat + 0.5*dt*k1)
        k3 = dudt(u_hat + 0.5*dt*k2)
        k4 = dudt(u_hat + dt*k3)
        
        u_hat_new = u_hat + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Apply dealiasing
        u_hat_new *= self.dealias_mask[:,:,:,np.newaxis]
        
        return u_hat_new
    
    def run_simulation(
        self, 
        u0_hat: np.ndarray,
        t_max: float = 10.0,
        dt: float = 0.01,
        save_interval: int = 10,
        forcing_amplitude: float = 0.0,
        verbose: bool = True
    ) -> Dict:
        """Run full NS simulation."""
        
        u_hat = u0_hat.copy()
        times = [0]
        diagnostics = [self.compute_diagnostics(u_hat)]
        
        if verbose:
            print(f"\nRunning NS: t_max={t_max}, dt={dt}, forcing={forcing_amplitude}")
            d0 = diagnostics[0]
            print(f"  Initial: E={d0['E']:.6f}, κ={d0['kappa']:.6f}, R={d0['R']:.6f}, δ={d0['delta_phi']:.1%}")
        
        t = 0
        step = 0
        start_time = time.time()
        
        while t < t_max:
            # Forcing (if enabled)
            if forcing_amplitude > 0:
                forcing = self.add_forcing(u_hat, forcing_amplitude)
            else:
                forcing = None
            
            # Time step
            u_hat = self.step_rk4(u_hat, dt, forcing)
            
            t += dt
            step += 1
            
            # Save diagnostics
            if step % save_interval == 0:
                times.append(t)
                diag = self.compute_diagnostics(u_hat)
                diagnostics.append(diag)
                
                if verbose and step % (save_interval * 10) == 0:
                    elapsed = time.time() - start_time
                    print(f"  t={t:.2f}: E={diag['E']:.6f}, κ={diag['kappa']:.6f}, R={diag['R']:.6f}, δ={diag['delta_phi']:.1%} ({elapsed:.1f}s)")
        
        if verbose:
            elapsed = time.time() - start_time
            df = diagnostics[-1]
            print(f"  Final: E={df['E']:.6f}, κ={df['kappa']:.6f}, R={df['R']:.6f}, δ={df['delta_phi']:.1%} ({elapsed:.1f}s)")
        
        return {
            'times': np.array(times),
            'diagnostics': diagnostics,
            'u_final_hat': u_hat
        }


def test_1_stability_of_phi_balance():
    """
    TEST 1: Is φ⁻² a STABLE attractor?
    
    Initialize near φ-balance (R ≈ 0.382) with small perturbation.
    Run full nonlinear NS.
    Measure: Does R return to φ⁻²?
    
    Expected (FIRM): YES - φ⁻² is locally stable.
    """
    print("\n" + "="*80)
    print("TEST 1: STABILITY OF φ-BALANCE")
    print("="*80)
    
    solver = FullNS3D(N=32, L=2*np.pi, nu=0.01)
    
    # Try to create initial condition with R ≈ φ⁻²
    R_targets = [PHI_INV_SQ * 0.9, PHI_INV_SQ, PHI_INV_SQ * 1.1]
    
    results = []
    
    for R_target in R_targets:
        print(f"\n--- Testing R₀ = {R_target:.4f} (target φ⁻² = {PHI_INV_SQ:.4f}) ---")
        
        u0_hat = solver.make_field_with_target_R(R_target, E0=1.0)
        d0 = solver.compute_diagnostics(u0_hat)
        print(f"  Actual R₀ = {d0['R']:.4f}")
        
        result = solver.run_simulation(u0_hat, t_max=20.0, dt=0.005, save_interval=50, verbose=True)
        results.append({
            'R_target': R_target,
            'R_initial': d0['R'],
            'result': result
        })
    
    # Analyze stability
    print("\n--- STABILITY ANALYSIS ---")
    for res in results:
        R_init = res['R_initial']
        R_vals = np.array([d['R'] for d in res['result']['diagnostics']])
        R_final = R_vals[-1]
        
        # Check if converging to φ⁻²
        dist_initial = abs(R_init - PHI_INV_SQ)
        dist_final = abs(R_final - PHI_INV_SQ)
        
        converged = dist_final < dist_initial * 0.5  # At least 50% reduction
        
        print(f"R₀={R_init:.4f} → R_final={R_final:.4f}")
        print(f"  Distance from φ⁻²: {dist_initial:.4f} → {dist_final:.4f}")
        print(f"  Converging? {'YES ✓' if converged else 'NO ✗'}")
    
    return results


def test_2_basin_of_attraction():
    """
    TEST 2: How large is the basin of φ⁻² attractor?
    
    Scan initial R from 0.2 to 0.8.
    Run full NS to equilibrium.
    Measure: Which R₀ converge to φ⁻²?
    
    Expected (FIRM): Depends on ν (Grace strength).
    """
    print("\n" + "="*80)
    print("TEST 2: BASIN OF ATTRACTION")
    print("="*80)
    
    solver = FullNS3D(N=32, L=2*np.pi, nu=0.01)
    
    # Scan initial R
    R_initial_vals = np.linspace(0.2, 0.8, 7)
    
    results = []
    
    for R_init in R_initial_vals:
        print(f"\n--- Testing R₀ = {R_init:.3f} ---")
        
        u0_hat = solver.make_field_with_target_R(R_init, E0=1.0)
        d0 = solver.compute_diagnostics(u0_hat)
        
        result = solver.run_simulation(u0_hat, t_max=30.0, dt=0.005, save_interval=100, verbose=False)
        
        R_vals = np.array([d['R'] for d in result['diagnostics']])
        R_final = R_vals[-1]
        
        converged = abs(R_final - PHI_INV_SQ) < 0.05  # Within 5% of φ⁻²
        
        print(f"  Actual R₀={d0['R']:.4f} → R_final={R_final:.4f}")
        print(f"  Converged to φ⁻²? {'YES ✓' if converged else 'NO ✗'}")
        
        results.append({
            'R_target': R_init,
            'R_initial': d0['R'],
            'R_final': R_final,
            'converged': converged,
            'R_trajectory': R_vals
        })
    
    # Summary
    print("\n--- BASIN ANALYSIS ---")
    n_converged = sum(r['converged'] for r in results)
    print(f"Converged to φ⁻²: {n_converged}/{len(results)}")
    
    if n_converged > 0:
        converged_R = [r['R_initial'] for r in results if r['converged']]
        print(f"Basin range: R ∈ [{min(converged_R):.3f}, {max(converged_R):.3f}]")
    else:
        print("WARNING: No convergence observed!")
    
    return results


def test_3_forced_turbulence():
    """
    TEST 3: Does FORCED turbulence reach φ⁻²?
    
    Add energy forcing at low k.
    Run to statistical equilibrium.
    Measure: R_equilibrium ≈ φ⁻²?
    
    Expected (FIRM): YES - forcing sustains Grace attractor.
    """
    print("\n" + "="*80)
    print("TEST 3: FORCED STATIONARY TURBULENCE")
    print("="*80)
    
    solver = FullNS3D(N=32, L=2*np.pi, nu=0.01)
    
    # Start from random initial condition
    u0_hat = solver.make_field_with_target_R(0.5, E0=1.0)
    d0 = solver.compute_diagnostics(u0_hat)
    print(f"Initial: R={d0['R']:.4f}, E={d0['E']:.4f}")
    
    # Run WITH forcing
    print("\n--- WITH FORCING ---")
    result_forced = solver.run_simulation(
        u0_hat, 
        t_max=50.0, 
        dt=0.005, 
        save_interval=100,
        forcing_amplitude=0.05,
        verbose=True
    )
    
    # Run WITHOUT forcing (for comparison)
    print("\n--- WITHOUT FORCING (decay) ---")
    result_decay = solver.run_simulation(
        u0_hat.copy(), 
        t_max=50.0, 
        dt=0.005, 
        save_interval=100,
        forcing_amplitude=0.0,
        verbose=True
    )
    
    # Analysis
    print("\n--- FORCING ANALYSIS ---")
    
    R_forced = np.array([d['R'] for d in result_forced['diagnostics']])
    R_decay = np.array([d['R'] for d in result_decay['diagnostics']])
    
    # Equilibrium values (last 20% of simulation)
    R_forced_eq = np.mean(R_forced[int(0.8*len(R_forced)):])
    R_decay_eq = np.mean(R_decay[int(0.8*len(R_decay)):])
    
    print(f"Forced equilibrium: R = {R_forced_eq:.4f} (δ = {abs(R_forced_eq - PHI_INV_SQ)/PHI_INV_SQ:.1%})")
    print(f"Decay equilibrium: R = {R_decay_eq:.4f} (δ = {abs(R_decay_eq - PHI_INV_SQ)/PHI_INV_SQ:.1%})")
    print(f"Target φ⁻²: {PHI_INV_SQ:.4f}")
    
    forced_matches = abs(R_forced_eq - PHI_INV_SQ) < 0.05
    print(f"\nForced turbulence reaches φ⁻²? {'YES ✓' if forced_matches else 'NO ✗'}")
    
    return {
        'forced': result_forced,
        'decay': result_decay,
        'R_forced_eq': R_forced_eq,
        'R_decay_eq': R_decay_eq
    }


def test_4_reynolds_dependence():
    """
    TEST 4: How does Re affect convergence?
    
    Vary viscosity ν (thus Re).
    Measure basin of attraction size.
    
    Expected (FIRM): High ν (low Re) → large basin (Grace wins)
                     Low ν (high Re) → small basin (Devourer competitive)
    """
    print("\n" + "="*80)
    print("TEST 4: REYNOLDS NUMBER DEPENDENCE")
    print("="*80)
    
    nu_vals = [0.02, 0.01, 0.005]  # High to low viscosity
    
    results = []
    
    for nu in nu_vals:
        Re_approx = 1.0 / nu  # Rough estimate
        print(f"\n--- ν = {nu:.3f} (Re ~ {Re_approx:.0f}) ---")
        
        solver = FullNS3D(N=32, L=2*np.pi, nu=nu)
        
        # Test a few initial R values
        R_tests = [0.3, PHI_INV_SQ, 0.5]
        
        nu_results = []
        
        for R_init in R_tests:
            u0_hat = solver.make_field_with_target_R(R_init, E0=1.0)
            d0 = solver.compute_diagnostics(u0_hat)
            
            result = solver.run_simulation(u0_hat, t_max=20.0, dt=0.005, save_interval=100, verbose=False)
            
            R_vals = np.array([d['R'] for d in result['diagnostics']])
            R_final = R_vals[-1]
            
            converged = abs(R_final - PHI_INV_SQ) < 0.05
            
            print(f"  R₀={d0['R']:.3f} → R_final={R_final:.3f}: {'✓' if converged else '✗'}")
            
            nu_results.append({
                'R_initial': d0['R'],
                'R_final': R_final,
                'converged': converged
            })
        
        n_converged = sum(r['converged'] for r in nu_results)
        print(f"  Convergence rate: {n_converged}/{len(R_tests)}")
        
        results.append({
            'nu': nu,
            'Re': Re_approx,
            'tests': nu_results,
            'convergence_rate': n_converged / len(R_tests)
        })
    
    # Summary
    print("\n--- REYNOLDS DEPENDENCE SUMMARY ---")
    for res in results:
        print(f"ν={res['nu']:.3f} (Re~{res['Re']:.0f}): {res['convergence_rate']:.0%} convergence")
    
    return results


if __name__ == '__main__':
    print("="*80)
    print("COMPREHENSIVE NS TESTING: GRACE VS. DEVOURER")
    print("="*80)
    print(f"Target φ⁻² = {PHI_INV_SQ:.6f}")
    print()
    print("Running 4 critical tests:")
    print("  1. Stability of φ-balance (is it an attractor?)")
    print("  2. Basin of attraction (how large?)")
    print("  3. Forced turbulence (does it reach φ⁻²?)")
    print("  4. Reynolds dependence (Grace vs. Devourer strength)")
    print()
    
    # Run all tests
    test1 = test_1_stability_of_phi_balance()
    test2 = test_2_basin_of_attraction()
    test3 = test_3_forced_turbulence()
    test4 = test_4_reynolds_dependence()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    print("\nTEST 1 (Stability): ")
    print("  Check if R returns to φ⁻² after perturbation")
    
    print("\nTEST 2 (Basin): ")
    print("  Scan which initial R converge to φ⁻²")
    
    print("\nTEST 3 (Forcing): ")
    print("  Does stationary turbulence reach φ⁻²?")
    
    print("\nTEST 4 (Reynolds): ")
    print("  How does ν affect basin size?")
    
    print("\n" + "="*80)
    print("Testing complete. Analyze results to determine if Grace wins.")
    print("="*80)

