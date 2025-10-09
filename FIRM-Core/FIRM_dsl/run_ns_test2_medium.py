#!/usr/bin/env python3
"""
NS Test 2: Medium Duration (t=10.0)
Grid: 64³, ν=0.005, Taylor-Green IC

Purpose: See if R(t) begins moving toward φ⁻²
Expected runtime: ~30 minutes
"""

import numpy as np
import matplotlib.pyplot as plt
from test_full_ns_convergence import PseudospectralNS
import json
from pathlib import Path

PHI_INV_SQ = ((np.sqrt(5) - 1) / 2)**2

print('='*70)
print('NS TEST 2: MEDIUM DURATION')
print('='*70)
print(f'Target: R → φ⁻² ≈ {PHI_INV_SQ:.6f}')
print('Grid: 64³, ν=0.005, t_max=10.0')
print('IC: Taylor-Green vortex')
print('Expected runtime: ~30 minutes')
print('='*70)
print()

# Setup
solver = PseudospectralNS(N=64, L=2*np.pi, nu=0.005)
u0_hat = solver.make_taylor_green()

# Run simulation
print('Starting simulation...')
result = solver.run_simulation(u0_hat, t_max=10.0, dt=0.002, save_interval=50)

# Extract diagnostics
times = result['times']
R_vals = np.array([d['R'] for d in result['diagnostics']])
E_vals = np.array([d['E'] for d in result['diagnostics']])
kappa_vals = np.array([d['kappa'] for d in result['diagnostics']])

# Analysis
print()
print('='*70)
print('RESULTS')
print('='*70)
print(f'Initial R: {R_vals[0]:.6f}')
print(f'Final R: {R_vals[-1]:.6f}')
print(f'Target φ⁻²: {PHI_INV_SQ:.6f}')
print(f'Distance from target: {abs(R_vals[-1] - PHI_INV_SQ):.6f}')
print()

# Check trend
if len(R_vals) > 10:
    R_early = R_vals[:len(R_vals)//3].mean()
    R_late = R_vals[2*len(R_vals)//3:].mean()
    trend = "toward φ⁻²" if abs(R_late - PHI_INV_SQ) < abs(R_early - PHI_INV_SQ) else "away from φ⁻²"
    print(f'Trend: {trend}')
    print(f'  Early third: R = {R_early:.6f}')
    print(f'  Late third: R = {R_late:.6f}')
    print()

# Check convergence
converged = abs(R_vals[-1] - PHI_INV_SQ) < 0.05
print(f'Converged (within 5%): {"YES ✓" if converged else "NO ✗"}')
print()

# Energy conservation
E_error = abs(E_vals[-1] - E_vals[0]) / E_vals[0]
print(f'Energy conservation error: {E_error*100:.2f}%')
print()

# Save results
output_dir = Path('.')
output_file = output_dir / 'ns_test2_medium_results.json'

results_dict = {
    'test': 'Test 2: Medium Duration',
    'parameters': {
        'N': 64,
        'nu': 0.005,
        't_max': 10.0,
        'dt': 0.002,
        'IC': 'Taylor-Green'
    },
    'results': {
        'R_initial': float(R_vals[0]),
        'R_final': float(R_vals[-1]),
        'R_target': float(PHI_INV_SQ),
        'distance_from_target': float(abs(R_vals[-1] - PHI_INV_SQ)),
        'converged': bool(converged),
        'energy_error': float(E_error)
    },
    'timeseries': {
        'times': times.tolist(),
        'R': R_vals.tolist(),
        'E': E_vals.tolist(),
        'kappa': kappa_vals.tolist()
    }
}

with open(output_file, 'w') as f:
    json.dump(results_dict, f, indent=2)

print(f'Results saved to: {output_file}')
print()

# Plot
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# R(t) plot
axes[0].plot(times, R_vals, 'b-', linewidth=2, label='R(t)')
axes[0].axhline(PHI_INV_SQ, color='r', linestyle='--', linewidth=2, label=f'φ⁻² = {PHI_INV_SQ:.4f}')
axes[0].set_xlabel('Time')
axes[0].set_ylabel('R = |ω|²/|∇u|²')
axes[0].set_title('Vorticity-to-Strain Ratio Evolution')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Energy plot
axes[1].plot(times, E_vals, 'g-', linewidth=2, label='Energy')
axes[1].set_xlabel('Time')
axes[1].set_ylabel('E')
axes[1].set_title('Energy Evolution')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plot_file = output_dir / 'ns_test2_medium_plot.png'
plt.savefig(plot_file, dpi=150)
print(f'Plot saved to: {plot_file}')
print()

print('='*70)
print('TEST 2 COMPLETE')
print('='*70)

