/**
 * Bootstrap Attractor (𝒳-type) - Ex Nihilo Generation
 * 
 * Mathematical Foundation:
 * Emergence map: 𝒳ₙ₊₁ = G(∅, 𝒳ₙ) where G generates from void
 * Attractor: Limit set of void-to-form transitions
 * Basin: All initial conditions in "pre-manifestation" space
 * 
 * Physical Interpretation: Big Bang/creation dynamics
 * Hebrew Correspondence: ב (Bet) - container/house
 */

import * as THREE from 'three';

export class BootstrapAttractor {
    constructor() {
        this.name = 'Bootstrap Attractor';
        this.type = '𝒳-type';
        this.hebrewLetter = 'ב'; // Bet - container/house
        
        // Bootstrap parameters
        this.voidState = new Set(); // Measure-zero initial set
        this.manifestationSteps = 0;
        this.maxManifestationSteps = 10;
        this.generationRate = 0.02; // Much lower rate of ex-nihilo generation
        this.complexityGrowth = 1.1; // Slower complexity growth
        
        // Dynamic properties
        this.intensity = 1.0;
        this.emergenceThreshold = 0.8; // Higher threshold for spontaneous generation
        this.voidProbability = 0.01; // Much lower probability of void-state generation
        this.creationEnergy = 0.0; // Energy available for creation
        
        // Visual components
        this.object3D = new THREE.Group();
        this.voidPoints = null; // Void state visualization
        this.emergentStructures = []; // Generated structures
        this.creationParticles = null; // Particles showing creation process
        
        // Bootstrap tracking
        this.generationHistory = [];
        this.totalCreated = 0;
        this.currentDimension = 0.0; // Starts at 0, grows with complexity
        
        this.log('🚀 Bootstrap Attractor initialized', 'info');
        this.log('Ex nihilo generation: void → form transitions', 'info');
        this.log('Hebrew correspondence: ב (Bet) - container/house', 'info');
        
        this.generateBootstrapSystem();
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toISOString();
        const color = type === 'error' ? '#ff0000' : (type === 'warn' ? '#ffff00' : '#00ff88');
        console.log(`%c[Bootstrap] ${message}`, `color: ${color}`);
    }
    
    generateBootstrapSystem() {
        this.log('🌌 Generating Bootstrap system from void state...', 'info');
        
        // Step 1: Create void state representation (measure-zero set)
        this.createVoidState();
        
        // Step 2: Initialize first emergence from void
        this.initiateFirstEmergence();
        
        // Step 3: Setup creation particle system
        this.setupCreationParticles();
        
        this.log(`✨ Bootstrap system generated with ${this.emergentStructures.length} initial structures`, 'success');
        this.log(`Current dimension: ${this.currentDimension.toFixed(3)}`, 'info');
        this.log(`Manifestation steps: ${this.manifestationSteps}/${this.maxManifestationSteps}`, 'info');
    }
    
    createVoidState() {
        // Create a minimal representation of void (measure-zero set)
        const voidGeometry = new THREE.BufferGeometry();
        const voidPositions = new Float32Array(30); // Very few points (10 points)
        
        // Void points are nearly at origin but with tiny perturbations
        for (let i = 0; i < 10; i++) {
            const idx = i * 3;
            // Extremely small random perturbations around origin
            voidPositions[idx] = (Math.random() - 0.5) * 0.001;
            voidPositions[idx + 1] = (Math.random() - 0.5) * 0.001;
            voidPositions[idx + 2] = (Math.random() - 0.5) * 0.001;
        }
        
        voidGeometry.setAttribute('position', new THREE.BufferAttribute(voidPositions, 3));
        
        const voidMaterial = new THREE.PointsMaterial({
            color: 0x000033,
            size: 0.001, // Nearly invisible
            opacity: 0.1,
            transparent: true,
            blending: THREE.AdditiveBlending
        });
        
        this.voidPoints = new THREE.Points(voidGeometry, voidMaterial);
        this.object3D.add(this.voidPoints);
        
        this.log('∅ Void state created (measure-zero set)', 'info');
    }
    
    initiateFirstEmergence() {
        // First bootstrap step: 𝒳₁ = G(∅, ∅)
        this.manifestationSteps = 1;
        this.currentDimension = 0.1; // Tiny initial dimension
        
        // Create first emergent structure from void
        const firstStructure = this.generateEmergentStructure(0.1, 50); // Small, simple
        this.emergentStructures.push(firstStructure);
        this.object3D.add(firstStructure);
        
        this.generationHistory.push({
            step: this.manifestationSteps,
            dimension: this.currentDimension,
            structureCount: this.emergentStructures.length,
            timestamp: Date.now()
        });
        
        this.log('● First emergence from void completed', 'success');
        this.log(`Dimension increased to: ${this.currentDimension.toFixed(3)}`, 'info');
    }
    
