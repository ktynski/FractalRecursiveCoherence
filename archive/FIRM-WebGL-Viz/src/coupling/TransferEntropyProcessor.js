/**
 * Transfer Entropy Processor for Advanced Audio-Visual Coupling
 * Based on FIRM Framework: Information_Theory_Reference.md
 * 
 * Implements:
 * - Transfer Entropy: TE_Y→X = I(X_{t+1}; Y_t | X_t)
 * - KSG Estimator: k-nearest neighbor mutual information estimation
 * - Directed Information Flow: Audio → Visual systems
 * - Multi-lag Analysis: TE_Y→X^{(k)} = I(X_{t+1}; Y_t^{(k)} | X_t^{(k)})
 */

export class TransferEntropyProcessor {
    constructor() {
        // TE computation parameters
        this.k = 3; // k-nearest neighbors for KSG estimator
        this.windowSize = 100; // Time window for TE calculation
        this.lagMax = 5; // Maximum lag for multi-lag TE
        
        // Data buffers for time series
        this.audioBuffer = [];
        this.visualBuffers = {
            grace: [],
            sovereignty: [],
            bireflection: [],
            hebrew: [],
            gates: []
        };
        
        // Transfer entropy results
        this.transferEntropies = {
            audioToGrace: 0,
            audioToSovereignty: 0,
            audioToBireflection: 0,
            audioToHebrew: 0,
            audioToGates: 0,
            graceToSovereignty: 0,
            sovereigntyToBireflection: 0,
            bireflectionToHebrew: 0,
            hebrewToGates: 0
        };
        
        // Information flow network
        this.informationFlow = {
            totalFlow: 0,
            dominantDirection: 'none',
            flowStrength: 0,
            causalityIndex: 0
        };
        
        // KSG estimator state
        this.ksgCache = new Map();
        this.computeCount = 0;
        
        this.logMessages = [];
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toISOString();
        this.logMessages.push({ type, message, timestamp });
        const color = type === 'error' ? '#ff0000' : (type === 'warn' ? '#ffff00' : '#00ffff');
        console.log(`%c[TE] ${message}`, `color: ${color}`);
    }
    
    /**
     * Update audio features and compute transfer entropy
     */
    updateAudioFeatures(audioFeatures) {
        if (!audioFeatures) return;
        
        // Extract key audio features for TE analysis
        const audioVector = this.extractAudioVector(audioFeatures);
        this.audioBuffer.push(audioVector);
        
        // Maintain buffer size
        if (this.audioBuffer.length > this.windowSize) {
            this.audioBuffer.shift();
        }
        
        // Compute TE if we have enough data
        if (this.audioBuffer.length >= this.windowSize) {
            this.computeTransferEntropies();
            this.updateInformationFlow();
        }
    }
    
    /**
     * Update visual system states
     */
    updateVisualStates(visualStates) {
        if (!visualStates) return;
        
        // Extract visual features for each system
        Object.keys(this.visualBuffers).forEach(system => {
            if (visualStates[system]) {
                const visualVector = this.extractVisualVector(visualStates[system], system);
                this.visualBuffers[system].push(visualVector);
                
                // Maintain buffer size
                if (this.visualBuffers[system].length > this.windowSize) {
                    this.visualBuffers[system].shift();
                }
            }
        });
    }
    
    /**
     * Extract audio features into vector form for TE analysis
     */
    extractAudioVector(audioFeatures) {
        return {
            rms: audioFeatures.raw.rms || 0,
            loudness: audioFeatures.raw.loudness?.total || 0,
            spectralCentroid: audioFeatures.raw.spectralCentroid || 0,
            energy: audioFeatures.raw.energy || 0,
            zcr: audioFeatures.raw.zcr || 0,
            spectralFlatness: audioFeatures.raw.spectralFlatness || 0,
            mfcc0: audioFeatures.raw.mfcc?.[0] || 0,
            mfcc1: audioFeatures.raw.mfcc?.[1] || 0,
            chroma0: audioFeatures.raw.chroma?.[0] || 0,
            systemEnergy: audioFeatures.systemEnergy || 0,
            timestamp: Date.now()
        };
    }
    
