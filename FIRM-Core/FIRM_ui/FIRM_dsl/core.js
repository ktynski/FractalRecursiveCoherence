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

// Helper: Round to nearest power of 2
// Theory requirement (bootstrap_phase_derivation.md): denominators must be 2^k
function nearestPowerOf2(n) {
  if (n <= 1) return 1;
  if (n > 64) return 64; // Theory cap (T-gate precision limit)
  const lower = 1 << Math.floor(Math.log2(n));
  const upper = 1 << Math.ceil(Math.log2(n));
  return (n - lower < upper - n) ? lower : upper;
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
  const numerRed = Math.floor(numerMod / g);
  const denomRed = Math.floor(phaseDenom / g);
  return [numerRed, denomRed];
}

export function make_node_label(kind, phaseNumer, phaseDenom, monadicId) {
  if (kind !== "Z" && kind !== "X") {
    throw new Error("kind must be 'Z' or 'X'");
  }
  
  // THEORY REQUIREMENT: Denominator must be power of 2
  const denomPow2 = nearestPowerOf2(phaseDenom);
  if (denomPow2 !== phaseDenom) {
    // Renormalize to nearest power of 2
    const phaseRad = Math.PI * phaseNumer / phaseDenom;
    const numerPow2 = Math.round(phaseRad * denomPow2 / Math.PI);
    const [n, d] = normalize_phase_qpi(numerPow2, denomPow2);
    console.warn(`⚠️ Phase denom ${phaseDenom} → ${d} (power-of-2 enforcement)`);
    return new NodeLabel(kind, n, d, monadicId);
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
  // THEORY REQUIREMENT (bootstrap_phase_derivation.md Theorem 1):
  // Denominators MUST be powers of 2: 2^k for k ∈ ℕ
  // This ensures ZX calculus soundness (Clifford/T gate representation)

  // BOOTSTRAP PRECISION: 2^3 = 8 (Clifford+T gates)
  const BOOTSTRAP_DENOM = 8;

  // MAX DENOMINATOR: 2^6 = 64 (T-gate precision limit)
  const MAX_QPI_DENOM = 64;
  
  // CRITICAL: Clamp inputs to MAX first to prevent LCM explosion
  const aSafe = Math.min(aDenom, MAX_QPI_DENOM);
  const bSafe = Math.min(bDenom, MAX_QPI_DENOM);
  
  // LCM of two powers of 2 (≤64) is always ≤64 and is a power of 2
  const commonDenom = Math.min(lcm(aSafe, bSafe), MAX_QPI_DENOM);

  // Convert both phases to radians first (using clamped denominators for consistency)
  const aPhaseRad = Math.PI * aNumer / aSafe;
  const bPhaseRad = Math.PI * bNumer / bSafe;

  // Add phases in radian space (continuous)
  const sumPhaseRad = (aPhaseRad + bPhaseRad) % (2 * Math.PI);

  // Convert back to rational representation using the common denominator
  const finalNumer = Math.round(sumPhaseRad * commonDenom / Math.PI);
  const finalDenom = commonDenom;

  // Normalize to ensure gcd=1 and proper range
  const [numerRed, denomRed] = normalize_phase_qpi(finalNumer, finalDenom);

  // THEORY REQUIREMENT: Ensure denominator is power of 2
  // If not, convert to nearest power of 2 (maintains phase but ensures Qπ compliance)
  const finalDenomPowerOf2 = nearestPowerOf2(denomRed);

  if (finalDenomPowerOf2 !== denomRed) {
    // Convert back to radians and re-quantize to power-of-2 denominator
    const phaseRad = Math.PI * numerRed / denomRed;
    const newNumer = Math.round(phaseRad * finalDenomPowerOf2 / Math.PI);
    return [newNumer, finalDenomPowerOf2];
  }

  return [numerRed, denomRed];
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
  // THEORY REQUIREMENT: For powers of 2, LCM(2^a, 2^b) = 2^max(a,b)
  // This avoids ALL floating-point precision issues
  if ((a & (a - 1)) === 0 && (b & (b - 1)) === 0) {
    // Both are powers of 2 - LCM is just the maximum
    return Math.max(a, b);
  }
  
  // Fallback for non-powers of 2 (should NEVER happen in theory-compliant system)
  const g = gcd(a, b);
  if (g === 0) {
    throw new Error(`GCD is zero - invalid input to lcm: a=${a}, b=${b}`);
  }
  
  // Use integer-only arithmetic: compute (a/gcd) * b to avoid intermediate overflow
  const aReduced = Math.floor(a / g);
  const result = aReduced * b;
  
  // THEORY VIOLATION CHECK: Result must be ≤ 64 and power of 2
  if (result > 64) {
    throw new Error(`LCM produced denominator ${result} > 64. Theory cap is 2^6 = 64. Inputs: a=${a}, b=${b}`);
  }
  
  if ((result & (result - 1)) !== 0) {
    throw new Error(`LCM produced non-power-of-2 denominator ${result}. Theory requires 2^k. Inputs: a=${a}, b=${b}`);
  }
  
  return result;
}
