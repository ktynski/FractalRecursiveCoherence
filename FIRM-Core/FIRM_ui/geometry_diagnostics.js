/**
 * geometry_diagnostics.js
 * 
 * Real-time diagnostic tools for interpreting Clifford field visualization.
 * 
 * Usage: Load in browser, then call window.analyzeVisibleGeometry()
 * 
 * Specification: FIRM_theory/clifford_visualization_physics_interpretation.md
 */

window.analyzeVisibleGeometry = function() {
  console.log('\n═══════════════════════════════════════════════════');
  console.log('    CLIFFORD FIELD GEOMETRY ANALYSIS');
  console.log('═══════════════════════════════════════════════════\n');
  
  // Get current Clifford field
  const field = window.renderer?.lastCliffordField;
  if (!field || !field.payload) {
    console.error('❌ No Clifford field available. Is rendering active?');
    return null;
  }
  
  const c = field.payload.components;
  if (!c || c.length !== 16) {
    console.error('❌ Invalid Clifford field structure');
    return null;
  }
  
  // ========================================
  // STEP 1: Component Magnitude Analysis
  // ========================================
  
  const analysis = {
    scalar: Math.abs(c[0]),
    vectors: {
      total: Math.sqrt(c[1]**2 + c[2]**2 + c[3]**2 + c[4]**2),
      e0: Math.abs(c[1]),
      e1: Math.abs(c[2]),
      e2: Math.abs(c[3]),
      e3: Math.abs(c[4])
    },
    bivectors: {
      total: Math.sqrt(c[5]**2 + c[6]**2 + c[7]**2 + c[8]**2 + c[9]**2 + c[10]**2),
      e01: Math.abs(c[5]),
      e02: Math.abs(c[6]),
      e03: Math.abs(c[7]),
      e12: Math.abs(c[8]),  // xy-plane rotation
      e13: Math.abs(c[9]),  // xz-plane rotation
      e23: Math.abs(c[10])  // yz-plane rotation
    },
    trivectors: {
      total: Math.sqrt(c[11]**2 + c[12]**2 + c[13]**2 + c[14]**2),
      e012: Math.abs(c[11]),
      e013: Math.abs(c[12]),
      e023: Math.abs(c[13]),
      e123: Math.abs(c[14])
    },
    pseudoscalar: Math.abs(c[15])
  };
  
  console.log('📊 MULTIVECTOR GRADE MAGNITUDES:');
  console.log(`  Grade 0 (Scalar):      ${analysis.scalar.toFixed(4)}`);
  console.log(`  Grade 1 (Vectors):     ${analysis.vectors.total.toFixed(4)}`);
  console.log(`  Grade 2 (Bivectors):   ${analysis.bivectors.total.toFixed(4)} ← CIRCLES/SPHERES`);
  console.log(`  Grade 3 (Trivectors):  ${analysis.trivectors.total.toFixed(4)}`);
  console.log(`  Grade 4 (Pseudoscalar): ${analysis.pseudoscalar.toFixed(4)}\n`);
  
  // Find dominant grade
  const gradeComparison = {
    'Grade-0 (Scalar)': analysis.scalar,
    'Grade-1 (Vectors)': analysis.vectors.total,
    'Grade-2 (Bivectors)': analysis.bivectors.total,
    'Grade-3 (Trivectors)': analysis.trivectors.total,
    'Grade-4 (Pseudoscalar)': analysis.pseudoscalar
  };
  
  const dominant = Object.entries(gradeComparison)
    .reduce((max, [grade, mag]) => mag > max.magnitude ? {grade, magnitude: mag} : max, 
            {grade: 'none', magnitude: 0});
  
  console.log(`🎯 DOMINANT GRADE: ${dominant.grade} (magnitude: ${dominant.magnitude.toFixed(4)})\n`);
  
  // ========================================
  // STEP 2: Geometric Feature Interpretation
  // ========================================
  
  console.log('🔍 OBSERVED GEOMETRIC FEATURES:\n');
  
  if (analysis.scalar > 0.2) {
    console.log('  ✓ UNIFORM COLOR REGIONS');
    console.log('    → Scalar field dominance');
    console.log('    → Physics: Mass/energy density, vacuum expectation value');
    console.log('    → ZX Source: Z-spiders with low phases\n');
  }
  
  if (analysis.bivectors.total > 0.3) {
    console.log('  ✓ CIRCLES/SPHERES WITH RADIAL EMISSION');
    console.log('    → Bivector field sources');
    console.log('    → Physics: Magnetic dipoles, EM radiation, angular momentum');
    console.log('    → ZX Source: X-spiders with non-zero phases');
    
    // Identify strongest bivector plane
    const bivPlanes = {
      'xy-plane (e12)': analysis.bivectors.e12,
      'xz-plane (e13)': analysis.bivectors.e13,
      'yz-plane (e23)': analysis.bivectors.e23
    };
    const strongestPlane = Object.entries(bivPlanes)
      .reduce((max, [plane, mag]) => mag > max.mag ? {plane, mag} : max, {plane: 'none', mag: 0});
    
    console.log(`    → Dominant plane: ${strongestPlane.plane} (${strongestPlane.mag.toFixed(4)})\n`);
  }
  
  if (analysis.vectors.total > 0.2) {
    console.log('  ✓ DIRECTIONAL FLOWS/GRADIENTS');
    console.log('    → Vector field components');
    console.log('    → Physics: Electric field, momentum density');
    console.log('    → ZX Source: Z-spiders with high connectivity\n');
  }
  
  if (analysis.bivectors.total > 0.1 && analysis.vectors.total > 0.1) {
    console.log('  ✓ GRID/LATTICE PATTERNS');
    console.log('    → Polynomial interference from multiple grades');
    console.log('    → Physics: Standing waves, photonic crystals');
    console.log('    → Spacing ≈ 2π/field_magnitude (dynamic)\n');
  }
  
  if (analysis.trivectors.total > 0.1) {
    console.log('  ✓ COMPLEX 3D TEXTURES');
    console.log('    → Trivector (grade-3) contributions');
    console.log('    → Physics: Higher-order field coupling');
    console.log('    → ZX Source: Multi-edge entanglement structures\n');
  }
  
  // ========================================
  // STEP 3: Correlate with ZX Graph
  // ========================================
  
  const zxSnap = window.zxEvolutionEngine?.getSnapshot();
  if (zxSnap) {
    const graph = zxSnap.graph;
    const zCount = Object.values(graph.labels).filter(l => l.kind === 'Z').length;
    const xCount = Object.values(graph.labels).filter(l => l.kind === 'X').length;
    
    console.log('🔗 ZX GRAPH STRUCTURE:\n');
    console.log(`  Z-spiders: ${zCount} → Scalar/rotor sources`);
    console.log(`  X-spiders: ${xCount} → Bivector/sphere sources`);
    console.log(`  Total nodes: ${graph.nodes.length}`);
    console.log(`  Edges: ${graph.edges.length}`);
    console.log(`  Coherence C(G): ${zxSnap.coherence.toFixed(4)}\n`);
    
    // Correlation analysis
    console.log('📈 CORRELATION ANALYSIS:\n');
    
    if (xCount > zCount) {
      console.log('  → More X than Z → Expect CIRCULAR features to dominate');
    } else if (zCount > xCount) {
      console.log('  → More Z than X → Expect UNIFORM regions to dominate');
    } else {
      console.log('  → Balanced Z/X → Expect MIXED geometry');
    }
    
    // Phase analysis
    const phases = Object.values(graph.labels).map(l => 
      (l.phase_numer / l.phase_denom) * Math.PI
    );
    const avgPhase = phases.reduce((sum, p) => sum + p, 0) / phases.length;
    const phaseVar = phases.reduce((sum, p) => sum + (p - avgPhase)**2, 0) / phases.length;
    
    console.log(`  → Average phase: ${avgPhase.toFixed(3)} rad`);
    console.log(`  → Phase variance: ${phaseVar.toFixed(3)}`);
    
    if (phaseVar < 0.1) {
      console.log('  → Low variance → Simple interference, cleaner geometry');
    } else {
      console.log('  → High variance → Complex interference, rich patterns');
    }
  }
  
  // ========================================
  // STEP 4: Specific Feature Locations
  // ========================================
  
  console.log('\n📍 FEATURE LOCATION GUIDE:\n');
  
  if (analysis.bivectors.e12 > 0.1) {
    console.log('  • Circles in XY-plane (top view): Look at z≈0 cross-section');
  }
  if (analysis.bivectors.e13 > 0.1) {
    console.log('  • Circles in XZ-plane (side view): Look at y≈0 cross-section');
  }
  if (analysis.bivectors.e23 > 0.1) {
    console.log('  • Circles in YZ-plane (front view): Look at x≈0 cross-section');
  }
  
  console.log('\n  Grid intersections occur at:');
  console.log('    scale1: x+y+z = n*10π  (linear grid)');
  console.log('    scale2: xy+yz+zx = m*2π  (bilinear grid)');
  console.log('    scale3: xyz = k*0.5π  (trilinear grid)\n');
  
  // ========================================
  // STEP 5: Evolution Stage
  // ========================================
  
  const rewrites = window.zxEvolutionEngine?.getRewriteHistory() || [];
  const stepCount = window.zxEvolutionEngine?._stepCount || 0;
  
  console.log('⏱️  EVOLUTION STAGE:\n');
  console.log(`  Steps: ${stepCount}`);
  console.log(`  Rewrites: ${rewrites.length}`);
  
  const bootstrapRewrite = rewrites.find(r => r.type === 'bootstrap_seed_pair');
  if (bootstrapRewrite) {
    const stepsSinceBootstrap = stepCount - (rewrites.indexOf(bootstrapRewrite) + 1);
    console.log(`  Steps since bootstrap: ${stepsSinceBootstrap}`);
    
    if (stepsSinceBootstrap <= 5) {
      console.log('  → Stage: STABILIZATION (color-flip suppressed)');
    } else {
      console.log('  → Stage: FREE EVOLUTION (all rewrites enabled)');
    }
  }
  
  console.log('\n═══════════════════════════════════════════════════\n');
  
  return {
    analysis,
    dominant: dominant.grade,
    zxGraph: zxSnap?.graph || null,
    stage: stepCount <= 7 ? 'stabilization' : 'free_evolution'
  };
};

