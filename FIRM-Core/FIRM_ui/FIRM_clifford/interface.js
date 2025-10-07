import { validate_object_g } from '../FIRM_dsl/core.js';
import { detectSovereignTriads, computePolarityOrientation, computeSovereigntyIndex } from '../sovereignty_detector.js';

export class MultivectorField {
  constructor(payload) {
    this.payload = payload;
    // Freeze the payload structure but allow mutation of components array for evolution
    if (this.payload && this.payload.components) {
      // Freeze payload properties except components array
      const { components, ...otherProps } = this.payload;
      Object.freeze(otherProps);
      // Keep components mutable for evolution updates
      this.payload.components = [...components]; // Ensure it's a proper array
    }
    Object.freeze(this);
  }

  // Method to safely update components for evolution
  updateComponents(newComponents) {
    if (this.payload && Array.isArray(newComponents) && newComponents.length === 16) {
      this.payload.components = [...newComponents]; // Create new array to ensure mutability
    }
  }

  /**
   * FSCTF-Native Coherent Tensor Product (⊗)
   * 
   * Combines two Clifford field states using Grace-mediated linear superposition.
   * 
   * Theory:
   * - Preserves Clifford algebra linear structure (addition is valid operation)
   * - Grace (𝒢) acts as identity element and coherence mediator
   * - Monoidal tensor reduces to weighted sum due to SGC coherence guarantees
   * 
   * Mathematical Basis:
   * From EsotericGuidance/Mathematical_Foundations.md:
   *   "When combining operators, model via ⊗ or categorical products/sums"
   * 
   * From EsotericGuidance/Algebraic_Structures.md:
   *   "Grace Operator (𝒢): Grade-0 scalar (1) - Identity element in Cl(ℝ³)"
   * 
   * Implementation:
   * (f ⊗ g) ≅ 𝒢 ∘ (f + g) in coherence-guaranteed morphism space
   * 
   * @param {MultivectorField} otherField - Field to combine with
   * @param {number} graceWeight - Grace magnitude for coherence mediation (typically graceMagnitude)
   * @returns {MultivectorField} Combined field with coherent superposition
   */
  coherentTensor(otherField, graceWeight = 1.618033988749) {
    if (!otherField || !otherField.payload || !otherField.payload.components) {
      return this;
    }
    
    if (otherField.payload.components.length !== 16) {
      console.warn('⚠️ Coherent tensor requires 16-component fields');
      return this;
    }
    
    // Grace-mediated weighted combination
    // Grace acts as coherence normalizer: higher grace → more contribution from evolution
    // Theory: 𝒢 ensures closure and coherence preservation
    const graceNormalized = Math.max(0.1, Math.min(10.0, graceWeight));
    const evolutionWeight = graceNormalized / (graceNormalized + 1.0); // Maps φ≈1.618 → ~0.618
    const baseWeight = 1.0 / (graceNormalized + 1.0);                  // Maps φ≈1.618 → ~0.382
    
    // Linear superposition (monoidal tensor in coherence-guaranteed space)
    const combined = new Array(16);
    for (let i = 0; i < 16; i++) {
      // Coherent superposition: both sources contribute proportionally
      // This preserves Clifford algebra linearity and phase relationships
      combined[i] = this.payload.components[i] * evolutionWeight + 
                    otherField.payload.components[i] * baseWeight;
    }
    
    console.log(`⊗ Coherent tensor: evolution=${evolutionWeight.toFixed(3)}, base=${baseWeight.toFixed(3)}, grace=${graceNormalized.toFixed(3)}`);
    
    return new MultivectorField({ components: combined, algebra: this.payload.algebra || 'Cl(1,3)' });
  }
}

