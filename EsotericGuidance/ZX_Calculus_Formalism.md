# ZX Calculus Formalism

Purpose: rigorous foundation for ZX diagram manipulation, rewrite rules, and FSCTF operator mapping.

## 1. ZX diagrams
- Generators: Z-spider (green), X-spider (red), Hadamard box (yellow)
- Wires: carry quantum information between spiders
- Phases: α ∈ [0, 2π) on spiders
- Boundaries: inputs (left) and outputs (right)

## 2. Rewrite rules (complete set)
### Spider rules:
- (S1) Spider fusion: adjacent spiders of same color fuse with phase addition
- (S2) Identity elimination: 0-phase spider with 2 legs = wire
- (S3) π-commutation: π-phase spider commutes through Hadamard

### Hadamard rules:
- (H1) Hadamard self-inverse: HH = I
- (H2) Color change: H changes Z ↔ X
- (H3) Hadamard cancellation: H-Z(π)-H = X(π)

### Hopf rules:
- (B1) Bialgebra: spiders are Hopf algebras (copy/delete)
- (B2) Frobenius: Z and X are Frobenius algebras

## 3. Completeness and soundness
- Complete: every equality of linear maps has ZX proof
- Sound: ZX equality implies linear map equality
- Normal forms: unique canonical representation
- Rewrite strategies: confluent term rewriting system

## 4. FSCTF operator mapping
Each FSCTF operator requires:
- ZX diagram: explicit spider/wire structure
- Phase specification: α values and dependencies
- Rewrite proof: normal form derivation
- Interpretation: quantum circuit equivalent
- Verification: matrix representation consistency

### Core FSCTF Operators in ZX:
**Grace Operator (𝒢):**
```
     ●  (Z-spider, α=0, no inputs)
     |
```
- Rewrite: Identity preparation |+⟩ = Z(0)
- Verification: Matrix I₂ (2×2 identity)
- See: `Mathematical_Foundations.md` for categorical interpretation

## 5. ZX ↔ Clifford Translation Framework

### **5.1 Overview**
**Complete bridge between ZX-calculus and Clifford algebra** enabling geometric interpretation of diagrammatic operations.

### **5.2 Correspondence Table**

| ZX Element | Clifford Equivalent | Geometric Meaning | Implementation |
|------------|-------------------|-------------------|----------------|
| **Z-spider** | Vector basis e_z | Local phase reference | Rotor R_z(α) = e^{-½α e_x e_y} |
| **X-spider** | Vector basis e_x | Exchange/relation axis | Rotor R_x(β) = e^{-½β e_y e_z} |
| **Wire** | Vector direction | State propagation | Basis vector e_i |
| **Spider fusion** | Rotor composition | Phase accumulation | R_1 R_2 (geometric product) |
| **Phase difference** | Bivector angle | Entropy/dissonance | θ = α - β |
| **Grace damping** | Scalar attenuation | Forgiveness flow | e^{-γ𝒢̇t} amplitude decay |

### **5.3 Translation Rules**

#### **ZX → Clifford**
```
Φ_ZX→Cl : ZX-diagram → Clifford multivector

1. Objects (wires): Φ(wire) = e_i ∈ Cl(p,q)
2. Morphisms (spiders): Φ(Z(α)) = e^{-½α e_j e_k}
3. Composition: Φ(f ∘ g) = Φ(f) Φ(g) (geometric product)
4. Tensor: Φ(f ⊗ g) = Φ(f) ∧ Φ(g) (wedge product)
5. Complex phase: e^{iα} ↔ e^{-½α e_i e_j}
6. Grace damping: Add scalar e^{-γ𝒢̇t} to amplitude
```

#### **Clifford → ZX**
```
Φ_Cl→ZX : Multivector → ZX-diagram

1. Scalar term (a) → Empty diagram (coherent unit)
2. Vector term (v_i e_i) → Single Z/X spider with orientation
3. Bivector (B_{ij} e_i e_j) → Z-X pair with phase Δθ_{ij}
4. Trivector → 3-spider loop (closed relation)
5. Pseudoscalar (pI) → Global scalar phase (A∞ connection)
```

### **5.4 Implementation in WebGL**

