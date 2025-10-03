/**
 * Sovereignty Attractor (Ψ-type) Implementation
 * Based on FIRM Framework: Fractal_Attractor_Theory.md
 * 
 * Recursive map: Ψₙ₊₁ = Ψₙ ∘ Ψₙ (self-composition)
 * Fixed point equation: Ψ* = F(Ψ*, Ψ*)
 * Dimension: D₀ = 2 + δ where δ encodes recursive depth
 */

import * as THREE from 'three';

export class SovereigntyAttractor {
    constructor() {
        // Sovereignty parameters
        this.recursiveDepth = 6; // Number of self-composition iterations
        this.dimension = 2.0 + Math.log2(this.recursiveDepth) / 10; // D₀ = 2 + δ
        this.particleCount = 3000;
        
        // Recursive self-composition parameters
        this.selfReference = 0.618; // Self-referential strength
        this.autonomy = 1.0; // No external input required
        this.complexity = this.recursiveDepth; // Complexity measure
        
        // Visual parameters
        this.scale = 2.5;
        this.intensity = 1.0;
        this.time = 0;
        
        // Recursive state
        this.recursiveStates = [];
        this.currentIteration = 0;
        
        this.geometry = null;
        this.material = null;
        this.points = null;
        
        this.init();
    }
    
    init() {
        this.createGeometry();
        this.createMaterial();
        this.createPoints();
    }
    
    createGeometry() {
        this.geometry = new THREE.BufferGeometry();
        
        // Generate Sovereignty attractor points using recursive self-composition
        const positions = new Float32Array(this.particleCount * 3);
        const colors = new Float32Array(this.particleCount * 3);
        const sizes = new Float32Array(this.particleCount);
        
        for (let i = 0; i < this.particleCount; i++) {
            const point = this.generateSovereigntyPoint(i);
            
            // Position
            positions[i * 3] = point.x;
            positions[i * 3 + 1] = point.y;
            positions[i * 3 + 2] = point.z;
            
            // Color (recursive depth gradient)
            const depthIntensity = point.depth / this.recursiveDepth;
            colors[i * 3] = 0.8 + depthIntensity * 0.2; // Red
            colors[i * 3 + 1] = 0.2 + depthIntensity * 0.6; // Green (depth-scaled)
            colors[i * 3 + 2] = 1.0 - depthIntensity * 0.3; // Blue (inverse depth)
            
            // Size (varies with recursive complexity)
            sizes[i] = 1.0 + point.complexity * 1.5;
        }
        
        this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        console.log(`[Sovereignty] Generated ${this.particleCount} points with recursive depth ${this.recursiveDepth}`);
    }
    
    generateSovereigntyPoint(index) {
        // Start with initial condition
        let x = (index / this.particleCount - 0.5) * 2; // [-1, 1]
        let y = Math.sin(index * 0.1) * 0.5;
        let z = Math.cos(index * 0.1) * 0.5;
        
        // Apply recursive self-composition: Ψₙ₊₁ = Ψₙ ∘ Ψₙ
        let complexity = 0;
        for (let depth = 0; depth < this.recursiveDepth; depth++) {
            // Self-composition operation: F(Ψ, Ψ) -> Ψ'
            const newX = this.selfCompose(x, y, z, depth).x;
            const newY = this.selfCompose(x, y, z, depth).y;
            const newZ = this.selfCompose(x, y, z, depth).z;
            
            // Update position
            x = newX * this.selfReference + x * (1 - this.selfReference);
            y = newY * this.selfReference + y * (1 - this.selfReference);
            z = newZ * this.selfReference + z * (1 - this.selfReference);
            
            // Accumulate complexity
            complexity += Math.sqrt(x*x + y*y + z*z) * (depth + 1) / this.recursiveDepth;
        }
        
        // Apply sovereign scaling (no external input)
        const sovereignScale = Math.pow(this.autonomy, complexity / this.recursiveDepth);
        
        return {
            x: x * sovereignScale * this.scale,
            y: y * sovereignScale * this.scale,
            z: z * sovereignScale * this.scale,
            depth: this.recursiveDepth,
            complexity: complexity / this.recursiveDepth
        };
    }
    
    selfCompose(x, y, z, depth) {
        // Self-composition function: Ψ(Ψ(point))
        // This represents the core sovereignty operation
        
        // First application: Ψ(point)
        const r1 = Math.sqrt(x*x + y*y + z*z);
        const theta1 = Math.atan2(y, x) + depth * 0.1;
        const phi1 = Math.acos(z / (r1 + 0.001)) + depth * 0.05;
        
        const x1 = r1 * Math.cos(theta1) * Math.sin(phi1);
        const y1 = r1 * Math.sin(theta1) * Math.sin(phi1);
        const z1 = r1 * Math.cos(phi1);
        
        // Second application: Ψ(Ψ(point)) - self-composition
        const r2 = Math.sqrt(x1*x1 + y1*y1 + z1*z1);
        const theta2 = Math.atan2(y1, x1) * (1 + depth * 0.1);
        const phi2 = Math.acos(z1 / (r2 + 0.001)) * (1 + depth * 0.05);
        
        // Apply recursive contraction to ensure convergence
        const contraction = 0.7 + 0.2 * Math.cos(depth * Math.PI / this.recursiveDepth);
        
        return {
            x: r2 * Math.cos(theta2) * Math.sin(phi2) * contraction,
            y: r2 * Math.sin(theta2) * Math.sin(phi2) * contraction,
            z: r2 * Math.cos(phi2) * contraction
        };
    }
    
