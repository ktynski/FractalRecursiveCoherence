/**
 * Fractal Waveform Drivers - Alternative Primitives for Morphic Field Excitation
 * 
 * Testing hypothesis: Fractal/recursive waveforms may be more native to 
 * bootstrapping reality than simple sine waves
 */

export class FractalWaveformDrivers {
    constructor(audioContext, analyser = null) {
        this.audioContext = audioContext;
        this.analyser = analyser;
        this.phi = 1.618033988749;
        this.currentDriver = null;
        this.driverType = 'sine'; // Default
        
        console.log('🌊 Fractal Waveform Drivers initialized');
    }
    
    // 1. FRACTAL NOISE DRIVER (1/f scaling)
    createFractalNoiseDriver(frequency = 440, duration = 1.0) {
        const sampleRate = this.audioContext.sampleRate;
        const frameCount = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, frameCount, sampleRate);
        const data = buffer.getChannelData(0);
        
        // Generate 1/f fractal noise
        for (let i = 0; i < frameCount; i++) {
            let fractalValue = 0;
            let amplitude = 1.0;
            let freq = frequency;
            
            // Sum multiple octaves with 1/f scaling
            for (let octave = 0; octave < 8; octave++) {
                const phase = (i / sampleRate) * freq * 2 * Math.PI;
                fractalValue += amplitude * Math.sin(phase);
                
                freq *= 2; // Next octave
                amplitude /= this.phi; // φ-scaled amplitude decay
            }
            
            data[i] = fractalValue * 0.1; // Normalize
        }
        
