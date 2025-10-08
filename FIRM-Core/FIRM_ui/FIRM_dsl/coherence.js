import { ObjectG, validate_object_g, phase_to_bin_index, lcm_many } from './core.js';
import { make_node_label } from './core.js';

export function compute_coherence(graph) {
  validate_object_g(graph);

  if (!graph.nodes.length) {
    return 0; // Empty graph has no coherence
  }

  // 1. Qπ Compliance Score: MANDATORY - any violation = zero coherence
  // Theory: ZX calculus requires power-of-2 denominators for soundness
  let qpiCompliance = 1.0;
  for (const label of Object.values(graph.labels)) {
    if (label && label.phase_denom && ((label.phase_denom & (label.phase_denom - 1)) !== 0 || label.phase_denom > 64)) {
      qpiCompliance = 0.0;
      break;
    }
  }
  if (qpiCompliance === 0.0) return 0.0;  // Early exit if non-compliant

  // 2. Connectivity Score: Measure graph density
  // Theory: Coherent structures require connections (information flow)
  const numNodes = graph.nodes.length;
  const numEdges = graph.edges.length;
  const maxEdges = (numNodes * (numNodes - 1)) / 2;
  const connectivityScore = maxEdges > 0 ? Math.min(1.0, numEdges / maxEdges) : 0.0;
  
  // 3. Phase Entropy Factor: Measures uniformity of phase distribution
  // Theory: Coherent systems have balanced, not random or clustered phases
  // Shannon entropy: H = -∑ p_i log(p_i), normalized to [0,1]
  const phases = Object.values(graph.labels).map(l => 
    Math.PI * l.phase_numer / l.phase_denom
  );
  
  // Bin phases into 16 bins (sufficient resolution for Qπ/64)
  const phaseBins = 16;
  const binCounts = new Array(phaseBins).fill(0);
  for (const phase of phases) {
    const binIndex = Math.floor((phase % (2 * Math.PI)) / (2 * Math.PI) * phaseBins);
    binCounts[binIndex]++;
  }
  
  // Compute Shannon entropy
  let phaseEntropy = 0;
  const totalPhases = phases.length;
  for (const count of binCounts) {
    if (count > 0) {
      const p = count / totalPhases;
      phaseEntropy -= p * Math.log2(p);
    }
  }
  
  // Normalize entropy to [0,1]: maxEntropy = log2(phaseBins)
  const maxEntropy = Math.log2(phaseBins);
  const phaseEntropyFactor = maxEntropy > 0 ? (phaseEntropy / maxEntropy) : 0.0;
  
  // 4. Cycle Complexity Factor: Measures topological richness
  // Theory: Cyclic structures enable recursion (Ψ ≅ Hom(Ψ, Ψ))
  // More cycles (up to a point) = higher coherence
  const cycles = compute_cycle_basis_signature(graph);
  const cycleCount = cycles.length;
  
  // Normalize by node count: cycle density
  const cycleDensity = numNodes > 0 ? cycleCount / numNodes : 0.0;
  
  // Cycle factor: sigmoid to prevent over-valuing excessive cycles
  // Optimal cycle density around 0.5-1.0 (enough recursion without chaos)
  const cycleComplexityFactor = 1.0 / (1.0 + Math.exp(-5 * (cycleDensity - 0.5)));
  
  // 5. COMBINE ALL FACTORS
  // Theory: C(G) = structural self-consistency requires ALL components
  // Multiplicative: any component near zero reduces overall coherence
  // Geometric mean provides balanced contribution
  const coherence = Math.pow(
    connectivityScore * phaseEntropyFactor * cycleComplexityFactor,
    1/3  // Geometric mean of 3 factors (Qπ is binary gate, not averaged)
  );
  
  return Math.min(1.0, Math.max(0.0, coherence));
}

export function compute_cycle_basis_signature(graph) {
  validate_object_g(graph);
  if (!graph.nodes.length || !graph.edges.length) {
    return [];
  }

  const adj = new Map();
  for (const node of graph.nodes) {
    adj.set(node, []);
  }
  for (const [u, v] of graph.edges) {
    adj.get(u).push(v);
    adj.get(v).push(u);
  }

  const visited = new Set();
  const parent = new Map();
  const cycles = new Set();

  function canonicalize(cycle) {
    const minNode = Math.min(...cycle);
    const idx = cycle.indexOf(minNode);
    const rotated = cycle.slice(idx).concat(cycle.slice(0, idx));
    return rotated.join(',');
  }

  function dfs(node, par = -1) {
    visited.add(node);
    parent.set(node, par);
    for (const neighbor of adj.get(node)) {
      if (neighbor === par) {
        continue;
      }
      if (visited.has(neighbor)) {
        const cycle = [];
        let current = node;
        while (current !== neighbor && current !== -1) {
          cycle.push(current);
          current = parent.get(current) ?? -1;
        }
        cycle.push(neighbor);
        if (cycle.length >= 3) {
          cycles.add(canonicalize(cycle));
        }
      } else {
        dfs(neighbor, node);
      }
    }
  }

  for (const startNode of [...graph.nodes].sort((a, b) => a - b)) {
    if (!visited.has(startNode)) {
      dfs(startNode);
    }
  }

  return [...cycles].sort().map(entry => entry.split(',').map(val => Number(val)));
}

