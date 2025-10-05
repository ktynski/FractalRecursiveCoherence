/**
 * shader_runtime.js
 * 
 * WebGL/WebGPU shader compilation and runtime management (no execution until validated).
 * 
 * This module provides shader compilation utilities with validation but does not
 * execute rendering operations until the complete pipeline is validated.
 */

export class WebGLShaderRuntime {
  constructor(canvas) {
    if (!canvas) {
      throw new Error("Canvas element required");
    }
    
    this.canvas = canvas;
    this.gl = null;
    this.programs = new Map();
    this.buffers = new Map();
    this.initialized = false;
  }
  
  initialize() {
    // Try WebGL2 first, fallback to WebGL1 (theory-preserving)
    // Mobile-friendly: allow without major performance caveat
    const contextOptions = {
      alpha: false,
      depth: false,
      antialias: false,
      powerPreference: 'high-performance',
      failIfMajorPerformanceCaveat: false  // Critical for mobile devices
    };
    
    this.gl = this.canvas.getContext('webgl2', contextOptions) || 
              this.canvas.getContext('webgl', contextOptions) ||
              this.canvas.getContext('experimental-webgl', contextOptions);  // Old mobile browsers
    
    if (!this.gl) {
      this.showWebGLError();
      return false;  // Signal initialization failure instead of throwing
    }
    
    // Log which version we're using
    const version = this.gl instanceof WebGL2RenderingContext ? 'WebGL2' : 'WebGL1';
    console.log(`🎮 Graphics context: ${version}`);
    try {
      const ctxParams = this.gl.getContextAttributes?.();
      console.log('🎮 Context attributes:', ctxParams);
      const debugInfo = this.gl.getExtension('WEBGL_debug_renderer_info');
      if (debugInfo) {
        const vendor = this.gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        const renderer = this.gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        console.log('🎮 GPU:', { vendor, renderer });
      }
    } catch (e) {
      console.warn('🎮 GPU diagnostics unavailable:', e?.message || e);
    }
    
    // Validate required extensions
    const requiredExtensions = ['EXT_color_buffer_float'];
    for (const ext of requiredExtensions) {
      if (!this.gl.getExtension(ext)) {
        console.warn(`Extension ${ext} not available`);
      }
    }
    
    this.initialized = true;
    return true;
  }
  
  compileShader(source, type) {
    if (!this.initialized) {
      throw new Error("Runtime not initialized");
    }
    
    const shader = this.gl.createShader(type);
    this.gl.shaderSource(shader, source);
    this.gl.compileShader(shader);
    
    if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
      const info = this.gl.getShaderInfoLog(shader);
      this.gl.deleteShader(shader);
      throw new Error(`Shader compilation failed: ${info}`);
    }
    
    return shader;
  }
  
  createProgram(vertexSource, fragmentSource, programName = 'default') {
    if (!this.initialized) {
      throw new Error("Runtime not initialized");
    }
    
    const vertexShader = this.compileShader(vertexSource, this.gl.VERTEX_SHADER);
    const fragmentShader = this.compileShader(fragmentSource, this.gl.FRAGMENT_SHADER);
    
    const program = this.gl.createProgram();
    this.gl.attachShader(program, vertexShader);
    this.gl.attachShader(program, fragmentShader);
    this.gl.linkProgram(program);
    
    if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
      const info = this.gl.getProgramInfoLog(program);
      this.gl.deleteProgram(program);
      throw new Error(`Program linking failed: ${info}`);
    }
    
    // Clean up shaders
    this.gl.deleteShader(vertexShader);
    this.gl.deleteShader(fragmentShader);
    
    this.programs.set(programName, program);
    return program;
  }
  
  createBuffer(data, target = null, usage = null) {
    if (!this.initialized) {
      throw new Error("Runtime not initialized");
    }
    
    const buffer = this.gl.createBuffer();
    const bufferTarget = target || this.gl.ARRAY_BUFFER;
    const bufferUsage = usage || this.gl.STATIC_DRAW;
    
    this.gl.bindBuffer(bufferTarget, buffer);
    this.gl.bufferData(bufferTarget, data, bufferUsage);
    
    return buffer;
  }
  
  validateProgram(programName) {
    const program = this.programs.get(programName);
    if (!program) {
      throw new Error(`Program ${programName} not found`);
    }
    
    this.gl.validateProgram(program);
    if (!this.gl.getProgramParameter(program, this.gl.VALIDATE_STATUS)) {
      const info = this.gl.getProgramInfoLog(program);
      throw new Error(`Program validation failed: ${info}`);
    }
    
    return true;
  }
  
  getUniformLocation(programName, uniformName) {
    const program = this.programs.get(programName);
    if (!program) {
      throw new Error(`Program ${programName} not found`);
    }
    
    return this.gl.getUniformLocation(program, uniformName);
  }
  
  dispose() {
    if (this.gl) {
      // Clean up programs
      this.programs.forEach(program => this.gl.deleteProgram(program));
      this.programs.clear();
      
      // Clean up buffers
      this.buffers.forEach(buffer => this.gl.deleteBuffer(buffer));
      this.buffers.clear();
    }
    
    this.initialized = false;
  }
}

