/**
 * CosmologicalGrace.js - Grace Attractor in Cosmological Context
 * 
 * Implements Grace Attractor (𝒢-type) that emerges from Bootstrap seed:
 * Bootstrap creates initial structure → Grace transforms it via φ-scaling
 * 
 * Mathematical Foundation:
 * IFS: S₁(z) = z/φ + 0, S₂(z) = z/φ + 1/φ  
 * Emergence: 𝒢 : ∅ → Ψ (morphism from void to sovereignty)
 * Hebrew Correspondence: א (Aleph) - threshold of silence
 */

import * as THREE from 'three';

export class CosmologicalGrace {
    constructor() {
        this.name = 'Cosmological Grace';
        this.type = '𝒢-type';
        this.hebrewLetter = 'א'; // Aleph - threshold of silence
        
        // Golden ratio φ = (1+√5)/2 ≈ 1.618
        this.phi = (1 + Math.sqrt(5)) / 2;
        this.invPhi = 1 / this.phi; // 1/φ ≈ 0.618
        
        // Attractor properties
        this.hausdorffDim = Math.log(this.phi) / Math.log(2); // ≈ 0.694
        this.particleCount = 3000; // Fewer particles for cleaner emergence
        this.iterations = 15; // More iterations for better convergence
        
        // Cosmological emergence properties
        this.emergencePhase = 0.0; // 0.0 = not emerged, 1.0 = fully manifested
        this.bootstrapSeedPosition = new THREE.Vector3(0, 0, 0); // Where Bootstrap ended
        this.spiralRadius = 0.0; // Grows with emergence
        this.maxSpiralRadius = 2.0;
        
        // Visual system
        this.object3D = new THREE.Group();
        this.graceSpiralPoints = null;
        this.emergenceParticles = null;
        this.connectionLines = null; // Lines connecting to Bootstrap seed
        
        // Emergence tracking
        this.emergenceHistory = [];
        this.lastEmergenceTime = 0;
        this.emergenceRate = 0.3; // Rate of φ-spiral growth
        
        this.log('✨ Cosmological Grace initialized', 'info');
        this.log('Awaiting emergence from Bootstrap seed...', 'info');
        this.log('Hebrew correspondence: א (Aleph) - threshold of silence', 'info');
        
        this.initializeGraceSystem();
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[Grace] ${message}`);
        
        // Try to log to UI if available
        try {
            const logContent = document.getElementById('log-content');
            if (logContent) {
                const logEntry = document.createElement('div');
                const colorMap = {
                    info: '#ffd700',
                    warning: '#ffff00',
                    error: '#ff0000',
                    success: '#00ffff',
                    emergence: '#ff69b4'
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
    
    initializeGraceSystem() {
        // Create initial seed point (dormant until Bootstrap completes)
        this.createSeedPoint();
        
        // Prepare spiral geometry (initially empty)
        this.createSpiralGeometry();
        
        // Create connection system to Bootstrap
        this.createBootstrapConnection();
        
        this.log('Grace system initialized in dormant state', 'info');
    }
    
    createSeedPoint() {
        const seedGeometry = new THREE.BufferGeometry();
        const seedPosition = new Float32Array([0, 0, 0]); // Single point at origin
        seedGeometry.setAttribute('position', new THREE.BufferAttribute(seedPosition, 3));
        
        const seedMaterial = new THREE.PointsMaterial({
            color: 0xffd700, // Golden
            size: 0.2,
            opacity: 0.1,
            transparent: true,
            blending: THREE.AdditiveBlending
        });
        
        this.graceSeed = new THREE.Points(seedGeometry, seedMaterial);
        this.object3D.add(this.graceSeed);
    }
    
    createSpiralGeometry() {
        this.spiralGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(this.particleCount * 3);
        const colors = new Float32Array(this.particleCount * 3);
        const sizes = new Float32Array(this.particleCount);
        
        // Initially all points at origin (will expand during emergence)
        for (let i = 0; i < this.particleCount; i++) {
            positions[i * 3] = 0;
            positions[i * 3 + 1] = 0;
            positions[i * 3 + 2] = 0;
            
            // Golden color gradient
            const intensity = i / this.particleCount;
            colors[i * 3] = 1.0; // Red
            colors[i * 3 + 1] = 0.618 * (1 + intensity); // Green (φ-scaled)
            colors[i * 3 + 2] = 0.0; // Blue
            
            sizes[i] = 0.1; // Start small
        }
        
        this.spiralGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.spiralGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        this.spiralGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        const spiralMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                phi: { value: this.phi },
                emergencePhase: { value: 0.0 },
                intensity: { value: 1.0 }
            },
            vertexShader: `
                attribute vec3 color;
                attribute float size;
                varying vec3 vColor;
                uniform float time;
                uniform float phi;
                uniform float emergencePhase;
                uniform float intensity;
                
                void main() {
                    vColor = color;
                    
                    vec3 pos = position;
                    
                    // φ-spiral emergence animation
                    float spiral = sin(time * phi + length(pos) * 10.0) * emergencePhase * 0.1;
                    pos += vec3(spiral, spiral * 0.618, spiral * 0.382);
                    
                    // Golden ratio pulsing
                    float pulse = sin(time * phi) * 0.1 + 1.0;
                    pos *= pulse;
                    
                    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    gl_PointSize = size * intensity * emergencePhase * (300.0 / -mvPosition.z);
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                
                void main() {
                    float r = length(gl_PointCoord - vec2(0.5));
                    if (r > 0.5) discard;
                    
                    float alpha = (1.0 - r * 2.0) * 0.8;
                    gl_FragColor = vec4(vColor, alpha);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            vertexColors: true
        });
        
        this.graceSpiralPoints = new THREE.Points(this.spiralGeometry, spiralMaterial);
        this.graceSpiralPoints.visible = false; // Hidden until emergence begins
        this.object3D.add(this.graceSpiralPoints);
    }
    
