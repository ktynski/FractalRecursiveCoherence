#!/usr/bin/env node

/**
 * Phase 3: Integration Testing
 * 
 * Test the theoretical coupling between mathematical core and attractor systems.
 * Verify all stage transitions work correctly with proper theoretical grounding.
 */

import { createMathematicalCore } from './src/mathematical-core.js';
import { createAttractorBridge } from './src/attractor-bridge.js';

class IntegrationTester {
    constructor() {
        this.testResults = [];
        this.mathCore = null;
        this.bridge = null;
    }
    
    async runAllTests() {
        console.log('🔗 FIRM Integration Testing - Mathematical ↔ Attractor Coupling');
        console.log('=' .repeat(80));
        
        try {
            await this.testBridgeInitialization();
            await this.testStageProgression();
            await this.testGraceCoupling();
            await this.testSovereigntyCoupling();
            await this.testBireflectionCoupling();
            await this.testHebrewCoupling();
            await this.test231GatesCoupling();
            await this.testCouplingConsistency();
            await this.testFullBootstrapSequence();
            
            this.reportResults();
            
        } catch (error) {
            console.error('❌ Integration testing failed:', error.message);
            process.exit(1);
        }
    }
    
    async testBridgeInitialization() {
        console.log('\n🌉 Testing Bridge Initialization...');
        
        this.mathCore = createMathematicalCore();
        if (this.mathCore) {
            this.pass('✅ Mathematical core created');
        } else {
            this.fail('❌ Failed to create mathematical core');
            return;
        }
        
        this.bridge = createAttractorBridge(this.mathCore);
        if (this.bridge) {
            this.pass('✅ Attractor bridge created');
        } else {
            this.fail('❌ Failed to create attractor bridge');
            return;
        }
        
        // Verify bridge has access to mathematical core
        if (this.bridge.mathCore === this.mathCore) {
            this.pass('✅ Bridge linked to mathematical core');
        } else {
            this.fail('❌ Bridge not properly linked');
        }
    }
    
    async testStageProgression() {
        console.log('\n🌟 Testing Bootstrap Stage Progression...');
        
        // Test VOID → EMERGENCE transition
        this.mathCore.bootstrapState.coherence = 0.0;
        this.mathCore.updateBootstrapStage();
        let activeAttractors = this.bridge.getActiveAttractors();
        
        if (this.mathCore.bootstrapState.stage === 'VOID' && activeAttractors.length === 0) {
            this.pass('✅ VOID stage: no active attractors');
        } else {
            this.fail(`❌ VOID stage incorrect: ${activeAttractors.length} attractors active`);
        }
        
        // Test EMERGENCE stage
        this.mathCore.bootstrapState.coherence = 1.0;
        this.mathCore.updateBootstrapStage();
        activeAttractors = this.bridge.getActiveAttractors();
        
        if (this.mathCore.bootstrapState.stage === 'EMERGENCE' && activeAttractors.includes('bootstrap')) {
            this.pass('✅ EMERGENCE stage: bootstrap attractor active');
        } else {
            this.fail(`❌ EMERGENCE stage incorrect: ${activeAttractors.join(', ')}`);
        }
        
        // Test FORMATION stage
        this.mathCore.bootstrapState.coherence = 5.0;
        this.mathCore.updateBootstrapStage();
        activeAttractors = this.bridge.getActiveAttractors();
        
        if (this.mathCore.bootstrapState.stage === 'FORMATION' && 
            activeAttractors.includes('bootstrap') && activeAttractors.includes('grace')) {
            this.pass('✅ FORMATION stage: bootstrap + grace attractors active');
        } else {
            this.fail(`❌ FORMATION stage incorrect: ${activeAttractors.join(', ')}`);
        }
        
        // Test STABILITY stage
        this.mathCore.bootstrapState.coherence = 10.0;
        this.mathCore.updateBootstrapStage();
        activeAttractors = this.bridge.getActiveAttractors();
        
        const expectedStability = ['bootstrap', 'grace', 'sovereignty', 'bireflection'];
        const hasAllStability = expectedStability.every(a => activeAttractors.includes(a));
        
        if (this.mathCore.bootstrapState.stage === 'STABILITY' && hasAllStability) {
            this.pass('✅ STABILITY stage: all core attractors active');
        } else {
            this.fail(`❌ STABILITY stage incorrect: ${activeAttractors.join(', ')}`);
        }
        
        // Test UNIVERSE stage
        this.mathCore.bootstrapState.coherence = 20.0;
        this.mathCore.updateBootstrapStage();
        activeAttractors = this.bridge.getActiveAttractors();
        
        const expectedUniverse = ['bootstrap', 'grace', 'sovereignty', 'bireflection', 'hebrew', 'gates'];
        const hasAllUniverse = expectedUniverse.every(a => activeAttractors.includes(a));
        
        if (this.mathCore.bootstrapState.stage === 'UNIVERSE' && hasAllUniverse) {
            this.pass('✅ UNIVERSE stage: all attractors active');
        } else {
            this.fail(`❌ UNIVERSE stage incorrect: ${activeAttractors.join(', ')}`);
        }
    }
    
