/**
 * FIRM Framework WebGL Visualization
 * Cosmological Sequence: Proper universe creation according to FIRM theory
 * Void (∅) → Bootstrap (𝒳) → Grace (𝒢) → Sovereignty (Ψ) → Bireflection (β) → Hebrew Network
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { CosmologicalGrace } from './attractors/CosmologicalGrace.js';
import { AudioProcessor } from './audio/AudioProcessor.js';
import { HebrewLetterNetwork } from './hebrew/HebrewLetterNetwork.js';
import { Gates231Network } from './gates/Gates231Network.js';
import { SovereigntyAttractor } from './attractors/SovereigntyAttractor.js';
import { BireflectionAttractor } from './attractors/BireflectionAttractor.js';
import { TransferEntropyProcessor } from './coupling/TransferEntropyProcessor.js';
import { CosmologicalBootstrap } from './attractors/CosmologicalBootstrap.js';
import { CosmologicalSequence } from './cosmology/CosmologicalSequence.js';

class FIRMVisualization {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.animationId = null;
        
        // Performance monitoring
        this.frameCount = 0;
        this.lastTime = performance.now();
        this.fps = 0;
        
        // Rendering controls (visual only - no theory changes)
        this.renderingSettings = {
            particleSize: 0.5,
            opacity: 0.4,
            background: 0.15,
            systemSeparation: 1.0
        };
        
        // System visibility toggles
        this.systemVisibility = {
            grace: true,
            sovereignty: true,
            bireflection: true,
            bootstrap: true,
            hebrew: true,
            gates: true
        };
        
        // Cosmological Sequence Controller
        this.cosmologicalSequence = null;
        
        // FIRM Attractors
        this.graceAttractor = null;
        this.sovereigntyAttractor = null;
        this.bireflectionAttractor = null;
        this.bootstrapAttractor = null;
        this.clock = new THREE.Clock();
        
        // Audio processing
        this.audioProcessor = null;
        this.audioFeatures = null;
        
        // Hebrew Letters Network
        this.hebrewNetwork = null;
        
        // 231-Gates Network
        this.gates231Network = null;
        
        // Transfer Entropy Coupling
        this.transferEntropyProcessor = null;
        this.teResults = null;
        
        // Status tracking
        this.status = {
            webgl: false,
            scene: false,
            rendering: false,
            cosmologicalSequence: false,
            graceAttractor: false,
            audioProcessor: false,
            hebrewNetwork: false,
            gates231Network: false,
            sovereigntyAttractor: false,
            bireflectionAttractor: false,
            bootstrapAttractor: false,
            transferEntropyCoupling: false
        };
        
        this.init();
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logContent = document.getElementById('log-content');
        const colorMap = {
            info: '#00ff00',
            warning: '#ffff00', 
            error: '#ff0000',
            success: '#00ffff'
        };
        
        const logEntry = document.createElement('div');
        logEntry.style.color = colorMap[type] || '#ffffff';
        logEntry.innerHTML = `[${timestamp}] ${message}`;
        logContent.appendChild(logEntry);
        
        // Keep only last 20 entries
        while (logContent.children.length > 20) {
            logContent.removeChild(logContent.firstChild);
        }
        
        // Auto-scroll to bottom
        logContent.parentElement.scrollTop = logContent.parentElement.scrollHeight;
        
        console.log(`[FIRM] ${message}`);
    }
    
    updateStatus(component, active) {
        this.status[component] = active;
        const statusElements = document.querySelectorAll('#status div');
        const statusMap = {
            'webgl': 0,
            'scene': 1, 
            'rendering': 2,
            'graceAttractor': 3,
            'audioProcessor': 4,
            'hebrewNetwork': 5,
            'gates231Network': 6,
            'sovereigntyAttractor': 7,
            'bireflectionAttractor': 8,
            'transferEntropyCoupling': 9
        };
        
        if (statusMap[component] !== undefined) {
            const indicator = statusElements[statusMap[component]]?.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${active ? 'status-active' : 'status-inactive'}`;
            }
        }
    }
    
    async init() {
        try {
            this.log('🌌 Initializing FIRM Cosmological Sequence...', 'info');
            
            // Step 1: Check WebGL support
            if (!this.checkWebGLSupport()) {
                throw new Error('WebGL not supported');
            }
            
            // Step 2: Create scene, camera, renderer
            await this.setupScene();
            
            // Step 3: Initialize Cosmological Sequence Controller
            await this.initializeCosmologicalSequence();
            
            // Step 4: Initialize Audio Processing (for creation energy)
            await this.initializeAudio();
            
            // Step 5: Create attractors in cosmological order (but don't activate yet)
            await this.createCosmologicalBootstrap();
            await this.createGraceAttractor();
            await this.createSovereigntyAttractor();
            await this.createBireflectionAttractor();
            
            // Step 6: Create Hebrew Network (activated last)
            await this.createHebrewNetwork();
            await this.create231GatesNetwork();
            
            // Step 7: Initialize Transfer Entropy Coupling
            await this.initializeTransferEntropyCoupling();
            
            // Step 8: Setup controls and UI
            this.setupControls();
            this.setupCosmologicalControls();
            this.setupRenderingControls();
            
            // Step 9: Start the cosmological sequence
            this.startRenderLoop();
            
            this.log('🎯 COSMOLOGICAL SEQUENCE ACTIVE: Starting from VOID (∅)', 'success');
            
            this.log('✅ Cosmological sequence initialized successfully!', 'success');
            
        } catch (error) {
            this.log(`❌ Initialization failed: ${error.message}`, 'error');
        }
    }
    
    checkWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
            
            if (!gl) {
                this.log('❌ WebGL not supported', 'error');
                this.updateStatus('webgl', false);
                return false;
            }
            
            this.log('✅ WebGL support detected', 'success');
            this.log(`GPU: ${gl.getParameter(gl.RENDERER)}`, 'info');
            this.log(`WebGL Version: ${gl.getParameter(gl.VERSION)}`, 'info');
            this.updateStatus('webgl', true);
            return true;
            
        } catch (error) {
            this.log(`❌ WebGL check failed: ${error.message}`, 'error');
            this.updateStatus('webgl', false);
            return false;
        }
    }
    
    async setupScene() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000011); // Dark blue background
        this.log('📦 Scene created', 'info');
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            75, // FOV
            window.innerWidth / window.innerHeight, // Aspect ratio
            0.1, // Near plane
            1000 // Far plane
        );
        this.camera.position.set(0, 0, 5);
        this.log('📷 Camera created and positioned', 'info');
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Add renderer to DOM
        const container = document.getElementById('container');
        container.appendChild(this.renderer.domElement);
        this.log('🖥️ Renderer created and added to DOM', 'info');
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        this.updateStatus('scene', true);
    }
    
    async createGraceAttractor() {
        try {
            this.log('🌟 Creating Cosmological Grace Attractor (φ-spiral emergence)...', 'info');
            
            // Create Cosmological Grace attractor
            this.graceAttractor = new CosmologicalGrace();
            const graceObject = this.graceAttractor.getObject3D();
            this.scene.add(graceObject);
            
            // Log attractor info
            const metrics = this.graceAttractor.getGraceMetrics();
            this.log(`φ = ${metrics.phi.toFixed(4)} (Golden Ratio)`, 'info');
            this.log(`Hausdorff Dimension: ${metrics.hausdorffDimension.toFixed(3)}`, 'info');
            this.log(`Particle Count: ${metrics.particleCount}`, 'info');
            this.log(`Emergence Phase: ${metrics.phase}`, 'info');
            
            // Add some ambient light for better visibility
            const ambientLight = new THREE.AmbientLight(0x202040, 0.3);
            this.scene.add(ambientLight);
            
            this.updateStatus('graceAttractor', true);
            this.updateObjectCount();
            this.log('✨ Grace Attractor created successfully', 'success');
            
        } catch (error) {
            this.log(`❌ Grace Attractor creation failed: ${error.message}`, 'error');
            this.updateStatus('graceAttractor', false);
            throw error;
        }
    }
    
    async initializeAudio() {
        try {
            this.log('🎵 Initializing Audio Integration...', 'info');
            
            // Create audio processor
            this.audioProcessor = new AudioProcessor();
            
            // Set up audio feature callback
            this.audioProcessor.onFeatures((features) => {
                this.audioFeatures = features;
                this.updateVisualsFromAudio(features);
            });
            
            // Initialize (will request microphone permission)
            await this.audioProcessor.initialize();
            
            // Start analysis
            this.audioProcessor.startAnalysis();
            
            this.updateStatus('audioProcessor', true);
            this.log('🎤 Audio integration successful', 'success');
            this.log('Grace Attractor now responds to audio input', 'info');
            
        } catch (error) {
            this.log(`⚠️ Audio initialization failed: ${error.message}`, 'warning');
            this.log('Visualization will continue without audio input', 'info');
            this.updateStatus('audioProcessor', false);
            // Don't throw - continue without audio
        }
    }
    
    async createHebrewNetwork() {
        try {
            this.log('🕎 Creating Hebrew Letters Network (22 letters)...', 'info');
            
            // Create Hebrew letter network
            this.hebrewNetwork = new HebrewLetterNetwork();
            const hebrewObject = this.hebrewNetwork.getObject3D();
            
            // Position the network to the side of the Grace Attractor
            hebrewObject.position.set(4, 0, 0);
            hebrewObject.scale.setScalar(0.8); // Slightly smaller scale
            
            this.scene.add(hebrewObject);
            
            // Log network info
            const info = this.hebrewNetwork.getInfo();
            this.log(`22 Hebrew Letters: ${info.letterCount} nodes`, 'info');
            this.log(`Tree of Life: ${info.connectionCount} connections`, 'info');
            this.log(`Sephiroth: ${info.sephiroth.length} levels`, 'info');
            this.log(`FSCTF Operators: ${info.fsctfOperators.join(', ')}`, 'info');
            
            this.updateStatus('hebrewNetwork', true);
            this.updateObjectCount();
            this.log('✨ Hebrew Letters Network created successfully', 'success');
            
        } catch (error) {
            this.log(`❌ Hebrew Network creation failed: ${error.message}`, 'error');
            this.updateStatus('hebrewNetwork', false);
            throw error;
        }
    }
    
    async create231GatesNetwork() {
        try {
            this.log('🔗 Creating 231-Gates Network (C(22,2) pairs)...', 'info');
            
            // Get Hebrew letters data for gate generation
            const hebrewLettersData = this.hebrewNetwork ? this.hebrewNetwork.hebrewLetters : [];
            
            // Create 231-Gates network
            this.gates231Network = new Gates231Network(hebrewLettersData);
            const gatesObject = this.gates231Network.getObject3D();
            
            // Position the gates network overlaying the Hebrew network
            gatesObject.position.set(4, 0, -1); // Slightly behind Hebrew network
            gatesObject.scale.setScalar(0.8);
            
            this.scene.add(gatesObject);
            
            // Log network info
            const info = this.gates231Network.getInfo();
            this.log(`${info.totalGates} total gates (${info.combinatorics})`, 'info');
            this.log(`${info.activeGates} active gates displayed`, 'info');
            this.log(`${info.motifTypes} unique motif types`, 'info');
            this.log(`Motifs: ${Object.keys(info.motifCounts).slice(0, 5).join(', ')}...`, 'info');
            
            this.updateStatus('gates231Network', true);
            this.updateObjectCount();
            this.log('✨ 231-Gates Network created successfully', 'success');
            
        } catch (error) {
            this.log(`❌ 231-Gates Network creation failed: ${error.message}`, 'error');
            this.updateStatus('gates231Network', false);
            throw error;
        }
    }
    
    async createSovereigntyAttractor() {
        try {
            this.log('👑 Creating Sovereignty Attractor (recursive self-composition)...', 'info');
            
            // Create Sovereignty attractor
            this.sovereigntyAttractor = new SovereigntyAttractor();
            const sovereigntyObject = this.sovereigntyAttractor.getObject3D();
            
            // Position the sovereignty attractor opposite to Grace attractor
            sovereigntyObject.position.set(-3, 1, 2);
            sovereigntyObject.scale.setScalar(0.7); // Slightly smaller for balance
            
            this.scene.add(sovereigntyObject);
            
            // Log attractor info
            const info = this.sovereigntyAttractor.getInfo();
            this.log(`Recursive Depth: ${info.recursiveDepth}`, 'info');
            this.log(`Fractal Dimension: ${info.dimension.toFixed(3)}`, 'info');
            this.log(`Particle Count: ${info.particleCount}`, 'info');
            this.log(`Self-Reference: ${info.selfReference}`, 'info');
            this.log(`Autonomy: ${info.autonomy}`, 'info');
            
            this.updateStatus('sovereigntyAttractor', true);
            this.updateObjectCount();
            this.log('✨ Sovereignty Attractor created successfully', 'success');
            
        } catch (error) {
            this.log(`❌ Sovereignty Attractor creation failed: ${error.message}`, 'error');
            this.updateStatus('sovereigntyAttractor', false);
            throw error;
        }
    }
    
    async createBireflectionAttractor() {
        try {
            this.log('🪞 Creating Bireflection Attractor (mirror symmetry)...', 'info');
            
            // Create Bireflection attractor
            this.bireflectionAttractor = new BireflectionAttractor();
            const bireflectionObject = this.bireflectionAttractor.getObject3D();
            
            // Position the bireflection attractor to showcase symmetry
            bireflectionObject.position.set(0, -2.5, 1);
            bireflectionObject.scale.setScalar(0.9); // Slightly smaller for balance
            
            this.scene.add(bireflectionObject);
            
            // Log attractor info
            const info = this.bireflectionAttractor.getInfo();
            this.log(`Mirror Pairs: ${info.mirrorPairs}`, 'info');
            this.log(`Fractal Dimension: ${info.dimension.toFixed(3)}`, 'info');
            this.log(`Particle Count: ${info.particleCount}`, 'info');
            this.log(`Reflection Axis: (${info.reflectionAxis.x}, ${info.reflectionAxis.y}, ${info.reflectionAxis.z})`, 'info');
            this.log(`Involution Depth: ${info.involutionDepth}`, 'info');
            
            // Get symmetry analysis
            const symmetryAnalysis = this.bireflectionAttractor.getSymmetryAnalysis();
            this.log(`Symmetry Ratio: ${symmetryAnalysis.symmetryRatio.toFixed(3)}`, 'info');
            this.log(`${symmetryAnalysis.involutionProperty}`, 'info');
            
            this.updateStatus('bireflectionAttractor', true);
            this.updateObjectCount();
            this.log('✨ Bireflection Attractor created successfully', 'success');
            
        } catch (error) {
            this.log(`❌ Bireflection Attractor creation failed: ${error.message}`, 'error');
            this.updateStatus('bireflectionAttractor', false);
            throw error;
        }
    }
    
    async createBootstrapAttractor() {
        try {
            this.log('🚀 Creating Bootstrap Attractor (ex nihilo generation)...', 'info');
            
            // Create Bootstrap attractor
            this.bootstrapAttractor = new BootstrapAttractor();
            
            // Add to scene
            this.scene.add(this.bootstrapAttractor.getObject3D());
            
            // Log Bootstrap metrics
            const metrics = this.bootstrapAttractor.getBootstrapMetrics();
            this.log(`Manifestation Steps: ${metrics.manifestationSteps}/${10}`, 'info');
            this.log(`Current Dimension: ${metrics.currentDimension.toFixed(3)}`, 'info');
            this.log(`Structure Count: ${metrics.structureCount}`, 'info');
            this.log(`Creation Energy: ${metrics.creationEnergy.toFixed(3)}`, 'info');
            this.log(`Hebrew Letter: ב (Bet) - container/house`, 'info');
            
            this.updateStatus('bootstrapAttractor', true);
            this.log('✨ Bootstrap Attractor created successfully', 'success');
        } catch (error) {
            this.log(`❌ Bootstrap Attractor creation failed: ${error.message}`, 'error');
            this.updateStatus('bootstrapAttractor', false);
            throw error;
        }
    }
    
    async initializeCosmologicalSequence() {
        try {
            this.log('🌌 Initializing Cosmological Sequence Controller...', 'info');
            
            // Create cosmological sequence controller
            this.cosmologicalSequence = new CosmologicalSequence();
            
            this.updateStatus('cosmologicalSequence', true);
            this.log('✨ Cosmological Sequence Controller created successfully', 'success');
            this.log('Starting in Phase 0: VOID (∅) - Pure emptiness', 'info');
        } catch (error) {
            this.log(`❌ Cosmological Sequence initialization failed: ${error.message}`, 'error');
            this.updateStatus('cosmologicalSequence', false);
            throw error;
        }
    }
    
    async createCosmologicalBootstrap() {
        try {
            this.log('🚀 Creating Cosmological Bootstrap (ex nihilo generation)...', 'info');
            
            // Create cosmological bootstrap attractor
            this.bootstrapAttractor = new CosmologicalBootstrap();
            
            // Add to scene
            this.scene.add(this.bootstrapAttractor.getObject3D());
            
            // Position at origin (where creation begins)
            this.bootstrapAttractor.getObject3D().position.set(0, 0, 0);
            
            // Log Bootstrap metrics
            const metrics = this.bootstrapAttractor.getBootstrapMetrics();
            this.log(`Generation Step: ${metrics.generationStep}/${metrics.maxSteps}`, 'info');
            this.log(`Current Dimension: ${metrics.currentDimension.toFixed(3)}`, 'info');
            this.log(`Structure Count: ${metrics.structureCount}`, 'info');
            this.log(`Phase: ${metrics.phase}`, 'info');
            this.log(`Hebrew Letter: ב (Bet) - container/house`, 'info');
            
            this.updateStatus('bootstrapAttractor', true);
            this.log('✨ Cosmological Bootstrap created successfully', 'success');
        } catch (error) {
            this.log(`❌ Cosmological Bootstrap creation failed: ${error.message}`, 'error');
            this.updateStatus('bootstrapAttractor', false);
            throw error;
        }
    }
    
    setupCosmologicalControls() {
        try {
            this.log('🎮 Setting up Cosmological Controls...', 'info');
            
            // Create cosmological control panel
            const controlsContainer = document.createElement('div');
            controlsContainer.id = 'cosmological-controls';
            controlsContainer.style.cssText = `
                position: fixed;
                bottom: 10px;
                right: 10px;
                width: 300px;
                padding: 15px;
                background: rgba(0,0,0,0.9);
                border-radius: 8px;
                border: 1px solid #333;
                color: white;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                z-index: 1000;
            `;
            
            controlsContainer.innerHTML = `
                <div style="color: #fff; font-size: 14px; margin-bottom: 10px; text-align: center;">
                    <strong>🌌 Cosmological Sequence</strong>
                </div>
                <div id="current-phase" style="margin-bottom: 10px; color: #00ffff;">
                    Phase 0: VOID (∅)
                </div>
                <div id="phase-description" style="margin-bottom: 10px; color: #ccc; font-size: 11px;">
                    Pure emptiness - measure-zero initial set
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="background: #333; height: 10px; border-radius: 5px; overflow: hidden;">
                        <div id="phase-progress" style="background: linear-gradient(90deg, #ff69b4, #00ffff); height: 100%; width: 0%; transition: width 0.3s;"></div>
                    </div>
                </div>
                <div style="display: flex; gap: 5px; margin-bottom: 10px;">
                    <button id="prev-phase" style="flex: 1; padding: 5px; background: #444; color: white; border: none; border-radius: 3px; cursor: pointer;">◀ Prev</button>
                    <button id="pause-resume" style="flex: 1; padding: 5px; background: #444; color: white; border: none; border-radius: 3px; cursor: pointer;">⏸️ Pause</button>
                    <button id="next-phase" style="flex: 1; padding: 5px; background: #444; color: white; border: none; border-radius: 3px; cursor: pointer;">Next ▶</button>
                </div>
                <div style="margin-bottom: 10px;">
                    <label style="color: #ccc; font-size: 11px;">Speed: <span id="speed-value">1.0x</span></label>
                    <input type="range" id="cosmological-speed" min="0.1" max="3.0" step="0.1" value="1.0" style="width: 100%;">
                </div>
                <div id="hebrew-letter" style="text-align: center; font-size: 16px; color: #ffd700;">
                    ∅
                </div>
            `;
            
            document.body.appendChild(controlsContainer);
            
            // Add event listeners
            document.getElementById('prev-phase').addEventListener('click', () => {
                if (this.cosmologicalSequence) {
                    this.cosmologicalSequence.retreatPhase();
                }
            });
            
            document.getElementById('next-phase').addEventListener('click', () => {
                if (this.cosmologicalSequence) {
                    this.cosmologicalSequence.advancePhase();
                }
            });
            
            document.getElementById('pause-resume').addEventListener('click', (e) => {
                if (this.cosmologicalSequence) {
                    if (this.cosmologicalSequence.autoAdvance) {
                        this.cosmologicalSequence.pause();
                        e.target.textContent = '▶️ Resume';
                    } else {
                        this.cosmologicalSequence.resume();
                        e.target.textContent = '⏸️ Pause';
                    }
                }
            });
            
            document.getElementById('cosmological-speed').addEventListener('input', (e) => {
                const speed = parseFloat(e.target.value);
                document.getElementById('speed-value').textContent = speed.toFixed(1) + 'x';
                if (this.cosmologicalSequence) {
                    this.cosmologicalSequence.setSpeed(speed * 0.002);
                }
            });
            
            this.log('✨ Cosmological Controls created successfully', 'success');
        } catch (error) {
            this.log(`❌ Cosmological Controls setup failed: ${error.message}`, 'error');
        }
    }
    
    async initializeTransferEntropyCoupling() {
        try {
            this.log('🔗 Initializing Transfer Entropy Coupling...', 'info');
            
            // Create Transfer Entropy Processor
            this.transferEntropyProcessor = new TransferEntropyProcessor();
            
            // Log initialization details
            this.log('KSG Estimator: k=3 nearest neighbors', 'info');
            this.log('Window Size: 100 samples', 'info');
            this.log('Max Lag: 5 time steps', 'info');
            this.log('TE Computation: Audio → Visual systems', 'info');
            this.log('Information Flow: Directed causality analysis', 'info');
            
            this.updateStatus('transferEntropyCoupling', true);
            this.log('✨ Transfer Entropy Coupling initialized successfully', 'success');
            
        } catch (error) {
            this.log(`❌ Transfer Entropy Coupling initialization failed: ${error.message}`, 'error');
            this.updateStatus('transferEntropyCoupling', false);
            throw error;
        }
    }
    
    updateVisualsFromAudio(features) {
        // Map audio features to Grace Attractor with optimized responsiveness
        if (this.graceAttractor && features) {
            // Moderate Grace intensity from audio volume (RMS)
            const enhancedIntensity = features.graceIntensity * 1.5 + 0.3; // Reduced amplification
            this.graceAttractor.setIntensity(enhancedIntensity);
            
            // Gentle scaling based on spectral content - reduced to prevent constant regeneration
            const scaleMultiplier = 1.0 + features.sovereigntyComplexity * 0.3 + features.systemEnergy * 0.2;
            this.graceAttractor.setScale(scaleMultiplier);
        }
        
        // Map audio features to Sovereignty Attractor with optimized dynamics
        if (this.sovereigntyAttractor && features) {
            // Moderate sovereignty intensity
            const enhancedSovereignty = features.sovereigntyComplexity * 1.5 + 0.4;
            this.sovereigntyAttractor.setIntensity(enhancedSovereignty);
            
            // Reduced recursive depth changes to prevent constant regeneration
            const audioComplexity = features.raw.spectralCentroid / 4000; // Normalize
            const energyBoost = features.systemEnergy * 0.5; // Reduced energy component
            const newDepth = Math.floor(6 + (audioComplexity + energyBoost) * 2); // 6-10 range, less variation
            this.sovereigntyAttractor.setRecursiveDepth(Math.min(10, Math.max(6, newDepth)));
        }
        
        // Map audio features to Bireflection Attractor with dramatic effects
        if (this.bireflectionAttractor && features) {
            // Enhanced bireflection intensity with amplification
            const enhancedBireflection = features.bireflectionSymmetry * 4.0 + 0.4;
            this.bireflectionAttractor.setIntensity(enhancedBireflection);
            
            // Dynamic mirror strength with more variation
            const mirrorStrength = 0.3 + features.bireflectionSymmetry * 1.4 + features.systemEnergy * 0.8;
            this.bireflectionAttractor.setMirrorStrength(Math.min(2.0, mirrorStrength));
            
            // Dynamic duality balance with audio-driven oscillation
            const audioOscillation = Math.sin(Date.now() * 0.001 * features.systemEnergy * 5) * 0.3;
            const dualityBalance = 0.5 + audioOscillation + features.systemEnergy * 0.3;
            this.bireflectionAttractor.setDualityBalance(Math.max(0.1, Math.min(0.9, dualityBalance)));
        }
        
        // Map audio features to Bootstrap Attractor with ex nihilo generation
        if (this.bootstrapAttractor && features) {
            // Bootstrap responds to system energy and complexity for creation
            const creationPotential = features.systemEnergy * 2.0 + features.sovereigntyComplexity * 1.5;
            this.bootstrapAttractor.setIntensity(creationPotential);
            
            // Adjust emergence threshold based on audio activity
            const emergenceThreshold = 0.3 - features.systemEnergy * 0.2; // More active = easier emergence
            this.bootstrapAttractor.setEmergenceThreshold(Math.max(0.1, emergenceThreshold));
            
            // Complexity growth rate based on spectral richness
            const complexityGrowth = 1.2 + features.sovereigntyComplexity * 0.5;
            this.bootstrapAttractor.setComplexityGrowth(Math.min(2.0, complexityGrowth));
        }
        
        // Map audio features to Hebrew Letters Network with enhanced dynamics
        if (this.hebrewNetwork && features) {
            // Set Hebrew letter activations from audio features
            this.hebrewNetwork.setAudioFeatures(features);
            
            // Enhanced network intensity with dramatic response
            const networkIntensity = 0.2 + features.systemEnergy * 1.5 + features.graceIntensity * 0.8;
            this.hebrewNetwork.setIntensity(Math.min(2.0, networkIntensity));
        }
        
        // Map audio features to 231-Gates Network with cascading effects
        if (this.gates231Network && features) {
            // Gate activations respond to Hebrew letter activations
            this.gates231Network.updateGateActivations(features);
            
            // Enhanced gate intensity with multiple audio features
            const gateIntensity = 0.1 + features.sovereigntyComplexity * 1.2 + 
                                features.bireflectionSymmetry * 0.8 + 
                                features.systemEnergy * 1.0;
            this.gates231Network.setIntensity(Math.min(2.5, gateIntensity));
        }
        
        // Update Transfer Entropy Coupling
        if (this.transferEntropyProcessor && features) {
            // Update audio features for TE computation
            this.transferEntropyProcessor.updateAudioFeatures(features);
            
            // Collect visual states for TE computation
            const visualStates = this.collectVisualStates();
            this.transferEntropyProcessor.updateVisualStates(visualStates);
            
            // Get TE results and apply advanced coupling
            this.teResults = this.transferEntropyProcessor.getTransferEntropies();
            this.applyTransferEntropyCoupling(this.teResults);
        }
        
        // Update UI with audio info, Bootstrap metrics, and TE results
        this.updateAudioUI(features);
        this.updateBootstrapUI();
        this.updateTransferEntropyUI(this.teResults);
    }
    
    updateAudioUI(features) {
        if (!features) return;
        
        // Update microphone status
        const micStatus = document.getElementById('mic-status');
        if (micStatus) {
            micStatus.textContent = this.audioProcessor?.isAnalyzing ? 'Active' : 'Inactive';
            micStatus.style.color = this.audioProcessor?.isAnalyzing ? '#00ff00' : '#ff0000';
        }
        
        // Update RMS (volume)
        const rmsElement = document.getElementById('audio-rms');
        if (rmsElement) {
            rmsElement.textContent = features.raw.rms.toFixed(3);
        }
        
        // Update Grace intensity
        const graceElement = document.getElementById('grace-intensity');
        if (graceElement) {
            graceElement.textContent = features.graceIntensity.toFixed(2);
        }
    }
    
    setupControls() {
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 100;
        
        this.log('🎮 Orbit controls enabled', 'info');
    }
    
    startRenderLoop() {
        this.updateStatus('rendering', true);
        this.log('🔄 Starting render loop...', 'info');
        this.animate();
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        const deltaTime = this.clock.getDelta();
        
        // Update controls
        if (this.controls) {
            this.controls.update();
        }
        
        // Update Cosmological Sequence Controller
        if (this.cosmologicalSequence) {
            this.cosmologicalSequence.update(deltaTime);
            this.updateCosmologicalUI();
            
            // Get current phase info
            const phaseInfo = this.cosmologicalSequence.getPhaseInfo();
            const currentPhase = phaseInfo.id;
            
            // Update attractors based on cosmological phase
            this.updateAttractorsForPhase(currentPhase, deltaTime, phaseInfo);
        }
        
        // Render
        this.renderer.render(this.scene, this.camera);
        
        // Update performance stats
        this.updatePerformanceStats();
    }
    
    updateAttractorsForPhase(currentPhase, deltaTime, phaseInfo) {
        // Phase 0: VOID - Show nothing but void state
        if (currentPhase === 0) {
            this.hideAllAttractors();
            return;
        }
        
        // Phase 1: BOOTSTRAP - Ex nihilo generation
        if (currentPhase >= 1 && this.bootstrapAttractor) {
            this.bootstrapAttractor.update(deltaTime, this.audioFeatures, currentPhase + phaseInfo.progress);
            this.showAttractor('bootstrap');
        }
        
        // Phase 2: GRACE - Golden ratio emergence
        if (currentPhase >= 2 && this.graceAttractor) {
            const intensity = this.cosmologicalSequence.getGraceIntensity();
            this.graceAttractor.update(deltaTime, this.audioFeatures, currentPhase + phaseInfo.progress);
            this.graceAttractor.setIntensity(intensity);
            this.showAttractor('grace');
            
            // Connect Grace to Bootstrap seed position
            if (this.bootstrapAttractor && this.graceAttractor.setBootstrapSeedPosition) {
                const bootstrapPosition = this.bootstrapAttractor.getObject3D().position;
                this.graceAttractor.setBootstrapSeedPosition(bootstrapPosition);
            }
        }
        
        // Phase 3: SOVEREIGNTY - Recursive self-awareness
        if (currentPhase >= 3 && this.sovereigntyAttractor) {
            const intensity = this.cosmologicalSequence.getSovereigntyIntensity();
            this.sovereigntyAttractor.update(deltaTime);
            this.sovereigntyAttractor.setIntensity(intensity);
            this.showAttractor('sovereignty');
            
            // Log sovereignty emergence
            if (intensity > 0.1 && intensity < 0.3) {
                this.log('🧠 Recursive self-awareness emerging...', 'info');
            } else if (intensity > 0.7 && intensity < 0.9) {
                this.log('👑 Sovereignty attractor approaching autonomy...', 'info');
            }
        }
        
        // Phase 4: BIREFLECTION - Observer/observed duality
        if (currentPhase >= 4 && this.bireflectionAttractor) {
            const intensity = this.cosmologicalSequence.getBireflectionIntensity();
            this.bireflectionAttractor.update(deltaTime);
            this.bireflectionAttractor.setIntensity(intensity);
            this.showAttractor('bireflection');
            
            // Log bireflection emergence
            if (intensity > 0.1 && intensity < 0.3) {
                this.log('🪞 Observer/observed duality emerging...', 'info');
            } else if (intensity > 0.5 && intensity < 0.7) {
                this.log('✨ Mirror symmetry β(β(z)) = z established', 'info');
            } else if (intensity >= 0.9) {
                this.log('🎭 Complete bireflection: Every point has mirror partner', 'info');
            }
        }
        
        // Phase 5: HEBREW NETWORK - Complete cosmic network
        if (currentPhase >= 5) {
            const intensity = this.cosmologicalSequence.getHebrewNetworkIntensity();
            
            if (this.hebrewNetwork) {
                this.hebrewNetwork.update(deltaTime, this.audioFeatures);
                this.hebrewNetwork.setIntensity(intensity);
                this.showAttractor('hebrew');
            }
            
            if (this.gates231Network) {
                this.gates231Network.update(deltaTime, this.audioFeatures);
                this.gates231Network.setIntensity(intensity);
                this.showAttractor('gates');
            }
            
            // Log Hebrew network activation
            if (intensity > 0.1 && intensity < 0.3) {
                this.log('🕎 Hebrew letter network activating...', 'info');
                this.log('22 letters beginning cosmic dance', 'info');
            } else if (intensity > 0.5 && intensity < 0.7) {
                this.log('🌐 231 Gates (C(22,2)) forming connections...', 'info');
            } else if (intensity >= 0.9) {
                this.log('✨ Complete cosmic network operational', 'success');
                this.log('🎯 FIRM Universe fully manifested!', 'success');
            }
        }
    }
    
    hideAllAttractors() {
        ['bootstrap', 'grace', 'sovereignty', 'bireflection', 'hebrew', 'gates'].forEach(name => {
            this.hideAttractor(name);
        });
    }
    
    showAttractor(name) {
        const attractor = this.getAttractorByName(name);
        if (attractor && attractor.object3D) {
            attractor.object3D.visible = true;
        } else if (attractor && attractor.getObject3D) {
            attractor.getObject3D().visible = true;
        }
    }
    
    hideAttractor(name) {
        const attractor = this.getAttractorByName(name);
        if (attractor && attractor.object3D) {
            attractor.object3D.visible = false;
        } else if (attractor && attractor.getObject3D) {
            attractor.getObject3D().visible = false;
        }
    }
    
    getAttractorByName(name) {
        switch (name) {
            case 'bootstrap': return this.bootstrapAttractor;
            case 'grace': return this.graceAttractor;
            case 'sovereignty': return this.sovereigntyAttractor;
            case 'bireflection': return this.bireflectionAttractor;
            case 'hebrew': return this.hebrewNetwork;
            case 'gates': return this.gates231Network;
            default: return null;
        }
    }
    
    updateCosmologicalUI() {
        try {
            const phaseInfo = this.cosmologicalSequence.getPhaseInfo();
            
            // Update phase display
            const currentPhaseEl = document.getElementById('current-phase');
            if (currentPhaseEl) {
                currentPhaseEl.textContent = `Phase ${phaseInfo.id}: ${phaseInfo.name} (${phaseInfo.symbol})`;
            }
            
            // Update description
            const descriptionEl = document.getElementById('phase-description');
            if (descriptionEl) {
                descriptionEl.textContent = phaseInfo.description;
            }
            
            // Update progress bar
            const progressEl = document.getElementById('phase-progress');
            if (progressEl) {
                progressEl.style.width = `${phaseInfo.progress * 100}%`;
            }
            
            // Update Hebrew letter
            const hebrewEl = document.getElementById('hebrew-letter');
            if (hebrewEl) {
                hebrewEl.textContent = phaseInfo.hebrewLetter || phaseInfo.symbol;
            }
            
            // Update info panel cosmology info
            const phaseNameEl = document.getElementById('current-phase-name');
            if (phaseNameEl) {
                phaseNameEl.textContent = `${phaseInfo.name} (${phaseInfo.symbol})`;
            }
            
            const progressPercentEl = document.getElementById('phase-progress-percent');
            if (progressPercentEl) {
                progressPercentEl.textContent = `${Math.round(phaseInfo.progress * 100)}%`;
            }
            
            const currentHebrewEl = document.getElementById('current-hebrew');
            if (currentHebrewEl) {
                currentHebrewEl.textContent = phaseInfo.hebrewLetter || phaseInfo.symbol;
            }
            
        } catch (error) {
            // Silently fail if UI elements not available
        }
    }
    
    updatePerformanceStats() {
        this.frameCount++;
        const currentTime = performance.now();
        
        if (currentTime >= this.lastTime + 1000) {
            this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
            this.frameCount = 0;
            this.lastTime = currentTime;
            
            // Update FPS display
            document.getElementById('fps').textContent = this.fps;
        }
    }
    
    updateObjectCount() {
        const objectCount = this.scene.children.length;
        document.getElementById('objects').textContent = objectCount;
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.log('📐 Window resized, camera and renderer updated', 'info');
    }
    
    collectVisualStates() {
        const states = {};
        
        if (this.graceAttractor) {
            const info = this.graceAttractor.getInfo();
            states.grace = {
                intensity: info.intensity || 1.0,
                scale: info.scale || 1.0,
                phi: info.phi || 1.618,
                hausdorffDimension: info.hausdorffDimension || 0.694,
                particleCount: info.particleCount || 5000
            };
        }
        
        if (this.sovereigntyAttractor) {
            const info = this.sovereigntyAttractor.getInfo();
            states.sovereignty = {
                intensity: info.intensity || 1.0,
                scale: info.scale || 1.0,
                recursiveDepth: info.recursiveDepth || 6,
                dimension: info.dimension || 2.258,
                selfReference: info.selfReference || 0.618,
                autonomy: info.autonomy || 1.0
            };
        }
        
        if (this.bireflectionAttractor) {
            const info = this.bireflectionAttractor.getInfo();
            const symmetry = this.bireflectionAttractor.getSymmetryAnalysis();
            states.bireflection = {
                intensity: info.intensity || 1.0,
                scale: info.scale || 1.0,
                mirrorPairs: info.mirrorPairs || 2000,
                symmetryRatio: symmetry.symmetryRatio || 0.996,
                mirrorStrength: info.mirrorStrength || 1.0,
                dualityBalance: info.dualityBalance || 0.5
            };
        }
        
        if (this.hebrewNetwork) {
            const info = this.hebrewNetwork.getInfo();
            states.hebrew = {
                intensity: 1.0,
                scale: 1.0,
                letterCount: info.letterCount || 22,
                connectionCount: info.connectionCount || 22,
                activations: {}
            };
        }
        
        if (this.gates231Network) {
            const info = this.gates231Network.getInfo();
            states.gates = {
                intensity: 1.0,
                scale: 1.0,
                totalGates: info.totalGates || 231,
                activeGates: info.activeGates || 50,
                motifTypes: info.motifTypes || 12
            };
        }
        
        if (this.bootstrapAttractor) {
            const metrics = this.bootstrapAttractor.getBootstrapMetrics();
            states.bootstrap = {
                intensity: metrics.complexity || 0.1,
                manifestationSteps: metrics.manifestationSteps || 0,
                currentDimension: metrics.currentDimension || 0.0,
                creationEnergy: metrics.creationEnergy || 0.0,
                structureCount: metrics.structureCount || 0,
                emergenceThreshold: metrics.emergenceThreshold || 0.3
            };
        }
        
        return states;
    }
    
    applyTransferEntropyCoupling(teResults) {
        if (!teResults) return;
        
        const te = teResults;
        const flow = teResults.informationFlow;
        
        // Enhanced TE-driven coupling with more visible effects
        
        // Grace Attractor - responds to total information flow
        if (this.graceAttractor && flow.totalFlow > 0.1) {
            const flowIntensity = Math.min(flow.totalFlow * 1.5, 2.0);
            this.graceAttractor.setIntensity(0.5 + flowIntensity * 0.8);
            // Scale based on flow strength
            const scaleMultiplier = 1.0 + flow.flowStrength * 0.3;
            this.graceAttractor.setScale(scaleMultiplier);
        }
        
        // Sovereignty - responds to audio-to-grace coupling
        if (this.sovereigntyAttractor && te.audioToGrace > 0.05) {
            const teStrength = Math.min(te.audioToGrace * 3, 2.0);
            this.sovereigntyAttractor.setIntensity(0.5 + teStrength * 0.7);
            // Dynamic recursive depth based on TE
            const newDepth = 6 + Math.floor(teStrength * 3);
            if (newDepth !== this.sovereigntyAttractor.recursiveDepth) {
                this.sovereigntyAttractor.setRecursiveDepth(newDepth);
            }
        }
        
        // Bireflection - enhanced mirror response
        if (this.bireflectionAttractor) {
            const teStrength = Math.max(te.sovereigntyToBireflection, te.audioToBireflection) * 2;
            this.bireflectionAttractor.setMirrorStrength(1.0 + teStrength * 1.0);
            this.bireflectionAttractor.setIntensity(0.3 + teStrength * 1.2);
            
            // Dynamic duality balance based on causality
            const dualityBalance = 0.5 + flow.causalityIndex * 0.4;
            this.bireflectionAttractor.setDualityBalance(dualityBalance);
        }
        
        // Hebrew Network - cascading activation
        if (this.hebrewNetwork) {
            const teStrength = Math.max(te.bireflectionToHebrew, te.audioToHebrew) * 2;
            this.hebrewNetwork.setIntensity(0.3 + teStrength * 1.5);
        }
        
        // Gates Network - final cascade effect
        if (this.gates231Network) {
            const teStrength = Math.max(te.hebrewToGates, te.audioToGates) * 2;
            this.gates231Network.setIntensity(0.2 + teStrength * 1.8);
        }
        
        // Global flow effects based on dominant direction
        if (flow.dominantDirection === 'audio-driven' && flow.flowStrength > 0.3) {
            // Enhance all systems when audio strongly drives
            const globalBoost = Math.min(flow.flowStrength * 1.5, 1.0);
            
            // Apply global intensity boost to all systems
            if (this.graceAttractor) {
                const currentIntensity = this.graceAttractor.intensity || 1.0;
                this.graceAttractor.setIntensity(currentIntensity * (1 + globalBoost * 0.3));
            }
            
            if (this.sovereigntyAttractor) {
                const currentIntensity = this.sovereigntyAttractor.intensity || 1.0;
                this.sovereigntyAttractor.setIntensity(currentIntensity * (1 + globalBoost * 0.3));
            }
        }
    }
    
    updateBootstrapUI() {
        if (!this.bootstrapAttractor) return;
        
        const metrics = this.bootstrapAttractor.getBootstrapMetrics();
        
        // Update Bootstrap metrics display
        const manifestationEl = document.getElementById('manifestation-steps');
        const dimensionEl = document.getElementById('bootstrap-dimension');
        const phaseEl = document.getElementById('bootstrap-phase');
        const creationEnergyEl = document.getElementById('creation-energy');
        const structureCountEl = document.getElementById('structure-count');
        
        if (manifestationEl) {
            manifestationEl.textContent = `${metrics.manifestationSteps}/10`;
        }
        
        if (dimensionEl) {
            dimensionEl.textContent = metrics.currentDimension.toFixed(3);
        }
        
        if (phaseEl) {
            phaseEl.textContent = metrics.phaseDescription;
        }
        
        if (creationEnergyEl) {
            creationEnergyEl.textContent = metrics.creationEnergy.toFixed(3);
        }
        
        if (structureCountEl) {
            structureCountEl.textContent = metrics.structureCount;
        }
    }

    updateTransferEntropyUI(teResults) {
        if (!teResults) return;
        
        // Update TE flow indicators
        const totalFlowEl = document.getElementById('total-flow');
        const dominantDirectionEl = document.getElementById('dominant-direction');
        const causalityIndexEl = document.getElementById('causality-index');
        
        if (totalFlowEl) {
            totalFlowEl.textContent = teResults.informationFlow.totalFlow.toFixed(3);
        }
        
        if (dominantDirectionEl) {
            dominantDirectionEl.textContent = teResults.informationFlow.dominantDirection;
        }
        
        if (causalityIndexEl) {
            causalityIndexEl.textContent = teResults.informationFlow.causalityIndex.toFixed(3);
        }
    }
    
    setupRenderingControls() {
        this.log('🎨 Setting up rendering controls...', 'info');
        
        // Set initial background
        this.updateBackgroundColor();
        
        // Particle Size Control
        const particleSizeSlider = document.getElementById('particle-size');
        const particleSizeValue = document.getElementById('particle-size-value');
        if (particleSizeSlider) {
            particleSizeSlider.addEventListener('input', (e) => {
                this.renderingSettings.particleSize = parseFloat(e.target.value);
                particleSizeValue.textContent = this.renderingSettings.particleSize.toFixed(1);
                this.updateRenderingSettings();
            });
        }
        
        // Opacity Control
        const opacitySlider = document.getElementById('opacity');
        const opacityValue = document.getElementById('opacity-value');
        if (opacitySlider) {
            opacitySlider.addEventListener('input', (e) => {
                this.renderingSettings.opacity = parseFloat(e.target.value);
                opacityValue.textContent = this.renderingSettings.opacity.toFixed(2);
                this.updateRenderingSettings();
            });
        }
        
        // Background Control
        const backgroundSlider = document.getElementById('background');
        const backgroundValue = document.getElementById('background-value');
        if (backgroundSlider) {
            backgroundSlider.addEventListener('input', (e) => {
                this.renderingSettings.background = parseFloat(e.target.value);
                backgroundValue.textContent = this.renderingSettings.background.toFixed(2);
                this.updateBackgroundColor();
            });
        }
        
        // System Separation Control
        const separationSlider = document.getElementById('system-separation');
        const separationValue = document.getElementById('separation-value');
        if (separationSlider) {
            separationSlider.addEventListener('input', (e) => {
                this.renderingSettings.systemSeparation = parseFloat(e.target.value);
                separationValue.textContent = this.renderingSettings.systemSeparation.toFixed(1);
                this.updateSystemSeparation();
            });
        }
        
        // System Visibility Toggles
        const toggles = ['grace', 'sovereignty', 'bireflection', 'bootstrap', 'hebrew', 'gates'];
        toggles.forEach(system => {
            const checkbox = document.getElementById(`show-${system}`);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.systemVisibility[system] = e.target.checked;
                    this.updateSystemVisibility();
                });
            }
        });
        
        this.log('✨ Rendering controls initialized', 'success');
    }
    
    updateRenderingSettings() {
        console.log('🎨 Updating rendering settings:', this.renderingSettings);
        
        // Grace Attractor
        if (this.graceAttractor && this.graceAttractor.material && this.graceAttractor.material.uniforms) {
            const uniforms = this.graceAttractor.material.uniforms;
            if (uniforms.size) uniforms.size.value = this.renderingSettings.particleSize;
            if (uniforms.opacity) uniforms.opacity.value = this.renderingSettings.opacity;
            if (uniforms.glowIntensity) uniforms.glowIntensity.value = this.renderingSettings.opacity;
        }
        
        // Sovereignty Attractor
        if (this.sovereigntyAttractor && this.sovereigntyAttractor.material && this.sovereigntyAttractor.material.uniforms) {
            const uniforms = this.sovereigntyAttractor.material.uniforms;
            if (uniforms.size) uniforms.size.value = this.renderingSettings.particleSize;
            if (uniforms.opacity) uniforms.opacity.value = this.renderingSettings.opacity;
            if (uniforms.glowIntensity) uniforms.glowIntensity.value = this.renderingSettings.opacity;
        }
        
        // Bireflection Attractor
        if (this.bireflectionAttractor && this.bireflectionAttractor.points && this.bireflectionAttractor.points.material) {
            this.bireflectionAttractor.points.material.size = this.renderingSettings.particleSize * 3;
            this.bireflectionAttractor.points.material.opacity = this.renderingSettings.opacity;
        }
        
        // Bootstrap Attractor structures
        if (this.bootstrapAttractor && this.bootstrapAttractor.emergentStructures) {
            this.bootstrapAttractor.emergentStructures.forEach(structure => {
                if (structure.material) {
                    structure.material.size = this.renderingSettings.particleSize * 1.5; // Smaller multiplier
                    structure.material.opacity = this.renderingSettings.opacity * 0.4; // Much lower opacity
                }
            });
        }
        
        // Bootstrap creation particles
        if (this.bootstrapAttractor && this.bootstrapAttractor.creationParticles && this.bootstrapAttractor.creationParticles.material) {
            this.bootstrapAttractor.creationParticles.material.size = this.renderingSettings.particleSize * 0.5;
            this.bootstrapAttractor.creationParticles.material.opacity = this.renderingSettings.opacity * 0.2;
        }
        
        // Hebrew Network
        if (this.hebrewNetwork && this.hebrewNetwork.letterPoints) {
            this.hebrewNetwork.letterPoints.forEach(points => {
                if (points && points.material) {
                    points.material.size = this.renderingSettings.particleSize * 4;
                    points.material.opacity = this.renderingSettings.opacity;
                }
            });
        }
        
        // Gates Network
        if (this.gates231Network && this.gates231Network.lines && this.gates231Network.lines.material) {
            this.gates231Network.lines.material.opacity = this.renderingSettings.opacity * 0.3;
        }
    }
    
    updateBackgroundColor() {
        if (this.renderer) {
            const bg = this.renderingSettings.background;
            this.renderer.setClearColor(new THREE.Color(bg, bg, bg * 1.2)); // Slightly blue tint
        }
    }
    
    updateSystemSeparation() {
        const sep = this.renderingSettings.systemSeparation;
        
        // Spread systems apart spatially for better visibility
        if (this.graceAttractor && this.graceAttractor.object3D) {
            this.graceAttractor.object3D.position.set(-2 * sep, 0, 0);
        }
        
        if (this.sovereigntyAttractor && this.sovereigntyAttractor.object3D) {
            this.sovereigntyAttractor.object3D.position.set(2 * sep, 0, 0);
        }
        
        if (this.bireflectionAttractor && this.bireflectionAttractor.object3D) {
            this.bireflectionAttractor.object3D.position.set(0, 2 * sep, 0);
        }
        
        if (this.bootstrapAttractor && this.bootstrapAttractor.object3D) {
            this.bootstrapAttractor.object3D.position.set(0, -2 * sep, 0);
        }
        
        if (this.hebrewNetwork && this.hebrewNetwork.object3D) {
            this.hebrewNetwork.object3D.position.set(-1 * sep, -1 * sep, 1 * sep);
        }
        
        if (this.gates231Network && this.gates231Network.object3D) {
            this.gates231Network.object3D.position.set(1 * sep, 1 * sep, -1 * sep);
        }
    }
    
    updateSystemVisibility() {
        // Toggle visibility of different systems
        if (this.graceAttractor && this.graceAttractor.object3D) {
            this.graceAttractor.object3D.visible = this.systemVisibility.grace;
        }
        
        if (this.sovereigntyAttractor && this.sovereigntyAttractor.object3D) {
            this.sovereigntyAttractor.object3D.visible = this.systemVisibility.sovereignty;
        }
        
        if (this.bireflectionAttractor && this.bireflectionAttractor.object3D) {
            this.bireflectionAttractor.object3D.visible = this.systemVisibility.bireflection;
        }
        
        if (this.bootstrapAttractor && this.bootstrapAttractor.object3D) {
            this.bootstrapAttractor.object3D.visible = this.systemVisibility.bootstrap;
        }
        
        if (this.hebrewNetwork && this.hebrewNetwork.object3D) {
            this.hebrewNetwork.object3D.visible = this.systemVisibility.hebrew;
        }
        
        if (this.gates231Network && this.gates231Network.object3D) {
            this.gates231Network.object3D.visible = this.systemVisibility.gates;
        }
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.renderer) {
            this.renderer.dispose();
        }
        this.log('🗑️ Visualization destroyed', 'info');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.firmViz = new FIRMVisualization();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.firmViz) {
        window.firmViz.destroy();
    }
});
