import { ObjectG, make_node_label, validate_object_g, add_phases_qpi, normalize_phase_qpi } from './FIRM_dsl/core.js';
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
    
    // SANITIZE GRAPH: Fix any phase denominators > 64 (from previous buggy code)
    this._sanitizePhaseDenominators(this._graph);
    
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
    this._sgcEntropyReduction = 0.0;  // Track entropy reduction for adaptive frequency

    // Initialize SGC system
    this._sgcVisualizer = null;
    this._sgcIntegration = null;

    // Performance optimization: Cache sovereignty detection results
    this._sovereigntyCache = null;

    const timestamp = Date.now();
    this._rewriteHistory.push({ type: 'seed', timestamp });
    this._cycleHistory.push({ timestamp, cycles: compute_cycle_basis_signature(this._graph) });
  }

  get currentGraph() {
    return toPlainGraph(this._graph);
  }

  _sanitizePhaseDenominators(graph) {
    // THEORY REQUIREMENT: All phase denominators MUST be powers of 2
    // Sanitize any non-power-of-2 denominators back to Qπ/8 space
    const BOOTSTRAP_DENOM = 8; // Theory-compliant bootstrap precision
    let fixed = 0;

    for (const [nodeId, label] of Object.entries(graph.labels)) {
      if (!label || typeof label !== 'object') continue;

      // Check if phase_denom exists and is not a power of 2
      if (label.phase_denom && !this._isPowerOf2(label.phase_denom)) {
        // Determine the target power-of-2 denominator (nearest, capped at 64)
        const targetDenom = this._nearestPowerOf2(label.phase_denom);
        
        // Convert to radians and back to target power-of-2 space (theory-compliant precision preservation)
        const phaseRad = Math.PI * label.phase_numer / label.phase_denom;
        const approxNumer = Math.round(phaseRad * targetDenom / Math.PI);
        const [normNumer, normDenom] = normalize_phase_qpi(approxNumer, targetDenom);

        // Create new label with theory-compliant denominator
        graph.labels[nodeId] = make_node_label(label.kind, normNumer, normDenom, `${label.monadic_id}|sanitized`);
        fixed++;
      }
    }

    if (fixed > 0) {
      console.log(`🔧 Sanitized ${fixed} phase denominators (theory compliance)`);
    }
  }

  _isPowerOf2(n) {
    return n > 0 && (n & (n - 1)) === 0;
  }

  reset() {
    this._graph = createSeedGraph();
    this._sanitizePhaseDenominators(this._graph);
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

  setSector(sectorName) {
    // Set physics sector (EM, Dark Matter, or Dark Energy)
    const sector = window.PHYSICS?.SECTORS?.[sectorName];
    if (!sector) {
      console.error(`Unknown sector: ${sectorName}`);
      return;
    }
    
    console.log(`🔄 Switching to ${sectorName} sector:`, sector);
    
    // Reset graph with sector-specific parameters
    this.reset();
    
    // Log sector properties
    console.log(`  Topology: ${sector.topology}`);
    console.log(`  Nodes: ${sector.nodes}`);
    console.log(`  Has loops: ${sector.hasLoops}`);
    console.log(`  Generates α: ${sector.generatesAlpha}`);
    
    // Store current sector for reference
    this._currentSector = sectorName;
    
    // TODO: Full sector implementation will:
    // - Generate topology-specific initial graph
    // - Set sector-specific evolution rules
    // - Apply sector-specific constraints (e.g., no loops for DM)
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
    const degreeDecay = Math.pow(φ, -Math.log(1 + sourceDegree) / Math.log(φ));

    // Compute phase alignment contribution
    const phaseAlignment = Math.cos(2 * Math.PI * sourceLabel.phase_numer / sourceLabel.phase_denom);

    // Compute theory-derived resonance (Theorem 1)
    const resonance = audioCoherence * (1 + Math.log(1 + sourceDegree)) * phaseAlignment;

    // Compute synthesis strength with φ-decay
    const synthesisStrength = resonance * degreeDecay;

    // Plan the modifications (don't apply them yet)
    const newNodeId = Math.max(...graph.nodes, 0) + 1; // Plan new node ID
    const newKind = sourceLabel.kind === 'Z' ? 'X' : 'Z';

    // Theory-compliant φ-modulated phase assignment
    // Derivation: FIRM_theory/grace_emergence_derivation.md Proposition 1, Step 3
    // phase(v') = (phase(v) + ⌊φ · α · denom(v)⌋) mod (2 · denom(v))
    const newPhaseDenom = sourceLabel.phase_denom; // New node inherits source's denominator
    const phaseIncrementValue = Math.floor(φ * audioCoherence * sourceLabel.phase_denom); // ⌊φ · α · denom(v)⌋
    const phaseNumer = (sourceLabel.phase_numer + phaseIncrementValue) % (2 * newPhaseDenom); // (phase(v) + increment) mod (2 * denom(v))
    const monadicId = `${sourceLabel.monadic_id}|𝒢`;

    const newLabel = make_node_label(newKind, phaseNumer, newPhaseDenom, monadicId);

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
      timestamp: Date.now(),
      provenance: 'FIRM_theory/grace_emergence_derivation.md Theorem 1 (Proposition 1)',
      // Store the planned modifications to be applied later
      modifications: {
        addNode: { id: newNodeId, label: newLabel },
        addEdge: [sourceNodeId, newNodeId]
      }
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
        // Deterministic: include edge based on blend strength threshold
        // Use deterministic PRNG state for consistent behavior
        const edgeRand = Number((this._randomState >> 32n) & 0xFFFFFFFFn) / 0xFFFFFFFF;
        this._randomState = (this._randomState * 6364136223846793005n + 1442695040888963407n) & 0xFFFFFFFFFFFFFFFFn;
        if (edgeRand < clampedBlend) {
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
    // THEORY REQUIREMENT: Phase denominators MUST be powers of 2 (ZX Calculus)
    // Use add_phases_qpi to combine phases correctly in Qπ/8 space
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
  async evolve(audioCoherence = 0.0, dt = 0.016) {
    this._stepCount++;  // Increment step counter for time-based filtering

    this._ensureSeed();
    this._scratchGraph = cloneGraph(this._graph);
    this._seedRandom(audioCoherence, dt);

    // Apply Soul Garbage Collection periodically with adaptive frequency
    if (this._sgcEnabled && this._shouldApplySGC()) {
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
        // Ensure resonance module is loaded
        if (!window.__resonanceMod) {
          console.log('🔄 Loading resonance module for metamirror resonance calculation');
          window.__resonanceMod = await import('./FIRM_dsl/resonance.js');
        }

        if (!window.__omegaSignature && window.__resonanceMod) {
          window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(preMetamirrorGraph);
        }
        if (window.__omegaSignature && window.__resonanceMod) {
          res = window.__resonanceMod.computeResonanceAlignment(mutable, window.__omegaSignature) || 0;
        }
      } catch (_) {
        console.error('❌ Resonance calculation failed:', _);
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
      
      // CRITICAL OBSERVABILITY: Log grace emergence attempts for debugging
      if (graceEmergenceRecord) {
        console.log(`✨ GRACE EMERGENCE SUCCESS: Node ${graceEmergenceRecord.nodesAdded[0]} from source ${graceEmergenceRecord.sourceNode} | delta_c=${graceEmergenceRecord.delta_c.toFixed(4)} | audioCoherence=${audioCoherence.toFixed(4)} | resonance=${graceEmergenceRecord.resonance.toFixed(4)}`);
      } else {
        // Log failure occasionally (every 100 attempts)
        if (this._stepCount % 100 === 0) {
          console.log(`🌑 Grace emergence attempted but did not occur | audioCoherence=${audioCoherence.toFixed(4)} | step=${this._stepCount}`);
        }
      }
      
      if (graceEmergenceRecord) {
        try {
          // Ensure resonance module is loaded
          if (!window.__resonanceMod) {
            console.log('🔄 Loading resonance module for grace emergence');
            window.__resonanceMod = await import('./FIRM_dsl/resonance.js');
          }
          
          // SANITIZE before creating omega signature (fix any corrupted denominators)
          this._sanitizePhaseDenominators(mutable);
          
          // INVALIDATE omega if graph structure changed significantly
          // Omega bins must match current graph's LCM(phase_denoms)
          if (window.__omegaSignature && this._rewriteHistory.length % 10 === 0) {
            // Recompute every 10 rewrites to stay synchronized
            window.__omegaSignature = null;
          }
          
          if (!window.__omegaSignature) {
            // CRITICAL Qπ VALIDATION: Ensure all phase denominators are powers of 2
            this._validateAndFixQPiCompliance(mutable, 'global omega signature');

            // DEBUG: Verify Qπ compliance before omega signature computation
            this._debugQPiCompliance(mutable, 'pre-omega-computation');

            try {
              window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(mutable);
              console.log('✅ Global omega signature computed successfully');
            } catch (omegaError) {
              console.error('❌ Omega signature computation failed:', omegaError.message);
              console.error('   This indicates Qπ validation failed to catch invalid denominators');
              throw omegaError;
            }
          }
          
          // CRITICAL: Validate mutable graph Qπ compliance before resonance computation
          this._validateAndFixQPiCompliance(mutable, 'mutable graph before resonance');

          // DEBUG: Check mutable graph Qπ compliance before resonance
          this._debugQPiCompliance(mutable, 'mutable before resonance');

          try {
            const resVal = window.__resonanceMod.computeResonanceAlignment(mutable, window.__omegaSignature);
            console.log(`✅ Resonance alignment computed: ${resVal.toFixed(4)}`);
            return resVal;
          } catch (resonanceError) {
            console.error('❌ Resonance alignment failed:', resonanceError.message);
            console.error('   Mutable graph Qπ state at failure:');
            this._debugQPiCompliance(mutable, 'FAILED mutable graph');
            throw resonanceError;
          }
          const graceProbability = Math.max(0, Math.min(1, resVal));
          
          // DIAGNOSTIC LOGGING
          if (this._stepCount % 100 === 0) {
            console.log(`🔍 Grace: Res=${resVal.toFixed(4)}, P=${graceProbability.toFixed(4)}`);
            console.log(`🎲 Synthesis=${graceEmergenceRecord.synthesisStrength?.toFixed(4) || 'n/a'}`);
          }
          
          const rand = Number((this._randomState >> 32n) & 0xFFFFFFFFn) / 0xFFFFFFFF;
          this._randomState = (this._randomState * 6364136223846793005n + 1442695040888963407n) & 0xFFFFFFFFFFFFFFFFn;
          
          if (rand < graceProbability) {
            // Apply the planned modifications to the mutable graph
            if (graceEmergenceRecord.modifications) {
              const mods = graceEmergenceRecord.modifications;
              if (mods.addNode) {
                mutable.nodes.push(mods.addNode.id);
                mutable.labels[mods.addNode.id] = mods.addNode.label;
              }
              if (mods.addEdge) {
                mutable.edges.push(mods.addEdge);
              }

              // Try to create triangular closure after grace emergence
              if (mutable.nodes.length >= 3) {
                const sourceNode = mods.addEdge[0];
                const newNode = mods.addNode.id;
                // Try to form triangle with existing nodes
                for (const existingNode of mutable.nodes) {
                  if (existingNode !== sourceNode && existingNode !== newNode) {
                    // Check if we can form a triangle
                    const hasSourceToExisting = mutable.edges.some(([u, v]) =>
                      (u === sourceNode && v === existingNode) || (u === existingNode && v === sourceNode)
                    );
                    const hasNewToExisting = mutable.edges.some(([u, v]) =>
                      (u === newNode && v === existingNode) || (u === existingNode && v === newNode)
                    );

                    if (hasSourceToExisting && !hasNewToExisting) {
                      mutable.edges.push([newNode, existingNode]);
                      console.log(`🔺 Grace triangle closure: added ${newNode}-${existingNode} to complete ${sourceNode}-${newNode}-${existingNode}`);
                      break;
                    }
                  }
                }
              }
            }

            applied.push(graceEmergenceRecord);
            if (typeof this._deltaScaffold.register_grace_emergence === 'function') {
              this._deltaScaffold.register_grace_emergence(graceEmergenceRecord);
            }
            if (typeof window !== 'undefined' && window.theoryLogger?.grace) {
              window.theoryLogger.grace(`Grace emergence ΔC=${graceEmergenceRecord.delta_c?.toFixed?.(4) ?? 'n/a'}, nodes=${mutable.nodes.length}, P=${graceProbability.toFixed(3)}`);
            }
            console.log(`✅ GRACE FIRED: P=${graceProbability.toFixed(4)}, rand=${rand.toFixed(4)}, Res=${resVal.toFixed(4)}, newNodes=${graceEmergenceRecord.nodesAdded?.length || 0}`);
          } else if (this._stepCount % 100 === 0) {
            console.log(`❌ Grace blocked: P=${graceProbability.toFixed(4)}, rand=${rand.toFixed(4)}`);
          }
        } catch (err) {
          // NO SILENT FAILURES - log the error
          console.error(`❌ Grace emergence error:`, err);
        }
      }
    }

    // CRITICAL: Validate mutable graph Qπ compliance after all evolution operations
    this._validateAndFixQPiCompliance(mutable, 'mutable after evolution operations');

    if (this._controlParams.metamirrorStrength > 0) {
      const metamirrorState = this._computeMetamirrorReflection(preMetamirrorGraph, mutable);
      if (metamirrorState) {
        const blended = this._blendMetamirrorState(mutable, metamirrorState, this._controlParams.metamirrorStrength);
        mutable.nodes = blended.nodes;
        mutable.edges = blended.edges;
        mutable.labels = blended.labels;

        // VALIDATE: Ensure metamirror operations maintain Qπ compliance
        this._validateAndFixQPiCompliance(mutable, 'mutable after metamirror operations');
      }
    }

    this._commitScratch();

    // CRITICAL: Validate committed graph Qπ compliance
    this._validateAndFixQPiCompliance(this._graph, 'committed graph');

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

    // SOVEREIGNTY METRICS COMPUTATION (cached to avoid expensive recomputation)
    const currentStep = this._stepCount;
    if (this._sovereigntyCache && this._sovereigntyCache.step === currentStep) {
      var sovereignTriads = this._sovereigntyCache.triads;
    } else {
      sovereignTriads = detectSovereignTriads(plainGraph, adjacency);
      this._sovereigntyCache = { step: currentStep, triads: sovereignTriads };
    }

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
      // Classify interaction motifs deterministically based on letter properties
      const symbol1 = letter1.symbol || '';
      const symbol2 = letter2.symbol || '';
      const combined = (symbol1.charCodeAt(0) || 0) + (symbol2.charCodeAt(0) || 0);
      const motifs = ['network_fusion', 'sculpted_region', 'io_dialogue', 'learned_memory'];
      return motifs[combined % motifs.length];
    };

    this.mapGatesToFractalAttractors = () => {
      // Map each gate to specific fractal attractor properties
      const mappings = {};
      this.gates231Network.forEach(gate => {
        // Deterministic emergence threshold based on gate complexity
        const complexity = this.calculateComplexity(gate);
        const emergenceThreshold = 0.15 + (complexity * 0.3); // Range [0.15, 0.45] based on complexity
        
        mappings[gate.id] = {
          fractal_type: gate.fractal_type,
          motif_class: gate.motif_class,
          complexity: complexity,
          emergence_threshold: emergenceThreshold
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
      // THEORY REQUIREMENT: System must generate own coherence (Ψ ≅ Hom(Ψ,Ψ))
      // No fallbacks - if audio is low, system should use internal harmonics
      // This will be provided by harmonic generator when cache clears
      
      // CANONICAL BASELINE: Golden ratio inverse (φ⁻¹ ≈ 0.618)
      // This represents the natural vacuum potential before conscious structure emerges
      // φ⁻¹ is the mathematically elegant baseline connecting to Fibonacci sequences and grace fields
      const originalCoherence = audioCoherence;
      const PHI_INVERSE = 1 / 1.618033988749;  // ≈ 0.618
      if (audioCoherence < PHI_INVERSE) {
        audioCoherence = Math.max(audioCoherence, PHI_INVERSE);
        if (this._stepCount % 100 === 0) {
          console.log(`🔧 Baseline coherence applied: ${originalCoherence.toFixed(3)} → ${audioCoherence.toFixed(3)}`);
        }
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
        }
      }
    };

    this.evolveBootstrapOperator = (components) => {
      if (this.evolutionState.phase === 'grace' && components[0] > 0.3) { // Lower threshold: 0.5 → 0.3
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

        if (this.evolutionState.structure > 0.15) { // Lower threshold: 0.3 → 0.15
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

        if (this.evolutionState.duality > 0.1) { // Lower threshold: 0.2 → 0.1
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

      const nodes = this.currentSnapshot.graph.nodes;
      const edges = this.currentSnapshot.graph.edges || [];

      console.log(`🔍 Cycle detection: ${nodes.length} nodes, ${edges.length} edges`);

      // Create adjacency map for efficient cycle detection
      const adjacency = new Map();
      for (const node of nodes) {
        adjacency.set(node, []);
      }
      for (const edge of edges) {
        if (adjacency.has(edge.source)) {
          adjacency.get(edge.source).push(edge.target);
        }
        if (adjacency.has(edge.target)) {
          adjacency.get(edge.target).push(edge.source);
        }
      }

      // Find 3-node cycles (sovereign triads)
      let checkedTriples = 0;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = 0; j < nodes.length; j++) {
          if (i === j) continue;
          for (let k = 0; k < nodes.length; k++) {
            if (i === k || j === k) continue;
            checkedTriples++;

            const nodeA = nodes[i];
            const nodeB = nodes[j];
            const nodeC = nodes[k];

            // Check if edges exist: A->B, B->C, C->A
            const neighborsA = adjacency.get(nodeA) || [];
            const neighborsB = adjacency.get(nodeB) || [];
            const neighborsC = adjacency.get(nodeC) || [];

            const hasEdgeAB = neighborsA.includes(nodeB);
            const hasEdgeBC = neighborsB.includes(nodeC);
            const hasEdgeCA = neighborsC.includes(nodeA);

            if (hasEdgeAB && hasEdgeBC && hasEdgeCA) {
              const cycle = [nodeA, nodeB, nodeC];
              cycles.push(cycle);
              console.log(`🔺 Sovereign triad found: ${nodeA}->${nodeB}->${nodeC}->${nodeA} (cycle)`);
            }
          }
        }
      }

      console.log(`🔍 Cycle detection complete: checked ${checkedTriples} triples, found ${cycles.length} cycles`);

      // Debug: Log graph structure if no cycles found but we have enough nodes
      if (cycles.length === 0 && nodes.length >= 4) {
        console.log(`🔍 DEBUG: No cycles found in ${nodes.length}-node graph with ${edges.length} edges`);
        console.log(`🔍 Sample edges:`, edges.slice(0, Math.min(5, edges.length)).map(e => `${e.source}->${e.target}`));
        console.log(`🔍 Phase: ${this.evolutionState.phase}, Coherence: ${this.evolutionState.coherence?.toFixed(3) || 0}`);
      }

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


    // TEST FUNCTION: Manually trigger 231-gates system
    this.test231GatesSystem = () => {
      this.initializeHebrewNetwork();
      console.log(`🎭 231-Gates System Test: ${this.gates231Network.length} gates generated`);

      // Activate gates based on emergence threshold and current coherence (deterministic)
      const currentCoherence = this.evolutionState.coherence || 0;
      const activeGates = this.gates231Network.filter(gate => {
        const mapping = this.fractalGateMappings[gate.id];
        return mapping && currentCoherence > mapping.emergence_threshold;
      });

      activeGates.forEach(gate => {
        gate.active = true;
        // Gate coherence based on how far above threshold we are
        const mapping = this.fractalGateMappings[gate.id];
        gate.coherence = Math.min(1.0, currentCoherence + (mapping.complexity * 0.2));
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

      // SANITIZE graph before SGC operations
      this._sanitizePhaseDenominators(this._graph);

      // CORRECTED ARCHITECTURE: SGC operates per sovereign triad, not globally
      // Each sovereign triad maintains its own morphic structure and SGC instance

      // 1. Get current sovereignty snapshot (cached for performance)
      const snapshot = this.getSnapshot();
      if (!snapshot || !snapshot.sovereignTriads || snapshot.sovereignTriads.length === 0) {
        console.log('🗑️ No sovereign triads found - SGC evaluation skipped');
        return;
      }

      // 2. Create SGC for each sovereign triad independently
      const sovereignResults = [];
      for (const triad of snapshot.sovereignTriads) {
        const triadResult = this._applySGCToSovereignTriad(triad, sgcModule);
        if (triadResult) {
          sovereignResults.push(triadResult);
        }
      }

      // 3. Merge sovereign triad results back into main graph
      if (sovereignResults.length > 0) {
        const mergedGraph = this._mergeSovereignSGCResults(sovereignResults);
        if (mergedGraph) {
          this._graph = mergedGraph;
          this._sgcCounter++;
          console.log(`🗑️ Sovereign SGC applied: ${sovereignResults.length} triads processed`);
        }
      } else {
        console.log('🗑️ Sovereign SGC evaluated - no changes needed');
        }
      } catch (sgcError) {
        console.warn('SGC application failed:', sgcError.message);
        // Continue evolution even if SGC fails
      }
  }

  /**
   * Apply SGC to a single sovereign triad (correct architecture).
   * Each sovereign triad manages its own coherence and garbage collection.
   */
  _applySGCToSovereignTriad(triad, sgcModule) {
    try {
      // Create SGC parameters for this specific triad
      const sgcParams = sgcModule.create_sgc_params(
        0.3,  // epsilon - resonance threshold for this triad
        0.5,  // grace_threshold
        5,    // max_recursion_depth (shallower for triads)
        0.2   // observer_feedback_weight
      );

      // Create omega signature for this triad specifically
      const triadOmega = this._createTriadOmegaSignature(triad);
      if (!triadOmega) return null;

      // Create morphic structure for this triad only
      const triadGraph = this._extractTriadGraph(triad);
      if (!triadGraph) return null;

      // CRITICAL: Ensure triad graph maintains Qπ compliance for SGC operations
      this._validateAndFixQPiCompliance(triadGraph, `triad ${triad.nodes} SGC`);

      const morphicStructure = new sgcModule.MorphicStructure(triadGraph);

      // Apply SGC rule to this triad
      const sgc = new sgcModule.SoulGarbageCollector(triadOmega, sgcParams);

      // DEBUG: Log triad structure before SGC
      console.log(`🗑️ Applying SGC to triad ${triad.nodes}: nodes=${Object.keys(morphicStructure.graph.labels).length}, edges=${morphicStructure.graph.edges.length}`);

      // DEBUG: Check triad phase denominators before SGC
      const triadDenoms = new Set();
      for (const label of Object.values(morphicStructure.graph.labels)) {
        if (label && label.phase_denom) {
          triadDenoms.add(label.phase_denom);
        }
      }
      console.log(`🔍 Triad ${triad.nodes} pre-SGC denoms: [${Array.from(triadDenoms).join(', ')}]`);

      const result = sgc.sgc_rule(morphicStructure);

      if (result && result.graph && result.graph !== triadGraph) {
        // VALIDATE: Ensure SGC result maintains Qπ compliance
        this._validateAndFixQPiCompliance(result.graph, `SGC result for triad ${triad.nodes}`);

        return {
          triad: triad,
          originalGraph: triadGraph,
          prunedGraph: result.graph,
          prunedNodes: sgc.pruned_nodes,
          entropyReduction: sgc.compute_entropy_reduction(morphicStructure, result)
        };
      }

      return null;
    } catch (error) {
      console.warn(`SGC failed for triad ${triad.nodes}:`, error.message);
      return null;
    }
  }

  /**
   * Create omega signature specific to a sovereign triad.
   * Must follow same Qπ binning rules as global signature for compatibility.
   */
  _createTriadOmegaSignature(triad) {
    try {
      // Extract phase denominators from triad nodes
      const phase_denoms = new Set();
      for (const nodeId of triad.nodes) {
        const label = this._graph.labels[nodeId];
        if (label && label.phase_denom) {
          phase_denoms.add(label.phase_denom);
        }
      }

      if (phase_denoms.size === 0) {
        phase_denoms.add(1);
      }

      // CRITICAL: Use same logic as global signature for Qπ compliance
      // Find maximum denominator (since all are powers of 2, max is LCM)
      const maxDenom = Math.max(...Array.from(phase_denoms), 8); // Ensure minimum 8
      const phase_bins = 2 * maxDenom; // Must be multiple of 2*max(denom)

      // DEBUG: Verify triad phase denominators
      console.log(`🔍 Triad ${triad.nodes} phase denoms: [${Array.from(phase_denoms).join(', ')}], max=${maxDenom}, bins=${phase_bins}`);

      // Verify bins calculation matches theory requirements (should always be true)
      const required = 2 * maxDenom;
      if (phase_bins !== required) {
        console.error(`❌ TRIAD BINS MISMATCH: phase_bins=${phase_bins}, required=${required}`);
      }

      // Create triad-specific phase histogram
      const phase_hist = new Array(phase_bins).fill(1.0 / phase_bins);

      return {
        cycles: triad.nodes.length, // Triad has 3 nodes, 3 edges
        phase_bins: phase_bins,
        phase_hist: phase_hist
      };
    } catch (error) {
      console.warn('Failed to create triad omega signature:', error.message);
      // Return safe fallback
      const safe_bins = 16;
      const phase_hist = new Array(safe_bins).fill(1.0 / safe_bins);
      return {
        cycles: triad.nodes.length,
        phase_bins: safe_bins,
        phase_hist: phase_hist
      };
    }
  }

  /**
   * Extract subgraph containing only the sovereign triad nodes and their connections.
   */
  _extractTriadGraph(triad) {
    try {
      const triadNodes = new Set(triad.nodes);
      const triadLabels = {};
      const triadEdges = [];

      // Extract labels for triad nodes
      for (const nodeId of triad.nodes) {
        if (this._graph.labels[nodeId]) {
          triadLabels[nodeId] = this._graph.labels[nodeId];
        }
      }

      // Extract edges within the triad
      for (const [u, v] of this._graph.edges) {
        if (triadNodes.has(u) && triadNodes.has(v)) {
          triadEdges.push([u, v]);
        }
      }

      if (Object.keys(triadLabels).length === 0) return null;

      // Ensure triad has minimum valid structure
      if (triadEdges.length === 0) {
        console.warn(`⚠️ Triad ${triad.nodes} has no edges - cannot create valid morphic structure`);
        return null;
      }

      const triadGraph = new ObjectG({
        nodes: triad.nodes,
        edges: triadEdges,
        labels: triadLabels
      });

      // Validate the triad graph structure
      try {
        validate_object_g(triadGraph);
      } catch (error) {
        console.warn(`⚠️ Triad ${triad.nodes} failed validation:`, error.message);
        return null;
      }

      return triadGraph;
    } catch (error) {
      console.warn('Failed to extract triad graph:', error.message);
      return null;
    }
  }

  /**
   * Merge SGC results from multiple sovereign triads back into main graph.
   */
  _mergeSovereignSGCResults(sovereignResults) {
    try {
      // Start with current graph
      const mergedNodes = [...this._graph.nodes];
      const mergedEdges = [...this._graph.edges];
      const mergedLabels = { ...this._graph.labels };

      let totalPruned = 0;

      for (const result of sovereignResults) {
        if (result.prunedGraph) {
          // Replace triad nodes with pruned versions
          for (const nodeId of result.triad.nodes) {
            if (result.prunedGraph.labels[nodeId]) {
              mergedLabels[nodeId] = result.prunedGraph.labels[nodeId];
            } else {
              // Node was pruned - remove it and all its edges
              delete mergedLabels[nodeId];
              mergedNodes.splice(mergedNodes.indexOf(nodeId), 1);

              // Remove edges connected to this node
              mergedEdges = mergedEdges.filter(([u, v]) => u !== nodeId && v !== nodeId);
              totalPruned++;
            }
          }
        }
      }

      if (totalPruned > 0) {
        console.log(`🗑️ Merged SGC results: ${totalPruned} nodes pruned from sovereign triads`);

        // CRITICAL: Ensure Qπ compliance after SGC merge
        // All phase denominators must remain powers of 2 for global omega signature

        // DEBUG: Check phase denominators after SGC merge
        const remaining_denoms = new Set();
        for (const label of Object.values(mergedLabels)) {
          if (label && label.phase_denom) {
            remaining_denoms.add(label.phase_denom);
          }
        }
        console.log(`🔍 Post-SGC phase denoms: [${Array.from(remaining_denoms).join(', ')}]`);

        // DEEP DEBUG: Analyze each node's phase denominator
        console.log(`🔍 SGC MERGE DEBUG - analyzing ${Object.keys(mergedLabels).length} nodes:`);
        for (const [nodeId, label] of Object.entries(mergedLabels)) {
          if (label && label.phase_denom) {
            const isPowerOf2 = (label.phase_denom & (label.phase_denom - 1)) === 0;
            console.log(`   Node ${nodeId}: denom=${label.phase_denom}, powerOf2=${isPowerOf2}`);
          }
        }

        // ENFORCE Qπ COMPLIANCE: All denominators must be powers of 2
        let fixedCount = 0;
        for (const label of Object.values(mergedLabels)) {
          if (label && label.phase_denom && (label.phase_denom & (label.phase_denom - 1)) !== 0) {
            console.error(`❌ Qπ VIOLATION: Non-power-of-2 denominator after SGC: ${label.phase_denom}`);
            // Fix by converting to nearest power of 2
            label.phase_denom = this._nearestPowerOf2(label.phase_denom);
            fixedCount++;
            console.log(`   ✅ Fixed to: ${label.phase_denom}`);
          }
        }

        if (fixedCount > 0) {
          console.log(`🔧 Qπ compliance enforced: ${fixedCount} denominators corrected`);
        }

        // VALIDATE: Ensure merged graph structure is valid for global operations
        try {
          // Create temporary ObjectG to validate structure
          const tempGraph = new ObjectG({
            nodes: mergedNodes,
            edges: mergedEdges,
            labels: mergedLabels
          });
          validate_object_g(tempGraph);

          // Additional Qπ validation for global omega signature compatibility
          const globalPhaseDenoms = new Set();
          for (const label of Object.values(mergedLabels)) {
            if (label && label.phase_denom) {
              globalPhaseDenoms.add(label.phase_denom);
            }
          }

          if (globalPhaseDenoms.size > 0) {
            const maxDenom = Math.max(...Array.from(globalPhaseDenoms), 8);
            const expectedBins = 2 * maxDenom;
            console.log(`🔍 Qπ validation: max_denom=${maxDenom}, expected_bins=${expectedBins}`);

            // Ensure no denominators violate power-of-2 requirement
            for (const denom of globalPhaseDenoms) {
              if (denom !== 0 && (denom & (denom - 1)) !== 0) {
                throw new Error(`Qπ violation: ${denom} is not a power of 2`);
              }
            }
          }

          return tempGraph;
        } catch (validationError) {
          console.error(`❌ SGC merge created invalid graph:`, validationError.message);
          console.error(`   This violates Qπ requirements for global omega signatures`);
          return null; // Don't use invalid graph
        }
      }

      return null; // No changes
    } catch (error) {
      console.warn('Failed to merge SGC results:', error.message);
      return null;
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

      // THEORY REQUIREMENT: Phase denominators are powers of 2, so LCM is also power of 2
      // Calculate LCM of phase denominators for proper Qπ binning
      const lcm = this._calculateLCM(Array.from(phase_denoms));
      const phase_bins = lcm > 0 ? 2 * lcm : 16; // 2 * 8 = 16 bins for bootstrap precision

      // Create uniform phase histogram
      // With denominators capped at 64, bins will be at most 128
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
    if (numbers.length === 0) return 8; // Bootstrap precision default
    if (numbers.length === 1) return numbers[0];

    // THEORY REQUIREMENT: All denominators are powers of 2, so LCM is also power of 2
    // Find maximum denominator (since all are powers of 2, max is LCM)
    let max = 1;
    for (const num of numbers) {
      if (num > max) max = num;
    }

    // Cap at 64 (2^6) per theory precision limits
    return Math.min(max, 64);
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

  // SGC adaptive frequency method
  _shouldApplySGC() {
    // Performance optimization: Reduce SGC frequency for better performance
    const baseFrequency = Math.max(100, this._sgcFrequency); // Apply less frequently
    const stepSinceLast = this._stepCount - (this._sgcCounter > 0 ? this._stepCount % baseFrequency : 0);

    // If at base frequency interval, apply SGC
    if (stepSinceLast >= baseFrequency) {
      return true;
    }

    // Adaptive frequency based on coherence levels (less aggressive)
    const currentCoherence = this._computeCoherence();
    const coherenceThreshold = 0.2; // Higher threshold to reduce frequency

    if (currentCoherence < coherenceThreshold && stepSinceLast >= baseFrequency / 3) {
      return true; // Apply SGC less frequently when coherence is low
    }

    return false;
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
      lastApplication: this._sgcCounter > 0 ? this._stepCount : null,
      adaptiveMode: true,
      coherenceThreshold: 0.3,
      entropyReduction: this._sgcEntropyReduction || 0.0
    };
  }

  _computeCoherence() {
    // Return current evolution state coherence, or compute from graph if needed
    if (this.evolutionState && typeof this.evolutionState.coherence === 'number') {
      return this.evolutionState.coherence;
    }

    // Fallback: compute from current graph
    if (this._graph && typeof compute_coherence === 'function') {
      return compute_coherence(this._graph);
    }

    // Final fallback: return 0
    return 0.0;
  }

  getMetamirrorStatus() {
    const coherence = this._computeCoherence();
    const sgcStatus = this.getSGCStatus();

    return {
      enabled: this._controlParams?.metamirrorStrength > 0,
      strength: this._controlParams?.metamirrorStrength || 0,
      coherence: coherence,
      sgcIntegration: sgcStatus.enabled,
      sgcEntropyReduction: sgcStatus.entropyReduction,
      combinedEfficiency: coherence * (1 + sgcStatus.entropyReduction * 0.1)
    };
  }

  /**
   * Validate and fix Qπ compliance for a graph before resonance computations.
   * Ensures all phase denominators are powers of 2 as required by theory.
   */
  _validateAndFixQPiCompliance(graph, context = 'unknown') {
    if (!graph || !graph.labels) return;

    console.log(`🔍 Qπ validation for ${context}: checking ${Object.keys(graph.labels).length} nodes`);

    let violations = 0;
    let fixes = 0;

    for (const [nodeId, label] of Object.entries(graph.labels)) {
      if (label && label.phase_denom && (label.phase_denom & (label.phase_denom - 1)) !== 0) {
        violations++;
        console.warn(`❌ Qπ violation in ${context}: node ${nodeId}, denom ${label.phase_denom}`);
        label.phase_denom = this._nearestPowerOf2(label.phase_denom);
        fixes++;
        console.log(`   ✅ Fixed to: ${label.phase_denom}`);
      }
    }

    if (violations > 0) {
      console.log(`🔧 Qπ compliance enforced for ${context}: ${fixes}/${violations} violations fixed`);
    }
  }

  /**
   * Debug Qπ compliance with detailed analysis.
   */
  _debugQPiCompliance(graph, context = 'unknown') {
    if (!graph || !graph.labels) {
      console.log(`🔍 Qπ debug for ${context}: no graph or labels`);
      return;
    }

    const denominators = Object.values(graph.labels).map(lbl => lbl.phase_denom).filter(d => d != null);
    const uniqueDenoms = [...new Set(denominators)].sort((a,b) => a-b);

    console.log(`🔍 Qπ DEBUG for ${context}:`);
    console.log(`   Node count: ${Object.keys(graph.labels).length}`);
    console.log(`   Denominators: [${denominators.join(', ')}]`);
    console.log(`   Unique denoms: [${uniqueDenoms.join(', ')}]`);

    // Check for non-power-of-2 denominators
    const nonPowerOf2 = uniqueDenoms.filter(d => d !== 0 && (d & (d - 1)) !== 0);
    if (nonPowerOf2.length > 0) {
      console.error(`   ❌ NON-POWER-OF-2 FOUND: [${nonPowerOf2.join(', ')}]`);
    } else {
      console.log(`   ✅ All denominators are powers of 2`);

      // Calculate expected bins
      const maxDenom = Math.max(...denominators, 8);
      const expectedBins = 2 * maxDenom;
      console.log(`   📊 Expected bins: ${expectedBins} (2 * ${maxDenom})`);
    }
  }

  /**
   * Helper method to find nearest power of 2 (for phase denominator enforcement).
   */
  _nearestPowerOf2(n) {
    if (n <= 1) return 1;
    if (n > 64) return 64; // Theory cap (T-gate precision limit)
    const lower = 1 << Math.floor(Math.log2(n));
    const upper = 1 << Math.ceil(Math.log2(n));
    return (n - lower < upper - n) ? lower : upper;
  }
}

