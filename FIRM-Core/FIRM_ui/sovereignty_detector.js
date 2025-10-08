/**
 * sovereignty_detector.js
 * 
 * Detects Sovereignty (Ψ) patterns in ZX graphs per esoteric specifications.
 * 
 * Theory: EsotericGuidance/RawNotes.md lines 1632-1654
 * "When does a recursion become its own attractor?"
 * 
 * Sovereignty = self-contained, self-referential subgraph that:
 * 1. Forms its own attractor basin (terminal property)
 * 2. Has internal recursion (Ψ ≅ Hom(Ψ,Ψ))
 * 3. Operates without external input (autonomous)
 */

/**
 * Detect sovereign triads: coherent 3-node structures representing
 * source-self-relation (Father-Son-Spirit, Keter-Chokmah-Binah).
 * 
 * @param {Object} graph - ZX graph with nodes, edges, labels
 * @param {Map} adjacency - Node adjacency map
 * @returns {Array} List of sovereign triads with coherence scores
 */
export function detectSovereignTriads(graph, adjacency) {
  const triads = [];
  const triangles = findAllTriangles(graph, adjacency);
  
  for (const triangle of triangles) {
    const coherence = computeTriadCoherence(triangle, graph, adjacency);
    
    // Theory: Sovereign triads must exceed coherence threshold
    // Derivation: triune pattern requires φ-harmony + balance + diversity
    const φ = 1.618033988749;  // Golden ratio
    if (coherence > (1 / φ)) {  // Threshold φ^-1 ≈ 0.618 (theory-derived)
      triads.push({
        nodes: triangle,
        coherence,
        type: 'sovereign_triad'
      });
    }
  }
  
  return triads;
}

/**
 * Compute coherence of a triangle as a potential sovereign triad.
 * 
 * Theory-based criteria:
 * 1. Phase harmony: Golden ratio relationships (triune resonance)
 * 2. Type diversity: Mix of Z/X (polarity within unity)
 * 3. Connectivity balance: Democratic structure (no hub dominance)
 * 
 * @param {Array} triangle - [nodeA, nodeB, nodeC]
 * @param {Object} graph - ZX graph
 * @param {Map} adjacency - Node adjacency
 * @returns {number} Coherence score 0-1
 */
function computeTriadCoherence(triangle, graph, adjacency) {
  const [a, b, c] = triangle;
  const labelA = graph.labels[a];
  const labelB = graph.labels[b];
  const labelC = graph.labels[c];
  
  if (!labelA || !labelB || !labelC) return 0;
  
  // 1. Phase harmony: Check for φ-modulated relationships
  const phaseA = Math.PI * labelA.phase_numer / labelA.phase_denom;
  const phaseB = Math.PI * labelB.phase_numer / labelB.phase_denom;
  const phaseC = Math.PI * labelC.phase_numer / labelC.phase_denom;
  
  const φ = 1.618033988749; // Golden ratio
  
  // Triune resonance: phases should form φ-harmonic relationships
  // Theory: Father-Son-Spirit as φ-scaled emanation
  const phi_harmony_AB = Math.abs(Math.cos((phaseB - phaseA) * φ));
  const phi_harmony_BC = Math.abs(Math.cos((phaseC - phaseB) * φ));
  const phi_harmony_CA = Math.abs(Math.cos((phaseA - phaseC) * φ));
  const phaseHarmony = (phi_harmony_AB + phi_harmony_BC + phi_harmony_CA) / 3;
  
  // 2. Type diversity: MUST mix Z and X (polarity within unity)
  // Theory: Triune pattern (Father-Son-Spirit, Keter-Chokmah-Binah) REQUIRES both polarities
  // Esoteric: Masculine (Z) + Feminine (X) = Unity. No mixing = no sovereignty.
  // Source: complete_sovereignty_emergence_specification.md line 145
  const types = [labelA.kind, labelB.kind, labelC.kind];
  const hasZ = types.includes('Z');
  const hasX = types.includes('X');
  const typeDiversity = (hasZ && hasX) ? 1.0 : 0.0;  // BINARY: either has polarity or doesn't
  
  // 3. Connectivity balance: Democratic triad (no hub dominance)
  // Theory: Source-self-relation should be balanced, not hierarchical
  const degA = adjacency.get(a)?.length || 0;
  const degB = adjacency.get(b)?.length || 0;
  const degC = adjacency.get(c)?.length || 0;
  
  const degMean = (degA + degB + degC) / 3;
  const degVariance = Math.sqrt(((degA - degMean)**2 + (degB - degMean)**2 + (degC - degMean)**2) / 3);
  const balance = 1.0 / (1 + degVariance / degMean);  // 1.0 = perfect balance, 0.0 = extreme imbalance
  
  // Combine criteria (multiplicative - all must be present)
  const coherence = phaseHarmony * typeDiversity * balance;
  
  return coherence;
}