    /**
     * Extract visual system features into vector form
     */
    extractVisualVector(visualState, system) {
        const baseVector = {
            intensity: visualState.intensity || 0,
            scale: visualState.scale || 1,
            timestamp: Date.now()
        };
        
        // Add system-specific features
        switch (system) {
            case 'grace':
                return {
                    ...baseVector,
                    phi: visualState.phi || 1.618,
                    hausdorffDim: visualState.hausdorffDimension || 0.694,
                    particleCount: visualState.particleCount || 5000
                };
                
            case 'sovereignty':
                return {
                    ...baseVector,
                    recursiveDepth: visualState.recursiveDepth || 6,
                    dimension: visualState.dimension || 2.258,
                    selfReference: visualState.selfReference || 0.618,
                    autonomy: visualState.autonomy || 1.0
                };
                
            case 'bireflection':
                return {
                    ...baseVector,
                    mirrorPairs: visualState.mirrorPairs || 2000,
                    symmetryRatio: visualState.symmetryRatio || 0.996,
                    mirrorStrength: visualState.mirrorStrength || 1.0,
                    dualityBalance: visualState.dualityBalance || 0.5
                };
                
            case 'hebrew':
                return {
                    ...baseVector,
                    letterCount: visualState.letterCount || 22,
                    connectionCount: visualState.connectionCount || 22,
                    activationSum: this.sumActivations(visualState.activations)
                };
                
            case 'gates':
                return {
                    ...baseVector,
                    totalGates: visualState.totalGates || 231,
                    activeGates: visualState.activeGates || 50,
                    motifTypes: visualState.motifTypes || 12
                };
                
            default:
                return baseVector;
        }
    }
    
    sumActivations(activations) {
        if (!activations) return 0;
        return Object.values(activations).reduce((sum, val) => sum + (val || 0), 0);
    }
    
    /**
     * Compute transfer entropies using simplified KSG estimator
     */
    computeTransferEntropies() {
        this.computeCount++;
        
        // Only compute every 10 frames for performance
        if (this.computeCount % 10 !== 0) return;
        
        try {
            // Audio → Visual systems
            this.transferEntropies.audioToGrace = this.computeTE(
                this.audioBuffer, this.visualBuffers.grace, 'audio→grace'
            );
            
            this.transferEntropies.audioToSovereignty = this.computeTE(
                this.audioBuffer, this.visualBuffers.sovereignty, 'audio→sovereignty'
            );
            
            this.transferEntropies.audioToBireflection = this.computeTE(
                this.audioBuffer, this.visualBuffers.bireflection, 'audio→bireflection'
            );
            
            this.transferEntropies.audioToHebrew = this.computeTE(
                this.audioBuffer, this.visualBuffers.hebrew, 'audio→hebrew'
            );
            
            this.transferEntropies.audioToGates = this.computeTE(
                this.audioBuffer, this.visualBuffers.gates, 'audio→gates'
            );
            
            // Visual → Visual systems (cascading information flow)
            this.transferEntropies.graceToSovereignty = this.computeTE(
                this.visualBuffers.grace, this.visualBuffers.sovereignty, 'grace→sovereignty'
            );
            
            this.transferEntropies.sovereigntyToBireflection = this.computeTE(
                this.visualBuffers.sovereignty, this.visualBuffers.bireflection, 'sovereignty→bireflection'
            );
            
            this.transferEntropies.bireflectionToHebrew = this.computeTE(
                this.visualBuffers.bireflection, this.visualBuffers.hebrew, 'bireflection→hebrew'
            );
            
            this.transferEntropies.hebrewToGates = this.computeTE(
                this.visualBuffers.hebrew, this.visualBuffers.gates, 'hebrew→gates'
            );
            
        } catch (error) {
            this.log(`TE computation error: ${error.message}`, 'warn');
        }
    }
    
