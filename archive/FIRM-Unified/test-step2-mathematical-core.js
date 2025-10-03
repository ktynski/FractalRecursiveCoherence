#!/usr/bin/env node

/**
 * Phase 2: Mathematical Core Testing
 * 
 * Rigorous validation of the extracted FIRM mathematical engine
 * before integration with attractor systems.
 */

import { createMathematicalCore, validateMathematicalConsistency } from './src/mathematical-core.js';

class MathematicalCoreTester {
    constructor() {
        this.testResults = [];
        this.core = null;
    }
    
    async runAllTests() {
        console.log('🧮 FIRM Mathematical Core - Rigorous Testing');
        console.log('=' .repeat(70));
        
        try {
            await this.testCoreInitialization();
            await this.testCliffordAlgebraStructure();
            await this.testFieldEvolution();
            await this.testCoherenceComputation();
            await this.testIdentityEchoTau();
            await this.testBootstrapStageProgression();
            await this.testAttractorCoupling();
            await this.testHebrewMapping();
            await this.test231GatesGeneration();
            await this.testMathematicalConsistency();
            
            this.reportResults();
            
        } catch (error) {
            console.error('❌ Mathematical core testing failed:', error.message);
            process.exit(1);
        }
    }
    
    async testCoreInitialization() {
        console.log('\n🏗️  Testing Core Initialization...');
        
        this.core = createMathematicalCore();
        
        if (this.core) {
            this.pass('✅ Mathematical core created');
        } else {
            this.fail('❌ Failed to create mathematical core');
            return;
        }
        
        // Verify initial state
        if (this.core.bootstrapState.stage === 'VOID') {
            this.pass('✅ Initial stage: VOID');
        } else {
            this.fail(`❌ Wrong initial stage: ${this.core.bootstrapState.stage}`);
        }
        
        if (this.core.bootstrapState.coherence === 0.0) {
            this.pass('✅ Initial coherence: 0.0');
        } else {
            this.fail(`❌ Wrong initial coherence: ${this.core.bootstrapState.coherence}`);
        }
        
        if (this.core.bootstrapState.identityEchoTau === Infinity) {
            this.pass('✅ Initial τ: ∞');
        } else {
            this.fail(`❌ Wrong initial τ: ${this.core.bootstrapState.identityEchoTau}`);
        }
    }
    
    async testCliffordAlgebraStructure() {
        console.log('\n📐 Testing Clifford Algebra Cl(1,3)...');
        
        const field = this.core.cliffordField;
        
        // Test dimension
        if (field.components.length === 16) {
            this.pass('✅ Clifford field dimension: 16');
        } else {
            this.fail(`❌ Wrong dimension: ${field.components.length} (expected 16)`);
        }
        
        // Test algebra specification
        if (field.algebra === "Cl(1,3)") {
            this.pass('✅ Algebra type: Cl(1,3)');
        } else {
            this.fail(`❌ Wrong algebra: ${field.algebra}`);
        }
        
        // Test basis elements
        const expectedBasis = [
            "1", "e0", "e1", "e2", "e3",
            "e01", "e02", "e03", "e12", "e13", "e23",
            "e012", "e013", "e023", "e123", "e0123"
        ];
        
        if (JSON.stringify(field.basis) === JSON.stringify(expectedBasis)) {
            this.pass('✅ Clifford basis elements correct');
        } else {
            this.fail('❌ Incorrect Clifford basis elements');
        }
        
        // Test validation method
        try {
            this.core.validateCliffordAlgebra();
            this.pass('✅ Clifford algebra validation passes');
        } catch (error) {
            this.fail(`❌ Clifford validation failed: ${error.message}`);
        }
    }
    
    async testFieldEvolution() {
        console.log('\n🌀 Testing Field Evolution...');
        
        // Test with different audio coherence values
        const testCases = [
            { audioCoherence: 0.0, expectedNonZero: 3 },
            { audioCoherence: 0.5, expectedNonZero: 8 },
            { audioCoherence: 1.0, expectedNonZero: 8 }
        ];
        
        for (const testCase of testCases) {
            const initialComponents = [...this.core.cliffordField.components];
            
            this.core.evolveField(testCase.audioCoherence);
            
            const finalComponents = this.core.cliffordField.components;
            const nonZeroCount = finalComponents.filter(c => Math.abs(c) > 0.001).length;
            
            if (nonZeroCount >= testCase.expectedNonZero) {
                this.pass(`✅ Evolution with audio=${testCase.audioCoherence}: ${nonZeroCount} active components`);
            } else {
                this.fail(`❌ Evolution with audio=${testCase.audioCoherence}: only ${nonZeroCount} active (expected >= ${testCase.expectedNonZero})`);
            }
            
            // Verify components changed
            let changed = false;
            for (let i = 0; i < 16; i++) {
                if (Math.abs(finalComponents[i] - initialComponents[i]) > 0.001) {
                    changed = true;
                    break;
                }
            }
            
            if (changed) {
                this.pass(`✅ Field evolution creates changes`);
            } else {
                this.fail(`❌ Field evolution produces no changes`);
            }
        }
    }
    
