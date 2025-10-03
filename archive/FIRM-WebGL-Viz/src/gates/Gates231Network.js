/**
 * 231-Gates Network for FIRM Framework
 * Implements C(22,2) = 231 undirected pairs between Hebrew letters
 * Based on FSCTF_231_Gates.md with motif classification and fractal interplay
 */

import * as THREE from 'three';

export class Gates231Network {
    constructor(hebrewLetters) {
        // Store reference to Hebrew letters for positioning
        this.hebrewLetters = hebrewLetters || [];
        
        // Gate motif classifications (from documentation)
        this.motifTypes = [
            'network_fusion', 'sculpted_region', 'io_dialogue', 'learned_memory',
            'curved_phase_bias', 'safe_anneal', 'locked_transition', 'controlled_chaos',
            'initiated_selection', 'micro_to_act', 'seeded_entangle', 'selective_entangle',
            'conditional_entangle', 'observed_history', 'historied_output', 'chaos_pruned',
            'graced_rebirth', 'chaos_resolved', 'housed_transport', 'bound_network'
        ];
        
        // Generate all 231 gates (C(22,2) combinations)
        this.gates = this.generateGates();
        
        // Visual parameters
        this.scale = 1.0;
        this.intensity = 0.5;
        this.activeGateCount = 50; // Show subset for performance
        this.animationSpeed = 0.1;
        
        // Audio-responsive parameters
        this.gateActivation = new Array(231).fill(0);
        this.motifWeights = {};
        
        // Three.js objects
        this.group = new THREE.Group();
        this.gateLines = [];
        this.gateParticles = [];
        this.activeGates = [];
        
        this.init();
    }
    
    log(message, type = 'info') {
        const colors = { info: '#00ff00', warning: '#ffff00', error: '#ff0000', success: '#00ffff' };
        console.log(`%c[231-Gates] ${message}`, `color: ${colors[type]}`);
    }
    
    generateGates() {
        const gates = [];
        let gateIndex = 0;
        
        // Generate all C(22,2) = 231 combinations
        for (let i = 0; i < 22; i++) {
            for (let j = i + 1; j < 22; j++) {
                const letterA = this.hebrewLetters[i] || { hebrew: 'א', fsctf: 'τ', role: 'threshold_silence' };
                const letterB = this.hebrewLetters[j] || { hebrew: 'ת', fsctf: '𝒢', role: 'completion_grace' };
                
                const gate = {
                    index: gateIndex,
                    i: i,
                    j: j,
                    letterA: letterA,
                    letterB: letterB,
                    motif: this.classifyPairMotif(letterA.role || 'generic', letterB.role || 'generic'),
                    zxComposition: this.getZXComposition(letterA.fsctf, letterB.fsctf),
                    fractalInterplay: this.getFractalInterplay(i, j),
                    strength: 0.3 + Math.random() * 0.4, // Base connection strength
                    phase: Math.random() * Math.PI * 2,  // Animation phase
                    color: this.getMotifColor(this.classifyPairMotif(letterA.role || 'generic', letterB.role || 'generic'))
                };
                
                gates.push(gate);
                gateIndex++;
            }
        }
        
        this.log(`Generated ${gates.length} gates from 22 Hebrew letters`, 'info');
        return gates;
    }
    
    classifyPairMotif(roleA, roleB) {
        // Simplified motif classification based on role combinations
        const roleSet = new Set([roleA, roleB]);
        
        if (roleSet.has('threshold_silence') && roleSet.has('completion_grace')) return 'graced_rebirth';
        if (roleSet.has('container') && roleSet.has('movement')) return 'network_fusion';
        if (roleSet.has('door') && roleSet.has('breath')) return 'io_dialogue';
        if (roleSet.has('connection') && roleSet.has('cut')) return 'controlled_chaos';
        if (roleSet.has('field') && roleSet.has('twist')) return 'locked_transition';
        if (roleSet.has('singularity') && roleSet.has('power')) return 'seeded_entangle';
        if (roleSet.has('memory') && roleSet.has('learning')) return 'learned_memory';
        if (roleSet.has('support') && roleSet.has('eye')) return 'safe_anneal';
        if (roleSet.has('expression') && roleSet.has('righteousness')) return 'chaos_resolved';
        if (roleSet.has('collective') && roleSet.has('beginning')) return 'observed_history';
        
        // Default classifications
        const motifIndex = (roleA.length + roleB.length) % this.motifTypes.length;
        return this.motifTypes[motifIndex];
    }
    
