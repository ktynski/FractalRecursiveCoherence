/**
 * interpretation_modal.js
 * 
 * Interactive physics interpretation modal for Clifford field visualization.
 * 
 * Provides real-time feature identification and physics correspondences.
 */

export function createInterpretationModal() {
  // Create modal HTML structure
  const modalHTML = `
    <div id="interpretationModal" class="modal-overlay" style="display: none;">
      <div class="modal-content">
        <div class="modal-header">
          <h2>🔬 Clifford Field Physics Interpretation</h2>
          <button id="closeModal" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <div class="interpretation-tabs">
            <button class="interp-tab active" data-tab="quick">Quick Guide</button>
            <button class="interp-tab" data-tab="realtime">Real-Time Analysis</button>
            <button class="interp-tab" data-tab="physics">Physics Reference</button>
            <button class="interp-tab" data-tab="experiments">Experiments</button>
          </div>
          
          <div class="tab-content">
            <!-- Quick Guide Tab -->
            <div id="tab-quick" class="tab-panel active">
              <h3>What Am I Looking At?</h3>
              <p><strong>Cl(1,3) Spacetime Manifold</strong> emerging from quantum ZX graph</p>
              
              <table class="feature-table">
                <thead>
                  <tr>
                    <th>Visual Feature</th>
                    <th>Math</th>
                    <th>Physics</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="feature-badge red">Uniform Glow</span></td>
                    <td>Scalar (grade-0)</td>
                    <td>Higgs field VEV, mass density</td>
                  </tr>
                  <tr>
                    <td><span class="feature-badge blue">Bright Spheres</span></td>
                    <td>Bivector (grade-2)</td>
                    <td>EM field sources, photon states</td>
                  </tr>
                  <tr>
                    <td><span class="feature-badge white">Grid Pattern</span></td>
                    <td>Multi-grade interference</td>
                    <td>Standing waves, lattice QCD</td>
                  </tr>
                  <tr>
                    <td><span class="feature-badge green">Directional Flows</span></td>
                    <td>Vectors (grade-1)</td>
                    <td>Momentum, gauge potential</td>
                  </tr>
                  <tr>
                    <td><span class="feature-badge purple">Concentric Shells</span></td>
                    <td>Radial modes</td>
                    <td>Atomic orbitals (1s, 2p, 3d...)</td>
                  </tr>
                </tbody>
              </table>
              
              <div class="key-insight">
                <h4>🎯 Key Insight</h4>
                <p><strong>Each sphere = One X-spider in ZX graph!</strong></p>
                <p>This creates a testable prediction you can verify right now.</p>
              </div>
              
              <h3>Color Meaning</h3>
              <ul>
                <li><span class="color-box" style="background: #ff5555;"></span> <strong>Red</strong> → Scalar strength (mass/energy)</li>
                <li><span class="color-box" style="background: #55ff55;"></span> <strong>Green</strong> → Vector strength (momentum/E-field)</li>
                <li><span class="color-box" style="background: #5555ff;"></span> <strong>Blue</strong> → Bivector strength (angular momentum/B-field)</li>
              </ul>
            </div>
            
            <!-- Real-Time Analysis Tab -->
            <div id="tab-realtime" class="tab-panel">
              <h3>Current Field State</h3>
              <button id="runAnalysis" class="action-btn">🔍 Analyze Now</button>
              <button id="verifySpheres" class="action-btn">📊 Verify Sphere Count</button>
              <button id="catalogFeatures" class="action-btn">📋 Catalog Features</button>
              
              <div id="analysisResults" class="results-panel">
                <p class="hint">Click "Analyze Now" to see current field composition</p>
              </div>
              
              <h3>Evolution Tracking</h3>
              <div class="tracking-controls">
                <label>Track for: 
                  <select id="trackDuration">
                    <option value="10">10 seconds</option>
                    <option value="30" selected>30 seconds</option>
                    <option value="60">60 seconds</option>
                  </select>
                </label>
                <button id="startTracking" class="action-btn">⏱️ Start Tracking</button>
              </div>
              
              <div id="trackingResults" class="results-panel"></div>
            </div>
            
            <!-- Physics Reference Tab -->
            <div id="tab-physics" class="tab-panel">
              <h3>Clifford Algebra ↔ Physics</h3>
              
              <div class="physics-section">
                <h4>Quantum Field Theory</h4>
                <ul>
                  <li><strong>Scalar (grade-0)</strong> → Higgs field φ, mass generation</li>
                  <li><strong>Bivectors (grade-2)</strong> → EM field strength F_μν</li>
                  <li><strong>Vectors (grade-1)</strong> → Gauge potential A_μ</li>
                </ul>
              </div>
              
              <div class="physics-section">
                <h4>General Relativity</h4>
                <ul>
                  <li><strong>Bivector sources</strong> → Localized spacetime curvature</li>
                  <li><strong>Sphere surface</strong> → Effective event horizon</li>
                  <li><strong>Radial emission</strong> → Geodesics in curved spacetime</li>
                </ul>
              </div>
              
              <div class="physics-section">
                <h4>Quantum Mechanics</h4>
                <ul>
                  <li><strong>Concentric shells</strong> → Radial wave function R_nl(r)</li>
                  <li><strong>Interference patterns</strong> → Two-photon states</li>
                  <li><strong>Sphere pairs</strong> → Entangled X-spiders (EPR correlation)</li>
                </ul>
              </div>
              
              <div class="physics-section">
                <h4>Lattice Gauge Theory</h4>
                <ul>
                  <li><strong>Background grid</strong> → Spacetime discretization (UV cutoff)</li>
                  <li><strong>Spheres at nodes</strong> → Plaquette excitations (Wilson loops)</li>
                  <li><strong>Your visualization</strong> → Non-perturbative QFT!</li>
                </ul>
              </div>
            </div>
            
            <!-- Experiments Tab -->
            <div id="tab-experiments" class="tab-panel">
              <h3>Testable Predictions</h3>
              
              <div class="experiment">
                <h4>🧪 Experiment 1: Sphere-Counting Theorem</h4>
                <p><strong>Hypothesis</strong>: N_spheres = N_X-spiders</p>
                <button class="test-btn" onclick="window.verifySphereCount()">Run Test</button>
                <p class="method">Method: Compares predicted sphere count from ZX graph with visual observation</p>
              </div>
              
              <div class="experiment">
                <h4>🧪 Experiment 2: φ-Spacing Law</h4>
                <p><strong>Hypothesis</strong>: Consecutive sphere radii ratio → φ = 1.618...</p>
                <p class="method">Method: Measure distances between nested spheres, compute ratios</p>
                <p class="status">Status: Requires manual measurement from different vantage points</p>
              </div>
              
              <div class="experiment">
                <h4>🧪 Experiment 3: Interference Fringe Prediction</h4>
                <p><strong>Hypothesis</strong>: Fringe spacing λ = 2π / |Δφ|</p>
                <button class="test-btn" onclick="window.predictInterference()">Predict Fringes</button>
                <p class="method">Method: Calculates expected interference from X-spider phase differences</p>
              </div>
              
              <div class="experiment">
                <h4>🧪 Experiment 4: Evolution Tracking</h4>
                <p><strong>Hypothesis</strong>: Complexity grows with ZX node count</p>
                <button class="test-btn" onclick="window.trackEvolution(30)">Track 30s</button>
                <p class="method">Method: Monitors feature count vs. graph size over time</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <p class="reference">📖 Full guide: <code>FIRM_theory/clifford_visualization_physics_interpretation.md</code></p>
        </div>
      </div>
    </div>
  `;
  
  // Inject modal into DOM
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  
  // Add modal styles
  const styles = `
    <style>
      .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.85);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(4px);
      }
      
      .modal-content {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        width: 90%;
        max-width: 900px;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
      }
      
      .modal-header {
        padding: 20px;
        border-bottom: 1px solid #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .modal-header h2 {
        margin: 0;
        font-size: 24px;
        color: #eee;
      }
      
      .close-btn {
        background: none;
        border: none;
        font-size: 32px;
        color: #888;
        cursor: pointer;
        padding: 0 8px;
        line-height: 1;
      }
      
      .close-btn:hover {
        color: #fff;
      }
      
      .modal-body {
        padding: 20px;
        overflow-y: auto;
        flex: 1;
      }
      
      .interpretation-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        border-bottom: 1px solid #333;
      }
      
      .interp-tab {
        padding: 10px 16px;
        background: none;
        border: none;
        border-bottom: 2px solid transparent;
        color: #888;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
      }
      
      .interp-tab:hover {
        color: #ccc;
      }
      
      .interp-tab.active {
        color: #fff;
        border-bottom-color: #4a9eff;
      }
      
      .tab-panel {
        display: none;
      }
      
      .tab-panel.active {
        display: block;
      }
      
      .feature-table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
      }
      
      .feature-table th,
      .feature-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #333;
      }
      
      .feature-table th {
        background: #252525;
        color: #ccc;
        font-weight: 600;
      }
      
      .feature-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
      }
      
      .feature-badge.red { background: #ff5555; color: #fff; }
      .feature-badge.blue { background: #5555ff; color: #fff; }
      .feature-badge.green { background: #55ff55; color: #000; }
      .feature-badge.white { background: #fff; color: #000; border: 1px solid #666; }
      .feature-badge.purple { background: #aa55ff; color: #fff; }
      
      .key-insight {
        background: #2a2a4a;
        border-left: 4px solid #4a9eff;
        padding: 16px;
        margin: 20px 0;
        border-radius: 4px;
      }
      
      .key-insight h4 {
        margin-top: 0;
        color: #4a9eff;
      }
      
      .color-box {
        display: inline-block;
        width: 16px;
        height: 16px;
        border-radius: 3px;
        vertical-align: middle;
        margin-right: 8px;
      }
      
      .action-btn {
        background: #2a5a2a;
        border: 1px solid #3a7a3a;
        color: #fff;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        margin: 4px;
        font-size: 14px;
      }
      
      .action-btn:hover {
        background: #3a7a3a;
      }
      
      .test-btn {
        background: #4a5a9a;
        border: 1px solid #5a6aaa;
        color: #fff;
        padding: 6px 14px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
      }
      
      .test-btn:hover {
        background: #5a6aaa;
      }
      
      .results-panel {
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 16px;
        margin: 12px 0;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        max-height: 300px;
        overflow-y: auto;
      }
      
      .hint {
        color: #888;
        font-style: italic;
      }
      
      .physics-section {
        background: #252525;
        padding: 12px;
        margin: 12px 0;
        border-radius: 6px;
        border-left: 3px solid #4a9eff;
      }
      
      .physics-section h4 {
        margin-top: 0;
        color: #4a9eff;
      }
      
      .experiment {
        background: #1a1a2a;
        padding: 16px;
        margin: 16px 0;
        border-radius: 6px;
        border: 1px solid #333;
      }
      
      .experiment h4 {
        margin-top: 0;
        color: #eee;
      }
      
      .experiment .method {
        font-size: 13px;
        color: #aaa;
        margin: 8px 0;
      }
      
      .experiment .status {
        font-size: 13px;
        color: #888;
        font-style: italic;
      }
      
      .modal-footer {
        padding: 16px 20px;
        border-top: 1px solid #333;
        background: #1a1a1a;
      }
      
      .reference {
        margin: 0;
        font-size: 12px;
        color: #888;
      }
      
      .reference code {
        background: #0a0a0a;
        padding: 2px 6px;
        border-radius: 3px;
        color: #4a9eff;
      }
      
      .tracking-controls {
        margin: 12px 0;
      }
      
      .tracking-controls select {
        background: #2a2a2a;
        border: 1px solid #444;
        color: #eee;
        padding: 6px;
        border-radius: 4px;
        margin: 0 8px;
      }
    </style>
  `;
  
  document.head.insertAdjacentHTML('beforeend', styles);
  
  // Set up event handlers
  setupModalHandlers();
  
  console.log('📖 Interpretation modal initialized');
}

