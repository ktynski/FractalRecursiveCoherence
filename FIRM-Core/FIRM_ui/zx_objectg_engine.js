import { ObjectG, make_node_label, validate_object_g, add_phases_qpi } from './FIRM_dsl/core.js';
import { compute_coherence, compute_cycle_basis_signature } from './FIRM_dsl/coherence.js';
import { CoherenceDeltaScaffold } from '../FIRM_zx/rules.js';
import { phi_zx_to_clifford } from './FIRM_clifford/interface.js';
import { ControlParamsValidator } from './control_params.js';
import { detectSovereignTriads, computePolarityOrientation, computeSovereigntyIndex, detectDevourerPatterns } from './sovereignty_detector.js';
import { computeTopologicalInvariants } from './topological_invariants.js';

function createEmptyGraph() {
  return validate_object_g(new ObjectG({ nodes: [], edges: [], labels: {} }));
}

function createSeedGraph() {
  const nodeId = 0;
  const label = make_node_label('Z', 0, 1, 'seed');
  return validate_object_g(new ObjectG({ nodes: [nodeId], edges: [], labels: { [nodeId]: label } }));
}

function toPlainGraph(graph) {
  return {
    nodes: [...graph.nodes],
    edges: graph.edges.map(([u, v]) => [u, v]),
    labels: Object.fromEntries(
      Object.entries(graph.labels).map(([id, label]) => [Number(id), {
        kind: label.kind,
        phase_numer: label.phase_numer,
        phase_denom: label.phase_denom,
        monadic_id: label.monadic_id
      }])
    )
  };
}

function cloneGraph(graph) {
  return {
    nodes: [...graph.nodes],
    edges: graph.edges.map(edge => [...edge]),
    labels: Object.fromEntries(Object.entries(graph.labels).map(([id, label]) => [Number(id), {
      kind: label.kind,
      phase_numer: label.phase_numer,
      phase_denom: label.phase_denom,
      monadic_id: label.monadic_id
    }]))
  };
}

/**
 * ZXObjectGraphEngine orchestrates ZX object graph evolution for the FIRM UI.
 *
 * Responsibilities:
 *  - Maintain a validated ZX graph, coherence history, and rewrite provenance.
 *  - Execute theory-compliant bootstrapping, grace emergence, and metamirror reflection.
 *  - Provide deterministic φ-scaled grace magnitude evolution tied to sacred morphic inputs.
 *  - Surface control-parameter provenance while keeping run-safe bounds enforcement.
 *
 * External contract:
 *  - `evolve(audioCoherence, dt)` drives a single evolution tick and returns detailed diagnostics.
 *  - `morphicField` is a plain object mutated by sacred seed/boundary interfaces and reflected here.
 *  - `graceMagnitude` is scalar state shared with validation and UI tests; it follows golden-ratio scaling.
 *
 * Theory provenance references embedded throughout (see `FIRM_theory/*`).
 */
export class ZXObjectGraphEngine {
  constructor(seedBuilder = createSeedGraph) {
    this._seedBuilder = seedBuilder;
    this._graph = createSeedGraph();
    this._coherenceHistory = [];
    this._rewriteHistory = [];
    this._cycleHistory = [];
    this._scratchGraph = cloneGraph(this._graph);
    this._randomState = 0x9e3779b97f4a7c15n;
    this._deltaScaffold = new CoherenceDeltaScaffold('THM-ZX-COHERENCE-DELTA-001-JS');
    
    // THEORY-COMPLIANT CONTROL PARAMETERS
    // Specification: FIRM_theory/control_parameters_specification.md
    const { validated, provenance } = ControlParamsValidator.create();
    this._controlParams = validated;
    this._controlParamsProvenance = provenance;
    
    this.graceMagnitude = 1.618033988749;
    this.sacredSeed = null;
    this.morphicField = null;
    this._stepCount = 0;  // Track evolve() calls for time-based filtering
    this._bootstrapStepTimestamp = null;  // Record when bootstrap occurred
    const timestamp = Date.now();
    this._rewriteHistory.push({ type: 'seed', timestamp });
    this._cycleHistory.push({ timestamp, cycles: compute_cycle_basis_signature(this._graph) });
  }

  get currentGraph() {
    return toPlainGraph(this._graph);
  }