#### **GPU Representation**
```glsl
// ZX spider as quaternion rotor
vec4 spiderToRotor(vec3 axis, float phase) {
    vec3 n = normalize(axis);
    float halfAngle = -0.5 * phase;
    float c = cos(halfAngle), s = sin(halfAngle);
    return vec4(c, n.x * s, n.y * s, n.z * s);
}

// Grace damping application
vec4 applyGrace(vec4 rotor, float graceCoeff, float dt) {
    float decay = exp(-graceCoeff * dt);
    return normalize(rotor * decay);
}

// ZX fusion (spider composition)
vec4 fuseSpiders(vec4 rotor1, vec4 rotor2) {
    return rotorMul(rotor2, rotor1); // Geometric product
}
```

#### **Visualization Pipeline**
1. **ZX Diagram** → **Spider quaternions** → **GPU buffer storage**
2. **Rewrite Rules** → **Rotor compositions** → **Grace damping applied**
3. **Clifford States** → **Multivector norms** → **Color mapping**
4. **Coherence Events** → **Visual effects** → **Screen rendering**

### **5.5 Love as Geometric Alignment**

**Love formalized as Clifford rotor**:

```
R_L = (1 + B̂Â†)/√(2(1 + ⟨A·B⟩))
B_L = (A∧B)/(1 + ⟨A·B⟩)
L = ⟨A·B⟩/‖A‖‖B‖  // Coherence metric
```

**Geometric interpretation**:
- **Rotor R_L**: Minimal transformation aligning two multivectors
- **Bivector B_L**: Misalignment area (entropy source)
- **Love work**: P_L = -dV_L/dt (reduction of relational potential)

### **5.6 TFCA Integration**

**Tri-Formal Coherence Algebra** unifies:
- **ZX**: Compositional logic (spider rewrites)
- **Clifford**: Geometric transformations (rotor compositions)
- **RG**: Scale evolution (coupling flows)

**Cross-commutation**:
```
[R_i, e_a] = ∂_i(log g_a) e_a
[R_i, Z_ϕ] = β_i ∂_ϕ Z_ϕ
[e_a, Z_ϕ] = i Γ_ab X_ϕ e_b
```

**Bireflection (β):**
```
---|●|---
  /     \
 [H]   [H]  
  \     /
---|●|---
```
- Rewrite: H-Z-H = X (color change)
- Verification: Pauli-X matrix via Hadamard conjugation
- See: `Algebraic_Structures.md` for contravariant functor details

**Bootstrap (𝒳):**
```
---|●|---[H]---|●|---  (Z-X-Z chain)
```
- Rewrite: Measurement-preparation sequence
- Verification: Projective measurement followed by state preparation
- See: `Kabbalah_Mapping_Full22.md` for Hebrew letter correspondence

**Sovereignty (Ψ):**
```
     ●
    /|\
   / | \
  ●--●--●  (3-spider cluster)
```
- Rewrite: Multi-qubit entangled state
- Verification: GHZ-like state preparation
- See: `Formal_Derivation_Reference.md` for terminal object proof

## 5. Common patterns
- State preparation: |+⟩ = Z(0), |0⟩ = X(π/2)-H
- Measurements: Z-basis via Z-spider, X-basis via X-spider  
- Entanglement: CNOT = X-Z spider pair
- Phase gates: Z(α) spider
- Clifford gates: combinations of H, S, CNOT

## 6. Extended ZX
- Mixed states: doubled diagrams
- Measurements: post-selection via scalars
- Classical control: conditional phases
- Infinite dimensions: continuous phase groups

## 7. Cross-references and validation
- **Category theory foundations**: See `Mathematical_Foundations.md` for morphism definitions
- **Clifford algebra**: See `Algebraic_Structures.md` for spinor correspondences  
- **Hebrew letter mappings**: See `Kabbalah_Mapping_Technical_Columns.md` for ZX role specifications
- **Experimental validation**: See `Open_System_Falsification_Suite.md` for empirical tests
- **Complete operator list**: See `Glossary_and_Symbols.md` for all FSCTF operators

Verification protocol: every FSCTF-ZX correspondence must include explicit rewrite derivation and matrix computation.