function setupModalHandlers() {
  const modal = document.getElementById('interpretationModal');
  const closeBtn = document.getElementById('closeModal');
  
  // Close modal
  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
  });
  
  // Close on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });
  
  // Close on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display !== 'none') {
      modal.style.display = 'none';
    }
  });
  
  // Tab switching
  const tabs = document.querySelectorAll('.interp-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Deactivate all tabs
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      
      // Activate clicked tab
      tab.classList.add('active');
      const targetPanel = document.getElementById(`tab-${tab.dataset.tab}`);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
    });
  });
  
  // Real-time analysis buttons
  const runAnalysisBtn = document.getElementById('runAnalysis');
  const verifySpheresBtn = document.getElementById('verifySpheres');
  const catalogBtn = document.getElementById('catalogFeatures');
  const startTrackingBtn = document.getElementById('startTracking');
  
  if (runAnalysisBtn) {
    runAnalysisBtn.addEventListener('click', () => {
      const results = window.analyzeVisibleGeometry();
      const resultsDiv = document.getElementById('analysisResults');
      
      if (results) {
        const html = `
          <div class="analysis-output">
            <h4>Dominant Grade: ${results.dominant}</h4>
            <pre>${JSON.stringify(results.analysis, null, 2)}</pre>
            <p class="hint">Check browser console for detailed analysis</p>
          </div>
        `;
        resultsDiv.innerHTML = html;
      } else {
        resultsDiv.innerHTML = '<p class="hint">Analysis failed - check console</p>';
      }
    });
  }
  
  if (verifySpheresBtn) {
    verifySpheresBtn.addEventListener('click', () => {
      const result = window.verifySphereCount();
      const resultsDiv = document.getElementById('analysisResults');
      
      const html = `
        <div class="analysis-output">
          <h4>Sphere-Counting Prediction</h4>
          <p><strong>X-spiders in ZX graph:</strong> ${result.predicted}</p>
          <p><strong>Predicted spheres:</strong> ~${result.predicted}</p>
          <p><strong>👁️ Your task:</strong> Manually count visible spheres in visualization</p>
          <p><strong>Theory:</strong> ${result.theory}</p>
          <p class="hint">If counts match → Direct evidence of ZX→Clifford mapping!</p>
        </div>
      `;
      resultsDiv.innerHTML = html;
    });
  }
  
  if (catalogBtn) {
    catalogBtn.addEventListener('click', () => {
      const catalog = window.catalogGeometry();
      const resultsDiv = document.getElementById('analysisResults');
      
      if (catalog && catalog.features) {
        const featureList = catalog.features.map(f => `
          <div class="catalog-item">
            <strong>${f.type}</strong>: ${f.physics}
            <br><small>ZX Source: ${f.zx_source} (count: ${f.count || 'N/A'})</small>
          </div>
        `).join('');
        
        resultsDiv.innerHTML = `
          <h4>Feature Catalog</h4>
          ${featureList}
          <p class="hint">See console for full JSON catalog</p>
        `;
      }
    });
  }
  
  if (startTrackingBtn) {
    startTrackingBtn.addEventListener('click', () => {
      const duration = parseInt(document.getElementById('trackDuration').value);
      const trackingDiv = document.getElementById('trackingResults');
      
      trackingDiv.innerHTML = `<p>⏱️ Tracking evolution for ${duration} seconds...</p>`;
      
      window.trackEvolution(duration);
      
      setTimeout(() => {
        const snapshots = window.evolutionSnapshots;
        if (snapshots) {
          const summary = `
            <h4>Evolution Summary</h4>
            <p><strong>Snapshots:</strong> ${snapshots.length}</p>
            <p><strong>Node growth:</strong> ${snapshots[snapshots.length-1].zx_stats.nodes - snapshots[0].zx_stats.nodes} nodes</p>
            <p><strong>Coherence Δ:</strong> ${(snapshots[snapshots.length-1].zx_stats.coherence - snapshots[0].zx_stats.coherence).toFixed(4)}</p>
            <p class="hint">Full data in window.evolutionSnapshots</p>
          `;
          trackingDiv.innerHTML = summary;
        }
      }, (duration + 1) * 1000);
    });
  }
}

// Show modal function
export function showInterpretationModal() {
  const modal = document.getElementById('interpretationModal');
  if (modal) {
    modal.style.display = 'flex';
  }
}

// Auto-initialize on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createInterpretationModal);
} else {
  createInterpretationModal();
}

// Make globally accessible
window.showInterpretationModal = showInterpretationModal;

