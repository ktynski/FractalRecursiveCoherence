import { ObjectG, validate_object_g, phase_to_bin_index, lcm_many } from './core.js';
import { make_node_label } from './core.js';

export function compute_coherence(graph) {
  validate_object_g(graph);
  const cycles = compute_cycle_basis_signature(graph);
  let cycleCoherence = 0.0;

  for (const cycle of cycles) {
    const cyclePhases = [];
    for (const nodeId of cycle) {
      const label = graph.labels[nodeId];
      if (label) {
        const phaseRadians = Math.PI * label.phase_numer / label.phase_denom;
        cyclePhases.push(phaseRadians);
      }
    }
    if (cyclePhases.length > 0) {
      const n = cyclePhases.length;
      const meanPhase = cyclePhases.reduce((acc, p) => acc + p, 0) / n;
      const variance = cyclePhases.reduce((acc, p) => acc + (p - meanPhase) ** 2, 0) / n;
      const phaseHarmony = 1.0 / (1.0 + variance);
      const spectralFlatness = phaseHarmony;
      cycleCoherence += spectralFlatness + phaseHarmony;
    }
  }

  let nodeResonance = 0.0;
  for (const [nodeId, label] of Object.entries(graph.labels)) {
    const degree = graph.edges.reduce((deg, [u, v]) => deg + (u === Number(nodeId) || v === Number(nodeId) ? 1 : 0), 0);
    const connectivityFactor = Math.log(1 + degree);
    const phaseSimplicity = 1.0 / (1.0 + label.phase_denom);
    nodeResonance += connectivityFactor * phaseSimplicity;
  }

  return cycleCoherence + nodeResonance;
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
    const required = 2 * lcm_many(denominators);
    if (bins % required !== 0) {
      throw new Error("bins must be a multiple of 2*LCM(phase_denoms) to avoid approximation");
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
  return 2 * lcm_many(denominators);
}
