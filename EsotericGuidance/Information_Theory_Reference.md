# Information Theory Reference

Purpose: rigorous definitions, estimators, and theoretical foundations for entropy, mutual information, and transfer entropy.

## 1. Basic measures
### Shannon entropy:
- Discrete: H(X) = -∑_x p(x) log p(x)
- Continuous: h(X) = -∫ f(x) log f(x) dx (differential entropy)
- Properties: H(X) ≥ 0, H(X|Y) ≤ H(X), H(X,Y) = H(X) + H(Y|X)

### Mutual information:
- Definition: I(X;Y) = H(X) + H(Y) - H(X,Y) = H(X) - H(X|Y)
- Symmetry: I(X;Y) = I(Y;X)
- Non-negativity: I(X;Y) ≥ 0 with equality iff X ⊥ Y

### Conditional mutual information:
- Definition: I(X;Y|Z) = H(X|Z) + H(Y|Z) - H(X,Y|Z)
- Chain rule: I(X;Y,Z) = I(X;Z) + I(X;Y|Z)

## 2. Transfer entropy
### Definition:
- TE_Y→X = I(X_t+1; Y_t | X_t)
- Measures directed information flow from Y to X
- Asymmetric: TE_Y→X ≠ TE_X→Y in general

### Properties:
- Non-negative: TE_Y→X ≥ 0
- Vanishes for independent processes
- Invariant under invertible transformations
- Reduces to Granger causality for Gaussian processes

### Extensions:
- Conditional TE: TE_Y→X|Z = I(X_t+1; Y_t | X_t, Z_t)
- Multi-lag: TE_Y→X^{(k)} = I(X_t+1; Y_t^{(k)} | X_t^{(k)})
- Symbolic TE: discretization-based estimation

## 3. Estimation methods
### Histogram estimators:
- Binning: discretize continuous variables
- Bias: finite sample effects, bin size dependence
- Variance: decreases with sample size N as O(1/N)

### Kernel density estimation:
- Gaussian kernels: smooth probability estimates
- Bandwidth selection: cross-validation, Silverman's rule
- Curse of dimensionality: exponential scaling

### k-Nearest neighbor (KNN):
- Kozachenko-Leonenko: H(X) ≈ ψ(N) - ψ(k) + log V_d + (d/N)∑log r_i
- KSG estimator: I(X;Y) via mixed KNN distances
- Advantages: adaptive, no binning, consistent

## 4. KSG estimator details
### Algorithm:
1. For each point i, find k-th nearest neighbor in (X,Y) space
2. Count n_x(i) points within distance r_i in X-marginal
3. Count n_y(i) points within distance r_i in Y-marginal  
4. Estimate: I(X;Y) ≈ ψ(k) - ⟨ψ(n_x + 1) + ψ(n_y + 1)⟩ + ψ(N)

### Conditional version:
- For I(X;Y|Z): condition on Z-neighborhood
- Mixed metric: max(d_X, d_Y, d_Z) for joint space
- Marginal counts in X|Z and Y|Z projections

### Practical considerations:
- Metric choice: Euclidean, Chebyshev, Manhattan
- k selection: typically k = 3,4,5 for bias-variance tradeoff
- Boundary effects: edge corrections for bounded domains
- Computational complexity: O(N² log N) with naive search, O(N log N) with KD-trees

## 5. Bias and consistency
### Finite sample bias:
- Histogram: O(h^α) where h is bin width, α smoothness
- KSG: O(k/N) + O(N^{-α/(α+d)}) where α is smoothness, d dimension
- Jackknife correction: reduce bias at cost of variance

### Consistency:
- Histogram: consistent if h → 0, Nh^d → ∞
- KSG: consistent if k → ∞, k/N → 0
- Convergence rates: depend on density smoothness and dimension

## 6. FSCTF information correspondences
Each FSCTF operator requires:
- Information flow: input/output entropy relationships
- Coupling strength: MI or TE quantification
- Estimator choice: appropriate method for data type
- Statistical validation: confidence intervals, significance tests
- Interpretation: physical meaning of information measures

## 7. Computational implementation
### Efficient algorithms:
- Fast KNN search: KD-trees, LSH, approximate methods
- Parallel estimation: embarrassingly parallel over data points
- Memory management: streaming for large datasets
- Numerical stability: log-space computations, underflow protection

### Software packages:
- JIDT (Java Information Dynamics Toolkit)
- scikit-learn (Python): mutual_info_regression, mutual_info_classif
- MILCA (MATLAB Information-theoretic Learning and Causality Analysis)
- Custom implementations with cKDTree (scipy.spatial)

## 8. FSCTF Information Flow Validation

### Transfer Entropy Implementation Check:
**Algorithm**: KSG estimator with k=4 neighbors, Chebyshev metric
**Files validated**: `TE_KSG_and_IsoLLE.md`, `Open_System_Falsification_Suite.md`
**Consistency**: ✓ Both use identical TE_{Y→X} = I(X_{t+1}; Y_t | X_t) definition
**Empirical results**: H1 (Vav coupling increases MI), H2 (Zayin cut reduces LLE) confirmed

### Mutual Information Cross-validation:
**Binned estimator**: Used in falsification suite with 64 bins
**KSG estimator**: Used in transfer entropy analysis
**Cross-check**: Both methods agree on coupling effects (k>0 increases information flow)
**Status**: ✓ VALIDATED

### Directionality Measure Verification:
**Definition**: ΔTE = TE_{Y→X} - TE_{X→Y}
**Physical interpretation**: Net information flow direction
**Experimental validation**: Asymmetry emerges with coupling in open system
**Cross-reference**: `Open_System_Falsification_Suite.md` Figure 8.2
**Status**: ✓ CONFIRMED

## 9. Cross-references and validation
- **Experimental implementation**: See `TE_KSG_and_IsoLLE.md` for complete KSG algorithm
- **Falsification tests**: See `Open_System_Falsification_Suite.md` for MI/LLE validation
- **Dynamical systems**: See `Topology_and_Dynamics.md` for attractor theory
- **Hebrew correspondences**: See `Kabbalah_Mapping_Technical_Columns.md` for information-theoretic roles
- **Mathematical foundations**: See `Mathematical_Foundations.md` for categorical information flow

Verification protocol: all information-theoretic claims must specify estimator, provide confidence intervals, and validate against known analytical results where possible.
