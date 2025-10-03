/**
 * CosmologicalBootstrap.js - True Ex Nihilo Generation
 * 
 * Implements the FIRM Bootstrap attractor (𝒳-type) according to cosmological sequence:
 * ∅ (void) ──→ ● ──→ ●● ──→ ●●● ──→ 𝒳*
 * 
 * Mathematical Foundation:
 * Emergence map: 𝒳ₙ₊₁ = G(∅, 𝒳ₙ) where G generates from void
 * Genesis: Finite attractor from measure-zero initial set
 * Hebrew Correspondence: ב (Bet) - container/house
 */

import * as THREE from 'three';

export class CosmologicalBootstrap {
    constructor() {
        this.name = 'Cosmological Bootstrap';
        this.type = '𝒳-type';
        this.hebrewLetter = 'ב'; // Bet - container/house
        
        // Ex nihilo generation parameters
        this.voidState = true; // Start in pure void
        this.generationStep = 0; // Current step in ∅ → ● → ●● → ●●● sequence
        this.maxGenerationSteps = 10;
        this.currentDimension = 0.0; // Fractal dimension grows with complexity
        this.structureCount = 0; // Number of emergent structures
        
        // Creation dynamics
        this.creationEnergy = 0.0; // Energy available for ex nihilo creation
        this.emergenceThreshold = 0.5; // Threshold for spontaneous generation
        this.complexityGrowthRate = 0.1; // Rate of dimensional increase
        
        // Visual system
        this.object3D = new THREE.Group();
        this.voidVisualization = null;
        this.emergentStructures = [];
        this.creationField = null;
        
        // Generation tracking
        this.generationHistory = [];
        this.lastGenerationTime = 0;
        this.generationInterval = 2000; // ms between generation steps
        
        this.log('🚀 Cosmological Bootstrap initialized', 'info');
        this.log('Starting in pure void state (∅)', 'info');
        this.log('Hebrew correspondence: ב (Bet) - container/house', 'info');
        
        this.initializeVoidState();
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[Bootstrap] ${message}`);
        
        // Try to log to UI if available
        try {
            const logContent = document.getElementById('log-content');
            if (logContent) {
                const logEntry = document.createElement('div');
                const colorMap = {
                    info: '#00ff88',
                    warning: '#ffff00',
                    error: '#ff0000',
                    success: '#00ffff',
                    genesis: '#ff69b4'
                };
                logEntry.style.color = colorMap[type] || '#ffffff';
                logEntry.innerHTML = `[${timestamp}] ${message}`;
                logContent.appendChild(logEntry);
                logContent.scrollTop = logContent.scrollHeight;
            }
        } catch (e) {
            // Silently fail if UI not available
        }
    }
    
    initializeVoidState() {
        // Create pure void visualization - single point of potential
        const voidGeometry = new THREE.BufferGeometry();
        const voidPosition = new Float32Array([0, 0, 0]); // Single point at origin
        voidGeometry.setAttribute('position', new THREE.BufferAttribute(voidPosition, 3));
        
        const voidMaterial = new THREE.PointsMaterial({
            color: 0x000011,
            size: 0.1,
            opacity: 0.05,
            transparent: true,
            blending: THREE.AdditiveBlending
        });
        
        this.voidVisualization = new THREE.Points(voidGeometry, voidMaterial);
        this.object3D.add(this.voidVisualization);
        
        this.log('∅ Void state initialized - measure-zero set at origin', 'info');
    }
    
    update(deltaTime, audioFeatures, cosmologyPhase) {
        // Only activate during Bootstrap phase or later
        if (cosmologyPhase < 1) {
            this.showVoidOnly();
            return;
        }
        
        // Update creation energy from audio or cosmological phase
        const phaseIntensity = this.getPhaseIntensity(cosmologyPhase);
        this.creationEnergy = Math.min(1.0, this.creationEnergy + phaseIntensity * deltaTime);
        
        // Update audio influence if available
        if (audioFeatures) {
            this.creationEnergy += audioFeatures.energy * 0.1 * deltaTime;
            this.creationEnergy = Math.min(1.0, this.creationEnergy);
        }
        
        // Check if we should perform next generation step
        const currentTime = performance.now();
        if (currentTime - this.lastGenerationTime > this.generationInterval && 
            this.creationEnergy > this.emergenceThreshold &&
            this.generationStep < this.maxGenerationSteps) {
            
            this.performGenerationStep();
            this.lastGenerationTime = currentTime;
        }
        
        // Update existing structures
        this.updateEmergentStructures(deltaTime);
        
        // Update visual intensity
        this.updateVisualIntensity(phaseIntensity);
    }
    
    getPhaseIntensity(cosmologyPhase) {
        // Bootstrap phase is 1, so we want full intensity during phase 1
        if (cosmologyPhase < 1) return 0.0;
        if (cosmologyPhase >= 2) return 1.0; // Full intensity after Bootstrap phase
        return cosmologyPhase - 1.0; // 0.0 to 1.0 during Bootstrap phase
    }
    
    showVoidOnly() {
        // Hide all emergent structures, show only void
        this.object3D.children.forEach(child => {
            if (child !== this.voidVisualization) {
                child.visible = false;
            }
        });
        
        if (this.voidVisualization) {
            this.voidVisualization.visible = true;
            this.voidVisualization.material.opacity = 0.05;
        }
    }
    
    performGenerationStep() {
        this.generationStep++;
        this.structureCount = this.generationStep;
        this.currentDimension = Math.min(2.0, this.generationStep * 0.2); // Dimension grows
        
        this.log(`🌟 GENERATION STEP ${this.generationStep}: Creating structure ${this.structureCount}`, 'genesis');
        this.log(`📐 Dimension increased to: ${this.currentDimension.toFixed(3)}`, 'genesis');
        
        // Create new emergent structure
        const structure = this.createEmergentStructure(this.generationStep);
        this.emergentStructures.push(structure);
        this.object3D.add(structure);
        
        // Record generation event
        this.generationHistory.push({
            step: this.generationStep,
            time: performance.now(),
            dimension: this.currentDimension,
            structureCount: this.structureCount,
            creationEnergy: this.creationEnergy
        });
        
        // Consume creation energy
        this.creationEnergy = Math.max(0.0, this.creationEnergy - 0.3);
        
        // Special messages for key steps
        if (this.generationStep === 1) {
            this.log('● First emergence from void completed', 'genesis');
        } else if (this.generationStep === 3) {
            this.log('●●● Complexity threshold reached', 'genesis');
        } else if (this.generationStep === this.maxGenerationSteps) {
            this.log('𝒳* Bootstrap attractor fully manifested', 'genesis');
        }
    }
    
    createEmergentStructure(step) {
        const structureGroup = new THREE.Group();
        
        // Each step creates more complex structure
        const particleCount = Math.min(100, step * 10);
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);
        
        // Generate structure based on step number
        for (let i = 0; i < particleCount; i++) {
            const angle = (i / particleCount) * Math.PI * 2;
            const radius = step * 0.1 + Math.random() * 0.05;
            const height = (Math.random() - 0.5) * step * 0.1;
            
            // Position in expanding spiral
            positions[i * 3] = Math.cos(angle) * radius;
            positions[i * 3 + 1] = Math.sin(angle) * radius;
            positions[i * 3 + 2] = height;
            
            // Color based on creation energy (purple to gold transition)
            const intensity = Math.min(1.0, step / this.maxGenerationSteps);
            colors[i * 3] = 0.5 + intensity * 0.5; // Red
            colors[i * 3 + 1] = 0.2 + intensity * 0.4; // Green  
            colors[i * 3 + 2] = 0.8 - intensity * 0.3; // Blue
            
            // Size based on structure complexity
            sizes[i] = 0.5 + intensity * 2.0;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                intensity: { value: 1.0 },
                step: { value: step }
            },
            vertexShader: `
                attribute vec3 color;
                attribute float size;
                varying vec3 vColor;
                uniform float time;
                uniform float intensity;
                uniform float step;
                
                void main() {
                    vColor = color;
                    
                    vec3 pos = position;
                    
                    // Pulsing emergence animation
                    float pulse = sin(time * 2.0 + step) * 0.1 + 1.0;
                    pos *= pulse;
                    
                    // Growth animation
                    pos *= min(1.0, time / step);
                    
                    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    gl_PointSize = size * intensity * (300.0 / -mvPosition.z);
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                
                void main() {
                    float r = length(gl_PointCoord - vec2(0.5));
                    if (r > 0.5) discard;
                    
                    float alpha = 1.0 - r * 2.0;
                    gl_FragColor = vec4(vColor, alpha * 0.8);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            vertexColors: true
        });
        
        const points = new THREE.Points(geometry, material);
        structureGroup.add(points);
        
        // Position structure relative to previous ones
        structureGroup.position.set(
            (step - 1) * 0.5 - 2.0, // Spread structures horizontally
            0,
            0
        );
        
        return structureGroup;
    }
    
