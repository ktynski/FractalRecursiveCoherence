/**
 * resonance_driven_engine.js
 * 
 * TRUE-TO-THEORY implementation using resonance-driven evolution
 * 
 * Theory Foundation (Theory.md + RESONANCE_BREAKTHROUGH.md):
 * - Coherence emerges from RESONANCE CONDITIONS, not brute-force calculations
 * - φ-structured resonance modes drive evolution
 * - Spectral gap γ = λ_max - λ₂ drives convergence rate
 * - No expensive matrix computations needed
 */

import { ObjectG, validate_object_g } from './FIRM_dsl/core.js';
import { compute_coherence } from './FIRM_dsl/coherence.js';
import { phi_zx_to_clifford } from './FIRM_clifford/interface.js';

/**
 * Resonance-Driven ZX Evolution Engine
 * 
 * Theory: Uses φ-structured resonance modes to drive evolution
 * Implementation: O(N) resonance evaluation, not O(N²) matrix computation
 */
export class ResonanceDrivenEngine {
  constructor() {
    this.phi = 1.618033988749; // Golden ratio φ
    this.nu = 1.0 / (2 * Math.PI * this.phi); // ν = 1/(2πφ) per Theory.md
    this.beta = 1.0; // Temperature parameter
    
    // Spectral properties (Theory.md Theorem 2.1.1)
    this.lambdaMax = this.phi; // Dominant eigenvalue
    this.lambda2 = this.phi - 0.1; // Second eigenvalue (spectral gap)
    this.spectralGap = this.lambdaMax - this.lambda2; // γ = λ_max - λ₂
    
    // Current state
    this.time = 0.0;
    this.stepCount = 0;
    this.currentGraph = null;
    this.currentCoherence = 0.0;
    this.resonancePhase = 0.0;
    this.rewriteHistory = []; // Track rewrite operations for metrics
    this._evolutionLock = false; // Prevent concurrent evolution calls
    
    // Resonance parameters
    this.resonanceFrequency = this.phi; // φ-based resonance
    this.resonanceAmplitude = 0.1;
    this.coherenceThreshold = 0.01;
    
    // φ-structured resonance modes (RESONANCE_BREAKTHROUGH.md)
    this.resonanceModes = {
      phi: this.phi,           // Mode 1: φ-wavelength
      phiSquared: this.phi * this.phi, // Mode 2: φ²-wavelength  
      unit: 1.0                // Mode 3: unit wavelength
    };
    
    // Control parameters for compatibility with main.js
    this._controlParams = {
      harmonicFundamentalFrequency: 220.0,
      autonomousEvolutionRate: 0.1,
      fieldBoundaryMin: 1.0,
      fieldBoundaryMax: 10.0,
      fieldBoundaryActivityScale: 0.5,
      naturalObservationDistanceScale: 1.2,
      consciousnessAwarenessThreshold: 0.3,
      consciousnessAwarenessIncrement: 0.01,
      optimalObservationAwarenessModMin: 0.5,
      optimalObservationAwarenessModScale: 0.5,
      optimalObservationFOV: 75.0,
      emergenceRate: { min: 0.1, max: 2.0 },
      targetEmergenceOffset: 0.5,
      targetEmergenceResonanceScale: 0.3
    };
    
    // Soul garbage collection state
    this._soulGarbageCollectionEnabled = false;
    
    // Initialization state
    this._initialized = false;
    
    console.log(`🔬 Resonance-Driven Engine initialized:`);
    console.log(`  Dominant eigenvalue λ_max: ${this.lambdaMax.toFixed(6)}`);
    console.log(`  Spectral gap γ: ${this.spectralGap.toFixed(6)}`);
    console.log(`  Resonance frequency: ${this.resonanceFrequency.toFixed(6)}`);
    console.log(`  Diffusion coefficient ν: ${this.nu.toFixed(6)}`);
    console.log(`  φ-structured modes: φ=${this.resonanceModes.phi.toFixed(3)}, φ²=${this.resonanceModes.phiSquared.toFixed(3)}, 1=${this.resonanceModes.unit.toFixed(3)}`);
    
    // Graph will be initialized by calling initializeGraph() separately
  }
  