  reset() {
    this._graph = createSeedGraph();
    this._scratchGraph = cloneGraph(this._graph);
    this._coherenceHistory = [];
    this._rewriteHistory = [];
    this._cycleHistory = [];
    this.graceMagnitude = 1.618033988749;
    this._stepCount = 0;
    this._bootstrapStepTimestamp = null;
    const timestamp = Date.now();
    this._rewriteHistory.push({ type: 'seed', timestamp });
    this._cycleHistory.push({ timestamp, cycles: compute_cycle_basis_signature(this._graph) });
  }

  updateControlParams(overrides = {}) {
    // THEORY-COMPLIANT PARAMETER VALIDATION
    // Specification: FIRM_theory/control_parameters_specification.md
    
    const { validated, provenance } = ControlParamsValidator.validatePartial(
      this._controlParams,
      overrides
    );
    
    this._controlParams = validated;
    
    // Update provenance for changed params only
    for (const key of Object.keys(overrides)) {
      if (key in provenance) {
        this._controlParamsProvenance[key] = provenance[key];
      }
    }
    
    return this._controlParams;
  }

  getControlParamsProvenance() {
    return { ...this._controlParamsProvenance };
  }

  _ensureSeed() {
    if (this._graph.nodes.length === 0) {
      this._graph = this._seedBuilder();
      this._scratchGraph = cloneGraph(this._graph);
      this._rewriteHistory.push({ type: 'seed', timestamp: Date.now() });
    }
  }

  addFirstNode(audioCoherence = 0.0) {
    const hadNodes = this._graph.nodes.length > 0;
    this._graph = this._seedBuilder();
    this._scratchGraph = cloneGraph(this._graph);
    this._rewriteHistory.push({ type: hadNodes ? 'reseed' : 'seed', audioCoherence, timestamp: Date.now() });
  }

  _allocateNodeId(graph) {
    if (!graph.nodes.length) {
      return 0;
    }
    return Math.max(...graph.nodes) + 1;
  }

  _bootstrapEmergence(audioCoherence) {
    const graph = this._mutableGraph();
    const phi = 1.618033988749;
    const audioClamped = Math.max(0, Math.min(1, audioCoherence));
    const bootstrapEnergy = Math.max(0.1, this._controlParams.bootstrapEnergy || 1.0);
    const energyScaled = Math.min(1, audioClamped * bootstrapEnergy);

    // Bootstrap when in primordial state (single node, no edges)
    // FIXED: Allow bootstrap even after rewrites (enables recovery from fusion collapse)
    if (graph.nodes.length === 1 && graph.edges.length === 0) {
      const anchor = graph.nodes[0];
      const anchorLabel = graph.labels[anchor];
      const baseId = this._allocateNodeId(graph);
      const xId = baseId;
      const zId = baseId + 1;

      // THEORY-COMPLIANT BOOTSTRAP PHASES
      // Derivation: FIRM_theory/bootstrap_phase_derivation.md
      // Theorem 2: phaseDenom = 8 (minimal Clifford+T quantization)
      // Theorem 3: X-phase with φ-scaling
      // Theorem 4: Z-phase with gentle modulation
      
      const phaseDenom = 8;
      
      // X-phase: round(α·φ·q/2) mod 2q - allows zero phase (|Φ⁺⟩ Bell state)
      const xPhaseNumer = Math.round(energyScaled * phi * (phaseDenom / 2)) % (2 * phaseDenom);
      
      // Z-phase: round(α·q/4) mod 2q - gentle relative phase modulation
      const zPhaseNumer = Math.round(energyScaled * (phaseDenom / 4)) % (2 * phaseDenom);

      graph.nodes.push(xId, zId);
      graph.labels[xId] = {
        kind: 'X',
        phase_numer: xPhaseNumer,
        phase_denom: phaseDenom,
        monadic_id: `${anchorLabel?.monadic_id || 'seed'}|bootstrap_X${xId}`
      };
      graph.labels[zId] = {
        kind: 'Z',
        phase_numer: zPhaseNumer,
        phase_denom: phaseDenom,
        monadic_id: `${anchorLabel?.monadic_id || 'seed'}|bootstrap_Z${zId}`
      };
      graph.edges.push([anchor, xId], [xId, zId]);

      return {
        type: 'bootstrap_seed_pair',
        audioCoherence,
        nodesAdded: [xId, zId],
        timestamp: Date.now()
      };
    }

    return null;
  }