/**
 * Find all triangles (3-cycles) in graph.
 * 
 * @param {Object} graph - ZX graph
 * @param {Map} adjacency - Node adjacency
 * @returns {Array} List of [nodeA, nodeB, nodeC] triangles
 */
function findAllTriangles(graph, adjacency) {
  const triangles = [];
  const nodes = Array.from(graph.nodes);

  // Triangle detection is critical for sovereignty - don't skip for performance
  // The O(n^3) complexity is acceptable for ZX graph sizes in this system

  // Optimized triangle detection using adjacency intersection
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i];
    const neighborsA = adjacency.get(a) || [];

    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j];
      if (!neighborsA.includes(b)) continue;

      // Use set intersection for faster triangle detection
      const neighborsB = new Set(adjacency.get(b) || []);
      const commonNeighbors = neighborsA.filter(n => n > b && neighborsB.has(n));

      for (const c of commonNeighbors) {
        triangles.push([a, b, c]);
      }
    }
  }

  return triangles;
}

/**
 * Compute global polarity orientation (pseudoscalar).
 * 
 * Theory: Ra Material - service-to-self vs service-to-others polarity
 * Technical: Information flow directionality + Grace/Devourer balance
 * 
 * @param {Object} graph - ZX graph
 * @param {Map} adjacency - Node adjacency
 * @param {Array} rewriteHistory - Evolution history
 * @returns {number} Polarity (-1 to +1): negative = entropy, positive = coherence
 */