  /**
   * Initialize with minimal ZX-diagram
   */
  async initializeGraph() {
    console.log('🔧 Initializing ZX graph...');
    
    // Import normalize_phase_qpi for proper phase normalization
    const { normalize_phase_qpi } = await import('./FIRM_dsl/core.js');
    console.log('🔧 normalize_phase_qpi imported:', typeof normalize_phase_qpi);
    
    // Normalize phases before construction
    const [norm_numer_0, norm_denom_0] = normalize_phase_qpi(0, 8);
    const [norm_numer_1, norm_denom_1] = normalize_phase_qpi(1, 8);
    console.log('🔧 Phase normalization complete');
    
    this.currentGraph = new ObjectG({
      nodes: [0, 1],
      edges: [[0, 1]],
      labels: {
        0: { kind: 'Z', phase_numer: norm_numer_0, phase_denom: norm_denom_0, monadic_id: 'node_0' },
        1: { kind: 'X', phase_numer: norm_numer_1, phase_denom: norm_denom_1, monadic_id: 'node_1' }
      }
    });
    console.log('🔧 Graph created:', !!this.currentGraph);
    
    this.currentCoherence = compute_coherence(this.currentGraph);
    console.log('🔧 Coherence computed:', this.currentCoherence);
    
    this._initialized = true;
    console.log(`✅ Initial graph: ${this.currentGraph.nodes.length} nodes, ${this.currentGraph.edges.length} edges, coherence = ${this.currentCoherence.toFixed(6)}`);
  }
  
  /**
   * Compute φ-structured resonance at position (x, y, z)
   * 
   * Theory: Coherence = density × resonance_factor
   * Implementation: O(1) computation using φ-modes
   */
  computeResonance(x, y, z) {
    // φ-structured resonance modes (RESONANCE_BREAKTHROUGH.md)
    const resonance_phi = Math.cos(x * this.resonanceModes.phi) * 
                         Math.cos(y * this.resonanceModes.phi) * 
                         Math.cos(z * this.resonanceModes.phi);
    
    const resonance_phiSquared = Math.cos(x * this.resonanceModes.phiSquared) * 
                               Math.cos(y * this.resonanceModes.phiSquared) * 
                               Math.cos(z * this.resonanceModes.phiSquared);
    
    const resonance_unit = Math.cos(x * this.resonanceModes.unit) * 
                          Math.cos(y * this.resonanceModes.unit) * 
                          Math.cos(z * this.resonanceModes.unit);
    
    // φ-duality structure: All weights involve 1/φ (golden ratio reciprocal)
    const phiInv = 1.0 / this.phi;
    
    const coherence = phiInv * (1.0 + resonance_phi) +           // φ-mode weighted by 1/φ
                     phiInv * (1.0 + resonance_phiSquared) / 2 + // φ²-mode
                     phiInv * (1.0 + resonance_unit);             // unit-mode weighted by 1/φ
    
    return coherence;
  }
  
  /**
   * Apply resonance-driven evolution with ZX rewrite rules
   * 
   * Theory: Resonance at φ drives emergent complexity via ZX calculus
   * Implementation: Fusion, color-flip, and grace emergence rules
   */
  async applyResonanceEvolution(resonanceFactor) {
    const graph = this.currentGraph;
    
    // Import normalize_phase_qpi for proper phase normalization
    const { normalize_phase_qpi } = await import('./FIRM_dsl/core.js');
    
    // 1. FUSION RULE: Merge same-color spiders
    await this.applyFusionRule(graph, resonanceFactor, normalize_phase_qpi);
    
    // 2. COLOR-FLIP RULE: Z ↔ X transformations (Hadamard)
    await this.applyColorFlipRule(graph, resonanceFactor);
    
    // 3. GRACE EMERGENCE: φ-scaling node addition
    await this.applyGraceEmergence(graph, resonanceFactor, normalize_phase_qpi);
    
    // 4. CYCLE FORMATION: Add edges to create cycles (PERFORMANCE: Only every 10 steps)
    if (this.stepCount % 10 === 0) {
      await this.applyCycleFormation(graph, resonanceFactor);
    }
    
    // 5. CLEANUP: Remove self-loops and invalid edges (PERFORMANCE: Only every 5 steps)
    if (this.stepCount % 5 === 0) {
      this.cleanupGraph(graph);
    }
    
    // 6. Phase evolution (existing)
    for (const nodeId of graph.nodes) {
      if (Math.random() < 0.1) { // 10% chance per node
        const label = graph.labels[nodeId];
        if (label) {
          // Evolve phase based on resonance
          const phaseChange = Math.floor(resonanceFactor * 2);
          const newPhaseNumer = Math.max(0, Math.min(7, label.phase_numer + phaseChange));
          const newPhaseDenom = label.phase_denom;
          
          // CRITICAL: Re-normalize phase after mutation
          const [normPhaseNumer, normPhaseDenom] = normalize_phase_qpi(newPhaseNumer, newPhaseDenom);
          label.phase_numer = normPhaseNumer;
          label.phase_denom = normPhaseDenom;
        }
      }
    }
  }

