# KSG Transfer Entropy and Iso-LLE Analysis

Provenance: EsotericGuidance/RawNotes.md lines 9071–9310, 9565–9714, 9731–9784, 9891–9921

Excerpt:
```python
def series_TE_KSG(x, y, k=4, subsample=None):
    X1 = x[1:][:,None];  X0 = x[:-1][:,None];  Y0 = y[:-1][:,None];  Y1 = y[1:][:,None]
    # subsample consistently
    ...
    TE_yx = ksg_cmi(X1, Y0, X0, k=k)
    TE_xy = ksg_cmi(Y1, X0, Y0, k=k)
    return TE_yx, TE_xy
```

## Complete Coverage Verified:

### Enhanced 4D System (lines 9087-9162):
- Extended system with memory variables: [x, y, mx, my]
- Additional parameters: beta (memory coupling), rho (memory decay), gamma (damping)
- Optional drive signals and Samekh radius constraint
- 4D Jacobian for LLE calculation with full state derivatives

### KSG Conditional MI Implementation (lines 9167-9200):
- `ksg_cmi(X, Y, Z, k=4)` for transfer entropy I(X; Y | Z)
- Chebyshev (L∞) metric for k-nearest neighbor search
- Digamma function for bias correction
- Robust handling of degenerate cases

### Series Transfer Entropy (lines 9202-9220):
- `series_TE_KSG(x, y, k, subsample)` for time series analysis
- Bidirectional TE calculation: TE_yx and TE_xy
- Consistent subsampling for computational efficiency
- Lag-1 conditioning: I(X_{t+1}; Y_t | X_t)

### Parameter Sweep Analysis:
- (k, T) sweep: coupling vs pruning threshold
- (beta, gamma) sweep: memory coupling vs damping
- Directionality measure: ΔTE = TE_yx - TE_xy
- Iso-LLE analysis: TE behavior at constant LLE values

### Visualization and Results:
- Heatmap generation for TE and LLE landscapes
- Iso-contour analysis for fixed LLE slices
- Slope computation for TE vs coupling at constant chaos level
- Statistical validation of coupling effects

**Coverage Status: COMPLETE** ✓