    updateEmergentStructures(deltaTime) {
        const currentTime = performance.now() / 1000.0;
        
        this.emergentStructures.forEach((structure, index) => {
            if (structure.children[0] && structure.children[0].material) {
                const material = structure.children[0].material;
                material.uniforms.time.value = currentTime;
                material.uniforms.intensity.value = Math.min(1.0, this.creationEnergy + 0.5);
            }
            
            // Gentle rotation to show 3D structure
            structure.rotation.y += deltaTime * 0.1;
        });
    }
    
    updateVisualIntensity(phaseIntensity) {
        // Update void visualization
        if (this.voidVisualization) {
            this.voidVisualization.material.opacity = Math.max(0.05, 0.2 * (1.0 - phaseIntensity));
            this.voidVisualization.visible = phaseIntensity < 0.9; // Hide void when fully emerged
        }
        
        // Show emergent structures based on phase
        this.emergentStructures.forEach((structure, index) => {
            structure.visible = index < this.generationStep && phaseIntensity > 0.1;
        });
    }
    
    getBootstrapMetrics() {
        return {
            generationStep: this.generationStep,
            maxSteps: this.maxGenerationSteps,
            currentDimension: this.currentDimension,
            structureCount: this.structureCount,
            creationEnergy: this.creationEnergy,
            voidState: this.voidState && this.generationStep === 0,
            phase: this.generationStep === 0 ? 'Void State' : 
                   this.generationStep < 3 ? 'Initial Emergence' :
                   this.generationStep < 7 ? 'Complexity Growth' :
                   'Attractor Manifestation'
        };
    }
    
    // Control methods
    reset() {
        this.generationStep = 0;
        this.structureCount = 0;
        this.currentDimension = 0.0;
        this.creationEnergy = 0.0;
        this.voidState = true;
        
        // Remove all emergent structures
        this.emergentStructures.forEach(structure => {
            this.object3D.remove(structure);
        });
        this.emergentStructures = [];
        
        this.generationHistory = [];
        this.lastGenerationTime = 0;
        
        this.log('🔄 Bootstrap reset to void state (∅)', 'warning');
    }
    
    forceGeneration() {
        if (this.generationStep < this.maxGenerationSteps) {
            this.creationEnergy = 1.0; // Force high energy
            this.performGenerationStep();
        }
    }
    
    getObject3D() {
        return this.object3D;
    }
}