    generateEmergentStructure(complexity, particleCount) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        // Generate structure based on bootstrap dynamics
        // More complex structures have more organized patterns
        for (let i = 0; i < particleCount; i++) {
            const idx = i * 3;
            
            // Bootstrap pattern: spiral emergence with increasing complexity
            const t = i / particleCount * Math.PI * 2 * complexity * 5;
            const r = complexity * (1 + Math.sin(t * 3) * 0.3);
            
            positions[idx] = r * Math.cos(t) * (0.5 + complexity);
            positions[idx + 1] = r * Math.sin(t) * (0.5 + complexity);
            positions[idx + 2] = (i / particleCount - 0.5) * complexity * 2;
            
            // Color based on emergence complexity - much dimmer
            const hue = (complexity * 360 + t * 57.2958) % 360; // Convert radians to degrees
            const saturation = 0.5 + complexity * 0.2; // Reduced saturation
            const lightness = 0.2 + complexity * 0.2; // Much dimmer (was 0.4 + 0.4)
            
            const color = new THREE.Color().setHSL(hue / 360, saturation, lightness);
            colors[idx] = color.r;
            colors[idx + 1] = color.g;
            colors[idx + 2] = color.b;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({
            size: 0.01 + complexity * 0.02, // Smaller particles
            vertexColors: true,
            opacity: 0.3 + complexity * 0.2, // Much lower opacity (was 0.6 + 0.4)
            transparent: true,
            blending: THREE.NormalBlending // Changed from AdditiveBlending to prevent white wash
        });
        
        const structure = new THREE.Points(geometry, material);
        structure.userData = {
            complexity: complexity,
            creationTime: Date.now(),
            emergenceStep: this.manifestationSteps
        };
        
        return structure;
    }
    
