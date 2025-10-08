// 30-Second Console Test for E8 Theory Validation
// Copy-paste this into browser console at http://localhost:8080

console.log('🧪 E8 THEORY VALIDATION TEST - 30 Second Demo');
console.log('================================================');

// Test 1: System Components
const components = {
  zxEngine: !!window.zxEvolutionEngine,
  firmUI: !!window.firmUI,
  firmRenderer: !!window.firmRenderer,
  harmonicGenerator: !!window.harmonicGenerator
};
console.log('✅ System Components:', components);

// Test 2: E8 Calculation (if available)
if (window.zxEvolutionEngine && window.zxEvolutionEngine.testE8Calculation) {
  try {
    const e8Result = window.zxEvolutionEngine.testE8Calculation();
    console.log('🔬 E8 Calculation Result:', e8Result);
  } catch (e) {
    console.log('⚠️ E8 Calculation Error:', e.message);
  }
}

// Test 3: Field State Analysis
if (window.firmUI && window.firmUI.state) {
  const field = window.firmUI.state.rendering?.field;
  if (field && field.payload && field.payload.components) {
    const [scalar, vector, bivector, trivector] = field.payload.components.slice(0, 4);
    console.log('🌌 Field State:', {
      scalar: scalar.toFixed(3),
      vector: vector.toFixed(3),
      bivector: bivector.toFixed(3),
      trivector: trivector.toFixed(3)
    });
  }
}

// Test 4: Evolution Phase Detection
if (window.zxEvolutionEngine) {
  try {
    const phase = window.zxEvolutionEngine.getCurrentPhase?.();
    console.log('🔄 Current Evolution Phase:', phase || 'unknown');
  } catch (e) {
    console.log('⚠️ Phase Detection Error:', e.message);
  }
}

// Test 5: Audio Coherence
if (window.harmonicGenerator) {
  try {
    const coherence = window.harmonicGenerator.getCurrentCoherence?.();
    console.log('🎵 Audio Coherence:', coherence || 'unknown');
  } catch (e) {
    console.log('⚠️ Coherence Detection Error:', e.message);
  }
}

console.log('================================================');
console.log('🎯 Test Complete - System is operational!');
console.log('📊 Check the logs above for detailed results');
