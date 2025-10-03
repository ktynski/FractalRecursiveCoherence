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
    this.gl = this.canvas.getContext('webgl2') || this.canvas.getContext('webgl');
    if (!this.gl) {
      throw new Error("WebGL not supported - hardware acceleration required");
    }
    
    // Log which version we're using
    const version = this.gl instanceof WebGL2RenderingContext ? 'WebGL2' : 'WebGL1';
    console.log(`🎮 Graphics context: ${version}`);
    
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