    createBootstrapConnection() {
        // Create connection lines that will show emergence from Bootstrap
        const connectionGeometry = new THREE.BufferGeometry();
        const connectionPositions = new Float32Array(6); // 2 points, 3 coords each
        
        // Line from Bootstrap seed to Grace center
        connectionPositions[0] = 0; // Bootstrap position (will be updated)
        connectionPositions[1] = 0;
        connectionPositions[2] = 0;
        connectionPositions[3] = 0; // Grace center
        connectionPositions[4] = 0;
        connectionPositions[5] = 0;
        
        connectionGeometry.setAttribute('position', new THREE.BufferAttribute(connectionPositions, 3));
        
        const connectionMaterial = new THREE.LineBasicMaterial({
            color: 0xffd700,
            opacity: 0.3,
            transparent: true,
            blending: THREE.AdditiveBlending
        });
        
        this.connectionLines = new THREE.Line(connectionGeometry, connectionMaterial);
        this.connectionLines.visible = false; // Hidden until emergence
        this.object3D.add(this.connectionLines);
    }
    
    update(deltaTime, audioFeatures, cosmologyPhase) {
        const currentTime = performance.now() / 1000.0;
        
        // Only activate during Grace phase (2) or later
        if (cosmologyPhase < 2) {
            this.showSeedOnly();
            return;
        }
        
        // Calculate emergence phase based on cosmology
        const gracePhaseProgress = cosmologyPhase >= 3 ? 1.0 : (cosmologyPhase - 2.0);
        this.emergencePhase = Math.min(1.0, this.emergencePhase + gracePhaseProgress * deltaTime * this.emergenceRate);
        
        // Update from audio if available
        if (audioFeatures && this.emergencePhase < 1.0) {
            this.emergencePhase += audioFeatures.energy * 0.05 * deltaTime;
            this.emergencePhase = Math.min(1.0, this.emergencePhase);
        }
        
        // Perform Grace emergence
        if (this.emergencePhase > 0.1) {
            this.performGraceEmergence();
        }
        
        // Update visual systems
        this.updateSpiralGeometry();
        this.updateShaderUniforms(currentTime);
        
        // Log emergence milestones
        if (this.emergencePhase > 0.3 && this.lastEmergenceTime < 0.3) {
            this.log('🌟 φ-spiral emergence beginning...', 'emergence');
        }
        if (this.emergencePhase > 0.7 && this.lastEmergenceTime < 0.7) {
            this.log('✨ Golden ratio structure manifesting...', 'emergence');
        }
        if (this.emergencePhase >= 1.0 && this.lastEmergenceTime < 1.0) {
            this.log('🎯 Grace Attractor fully manifested: D_H = 0.694', 'emergence');
        }
        
        this.lastEmergenceTime = this.emergencePhase;
    }
    
    showSeedOnly() {
        // Show only the seed point, hide spiral
        if (this.graceSeed) {
            this.graceSeed.visible = true;
            this.graceSeed.material.opacity = 0.1;
        }
        if (this.graceSpiralPoints) {
            this.graceSpiralPoints.visible = false;
        }
        if (this.connectionLines) {
            this.connectionLines.visible = false;
        }
    }
    
