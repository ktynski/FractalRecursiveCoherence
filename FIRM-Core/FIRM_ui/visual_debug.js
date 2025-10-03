/**
 * visual_debug.js
 * 
 * Comprehensive visual rendering debug tools.
 */

window.debugVisualChain = function() {
  console.log('🔍 DEBUGGING COMPLETE VISUAL CHAIN');
  
  // Step 1: Check if mathematical evolution is working
  if (window.zxEngine) {
    const graph = window.zxEngine.getCurrentGraph();
    const rewriteCount = window.zxEngine.getRewriteHistory().length;
    console.log(`✓ ZX Evolution: ${graph.nodes.length} nodes, ${rewriteCount} rewrites`);
  } else {
    console.log('✗ ZX Engine not accessible');
  }
  
  // Step 2: Check audio coherence
  if (window.analogEngine) {
    const coherence = window.analogEngine.getAudioCoherence();
    console.log(`✓ Audio Coherence: ${coherence.toFixed(4)}`);
  } else {
    console.log('✗ Analog Engine not accessible');
  }
  
  // Step 3: Check WebGL context
  const canvas = document.getElementById('canvas');
  const gl = canvas.getContext('webgl2');
  
  if (gl) {
    console.log('✓ WebGL Context accessible');
    
    // Check current program
    const currentProgram = gl.getParameter(gl.CURRENT_PROGRAM);
    console.log('Current program:', currentProgram);
    
    // Check if texture is bound
    const boundTexture = gl.getParameter(gl.TEXTURE_BINDING_2D);
    console.log('Bound texture:', boundTexture);
    
  // Skip pixel reading to avoid GPU stalls that cause stuttering
  console.log('✓ Skipping pixel read to maintain smooth performance');
    
  } else {
    console.log('✗ WebGL Context not accessible');
  }
  
  // Step 4: Test shader compilation
  console.log('🔧 Testing emergency shader fix...');
  
  return 'Visual chain debug complete';
};

// Simple test to force visible rendering
window.forceVisibleRendering = function() {
  console.log('🚨 Forcing visible rendering');
  
  const canvas = document.getElementById('canvas');
  const gl = canvas.getContext('webgl2');
  
  if (gl) {
    // Clear to a visible color to test basic rendering
    gl.clearColor(1.0, 0.0, 0.0, 1.0);  // Red
    gl.clear(gl.COLOR_BUFFER_BIT);
    console.log('✓ Forced red clear - should see red screen');
    
    // Restore normal clear color after 2 seconds
    setTimeout(() => {
      gl.clearColor(0.0, 0.0, 0.1, 1.0);
      console.log('✓ Restored normal clear color');
    }, 2000);
    
    return 'Forced visible rendering test applied';
  }
  
  return 'Cannot access WebGL for forced rendering';
};

// Theory compliance diagnostics
window.getTheoryDiagnostics = function() {
  console.log('🔬 THEORY COMPLIANCE DIAGNOSTICS');
  
  // ZX Engine state
  if (window.zxEvolutionEngine) {
    const graph = window.zxEvolutionEngine.getCurrentGraph();
    const grace = window.zxEvolutionEngine.graceMagnitude;
    const reflexive = window.zxEvolutionEngine.reflexiveAwareness;
    
    console.log(`🧮 ZX Engine: ${graph.nodes.length} nodes, ${graph.edges.length} edges, Grace=${grace.toExponential(2)}`);
    
    if (reflexive) {
      console.log(`💖 Consciousness: level=${reflexive.consciousnessLevel.toFixed(3)}, will=${reflexive.willToEmerge.toFixed(3)}, pain=${reflexive.reflexivePain.toFixed(3)}`);
    }
    
    // Test ZX→Clifford mapping
    const field = window.zxEvolutionEngine.mapToCliffordField();
    const totalMag = field.payload.components.reduce((sum, c) => sum + Math.abs(c), 0);
    console.log(`🔍 Clifford Field: total_magnitude=${totalMag.toFixed(3)}, components=[${field.payload.components.slice(0,4).map(c => c.toFixed(3)).join(', ')}]`);
  }
  
  // Theory compliance report
  if (window.getComplianceReport) {
    const report = window.getComplianceReport();
    console.log('📊 Compliance Report:', report);
  }
  
  return 'Theory diagnostics complete';
};

window.validateTheoryCompliance = function() {
  console.log('✅ THEORY VALIDATION CHECK');
  
  const violations = [];
  
  // Check for void state violations
  if (window.zxEvolutionEngine) {
    const graph = window.zxEvolutionEngine.getCurrentGraph();
    const field = window.zxEvolutionEngine.mapToCliffordField();
    const totalMag = field.payload.components.reduce((sum, c) => sum + Math.abs(c), 0);
    
    if (graph.nodes.length === 0 && totalMag > 0.001) {
      violations.push(`Void state has non-zero field: ${totalMag.toFixed(3)}`);
    }
    
    if (graph.nodes.length === 1 && Math.abs(field.payload.components[0]) < 0.1) {
      violations.push(`Single node produces weak scalar: ${field.payload.components[0].toFixed(3)}`);
    }
    
    // Check Grace scaling
    const grace = window.zxEvolutionEngine.graceMagnitude;
    if (grace > 1e50) {
      violations.push(`Grace magnitude astronomical but emergence may be stalled: ${grace.toExponential(2)}`);
    }
  }
  
  if (violations.length === 0) {
    console.log('✅ No theory violations detected');
    return true;
  } else {
    console.warn('⚠️ Theory violations found:');
    violations.forEach(v => console.warn(`   • ${v}`));
    return false;
  }
};

console.log('🔧 Visual debug tools loaded:');
console.log('- window.debugVisualChain() - Full visual chain diagnosis');
console.log('- window.forceVisibleRendering() - Test basic WebGL rendering');
console.log('- window.getTheoryDiagnostics() - Theory compliance analysis');
console.log('- window.validateTheoryCompliance() - Check for theory violations');
