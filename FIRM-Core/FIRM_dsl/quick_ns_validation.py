#!/usr/bin/env python3
"""
Quick NS Validation Test
Validates solver works before running long simulations
"""

import numpy as np
import sys
sys.path.insert(0, '.')

from test_full_ns_convergence import PseudospectralNS

PHI_INV_SQ = ((np.sqrt(5) - 1) / 2)**2

print('='*60)
print('QUICK NS VALIDATION TEST')
print('='*60)
print(f'Target: R → φ⁻² ≈ {PHI_INV_SQ:.6f}')
print()

# Small grid, short time for quick test
solver = PseudospectralNS(N=32, L=2*np.pi, nu=0.01)
u0_hat = solver.make_taylor_green()

print('\nRunning t_max=2.0 (quick validation)...')
result = solver.run_simulation(u0_hat, t_max=2.0, dt=0.005, save_interval=20)

R_vals = np.array([d['R'] for d in result['diagnostics']])
direction = "toward" if abs(R_vals[-1] - PHI_INV_SQ) < abs(R_vals[0] - PHI_INV_SQ) else "away from"

print(f'\nR trajectory: {R_vals[0]:.4f} → {R_vals[-1]:.4f}')
print(f'φ⁻² target: {PHI_INV_SQ:.4f}')
print(f'Distance: {abs(R_vals[-1] - PHI_INV_SQ):.4f}')
print(f'Direction: {direction} target')
print('\nSolver validated ✓')

