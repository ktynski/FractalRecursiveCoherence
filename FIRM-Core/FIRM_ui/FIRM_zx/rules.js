const DEFAULT_PROOF_ID = 'THM-ZX-COHERENCE-DELTA-001-JS';

function validateSignatureDict(name, sig) {
  if (typeof sig !== 'object' || sig === null) {
    throw new Error(`${name} signature must be a dictionary`);
  }
}

function isFiniteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
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

export class CoherenceDeltaScaffold {
  constructor(proofId = DEFAULT_PROOF_ID) {
    this.proof_id = proofId;
  }

  validate_delta_computation_structure(preSignature, postSignature) {
    validateSignatureDict('pre', preSignature);
    validateSignatureDict('post', postSignature);

    const pre_cycles = preSignature?.cycles ?? 0;
    const pre_nodes = preSignature?.nodes ?? 0;
    const post_cycles = postSignature?.cycles ?? 0;
    const post_nodes = postSignature?.nodes ?? 0;

    return {
      delta_cycles: post_cycles - pre_cycles,
      delta_nodes: post_nodes - pre_nodes,
      coherence_terms_affected: Math.abs(post_cycles - pre_cycles) + Math.abs(post_nodes - pre_nodes),
      computation_valid: true,
      proof_id: this.proof_id
    };
  }

  compute_fusion_delta_c(spider1Signature, spider2Signature) {
    validateSignatureDict('spider1', spider1Signature);
    validateSignatureDict('spider2', spider2Signature);

    const phase1_n = spider1Signature.phase_numer ?? 0;
    const phase1_d = spider1Signature.phase_denom ?? 1;
    const phase2_n = spider2Signature.phase_numer ?? 0;
    const phase2_d = spider2Signature.phase_denom ?? 1;
    const deg1 = spider1Signature.degree ?? 0;
    const deg2 = spider2Signature.degree ?? 0;

    const phase1_rad = Math.PI * phase1_n / phase1_d;
    const phase2_rad = Math.PI * phase2_n / phase2_d;
    const phase_diff = Math.abs(phase1_rad - phase2_rad);
    const phase_alignment = Math.cos(phase_diff);

    const connectivity_gain = Math.log(1 + deg1 + deg2) - Math.log(1 + deg1) - Math.log(1 + deg2);

    const combined_denom = gcd(phase1_d, phase2_d);
    const simplification_gain = 1.0 / combined_denom - 1.0 / phase1_d - 1.0 / phase2_d;

    return phase_alignment + connectivity_gain + simplification_gain;
  }

  compute_color_flip_delta_c(signature) {
    validateSignatureDict('bialgebra', signature);

    const spider_type = signature.type;
    if (spider_type !== 'Z' && spider_type !== 'X') {
      throw new Error('Spider type must be Z or X');
    }

    const phase_numer = signature.phase_numer ?? 0;
    const phase_denom = signature.phase_denom ?? 1;
    const degree = signature.degree ?? 0;

    const phase_rad = Math.PI * phase_numer / phase_denom;
    const phase_stability = Math.cos(2 * phase_rad);
    const degree_impact = Math.log(1 + degree);
    const type_factor = spider_type === 'Z' ? 1.0 : -1.0;

    return type_factor * phase_stability * degree_impact;
  }

  compute_grace_resonance(spiderSignature, synthesisStrength) {
    validateSignatureDict('grace_spider', spiderSignature);

    const kind = spiderSignature.kind;
    const phase_numer = spiderSignature.phase_numer ?? 0;
    const phase_denom = spiderSignature.phase_denom ?? 1;
    const degree = spiderSignature.degree ?? 0;

    const phase_rad = Math.PI * phase_numer / Math.max(1, phase_denom);
    const alignment = Math.cos(phase_rad);
    const degreeFactor = Math.log(1 + degree * 0.5);
    const kindFactor = kind === 'Z' ? 1.0 : 0.85;

    return kindFactor * (alignment + degreeFactor) * Math.max(0.01, synthesisStrength);
  }

  compute_grace_delta_c({ kind, phase_numer, phase_denom, source_phase_numer, source_phase_denom, new_nodes, old_nodes }) {
    const φ = 1.618033988749;

    const phaseRad = Math.PI * phase_numer / Math.max(1, phase_denom);
    const sourcePhaseRad = Math.PI * source_phase_numer / Math.max(1, source_phase_denom);
    const phaseAlignment = Math.cos(phaseRad - sourcePhaseRad);
    const kindFactor = kind === 'Z' ? 1.0 : 0.85;

    return phaseAlignment * kindFactor * (new_nodes - old_nodes * φ);
  }

  register_grace_emergence(event) {
    console.log('ΔC(grace) =', event.delta_c, 'nodes=', event.nodesAdded, 'φ-scale=', 1.618033988749);
  }

  compute_grace_projection(nodes) {
    const φ = 1.618033988749;
    return nodes * φ;
  }

  _computeDeltaForCandidate(candidate) {
    if (isFiniteNumber(candidate.delta_c)) {
      return candidate.delta_c;
    }
    if (candidate.type === 'fusion') {
      return this.compute_fusion_delta_c(candidate.spider1, candidate.spider2);
    }
    if (candidate.type === 'color_flip') {
      return this.compute_color_flip_delta_c(candidate.signature);
    }
    return Number.NaN;
  }

  schedule_rewrites_by_delta_c(candidateRewrites) {
    if (!Array.isArray(candidateRewrites)) {
      throw new Error('candidate_rewrites must be a list');
    }

    const annotated = candidateRewrites.map(candidate => {
      try {
        const delta_c = this._computeDeltaForCandidate(candidate);
        return { ...candidate, delta_c };
      } catch (error) {
        console.warn('⚠️ Failed to compute ΔC for candidate', candidate, error);
        return { ...candidate, delta_c: Number.NaN };
      }
    });

    return annotated
      .filter(candidate => isFiniteNumber(candidate.delta_c))
      .sort((a, b) => b.delta_c - a.delta_c);
  }
}

export default CoherenceDeltaScaffold;