  /**
   * ZX FUSION RULE: Merge same-color spiders
   * 
   * Theory: Z(α) + Z(β) → Z(α + β) and X(α) + X(β) → X(α + β)
   * Implementation: Find adjacent same-color spiders and merge them
   */
  async applyFusionRule(graph, resonanceFactor, normalize_phase_qpi) {
    const fusionProbability = 0.02 * Math.abs(resonanceFactor); // 2% base chance (lower than grace for growth)
    
    if (Math.random() < fusionProbability) {
      // Find potential fusion candidates (adjacent same-color spiders)
      const fusionCandidates = [];
      
      for (const [src, dst] of graph.edges) {
        const srcLabel = graph.labels[src];
        const dstLabel = graph.labels[dst];
        
        if (srcLabel && dstLabel && srcLabel.kind === dstLabel.kind) {
          fusionCandidates.push([src, dst]);
        }
      }
      
      if (fusionCandidates.length > 0) {
        const [node1, node2] = fusionCandidates[Math.floor(Math.random() * fusionCandidates.length)];
        const label1 = graph.labels[node1];
        const label2 = graph.labels[node2];
        
        // Fuse phases: α + β
        const fusedPhaseNumer = label1.phase_numer * label2.phase_denom + label2.phase_numer * label1.phase_denom;
        const fusedPhaseDenom = label1.phase_denom * label2.phase_denom;
        
        // Normalize fused phase
        const [normPhaseNumer, normPhaseDenom] = normalize_phase_qpi(fusedPhaseNumer, fusedPhaseDenom);
        
        // Update node1 with fused phase (preserve monadic_id)
        graph.labels[node1].phase_numer = normPhaseNumer;
        graph.labels[node1].phase_denom = normPhaseDenom;
        if (!graph.labels[node1].monadic_id) {
          graph.labels[node1].monadic_id = `node_${node1}`;
        }
        
        // CRITICAL: Redirect edges BEFORE removing node2
        for (let i = 0; i < graph.edges.length; i++) {
          if (graph.edges[i][0] === node2) graph.edges[i][0] = node1;
          if (graph.edges[i][1] === node2) graph.edges[i][1] = node1;
        }
        
        // Remove self-loops (node1-node1)
        graph.edges = graph.edges.filter(([src, dst]) => src !== dst);
        
        // NOW remove node2 and its label
        graph.nodes = graph.nodes.filter(n => n !== node2);
        delete graph.labels[node2];
        
        this.cleanupGraph(graph); // Immediate cleanup
        this._addRewriteOperation('fusion');
        console.log(`🔥 FUSION: Merged ${node1} + ${node2} → ${node1} (phase=${normPhaseNumer}/${normPhaseDenom})`);
      }
    }
  }

  /**
   * ZX COLOR-FLIP RULE: Z ↔ X transformations (Hadamard)
   * 
   * Theory: Z(α) ↔ X(α) (basis change)
   * Implementation: Randomly flip spider types with phase preservation
   */
  async applyColorFlipRule(graph, resonanceFactor) {
    const flipProbability = 0.03 * Math.abs(resonanceFactor); // 3% base chance
    
    if (Math.random() < flipProbability) {
      // Find a random node to flip
      const nodeId = graph.nodes[Math.floor(Math.random() * graph.nodes.length)];
      const label = graph.labels[nodeId];
      
      if (label) {
        const oldKind = label.kind;
        const newKind = oldKind === 'Z' ? 'X' : 'Z';
        
        // Flip spider type (phase preserved)
        label.kind = newKind;
        
        this._addRewriteOperation('color_flip');
        console.log(`🔄 COLOR-FLIP: ${nodeId} ${oldKind} → ${newKind} (phase=${label.phase_numer}/${label.phase_denom})`);
      }
    }
  }