    async testGraceCoupling() {
        console.log('\n🌟 Testing Grace Attractor Coupling...');
        
        // Set up test state with strong scalar component
        this.mathCore.cliffordField.components[0] = 10.0;  // Strong scalar
        this.mathCore.bootstrapState.coherence = 5.0;     // FORMATION stage
        
        const graceState = this.bridge.computeGraceCoupling();
        
        // Verify theoretical requirements
        if (graceState.phi === 1.618) {
            this.pass('✅ Grace φ = 1.618 (golden ratio)');
        } else {
            this.fail(`❌ Wrong Grace φ: ${graceState.phi}`);
        }
        
        if (graceState.amplitude > 0) {
            this.pass(`✅ Grace amplitude: ${graceState.amplitude.toFixed(3)}`);
        } else {
            this.fail(`❌ Zero Grace amplitude: ${graceState.amplitude}`);
        }
        
        if (graceState.active && this.mathCore.bootstrapState.coherence >= 3.0) {
            this.pass('✅ Grace activation follows coherence threshold');
        } else {
            this.fail('❌ Grace activation threshold incorrect');
        }
    }
    
    async testSovereigntyCoupling() {
        console.log('\n🏛️  Testing Sovereignty Attractor Coupling...');
        
        // Set up test state with strong bivector components
        this.mathCore.cliffordField.components[5] = 3.0;   // e01
        this.mathCore.cliffordField.components[6] = 4.0;   // e02
        this.mathCore.bootstrapState.coherence = 10.0;    // STABILITY stage
        
        const sovereigntyState = this.bridge.computeSovereigntyCoupling();
        
        // Verify recursive depth calculation
        if (sovereigntyState.recursiveDepth >= 3 && sovereigntyState.recursiveDepth <= 9) {
            this.pass(`✅ Sovereignty recursive depth: ${sovereigntyState.recursiveDepth}`);
        } else {
            this.fail(`❌ Invalid recursive depth: ${sovereigntyState.recursiveDepth}`);
        }
        
        if (sovereigntyState.complexity > 0) {
            this.pass(`✅ Sovereignty complexity: ${sovereigntyState.complexity.toFixed(3)}`);
        } else {
            this.fail(`❌ Zero Sovereignty complexity: ${sovereigntyState.complexity}`);
        }
    }
    
    async testBireflectionCoupling() {
        console.log('\n🪞 Testing Bireflection Attractor Coupling...');
        
        // Set up test state with strong vector components
        this.mathCore.cliffordField.components[1] = 2.0;   // e0
        this.mathCore.cliffordField.components[2] = 3.0;   // e1
        this.mathCore.cliffordField.components[3] = 1.0;   // e2
        this.mathCore.bootstrapState.coherence = 10.0;    // STABILITY stage
        
        const bireflectionState = this.bridge.computeBireflectionCoupling();
        
        // Verify involution property
        if (bireflectionState.symmetryOrder === 2) {
            this.pass('✅ Bireflection involution: β∘β = 1');
        } else {
            this.fail(`❌ Not involution: order ${bireflectionState.symmetryOrder}`);
        }
        
        // Verify mirror axis normalization
        const axis = bireflectionState.mirrorAxis;
        const magnitude = Math.sqrt(axis.reduce((sum, a) => sum + a*a, 0));
        
        if (Math.abs(magnitude - 1.0) < 0.001) {
            this.pass('✅ Mirror axis normalized');
        } else {
            this.fail(`❌ Mirror axis not normalized: magnitude ${magnitude.toFixed(3)}`);
        }
    }
    
