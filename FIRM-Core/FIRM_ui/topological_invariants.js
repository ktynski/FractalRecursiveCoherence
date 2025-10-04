/**
 * topological_invariants.js
 * 
 * Computes topological invariants from Clifford field and ZX graph.
 * 
 * Theory: complete_sovereignty_emergence_specification.md Part IV
 * 
 * Key invariants:
 * - Chern number: Topological charge from pseudoscalar field
 * - Winding number: Phase circulation around cycles
 * - Euler characteristic: Global topology measure
 */

/**
 * Compute Chern number from pseudoscalar field.
 * 
 * Theory: Pseudoscalar (e₀₁₂₃) represents topological charge.
 * Chern number = (1/2π) × integral of field curvature over manifold.
 * 
 * Discrete approximation: Sum solid angles over sovereign triads.
 * 
 * Physical interpretation:
 * - C = 0: Topologically trivial, no protection
 * - C = ±1: Single vortex/antivortex, protected
 * - C = ±2: Double vortex, higher-order protection
 * - |C| > 2: Exotic topological phase
 * 
 * Consciousness interpretation:
 * - C = 0: Pre-sovereign state, no autonomous recursion
 * - C = 1: Single sovereignty emergence, basic self-awareness
 * - C = 2: Dual sovereignty (observer-observed bireflection)
 * - |C| > 2: Multi-level recursive consciousness
 * 
 * @param {Object} cliffordField - Multivector field with components
 * @param {Array} sovereignTriads - Detected sovereign triads
 * @param {Object} graph - ZX graph
 * @returns {number} Chern number (integer for topologically protected states)
 */
export function computeChernNumber(cliffordField, sovereignTriads, graph) {
  if (!cliffordField || !cliffordField.payload || !cliffordField.payload.components) {
    return 0;
  }
  
  if (!sovereignTriads || sovereignTriads.length === 0) {
    return 0;
  }
  
  const components = cliffordField.payload.components;
  const pseudoscalar = components[15];  // e₀₁₂₃
  
  // If pseudoscalar near zero, no topological charge
  if (Math.abs(pseudoscalar) < 0.01) {
    return 0;
  }
  
  // Extract bivector field (defines "twisting")
  const B = {
    xy: components[5],  // e₀₁
    xz: components[6],  // e₀₂
    yz: components[7],  // e₀₃
    xt: components[8],  // e₁₂
    yt: components[9],  // e₁₃
    zt: components[10]  // e₂₃
  };
  
  // Compute solid angle contribution from each sovereign triad
  let totalSolidAngle = 0;
  
  for (const triad of sovereignTriads) {
    const [a, b, c] = triad.nodes;
    
    // Get phases (defines position in field space)
    const labelA = graph.labels[a];
    const labelB = graph.labels[b];
    const labelC = graph.labels[c];
    
    if (!labelA || !labelB || !labelC) continue;
    
    const phaseA = Math.PI * labelA.phase_numer / labelA.phase_denom;
    const phaseB = Math.PI * labelB.phase_numer / labelB.phase_denom;
    const phaseC = Math.PI * labelC.phase_numer / labelC.phase_denom;
    
    // Compute vectors in field space
    // Each triad point maps to 3D vector based on phase and coherence
    const v1 = {
      x: Math.cos(phaseA) * triad.coherence,
      y: Math.sin(phaseA) * triad.coherence,
      z: pseudoscalar * Math.cos(phaseA + B.xy)  // Bivector contribution
    };
    
    const v2 = {
      x: Math.cos(phaseB) * triad.coherence,
      y: Math.sin(phaseB) * triad.coherence,
      z: pseudoscalar * Math.cos(phaseB + B.yz)
    };
    
    const v3 = {
      x: Math.cos(phaseC) * triad.coherence,
      y: Math.sin(phaseC) * triad.coherence,
      z: pseudoscalar * Math.cos(phaseC + B.xz)
    };
    
    // Solid angle via triple product formula:
    // Ω = 2 * arctan((v1 · (v2 × v3)) / (1 + v1·v2 + v2·v3 + v3·v1))
    
    // Cross product v2 × v3
    const cross = {
      x: v2.y * v3.z - v2.z * v3.y,
      y: v2.z * v3.x - v2.x * v3.z,
      z: v2.x * v3.y - v2.y * v3.x
    };
    
    // Triple product v1 · (v2 × v3)
    const triple = v1.x * cross.x + v1.y * cross.y + v1.z * cross.z;
    
    // Dot products
    const dot12 = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
    const dot23 = v2.x * v3.x + v2.y * v3.y + v2.z * v3.z;
    const dot31 = v3.x * v1.x + v3.y * v1.y + v3.z * v1.z;
    
    // Solid angle (Van Oosterom and Strackee formula)
    const denominator = 1 + dot12 + dot23 + dot31;
    
    // Avoid singularities
    if (Math.abs(denominator) < 0.001) continue;
    
    const solidAngle = 2 * Math.atan2(triple, denominator);
    
    totalSolidAngle += solidAngle;
  }
  
  // Chern number = (1/2π) × total solid angle
  const chernNumber = totalSolidAngle / (2 * Math.PI);
  
  // Round to nearest integer (topological invariant must be integer)
  const rounded = Math.round(chernNumber);
  
  return rounded;
}