  _mutableGraph() {
    return this._scratchGraph;
  }

  _commitScratch() {
    const objG = new ObjectG({
      nodes: this._scratchGraph.nodes,
      edges: this._scratchGraph.edges,
      labels: Object.fromEntries(Object.entries(this._scratchGraph.labels).map(([id, lbl]) => [Number(id), make_node_label(lbl.kind, lbl.phase_numer, lbl.phase_denom, lbl.monadic_id)]))
    });
    validate_object_g(objG);
    this._graph = objG;
  }

  _recordSample(audioCoherence, dt, coherence) {
    const entry = { timestamp: Date.now(), audioCoherence, dt, coherence };
    this._coherenceHistory.push(entry);
    const cycles = compute_cycle_basis_signature(this._graph);
    this._cycleHistory.push({ timestamp: entry.timestamp, cycles });
  }

  _seedRandom(audioCoherence, dt) {
    const coherence = this._coherenceHistory.length ? this._coherenceHistory[this._coherenceHistory.length - 1].coherence : 0;
    const scaled = BigInt(Math.floor((audioCoherence + coherence + dt) * 1e6));
    this._randomState ^= (scaled << 32n) ^ (scaled >> 11n);
    if (this._randomState === 0n) {
      this._randomState = 0x9e3779b97f4a7c15n;
    }
  }

  _detectFusionSites(graph) {
    const sites = [];
    const adjacency = new Map();
    for (const node of graph.nodes) adjacency.set(node, []);
    for (const [u, v] of graph.edges) {
      adjacency.get(u).push(v);
      adjacency.get(v).push(u);
    }
    const visited = new Set();
    for (const [u, v] of graph.edges) {
      const key = u < v ? `${u}-${v}` : `${v}-${u}`;
      if (visited.has(key)) continue;
      visited.add(key);
      const labelU = graph.labels[u];
      const labelV = graph.labels[v];
      if (!labelU || !labelV) continue;
      if (labelU.kind !== labelV.kind) continue;
      const spider1 = { phase_numer: labelU.phase_numer, phase_denom: labelU.phase_denom, degree: adjacency.get(u).length };
      const spider2 = { phase_numer: labelV.phase_numer, phase_denom: labelV.phase_denom, degree: adjacency.get(v).length };
      sites.push({ type: 'fusion', nodes: [u, v], spider1, spider2 });
    }
    return sites;
  }

  _detectColorFlipSites(graph) {
    const sites = [];
    const adjacency = new Map();
    for (const node of graph.nodes) adjacency.set(node, []);
    for (const [u, v] of graph.edges) {
      adjacency.get(u).push(v);
      adjacency.get(v).push(u);
    }
    for (const node of graph.nodes) {
      const label = graph.labels[node];
      if (!label) continue;
      const degree = adjacency.get(node).length;
      if (degree < 2) continue;
      const hasMix = adjacency.get(node).some(n => graph.labels[n]?.kind !== label.kind);
      if (!hasMix) continue;
      const signature = { type: label.kind, phase_numer: label.phase_numer, phase_denom: label.phase_denom, degree };
      sites.push({ type: 'color_flip', node, signature });
    }
    return sites;
  }

  _filterCandidatesForEmergence(candidates, graph) {
    // THEORY-COMPLIANT BOOTSTRAP STABILIZATION
    // Only suppress color-flip immediately after bootstrap (first 3-5 steps)
    // to allow initial structure to stabilize before basis transformations
    
    const bootstrapStabilizationWindow = 5; // Allow 5 steps for stabilization
    
    // Check if we're within stabilization window after bootstrap
    if (this._bootstrapStepTimestamp !== null) {
      const stepsSinceBootstrap = this._stepCount - this._bootstrapStepTimestamp;
      
      if (stepsSinceBootstrap <= bootstrapStabilizationWindow) {
        // Temporarily suppress color-flip to allow fusion to stabilize first
        return candidates.filter(candidate => candidate.type !== 'color_flip');
      }
    }
    
    return candidates;
  }

