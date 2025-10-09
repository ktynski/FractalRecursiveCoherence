#!/usr/bin/env python3
"""Quick critical test: Is φ⁻² stable?"""

import numpy as np
from test_grace_vs_devourer import FullNS3D, PHI_INV_SQ

print("="*60)
print("QUICK TEST: φ-BALANCE STABILITY")
print("="*60)
print(f"Target φ⁻² = {PHI_INV_SQ:.6f}")

# Small, fast setup
solver = FullNS3D(N=24, L=2*np.pi, nu=0.02)  # Smaller, higher viscosity

# Create field near φ-balance
print("\nCreating initial field with R ≈ φ⁻²...")
u0_hat = solver.make_field_with_target_R(PHI_INV_SQ, E0=1.0)
d0 = solver.compute_diagnostics(u0_hat)

print(f"Initial: R = {d0['R']:.6f}, E = {d0['E']:.6f}")
print(f"Distance from φ⁻²: {abs(d0['R'] - PHI_INV_SQ):.6f}")

# Run short simulation
print("\nRunning NS for t=5.0...")
result = solver.run_simulation(
    u0_hat, 
    t_max=5.0, 
    dt=0.01, 
    save_interval=10,
    verbose=True
)

# Check result
R_vals = np.array([d['R'] for d in result['diagnostics']])
R_final = R_vals[-1]

print("\n" + "="*60)
print("RESULT")
print("="*60)
print(f"R: {d0['R']:.6f} → {R_final:.6f}")
print(f"Distance from φ⁻²: {abs(d0['R'] - PHI_INV_SQ):.6f} → {abs(R_final - PHI_INV_SQ):.6f}")

if abs(R_final - PHI_INV_SQ) < abs(d0['R'] - PHI_INV_SQ):
    print("\n✓ R is CONVERGING toward φ⁻²!")
    print("φ-balance appears to be a stable attractor.")
else:
    print("\n✗ R is DIVERGING from φ⁻².")
    print("φ-balance may not be stable, or timescale too short.")

# Show trajectory
print("\nR trajectory:")
times = result['times']
for i in range(0, len(times), len(times)//5):
    print(f"  t={times[i]:.2f}: R={R_vals[i]:.6f}")