    performGraceEmergence() {
        // Show the emerging spiral
        if (this.graceSpiralPoints) {
            this.graceSpiralPoints.visible = true;
        }
        
        // Show connection to Bootstrap
        if (this.connectionLines) {
            this.connectionLines.visible = true;
            this.connectionLines.material.opacity = 0.3 * this.emergencePhase;
        }
        
        // Fade out seed as spiral emerges
        if (this.graceSeed) {
            this.graceSeed.material.opacity = Math.max(0.05, 0.3 * (1.0 - this.emergencePhase));
        }
    }
    
    updateSpiralGeometry() {
        if (!this.spiralGeometry) return;
        
        const positions = this.spiralGeometry.attributes.position.array;
        const sizes = this.spiralGeometry.attributes.size.array;
        
        // Generate φ-spiral points based on emergence phase
        for (let i = 0; i < this.particleCount; i++) {
            const progress = (i / this.particleCount) * this.emergencePhase;
            
            if (progress > 0) {
                // Apply IFS transformations for Grace attractor
                let x = 0, y = 0, z = 0;
                
                // Iterative Function System with φ scaling
                for (let iter = 0; iter < this.iterations; iter++) {
                    const choice = ((i + iter * 1000) % 1000) / 1000;
                    
                    if (choice < this.invPhi) {
                        // S₁(z) = z/φ
                        x *= this.invPhi;
                        y *= this.invPhi;
                        z *= this.invPhi;
                    } else {
                        // S₂(z) = z/φ + 1/φ
                        x = x * this.invPhi + this.invPhi;
                        y = y * this.invPhi + this.invPhi * Math.sin(iter * 0.618);
                        z = z * this.invPhi + this.invPhi * Math.cos(iter * 0.618);
                    }
                }
                
                // Add spiral component scaled by emergence
                const angle = i * 0.618 * Math.PI; // φ-scaled angle
                const radius = Math.pow(this.invPhi, i % 8) * progress;
                
                positions[i * 3] = (x + radius * Math.cos(angle)) * this.emergencePhase;
                positions[i * 3 + 1] = (y + radius * Math.sin(angle)) * this.emergencePhase;
                positions[i * 3 + 2] = z * this.emergencePhase;
                
                sizes[i] = (0.5 + progress * 2.0) * this.emergencePhase;
            } else {
                // Keep at origin until emergence reaches this particle
                positions[i * 3] = 0;
                positions[i * 3 + 1] = 0;
                positions[i * 3 + 2] = 0;
                sizes[i] = 0.1;
            }
        }
        
        this.spiralGeometry.attributes.position.needsUpdate = true;
        this.spiralGeometry.attributes.size.needsUpdate = true;
    }
    
    updateShaderUniforms(time) {
        if (this.graceSpiralPoints && this.graceSpiralPoints.material) {
            const material = this.graceSpiralPoints.material;
            material.uniforms.time.value = time;
            material.uniforms.emergencePhase.value = this.emergencePhase;
        }
    }
    
    setIntensity(value) {
        this.intensity = Math.max(0, Math.min(2, value));
        if (this.graceSpiralPoints && this.graceSpiralPoints.material) {
            this.graceSpiralPoints.material.uniforms.intensity.value = this.intensity;
        }
    }
    
    setBootstrapSeedPosition(position) {
        this.bootstrapSeedPosition.copy(position);
        
        // Update connection line
        if (this.connectionLines) {
            const positions = this.connectionLines.geometry.attributes.position.array;
            positions[0] = position.x;
            positions[1] = position.y;
            positions[2] = position.z;
            this.connectionLines.geometry.attributes.position.needsUpdate = true;
        }
    }
    
    getGraceMetrics() {
        return {
            emergencePhase: this.emergencePhase,
            phi: this.phi,
            hausdorffDimension: this.hausdorffDim,
            particleCount: this.particleCount,
            spiralRadius: this.spiralRadius,
            phase: this.emergencePhase < 0.3 ? 'Seed State' :
                   this.emergencePhase < 0.7 ? 'φ-Spiral Emergence' :
                   'Manifested Grace Attractor'
        };
    }
    
    getObject3D() {
        return this.object3D;
    }
    
    dispose() {
        if (this.spiralGeometry) this.spiralGeometry.dispose();
        if (this.graceSpiralPoints && this.graceSpiralPoints.material) {
            this.graceSpiralPoints.material.dispose();
        }
        this.log('Grace Attractor disposed', 'info');
    }
}
