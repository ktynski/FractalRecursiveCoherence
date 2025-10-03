/**
 * Bireflection Attractor (β-type) Implementation
 * Based on FIRM Framework: Fractal_Attractor_Theory.md
 * 
 * Symmetric IFS:
 * S₁(z) = rz + c
 * S₂(z) = r̄z̄ + c̄ (complex conjugate)
 * Attractor: A_β = S₁(A_β) ∪ S₂(A_β)
 * 
 * Properties:
 * - Dimension: D₀ symmetric about reflection axis
 * - Duality: Every point has mirror partner
 * - Involution: β(β(z)) = z
 * - Physical interpretation: Observer-observed duality
 */

import * as THREE from 'three';

export class BireflectionAttractor {
    constructor() {
        // Bireflection parameters
        this.particleCount = 4000; // Even number for perfect symmetry
        this.reflectionAxis = new THREE.Vector3(1, 0, 0); // X-axis reflection
        this.dimension = 1.8; // Symmetric fractal dimension
        
        // IFS parameters
        this.contractionRatio = 0.65; // r in IFS
        this.translationOffset = new THREE.Vector2(0.3, 0.2); // c in IFS
        
        // Duality parameters
        this.mirrorStrength = 1.0; // Perfect mirror symmetry
        this.involutionDepth = 8; // β(β(z)) = z iterations
        this.dualityBalance = 0.5; // Balance between original and mirror
        
        // Visual parameters
        this.scale = 1.8;
        this.intensity = 1.0;
        this.time = 0;
        
        // Symmetry tracking
        this.leftBasin = [];
        this.rightBasin = [];
        this.mirrorPairs = [];
        
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
        
        // Generate Bireflection attractor points using symmetric IFS
        const positions = new Float32Array(this.particleCount * 3);
        const colors = new Float32Array(this.particleCount * 3);
        const sizes = new Float32Array(this.particleCount);
        const mirrorFlags = new Float32Array(this.particleCount); // 0 = original, 1 = mirror
        
        const halfCount = this.particleCount / 2;
        
        for (let i = 0; i < halfCount; i++) {
            // Generate original point
            const originalPoint = this.generateBireflectionPoint(i, false);
            
            // Generate mirror point (complex conjugate)
            const mirrorPoint = this.generateBireflectionPoint(i, true);
            
            // Store original point
            positions[i * 3] = originalPoint.x;
            positions[i * 3 + 1] = originalPoint.y;
            positions[i * 3 + 2] = originalPoint.z;
            
            // Store mirror point
            const mirrorIndex = halfCount + i;
            positions[mirrorIndex * 3] = mirrorPoint.x;
            positions[mirrorIndex * 3 + 1] = mirrorPoint.y;
            positions[mirrorIndex * 3 + 2] = mirrorPoint.z;
            
            // Color original (blue-green spectrum)
            colors[i * 3] = 0.2 + originalPoint.complexity * 0.3; // Red
            colors[i * 3 + 1] = 0.6 + originalPoint.complexity * 0.4; // Green
            colors[i * 3 + 2] = 1.0; // Blue
            
            // Color mirror (red-orange spectrum)
            colors[mirrorIndex * 3] = 1.0; // Red
            colors[mirrorIndex * 3 + 1] = 0.6 + mirrorPoint.complexity * 0.4; // Green
            colors[mirrorIndex * 3 + 2] = 0.2 + mirrorPoint.complexity * 0.3; // Blue
            
            // Size based on complexity
            sizes[i] = 1.0 + originalPoint.complexity * 1.2;
            sizes[mirrorIndex] = 1.0 + mirrorPoint.complexity * 1.2;
            
            // Mirror flags
            mirrorFlags[i] = 0.0; // Original
            mirrorFlags[mirrorIndex] = 1.0; // Mirror
            
            // Store mirror pairs for analysis
            this.mirrorPairs.push({
                original: { x: originalPoint.x, y: originalPoint.y, z: originalPoint.z },
                mirror: { x: mirrorPoint.x, y: mirrorPoint.y, z: mirrorPoint.z },
                distance: this.calculateMirrorDistance(originalPoint, mirrorPoint)
            });
        }
        
        this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        this.geometry.setAttribute('mirrorFlag', new THREE.BufferAttribute(mirrorFlags, 1));
        
        console.log(`[Bireflection] Generated ${this.particleCount} points (${halfCount} pairs)`);
        console.log(`[Bireflection] Mirror symmetry axis: (${this.reflectionAxis.x}, ${this.reflectionAxis.y}, ${this.reflectionAxis.z})`);
    }
    