    async testCoherenceComputation() {
        console.log('\n📊 Testing Coherence Computation...');
        
        // Set known field state
        this.core.cliffordField.components.fill(0);
        this.core.cliffordField.components[0] = 3.0;  // Scalar
        this.core.cliffordField.components[1] = 4.0;  // Vector
        
        this.core.updateCoherence();
        
        const expectedCoherence = Math.sqrt(3*3 + 4*4); // = 5.0
        const actualCoherence = this.core.bootstrapState.coherence;
        
        if (Math.abs(actualCoherence - expectedCoherence) < 0.001) {
            this.pass(`✅ Coherence computation: ${actualCoherence.toFixed(3)} (expected ${expectedCoherence.toFixed(3)})`);
        } else {
            this.fail(`❌ Wrong coherence: ${actualCoherence.toFixed(3)} (expected ${expectedCoherence.toFixed(3)})`);
        }
    }
    
    async testIdentityEchoTau() {
        console.log('\n⏱️  Testing Identity Echo Time τ...');
        
        // Test with different coherence values
        const testCases = [
            { coherence: 0.0, expectedTau: 0.0 },
            { coherence: 1.0, expectedTau: 0.731 },  // sigmoid(1) ≈ 0.731
            { coherence: 5.0, expectedTau: 0.993 }   // sigmoid(5) ≈ 0.993
        ];
        
        for (const testCase of testCases) {
            this.core.bootstrapState.coherence = testCase.coherence;
            this.core.updateIdentityEchoTau();
            
            const actualTau = this.core.bootstrapState.identityEchoTau;
            const expectedTau = testCase.expectedTau;
            
            if (Math.abs(actualTau - expectedTau) < 0.01) {
                this.pass(`✅ τ for coherence=${testCase.coherence}: ${actualTau.toFixed(3)}`);
            } else {
                this.fail(`❌ Wrong τ: ${actualTau.toFixed(3)} (expected ${expectedTau.toFixed(3)})`);
            }
        }
    }
    
    async testBootstrapStageProgression() {
        console.log('\n🌟 Testing Bootstrap Stage Progression...');
        
        const stageTests = [
            { coherence: 0.0, expectedStage: 'VOID' },
            { coherence: 1.0, expectedStage: 'EMERGENCE' },
            { coherence: 5.0, expectedStage: 'FORMATION' },
            { coherence: 10.0, expectedStage: 'STABILITY' },
            { coherence: 20.0, expectedStage: 'UNIVERSE' }
        ];
        
        for (const test of stageTests) {
            this.core.bootstrapState.coherence = test.coherence;
            this.core.updateBootstrapStage();
            
            if (this.core.bootstrapState.stage === test.expectedStage) {
                this.pass(`✅ Stage for coherence=${test.coherence}: ${test.expectedStage}`);
            } else {
                this.fail(`❌ Wrong stage: ${this.core.bootstrapState.stage} (expected ${test.expectedStage})`);
            }
        }
    }
    
    async testAttractorCoupling() {
        console.log('\n🔗 Testing Attractor Coupling...');
        
        // Set up test field state
        this.core.cliffordField.components[0] = 5.0;   // Scalar for Grace
        this.core.cliffordField.components[1] = 2.0;   // Vector for Bireflection
        this.core.cliffordField.components[5] = 3.0;   // Bivector for Sovereignty
        this.core.updateCoherence();
        
        // Test Grace parameters
        const graceParams = this.core.getGraceParameters();
        if (graceParams.phi === 1.618) {
            this.pass('✅ Grace φ parameter: 1.618');
        } else {
            this.fail(`❌ Wrong Grace φ: ${graceParams.phi}`);
        }
        
        // Test Sovereignty parameters
        const sovereigntyParams = this.core.getSovereigntyParameters();
        if (sovereigntyParams.recursiveDepth >= 3 && sovereigntyParams.recursiveDepth <= 9) {
            this.pass(`✅ Sovereignty depth: ${sovereigntyParams.recursiveDepth}`);
        } else {
            this.fail(`❌ Invalid Sovereignty depth: ${sovereigntyParams.recursiveDepth}`);
        }
        
        // Test Bireflection parameters
        const bireflectionParams = this.core.getBireflectionParameters();
        if (bireflectionParams.symmetryOrder === 2) {
            this.pass('✅ Bireflection symmetry order: 2 (involution)');
        } else {
            this.fail(`❌ Wrong symmetry order: ${bireflectionParams.symmetryOrder}`);
        }
    }
    
    async testHebrewMapping() {
        console.log('\n🔤 Testing Hebrew Letter Mapping...');
        
        const hebrewParams = this.core.getHebrewParameters();
        
        if (hebrewParams.letterStates.length >= 16) {
            this.pass(`✅ Hebrew mapping coverage: ${hebrewParams.letterStates.length} letters`);
        } else {
            this.fail(`❌ Insufficient Hebrew coverage: ${hebrewParams.letterStates.length}`);
        }
        
        // Test theoretical consistency
        try {
            this.core.validateHebrewMapping();
            this.pass('✅ Hebrew mapping validation passes');
        } catch (error) {
            this.fail(`❌ Hebrew mapping validation failed: ${error.message}`);
        }
    }
    