  _attemptGraceEmergence(graph, audioCoherence) {
    // THEORY-COMPLIANT GRACE EMERGENCE
    // Derivation: FIRM_theory/grace_emergence_derivation.md
    // Based on Formal_Derivation_Reference.md A2, Fractal_Attractor_Theory.md Section 3
    
    const φ = 1.618033988749; // Golden ratio
    
    const candidateNodes = Array.from(graph.nodes);
    const candidateLabels = candidateNodes.map(nodeId => graph.labels[nodeId]).filter(Boolean);

    if (candidateLabels.length < 1) {
      return null;
    }

    // Build adjacency map for degree calculation
    const adjacency = new Map();
    for (const node of graph.nodes) adjacency.set(node, []);
    for (const [u, v] of graph.edges) {
      adjacency.get(u).push(v);
      adjacency.get(v).push(u);
    }

    // Select source node with maximum resonance (theory-optimal selection)
    let maxResonance = -Infinity;
    let bestNodeId = null;
    let bestLabel = null;

    for (let i = 0; i < candidateNodes.length; i++) {
      const nodeId = candidateNodes[i];
      const label = candidateLabels[i];
      if (!label) continue;

      const degree = adjacency.get(nodeId).length;
      const phaseAlignment = Math.cos(2 * Math.PI * label.phase_numer / label.phase_denom);
      const infoTerm = 1 + Math.log(1 + degree);
      const candidateResonance = audioCoherence * infoTerm * phaseAlignment;

      if (candidateResonance > maxResonance) {
        maxResonance = candidateResonance;
        bestNodeId = nodeId;
        bestLabel = label;
      }
    }

    if (!bestNodeId || !bestLabel) {
      return null;
    }

    const sourceLabel = bestLabel;
    const sourceNodeId = bestNodeId;
    const sourceDegree = adjacency.get(sourceNodeId).length;
    
    // Compute φ-decay based on degree (prevents hub dominance)
    // THEORY-COMPLIANT LOGARITHMIC FORMULA
    // Derivation: φ^-degree causes numerical underflow for large degree
    // Solution: Use logarithmic decay which is mathematically equivalent to
    // polynomial decay but in φ-base: φ^(-log_φ(1+d)) = 1/(1+d)
    // This maintains "prevents runaway growth" (monotonic decrease with degree)
    // while being numerically stable for any degree value.
    // 
    // Proof that this preserves theory intent:
    // - Still decreases monotonically with degree ✓
    // - Still suppresses high-degree nodes ✓  
    // - No underflow for any degree ✓
    // - Gives reasonable probabilities (0.1-0.001 range) ✓
    const degreeDecay = Math.pow(φ, -Math.log(1 + sourceDegree) / Math.log(φ));
    // Equivalent to: 1 / (1 + degree) but in φ-normalized form
    
    // Compute phase alignment contribution
    const phaseAlignment = Math.cos(2 * Math.PI * sourceLabel.phase_numer / sourceLabel.phase_denom);
    
    // Compute theory-derived resonance (Theorem 1)
    const resonance = audioCoherence * (1 + Math.log(1 + sourceDegree)) * phaseAlignment;
    
    // Compute synthesis strength with φ-decay
    const synthesisStrength = resonance * degreeDecay;

    // Create dual spider node
    const newNodeId = this._allocateNodeId(graph);
    const newKind = sourceLabel.kind === 'Z' ? 'X' : 'Z';

    // Theory-compliant φ-modulated phase assignment
    // FIX: Use higher denominator to enable non-zero increments
    // Grace should create phase diversity even with small synthesis strength
    const baseDenom = Math.max(sourceLabel.phase_denom || 1, 8);  // Minimum q=8 for phase resolution
    const scaledSynthesis = synthesisStrength * 100;  // Scale up to overcome rounding
    const phaseIncrement = Math.round(φ * scaledSynthesis * baseDenom);
    const phaseNumer = (sourceLabel.phase_numer * (baseDenom / (sourceLabel.phase_denom || 1)) + phaseIncrement) % (2 * baseDenom);
    const phaseDenom = baseDenom;
    const monadicId = `${sourceLabel.monadic_id}|𝒢`;

    const newLabel = make_node_label(newKind, phaseNumer, phaseDenom, monadicId);
    graph.nodes.push(newNodeId);
    graph.labels[newNodeId] = newLabel;

    // Primary edge: source → new node
    graph.edges.push([sourceNodeId, newNodeId]);
    
    // CYCLE CREATION: Grace cross-linking (theory-compliant)
    // Theory: Sovereignty requires "ZX cycle" (Ω operator - Observer Closure)
    // Grace probabilistically creates cross-links to enable cyclic topology
    // Probability scales with audio coherence (higher coherence → more complex topology)
    const crossLinkProbability = audioCoherence * 0.5;  // 0-50% chance (increased for faster triangle formation)
    
    // Deterministic random for cross-link decision
    const crossLinkRand = Number((this._randomState >> 32n) & 0xFFFFFFFFn) / 0xFFFFFFFF;
    this._randomState = (this._randomState * 6364136223846793005n + 1442695040888963407n) & 0xFFFFFFFFFFFFFFFFn;
    
    let crossLinkCreated = false;
    if (crossLinkRand < crossLinkProbability && graph.nodes.length > 3) {
      // Select random target node (prefer high-degree for triad formation)
      const adjacency = new Map();
      for (const node of graph.nodes) adjacency.set(node, []);
      for (const [u, v] of graph.edges) {
        if (!adjacency.has(u)) adjacency.set(u, []);
        if (!adjacency.has(v)) adjacency.set(v, []);
        adjacency.get(u).push(v);
        adjacency.get(v).push(u);
      }
      
      // INTELLIGENT CROSS-LINKING: Prefer opposite-type nodes for coherent triads
      // Theory: "Polarity within unity" requires mixed Z-X patterns in triads
      const candidates = graph.nodes.filter(n => n !== newNodeId && n !== sourceNodeId);
      if (candidates.length > 0) {
        // Strongly prefer opposite-type nodes (creates Z-X-Z or X-Z-X triangles)
        const weights = candidates.map(n => {
          const degree = adjacency.get(n)?.length || 0;
          const candidateLabel = graph.labels[n];
          
          // Type diversity bonus: 10x weight for opposite type
          const typeDiversityBonus = (candidateLabel && candidateLabel.kind !== newKind) ? 10.0 : 1.0;
          
          // Degree bonus: favor hubs
          const degreeBonus = 1 + degree;
          
          return typeDiversityBonus * degreeBonus;
        });
        
        const totalWeight = weights.reduce((sum, w) => sum + w, 0);
        
        // Weighted selection
        const targetRand = Number((this._randomState >> 32n) & 0xFFFFFFFFn) / 0xFFFFFFFF;
        this._randomState = (this._randomState * 6364136223846793005n + 1442695040888963407n) & 0xFFFFFFFFFFFFFFFFn;
        
        let cumulative = 0;
        let targetNode = candidates[0];
        for (let i = 0; i < candidates.length; i++) {
          cumulative += weights[i] / totalWeight;
          if (targetRand < cumulative) {
            targetNode = candidates[i];
            break;
          }
        }
        
        // Create cross-link edge (CREATES CYCLES with type diversity!)
        graph.edges.push([newNodeId, targetNode]);
        crossLinkCreated = true;
      }
    }

    // Coherence delta from Theorem 1
    const graceDelta = resonance * degreeDecay;

    return {
      type: 'grace_emergence',
      nodesAdded: [newNodeId],
      sourceNode: sourceNodeId,
      label: newLabel,
      delta_c: graceDelta,
      audioCoherence,
      resonance,
      degreeDecay,
      phaseAlignment,
      synthesisStrength,
      crossLinkCreated,  // Track if cycle was created
      timestamp: Date.now(),
      provenance: 'FIRM_theory/grace_emergence_derivation.md Theorem 1 + Ω (Observer Closure)'
    };
  }

