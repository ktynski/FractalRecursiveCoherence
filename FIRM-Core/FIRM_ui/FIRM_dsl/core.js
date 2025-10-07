// Core categorical constructs for the FIRM DSL in JavaScript.
// Mirrors FIRM_dsl/core.py without introducing empirical parameters or floats.

export class NodeLabel {
  constructor(kind, phaseNumer, phaseDenom, monadicId) {
    this.kind = kind;
    this.phase_numer = phaseNumer;
    this.phase_denom = phaseDenom;
    this.monadic_id = monadicId;
    Object.freeze(this);
  }
}

export class ObjectG {
  constructor({ nodes, edges, labels }) {
    this.nodes = Array.from(nodes || []);
    this.edges = Array.from(edges || []);
    this.labels = { ...labels };
    // Keep arrays mutable for evolution but freeze the overall object structure
    // Object.freeze(this.nodes);  // Removed to allow evolution modifications
    // Object.freeze(this.edges);  // Removed to allow evolution modifications
    // Object.freeze(this.labels); // Removed to allow evolution modifications
    Object.freeze(this);
  }
}

export function normalize_phase_qpi(phaseNumer, phaseDenom) {
  if (!Number.isInteger(phaseDenom) || phaseDenom <= 0) {
    throw new Error("phase_denom must be a positive integer");
  }
  const mod = 2 * phaseDenom;
  let numerMod = phaseNumer % mod;
  if (numerMod < 0) {
    numerMod += mod;
  }
  const g = gcd(Math.abs(numerMod), phaseDenom);
  const numerRed = numerMod / g;
  const denomRed = phaseDenom / g;
  return [numerRed, denomRed];
}

export function make_node_label(kind, phaseNumer, phaseDenom, monadicId) {
  if (kind !== "Z" && kind !== "X") {
    throw new Error("kind must be 'Z' or 'X'");
  }
  const [n, d] = normalize_phase_qpi(phaseNumer, phaseDenom);
  return new NodeLabel(kind, n, d, monadicId);
}

export function validate_object_g(obj) {
  const nodeSet = new Set(obj.nodes);
  for (const [u, v] of obj.edges) {
    if (u === v) {
      throw new Error("Self-loops are not permitted in ZX object graphs");
    }
    if (!nodeSet.has(u) || !nodeSet.has(v)) {
      throw new Error("Edge references unknown node id");
    }
  }
  for (const [nid, lbl] of Object.entries(obj.labels)) {
    const nodeId = Number(nid);
    if (!nodeSet.has(nodeId)) {
      throw new Error("Label references unknown node id");
    }
    const [cn, cd] = normalize_phase_qpi(lbl.phase_numer, lbl.phase_denom);
    if (cn !== lbl.phase_numer || cd !== lbl.phase_denom) {
      throw new Error("NodeLabel phase must be Qπ-normalized prior to construction");
    }
    if (lbl.kind !== "Z" && lbl.kind !== "X") {
      throw new Error("NodeLabel.kind must be 'Z' or 'X'");
    }
  }
  return obj;
}

export function add_phases_qpi(aNumer, aDenom, bNumer, bDenom) {
  const l = lcm(aDenom, bDenom);
  const an = aNumer * (l / aDenom);
  const bn = bNumer * (l / bDenom);
  return normalize_phase_qpi(an + bn, l);
}

export function phase_to_bin_index(phaseNumer, phaseDenom, bins) {
  if (!Number.isInteger(bins) || bins <= 0) {
    throw new Error("bins must be a positive integer");
  }
  const [n, d] = normalize_phase_qpi(phaseNumer, phaseDenom);
  const period = 2 * d;
  if (bins % period !== 0) {
    throw new Error("bins must be a multiple of 2*phase_denom to avoid approximation");
  }
  const step = bins / period;
  return (n * step) % bins;
}

export function lcm_many(values) {
  if (!Array.isArray(values) || values.length === 0) {
    throw new Error("values must be non-empty");
  }
  let l = 1;
  for (const v of values) {
    if (!Number.isInteger(v) || v <= 0) {
      throw new Error("values must be positive integers");
    }
    l = lcm(l, v);
  }
  return l;
}

function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    const temp = y;
    y = x % y;
    x = temp;
  }
  return x || 1;
}

function lcm(a, b) {
  return Math.abs(a * b) / gcd(a, b);
}