export function phi_zx_to_clifford(graph, rewriteHistory = []) {
  validate_object_g(graph);
  const components = new Array(16).fill(0);

  // THEORY: mapping.py line 5-8
  // "Φ maps Z-spiders to scalar rotors, X-spiders to phase bivectors,
  //  Connection is built from rotor phase deltas; curvature via bivector commutator."
  
  // Build adjacency for connectivity analysis
  const adjacency = new Map();
  for (const nodeId of graph.nodes) {
    adjacency.set(nodeId, []);
  }
  for (const [u, v] of graph.edges) {
    adjacency.get(u).push(v);
    adjacency.get(v).push(u);
  }

  // GRADE-0 & GRADE-2: Z-spiders → scalar rotors, X-spiders → phase bivectors
  for (const [nodeId, label] of Object.entries(graph.labels)) {
    const phaseRad = Math.PI * label.phase_numer / label.phase_denom;
    const degree = adjacency.get(Number(nodeId))?.length || 0;
    const weight = Math.sqrt(1 + degree);

    if (label.kind === 'Z') {
      // Z-spider → scalar rotor: Rotor = cos(θ/2) + sin(θ/2) * bivector
      const scalarPart = weight * Math.cos(phaseRad / 2);
      const bivectorPart = weight * Math.sin(phaseRad / 2);
      components[0] += scalarPart;      // Scalar
      components[5] += bivectorPart;    // e₀₁ bivector
    } else if (label.kind === 'X') {
      // X-spider → phase bivector in e₁₂ plane
      const biv12 = weight * Math.cos(phaseRad);
      const biv13 = weight * Math.sin(phaseRad);
      components[6] += biv12;           // e₁₂ bivector
      components[7] += biv13;           // e₁₃ bivector
    }
  }
  
  // GRADE-1: Vector components from gauge connection
  // Theory: clifford_visualization_physics_interpretation.md lines 646-650
  // "Z-spider with high connectivity → vector components"
  // "Edge structure → momentum flow direction"
  // mapping.py line 8: "Connection is built from rotor phase deltas"
  for (const [u, v] of graph.edges) {
    const labelU = graph.labels[u];
    const labelV = graph.labels[v];
    if (!labelU || !labelV) continue;
    
    // Compute phase difference along edge (gauge connection)
    const phaseU = Math.PI * labelU.phase_numer / labelU.phase_denom;
    const phaseV = Math.PI * labelV.phase_numer / labelV.phase_denom;
    const phaseDelta = phaseV - phaseU;
    
    // Connection strength from connectivity
    const degU = adjacency.get(u)?.length || 0;
    const degV = adjacency.get(v)?.length || 0;
    const connectionWeight = Math.sqrt((degU + degV) / 2) / graph.edges.length;
    
    // Vector components from gauge connection (∂A = F relationship)
    components[1] += connectionWeight * Math.cos(phaseDelta);     // e₀ vector
    components[2] += connectionWeight * Math.sin(phaseDelta);     // e₁ vector
    components[3] += connectionWeight * Math.cos(phaseDelta * 2); // e₂ vector
    components[4] += connectionWeight * Math.sin(phaseDelta * 2); // e₃ vector
  }
  
  // GRADE-2: Additional bivector components from edge orientation
  // Theory: mapping.py line 8: "curvature via bivector commutator"
  for (const [u, v] of graph.edges) {
    const labelU = graph.labels[u];
    const labelV = graph.labels[v];
    if (!labelU || !labelV || labelU.kind === labelV.kind) continue;
    
    // Mixed Z-X edges contribute to boost bivectors (e₀ᵢ)
    const phaseU = Math.PI * labelU.phase_numer / labelU.phase_denom;
    const phaseV = Math.PI * labelV.phase_numer / labelV.phase_denom;
    const edgeWeight = 1.0 / Math.sqrt(graph.edges.length);
    
    components[8] += edgeWeight * Math.sin(phaseU - phaseV);  // e₀₂ bivector
    components[9] += edgeWeight * Math.cos(phaseU + phaseV);  // e₀₃ bivector
    components[10] += edgeWeight * Math.sin(phaseU + phaseV); // e₂₃ bivector
  }
  
  // GRADE-3: Trivector components from Sovereignty (Ψ) triads
  // Theory: RawNotes.md lines 1632-1654 - "Emergence of soulhood"
  // Sovereignty = coherent triads (source-self-relation structure)
  // Not just triangles, but harmonious triune patterns
  // NOTE: rewriteHistory now passed as parameter from engine
  const sovereignTriads = detectSovereignTriads(graph, adjacency);
  
  if (sovereignTriads.length > 0) {
    // Trivector strength from sovereign triad coherence
    const sovereigntyIndex = computeSovereigntyIndex(sovereignTriads, graph, adjacency);
    const trivectorStrength = sovereigntyIndex * Math.sqrt(sovereignTriads.length) / graph.nodes.length;
    
    // Distribute across trivector components based on triad orientations
    for (const triad of sovereignTriads) {
      const [a, b, c] = triad.nodes;
      const phaseA = Math.PI * graph.labels[a].phase_numer / graph.labels[a].phase_denom;
      const phaseB = Math.PI * graph.labels[b].phase_numer / graph.labels[b].phase_denom;
      const phaseC = Math.PI * graph.labels[c].phase_numer / graph.labels[c].phase_denom;
      
      // Orientation from phase relationships
      const orientation = (phaseA + phaseB + phaseC) / 3;
      
      components[11] += triad.coherence * trivectorStrength * Math.sin(orientation);      // e₀₁₂
      components[12] += triad.coherence * trivectorStrength * Math.cos(orientation);      // e₀₁₃
      components[13] += triad.coherence * trivectorStrength * Math.sin(orientation * 2);  // e₀₂₃
      components[14] += triad.coherence * trivectorStrength * Math.cos(orientation * 2);  // e₁₂₃

      // DEBUG: Log when trivectors are being generated
      if (trivectorStrength > 0.01) {
        const trivectorMagnitude = Math.sqrt(components[11]**2 + components[12]**2 + components[13]**2 + components[14]**2);
        console.log(`🔺 Setting trivectors for triad ${triad.id}: strength=${trivectorStrength.toFixed(3)}, magnitude=${trivectorMagnitude.toFixed(3)}`);
      }
    }
  }
  
  // GRADE-4: Pseudoscalar from polarity orientation
  // Theory: Ra Material - service-to-self vs service-to-others
  // Polarity = directional will/flow asymmetry
  const polarity = computePolarityOrientation(graph, adjacency, rewriteHistory);
  components[15] = polarity * 0.5;  // e₀₁₂₃ pseudoscalar (scaled for normalization)

  // Normalize to unit magnitude
  const magnitudeSq = components.reduce((acc, c) => acc + c * c, 0);
  if (magnitudeSq > 0) {
    const norm = Math.sqrt(magnitudeSq);
    for (let i = 0; i < components.length; i += 1) {
      components[i] /= norm;
    }
  }

  return new MultivectorField({ components, algebra: 'Cl(1,3)' });
}

