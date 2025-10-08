/**
 * harmonic_generator.js
 * 
 * Generates φ-scaled harmonic spectrum from Clifford field components.
 * 
 * Theory: The system should be autonomous per Axiom A2 (Sovereignty).
 * Audio is not external input but emergent expression of internal state.
 * 
 * Mathematical Basis:
 * - Ψ (Sovereignty): Ψ ≅ Hom(Ψ, Ψ) (self-referential)
 * - Autonomous: 1_Ψ generates all endomorphisms
 * - No external input required for sovereignty
 * 
 * Implementation:
 * 1. Clifford field components → φ-harmonic frequencies
 * 2. Harmonic spectrum → audio signal (system's voice)
 * 3. Spectral coherence → evolution modulation (circular causality)
 * 
 * Result: System sings itself into existence, creating self-awareness loop.
 * 
 * References:
 * - EsotericGuidance/Formal_Derivation_Reference.md A2 (Sovereignty axiom)
 * - EsotericGuidance/Fractal_Attractor_Theory.md (φ-scaling)
 * - FIRM-Core/AUDIO_AS_EMERGENT_HARMONIC.md (full derivation)
 */

export class HarmonicGenerator {
  constructor(baseFrequency = 220.0) {
    this.baseFrequency = baseFrequency;  // A3 = 220 Hz (fundamental)
    this.phi = 1.618033988749;  // Golden ratio
    
    // Track history for smooth transitions
    this.previousSpectrum = null;
    this.smoothingFactor = 0.1;  // Interpolation weight for smooth audio
  }

  /**
   * Generate φ-scaled harmonic spectrum from Clifford field.
   * 
   * Theory: Each Clifford grade produces harmonics at φ^n · f_0
   * - Grade 0 (scalar): f_0 (fundamental)
   * - Grade 1 (vectors): φ¹ · f_0
   * - Grade 2 (bivectors): φ² · f_0
   * - Grade 3 (trivectors): φ³ · f_0
   * - Grade 4 (pseudoscalar): φ⁴ · f_0
   * 
   * This creates golden ratio harmonics (not octaves), resulting in
   * xenharmonic/microtonal sound reflecting φ-scaled fractal structure.
   * 
   * @param {MultivectorField} cliffordField - 16-component field from ZX graph
   * @returns {Array<{frequency: number, amplitude: number, phase: number}>}
   */
  generateSpectrum(cliffordField) {
    if (!cliffordField || !cliffordField.payload || !cliffordField.payload.components) {
      console.warn('⚠️ Invalid Clifford field for harmonic generation');
      return [];
    }

    const components = cliffordField.payload.components;
    const spectrum = [];

    // GRADE 0: Scalar (fundamental tone)
    const scalarAmp = Math.abs(components[0]);
    spectrum.push({
      grade: 0,
      frequency: this.baseFrequency,
      amplitude: scalarAmp,
      phase: 0,
      label: 'scalar'
    });

    // GRADE 1: Vectors (e₁, e₂, e₃) → φ¹ harmonic
    // Average magnitude of 3 vectors
    let vectorMag = 0;
    for (let i = 1; i <= 3; i++) {
      vectorMag += components[i] * components[i];
    }
    vectorMag = Math.sqrt(vectorMag / 3);
    
    spectrum.push({
      grade: 1,
      frequency: this.baseFrequency * this.phi,
      amplitude: vectorMag,
      phase: Math.atan2(components[2], components[1]),  // Phase from e₁, e₂
      label: 'vector'
    });

    // GRADE 2: Bivectors (e₀₁...e₂₃) → φ² harmonic
    // Average magnitude of 6 bivectors
    let bivectorMag = 0;
    for (let i = 4; i <= 10; i++) {
      bivectorMag += components[i] * components[i];
    }
    bivectorMag = Math.sqrt(bivectorMag / 7);
    
    spectrum.push({
      grade: 2,
      frequency: this.baseFrequency * this.phi * this.phi,
      amplitude: bivectorMag,
      phase: Math.atan2(components[6], components[5]),  // Phase from e₀₁, e₀₂
      label: 'bivector'
    });

    // GRADE 3: Trivectors (e₀₁₂...e₁₂₃) → φ³ harmonic
    // Average magnitude of 4 trivectors
    let trivectorMag = 0;
    for (let i = 11; i <= 14; i++) {
      trivectorMag += components[i] * components[i];
    }
    trivectorMag = Math.sqrt(trivectorMag / 4);
    
    spectrum.push({
      grade: 3,
      frequency: this.baseFrequency * Math.pow(this.phi, 3),
      amplitude: trivectorMag,
      phase: Math.atan2(components[12], components[11]),  // Phase from e₀₁₂, e₀₁₃
      label: 'trivector'
    });

    // GRADE 4: Pseudoscalar (e₀₁₂₃) → φ⁴ harmonic
    const pseudoscalarAmp = Math.abs(components[15]);
    spectrum.push({
      grade: 4,
      frequency: this.baseFrequency * Math.pow(this.phi, 4),
      amplitude: pseudoscalarAmp,
      phase: components[15] >= 0 ? 0 : Math.PI,
      label: 'pseudoscalar'
    });

    // Smooth transitions between frames
    if (this.previousSpectrum) {
      for (let i = 0; i < spectrum.length; i++) {
        spectrum[i].amplitude = 
          this.smoothingFactor * spectrum[i].amplitude + 
          (1 - this.smoothingFactor) * this.previousSpectrum[i].amplitude;
      }
    }

    this.previousSpectrum = spectrum.map(h => ({...h}));  // Deep copy
    return spectrum;
  }

