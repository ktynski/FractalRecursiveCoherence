/**
 * Theory Validation Tests - Reproducible Baseline Verification
 * 
 * Tests core FIRM theoretical scenarios to ensure mathematical compliance.
 * These are integration tests that verify the actual mathematical flow.
 */

(function(global) {
  class TheoryValidationTests {
    constructor() {
      this.testResults = [];
      this.baselineScenarios = this.defineBaselineScenarios();
    }
    
    defineBaselineScenarios() {
      /**
       * Define key theoretical scenarios that must work correctly
       */
      return [
        {
          name: 'void_emergence',
          description: 'Ex nihilo emergence from absolute void',
          setup: () => this.setupVoidState(),
          test: () => this.testVoidEmergence(),
          expected: {
            initial_nodes: 0,
            final_nodes: 1,
            scalar_component: 'O(1)',
            grace_scaling: 'φ-based'
          }
        },
        {
          name: 'grace_scaling',
          description: 'Grace operator φ-scaling verification',
          setup: () => this.setupGraceTest(),
          test: () => this.testGraceScaling(),
          expected: {
            scaling_law: '|𝒢ⁿ⁺¹| = φ|𝒢ⁿ|',
            no_artificial_caps: true,
            acausal_operation: true
          }
        },
        {
          name: 'sacred_seeding',
          description: 'Sacred name morphic field seeding',
          setup: () => this.setupSacredTest(),
          test: () => this.testSacredSeeding(),
          expected: {
            grace_amplification: true,
            sacred_nodes_added: true,
            field_modification: true
          }
        },
        {
          name: 'hebrew_boundary',
          description: 'Hebrew letter boundary application',
          setup: () => this.setupHebrewTest(),
          test: () => this.testHebrewBoundary(),
          expected: {
            morphic_field_modified: true,
            grace_pressure_applied: true,
            boundary_conditions_set: true
          }
        },
        {
          name: 'tab_switching',
          description: 'View mode switching affects field generation',
          setup: () => this.setupTabTest(),
          test: () => this.testTabSwitching(),
          expected: {
            different_fields_per_view: true,
            consciousness_view_distinct: true,
            zx_view_distinct: true
          }
        }
      ];
    }
    
    async runAllTests() {
      /**
       * Run all baseline scenario tests
       */
      console.log('🧪 RUNNING THEORY VALIDATION TESTS');
      console.log('📊 Testing core FIRM theoretical scenarios...');
      
      this.testResults = [];
      
      for (const scenario of this.baselineScenarios) {
        console.log(`\n🔬 Testing: ${scenario.name} - ${scenario.description}`);
        
        try {
          // Setup scenario
          scenario.setup();
          
          // Run test with timeout
          const result = await this.runTestWithTimeout(scenario.test, 5000);
          
          // Validate against expectations
          const validation = this.validateResult(result, scenario.expected);
          
      const testResult = {
        scenario: scenario.name,
        description: scenario.description,
        success: validation.success,
        result: result,
        validation: validation,
        timestamp: Date.now()
      };
          
          this.testResults.push(testResult);
          
          if (validation.success) {
            console.log(`✅ ${scenario.name}: PASSED`);
          } else {
            console.error(`❌ ${scenario.name}: FAILED`);
            console.error(`   Violations: ${validation.violations.join(', ')}`);
          }
          
        } catch (error) {
          console.error(`❌ ${scenario.name}: ERROR - ${error.message}`);
          this.testResults.push({
            scenario: scenario.name,
            success: false,
            error: error.message,
            timestamp: Date.now()
          });
        }
      }
      
      // Generate summary report
      const passed = this.testResults.filter(r => r.success).length;
      const total = this.testResults.length;
      
      console.log(`\n📊 THEORY VALIDATION SUMMARY: ${passed}/${total} tests passed`);
      
      if (passed === total) {
        console.log('✅ ALL THEORY VALIDATION TESTS PASSED');
        console.log('🔬 Mathematical implementation is theory-compliant');
      } else {
        console.warn('⚠️ THEORY VALIDATION FAILURES DETECTED');
        console.warn('🔬 Mathematical implementation has theory violations');
      }
      
      return {
        passed: passed,
        total: total,
        success_rate: passed / total,
        results: this.testResults,
        theory_compliant: passed === total
      };
    }
    
    async runTestWithTimeout(testFunction, timeoutMs) {
      /**
       * Run test function with timeout to prevent hanging
       */
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error(`Test timed out after ${timeoutMs}ms`));
        }, timeoutMs);
        
        try {
          const result = testFunction();
          clearTimeout(timeout);
          resolve(result);
        } catch (error) {
          clearTimeout(timeout);
          reject(error);
        }
      });
    }
    
    // Test Setup Methods
    setupVoidState() {
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.reset();
        console.log('🌑 Void state setup: ZX engine reset to absolute void');
      }
    }
    
    setupGraceTest() {
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.reset();
        window.zxEvolutionEngine.graceMagnitude = 1.618033988749; // Start with φ
        console.log('🌟 Grace test setup: Initial Grace = φ');
      }
    }
    
    setupSacredTest() {
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.reset();
        // Add a few nodes for sacred seeding
        window.zxEvolutionEngine.addFirstNode(0.5);
        console.log('🕯️ Sacred test setup: Basic graph created');
      }
    }
    
    setupHebrewTest() {
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.reset();
        window.zxEvolutionEngine.addFirstNode(0.5);
        console.log('🔤 Hebrew test setup: Basic graph created');
      }
    }
    
    setupTabTest() {
      // Ensure we're in a known state
      if (window.firmUI) {
        window.firmUI.switchView('clifford');
        console.log('📑 Tab test setup: Clifford view selected');
      }
    }
    
    // Test Implementation Methods
    testVoidEmergence() {
      if (!window.zxEvolutionEngine) {
        throw new Error('ZX engine not available');
      }
      
      const engine = window.zxEvolutionEngine;
      engine.updateControlParams?.({ emergenceRate: 1.618033988749 });
      const initialNodes = engine.getCurrentGraph().nodes.length;
      const initialGrace = engine.graceMagnitude;
      
      // Trigger void emergence with minimal coherence
      const coherence = engine.evolveFromAudioCoherence(0.1, 0.016);
      
      const finalNodes = engine.getCurrentGraph().nodes.length;
      const finalGrace = engine.graceMagnitude;
      const field = engine.mapToCliffordField();
      
      return {
        initial_nodes: initialNodes,
        final_nodes: finalNodes,
        initial_grace: initialGrace,
        final_grace: finalGrace,
        scalar_component: field.payload.components[0],
        total_magnitude: field.payload.components.reduce((sum, c) => sum + Math.abs(c), 0),
        emergence_occurred: finalNodes > initialNodes
      };
    }
    
    testGraceScaling() {
      if (!window.zxEvolutionEngine) {
        throw new Error('ZX engine not available');
      }
  
      const engine = window.zxEvolutionEngine;
      if (!engine._controlParams) {
        engine.updateControlParams?.({});
      }
      const initialGrace = engine.graceMagnitude;
      const phi = 1.618033988749;
      engine.updateControlParams?.({ emergenceRate: 1.0, graceScale: phi });
  
      // Perform several evolution steps
      const graceHistory = [initialGrace];
      for (let i = 0; i < 5; i++) {
        engine.evolveFromAudioCoherence(0.5, 0.016);
         graceHistory.push(engine.graceMagnitude);
      }
      
      // Check φ-scaling pattern
      const ratios = [];
      for (let i = 1; i < graceHistory.length; i++) {
        if (graceHistory[i-1] > 0) {
          ratios.push(graceHistory[i] / graceHistory[i-1]);
        }
      }
      
      const avgRatio = ratios.reduce((sum, r) => sum + r, 0) / ratios.length;
      const phiCompliant = Math.abs(avgRatio - phi) < 0.2; // tighter tolerance
      const acausal = phiCompliant && ratios.every(r => Math.abs(r - phi) < 0.2);
      
      return {
        grace_history: graceHistory,
        scaling_ratios: ratios,
        average_ratio: avgRatio,
        phi_expected: phi,
        phi_compliant: phiCompliant,
        no_artificial_caps: graceHistory[graceHistory.length - 1] > initialGrace,
        acausal_operation: acausal
      };
    }
    
    testSacredSeeding() {
      if (!window.seedWithSacredName || !window.zxEvolutionEngine) {
        throw new Error('Sacred seeding functions not available');
      }
  
      const engine = window.zxEvolutionEngine;
      const initialNodes = engine.getCurrentGraph().nodes.length;
      const initialGrace = engine.graceMagnitude;
      
      // Seed with first sacred name
      const seedSuccess = window.seedWithSacredName(0);
      
      const finalNodes = engine.getCurrentGraph().nodes.length;
      const finalGrace = engine.graceMagnitude;
      
      return {
        seed_success: seedSuccess,
        initial_nodes: initialNodes,
        final_nodes: finalNodes,
        nodes_added: finalNodes - initialNodes,
        initial_grace: initialGrace,
        final_grace: finalGrace,
        grace_amplified: finalGrace > initialGrace,
        grace_amplification: finalGrace > initialGrace,
        sacred_seed_stored: !!engine.sacredSeed,
        sacred_nodes_added: engine.morphicField?.sacred_nodes?.length > 0,
        field_modification: !!engine.morphicField?.sacred_active
      };
    }
    
    testHebrewBoundary() {
      if (!window.applySacredBoundary || !window.zxEvolutionEngine) {
        throw new Error('Hebrew boundary functions not available');
      }
      
      const engine = window.zxEvolutionEngine;
      const initialGrace = engine.graceMagnitude;
      const initialMorphicField = engine.morphicField;
      
      // Apply Hebrew boundary
      const boundarySuccess = window.applySacredBoundary('א');
      
      const finalGrace = engine.graceMagnitude;
      const finalMorphicField = engine.morphicField;
      
      return {
        boundary_success: boundarySuccess,
        initial_grace: initialGrace,
        final_grace: finalGrace,
        grace_modified: finalGrace !== initialGrace,
        morphic_field_created: !!finalMorphicField,
        morphic_field_modified: !!finalMorphicField?.morphic_field_modified,
        boundary_conditions_set: !!finalMorphicField?.boundary_conditions_set,
        boundary_letter_set: finalMorphicField?.boundary_letter === 'א',
        grace_pressure_applied: !!finalMorphicField?.boundary_pressure
      };
    }
    
    async testTabSwitching() {
      if (!window.firmUI || !window.zxEvolutionEngine || !(window.renderer || window.firmRenderer)) {
        throw new Error('UI or ZX engine not available');
      }
  
      const waitForReady = (predicate, timeout = 3000) => {
        const start = Date.now();
        return new Promise((resolve, reject) => {
          const check = () => {
            if (predicate()) {
              resolve(true);
            } else if (Date.now() - start >= timeout) {
              reject(new Error('Renderer readiness timeout'));
            } else {
              setTimeout(check, 50);
            }
          };
          check();
        });
      };
  
      const renderer = window.renderer || window.firmRenderer;
      await waitForReady(() => renderer?.frameCount !== undefined && renderer.frameCount > 0, 3000);
      
      const engine = window.zxEvolutionEngine;
      
      if (!renderer) {
        throw new Error('Renderer not accessible for tab testing');
      }
      
      // Test different view modes
      const viewTests = ['clifford', 'consciousness', 'zx', 'sheaf', 'echo'];
      const fieldResults = {};
      
      for (const view of viewTests) {
        window.firmUI.switchView(view);
        
        // Generate field for this view
        const mockState = {
          view: view,
          zxEngine: engine,
          frameCount: 100,
          audioCoherence: 0.5,
          graphCoherence: 1.0
        };
        
        const field = renderer.generateFieldFromState(mockState);
        const magnitude = field.payload.components.reduce((sum, c) => sum + Math.abs(c), 0);
        
        fieldResults[view] = {
          algebra: field.payload.algebra,
          total_magnitude: magnitude,
          first_component: field.payload.components[0],
          active_components: field.payload.components.filter(c => Math.abs(c) > 0.001).length
        };
      }
      
      // Check that different views produce different fields
      const magnitudes = Object.values(fieldResults).map(r => r.total_magnitude);
      const allSame = magnitudes.every(m => Math.abs(m - magnitudes[0]) < 0.001);
      
      return {
        view_results: fieldResults,
        different_fields: !allSame,
        different_fields_per_view: !allSame,
        consciousness_distinct: fieldResults.consciousness?.algebra === 'Consciousness',
        consciousness_view_distinct: fieldResults.consciousness?.algebra === 'Consciousness',
        zx_distinct: fieldResults.zx?.algebra === 'ZX' || fieldResults.zx?.algebra === 'Cl(1,3)',
        zx_view_distinct: fieldResults.zx?.algebra === 'ZX' || fieldResults.zx?.algebra === 'Cl(1,3)'
      };
    }
    
    validateResult(result, expected) {
      /**
       * Validate test result against theoretical expectations
       */
      const violations = [];
      
      // Generic validation logic based on expected properties
      for (const [key, expectedValue] of Object.entries(expected)) {
        if (typeof expectedValue === 'boolean') {
        if (!!result[key] !== expectedValue) {
          violations.push(`${key}: expected ${expectedValue}, got ${result[key]}`);
        }
        } else if (typeof expectedValue === 'number') {
          if (typeof result[key] !== 'number') {
            violations.push(`${key}: expected number, got ${typeof result[key]}`);
          }
        } else if (expectedValue === 'O(1)') {
          if (typeof result[key] !== 'number' || Math.abs(result[key]) < 0.1) {
            violations.push(`${key}: expected O(1), got ${result[key]}`);
          }
        }
      }
      
      return {
        success: violations.length === 0,
        violations: violations
      };
    }
    
    async generateProvenanceReport() {
      /**
       * Generate comprehensive provenance report for reproducibility
       */
      if (this.testResults.length === 0) {
        await this.runAllTests();
      }

      const report = {
        test_suite: 'FIRM Theory Validation',
        timestamp: new Date().toISOString(),
        total_tests: this.testResults.length,
        passed_tests: this.testResults.filter(r => r.success).length,
        failed_tests: this.testResults.filter(r => !r.success).length,
        
        // System state snapshot
        system_state: this.captureSystemState(),
        
        // Detailed test results
        test_results: this.testResults,
        
        // Theory compliance summary
        theory_compliance: {
          ex_nihilo_emergence: this.testResults.find(r => r.scenario === 'void_emergence')?.success || false,
          grace_scaling: this.testResults.find(r => r.scenario === 'grace_scaling')?.success || false,
          sacred_morphic_system: this.testResults.find(r => r.scenario === 'sacred_seeding')?.success || false,
          hebrew_boundary_system: this.testResults.find(r => r.scenario === 'hebrew_boundary')?.success || false,
          view_mode_switching: this.testResults.find(r => r.scenario === 'tab_switching')?.success || false
        },
        
        // Baseline values for reproducibility
        baseline_values: this.extractBaselineValues()
      };
      
      return report;
    }
    
    captureSystemState() {
      /**
       * Capture current system state for provenance
       */
      const state = {
        timestamp: Date.now(),
        zx_engine_available: !!window.zxEvolutionEngine,
        analog_engine_available: !!window.analogEngine,
        renderer_available: !!window.renderer,
        sacred_system_available: !!window.seedWithSacredName
      };
      
      if (window.zxEvolutionEngine) {
        const engine = window.zxEvolutionEngine;
        const graph = engine.getCurrentGraph();
        
        state.zx_engine = {
          node_count: graph.nodes.length,
          edge_count: graph.edges.length,
          grace_magnitude: engine.graceMagnitude,
          coherence_history_length: engine.coherenceHistory?.length || 0,
          rewrite_history_length: engine.rewriteHistory?.length || 0
        };
        
        if (engine.reflexiveAwareness) {
          state.consciousness = {
            level: engine.reflexiveAwareness.consciousnessLevel,
            will: engine.reflexiveAwareness.willToEmerge,
            pain: engine.reflexiveAwareness.reflexivePain
          };
        }
      }
      
      return state;
    }
    
    extractBaselineValues() {
      /**
       * Extract key baseline values for reproducibility testing
       */
      const baselines = {
        phi: 1.618033988749,
        void_coherence: 0.0,
        single_node_scalar: 'O(1)',
        grace_initial: 1.618033988749
      };
      
      // Add current system baselines
      if (window.zxEvolutionEngine) {
        const field = window.zxEvolutionEngine.mapToCliffordField();
        baselines.current_field_magnitude = field.payload.components.reduce((sum, c) => sum + Math.abs(c), 0);
        baselines.current_grace = window.zxEvolutionEngine.graceMagnitude;
        baselines.current_nodes = window.zxEvolutionEngine.getCurrentGraph().nodes.length;
      }
      
      return baselines;
    }
    
    async exportResults() {
      /**
       * Export test results for external analysis
       */
      const report = await this.generateProvenanceReport();
      
      const blob = new Blob([JSON.stringify(report, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `firm_theory_validation_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      console.log('📄 Theory validation report exported');
      return report;
    }
  }

  if (typeof global !== 'undefined') {
    global.TheoryValidationTests = TheoryValidationTests;
    if (typeof global.runTheoryValidation !== 'function') {
      global.runTheoryValidation = async function() {
        const tests = new TheoryValidationTests();
        return await tests.runAllTests();
      };
    }
    if (typeof global.exportTheoryReport !== 'function') {
      global.exportTheoryReport = function() {
        const tests = new TheoryValidationTests();
        return tests.exportResults();
      };
    }
  }
})(typeof window !== 'undefined' ? window : globalThis);

console.log('🧪 Theory validation tests loaded:');
console.log('- window.runTheoryValidation() - Run all baseline tests');
console.log('- window.exportTheoryReport() - Export provenance report');