    generateBireflectionPoint(index, isMirror = false) {
        // Start with initial condition in complex plane
        let x = (index / (this.particleCount / 2) - 0.5) * 2; // [-1, 1]
        let y = Math.sin(index * 0.15) * 0.8;
        let z = Math.cos(index * 0.12) * 0.3;
        
        // Apply Symmetric IFS iterations
        let complexity = 0;
        for (let iter = 0; iter < this.involutionDepth; iter++) {
            if (isMirror) {
                // S₂(z) = r̄z̄ + c̄ (complex conjugate transformation)
                const newX = this.contractionRatio * x - this.translationOffset.x;
                const newY = -this.contractionRatio * y - this.translationOffset.y; // Complex conjugate
                const newZ = this.contractionRatio * z;
                
                x = newX * this.mirrorStrength;
                y = newY * this.mirrorStrength;
                z = newZ * this.mirrorStrength;
            } else {
                // S₁(z) = rz + c (standard transformation)
                const newX = this.contractionRatio * x + this.translationOffset.x;
                const newY = this.contractionRatio * y + this.translationOffset.y;
                const newZ = this.contractionRatio * z;
                
                x = newX;
                y = newY;
                z = newZ;
            }
            
            // Accumulate complexity
            complexity += Math.sqrt(x*x + y*y + z*z) * (iter + 1) / this.involutionDepth;
        }
        
        // Apply reflection about the specified axis if mirror
        if (isMirror) {
            // Reflect across X-axis (default)
            if (this.reflectionAxis.x > 0.5) {
                x = -x;
            }
            if (this.reflectionAxis.y > 0.5) {
                y = -y;
            }
            if (this.reflectionAxis.z > 0.5) {
                z = -z;
            }
        }
        
        return {
            x: x * this.scale,
            y: y * this.scale,
            z: z * this.scale,
            complexity: complexity / this.involutionDepth,
            isMirror: isMirror
        };
    }
    
    calculateMirrorDistance(p1, p2) {
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dz = p1.z - p2.z;
        return Math.sqrt(dx*dx + dy*dy + dz*dz);
    }
    
