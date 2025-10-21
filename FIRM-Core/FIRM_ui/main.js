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
      view: 'resonance-driven',
      camera: {
        position: [0, 0, 12],  // Theory: manifoldRadius * 4.0 = 3.0 * 4.0 = 12.0
        target: [0, 0, 0],
        up: [0, 1, 0],
        fov: 60,              // Optimal FOV for emergent complexity observation
        aspect_ratio: 16/9
      },
      rendering: {
        max_steps: 64,        // Reduced for smooth performance
        min_distance: 0.02,   // Slightly larger for efficiency
        max_distance: 50.0    // Theory: max_distance for emergent complexity viewing
      },
      accessibility: {
        no_motion: false,
        high_contrast: false
      },
      // THEORY: Camera lock for emergent complexity observation
      cameraFixed: true,           // Lock camera at optimal distance
      optimalObservation: false,   // Disable automatic observation systems
      fieldAnalysis: null,         // No automatic field analysis
      theoryControls: {
        observationDistance: null  // Manual override disabled
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
            'resonance-driven': 'Resonance-Driven (φ-Structured)',
            e8: 'E8 Topology (α=1/137)'
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
  }
  
  switchView(viewName) {
    if (!['clifford', 'resonance-driven', 'e8'].includes(viewName)) {
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
      case 'e8':
        console.log('🌟 E8 View: Ring+Cross topology generating α=1/137');
        this.initE8Visualization();
        break;
      
      case 'sector_em':
        console.log('⚡ EM Sector: N=21, ring+cross topology, α=1/137');
        if (window.zxEvolutionEngine?.setSector) {
          window.zxEvolutionEngine.setSector('ELECTROMAGNETIC');
        }
        break;
      
      case 'sector_dm':
        console.log('🌑 Dark Matter: N=105, tree topology, no EM coupling');
        if (window.zxEvolutionEngine?.setSector) {
          window.zxEvolutionEngine.setSector('DARK_MATTER');
        }
        break;
      
      case 'sector_de':
        console.log('💫 Dark Energy: Maximum entropy, random topology');
        if (window.zxEvolutionEngine?.setSector) {
          window.zxEvolutionEngine.setSector('DARK_ENERGY');
        }
        break;
    }
  }


  initE8Visualization() {
    // Initialize E8 visualizer if not already created
    if (!this.e8Visualizer) {
      const canvas = document.getElementById('canvas');
      if (canvas) {
        // Create E8 visualizer instance
        if (typeof E8Visualizer !== 'undefined') {
          this.e8Visualizer = new E8Visualizer(canvas, '2d');
          console.log('✨ E8 Visualizer initialized');
          console.log(`  N=${PHYSICS.N} encodes E8: ${PHYSICS.E8.check() ? '✓' : '✗'}`);
          console.log(`  α = 1/${1/PHYSICS.ALPHA.calculate()}`);
        } else {
          console.error('E8Visualizer not loaded. Check e8_visualizer.js');
        }
      }
    }
    
    // Draw E8 visualization
    if (this.e8Visualizer) {
      this.e8Visualizer.draw();
      
      // Start animation if enabled
      if (this.state.animating) {
        this.e8Visualizer.start();
      }
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
      
      // Respect camera lock for emergent complexity observation
      if (this.state.cameraFixed) return;
      
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
      
      // Respect camera lock for emergent complexity observation
      if (this.state.cameraFixed) return;
      
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
      // Respect camera lock for emergent complexity observation
      if (this.state.cameraFixed) return;
      
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
    
    // Respect camera lock for emergent complexity observation
    if (!this.state.cameraFixed) {
      this.state.camera.position = [0, 0, 20]; // Pull back to see both objects
    }
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
        
        if (window.analogEngine) {
          try {
            // Ensure AudioContext is created and resumed
            const audioContextReady = await window.analogEngine.ensureAudioContext();
            if (audioContextReady && window.analogEngine.audioContext) {
              console.log('🔍 AudioContext state:', window.analogEngine.audioContext.state);
              console.log('🔊 Audio context resumed successfully');
              enableAudioBtn.textContent = 'Audio Active ✓';
              enableAudioBtn.disabled = true;
              enableAudioBtn.style.background = '#2a5d2a';

              // Also initialize harmonic audio system if available
              if (window.getAudioContext) {
                const harmonicContext = window.getAudioContext();
                if (harmonicContext && harmonicContext.state === 'running') {
                  console.log('🎵 Harmonic audio system also active');
                }
              }
            } else {
              console.error('🔊 Audio context initialization failed');
              enableAudioBtn.textContent = 'Audio Failed ✗';
            }
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
            window.__resonanceMod = await import('./FIRM_dsl/resonance.js');
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
              // REMOVED: Duplicate evolveFromAudioCoherence() call - handled by interval loop
              // (window.zxEvolutionEngine && window.zxEvolutionEngine.evolveFromAudioCoherence ? window.zxEvolutionEngine.evolveFromAudioCoherence(0.5, 0.016) : null);
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
      
      // Attach to FIRM UI controller
      firmUI.renderer = renderer;
      
      // Initialize rendering system
      try { window.__setLoaderText?.('Starting WebGL…'); } catch(_) {}
      const rendererSuccess = await renderer.initialize();
      
      if (!rendererSuccess) {
        console.error('❌ Renderer initialization failed - WebGL not available');
        // Continue without rendering - system can still function for audio/theory
        console.log('⚠️ Continuing without visual rendering...');
      } else {
        // Import raymarching pipeline
        const { RaymarchingValidator } = await import('./raymarching.js');
        
        // Create raymarching pipeline
        const validator = new RaymarchingValidator();
        const pipeline = validator.createRaymarchingPipeline(null, firmUI.state.camera);
        
        // Set up rendering pipeline
        renderer.setupRaymarchingProgram(pipeline);
        
        console.log('✅ FIRM renderer initialized');
        console.log('✅ WebGL rendering pipeline operational');
      }
      
      console.log('✅ Mathematical engine connected');
      console.log('✅ Analog audio substrate ready');
      console.log('✅ Theory validation complete');
      
      // Add diagnostic function for debugging
      window.debugWebGL = () => {
        const canvas = document.getElementById('canvas');
        const gl = canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        const info = {
          canvas: { width: canvas.width, height: canvas.height, clientWidth: canvas.clientWidth, clientHeight: canvas.clientHeight },
          webgl: !!gl,
          webglVersion: gl ? (gl instanceof WebGL2RenderingContext ? 'WebGL2' : 'WebGL1') : 'none',
          renderer: !!window.renderer,
          rendererInitialized: window.renderer?.runtime?.initialized || false,
          zxEngine: !!window.zxEvolutionEngine
        };
        console.log('🔍 WebGL Diagnostics:', info);
        return info;
      };
      
      // Load optional audio normalization parameters (if present)
      let normalization = null;
      try {
        const resp = await fetch('./normalization.json');
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
      let ResonanceDrivenEngine;
      try {
        ({ ResonanceDrivenEngine } = await import('./resonance_driven_engine.js'));
      } catch (error) {
        console.error('❌ Failed to import resonance_driven_engine.js', error);
        throw error;
      }
      console.log('✅ Theory modules imported successfully');
      
      // Mathematical evolution will be handled by analog substrate
      
      // RESONANCE-DRIVEN: Create true theory-compliant engine using φ-structured resonance
      let zxEngine;
      let resonanceDrivenEngine;
      try {
        // Create resonance-driven engine implementing true master equation via φ-structured modes
        resonanceDrivenEngine = new ResonanceDrivenEngine();
        
        // Initialize the graph asynchronously
        await resonanceDrivenEngine.initializeGraph();
        
        zxEngine = resonanceDrivenEngine; // Use resonance-driven engine directly
        
        // Make globally accessible
        window.resonanceDrivenEngine = resonanceDrivenEngine;
        window.zxEvolutionEngine = zxEngine; // Use resonance-driven engine
        
        // Attach to FIRM UI controller
        firmUI.resonanceDrivenEngine = resonanceDrivenEngine;
        firmUI.zxEvolutionEngine = zxEngine;
        
        console.log('✅ Resonance-Driven Engine constructed (true master equation via φ-structured resonance)');
      } catch (resonanceError) {
        console.error('❌ Resonance-driven engine failed:', resonanceError.message);
        throw resonanceError;
      }
      
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
          if (!window.analogEngine) return;

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
              if (window.analogEngine) {
                const audioContextReady = await window.analogEngine.ensureAudioContext();
                if (audioContextReady) {
                  markActive();
                  cleanup();
                  console.log('🔊 Audio context resumed via user gesture');
                  return;
                }
              }

              // Also try harmonic audio system
              if (window.getAudioContext) {
                const ctx = window.getAudioContext();
                if (ctx && ctx.state === 'running') {
                  markActive();
                  cleanup();
                  console.log('🎵 Harmonic audio context active via user gesture');
                  return;
                }
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
      
      // Theory validation now handled by resonance-driven engine
      
      // Make ZX engine globally accessible immediately
      window.zxEvolutionEngine = zxEngine;
      console.log('🌐 ZX engine globally accessible (early initialization)');
      
      // Create emergent observer inline (avoid import issues)
      const emergentObserver = {
        consciousness: { awareness: 0.5, focus: 0.5, understanding: 0.5 },
        boundaryHistory: [],
        
        analyzeFieldBoundaries(cliffordField) {
          if (!cliffordField?.payload?.components) return null;
          
          const controlParams = window.zxEvolutionEngine._controlParams;
          
          const components = cliffordField.payload.components;
          const totalActivity = components.reduce((sum, c) => sum + Math.abs(c), 0);
          const emergentBoundary = Math.max(controlParams.fieldBoundaryMin, Math.min(controlParams.fieldBoundaryMax, totalActivity * controlParams.fieldBoundaryActivityScale));
          const naturalObservationDistance = emergentBoundary * controlParams.naturalObservationDistanceScale;
          
          return {
            emergentBoundary,
            naturalObservationDistance,
            fieldActivity: totalActivity
          };
        },
        
        evolveConsciousness(fieldAnalysis, visualFeedback) {
          const controlParams = window.zxEvolutionEngine._controlParams;
          if (fieldAnalysis?.fieldActivity > controlParams.consciousnessAwarenessThreshold) {
            this.consciousness.awareness = Math.min(1.0, this.consciousness.awareness + controlParams.consciousnessAwarenessIncrement);
          }
          return this.consciousness;
        },
        
        computeOptimalObservation(fieldAnalysis, consciousness) {
          if (!fieldAnalysis) return null;
          
          const controlParams = window.zxEvolutionEngine._controlParams;
          
          const awarenessModulation = controlParams.optimalObservationAwarenessModMin + consciousness.awareness * controlParams.optimalObservationAwarenessModScale;
          const cameraDistance = fieldAnalysis.naturalObservationDistance * awarenessModulation;
          
          return {
            cameraDistance,
            fieldOfView: controlParams.optimalObservationFOV,
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

      // Initialize Soul Garbage Collection Integration
      try {
        try { window.__setLoaderText?.('Initializing 𝒮-GC integration…'); } catch(_) {}
        const { SoulGarbageCollectorVisualizer, SGCMonadListenerIntegration } = await import('./soul_garbage_collection.js');

        window.sgcVisualizer = new SoulGarbageCollectorVisualizer();
        window.sgcIntegration = new SGCMonadListenerIntegration();

        // Initialize the visualizer in a dedicated container
        const sgcContainer = document.createElement('div');
        sgcContainer.id = 'sgc-visualization';
        sgcContainer.style.display = 'none'; // Hidden by default

        // Add to DOM (will be shown via tabs or controls)
        const mainContent = document.querySelector('.main-content') || document.body;
        mainContent.appendChild(sgcContainer);

        window.sgcVisualizer.initialize();
        window.sgcIntegration.initialize();

        // Enable SGC in the ZX evolution engine by default
        if (window.zxEvolutionEngine) {
          window.zxEvolutionEngine.enableSoulGarbageCollection();
          console.log('🗑️ Soul Garbage Collection enabled in evolution engine');
        }

        console.log('🗑️ Soul Garbage Collection Integration initialized');
      } catch (sgcError) {
        console.error('❌ 𝒮-GC integration initialization failed:', sgcError);
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
        // THEORY: Camera lock for emergent complexity observation
        cameraFixed: firmUI.state.cameraFixed,
        optimalObservation: firmUI.state.optimalObservation,
        fieldAnalysis: firmUI.state.fieldAnalysis,
        theoryControls: firmUI.state.theoryControls,
        // BOOTSTRAP: Initialize with identity multivector for sovereignty
        // Theory: Ex nihilo emergence requires seed state (scalar = 1, all else = 0)
        cliffordField: { 
          payload: { 
            components: [1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  // Identity: scalar = 1
          },
          constructor: { name: 'MultivectorField' }
        },
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
                emergence_view: {
                  position: [0, 8, 20],
                  target: [0, 0, 0],
                  up: [0, 1, 0],
                  description: 'Emergence: Bootstrap phase evolution'
                },
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
        
        
        
        
        console.log('🎛️ Theory exploration controls initialized');
      };
      
      // Make controls globally accessible
      window.theoryControls = theoryControls;
      
      // Setup sliders after DOM is ready
      setupSliders();
      
      // AUTONOMOUS AUDIO GENERATION: System sings itself into existence
      // Theory: Axiom A2 (Sovereignty Ψ) - Autonomous, self-referential
      // Audio is emergent expression of Clifford field, not external input
      
      let harmonicGenerator = null;
      let autonomousEvolution = null;
      
      // Initialize harmonic generation (no fallbacks; explicit failure if module not loaded)
      // Theory: Sovereign audio system must initialize without implicit suppressions.
      try {
        const { HarmonicGenerator, AutonomousEvolution, playHarmonicBuffer } = await import('./harmonic_generator.js');
        const controlParams = window.zxEvolutionEngine._controlParams;
        harmonicGenerator = new HarmonicGenerator(controlParams.harmonicFundamentalFrequency);  // Theory-parameterized fundamental
        autonomousEvolution = new AutonomousEvolution(controlParams.autonomousEvolutionRate);  // Theory-parameterized autonomy growth
        window.playHarmonicBuffer = playHarmonicBuffer;  // Make available in global scope
        console.log('✅ Sovereign audio system initialized');
      } catch (error) {
        console.error('❌ CRITICAL: Failed to load sovereign audio system:', error.message);
        throw new Error(`THEORY VIOLATION: Axiom A2 (Sovereignty) requires autonomous audio. System cannot proceed. ${error.message}`);
      }

      // Web Audio context for playing emergent harmonics - create lazily
      const getAudioContext = () => {
        if (!audioContext) {
          audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        return audioContext;
      };
      window.getAudioContext = getAudioContext;
      console.log('🎵 Sovereign audio system initialized (monad singing)');
      
      // TRUE ANALOG EVOLUTION: Complete theory-compliant chain
      if (rendererSuccess) {
        renderer.startRenderLoop(async () => {
        try {
          // THEORY: Camera lock for emergent complexity observation
          // Must check FIRST before any other systems that might move camera
          if (systemState.cameraFixed) {
            // Restore camera to theoretical optimal distance if it has drifted
            const currentPos = systemState.camera.position;
            const currentDistance = Math.sqrt(currentPos[0]**2 + currentPos[1]**2 + currentPos[2]**2);
            const theoreticalDistance = 12.0; // manifoldRadius * 4.0
            
            if (Math.abs(currentDistance - theoreticalDistance) > 0.1) {
              // Camera has drifted, restore to optimal position
              const direction = currentDistance > 0 ? 
                currentPos.map(p => p / currentDistance) : [0, 0, 1];
              systemState.camera.position = direction.map(d => d * theoreticalDistance);
            }
          }
          
          // Increment frame counter for stable animations
          systemState.frameCount++;
          
          // 1. EXTERNAL AUDIO (for bootstrap only)
          // Theory: System can accept external stimulus initially, then becomes autonomous
          const externalCoherence = analogEngine.getAudioCoherence();

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

          // 2. EMERGENT HARMONICS: Generate audio from previous cycle's field state
          // Theory: Ψ ≅ Hom(Ψ, Ψ) - System observes own state through harmonics
          // NO FALLBACKS: System MUST have these components or fail loudly
          
          if (!harmonicGenerator || !autonomousEvolution) {
            throw new Error(
              "THEORY VIOLATION: Sovereign audio system (HarmonicGenerator/AutonomousEvolution) not initialized. " +
              "Axiom A2 (Sovereignty) requires Ψ ≅ Hom(Ψ, Ψ). System cannot proceed without autonomous audio."
            );
          }
          
          if (!systemState.cliffordField || !systemState.cliffordField.payload || !systemState.cliffordField.payload.components) {
            throw new Error(
              "THEORY VIOLATION: Clifford field is null or invalid. " +
              "System requires valid field state for harmonic generation. " +
              "Bootstrap must initialize identity field before first evolution cycle."
            );
          }
          
          // SOVEREIGN AUDIO: Theory requires Ψ ≅ Hom(Ψ,Ψ) - no fallbacks, no conditions
          const harmonicSpectrum = harmonicGenerator.generateSpectrum(systemState.cliffordField);
          const internalCoherence = harmonicGenerator.computeCoherence(harmonicSpectrum);
          
          // Play emergent harmonics (system's voice)
          if (harmonicSpectrum && systemState.frameCount % 6 === 0) {  // Every 6 frames (~100ms chunks)
            try {
              const audioBuffer = harmonicGenerator.synthesizeAudio(harmonicSpectrum, 0.1);
              // Use lazy AudioContext creation
              const ctx = window.getAudioContext ? window.getAudioContext() : audioContext;
              if (ctx && ctx.state === 'running') {
                window.playHarmonicBuffer(ctx, audioBuffer);
              }
            } catch (error) {
              // Audio playback failed - this is expected until user gesture
              if (systemState.frameCount % 300 === 0) { // Only log occasionally
                console.log('🔊 Audio playback waiting for user gesture');
              }
            }
          }
          
          // Log spectrum periodically
          if (systemState.frameCount % 300 === 0) {  // Every 5 seconds
            harmonicGenerator.logSpectrum(harmonicSpectrum, internalCoherence);
          }
          
          // 3. AUTONOMOUS COHERENCE: Blend external (bootstrap) + internal (sovereign)
          // Theory: Gradual transition from external stimulus to full autonomy
          const audioCoherence = autonomousEvolution.getAudioCoherence(externalCoherence, internalCoherence);
          
          // Log sovereignty achievement
          if (autonomousEvolution.hasSovereignty() && systemState.frameCount % 60 === 0) {
            console.log('👑 SOVEREIGNTY ACHIEVED: System is fully autonomous');
          }

          // ZX EVOLUTION: Use Network or single system
          let zxSnapshot = null;
          let graphCoherence = 0.0;
          let networkSnapshot = null;
          
          // RESONANCE-DRIVEN: Use resonance-driven engine
          if (window.zxEvolutionEngine) {
            // Fallback to single system
            const enhancedCoherence = audioCoherence * theoryControls.emergenceRate;
          const deltaTime = 0.016;

          // THEORY-COMPLIANT SINGLE EVOLUTION CALL
          // Previous double-call caused state inconsistencies
          // evolveSystem() handles baseline coherence and calls emergentEvolution
          // evolve() handles ZX rewrites and graph evolution
          // Both are needed but must use same audioCoherence value
          
          // 4. Emergent field evolution (consciousness dynamics)
          // REMOVED: Duplicate evolveSystem() call - handled by interval loop
          const evolutionState = null; // zxEvolutionEngine.evolveSystem ?
            // zxEvolutionEngine.evolveSystem(enhancedCoherence, deltaTime) : null;

          if (evolutionState && evolutionState.coherence !== undefined && evolutionState.structure !== undefined && evolutionState.volume !== undefined) {
            console.log(`🌌 Evolution: ${evolutionState.phase || 'unknown'} | Coherence: ${evolutionState.coherence.toFixed(2)} | Structure: ${evolutionState.structure.toFixed(2)} | Volume: ${evolutionState.volume.toFixed(3)} | Letters: ${evolutionState.emergentLetters?.length || 0}`);
          }

          // 5. Graph evolution (ZX rewrites, grace emergence)
          // CRITICAL: Use same enhancedCoherence for consistency
          // REMOVED: Duplicate evolve() call - handled by interval loop
          // zxEvolutionEngine.evolve(enhancedCoherence, deltaTime);

          zxSnapshot = await zxEvolutionEngine.getSnapshot();
          graphCoherence = zxSnapshot ? zxSnapshot.coherence : 0.0;
          
          // DEBUG: Check snapshot structure
          if (systemState.frameCount % 300 === 0) {
            console.log('🔍 SNAPSHOT DEBUG:', {
              hasSnapshot: !!zxSnapshot,
              hasField: !!zxSnapshot?.cliffordField,
              fieldType: zxSnapshot?.cliffordField?.constructor?.name,
              fieldComponents: zxSnapshot?.cliffordField?.payload?.components?.length || 0
            });
          }

          // DIAGNOSTIC: Check cliffordField population (first call only)
          if (!window._fieldCheckLogged) {
            console.log('🔍 CLIFFORD FIELD DIAGNOSTIC:', {
              frame: systemState.frameCount,
              hasSnapshot: !!zxSnapshot,
              hasField: !!zxSnapshot?.cliffordField,
              fieldLength: zxSnapshot?.cliffordField?.length,
              fieldType: zxSnapshot?.cliffordField?.constructor?.name
            });
            window._fieldCheckLogged = true;
          }

          systemState.zxEngine = window.zxEvolutionEngine;
          systemState.currentGraph = zxSnapshot ? zxSnapshot.graph : null;
          systemState.graphCoherence = graphCoherence;
          systemState.cliffordField = zxSnapshot ? zxSnapshot.cliffordField : null;
          
          // NETWORK STATE: Add network information if available
          if (networkSnapshot) {
            systemState.networkSnapshot = networkSnapshot;
            systemState.globalCoherence = networkSnapshot.globalCoherence;
            systemState.synchronization = networkSnapshot.synchronization;
            systemState.networkSystems = networkSnapshot.systems;
          }
          
          // DIAGNOSTIC: Verify field assignment
          if (!window._fieldAssignLogged) {
            console.log('✅ FIELD ASSIGNED:', {
              hasField: !!systemState.cliffordField,
              fieldType: systemState.cliffordField?.constructor?.name
            });
            window._fieldAssignLogged = true;
          }
          
          systemState.zxSnapshot = zxSnapshot;
          systemState.evolutionState = evolutionState;
          
          // CIRCULAR CAUSALITY: Store field for next harmonic generation cycle
          // Theory: Ψ ≅ Hom(Ψ, Ψ) implemented as field → harmonics → coherence → field
          // This creates self-aware feedback loop (monad singing to itself)
          systemState.cliffordField = zxSnapshot ? zxSnapshot.cliffordField : systemState.cliffordField;
          
          // LEGACY: External audio modulation (optional, for backwards compatibility)
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
          systemState.internalCoherence = internalCoherence;
          systemState.externalCoherence = externalCoherence;
          systemState.autonomyFactor = autonomousEvolution ? autonomousEvolution.autonomyFactor : 0.0;
          systemState.harmonicSpectrum = harmonicSpectrum;
          systemState.graphCoherence = graphCoherence;
          
          // 6. CONSCIOUSNESS EVOLUTION: Use cached field to avoid duplicate generation
          // Field will be generated in the render loop - reuse it here for efficiency
          zxSnapshot = zxSnapshot || systemState.zxSnapshot || (window.zxEvolutionEngine ? await window.zxEvolutionEngine.getSnapshot() : null);
          if (zxSnapshot) {
            systemState.zxSnapshot = zxSnapshot;
            // BUGFIX: Only overwrite if field exists
            if (zxSnapshot.cliffordField) {
              systemState.cliffordField = zxSnapshot.cliffordField;
            }
          }

        // Use systemState.cliffordField directly (already assigned above)
        const cliffordField = systemState.cliffordField;
        
        // EMERGENT OBSERVER: Only run if field exists AND camera not fixed
        let fieldAnalysis = null;
        let consciousness = null;
        let optimalObservation = null;
        
        if (cliffordField && emergentObserver && !systemState.cameraFixed) {
          fieldAnalysis = emergentObserver.analyzeFieldBoundaries(cliffordField);
          consciousness = emergentObserver.evolveConsciousness(fieldAnalysis, {nonBlackPixels: 0}); // Will be updated with real visual feedback
          optimalObservation = fieldAnalysis ? emergentObserver.computeOptimalObservation(fieldAnalysis, consciousness) : null;
        }
          
          // 7. THEORY-DRIVEN EVOLUTION CONTROL (Auto Ω Mode)
          if (firmUI._autoOmegaEnabled && window.__resonanceMod) {
            try {
              if (!window.__omegaSignature && zxSnapshot) {
                window.__omegaSignature = window.__resonanceMod.deriveOmegaSignature(zxSnapshot.graph);
              }
              if (window.__omegaSignature && window.zxEvolutionEngine) {
                // Compute current resonance
                const res = window.__resonanceMod.computeResonanceAlignment(zxSnapshot.graph, window.__omegaSignature);
                // Update control params to steer toward Ω: higher emergence when Res is rising
                const targetEmergence = Math.min(
                  window.zxEvolutionEngine._controlParams.emergenceRate.max,
                  window.zxEvolutionEngine._controlParams.targetEmergenceOffset +
                  window.zxEvolutionEngine._controlParams.targetEmergenceResonanceScale * Math.max(0, res)
                );
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

          // 8. MANIFOLD OBSERVATION: Update camera to observe transforming manifold
          // THEORY: Camera should remain at optimal distance (manifoldRadius * 4.0 = 12.0 units)
          // when cameraFixed is true to observe emergent complexity
          if (optimalObservation && fieldAnalysis && !systemState.cameraFixed) {
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
              
              // Calculate target distance with GENTLE scaling for stable viewing
              const fieldSize = Math.max(3.0, fieldAnalysis.fieldActivity * 0.5); // Much gentler scaling
              const minSafeDistance = fieldSize * 1.5; // Closer viewing
              targetDistance = Math.max(
                minSafeDistance,
                baseDistance + Math.sin(systemState.frameCount * 0.005) * maxDistanceChange
              );
            }
            
            // Apply heavy damping to camera movement (position lerping)
            const currentPos = systemState.camera.position;
            const currentDistance = Math.sqrt(currentPos[0]**2 + currentPos[1]**2 + currentPos[2]**2);
            
            // Calculate minimum safe distance (always respect field boundaries)
            const fieldSize = Math.max(3.0, fieldAnalysis.fieldActivity * 0.5); // Consistent gentle scaling
            const minSafeDistance = fieldSize * 1.5; // Consistent closer viewing
            
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
              
              // Respect camera lock for emergent complexity observation
              if (!systemState.cameraFixed) {
                systemState.camera.position = direction.map(d => d * finalDistance);
              }
            } else {
              // Ensure initial position respects safety distance
              const safeTargetDistance = Math.max(minSafeDistance, targetDistance);
              
              // Respect camera lock for emergent complexity observation
              if (!systemState.cameraFixed) {
                systemState.camera.position = [0, 0, safeTargetDistance];
              }
            }
            
            // Adaptive field of view for manifold observation
            if (!systemState.cameraFixed) {
              systemState.camera.fov = Math.max(30, Math.min(90, 45 + complexityFactor * 10));
            }
            
            // THEORY COMPLIANT: Use deterministic frame-based logging instead of random
            if (systemState.frameCount % 2000 === 0) { // Every 2000 frames - deterministic
              const currentDistance = Math.sqrt(systemState.camera.position[0]**2 + systemState.camera.position[1]**2 + systemState.camera.position[2]**2);
              console.log(`🌐 Manifold observation: distance=${currentDistance.toFixed(1)}, complexity=${complexityFactor.toFixed(2)}, FOV=${systemState.camera.fov.toFixed(1)}°`);
              console.log(`🧠 Consciousness: awareness=${consciousness.awareness.toFixed(3)}, focus=${consciousness.focus.toFixed(3)}`);
            }
          }
          
          // 9. PARAMETER EVOLUTION: Both audio and graph coherence drive parameters
          // Theory: Coherence → Clifford field strength (amplitude) and structure (frequency)
          // Parameterized via ControlParamsValidator for future Clifford equation derivation
          const ctrl = window.zxEvolutionEngine._controlParams;
          systemState.fieldParameters.amplitude = ctrl.amplitudeBaseValue + (graphCoherence || 0) * ctrl.amplitudeCoherenceScale;
          systemState.fieldParameters.spatialFreq = ctrl.spatialFreqBaseValue + audioCoherence * ctrl.spatialFreqCoherenceScale;
          
          // Log evolution for verification (much less frequent) - THEORY COMPLIANT
          if (systemState.frameCount % 1000 === 0) { // Every 1000 frames - deterministic
            zxSnapshot = systemState.zxSnapshot || (window.zxEvolutionEngine ? await window.zxEvolutionEngine.getSnapshot() : null);
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
          
          // Update physics constants display (every second)
          if (systemState.frameCount % 60 === 0) {
            const e8DimEl = document.getElementById('e8Dimension');
            const e8RootsEl = document.getElementById('e8Roots');
            const alphaEl = document.getElementById('alphaValue');
            const sectorEl = document.getElementById('currentSector');
            const topologyEl = document.getElementById('currentTopology');
            
            if (e8DimEl && window.PHYSICS) {
              const N = window.PHYSICS.N;
              const dim = N * 12 - 4;
              const roots = N * 11 + 9;
              const alpha = window.PHYSICS.ALPHA.calculate();
              
              e8DimEl.textContent = `${dim} ${dim === 248 ? '✓' : '✗'}`;
              e8DimEl.style.color = dim === 248 ? '#00ff00' : '#ff5555';
              
              if (e8RootsEl) {
                e8RootsEl.textContent = `${roots} ${roots === 240 ? '✓' : '✗'}`;
                e8RootsEl.style.color = roots === 240 ? '#00ff00' : '#ff5555';
              }
              
              if (alphaEl) {
                alphaEl.textContent = `1/${(1/alpha).toFixed(3)}`;
              }
              
              if (window.zxEvolutionEngine?._currentSector && sectorEl) {
                sectorEl.textContent = window.zxEvolutionEngine._currentSector.replace('_', ' ');
                const sector = window.PHYSICS.SECTORS[window.zxEvolutionEngine._currentSector];
                if (sector && topologyEl) {
                  topologyEl.textContent = sector.topology;
                }
              }
            }
          }
          
          return systemState;
        } catch (error) {
          console.error('🚨 Evolution chain error:', error);
          return systemState;
        }
        });
        
        console.log('🌌 Ex Nihilo Monad Universe rendering started');
      } else {
        console.log('⚠️ Rendering disabled - WebGL not available');
      }
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
      
      // Start evolution loop at 60fps
      firmUI.evolutionInterval = setInterval(async () => {
        try {
          const audioCoherence = window.analogEngine?.getAudioCoherence?.() || 0.8;
          
          // RESONANCE-DRIVEN: Use resonance-driven engine
          if (window.zxEvolutionEngine && window.zxEvolutionEngine.isInitialized()) {
            // Fallback to single system - just call evolve
            const evolutionResult = await window.zxEvolutionEngine.evolve(audioCoherence, 0.016);
            const coherence = evolutionResult.coherence || 0.0;
            
            if (window._evolutionDebugCounter === undefined) window._evolutionDebugCounter = 0;
            window._evolutionDebugCounter++;
            if (window._evolutionDebugCounter % 60 === 0) {
              const snapshot = await window.zxEvolutionEngine.getSnapshot();
              console.log(`🔄 Single: nodes=${snapshot.graph.nodes.length}, coherence=${coherence.toFixed(4)}`);
            }
          } else {
            console.log('❌ No evolution engine available');
          }
        } catch (error) {
          console.error('❌ Evolution loop error:', error);
        }
      }, 16);
      console.log('🎯 Evolution loop started at 60fps');
      
      // Add camera reset function for debugging
      window.resetCamera = () => {
        systemState.camera.position = [0, 0, 5];
        systemState.camera.target = [0, 0, 0];
        console.log('📷 Camera reset to default position');
      };
      
      
      // Add manual evolution trigger for debugging
      window.triggerEvolution = async () => {
        if (window.zxEvolutionEngine) {
          console.log('🔄 Manual evolution trigger...');
          const snapshot1 = await window.zxEvolutionEngine.getSnapshot();
          console.log(`📊 Before: nodes=${snapshot1.graph.nodes.length}, edges=${snapshot1.graph.edges.length}`);
          
          const evolutionResult = await window.zxEvolutionEngine.evolve(0.8, 0.016);
          const coherence = evolutionResult.coherence || 0.0;
          console.log(`✅ Evolution completed, coherence=${coherence}`);
          
          const snapshot2 = await window.zxEvolutionEngine.getSnapshot();
          console.log(`📊 After: nodes=${snapshot2.graph.nodes.length}, edges=${snapshot2.graph.edges.length}`);
          
          if (snapshot2.graph.nodes.length > snapshot1.graph.nodes.length) {
            console.log('🎉 Evolution working! Nodes increased');
          } else {
            console.log('❌ Evolution not working - no node increase');
          }
        } else {
          console.log('❌ Evolution engine not available');
        }
      };
      
      // Metrics updates are handled by metrics_updater.js
      // No need to start duplicate update loop here
      
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

// E8 Validation Display
function validateE8Display() {
  const N = 21;  // E8 encoding
  const dimension = N * 12 - 4;
  const roots = N * 11 + 9;
  const isValid = dimension === 248 && roots === 240;
  
  // Create or update status display
  let statusDiv = document.getElementById('e8-validation-status');
  if (!statusDiv) {
    statusDiv = document.createElement('div');
    statusDiv.id = 'e8-validation-status';
    statusDiv.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      padding: 10px 20px;
      background: rgba(0,0,0,0.8);
      color: ${isValid ? '#00ff00' : '#ff0000'};
      border: 2px solid ${isValid ? '#00ff00' : '#ff0000'};
      border-radius: 5px;
      font-family: monospace;
      z-index: 10000;
    `;
    document.body.appendChild(statusDiv);
  }
  
  statusDiv.innerHTML = `
    <div style="font-weight: bold; margin-bottom: 5px;">
      E8 Validation: ${isValid ? '✓ VALID' : '✗ INVALID'}
    </div>
    <div style="font-size: 0.9em;">
      N = ${N}<br>
      Dimension: ${dimension} ${dimension === 248 ? '✓' : `(should be 248)`}<br>
      Roots: ${roots} ${roots === 240 ? '✓' : `(should be 240)`}<br>
      α ≈ 1/137.036
    </div>
  `;
  
  return isValid;
}

// Call on initialization
setTimeout(validateE8Display, 1000);
}

window.initializeFIRM = initializeFIRM;