// Advanced cataloging function
window.catalogGeometry = function() {
  const analysis = window.analyzeVisibleGeometry();
  
  if (!analysis) return null;
  
  const catalog = {
    timestamp: Date.now(),
    camera: window.firmUI.state.camera.position,
    features: [],
    zx_graph: window.zxEvolutionEngine.getCurrentGraph()
  };
  
  // Catalog each feature type with physics interpretation
  if (analysis.analysis.scalar > 0.2) {
    catalog.features.push({
      type: 'UNIFORM_ZONE',
      magnitude: analysis.analysis.scalar,
      physics: 'Scalar field VEV (Higgs-like mass generation)',
      qft_analog: 'Higgs condensate φ = v',
      color_expected: 'Red-dominant',
      zx_source: 'Z-spiders',
      count: Object.values(catalog.zx_graph.labels).filter(l => l.kind === 'Z').length
    });
  }
  
  if (analysis.analysis.bivectors.total > 0.3) {
    const xCount = Object.values(catalog.zx_graph.labels).filter(l => l.kind === 'X').length;
    catalog.features.push({
      type: 'SPHERICAL_EMISSION',
      magnitude: analysis.analysis.bivectors.total,
      physics: 'EM field sources (magnetic dipoles, photon states)',
      qft_analog: 'Field strength tensor F_μν',
      gr_analog: 'Localized spacetime curvature',
      color_expected: 'Blue-dominant',
      zx_source: 'X-spiders',
      count: xCount,
      predicted_spheres: xCount,
      strongest_plane: Object.entries(analysis.analysis.bivectors)
        .filter(([k]) => k.length === 3)
        .reduce((max, [plane, mag]) => mag > max.mag ? {plane, mag} : max, {plane: 'none', mag: 0}).plane
    });
  }
  
  if (analysis.analysis.vectors.total > 0.2) {
    catalog.features.push({
      type: 'DIRECTIONAL_FLOW',
      magnitude: analysis.analysis.vectors.total,
      physics: 'Gauge potential A_μ, momentum density',
      qft_analog: 'Gauge connection ∇_μ',
      color_expected: 'Green-dominant',
      zx_source: 'High-connectivity nodes'
    });
  }
  
  if (analysis.analysis.trivectors.total > 0.1) {
    catalog.features.push({
      type: 'COMPLEX_3D_TEXTURE',
      magnitude: analysis.analysis.trivectors.total,
      physics: 'Higher-order field coupling, weak interaction analog',
      qft_analog: 'Three-point vertex',
      color_expected: 'Mixed/complex',
      zx_source: 'Multi-edge entanglement structures'
    });
  }
  
  if (analysis.analysis.pseudoscalar > 0.1) {
    catalog.features.push({
      type: 'GLOBAL_CHIRALITY',
      magnitude: analysis.analysis.pseudoscalar,
      physics: 'Topological invariant, parity violation',
      qft_analog: 'Chern-Simons term, θ-vacuum',
      color_expected: 'Global twist',
      zx_source: 'Full graph topology'
    });
  }
  
  console.log('\n═══════════════════════════════════════════════════');
  console.log('         COMPREHENSIVE GEOMETRY CATALOG');
  console.log('═══════════════════════════════════════════════════\n');
  console.log(JSON.stringify(catalog, null, 2));
  console.log('\n═══════════════════════════════════════════════════\n');
  
  return catalog;
};

