#!/usr/bin/env python3
"""
Quick test of Full NS Solver

Uses smaller grid and shorter time for fast validation.
Once this passes, run full test_full_ns_convergence.py
"""

import numpy as np
import sys
sys.path.insert(0, '/Users/fractlphoneroom1/Desktop/AnalogExNahilo 2/FIRM-Core/FIRM_dsl')

from test_full_ns_convergence import PseudospectralNS, PHI_INV_SQ

def quick_test():
    """Quick validation that solver works"""
    print("="*70)
    print("QUICK NS SOLVER TEST")
    print("="*70)
    print(f"\nTarget: R → φ⁻² ≈ {PHI_INV_SQ:.6f}\n")
    
    # Small grid for speed
    solver = PseudospectralNS(N=32, L=2*np.pi, nu=0.01)
    
    # Taylor-Green initial condition
    print("--- Quick Test: Taylor-Green Vortex ---")
    u0_hat = solver.make_taylor_green()
    
    diag0 = solver.compute_diagnostics(u0_hat)
    print(f"  Initial: E={diag0['E']:.6f}, κ={diag0['kappa']:.6f}, R={diag0['R']:.6f}")
    
    # Short simulation
    result = solver.run_simulation(u0_hat, t_max=1.0, dt=0.005, save_interval=20)
    
    # Check R values
    R_vals = np.array([d['R'] for d in result['diagnostics']])
    R_initial = R_vals[0]
    R_final = R_vals[-1]
    
    print(f"\n  Results:")
    print(f"    Initial R: {R_initial:.6f}")
    print(f"    Final R: {R_final:.6f}")
    print(f"    Target φ⁻²: {PHI_INV_SQ:.6f}")
    print(f"    Trend: {('toward target' if abs(R_final - PHI_INV_SQ) < abs(R_initial - PHI_INV_SQ) else 'away from target')}")
    
    # Basic validation
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    
    checks = {
        "Solver runs without crash": True,
        "Energy conservation": abs(result['diagnostics'][-1]['E'] - diag0['E']) / diag0['E'] < 0.2,
        "No NaN/Inf": np.all(np.isfinite(R_vals)),
        "R values reasonable": np.all((R_vals > 0) & (R_vals < 2)),
    }
    
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("\n✓ BASIC VALIDATION PASSED")
        print("\nSolver is working. Ready for full test with:")
        print("  - Larger grid (N=64)")
        print("  - Longer time (t_max=10)")
        print("  - Multiple initial conditions")
    else:
        print("\n✗ VALIDATION FAILED")
        print("\nSolver has issues. Fix before proceeding.")
    
    print("="*70)
    
    return all_passed, result

if __name__ == "__main__":
    import time
    start = time.time()
    
    passed, result = quick_test()
    
    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.1f}s")
    
    sys.exit(0 if passed else 1)