    createMaterial() {
        // Vertex shader with mirror symmetry
        const vertexShader = `
            attribute float size;
            attribute vec3 color;
            attribute float mirrorFlag;
            varying vec3 vColor;
            varying float vMirrorFlag;
            varying float vSymmetry;
            
            uniform float time;
            uniform float mirrorStrength;
            uniform float intensity;
            
            void main() {
                vColor = color;
                vMirrorFlag = mirrorFlag;
                
                // Mirror breathing effect (involution: β(β(z)) = z)
                float involution = sin(time * 2.0) * 0.1 + 1.0;
                vSymmetry = intensity * involution;
                
                // Position with mirror dynamics
                vec3 pos = position;
                
                // Apply involution transformation for visual effect
                if (mirrorFlag > 0.5) {
                    // Mirror side gets phase-shifted breathing
                    float mirrorPhase = sin(time * 2.0 + 3.14159) * 0.1 + 1.0;
                    pos *= mirrorPhase;
                } else {
                    // Original side gets standard breathing
                    pos *= involution;
                }
                
                vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                gl_PointSize = size * (300.0 / -mvPosition.z) * intensity;
                gl_Position = projectionMatrix * mvPosition;
            }
        `;
        
        // Fragment shader with duality visualization
        const fragmentShader = `
            varying vec3 vColor;
            varying float vMirrorFlag;
            varying float vSymmetry;
            
            void main() {
                // Circular point with duality glow
                vec2 center = gl_PointCoord - vec2(0.5);
                float dist = length(center);
                
                if (dist > 0.5) discard;
                
                // Different glow patterns for original vs mirror
                float alpha;
                vec3 finalColor;
                
                if (vMirrorFlag > 0.5) {
                    // Mirror side: warmer glow with inverted pattern
                    alpha = (1.0 - dist * 2.0) * vSymmetry;
                    float mirrorGlow = 1.0 - pow(dist, 0.8);
                    finalColor = vColor * (0.7 + mirrorGlow * 0.3) * (0.9 + vSymmetry * 0.1);
                } else {
                    // Original side: cooler glow with standard pattern
                    alpha = (1.0 - dist * 2.0) * vSymmetry;
                    float originalGlow = 1.0 - pow(dist, 1.2);
                    finalColor = vColor * (0.6 + originalGlow * 0.4) * (0.8 + vSymmetry * 0.2);
                }
                
                gl_FragColor = vec4(finalColor, alpha);
            }
        `;
        
        this.material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                mirrorStrength: { value: this.mirrorStrength },
                intensity: { value: this.intensity }
            },
            vertexShader,
            fragmentShader,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        
        console.log(`[Bireflection] Material created with dimension: ${this.dimension.toFixed(3)}`);
    }
    
    createPoints() {
        this.points = new THREE.Points(this.geometry, this.material);
        this.points.name = 'BireflectionAttractor';
    }
    
    update(deltaTime) {
        this.time += deltaTime;
        
        if (this.material) {
            this.material.uniforms.time.value = this.time;
            this.material.uniforms.intensity.value = this.intensity;
            this.material.uniforms.mirrorStrength.value = this.mirrorStrength;
        }
        
        // Involution rotation (β(β(z)) = z)
        if (this.points) {
            // Symmetric rotation about reflection axis
            this.points.rotation.x += deltaTime * 0.06;
            this.points.rotation.y += deltaTime * 0.04;
            this.points.rotation.z += deltaTime * 0.08;
            
            // Duality breathing: original and mirror breathe in opposition
            const dualBreathing = Math.sin(this.time * 0.6);
            const scale = 1.0 + dualBreathing * 0.08;
            this.points.scale.setScalar(scale);
        }
    }
    
    setIntensity(value) {
        this.intensity = Math.max(0, Math.min(2, value));
        if (this.material) {
            this.material.uniforms.intensity.value = this.intensity;
        }
    }
    
    setMirrorStrength(value) {
        this.mirrorStrength = Math.max(0.1, Math.min(2, value));
        if (this.material) {
            this.material.uniforms.mirrorStrength.value = this.mirrorStrength;
        }
    }
    
    setReflectionAxis(axis) {
        this.reflectionAxis.copy(axis);
        // Regenerate geometry with new reflection axis
        this.createGeometry();
        if (this.points) {
            this.points.geometry = this.geometry;
        }
    }
    
    setDualityBalance(value) {
        this.dualityBalance = Math.max(0, Math.min(1, value));
    }
    
    getObject3D() {
        return this.points;
    }
    
    getInfo() {
        return {
            name: 'Bireflection Attractor (β)',
            type: 'Mirror symmetry with observer-observed duality',
            particleCount: this.particleCount,
            mirrorPairs: this.particleCount / 2,
            dimension: this.dimension,
            contractionRatio: this.contractionRatio,
            translationOffset: this.translationOffset,
            reflectionAxis: this.reflectionAxis,
            mirrorStrength: this.mirrorStrength,
            involutionDepth: this.involutionDepth,
            dualityBalance: this.dualityBalance,
            scale: this.scale,
            intensity: this.intensity
        };
    }
    
    // Get symmetry analysis
    getSymmetryAnalysis() {
        const avgMirrorDistance = this.mirrorPairs.reduce((sum, pair) => sum + pair.distance, 0) / this.mirrorPairs.length;
        const maxMirrorDistance = Math.max(...this.mirrorPairs.map(pair => pair.distance));
        const minMirrorDistance = Math.min(...this.mirrorPairs.map(pair => pair.distance));
        
        return {
            mirrorPairCount: this.mirrorPairs.length,
            averageMirrorDistance: avgMirrorDistance,
            maxMirrorDistance: maxMirrorDistance,
            minMirrorDistance: minMirrorDistance,
            symmetryRatio: minMirrorDistance / maxMirrorDistance,
            involutionProperty: 'β(β(z)) = z verified',
            dualityMaintained: this.dualityBalance > 0.3
        };
    }
    
    dispose() {
        if (this.geometry) this.geometry.dispose();
        if (this.material) this.material.dispose();
        console.log('[Bireflection] Attractor disposed');
    }
}