// Time-evolution tracker
window.trackEvolution = function(duration_seconds = 30) {
  console.log(`\n⏱️  Tracking evolution for ${duration_seconds} seconds...\n`);
  
  const snapshots = [];
  const interval = 1000; // 1 second
  
  const timer = setInterval(() => {
    const snap = {
      time: Date.now(),
      geometry: window.catalogGeometry(),
      zx_stats: {
        nodes: window.zxEvolutionEngine.getCurrentGraph().nodes.length,
        coherence: window.zxEvolutionEngine.getSnapshot().coherence,
        rewrites: window.zxEvolutionEngine.getRewriteHistory().length
      }
    };
    
    snapshots.push(snap);
    
    console.log(`[T+${snapshots.length}s] Nodes: ${snap.zx_stats.nodes}, ` +
                `Features: ${snap.geometry.features.length}, ` +
                `C(G): ${snap.zx_stats.coherence.toFixed(3)}`);
  }, interval);
  
  setTimeout(() => {
    clearInterval(timer);
    
    console.log('\n═══════════════════════════════════════════════════');
    console.log('          EVOLUTION TRACKING SUMMARY');
    console.log('═══════════════════════════════════════════════════\n');
    
    // Analyze trends
    const nodeGrowth = snapshots[snapshots.length-1].zx_stats.nodes - snapshots[0].zx_stats.nodes;
    const coherenceChange = snapshots[snapshots.length-1].zx_stats.coherence - snapshots[0].zx_stats.coherence;
    
    console.log(`Duration: ${duration_seconds} seconds`);
    console.log(`Snapshots captured: ${snapshots.length}`);
    console.log(`\nZX Graph Evolution:`);
    console.log(`  Node growth: ${nodeGrowth} (${(nodeGrowth/duration_seconds).toFixed(2)} nodes/sec)`);
    console.log(`  Final nodes: ${snapshots[snapshots.length-1].zx_stats.nodes}`);
    console.log(`  Total rewrites: ${snapshots[snapshots.length-1].zx_stats.rewrites}`);
    console.log(`\nCoherence Evolution:`);
    console.log(`  Initial C(G): ${snapshots[0].zx_stats.coherence.toFixed(4)}`);
    console.log(`  Final C(G): ${snapshots[snapshots.length-1].zx_stats.coherence.toFixed(4)}`);
    console.log(`  Change ΔC: ${coherenceChange.toFixed(4)}`);
    
    // Feature trend analysis
    const featureCounts = snapshots.map(s => s.geometry.features.length);
    const avgFeatures = featureCounts.reduce((a,b) => a+b, 0) / featureCounts.length;
    console.log(`\nGeometric Complexity:`);
    console.log(`  Average features: ${avgFeatures.toFixed(1)}`);
    console.log(`  Feature range: ${Math.min(...featureCounts)} - ${Math.max(...featureCounts)}`);
    
    window.evolutionSnapshots = snapshots;
    console.log(`\n💾 Full data stored in: window.evolutionSnapshots`);
    console.log('═══════════════════════════════════════════════════\n');
    
    return snapshots;
  }, duration_seconds * 1000);
};

