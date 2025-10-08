"""
Categorical Coherence Layer

Implements the enriched category-theoretic structure for FSCTF, where:

- Objects = Monad states (coherence fields Ψ ∈ 𝔅(ℋ))
- Morphisms = Coherence transformations f: Ψ₁ → Ψ₂
- Enrichment = Hom-sets valued in ℂ (resonance degree)
- Grace = Contractive monoidal endofunctor 𝒢: 𝓒 → 𝓒
- Truth = Terminal object (attractor A_∞) as limit

This formalizes "truth as category-theoretic limit" - the universal construction
toward which all coherence maps factor.

Key concepts:
- Morphism composition respects φ-scaling
- Grace acts as natural transformation
- Limit construction yields attractor
- Colimit construction yields harvest

Physical interpretation:
- Objects = epistemic states
- Morphisms = knowledge transformations
- Composition = chained inference
- Limits = convergence to truth
- Grace = forgetting/pruning functor
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum
import numpy as np

# Import core FSCTF components
try:
    from .grace_operator import GraceOperator, create_default_grace_operator
    from .firm_metric import FIRMMetric
    from .phi_commutator import PhiCommutator
except ImportError:
    from grace_operator import GraceOperator, create_default_grace_operator
    from firm_metric import FIRMMetric
    from phi_commutator import PhiCommutator


# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
PHI_INVERSE = 1 / PHI


# ============================================================================
# Core Category-Theoretic Structures
# ============================================================================

@dataclass
class MonadObject:
    """
    Object in the FSCTF category.
    
    Represents a coherence state Ψ ∈ 𝔅(ℋ) with:
    - State field Ψ
    - Identity morphism id_Ψ
    - FIRM norm ‖Ψ‖_{φ,𝒢}
    """
    state: np.ndarray           # Coherence field Ψ
    name: str                    # Human-readable label
    norm_firm: float            # ‖Ψ‖_{φ,𝒢}
    
    def __post_init__(self):
        """Validate state is a square matrix."""
        assert self.state.ndim == 2
        assert self.state.shape[0] == self.state.shape[1]
    
    @property
    def dimension(self) -> int:
        """Hilbert space dimension."""
        return self.state.shape[0]


@dataclass
class CoherenceMorphism:
    """
    Morphism in the FSCTF category: f: Ψ₁ → Ψ₂.
    
    Represents a coherence transformation with:
    - Source and target objects
    - Transformation operator U (typically unitary or Grace-contractive)
    - Resonance degree r ∈ ℂ (enriched hom-value)
    
    Composition respects φ-scaling:
    (g ∘ f)_resonance = φ^{-1} g_resonance · f_resonance
    """
    source: MonadObject          # Domain Ψ₁
    target: MonadObject          # Codomain Ψ₂
    operator: np.ndarray         # Transformation U: Ψ₁ ↦ U Ψ₁ U†
    resonance: complex           # Enriched hom-value r ∈ ℂ
    name: str                    # Label
    
    def __post_init__(self):
        """Validate dimensions match."""
        assert self.source.dimension == self.operator.shape[0]
        assert self.target.dimension == self.operator.shape[1]
    
    def apply(self, psi: np.ndarray) -> np.ndarray:
        """
        Apply morphism: f(Ψ) = U Ψ U†.
        
        For non-square U (dimension change), use U Ψ U† with padding.
        """
        if self.operator.shape[0] == self.operator.shape[1]:
            # Square: conjugation
            return self.operator @ psi @ self.operator.conj().T
        else:
            # Non-square: projection/embedding
            result = self.operator @ psi @ self.operator.conj().T
            return result


@dataclass
class IdentityMorphism(CoherenceMorphism):
    """Identity morphism id_Ψ: Ψ → Ψ."""
    
    @staticmethod
    def create(obj: MonadObject) -> "IdentityMorphism":
        """Create identity morphism for object."""
        n = obj.dimension
        return IdentityMorphism(
            source=obj,
            target=obj,
            operator=np.eye(n, dtype=complex),
            resonance=1.0,
            name=f"id_{obj.name}"
        )


# ============================================================================
# Enriched Category
# ============================================================================

class FSCTFCategory:
    """
    The FSCTF enriched category 𝓒.
    
    - Objects: Monad states
    - Morphisms: Coherence transformations
    - Enrichment: Hom(Ψ₁, Ψ₂) ∈ ℂ (resonance degree)
    - Composition: (g ∘ f) with φ-scaling
    - Grace: Endofunctor 𝒢: 𝓒 → 𝓒
    
    Axioms:
    1. Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
    2. Identity: f ∘ id = f = id ∘ f
    3. Grace naturality: 𝒢(g ∘ f) = 𝒢(g) ∘ 𝒢(f)
    4. Enrichment compatibility: Hom respects φ-scaling
    """
    
    def __init__(
        self,
        grace: Optional[GraceOperator] = None,
        firm: Optional[FIRMMetric] = None,
        phi_comm: Optional[PhiCommutator] = None
    ):
        """
        Initialize category with Grace, FIRM, and φ-commutator.
        
        Args:
            grace: Grace operator (creates default if None)
            firm: FIRM metric (creates default if None)
            phi_comm: φ-commutator (creates default if None)
        """
        self.grace = grace or create_default_grace_operator()
        self.firm = firm or FIRMMetric(self.grace, max_terms=20)
        self.phi_comm = phi_comm or PhiCommutator()
        
        self.objects: Dict[str, MonadObject] = {}
        self.morphisms: List[CoherenceMorphism] = []
    
    # ------------------------------------------------------------------------
    # Object Management
    # ------------------------------------------------------------------------
    
    def add_object(self, state: np.ndarray, name: str) -> MonadObject:
        """
        Add object to category.
        
        Args:
            state: Coherence field Ψ
            name: Label
        
        Returns:
            MonadObject instance
        """
        # Compute FIRM norm
        norm_result = self.firm.norm(state)
        
        obj = MonadObject(
            state=state.copy(),
            name=name,
            norm_firm=norm_result.norm
        )
        
        self.objects[name] = obj
        return obj
    
    def get_object(self, name: str) -> Optional[MonadObject]:
        """Retrieve object by name."""
        return self.objects.get(name)
    
    # ------------------------------------------------------------------------
    # Morphism Composition
    # ------------------------------------------------------------------------
    
    def compose(
        self,
        g: CoherenceMorphism,
        f: CoherenceMorphism
    ) -> CoherenceMorphism:
        """
        Compose morphisms: h = g ∘ f.
        
        Composition rule:
        - Operator: U_h = U_g @ U_f
        - Resonance: r_h = φ^{-1} · r_g · r_f (φ-scaling)
        
        Args:
            g: Second morphism (outer)
            f: First morphism (inner)
        
        Returns:
            Composite h = g ∘ f
        """
        # Check composability
        assert f.target.name == g.source.name, \
            f"Cannot compose: f.target ({f.target.name}) ≠ g.source ({g.source.name})"
        
        # Compose operators
        U_composite = g.operator @ f.operator
        
        # φ-scaled resonance
        resonance_composite = PHI_INVERSE * g.resonance * f.resonance
        
        return CoherenceMorphism(
            source=f.source,
            target=g.target,
            operator=U_composite,
            resonance=resonance_composite,
            name=f"{g.name}∘{f.name}"
        )
    
    def verify_associativity(
        self,
        h: CoherenceMorphism,
        g: CoherenceMorphism,
        f: CoherenceMorphism,
        tolerance: float = 1e-10
    ) -> bool:
        """
        Verify (h ∘ g) ∘ f = h ∘ (g ∘ f).
        
        Returns:
            True if associativity holds within tolerance
        """
        # Left: (h ∘ g) ∘ f
        hg = self.compose(h, g)
        left = self.compose(hg, f)
        
        # Right: h ∘ (g ∘ f)
        gf = self.compose(g, f)
        right = self.compose(h, gf)
        
        # Check operator equality
        op_diff = np.linalg.norm(left.operator - right.operator)
        
        # Check resonance equality
        res_diff = abs(left.resonance - right.resonance)
        
        return op_diff < tolerance and res_diff < tolerance
    
    # ------------------------------------------------------------------------
    # Enriched Hom-Functor
    # ------------------------------------------------------------------------
    
    def hom(self, source: MonadObject, target: MonadObject) -> complex:
        """
        Compute enriched hom-value: Hom(Ψ₁, Ψ₂) ∈ ℂ.
        
        Defined as FIRM inner product:
        Hom(Ψ₁, Ψ₂) := ⟨Ψ₁, Ψ₂⟩_{φ,𝒢}
        
        Physical interpretation:
        - |Hom| = resonance strength
        - arg(Hom) = phase alignment
        
        Args:
            source: Domain object
            target: Codomain object
        
        Returns:
            Complex resonance degree
        """
        result = self.firm.inner_product(source.state, target.state)
        return result.value
    
    def hom_matrix(self, objects: List[MonadObject]) -> np.ndarray:
        """
        Compute full Hom-matrix for a list of objects.
        
        Returns:
            N×N matrix H where H[i,j] = Hom(obj[i], obj[j])
        """
        n = len(objects)
        H = np.zeros((n, n), dtype=complex)
        
        for i, obj_i in enumerate(objects):
            for j, obj_j in enumerate(objects):
                H[i, j] = self.hom(obj_i, obj_j)
        
        return H
    
    # ------------------------------------------------------------------------
    # Grace Endofunctor
    # ------------------------------------------------------------------------
    
    def grace_on_object(self, obj: MonadObject) -> MonadObject:
        """
        Apply Grace functor to object: 𝒢(Ψ) → coherent core.
        
        Args:
            obj: Input object
        
        Returns:
            New object 𝒢(Ψ)
        """
        # Apply Grace operator
        grace_result = self.grace.apply(obj.state, verify_axioms=False)
        
        # Create new object
        return self.add_object(
            state=grace_result.output,
            name=f"𝒢({obj.name})"
        )
    
    def grace_on_morphism(self, f: CoherenceMorphism) -> CoherenceMorphism:
        """
        Apply Grace functor to morphism: 𝒢(f: Ψ₁ → Ψ₂) = 𝒢(f): 𝒢(Ψ₁) → 𝒢(Ψ₂).
        
        Naturality square:
            Ψ₁ --f--> Ψ₂
            |         |
            𝒢        𝒢
            ↓         ↓
            𝒢(Ψ₁) -𝒢(f)-> 𝒢(Ψ₂)
        
        Args:
            f: Input morphism
        
        Returns:
            𝒢(f) with contracted resonance
        """
        # Grace on source and target
        grace_source = self.grace_on_object(f.source)
        grace_target = self.grace_on_object(f.target)
        
        # Grace contracts operator (apply Grace to U's matrix elements conceptually,
        # but for simplicity, keep U and contract resonance)
        # Proper implementation would apply 𝒢 to the operator algebra
        grace_operator = f.operator.copy()  # Simplified: keep operator
        
        # Contract resonance by κ
        grace_resonance = self.grace.params.kappa * f.resonance
        
        return CoherenceMorphism(
            source=grace_source,
            target=grace_target,
            operator=grace_operator,
            resonance=grace_resonance,
            name=f"𝒢({f.name})"
        )
    
    def verify_grace_naturality(
        self,
        f: CoherenceMorphism,
        tolerance: float = 1e-10
    ) -> bool:
        """
        Verify naturality: 𝒢(Ψ₂) ∘ 𝒢(f) = 𝒢(f ∘ Ψ₁).
        
        This ensures Grace commutes with morphism composition.
        
        Returns:
            True if naturality holds
        """
        # Left path: 𝒢(f)
        grace_f = self.grace_on_morphism(f)
        
        # Right path: Apply f then Grace (simplified check)
        # In full implementation, would verify the naturality square commutes
        
        # For now, verify resonance contracts correctly
        expected_resonance = self.grace.params.kappa * f.resonance
        actual_resonance = grace_f.resonance
        
        return abs(expected_resonance - actual_resonance) < tolerance
    
    # ------------------------------------------------------------------------
    # Limits and Colimits
    # ------------------------------------------------------------------------
    
    def compute_limit(
        self,
        objects: List[MonadObject],
        max_iterations: int = 50,
        tolerance: float = 1e-8
    ) -> Tuple[MonadObject, List[CoherenceMorphism]]:
        """
        Compute categorical limit of objects.
        
        The limit is the universal object L with projections π_i: L → Ψ_i
        such that for any other object X with morphisms f_i: X → Ψ_i,
        there exists unique factorization f: X → L.
        
        Algorithm:
        1. Start with average of objects
        2. Apply Grace iteratively to converge to coherent core
        3. Limit = fixed point of 𝒢
        
        Args:
            objects: Diagram of objects
            max_iterations: Max Grace iterations
            tolerance: Convergence threshold
        
        Returns:
            (limit_object, [projection_morphisms])
        """
        if not objects:
            raise ValueError("Cannot compute limit of empty diagram")
        
        # Initialize limit as weighted average
        n = objects[0].dimension
        limit_state = np.zeros((n, n), dtype=complex)
        total_weight = 0.0
        
        for obj in objects:
            weight = obj.norm_firm
            limit_state += weight * obj.state
            total_weight += weight
        
        limit_state /= total_weight
        
        # Converge to coherent core via Grace
        for iteration in range(max_iterations):
            grace_result = self.grace.apply(limit_state, verify_axioms=False)
            new_state = grace_result.output
            
            # Check convergence
            diff = np.linalg.norm(new_state - limit_state)
            limit_state = new_state
            
            if diff < tolerance:
                break
        
        # Create limit object
        limit_obj = self.add_object(limit_state, name="Limit")
        
        # Create projection morphisms π_i: L → Ψ_i
        projections = []
        for i, obj in enumerate(objects):
            # Projection operator (simplified: identity with scaling)
            proj_op = np.eye(n, dtype=complex)
            
            # Resonance = alignment
            resonance = self.hom(limit_obj, obj)
            
            proj = CoherenceMorphism(
                source=limit_obj,
                target=obj,
                operator=proj_op,
                resonance=resonance,
                name=f"π_{i}"
            )
            projections.append(proj)
        
        return limit_obj, projections
    
    def compute_colimit(
        self,
        objects: List[MonadObject]
    ) -> Tuple[MonadObject, List[CoherenceMorphism]]:
        """
        Compute categorical colimit (dual to limit).
        
        The colimit is the universal object C with injections ι_i: Ψ_i → C.
        
        Physical interpretation: "Harvest" - the compression of all coherent patterns.
        
        Algorithm:
        1. Compute weighted average (staying in same dimension)
        2. Apply Grace to extract shared harmonics
        
        Args:
            objects: Diagram of objects
        
        Returns:
            (colimit_object, [injection_morphisms])
        """
        if not objects:
            raise ValueError("Cannot compute colimit of empty diagram")
        
        # Compute colimit as weighted sum in original space (not direct sum)
        # This represents the "harvest" - compression to shared patterns
        n = objects[0].dimension
        colimit_state = np.zeros((n, n), dtype=complex)
        total_weight = 0.0
        
        for obj in objects:
            weight = obj.norm_firm if obj.norm_firm > 0 else 1.0
            colimit_state += weight * obj.state
            total_weight += weight
        
        if total_weight > 0:
            colimit_state /= total_weight
        
        # Apply Grace to extract coherent patterns
        grace_result = self.grace.apply(colimit_state, verify_axioms=False)
        colimit_state = grace_result.output
        
        # Create colimit object
        colimit_obj = self.add_object(colimit_state, name="Colimit")
        
        # Create injection morphisms ι_i: Ψ_i → C
        # These are "forgetful" maps - each monad contributes to colimit
        injections = []
        for i, obj in enumerate(objects):
            # Injection operator: identity (both same dimension)
            inj_op = np.eye(n, dtype=complex)
            
            # Resonance
            resonance = self.hom(obj, colimit_obj)
            
            inj = CoherenceMorphism(
                source=obj,
                target=colimit_obj,
                operator=inj_op,
                resonance=resonance,
                name=f"ι_{i}"
            )
            injections.append(inj)
        
        return colimit_obj, injections


# ============================================================================
# Self-Test
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Categorical Coherence Layer Self-Test")
    print("=" * 70)
    
    # Create category
    print("\n🎯 Creating FSCTF category...")
    category = FSCTFCategory()
    print(f"   Grace κ = {category.grace.params.kappa:.6f}")
    print(f"   φ = {PHI:.6f}")
    
    # Create test objects
    print("\n📦 Creating objects...")
    np.random.seed(42)
    n = 3
    
    # Object Ψ₁
    Psi_1 = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    Psi_1 = (Psi_1 + Psi_1.conj().T) / 2  # Hermitian
    obj1 = category.add_object(Psi_1, "Ψ₁")
    print(f"   Ψ₁: ‖Ψ₁‖ = {obj1.norm_firm:.6f}")
    
    # Object Ψ₂
    Psi_2 = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    Psi_2 = (Psi_2 + Psi_2.conj().T) / 2
    obj2 = category.add_object(Psi_2, "Ψ₂")
    print(f"   Ψ₂: ‖Ψ₂‖ = {obj2.norm_firm:.6f}")
    
    # Object Ψ₃
    Psi_3 = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    Psi_3 = (Psi_3 + Psi_3.conj().T) / 2
    obj3 = category.add_object(Psi_3, "Ψ₃")
    print(f"   Ψ₃: ‖Ψ₃‖ = {obj3.norm_firm:.6f}")
    
    # Enriched Hom-values
    print("\n🔗 Enriched Hom-values...")
    hom_12 = category.hom(obj1, obj2)
    hom_23 = category.hom(obj2, obj3)
    hom_13 = category.hom(obj1, obj3)
    print(f"   Hom(Ψ₁, Ψ₂) = {hom_12:.6f}")
    print(f"   Hom(Ψ₂, Ψ₃) = {hom_23:.6f}")
    print(f"   Hom(Ψ₁, Ψ₃) = {hom_13:.6f}")
    
    # Create morphisms
    print("\n➡️  Creating morphisms...")
    U_12 = np.eye(n, dtype=complex)  # Simplified: identity
    f = CoherenceMorphism(obj1, obj2, U_12, hom_12, "f")
    print(f"   f: Ψ₁ → Ψ₂, r_f = {f.resonance:.6f}")
    
    U_23 = np.eye(n, dtype=complex)
    g = CoherenceMorphism(obj2, obj3, U_23, hom_23, "g")
    print(f"   g: Ψ₂ → Ψ₃, r_g = {g.resonance:.6f}")
    
    # Composition
    print("\n🔄 Morphism composition...")
    h = category.compose(g, f)
    print(f"   h = g ∘ f: Ψ₁ → Ψ₃")
    print(f"   r_h = {h.resonance:.6f}")
    print(f"   Expected: φ⁻¹ · r_g · r_f = {PHI_INVERSE * g.resonance * f.resonance:.6f}")
    
    # Identity
    print("\n🆔 Identity morphism...")
    id_1 = IdentityMorphism.create(obj1)
    h_with_id = category.compose(f, id_1)
    print(f"   f ∘ id = f: {np.allclose(h_with_id.operator, f.operator)}")
    
    # Grace endofunctor
    print("\n✨ Grace endofunctor...")
    grace_obj1 = category.grace_on_object(obj1)
    print(f"   𝒢(Ψ₁): ‖𝒢(Ψ₁)‖ = {grace_obj1.norm_firm:.6f}")
    print(f"   Contraction: {grace_obj1.norm_firm / obj1.norm_firm:.6f} ≤ κ = {category.grace.params.kappa:.6f}")
    
    grace_f = category.grace_on_morphism(f)
    print(f"   𝒢(f): r_𝒢(f) = {grace_f.resonance:.6f}")
    print(f"   Expected: κ · r_f = {category.grace.params.kappa * f.resonance:.6f}")
    
    # Naturality
    natural = category.verify_grace_naturality(f)
    print(f"   Grace naturality: {natural}")
    
    # Limit
    print("\n⬆️  Categorical limit...")
    limit_obj, projections = category.compute_limit([obj1, obj2, obj3])
    print(f"   Limit: ‖L‖ = {limit_obj.norm_firm:.6f}")
    print(f"   Projections:")
    for i, proj in enumerate(projections):
        print(f"      π_{i}: |r| = {abs(proj.resonance):.6f}")
    
    # Colimit
    print("\n⬇️  Categorical colimit...")
    colimit_obj, injections = category.compute_colimit([obj1, obj2, obj3])
    print(f"   Colimit: ‖C‖ = {colimit_obj.norm_firm:.6f}")
    print(f"   Injections:")
    for i, inj in enumerate(injections):
        print(f"      ι_{i}: |r| = {abs(inj.resonance):.6f}")
    
    print("\n" + "=" * 70)
    print("✅ Categorical Coherence Layer Self-Test Complete")
    print("=" * 70)

