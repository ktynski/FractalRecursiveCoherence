#!/usr/bin/env python3
"""
Full Navier-Stokes Solver with Pseudospectral Method

This is the CORRECT test - with full nonlinear dynamics.
Previous test used diffusion-only, which cannot show φ-convergence.

The vortex stretching term ω·(ω·∇)u is ESSENTIAL for the mechanism.
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
import time

PHI = (1 + np.sqrt(5)) / 2
PHI_INV_SQ = ((np.sqrt(5) - 1) / 2)**2  # ≈ 0.382


class PseudospectralNS:
    """Full 3D Navier-Stokes solver using pseudospectral method"""
    
    def __init__(self, N: int = 64, L: float = 2*np.pi, nu: float = 0.001):
        self.N = N
        self.L = L
        self.nu = nu
        
        # Wavenumbers
        k = 2*np.pi/L * np.fft.fftfreq(N, 1/N)
        kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
        
        self.k = np.stack([kx, ky, kz], axis=-1)
        self.k_sq = kx**2 + ky**2 + kz**2
        self.k_sq[0,0,0] = 1.0  # Avoid division by zero
        
        # Dealising mask (2/3 rule)
        k_max = np.max(np.abs(k))
        k_mag = np.sqrt(self.k_sq)
        self.dealias = (k_mag <= 2*k_max/3).astype(float)
        
        print(f"Initialized NS solver: {N}³ grid, ν={nu}, L={L}")
        print(f"  Max wavenumber: {k_max:.2f}")
        print(f"  Dealias cutoff: {2*k_max/3:.2f}")
    
    def project_divergence_free(self, u_hat: np.ndarray) -> np.ndarray:
        """Project velocity onto divergence-free subspace"""
        # u_hat = u_hat - k·(k·u_hat)/|k|² 
        k_dot_u = np.sum(self.k * u_hat, axis=-1, keepdims=True)
        u_hat_proj = u_hat - self.k * k_dot_u / self.k_sq[:,:,:,np.newaxis]
        u_hat_proj[0,0,0,:] = 0  # Zero mean
        return u_hat_proj
    
    def compute_nonlinear(self, u_hat: np.ndarray) -> np.ndarray:
        """
        Compute nonlinear term: -(u·∇)u in Fourier space
        
        Uses pseudospectral method:
        1. Transform to real space
        2. Compute products
        3. Transform back
        4. Dealias
        """
        # Transform to real space
        u = np.real(np.fft.ifftn(u_hat, axes=(0,1,2)))
        
        # Compute ∇u (all 9 components)
        grad_u = np.zeros((self.N, self.N, self.N, 3, 3), dtype=complex)
        for i in range(3):
            for j in range(3):
                grad_u[:,:,:,i,j] = np.fft.fftn(
                    np.real(np.fft.ifftn(1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2))),
                    axes=(0,1,2))
        
        # Compute (u·∇)u in real space
        u_grad_u = np.zeros((self.N, self.N, self.N, 3))
        for i in range(3):
            for j in range(3):
                grad_u_ij = np.real(np.fft.ifftn(grad_u[:,:,:,i,j], axes=(0,1,2)))
                u_grad_u[:,:,:,i] += u[:,:,:,j] * grad_u_ij
        
        # Transform back to Fourier space
        nonlinear_hat = np.fft.fftn(u_grad_u, axes=(0,1,2))
        
        # Dealias
        nonlinear_hat *= self.dealias[:,:,:,np.newaxis]
        
        return -nonlinear_hat
    
    def rhs(self, u_hat: np.ndarray) -> np.ndarray:
        """
        RHS of NS equations: du/dt = -P[(u·∇)u] + ν∇²u
        where P is projection onto divergence-free subspace
        """
        # Nonlinear term
        nonlinear = self.compute_nonlinear(u_hat)
        
        # Diffusion
        diffusion = -self.nu * self.k_sq[:,:,:,np.newaxis] * u_hat
        
        # Total RHS
        rhs = nonlinear + diffusion
        
        # Project to maintain incompressibility
        rhs_proj = self.project_divergence_free(rhs)
        
        return rhs_proj
    
    def step_rk4(self, u_hat: np.ndarray, dt: float) -> np.ndarray:
        """RK4 time step"""
        k1 = self.rhs(u_hat)
        k2 = self.rhs(u_hat + 0.5*dt*k1)
        k3 = self.rhs(u_hat + 0.5*dt*k2)
        k4 = self.rhs(u_hat + dt*k3)
        
        u_hat_new = u_hat + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Ensure divergence-free
        u_hat_new = self.project_divergence_free(u_hat_new)
        
        return u_hat_new
    
    def compute_diagnostics(self, u_hat: np.ndarray) -> Dict:
        """Compute all flow diagnostics"""
        u = np.real(np.fft.ifftn(u_hat, axes=(0,1,2)))
        
        # Energy
        E = 0.5 * np.mean(np.sum(u**2, axis=-1))
        
        # Vorticity
        omega = np.zeros_like(u)
        omega[:,:,:,0] = np.real(np.fft.ifftn(
            1j * (self.k[:,:,:,1]*u_hat[:,:,:,2] - self.k[:,:,:,2]*u_hat[:,:,:,1]),
            axes=(0,1,2)))
        omega[:,:,:,1] = np.real(np.fft.ifftn(
            1j * (self.k[:,:,:,2]*u_hat[:,:,:,0] - self.k[:,:,:,0]*u_hat[:,:,:,2]),
            axes=(0,1,2)))
        omega[:,:,:,2] = np.real(np.fft.ifftn(
            1j * (self.k[:,:,:,0]*u_hat[:,:,:,1] - self.k[:,:,:,1]*u_hat[:,:,:,0]),
            axes=(0,1,2)))
        
        # Enstrophy
        kappa = 0.5 * np.mean(np.sum(omega**2, axis=-1))
        
        # Compute |∇u|²
        grad_u_sq = 0.0
        for i in range(3):
            for j in range(3):
                grad_ij = np.real(np.fft.ifftn(
                    1j * self.k[:,:,:,j] * u_hat[:,:,:,i], axes=(0,1,2)))
                grad_u_sq += np.mean(grad_ij**2)
        
        # R ratio
        omega_sq = np.mean(np.sum(omega**2, axis=-1))
        R = omega_sq / grad_u_sq if grad_u_sq > 1e-10 else 0.0
        
        return {
            'E': E,
            'kappa': kappa,
            'R': R,
            'omega_sq': omega_sq,
            'grad_u_sq': grad_u_sq,
            'omega_max': np.max(np.sqrt(np.sum(omega**2, axis=-1)))
        }
    
    def make_taylor_green(self) -> np.ndarray:
        """Taylor-Green vortex initial condition"""
        x = np.linspace(0, self.L, self.N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        u = np.zeros((self.N, self.N, self.N, 3))
        u[:,:,:,0] =  np.sin(X) * np.cos(Y) * np.cos(Z)
        u[:,:,:,1] = -np.cos(X) * np.sin(Y) * np.cos(Z)
        u[:,:,:,2] =  0.0
        
        u_hat = np.fft.fftn(u, axes=(0,1,2))
        u_hat = self.project_divergence_free(u_hat)
        
        return u_hat
    
    def make_random_field(self, E0: float = 1.0, k_peak: int = 4) -> np.ndarray:
        """Random initial condition with energy E0"""
        # Random phases
        u_hat = (np.random.randn(self.N, self.N, self.N, 3) + 
                 1j*np.random.randn(self.N, self.N, self.N, 3))
        
        # Energy spectrum ~ k⁴ exp(-k²/k_peak²)
        k_mag = np.sqrt(self.k_sq)
        spectrum = k_mag**4 * np.exp(-k_mag**2 / k_peak**2)
        spectrum[0,0,0] = 0
        
        u_hat *= np.sqrt(spectrum[:,:,:,np.newaxis])
        
        # Make divergence-free
        u_hat = self.project_divergence_free(u_hat)
        
        # Normalize energy
        diag = self.compute_diagnostics(u_hat)
        u_hat *= np.sqrt(E0 / (diag['E'] + 1e-10))
        
        return u_hat
    
    def run_simulation(self, u0_hat: np.ndarray, t_max: float = 10.0, 
                      dt: float = 0.001, save_interval: int = 100) -> Dict:
        """Run full NS simulation"""
        print(f"\nRunning simulation: t_max={t_max}, dt={dt}")
        
        u_hat = u0_hat.copy()
        
        n_steps = int(t_max / dt)
        times = []
        diagnostics = []
        
        diag0 = self.compute_diagnostics(u_hat)
        print(f"  Initial: E={diag0['E']:.6f}, κ={diag0['kappa']:.6f}, R={diag0['R']:.6f}")
        
        start_time = time.time()
        
        for step in range(n_steps):
            t = step * dt
            
            if step % save_interval == 0:
                diag = self.compute_diagnostics(u_hat)
                times.append(t)
                diagnostics.append(diag)
                
                if step % (save_interval * 10) == 0:
                    print(f"  t={t:.3f}: E={diag['E']:.6f}, κ={diag['kappa']:.6f}, "
                          f"R={diag['R']:.6f} (target {PHI_INV_SQ:.6f})")
            
            # Check CFL condition
            if step == 0:
                u_max = diag0['omega_max'] * self.L / (2*np.pi)
                dt_cfl = 0.5 * (self.L/self.N) / u_max if u_max > 0 else dt
                if dt > dt_cfl:
                    print(f"  WARNING: dt={dt} > dt_CFL={dt_cfl:.6f}")
            
            # Time step
            u_hat = self.step_rk4(u_hat, dt)
        
        elapsed = time.time() - start_time
        print(f"  Completed in {elapsed:.1f}s ({n_steps/elapsed:.0f} steps/s)")
        
        # Final diagnostics
        diag_final = self.compute_diagnostics(u_hat)
        print(f"  Final: E={diag_final['E']:.6f}, κ={diag_final['kappa']:.6f}, "
              f"R={diag_final['R']:.6f}")
        
        return {
            'times': np.array(times),
            'diagnostics': diagnostics,
            'u_hat_final': u_hat
        }


def test_phi_convergence():
    """
    CRITICAL TEST: Does R(t) → φ⁻² with FULL nonlinear NS?
    
    This is the real test. Previous test used diffusion-only.
    """
    print("="*70)
    print("CRITICAL TEST: φ-Convergence with Full Nonlinear NS")
    print("="*70)
    print(f"\nTarget: R → φ⁻² ≈ {PHI_INV_SQ:.6f}")
    print("\nThis is the CORRECT test (with vortex stretching).")
    print("Previous test used diffusion-only, which cannot show φ-convergence.\n")
    
    # Setup
    solver = PseudospectralNS(N=64, L=2*np.pi, nu=0.005)
    
    # Initial condition: Taylor-Green vortex
    print("\n--- Test 1: Taylor-Green Vortex ---")
    u0_hat = solver.make_taylor_green()
    result_tg = solver.run_simulation(u0_hat, t_max=5.0, dt=0.001, save_interval=50)
    
    # Analyze convergence
    R_vals = np.array([d['R'] for d in result_tg['diagnostics']])
    R_final = R_vals[-10:].mean()
    deviation = abs(R_final - PHI_INV_SQ)
    
    print(f"\n  Results:")
    print(f"    Initial R: {R_vals[0]:.6f}")
    print(f"    Final R (avg last 10): {R_final:.6f}")
    print(f"    Target φ⁻²: {PHI_INV_SQ:.6f}")
    print(f"    Deviation: {deviation:.6f} ({deviation/PHI_INV_SQ*100:.1f}%)")
    print(f"    Converged: {deviation < 0.05} {'✓' if deviation < 0.05 else '✗'}")
    
    # Random initial condition
    print("\n--- Test 2: Random Turbulent Field ---")
    u0_hat = solver.make_random_field(E0=1.0, k_peak=4)
    result_rand = solver.run_simulation(u0_hat, t_max=5.0, dt=0.001, save_interval=50)
    
    R_vals_rand = np.array([d['R'] for d in result_rand['diagnostics']])
    R_final_rand = R_vals_rand[-10:].mean()
    deviation_rand = abs(R_final_rand - PHI_INV_SQ)
    
    print(f"\n  Results:")
    print(f"    Initial R: {R_vals_rand[0]:.6f}")
    print(f"    Final R (avg last 10): {R_final_rand:.6f}")
    print(f"    Target φ⁻²: {PHI_INV_SQ:.6f}")
    print(f"    Deviation: {deviation_rand:.6f} ({deviation_rand/PHI_INV_SQ*100:.1f}%)")
    print(f"    Converged: {deviation_rand < 0.05} {'✓' if deviation_rand < 0.05 else '✗'}")
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    both_converged = (deviation < 0.05) and (deviation_rand < 0.05)
    
    if both_converged:
        print("✓ BOTH TESTS PASSED: R(t) → φ⁻² with full nonlinear NS")
        print("\nCONCLUSION: Theory is CORRECT. Previous test failure was due to")
        print("using diffusion-only (missing vortex stretching term).")
        print("\nThe φ-convergence mechanism REQUIRES the nonlinear term (u·∇)u.")
    else:
        print("⚠ TESTS DID NOT FULLY CONVERGE")
        print(f"\n  Taylor-Green: {deviation:.6f} (target < 0.05)")
        print(f"  Random: {deviation_rand:.6f} (target < 0.05)")
        print("\nPossible reasons:")
        print("  - Need longer time (t_max > 5)")
        print("  - Need lower viscosity (smaller ν)")
        print("  - Mechanism only works in certain parameter regimes")
    
    print("="*70)
    
    return {
        'taylor_green': result_tg,
        'random': result_rand,
        'converged': both_converged
    }


if __name__ == "__main__":
    results = test_phi_convergence()