    async testHebrewCoupling() {
        console.log('\n🔤 Testing Hebrew Letter Coupling...');
        
        // Set up test state with multiple active components
        for (let i = 0; i < 16; i++) {
            this.mathCore.cliffordField.components[i] = 0.5 + 0.3 * Math.sin(i);
        }
        this.mathCore.bootstrapState.coherence = 20.0;    // UNIVERSE stage
        
        const hebrewState = this.bridge.computeHebrewCoupling();
        
        // Verify letter count
        if (hebrewState.letterStates.length >= 16) {
            this.pass(`✅ Hebrew letters mapped: ${hebrewState.letterStates.length}`);
        } else {
            this.fail(`❌ Insufficient Hebrew mapping: ${hebrewState.letterStates.length}`);
        }
        
        // Verify active letters
        if (hebrewState.activeLetters > 0) {
            this.pass(`✅ Active Hebrew letters: ${hebrewState.activeLetters}`);
        } else {
            this.fail('❌ No active Hebrew letters');
        }
        
        // Verify theoretical mappings
        const aleph = hebrewState.letterStates.find(l => l.hebrew === 'א');
        if (aleph && aleph.fsctf === 'τ') {
            this.pass('✅ Aleph (א) → τ mapping correct');
        } else {
            this.fail('❌ Aleph mapping incorrect');
        }
    }
    
    async test231GatesCoupling() {
        console.log('\n🚪 Testing 231-Gates Coupling...');
        
        const gatesState = this.bridge.compute231GatesCoupling();
        
        // Verify gate count
        if (gatesState.totalGateCount === 231) {
            this.pass('✅ Total gates: 231');
        } else {
            this.fail(`❌ Wrong gate count: ${gatesState.totalGateCount}`);
        }
        
        // Verify gate structure
        const firstGate = gatesState.gates[0];
        const requiredProperties = ['index', 'letterPair', 'hebrewPair', 'fsctfPair', 'strength', 'phase', 'active', 'meaning'];
        const hasAllProperties = requiredProperties.every(prop => firstGate.hasOwnProperty(prop));
        
        if (hasAllProperties) {
            this.pass('✅ Gate structure complete');
        } else {
            this.fail('❌ Gate structure incomplete');
        }
        
        // Verify combinations are unique
        const pairStrings = gatesState.gates.map(g => `${g.letterPair[0]}-${g.letterPair[1]}`);
        const uniquePairs = new Set(pairStrings);
        
        if (uniquePairs.size === 231) {
            this.pass('✅ All gate combinations unique');
        } else {
            this.fail(`❌ Duplicate combinations: ${231 - uniquePairs.size}`);
        }
    }
    
    async testCouplingConsistency() {
        console.log('\n🔬 Testing Coupling Consistency...');
        
        try {
            const validation = this.bridge.validateCouplingConsistency();
            
            if (validation.valid) {
                this.pass('✅ All couplings theoretically consistent');
                this.pass(`✅ Active attractors: ${validation.activeAttractors.join(', ')}`);
            } else {
                this.fail('❌ Coupling consistency validation failed');
            }
            
        } catch (error) {
            this.fail(`❌ Consistency check failed: ${error.message}`);
        }
    }
    
