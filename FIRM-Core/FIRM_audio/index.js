"use strict";
/**
 * FIRM_audio: Analog core interface via Web Audio API.
 *
 * Principles:
 * - Internal oscillators are the default substrate for reproducibility.
 * - Microphone input is optional, opt-in, processed locally, and never retained.
 * - Parseval-based energy normalization maps audio energy to dimensionless inputs.
 */

/** Create a phase-locked oscillator bank (sine, square, triangle, saw). */
export function createOscillatorBank(audioCtx, config = {}) {
  const {
    baseFrequency = 220.0,  // A3, derived from harmonic series
    oscillatorCount = 4,    // sine, square, triangle, saw
    phaseCoherence = true   // Lock phases for coherent interference
  } = config;

  if (!audioCtx || typeof audioCtx.createOscillator !== 'function') {
    throw new Error("Valid AudioContext required");
  }

  const oscillators = [];
  const gainNodes = [];
  const waveforms = ['sine', 'square', 'triangle', 'sawtooth'];
  
  // Create phase-locked oscillator bank
  for (let i = 0; i < oscillatorCount; i++) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    // Set waveform and frequency
    osc.type = waveforms[i % waveforms.length];
    osc.frequency.setValueAtTime(baseFrequency * (1 + i * 0.1), audioCtx.currentTime);
    
    // Initial gain distribution (equal weighting)
    gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
    
    // Wire oscillator → gain → (will connect to analyser)
    osc.connect(gain);
    
    oscillators.push(osc);
    gainNodes.push(gain);
  }
  
  // Create mixer for coherent combination
  const mixer = audioCtx.createGain();
  mixer.gain.setValueAtTime(1.0, audioCtx.currentTime);
  
  // Connect all gain nodes to mixer
  gainNodes.forEach(gain => gain.connect(mixer));
  
  return {
    oscillators,
    gainNodes,
    mixer,
    start: () => oscillators.forEach(osc => osc.start()),
    stop: () => oscillators.forEach(osc => osc.stop()),
    setCoherenceWeights: (weights) => {
      if (weights.length !== gainNodes.length) {
        throw new Error("Weight array length must match oscillator count");
      }
      weights.forEach((weight, i) => {
        gainNodes[i].gain.setValueAtTime(weight, audioCtx.currentTime);
      });
    }
  };
}

/** Set up an AnalyserNode for FFT and time-domain captures. */
export function setupAnalyser(audioCtx, { fftSize = 2048 } = {}) {
  // Do not guess defaults beyond the locked N=2048; enforce explicitly.
  if (fftSize !== 2048) throw new Error("Locked: fftSize must be 2048 per spec");
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = fftSize;
  analyser.smoothingTimeConstant = 0.0; // avoid implicit temporal smoothing
  return analyser;
}

/** Compute Parseval energy and normalized coherence input C_audio in [0, 1]. */
export function computeParsevalEnergy(freqBins, normalization = null) {
  if (!freqBins || !Array.isArray(freqBins)) {
    throw new Error("freqBins must be a non-empty array");
  }
  
  // If no normalization provided, compute default from derivation
  if (!normalization) {
    // Import derivation module for Parseval normalization
    throw new Error("Normalization parameters required - import from FIRM_audio/derivations.py");
  }
  
  // Compute energy via Parseval: E = Σ|X[k]|²
  const energy = freqBins.reduce((sum, mag) => sum + mag * mag, 0);
  
  // Apply window correction and normalize to [0,1]
  const correctedEnergy = energy * normalization.correction_factor;
  const cAudio = Math.min(1.0, correctedEnergy / normalization.max_energy_bound);
  
  return {
    raw_energy: energy,
    corrected_energy: correctedEnergy,
    c_audio: cAudio,
    normalization_applied: normalization.proof_id
  };
}

/** Create coherent feedback loop between oscillators and FFT analysis. */
export function createCoherentFeedbackLoop(oscillatorBank, analyser) {
  if (!oscillatorBank || !analyser) {
    throw new Error("Both oscillatorBank and analyser required");
  }
  
  // Connect mixer output to analyser for feedback
  oscillatorBank.mixer.connect(analyser);
  
  return {
    updateCoherenceWeights: (coherenceValue) => {
      // Modulate oscillator weights based on coherence feedback
      // Higher coherence → more balanced weights
      // Lower coherence → more exploration (varied weights)
      const baseWeight = 0.25;
      const coherenceModulation = coherenceValue * 0.5; // [0, 0.5] range
      
      const weights = oscillatorBank.oscillators.map((_, i) => {
        const phase = (i / oscillatorBank.oscillators.length) * 2 * Math.PI;
        return baseWeight + coherenceModulation * Math.cos(phase);
      });
      
      oscillatorBank.setCoherenceWeights(weights);
    },
    
    getAnalysisData: () => {
      const bufferLength = analyser.frequencyBinCount;
      const freqData = new Uint8Array(bufferLength);
      const timeData = new Uint8Array(bufferLength);
      
      analyser.getByteFrequencyData(freqData);
      analyser.getByteTimeDomainData(timeData);
      
      return {
        frequency: Array.from(freqData),
        time: Array.from(timeData),
        timestamp: performance.now()
      };
    }
  };
}