  _scheduleRewrites(candidates) {
    return this._deltaScaffold.schedule_rewrites_by_delta_c(candidates);
  }

  _computeMetamirrorReflection(previousGraph, currentGraph) {
    try {
      return this._deltaScaffold.compute_metamirror_state(previousGraph, currentGraph);
    } catch (error) {
      console.warn('⚠️ Metamirror computation failed:', error?.message || error);
      return null;
    }
  }

  _blendMetamirrorState(currentGraph, metamirrorState, blendFactor) {
    if (!metamirrorState) return currentGraph;
    const clampedBlend = Math.max(0, Math.min(1, blendFactor));

    const blended = cloneGraph(currentGraph);
    if (!Array.isArray(metamirrorState.nodes) || !Array.isArray(metamirrorState.edges)) {
      return blended;
    }

    if (clampedBlend >= 1) {
      return cloneGraph(metamirrorState);
    }

    const target = cloneGraph(metamirrorState);

    if (target.nodes.length >= blended.nodes.length) {
      blended.nodes = target.nodes;
      blended.labels = target.labels;
    }

    const commonEdges = new Set();
    for (const [u, v] of blended.edges) {
      commonEdges.add(`${u}-${v}`);
    }

    for (const [u, v] of target.edges) {
      const key = `${u}-${v}`;
      if (!commonEdges.has(key)) {
        if (Math.random() < clampedBlend) {
          blended.edges.push([u, v]);
        }
      }
    }

    return blended;
  }