    async testFullBootstrapSequence() {
        console.log('\n🌌 Testing Full Bootstrap Sequence...');
        
        // Reset to initial state
        this.mathCore = createMathematicalCore();
        this.bridge = createAttractorBridge(this.mathCore);
        
        const stages = ['VOID', 'EMERGENCE', 'FORMATION', 'STABILITY', 'UNIVERSE'];
        const coherenceValues = [0.0, 1.0, 5.0, 10.0, 20.0];
        
        for (let i = 0; i < stages.length; i++) {
            const expectedStage = stages[i];
            const coherence = coherenceValues[i];
            
            // Set coherence and update
            this.mathCore.bootstrapState.coherence = coherence;
            this.mathCore.updateBootstrapStage();
            this.mathCore.updateIdentityEchoTau();
            
            // Get coupling state
            const couplings = this.bridge.updateAllCouplings();
            const activeAttractors = this.bridge.getActiveAttractors();
            
            // Verify stage
            if (this.mathCore.bootstrapState.stage === expectedStage) {
                this.pass(`✅ Stage ${i}: ${expectedStage} (coherence=${coherence})`);
            } else {
                this.fail(`❌ Wrong stage: ${this.mathCore.bootstrapState.stage} (expected ${expectedStage})`);
            }
            
            // Verify τ calculation
            const tau = this.mathCore.bootstrapState.identityEchoTau;
            if (coherence === 0.0) {
                if (tau === 0.0) {
                    this.pass(`✅ τ = 0 for void state`);
                } else {
                    this.fail(`❌ Wrong τ for void: ${tau}`);
                }
            } else {
                if (tau > 0 && tau <= 1.0) {
                    this.pass(`✅ τ = ${tau.toFixed(3)} for coherence=${coherence}`);
                } else {
                    this.fail(`❌ Invalid τ: ${tau} for coherence=${coherence}`);
                }
            }
            
            // Verify active attractors match stage
            const expectedCounts = [0, 1, 2, 4, 6]; // VOID, EMERGENCE, FORMATION, STABILITY, UNIVERSE
            if (activeAttractors.length === expectedCounts[i]) {
                this.pass(`✅ Active attractors: ${activeAttractors.length} (${activeAttractors.join(', ')})`);
            } else {
                this.fail(`❌ Wrong attractor count: ${activeAttractors.length} (expected ${expectedCounts[i]})`);
            }
        }
    }
    
    async testGraceCoupling() {
        console.log('\n🌟 Testing Grace Attractor Coupling...');
        
        // Set up FORMATION stage
        this.mathCore.cliffordField.components[0] = 8.0;  // Strong scalar
        this.mathCore.updateCoherence();
        this.mathCore.updateBootstrapStage();
        
        const graceState = this.bridge.computeGraceCoupling();
        
        // Verify theoretical properties
        this.verifyProperty(graceState.phi === 1.618, 'Grace φ = 1.618');
        this.verifyProperty(graceState.amplitude > 0, `Grace amplitude = ${graceState.amplitude.toFixed(3)}`);
        this.verifyProperty(graceState.active, 'Grace attractor active in FORMATION stage');
        this.verifyProperty(Math.abs(graceState.phase) <= Math.PI, `Grace phase = ${graceState.phase.toFixed(3)}`);
    }
    
    async testSovereigntyCoupling() {
        console.log('\n🏛️  Testing Sovereignty Attractor Coupling...');
        
        // Set up STABILITY stage with strong bivectors
        this.mathCore.cliffordField.components[5] = 4.0;   // e01
        this.mathCore.cliffordField.components[6] = 3.0;   // e02
        this.mathCore.updateCoherence();
        this.mathCore.updateBootstrapStage();
        
        const sovereigntyState = this.bridge.computeSovereigntyCoupling();
        
        this.verifyProperty(sovereigntyState.recursiveDepth >= 3, `Sovereignty depth = ${sovereigntyState.recursiveDepth}`);
        this.verifyProperty(sovereigntyState.complexity > 0, `Sovereignty complexity = ${sovereigntyState.complexity.toFixed(3)}`);
        this.verifyProperty(sovereigntyState.active, 'Sovereignty attractor active in STABILITY stage');
    }
    
    async testBireflectionCoupling() {
        console.log('\n🪞 Testing Bireflection Attractor Coupling...');
        
        // Set up STABILITY stage with strong vectors
        this.mathCore.cliffordField.components[1] = 2.0;   // e0
        this.mathCore.cliffordField.components[2] = 3.0;   // e1
        this.mathCore.cliffordField.components[3] = 1.0;   // e2
        this.mathCore.updateCoherence();
        this.mathCore.updateBootstrapStage();
        
        const bireflectionState = this.bridge.computeBireflectionCoupling();
        
        this.verifyProperty(bireflectionState.symmetryOrder === 2, 'Bireflection involution property');
        this.verifyProperty(bireflectionState.reflectionStrength > 0, `Reflection strength = ${bireflectionState.reflectionStrength.toFixed(3)}`);
        this.verifyProperty(Array.isArray(bireflectionState.mirrorAxis) && bireflectionState.mirrorAxis.length === 3, 'Mirror axis is 3D vector');
        
        // Verify axis normalization
        const axisMagnitude = Math.sqrt(bireflectionState.mirrorAxis.reduce((sum, a) => sum + a*a, 0));
        this.verifyProperty(Math.abs(axisMagnitude - 1.0) < 0.001, `Mirror axis normalized (magnitude=${axisMagnitude.toFixed(3)})`);
    }
    