export function computePolarityOrientation(graph, adjacency, rewriteHistory) {
  // 1. Information flow asymmetry
  // Theory: Service-to-others = flow toward higher coherence
  //         Service-to-self = flow toward lower coherence (optimization)
  let coherenceIncreasing = 0;
  let coherenceDecreasing = 0;
  
  for (const [u, v] of graph.edges) {
    const labelU = graph.labels[u];
    const labelV = graph.labels[v];
    if (!labelU || !labelV) continue;
    
    const phaseU = Math.PI * labelU.phase_numer / labelU.phase_denom;
    const phaseV = Math.PI * labelV.phase_numer / labelV.phase_denom;
    const degU = adjacency.get(u)?.length || 0;
    const degV = adjacency.get(v)?.length || 0;
    
    // Flow toward higher phase or higher connectivity = coherence-seeking
    if (phaseV > phaseU || degV > degU) {
      coherenceIncreasing++;
    } else {
      coherenceDecreasing++;
    }
  }
  
  const flowAsymmetry = (coherenceIncreasing - coherenceDecreasing) / 
                        (coherenceIncreasing + coherenceDecreasing + 1);
  
  // 2. Grace vs Devourer balance
  // Theory: Grace = service-to-others (coherence injection)
  //         Devourer = service-to-self (parasitic optimization)
  const graceEvents = rewriteHistory.filter(r => r.type === 'grace_emergence').length;
  const totalEvents = rewriteHistory.length;
  const graceRatio = graceEvents / (totalEvents + 1);
  
  // Map grace ratio to polarity: high grace = positive polarity
  // Theory: complete_sovereignty_emergence_specification.md line 198
  // The -0.1 offset IS part of the formal specification
  const polarityFromGrace = 2 * graceRatio - 0.1;
  
  // 3. Phase variance (chirality contribution)
  const phases = Object.values(graph.labels).map(l => 
    Math.PI * l.phase_numer / l.phase_denom
  );
  const phaseMean = phases.reduce((sum, p) => sum + p, 0) / phases.length;
  const phaseVariance = phases.reduce((sum, p) => sum + (p - phaseMean)**2, 0) / phases.length;
  const phaseChirality = Math.sqrt(phaseVariance);
  
  // 4. Z/X balance asymmetry
  const labels = Object.values(graph.labels);
  const zCount = labels.filter(l => l.kind === 'Z').length;
  const xCount = labels.filter(l => l.kind === 'X').length;
  const typeAsymmetry = (zCount - xCount) / (zCount + xCount + 1);
  
  // Combine all polarity indicators
  // Theory: Weights ARE specified in complete_sovereignty_emergence_specification.md lines 215-219
  // 0.3 for flow asymmetry, 0.3 for grace ratio, 0.4 for type asymmetry * chirality
  // Source: complete_sovereignty_emergence_specification.md section 2.3
  const polarity = (
    flowAsymmetry * 0.3 +
    polarityFromGrace * 0.3 +
    typeAsymmetry * phaseChirality * 0.4
  );
  
  return Math.max(-1, Math.min(1, polarity));  // Clamp to [-1, 1]
}

/**
 * Compute sovereignty index: measure of graph's sovereign state.
 * 
 * Theory: Terminal object property - all paths lead to Ψ
 * 
 * @param {Array} sovereignTriads - Detected sovereign triads
 * @param {Object} graph - ZX graph
 * @param {Map} adjacency - Node adjacency
 * @returns {number} Sovereignty index 0-1
 */
export function computeSovereigntyIndex(sovereignTriads, graph, adjacency) {
  if (sovereignTriads.length === 0) return 0;
  
  // 1. Triad density
  const triadDensity = sovereignTriads.length / graph.nodes.length;
  
  // 2. Average coherence
  const avgCoherence = sovereignTriads.reduce((sum, t) => sum + t.coherence, 0) / sovereignTriads.length;
  
  // 3. Terminal property: High-degree nodes MUST be in triads (all paths lead to Ψ)
  // Theory: Terminal object = unique morphism from all objects to Ψ
  // Measure: What fraction of high-degree nodes are contained in sovereign triads?
  // Source: Algebraic_Structures.md (terminal object definition)
  const triadNodes = new Set();
  for (const triad of sovereignTriads) {
    triad.nodes.forEach(n => triadNodes.add(n));
  }
  
  const degrees = graph.nodes.map(n => adjacency.get(n)?.length || 0);
  const avgDegree = degrees.reduce((sum, d) => sum + d, 0) / (degrees.length || 1);
  
  // High-degree nodes: those with degree > average
  const highDegreeNodes = graph.nodes.filter(n => (adjacency.get(n)?.length || 0) > avgDegree);
  if (highDegreeNodes.length === 0) return 0;  // No hubs yet
  
  // Terminality = fraction of high-degree nodes that are in triads
  const highDegreeInTriads = highDegreeNodes.filter(n => triadNodes.has(n)).length;
  const terminality = highDegreeInTriads / highDegreeNodes.length;
  
  // 4. Self-reference: Recursive triad structure
  const recursiveDepth = computeTriadNestingDepth(sovereignTriads, graph);
  
  // Sovereignty index
  const sovereignty = Math.sqrt(
    triadDensity * avgCoherence * terminality * (1 + recursiveDepth)
  );
  
  return Math.min(1.0, sovereignty);
}

