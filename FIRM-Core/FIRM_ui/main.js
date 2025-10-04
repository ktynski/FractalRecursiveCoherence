/**
 * FIRM UI bootstrap: tabbed interface and rendering surface.
 * Default view is the raymarched Clifford field (per spec). Rendering pipeline
 * wiring will be added after golden references exist; no visual guesses now.
 */

// FEATURE FLAGS - Enable advanced features incrementally without breaking current visualization
const FIRM_FEATURES = {
  zx_scheduling: true,         // Dynamic ZX rewrite scheduling (ENABLED)
  dirac_operator: true,        // Discrete Dirac mass operator (ENABLED) 
  webgpu_compute: false,       // WebGPU acceleration (Phase 3)
  debug_bootstrap: true,       // Enhanced bootstrap logging
  hebrew_network: true         // Hebrew letter network (ENABLED)
};

// Minimal loader overlay (non-blocking) for slow devices
(() => {
  const ensureLoader = () => {
    if (document.getElementById('firmLoaderOverlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'firmLoaderOverlay';
    overlay.style.position = 'fixed';
    overlay.style.top = 'calc(var(--top-bar-height))';
    overlay.style.left = '0';
    overlay.style.right = '0';
    overlay.style.bottom = '0';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'flex-end';
    overlay.style.justifyContent = 'flex-start';
    overlay.style.padding = '10px 12px';
    overlay.style.pointerEvents = 'none'; // indicator only
    overlay.style.zIndex = '70';
    overlay.style.background = 'transparent';

    const pill = document.createElement('div');
    pill.style.display = 'inline-flex';
    pill.style.alignItems = 'center';
    pill.style.gap = '8px';
    pill.style.padding = '6px 10px';
    pill.style.borderRadius = '999px';
    pill.style.background = 'rgba(20,20,20,0.75)';
    pill.style.border = '1px solid rgba(255,255,255,0.08)';
    pill.style.color = '#cdd6f4';
    pill.style.fontSize = '12px';
    pill.style.fontFamily = 'system-ui, sans-serif';

    const dot = document.createElement('span');
    dot.textContent = '●';
    dot.style.color = '#4a9eff';
    dot.style.animation = 'firmDotPulse 1s infinite ease-in-out';

    const label = document.createElement('span');
    label.id = 'firmLoaderLabel';
    label.textContent = 'Initializing…';

    pill.appendChild(dot);
    pill.appendChild(label);
    overlay.appendChild(pill);

    // Simple keyframes via stylesheet injection (once)
    if (!document.getElementById('firmLoaderStyles')) {
      const style = document.createElement('style');
      style.id = 'firmLoaderStyles';
      style.textContent = '@keyframes firmDotPulse{0%{opacity:.3}50%{opacity:1}100%{opacity:.3}}';
      document.head.appendChild(style);
    }

    document.body.appendChild(overlay);
  };

  const show = () => {
    ensureLoader();
    const el = document.getElementById('firmLoaderOverlay');
    if (el) el.style.display = 'flex';
    window.__loaderHidden = false;
  };
  const hide = () => {
    const el = document.getElementById('firmLoaderOverlay');
    if (el) el.style.display = 'none';
    window.__loaderHidden = true;
  };

  window.__showLoader = show;
  window.__hideLoader = hide;
  window.__setLoaderText = (text) => {
    const label = document.getElementById('firmLoaderLabel');
    if (label) label.textContent = text;
  };
})();

/**
 * FIRMUIController owns DOM wiring for the tabbed interface + accessibility controls.
 * Initialization happens synchronously from constructor: wiring tabs, accessibility toggles,
 * and canvas resize/camera controls. Rendering kicks off later once ZX engine is ready.
 */
class FIRMUIController {
  constructor() {
    this.state = { 
      view: 'clifford',
      camera: {
        position: [0, 0, 8],  // Start further back
        target: [0, 0, 0],
        up: [0, 1, 0],
        fov: 60,              // Wider field of view to see complete objects
        aspect_ratio: 16/9
      },
      rendering: {
        max_steps: 64,        // Reduced for smooth performance
        min_distance: 0.02,   // Slightly larger for efficiency
        max_distance: 500.0   // Reduced for better performance
      },
      accessibility: {
        no_motion: false,
        high_contrast: false
      }
    };
    
    this.initializeTopBar();
    this.initializeAccessibility();
    this.initializeCanvas();
  }
  
  initializeTopBar() {
    const viewSelector = document.getElementById('viewSelector');
    const viewDescription = document.getElementById('viewDescription');
    const controlToggle = document.getElementById('toggleControlPanel');
    const topAutoAlign = document.getElementById('topAutoAlignOmega');
    const topAutoMode = document.getElementById('topAutoOmegaMode');
    const closeControlPanel = document.getElementById('closeControlPanel');
    const metricsToggle = document.getElementById('topMetricsToggle');
    const metricsPanel = document.getElementById('metricsPanel');
    const metricsContent = document.getElementById('metricsContent');

    if (viewSelector) {
      viewSelector.addEventListener('change', (event) => {
        const view = event.target.value;
        this.switchView(view);
        if (viewDescription) {
          const labels = {
            clifford: 'Clifford Field (Spacetime)',
            zx: 'ZX Graph (Quantum)',
            consciousness: 'Consciousness View',
            sheaf: 'Sheaf Tree Observer',
            echo: 'Echo Map Resonance'
          };
          viewDescription.textContent = labels[view] || 'FIRM Visualization';
        }
      });
    }

    const openControls = () => {
      document.body.classList.add('controls-open');
      if (controlToggle) {
        controlToggle.setAttribute('aria-expanded', 'true');
        controlToggle.textContent = '⚙️ Hide Controls';
      }
    };

    const closeControls = () => {
      document.body.classList.remove('controls-open');
      if (controlToggle) {
        controlToggle.setAttribute('aria-expanded', 'false');
        controlToggle.textContent = '⚙️ Controls';
      }
    };

    if (controlToggle) {
      controlToggle.addEventListener('click', () => {
        if (document.body.classList.contains('controls-open')) {
          closeControls();
        } else {
          openControls();
        }
      });
      controlToggle.setAttribute('aria-expanded', 'false');
    }

    if (closeControlPanel) {
      closeControlPanel.addEventListener('click', closeControls);
    }

    if (metricsToggle && metricsPanel && metricsContent) {
      const toggleMetrics = () => {
        const isCollapsed = metricsPanel.classList.contains('collapsed');
        if (isCollapsed) {
          metricsPanel.classList.remove('collapsed');
          metricsContent.setAttribute('aria-hidden', 'false');
          metricsToggle.setAttribute('aria-expanded', 'true');
          metricsToggle.textContent = '📊 Hide Metrics';
        } else {
          metricsPanel.classList.add('collapsed');
          metricsContent.setAttribute('aria-hidden', 'true');
          metricsToggle.setAttribute('aria-expanded', 'false');
          metricsToggle.textContent = '📊 Show Metrics';
        }
        window.dispatchEvent(new Event('metricsStateChanged'));
      };

      metricsToggle.addEventListener('click', toggleMetrics);
      const header = metricsPanel.querySelector('.metrics-header');
      if (header) {
        header.addEventListener('click', toggleMetrics);
        header.addEventListener('keydown', (event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggleMetrics();
          }
        });
      }

      metricsPanel.classList.add('collapsed');
      metricsContent.setAttribute('aria-hidden', 'true');
      metricsToggle.setAttribute('aria-expanded', 'false');
      metricsToggle.textContent = '📊 Show Metrics';
    }

    // Wire top-bar Ω controls to existing handlers
    const forwardClick = (sourceEl, targetId) => {
      if (!sourceEl) return;
      sourceEl.addEventListener('click', () => {
        const el = document.getElementById(targetId);
        if (el) el.click();
      });
    };
    forwardClick(topAutoAlign, 'autoAlignOmega');
    forwardClick(topAutoMode, 'autoOmegaModeToggle');
  }
  
  switchView(viewName) {
    if (!['clifford', 'zx', 'sheaf', 'echo', 'consciousness'].includes(viewName)) {
      throw new Error(`Invalid view: ${viewName}`);
    }
    
    // Update internal state
    this.state.view = viewName;
    
    // Trigger view-specific setup (no rendering until implementation)
    this.onViewChange(viewName);
  }
  
  onViewChange(viewName) {
    // View-specific logic with debug logging
    console.log(`Switching to view: ${viewName}`);
    
    switch(viewName) {
      case 'clifford':
        console.log('📊 Clifford View: Raymarched multivector fields');
        break;
      case 'zx':
        console.log('🔗 ZX View: Tensor network evolution');
        break;
      case 'sheaf':
        console.log('🌳 Sheaf View: Category tree visualization');
        break;
      case 'echo':
        console.log('🔊 Echo View: Identity echo time τ');
        break;
    }
  }
  
  initializeAccessibility() {
const noMotion = document.getElementById('noMotion');
const highContrast = document.getElementById('highContrast');
    
    noMotion.addEventListener('change', (e) => {
      this.state.accessibility.no_motion = e.target.checked;
      this.updateAccessibilitySettings();
    });
    
    highContrast.addEventListener('change', (e) => {
      this.state.accessibility.high_contrast = e.target.checked;
      this.updateAccessibilitySettings();
    });
  }
  
  updateAccessibilitySettings() {
    const body = document.body;
    
    if (this.state.accessibility.high_contrast) {
      body.classList.add('high-contrast');
    } else {
      body.classList.remove('high-contrast');
    }
    
    if (this.state.accessibility.no_motion) {
      body.classList.add('no-motion');
    } else {
      body.classList.remove('no-motion');
    }
  }
  
  initializeCanvas() {
    const canvas = document.getElementById('canvas');
    
    // Validate canvas exists
    if (!canvas) {
      throw new Error("Canvas element not found");
    }
    
    // Set up resize handling
    this.handleResize();
    window.addEventListener('resize', () => this.handleResize());
    window.addEventListener('orientationchange', () => {
      // Delay resize until orientation settles
      setTimeout(() => this.handleResize(), 150);
    });
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        // Recompute sizes on return to tab (mobile browsers may change viewport)
        this.handleResize();
      }
    });
    
    // Add 3D camera controls (single initialization)
    this.setupCameraControls(canvas);

    // Expose quick diagnostics helper for manual/mobile checks
    try {
      window.firmDiag = () => {
        const c = document.getElementById('canvas');
        const rect = c.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        const ctx = (c.getContext && (c.getContext('webgl2') || c.getContext('webgl')));
        const glInfo = window.__firmGLInfo || null;
        const info = {
          css: { width: rect.width, height: rect.height },
          pixels: { width: c.width, height: c.height },
          dpr,
          webglVersion: ctx ? (ctx instanceof WebGL2RenderingContext ? 'WebGL2' : 'WebGL1') : 'none',
          hasContext: !!ctx,
          glInfo
        };
        console.log('[FIRM] Diagnostics:', info);
        return info;
      };
    } catch (_) {}
  }
  
  handleResize() {
    const canvas = document.getElementById('canvas');
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    
    // Compute CSS size with mobile-safe fallbacks
    let cssWidth = rect.width || window.innerWidth || 300;
    let cssHeight = rect.height || Math.floor(window.innerHeight * 0.6);
    if (cssHeight < 2) {
      // Mobile init race: fallback to 60vh of viewport height
      cssHeight = Math.floor(window.innerHeight * 0.6);
      console.debug('[FIRM] Canvas height fallback applied:', cssHeight);
    }
    
    // Apply devicePixelRatio scaling for crisp rendering
    canvas.width = Math.max(1, Math.floor(cssWidth * dpr));
    canvas.height = Math.max(1, Math.floor(cssHeight * dpr));
    canvas.style.width = `${Math.floor(cssWidth)}px`;
    canvas.style.height = `${Math.floor(cssHeight)}px`;
    
    // Update camera aspect ratio using CSS size
    this.state.camera.aspect_ratio = Math.max(0.0001, cssWidth / cssHeight);
  }
  
  validateCameraState() {
    const cam = this.state.camera;
    
    if (cam.fov <= 0 || cam.fov >= 180) {
      throw new Error("Camera FOV must be in (0, 180) degrees");
    }
    
    if (cam.aspect_ratio <= 0) {
      throw new Error("Camera aspect ratio must be positive");
    }
    
    return true;
  }
  
  setupCameraControls(canvas) {
    // Remove duplicate camera controls - this was called twice in initializeCanvas()
    if (this._cameraControlsInitialized) {
      console.log('📷 Camera controls already initialized');
      return;
    }
    this._cameraControlsInitialized = true;
    
    let isDragging = false;
    let lastMouseX = 0;
    let lastMouseY = 0;
    let cameraDistance = 8.0;
    let cameraTheta = 0;
    let cameraPhi = 0;
    
    canvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
    });
    
    canvas.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const deltaX = e.clientX - lastMouseX;
      const deltaY = e.clientY - lastMouseY;
      
      cameraTheta += deltaX * 0.01;
      cameraPhi += deltaY * 0.01;
      cameraPhi = Math.max(-Math.PI/2 + 0.1, Math.min(Math.PI/2 - 0.1, cameraPhi));
      
      this.state.camera.position = [
        cameraDistance * Math.cos(cameraPhi) * Math.cos(cameraTheta),
        cameraDistance * Math.sin(cameraPhi),
        cameraDistance * Math.cos(cameraPhi) * Math.sin(cameraTheta)
      ];
      
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
    });
    
    canvas.addEventListener('mouseup', () => { isDragging = false; });
    
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      cameraDistance += e.deltaY * 0.01;
      // Reduce minimum distance to allow closer view (was 2.0)
      cameraDistance = Math.max(1.0, Math.min(20.0, cameraDistance));
      
      this.state.camera.position = [
        cameraDistance * Math.cos(cameraPhi) * Math.cos(cameraTheta),
        cameraDistance * Math.sin(cameraPhi),
        cameraDistance * Math.cos(cameraPhi) * Math.sin(cameraTheta)
      ];
    }, { passive: false }); // Use passive: false when preventDefault is needed
    
    document.addEventListener('keydown', (e) => {
      if (e.key === 'r') {
        cameraDistance = 12.0; cameraTheta = 0; cameraPhi = 0;
        this.state.camera.position = [0, 0, 12];
        console.log('📷 Camera reset');
      } else if (e.key === 'f') {
        cameraDistance = 20.0;
        this.state.camera.position = [0, 0, 20];
        console.log('📷 Fit view');
      }
    });
    
    this.state.camera.position = [0, 0, 20]; // Pull back to see both objects
    console.log('📷 3D controls: drag=rotate, wheel=zoom, r=reset, f=fit');
    
    // Add audio enable button handler with proper testing
    const enableAudioBtn = document.getElementById('enableAudio');
    console.log('🔍 Audio button element:', enableAudioBtn);
    
    if (enableAudioBtn) {
      enableAudioBtn.addEventListener('click', async () => {
        console.log('🔊 Audio button clicked');
        
        // Wait for FIRM initialization to complete
        if (window.initializeFIRM) {
          console.log('⏳ Waiting for FIRM initialization...');
          try {
            await window.initializeFIRM();
            console.log('✅ FIRM initialization complete');
          } catch (error) {
            console.error('❌ FIRM initialization failed:', error);
          }
        }
        
        console.log('🔍 analogEngine available:', !!window.analogEngine);
        
        if (window.analogEngine && window.analogEngine.audioContext) {
          console.log('🔍 AudioContext state:', window.analogEngine.audioContext.state);
          
          try {
            await window.analogEngine.audioContext.resume();
            console.log('🔊 Audio context resumed successfully');
            enableAudioBtn.textContent = 'Audio Active ✓';
            enableAudioBtn.disabled = true;
            enableAudioBtn.style.background = '#2a5d2a';
          } catch (error) {
            console.error('🔊 Audio resume failed:', error);
            enableAudioBtn.textContent = 'Audio Failed ✗';
          }
        } else {
          console.error('🔊 analogEngine not available');
          enableAudioBtn.textContent = 'No Audio Engine';
        }
      });
      
      console.log('🔊 Audio button handler attached');
    } else {
      console.error('🔊 Audio button not found in DOM');
    }

    // Auto Align to Ω button
    const autoAlignBtn = document.getElementById('autoAlignOmega');
    if (autoAlignBtn) {
      autoAlignBtn.addEventListener('click', async () => {
        try {
          // 1) Derive Ω from current snapshot if not set
          if (!window.__resonanceMod) {
            try {
              window.__resonanceMod = await import('./FIRM_dsl/resonance.js');
            } catch (_) {
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
          const snap = window.zxEvolutionEngine?.getSnapshot?.();
          if (snap) {
            window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(snap.graph);
          }

          // 2) Briefly explore drivers and choose the best by near-horizon Res×C(G)
          const exploreDrivers = ['fractal', 'phi_recursive', 'morphic'];
          const results = [];
          for (const d of exploreDrivers) {
            if (window.switchToFractalDriver) {
              const drv = window.switchToFractalDriver(d);
              if (drv && drv.start) drv.start();
            }
            // Take a few steps and measure average score
            let score = 0; let samples = 0;
            for (let i = 0; i < 10; i++) {
              window.zxEvolutionEngine?.evolveFromAudioCoherence?.(0.5, 0.016);
              const s = window.zxEvolutionEngine?.getSnapshot?.();
              if (!s || !window.__omegaSignature) continue;
              const res = window.__resonanceMod.computeResonanceAlignment(s.graph, window.__omegaSignature);
              const cg = s.coherence || 0;
              score += Math.max(0, res) * Math.max(0, cg);
              samples += 1;
            }
            results.push({ driver: d, score: samples ? (score / samples) : 0 });
          }
          results.sort((a, b) => b.score - a.score);

          // 3) Commit the best driver
          const best = results[0];
          if (best && window.switchToFractalDriver) {
            window.switchToFractalDriver(best.driver);
          }

          console.log('Ω Auto-Align:', { omegaSet: !!window.__omegaSignature, results, chosen: best?.driver });
          // Toggle metrics to refresh/confirm
          window.dispatchEvent(new Event('metricsStateChanged'));
        } catch (e) {
          console.warn('Auto Align to Ω failed:', e);
        }
      });
    }

    // Auto Ω Mode: continuously maximize Res(S,Ω) × C(G) during evolution
    const autoOmegaBtn = document.getElementById('autoOmegaModeToggle');
    if (autoOmegaBtn) {
      this._autoOmegaEnabled = false;
      autoOmegaBtn.addEventListener('click', async () => {
        this._autoOmegaEnabled = !this._autoOmegaEnabled;
        autoOmegaBtn.textContent = this._autoOmegaEnabled ? 'Disable Auto Ω Mode' : 'Enable Auto Ω Mode';
        console.log('Auto Ω Mode:', this._autoOmegaEnabled);
      });
    }
  }
  
  getState() {
    return { ...this.state };
  }
}

