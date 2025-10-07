/**
 * Soul Garbage Collection (𝒮-GC) UI Visualization
 *
 * Visualizes the recursive coherence-sieve rule in action:
 * 𝒮GC(μ) = ∅ if resonance(μ) < ε and grace(μ) = true,
 *          else μ ← { 𝒮GC(ν) | ν ∈ children(μ) }
 *
 * Integrates with existing FIRM UI to show:
 * - Morphic structure before/after pruning
 * - Entropy reduction metrics
 * - Grace field states
 * - Resonance alignment visualization
 */

class SoulGarbageCollectorVisualizer {
    constructor() {
        this.sgcState = {
            isRunning: false,
            currentStep: 0,
            totalSteps: 0,
            prunedNodes: [],
            entropyReduction: 0,
            structures: {
                before: null,
                after: null
            }
        };

        this.canvas = null;
        this.animationFrame = null;

        // Integration with ZX evolution engine
        this.evolutionMode = true;  // Run as background process vs separate view
        this.lastUpdateTime = 0;
        this.updateInterval = 1000;  // Update UI every second
    }

    initialize(containerId = 'sgc-visualization') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('SGC visualization container not found');
            return;
        }

        // Create visualization structure - adapted for integration mode
        container.innerHTML = `
            <div class="sgc-visualizer">
                <div class="sgc-header">
                    <h3>𝒮-GC: Soul Garbage Collection</h3>
                    <div class="sgc-status">
                        <span id="sgc-integration-status" class="status-indicator">🔄 Integrating...</span>
                        <span id="sgc-frequency-display">Every 50 steps</span>
                    </div>
                </div>

                <div class="sgc-metrics">
                    <div class="metric-group">
                        <div class="metric">
                            <span class="metric-label">Entropy Reduction:</span>
                            <span id="sgc-entropy-value" class="metric-value">0.0</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Pruned Nodes:</span>
                            <span id="sgc-pruned-value" class="metric-value">0</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Applications:</span>
                            <span id="sgc-applications-value" class="metric-value">0</span>
                        </div>
                    </div>
                </div>

                <div class="sgc-controls-integration">
                    <div class="control-group">
                        <label>SGC Frequency (steps):</label>
                        <input type="range" id="sgc-frequency-slider" min="10" max="200" value="50" step="10">
                        <span id="sgc-frequency-value">50</span>
                    </div>
                    <div class="control-group">
                        <button id="sgc-toggle-btn" class="btn-primary">Enable 𝒮-GC</button>
                        <button id="sgc-status-btn" class="btn-secondary">Status</button>
                    </div>
                </div>

                <div class="sgc-visualization-area">
                    <div class="structure-current">
                        <h4>Current Graph Structure</h4>
                        <canvas id="sgc-current-canvas" width="400" height="300"></canvas>
                    </div>
                </div>

                <div class="sgc-log">
                    <h4>𝒮-GC Log</h4>
                    <div id="sgc-log-content" class="log-content"></div>
                </div>
            </div>
        `;

        // Set up canvas contexts (integration mode uses single canvas)
        this.currentCanvas = document.getElementById('sgc-current-canvas');
        this.currentCtx = this.currentCanvas.getContext('2d');

        // Set up event listeners for integration mode
        this.setupIntegrationEventListeners();

        // Start in integration mode
        this.startEvolutionIntegration();
    }

    setupIntegrationEventListeners() {
        const toggleBtn = document.getElementById('sgc-toggle-btn');
        const statusBtn = document.getElementById('sgc-status-btn');
        const frequencySlider = document.getElementById('sgc-frequency-slider');
        const frequencyValue = document.getElementById('sgc-frequency-value');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleSGC());
        }

        if (statusBtn) {
            statusBtn.addEventListener('click', () => this.showSGCStatus());
        }

        if (frequencySlider) {
            frequencySlider.addEventListener('input', (e) => {
                const frequency = parseInt(e.target.value);
                frequencyValue.textContent = frequency;
                this.setSGCFrequency(frequency);
            });
        }
    }

    async runSGCFully() {
        if (this.sgcState.isRunning) return;

        this.sgcState.isRunning = true;
        this.log('Starting Soul Garbage Collection...');

        try {
            // Simulate 𝒮-GC process
            await this.simulateSGCProcess();

            // Update visualization
            this.updateVisualization();

            this.log('𝒮-GC completed successfully');

        } catch (error) {
            this.log(`Error in 𝒮-GC: ${error.message}`, 'error');
        } finally {
            this.sgcState.isRunning = false;
        }
    }

    async stepSGC() {
        if (this.sgcState.currentStep >= this.sgcState.totalSteps) {
            this.log('𝒮-GC already completed');
            return;
        }

        // Simulate one step of 𝒮-GC
        await this.simulateSGCStep();

        this.sgcState.currentStep++;
        this.updateProgress();

        if (this.sgcState.currentStep >= this.sgcState.totalSteps) {
            this.log('𝒮-GC completed');
        }
    }

    resetSGC() {
        this.sgcState = {
            isRunning: false,
            currentStep: 0,
            totalSteps: 0,
            prunedNodes: [],
            entropyReduction: 0,
            structures: {
                before: null,
                after: null
            }
        };

        this.updateVisualization();
        this.updateMetrics();
        this.log('𝒮-GC reset');
    }

    // Integration mode methods
    toggleSGC() {
        if (window.zxEvolutionEngine) {
            if (window.zxEvolutionEngine._sgcEnabled) {
                window.zxEvolutionEngine.disableSoulGarbageCollection();
                this.updateIntegrationStatus('Disabled');
                this.log('𝒮-GC disabled');
            } else {
                window.zxEvolutionEngine.enableSoulGarbageCollection();
                this.updateIntegrationStatus('Enabled');
                this.log('𝒮-GC enabled');
            }
        }
    }

    setSGCFrequency(frequency) {
        if (window.zxEvolutionEngine) {
            window.zxEvolutionEngine.setSGCFrequency(frequency);
            this.updateFrequencyDisplay(frequency);
            this.log(`𝒮-GC frequency set to every ${frequency} steps`);
        }
    }

    showSGCStatus() {
        if (window.zxEvolutionEngine) {
            const status = window.zxEvolutionEngine.getSGCStatus();
            this.log(`𝒮-GC Status: ${status.enabled ? 'Enabled' : 'Disabled'}, Frequency: ${status.frequency}, Applications: ${status.applications}`);
        }
    }

    updateIntegrationStatus(status) {
        const statusEl = document.getElementById('sgc-integration-status');
        if (statusEl) {
            statusEl.textContent = status;
            statusEl.className = `status-indicator ${status === 'Enabled' ? 'enabled' : 'disabled'}`;
        }
    }

    updateFrequencyDisplay(frequency) {
        const displayEl = document.getElementById('sgc-frequency-display');
        if (displayEl) {
            displayEl.textContent = `Every ${frequency} steps`;
        }
    }

    async simulateSGCProcess() {
        this.sgcState.totalSteps = 5;
        this.sgcState.currentStep = 0;

        // Simulate the 𝒮-GC algorithm step by step
        for (let step = 0; step < this.sgcState.totalSteps; step++) {
            await this.simulateSGCStep();
            this.sgcState.currentStep = step + 1;

            // Small delay for visualization
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }

    async simulateSGCStep() {
        if (!this.sgcState.structures.before) return;

        const before = this.sgcState.structures.before;
        const after = JSON.parse(JSON.stringify(before));

        // Simulate pruning based on coherence and grace
        const prunedNodes = [];

        for (let i = after.nodes.length - 1; i >= 0; i--) {
            const node = after.nodes[i];

            // 𝒮-GC rule: prune if resonance < ε and grace = true
            const epsilon = 0.3; // Coherence threshold
            if (node.resonance < epsilon && node.grace) {
                prunedNodes.push(node.id);
                after.nodes.splice(i, 1);

                // Remove edges connected to pruned node
                after.edges = after.edges.filter(edge =>
                    edge.from !== node.id && edge.to !== node.id
                );
            }
        }

        this.sgcState.structures.after = after;
        this.sgcState.prunedNodes = prunedNodes;

        // Calculate entropy reduction (simplified)
        const coherenceBefore = before.nodes.reduce((sum, n) => sum + n.coherence, 0) / before.nodes.length;
        const coherenceAfter = after.nodes.length > 0 ?
            after.nodes.reduce((sum, n) => sum + n.coherence, 0) / after.nodes.length : 0;

        this.sgcState.entropyReduction = Math.max(0, coherenceAfter - coherenceBefore);

        this.updateVisualization();
        this.updateMetrics();
    }

    updateVisualization() {
        // In integration mode, draw current graph structure
        if (window.zxEvolutionEngine) {
            const currentGraph = window.zxEvolutionEngine.currentGraph;
            if (currentGraph) {
                this.drawCurrentGraphStructure(this.currentCtx, currentGraph);
            }
        }
    }

    drawMorphicStructure(ctx, structure, phase) {
        if (!structure || !ctx) return;

        const canvas = ctx.canvas;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw edges first
        ctx.strokeStyle = phase === 'before' ? '#4a5568' : '#2d3748';
        ctx.lineWidth = 2;

        structure.edges.forEach(edge => {
            const fromNode = structure.nodes.find(n => n.id === edge.from);
            const toNode = structure.nodes.find(n => n.id === edge.to);

            if (fromNode && toNode) {
                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }
        });

        // Draw nodes
        structure.nodes.forEach(node => {
            // Node color based on field regime and coherence
            const regimeColors = {
                vacuum: '#e2e8f0',
                dark_sector: '#4299e1',
                matter: '#38a169'
            };

            const baseColor = regimeColors[node.fieldRegime] || '#cbd5e0';
            const intensity = node.coherence;
            const alpha = 0.3 + (intensity * 0.7);

            // Node fill
            ctx.fillStyle = this.hexToRgba(baseColor, alpha);
            ctx.beginPath();
            ctx.arc(node.x, node.y, 15, 0, 2 * Math.PI);
            ctx.fill();

            // Node border
            ctx.strokeStyle = node.grace ? '#38a169' : '#e53e3e';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Node label
            ctx.fillStyle = '#2d3748';
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(node.id.toString(), node.x, node.y + 3);
        });
    }

    updateMetrics() {
        const entropyEl = document.getElementById('sgc-entropy-value');
        const prunedEl = document.getElementById('sgc-pruned-value');
        const applicationsEl = document.getElementById('sgc-applications-value');

        if (entropyEl) entropyEl.textContent = this.sgcState.entropyReduction.toFixed(3);
        if (prunedEl) prunedEl.textContent = this.sgcState.prunedNodes.length.toString();
        if (applicationsEl) {
            if (window.zxEvolutionEngine) {
                const status = window.zxEvolutionEngine.getSGCStatus();
                applicationsEl.textContent = status.applications.toString();
            }
        }
    }

    drawCurrentGraphStructure(ctx, graph) {
        if (!graph || !ctx) return;

        const canvas = ctx.canvas;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (!graph.nodes || !graph.edges) return;

        // Draw edges first
        ctx.strokeStyle = '#4a5568';
        ctx.lineWidth = 2;

        for (const [u, v] of graph.edges) {
            const uNode = graph.nodes.find(n => n === u);
            const vNode = graph.nodes.find(n => n === v);

            if (uNode !== undefined && vNode !== undefined) {
                const uX = 200 + 120 * Math.cos((uNode / graph.nodes.length) * 2 * Math.PI);
                const uY = 150 + 120 * Math.sin((uNode / graph.nodes.length) * 2 * Math.PI);
                const vX = 200 + 120 * Math.cos((vNode / graph.nodes.length) * 2 * Math.PI);
                const vY = 150 + 120 * Math.sin((vNode / graph.nodes.length) * 2 * Math.PI);

                ctx.beginPath();
                ctx.moveTo(uX, uY);
                ctx.lineTo(vX, vY);
                ctx.stroke();
            }
        }

        // Draw nodes
        for (let i = 0; i < graph.nodes.length; i++) {
            const nodeId = graph.nodes[i];
            const x = 200 + 120 * Math.cos((i / graph.nodes.length) * 2 * Math.PI);
            const y = 150 + 120 * Math.sin((i / graph.nodes.length) * 2 * Math.PI);

            // Node color based on field regime
            const fieldRegime = this.getNodeFieldRegime(i);
            const regimeColors = {
                vacuum: '#e2e8f0',
                dark_sector: '#4299e1',
                matter: '#38a169'
            };

            const baseColor = regimeColors[fieldRegime] || '#cbd5e0';
            const alpha = 0.7;

            // Node fill
            ctx.fillStyle = this.hexToRgba(baseColor, alpha);
            ctx.beginPath();
            ctx.arc(x, y, 12, 0, 2 * Math.PI);
            ctx.fill();

            // Node border
            ctx.strokeStyle = '#2d3748';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Node label
            ctx.fillStyle = '#2d3748';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(nodeId.toString(), x, y + 2);
        }
    }

    getNodeFieldRegime(index) {
        // Simplified field regime assignment based on node index
        if (index < 2) return 'vacuum';
        if (index < 5) return 'dark_sector';
        return 'matter';
    }

    updateProgress() {
        const progressFill = document.getElementById('sgc-progress-fill');
        const progressText = document.getElementById('sgc-progress-text');

        if (progressFill && progressText && this.sgcState.totalSteps > 0) {
            const percentage = (this.sgcState.currentStep / this.sgcState.totalSteps) * 100;
            progressFill.style.width = `${percentage}%`;
            progressText.textContent = `Step ${this.sgcState.currentStep}/${this.sgcState.totalSteps}`;
        }
    }

    log(message, type = 'info') {
        const logContent = document.getElementById('sgc-log-content');
        if (!logContent) return;

        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;

        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    }

    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Integration methods for evolution engine
    updateFromEvolution(sgc, result) {
        if (!sgc || !result) return;

        // Update state from SGC results
        this.sgcState.prunedNodes = sgc.pruned_nodes || [];
        this.sgcState.entropyReduction = sgc.compute_entropy_reduction ?
            sgc.compute_entropy_reduction(null, result) : 0;

        // Update structures if available
        if (result && result.graph) {
            this.sgcState.structures.after = this._convertGraphToStructure(result.graph);
        }

        // Update UI periodically (not on every evolution step for performance)
        const now = Date.now();
        if (now - this.lastUpdateTime > this.updateInterval) {
            this.updateMetrics();
            this.lastUpdateTime = now;
        }
    }

    _convertGraphToStructure(graph) {
        if (!graph || !graph.nodes || !graph.edges) return null;

        const nodes = [];
        const edges = [];

        // Convert nodes
        for (const nodeId of graph.nodes) {
            nodes.push({
                id: nodeId,
                x: 150 + 80 * Math.cos((nodeId / graph.nodes.length) * 2 * Math.PI),
                y: 150 + 80 * Math.sin((nodeId / graph.nodes.length) * 2 * Math.PI),
                coherence: Math.random(), // Simplified for now
                resonance: Math.random(),
                grace: Math.random() > 0.5,
                fieldRegime: 'matter' // Simplified for now
            });
        }

        // Convert edges
        for (const [u, v] of graph.edges) {
            edges.push({ from: u, to: v });
        }

        return { nodes, edges };
    }

    startEvolutionIntegration() {
        this.evolutionMode = true;
        this.log('SGC integrated with evolution engine');
    }

    stopEvolutionIntegration() {
        this.evolutionMode = false;
        this.log('SGC evolution integration stopped');
    }
}

// Integration with existing FIRM UI
class SGCMonadListenerIntegration {
    constructor() {
        this.monadListener = null;
        this.sgcVisualizer = new SoulGarbageCollectorVisualizer();
    }

    initialize() {
        // Initialize 𝒮-GC visualizer
        this.sgcVisualizer.initialize();

        // Set up integration with monad listener if available
        this.setupMonadListenerIntegration();
    }

    setupMonadListenerIntegration() {
        // This would integrate with the actual monad listener when available
        // For now, we'll use the visualizer standalone
        console.log('𝒮-GC UI integration initialized');
    }

    // Method to be called when monad listener produces results
    onMonadListenerResult(morphicObject) {
        // Apply 𝒮-GC to the morphic object
        this.applySGCToMObject(morphicObject);
    }

    async applySGCToMObject(morphicObject) {
        this.log('Applying 𝒮-GC to morphic object...');

        // Simulate 𝒮-GC application (in real implementation, call actual API)
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Update visualization with results
        this.sgcVisualizer.updateVisualization();
        this.log('𝒮-GC applied to morphic object');
    }
}

// Export for use in FIRM UI
export { SoulGarbageCollectorVisualizer, SGCMonadListenerIntegration };