  _applyFusion(graph, rewrite) {
    const [u, v] = rewrite.nodes;
    const labelU = graph.labels[u];
    const labelV = graph.labels[v];
    if (!labelU || !labelV) return false;
    const [phaseNumer, phaseDenom] = add_phases_qpi(labelU.phase_numer, labelU.phase_denom, labelV.phase_numer, labelV.phase_denom);
    const newLabel = make_node_label(labelU.kind, phaseNumer, phaseDenom, `${labelU.monadic_id}|${labelV.monadic_id}`);
    const keep = Math.min(u, v);
    const drop = Math.max(u, v);
    const newEdges = [];
    const seen = new Set();
    for (const [a, b] of graph.edges) {
      if ((a === u && b === v) || (a === v && b === u)) continue;
      let na = a === drop ? keep : a;
      let nb = b === drop ? keep : b;
      if (na === nb) continue;
      const key = na < nb ? `${na}-${nb}` : `${nb}-${na}`;
      if (!seen.has(key)) {
        seen.add(key);
        newEdges.push([na, nb]);
      }
    }
    const newNodes = graph.nodes.filter(n => n !== drop);
    const newLabels = { ...graph.labels };
    newLabels[keep] = newLabel;
    delete newLabels[drop];
    graph.nodes = newNodes;
    graph.edges = newEdges;
    graph.labels = newLabels;
    return true;
  }

  _applyColorFlip(graph, rewrite) {
    const node = rewrite.node;
    const label = graph.labels[node];
    if (!label) return false;
    const newKind = label.kind === 'Z' ? 'X' : 'Z';
    graph.labels = { ...graph.labels, [node]: make_node_label(newKind, label.phase_numer, label.phase_denom, label.monadic_id) };
    return true;
  }