  /**
   * GRACE EMERGENCE: φ-scaling node addition
   * 
   * Theory: 𝒢 : ∅ → Ψ with φ-scaling |𝒢ⁿ⁺¹| = φ|𝒢ⁿ|
   * Implementation: Add new node with φ-modulated phase
   */
  async applyGraceEmergence(graph, resonanceFactor, normalize_phase_qpi) {
    const graceProbability = 0.10 * Math.abs(resonanceFactor); // 10% base chance (higher than fusion for growth)
    
    if (Math.random() < graceProbability) {
      // Generate unique node ID to prevent duplicates
      let newNodeId = Date.now() + Math.floor(Math.random() * 1000);
      while (graph.nodes.includes(newNodeId)) {
        newNodeId = Date.now() + Math.floor(Math.random() * 1000);
      }
      
      const spiderType = Math.random() < 0.5 ? 'Z' : 'X';
      
      // φ-scaling phase assignment
      const phi = 1.618033988749; // Golden ratio
      const basePhase = Math.floor(Math.random() * 8);
      const gracePhase = Math.floor(basePhase * phi) % 8;
      
      // Add grace node
      graph.nodes.push(newNodeId);
      graph.labels[newNodeId] = {
        kind: spiderType,
        phase_numer: gracePhase,
        phase_denom: 8,
        monadic_id: `grace_${newNodeId}`
      };
      
      // DEBUG: Verify label creation
      console.log(`🔧 DEBUG: Created label for node ${newNodeId}:`, graph.labels[newNodeId]);
      console.log(`🔧 DEBUG: Total labels after creation:`, Object.keys(graph.labels).length);
      
      // Connect to existing node (prefer high-degree nodes)
      if (graph.nodes.length > 1) {
        const nodeDegrees = graph.nodes.map(nodeId => {
          return graph.edges.filter(([src, dst]) => src === nodeId || dst === nodeId).length;
        });
        const maxDegree = Math.max(...nodeDegrees);
        const highDegreeNodes = graph.nodes.filter((_, i) => nodeDegrees[i] === maxDegree);
        const targetNode = highDegreeNodes[Math.floor(Math.random() * highDegreeNodes.length)];
        
        if (targetNode !== newNodeId) {
          graph.edges.push([newNodeId, targetNode]);
          // REMOVED: Immediate cleanup - let main evolution cleanup handle it
          // this.cleanupGraph(graph); // Immediate cleanup
          this._addRewriteOperation('grace_emergence');
          console.log(`🌟 GRACE: Added node ${newNodeId} (φ-phase=${gracePhase}/8) → ${targetNode}`);
        }
      }
    }
  }
  
  /**
   * Resonance-driven evolution step
   * 
   * Theory: ∂ρ/∂t = -grad_g ℱ[ρ] converges to 𝒞ρ_∞ = λ_max ρ_∞
   * Implementation: Resonance-driven evolution without matrix computation
   */
  async evolve(dt = 0.016) {
    // Prevent concurrent evolution calls
    if (this._evolutionLock) {
      console.warn('⚠️ Evolution already in progress, skipping call');
      return { coherence: this.currentCoherence, step: this.stepCount };
    }
    
    this._evolutionLock = true;
    
    try {
      // Ensure engine is initialized
      if (!this._initialized || !this.currentGraph) {
        console.warn('⚠️ Engine not initialized, skipping evolution step');
        return {
          time: this.time,
          step: this.stepCount,
          coherence: this.currentCoherence || 0.0,
          resonancePhase: this.resonancePhase,
          spectralGap: this.spectralGap,
          evolutionProbability: 0.0,
          resonanceFactor: 0.0
        };
      }
    
    // Update resonance phase
    this.resonancePhase += this.resonanceFrequency * dt;
    
    // Ensure all phases are Qπ-normalized before coherence computation
    await this._ensurePhaseNormalization();
    
    // DEBUG: Validate graph structure before coherence computation
    const invalidEdges = this.currentGraph.edges.filter(([src, dst]) => 
      !this.currentGraph.nodes.includes(src) || !this.currentGraph.nodes.includes(dst)
    );
    if (invalidEdges.length > 0) {
      console.error(`❌ Invalid edges in evolve():`, {
        invalidEdges: invalidEdges,
        nodes: this.currentGraph.nodes,
        allEdges: this.currentGraph.edges
      });
      // Remove invalid edges to prevent crashes
      const originalEdgeCount = this.currentGraph.edges.length;
      this.currentGraph.edges = this.currentGraph.edges.filter(([src, dst]) => 
        this.currentGraph.nodes.includes(src) && this.currentGraph.nodes.includes(dst)
      );
      
      // Track rewrite operation if edges were removed
      if (this.currentGraph.edges.length < originalEdgeCount) {
        this._addRewriteOperation('remove_invalid_edges');
      }
    }
    
    // Compute current coherence
    const currentCoherence = compute_coherence(this.currentGraph);
    
    // Spectral resonance condition (Theory.md)
    const resonanceFactor = Math.sin(this.resonancePhase);
    const coherenceGap = this.lambdaMax - currentCoherence;
    
    // Evolution probability based on spectral gap
    const evolutionProbability = Math.min(1.0, coherenceGap / this.spectralGap);
    
    // Apply resonance-driven evolution
    if (Math.random() < evolutionProbability) {
      await this.applyResonanceEvolution(resonanceFactor);
    }
    
    // Update time and step count
    this.time += dt;
    this.stepCount++;
    
    // Debug logging
    if (this.stepCount % 100 === 0) {
      console.log(`⏰ Resonance step ${this.stepCount}: coherence = ${currentCoherence.toFixed(6)}, gap = ${coherenceGap.toFixed(6)}, resonance = ${resonanceFactor.toFixed(3)}`);
    }
    
    return {
      time: this.time,
      step: this.stepCount,
      coherence: currentCoherence,
      resonancePhase: this.resonancePhase,
      spectralGap: this.spectralGap,
      evolutionProbability: evolutionProbability,
      resonanceFactor: resonanceFactor
    };
    } catch (error) {
      console.error('❌ Error in evolution step:', error);
      return {
        time: this.time,
        step: this.stepCount,
        coherence: this.currentCoherence || 0.0,
        resonancePhase: this.resonancePhase,
        spectralGap: this.spectralGap,
        evolutionProbability: 0.0,
        resonanceFactor: 0.0
      };
    } finally {
      // Always release the lock
      this._evolutionLock = false;
    }
  }
  