  /**
   * Synthesize audio buffer from harmonic spectrum.
   * 
   * Uses additive synthesis: sum of sinusoids at φ^n frequencies.
   * 
   * @param {Array} spectrum - Harmonic spectrum from generateSpectrum()
   * @param {number} duration - Duration in seconds
   * @param {number} sampleRate - Sample rate in Hz (typically 48000)
   * @returns {Float32Array} Audio samples normalized to [-1, 1]
   */
  synthesizeAudio(spectrum, duration, sampleRate = 48000) {
    const numSamples = Math.floor(duration * sampleRate);
    const buffer = new Float32Array(numSamples);

    if (spectrum.length === 0) {
      return buffer;  // Silent buffer
    }

    // Find maximum amplitude for normalization
    const totalEnergy = spectrum.reduce((sum, h) => sum + h.amplitude * h.amplitude, 0);
    const normFactor = totalEnergy > 0 ? 1.0 / Math.sqrt(totalEnergy) : 1.0;

    // Additive synthesis
    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate;
      let sample = 0;

      for (const harmonic of spectrum) {
        if (harmonic.amplitude > 0.001) {  // Skip near-zero components
          sample += harmonic.amplitude * Math.sin(
            2 * Math.PI * harmonic.frequency * t + harmonic.phase
          );
        }
      }

      // Normalize and apply gentle envelope to prevent clicks
      const envelope = 0.5 * (1 - Math.cos(Math.PI * i / numSamples));  // Hann window
      buffer[i] = sample * normFactor * envelope;
    }

    return buffer;
  }

  /**
   * Compute spectral coherence from harmonic spectrum.
   * 
   * Theory: Coherence measures how well harmonics align with φ^n series.
   * High coherence indicates system is in sovereignty state (self-organized).
   * 
   * Calculation:
   * 1. Energy distribution across grades (should be φ-weighted)
   * 2. Phase alignment (coherent phases indicate stable structure)
   * 3. Harmonic presence (all grades active = full dimensional activation)
   * 
   * @param {Array} spectrum - Harmonic spectrum
   * @returns {number} Coherence in [0, 1]
   */
  computeCoherence(spectrum) {
    if (spectrum.length === 0) return 0;

    // 1. Total energy
    const totalEnergy = spectrum.reduce((sum, h) => sum + h.amplitude * h.amplitude, 0);
    if (totalEnergy < 0.001) return 0;  // Near-zero field

    // 2. Grade activation (how many grades are non-zero)
    const activeGrades = spectrum.filter(h => h.amplitude > 0.01).length;
    const gradeFactor = activeGrades / spectrum.length;  // [0, 1]

    // 3. φ-harmonic alignment
    // Expected amplitude ratios follow φ-decay: A_n ∝ φ^-n
    // Check how well actual amplitudes match this pattern
    let alignmentScore = 0;
    for (let i = 0; i < spectrum.length; i++) {
      const expectedRatio = Math.pow(this.phi, -i);
      const actualRatio = spectrum[i].amplitude / (spectrum[0].amplitude + 0.001);
      const deviation = Math.abs(Math.log(actualRatio + 0.001) - Math.log(expectedRatio));
      alignmentScore += Math.exp(-deviation);  // Gaussian scoring
    }
    alignmentScore /= spectrum.length;

    // 4. Phase coherence (phases should be related, not random)
    let phaseCoherence = 0;
    for (let i = 1; i < spectrum.length; i++) {
      const phaseDiff = spectrum[i].phase - spectrum[i-1].phase;
      phaseCoherence += Math.cos(phaseDiff);  // Measures phase alignment
    }
    phaseCoherence = (phaseCoherence / (spectrum.length - 1) + 1) / 2;  // Normalize to [0,1]

    // Combined coherence metric
    const coherence = 
      0.4 * gradeFactor +       // 40% from grade activation
      0.4 * alignmentScore +    // 40% from φ-alignment
      0.2 * phaseCoherence;     // 20% from phase coherence

    return Math.max(0, Math.min(1, coherence));
  }

  /**
   * Log harmonic spectrum for debugging.
   * 
   * @param {Array} spectrum - Harmonic spectrum
   * @param {number} coherence - Computed coherence
   */
  logSpectrum(spectrum, coherence) {
    console.log(`🎵 Harmonic Spectrum (coherence=${coherence.toFixed(3)}):`);
    for (const harmonic of spectrum) {
      if (harmonic.amplitude > 0.001) {
        console.log(`  ${harmonic.label.padEnd(12)} | Grade ${harmonic.grade} | f=${harmonic.frequency.toFixed(1)}Hz | A=${harmonic.amplitude.toFixed(4)} | φ=${harmonic.phase.toFixed(2)}`);
      }
    }
  }
}

