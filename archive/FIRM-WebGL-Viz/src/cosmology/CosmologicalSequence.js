/**
 * CosmologicalSequence.js
 * 
 * Implements the proper FIRM cosmological sequence:
 * Void (∅) → Bootstrap (𝒳) → Grace (𝒢) → Sovereignty (Ψ) → Bireflection (β) → Hebrew Network
 * 
 * Based on FIRM theory: universe builds structure through specific mathematical operations
 */

export class CosmologicalSequence {
    constructor() {
        this.currentPhase = 0;
        this.phaseProgress = 0.0;
        this.autoAdvance = true;
        this.phaseSpeed = 0.002; // Speed of phase progression
        
        // Cosmological phases
        this.phases = [
            {
                id: 0,
                name: "VOID",
                symbol: "∅",
                description: "Pure emptiness - measure-zero initial set",
                duration: 3.0, // seconds to spend in this phase
                color: [0.0, 0.0, 0.0], // Pure black
                hebrewLetter: null
            },
            {
                id: 1,
                name: "BOOTSTRAP",
                symbol: "𝒳",
                description: "Ex nihilo generation - something from nothing",
                duration: 5.0,
                color: [0.1, 0.0, 0.2], // Deep purple emergence
                hebrewLetter: "ב", // Bet - container/house
                equation: "𝒳ₙ₊₁ = G(∅, 𝒳ₙ)"
            },
            {
                id: 2,
                name: "GRACE",
                symbol: "𝒢",
                description: "Golden ratio emergence - coherent manifestation",
                duration: 4.0,
                color: [1.0, 0.618, 0.0], // Golden
                hebrewLetter: "א", // Aleph - threshold of silence
                equation: "S₁(z) = z/φ, S₂(z) = z/φ + 1/φ"
            },
            {
                id: 3,
                name: "SOVEREIGNTY",
                symbol: "Ψ",
                description: "Recursive self-awareness - autonomous identity",
                duration: 4.0,
                color: [0.0, 1.0, 1.0], // Cyan
                hebrewLetter: "ת", // Tav - completion
                equation: "Ψₙ₊₁ = Ψₙ ∘ Ψₙ"
            },
            {
                id: 4,
                name: "BIREFLECTION",
                symbol: "β",
                description: "Observer/observed duality - mirror symmetry",
                duration: 4.0,
                color: [1.0, 1.0, 1.0], // White light split
                hebrewLetter: "ר", // Resh - reflection
                equation: "β(β(z)) = z"
            },
            {
                id: 5,
                name: "HEBREW_NETWORK",
                symbol: "22×231",
                description: "Complete cosmic network - 22 letters, 231 gates",
                duration: 10.0,
                color: [0.8, 0.8, 1.0], // Soft blue-white
                hebrewLetter: "all 22",
                equation: "C(22,2) = 231 gates"
            }
        ];
        
        this.startTime = performance.now();
        this.phaseStartTime = this.startTime;
        
        this.log('🌌 Cosmological Sequence initialized', 'info');
        this.log('Phase 0: VOID (∅) - Pure emptiness before creation', 'info');
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[Cosmology] ${message}`);
        
        // Try to log to UI if available
        try {
            const logContent = document.getElementById('log-content');
            if (logContent) {
                const logEntry = document.createElement('div');
                const colorMap = {
                    info: '#00ff00',
                    warning: '#ffff00',
                    error: '#ff0000',
                    success: '#00ffff',
                    cosmology: '#ff69b4'
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
    
    update(deltaTime) {
        if (!this.autoAdvance) return;
        
        const currentTime = performance.now();
        const phaseElapsed = (currentTime - this.phaseStartTime) / 1000.0;
        const currentPhaseDuration = this.phases[this.currentPhase].duration;
        
        this.phaseProgress = Math.min(phaseElapsed / currentPhaseDuration, 1.0);
        
        // Check if we should advance to next phase
        if (this.phaseProgress >= 1.0 && this.currentPhase < this.phases.length - 1) {
            this.advancePhase();
        }
    }
    
    advancePhase() {
        this.currentPhase = Math.min(this.currentPhase + 1, this.phases.length - 1);
        this.phaseProgress = 0.0;
        this.phaseStartTime = performance.now();
        
        const phase = this.phases[this.currentPhase];
        this.log(`🎯 PHASE TRANSITION → ${phase.name} (${phase.symbol})`, 'cosmology');
        this.log(`📖 ${phase.description}`, 'cosmology');
        if (phase.equation) {
            this.log(`🔬 ${phase.equation}`, 'cosmology');
        }
        if (phase.hebrewLetter) {
            this.log(`🕎 Hebrew: ${phase.hebrewLetter}`, 'cosmology');
        }
    }
    
    retreatPhase() {
        this.currentPhase = Math.max(this.currentPhase - 1, 0);
        this.phaseProgress = 0.0;
        this.phaseStartTime = performance.now();
        
        const phase = this.phases[this.currentPhase];
        this.log(`⏪ PHASE RETREAT → ${phase.name} (${phase.symbol})`, 'cosmology');
    }
    
    jumpToPhase(phaseId) {
        if (phaseId >= 0 && phaseId < this.phases.length) {
            this.currentPhase = phaseId;
            this.phaseProgress = 0.0;
            this.phaseStartTime = performance.now();
            
            const phase = this.phases[this.currentPhase];
            this.log(`🎯 JUMP TO PHASE → ${phase.name} (${phase.symbol})`, 'cosmology');
        }
    }
    
    getCurrentPhase() {
        return this.phases[this.currentPhase];
    }
    
    getPhaseInfo() {
        const phase = this.getCurrentPhase();
        return {
            id: this.currentPhase,
            name: phase.name,
            symbol: phase.symbol,
            description: phase.description,
            progress: this.phaseProgress,
            color: phase.color,
            hebrewLetter: phase.hebrewLetter,
            equation: phase.equation,
            totalPhases: this.phases.length
        };
    }
    
    // Phase-specific activation states
    shouldShowVoid() {
        return this.currentPhase === 0;
    }
    
    shouldShowBootstrap() {
        return this.currentPhase >= 1;
    }
    
    shouldShowGrace() {
        return this.currentPhase >= 2;
    }
    
    shouldShowSovereignty() {
        return this.currentPhase >= 3;
    }
    
    shouldShowBireflection() {
        return this.currentPhase >= 4;
    }
    
    shouldShowHebrewNetwork() {
        return this.currentPhase >= 5;
    }
    
    // Get activation intensity for each system (0.0 to 1.0)
    getBootstrapIntensity() {
        if (this.currentPhase < 1) return 0.0;
        if (this.currentPhase === 1) return this.phaseProgress;
        return 1.0;
    }
    
    getGraceIntensity() {
        if (this.currentPhase < 2) return 0.0;
        if (this.currentPhase === 2) return this.phaseProgress;
        return 1.0;
    }
    
    getSovereigntyIntensity() {
        if (this.currentPhase < 3) return 0.0;
        if (this.currentPhase === 3) return this.phaseProgress;
        return 1.0;
    }
    
    getBireflectionIntensity() {
        if (this.currentPhase < 4) return 0.0;
        if (this.currentPhase === 4) return this.phaseProgress;
        return 1.0;
    }
    
    getHebrewNetworkIntensity() {
        if (this.currentPhase < 5) return 0.0;
        if (this.currentPhase === 5) return this.phaseProgress;
        return 1.0;
    }
    
    // Control methods
    pause() {
        this.autoAdvance = false;
        this.log('⏸️ Cosmological sequence paused', 'warning');
    }
    
    resume() {
        this.autoAdvance = true;
        this.phaseStartTime = performance.now() - (this.phaseProgress * this.phases[this.currentPhase].duration * 1000);
        this.log('▶️ Cosmological sequence resumed', 'success');
    }
    
    reset() {
        this.currentPhase = 0;
        this.phaseProgress = 0.0;
        this.phaseStartTime = performance.now();
        this.autoAdvance = true;
        this.log('🔄 Cosmological sequence reset to VOID', 'warning');
    }
    
    setSpeed(speed) {
        this.phaseSpeed = Math.max(0.001, Math.min(0.01, speed));
        // Adjust all phase durations
        this.phases.forEach(phase => {
            phase.duration = phase.duration * (0.002 / this.phaseSpeed);
        });
        this.log(`⚡ Cosmological speed set to ${speed.toFixed(4)}`, 'info');
    }
}