    getZXComposition(fsctfA, fsctfB) {
        // Simplified ZX calculus composition
        return `${fsctfA} → ${fsctfB}`;
    }
    
    getFractalInterplay(i, j) {
        // Deterministic fractal interplay based on indices
        const combinations = [
            'seed_in_cell', 'transport_on_cluster', 'pruned_hull', 'nested_tori',
            'critical_basin', 'mode_locking_map', 'chaos_with_spine', 'shadowed_branching',
            'filament_to_omega', 'composed_attractors'
        ];
        
        const index = (i * 7 + j * 11) % combinations.length;
        return combinations[index];
    }
    
    getMotifColor(motif) {
        // Color mapping for different motif types
        const colors = {
            'network_fusion': 0x00ffff,      // Cyan - network connections
            'sculpted_region': 0xff6600,     // Orange - sculpted forms
            'io_dialogue': 0x00ff00,         // Green - input/output
            'learned_memory': 0x9900ff,      // Purple - memory processes
            'curved_phase_bias': 0xffff00,   // Yellow - phase transitions
            'safe_anneal': 0x0066ff,         // Blue - annealing processes
            'locked_transition': 0xff0066,   // Pink - locked states
            'controlled_chaos': 0xff3300,    // Red - chaotic dynamics
            'seeded_entangle': 0x66ff00,     // Lime - quantum entanglement
            'graced_rebirth': 0xffd700,      // Gold - grace processes
            'chaos_resolved': 0x00ff66,      // Mint - resolved chaos
            'observed_history': 0x6600ff     // Violet - historical observation
        };
        
        return new THREE.Color(colors[motif] || 0x888888);
    }
    
    init() {
        this.createGateNetwork();
        this.selectActiveGates();
        this.log(`231-Gates Network initialized with ${this.activeGates.length} active gates`, 'success');
    }
    
    createGateNetwork() {
        // Create visual representation for all gates
        this.gates.forEach((gate, index) => {
            // Create line geometry for gate connection
            const positionA = this.getLetterPosition(gate.i);
            const positionB = this.getLetterPosition(gate.j);
            
            const geometry = new THREE.BufferGeometry().setFromPoints([positionA, positionB]);
            const material = new THREE.LineBasicMaterial({
                color: gate.color,
                transparent: true,
                opacity: 0.1, // Start very faint
                linewidth: 1
            });
            
            const line = new THREE.Line(geometry, material);
            line.userData = { gate: gate, originalOpacity: 0.1 };
            
            this.gateLines.push(line);
            this.group.add(line);
            
            // Create particle effect at midpoint for active gates
            const midpoint = new THREE.Vector3().addVectors(positionA, positionB).multiplyScalar(0.5);
            const particleGeometry = new THREE.SphereGeometry(0.02, 8, 8);
            const particleMaterial = new THREE.MeshBasicMaterial({
                color: gate.color,
                transparent: true,
                opacity: 0
            });
            
            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            particle.position.copy(midpoint);
            particle.userData = { gate: gate, basePosition: midpoint.clone() };
            
            this.gateParticles.push(particle);
            this.group.add(particle);
        });
        
        this.log(`Created ${this.gateLines.length} gate connections`, 'info');
    }
    
    getLetterPosition(letterIndex) {
        // Get position from Hebrew letter network or use default positions
        if (letterIndex < this.hebrewLetters.length) {
            const letter = this.hebrewLetters[letterIndex];
            return new THREE.Vector3(
                letter.position[0] * 1.5,
                letter.position[1] * 1.5,
                letter.position[2] * 1.5
            );
        }
        
        // Fallback: circular arrangement
        const angle = (letterIndex / 22) * Math.PI * 2;
        const radius = 3;
        return new THREE.Vector3(
            Math.cos(angle) * radius,
            Math.sin(angle) * radius,
            0
        );
    }
    