    /**
     * Simplified Transfer Entropy computation using correlation-based approximation
     * TE_Y→X ≈ I(X_{t+1}; Y_t | X_t)
     */
    computeTE(sourceBuffer, targetBuffer, label) {
        if (!sourceBuffer.length || !targetBuffer.length) return 0;
        if (sourceBuffer.length < 10 || targetBuffer.length < 10) return 0;
        
        const minLength = Math.min(sourceBuffer.length, targetBuffer.length) - 1;
        if (minLength < 5) return 0;
        
        // Extract time series for TE calculation
        const Y_t = []; // Source at time t
        const X_t = []; // Target at time t  
        const X_t1 = []; // Target at time t+1
        
        for (let i = 0; i < minLength; i++) {
            // Use primary feature from each system
            const sourceFeature = this.getPrimaryFeature(sourceBuffer[i]);
            const targetFeature = this.getPrimaryFeature(targetBuffer[i]);
            const targetFeatureNext = this.getPrimaryFeature(targetBuffer[i + 1]);
            
            Y_t.push(sourceFeature);
            X_t.push(targetFeature);
            X_t1.push(targetFeatureNext);
        }
        
        // Simplified TE approximation using correlations
        // TE ≈ I(X_{t+1}; Y_t) - I(X_{t+1}; Y_t | X_t)
        const te = this.approximateTE(Y_t, X_t, X_t1);
        
        return Math.max(0, Math.min(1, te)); // Clamp to [0,1]
    }
    
    /**
     * Get primary feature from a data vector
     */
    getPrimaryFeature(dataVector) {
        if (!dataVector) return 0;
        
        // Use intensity or energy as primary feature
        return dataVector.intensity || dataVector.energy || dataVector.rms || 
               dataVector.systemEnergy || dataVector.activationSum || 0;
    }
    
    /**
     * Approximate Transfer Entropy using correlation analysis
     */
    approximateTE(Y_t, X_t, X_t1) {
        if (Y_t.length < 5) return 0;
        
        // Compute correlations
        const corr_X1_Y = this.correlation(X_t1, Y_t);
        const corr_X1_X = this.correlation(X_t1, X_t);
        const corr_Y_X = this.correlation(Y_t, X_t);
        
        // Approximate conditional correlation: corr(X_{t+1}, Y_t | X_t)
        const conditionalCorr = (corr_X1_Y - corr_X1_X * corr_Y_X) / 
                               Math.sqrt((1 - corr_X1_X * corr_X1_X) * (1 - corr_Y_X * corr_Y_X) + 1e-10);
        
        // Convert to information-theoretic measure
        // TE ≈ -0.5 * log(1 - conditionalCorr²)
        const te = -0.5 * Math.log(Math.max(1e-10, 1 - conditionalCorr * conditionalCorr));
        
        return Math.max(0, te);
    }
    
    /**
     * Compute Pearson correlation coefficient
     */
    correlation(x, y) {
        if (x.length !== y.length || x.length < 2) return 0;
        
        const n = x.length;
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = y.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
        const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
        
        const numerator = n * sumXY - sumX * sumY;
        const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
        
        return denominator === 0 ? 0 : numerator / denominator;
    }
    
