/**
 * Grace Attractor (𝒢-type) Implementation
 * Based on FIRM Framework: Fractal_Attractor_Theory.md
 * 
 * IFS: S₁(z) = z/φ + 0, S₂(z) = z/φ + 1/φ
 * Hausdorff dimension: D₀ ≈ ln(φ)/ln(2) ≈ 0.694
 */

import * as THREE from 'three';

export class GraceAttractor {
    constructor() {
        // Golden ratio φ = (1+√5)/2 ≈ 1.618
        this.phi = (1 + Math.sqrt(5)) / 2;
        this.invPhi = 1 / this.phi; // 1/φ ≈ 0.618
        
        // Attractor properties
        this.hausdorffDim = Math.log(this.phi) / Math.log(2); // ≈ 0.694
        this.particleCount = 5000;
        this.iterations = 12; // IFS iteration depth
        
        // Visual parameters
        this.scale = 2.0;
        this.intensity = 1.0;
        this.time = 0;
        
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
        
        // Generate Grace attractor points using IFS
        const positions = new Float32Array(this.particleCount * 3);
        const colors = new Float32Array(this.particleCount * 3);
        const sizes = new Float32Array(this.particleCount);
        
        for (let i = 0; i < this.particleCount; i++) {
            const point = this.generateGracePoint(i);
            
            // Position
            positions[i * 3] = point.x;
            positions[i * 3 + 1] = point.y;
            positions[i * 3 + 2] = point.z;
            
            // Color (golden gradient based on φ-scaling)
            const intensity = point.intensity;
            colors[i * 3] = 1.0; // Red
            colors[i * 3 + 1] = 0.618 * intensity; // Green (φ-scaled)
            colors[i * 3 + 2] = 0.0; // Blue
            
            // Size (varies with φ-scaling)
            sizes[i] = 1.0 + intensity * 2.0;
        }
        
        this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        console.log(`[Grace] Generated ${this.particleCount} points with φ=${this.phi.toFixed(3)}`);
    }
    
    generateGracePoint(index) {
        // Start from void (origin)
        let x = 0, y = 0, z = 0;
        
        // Apply IFS transformations iteratively
        for (let iter = 0; iter < this.iterations; iter++) {
            // Choose transformation based on golden ratio probability
            const choice = (index + iter * 1000) % 1000 / 1000;
            
            if (choice < this.invPhi) {
                // S₁(z) = z/φ + 0
                x = x * this.invPhi;
                y = y * this.invPhi;
                z = z * this.invPhi;
            } else {
                // S₂(z) = z/φ + 1/φ
                x = x * this.invPhi + this.invPhi;
                y = y * this.invPhi + this.invPhi * Math.sin(iter * 0.618);
                z = z * this.invPhi + this.invPhi * Math.cos(iter * 0.618);
            }
        }
        
        // Add spiral component for 3D visualization
        const angle = index * 0.618 * Math.PI; // φ-scaled angle
        const radius = Math.pow(this.invPhi, index % 8); // φ-scaled radius
        
        const spiralX = x + radius * Math.cos(angle);
        const spiralY = y + radius * Math.sin(angle);
        const spiralZ = z + (index % 100) * 0.01 - 0.5; // Slight Z variation
        
        // Calculate intensity based on distance from center (emergence strength)
        const distance = Math.sqrt(spiralX * spiralX + spiralY * spiralY + spiralZ * spiralZ);
        const intensity = Math.exp(-distance * 2) + 0.1; // Exponential falloff
        
        return {
            x: spiralX * this.scale,
            y: spiralY * this.scale,
            z: spiralZ * this.scale,
            intensity: intensity
        };
    }
    
    createMaterial() {
        // Vertex shader with φ-scaling animation
        const vertexShader = `
            attribute vec3 color;
            varying vec3 vColor;
            varying float vIntensity;
            
            uniform float time;
            uniform float phi;
            uniform float intensity;
            uniform float size;
            
            void main() {
                vColor = color;
                
                // φ-scaled pulsing based on time
                float pulse = sin(time * phi) * 0.5 + 0.5;
                vIntensity = intensity * pulse;
                
                // Position with slight φ-scaled breathing
                vec3 pos = position;
                pos *= 1.0 + sin(time * phi * 0.5) * 0.1;
                
                vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                gl_PointSize = size * (100.0 / -mvPosition.z) * intensity; // Reduced from 300.0
                gl_Position = projectionMatrix * mvPosition;
            }
        `;
        
        // Fragment shader with golden glow
        const fragmentShader = `
            varying vec3 vColor;
            varying float vIntensity;
            
            uniform float opacity;
            uniform float glowIntensity;
            
            void main() {
                // Circular point with soft edges
                vec2 center = gl_PointCoord - vec2(0.5);
                float dist = length(center);
                
                if (dist > 0.5) discard;
                
                // Golden glow effect with controllable parameters
                float alpha = (1.0 - dist * 2.0) * vIntensity * opacity * glowIntensity;
                vec3 finalColor = vColor * (0.9 + vIntensity * 0.1);
                
                gl_FragColor = vec4(finalColor, alpha);
            }
        `;
        
        this.material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                phi: { value: this.phi },
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
        
        console.log(`[Grace] Material created with Hausdorff dimension: ${this.hausdorffDim.toFixed(3)}`);
    }
    
    createPoints() {
        this.points = new THREE.Points(this.geometry, this.material);
        this.points.name = 'GraceAttractor';
    }
    
    update(deltaTime) {
        this.time += deltaTime;
        
        if (this.material) {
            this.material.uniforms.time.value = this.time;
            this.material.uniforms.intensity.value = this.intensity;
        }
        
        // Gentle rotation around φ-scaled axis
        if (this.points) {
            this.points.rotation.z += deltaTime * 0.1 * this.invPhi;
            this.points.rotation.y += deltaTime * 0.05 * this.invPhi;
        }
    }
    
    setIntensity(value) {
        this.intensity = Math.max(0, Math.min(2, value));
        if (this.material) {
            this.material.uniforms.intensity.value = this.intensity;
        }
    }
    
    setScale(value) {
        this.scale = Math.max(0.1, Math.min(5, value));
        // Use Three.js scaling instead of regenerating geometry
        if (this.object3D) {
            this.object3D.scale.setScalar(this.scale);
        }
        if (this.points) {
            this.points.geometry = this.geometry;
        }
    }
    
    getObject3D() {
        return this.points;
    }
    
    getInfo() {
        return {
            name: 'Grace Attractor (𝒢)',
            type: 'Self-similar emergence from void',
            phi: this.phi,
            hausdorffDimension: this.hausdorffDim,
            particleCount: this.particleCount,
            iterations: this.iterations,
            scale: this.scale,
            intensity: this.intensity
        };
    }
    
    dispose() {
        if (this.geometry) this.geometry.dispose();
        if (this.material) this.material.dispose();
        console.log('[Grace] Attractor disposed');
    }
}
