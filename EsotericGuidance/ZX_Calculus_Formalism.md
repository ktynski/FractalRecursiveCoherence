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