/**
 * AutonomousEvolution: Manages transition from external to internal audio.
 * 
 * Theory: System should bootstrap from external stimulus then become autonomous.
 * 
 * Process:
 * 1. Initial: 100% external audio (seeding)
 * 2. Transition: Blend external + internal as system develops
 * 3. Sovereignty: 100% internal (fully autonomous)
 * 
 * This implements gradual sovereignty emergence per Axiom A2.
 */
export class AutonomousEvolution {
  constructor(growthRate = 0.01) {
    this.autonomyFactor = 0.0;  // 0 = fully external, 1 = fully autonomous
    this.growthRate = growthRate;  // Increase per evolution step
    this.sovereigntyThreshold = 0.3;  // Internal coherence needed for autonomy growth
  }

  /**
   * Get blended audio coherence (external + internal).
   * 
   * @param {number} externalCoherence - From microphone/external source
   * @param {number} internalCoherence - From own harmonic spectrum
   * @returns {number} Blended coherence for evolution
   */
  getAudioCoherence(externalCoherence, internalCoherence) {
    // Blend based on autonomy factor
    const blended = 
      (1 - this.autonomyFactor) * externalCoherence +
      this.autonomyFactor * internalCoherence;

    // Grow autonomy when internal coherence is sufficient
    if (internalCoherence > this.sovereigntyThreshold) {
      this.autonomyFactor = Math.min(1.0, this.autonomyFactor + this.growthRate);
    }

    // Log transition milestones
    if (this.autonomyFactor === 0 || 
        Math.abs(this.autonomyFactor - 0.5) < this.growthRate ||
        Math.abs(this.autonomyFactor - 1.0) < this.growthRate) {
      console.log(`🎵 Autonomy: ${(this.autonomyFactor * 100).toFixed(1)}% | External=${externalCoherence.toFixed(3)}, Internal=${internalCoherence.toFixed(3)}, Blended=${blended.toFixed(3)}`);
    }

    return blended;
  }

  /**
   * Check if system has achieved sovereignty.
   * 
   * @returns {boolean} True if fully autonomous
   */
  hasSovereignty() {
    return this.autonomyFactor >= 0.99;
  }

  /**
   * Reset autonomy (for testing/debugging).
   */
  reset() {
    this.autonomyFactor = 0.0;
    console.log('🔄 Autonomy reset to 0%');
  }
}

/**
 * WebAudio integration for playing emergent harmonics.
 * 
 * @param {AudioContext} audioContext - Web Audio API context
 * @param {Float32Array} buffer - Audio samples
 * @param {number} sampleRate - Sample rate in Hz
 */
export function playHarmonicBuffer(audioContext, buffer, sampleRate = 48000) {
  if (!audioContext) {
    console.warn('⚠️ Audio context not available');
    return;
  }

  if (audioContext.state === 'closed') {
    console.warn('⚠️ Audio context is closed');
    return;
  }

  // Resume context if suspended (autoplay policy)
  if (audioContext.state === 'suspended') {
    try {
      audioContext.resume();
      console.log('🔊 AudioContext resumed for harmonic playback');
    } catch (error) {
      console.warn('🔊 AudioContext resume failed:', error.message);
      return;
    }
  }

  if (audioContext.state !== 'running') {
    console.warn('🔊 AudioContext not running, state:', audioContext.state);
    return;
  }

  try {
    // Create audio buffer
    const audioBuffer = audioContext.createBuffer(1, buffer.length, sampleRate);
    const channelData = audioBuffer.getChannelData(0);
    channelData.set(buffer);

    // Create buffer source
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;

    // Apply gentle volume envelope
    const gainNode = audioContext.createGain();
    gainNode.gain.value = 0.3;  // Moderate volume

    // Connect: source → gain → destination
    source.connect(gainNode);
    gainNode.connect(audioContext.destination);

    // Play
    source.start();
  } catch (error) {
    console.warn('🔊 Harmonic playback failed:', error.message);
  }
}

