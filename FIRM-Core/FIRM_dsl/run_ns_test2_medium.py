#!/usr/bin/env python3
"""
NS Test 3: Large Scale (t=20.0)
Grid: 128³, ν=0.001, Taylor-Green IC

Purpose: Validate φ-convergence with sufficient resolution and duration
Expected runtime: ~2-4 hours
Memory: ~32 MB for 128³ complex arrays
"""

import numpy as np
import matplotlib.pyplot as plt
from test_full_ns_convergence import PseudospectralNS
import json
from pathlib import Path

PHI_INV_SQ = ((np.sqrt(5) - 1) / 2)**2

print('='*70)
print('NS TEST 3: LARGE SCALE VALIDATION')
print('='*70)
print(f'Target: R → φ⁻² ≈ {PHI_INV_SQ:.6f}')
print('Grid: 128³, ν=0.001, t_max=20.0')
print('IC: Taylor-Green vortex')
print('Memory: ~32 MB, Runtime: ~2-4 hours')
print('='*70)
print()

# Setup for 128³
solver = PseudospectralNS(N=128, L=2*np.pi, nu=0.001)
u0_hat = solver.make_taylor_green()

# Run longer simulation for convergence validation
print('Starting large-scale simulation...')
print('This will test φ-convergence in fully developed turbulence...')
result = solver.run_simulation(u0_hat, t_max=20.0, dt=0.001, save_interval=100)

# Extract diagnostics
times = result['times']
R_vals = np.array([d['R'] for d in result['diagnostics']])
E_vals = np.array([d['E'] for d in result['diagnostics']])
kappa_vals = np.array([d['kappa'] for d in result['diagnostics']])

# Analysis for large-scale simulation
print()
print('='*70)
print('LARGE-SCALE SIMULATION RESULTS')
print('='*70)
print(f'Initial R: {R_vals[0]:.6f}')
print(f'Final R: {R_vals[-1]:.6f}')
print(f'Target φ⁻²: {PHI_INV_SQ:.6f}')
print(f'Distance from target: {abs(R_vals[-1] - PHI_INV_SQ):.6f}')
print()

# Check trend over longer timescale
if len(R_vals) > 20:
    # Check first half vs second half
    midpoint = len(R_vals) // 2
    R_first_half = R_vals[:midpoint].mean()
    R_second_half = R_vals[midpoint:].mean()
    trend = "toward φ⁻²" if abs(R_second_half - PHI_INV_SQ) < abs(R_first_half - PHI_INV_SQ) else "away from φ⁻²"
    print(f'Long-term trend: {trend}')
    print(f'  First half: R = {R_first_half:.6f}')
    print(f'  Second half: R = {R_second_half:.6f}')
    print()

    # Check if approaching target
    approach_rate = abs(R_second_half - PHI_INV_SQ) / abs(R_first_half - PHI_INV_SQ)
    if approach_rate < 1.0:
        print(f'Approaching target (rate: {approach_rate:.3f})')
    else:
        print(f'Moving away from target (rate: {approach_rate:.3f})')
    print()

# Check convergence (tighter tolerance for large simulation)
converged = abs(R_vals[-1] - PHI_INV_SQ) < 0.02  # 2% tolerance
converged_strict = abs(R_vals[-1] - PHI_INV_SQ) < 0.01  # 1% tolerance
print(f'Converged (within 2%): {"YES ✓" if converged else "NO ✗"}')
print(f'Converged (within 1%): {"YES ✓" if converged_strict else "NO ✗"}')
print()

# Energy conservation
E_error = abs(E_vals[-1] - E_vals[0]) / E_vals[0]
print(f'Energy conservation error: {E_error*100:.2f}%')
print()

# Save results
output_dir = Path('.')
output_file = output_dir / 'ns_test3_large_scale_results.json'

results_dict = {
    'test': 'Test 3: Large Scale (128³)',
    'parameters': {
        'N': 128,
        'nu': 0.001,
        't_max': 20.0,
        'dt': 0.001,
        'IC': 'Taylor-Green',
        'memory_mb': 32,
        'expected_runtime_hours': 3
    },
    'results': {
        'R_initial': float(R_vals[0]),
        'R_final': float(R_vals[-1]),
        'R_target': float(PHI_INV_SQ),
        'distance_from_target': float(abs(R_vals[-1] - PHI_INV_SQ)),
        'converged_2percent': bool(converged),
        'converged_1percent': bool(converged_strict),
        'energy_error': float(E_error),
        'trend_approach_rate': float(approach_rate) if 'approach_rate' in locals() else None
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
plot_file = output_dir / 'ns_test3_large_scale_plot.png'
plt.savefig(plot_file, dpi=150)
print(f'Plot saved to: {plot_file}')
print()

# Additional analysis for large-scale simulation
print("LARGE-SCALE VALIDATION SUMMARY:")
print("-" * 50)

# Statistical analysis of convergence
if len(R_vals) > 50:  # Sufficient data for statistics
    R_std = np.std(R_vals[-len(R_vals)//4:])  # Last quarter
    print(f"R(t) stability (last quarter std): {R_std:.6f}")

    # Check if R is approaching target monotonically
    distances = [abs(r - PHI_INV_SQ) for r in R_vals]
    if len(distances) > 10:
        early_distances = distances[:len(distances)//3]
        late_distances = distances[2*len(distances)//3:]
        avg_early = np.mean(early_distances)
        avg_late = np.mean(late_distances)

        if avg_late < avg_early:
            print(f"✓ Converging toward target (early: {avg_early:.4f}, late: {avg_late:.4f})")
        else:
            print(f"⚠ Not converging (early: {avg_early:.4f}, late: {avg_late:.4f})")

print()

print('='*70)
print('LARGE-SCALE NS SIMULATION COMPLETE')
print('='*70)
print()
print("Next steps:")
print("- Compare with 64³ results for scaling analysis")
print("- Run additional IC (ABC flow, random) for robustness")
print("- Analyze spectral evolution for φ-signature")
print("- Prepare for publication if convergence confirmed")