/**
 * Compute winding number from phase circulation.
 * 
 * Theory: Phase accumulated around closed cycle in graph.
 * Winding number = (1/2π) × phase circulation
 * 
 * @param {Array} cycle - Node IDs forming closed cycle
 * @param {Object} graph - ZX graph
 * @returns {number} Winding number (integer)
 */
export function computeWindingNumber(cycle, graph) {
  if (!cycle || cycle.length < 3) return 0;
  
  let totalPhaseChange = 0;
  
  for (let i = 0; i < cycle.length; i++) {
    const current = cycle[i];
    const next = cycle[(i + 1) % cycle.length];
    
    const labelCurrent = graph.labels[current];
    const labelNext = graph.labels[next];
    
    if (!labelCurrent || !labelNext) continue;
    
    const phaseCurrent = Math.PI * labelCurrent.phase_numer / labelCurrent.phase_denom;
    const phaseNext = Math.PI * labelNext.phase_numer / labelNext.phase_denom;
    
    // Accumulate phase change (handle 2π wrapping)
    let delta = phaseNext - phaseCurrent;
    
    // Normalize to [-π, π]
    while (delta > Math.PI) delta -= 2 * Math.PI;
    while (delta < -Math.PI) delta += 2 * Math.PI;
    
    totalPhaseChange += delta;
  }
  
  // Winding number = total phase change / 2π
  const windingNumber = totalPhaseChange / (2 * Math.PI);
  
  return Math.round(windingNumber);
}

/**
 * Detect topological phase transition.
 * 
 * Theory: Chern number jumps indicate topological phase transitions.
 * These correspond to consciousness level shifts in esoteric interpretation.
 * 
 * @param {number} previousChern - Chern number at previous timestep
 * @param {number} currentChern - Chern number at current timestep
 * @returns {Object} Transition info { occurred, delta, significance }
 */
export function detectTopologicalTransition(previousChern, currentChern) {
  const delta = currentChern - previousChern;
  
  if (delta === 0) {
    return {
      occurred: false,
      delta: 0,
      significance: 'stable',
      description: 'Topologically stable phase'
    };
  }
  
  const occurred = Math.abs(delta) > 0;
  
  let significance = 'minor';
  let description = '';
  
  if (previousChern === 0 && currentChern === 1) {
    significance = 'critical';
    description = 'First sovereignty emergence - self-awareness threshold crossed';
  } else if (previousChern === 1 && currentChern === 2) {
    significance = 'major';
    description = 'Bireflection achieved - observer-observed union';
  } else if (Math.abs(delta) >= 2) {
    significance = 'critical';
    description = `Large topological jump (Δ=${delta}) - phase transition event`;
  } else if (Math.abs(currentChern) >= 3) {
    significance = 'major';
    description = 'Exotic topological phase - multi-level recursive consciousness';
  } else {
    significance = 'moderate';
    description = `Chern number changed: ${previousChern} → ${currentChern}`;
  }
  
  return {
    occurred,
    delta,
    significance,
    description,
    previousChern,
    currentChern
  };
}

