/**
 * metrics_updater.js
 * 
 * Real-time scientific metrics panel updater.
 * Updates metrics display every second with current ZX graph and Clifford field state.
 */

async function updateScientificMetrics() {
  // Check if ZX engine is available
  if (!window.zxEvolutionEngine) {
    return;
  }
  
  try {
    // Get current snapshot
    const snapshot = window.zxEvolutionEngine.getSnapshot();
    const graph = snapshot.graph;
    const rewrites = window.zxEvolutionEngine.getRewriteHistory();
    
    // ZX Graph Structure
    document.getElementById('metric-nodes').textContent = graph.nodes.length;
    
    const zCount = Object.values(graph.labels).filter(l => l.kind === 'Z').length;
    const xCount = Object.values(graph.labels).filter(l => l.kind === 'X').length;
    document.getElementById('metric-z-spiders').textContent = zCount;
    document.getElementById('metric-x-spiders').textContent = xCount;
    document.getElementById('metric-edges').textContent = graph.edges.length;
    document.getElementById('metric-coherence').textContent = snapshot.coherence.toFixed(4);
    
    // Clifford Field Components
    if (snapshot.cliffordField && snapshot.cliffordField.payload) {
      const c = snapshot.cliffordField.payload.components;
      
      const scalar = Math.abs(c[0]);
      const vectors = Math.sqrt(c[1]**2 + c[2]**2 + c[3]**2 + c[4]**2);
      const bivectors = Math.sqrt(c[5]**2 + c[6]**2 + c[7]**2 + c[8]**2 + c[9]**2 + c[10]**2);
      const trivectors = Math.sqrt(c[11]**2 + c[12]**2 + c[13]**2 + c[14]**2);
      const pseudo = Math.abs(c[15]);
      
      document.getElementById('metric-scalar').textContent = scalar.toFixed(4);
      document.getElementById('metric-vectors').textContent = vectors.toFixed(4);
      document.getElementById('metric-bivectors').textContent = bivectors.toFixed(4);
      document.getElementById('metric-trivectors').textContent = trivectors.toFixed(4);
      document.getElementById('metric-pseudo').textContent = pseudo.toFixed(4);
      
      // Determine dominant grade
      const grades = {
        'Scalar': scalar,
        'Vector': vectors,
        'Bivector': bivectors,
        'Trivector': trivectors,
        'Pseudo': pseudo
      };
      
      const dominant = Object.entries(grades).reduce((max, [name, val]) => 
        val > max.val ? {name, val} : max, {name: '-', val: 0}
      );
      
      document.getElementById('metric-dom-grade').textContent = dominant.name;
    }
    
    // Evolution Dynamics
    document.getElementById('metric-rewrites').textContent = rewrites.length;
    document.getElementById('metric-fusion').textContent = rewrites.filter(r => r.type === 'fusion').length;
    document.getElementById('metric-colorflip').textContent = rewrites.filter(r => r.type === 'color_flip').length;
    document.getElementById('metric-grace').textContent = rewrites.filter(r => r.type === 'grace_emergence').length;
    document.getElementById('metric-steps').textContent = window.zxEvolutionEngine._stepCount || 0;
    
    // Physics Observables
    document.getElementById('metric-pred-spheres').textContent = xCount;
    
    // Get audio coherence
    const audioCoherence = window.analogEngine?.getAudioCoherence() || 0;
    document.getElementById('metric-audio').textContent = audioCoherence.toFixed(3);
    
    // Get control parameters
    const controlParams = window.zxEvolutionEngine._controlParams || {};
    document.getElementById('metric-boot-energy').textContent = (controlParams.bootstrapEnergy || 1.0).toFixed(2);
    document.getElementById('metric-emerg-rate').textContent = (controlParams.emergenceRate || 1.0).toFixed(2);
    
    // Resonance metrics (Ω and Res) with resilient fallback
    try {
      if (!window.__resonanceMod) {
        try {
          window.__resonanceMod = await import('./FIRM_dsl/resonance.js');
        } catch (_) {
          // Fallback: build minimal module from core/coherence
          const coh = await import('./FIRM_dsl/coherence.js');
          const core = await import('./FIRM_dsl/core.js');
          window.__resonanceMod = {
            deriveOmegaSignature(graph) {
              core.validate_object_g(graph);
              const cycles = coh.compute_cycle_basis_signature(graph);
              const phase_bins = coh.derive_minimal_qpi_bins(graph);
              const phase_hist = coh.compute_phase_histogram_signature(graph, phase_bins);
              return { cycles, phase_bins, phase_hist };
            },
            computeResonanceAlignment(graph, omega) {
              core.validate_object_g(graph);
              if (!omega || !Number.isInteger(omega.phase_bins) || omega.phase_bins <= 0) {
                throw new Error('Invalid omega signature');
              }
              const cycles_s = coh.compute_cycle_basis_signature(graph);
              const hist_s = coh.compute_phase_histogram_signature(graph, omega.phase_bins);
              const safeCycles = omega.cycles || [];
              const safeHist = omega.phase_hist || new Array(omega.phase_bins).fill(0);
              return coh.similarity_S(cycles_s, safeCycles, hist_s, safeHist);
            }
          };
        }
      }
      if (!window.__omegaSignature && window.zxEvolutionEngine) {
        window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(snapshot.graph);
      }
      if (window.__omegaSignature) {
        const res = window.__resonanceMod.computeResonanceAlignment(snapshot.graph, window.__omegaSignature);
        const resElem = document.getElementById('metric-resonance');
        if (resElem) resElem.textContent = Number.isFinite(res) ? res.toFixed(4) : 'n/a';
      }
    } catch (e) {
      // resonance metrics are optional; proceed silently
    }
    
  } catch (error) {
    // Silent fail - metrics are non-critical
    console.warn('Metrics update failed:', error);
  }
}

