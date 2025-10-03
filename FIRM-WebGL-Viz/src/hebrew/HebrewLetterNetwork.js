/**
 * Hebrew Letter Network for FIRM Framework
 * Implements the 22 Hebrew letters as positioned nodes with FSCTF operator mappings
 * Based on Kabbalah_Mapping_Full22.md and Tree of Life positioning
 */

import * as THREE from 'three';

export class HebrewLetterNetwork {
    constructor() {
        // Hebrew letters with FSCTF mappings (from our documentation)
        this.hebrewLetters = [
            { hebrew: 'א', name: 'Aleph', fsctf: 'τ', meaning: 'Silence, breath, void', sephira: 'Keter', gematria: 1, position: [0, 3, 0] },
            { hebrew: 'ב', name: 'Bet', fsctf: 'β', meaning: 'House, container', sephira: 'Chokhmah', gematria: 2, position: [-2, 2, 0] },
            { hebrew: 'ג', name: 'Gimel', fsctf: 'γ', meaning: 'Camel, movement', sephira: 'Binah', gematria: 3, position: [2, 2, 0] },
            { hebrew: 'ד', name: 'Dalet', fsctf: 'κ', meaning: 'Door', sephira: 'Chesed', gematria: 4, position: [-3, 1, 0] },
            { hebrew: 'ה', name: 'Heh', fsctf: 'ε', meaning: 'Breath, manifestation', sephira: 'Gevurah', gematria: 5, position: [3, 1, 0] },
            { hebrew: 'ו', name: 'Vav', fsctf: 'φ', meaning: 'Hook, connection', sephira: 'Tiferet', gematria: 6, position: [0, 1, 0] },
            { hebrew: 'ז', name: 'Zayin', fsctf: 'ζ', meaning: 'Sword, cut, division', sephira: 'Netzach', gematria: 7, position: [-2, 0, 0] },
            { hebrew: 'ח', name: 'Chet', fsctf: 'χ', meaning: 'Fence, field', sephira: 'Hod', gematria: 8, position: [2, 0, 0] },
            { hebrew: 'ט', name: 'Tet', fsctf: 'θ', meaning: 'Serpent, hidden good', sephira: 'Yesod', gematria: 9, position: [0, 0, 0] },
            { hebrew: 'י', name: 'Yod', fsctf: 'ψ', meaning: 'Hand, singularity', sephira: 'Malkuth', gematria: 10, position: [0, -1, 0] },
            { hebrew: 'כ', name: 'Kaf', fsctf: 'κ⁺', meaning: 'Palm, power', sephira: 'Keter', gematria: 20, position: [-1, 3, 0] },
            { hebrew: 'ל', name: 'Lamed', fsctf: 'λ', meaning: 'Ox-goad, learning', sephira: 'Chokhmah', gematria: 30, position: [1, 3, 0] },
            { hebrew: 'מ', name: 'Mem', fsctf: 'μ', meaning: 'Water, memory', sephira: 'Binah', gematria: 40, position: [-1, 2, 0] },
            { hebrew: 'נ', name: 'Nun', fsctf: 'η', meaning: 'Fish, faith', sephira: 'Gevurah', gematria: 50, position: [1, 2, 0] },
            { hebrew: 'ס', name: 'Samech', fsctf: 'σ', meaning: 'Support, prop', sephira: 'Chesed', gematria: 60, position: [-1, 1, 0] },
            { hebrew: 'ע', name: 'Ayin', fsctf: 'ω', meaning: 'Eye, fountain', sephira: 'Tiferet', gematria: 70, position: [1, 1, 0] },
            { hebrew: 'פ', name: 'Peh', fsctf: 'π', meaning: 'Mouth, expression', sephira: 'Netzach', gematria: 80, position: [-1, 0, 0] },
            { hebrew: 'צ', name: 'Tzadi', fsctf: 'ξ', meaning: 'Fishhook, righteousness', sephira: 'Hod', gematria: 90, position: [1, 0, 0] },
            { hebrew: 'ק', name: 'Qof', fsctf: 'ρ', meaning: 'Back of head, collective', sephira: 'Yesod', gematria: 100, position: [-0.5, 0, 0] },
            { hebrew: 'ר', name: 'Resh', fsctf: 'ℜ', meaning: 'Head, beginning', sephira: 'Malkuth', gematria: 200, position: [0.5, 0, 0] },
            { hebrew: 'ש', name: 'Shin', fsctf: 'ψ⁺', meaning: 'Fire, spirit, trinity', sephira: 'Chesed', gematria: 300, position: [0, -0.5, 0] },
            { hebrew: 'ת', name: 'Tav', fsctf: '𝒢', meaning: 'Mark, completion', sephira: 'Malkuth', gematria: 400, position: [0, -2, 0] }
        ];
        
        // Visual parameters
        this.scale = 1.5;
        this.letterSize = 0.3;
        this.glowIntensity = 1.0;
        this.networkOpacity = 0.8;
        
        // Audio-responsive parameters
        this.audioActivation = new Array(22).fill(0);
        this.baseIntensity = new Array(22).fill(0.3);
        
        // Three.js objects
        this.group = new THREE.Group();
        this.letterMeshes = [];
        this.connectionLines = [];
        this.textSprites = [];
        
        this.init();
    }
    