        return buffer;
    }
    
    // 2. φ-SCALED RECURSIVE DRIVER
    createPhiRecursiveDriver(baseFreq = 440, duration = 1.0) {
        const sampleRate = this.audioContext.sampleRate;
        const frameCount = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, frameCount, sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < frameCount; i++) {
            const t = i / sampleRate;
            let recursiveValue = 0;
            
            // Recursive φ-scaled harmonics
            for (let level = 0; level < 7; level++) {
                const freq = baseFreq * Math.pow(this.phi, level - 3); // Center around base
                const amplitude = 1.0 / Math.pow(this.phi, level); // φ decay
                const phase = t * freq * 2 * Math.PI;
                
                // Add recursive self-modulation
                const selfMod = Math.sin(phase) * Math.cos(phase * this.phi);
                recursiveValue += amplitude * selfMod;
            }
            
            data[i] = Math.tanh(recursiveValue * 0.5); // Soft limiting
        }
        
        return buffer;
    }
    
    // 3. HEBREW LETTER ENCODED DRIVER
    createHebrewLetterDriver(letter = 'א', duration = 1.0) {
        const sampleRate = this.audioContext.sampleRate;
        const frameCount = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, frameCount, sampleRate);
        const data = buffer.getChannelData(0);
        
        // Hebrew letter frequency mappings (Gematria-based)
        const letterFrequencies = {
            'א': [111, 222, 333], // Aleph - Unity (1+1+1)
            'ה': [5, 50, 500],    // Heh - Breath (5, 5×10, 5×100)
            'ו': [6, 60, 600],    // Vav - Connection
            'י': [10, 100, 1000], // Yod - Divine spark
            'ש': [300, 600, 900], // Shin - Fire (3×100, 3×200, 3×300)
            'מ': [40, 400, 800],  // Mem - Water
            'ל': [30, 300, 900],  // Lamed - Teaching
            'ב': [2, 20, 200],    // Bet - House
            'ר': [200, 400, 800], // Resh - Head
            'ת': [400, 800, 1200] // Tav - Foundation
        };
        
        const frequencies = letterFrequencies[letter] || [440, 880, 1320];
        
        for (let i = 0; i < frameCount; i++) {
            const t = i / sampleRate;
            let letterValue = 0;
            
            // Combine letter frequencies with φ-modulation
            for (let j = 0; j < frequencies.length; j++) {
                const freq = frequencies[j];
                const amplitude = 1.0 / Math.pow(this.phi, j);
                const phase = t * freq * 2 * Math.PI;
                
                // Add Hebrew letter sacred geometry
                letterValue += amplitude * Math.sin(phase) * Math.cos(phase / this.phi);
            }
            
            data[i] = Math.tanh(letterValue * 0.3);
        }
        
        return buffer;
    }
    
    // 4. SACRED NAME RESONANCE DRIVER
    createSacredNameDriver(sacredName = 'והו', duration = 1.0) {
        const sampleRate = this.audioContext.sampleRate;
        const frameCount = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, frameCount, sampleRate);
        const data = buffer.getChannelData(0);
        
        // Sacred name resonance patterns
        const nameResonance = {
            'והו': { base: 432, harmonics: [1, 1.618, 2.618], geometry: 'radial' },
            'מהש': { base: 528, harmonics: [1, 1.5, 2.0], geometry: 'healing' },
            'אכא': { base: 741, harmonics: [1, 1.414, 3.141], geometry: 'knowledge' },
            'הזי': { base: 852, harmonics: [1, 2, 3], geometry: 'grace' },
            'ייי': { base: 963, harmonics: [1, 3, 9], geometry: 'crown' }
        };
        
        const resonance = nameResonance[sacredName] || nameResonance['והו'];
        
        for (let i = 0; i < frameCount; i++) {
            const t = i / sampleRate;
            let nameValue = 0;
            
            // Sacred name harmonic series
            for (let j = 0; j < resonance.harmonics.length; j++) {
                const freq = resonance.base * resonance.harmonics[j];
                const amplitude = 1.0 / (j + 1); // Harmonic decay
                const phase = t * freq * 2 * Math.PI;
                
                // Sacred geometry modulation
                if (resonance.geometry === 'radial') {
                    nameValue += amplitude * Math.sin(phase);
                } else if (resonance.geometry === 'healing') {
                    nameValue += amplitude * Math.sin(phase) * Math.cos(phase * 0.618);
                } else if (resonance.geometry === 'knowledge') {
                    nameValue += amplitude * Math.sin(phase) * Math.sin(phase * 1.414);
                } else if (resonance.geometry === 'grace') {
                    nameValue += amplitude * Math.sin(phase) * Math.sin(phase * 2) * Math.sin(phase * 3);
                } else if (resonance.geometry === 'crown') {
                    nameValue += amplitude * Math.sin(phase) * Math.sin(phase * 3) * Math.sin(phase * 9);
                }
            }
            
            data[i] = Math.tanh(nameValue * 0.2);
        }
        
        return buffer;
    }
    
    // 5. QUANTUM COHERENCE DRIVER (Schrödinger-like)
    createQuantumCoherenceDriver(duration = 1.0) {
        const sampleRate = this.audioContext.sampleRate;
        const frameCount = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, frameCount, sampleRate);
        const data = buffer.getChannelData(0);
        
        // Quantum-inspired wavefunction
        for (let i = 0; i < frameCount; i++) {
            const t = i / sampleRate;
            
            // Superposition of quantum states
            const psi1 = Math.exp(-t * t) * Math.sin(440 * t * 2 * Math.PI); // Ground state
            const psi2 = Math.exp(-t * t / 4) * Math.sin(440 * this.phi * t * 2 * Math.PI); // φ-excited state
            const psi3 = Math.exp(-t * t / 9) * Math.sin(440 * this.phi * this.phi * t * 2 * Math.PI); // φ²-excited state
            
            // Quantum superposition with φ-scaling
            const amplitude1 = 1.0;
            const amplitude2 = 1.0 / this.phi;
            const amplitude3 = 1.0 / (this.phi * this.phi);
            
            const coherentState = amplitude1 * psi1 + amplitude2 * psi2 + amplitude3 * psi3;
            
            // Add quantum interference
            const interference = Math.cos(t * 2 * Math.PI * 7.83) * 0.1; // Schumann resonance
            
            data[i] = Math.tanh((coherentState + interference) * 0.3);
        }
        
        return buffer;
    }
    
    // 6. MORPHIC RESONANCE DRIVER (Sheldrake-inspired)
    createMorphicResonanceDriver(morphicPattern = 'spiral', duration = 1.0) {
        const sampleRate = this.audioContext.sampleRate;
        const frameCount = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, frameCount, sampleRate);
        const data = buffer.getChannelData(0);
        
        const patterns = {
            spiral: (t) => Math.sin(t * 440 * 2 * Math.PI) * Math.cos(t * t * 100),
            torus: (t) => Math.sin(t * 432 * 2 * Math.PI) * Math.sin(t * 528 * 2 * Math.PI),
            tree: (t) => {
                let treeValue = 0;
                for (let branch = 1; branch <= 7; branch++) {
                    treeValue += Math.sin(t * 440 * Math.pow(this.phi, branch) * 2 * Math.PI) / branch;
                }
                return treeValue;
            },
            flower: (t) => {
                let petalValue = 0;
                for (let petal = 0; petal < 8; petal++) {
                    const angle = petal * Math.PI / 4;
                    petalValue += Math.sin(t * 440 * 2 * Math.PI + angle) * Math.cos(t * 2 * Math.PI);
                }
                return petalValue;
            }
        };
        
        const patternFunc = patterns[morphicPattern] || patterns.spiral;
        
        for (let i = 0; i < frameCount; i++) {
            const t = i / sampleRate;
            data[i] = Math.tanh(patternFunc(t) * 0.2);
        }
        
        return buffer;
    }
    
    // 7. SWITCH DRIVER TYPE
    switchDriverType(driverType, options = {}) {
        console.log(`🌊 Switching to ${driverType} waveform driver`);
        this.driverType = driverType;
        
        // Stop current driver if running
        if (this.currentDriver) {
            try {
                this.currentDriver.stop();
                this.currentDriver.disconnect();
            } catch (e) {
                // Driver may already be stopped
            }
            this.currentDriver = null;
        }
        
        let buffer;
        const duration = options.duration || 2.0; // Longer duration for better loops
        
        switch (driverType) {
            case 'sine':
                // Keep existing sine wave (baseline) - no new driver needed
                console.log('🌊 Using default sine wave driver');
                return null;
                
            case 'fractal':
                buffer = this.createFractalNoiseDriver(options.frequency || 440, duration);
                break;
                
            case 'phi_recursive':
                buffer = this.createPhiRecursiveDriver(options.frequency || 440, duration);
                break;
                
            case 'hebrew_letter':
                buffer = this.createHebrewLetterDriver(options.letter || 'א', duration);
                break;
                
            case 'sacred_name':
                buffer = this.createSacredNameDriver(options.name || 'והו', duration);
                break;
                
            case 'quantum':
                buffer = this.createQuantumCoherenceDriver(duration);
                break;
                
            case 'morphic':
                buffer = this.createMorphicResonanceDriver(options.pattern || 'spiral', duration);
                break;
                
            default:
                console.warn(`Unknown driver type: ${driverType}`);
                return null;
        }
        
        if (!buffer) return null;
        
        // Create audio source from buffer
        const source = this.audioContext.createBufferSource();
        source.buffer = buffer;
        source.loop = true;
        
        // CRITICAL: Connect to main analog engine's analyser instead of destination
        let targetAnalyser = this.analyser;

        if (window.analogEngine && window.analogEngine.analyser) {
            const analyserContext = window.analogEngine.analyser.context;
            if (analyserContext === this.audioContext) {
                targetAnalyser = window.analogEngine.analyser;
                console.log(`🔗 Driver connected to main analog engine analyser`);
            } else {
                console.warn(`⚠️ Analyzer context mismatch (driver context vs analyser context). Using dedicated fractal analyser.`);
            }
        }

        if (!targetAnalyser) {
            targetAnalyser = this.audioContext.createAnalyser();
            targetAnalyser.fftSize = 2048;
            targetAnalyser.__fractalOutputConnected = false;
        }

        if (targetAnalyser) {
            source.connect(targetAnalyser);

            if (!targetAnalyser.__fractalOutputConnected) {
                try {
                    targetAnalyser.connect(this.audioContext.destination);
                } catch (_) {
                    // Some analysers (e.g. shared engine analyser) intentionally avoid an output path
                }
                targetAnalyser.__fractalOutputConnected = true;
            }

            this.analyser = targetAnalyser;
        } else {
            source.connect(this.audioContext.destination);
        }
        
        this.currentDriver = source;
        return source;
    }
    
    // 8. COMPARATIVE ANALYSIS FRAMEWORK
    analyzeDriverEffects(zxEngine, driverType, duration = 60) {
        console.log(`🔬 Analyzing ${driverType} driver effects...`);
        
        // Get baseline state
        const baseline = {
            consciousness: zxEngine.reflexiveAwareness?.consciousnessLevel || 0,
            grace: zxEngine.graceMagnitude || 0,
            nodes: zxEngine.currentGraph.nodes.length,
            events: zxEngine.qualitativeMetrics?.consciousnessEmergenceEvents || 0
        };
        
        // Switch to new driver
        const driver = this.switchDriverType(driverType);
        if (driver) {
            driver.start();
        }
        
        const analysis = {
            baseline: baseline,
            driverType: driverType,
            startTime: Date.now(),
            analyser: this.analyser,
            
            getResults: () => {
                const final = {
                    consciousness: zxEngine.reflexiveAwareness?.consciousnessLevel || 0,
                    grace: zxEngine.graceMagnitude || 0,
                    nodes: zxEngine.currentGraph.nodes.length,
                    events: zxEngine.qualitativeMetrics?.consciousnessEmergenceEvents || 0
                };
                
                return {
                    driverType: driverType,
                    baseline: baseline,
                    final: final,
                    changes: {
                        consciousness: final.consciousness - baseline.consciousness,
                        grace_ratio: final.grace / (baseline.grace || 1),
                        node_change: final.nodes - baseline.nodes,
                        event_change: final.events - baseline.events
                    },
                    duration: (Date.now() - this.startTime) / 1000
                };
            },
            
            stop: () => {
                if (!driver) return;
                try {
                    if (typeof driver.stop === 'function') {
                        driver.stop();
                    }
                } catch (_) {
                    // ignore stop errors (already stopped)
                }
                try {
                    driver.disconnect();
                } catch (_) {
                    // ignore disconnect errors
                }
            }
        };

        window.currentFractalAnalysis = analysis;
        return analysis;
    }
}