  /**
   * Map ZX graph to Clifford field using resonance
   * 
   * Theory: Field emerges from resonance structure, not explicit computation
   */
  mapToCliffordField() {
    // Handle uninitialized state
    if (!this._initialized || !this.currentGraph) {
      console.log('⚠️ mapToCliffordField: Uninitialized state', {
        initialized: this._initialized,
        hasGraph: !!this.currentGraph
      });
      return {
        payload: {
          components: new Array(16).fill(0),
          algebra: 'Cl(1,3)'
        }
      };
    }
    
    console.log('🔧 mapToCliffordField: Generating field from graph', {
      nodeCount: this.currentGraph.nodes.length,
      edgeCount: this.currentGraph.edges.length
    });
    
    const graph = this.currentGraph;
    const nodeCount = graph.nodes.length;
    const edgeCount = graph.edges.length;
    
    // Base field components (Clifford Cl(1,3) = 16 components)
    const components = new Array(16).fill(0);
    
    // Resonance-driven field generation
    for (let i = 0; i < 16; i++) {
      // Use resonance modes to generate field components
      const x = (i % 4) * 0.5;
      const y = Math.floor(i / 4) * 0.5;
      const z = this.time * 0.1;
      
      // Compute resonance at this position
      const resonance = this.computeResonance(x, y, z);
      
      // Field component based on resonance and graph structure
      components[i] = resonance * (1.0 + nodeCount * 0.1) * (1.0 + edgeCount * 0.05);
    }
    
    // Add time-varying base field components
    const timePhase = this.time * this.phi;
    components[0] += Math.sin(timePhase) * 0.1; // Scalar component
    components[1] += Math.cos(timePhase) * 0.1; // Vector component
    components[2] += Math.sin(timePhase * this.phi) * 0.1; // Bivector component
    
    const field = {
      payload: {
        components: components,
        algebra: 'Cl(1,3)'
      }
    };
    
    // DEBUG: Log field generation occasionally
    if (this.stepCount % 1000 === 0) {
      console.log('🌊 Field generated:', {
        step: this.stepCount,
        nodeCount: nodeCount,
        edgeCount: edgeCount,
        components: components.slice(0, 4).map(c => c.toFixed(3))
      });
    }
    
    return field;
  }