    log(message, type = 'info') {
        const colors = { info: '#00ff00', warning: '#ffff00', error: '#ff0000', success: '#00ffff' };
        console.log(`%c[Hebrew] ${message}`, `color: ${colors[type]}`);
    }
    
    init() {
        this.createLetterNodes();
        this.createConnections();
        this.log('Hebrew Letter Network initialized with 22 letters', 'success');
    }
    
    createLetterNodes() {
        this.hebrewLetters.forEach((letter, index) => {
            // Create letter node geometry
            const geometry = new THREE.SphereGeometry(this.letterSize, 16, 16);
            
            // Create material with Hebrew letter-specific properties
            const material = new THREE.MeshBasicMaterial({
                color: this.getLetterColor(letter),
                transparent: true,
                opacity: this.networkOpacity
            });
            
            // Create mesh
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(
                letter.position[0] * this.scale,
                letter.position[1] * this.scale,
                letter.position[2] * this.scale
            );
            
            // Store reference data
            mesh.userData = {
                letter: letter,
                index: index,
                originalColor: material.color.clone()
            };
            
            this.letterMeshes.push(mesh);
            this.group.add(mesh);
            
            // Create Hebrew text sprite
            const textSprite = this.createTextSprite(letter.hebrew, letter.fsctf);
            textSprite.position.copy(mesh.position);
            textSprite.position.y += this.letterSize + 0.2;
            
            this.textSprites.push(textSprite);
            this.group.add(textSprite);
        });
        
        this.log(`Created ${this.letterMeshes.length} Hebrew letter nodes`, 'info');
    }
    