export class WebGPUShaderRuntime {
  constructor(canvas) {
    if (!canvas) {
      throw new Error("Canvas element required");
    }
    
    this.canvas = canvas;
    this.device = null;
    this.context = null;
    this.pipelines = new Map();
    this.buffers = new Map();
    this.initialized = false;
  }
  
  async initialize() {
    if (!navigator.gpu) {
      throw new Error("WebGPU not supported");
    }
    
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) {
      throw new Error("WebGPU adapter not available");
    }
    
    this.device = await adapter.requestDevice();
    this.context = this.canvas.getContext('webgpu');
    
    if (!this.context) {
      throw new Error("WebGPU context not available");
    }
    
    // Configure canvas context
    this.context.configure({
      device: this.device,
      format: 'bgra8unorm',
      alphaMode: 'premultiplied'
    });
    
    this.initialized = true;
    return true;
  }
  
  showWebGLError() {
    /**
     * Display user-friendly WebGL error message instead of throwing.
     * Critical for mobile devices where WebGL may be unavailable.
     */
    const errorHTML = `
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                  background: rgba(0,0,0,0.9); color: #fff; padding: 2rem;
                  border-radius: 8px; max-width: 90%; text-align: center; z-index: 10000;">
        <h2 style="color: #ff5555; margin-top: 0;">⚠️ WebGL Not Available</h2>
        <p style="margin: 1rem 0;">This visualization requires WebGL, which is not available on your device.</p>
        
        <div style="text-align: left; margin: 1.5rem 0; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 4px;">
          <p style="margin: 0.5rem 0;"><strong>Possible causes:</strong></p>
          <ul style="margin: 0.5rem 0;">
            <li>Hardware acceleration is disabled</li>
            <li>Battery saver mode is active</li>
            <li>Your browser doesn't support WebGL</li>
            <li>WebGL is blocked by security settings</li>
          </ul>
          
          <p style="margin: 1rem 0 0.5rem 0;"><strong>Try this:</strong></p>
          <ul style="margin: 0.5rem 0;">
            <li>Disable battery saver mode</li>
            <li>Use Chrome, Firefox, or Safari</li>
            <li>Enable "Use hardware acceleration" in browser settings</li>
            <li>Try on a desktop/laptop computer</li>
          </ul>
        </div>
        
        <p style="margin-top: 1.5rem; font-size: 0.9em; color: #888;">
          Check your browser's console for technical details.
        </p>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', errorHTML);
    console.error('❌ WebGL initialization failed');
    console.error('Device info:', {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      vendor: navigator.vendor
    });
  }
  
  createComputePipeline(shaderSource, pipelineName = 'default') {
    if (!this.initialized) {
      throw new Error("Runtime not initialized");
    }
    
    const shaderModule = this.device.createShaderModule({
      code: shaderSource
    });
    
    const pipeline = this.device.createComputePipeline({
      layout: 'auto',
      compute: {
        module: shaderModule,
        entryPoint: 'main'
      }
    });
    
    this.pipelines.set(pipelineName, pipeline);
    return pipeline;
  }
  
  createBuffer(size, usage) {
    if (!this.initialized) {
      throw new Error("Runtime not initialized");
    }
    
    const buffer = this.device.createBuffer({
      size,
      usage
    });
    
    return buffer;
  }
  
  dispose() {
    if (this.device) {
      // Clean up pipelines and buffers
      this.pipelines.clear();
      this.buffers.forEach(buffer => buffer.destroy());
      this.buffers.clear();
      
      this.device.destroy();
    }
    
    this.initialized = false;
  }
}

// NOTE: UI event handlers are managed in main.js to avoid conflicts
// This file only provides WebGL shader compilation utilities
