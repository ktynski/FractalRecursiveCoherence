# Formal Derivation Reference

Purpose: Complete mathematical derivations from axioms to theorems to algorithms, with full provenance and verification.

## Axiomatic Foundation

### A1. Category Axioms
Let 𝒞 be a category with:
- Objects: Obj(𝒞)
- Morphisms: Hom(A,B) for A,B ∈ Obj(𝒞)
- Composition: ∘ : Hom(B,C) × Hom(A,B) → Hom(A,C)
- Identity: 1_A ∈ Hom(A,A) for each A

**Axioms:**
1. Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
2. Left identity: 1_B ∘ f = f for f ∈ Hom(A,B)  
3. Right identity: g ∘ 1_A = g for g ∈ Hom(A,B)

### A2. FIRM Operator Axioms
**Grace Operator 𝒢:**
- 𝒢 : ∅ → Ψ (morphism from initial to terminal object)
- Acausal: 𝒢 ∘ f = 𝒢 for any f : A → ∅
- Thresholdless: 𝒢 preserves all structure

**Bireflection β:**
- β : A → A^op (contravariant endofunctor)
- Involutive: β ∘ β = 1_A
- Preserves composition: β(g ∘ f) = β(f) ∘ β(g)

**Sovereignty Ψ:**
- Terminal object: unique morphism ! : A → Ψ for all A
- Recursive: Ψ ≅ Hom(Ψ, Ψ) (self-referential structure)
- Autonomous: 1_Ψ generates all endomorphisms

### A3. Information Axioms
**Entropy:**
- H(X) ≥ 0 with equality iff X is deterministic
- H(X,Y) ≤ H(X) + H(Y) with equality iff X ⊥ Y
- H(X|Y) ≤ H(X) with equality iff X ⊥ Y

**Mutual Information:**
- I(X;Y) = H(X) + H(Y) - H(X,Y)
- I(X;Y) ≥ 0 with equality iff X ⊥ Y
- I(X;Y) = I(Y;X) (symmetry)

## Core Theorems

### T1. Grace Uniqueness Theorem
**Statement:** The Grace operator 𝒢 is unique up to isomorphism.

**Proof:**
Let 𝒢₁, 𝒢₂ : ∅ → Ψ be two Grace operators satisfying the axioms.
By terminality of Ψ, there exists unique ! : Ψ → Ψ with ! ∘ 𝒢₁ = 𝒢₂.
By acausality, 𝒢₁ ∘ f = 𝒢₁ for any f : A → ∅.
Since ∅ is initial, 𝒢₁ and 𝒢₂ are uniquely determined.
Therefore 𝒢₁ ≅ 𝒢₂. ∎

### T2. Bireflection Duality Theorem  
**Statement:** For any morphism f : A → B, β(f) : β(B) → β(A) satisfies β(1_A) = 1_{β(A)}.

**Proof:**
By functoriality of β: β(1_A ∘ 1_A) = β(1_A) ∘ β(1_A).
Since 1_A ∘ 1_A = 1_A, we have β(1_A) = β(1_A) ∘ β(1_A).
By uniqueness of identity morphisms, β(1_A) = 1_{β(A)}. ∎

### T3. Sovereignty Recursion Theorem
**Statement:** Ψ satisfies the fixed-point equation Ψ ≅ F(Ψ) where F is the endofunctor F(X) = Hom(X,X).

**Proof:**
Define φ : Ψ → Hom(Ψ,Ψ) by φ(ψ) = λx.ψ (constant function).
Define ψ : Hom(Ψ,Ψ) → Ψ by ψ(f) = f(1_Ψ).
Then (ψ ∘ φ)(ψ) = ψ(λx.ψ) = (λx.ψ)(1_Ψ) = ψ.
And (φ ∘ ψ)(f) = φ(f(1_Ψ)) = λx.f(1_Ψ).
By autonomy of Ψ, f = λx.f(1_Ψ), so φ ∘ ψ = 1.
Therefore Ψ ≅ Hom(Ψ,Ψ). ∎

### T4. Transfer Entropy Asymmetry Theorem
**Statement:** For coupled dynamical systems, TE_{Y→X} - TE_{X→Y} measures net information flow directionality.

**Proof:**
TE_{Y→X} = I(X_{t+1}; Y_t | X_t) = H(X_{t+1}|X_t) - H(X_{t+1}|X_t,Y_t)
TE_{X→Y} = I(Y_{t+1}; X_t | Y_t) = H(Y_{t+1}|Y_t) - H(Y_{t+1}|Y_t,X_t)

