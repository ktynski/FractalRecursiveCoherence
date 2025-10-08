/**
 * analog_engine.js
 * Shared AudioContext + Analyser management for theory-driven evolution.
 */

function createOscillatorBank(audioContext, analyser) {
  const oscillators = [];
  const waveforms = ['sine', 'square', 'triangle', 'sawtooth'];

  for (let i = 0; i < waveforms.length; i++) {
    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();
    osc.type = waveforms[i];
    osc.frequency.value = 220 * (1 + i * 0.1);
    gain.gain.value = 0.2;
    osc.connect(gain);
    gain.connect(analyser);
    oscillators.push({ osc, gain });
  }

  return oscillators;
}

export function createAnalogEngine() {
  let audioContext = null;  // Create lazily on first user interaction
  let analyser = null;
  let oscillators = [];
  let freqDataBuffer = null;
  let isActive = false;
  let modulationPhase = 0;

  const engine = {
    audioContext,
    analyser,
    oscillators,
    freqDataBuffer,
    isActive,

    async initialize() {
      // Create AudioContext lazily on first initialization
      if (!this.audioContext) {
        try {
          this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
          console.warn('🔊 AudioContext creation failed (user gesture required):', error.message);
          return; // Exit early if AudioContext can't be created yet
        }
      }

      // Do NOT await resume here; let UI handle user-gesture resumption
      try {
        if (this.audioContext.state === 'suspended') {
          // Best-effort resume, ignore failure
          this.audioContext.resume().catch(() => {});
        }
      } catch (_) {}

      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.freqDataBuffer = new Float32Array(this.analyser.frequencyBinCount);
      this.isActive = true;

      // Start oscillators only when context is running
      this.ensureActive();
    },

    // Helper method to ensure AudioContext is created and resumed
    async ensureAudioContext() {
      if (!this.audioContext) {
        try {
          this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
          console.warn('🔊 AudioContext creation failed (user gesture required):', error.message);
          return false;
        }
      }

      if (this.audioContext.state === 'suspended') {
        try {
          await this.audioContext.resume();
          console.log('🔊 AudioContext resumed successfully');
          return true;
        } catch (error) {
          console.warn('🔊 AudioContext resume failed:', error.message);
          return false;
        }
      }

      return this.audioContext.state === 'running';
    },

    ensureActive() {
      if (!this.analyser) return;
      if (this.audioContext.state !== 'running') return;
      if (this.oscillators && this.oscillators.length > 0) return;
      try {
        this.oscillators = createOscillatorBank(this.audioContext, this.analyser);
        this.oscillators.forEach(({ osc }) => osc.start());
      } catch (_) {
        // If starting fails (policy), will retry on next ensureActive()
        this.oscillators = [];
      }
    },
    
    // THEORY-COMPLIANT: Modulate audio based on graph state (bidirectional coupling)
    modulateFromGraphState(graphCoherence, nodes) {
      if (!this.isActive || !this.oscillators || this.oscillators.length === 0) return;
      
      const φ = 1.618033988749;
      this.modulationPhase = (this.modulationPhase || 0) + 0.05;  // Advance modulation phase
      const modulationPhase = this.modulationPhase;
      
      // Bidirectional coupling: Graph → Audio
      const complexity = Math.min(1.0, nodes / 1000);  // 0-1 based on size
      const coherenceNorm = Math.min(1.0, graphCoherence / 200);  // 0-1
      
      // Modulate each oscillator (creates dynamic spectral content)
      this.oscillators.forEach(({ osc, gain }, i) => {
        // Frequency modulation: Graph complexity affects pitch
        const baseFreq = 220 * (1 + i * 0.1);
        const φModulation = Math.sin(modulationPhase * φ + i) * complexity * 50;
        const newFreq = baseFreq + φModulation;
        osc.frequency.setValueAtTime(newFreq, this.audioContext.currentTime);
        
        // Gain modulation: Coherence affects volume
        const baseGain = 0.15;
        const coherenceModulation = coherenceNorm * 0.2 * Math.cos(modulationPhase + i * φ);
        const newGain = baseGain + coherenceModulation;
        gain.gain.setValueAtTime(Math.max(0, newGain), this.audioContext.currentTime);
      });
    },

    getAudioCoherence() {
      if (!this.analyser || !this.audioContext || this.audioContext.state !== 'running') {
        return 0.5; // Safe default when audio is not available
      }

      const byteBuffer = new Uint8Array(this.analyser.frequencyBinCount);
      try {
        this.analyser.getByteFrequencyData(byteBuffer);
      } catch (_) {
        // On Safari iOS before resume, this may throw; return a safe default
        return 0.5;
      }
      let energy = 0;
      for (let i = 0; i < byteBuffer.length; i++) {
        energy += byteBuffer[i] * byteBuffer[i];
      }
      const coherence = energy / (byteBuffer.length * 255 * 255);
      return Math.max(0.1, Math.min(1.0, coherence));
    },

    stop() {
      this.oscillators.forEach(({ osc, gain }) => {
        try {
          osc.stop();
          osc.disconnect();
          gain.disconnect();
        } catch (_) {
          // No-op if already stopped
        }
      });
      this.oscillators = [];
      if (this.analyser) {
        try {
          this.analyser.disconnect();
        } catch (_) {
          // Ignore
        }
      }
    }
  };

  return engine;
}

export default createAnalogEngine;