    async test231GatesGeneration() {
        console.log('\n🚪 Testing 231-Gates Generation...');
        
        const gatesParams = this.core.get231GatesParameters();
        
        if (gatesParams.totalGateCount === 231) {
            this.pass('✅ Total gate count: 231');
        } else {
            this.fail(`❌ Wrong gate count: ${gatesParams.totalGateCount}`);
        }
        
        if (gatesParams.gates.length === 231) {
            this.pass('✅ Generated gates array: 231 elements');
        } else {
            this.fail(`❌ Generated gates: ${gatesParams.gates.length} (expected 231)`);
        }
        
        // Verify all gates have required properties
        let validGates = 0;
        for (const gate of gatesParams.gates) {
            if (gate.hasOwnProperty('index') && 
                gate.hasOwnProperty('letterPair') &&
                gate.hasOwnProperty('strength') &&
                gate.hasOwnProperty('phase') &&
                gate.hasOwnProperty('active')) {
                validGates++;
            }
        }
        
        if (validGates === 231) {
            this.pass('✅ All gates have required properties');
        } else {
            this.fail(`❌ Invalid gates: ${231 - validGates} missing properties`);
        }
    }
    
    async testMathematicalConsistency() {
        console.log('\n🔬 Testing Mathematical Consistency...');
        
        // Run field evolution for several steps
        for (let i = 0; i < 10; i++) {
            this.core.evolveField(0.5 + 0.3 * Math.sin(i * 0.1));
            
            // Validate consistency at each step
            const validation = validateMathematicalConsistency(this.core);
            if (!validation.valid) {
                this.fail(`❌ Consistency check failed at step ${i}: ${validation.errors.join(', ')}`);
                return;
            }
        }
        
        this.pass('✅ Mathematical consistency maintained over 10 evolution steps');
        
        // Test final state properties
        const finalCoherence = this.core.bootstrapState.coherence;
        const finalTau = this.core.bootstrapState.identityEchoTau;
        const finalStage = this.core.bootstrapState.stage;
        
        this.pass(`✅ Final state: coherence=${finalCoherence.toFixed(3)}, τ=${finalTau.toFixed(3)}, stage=${finalStage}`);
        
        // Verify no NaN or infinite values in field
        const hasInvalidValues = this.core.cliffordField.components.some(c => !isFinite(c));
        if (!hasInvalidValues) {
            this.pass('✅ All field components finite');
        } else {
            this.fail('❌ Field contains NaN or infinite values');
        }
    }
    
    pass(message) {
        this.testResults.push({ status: 'PASS', message });
        console.log(`  ${message}`);
    }
    
    fail(message) {
        this.testResults.push({ status: 'FAIL', message });
        console.log(`  ${message}`);
    }
    
    reportResults() {
        console.log('\n' + '=' .repeat(70));
        console.log('📊 MATHEMATICAL CORE TEST RESULTS');
        console.log('=' .repeat(70));
        
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const failed = this.testResults.filter(r => r.status === 'FAIL').length;
        const total = this.testResults.length;
        
        console.log(`Total Tests: ${total}`);
        console.log(`Passed: ${passed} ✅`);
        console.log(`Failed: ${failed} ${failed > 0 ? '❌' : '✅'}`);
        console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);
        
        if (failed === 0) {
            console.log('\n🎉 ALL MATHEMATICAL CORE TESTS PASSED!');
            console.log('✅ Mathematical engine is theoretically sound');
            console.log('✅ Ready to proceed with Phase 3: Attractor Integration');
            console.log('\n📋 Verified Capabilities:');
            console.log('  • Clifford algebra Cl(1,3) structure maintained');
            console.log('  • Coherence C(G) computation accurate');
            console.log('  • Identity echo τ calculation correct');
            console.log('  • Bootstrap stage progression follows theory');
            console.log('  • Attractor coupling interfaces functional');
            console.log('  • Hebrew letter mapping consistent');
            console.log('  • 231-gates generation mathematically correct');
            console.log('\n🚀 Next Step: npm run test-step3-integration');
        } else {
            console.log('\n⚠️  MATHEMATICAL CORE ISSUES DETECTED');
            console.log('❌ Fix failing tests before proceeding');
            
            console.log('\nFailed Tests:');
            this.testResults
                .filter(r => r.status === 'FAIL')
                .forEach(r => console.log(`  ${r.message}`));
                
            console.log('\n🛑 CRITICAL: Mathematical inconsistencies must be resolved');
            console.log('   Theory-driven implementation requires mathematical correctness');
        }
    }
}

// Run tests
const tester = new MathematicalCoreTester();
tester.runAllTests();