    selectActiveGates() {
        // Select subset of gates to display actively (for performance)
        this.activeGates = [];
        
        // Prioritize interesting motifs
        const priorityMotifs = ['graced_rebirth', 'network_fusion', 'controlled_chaos', 'seeded_entangle'];
        
        // First, add all priority motif gates
        this.gates.forEach(gate => {
            if (priorityMotifs.includes(gate.motif) && this.activeGates.length < this.activeGateCount) {
                this.activeGates.push(gate);
            }
        });
        
        // Fill remaining slots with random selection
        const remainingGates = this.gates.filter(gate => !this.activeGates.includes(gate));
        while (this.activeGates.length < this.activeGateCount && remainingGates.length > 0) {
            const randomIndex = Math.floor(Math.random() * remainingGates.length);
            this.activeGates.push(remainingGates.splice(randomIndex, 1)[0]);
        }
        
        this.log(`Selected ${this.activeGates.length} active gates from ${this.gates.length} total`, 'info');
    }
    
    update(deltaTime, audioFeatures) {
        const time = Date.now() * 0.001;
        
        // Update gate activations based on audio features
        if (audioFeatures && audioFeatures.hebrewActivation) {
            this.updateGateActivations(audioFeatures);
        }
        
        // Animate active gates
        this.activeGates.forEach((gate, index) => {
            const lineIndex = gate.index;
            const line = this.gateLines[lineIndex];
            const particle = this.gateParticles[lineIndex];
            
            if (line && particle) {
                // Audio-responsive activation
                const letterActivationA = audioFeatures?.hebrewActivation?.[gate.i] || 0;
                const letterActivationB = audioFeatures?.hebrewActivation?.[gate.j] || 0;
                const gateActivation = (letterActivationA + letterActivationB) / 2;
                
                // Base pulsing animation
                const pulsePhase = time * this.animationSpeed + gate.phase;
                const pulse = Math.sin(pulsePhase) * 0.5 + 0.5;
                
                // Combined intensity
                const intensity = (gateActivation * 0.7 + pulse * 0.3) * this.intensity;
                
                // Update line opacity
                line.material.opacity = 0.1 + intensity * 0.6;
                
                // Update particle
                particle.material.opacity = intensity * 0.8;
                const particleScale = 1.0 + intensity * 2.0;
                particle.scale.setScalar(particleScale);
                
                // Particle movement along connection
                const t = (Math.sin(pulsePhase * 2) + 1) / 2;
                const posA = this.getLetterPosition(gate.i);
                const posB = this.getLetterPosition(gate.j);
                particle.position.lerpVectors(posA, posB, t);
            }
        });
        
        // Gentle rotation of entire network
        this.group.rotation.z += deltaTime * 0.05;
    }
    
    updateGateActivations(audioFeatures) {
        // Map audio features to gate activations
        if (audioFeatures.hebrewActivation) {
            this.gates.forEach(gate => {
                const activationA = audioFeatures.hebrewActivation[gate.i] || 0;
                const activationB = audioFeatures.hebrewActivation[gate.j] || 0;
                this.gateActivation[gate.index] = (activationA + activationB) / 2;
            });
        }
    }
    
    setIntensity(intensity) {
        this.intensity = Math.max(0, Math.min(2, intensity));
    }
    
    setActiveGateCount(count) {
        this.activeGateCount = Math.max(10, Math.min(231, count));
        this.selectActiveGates();
    }
    
    getObject3D() {
        return this.group;
    }
    
    getInfo() {
        const motifCounts = {};
        this.gates.forEach(gate => {
            motifCounts[gate.motif] = (motifCounts[gate.motif] || 0) + 1;
        });
        
        return {
            name: '231-Gates Network',
            type: 'Undirected pairs between 22 Hebrew letters',
            totalGates: this.gates.length,
            activeGates: this.activeGates.length,
            motifTypes: Object.keys(motifCounts).length,
            motifCounts: motifCounts,
            scale: this.scale,
            intensity: this.intensity,
            combinatorics: 'C(22,2) = 231 unique pairs'
        };
    }
    
    getGateByIndex(index) {
        return this.gates[index] || null;
    }
    
    getGatesByMotif(motif) {
        return this.gates.filter(gate => gate.motif === motif);
    }
    
    dispose() {
        // Dispose geometries and materials
        this.gateLines.forEach(line => {
            line.geometry.dispose();
            line.material.dispose();
        });
        
        this.gateParticles.forEach(particle => {
            particle.geometry.dispose();
            particle.material.dispose();
        });
        
        this.log('231-Gates Network disposed', 'info');
    }
}