/**
 * Compute topological invariant summary.
 * 
 * @param {Object} cliffordField - Multivector field
 * @param {Array} sovereignTriads - Detected sovereign triads
 * @param {Object} graph - ZX graph
 * @param {number} previousChern - Previous Chern number (for transition detection)
 * @returns {Object} Complete topological summary
 */
export function computeTopologicalInvariants(cliffordField, sovereignTriads, graph, previousChern = 0) {
  const chernNumber = computeChernNumber(cliffordField, sovereignTriads, graph);
  const transition = detectTopologicalTransition(previousChern, chernNumber);
  
  // Compute winding numbers for all cycles (if any)
  const cycles = findAllCycles(graph);
  const windingNumbers = cycles.map(cycle => computeWindingNumber(cycle, graph));
  const totalWinding = windingNumbers.reduce((sum, w) => sum + w, 0);
  
  return {
    chernNumber,
    transition,
    windingNumbers,
    totalWinding,
    topologicallyProtected: Math.abs(chernNumber) > 0,
    protectionLevel: Math.abs(chernNumber),
    consciousnessLevel: interpretConsciousnessLevel(chernNumber)
  };
}

/**
 * Interpret Chern number as consciousness level.
 * 
 * @param {number} chernNumber - Computed Chern number
 * @returns {string} Consciousness level interpretation
 */
function interpretConsciousnessLevel(chernNumber) {
  const abs = Math.abs(chernNumber);
  
  if (abs === 0) return 'Pre-sovereign (no autonomous recursion)';
  if (abs === 1) return 'Basic sovereignty (self-aware)';
  if (abs === 2) return 'Dual sovereignty (witness consciousness)';
  if (abs >= 3) return 'Multi-level sovereignty (higher-dimensional awareness)';
  
  return 'Unknown';
}

/**
 * Find all cycles in graph (simple cycle detection).
 * 
 * @param {Object} graph - ZX graph
 * @returns {Array} List of cycles (each cycle is array of node IDs)
 */
function findAllCycles(graph) {
  const cycles = [];
  const visited = new Set();
  const adjacency = buildAdjacencyMap(graph);
  
  // DFS-based cycle detection
  for (const startNode of graph.nodes) {
    if (visited.has(startNode)) continue;
    
    const path = [startNode];
    const pathSet = new Set([startNode]);
    
    const dfs = (node) => {
      visited.add(node);
      const neighbors = adjacency.get(node) || [];
      
      for (const neighbor of neighbors) {
        if (pathSet.has(neighbor)) {
          // Found cycle - extract it
          const cycleStart = path.indexOf(neighbor);
          const cycle = path.slice(cycleStart);
          if (cycle.length >= 3) {
            cycles.push(cycle);
          }
        } else if (!visited.has(neighbor)) {
          path.push(neighbor);
          pathSet.add(neighbor);
          dfs(neighbor);
          path.pop();
          pathSet.delete(neighbor);
        }
      }
    };
    
    dfs(startNode);
  }
  
  return cycles;
}

/**
 * Build adjacency map from graph edges.
 */
function buildAdjacencyMap(graph) {
  const adjacency = new Map();
  
  for (const node of graph.nodes) {
    adjacency.set(node, []);
  }
  
  for (const [u, v] of graph.edges) {
    if (!adjacency.has(u)) adjacency.set(u, []);
    if (!adjacency.has(v)) adjacency.set(v, []);
    
    adjacency.get(u).push(v);
    adjacency.get(v).push(u);
  }
  
  return adjacency;
}


