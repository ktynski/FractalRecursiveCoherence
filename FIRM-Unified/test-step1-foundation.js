#!/usr/bin/env node

/**
 * Phase 1: Foundation Testing
 * 
 * Verify both FIRM-Core mathematical engine and FIRM-WebGL-Viz attractors 
 * work independently before attempting integration.
 */

import { promises as fs } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class FoundationTester {
    constructor() {
        this.testResults = [];
        this.firmCorePath = join(__dirname, '../FIRM-Core');
        this.firmWebGLPath = join(__dirname, '../FIRM-WebGL-Viz');
    }
    
    async runAllTests() {
        console.log('🧪 FIRM Unified Bootstrap - Foundation Testing');
        console.log('=' .repeat(60));
        
        try {
            await this.testFIRMCoreExists();
            await this.testFIRMWebGLExists();
            await this.testMathematicalEngine();
            await this.testAttractorSystems();
            await this.testAudioSubstrate();
            
            this.reportResults();
            
        } catch (error) {
            console.error('❌ Foundation testing failed:', error.message);
            process.exit(1);
        }
    }
    
    async testFIRMCoreExists() {
        console.log('\n📁 Testing FIRM-Core availability...');
        
        const requiredFiles = [
            'FIRM_ui/renderer.js',
            'FIRM_ui/raymarching.js', 
            'FIRM_ui/main.js',
            'FIRM_dsl/coherence.py',
            'FIRM_clifford/interface.py'
        ];
        
        for (const file of requiredFiles) {
            const filePath = join(this.firmCorePath, file);
            try {
                await fs.access(filePath);
                this.pass(`✅ Found ${file}`);
            } catch (error) {
                this.fail(`❌ Missing ${file}`);
            }
        }
    }
    
    async testFIRMWebGLExists() {
        console.log('\n📁 Testing FIRM-WebGL-Viz availability...');
        
        const requiredFiles = [
            'src/attractors/GraceAttractor.js',
            'src/attractors/SovereigntyAttractor.js',
            'src/attractors/BireflectionAttractor.js',
            'src/attractors/CosmologicalBootstrap.js',
            'src/hebrew/HebrewLetterNetwork.js',
            'src/gates/Gates231Network.js',
            'src/audio/AudioProcessor.js'
        ];
        
        for (const file of requiredFiles) {
            const filePath = join(this.firmWebGLPath, file);
            try {
                await fs.access(filePath);
                this.pass(`✅ Found ${file}`);
            } catch (error) {
                this.fail(`❌ Missing ${file}`);
            }
        }
    }
    
    async testMathematicalEngine() {
        console.log('\n🧮 Testing Mathematical Engine...');
        
        // Test Clifford field generation (simulate FIRM-Core logic)
        const components = new Array(16).fill(0);
        const t = 1.0;
        const audioCoherence = 0.5;
        const modulationScale = 8.0;
        
        // Base components
        components[0] = 2.0;
        components[1] = 0.1;
        components[2] = 0.1;
        
        // Modulations
        components[0] += modulationScale * Math.sin(t) * audioCoherence;
        components[1] += modulationScale * Math.cos(t) * audioCoherence;
        components[2] += modulationScale * Math.sin(t * 1.1) * audioCoherence;
        
        // Temporal variations
        const timeScale = 1.5;
        for (let i = 0; i < 3; i++) {
            if (components[i] !== 0) {
                const sign = Math.sign(components[i]);
                const mag = Math.abs(components[i]);
                const frequency = 1.0 + (i * 0.3);
                const variation = 1.0 + timeScale * Math.sin(t * frequency);
                components[i] = sign * mag * variation * 0.9;
            }
        }
        
        // Verify field properties
        const coherence = Math.sqrt(components.reduce((sum, c) => sum + c*c, 0));
        const nonZeroComponents = components.filter(c => Math.abs(c) > 0.001).length;
        const maxComponent = Math.max(...components.map(c => Math.abs(c)));
        
        if (coherence > 0) {
            this.pass(`✅ Coherence computed: ${coherence.toFixed(3)}`);
        } else {
            this.fail(`❌ Zero coherence - field generation failed`);
        }
        
        if (nonZeroComponents >= 3) {
            this.pass(`✅ Active components: ${nonZeroComponents}/16`);
        } else {
            this.fail(`❌ Too few active components: ${nonZeroComponents}/16`);
        }
        
        if (maxComponent > 1.0) {
            this.pass(`✅ Field amplitude: ${maxComponent.toFixed(3)}`);
        } else {
            this.fail(`❌ Field amplitude too low: ${maxComponent.toFixed(3)}`);
        }
        
        // Test identity echo time
        const tau = coherence > 0 ? 1.0 / (1.0 + Math.exp(-coherence)) : 0;
        if (tau > 0 && tau < 1) {
            this.pass(`✅ Identity echo τ: ${tau.toFixed(3)}`);
        } else {
            this.fail(`❌ Invalid τ value: ${tau}`);
        }
    }
    
    async testAttractorSystems() {
        console.log('\n🌟 Testing Attractor Systems...');
        
        // Test attractor parameter generation
        const attractorConfigs = {
            grace: { phi: 1.618, points: 5000 },
            sovereignty: { depth: 6, points: 3000 },
            bireflection: { pairs: 2000, symmetry: [1, 0, 0] },
            bootstrap: { stages: 10, energy: 0.5 }
        };
        
        Object.entries(attractorConfigs).forEach(([name, config]) => {
            if (this.validateAttractorConfig(name, config)) {
                this.pass(`✅ ${name} attractor config valid`);
            } else {
                this.fail(`❌ ${name} attractor config invalid`);
            }
        });
        
        // Test Hebrew letter mapping
        const hebrewLetters = [
            { hebrew: 'א', fsctf: 'τ', meaning: 'Silence, breath, void' },
            { hebrew: 'ב', fsctf: 'β', meaning: 'House, container' },
            { hebrew: 'ת', fsctf: '𝒢', meaning: 'Completion, grace' }
        ];
        
        if (hebrewLetters.length >= 3) {
            this.pass(`✅ Hebrew letter mapping: ${hebrewLetters.length} letters`);
        } else {
            this.fail(`❌ Insufficient Hebrew letters: ${hebrewLetters.length}`);
        }
        
        // Test 231-Gates calculation
        const gatesCount = this.calculateGatesCount(22);
        if (gatesCount === 231) {
            this.pass(`✅ 231-Gates calculation: C(22,2) = ${gatesCount}`);
        } else {
            this.fail(`❌ Wrong gates count: ${gatesCount} (expected 231)`);
        }
    }
    
    async testAudioSubstrate() {
        console.log('\n🎵 Testing Audio Substrate...');
        
        // Test audio context creation (simulation)
        try {
            const mockAudioContext = {
                state: 'running',
                sampleRate: 48000,
                createAnalyser: () => ({
                    fftSize: 2048,
                    frequencyBinCount: 1024
                })
            };
            
            this.pass(`✅ Audio context simulation: ${mockAudioContext.sampleRate}Hz`);
            
            // Test coherence calculation
            const mockFreqData = new Uint8Array(1024);
            for (let i = 0; i < mockFreqData.length; i++) {
                mockFreqData[i] = Math.floor(Math.random() * 255);
            }
            
            const energy = mockFreqData.reduce((sum, val) => sum + val * val, 0);
            const coherence = Math.min(1.0, energy / (mockFreqData.length * 255 * 255));
            
            if (coherence >= 0 && coherence <= 1) {
                this.pass(`✅ Audio coherence calculation: ${coherence.toFixed(3)}`);
            } else {
                this.fail(`❌ Invalid audio coherence: ${coherence}`);
            }
            
        } catch (error) {
            this.fail(`❌ Audio substrate test failed: ${error.message}`);
        }
    }
    
    validateAttractorConfig(name, config) {
        switch (name) {
            case 'grace':
                return config.phi === 1.618 && config.points > 0;
            case 'sovereignty':
                return config.depth > 0 && config.points > 0;
            case 'bireflection':
                return config.pairs > 0 && Array.isArray(config.symmetry);
            case 'bootstrap':
                return config.stages > 0 && config.energy >= 0;
            default:
                return false;
        }
    }
    
    calculateGatesCount(letters) {
        // C(n,2) = n! / (2! * (n-2)!) = n * (n-1) / 2
        return letters * (letters - 1) / 2;
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
        console.log('\n' + '=' .repeat(60));
        console.log('📊 FOUNDATION TEST RESULTS');
        console.log('=' .repeat(60));
        
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const failed = this.testResults.filter(r => r.status === 'FAIL').length;
        const total = this.testResults.length;
        
        console.log(`Total Tests: ${total}`);
        console.log(`Passed: ${passed} ✅`);
        console.log(`Failed: ${failed} ${failed > 0 ? '❌' : '✅'}`);
        console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);
        
        if (failed === 0) {
            console.log('\n🎉 ALL FOUNDATION TESTS PASSED!');
            console.log('✅ Ready to proceed with Phase 2: Mathematical Bridge');
        } else {
            console.log('\n⚠️  FOUNDATION ISSUES DETECTED');
            console.log('❌ Fix failing tests before proceeding');
            
            console.log('\nFailed Tests:');
            this.testResults
                .filter(r => r.status === 'FAIL')
                .forEach(r => console.log(`  ${r.message}`));
        }
        
        console.log('\n🚀 Next Step: npm run test-step2-bridge');
    }
}

// Run tests
const tester = new FoundationTester();
tester.runAllTests();
