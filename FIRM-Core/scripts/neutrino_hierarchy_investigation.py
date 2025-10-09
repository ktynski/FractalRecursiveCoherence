#!/usr/bin/env python3
"""
Investigation: What M_R pattern from N=21 gives correct neutrino hierarchy?

Goal: Find algebraic formula M_R(generation) that produces:
- m_ν1 < m_ν2 < m_ν3 (normal ordering)
- Δm²_21 ~ 7.5×10^-5 eV²
- Δm²_31 ~ 2.5×10^-3 eV²

Given:
- y_ν from SO(10) (comparable to charged leptons)
- m_ν = m_D² / M_R where m_D = y_ν × v
- N = 21 from Fibonacci

Strategy: Try different M_R patterns and see which matches data.
"""

import numpy as np

# Constants
N = 21
v = 246.0  # GeV
y_e = 0.000511 / v  # electron Yukawa

# Measured values
Delta_m21_sq_measured = 7.53e-5  # eV²
Delta_m31_sq_measured = 2.453e-3  # eV²

# Yukawa couplings (from SO(10))
y_nu = [
    y_e,                    # ν_e
    y_e * (10*N - 3),      # ν_μ (same as μ/e ratio)
    y_e * (2*N)            # ν_τ (intermediate)
]

# Dirac masses
m_D = [y * v for y in y_nu]  # in GeV

print("="*80)
print("NEUTRINO HIERARCHY INVESTIGATION")
print("="*80)
print(f"\nGiven: N = {N}, v = {v} GeV")
print(f"\nDirac masses (from SO(10) Yukawa):")
for i, md in enumerate(m_D, 1):
    print(f"  m_D{i} = {md:.3e} GeV = {md*1e3:.2f} MeV")

print("\n" + "-"*80)
print("TESTING M_R PATTERNS")
print("-"*80)

def test_pattern(name, M_R_list):
    """Test a specific M_R pattern."""
    print(f"\n### Pattern: {name}")
    print(f"M_R values:")
    for i, MR in enumerate(M_R_list, 1):
        print(f"  M_R{i} = {MR:.3e} GeV")
    
    # Compute neutrino masses
    m_nu = [(m_D[i]**2) / M_R_list[i] * 1e9 for i in range(3)]  # in eV
    
    print(f"\nNeutrino masses:")
    for i, m in enumerate(m_nu, 1):
        print(f"  m_ν{i} = {m:.6f} eV")
    
    # Check ordering
    ordering = "✓ Normal" if m_nu[0] < m_nu[1] < m_nu[2] else "✗ Inverted/other"
    print(f"\nOrdering: {ordering}")
    
    # Compute Δm²
    Delta_m21_sq = m_nu[1]**2 - m_nu[0]**2
    Delta_m31_sq = m_nu[2]**2 - m_nu[0]**2
    
    print(f"\nMass-squared differences:")
    print(f"  Δm²_21 = {Delta_m21_sq:.3e} eV²")
    print(f"  Measured: {Delta_m21_sq_measured:.3e} eV²")
    error_21 = abs(Delta_m21_sq - Delta_m21_sq_measured) / Delta_m21_sq_measured * 100
    print(f"  Error: {error_21:.1f}%")
    
    print(f"  Δm²_31 = {Delta_m31_sq:.3e} eV²")
    print(f"  Measured: {Delta_m31_sq_measured:.3e} eV²")
    error_31 = abs(Delta_m31_sq - Delta_m31_sq_measured) / Delta_m31_sq_measured * 100
    print(f"  Error: {error_31:.1f}%")
    
    # Overall assessment
    if ordering == "✓ Normal" and error_21 < 20 and error_31 < 20:
        print(f"\n>>> EXCELLENT! This pattern works! <<<")
        return True
    elif ordering == "✓ Normal" and error_21 < 50 and error_31 < 50:
        print(f"\n>>> GOOD! Close to data. <<<")
        return True
    else:
        print(f"\n>>> Doesn't match data. <<<")
        return False

# Pattern 1: All same (baseline)
print("\n" + "="*80)
M_R_1 = [N**5 * v] * 3
test_pattern("All same: M_R = N^5 × v", M_R_1)

# Pattern 2: Inverted power (M_R decreases with generation)
print("\n" + "="*80)
M_R_2 = [N**5 * v, N**4 * v, N**3 * v]
test_pattern("Inverted power: M_R = N^(6-gen) × v", M_R_2)

# Pattern 3: Squared inverted
print("\n" + "="*80)
M_R_3 = [N**6 * v, N**4 * v, N**2 * v]
test_pattern("Squared inverted: M_R = N^(2(4-gen)) × v", M_R_3)

# Pattern 4: Linear decrease
print("\n" + "="*80)
M_R_4 = [N**5 * v, N**5 * v / 2, N**5 * v / 5]
test_pattern("Linear decrease: M_R ~ N^5 × v / gen^2", M_R_4)

# Pattern 5: Fibonacci-like ratios
print("\n" + "="*80)
M_R_5 = [N**5 * v, N**5 * v / 1.6, N**5 * v / 2.6]
test_pattern("Fibonacci ratios: M_R ~ N^5 × v / φ^gen", M_R_5)

# Pattern 6: From charged lepton hierarchy (inverted)
# Charged: m_e : m_μ : m_τ = 1 : 207 : 3477
# Neutrino M_R should be INVERTED to compensate
print("\n" + "="*80)
M_R_6 = [N**5 * v * 3477, N**5 * v * 207, N**5 * v * 1]
test_pattern("Inverted charged hierarchy: M_R ∝ 1/m_charged", M_R_6)

# Pattern 7: Try to match data exactly (work backwards)
# Need: Δm²_21 = 7.5×10^-5, Δm²_31 = 2.5×10^-3
# Given m_D, what M_R gives this?
print("\n" + "="*80)
print("\n### Working Backwards from Data")
print("\nGoal: Δm²_21 = 7.5×10^-5 eV², Δm²_31 = 2.5×10^-3 eV²")

# Assume m1 << m2, m3, so:
# Δm²_21 ≈ m2² ⟹ m2 ≈ sqrt(7.5×10^-5) ≈ 0.0087 eV
# Δm²_31 ≈ m3² ⟹ m3 ≈ sqrt(2.5×10^-3) ≈ 0.05 eV

m2_target = np.sqrt(Delta_m21_sq_measured)  # eV
m3_target = np.sqrt(Delta_m31_sq_measured)  # eV
m1_target = 0.001  # small but nonzero

print(f"\nTarget masses:")
print(f"  m1 ~ {m1_target:.6f} eV (assumed small)")
print(f"  m2 ~ {m2_target:.6f} eV")
print(f"  m3 ~ {m3_target:.6f} eV")

# Work backwards: M_R = m_D² / m_ν
M_R_target = [
    (m_D[0]**2) / (m1_target * 1e-9),  # Convert eV to GeV
    (m_D[1]**2) / (m2_target * 1e-9),
    (m_D[2]**2) / (m3_target * 1e-9)
]

print(f"\nRequired M_R:")
for i, MR in enumerate(M_R_target, 1):
    print(f"  M_R{i} = {MR:.3e} GeV")
    
# Express in terms of N and v
print(f"\nIn terms of N^p × v:")
for i, MR in enumerate(M_R_target, 1):
    ratio = MR / v
    power = np.log(ratio) / np.log(N) if ratio > 0 else 0
    print(f"  M_R{i} = N^{power:.2f} × v")

# Test this pattern
test_pattern("Backwards from data", M_R_target)

print("\n" + "="*80)
print("INVESTIGATION COMPLETE")
print("="*80)