    createMaterial() {
        // Vertex shader with recursive self-composition
        const vertexShader = `
            attribute float size;
            attribute vec3 color;
            varying vec3 vColor;
            varying float vComplexity;
            
            uniform float time;
            uniform float recursiveDepth;
            uniform float intensity;
            
            void main() {
                vColor = color;
                
                // Recursive pulsing based on self-composition
                float recursivePulse = sin(time * recursiveDepth * 0.5) * 0.3 + 0.7;
                vComplexity = intensity * recursivePulse;
                
                // Position with recursive breathing (self-referential)
                vec3 pos = position;
                float selfRef = 1.0 + sin(time * 0.3) * 0.15;
                pos *= selfRef;
                
                vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                gl_PointSize = size * (120.0 / -mvPosition.z) * intensity; // Reduced from 400.0
                gl_Position = projectionMatrix * mvPosition;
            }
        `;
        
        // Fragment shader with sovereignty glow
        const fragmentShader = `
            varying vec3 vColor;
            varying float vComplexity;
            
            void main() {
                // Circular point with recursive glow
                vec2 center = gl_PointCoord - vec2(0.5);
                float dist = length(center);
                
                if (dist > 0.5) discard;
                
                // Sovereignty glow effect (self-referential)
                float alpha = (1.0 - dist * 2.0) * vComplexity;
                float glow = 1.0 - dist;
                vec3 finalColor = vColor * (0.6 + glow * 0.4) * (0.8 + vComplexity * 0.2);
                
                gl_FragColor = vec4(finalColor, alpha);
            }
        `;
        
        this.material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                recursiveDepth: { value: this.recursiveDepth },
                intensity: { value: this.intensity },
                size: { value: 2.0 },
                opacity: { value: 0.8 },
                glowIntensity: { value: 1.0 }
            },
            vertexShader,
            fragmentShader,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        
        console.log(`[Sovereignty] Material created with dimension: ${this.dimension.toFixed(3)}`);
    }
    
    createPoints() {
        this.points = new THREE.Points(this.geometry, this.material);
        this.points.name = 'SovereigntyAttractor';
    }
    
    update(deltaTime) {
        this.time += deltaTime;
        
        if (this.material) {
            this.material.uniforms.time.value = this.time;
            this.material.uniforms.intensity.value = this.intensity;
        }
        
        // Self-referential rotation (autonomous)
        if (this.points) {
            // Recursive rotation pattern
            this.points.rotation.x += deltaTime * 0.08 * this.autonomy;
            this.points.rotation.y += deltaTime * 0.12 * this.autonomy;
            this.points.rotation.z += deltaTime * 0.05 * this.autonomy;
            
            // Self-composition breathing effect
            const breathe = 1.0 + Math.sin(this.time * 0.4) * 0.1;
            this.points.scale.setScalar(breathe);
        }
        
        // Update current iteration for recursive visualization
        this.currentIteration = (this.currentIteration + deltaTime * 2) % this.recursiveDepth;
    }
    
    setIntensity(value) {
        this.intensity = Math.max(0, Math.min(2, value));
        if (this.material) {
            this.material.uniforms.intensity.value = this.intensity;
        }
    }
    
    setRecursiveDepth(depth) {
        const newDepth = Math.max(3, Math.min(12, depth));
        
        // Only regenerate if depth actually changed significantly
        if (Math.abs(newDepth - this.recursiveDepth) < 0.1) {
            return; // Skip if change is too small
        }
        
        this.recursiveDepth = newDepth;
        this.dimension = 2.0 + Math.log2(this.recursiveDepth) / 10;
        this.complexity = this.recursiveDepth;
        
        // Use shader uniforms instead of regenerating geometry when possible
        if (this.material && this.material.uniforms.recursiveDepth) {
            this.material.uniforms.recursiveDepth.value = this.recursiveDepth;
        } else {
            // Only regenerate geometry if really necessary
            this.createGeometry();
            if (this.points) {
                this.points.geometry = this.geometry;
            }
        }
        
        if (this.material) {
            this.material.uniforms.recursiveDepth.value = this.recursiveDepth;
        }
    }
    
    setAutonomy(value) {
        this.autonomy = Math.max(0.1, Math.min(2, value));
    }
    
    getObject3D() {
        return this.points;
    }
    
    getInfo() {
        return {
            name: 'Sovereignty Attractor (Ψ)',
            type: 'Self-referential recursive identity',
            recursiveDepth: this.recursiveDepth,
            dimension: this.dimension,
            particleCount: this.particleCount,
            selfReference: this.selfReference,
            autonomy: this.autonomy,
            complexity: this.complexity,
            scale: this.scale,
            intensity: this.intensity,
            currentIteration: Math.floor(this.currentIteration)
        };
    }
    
    // Get recursive state for analysis
    getRecursiveState() {
        return {
            depth: this.recursiveDepth,
            iteration: this.currentIteration,
            complexity: this.complexity,
            selfCompositionCount: this.recursiveDepth * this.particleCount
        };
    }
    
    dispose() {
        if (this.geometry) this.geometry.dispose();
        if (this.material) this.material.dispose();
        console.log('[Sovereignty] Attractor disposed');
    }
}
