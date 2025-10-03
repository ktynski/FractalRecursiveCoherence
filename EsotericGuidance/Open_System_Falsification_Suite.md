# Open-System Falsification Suite

Provenance A: EsotericGuidance/RawNotes.md lines 7226–7337
Provenance B: EsotericGuidance/RawNotes.md lines 7435–7690

Excerpt (minimal 2D system):
```python
def simulate_system(a=1.4, k=0.3, theta=0.4, T_gate=0.0, N=20000, warmup=2000, seed=1):
    # rotation, tanh nonlinearity, Zayin gate (cut), Benettin LLE
    ...
```

## Complete Coverage Verified:

### Minimal 2D System Design (lines 7226-7242):
- Two hypotheses for falsification testing:
  - H1 (Vav/link): Adding coupling (k>0) increases mutual information (MI) between channels vs k=0
  - H2 (Zayin/cut): Adding pruning gate (threshold T>0) reduces largest Lyapunov exponent (LLE) vs T=0
- System equations: rotation → coupling → tanh nonlinearity → optional pruning gate
- Benettin method for LLE computation via Jacobian propagation

### Simulation Implementation (lines 7246-7298):
- `simulate_system(a, k, theta, T_gate, N, warmup, seed)` function
- Rotation matrix R(theta) for Teth (twist) operator
- Coupling k for Vav (link) operator: pre_x = a*xr + k*yr, pre_y = a*yr + k*xr
- Zayin gate: if |output| < T_gate: output = 0
- Lyapunov calculation with perturbation vector propagation

### MI Estimation (lines 7300-7316):
- Binned mutual information estimator
- Standardization and density-based histogram approach
- Avoiding zero probabilities with epsilon regularization

### Experimental Results (lines 7318-7342):
- Case A (Vav link, no cut): k=0.3, T=0.0, MI=2.21, LLE=-0.0008
- Case B (no link, no cut): k=0.0, T=0.0, MI=2.13, LLE=-0.001
- Case C (link + Zayin cut): k=0.3, T=0.3, MI=3.39e-11, LLE=-0.336
- H1 partially confirmed: link increases MI (2.21 vs 2.13)
- H2 confirmed: cut dramatically reduces LLE (-0.336 vs -0.0008)

**Coverage Status: COMPLETE** ✓