  /**
   * CYCLE FORMATION: Add edges to create cycles for sovereignty emergence
   * 
   * Theory: Cycles are necessary for sovereign triad formation
   * Implementation: Add edges between nodes to create 3-node cycles
   */
  async applyCycleFormation(graph, resonanceFactor) {
    const cycleProbability = 0.15 * Math.abs(resonanceFactor); // 15% base chance
    const randomValue = Math.random();
    
    console.log(`🔺 CYCLE CHECK: prob=${cycleProbability.toFixed(3)}, random=${randomValue.toFixed(3)}, nodes=${graph.nodes.length}`);
    
    if (randomValue < cycleProbability && graph.nodes.length >= 3) {
      // Find potential cycle formation opportunities
      // PERFORMANCE: Limit search to first 20 nodes to prevent O(n³) explosion
      const searchLimit = Math.min(20, graph.nodes.length);
      const potentialCycles = [];
      
      for (let i = 0; i < searchLimit; i++) {
        for (let j = i + 1; j < searchLimit; j++) {
          for (let k = j + 1; k < searchLimit; k++) {
            const node1 = graph.nodes[i];
            const node2 = graph.nodes[j];
            const node3 = graph.nodes[k];
            
            // Check if any two edges exist
            const hasEdge12 = graph.edges.some(([src, dst]) => 
              (src === node1 && dst === node2) || (src === node2 && dst === node1));
            const hasEdge23 = graph.edges.some(([src, dst]) => 
              (src === node2 && dst === node3) || (src === node3 && dst === node2));
            const hasEdge31 = graph.edges.some(([src, dst]) => 
              (src === node3 && dst === node1) || (src === node1 && dst === node3));
            
            const edgeCount = [hasEdge12, hasEdge23, hasEdge31].filter(Boolean).length;
            if (edgeCount === 2) {
              // Missing one edge to complete the triangle
              const missingEdge = !hasEdge12 ? [node1, node2] : 
                                 !hasEdge23 ? [node2, node3] : [node3, node1];
              potentialCycles.push({
                nodes: [node1, node2, node3],
                missingEdge: missingEdge
              });
            }
          }
        }
      }
      
      if (potentialCycles.length > 0) {
        // Choose a random potential cycle to complete
        const cycle = potentialCycles[Math.floor(Math.random() * potentialCycles.length)];
        const [src, dst] = cycle.missingEdge;
        
        // Add the missing edge to complete the triangle
        graph.edges.push([src, dst]);
        this.cleanupGraph(graph); // Immediate cleanup
        
        this._addRewriteOperation('cycle_formation');
        console.log(`🔺 CYCLE: Completed triangle ${cycle.nodes.join('-')} with edge [${src}, ${dst}]`);
      } else {
        // No potential cycles, add a random edge between unconnected nodes
        const unconnectedPairs = [];
        for (let i = 0; i < graph.nodes.length; i++) {
          for (let j = i + 1; j < graph.nodes.length; j++) {
            const node1 = graph.nodes[i];
            const node2 = graph.nodes[j];
            
            const hasEdge = graph.edges.some(([src, dst]) => 
              (src === node1 && dst === node2) || (src === node2 && dst === node1));
            
            if (!hasEdge) {
              unconnectedPairs.push([node1, node2]);
            }
          }
        }
        
        if (unconnectedPairs.length > 0) {
          const [src, dst] = unconnectedPairs[Math.floor(Math.random() * unconnectedPairs.length)];
          graph.edges.push([src, dst]);
          this.cleanupGraph(graph); // Immediate cleanup
          
          this._addRewriteOperation('edge_addition');
          console.log(`🔗 EDGE: Added edge [${src}, ${dst}] for cycle formation`);
        }
      }
    }
  }

  /**
   * CLEANUP: Remove self-loops and invalid edges
   * 
   * Theory: ZX graphs must not have self-loops
   * Implementation: Remove any edges where src === dst
   */
  cleanupGraph(graph) {
    const originalNodeCount = graph.nodes.length;
    const originalEdgeCount = graph.edges.length;
    
    // Remove duplicate nodes (keep first occurrence)
    const uniqueNodes = [];
    const seenNodes = new Set();
    for (const nodeId of graph.nodes) {
      if (!seenNodes.has(nodeId)) {
        uniqueNodes.push(nodeId);
        seenNodes.add(nodeId);
      } else {
        console.log(`🔧 DEBUG: Removing duplicate node ${nodeId}`);
      }
    }
    graph.nodes = uniqueNodes;
    
    // Remove labels for non-existent nodes
    // CRITICAL: Convert nodeIds to numbers for proper comparison
    const nodeSet = new Set(graph.nodes.map(n => Number(n)));
    const labelsBefore = Object.keys(graph.labels).length;
    for (const nodeId of Object.keys(graph.labels)) {
      const numericNodeId = Number(nodeId);
      if (!nodeSet.has(numericNodeId)) {
        console.log(`🔧 DEBUG: Removing label for non-existent node ${nodeId}`);
        delete graph.labels[nodeId];
      }
    }
    const labelsAfter = Object.keys(graph.labels).length;
    if (labelsBefore !== labelsAfter) {
      console.log(`🔧 DEBUG: Labels changed from ${labelsBefore} to ${labelsAfter} during cleanup`);
    }
    
    // Remove self-loops
    graph.edges = graph.edges.filter(([src, dst]) => src !== dst);
    
    // Remove edges to non-existent nodes
    graph.edges = graph.edges.filter(([src, dst]) => 
      nodeSet.has(src) && nodeSet.has(dst)
    );
    
    const removedNodes = originalNodeCount - graph.nodes.length;
    const removedEdges = originalEdgeCount - graph.edges.length;
    if (removedNodes > 0 || removedEdges > 0) {
      console.log(`🧹 CLEANUP: Removed ${removedNodes} duplicate nodes, ${removedEdges} invalid edges`);
    }
  }
  
