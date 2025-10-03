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
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  let analyser = null;
  let oscillators = [];
  let freqDataBuffer = null;

  const engine = {
    audioContext,
    analyser,
    oscillators,
    freqDataBuffer,

    async initialize() {
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.freqDataBuffer = new Float32Array(this.analyser.frequencyBinCount);
      this.oscillators = createOscillatorBank(this.audioContext, this.analyser);
      this.oscillators.forEach(({ osc }) => osc.start());
    },

    getAudioCoherence() {
      if (!this.analyser) {
        return 0.5;
      }

      const byteBuffer = new Uint8Array(this.analyser.frequencyBinCount);
      this.analyser.getByteFrequencyData(byteBuffer);
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