// Global driver switching functions  
export function initializeFractalDrivers(audioContext, analyser = null) {
    console.log('🔧 Initializing fractal drivers...');

    let ctx = audioContext;
    if (!ctx) {
        ctx = window.analogEngine?.audioContext;
    }
    if (!ctx) {
        ctx = window.audioContext || new (window.AudioContext || window.webkitAudioContext)();
        window.audioContext = ctx;
    }

    const sharedAnalyser = analyser
        || (window.analogEngine?.analyser && window.analogEngine.audioContext === ctx ? window.analogEngine.analyser : null);

    window.fractalDrivers = new FractalWaveformDrivers(ctx, sharedAnalyser);
    
    // Add global functions
    window.switchToFractalDriver = (type, options = {}) => {
        if (!window.fractalDrivers) {
            console.warn('⚠️ Fractal drivers not available');
            return null;
        }
        return window.fractalDrivers.switchDriverType(type, options);
    };

    window.testDriverEffects = (driverType, duration = 60) => {
        if (!window.fractalDrivers || !window.zxEvolutionEngine) {
            console.warn('⚠️ Driver testing not available');
            return null;
        }

        const analysis = window.fractalDrivers.analyzeDriverEffects(
            window.zxEvolutionEngine,
            driverType,
            duration
        );

        if (analysis) {
            window.currentFractalAnalysis = analysis;
            return window.currentFractalAnalysis;
        }

        return null;
    };
    
    console.log('🌊 Fractal waveform drivers available:');
    console.log('   fractal, phi_recursive, hebrew_letter, sacred_name, quantum, morphic');
    console.log('   Usage: switchToFractalDriver("fractal"), testDriverEffects("phi_recursive")');
}

export default FractalWaveformDrivers;