// Initialize metrics panel functionality
function initializeMetricsPanel() {
  const metricsHeader = document.querySelector('.metrics-header');
  const metricsContent = document.getElementById('metricsContent');
  const metricsPanel = document.getElementById('metricsPanel');
  const topBar = document.getElementById('topBar');

  const root = document.documentElement;

  const updateLayoutOffsets = () => {
    window.requestAnimationFrame(() => {
      const topHeight = topBar ? topBar.offsetHeight : 64;
      root.style.setProperty('--top-bar-height', `${topHeight}px`);

      if (metricsPanel) {
        const panelHeight = metricsPanel.classList.contains('collapsed')
          ? metricsHeader.offsetHeight
          : metricsPanel.offsetHeight;
        root.style.setProperty('--metrics-height', `${panelHeight}px`);
      }
    });
  };

  if (!metricsHeader || !metricsContent || !metricsPanel) {
    console.warn('Metrics panel elements not found');
    return;
  }

  const applyState = (expanded) => {
    if (expanded) {
      metricsPanel.classList.remove('collapsed');
      metricsPanel.classList.add('expanded');
      metricsContent.setAttribute('aria-hidden', 'false');
    } else {
      metricsPanel.classList.remove('expanded');
      metricsPanel.classList.add('collapsed');
      metricsContent.setAttribute('aria-hidden', 'true');
    }

    updateLayoutOffsets();
  };

  // Initialize collapsed state from class
  const initialExpanded = !metricsPanel.classList.contains('collapsed');
  applyState(initialExpanded);
 
  const handleToggle = () => {
    const nowCollapsed = metricsPanel.classList.contains('collapsed');
    applyState(!nowCollapsed);
    document.body.dataset.metricsState = nowCollapsed ? 'expanded' : 'collapsed';
  };
 
  window.addEventListener('metricsStateChanged', () => {
    updateLayoutOffsets();
  });
  window.addEventListener('resize', updateLayoutOffsets);
 
  updateLayoutOffsets();
 
  window.addEventListener('beforeunload', () => {
    window.removeEventListener('metricsStateChanged', updateLayoutOffsets);
    window.removeEventListener('resize', updateLayoutOffsets);
  });
 
  console.log('📊 Scientific metrics panel initialized');
}

// Initialize interpretation modal button
function initializeInterpretationButton() {
  const openBtn = document.getElementById('openInterpretation');
  if (openBtn) {
    openBtn.addEventListener('click', () => {
      if (window.showInterpretationModal) {
        window.showInterpretationModal();
      } else {
        console.warn('Interpretation modal not loaded yet');
      }
    });
  }
}

// Start metrics update loop
function startMetricsUpdates() {
  // Update immediately
  updateScientificMetrics();
  
  // Update every second
  setInterval(updateScientificMetrics, 1000);
  
  console.log('📊 Metrics update loop started (1Hz)');
}

// Initialize on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initializeMetricsPanel();
    initializeInterpretationButton();
    
    // Wait for ZX engine to be ready, then start metrics
    const waitForEngine = setInterval(() => {
      if (window.zxEvolutionEngine) {
        clearInterval(waitForEngine);
        startMetricsUpdates();
      }
    }, 100);
  });
} else {
  initializeMetricsPanel();
  initializeInterpretationButton();
  
  if (window.zxEvolutionEngine) {
    startMetricsUpdates();
  } else {
    const waitForEngine = setInterval(() => {
      if (window.zxEvolutionEngine) {
        clearInterval(waitForEngine);
        startMetricsUpdates();
      }
    }, 100);
  }
}