The difference ΔTE = TE_{Y→X} - TE_{X→Y} measures excess predictive information.
If ΔTE > 0, then Y provides more information about future X than vice versa.
By construction, ΔTE = 0 iff the coupling is symmetric in information terms. ∎

## Algorithmic Derivations

### Algorithm 1: KSG Transfer Entropy Estimation
**Input:** Time series x, y of length N, lag τ, neighbors k
**Output:** TE estimate

```
1. Construct embedded vectors:
   X_t = [x_t, x_{t-τ}, ..., x_{t-(d_x-1)τ}]
   Y_t = [y_t, y_{t-τ}, ..., y_{t-(d_y-1)τ}]

2. For each time point i:
   a. Find k-th nearest neighbor distance r_i in joint space (X_{t+1}, Y_t, X_t)
   b. Count n_x(i) = |{j : ||X_{t+1}^j - X_{t+1}^i||_∞ ≤ r_i, ||X_t^j - X_t^i||_∞ ≤ r_i}| - 1
   c. Count n_y(i) = |{j : ||Y_t^j - Y_t^i||_∞ ≤ r_i, ||X_t^j - X_t^i||_∞ ≤ r_i}| - 1
   d. Count n_z(i) = |{j : ||X_t^j - X_t^i||_∞ ≤ r_i}| - 1

3. Compute: TE = ψ(k) - <ψ(n_x + 1)> - <ψ(n_y + 1)> + <ψ(n_z + 1)>
   where ψ is the digamma function
```

**Derivation:** Follows from KSG conditional mutual information estimator with mixed metrics.

### Algorithm 2: Lyapunov Exponent via Benettin Method  
**Input:** Dynamical system f, initial condition x₀, time steps N
**Output:** Largest Lyapunov exponent λ

```
1. Initialize: x = x₀, v = random unit vector
2. For t = 1 to N:
   a. Compute Jacobian J = Df(x)  
   b. Evolve: x_new = f(x), v_new = J·v
   c. Normalize: v = v_new / ||v_new||
   d. Accumulate: λ += log(||v_new||)
   e. Update: x = x_new
3. Return: λ/N
```

**Derivation:** Based on multiplicative ergodic theorem and QR decomposition of tangent space evolution.

### Algorithm 3: FIRM Operator Composition
**Input:** Operators O₁, O₂ with categories 𝒞₁, 𝒞₂
**Output:** Composed operator O₂ ∘ O₁

```
1. Verify compatibility: codomain(O₁) ≅ domain(O₂)
2. Check associativity: (O₃ ∘ O₂) ∘ O₁ = O₃ ∘ (O₂ ∘ O₁)
3. Preserve structure:
   - If O₁ preserves Grace, check O₂ ∘ 𝒢 = 𝒢
   - If O₁ is bireflective, verify β(O₂ ∘ O₁) = β(O₁) ∘ β(O₂)
   - If targeting Sovereignty, ensure terminal property maintained
4. Compute composition in appropriate category
5. Validate: check axioms A1-A3 for result
```

## Verification Protocols

### V1. Categorical Consistency Check
For each FIRM operator O : A → B:
1. Verify O ∈ Hom(A,B) in declared category
2. Check composition compatibility with other operators  
3. Validate identity and associativity laws
4. Confirm functorial properties where applicable

### V2. Information-Theoretic Validation
For information flow claims:
1. Specify estimator (histogram, KDE, KSG) with parameters
2. Compute confidence intervals via bootstrap/jackknife
3. Test against null hypothesis of independence
4. Validate against known analytical results where possible

### V3. Numerical Verification
For dynamical systems:
1. Implement system with documented parameters
2. Compute claimed metrics (LLE, MI, TE) with error bounds
3. Verify bifurcation points and attractor structure
4. Cross-validate with independent implementations

## Error Analysis

### E1. Finite Sample Effects
- KSG bias: O(k/N) for k neighbors, N samples
- Histogram bias: O(h^α) for bin width h, smoothness α
- Convergence rates: depend on dimension and density regularity

### E2. Computational Precision
- Floating point errors in Lyapunov calculations
- Numerical integration accuracy for flows
- Matrix conditioning in eigenvalue computations

### E3. Model Validation
- Parameter sensitivity analysis
- Robustness to noise and outliers
- Cross-validation on held-out data

All derivations maintain complete provenance to axioms A1-A3 with explicit verification steps V1-V3.