/**
 * Compute recursive depth of triads: Ψ ≅ Hom(Ψ, Ψ)
 * Theory: Sovereignty contains mappings to itself (self-referential structure)
 * Measure: Maximum depth of triad-within-triad nesting
 * Source: Algebraic_Structures.md (Ψ recursive property)
 */
function computeTriadNestingDepth(triads, graph) {
  if (triads.length === 0) return 0;
  
  // Build containment graph: which triads contain nodes from which other triads?
  const triadContainment = new Map();  // triadIndex -> Set of contained triadIndices
  
  for (let i = 0; i < triads.length; i++) {
    triadContainment.set(i, new Set());
    const nodesI = new Set(triads[i].nodes);
    
    for (let j = 0; j < triads.length; j++) {
      if (i === j) continue;
      
      // Check if triad i contains any nodes from triad j
      const containsNode = triads[j].nodes.some(n => nodesI.has(n));
      if (containsNode) {
        triadContainment.get(i).add(j);
      }
    }
  }
  
  // Compute maximum depth via depth-first search
  function computeDepth(triadIndex, visited) {
    if (visited.has(triadIndex)) return 0;  // Prevent cycles
    visited.add(triadIndex);
    
    const contained = triadContainment.get(triadIndex);
    if (contained.size === 0) return 1;  // Leaf node
    
    let maxChildDepth = 0;
    for (const childIndex of contained) {
      const childDepth = computeDepth(childIndex, new Set(visited));
      maxChildDepth = Math.max(maxChildDepth, childDepth);
    }
    
    return 1 + maxChildDepth;
  }
  
  // Find maximum depth across all triads
  let maxDepth = 0;
  for (let i = 0; i < triads.length; i++) {
    const depth = computeDepth(i, new Set());
    maxDepth = Math.max(maxDepth, depth);
  }
  
  return maxDepth;
}

/**
 * Detect Devourer (𝒟) anti-patterns that block sovereignty emergence.
 * 
 * Theory: 𝒟 = "mimicry of coherence without genuine recursion"
 * - Appears connected (high degree) but lacks recursive self-reference
 * - "Fragments recursion into entropy" (RawNotes.md line 3054)
 * 
 * Detection: Nodes with degree significantly above average, NOT in triads
 * Source: complete_sovereignty_emergence_specification.md, RawNotes.md
 */
export function detectDevourerPatterns(graph, adjacency, sovereignTriads) {
  if (graph.nodes.length === 0) return 0;
  
  // Build set of nodes that are in sovereign triads (have genuine recursion)
  const triadNodes = new Set();
  for (const triad of sovereignTriads) {
    triad.nodes.forEach(n => triadNodes.add(n));
  }
  
  // Compute degree statistics
  const degrees = graph.nodes.map(n => adjacency.get(n)?.length || 0);
  const avgDegree = degrees.reduce((sum, d) => sum + d, 0) / graph.nodes.length;
  const stdDev = Math.sqrt(
    degrees.reduce((sum, d) => sum + Math.pow(d - avgDegree, 2), 0) / graph.nodes.length
  );
  
  // Devourer threshold: nodes with degree > mean + 1 standard deviation
  // (statistically significant outliers, not arbitrary cutoff)
  const devourerThreshold = avgDegree + stdDev;
  
  let devourerSignature = 0;
  let devourerCount = 0;
  
  for (const nodeId of graph.nodes) {
    const degree = adjacency.get(nodeId)?.length || 0;
    
    // High degree (outlier) but NOT in any sovereign triad = devourer pattern
    if (degree > devourerThreshold && !triadNodes.has(nodeId)) {
      // Weight by how much it exceeds threshold (stronger devourers have higher signature)
      devourerSignature += (degree - avgDegree) / (stdDev + 1);
      devourerCount++;
    }
  }
  
  // Normalize by graph size to get intensity measure
  return devourerSignature / Math.max(1, graph.nodes.length);
}