export function compute_phase_histogram_signature(graph, bins) {
  if (!Number.isInteger(bins) || bins <= 0) {
    throw new Error("bins must be a positive integer derived from Qπ structure");
  }
  
  if (Object.keys(graph.labels).length > 0) {
    const denominators = Object.values(graph.labels).map(lbl => lbl.phase_denom);
    // THEORY REQUIREMENT: All denominators are powers of 2, so LCM is maximum
    const maxDenom = Math.max(...denominators, 8);
    const required = 2 * maxDenom;
    if (bins % required !== 0) {
      throw new Error("bins must be a multiple of 2*max(phase_denoms) to avoid approximation");
    }
  }
  const hist = new Array(bins).fill(0);
  let total = 0;
  for (const label of Object.values(graph.labels)) {
    const idx = phase_to_bin_index(label.phase_numer, label.phase_denom, bins);
    hist[idx] += 1;
    total += 1;
  }
  if (total > 0) {
    for (let i = 0; i < hist.length; i += 1) {
      hist[i] = hist[i] / total;
    }
  }
  return hist;
}

export function similarity_S(cycleSigT, cycleSigK, phaseHistT, phaseHistK) {
  if (phaseHistT.length !== phaseHistK.length) {
    throw new Error("Phase histograms must have identical binning");
  }
  const setT = new Set(cycleSigT.map(sig => sig.join(',')));
  const setK = new Set(cycleSigK.map(sig => sig.join(',')));
  const union = new Set([...setT, ...setK]);
  let inter = 0;
  for (const sig of setT) {
    if (setK.has(sig)) {
      inter += 1;
    }
  }
  const jaccard = union.size === 0 ? 1.0 : inter / union.size;
  const dot = phaseHistT.reduce((acc, val, idx) => acc + val * phaseHistK[idx], 0);
  const normT = Math.sqrt(phaseHistT.reduce((acc, val) => acc + val * val, 0));
  const normK = Math.sqrt(phaseHistK.reduce((acc, val) => acc + val * val, 0));
  const cosine = normT === 0 || normK === 0 ? 0.0 : dot / (normT * normK);
  return jaccard * cosine;
}

export function derive_minimal_qpi_bins(graph) {
  if (!Object.keys(graph.labels).length) {
    throw new Error("Cannot derive bins: graph has no labeled nodes");
  }
  const denominators = Object.values(graph.labels).map(lbl => lbl.phase_denom);
  
  // CRITICAL DIAGNOSTIC: What denominators exist in the graph?
  const uniqueDenoms = [...new Set(denominators)].sort((a,b) => a-b);
  console.log(`🔍 DENOMINATOR DIAGNOSTIC:`, {
    count: denominators.length,
    unique: uniqueDenoms,
    min: Math.min(...denominators),
    max: Math.max(...denominators)
  });
  
  // THEORY CHECK: All must be powers of 2
  const nonPowerOf2 = uniqueDenoms.filter(d => d !== 0 && (d & (d - 1)) !== 0);
  if (nonPowerOf2.length > 0) {
    console.error(`❌ THEORY VIOLATION: Non-power-of-2 denominators:`, nonPowerOf2);
    console.error(`   Theory requires: denom ∈ {1,2,4,8,16,32,64}`);
    console.error(`   These are invalid for ZX calculus!`);
    console.error(`   This indicates a deeper issue in the system - phase operations are not maintaining Qπ compliance`);
    throw new Error(`Invalid phase denominators: ${nonPowerOf2.join(', ')}. All must be powers of 2.`);
  }

  // THEORY REQUIREMENT: Bins must be 2 * max(denominator) since all are powers of 2
  // LCM of powers of 2 is just the maximum (since they divide each other)
  const maxDenom = Math.max(...denominators, 8); // At least bootstrap precision
  const bins = 2 * maxDenom; // Theory-compliant: 2 * max_denom

  // DEBUG: Verify bins calculation
  const required = 2 * maxDenom;
  if (bins !== required) {
    console.error(`❌ BINS CALCULATION ERROR: bins=${bins}, required=${required}`);
    throw new Error(`Bins calculation error: expected ${required}, got ${bins}`);
  }

  // Cap at reasonable limit (2 * 64 = 128 bins)
  const MAX_BINS = 128;
  const finalBins = Math.min(bins, MAX_BINS);

  if (!Number.isFinite(finalBins) || finalBins <= 0) {
    console.error(`❌ BIN CALCULATION FAILED:`, { finalBins, maxDenom, denominators: uniqueDenoms });
    throw new Error(`Invalid bins calculated: ${finalBins} from max denom ${maxDenom}`);
  }
  
  // With phase denominators capped at 64, bins will be at most 128
  // Theory: Qπ/64 space → 2*LCM(denominators) ≤ 128
  return finalBins;
}