// Sphere counting verification
window.verifySphereCount = function() {
  const xCount = Object.values(window.zxEvolutionEngine.getCurrentGraph().labels)
    .filter(l => l.kind === 'X').length;
  
  console.log('\n═══════════════════════════════════════════════════');
  console.log('       SPHERE-COUNTING VERIFICATION');
  console.log('═══════════════════════════════════════════════════\n');
  console.log(`📊 X-spiders in ZX graph: ${xCount}`);
  console.log(`🔮 Predicted spherical features: ~${xCount}`);
  console.log(`\n👁️  Manually count visible spheres in visualization`);
  console.log(`✓ Theory prediction: Each X-spider → one sphere`);
  console.log(`\nIf counts match → Direct evidence of ZX→Clifford mapping!\n`);
  console.log('═══════════════════════════════════════════════════\n');
  
  return {predicted: xCount, theory: 'N_spheres = N_X-spiders'};
};

// Phase interference predictor
window.predictInterference = function() {
  const graph = window.zxEvolutionEngine.getCurrentGraph();
  const xSpiders = Object.entries(graph.labels).filter(([id, l]) => l.kind === 'X');
  
  if (xSpiders.length < 2) {
    console.log('Need at least 2 X-spiders for interference patterns');
    return null;
  }
  
  console.log('\n═══════════════════════════════════════════════════');
  console.log('       INTERFERENCE PATTERN PREDICTION');
  console.log('═══════════════════════════════════════════════════\n');
  
  const phasePairs = [];
  for (let i = 0; i < xSpiders.length; i++) {
    for (let j = i+1; j < xSpiders.length; j++) {
      const [id1, l1] = xSpiders[i];
      const [id2, l2] = xSpiders[j];
      
      const phase1 = (l1.phase_numer / l1.phase_denom) * Math.PI;
      const phase2 = (l2.phase_numer / l2.phase_denom) * Math.PI;
      const phaseDiff = Math.abs(phase2 - phase1);
      
      const expected_fringes = phaseDiff > 0 ? Math.floor(20 / phaseDiff) : 0;
      
      phasePairs.push({
        pair: `X${id1} ↔ X${id2}`,
        phase1: phase1.toFixed(3),
        phase2: phase2.toFixed(3),
        phaseDiff: phaseDiff.toFixed(3),
        expected_fringes: expected_fringes
      });
      
      console.log(`${phasePairs[phasePairs.length-1].pair}:`);
      console.log(`  Phases: ${phase1.toFixed(3)} ↔ ${phase2.toFixed(3)} rad`);
      console.log(`  Δφ: ${phaseDiff.toFixed(3)} rad`);
      console.log(`  Predicted interference fringes: ~${expected_fringes}\n`);
    }
  }
  
  console.log('👁️  Look for wave-like patterns between sphere pairs');
  console.log('✓ Fringe spacing λ ≈ 2π / Δφ (inverse of phase difference)\n');
  console.log('═══════════════════════════════════════════════════\n');
  
  return phasePairs;
};

// Auto-run on load
console.log('🔧 Advanced geometry diagnostics loaded!');
console.log('');
console.log('Available commands:');
console.log('  window.analyzeVisibleGeometry() - Real-time field analysis');
console.log('  window.catalogGeometry() - Comprehensive feature catalog');
console.log('  window.trackEvolution(30) - Track for 30 seconds');
console.log('  window.verifySphereCount() - Test sphere-counting theorem');
console.log('  window.predictInterference() - Predict interference patterns');
console.log('');
console.log('📖 Full interpretation guide:');
console.log('   FIRM_theory/clifford_visualization_physics_interpretation.md');
console.log('');