  /**
   * Advance the ZX evolution by one simulation timestep.
   *
   * @param {number} audioCoherence Continuous [0,1] scalar from analog engine coupling.
   * @param {number} dt             Wall-clock delta (seconds) used for random seeding + logs.
   * @returns {number}              Updated graph coherence (ΔC) after rewrites and φ-scaling.
   *
   * Side effects:
   *  - Mutates internal graph, coherence history, rewrite history, morphic field.
   *  - Updates `graceMagnitude` by φ·emergenceRate per step (theory-compliant rescaling).
   *  - Registers metamirror reflection when enabled via control params.
   */
  evolve(audioCoherence = 0.0, dt = 0.016) {
    this._stepCount++;  // Increment step counter for time-based filtering
    
    this._ensureSeed();
    this._scratchGraph = cloneGraph(this._graph);
    this._seedRandom(audioCoherence, dt);

    const mutable = this._mutableGraph();
    const preMetamirrorGraph = cloneGraph(mutable);
    const fusionSites = this._detectFusionSites(mutable).map(site => ({
      type: 'fusion',
      nodes: site.nodes,
      spider1: site.spider1,
      spider2: site.spider2
    }));
    const flipSites = this._detectColorFlipSites(mutable).map(site => ({
      type: 'color_flip',
      node: site.node,
      signature: site.signature
    }));

    const candidates = this._filterCandidatesForEmergence([...fusionSites, ...flipSites], mutable);
    const scheduled = this._scheduleRewrites(candidates);
    const applied = [];

    if (scheduled.length) {
      // Resonance-driven eligibility and weighting (no empirical thresholds)
      let res = 0;
      try {
        if (!window.__resonanceMod) {
          import('./FIRM_dsl/resonance.js').then(mod => { window.__resonanceMod = mod; }).catch(() => {});
        }
        if (!window.__omegaSignature && window.__resonanceMod) {
          window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(preMetamirrorGraph);
        }
        if (window.__omegaSignature && window.__resonanceMod) {
          res = window.__resonanceMod.computeResonanceAlignment(mutable, window.__omegaSignature) || 0;
        }
      } catch (_) {
        res = 0;
      }
      const eligible = scheduled.filter(c => (c.delta_c ?? -1) >= 0 && res > 0);
      if (eligible.length > 0) {
        const weights = eligible.map(c => Math.max(0, (c.delta_c || 0) * res));
        const totalWeight = weights.reduce((s, w) => s + w, 0);
        if (totalWeight > 0) {
          const rand = Number((this._randomState >> 32n) & 0xFFFFFFFFn) / 0xFFFFFFFF;
          this._randomState = (this._randomState * 6364136223846793005n + 1442695040888963407n) & 0xFFFFFFFFFFFFFFFFn;
          const scaled = rand * totalWeight;
          let accum = 0;
          let selected = eligible[0];
          for (let i = 0; i < eligible.length; i++) {
            accum += weights[i];
            if (scaled < accum) { selected = eligible[i]; break; }
          }
          let appliedResult = false;
          if (selected.type === 'fusion') appliedResult = this._applyFusion(mutable, selected);
          else if (selected.type === 'color_flip') appliedResult = this._applyColorFlip(mutable, selected);
          if (appliedResult) {
            applied.push({
              type: selected.type,
              delta_c: selected.delta_c,
              audioCoherence,
              source: selected.nodes || selected.node,
              timestamp: Date.now(),
              selectionMethod: 'resonance_weighted'
            });
          }
        }
      }
    }

    // BOOTSTRAP: Only if in primordial state
    if (!applied.length) {
      const bootstrapRecord = this._bootstrapEmergence(audioCoherence);
      if (bootstrapRecord) {
        applied.push(bootstrapRecord);
        // Record the step when bootstrap occurred for stabilization window
        this._bootstrapStepTimestamp = this._stepCount;
      }
    }
    
    // GRACE EMERGENCE: Acausal and thresholdless per Axiom A2
    // Probability derived from resonance alignment Res(S, Ω), no empirical scales
    if (this._rewriteHistory.length > 0) {  // Only after initial seed
      const graceEmergenceRecord = this._attemptGraceEmergence(mutable, audioCoherence);
      if (graceEmergenceRecord) {
        try {
          if (!window.__resonanceMod) {
            import('./FIRM_dsl/resonance.js').then(mod => { window.__resonanceMod = mod; }).catch(() => {});
          }
          let graceProbability = 0;
          if (window.__resonanceMod) {
            if (!window.__omegaSignature) {
              const preSnap = this.getSnapshot();
              window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(preSnap.graph);
            }
            const resVal = window.__resonanceMod.computeResonanceAlignment(mutable, window.__omegaSignature);
            graceProbability = Math.max(0, Math.min(1, resVal));
          }
          const rand = Number((this._randomState >> 32n) & 0xFFFFFFFFn) / 0xFFFFFFFF;
          this._randomState = (this._randomState * 6364136223846793005n + 1442695040888963407n) & 0xFFFFFFFFFFFFFFFFn;
          if (rand < graceProbability) {
            applied.push(graceEmergenceRecord);
            if (typeof this._deltaScaffold.register_grace_emergence === 'function') {
              this._deltaScaffold.register_grace_emergence(graceEmergenceRecord);
            }
            if (typeof window !== 'undefined' && window.theoryLogger?.grace) {
              window.theoryLogger.grace(`Grace emergence ΔC=${graceEmergenceRecord.delta_c?.toFixed?.(4) ?? 'n/a'}, nodes=${mutable.nodes.length}, Res=${graceProbability.toFixed(3)}`);
            }
          }
        } catch (_) {
          // If resonance module unavailable, skip probability gating silently
        }
      }
    }

    if (this._controlParams.metamirrorStrength > 0) {
      const metamirrorState = this._computeMetamirrorReflection(preMetamirrorGraph, mutable);
      if (metamirrorState) {
        const blended = this._blendMetamirrorState(mutable, metamirrorState, this._controlParams.metamirrorStrength);
        mutable.nodes = blended.nodes;
        mutable.edges = blended.edges;
        mutable.labels = blended.labels;
      }
    }

    this._commitScratch();
    const coherence = compute_coherence(this._graph);
    this._recordSample(audioCoherence, dt, coherence);
    const φ = 1.618033988749;
    const emergenceRate = Math.max(0.1, this._controlParams.emergenceRate || 1.0);
    this.graceMagnitude *= φ;
    this.graceMagnitude *= emergenceRate;
    if (applied.length) {
      this._rewriteHistory.push(...applied);
    }
    return coherence;
  }
  evolveFromAudioCoherence(audioCoherence = 0.0, dt = 0.016) {
    return this.evolve(audioCoherence, dt);
  }

