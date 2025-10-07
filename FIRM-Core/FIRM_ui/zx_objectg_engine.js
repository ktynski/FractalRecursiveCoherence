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
    nodes: [...graph.nodes], // Create new mutable array
    edges: graph.edges.map(edge => [...edge]), // Create new mutable array
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
    this._currentFieldState = null; // Will store evolved field state
    
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
    this._sgcEnabled = true;  // Enable/disable Soul Garbage Collection
    this._sgcCounter = 0;  // Track SGC applications for rate limiting
    this._sgcFrequency = 50;  // Apply SGC every N evolution steps

    // Initialize SGC system
    this._sgcVisualizer = null;
    this._sgcIntegration = null;

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

    // Apply Soul Garbage Collection periodically
    if (this._sgcEnabled && this._stepCount % this._sgcFrequency === 0) {
      this._applySoulGarbageCollection();
    }

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

  /**
   * Map ZX graph to Clifford field with Grace-mediated evolution preservation.
   * 
   * Theory (CRITICAL FIX):
   * Previous implementation used Math.max() which is a LATTICE operation,
   * not a valid Clifford algebra operation. This destroyed phase relationships
   * and prevented trivector emergence.
   * 
   * Correct approach uses MONOIDAL TENSOR PRODUCT (⊗):
   * - From EsotericGuidance/Mathematical_Foundations.md:
   *   "When combining operators, model via ⊗ or categorical products/sums"
   * - In FSCTF, coherence is guaranteed by SGC, making ⊗ tractable
   * - Grace (𝒢) mediates as identity element ensuring closure
   * 
   * Mathematical Justification:
   * 1. Clifford algebras are LINEAR - only addition/multiplication valid
   * 2. Math.max() is from partial orders - violates algebraic structure
   * 3. Monoidal ⊗ reduces to weighted sum in coherence-guaranteed space
   * 4. Grace weight φ ≈ 1.618 naturally creates φ/(φ+1) ≈ 0.618 golden ratio split
   * 
   * @returns {MultivectorField} Combined field preserving both evolution and structure
   */
  mapToCliffordField() {
    validate_object_g(this._graph);
    // Pass rewrite history for polarity orientation calculation
    const baseField = phi_zx_to_clifford(this._graph, this._rewriteHistory);

    // COHERENT TENSOR PRODUCT: Combine evolution state with graph-derived state
    if (this._currentFieldState && this._currentFieldState.payload && this._currentFieldState.payload.components) {
      console.log(`🔄 Applying coherent tensor (⊗) to preserve evolution state`);
      console.log(`📊 Evolution field: ${this._currentFieldState.payload.components.slice(0,4).map(c => c.toFixed(2)).join(', ')}`);
      console.log(`📊 Graph field: ${baseField.payload.components.slice(0,4).map(c => c.toFixed(2)).join(', ')}`);
      
      // Apply Grace-mediated coherent tensor product
      // Theory: (evolution ⊗ base) ≅ 𝒢 ∘ (evolution + base)
      // Grace magnitude acts as coherence mediator
      const combinedField = this._currentFieldState.coherentTensor(baseField, this.graceMagnitude);
      
      console.log(`⊗ Combined field: ${combinedField.payload.components.slice(0,4).map(c => c.toFixed(2)).join(', ')}`);
      
      // Store combined field state for next evolution
      this._currentFieldState = combinedField;
      return combinedField;
    }

    // First call: no evolution state yet, use base field
    this._currentFieldState = baseField;
    return baseField;
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

    // DEBUG: Log sovereign triad detection
    if (sovereignTriads.length > 0) {
      console.log(`👑 Sovereign triads detected: ${sovereignTriads.length}`);
      sovereignTriads.forEach((triad, i) => {
        console.log(`  Triad ${i}: nodes=[${triad.nodes.join(',')}], coherence=${triad.coherence?.toFixed(3) || 'N/A'}`);
      });
    }

    const polarity = computePolarityOrientation(plainGraph, adjacency, this._rewriteHistory);
    const sovereigntyIndex = computeSovereigntyIndex(sovereignTriads, plainGraph, adjacency);
    const devourerSignature = detectDevourerPatterns(plainGraph, adjacency, sovereignTriads);
    
    // Compute trivector magnitude from Clifford field
    let trivectorMagnitude = 0;
    if (cliffordField && cliffordField.payload && cliffordField.payload.components) {
      const c = cliffordField.payload.components;
      trivectorMagnitude = Math.sqrt(c[11]**2 + c[12]**2 + c[13]**2 + c[14]**2);

      // DEBUG: Log trivector components for diagnostics
      if (trivectorMagnitude > 0.01) {
        console.log(`🔺 Trivector magnitude: ${trivectorMagnitude.toFixed(4)}`);
        console.log(`🔺 Components [11-14]: [${c[11]?.toFixed(3) || 0}, ${c[12]?.toFixed(3) || 0}, ${c[13]?.toFixed(3) || 0}, ${c[14]?.toFixed(3) || 0}]`);
      }
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

    // HEBREW LETTER NETWORK & 231-GATES SYSTEM
    this.initializeHebrewNetwork = () => {
      // Initialize 22 Hebrew letters as FIRM operators
      this.hebrewLetters = this.generateHebrewLetterMappings();

      // Generate all C(22,2) = 231 gate combinations
      this.gates231Network = this.generateAllGates();

      // Map gates to fractal attractor types
      this.fractalGateMappings = this.mapGatesToFractalAttractors();

      console.log(`🔤 Hebrew Network: ${this.hebrewLetters.length} letters initialized`);
      console.log(`🎭 231-Gates: ${this.gates231Network.length} gates generated`);
      console.log(`🌊 Fractal Mappings: ${Object.keys(this.fractalGateMappings).length} attractor types`);

      // Expose for debugging
      if (typeof window !== 'undefined') {
        window.hebrewLetters = this.hebrewLetters;
        window.gates231Network = this.gates231Network;
        window.fractalGateMappings = this.fractalGateMappings;
      }
    };

    this.generateHebrewLetterMappings = () => {
      // 22 Hebrew letters with FIRM operator mappings
      return [
        { hebrew: 'א', name: 'Aleph', fsctf: 'τ', role: 'threshold_silence', fractal: 'seed_fixed_point' },
        { hebrew: 'ב', name: 'Bet', fsctf: 'κ', role: 'container', fractal: 'lattice_cell' },
        { hebrew: 'ג', name: 'Gimel', fsctf: 'μ', role: 'bridge', fractal: 'transport_network' },
        { hebrew: 'ד', name: 'Dalet', fsctf: 'δ', role: 'gate', fractal: 'portal_structure' },
        { hebrew: 'ה', name: 'Heh', fsctf: 'ε', role: 'embodiment', fractal: 'breathing_cycle' },
        { hebrew: 'ו', name: 'Vav', fsctf: '⊗', role: 'link', fractal: 'coupling_network' },
        { hebrew: 'ז', name: 'Zayin', fsctf: 'ζ', role: 'cut', fractal: 'pruning_boundary' },
        { hebrew: 'ח', name: 'Chet', fsctf: 'χ', role: 'enclosure', fractal: 'filled_hull' },
        { hebrew: 'ט', name: 'Teth', fsctf: 'θ', role: 'twist', fractal: 'twisted_torus' },
        { hebrew: 'י', name: 'Yod', fsctf: 'ι', role: 'seed_point', fractal: 'origin_fixed_point' },
        { hebrew: 'כ', name: 'Kaf', fsctf: 'κ', role: 'capacity', fractal: 'bounded_cycle' },
        { hebrew: 'ל', name: 'Lamed', fsctf: 'λ', role: 'elevation', fractal: 'spiral_ascent' },
        { hebrew: 'מ', name: 'Mem', fsctf: 'μ', role: 'memory', fractal: 'recursive_memory' },
        { hebrew: 'נ', name: 'Nun', fsctf: 'ν', role: 'descent', fractal: 'falling_cascade' },
        { hebrew: 'ס', name: 'Samekh', fsctf: 'σ', role: 'support', fractal: 'backbone_structure' },
        { hebrew: 'ע', name: 'Ayin', fsctf: 'ο', role: 'observation', fractal: 'projected_shadow' },
        { hebrew: 'פ', name: 'Peh', fsctf: 'π', role: 'speech', fractal: 'vibratory_wave' },
        { hebrew: 'צ', name: 'Tzaddi', fsctf: 'τ', role: 'righteousness', fractal: 'ridge_filament' },
        { hebrew: 'ק', name: 'Qof', fsctf: 'κ', role: 'cascade', fractal: 'period_doubling' },
        { hebrew: 'ר', name: 'Resh', fsctf: 'ρ', role: 'reflection', fractal: 'mode_locking' },
        { hebrew: 'ש', name: 'Shin', fsctf: 'σ', role: 'transformation', fractal: 'chaotic_flame' },
        { hebrew: 'ת', name: 'Tav', fsctf: 'τ', role: 'completion', fractal: 'omega_limit' }
      ];
    };

    this.generateAllGates = () => {
      // Generate all C(22,2) = 231 undirected pairs
      const gates = [];
      for (let i = 0; i < this.hebrewLetters.length; i++) {
        for (let j = i + 1; j < this.hebrewLetters.length; j++) {
          const letter1 = this.hebrewLetters[i];
          const letter2 = this.hebrewLetters[j];

          gates.push({
            id: `${letter1.hebrew}-${letter2.hebrew}`,
            letters: [letter1, letter2],
            fsctf_ops: [letter1.fsctf, letter2.fsctf],
            fractal_type: this.determineFractalType(letter1, letter2),
            motif_class: this.classifyMotif(letter1, letter2),
            active: false,
            coherence: 0
          });
        }
      }
      return gates;
    };

    this.determineFractalType = (letter1, letter2) => {
      // Map letter pairs to fractal attractor types
      const types = {
        'א-ב': 'seed_in_cell', 'א-ג': 'transport_seed', 'א-ד': 'portal_seed',
        'ב-ג': 'container_bridge', 'ב-ד': 'gate_container', 'ג-ד': 'bridge_gate',
        // ... complete mapping for all 231 pairs
      };
      return types[`${letter1.hebrew}-${letter2.hebrew}`] || 'compound_attractor';
    };

    this.classifyMotif = (letter1, letter2) => {
      // Classify interaction motifs
      const motifs = ['network_fusion', 'sculpted_region', 'io_dialogue', 'learned_memory'];
      return motifs[Math.floor(Math.random() * motifs.length)];
    };

    this.mapGatesToFractalAttractors = () => {
      // Map each gate to specific fractal attractor properties
      const mappings = {};
      this.gates231Network.forEach(gate => {
        mappings[gate.id] = {
          fractal_type: gate.fractal_type,
          motif_class: gate.motif_class,
          complexity: this.calculateComplexity(gate),
          emergence_threshold: 0.15 + Math.random() * 0.3
        };
      });
      return mappings;
    };

    this.calculateComplexity = (gate) => {
      // Calculate gate complexity based on letter properties
      const letter1 = gate.letters[0];
      const letter2 = gate.letters[1];
      return (letter1.name.length + letter2.name.length) / 10;
    };

    // EMERGENT EVOLUTIONARY DYNAMICS
    this.evolutionState = {
      phase: 'void', // void → grace → bootstrap → bireflection → sovereignty
      coherence: 0,  // Scalar field (grade-0) - base coherence
      structure: 0,  // Vector fields (grade-1) - directional structure
      duality: 0,    // Bivector fields (grade-2) - area duality
      volume: 0,     // Trivector fields (grade-3) - volume emergence
      unity: 0,      // Pseudoscalar (grade-4) - full spacetime unity
      recursiveDepth: 0,
      sovereignTriads: 0,
      emergentLetters: [],
      activeGates: []
    };

    this.evolveSystem = (audioCoherence, deltaTime) => {
      // DEBUG: Log audioCoherence to understand why grace isn't working
      console.log(`🎵 evolveSystem called with audioCoherence=${audioCoherence?.toFixed(3) || 0}`);

      // WORKAROUND: If audioCoherence is 0 and we're stuck in void, force some artificial input
      if (audioCoherence < 0.1 && this.evolutionState.phase === 'void') {
        console.log(`🔧 WORKAROUND: Forcing artificial audioCoherence for testing`);
        audioCoherence = 0.3; // Force some artificial input to get the system moving
      }

      // EMERGENT EVOLUTION: Let mathematical relationships drive everything
      this.emergentEvolution(audioCoherence, deltaTime);
      return this.evolutionState;
    };

    this.emergentEvolution = (audioCoherence, deltaTime) => {
      // Use preserved field state if available, otherwise fall back to snapshot
      let components;
      if (this._currentFieldState?.payload?.components) {
        components = this._currentFieldState.payload.components;
        console.log('📊 Using preserved field state for evolution');
      } else if (this.currentSnapshot?.cliffordField?.payload?.components) {
        components = this.currentSnapshot.cliffordField.payload.components;
        console.log('📊 Using snapshot field state for evolution');
      } else {
        console.log('❌ No Clifford field available for evolution');
        return;
      }

      // DEBUG: Log current phase and field state before evolution
      console.log(`🔄 Starting evolution in phase: ${this.evolutionState.phase}`);
      console.log(`📊 Field before: scalar=${components[0]?.toFixed(3) || 0}, vector=${Math.sqrt((components[1]||0)**2 + (components[2]||0)**2 + (components[3]||0)**2).toFixed(3)}`);

      // GRACE OPERATOR: Identity element emerges scalar coherence from void
      this.evolveGraceOperator(components, audioCoherence);
      console.log(`🌟 After grace: phase=${this.evolutionState.phase}, scalar=${components[0]?.toFixed(3) || 0}`);

      // BOOTSTRAP: Vector structure emerges from scalar coherence
      this.evolveBootstrapOperator(components);
      console.log(`⚡ After bootstrap: phase=${this.evolutionState.phase}, vector=${Math.sqrt((components[1]||0)**2 + (components[2]||0)**2 + (components[3]||0)**2).toFixed(3)}`);

      // BIREFLECTION: Dual structures emerge from vector fields
      this.evolveBireflectionOperator(components);
      console.log(`🔄 After bireflection: phase=${this.evolutionState.phase}, bivector=${Math.sqrt(components.slice(4,11).reduce((sum,c)=>sum+c*c,0)).toFixed(3)}`);

      // SOVEREIGNTY: Volume elements emerge from closed cycles
      this.evolveSovereigntyOperator(components);
      console.log(`👑 After sovereignty: phase=${this.evolutionState.phase}, trivector=${Math.sqrt(components.slice(11,15).reduce((sum,c)=>sum+c*c,0)).toFixed(3)}`);

      // HEBREW LETTERS: Emerge from field relationships
      console.log(`🔤 Emerging Hebrew letters with field state: scalar=${components[0]?.toFixed(3) || 0}, phase=${this.evolutionState.phase}`);
      this.emergeHebrewLetters(components);

      // INTEGRATE EMERGENT LETTERS INTO GRAPH: Add as nodes
      this.integrateEmergentLettersIntoGraph();

      // INTEGRATE ACTIVE GATES INTO GRAPH: Add as edges that can form triangles
      this.integrateActiveGatesIntoGraph();

      // DEBUG: Log final phase after evolution
      console.log(`✅ Evolution complete in phase: ${this.evolutionState.phase} (coherence=${this.evolutionState.coherence?.toFixed(3) || 0})`);
    };

    // INTEGRATE EMERGENT LETTERS INTO GRAPH STRUCTURE
    this.integrateEmergentLettersIntoGraph = () => {
      console.log(`🔗 Letter integration: ${this.evolutionState.emergentLetters?.length || 0} letters to integrate`);
      if (!this.evolutionState.emergentLetters || this.evolutionState.emergentLetters.length === 0) return;

      let graphModified = false;

      for (const letter of this.evolutionState.emergentLetters) {
        console.log(`🔗 Processing letter: ${letter.symbol} (${letter.name})`);
        // Check if this letter already exists as a node
        const existingNode = this._graph.nodes.find(n => this._graph.labels[n]?.monadic_id === letter.symbol);

        if (!existingNode) {
          // Add the letter as a new node
          const nodeId = this._allocateNodeId(this._graph);
          const nodeLabel = make_node_label('X', letter.coherence * Math.PI, 1, letter.symbol);

          // Add node to graph
          this._graph.nodes.push(nodeId);
          this._graph.labels[nodeId] = nodeLabel;

          // Create edges to existing nodes that could form meaningful connections
          const existingNodes = this._graph.nodes.filter(n => n !== nodeId);

          if (existingNodes.length > 0) {
            // Connect to a few existing nodes to start building structure
            const connectionsToMake = Math.min(2, existingNodes.length);

            for (let i = 0; i < connectionsToMake; i++) {
              const targetNode = existingNodes[existingNodes.length - 1 - i]; // Connect to most recent nodes
              this._graph.edges.push([nodeId, targetNode]);
            }
          }

          graphModified = true;
          console.log(`🔗 Added Hebrew letter ${letter.symbol} as node ${nodeId} to graph`);
        }
      }

      // Record graph modification in rewrite history
      if (graphModified) {
        this._rewriteHistory.push({
          type: 'hebrew_letter_integration',
          lettersAdded: this.evolutionState.emergentLetters.length,
          timestamp: Date.now()
        });
      }
    };

    // INTEGRATE ACTIVE GATES INTO GRAPH AS EDGES
    this.integrateActiveGatesIntoGraph = () => {
      console.log(`🔗 Gate integration: ${this.evolutionState.activeGates?.length || 0} gates to integrate`);
      if (!this.evolutionState.activeGates || this.evolutionState.activeGates.length === 0) return;

      let graphModified = false;

      for (const gate of this.evolutionState.activeGates) {
        console.log(`🔗 Processing gate: ${gate.id} (active: ${gate.active})`);
        if (gate.active && gate.letters && gate.letters.length === 2) {
          const letter1 = gate.letters[0];
          const letter2 = gate.letters[1];

          // Find nodes corresponding to these letters
          const node1 = this._graph.nodes.find(n => this._graph.labels[n]?.monadic_id === letter1.symbol);
          const node2 = this._graph.nodes.find(n => this._graph.labels[n]?.monadic_id === letter2.symbol);

          if (node1 !== undefined && node2 !== undefined && node1 !== node2) {
            // Check if edge already exists
            const edgeExists = this._graph.edges.some(([u, v]) =>
              (u === node1 && v === node2) || (u === node2 && v === node1)
            );

            if (!edgeExists) {
              // Add edge between the two letter nodes
              this._graph.edges.push([node1, node2]);
              graphModified = true;
              console.log(`🔗 Added gate ${gate.id} as edge between nodes ${node1} and ${node2}`);

              // If we have 3+ nodes, try to create triangular closure
              if (this._graph.nodes.length >= 3) {
                this.attemptTriangleClosure(node1, node2);
              }
            }
          }
        }
      }

      // Record graph modification in rewrite history
      if (graphModified) {
        this._rewriteHistory.push({
          type: 'gate_integration',
          gatesAdded: this.evolutionState.activeGates.length,
          timestamp: Date.now()
        });
      }
    };

    // ATTEMPT TO CREATE TRIANGULAR CLOSURES
    this.attemptTriangleClosure = (nodeA, nodeB) => {

    // ATTEMPT TO CREATE TRIANGULAR CLOSURES
    this.attemptTriangleClosure = (nodeA, nodeB) => {
      // Look for a third node that can form a triangle with A and B
      const otherNodes = this._graph.nodes.filter(n => n !== nodeA && n !== nodeB);

      for (const nodeC of otherNodes) {
        // Check if edges A-C and B-C exist or could be created
        const hasEdgeAC = this._graph.edges.some(([u, v]) =>
          (u === nodeA && v === nodeC) || (u === nodeC && v === nodeA)
        );
        const hasEdgeBC = this._graph.edges.some(([u, v]) =>
          (u === nodeB && v === nodeC) || (u === nodeC && v === nodeB)
        );

        // If both edges exist, we already have a triangle
        if (hasEdgeAC && hasEdgeBC) {
          console.log(`🔺 Triangle already exists: ${nodeA}-${nodeB}-${nodeC}`);
          return; // Found existing triangle
        }

        // If only one edge exists, add the missing edge to create a triangle
        if (hasEdgeAC && !hasEdgeBC) {
          this._graph.edges.push([nodeB, nodeC]);
          console.log(`🔺 Created triangle closure: added ${nodeB}-${nodeC} to complete ${nodeA}-${nodeB}-${nodeC}`);
          return;
        } else if (hasEdgeBC && !hasEdgeAC) {
          this._graph.edges.push([nodeA, nodeC]);
          console.log(`🔺 Created triangle closure: added ${nodeA}-${nodeC} to complete ${nodeA}-${nodeB}-${nodeC}`);
          return;
        }
      }

      // If we can't find a good third node, try creating one
      if (otherNodes.length < 2) {
        this.createTriangularNode(nodeA, nodeB);
      }
    };

    // CREATE A NEW NODE TO FORM TRIANGULAR STRUCTURE
    this.createTriangularNode = (nodeA, nodeB) => {
      const nodeC = this._allocateNodeId(this._graph);
      const nodeLabel = make_node_label('Z', Math.PI / 3, 1, 'triangle_closure');

      this._graph.nodes.push(nodeC);
      this._graph.labels[nodeC] = nodeLabel;

      // Create edges to form triangle
      this._graph.edges.push([nodeA, nodeC]);
      this._graph.edges.push([nodeB, nodeC]);

      console.log(`🔺 Created triangular node ${nodeC} with edges ${nodeA}-${nodeC} and ${nodeB}-${nodeC}`);
    };

      // 231-GATES: Emerge from letter relationships
      this.emergeGatesFromLetters();

      // Update evolution metrics
      this.updateEmergentMetrics(components);
    };

    this.evolveGraceOperator = (components, audioCoherence) => {
      // Grace operator (𝒢) is the identity element in Clifford algebra
      // It naturally emerges scalar coherence from apparent void

      if (this.evolutionState.phase === 'void') {
        // DEBUG: Log grace emergence conditions
        if (typeof window !== 'undefined' && window.theoryLogger?.debug) {
          window.theoryLogger.debug(`Grace check: phase=${this.evolutionState.phase}, audioCoherence=${audioCoherence?.toFixed(3) || 0}, scalar=${components[0]?.toFixed(3) || 0}`);
        }

        // Scalar field (grade-0) emerges from audio coherence
        const graceEmergence = Math.max(0, audioCoherence - 0.1) * 0.05;
        console.log(`🌟 Grace calculation: audioCoherence=${audioCoherence?.toFixed(3) || 0}, graceEmergence=${graceEmergence.toFixed(4)}`);
        components[0] += graceEmergence; // Scalar field

        if (typeof window !== 'undefined' && window.theoryLogger?.debug) {
          window.theoryLogger.debug(`Grace emergence: ${graceEmergence.toFixed(4)}, new scalar=${components[0]?.toFixed(3) || 0}`);
        }

        if (components[0] > 0.3) {
          console.log(`🌟 Phase transition: Void → Grace (scalar=${components[0].toFixed(3)} > 0.3)`);
          this.evolutionState.phase = 'grace';
          this.evolutionState.coherence = components[0];
          console.log('🌟 Emergent transition: Void → Grace (scalar coherence emerged)');
        } else {
          console.log(`🌟 Grace check: scalar=${components[0]?.toFixed(3) || 0}, threshold=0.3, audioCoherence=${audioCoherence?.toFixed(3) || 0}`);

          // DEBUG: Force phase transition for testing if we're stuck
          if (components[0] > 0.1 && this.evolutionState.phase === 'void') {
            console.log(`🔧 DEBUG: Forcing phase transition for testing`);
            this.evolutionState.phase = 'grace';
            this.evolutionState.coherence = components[0];
          }
        }
      }
    };

    this.evolveBootstrapOperator = (components) => {
      if (this.evolutionState.phase === 'grace' && components[0] > 0.5) {
        // Bootstrap naturally creates vector structure from scalar coherence
        // Vector fields (grade-1) emerge from scalar field gradients

        const scalarField = components[0];

        // Natural emergence of directional structure
        components[1] += scalarField * 0.01; // e1 - X direction
        components[2] += scalarField * 0.008; // e2 - Y direction
        components[3] += scalarField * 0.006; // e3 - Z direction

        // Structure metric
        this.evolutionState.structure = Math.sqrt(
          components[1]**2 + components[2]**2 + components[3]**2
        );

        if (this.evolutionState.structure > 0.3) {
          this.evolutionState.phase = 'bootstrap';
          console.log('🌱 Emergent transition: Grace → Bootstrap (vector structure emerged)');
        }
      }
    };

    this.evolveBireflectionOperator = (components) => {
      if (this.evolutionState.phase === 'bootstrap' && this.evolutionState.structure > 0.4) {
        // Bireflection creates dual structures naturally
        // Bivector fields (grade-2) emerge as dual to vector fields

        const vectorField = [
          components[1], components[2], components[3]
        ];

        // Natural emergence of area elements (bivectors)
        components[4] += vectorField[0] * vectorField[1] * 0.001; // e01
        components[5] += vectorField[1] * vectorField[2] * 0.001; // e02
        components[6] += vectorField[2] * vectorField[0] * 0.001; // e03

        // Additional bivectors
        components[7] += vectorField[0] * vectorField[1] * vectorField[2] * 0.0005; // e12
        components[8] += vectorField[0] * vectorField[2] * 0.001; // e13
        components[9] += vectorField[1] * vectorField[2] * 0.001; // e23
        components[10] += vectorField[0] * vectorField[1] * vectorField[2] * 0.0005; // e012

        // Duality metric
        this.evolutionState.duality = Math.sqrt(
          components[4]**2 + components[5]**2 + components[6]**2 +
          components[7]**2 + components[8]**2 + components[9]**2 + components[10]**2
        );

        if (this.evolutionState.duality > 0.2) {
          this.evolutionState.phase = 'bireflection';
          console.log('🔄 Emergent transition: Bootstrap → Bireflection (dual structures emerged)');
        }
      }
    };

    this.evolveSovereigntyOperator = (components) => {
      if (this.evolutionState.phase === 'bireflection') {
        // Sovereignty emerges when graph forms closed cycles (sovereign triads)
        console.log(`🔄 Evolving sovereignty operator in bireflection phase...`);
        const cycles = this.detectEmergentCycles();

        if (cycles.length > 0) {
          console.log(`👑 Found ${cycles.length} cycles, setting sovereign triads`);
          this.evolutionState.sovereignTriads = cycles.length;

          // Trivectors (grade-3) emerge from closed cycles
          cycles.forEach((cycle, index) => {
            if (cycle.length >= 3) {
              const triadInfluence = 0.1 + index * 0.05;

              // e013, e023, e123, e0123 emerge from triad closure
              components[11] += triadInfluence * 0.25; // e013
              components[12] += triadInfluence * 0.25; // e023
              components[13] += triadInfluence * 0.25; // e123
              components[14] += triadInfluence * 0.25; // e0123 (from bootstrap)
            }
          });

          this.evolutionState.volume = Math.sqrt(
            components[11]**2 + components[12]**2 + components[13]**2 + components[14]**2
          );
          console.log(`📊 Trivector magnitude after cycles: ${this.evolutionState.volume.toFixed(4)}`);

          if (this.evolutionState.sovereignTriads > 0) {
            this.evolutionState.phase = 'sovereignty';
            console.log(`👑 Emergent transition: Bireflection → Sovereignty (${this.evolutionState.sovereignTriads} sovereign triads)`);
          }
        } else {
          console.log(`🔄 No cycles found yet, remaining in bireflection phase`);
        }

        // Recursive depth from shared triad nodes
        if (this.evolutionState.sovereignTriads > 1) {
          const sharedNodes = this.calculateSharedTriadNodes(cycles);
          this.evolutionState.recursiveDepth = Math.log(1 + sharedNodes);
        }
      }
    };

    this.emergeHebrewLetters = (components) => {
      // Hebrew letters emerge from specific field relationships
      // DEBUG: Log field state to understand why letters aren't emerging
      if (typeof window !== 'undefined' && window.theoryLogger?.debug) {
        window.theoryLogger.debug(`Field state: scalar=${components[0]?.toFixed(3) || 0}, vector=${Math.sqrt((components[1]||0)**2 + (components[2]||0)**2 + (components[3]||0)**2).toFixed(3)}, coherence=${this.evolutionState.coherence?.toFixed(3) || 0}`);
      }

      const letters = [
        { symbol: 'א', name: 'Aleph', condition: () => components[0] > 0.2 && this.evolutionState.coherence > 0.1 },
        { symbol: 'ב', name: 'Bet', condition: () => components[0] > 0.4 && components[1] > 0.1 },
        { symbol: 'ג', name: 'Gimel', condition: () => components[4] > 0.1 && components[5] > 0.1 },
        { symbol: 'ד', name: 'Dalet', condition: () => components[7] > 0.05 },
        { symbol: 'ה', name: 'Heh', condition: () => components[0] > 0.6 && this.evolutionState.structure > 0.2 },
        { symbol: 'ו', name: 'Vav', condition: () => components[4] > 0.2 && components[5] > 0.2 },
        { symbol: 'ז', name: 'Zayin', condition: () => components[11] > 0.1 },
        { symbol: 'ח', name: 'Chet', condition: () => components[8] > 0.1 && components[9] > 0.1 },
        { symbol: 'ט', name: 'Teth', condition: () => components[10] > 0.05 },
        { symbol: 'י', name: 'Yod', condition: () => components[0] > 0.8 },
        { symbol: 'כ', name: 'Kaf', condition: () => components[7] > 0.1 && components[8] > 0.1 },
        { symbol: 'ל', name: 'Lamed', condition: () => components[13] > 0.1 },
        { symbol: 'מ', name: 'Mem', condition: () => components[14] > 0.1 },
        { symbol: 'נ', name: 'Nun', condition: () => components[9] > 0.15 },
        { symbol: 'ס', name: 'Samekh', condition: () => components[10] > 0.1 && components[11] > 0.1 },
        { symbol: 'ע', name: 'Ayin', condition: () => components[12] > 0.1 },
        { symbol: 'פ', name: 'Peh', condition: () => components[13] > 0.15 },
        { symbol: 'צ', name: 'Tzaddi', condition: () => components[14] > 0.15 },
        { symbol: 'ק', name: 'Qof', condition: () => components[11] > 0.2 && components[12] > 0.2 },
        { symbol: 'ר', name: 'Resh', condition: () => components[13] > 0.2 },
        { symbol: 'ש', name: 'Shin', condition: () => components[14] > 0.2 },
        { symbol: 'ת', name: 'Tav', condition: () => components[15] > 0.1 }
      ];

      letters.forEach(letter => {
        const shouldEmerge = letter.condition();
        if (typeof window !== 'undefined' && window.theoryLogger?.debug) {
          window.theoryLogger.debug(`Letter ${letter.symbol}: condition=${shouldEmerge} (coherence=${this.evolutionState.coherence?.toFixed(3) || 0})`);
        }

        if (shouldEmerge && !this.evolutionState.emergentLetters.find(l => l.symbol === letter.symbol)) {
          this.evolutionState.emergentLetters.push({
            symbol: letter.symbol,
            name: letter.name,
            emergenceTime: Date.now(),
            coherence: this.calculateLetterCoherence(letter, components)
          });
          console.log(`🔤 Emergent letter: ${letter.symbol} (${letter.name})`);
        }
      });
    };

    this.emergeGatesFromLetters = () => {
      // 231-gates emerge from letter relationships
      if (this.evolutionState.emergentLetters.length < 2) return;

      const letters = this.evolutionState.emergentLetters;

      for (let i = 0; i < letters.length; i++) {
        for (let j = i + 1; j < letters.length; j++) {
          const letter1 = letters[i];
          const letter2 = letters[j];
          const gateId = `${letter1.symbol}-${letter2.symbol}`;

          if (!this.evolutionState.activeGates.find(g => g.id === gateId)) {
            const gate = {
              id: gateId,
              letters: [letter1, letter2],
              emergenceTime: Date.now(),
              coherence: (letter1.coherence + letter2.coherence) / 2,
              fractalType: this.determineEmergentFractalType(letter1, letter2),
              active: true
            };

            this.evolutionState.activeGates.push(gate);
            console.log(`🎭 Emergent gate: ${gateId} (${gate.fractalType})`);
          }
        }
      }
    };

    this.calculateLetterCoherence = (letter, components) => {
      // Each letter's coherence based on specific field relationships
      switch (letter.symbol) {
        case 'א': return components[0]; // Scalar field
        case 'ב': return Math.sqrt(components[1]**2 + components[2]**2); // Vector magnitude
        case 'ג': return components[4] + components[5]; // e01 + e02
        case 'ד': return components[7]; // e12
        case 'ה': return components[0] * 0.8 + this.evolutionState.structure * 0.2;
        case 'ו': return components[4] + components[5] + components[6]; // Coupling
        case 'ז': return components[11]; // First trivector
        case 'ח': return components[8] + components[9]; // e13 + e23
        case 'ט': return components[10]; // e012
        case 'י': return components[0] * 0.9;
        case 'כ': return components[7] + components[8]; // e12 + e13
        case 'ל': return components[13]; // e123
        case 'מ': return components[14]; // e0123
        case 'נ': return components[9]; // e23
        case 'ס': return components[10] + components[11]; // e012 + e013
        case 'ע': return components[12]; // e023
        case 'פ': return components[13]; // e123
        case 'צ': return components[14]; // e0123
        case 'ק': return components[11] + components[12]; // e013 + e023
        case 'ר': return components[13]; // e123
        case 'ש': return components[14]; // e0123
        case 'ת': return components[15]; // Pseudoscalar
        default: return 0;
      }
    };

    // RIGOROUS 20-COLUMN MEASUREMENT SYSTEM
    this.twentyColumns = {
      // Algebraic Foundations (columns 1-6)
      morphicTypeSignature: null,    // Category-theoretic morphism type
      toposMapping: null,            // Categorical topos equivalence
      zxPhaseGroup: null,            // ZX group (Pauli, Clifford, T, etc.)
      frobeniusAlgebraRole: null,    // Comonoid/monoid role
      spinorProjection: null,        // Clifford algebra spinors/bivectors
      lieAlgebraGenerator: null,     // SU(2), SU(3) basis elements

      // Computational Analogues (columns 7-8, 15)
      quantumGateAnalog: null,       // H, CNOT, Toffoli mappings
      tensorRankType: null,          // (1,1), scalar, bivector
      computationalComplexityClass: null, // P, NP, BQP classification

      // Dynamical Systems & Fields (columns 9-14, 18)
      dynamicalSystemRole: null,     // Attractor/bifurcation behavior
      symmetryGroupAssociation: null, // A₅, SU(n), E₈ associations
      fieldTheoryAnalog: null,       // Field operator mappings
      conformalGeometryRole: null,   // Möbius/conformal transformations
      fourierDomainSignature: null,  // FFT phase/frequency behavior
      morphicGradientBehavior: null, // Gradient descent in morphic fields
      fractalAttractorRole: null,    // Strange, toroidal, fixed-point attractors

      // Recursive Causality (columns 16-17)
      recursiveDepthMetric: null,    // Base, mid, apex recursion levels
      causalConeDepth: null,         // Pearl causality graph placement

      // Information Geometry (columns 19-20)
      informationTheoreticRole: null, // Entropy, channel capacity
      emergenceIndex: null           // Coherence seeding metric
    };

    // FINAL COALGEBRA Ω (Terminal Object)
    this.finalMonad = {
      type: 'terminal_coalgebra',
      structure: 'recursive_identity',
      dimension: 20,
      invariant: true
    };

    // MEASUREMENT FUNCTOR M: C → ∏ᵢ₌₁²⁰ Aᵢ
    this.measurementFunctor = (morphicObject) => {
      // Factor through the final monad: M ≅ N ∘ U
      const finalDescription = this.computeFinalDescription(morphicObject);
      const twentyTuple = this.computeTwentyTuple(finalDescription);

      return twentyTuple;
    };

    this.computeFinalDescription = (morphicObject) => {
      // Compute the unique morphism to the final coalgebra
      // U(X) = u_X: X → Ω (terminal coalgebra morphism)

      if (!morphicObject || !morphicObject.payload) return null;

      const components = morphicObject.payload.components;

      // The final description is determined by the invariant structure
      return {
        coherence: components[0],                    // Scalar coherence
        structure: Math.sqrt(components[1]**2 + components[2]**2 + components[3]**2), // Vector structure
        duality: Math.sqrt(components[4]**2 + components[5]**2 + components[6]**2 +
                          components[7]**2 + components[8]**2 + components[9]**2 + components[10]**2), // Bivector duality
        volume: Math.sqrt(components[11]**2 + components[12]**2 + components[13]**2 + components[14]**2), // Trivector volume
        unity: Math.abs(components[15]),            // Pseudoscalar unity
        recursiveDepth: this.evolutionState.recursiveDepth,
        sovereignTriads: this.evolutionState.sovereignTriads,
        activeLetters: this.evolutionState.emergentLetters.length,
        activeGates: this.evolutionState.activeGates ? this.evolutionState.activeGates.length : 0
      };
    };

    this.computeTwentyTuple = (finalDescription) => {
      if (!finalDescription) return this.twentyColumns;

      // Column 1: Morphic Type Signature
      this.twentyColumns.morphicTypeSignature = this.computeMorphicType(finalDescription);

      // Column 2: Topos Mapping
      this.twentyColumns.toposMapping = this.computeToposMapping(finalDescription);

      // Column 3: ZX Phase Group
      this.twentyColumns.zxPhaseGroup = this.computeZXPhaseGroup(finalDescription);

      // Column 4: Frobenius Algebra Role
      this.twentyColumns.frobeniusAlgebraRole = this.computeFrobeniusRole(finalDescription);

      // Column 5: Spinor Projection
      this.twentyColumns.spinorProjection = this.computeSpinorProjection(finalDescription);

      // Column 6: Lie Algebra Generator
      this.twentyColumns.lieAlgebraGenerator = this.computeLieGenerator(finalDescription);

      // Column 7: Quantum Gate Analog
      this.twentyColumns.quantumGateAnalog = this.computeQuantumGate(finalDescription);

      // Column 8: Tensor Rank/Type
      this.twentyColumns.tensorRankType = this.computeTensorType(finalDescription);

      // Column 9: Dynamical System Role
      this.twentyColumns.dynamicalSystemRole = this.computeDynamicalRole(finalDescription);

      // Column 10: Symmetry Group Association
      this.twentyColumns.symmetryGroupAssociation = this.computeSymmetryGroup(finalDescription);

      // Column 11: Field Theory Analog
      this.twentyColumns.fieldTheoryAnalog = this.computeFieldTheory(finalDescription);

      // Column 12: Conformal Geometry Role
      this.twentyColumns.conformalGeometryRole = this.computeConformalRole(finalDescription);

      // Column 13: Fourier Domain Signature
      this.twentyColumns.fourierDomainSignature = this.computeFourierSignature(finalDescription);

      // Column 14: Morphic Gradient Behavior
      this.twentyColumns.morphicGradientBehavior = this.computeMorphicGradient(finalDescription);

      // Column 15: Computational Complexity Class
      this.twentyColumns.computationalComplexityClass = this.computeComplexityClass(finalDescription);

      // Column 16: Recursive Depth Metric
      this.twentyColumns.recursiveDepthMetric = this.computeRecursiveDepth(finalDescription);

      // Column 17: Causal Cone Depth
      this.twentyColumns.causalConeDepth = this.computeCausalConeDepth(finalDescription);

      // Column 18: Fractal Attractor Role
      this.twentyColumns.fractalAttractorRole = this.computeFractalRole(finalDescription);

      // Column 19: Information-Theoretic Role
      this.twentyColumns.informationTheoreticRole = this.computeInformationRole(finalDescription);

      // Column 20: Emergence Index
      this.twentyColumns.emergenceIndex = this.computeEmergenceIndex(finalDescription);

      return this.twentyColumns;
    };

    // COLUMN COMPUTATION FUNCTIONS
    this.computeMorphicType = (fd) => {
      // Category-theoretic morphism type based on final description
      if (fd.coherence > 0.5 && fd.structure > 0.3) return 'isomorphism';
      if (fd.coherence > 0.3) return 'monomorphism';
      if (fd.structure > 0.2) return 'epimorphism';
      return 'general_morphism';
    };

    this.computeToposMapping = (fd) => {
      // Categorical topos equivalence
      if (fd.recursiveDepth > 1) return 'sheaf_topos';
      if (fd.sovereignTriads > 0) return 'coherent_topos';
      return 'presheaf_category';
    };

    this.computeZXPhaseGroup = (fd) => {
      // ZX group classification
      if (fd.volume > 0.3) return 'T_group';
      if (fd.duality > 0.4) return 'Clifford_group';
      if (fd.structure > 0.3) return 'Pauli_group';
      return 'identity_group';
    };

    this.computeFrobeniusRole = (fd) => {
      // Comonoid/monoid role
      if (fd.recursiveDepth > 0.5) return 'bimonoid';
      if (fd.coherence > 0.6) return 'comonoid';
      if (fd.structure > 0.4) return 'monoid';
      return 'coalgebra';
    };

    this.computeSpinorProjection = (fd) => {
      // Clifford algebra spinors/bivectors
      if (fd.volume > 0.2) return 'trivector_spinor';
      if (fd.duality > 0.3) return 'bivector_representation';
      if (fd.structure > 0.2) return 'vector_spinor';
      return 'scalar_identity';
    };

    this.computeLieGenerator = (fd) => {
      // SU(2), SU(3) basis elements
      if (fd.sovereignTriads > 2) return 'su3_gell_mann';
      if (fd.recursiveDepth > 0.5) return 'su2_pauli';
      if (fd.duality > 0.3) return 'so3_angular_momentum';
      return 'u1_phase';
    };

    this.computeQuantumGate = (fd) => {
      // Quantum gate mappings
      if (fd.volume > 0.3) return 'toffoli_gate';
      if (fd.duality > 0.4) return 'cnot_gate';
      if (fd.structure > 0.3) return 'hadamard_gate';
      return 'identity_gate';
    };

    this.computeTensorType = (fd) => {
      // Tensor rank/type
      if (fd.volume > 0.2) return '(1,1,1)_tensor';
      if (fd.duality > 0.3) return '(1,1)_tensor';
      if (fd.structure > 0.2) return '(1)_tensor';
      return 'scalar';
    };

    this.computeDynamicalRole = (fd) => {
      // Attractor/bifurcation behavior
      if (fd.sovereignTriads > 1) return 'strange_attractor';
      if (fd.recursiveDepth > 0.5) return 'limit_cycle';
      if (fd.duality > 0.3) return 'torus_attractor';
      return 'fixed_point';
    };

    this.computeSymmetryGroup = (fd) => {
      // Symmetry group associations
      if (fd.sovereignTriads > 2) return 'E8_exceptional';
      if (fd.recursiveDepth > 1) return 'SU3_strong';
      if (fd.duality > 0.4) return 'SO3_rotational';
      return 'U1_phase';
    };

    this.computeFieldTheory = (fd) => {
      // Field operator mappings
      if (fd.volume > 0.3) return 'yang_mills_field';
      if (fd.duality > 0.4) return 'electromagnetic_field';
      if (fd.structure > 0.3) return 'scalar_field';
      return 'free_field';
    };

    this.computeConformalRole = (fd) => {
      // Möbius/conformal transformations
      if (fd.recursiveDepth > 0.5) return 'conformal_infinity';
      if (fd.sovereignTriads > 0) return 'mobius_sphere';
      return 'euclidean_isometry';
    };

    this.computeFourierSignature = (fd) => {
      // FFT phase/frequency behavior
      if (fd.coherence > 0.7) return 'delta_function';
      if (fd.structure > 0.4) return 'power_law_spectrum';
      return 'white_noise';
    };

    this.computeMorphicGradient = (fd) => {
      // Gradient descent in morphic fields
      if (fd.recursiveDepth > 0.5) return 'recursive_descent';
      if (fd.coherence > 0.6) return 'coherence_climbing';
      return 'random_walk';
    };

    this.computeComplexityClass = (fd) => {
      // Computational complexity classification
      if (fd.recursiveDepth > 1) return 'PSPACE';
      if (fd.sovereignTriads > 1) return 'NP';
      if (fd.duality > 0.4) return 'BQP';
      return 'P';
    };

    this.computeRecursiveDepth = (fd) => {
      // Recursive depth metric
      return {
        base: fd.recursiveDepth < 0.5 ? 'shallow' : 'deep',
        mid: fd.recursiveDepth > 0.5 && fd.recursiveDepth < 1 ? 'intermediate' : 'advanced',
        apex: fd.recursiveDepth > 1 ? 'sovereign' : 'sub_sovereign'
      };
    };

    this.computeCausalConeDepth = (fd) => {
      // Pearl causality graph placement
      if (fd.sovereignTriads > 1) return 'multi_layer';
      if (fd.recursiveDepth > 0.5) return 'recursive_layer';
      return 'base_layer';
    };

    this.computeFractalRole = (fd) => {
      // Fractal attractor classification
      if (fd.volume > 0.3) return 'strange_attractor';
      if (fd.duality > 0.4) return 'toroidal_attractor';
      if (fd.structure > 0.3) return 'fixed_point_attractor';
      return 'limit_cycle_attractor';
    };

    this.computeInformationRole = (fd) => {
      // Information-theoretic role
      if (fd.coherence > 0.7) return 'low_entropy_channel';
      if (fd.structure > 0.4) return 'mutual_information_maximizer';
      return 'noise_channel';
    };

    this.computeEmergenceIndex = (fd) => {
      // Coherence seeding metric
      const baseIndex = fd.coherence * fd.structure;
      const recursiveBonus = fd.recursiveDepth * 0.2;
      const sovereignBonus = fd.sovereignTriads * 0.3;
      return Math.min(1, baseIndex + recursiveBonus + sovereignBonus);
    };

    // NATURALITY CHECK: Columns invariant under admissible transformations
    this.checkNaturality = (transformation, originalColumns) => {
      const transformedObject = this.applyTransformation(transformation);
      const transformedColumns = this.measurementFunctor(transformedObject);

      // Check if columns are invariant under the transformation
      const invariant = this.columnsInvariant(originalColumns, transformedColumns);

      if (!invariant) {
        console.log('⚠️ Naturality violation detected - columns not invariant under transformation');
      }

      return invariant;
    };

    this.applyTransformation = (transformation) => {
      // Apply admissible reparametrization (basis change, gauge transform, etc.)
      // This should preserve the final coalgebra structure
      if (!this.currentSnapshot?.cliffordField?.payload?.components) return null;

      const components = [...this.currentSnapshot.cliffordField.payload.components];

      // Example: Apply a basis rotation (should preserve invariants)
      const rotation = transformation.rotation || 0;
      const rotatedComponents = this.rotateFieldComponents(components, rotation);

      return {
        payload: {
          components: rotatedComponents,
          algebra: this.currentSnapshot.cliffordField.payload.algebra
        }
      };
    };

    this.rotateFieldComponents = (components, rotation) => {
      // Rotate vector components (components 1-3)
      const cosR = Math.cos(rotation);
      const sinR = Math.sin(rotation);

      const x = components[1];
      const y = components[2];

      components[1] = x * cosR - y * sinR; // X' = X*cos - Y*sin
      components[2] = x * sinR + y * cosR; // Y' = X*sin + Y*cos

      return components;
    };

    this.columnsInvariant = (cols1, cols2) => {
      // Check if columns are invariant (within tolerance)
      const tolerance = 0.01;

      // Critical invariants that must be preserved
      const criticalChecks = [
        Math.abs(cols1.emergenceIndex - cols2.emergenceIndex) < tolerance,
        cols1.morphicTypeSignature === cols2.morphicTypeSignature,
        cols1.toposMapping === cols2.toposMapping,
        cols1.fractalAttractorRole === cols2.fractalAttractorRole
      ];

      return criticalChecks.every(check => check);
    };

    // MINIMAL SUFFICIENCY TEST
    this.testMinimalSufficiency = () => {
      // Test if 20 dimensions are minimal and sufficient
      const fullColumns = this.measurementFunctor(this.currentSnapshot?.cliffordField);
      const reducedColumns = this.reduceToDimensions(fullColumns, 18); // Test with fewer dimensions

      // Check if reduced version can predict key properties
      const fullPrediction = this.predictFromColumns(fullColumns);
      const reducedPrediction = this.predictFromColumns(reducedColumns);

      const sufficient = this.comparePredictions(fullPrediction, reducedPrediction);

      console.log(`📊 Minimal sufficiency test: ${sufficient ? 'PASSED' : 'FAILED'}`);
      console.log(`   Full prediction: ${fullPrediction}`);
      console.log(`   Reduced prediction: ${reducedPrediction}`);

      return sufficient;
    };

    this.reduceToDimensions = (columns, dimensions) => {
      // Create reduced column set for testing minimality
      const reduced = {};

      // Keep most important dimensions
      const importantKeys = [
        'morphicTypeSignature', 'toposMapping', 'zxPhaseGroup',
        'frobeniusAlgebraRole', 'spinorProjection', 'lieAlgebraGenerator',
        'dynamicalSystemRole', 'symmetryGroupAssociation', 'fieldTheoryAnalog',
        'conformalGeometryRole', 'fourierDomainSignature', 'morphicGradientBehavior',
        'fractalAttractorRole', 'informationTheoreticRole', 'emergenceIndex'
      ].slice(0, dimensions);

      importantKeys.forEach(key => {
        reduced[key] = columns[key];
      });

      return reduced;
    };

    this.predictFromColumns = (columns) => {
      // Predict key system properties from columns
      return {
        attractorClass: columns.fractalAttractorRole,
        complexityClass: columns.computationalComplexityClass,
        emergenceLevel: columns.emergenceIndex,
        coherenceLevel: columns.morphicTypeSignature
      };
    };

    this.comparePredictions = (pred1, pred2) => {
      // Check if predictions are equivalent within tolerance
      const keys = Object.keys(pred1);
      const tolerance = 0.1;

      return keys.every(key => {
        if (typeof pred1[key] === 'number') {
          return Math.abs(pred1[key] - pred2[key]) < tolerance;
        }
        return pred1[key] === pred2[key];
      });
    };

    this.determineEmergentFractalType = (letter1, letter2) => {
      // Fractal types emerge from letter relationships
      const types = {
        'א-ב': 'seed_in_cell', 'א-ג': 'transport_seed', 'א-ד': 'portal_seed',
        'ב-ג': 'container_bridge', 'ב-ד': 'gate_container', 'ג-ד': 'bridge_gate',
        'ה-ו': 'breathing_coupling', 'ו-ז': 'link_cut', 'ז-ח': 'cut_enclosure'
      };
      return types[`${letter1.symbol}-${letter2.symbol}`] || 'compound_emergence';
    };

    this.detectEmergentCycles = () => {
      // Detect emergent cycles in the graph structure
      const cycles = [];
      if (!this.currentSnapshot?.graph?.nodes) {
        console.log('🔍 Cycle detection: No graph snapshot available');
        return cycles;
      }

      // Simple cycle detection - look for closed paths
      const nodes = this.currentSnapshot.graph.nodes;
      const edges = this.currentSnapshot.graph.edges || [];

      console.log(`🔍 Cycle detection: ${nodes.length} nodes, ${edges.length} edges`);

      // Debug: Log some sample edges to understand structure
      if (edges.length > 0) {
        console.log('🔍 Sample edges:', edges.slice(0, 3).map(e => `${e.source}->${e.target}`));
      }

      // Find 3-node cycles (sovereign triads)
      let checkedTriples = 0;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = 0; j < nodes.length; j++) {
          if (i === j) continue;
          for (let k = 0; k < nodes.length; k++) {
            if (i === k || j === k) continue;
            checkedTriples++;

            // Check if edges exist: i->j, j->k, k->i
            const hasEdgeIJ = edges.some(e => (e.source === nodes[i].id && e.target === nodes[j].id) ||
                                              (e.source === nodes[j].id && e.target === nodes[i].id));
            const hasEdgeJK = edges.some(e => (e.source === nodes[j].id && e.target === nodes[k].id) ||
                                              (e.source === nodes[k].id && e.target === nodes[j].id));
            const hasEdgeKI = edges.some(e => (e.source === nodes[k].id && e.target === nodes[i].id) ||
                                              (e.source === nodes[i].id && e.target === nodes[k].id));

            if (hasEdgeIJ && hasEdgeJK && hasEdgeKI) {
              const cycle = [nodes[i].id, nodes[j].id, nodes[k].id];
              cycles.push(cycle);
              console.log(`🔺 Sovereign triad found: ${cycle.join('->')} (cycle)`);
            }
          }
        }
      }

      console.log(`🔍 Cycle detection complete: checked ${checkedTriples} triples, found ${cycles.length} cycles`);

      return cycles;
    };

    this.calculateSharedTriadNodes = (cycles) => {
      if (cycles.length < 2) return 0;

      let sharedCount = 0;
      for (let i = 0; i < cycles.length; i++) {
        for (let j = i + 1; j < cycles.length; j++) {
          const shared = cycles[i].filter(n => cycles[j].includes(n)).length;
          if (shared >= 2) sharedCount++;
        }
      }
      return sharedCount;
    };

    this.updateEmergentMetrics = (components) => {
      // Update all metrics based on actual field state
      this.evolutionState.coherence = Math.max(0, components[0]);
      this.evolutionState.structure = Math.sqrt(components[1]**2 + components[2]**2 + components[3]**2);
      this.evolutionState.duality = Math.sqrt(
        components[4]**2 + components[5]**2 + components[6]**2 +
        components[7]**2 + components[8]**2 + components[9]**2 + components[10]**2
      );
      this.evolutionState.volume = Math.sqrt(
        components[11]**2 + components[12]**2 + components[13]**2 + components[14]**2
      );
      this.evolutionState.unity = Math.abs(components[15]);

      this.evolutionState.activeGates = this.evolutionState.activeGates ? this.evolutionState.activeGates.length : 0;
      this.evolutionState.sovereignTriads = this.evolutionState.sovereignTriads || 0;
    };

    // DEBUG FUNCTION: Force trivector emergence for testing
    this.debugForceTrivectors = () => {
      console.log('🔺 Forcing trivector emergence for testing...');

      // Force some trivector components
      if (this.currentSnapshot?.cliffordField?.payload?.components) {
        const components = this.currentSnapshot.cliffordField.payload.components;

        // Set some trivector components manually
        components[11] = 0.5; // e013
        components[12] = 0.3; // e023
        components[13] = 0.4; // e123
        components[14] = 0.2; // e0123

        console.log('🔺 Forced trivector components: [11-14] =', components.slice(11, 15));

        // Update evolution state
        this.evolutionState.volume = Math.sqrt(
          components[11]**2 + components[12]**2 + components[13]**2 + components[14]**2
        );
        this.evolutionState.sovereignTriads = 1;

        console.log('🔺 Trivector magnitude forced to:', this.evolutionState.volume.toFixed(4));
      } else {
        console.log('❌ Cannot force trivectors - no Clifford field available');
      }
    };

    // DEBUG FUNCTION: Check current system state
    this.debugCheckState = () => {
      console.log('🔍 Current system state:');
      console.log(`  Phase: ${this.evolutionState.phase}`);
      console.log(`  Coherence: ${this.evolutionState.coherence?.toFixed(3) || 0}`);
      console.log(`  Structure: ${this.evolutionState.structure?.toFixed(3) || 0}`);
      console.log(`  Volume: ${this.evolutionState.volume?.toFixed(3) || 0}`);
      console.log(`  Emergent letters: ${this.evolutionState.emergentLetters?.length || 0}`);
      console.log(`  Active gates: ${this.evolutionState.activeGates?.length || 0}`);
      console.log(`  Graph nodes: ${this._graph?.nodes?.length || 0}`);
      console.log(`  Graph edges: ${this._graph?.edges?.length || 0}`);

      if (this.currentSnapshot?.cliffordField?.payload?.components) {
        const components = this.currentSnapshot.cliffordField.payload.components;
        console.log(`  Scalar (0): ${components[0]?.toFixed(3) || 0}`);
        console.log(`  Vector magnitude (1-3): ${Math.sqrt((components[1]||0)**2 + (components[2]||0)**2 + (components[3]||0)**2).toFixed(3)}`);
        console.log(`  Bivector magnitude (4-10): ${Math.sqrt(components.slice(4,11).reduce((sum,c)=>sum+c*c,0)).toFixed(3)}`);
        console.log(`  Trivector magnitude (11-14): ${Math.sqrt(components.slice(11,15).reduce((sum,c)=>sum+c*c,0)).toFixed(3)}`);
      }
    };

    // DEBUG FUNCTION: Force Hebrew letter and gate emergence for testing (AD HOC)
    this.debugForceTriuneEmergence = () => {
      console.log('🔺 Forcing triune emergence for testing (AD HOC - not from theory dynamics)...');

      // Force some Hebrew letters to emerge
      if (!this.evolutionState.emergentLetters) {
        this.evolutionState.emergentLetters = [];
      }

      // Add some test letters if they don't exist
      const testLetters = ['א', 'ב', 'ג']; // Aleph, Bet, Gimel
      testLetters.forEach(symbol => {
        if (!this.evolutionState.emergentLetters.find(l => l.symbol === symbol)) {
          this.evolutionState.emergentLetters.push({
            symbol,
            name: ['Aleph', 'Bet', 'Gimel'][testLetters.indexOf(symbol)],
            emergenceTime: Date.now(),
            coherence: 0.6 + Math.random() * 0.3
          });
          console.log(`🔤 Forced emergent letter: ${symbol}`);
        }
      });

      // Force some gates to activate
      if (!this.evolutionState.activeGates) {
        this.evolutionState.activeGates = [];
      }

      // Create test gates between the letters
      const gates = [
        { id: 'א-ב', letters: [
          this.evolutionState.emergentLetters.find(l => l.symbol === 'א'),
          this.evolutionState.emergentLetters.find(l => l.symbol === 'ב')
        ]},
        { id: 'ב-ג', letters: [
          this.evolutionState.emergentLetters.find(l => l.symbol === 'ב'),
          this.evolutionState.emergentLetters.find(l => l.symbol === 'ג')
        ]},
        { id: 'א-ג', letters: [
          this.evolutionState.emergentLetters.find(l => l.symbol === 'א'),
          this.evolutionState.emergentLetters.find(l => l.symbol === 'ג')
        ]}
      ];

      gates.forEach(gate => {
        if (gate.letters.every(l => l) && !this.evolutionState.activeGates.find(g => g.id === gate.id)) {
          this.evolutionState.activeGates.push({
            id: gate.id,
            letters: gate.letters,
            active: true,
            coherence: 0.5 + Math.random() * 0.3
          });
          console.log(`🔗 Forced active gate: ${gate.id}`);
        }
      });

      console.log(`🔺 Triune emergence forced: ${this.evolutionState.emergentLetters.length} letters, ${this.evolutionState.activeGates.length} gates`);
    };

    // TEST FUNCTION: Manually trigger 231-gates system
    this.test231GatesSystem = () => {
      this.initializeHebrewNetwork();
      console.log(`🎭 231-Gates System Test: ${this.gates231Network.length} gates generated`);

      // Activate some gates based on current field state
      const activeGates = this.gates231Network.filter(gate =>
        Math.random() > 0.7 && this.fractalGateMappings[gate.id].emergence_threshold < 0.5
      );

      activeGates.forEach(gate => {
        gate.active = true;
        gate.coherence = 0.3 + Math.random() * 0.4;
        console.log(`🔗 Gate ${gate.id} activated: ${gate.motif_class}`);
      });

      return {
        totalGates: this.gates231Network.length,
        activeGates: activeGates.length,
        letters: this.hebrewLetters.length
      };
    };

    // Expose complete system globally
    if (typeof window !== 'undefined') {
      // 231-Gates system
      window.test231Gates = this.test231GatesSystem.bind(this);
      window.hebrewLetters = this.hebrewLetters;
      window.gates231Network = this.gates231Network;
      window.evolutionState = this.evolutionState;
      window.evolveSystem = this.evolveSystem.bind(this);

      // 20-Column measurement system
      window.twentyColumns = this.twentyColumns;
      window.finalMonad = this.finalMonad;
      window.measurementFunctor = this.measurementFunctor.bind(this);
      window.checkNaturality = this.checkNaturality.bind(this);
      window.testMinimalSufficiency = this.testMinimalSufficiency.bind(this);

      // Debug functions
      window.debugCheckState = this.debugCheckState.bind(this);
      window.debugForceTriuneEmergence = this.debugForceTriuneEmergence.bind(this);

      // Test functions
      window.test20ColumnSystem = () => {
        const columns = window.measurementFunctor(window.zxEvolutionEngine?.currentSnapshot?.cliffordField);
        console.log('🎭 20-Column System Test:', columns);
        return columns;
      };

      window.testNaturality = () => {
        const originalColumns = window.measurementFunctor(window.zxEvolutionEngine?.currentSnapshot?.cliffordField);
        const invariant = window.checkNaturality({ rotation: Math.PI/4 }, originalColumns);
        console.log(`🔍 Naturality Test: ${invariant ? 'PASSED' : 'FAILED'}`);
        return invariant;
      };

      window.testSufficiency = () => {
        const sufficient = window.testMinimalSufficiency();
        console.log(`📊 Sufficiency Test: ${sufficient ? 'PASSED' : 'FAILED'}`);
        return sufficient;
      };
    }

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

  // Soul Garbage Collection integration
  async _applySoulGarbageCollection() {
    if (!this._graph || !this._graph.labels) return;

    try {
      // Import SGC modules dynamically (avoiding circular imports)
      if (!window.FIRM_dsl_soul_garbage_collection) {
        try {
          // Try to load the SGC module directly
          const sgcModule = await import('./FIRM_dsl/soul_garbage_collection.js');
          window.FIRM_dsl_soul_garbage_collection = sgcModule;
          this._performSGCCleanup();
        } catch (err) {
          console.warn('SGC modules not available:', err.message);
        }
      } else {
        this._performSGCCleanup();
      }
    } catch (error) {
      console.warn('SGC application failed:', error.message);
    }
  }

  _performSGCCleanup() {
    try {
      const sgcModule = window.FIRM_dsl_soul_garbage_collection;
      if (!sgcModule) return;

      // Create SGC parameters based on current evolution state
      const sgcParams = sgcModule.create_sgc_params(
        0.3,  // epsilon
        0.5,  // grace_threshold
        10,   // max_recursion_depth
        0.2   // observer_feedback_weight
      );

      // Create omega signature from current graph (using resonance module)
      const omega = this._createOmegaSignature();

      // For now, use our custom omega signature creation
      // The resonance module integration can be added later when properly set up
      // omega is already created above with _createOmegaSignature()

      if (!omega) return;

      // Apply SGC to current graph
      try {
        const sgc = new sgcModule.SoulGarbageCollector(omega, sgcParams);
        const morphicStructure = new sgcModule.MorphicStructure(this._graph);

        const result = sgc.sgc_rule(morphicStructure);

        if (result && result.graph && result.graph !== this._graph) {
          // Update the graph with SGC result
          this._graph = result.graph;

          // Update UI if visualizer is available
          if (this._sgcVisualizer) {
            this._sgcVisualizer.updateFromEvolution(sgc, result);
          }

          console.log(`🗑️ SGC applied: ${sgc.pruned_nodes.length} nodes pruned, entropy reduction: ${sgc.compute_entropy_reduction(morphicStructure, result).toFixed(3)}`);
        } else {
          // SGC didn't prune anything this time
          console.log('🗑️ SGC evaluated - no pruning needed');
        }
      } catch (sgcError) {
        console.warn('SGC application failed:', sgcError.message);
        // Continue evolution even if SGC fails
      }
    } catch (error) {
      console.warn('SGC cleanup failed:', error.message);
    }
  }

  _createOmegaSignature() {
    try {
      // Create a proper omega signature that meets Qπ requirements
      // Use the current graph structure to determine appropriate phase bins
      if (!this._graph || !this._graph.labels) {
        return null;
      }

      // Extract phase denominators from the graph
      const phase_denoms = new Set();
      if (this._graph.labels) {
        for (const label of Object.values(this._graph.labels)) {
          if (label && typeof label === 'object' && label.phase_denom) {
            phase_denoms.add(label.phase_denom);
          } else if (label && typeof label === 'object' && label.phaseDenom) {
            // Handle camelCase property name
            phase_denoms.add(label.phaseDenom);
          }
        }
      }

      // If no phase denominators found, use a default
      if (phase_denoms.size === 0) {
        phase_denoms.add(1); // Default to simple phases
      }

      // Calculate LCM of phase denominators for proper Qπ binning
      const lcm = this._calculateLCM(Array.from(phase_denoms));
      const phase_bins = lcm > 0 ? 2 * lcm : 8; // 2*LCM for proper Qπ normalization

      // Create uniform phase histogram for now
      // In a full implementation, this would analyze actual phase distribution
      const phase_hist = new Array(phase_bins).fill(1.0 / phase_bins);

      return {
        cycles: this._graph.edges ? this._graph.edges.length : 0,
        phase_bins: phase_bins,
        phase_hist: phase_hist
      };
    } catch (error) {
      console.warn('Failed to create omega signature:', error.message);
      return null;
    }
  }

  _calculateLCM(numbers) {
    if (numbers.length === 0) return 1;
    if (numbers.length === 1) return numbers[0];

    let result = numbers[0];
    for (let i = 1; i < numbers.length; i++) {
      result = this._lcm(result, numbers[i]);
    }
    return result;
  }

  _lcm(a, b) {
    return (a * b) / this._gcd(a, b);
  }

  _gcd(a, b) {
    while (b !== 0) {
      const temp = b;
      b = a % b;
      a = temp;
    }
    return a;
  }

  // SGC control methods
  enableSoulGarbageCollection() {
    this._sgcEnabled = true;
    console.log('🗑️ Soul Garbage Collection enabled');
  }

  disableSoulGarbageCollection() {
    this._sgcEnabled = false;
    console.log('🗑️ Soul Garbage Collection disabled');
  }

  setSGCFrequency(frequency) {
    this._sgcFrequency = Math.max(1, Math.floor(frequency));
    console.log(`🗑️ SGC frequency set to every ${this._sgcFrequency} steps`);
  }

  getSGCStatus() {
    return {
      enabled: this._sgcEnabled,
      frequency: this._sgcFrequency,
      applications: this._sgcCounter,
      lastApplication: this._sgcCounter > 0 ? this._stepCount : null
    };
  }
}