// Helper: Count triangles in graph (3-cycles)
function countTriangles(graph, adjacency) {
  let triangles = 0;
  const nodes = Array.from(graph.nodes);
  
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i];
    const neighborsA = adjacency.get(a) || [];
    
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j];
      if (!neighborsA.includes(b)) continue;
      
      const neighborsB = adjacency.get(b) || [];
      for (let k = j + 1; k < nodes.length; k++) {
        const c = nodes[k];
        if (neighborsA.includes(c) && neighborsB.includes(c)) {
          triangles++;
        }
      }
    }
  }
  
  return triangles;
}

// Helper: Compute global chirality from oriented cycles
function computeGraphChirality(graph, adjacency) {
  // Simple heuristic: compare Z vs X spider imbalance weighted by phase variance
  const labels = Object.values(graph.labels);
  const zCount = labels.filter(l => l.kind === 'Z').length;
  const xCount = labels.filter(l => l.kind === 'X').length;
  
  // Chirality from Z/X asymmetry and phase distribution
  const imbalance = (zCount - xCount) / (zCount + xCount + 1);
  
  // Phase variance contributes to chirality
  const phases = labels.map(l => Math.PI * l.phase_numer / l.phase_denom);
  const phaseMean = phases.reduce((sum, p) => sum + p, 0) / phases.length;
  const phaseVariance = phases.reduce((sum, p) => sum + (p - phaseMean)**2, 0) / phases.length;
  
  return imbalance * Math.sqrt(phaseVariance) * 0.1;
}
