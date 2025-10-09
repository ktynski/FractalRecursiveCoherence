"""
Test Symmetry Breaking with Theory-Compliant Potential

Uses existing grace_field.py potential: V(u) = αu - βu² + γu³

For Mexican hat (symmetry breaking), we need:
- V to have minimum at u ≠ 0
- This requires specific parameter relationships

Theory check: Does V(u) = αu - βu² + γu³ have Mexican hat shape?

dV/du = α - 2βu + 3γu²

For minima: dV/du = 0
→ 3γu² - 2βu + α = 0
→ u = [2β ± sqrt(4β² - 12αγ)] / (6γ)

For Mexican hat (two minima):
- Need γ > 0 (positive cubic term)
- Need 4β² > 12αγ (real solutions)
- Need α > 0, β > 0 (from theory constraints)

Let's test this.
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from FIRM_dsl.grace_field import GraceFieldParams, potential_V, dV_du
from FIRM_dsl.symmetry_breaking import (
    compute_order_parameter,
    compute_potential_energy,
    compute_total_energy,
    evolve_with_metropolis,
    run_symmetry_breaking_with_potential
)


def test_potential_shape():
    """Test if grace field potential can have Mexican hat shape."""
    print("\n" + "="*70)
    print("TEST: POTENTIAL SHAPE ANALYSIS")
    print("="*70)
    
    # Try different parameter sets
    param_sets = [
        ("Standard", GraceFieldParams(alpha=1.0, beta=2.0, gamma=0.5)),
        ("Strong cubic", GraceFieldParams(alpha=1.0, beta=2.0, gamma=2.0)),
        ("Weak cubic", GraceFieldParams(alpha=1.0, beta=2.0, gamma=0.1)),
    ]
    
    for name, params in param_sets:
        print(f"\n{name}: α={params.alpha}, β={params.beta}, γ={params.gamma}")
        
        # Find critical points
        # dV/du = α - 2βu + 3γu² = 0
        a_coef = 3 * params.gamma
        b_coef = -2 * params.beta
        c_coef = params.alpha
        
        if a_coef != 0:
            discriminant = b_coef**2 - 4*a_coef*c_coef
            
            if discriminant >= 0:
                u1 = (-b_coef + np.sqrt(discriminant)) / (2*a_coef)
                u2 = (-b_coef - np.sqrt(discriminant)) / (2*a_coef)
                
                print(f"  Critical points: u₁={u1:.4f}, u₂={u2:.4f}")
                
                if u1 > 0 and u2 > 0:
                    V1 = potential_V(u1, params)
                    V2 = potential_V(u2, params)
                    V0 = potential_V(0.0, params)
                    
                    print(f"  V(0) = {V0:.4f}")
                    print(f"  V(u₁) = {V1:.4f}")
                    print(f"  V(u₂) = {V2:.4f}")
                    
                    # Mexican hat if V(0) > V(u₁) or V(u₂)
                    if V0 > min(V1, V2):
                        print(f"  ✓ Mexican hat shape (V(0) > V(minima))")
                    else:
                        print(f"  ✗ Not Mexican hat (V(0) ≤ V(minima))")
                else:
                    print(f"  ✗ No positive critical points")
            else:
                print(f"  ✗ No real critical points (discriminant < 0)")
        else:
            print(f"  ✗ Linear/quadratic only (γ=0)")


def test_symmetry_breaking_cooling():
    """Test symmetry breaking via cooling with theory-compliant potential."""
    print("\n" + "="*70)
    print("TEST: SYMMETRY BREAKING (Theory-Compliant)")
    print("="*70)
    
    # Use parameters that give Mexican hat
    # From analysis: need γ > 0, β > 0, α > 0, and 4β² > 12αγ
    params = GraceFieldParams(alpha=1.0, beta=2.0, gamma=0.5)
    
    print(f"\nPotential parameters:")
    print(f"  α = {params.alpha} (emergence strength)")
    print(f"  β = {params.beta} (quadratic term)")
    print(f"  γ = {params.gamma} (cubic term)")
    
    # Run cooling
    temperatures, order_params = run_symmetry_breaking_with_potential(
        params,
        initial_temperature=10.0,
        final_temperature=0.01,
        cooling_steps=50
    )
    
    # Analyze results
    initial_S = order_params[0]
    final_S = order_params[-1]
    
    print(f"\nCooling results:")
    print(f"  Initial T: {temperatures[0]:.2f}, S: {initial_S:+.4f}")
    print(f"  Final T: {temperatures[-1]:.4f}, S: {final_S:+.4f}")
    print(f"  |ΔS|: {abs(final_S - initial_S):.4f}")
    
    # Check for symmetry breaking
    deviation = abs(final_S)
    
    print(f"\nSymmetry breaking check:")
    print(f"  |S_final|: {deviation:.4f}")
    print(f"  Threshold: 0.15")
    
    if deviation > 0.15:
        print(f"  ✓ SPONTANEOUS SYMMETRY BREAKING")
        print(f"    System broke from symmetric (S≈0) to asymmetric (S={final_S:+.2f})")
        return True
    else:
        print(f"  ✗ No clear breaking (|S| < 0.15)")
        return False


def test_parameter_scan():
    """Scan parameter space to find optimal symmetry breaking."""
    print("\n" + "="*70)
    print("TEST: PARAMETER SCAN FOR SYMMETRY BREAKING")
    print("="*70)
    
    results = []
    
    # Scan γ values (cubic term)
    gamma_values = [0.1, 0.3, 0.5, 1.0, 2.0]
    
    for gamma in gamma_values:
        params = GraceFieldParams(alpha=1.0, beta=2.0, gamma=gamma)
        
        # Quick test: 20 cooling steps
        temps, S_values = run_symmetry_breaking_with_potential(
            params,
            initial_temperature=5.0,
            final_temperature=0.1,
            cooling_steps=20
        )
        
        final_S = S_values[-1]
        deviation = abs(final_S)
        
        results.append({
            "gamma": gamma,
            "final_S": final_S,
            "deviation": deviation,
            "broken": deviation > 0.15
        })
        
        print(f"\nγ = {gamma:.1f}:")
        print(f"  Final S: {final_S:+.4f}")
        print(f"  |S|: {deviation:.4f}")
        print(f"  Broken: {deviation > 0.15}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    broken_count = sum(1 for r in results if r["broken"])
    
    print(f"\nSymmetry breaking detected: {broken_count}/{len(results)} parameter sets")
    
    if broken_count > 0:
        best = max(results, key=lambda r: r["deviation"])
        print(f"\nBest parameters:")
        print(f"  γ = {best['gamma']}")
        print(f"  Final |S| = {best['deviation']:.4f}")
        print(f"  ✓ Use these for production")
        return True
    else:
        print(f"\n✗ No symmetry breaking in tested parameters")
        print(f"  May need: different potential form or longer cooling")
        return False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