    createTextSprite(hebrewChar, fsctfSymbol) {
        // Create canvas for text
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 128;
        
        // Draw Hebrew character and FSCTF symbol
        context.fillStyle = '#ffffff';
        context.font = '48px Arial Unicode MS, serif';
        context.textAlign = 'center';
        context.fillText(hebrewChar, 64, 40);
        
        context.fillStyle = '#ffd700';
        context.font = '24px Arial';
        context.fillText(fsctfSymbol, 64, 80);
        
        // Create texture and sprite
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ 
            map: texture,
            transparent: true
        });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(0.5, 0.5, 1);
        
        return sprite;
    }
    
    getLetterColor(letter) {
        // Color based on Sephirotic associations
        const sephirothColors = {
            'Keter': 0xffffff,      // White - Crown
            'Chokhmah': 0x808080,   // Gray - Wisdom  
            'Binah': 0x000000,      // Black - Understanding
            'Chesed': 0x0000ff,     // Blue - Mercy
            'Gevurah': 0xff0000,    // Red - Severity
            'Tiferet': 0xffff00,    // Yellow - Beauty
            'Netzach': 0x00ff00,    // Green - Victory
            'Hod': 0xff8000,        // Orange - Glory
            'Yesod': 0x800080,      // Purple - Foundation
            'Malkuth': 0x8b4513     // Brown - Kingdom
        };
        
        return new THREE.Color(sephirothColors[letter.sephira] || 0xffd700);
    }
    
    createConnections() {
        // Create Tree of Life connections (22 paths between 10 sephiroth)
        const connections = [
            [0, 1], [0, 2], [0, 5],     // From Keter
            [1, 2], [1, 3], [1, 5],     // From Chokhmah
            [2, 4], [2, 5],             // From Binah
            [3, 4], [3, 5], [3, 6],     // From Chesed
            [4, 5], [4, 7],             // From Gevurah
            [5, 6], [5, 7], [5, 8],     // From Tiferet
            [6, 7], [6, 8], [6, 9],     // From Netzach
            [7, 8], [7, 9],             // From Hod
            [8, 9]                      // From Yesod to Malkuth
        ];
        
        connections.forEach((connection, index) => {
            if (index < this.letterMeshes.length) {
                const startPos = this.letterMeshes[connection[0]].position;
                const endPos = this.letterMeshes[connection[1]].position;
                
                const geometry = new THREE.BufferGeometry().setFromPoints([startPos, endPos]);
                const material = new THREE.LineBasicMaterial({
                    color: 0x444444,
                    transparent: true,
                    opacity: 0.3
                });
                
                const line = new THREE.Line(geometry, material);
                line.userData = { connectionIndex: index };
                
                this.connectionLines.push(line);
                this.group.add(line);
            }
        });
        
        this.log(`Created ${this.connectionLines.length} Tree of Life connections`, 'info');
    }
    
    update(deltaTime, audioFeatures) {
        // Update letter activation based on audio features
        if (audioFeatures && audioFeatures.hebrewActivation) {
            this.audioActivation = audioFeatures.hebrewActivation;
            
            // Update visual properties based on audio
            this.letterMeshes.forEach((mesh, index) => {
                const activation = this.audioActivation[index] || 0;
                const intensity = this.baseIntensity[index] + activation;
                
                // Update material properties
                mesh.material.opacity = this.networkOpacity * (0.5 + intensity * 0.5);
                
                // Pulse effect based on activation
                const pulseScale = 1.0 + Math.sin(Date.now() * 0.005 + index) * activation * 0.2;
                mesh.scale.setScalar(pulseScale);
                
                // Color intensity modulation
                const color = mesh.userData.originalColor.clone();
                color.multiplyScalar(0.7 + activation * 0.3);
                mesh.material.color.copy(color);
            });
            
            // Update connection line intensities
            this.connectionLines.forEach((line, index) => {
                const avgActivation = (this.audioActivation[index] + this.audioActivation[index + 1]) / 2 || 0;
                line.material.opacity = 0.3 + avgActivation * 0.4;
            });
        }
        
        // Gentle rotation of the entire network
        this.group.rotation.y += deltaTime * 0.1;
    }
    
    setAudioFeatures(features) {
        if (features && features.hebrewActivation) {
            this.audioActivation = features.hebrewActivation;
        }
    }
    
    setScale(scale) {
        this.scale = Math.max(0.5, Math.min(3.0, scale));
        
        // Update positions
        this.letterMeshes.forEach((mesh, index) => {
            const letter = this.hebrewLetters[index];
            mesh.position.set(
                letter.position[0] * this.scale,
                letter.position[1] * this.scale,
                letter.position[2] * this.scale
            );
        });
        
        // Update text sprite positions
        this.textSprites.forEach((sprite, index) => {
            const mesh = this.letterMeshes[index];
            sprite.position.copy(mesh.position);
            sprite.position.y += this.letterSize + 0.2;
        });
        
        // Update connection lines
        this.connectionLines.forEach(line => {
            line.geometry.dispose();
            // Recreate geometry with new positions would go here
        });
    }
    
    setIntensity(intensity) {
        this.glowIntensity = Math.max(0, Math.min(2, intensity));
        this.networkOpacity = 0.4 + this.glowIntensity * 0.4;
        
        // Update all materials
        this.letterMeshes.forEach(mesh => {
            mesh.material.opacity = this.networkOpacity;
        });
    }
    
    getObject3D() {
        return this.group;
    }
    
    getInfo() {
        return {
            name: 'Hebrew Letter Network',
            type: '22-Letter Kabbalistic Tree of Life',
            letterCount: this.hebrewLetters.length,
            connectionCount: this.connectionLines.length,
            scale: this.scale,
            intensity: this.glowIntensity,
            sephiroth: ['Keter', 'Chokhmah', 'Binah', 'Chesed', 'Gevurah', 'Tiferet', 'Netzach', 'Hod', 'Yesod', 'Malkuth'],
            fsctfOperators: this.hebrewLetters.map(l => l.fsctf)
        };
    }
    
    getLetterByIndex(index) {
        return this.hebrewLetters[index] || null;
    }
    
    getLetterByHebrew(hebrew) {
        return this.hebrewLetters.find(l => l.hebrew === hebrew) || null;
    }
    
    dispose() {
        // Dispose geometries and materials
        this.letterMeshes.forEach(mesh => {
            mesh.geometry.dispose();
            mesh.material.dispose();
        });
        
        this.connectionLines.forEach(line => {
            line.geometry.dispose();
            line.material.dispose();
        });
        
        this.textSprites.forEach(sprite => {
            sprite.material.map.dispose();
            sprite.material.dispose();
        });
        
        this.log('Hebrew Letter Network disposed', 'info');
    }
}