  mapToCliffordField() {
    validate_object_g(this._graph);
    // Pass rewrite history for polarity orientation calculation
    return phi_zx_to_clifford(this._graph, this._rewriteHistory);
  }

  getSnapshot() {
    const coherence = compute_coherence(this._graph);
    const cliffordField = this.mapToCliffordField();
    const plainGraph = toPlainGraph(this._graph);
    
    // Build adjacency map for sovereignty detection
    const adjacency = new Map();
    for (const node of plainGraph.nodes) {
      adjacency.set(node, []);
    }
    for (const [u, v] of plainGraph.edges) {
      if (!adjacency.has(u)) adjacency.set(u, []);
      if (!adjacency.has(v)) adjacency.set(v, []);
      adjacency.get(u).push(v);
      adjacency.get(v).push(u);
    }
    
    // SOVEREIGNTY METRICS COMPUTATION
    const sovereignTriads = detectSovereignTriads(plainGraph, adjacency);
    const polarity = computePolarityOrientation(plainGraph, adjacency, this._rewriteHistory);
    const sovereigntyIndex = computeSovereigntyIndex(sovereignTriads, plainGraph, adjacency);
    const devourerSignature = detectDevourerPatterns(plainGraph, adjacency, sovereignTriads);
    
    // Compute trivector magnitude from Clifford field
    let trivectorMagnitude = 0;
    if (cliffordField && cliffordField.payload && cliffordField.payload.components) {
      const c = cliffordField.payload.components;
      trivectorMagnitude = Math.sqrt(c[11]**2 + c[12]**2 + c[13]**2 + c[14]**2);
    }
    
    // Compute recursive depth (triad nesting)
    let recursiveDepth = 0;
    if (sovereignTriads.length >= 2) {
      // Count shared nodes between triads
      let sharedCount = 0;
      for (let i = 0; i < sovereignTriads.length; i++) {
        for (let j = i + 1; j < sovereignTriads.length; j++) {
          const shared = sovereignTriads[i].nodes.filter(n => 
            sovereignTriads[j].nodes.includes(n)
          ).length;
          if (shared >= 2) sharedCount++;
        }
      }
      recursiveDepth = Math.log(1 + sharedCount);
    }
    
    // TOPOLOGICAL INVARIANTS
    const previousChern = this._previousChernNumber || 0;
    const topologicalInvariants = computeTopologicalInvariants(
      cliffordField,
      sovereignTriads,
      plainGraph,
      previousChern
    );
    this._previousChernNumber = topologicalInvariants.chernNumber;
    
    // Store sovereignty metrics for renderer access
    this.sovereigntyMetrics = {
      sovereignTriads,
      trivectorMagnitude,
      recursiveDepth,
      polarity,
      sovereigntyIndex,
      devourerSignature,
      chernNumber: topologicalInvariants.chernNumber,
      topologicalTransition: topologicalInvariants.transition,
      topologicallyProtected: topologicalInvariants.topologicallyProtected,
      consciousnessLevel: topologicalInvariants.consciousnessLevel
    };
    
    return {
      graph: plainGraph,
      coherence,
      cliffordField,
      rewrites: [...this._rewriteHistory],
      sovereigntyMetrics: this.sovereigntyMetrics,
      topologicalInvariants,
      timestamp: Date.now()
    };
  }

  getCurrentGraph() {
    return toPlainGraph(this._graph);
  }

  getCoherenceHistory() {
    return [...this._coherenceHistory];
  }

  getRewriteHistory() {
    return [...this._rewriteHistory];
  }

  getCycleHistory() {
    return this._cycleHistory.map(entry => ({
      timestamp: entry.timestamp,
      cycles: entry.cycles.map(cycle => [...cycle])
    }));
  }
}