    setupCreationParticles() {
        // Particles that show the creation process in action
        const particleCount = 200;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const velocities = new Float32Array(particleCount * 3);
        const lifetimes = new Float32Array(particleCount);
        
        for (let i = 0; i < particleCount; i++) {
            const idx = i * 3;
            // Start near void state
            positions[idx] = (Math.random() - 0.5) * 0.01;
            positions[idx + 1] = (Math.random() - 0.5) * 0.01;
            positions[idx + 2] = (Math.random() - 0.5) * 0.01;
            
            // Random velocities for emergence
            velocities[idx] = (Math.random() - 0.5) * 0.02;
            velocities[idx + 1] = (Math.random() - 0.5) * 0.02;
            velocities[idx + 2] = (Math.random() - 0.5) * 0.02;
            
            lifetimes[i] = Math.random();
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
        geometry.setAttribute('lifetime', new THREE.BufferAttribute(lifetimes, 1));
        
        const material = new THREE.PointsMaterial({
            color: 0x004422, // Much darker green
            size: 0.005, // Smaller
            opacity: 0.3, // Much lower opacity
            transparent: true,
            blending: THREE.NormalBlending // Changed from AdditiveBlending
        });
        
        this.creationParticles = new THREE.Points(geometry, material);
        this.object3D.add(this.creationParticles);
        
        this.log('✨ Creation particle system initialized', 'info');
    }
    
    update(deltaTime, audioFeatures = null) {
        // Update creation energy from audio or autonomous generation
        if (audioFeatures) {
            this.creationEnergy += audioFeatures.systemEnergy * deltaTime * 0.5;
        } else {
            // Autonomous energy accumulation
            this.creationEnergy += deltaTime * 0.1;
        }
        
        // Spontaneous generation check
        if (this.creationEnergy > this.emergenceThreshold && 
            this.manifestationSteps < this.maxManifestationSteps &&
            Math.random() < this.voidProbability) {
            
            this.performBootstrapStep();
        }
        
        // Update creation particles
        this.updateCreationParticles(deltaTime);
        
        // Update existing emergent structures
        this.updateEmergentStructures(deltaTime);
        
        // Decay creation energy
        this.creationEnergy *= Math.exp(-deltaTime * 0.5);
    }
    
    performBootstrapStep() {
        this.log('🌟 Performing bootstrap step: void → form transition', 'info');
        
        // Bootstrap iteration: 𝒳ₙ₊₁ = G(∅, 𝒳ₙ)
        this.manifestationSteps++;
        
        // EMERGENT COMPLEXITY: Instead of just adding particles, 
        // reorganize existing structures into more complex patterns
        const oldDimension = this.currentDimension;
        this.currentDimension = Math.min(3.0, 
            this.currentDimension * this.complexityGrowth + 0.1);
        
        // Phase transition check: qualitative change in organization
        const phaseThreshold = Math.floor(this.currentDimension);
        if (phaseThreshold > Math.floor(oldDimension)) {
            this.performPhaseTransition(phaseThreshold);
        }
        
        // Self-organize existing structures instead of creating new ones
        this.selfOrganizeStructures();
        
        // Only create new structure if we have very few (max 3 total)
        if (this.emergentStructures.length < 3) {
            const complexity = this.currentDimension / 3.0;
            const particleCount = Math.floor(30 + complexity * 50); // Fixed small count
            const newStructure = this.generateEmergentStructure(complexity, particleCount);
            this.emergentStructures.push(newStructure);
            this.object3D.add(newStructure);
            this.totalCreated++;
        }
        
        // Consume creation energy
        this.creationEnergy -= this.emergenceThreshold;
        
        // Record generation event
        this.generationHistory.push({
            step: this.manifestationSteps,
            dimension: this.currentDimension,
            structureCount: this.emergentStructures.length,
            timestamp: Date.now(),
            phase: Math.floor(this.currentDimension)
        });
        
        this.log(`● Step ${this.manifestationSteps}: Complexity increased`, 'success');
        this.log(`Dimension: ${oldDimension.toFixed(3)} → ${this.currentDimension.toFixed(3)}`, 'info');
        this.log(`Phase: ${Math.floor(this.currentDimension)} (${this.getPhaseDescription()})`, 'info');
    }
    
    updateCreationParticles(deltaTime) {
        if (!this.creationParticles) return;
        
        const positions = this.creationParticles.geometry.attributes.position.array;
        const velocities = this.creationParticles.geometry.attributes.velocity.array;
        const lifetimes = this.creationParticles.geometry.attributes.lifetime.array;
        
        for (let i = 0; i < positions.length / 3; i++) {
            const idx = i * 3;
            
            // Update positions
            positions[idx] += velocities[idx] * deltaTime;
            positions[idx + 1] += velocities[idx + 1] * deltaTime;
            positions[idx + 2] += velocities[idx + 2] * deltaTime;
            
            // Update lifetimes
            lifetimes[i] -= deltaTime * 0.5;
            
            // Reset particles that have died
            if (lifetimes[i] <= 0) {
                // Respawn near void state
                positions[idx] = (Math.random() - 0.5) * 0.01;
                positions[idx + 1] = (Math.random() - 0.5) * 0.01;
                positions[idx + 2] = (Math.random() - 0.5) * 0.01;
                
                velocities[idx] = (Math.random() - 0.5) * 0.02;
                velocities[idx + 1] = (Math.random() - 0.5) * 0.02;
                velocities[idx + 2] = (Math.random() - 0.5) * 0.02;
                
                lifetimes[i] = 1.0;
            }
        }
        
        this.creationParticles.geometry.attributes.position.needsUpdate = true;
        this.creationParticles.geometry.attributes.lifetime.needsUpdate = true;
    }
    
    updateEmergentStructures(deltaTime) {
        // Rotate and evolve emergent structures
        this.emergentStructures.forEach((structure, index) => {
            const complexity = structure.userData.complexity;
            const age = (Date.now() - structure.userData.creationTime) / 1000;
            
            // Rotate based on complexity and age
            structure.rotation.y += deltaTime * complexity * 0.5;
            structure.rotation.x += deltaTime * complexity * 0.3;
            
            // Scale oscillation based on age
            const scaleOscillation = 1 + Math.sin(age * 2) * 0.1 * complexity;
            structure.scale.setScalar(scaleOscillation);
        });
    }
    
    // Control methods
    setIntensity(value) {
        this.intensity = Math.max(0.1, Math.min(3.0, value));
        this.generationRate = this.intensity * 0.1;
        this.voidProbability = this.intensity * 0.05;
        
        // Update material properties
        this.emergentStructures.forEach(structure => {
            if (structure.material) {
                structure.material.opacity = 0.4 + this.intensity * 0.4;
                structure.material.size = 0.02 + this.intensity * 0.03;
            }
        });
    }
    
    setEmergenceThreshold(value) {
        this.emergenceThreshold = Math.max(0.1, Math.min(1.0, value));
    }
    
    setComplexityGrowth(value) {
        this.complexityGrowth = Math.max(1.1, Math.min(2.0, value));
    }
    
    // Bootstrap-specific methods
    triggerManualEmergence() {
        if (this.manifestationSteps < this.maxManifestationSteps) {
            this.creationEnergy = this.emergenceThreshold + 0.1;
            this.log('⚡ Manual emergence triggered', 'info');
        }
    }
    
    resetToVoidState() {
        this.log('🔄 Resetting to void state...', 'warn');
        
        // Remove all emergent structures
        this.emergentStructures.forEach(structure => {
            this.object3D.remove(structure);
        });
        this.emergentStructures = [];
        
        // Reset parameters
        this.manifestationSteps = 0;
        this.currentDimension = 0.0;
        this.creationEnergy = 0.0;
        this.totalCreated = 0;
        this.generationHistory = [];
        
        // Reinitialize first emergence
        this.initiateFirstEmergence();
        
        this.log('∅ Reset to void state complete', 'success');
    }
    
    performPhaseTransition(phase) {
        this.log(`🌟 PHASE TRANSITION: Entering phase ${phase}`, 'success');
        
        // Qualitative reorganization of existing structures
        this.emergentStructures.forEach((structure, index) => {
            if (!structure.geometry) return;
            
            const positions = structure.geometry.attributes.position.array;
            const colors = structure.geometry.attributes.color.array;
            
            // Apply phase-specific transformation
            for (let i = 0; i < positions.length; i += 3) {
                switch(phase) {
                    case 1: // Linear organization
                        positions[i] = positions[i] + (index - 1) * 0.5; // Separate structures
                        break;
                    case 2: // Circular organization  
                        const angle = (i / positions.length) * Math.PI * 2;
                        const r = 0.5 + index * 0.3;
                        positions[i] = r * Math.cos(angle);
                        positions[i + 1] = r * Math.sin(angle);
                        break;
                    case 3: // Spiral organization
                        const t = (i / positions.length) * Math.PI * 4;
                        const spiral_r = 0.1 + t * 0.1;
                        positions[i] = spiral_r * Math.cos(t);
                        positions[i + 1] = spiral_r * Math.sin(t);
                        positions[i + 2] = t * 0.1;
                        break;
                }
                
                // Update colors to reflect phase
                const hue = (phase * 60) % 360; // Different color per phase
                const color = new THREE.Color().setHSL(hue / 360, 0.6, 0.3);
                colors[i] = color.r;
                colors[i + 1] = color.g;
                colors[i + 2] = color.b;
            }
            
            structure.geometry.attributes.position.needsUpdate = true;
            structure.geometry.attributes.color.needsUpdate = true;
        });
    }
    
    selfOrganizeStructures() {
        // Self-organization: local interactions create global patterns
        if (this.emergentStructures.length < 2) return;
        
        // Interact structures based on proximity and complexity
        for (let i = 0; i < this.emergentStructures.length; i++) {
            for (let j = i + 1; j < this.emergentStructures.length; j++) {
                const struct1 = this.emergentStructures[i];
                const struct2 = this.emergentStructures[j];
                
                if (!struct1.geometry || !struct2.geometry) continue;
                
                // Calculate interaction strength based on "complexity resonance"
                const complexity1 = struct1.userData?.complexity || 0.5;
                const complexity2 = struct2.userData?.complexity || 0.5;
                const resonance = 1.0 - Math.abs(complexity1 - complexity2);
                
                if (resonance > 0.7) { // Strong resonance
                    this.createComplexityBridge(struct1, struct2, resonance);
                }
            }
        }
    }
    
    createComplexityBridge(struct1, struct2, strength) {
        // Create emergent connection between resonant structures
        const pos1 = struct1.position;
        const pos2 = struct2.position;
        
        // Simple bridge geometry
        const bridgeGeometry = new THREE.BufferGeometry();
        const bridgePositions = new Float32Array([
            pos1.x, pos1.y, pos1.z,
            pos2.x, pos2.y, pos2.z
        ]);
        bridgeGeometry.setAttribute('position', new THREE.BufferAttribute(bridgePositions, 3));
        
        const bridgeMaterial = new THREE.LineBasicMaterial({
            color: new THREE.Color().setHSL(0.15, 0.8, 0.4), // Golden connection
            opacity: strength * 0.3,
            transparent: true
        });
        
        const bridge = new THREE.Line(bridgeGeometry, bridgeMaterial);
        bridge.userData = { type: 'complexity_bridge', strength: strength };
        
        this.object3D.add(bridge);
        
        this.log(`🔗 Complexity bridge formed (strength: ${strength.toFixed(2)})`, 'info');
    }
    
    getPhaseDescription() {
        const phase = Math.floor(this.currentDimension);
        switch(phase) {
            case 0: return 'Void State';
            case 1: return 'Linear Emergence';
            case 2: return 'Circular Organization';
            case 3: return 'Spiral Complexity';
            default: return 'Transcendent Form';
        }
    }
    
    // Analysis methods
    getBootstrapMetrics() {
        return {
            manifestationSteps: this.manifestationSteps,
            currentDimension: this.currentDimension,
            totalCreated: this.totalCreated,
            creationEnergy: this.creationEnergy,
            emergenceThreshold: this.emergenceThreshold,
            structureCount: this.emergentStructures.length,
            generationRate: this.generationRate,
            voidProbability: this.voidProbability,
            complexity: this.currentDimension / 3.0,
            phase: Math.floor(this.currentDimension),
            phaseDescription: this.getPhaseDescription(),
            generationHistory: this.generationHistory.slice(-5) // Last 5 events
        };
    }
    
    getObject3D() {
        return this.object3D;
    }
}