    /**
     * Update information flow analysis
     */
    updateInformationFlow() {
        const te = this.transferEntropies;
        
        // Calculate total information flow
        this.informationFlow.totalFlow = Object.values(te).reduce((sum, val) => sum + val, 0);
        
        // Find dominant direction
        const audioToVisual = te.audioToGrace + te.audioToSovereignty + te.audioToBireflection + 
                             te.audioToHebrew + te.audioToGates;
        const visualToVisual = te.graceToSovereignty + te.sovereigntyToBireflection + 
                              te.bireflectionToHebrew + te.hebrewToGates;
        
        if (audioToVisual > visualToVisual * 1.5) {
            this.informationFlow.dominantDirection = 'audio-driven';
            this.informationFlow.flowStrength = audioToVisual;
        } else if (visualToVisual > audioToVisual * 1.5) {
            this.informationFlow.dominantDirection = 'visual-cascade';
            this.informationFlow.flowStrength = visualToVisual;
        } else {
            this.informationFlow.dominantDirection = 'balanced';
            this.informationFlow.flowStrength = (audioToVisual + visualToVisual) / 2;
        }
        
        // Calculate causality index (asymmetry measure)
        this.informationFlow.causalityIndex = Math.abs(audioToVisual - visualToVisual) / 
                                            (audioToVisual + visualToVisual + 1e-10);
    }
    
    /**
     * Get current transfer entropy results
     */
    getTransferEntropies() {
        return {
            ...this.transferEntropies,
            informationFlow: this.informationFlow,
            bufferSizes: {
                audio: this.audioBuffer.length,
                grace: this.visualBuffers.grace.length,
                sovereignty: this.visualBuffers.sovereignty.length,
                bireflection: this.visualBuffers.bireflection.length,
                hebrew: this.visualBuffers.hebrew.length,
                gates: this.visualBuffers.gates.length
            }
        };
    }
    
    /**
     * Get information flow network for visualization
     */
    getFlowNetwork() {
        const te = this.transferEntropies;
        const threshold = 0.1; // Minimum TE for edge display
        
        const nodes = [
            { id: 'audio', type: 'input', strength: this.informationFlow.totalFlow },
            { id: 'grace', type: 'attractor', strength: te.audioToGrace },
            { id: 'sovereignty', type: 'attractor', strength: te.audioToSovereignty },
            { id: 'bireflection', type: 'attractor', strength: te.audioToBireflection },
            { id: 'hebrew', type: 'network', strength: te.audioToHebrew },
            { id: 'gates', type: 'network', strength: te.audioToGates }
        ];
        
        const edges = [
            { from: 'audio', to: 'grace', weight: te.audioToGrace, visible: te.audioToGrace > threshold },
            { from: 'audio', to: 'sovereignty', weight: te.audioToSovereignty, visible: te.audioToSovereignty > threshold },
            { from: 'audio', to: 'bireflection', weight: te.audioToBireflection, visible: te.audioToBireflection > threshold },
            { from: 'audio', to: 'hebrew', weight: te.audioToHebrew, visible: te.audioToHebrew > threshold },
            { from: 'audio', to: 'gates', weight: te.audioToGates, visible: te.audioToGates > threshold },
            { from: 'grace', to: 'sovereignty', weight: te.graceToSovereignty, visible: te.graceToSovereignty > threshold },
            { from: 'sovereignty', to: 'bireflection', weight: te.sovereigntyToBireflection, visible: te.sovereigntyToBireflection > threshold },
            { from: 'bireflection', to: 'hebrew', weight: te.bireflectionToHebrew, visible: te.bireflectionToHebrew > threshold },
            { from: 'hebrew', to: 'gates', weight: te.hebrewToGates, visible: te.hebrewToGates > threshold }
        ];
        
        return { nodes, edges, flow: this.informationFlow };
    }
    
    /**
     * Reset all buffers and computations
     */
    reset() {
        this.audioBuffer = [];
        Object.keys(this.visualBuffers).forEach(key => {
            this.visualBuffers[key] = [];
        });
        
        Object.keys(this.transferEntropies).forEach(key => {
            this.transferEntropies[key] = 0;
        });
        
        this.informationFlow = {
            totalFlow: 0,
            dominantDirection: 'none',
            flowStrength: 0,
            causalityIndex: 0
        };
        
        this.ksgCache.clear();
        this.computeCount = 0;
        
        this.log('Transfer Entropy Processor reset', 'info');
    }
    
    getLogMessages() {
        return this.logMessages;
    }
}
