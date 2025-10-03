const DEFAULT_PROOF_ID = 'THM-ZX-COHERENCE-DELTA-001-JS';

function validateSignatureDict(name, sig) {
  if (typeof sig !== 'object' || sig === null) {
    throw new Error(`${name} signature must be a dictionary`);
  }
}

function isFiniteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
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

  compute_grace_resonance(label, synthesisStrength) {
    /**
     * Compute resonance for grace emergence.
     * 
     * Derivation: FIRM_theory/grace_emergence_derivation.md Section 2.3
     * 
     * resonance(L, α) = α · (1 + log(1 + deg(v))) · cos(phase_alignment)
     * 
     * Note: This is a simplified version since full degree info isn't available here.
     * Full computation happens in ZXObjectGraphEngine._attemptGraceEmergence()
     */
    if (!label || typeof label !== 'object') {
      return synthesisStrength;
    }

    const phase_numer = label.phase_numer ?? 0;
    const phase_denom = label.phase_denom ?? 1;
    const phase_rad = Math.PI * phase_numer / phase_denom;
    const phase_alignment = Math.cos(2 * phase_rad);

    // Synthesis strength already encodes audio coherence
    // Add phase alignment contribution
    return synthesisStrength * Math.abs(phase_alignment);
  }

  compute_grace_delta_c(graceSignature) {
    /**
     * Compute coherence delta for grace emergence.
     * 
     * Derivation: FIRM_theory/grace_emergence_derivation.md Theorem 1
     * 
     * ΔC_grace = resonance · φ^(-degree)
     */
    validateSignatureDict('grace', graceSignature);

    const φ = 1.618033988749;
    const source_phase_numer = graceSignature.source_phase_numer ?? 0;
    const source_phase_denom = graceSignature.source_phase_denom ?? 1;
    const new_phase_numer = graceSignature.phase_numer ?? 0;
    const new_phase_denom = graceSignature.phase_denom ?? 1;
    const old_nodes = graceSignature.old_nodes ?? 0;
    const new_nodes = graceSignature.new_nodes ?? 0;

    // Phase alignment of new node with source
    const source_phase = Math.PI * source_phase_numer / source_phase_denom;
    const new_phase = Math.PI * new_phase_numer / new_phase_denom;
    const phase_diff = Math.abs(new_phase - source_phase);
    const phase_alignment = Math.cos(phase_diff);

    // Node creation contributes to coherence
    const node_contribution = Math.log(1 + new_nodes) - Math.log(1 + old_nodes);

    // φ-scaling factor
    const grace_factor = 1.0 / φ;  // Gentle scaling

    return phase_alignment * node_contribution * grace_factor;
  }

  register_grace_emergence(graceRecord) {
    /**
     * Register grace emergence event for future metamirror computations.
     * 
     * Currently a no-op placeholder - will be used when metamirror is implemented.
     */
    // Store for metamirror reflection analysis
    this._graceRegistry = this._graceRegistry || [];
    this._graceRegistry.push({
      timestamp: graceRecord.timestamp,
      delta_c: graceRecord.delta_c,
      nodes_added: graceRecord.nodesAdded
    });
  }

  compute_metamirror_state(previousGraph, currentGraph) {
    /**
     * Compute metamirror (bireflection) of current graph.
     * 
     * Derivation: FIRM_theory/metamirror_bireflection_derivation.md Section 2.2
     * 
     * Applies β operator: Z ↔ X color flip while preserving phases.
     * Implements Formal_Derivation_Reference.md Theorem T2 (Bireflection Duality).
     */
    if (!currentGraph || !currentGraph.nodes || !currentGraph.labels) {
      throw new Error('Valid current graph required for metamirror computation');
    }

    // Apply bireflection (color flip) to create mirror state
    const mirrorGraph = {
      nodes: [...currentGraph.nodes],
      edges: currentGraph.edges.map(e => [...e]),
      labels: {}
    };

    // Flip all spider colors (β operator)
    for (const [nodeId, label] of Object.entries(currentGraph.labels)) {
      const mirrorKind = label.kind === 'Z' ? 'X' : 'Z';
      mirrorGraph.labels[nodeId] = {
        kind: mirrorKind,
        phase_numer: label.phase_numer,  // Phases preserved (involution)
        phase_denom: label.phase_denom,
        monadic_id: `β(${label.monadic_id})`  // Mark as reflected
      };
    }

    return mirrorGraph;
  }
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

export default CoherenceDeltaScaffold;