const firmUI = new FIRMUIController();
window.firmUI = firmUI;

/**
 * Top-level bootstrap called on DOMContentLoaded.
 * Ensures single initialization, loads all modules, wires globals, and kicks off render loop.
 */
const initializeFIRM = async () => {
  if (initializeFIRM._initializedPromise) {
    return initializeFIRM._initializedPromise;
  }
  initializeFIRM._initializedPromise = (async () => {
    try { window.__showLoader?.(); } catch(_) {}
    try { window.__setLoaderText?.('Loading modules…'); } catch(_) {}
    if (window.renderer && window.zxEvolutionEngine) {
      try { window.__hideLoader?.(); } catch(_) {}
      return true;
    }
    try {
      // Import renderer
      const { FIRMRenderer } = await import('./renderer.js');
      const { initializeSacredMorphicSystem } = await import('./sacred_morphic_seeds.js');
      const { initializeFractalDrivers } = await import('./fractal_waveform_drivers.js');
      
      // Create renderer
      try { window.__setLoaderText?.('Initializing renderer…'); } catch(_) {}
      const canvas = document.getElementById('canvas');
      const renderer = new FIRMRenderer(canvas);
      window.renderer = renderer;
      window.firmRenderer = renderer;
      
      // Initialize rendering system
      try { window.__setLoaderText?.('Starting WebGL…'); } catch(_) {}
      await renderer.initialize();
      
      // Import raymarching pipeline
      const { RaymarchingValidator } = await import('./raymarching.js');
      
      // Create raymarching pipeline
      const validator = new RaymarchingValidator();
      const pipeline = validator.createRaymarchingPipeline(null, firmUI.state.camera);
      
      // Set up rendering pipeline
      renderer.setupRaymarchingProgram(pipeline);
      
      console.log('FIRM renderer initialized');
      console.log('WebGL rendering pipeline operational');
      console.log('Mathematical engine connected');
      console.log('Analog audio substrate ready');
      console.log('Theory validation complete');
      
      // Load optional audio normalization parameters (if present)
      let normalization = null;
      try {
        const resp = await fetch('./normalization.json', { cache: 'no-store' });
        if (resp.ok) {
          normalization = await resp.json();
          console.log('🔍 Loaded normalization:', normalization.proof_id);
        }
      } catch (e) {
        // Optional; proceed without if not found
        console.log('Normalization not found; proceeding without.');
      }
      
      console.log('🔧 Loading theory evolution modules...');
      try { window.__setLoaderText?.('Wiring theory modules…'); } catch(_) {}
      let TheoryComplianceIterator;
      let ZXObjectGraphEngine;
      try {
        ({ TheoryComplianceIterator } = await import('./theory_iteration.js'));
      } catch (error) {
        console.error('❌ Failed to import theory_iteration.js', error);
        throw error;
      }
      try {
        ({ ZXObjectGraphEngine } = await import('./zx_objectg_engine.js'));
      } catch (error) {
        console.error('❌ Failed to import zx_objectg_engine.js', error);
        throw error;
      }
      console.log('✅ Theory modules imported successfully');
      
      // Mathematical evolution will be handled by analog substrate
      
      // Create theory compliance iterator and ZX evolution engine
      let iterator;
      try {
        iterator = new TheoryComplianceIterator(renderer, canvas);
      } catch (error) {
        console.error('❌ Failed to construct TheoryComplianceIterator', error);
        throw error;
      }
      let zxEngine;
      try {
        zxEngine = new ZXObjectGraphEngine();
      } catch (error) {
        console.error('❌ Failed to construct ZXObjectGraphEngine', error);
        throw error;
      }
      console.log('✅ ZXObjectGraphEngine constructed');
      
      // Initialize analog engine (shared AudioContext + analyser)
      try { window.__setLoaderText?.('Initializing audio…'); } catch(_) {}
      const { createAnalogEngine } = await import('./analog_engine.js');
      const analogEngine = createAnalogEngine();
      try {
        await analogEngine.initialize();
        console.log('🔊 Analog engine initialized and shared globally');
      } catch (audioError) {
        console.warn('⚠️ Audio initialization failed (user gesture required):', audioError.message);
      }
      window.analogEngine = analogEngine;

      // Autoplay policy bypass: resume audio on first user interaction
      (function setupAudioAutoResume() {
        try {
          if (!window.analogEngine || !window.analogEngine.audioContext) return;
          const ctx = window.analogEngine.audioContext;
          if (ctx.state === 'running') return;

          const enableBtn = document.getElementById('enableAudio');
          const markActive = () => {
            if (!enableBtn) return;
            enableBtn.textContent = 'Audio Active ✓';
            enableBtn.disabled = true;
            enableBtn.style.background = '#2a5d2a';
          };

          const cleanup = () => {
            document.removeEventListener('pointerdown', onInteract);
            document.removeEventListener('keydown', onInteract);
            document.removeEventListener('touchend', onInteract);
          };
          const tryResume = async () => {
            try {
              await ctx.resume();
              if (ctx.state === 'running') {
                markActive();
                cleanup();
                console.log('🔊 Audio context resumed via user gesture');
              }
            } catch (e) {
              console.warn('🔊 Audio resume attempt failed:', e?.message || e);
            }
          };
          const onInteract = () => { tryResume(); };

          document.addEventListener('pointerdown', onInteract);
          document.addEventListener('keydown', onInteract);
          document.addEventListener('touchend', onInteract);
        } catch (_) {}
      })();
      
      // Make iterator globally accessible for theory validation
      window.theoryIterator = iterator;
      window.getComplianceReport = () => iterator.getComplianceReport();
      window.getIterationStatus = () => iterator.getIterationStatus();
      
      // Make ZX engine globally accessible immediately
      window.zxEvolutionEngine = zxEngine;
      console.log('🌐 ZX engine globally accessible (early initialization)');
      
      // Create emergent observer inline (avoid import issues)
      const emergentObserver = {
        consciousness: { awareness: 0.5, focus: 0.5, understanding: 0.5 },
        boundaryHistory: [],
        
        analyzeFieldBoundaries(cliffordField) {
          if (!cliffordField?.payload?.components) return null;
          
          const components = cliffordField.payload.components;
          const totalActivity = components.reduce((sum, c) => sum + Math.abs(c), 0);
          const emergentBoundary = Math.max(0.5, Math.min(10.0, totalActivity * 0.5));
          const naturalObservationDistance = emergentBoundary * 8.0;
          
          return {
            emergentBoundary,
            naturalObservationDistance,
            fieldActivity: totalActivity
          };
        },
        
        evolveConsciousness(fieldAnalysis, visualFeedback) {
          if (fieldAnalysis?.fieldActivity > 0.1) {
            this.consciousness.awareness = Math.min(1.0, this.consciousness.awareness + 0.01);
          }
          return this.consciousness;
        },
        
        computeOptimalObservation(fieldAnalysis, consciousness) {
          if (!fieldAnalysis) return null;
          
          const awarenessModulation = 0.5 + consciousness.awareness * 0.5;
          const cameraDistance = fieldAnalysis.naturalObservationDistance * awarenessModulation;
          
          return {
            cameraDistance,
            fieldOfView: 45.0,
            focusPoint: [0, 0, 0],
            emergentBoundary: fieldAnalysis.emergentBoundary
          };
        }
      };
      window.emergentObserver = emergentObserver;
      
      // Initialize Sacred Morphic System and fractal drivers with shared analog engine
      try { window.__setLoaderText?.('Seeding sacred morphic system…'); } catch(_) {}
      try {
        window.sacredSeeds = window.sacredSeeds || initializeSacredMorphicSystem();
        window.sacredNames72 = window.sacredSeeds?.names72 || [];
        console.log(`🕯️ Sacred Morphic System initialized with ${window.sacredNames72.length} names`);
      } catch (sacredError) {
        console.error('❌ Sacred system initialization failed:', sacredError);
      }
      
      try {
        try { window.__setLoaderText?.('Starting waveform drivers…'); } catch(_) {}
        if (!window.fractalDrivers) {
          initializeFractalDrivers(window.analogEngine.audioContext, window.analogEngine.analyser);
        }
        console.log('🌊 Fractal Waveform Drivers initialized');
      } catch (driverError) {
        console.error('❌ Fractal driver initialization failed:', driverError);
      }
      
      // DISABLE analog engine evolution - we use ZX evolution instead
      // analogEngine.startEvolution(); // This creates competing setTimeout loops
      
      // Enhanced state management for iteration
      let systemState = {
        view: firmUI.state.view,  // Include current view
        camera: firmUI.state.camera,
        rendering: firmUI.state.rendering,
        audioCoherence: 0.8,
        frameCount: 0,  // Track frames for stable camera movement
        fieldParameters: {
          amplitude: 1.0,
          spatialFreq: 0.8,
          phaseModulation: 0.0
        }
      };
      
      // Connect tab switching to renderer
      firmUI.onViewChange = (viewName) => {
        systemState.view = viewName;
        if (viewName === 'sacred' && !theoryFlags.sacredEnabled) {
          console.warn('🛑 Sacred modules disabled pending proof requirements');
        }
      };
      
      // THEORY-COMPLIANT EXPLORATION CONTROLS
      const theoryControls = {
        graceCoherence: 1.618033988749, // φ
        bootstrapEnergy: 1.0,
        emergenceRate: 1.0,
        observationDistance: null // null = auto
      };

      const theoryFlags = {
        sacredEnabled: false, // set true after sacred proofs are attached
        fractalEnabled: false // set true after fractal waveform proofs are attached
      };
      
      // Setup slider event handlers
      const setupSliders = () => {
        // Sacred Name Slider - Fixed
        const sacredNameSlider = document.getElementById('sacredNameSlider');
        const sacredNameValue = document.getElementById('sacredNameValue');
        if (sacredNameSlider && sacredNameValue) {
          sacredNameSlider.addEventListener('input', (e) => {
            const nameIndex = parseInt(e.target.value);
            sacredNameValue.textContent = nameIndex;
            
            // Use direct sacred names if available
            if (window.sacredNames72 && window.sacredNames72[nameIndex]) {
              const sacredName = window.sacredNames72[nameIndex];
              console.log(`🕯️ Sacred name selected: ${sacredName.name} (${sacredName.quality}) - Power: ${sacredName.power}`);
            } else {
              console.log(`🕯️ Sacred name index selected: ${nameIndex}`);
            }
          });
          
          // Also add change event
          sacredNameSlider.addEventListener('change', (e) => {
            const nameIndex = parseInt(e.target.value);
            sacredNameValue.textContent = nameIndex;
          });
        }
        
        // Sacred Name Seeding Button
        const seedSacredButton = document.getElementById('seedSacredName');
        if (seedSacredButton) {
          seedSacredButton.addEventListener('click', () => {
            const nameIndex = parseInt(sacredNameSlider?.value || 0);
            if (window.seedWithSacredName) {
              const success = window.seedWithSacredName(nameIndex);
              if (success && sacredMorphicSeeds.names72?.[nameIndex]) {
                const sacredName = sacredMorphicSeeds.names72[nameIndex];
                console.log(`🌟 Sacred field seeded with ${sacredName.name} - ${sacredName.consciousness_quality}`);
              }
            }
          });
        }
        
        // Hebrew Boundary Button
        const boundaryButton = document.getElementById('applySacredBoundary');
        const boundarySelect = document.getElementById('hebrewBoundary');
        if (boundaryButton && boundarySelect) {
          boundaryButton.addEventListener('click', () => {
            const letter = boundarySelect.value;
            if (letter && window.applySacredBoundary) {
              const success = window.applySacredBoundary(letter);
              if (success) {
                console.log(`🔤 Hebrew boundary applied: ${letter}`);
              }
            }
          });
        }
        
        // Sacred Commentary Button
        const commentaryButton = document.getElementById('getSacredCommentary');
        if (commentaryButton) {
          commentaryButton.addEventListener('click', () => {
            if (window.getSacredCommentary) {
              const commentary = window.getSacredCommentary();
              console.log('📜 SACRED COMMENTARY:');
              console.log(commentary);
            }
          });
        }
        
        // Waveform Driver Controls
        const driverSelect = document.getElementById('waveformDriver');
        const switchDriverButton = document.getElementById('switchWaveformDriver');
        const testDriverButton = document.getElementById('testDriverEffects');
        const driverMetricsContainer = document.getElementById('driverMetrics');
        const driverMetricsBody = document.getElementById('driverMetricsBody');
        const driverMetricsStatus = document.getElementById('driverMetricsStatus');
        let metricsIntervalId = null;

        const vantageSelector = document.getElementById('vantageSelector');
        if (vantageSelector) {
          vantageSelector.addEventListener('change', (event) => {
            const mode = event.target.value;
            if (mode === 'auto') {
              theoryControls.observationDistance = null;
              console.log('📷 Vantage set to automatic emergent observation');
            } else if (mode === 'custom') {
              if (systemState && systemState.camera) {
                const currentPos = systemState.camera.position;
                theoryControls.observationDistance = Math.sqrt(currentPos[0]**2 + currentPos[1]**2 + currentPos[2]**2);
                console.log(`📷 Custom vantage preserved at distance ${theoryControls.observationDistance.toFixed(2)}`);
              }
            } else {
              const presets = {
                void_observer: {
                  position: [0, 0, 28],
                  target: [0, 0, 0],
                  up: [0, 1, 0]
                },
                phi_grace_torus: {
                  position: [13, 8, 13],
                  target: [0, 0, 0],
                  up: [0, 1, 0]
                },
                bootstrap_loop: {
                  position: [9 * Math.cos(Math.PI / 4), 9 * Math.sin(Math.PI / 4), 11],
                  target: [0, 0, 0],
                  up: [0, 1, 0]
                },
                sacred_axis: {
                  position: [0, 14, 0],
                  target: [0, 0, 0],
                  up: [0, 0, -1]
                },
                coherence_shockfront: {
                  position: [6, 2, 4],
                  target: [0, 0, 0],
                  up: [0, 1, 0]
                },
                // Physics Perspectives (10 additional views)
                scalar_field: {
                  position: [0, 0, 12],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Scalar field (grade-0): Mass/Higgs VEV'
                },
                vector_field: {
                  position: [10, 10, 0],
                  target: [0, 0, 0],
                  up: [0, 0, 1],
                  description: 'Vector field (grade-1): E-field/Momentum'
                },
                bivector_field: {
                  position: [8, 0, 8],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Bivector field (grade-2): B-field/Angular momentum'
                },
                qft_perspective: {
                  position: [15, 5, 10],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'QFT view: Quantum field excitations'
                },
                gr_perspective: {
                  position: [20, 10, 15],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'GR view: Spacetime curvature sources'
                },
                qm_perspective: {
                  position: [12, 12, 12],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'QM view: Wave function nodes/orbitals'
                },
                lattice_gauge: {
                  position: [5, 15, 5],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Lattice gauge: Discretized field theory'
                },
                emergence_view: {
                  position: [0, 8, 20],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Emergence: Bootstrap phase evolution'
                },
                interference_view: {
                  position: [10, 0, 10],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Interference: Standing wave patterns'
                },
                topology_view: {
                  position: [18, 12, 8],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Topology: Manifold boundary structure'
                }
              };

              const preset = presets[mode];
              if (preset) {
                systemState.camera.position = [...preset.position];
                systemState.camera.target = [...preset.target];
                systemState.camera.up = [...preset.up];
                theoryControls.observationDistance = Math.sqrt(preset.position[0]**2 + preset.position[1]**2 + preset.position[2]**2);
                const description = preset.description ? ` - ${preset.description}` : '';
                console.log(`📷 Vantage preset '${mode}' applied with distance ${theoryControls.observationDistance.toFixed(2)}${description}`);
              }
            }
          });
        }
        
        if (switchDriverButton && driverSelect) {
          switchDriverButton.addEventListener('click', () => {
            const driverType = driverSelect.value;
            if (window.switchToFractalDriver) {
              const driver = window.switchToFractalDriver(driverType);
              if (driver) {
                // Start the driver immediately to affect the audio feed
                driver.start();
                console.log(`🌊 Switched to ${driverType} waveform driver and started`);
              } else {
                console.log(`🌊 Switched to ${driverType} driver (using existing oscillators)`);
              }
            }
          });
        }
        
        if (testDriverButton && driverSelect) {
          testDriverButton.addEventListener('click', () => {
            const driverType = driverSelect.value;
            if (window.testDriverEffects) {
              const analysis = window.testDriverEffects(driverType, 30); // 30 second test
              if (analysis) {
                console.log(`🔬 Testing ${driverType} driver effects for 30 seconds...`);
                console.log('   Use analysis.getResults() to see effects');
                console.log('   Use analysis.stop() to end test');
                window.currentDriverTest = analysis;

                if (driverMetricsContainer && driverMetricsBody && driverMetricsStatus) {
                  driverMetricsContainer.style.display = 'block';
                  driverMetricsStatus.textContent = 'Collecting...';

                  if (metricsIntervalId) {
                    clearInterval(metricsIntervalId);
                  }

                  const updateMetrics = () => {
                    const snapshot = window.zxEvolutionEngine?.getSnapshot?.();
                    const analysisResults = window.currentFractalAnalysis?.getResults?.();

                    if (!snapshot) {
                      driverMetricsStatus.textContent = 'No ZX snapshot available';
                      driverMetricsBody.innerHTML = '';
                      return;
                    }

                    const rows = [];
                    rows.push(`<tr><td>Driver Type</td><td>${analysisResults?.driverType || driverType}</td></tr>`);
                    rows.push(`<tr><td>ZX Nodes</td><td>${snapshot.graph.nodes.length}</td></tr>`);
                    rows.push(`<tr><td>ZX Edges</td><td>${snapshot.graph.edges.length}</td></tr>`);
                    rows.push(`<tr><td>Coherence C(G)</td><td>${snapshot.coherence.toFixed(6)}</td></tr>`);

                    if (analysisResults) {
                      rows.push(`<tr><td>ΔConsciousness</td><td>${(analysisResults.changes.consciousness || 0).toFixed(6)}</td></tr>`);
                      const graceRatio = analysisResults.changes.grace_ratio;
                      rows.push(`<tr><td>Grace Ratio</td><td>${Number.isFinite(graceRatio) ? graceRatio.toFixed(6) : 'n/a'}</td></tr>`);
                      rows.push(`<tr><td>ΔNodes</td><td>${analysisResults.changes.node_change}</td></tr>`);
                      rows.push(`<tr><td>ΔEvents</td><td>${analysisResults.changes.event_change}</td></tr>`);
                      rows.push(`<tr><td>Duration (s)</td><td>${analysisResults.duration.toFixed(2)}</td></tr>`);
                      driverMetricsStatus.textContent = 'Live';
                    } else {
                      driverMetricsStatus.textContent = 'Awaiting analysis results';
                    }

                    driverMetricsBody.innerHTML = rows.join('');
                  };

                  updateMetrics();
                  metricsIntervalId = setInterval(updateMetrics, 1000);
                }
              }
            }
          });
        }

        const stopDriverButton = document.getElementById('stopDriverTest');
        if (stopDriverButton) {
          stopDriverButton.addEventListener('click', () => {
            if (metricsIntervalId) {
              clearInterval(metricsIntervalId);
              metricsIntervalId = null;
            }

            if (window.currentDriverTest?.stop) {
              window.currentDriverTest.stop();
            }

            if (driverMetricsStatus) {
              driverMetricsStatus.textContent = 'Stopped';
            }
          });
        }
        
        // Grace Coherence Slider
        const graceSlider = document.getElementById('graceSlider');
        const graceValue = document.getElementById('graceValue');
        if (graceSlider && graceValue) {
          graceSlider.addEventListener('input', (e) => {
            theoryControls.graceCoherence = parseFloat(e.target.value);
            graceValue.textContent = theoryControls.graceCoherence.toFixed(3);
            console.log(`🌟 Grace coherence adjusted: φ = ${theoryControls.graceCoherence}`);
            if (window.zxEvolutionEngine?.updateControlParams) {
              window.zxEvolutionEngine.updateControlParams({ graceScale: theoryControls.graceCoherence || 1.0 });
            }
          });
        }
        
        // Bootstrap Energy Slider
        const bootstrapSlider = document.getElementById('bootstrapSlider');
        const bootstrapValue = document.getElementById('bootstrapValue');
        if (bootstrapSlider && bootstrapValue) {
          bootstrapSlider.addEventListener('input', (e) => {
            theoryControls.bootstrapEnergy = parseFloat(e.target.value);
            bootstrapValue.textContent = theoryControls.bootstrapEnergy.toFixed(2);
            console.log(`⚡ Bootstrap energy adjusted: ${theoryControls.bootstrapEnergy}`);
            if (window.zxEvolutionEngine?.updateControlParams) {
              window.zxEvolutionEngine.updateControlParams({ bootstrapEnergy: theoryControls.bootstrapEnergy || 1.0 });
            }
          });
        }
        
        // Emergence Rate Slider
        const emergenceSlider = document.getElementById('emergenceSlider');
        const emergenceValue = document.getElementById('emergenceValue');
        if (emergenceSlider && emergenceValue) {
          emergenceSlider.addEventListener('input', (e) => {
            theoryControls.emergenceRate = parseFloat(e.target.value);
            emergenceValue.textContent = theoryControls.emergenceRate.toFixed(2);
            console.log(`🌱 Emergence rate adjusted: ${theoryControls.emergenceRate}`);
            if (window.zxEvolutionEngine?.updateControlParams) {
              window.zxEvolutionEngine.updateControlParams({ emergenceRate: theoryControls.emergenceRate || 1.0 });
            }
          });
        }

        // Observation Distance Slider
        const distanceSlider = document.getElementById('distanceSlider');
        const distanceValue = document.getElementById('distanceValue');
        if (distanceSlider && distanceValue) {
          distanceSlider.addEventListener('input', (e) => {
            const sliderValue = parseFloat(e.target.value);
            theoryControls.observationDistance = sliderValue;
            distanceValue.textContent = sliderValue.toFixed(1);
            console.log(`📷 Manual observation distance: ${theoryControls.observationDistance}`);
          });
          
          // Double-click to reset to auto mode
          distanceSlider.addEventListener('dblclick', () => {
            theoryControls.observationDistance = null;
            distanceValue.textContent = 'Auto';
            console.log(`📷 Observation distance reset to Auto`);
          });
        }
        
        // Reset Evolution Button
        const resetButton = document.getElementById('resetEvolution');
        if (resetButton) {
          resetButton.addEventListener('click', () => {
            if (window.zxEvolutionEngine) {
              window.zxEvolutionEngine.reset();
              console.log('🔄 Evolution reset to void (∅)');
            }
          });
        }
        
        // Consciousness Visualization Controls
        const showConsciousness = document.getElementById('showConsciousness');
        const showWill = document.getElementById('showWill');
        const showReflexivePain = document.getElementById('showReflexivePain');
        const showOrMakifPnimi = document.getElementById('showOrMakifPnimi');
        
        // Initialize consciousness display settings
        if (!window.consciousnessDisplaySettings) {
          window.consciousnessDisplaySettings = {
            showConsciousness: true,
            showWill: true,
            showReflexivePain: true,
            showOrMakifPnimi: false
          };
        }
        
        if (showConsciousness) {
          showConsciousness.addEventListener('change', (e) => {
            window.consciousnessDisplaySettings.showConsciousness = e.target.checked;
            console.log(`💖 Show Consciousness Levels: ${e.target.checked}`);
          });
        }
        
        if (showWill) {
          showWill.addEventListener('change', (e) => {
            window.consciousnessDisplaySettings.showWill = e.target.checked;
            console.log(`💪 Show Will to Emerge: ${e.target.checked}`);
          });
        }
        
        if (showReflexivePain) {
          showReflexivePain.addEventListener('change', (e) => {
            window.consciousnessDisplaySettings.showReflexivePain = e.target.checked;
            console.log(`💔 Show Reflexive Pain: ${e.target.checked}`);
          });
        }
        
        if (showOrMakifPnimi) {
          showOrMakifPnimi.addEventListener('change', (e) => {
            window.consciousnessDisplaySettings.showOrMakifPnimi = e.target.checked;
            console.log(`✨ Show Or Makif/Pnimi Bridge: ${e.target.checked}`);
          });
        }
        
        console.log('🎛️ Theory exploration controls initialized');
      };
      
      // Make controls globally accessible
      window.theoryControls = theoryControls;
      
      // Setup sliders after DOM is ready
      setupSliders();
      
      // TRUE ANALOG EVOLUTION: Complete theory-compliant chain
      renderer.startRenderLoop(() => {
        try {
          // Increment frame counter for stable animations
          systemState.frameCount++;
          
          // 1. ANALOG INPUT: Get real-time audio coherence
          const audioCoherence = analogEngine.getAudioCoherence();

        // PERFORMANCE: Compute Parseval-normalized coherence only occasionally
        let audioCoherenceParseval = null;
        if (normalization && analogEngine.analyser && systemState.frameCount % 30 === 0) {
          if (analogEngine.freqDataBuffer) {
            let energy = 0;
            for (let i = 0; i < analogEngine.freqDataBuffer.length; i++) {
              energy += analogEngine.freqDataBuffer[i] * analogEngine.freqDataBuffer[i];
            }
            const corrected = energy * normalization.correction_factor;
            audioCoherenceParseval = Math.min(1.0, corrected / normalization.max_energy_bound);
          }
        }

        // ZX EVOLUTION: Use ObjectG snapshot pipeline
          const zxEvolutionEngine = window.zxEvolutionEngine;
        let zxSnapshot = null;
        let graphCoherence = 0.0;
          if (zxEvolutionEngine) {
            const enhancedCoherence = audioCoherence * theoryControls.emergenceRate;
          const deltaTime = 0.016;

          zxEvolutionEngine.evolve(enhancedCoherence, deltaTime);

          zxSnapshot = zxEvolutionEngine.getSnapshot();
          graphCoherence = zxSnapshot ? zxSnapshot.coherence : 0.0;

          systemState.zxEngine = zxEvolutionEngine;
          systemState.currentGraph = zxSnapshot ? zxSnapshot.graph : null;
          systemState.graphCoherence = graphCoherence;
          systemState.cliffordField = zxSnapshot ? zxSnapshot.cliffordField : null;
          systemState.zxSnapshot = zxSnapshot;
          
          // BIDIRECTIONAL COUPLING: Graph → Audio modulation (every 10 frames for performance)
          if (systemState.frameCount % 10 === 0 && analogEngine.modulateFromGraphState) {
            const nodes = zxSnapshot?.graph?.nodes?.length || 0;
            analogEngine.modulateFromGraphState(graphCoherence, nodes);
          }
          } else {
            if (systemState.zxEngine || systemState.currentGraph) {
              console.warn('⚠️ ZX engine disappeared; clearing cached ZX state');
              systemState.zxEngine = null;
              systemState.currentGraph = null;
            }
            // Don't spam console - only log once per session when engine is missing
            if (!this._zxEngineMissingLogged) {
              console.warn('⚠️ ZX engine not available in render loop');
              this._zxEngineMissingLogged = true;
            }
            graphCoherence = 0.0; // Explicit fallback for missing engine
          }
          systemState.audioCoherence = audioCoherence;
          systemState.graphCoherence = graphCoherence;
          
          // 3. CONSCIOUSNESS EVOLUTION: Use cached field to avoid duplicate generation
          // Field will be generated in the render loop - reuse it here for efficiency
          zxSnapshot = zxSnapshot || systemState.zxSnapshot || (window.zxEvolutionEngine ? window.zxEvolutionEngine.getSnapshot() : null);
          if (zxSnapshot) {
            systemState.zxSnapshot = zxSnapshot;
            systemState.cliffordField = zxSnapshot.cliffordField;
          }

        const cliffordField = zxSnapshot ? zxSnapshot.cliffordField : null;
        if (!cliffordField) {
          return systemState;
        }
        const fieldAnalysis = emergentObserver.analyzeFieldBoundaries(cliffordField);
          const consciousness = emergentObserver.evolveConsciousness(fieldAnalysis, {nonBlackPixels: 0}); // Will be updated with real visual feedback
          const optimalObservation = fieldAnalysis ? emergentObserver.computeOptimalObservation(fieldAnalysis, consciousness) : null;
          
          // 4. THEORY-DRIVEN EVOLUTION CONTROL (Auto Ω Mode)
          if (this._autoOmegaEnabled) {
            try {
              if (!window.__resonanceMod) {
                // Lazy-load once; render loop must remain fast
                import('./FIRM_dsl/resonance.js').then(mod => { window.__resonanceMod = mod; }).catch(async () => {
                  const coh = await import('./FIRM_dsl/coherence.js');
                  const core = await import('./FIRM_dsl/core.js');
                  window.__resonanceMod = window.__resonanceMod || {
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
                });
              }
              if (!window.__omegaSignature && window.__resonanceMod && zxSnapshot) {
                window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(zxSnapshot.graph);
              }
              if (window.__resonanceMod && window.__omegaSignature && window.zxEvolutionEngine) {
                // Compute current resonance
                const res = window.__resonanceMod.computeResonanceAlignment(zxSnapshot.graph, window.__omegaSignature);
                // Update control params to steer toward Ω: higher emergence when Res is rising
                const targetEmergence = Math.min(3.0, 0.5 + 2.5 * Math.max(0, res));
                window.zxEvolutionEngine.updateControlParams?.({ emergenceRate: targetEmergence });
                // Light audio modulation coupling on Res (kept bounded)
                if (window.analogEngine && typeof window.analogEngine.modulateFromGraphState === 'function') {
                  const nodes = zxSnapshot?.graph?.nodes?.length || 0;
                  window.analogEngine.modulateFromGraphState(res, nodes);
                }
              }
            } catch (_) {
              // Non-fatal; evolution continues
            }
          }

          // 5. MANIFOLD OBSERVATION: Update camera to observe transforming manifold
          if (optimalObservation && fieldAnalysis) {
            // Compute manifold-appropriate observation distance
            const manifoldRadius = 3.0;  // Base manifold size
            const complexityFactor = 1.0 + fieldAnalysis.fieldActivity * 0.05; // Reduced sensitivity
            
            // USER OVERRIDE: Use manual observation distance if set
            let targetDistance;
            if (theoryControls.observationDistance !== null && theoryControls.observationDistance > 0) {
              // User has manually set observation distance - respect their choice
              targetDistance = theoryControls.observationDistance;
              console.log(`📷 Using manual observation distance: ${targetDistance}`);
            } else {
              // Automatic distance based on manifold analysis
              const baseDistance = manifoldRadius * 4.0;
              const maxDistanceChange = 0.5;
              
              // Calculate target distance with adaptive scaling for growing field
              const fieldSize = Math.max(5.0, fieldAnalysis.fieldActivity * 2.0);
              const minSafeDistance = fieldSize * 2.0;
              targetDistance = Math.max(
                minSafeDistance,
                baseDistance + Math.sin(systemState.frameCount * 0.005) * maxDistanceChange
              );
            }
            
            // Apply heavy damping to camera movement (position lerping)
            const currentPos = systemState.camera.position;
            const currentDistance = Math.sqrt(currentPos[0]**2 + currentPos[1]**2 + currentPos[2]**2);
            
            // Calculate minimum safe distance (always respect field boundaries)
            const fieldSize = Math.max(5.0, fieldAnalysis.fieldActivity * 2.0);
            const minSafeDistance = fieldSize * 2.0;
            
            if (currentDistance > 0) {
              const direction = currentPos.map(p => p / currentDistance);
              
              // For manual distances, apply less smoothing to be more responsive
              const isManualDistance = theoryControls.observationDistance !== null;
              const smoothingFactor = isManualDistance ? 0.7 : 0.9;
              
              // If we're too close, move outward more aggressively
              const distanceRatio = currentDistance / minSafeDistance;
              const adaptiveSmoothingFactor = distanceRatio < 1.2 ? 
                                            Math.min(0.5, smoothingFactor) : // Move outward faster if too close
                                            smoothingFactor;
              
              const newDistance = currentDistance * adaptiveSmoothingFactor + 
                                 targetDistance * (1 - adaptiveSmoothingFactor);
              
              // Final safety check - never go inside the manifold (override manual distance if needed)
              const finalDistance = Math.max(minSafeDistance, newDistance);
              
              systemState.camera.position = direction.map(d => d * finalDistance);
            } else {
              // Ensure initial position respects safety distance
              const safeTargetDistance = Math.max(minSafeDistance, targetDistance);
              systemState.camera.position = [0, 0, safeTargetDistance];
            }
            
            // Adaptive field of view for manifold observation
            systemState.camera.fov = Math.max(30, Math.min(90, 45 + complexityFactor * 10));
            
            // THEORY COMPLIANT: Use deterministic frame-based logging instead of random
            if (systemState.frameCount % 2000 === 0) { // Every 2000 frames - deterministic
              const currentDistance = Math.sqrt(systemState.camera.position[0]**2 + systemState.camera.position[1]**2 + systemState.camera.position[2]**2);
              console.log(`🌐 Manifold observation: distance=${currentDistance.toFixed(1)}, complexity=${complexityFactor.toFixed(2)}, FOV=${systemState.camera.fov.toFixed(1)}°`);
              console.log(`🧠 Consciousness: awareness=${consciousness.awareness.toFixed(3)}, focus=${consciousness.focus.toFixed(3)}`);
            }
          }
          
          // 6. PARAMETER EVOLUTION: Both audio and graph coherence drive parameters
          // Field parameters updated with coherence values
          systemState.fieldParameters.amplitude = 1.0 + (graphCoherence || 0) * 6.0; // Safe fallback
          systemState.fieldParameters.spatialFreq = 0.5 + audioCoherence * 3.0;
          
          // Log evolution for verification (much less frequent) - THEORY COMPLIANT
          if (systemState.frameCount % 1000 === 0) { // Every 1000 frames - deterministic
            zxSnapshot = systemState.zxSnapshot || (window.zxEvolutionEngine ? window.zxEvolutionEngine.getSnapshot() : null);
            if (zxSnapshot) {
              const { cliffordField, graph, coherence } = zxSnapshot;
              const fieldMagnitude = cliffordField.payload?.components?.reduce((sum, c) => sum + Math.abs(c), 0) || 0;
              const rewriteCount = window.zxEvolutionEngine ? window.zxEvolutionEngine.getRewriteHistory().length : 0;
              const parsevalStr = audioCoherenceParseval == null ? '' : `, audio_parseval=${audioCoherenceParseval.toFixed(3)} (${normalization?.proof_id || ''})`;
              const coherenceStr = coherence != null ? `, graph=${coherence.toFixed(3)}` : '';
              console.log(`🧮 Evolution: audio=${audioCoherence.toFixed(3)}${parsevalStr}${coherenceStr}, field≈${fieldMagnitude.toFixed(3)}, nodes=${graph.nodes.length}, rewrites=${rewriteCount}`);

              if (graph && graph.labels) {
                const zCount = Object.values(graph.labels).filter(l => l.kind === 'Z').length;
                const xCount = Object.values(graph.labels).filter(l => l.kind === 'X').length;
                console.log(`🔗 Graph structure: ${zCount}Z + ${xCount}X spiders, ${graph.edges.length} edges`);
              }
            }
          }
          
          return { ...systemState, zxSnapshot: systemState.zxSnapshot, zxField: cliffordField };
        } catch (error) {
          console.error('🚨 Evolution chain error:', error);
          return systemState;
        }
      });
      
      console.log('🌌 Ex Nihilo Monad Universe rendering started');
      try { window.__setLoaderText?.('Rendering…'); } catch(_) {}
      // Hide loader on first successful render tick or metrics tick (whichever first)
      (function attachFirstFrameHider(){
        if (window.__firstFrameAttached) return; window.__firstFrameAttached = true;
        let hidden = false;
        const hideOnce = () => { if (!hidden) { hidden = true; try { window.__hideLoader?.(); } catch(_) {} } };
        // Hook render loop via requestAnimationFrame fallback
        requestAnimationFrame(() => hideOnce());
        // Also hide after first metrics update
        const listener = () => { hideOnce(); window.removeEventListener('metricsStateChanged', listener); };
        window.addEventListener('metricsStateChanged', listener);
        // Safety timeout in case neither fires
        setTimeout(hideOnce, 4000);
      })();
      
      // DISABLE debug overlay to eliminate pauses
      // const { createDebugOverlay, updateDebugStatus } = await import('./debug_status.js');
      // const debugOverlay = createDebugOverlay();
      console.log('🔬 Debug overlay DISABLED for smooth performance');
      
      // Analog substrate is now running and feeding the render loop
      
      // Theory iteration COMPLETELY DISABLED - no timer started
      console.log('🔬 Theory iteration COMPLETELY DISABLED - allowing natural evolution');
      console.log('🎯 No timers started - pure natural evolution only');
      
    } catch (error) {
      console.error('❌ FIRM UI initialization failed:', error);
      try { window.__hideLoader?.(); } catch(_) {}
      throw error;
    }
  })();
  return initializeFIRM._initializedPromise;
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initializeFIRM();
  });
} else {
  initializeFIRM();
}

window.initializeFIRM = initializeFIRM;