  /**
   * Detect sovereign triads (3-node cycles with φ-harmony)
   * 
   * Theory: Sovereign triads are coherent source-self-relation triangles
   * Implementation: Find 3-node cycles with φ-harmony + type diversity + balance
   */
  detectSovereignTriads(graph) {
    const triads = [];
    
    // PERFORMANCE: Limit search to first 20 nodes to prevent O(n³) explosion
    const searchLimit = Math.min(20, graph.nodes.length);
    
    // Find all 3-node cycles
    for (let i = 0; i < searchLimit; i++) {
      for (let j = i + 1; j < searchLimit; j++) {
        for (let k = j + 1; k < searchLimit; k++) {
          const node1 = graph.nodes[i];
          const node2 = graph.nodes[j];
          const node3 = graph.nodes[k];
          
          // Check if they form a triangle
          const hasEdge12 = graph.edges.some(([src, dst]) => 
            (src === node1 && dst === node2) || (src === node2 && dst === node1));
          const hasEdge23 = graph.edges.some(([src, dst]) => 
            (src === node2 && dst === node3) || (src === node3 && dst === node2));
          const hasEdge31 = graph.edges.some(([src, dst]) => 
            (src === node3 && dst === node1) || (src === node1 && dst === node3));
          
          if (hasEdge12 && hasEdge23 && hasEdge31) {
            const label1 = graph.labels[node1];
            const label2 = graph.labels[node2];
            const label3 = graph.labels[node3];
            
            if (label1 && label2 && label3) {
              // Check φ-harmony (phases in golden ratio relationship)
              const phase1 = label1.phase_numer / label1.phase_denom;
              const phase2 = label2.phase_numer / label2.phase_denom;
              const phase3 = label3.phase_numer / label3.phase_denom;
              
              const phi = 1.618033988749;
              const phiHarmony = Math.abs(phase2 - phase1 * phi) < 0.1 || 
                                Math.abs(phase3 - phase2 * phi) < 0.1 ||
                                Math.abs(phase1 - phase3 * phi) < 0.1;
              
              // Check type diversity (mix of Z and X)
              const types = [label1.kind, label2.kind, label3.kind];
              const typeDiversity = new Set(types).size > 1;
              
              // Check balance (not all same type)
              const balance = !types.every(t => t === types[0]);
              
              if (phiHarmony && typeDiversity && balance) {
                triads.push({
                  nodes: [node1, node2, node3],
                  phases: [phase1, phase2, phase3],
                  types: types,
                  coherence: (phiHarmony ? 1 : 0) + (typeDiversity ? 1 : 0) + (balance ? 1 : 0)
                });
              }
            }
          }
        }
      }
    }
    
    return triads;
  }

  /**
   * Get current system state snapshot
   */
  async getSnapshot() {
    // Handle uninitialized state
    if (!this._initialized || !this.currentGraph) {
      return {
        time: this.time,
        step: this.stepCount,
        graph: { nodes: [], edges: [], labels: {} },
        coherence: 0.0,
        cliffordField: null,
        resonancePhase: this.resonancePhase,
        spectralGap: this.spectralGap,
        lambdaMax: this.lambdaMax,
        resonanceModes: this.resonanceModes
      };
    }
    
    // Ensure phases are normalized before coherence computation
    await this._ensurePhaseNormalization();
    
    const graph = this.currentGraph;
    
    // DEBUG: Validate graph structure before coherence computation
    if (this.stepCount % 1000 === 0) {
      const invalidEdges = graph.edges.filter(([src, dst]) => 
        !graph.nodes.includes(src) || !graph.nodes.includes(dst)
      );
      if (invalidEdges.length > 0) {
        console.error(`❌ Invalid edges detected:`, {
          invalidEdges: invalidEdges,
          nodes: graph.nodes,
          allEdges: graph.edges
        });
      }
    }
    
    const coherence = compute_coherence(graph);
    const cliffordField = this.mapToCliffordField();
    
    // Detect sovereign triads
    const sovereignTriads = this.detectSovereignTriads(graph);
    
    return {
      time: this.time,
      step: this.stepCount,
      graph: graph,
      coherence: coherence,
      cliffordField: cliffordField,
      resonancePhase: this.resonancePhase,
      spectralGap: this.spectralGap,
      lambdaMax: this.lambdaMax,
      resonanceModes: this.resonanceModes,
      sovereignTriads: sovereignTriads,
      sovereigntyLevel: sovereignTriads.length
    };
  }
  
