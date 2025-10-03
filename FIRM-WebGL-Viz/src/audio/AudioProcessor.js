/**
 * Audio Processor for FIRM Framework
 * Integrates Web Audio API with Meyda for real-time feature extraction
 * Maps audio features to FIRM operators and fractal attractors
 */

import Meyda from 'meyda';

export class AudioProcessor {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.sourceNode = null;
        this.analyzer = null;
        
        // Audio features for FIRM mapping
        this.features = {
            rms: 0,              // Volume → Grace intensity
            spectralCentroid: 0, // Brightness → Sovereignty complexity
            mfcc: new Array(13).fill(0), // Spectral shape → Hebrew letters
            zcr: 0,              // Zero crossing rate → Bireflection symmetry
            spectralRolloff: 0,  // High freq content → Bootstrap emergence
            energy: 0,           // Total energy → Overall system activation
            chroma: new Array(12).fill(0) // Pitch classes → 12-fold symmetries
        };
        
        // Transfer entropy estimation (simplified)
        this.channelHistory = {
            left: [],
            right: []
        };
        this.historyLength = 100;
        
        // Status tracking
        this.isInitialized = false;
        this.isAnalyzing = false;
        this.sampleRate = 44100;
        
        this.callbacks = [];
    }
    
    log(message, type = 'info') {
        const colors = { info: '#00ff00', warning: '#ffff00', error: '#ff0000', success: '#00ffff' };
        console.log(`%c[Audio] ${message}`, `color: ${colors[type]}`);
    }
    
    async initialize() {
        try {
            this.log('🎵 Initializing Audio Processor...', 'info');
            
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.sampleRate = this.audioContext.sampleRate;
            this.log(`Audio Context created (${this.sampleRate}Hz)`, 'info');
            
            // Request microphone access
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false,
                    sampleRate: this.sampleRate
                }
            });
            this.log('✅ Microphone access granted', 'success');
            
            // Create source node
            this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Initialize Meyda analyzer
            this.setupMeydaAnalyzer();
            
            this.isInitialized = true;
            this.log('🎤 Audio Processor initialized successfully', 'success');
            
            return true;
            
        } catch (error) {
            this.log(`❌ Audio initialization failed: ${error.message}`, 'error');
            throw error;
        }
    }
    
    setupMeydaAnalyzer() {
        // Configure Meyda for FIRM-relevant features
        this.analyzer = Meyda.createMeydaAnalyzer({
            audioContext: this.audioContext,
            source: this.sourceNode,
            bufferSize: 1024,
            featureExtractors: [
                'rms',              // Root Mean Square (volume)
                'energy',           // Total energy
                'spectralCentroid', // Brightness
                'spectralRolloff',  // High frequency content
                'zcr',              // Zero crossing rate
                'mfcc',             // Mel-frequency cepstral coefficients
                'chroma'            // Pitch class profile
            ],
            callback: (features) => this.processFeatures(features)
        });
        
        this.log('🔊 Meyda analyzer configured', 'info');
    }
    
    processFeatures(features) {
        if (!features) return;
        
        // Update feature values with smoothing
        const smoothing = 0.8;
        this.features.rms = this.features.rms * smoothing + (features.rms || 0) * (1 - smoothing);
        this.features.energy = this.features.energy * smoothing + (features.energy || 0) * (1 - smoothing);
        this.features.spectralCentroid = this.features.spectralCentroid * smoothing + 
            (features.spectralCentroid || 0) * (1 - smoothing);
        this.features.spectralRolloff = this.features.spectralRolloff * smoothing + 
            (features.spectralRolloff || 0) * (1 - smoothing);
        this.features.zcr = this.features.zcr * smoothing + (features.zcr || 0) * (1 - smoothing);
        
        // Update arrays
        if (features.mfcc) {
            for (let i = 0; i < Math.min(13, features.mfcc.length); i++) {
                this.features.mfcc[i] = this.features.mfcc[i] * smoothing + 
                    features.mfcc[i] * (1 - smoothing);
            }
        }
        
        if (features.chroma) {
            for (let i = 0; i < Math.min(12, features.chroma.length); i++) {
                this.features.chroma[i] = this.features.chroma[i] * smoothing + 
                    features.chroma[i] * (1 - smoothing);
            }
        }
        
        // Notify callbacks with processed features
        this.notifyCallbacks(this.getFIRMFeatures());
    }
    
    getFIRMFeatures() {
        // Map audio features to FIRM operators
        return {
            // Grace Operator (𝒢) - Volume-based emergence
            graceIntensity: Math.min(2.0, this.features.rms * 10), // 0-2 range
            
            // Sovereignty (Ψ) - Spectral complexity for recursive depth
            sovereigntyComplexity: Math.min(1.0, this.features.spectralCentroid / 4000), // Normalize
            
            // Bireflection (β) - Zero crossing rate for symmetry
            bireflectionSymmetry: Math.min(1.0, this.features.zcr / 0.5),
            
            // Bootstrap (𝒳) - High frequency emergence
            bootstrapEmergence: Math.min(1.0, this.features.spectralRolloff / 8000),
            
            // Hebrew Letters (22 mappings) - MFCC + Chroma features
            hebrewActivation: this.mapToHebrewLetters(),
            
            // Overall system energy
            systemEnergy: Math.min(2.0, this.features.energy * 5),
            
            // Fractal dimension modulation (based on spectral complexity)
            fractalDimension: 0.694 + (this.features.spectralCentroid / 10000) * 0.3, // 0.694-0.994 range
            
            // Raw features for advanced processing
            raw: { ...this.features }
        };
    }
    
    mapToHebrewLetters() {
        // Map 13 MFCC + 12 Chroma = 25 features to 22 Hebrew letters
        const letterActivation = new Array(22).fill(0);
        
        // Use MFCC coefficients for first 13 letters (א through מ)
        for (let i = 0; i < Math.min(13, letterActivation.length); i++) {
            letterActivation[i] = Math.abs(this.features.mfcc[i]) || 0;
        }
        
        // Use Chroma features for remaining letters, combining some
        const chromaStart = 13;
        for (let i = 0; i < Math.min(9, 12); i++) { // 9 remaining letters
            if (chromaStart + i < letterActivation.length) {
                letterActivation[chromaStart + i] = this.features.chroma[i] || 0;
            }
        }
        
        // Normalize to 0-1 range
        const maxVal = Math.max(...letterActivation, 0.001);
        return letterActivation.map(val => val / maxVal);
    }
    
    // Simplified transfer entropy estimation for real-time use
    estimateTransferEntropy(signal1, signal2) {
        // Simplified mutual information approximation
        // In a full implementation, this would use KSG estimator
        const correlation = this.calculateCorrelation(signal1, signal2);
        return Math.abs(correlation) * 0.5; // Rough approximation
    }
    
    calculateCorrelation(arr1, arr2) {
        if (arr1.length !== arr2.length || arr1.length === 0) return 0;
        
        const mean1 = arr1.reduce((a, b) => a + b) / arr1.length;
        const mean2 = arr2.reduce((a, b) => a + b) / arr2.length;
        
        let numerator = 0, denom1 = 0, denom2 = 0;
        
        for (let i = 0; i < arr1.length; i++) {
            const diff1 = arr1[i] - mean1;
            const diff2 = arr2[i] - mean2;
            numerator += diff1 * diff2;
            denom1 += diff1 * diff1;
            denom2 += diff2 * diff2;
        }
        
        return numerator / Math.sqrt(denom1 * denom2) || 0;
    }
    
    startAnalysis() {
        if (!this.isInitialized) {
            throw new Error('Audio processor not initialized');
        }
        
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
        
        this.analyzer.start();
        this.isAnalyzing = true;
        this.log('🎵 Audio analysis started', 'success');
    }
    
    stopAnalysis() {
        if (this.analyzer) {
            this.analyzer.stop();
        }
        this.isAnalyzing = false;
        this.log('⏸️ Audio analysis stopped', 'info');
    }
    
    onFeatures(callback) {
        this.callbacks.push(callback);
    }
    
    notifyCallbacks(features) {
        this.callbacks.forEach(callback => {
            try {
                callback(features);
            } catch (error) {
                this.log(`Callback error: ${error.message}`, 'error');
            }
        });
    }
    
    getStatus() {
        return {
            initialized: this.isInitialized,
            analyzing: this.isAnalyzing,
            sampleRate: this.sampleRate,
            contextState: this.audioContext?.state,
            features: { ...this.features }
        };
    }
    
    dispose() {
        this.stopAnalysis();
        
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        
        if (this.audioContext) {
            this.audioContext.close();
        }
        
        this.callbacks = [];
        this.log('🗑️ Audio processor disposed', 'info');
    }
}
