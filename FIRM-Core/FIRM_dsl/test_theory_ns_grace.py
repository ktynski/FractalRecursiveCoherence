#!/usr/bin/env python3
"""
Test Theory's Actual NS Claim: NS + Grace Term

Implements the theory from newnotes.md with proper definitions:
- Grace operator: G(Ψ) = -γ(Ψ - ⟨Ψ⟩) where γ = φ⁻¹ - 1 ≈ 0.382
- Test: Does Grace prevent blow-up and accelerate enstrophy decay?
"""

import numpy as np
from scipy.fft import fftn, ifftn
import matplotlib.pyplot as plt
import time

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
PHI_INV = 1 / PHI  # ≈ 0.618
GAMMA_GRACE = PHI_INV - 1  # ≈ -0.382 (magnitude 0.382)


class NSWithGrace:
    """3D Navier-Stokes with Grace dissipation term."""
    
    def __init__(self, N=32, L=2*np.pi, nu=0.01, grace_strength=abs(GAMMA_GRACE)):
        self.N = N
        self.L = L
        self.nu = nu
        self.gamma = grace_strength
        
        # Wavenumbers
        k1d = np.fft.fftfreq(N, d=1/N) * (2*np.pi/L)
        kx, ky, kz = np.meshgrid(k1d, k1d, k1d, indexing='ij')
        self.k = np.stack([kx, ky, kz], axis=-1)
        self.k_sq = np.sum(self.k**2, axis=-1)
        
        # Dealiasing
        k_max = N // 3
        self.dealias = (np.abs(kx) <= k_max) & (np.abs(ky) <= k_max) & (np.abs(kz) <= k_max)
        
        print(f"NS + Grace: N={N}, ν={nu}, γ={self.gamma:.4f} (φ⁻¹−1)")
    
    def grace_operator(self, u_hat):
        """
        Grace dissipation: G(u) = -γ(u - ⟨u⟩)
        
        In Fourier space:
        - For k=0: G = 0 (don't affect mean)
        - For k≠0: G = -γ·u_k (drive fluctuations to zero)
        """
        grace_hat = -self.gamma * u_hat.copy()
        grace_hat[0,0,0,:] = 0  # Preserve mean flow
        return grace_hat
    
    def project_divergence_free(self, u_hat):
        """Project to divergence-free subspace."""
        k_sq = self.k_sq.copy()
        k_sq[k_sq == 0] = 1
        
        u_hat_proj = u_hat.copy()
        
        # k·u
        k_dot_u = np.zeros((self.N, self.N, self.N), dtype=complex)
        for j in range(3):
            k_dot_u += self.k[:,:,:,j] * u_hat[:,:,:,j]
        
        # u - k(k·u)/|k|²
        for i in range(3):
            u_hat_proj[:,:,:,i] -= self.k[:,:,:,i] * k_dot_u / k_sq
        
        u_hat_proj[0,0,0,:] = 0
        return u_hat_proj
    
    def rhs_nonlinear(self, u_hat):
        """Nonlinear term (u·∇)u."""
        u = np.real(ifftn(u_hat, axes=(0,1,2)))
        
        convection = np.zeros_like(u)
        for i in range(3):
            for j in range(3):
                du_ij = np.real(ifftn(1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
                convection[:,:,:,i] += u[:,:,:,j] * du_ij
        
        conv_hat = fftn(convection, axes=(0,1,2))
        conv_hat *= self.dealias[:,:,:,np.newaxis]
        
        return -conv_hat
    
    def step_rk4(self, u_hat, dt, use_grace=True):
        """RK4 step with optional Grace term."""
        
        def dudt(u_h):
            # Nonlinear
            nl = self.rhs_nonlinear(u_h)
            # Viscous
            visc = -self.nu * self.k_sq[:,:,:,np.newaxis] * u_h
            # Grace (optional)
            grace = self.grace_operator(u_h) if use_grace else 0
            # Project
            rhs = self.project_divergence_free(nl + visc + grace)
            return rhs
        
        k1 = dudt(u_hat)
        k2 = dudt(u_hat + 0.5*dt*k1)
        k3 = dudt(u_hat + 0.5*dt*k2)
        k4 = dudt(u_hat + dt*k3)
        
        u_hat_new = u_hat + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        u_hat_new *= self.dealias[:,:,:,np.newaxis]
        
        return u_hat_new
    
    def compute_diagnostics(self, u_hat):
        """Compute energy, enstrophy, etc."""
        u = np.real(ifftn(u_hat, axes=(0,1,2)))
        
        # Energy
        E = 0.5 * np.mean(np.sum(u**2, axis=-1))
        
        # Vorticity
        omega_hat = np.zeros_like(u_hat)
        omega_hat[:,:,:,0] = 1j * (self.k[:,:,:,1]*u_hat[:,:,:,2] - self.k[:,:,:,2]*u_hat[:,:,:,1])
        omega_hat[:,:,:,1] = 1j * (self.k[:,:,:,2]*u_hat[:,:,:,0] - self.k[:,:,:,0]*u_hat[:,:,:,2])
        omega_hat[:,:,:,2] = 1j * (self.k[:,:,:,0]*u_hat[:,:,:,1] - self.k[:,:,:,1]*u_hat[:,:,:,0])
        
        omega = np.real(ifftn(omega_hat, axes=(0,1,2)))
        kappa = 0.5 * np.mean(np.sum(omega**2, axis=-1))
        
        # φ-weighted enstrophy
        kappa_phi = kappa / PHI
        
        return {'E': E, 'kappa': kappa, 'kappa_phi': kappa_phi}
    
    def run_simulation(self, u0_hat, t_max=10, dt=0.01, use_grace=True, verbose=True):
        """Run NS with/without Grace."""
        u_hat = u0_hat.copy()
        times = [0]
        diagnostics = [self.compute_diagnostics(u_hat)]
        
        if verbose:
            grace_str = "WITH Grace" if use_grace else "WITHOUT Grace"
            print(f"\nRunning NS {grace_str}: t_max={t_max}, dt={dt}")
            print(f"  Initial: E={diagnostics[0]['E']:.6f}, κ={diagnostics[0]['kappa']:.6f}")
        
        t = 0
        step = 0
        start_time = time.time()
        
        while t < t_max:
            u_hat = self.step_rk4(u_hat, dt, use_grace)
            t += dt
            step += 1
            
            if step % 10 == 0:
                times.append(t)
                diag = self.compute_diagnostics(u_hat)
                diagnostics.append(diag)
                
                if verbose and step % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"  t={t:.2f}: E={diag['E']:.6f}, κ={diag['kappa']:.6f} ({elapsed:.1f}s)")
        
        if verbose:
            elapsed = time.time() - start_time
            df = diagnostics[-1]
            print(f"  Final: E={df['E']:.6f}, κ={df['kappa']:.6f} ({elapsed:.1f}s)")
        
        return {'times': np.array(times), 'diagnostics': diagnostics}


def make_random_field(N, L, E0=1.0, k_peak=3):
    """Create random divergence-free field."""
    k1d = np.fft.fftfreq(N, d=1/N) * (2*np.pi/L)
    kx, ky, kz = np.meshgrid(k1d, k1d, k1d, indexing='ij')
    k = np.stack([kx, ky, kz], axis=-1)
    k_sq = np.sum(k**2, axis=-1)
    k_mag = np.sqrt(k_sq)
    
    # Random field
    u_hat = np.zeros((N, N, N, 3), dtype=complex)
    phases = np.random.uniform(0, 2*np.pi, (N, N, N))
    amplitudes = np.exp(-((k_mag - k_peak) / 2)**2)
    
    for i in range(3):
        u_hat[:,:,:,i] = amplitudes * np.exp(1j * phases)
    
    # Project divergence-free
    k_sq_safe = k_sq.copy()
    k_sq_safe[k_sq_safe == 0] = 1
    
    k_dot_u = np.zeros((N, N, N), dtype=complex)
    for j in range(3):
        k_dot_u += k[:,:,:,j] * u_hat[:,:,:,j]
    
    for i in range(3):
        u_hat[:,:,:,i] -= k[:,:,:,i] * k_dot_u / k_sq_safe
    
    u_hat[0,0,0,:] = 0
    
    # Normalize energy
    u = np.real(ifftn(u_hat, axes=(0,1,2)))
    E_current = np.mean(np.sum(u**2, axis=-1))
    u_hat *= np.sqrt(E0 / E_current)
    
    return u_hat


def test_1_grace_dissipation_rate():
    """
    TEST 1: Does Grace accelerate enstrophy decay?
    
    Theory predicts: With Grace, κ decays with additional rate γ ≈ 0.382
    """
    print("="*80)
    print("TEST 1: GRACE DISSIPATION RATE")
    print("="*80)
    
    solver = NSWithGrace(N=24, L=2*np.pi, nu=0.02)
    u0 = make_random_field(24, 2*np.pi, E0=1.0)
    
    # Without Grace
    print("\n--- Standard NS (no Grace) ---")
    result_no_grace = solver.run_simulation(u0, t_max=5, dt=0.01, use_grace=False)
    
    # With Grace
    print("\n--- NS + Grace ---")
    result_with_grace = solver.run_simulation(u0, t_max=5, dt=0.01, use_grace=True)
    
    # Extract enstrophy
    kappa_no = np.array([d['kappa'] for d in result_no_grace['diagnostics']])
    kappa_yes = np.array([d['kappa'] for d in result_with_grace['diagnostics']])
    times = result_no_grace['times']
    
    # Fit exponential decay: κ(t) = κ₀·exp(-λt)
    def fit_exp_decay(kappa, times):
        log_kappa = np.log(kappa + 1e-10)
        slope = (log_kappa[-1] - log_kappa[0]) / (times[-1] - times[0])
        return -slope
    
    rate_no = fit_exp_decay(kappa_no, times)
    rate_yes = fit_exp_decay(kappa_yes, times)
    
    print("\n--- RESULTS ---")
    print(f"Decay rate WITHOUT Grace: λ = {rate_no:.4f}")
    print(f"Decay rate WITH Grace: λ = {rate_yes:.4f}")
    print(f"Difference: Δλ = {rate_yes - rate_no:.4f}")
    print(f"Theoretical (γ = φ⁻¹−1): {abs(GAMMA_GRACE):.4f}")
    print(f"Match: {'YES ✓' if np.isclose(rate_yes - rate_no, abs(GAMMA_GRACE), rtol=0.3) else 'NO ✗'}")
    
    return result_no_grace, result_with_grace


def test_2_high_reynolds_stability():
    """
    TEST 2: Does Grace prevent instability at high Re?
    
    Theory predicts: Grace term stabilizes even when ν is very small
    """
    print("\n" + "="*80)
    print("TEST 2: HIGH REYNOLDS NUMBER STABILITY")
    print("="*80)
    
    # Very low viscosity (high Re)
    solver_low_nu = NSWithGrace(N=24, L=2*np.pi, nu=0.002, grace_strength=abs(GAMMA_GRACE))
    
    # High energy initial condition
    u0 = make_random_field(24, 2*np.pi, E0=5.0)
    d0 = solver_low_nu.compute_diagnostics(u0)
    
    print(f"\nInitial: E={d0['E']:.3f}, κ={d0['kappa']:.3f}")
    print(f"Reynolds number ~ {d0['E']**0.5 * 2*np.pi / 0.002:.0f}")
    
    # Run WITH Grace
    print("\n--- WITH Grace (should stay smooth) ---")
    result_grace = solver_low_nu.run_simulation(u0, t_max=3, dt=0.005, use_grace=True)
    
    kappa_vals = np.array([d['kappa'] for d in result_grace['diagnostics']])
    max_kappa = np.max(kappa_vals)
    final_kappa = kappa_vals[-1]
    
    print(f"\nMax enstrophy: {max_kappa:.3f}")
    print(f"Final enstrophy: {final_kappa:.3f}")
    print(f"Remained bounded: {'YES ✓' if max_kappa < d0['kappa'] * 2 else 'NO ✗ (grew too much)'}")
    
    return result_grace


def test_3_grace_strength_scan():
    """
    TEST 3: Is γ = φ⁻¹−1 optimal?
    
    Scan different Grace strengths and see if φ-value is special
    """
    print("\n" + "="*80)
    print("TEST 3: OPTIMAL GRACE STRENGTH")
    print("="*80)
    
    u0 = make_random_field(24, 2*np.pi, E0=1.0)
    
    gamma_vals = [0.1, 0.2, abs(GAMMA_GRACE), 0.5, 0.8]
    
    print(f"\nTesting different γ values (φ-predicted: {abs(GAMMA_GRACE):.4f})")
    
    results = []
    for gamma in gamma_vals:
        solver = NSWithGrace(N=24, L=2*np.pi, nu=0.02, grace_strength=gamma)
        result = solver.run_simulation(u0, t_max=3, dt=0.01, use_grace=True, verbose=False)
        
        kappa_vals = np.array([d['kappa'] for d in result['diagnostics']])
        final_kappa = kappa_vals[-1]
        
        print(f"  γ={gamma:.4f}: final κ={final_kappa:.6f}")
        results.append((gamma, final_kappa))
    
    # Check if φ-value gives lowest enstrophy
    gammas, finals = zip(*results)
    min_idx = np.argmin(finals)
    
    print(f"\nOptimal γ: {gammas[min_idx]:.4f}")
    print(f"φ-predicted: {abs(GAMMA_GRACE):.4f}")
    print(f"Match: {'YES ✓' if np.isclose(gammas[min_idx], abs(GAMMA_GRACE), rtol=0.2) else 'NO ✗'}")
    
    return results


if __name__ == '__main__':
    print("="*80)
    print("TESTING THEORY'S ACTUAL NS CLAIM")
    print("="*80)
    print(f"φ = {PHI:.6f}")
    print(f"φ⁻¹ = {PHI_INV:.6f}")
    print(f"γ = φ⁻¹−1 = {GAMMA_GRACE:.6f} (magnitude: {abs(GAMMA_GRACE):.6f})")
    print()
    print("Theory: Adding Grace term G(Ψ) = -γ(Ψ−⟨Ψ⟩) prevents blow-up")
    print()
    
    # Run tests
    np.random.seed(42)
    
    test_1_grace_dissipation_rate()
    test_2_high_reynolds_stability()
    test_3_grace_strength_scan()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