  /**
   * Get grace magnitude (φ-based scaling)
   */
  get graceMagnitude() {
    return this.phi;
  }
  
  /**
   * Enable soul garbage collection
   * Theory: 𝒮-GC maintains coherence by removing incoherent structures
   */
  enableSoulGarbageCollection() {
    this._soulGarbageCollectionEnabled = true;
    console.log('🗑️ Soul Garbage Collection enabled in resonance-driven engine');
  }
  
  /**
   * Disable soul garbage collection
   */
  disableSoulGarbageCollection() {
    this._soulGarbageCollectionEnabled = false;
    console.log('🗑️ Soul Garbage Collection disabled in resonance-driven engine');
  }
  
  /**
   * Check if soul garbage collection is enabled
   */
  isSoulGarbageCollectionEnabled() {
    return this._soulGarbageCollectionEnabled;
  }
  
  /**
   * Check if engine is initialized
   */
  isInitialized() {
    return this._initialized;
  }
  
  /**
   * Ensure all phases in current graph are Qπ-normalized
   */
  async _ensurePhaseNormalization() {
    if (!this.currentGraph || !this.currentGraph.labels) return;
    
    const { normalize_phase_qpi } = await import('./FIRM_dsl/core.js');
    
    for (const nodeId in this.currentGraph.labels) {
      const label = this.currentGraph.labels[nodeId];
      if (label && label.phase_numer !== undefined && label.phase_denom !== undefined) {
        const [normPhaseNumer, normPhaseDenom] = normalize_phase_qpi(label.phase_numer, label.phase_denom);
        label.phase_numer = normPhaseNumer;
        label.phase_denom = normPhaseDenom;
      }
    }
  }
  
  /**
   * Evolve from audio coherence (compatibility method)
   * Theory: Audio coherence drives resonance evolution
   */
  evolveFromAudioCoherence(audioCoherence, dt = 0.016) {
    // Use audio coherence to modulate resonance frequency
    this.resonanceFrequency = this.phi * (1.0 + audioCoherence * 0.1);
    return this.evolve(dt);
  }
  
  /**
   * Evolve system (compatibility method)
   * Theory: System evolution via resonance-driven dynamics
   */
  async evolveSystem(coherence, deltaTime = 0.016) {
    // Use coherence to modulate evolution probability
    this.coherenceThreshold = Math.max(0.01, coherence);
    const result = await this.evolve(deltaTime);
    
    // Return expected structure for compatibility
    return {
      phase: 'resonance-driven',
      coherence: result.coherence || 0.0,
      structure: result.coherence || 0.0,
      volume: Math.abs(result.resonanceFactor || 0.0),
      emergentLetters: []
    };
  }
  
  /**
   * Modulate from graph state (compatibility method)
   * Theory: Graph state modulates audio output
   */
  modulateFromGraphState() {
    if (!this.currentGraph) return null;
    
    const nodeCount = this.currentGraph.nodes.length;
    const edgeCount = this.currentGraph.edges.length;
    const complexity = nodeCount + edgeCount;
    
    // Return modulation parameters based on graph complexity
    return {
      frequency: this.resonanceFrequency * (1.0 + complexity * 0.01),
      amplitude: Math.min(1.0, complexity * 0.1),
      phase: this.resonancePhase
    };
  }

  /**
   * Get rewrite history for metrics tracking
   * Returns array of rewrite operations performed during evolution
   */
  getRewriteHistory() {
    return this.rewriteHistory;
  }

  /**
   * Add rewrite operation to history
   * Called when graph modifications occur during evolution
   */
  _addRewriteOperation(operation) {
    this.rewriteHistory.push({
      timestamp: this.time,
      step: this.stepCount,
      operation: operation,
      nodeCount: this.currentGraph?.nodes?.length || 0,
      edgeCount: this.currentGraph?.edges?.length || 0
    });
    
    // Keep history bounded to prevent memory issues
    if (this.rewriteHistory.length > 1000) {
      this.rewriteHistory = this.rewriteHistory.slice(-500);
    }
  }
}