    async testHebrewCoupling() {
        console.log('\n🔤 Testing Hebrew Letter Coupling...');
        
        // Set up UNIVERSE stage
        this.mathCore.bootstrapState.coherence = 20.0;
        this.mathCore.updateBootstrapStage();
        
        const hebrewState = this.bridge.computeHebrewCoupling();
        
        this.verifyProperty(hebrewState.letterStates.length >= 16, `Hebrew letters: ${hebrewState.letterStates.length}`);
        this.verifyProperty(hebrewState.totalCoherence === 20.0, `Total coherence: ${hebrewState.totalCoherence}`);
        this.verifyProperty(hebrewState.active, 'Hebrew network active in UNIVERSE stage');
        
        // Verify specific letter mappings
        const aleph = hebrewState.letterStates.find(l => l.hebrew === 'א');
        const bet = hebrewState.letterStates.find(l => l.hebrew === 'ב');
        
        this.verifyProperty(aleph && aleph.fsctf === 'τ', 'Aleph (א) → τ mapping');
        this.verifyProperty(bet && bet.fsctf === 'β', 'Bet (ב) → β mapping');
    }
    
    async test231GatesCoupling() {
        console.log('\n🚪 Testing 231-Gates Coupling...');
        
        const gatesState = this.bridge.compute231GatesCoupling();
        
        this.verifyProperty(gatesState.totalGateCount === 231, 'Total gate count = 231');
        this.verifyProperty(gatesState.gates.length === 231, 'Generated gates array = 231');
        this.verifyProperty(gatesState.activeGateCount >= 0, `Active gates: ${gatesState.activeGateCount}`);
        
        // Verify gate mathematical properties
        const sampleGate = gatesState.gates[0];
        this.verifyProperty(sampleGate.letterPair.length === 2, 'Gate has letter pair');
        this.verifyProperty(sampleGate.hebrewPair.length === 2, 'Gate has Hebrew pair');
        this.verifyProperty(sampleGate.fsctfPair.length === 2, 'Gate has FSCTF pair');
        this.verifyProperty(typeof sampleGate.strength === 'number', 'Gate has numeric strength');
    }
    
    verifyProperty(condition, description) {
        if (condition) {
            this.pass(`✅ ${description}`);
        } else {
            this.fail(`❌ ${description}`);
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
        console.log('\n' + '=' .repeat(80));
        console.log('📊 INTEGRATION TEST RESULTS');
        console.log('=' .repeat(80));
        
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const failed = this.testResults.filter(r => r.status === 'FAIL').length;
        const total = this.testResults.length;
        
        console.log(`Total Tests: ${total}`);
        console.log(`Passed: ${passed} ✅`);
        console.log(`Failed: ${failed} ${failed > 0 ? '❌' : '✅'}`);
        console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);
        
        if (failed === 0) {
            console.log('\n🎉 ALL INTEGRATION TESTS PASSED!');
            console.log('✅ Mathematical ↔ Attractor coupling is theoretically sound');
            console.log('✅ Bootstrap sequence progression verified');
            console.log('✅ All attractor coupling interfaces functional');
            console.log('\n📋 Integration Capabilities Verified:');
            console.log('  • VOID → EMERGENCE → FORMATION → STABILITY → UNIVERSE');
            console.log('  • Clifford field → Grace attractor (φ=1.618)');
            console.log('  • Bivector field → Sovereignty attractor (recursive depth)');
            console.log('  • Vector field → Bireflection attractor (mirror symmetry)');
            console.log('  • All components → Hebrew letter network (22 operators)');
            console.log('  • Hebrew combinations → 231-gates network');
            console.log('\n🚀 Ready for Phase 4: Visual Implementation');
            console.log('   Next: Create working unified visualization');
        } else {
            console.log('\n⚠️  INTEGRATION ISSUES DETECTED');
            console.log('❌ Fix coupling inconsistencies before visual implementation');
            
            console.log('\nFailed Tests:');
            this.testResults
                .filter(r => r.status === 'FAIL')
                .forEach(r => console.log(`  ${r.message}`));
                
            console.log('\n🛑 CRITICAL: Integration must be mathematically consistent');
            console.log('   Visual implementation depends on correct coupling');
        }
    }
}

// Run tests
const tester = new IntegrationTester();
tester.runAllTests();
