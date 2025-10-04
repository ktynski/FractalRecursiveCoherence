/**
 * renderer.js
 * 
 * WebGL rendering execution for FIRM Clifford field visualization.
 * 
 * This module connects the proven mathematical engine to visual output,
 * maintaining theory fidelity throughout the rendering pipeline.
 */

import { WebGLShaderRuntime } from './shader_runtime.js';

export class FIRMRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.runtime = new WebGLShaderRuntime(canvas);
    this.currentPipeline = null;
    this.fieldTexture = null;
    this.previousComponents = null;
    this.uniformLocations = new Map();
    this.frameCount = 0;
    this.isRunning = false;
    
    // Enhanced bootstrap tracking
    this.previousField = null;
    this.diracHistory = [];
    this.massEvolution = [];
    this.lastStage = 'NASCENT';
    
    // PERFORMANCE: Cache expensive matrix calculations
    this.cachedMatrices = null;
    this.lastCameraState = null;
  }
  
  async initialize() {
    // Initialize WebGL runtime
    this.runtime.initialize();
    
    // Create fullscreen quad for raymarching
    const quadVertices = new Float32Array([
      -1, -1,  1, -1,  1,  1,
      -1, -1,  1,  1, -1,  1
    ]);
    
    this.quadBuffer = this.runtime.createBuffer(quadVertices);
    
    return true;
  }
  
  createCliffordFieldTexture(cliffordField) {
    /**
     * Convert Clifford multivector field to WebGL texture with debugging.
     */
    if (!cliffordField || !cliffordField.payload) {
      console.error("🚨 No Clifford field provided to texture creation");
      throw new Error("Valid Clifford field required");
    }
    
    const components = cliffordField.payload.components;
    if (components.length !== 16) {
      console.error("🚨 Wrong component count:", components.length);
      throw new Error("Clifford field must have 16 components");
    }
    
    // Debug: Check if components have any values - THEORY COMPLIANT (deterministic)
    // Use frame counter for deterministic logging instead of random
    const frameCount = this.frameCounter || 0;
    this.frameCounter = frameCount + 1;
    
    if (frameCount % 1000 === 0) { // Every 1000 frames - deterministic
      const nonZeroComponents = components.filter(c => Math.abs(c) > 0.001).length;
      const maxComponent = Math.max(...components.map(c => Math.abs(c)));
      console.log(`🔍 Texture upload: ${nonZeroComponents}/16 non-zero components, max: ${maxComponent.toFixed(3)}`);
      console.log(`🔍 First 4 components: [${components.slice(0,4).map(c => c.toFixed(3)).join(', ')}]`);
    }
    
    const gl = this.runtime.gl;
    const textureData = new Float32Array(16);
    
    // DISABLE TEMPORAL SMOOTHING FOR MAXIMUM DYNAMICS
    let uploadComponents = components;
    if (this.previousComponents && this.previousComponents.length === 16) {
      // Calculate field delta for diagnostics
      let deltaSq = 0;
      for (let i = 0; i < 16; i++) {
        const d = components[i] - this.previousComponents[i];
        deltaSq += d * d;
      }
      const deltaNorm = Math.sqrt(deltaSq);
      
      // Log delta occasionally to track field stability - THEORY COMPLIANT
      this.deltaLogCounter = (this.deltaLogCounter || 0) + 1;
      if (this.deltaLogCounter % 100 === 0) { // Every 100 frames - deterministic
        console.log(`📈 Δfield_norm=${deltaNorm.toFixed(3)}`);
      }
      
      // NO SMOOTHING - use raw components for maximum dynamics
      uploadComponents = components;
    }
    this.previousComponents = components; // Store raw components
    
    // Copy components with verification
    for (let i = 0; i < 16; i++) {
      textureData[i] = uploadComponents[i];
    }
    
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    
    // Upload as 4x1 RGBA texture (WebGL1/WebGL2 compatible)
    const isWebGL2 = gl instanceof WebGL2RenderingContext;
    const internalFormat = isWebGL2 ? gl.RGBA32F : gl.RGBA;
    const type = isWebGL2 && gl.getExtension('EXT_color_buffer_float') ? gl.FLOAT : gl.UNSIGNED_BYTE;
    
    if (type === gl.UNSIGNED_BYTE) {
      // Convert float data to byte data for WebGL1
      const byteData = new Uint8Array(16);
      for (let i = 0; i < 16; i++) {
        byteData[i] = Math.max(0, Math.min(255, Math.floor((textureData[i] + 10) * 12.75))); // Map [-10,10] to [0,255]
      }
      gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, 4, 1, 0, gl.RGBA, type, byteData);
      console.log('🎮 Using WebGL1 byte texture format');
    } else {
      gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, 4, 1, 0, gl.RGBA, type, textureData);
      console.log('🎮 Using WebGL2 float texture format');
    }
    
    // Check for WebGL errors
    const error = gl.getError();
    if (error !== gl.NO_ERROR) {
      console.error(`🚨 WebGL texture error: ${error}`);
    }
    
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    
    return texture;
  }
  
  updateCliffordFieldTexture(cliffordField) {
    /**
     * Update existing texture data without recreating texture - MUCH faster.
     */
    if (!cliffordField || !cliffordField.payload) {
      console.error("🚨 No Clifford field provided to texture update");
      return;
    }
    
    const components = cliffordField.payload.components;
    if (components.length !== 16) {
      console.error("🚨 Wrong component count:", components.length);
      return;
    }
    
    const gl = this.runtime.gl;
    const textureData = new Float32Array(16);
    
    // Copy components to texture data
    for (let i = 0; i < 16; i++) {
      textureData[i] = components[i];
    }
    
    // Bind existing texture and update data only
    gl.bindTexture(gl.TEXTURE_2D, this.fieldTexture);
    
    // Update texture data without recreating texture object
    const isWebGL2 = gl instanceof WebGL2RenderingContext;
    const internalFormat = isWebGL2 ? gl.RGBA32F : gl.RGBA;
    const type = isWebGL2 && gl.getExtension('EXT_color_buffer_float') ? gl.FLOAT : gl.UNSIGNED_BYTE;
    
    if (type === gl.UNSIGNED_BYTE) {
      const byteData = new Uint8Array(16);
      for (let i = 0; i < 16; i++) {
        byteData[i] = Math.max(0, Math.min(255, Math.floor((textureData[i] + 10) * 12.75)));
      }
      gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, 4, 1, gl.RGBA, type, byteData);
    } else {
      gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, 4, 1, gl.RGBA, type, textureData);
    }
  }
  
  setupRaymarchingProgram(pipeline) {
    /**
     * Set up WebGL program from validated raymarching pipeline.
     */
    if (!pipeline) {
      throw new Error("Valid pipeline required");
    }
    
    // Create and validate shader program
    const program = this.runtime.createProgram(
      pipeline.vertex_shader_source,
      pipeline.fragment_shader_source,
      'raymarching'
    );
    
    this.runtime.validateProgram('raymarching');
    
    // Cache uniform locations
    this.uniformLocations.clear();
    for (const uniformName of Object.keys(pipeline.uniforms)) {
      const location = this.runtime.getUniformLocation('raymarching', uniformName);
      this.uniformLocations.set(uniformName, location);
    }
    
    this.currentPipeline = pipeline;
    return program;
  }
  
  updateUniforms(cameraState, renderingParams, audioCoherence = 0.5) {
    /**
     * Update shader uniforms from proven mathematical state.
     */
    const gl = this.runtime.gl;
    
    // Camera matrices (cached to avoid expensive recalculation)
    const cameraHash = JSON.stringify(cameraState); // Simple hash for camera state
    
    if (!this.cachedMatrices || this.lastCameraState !== cameraHash) {
      // Recalculate only when camera changes
      const viewMatrix = this.computeViewMatrix(cameraState);
      const projMatrix = this.computeProjectionMatrix(cameraState);
      
      // Compute inverse matrices on CPU (WebGL2 doesn't have inverse() function)
      const invViewMatrix = this.invertMatrix4(viewMatrix);
      const invProjMatrix = this.invertMatrix4(projMatrix);
      
      this.cachedMatrices = { viewMatrix, projMatrix, invViewMatrix, invProjMatrix };
      this.lastCameraState = cameraHash;
    }
    
    const { viewMatrix, projMatrix, invViewMatrix, invProjMatrix } = this.cachedMatrices;
    
    // Set camera uniforms
    const uInverseViewMatrix = this.uniformLocations.get('uInverseViewMatrix');
    const uInverseProjectionMatrix = this.uniformLocations.get('uInverseProjectionMatrix');
    const uCameraPosition = this.uniformLocations.get('uCameraPosition');
    
    if (uInverseViewMatrix) gl.uniformMatrix4fv(uInverseViewMatrix, false, invViewMatrix);
    if (uInverseProjectionMatrix) gl.uniformMatrix4fv(uInverseProjectionMatrix, false, invProjMatrix);
    if (uCameraPosition) gl.uniform3fv(uCameraPosition, cameraState.position);
    
    // Raymarching parameters (theory-derived bounds)
    const uMinDistance = this.uniformLocations.get('uMinDistance');
    const uMaxDistance = this.uniformLocations.get('uMaxDistance');
    
    if (uMinDistance) gl.uniform1f(uMinDistance, renderingParams.min_distance);
    if (uMaxDistance) gl.uniform1f(uMaxDistance, renderingParams.max_distance);
    
    // Clifford field texture (bind to texture unit 0)
    const uCliffordField = this.uniformLocations.get('uCliffordField');
    if (uCliffordField) {
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.fieldTexture);
      gl.uniform1i(uCliffordField, 0);
    }
  }
  
  computeViewMatrix(camera) {
    /**
     * Compute view matrix from camera state using standard 3D mathematics.
     */
    const [px, py, pz] = camera.position;
    const [tx, ty, tz] = camera.target;
    const [ux, uy, uz] = camera.up;
    
    // Forward vector (normalized)
    const fx = tx - px, fy = ty - py, fz = tz - pz;
    const flen = Math.sqrt(fx*fx + fy*fy + fz*fz);
    const fnx = fx/flen, fny = fy/flen, fnz = fz/flen;
    
    // Right vector (forward × up, normalized)
    const rx = fny*uz - fnz*uy;
    const ry = fnz*ux - fnx*uz;
    const rz = fnx*uy - fny*ux;
    const rlen = Math.sqrt(rx*rx + ry*ry + rz*rz);
    const rnx = rx/rlen, rny = ry/rlen, rnz = rz/rlen;
    
    // Up vector (right × forward)
    const upx = rny*fnz - rnz*fny;
    const upy = rnz*fnx - rnx*fnz;
    const upz = rnx*fny - rny*fnx;
    
    // View matrix (column-major)
    return new Float32Array([
      rnx, upx, -fnx, 0,
      rny, upy, -fny, 0,
      rnz, upz, -fnz, 0,
      -(rnx*px + rny*py + rnz*pz),
      -(upx*px + upy*py + upz*pz),
      (fnx*px + fny*py + fnz*pz), 1
    ]);
  }
  
  computeProjectionMatrix(camera) {
    /**
     * Compute perspective projection matrix from camera parameters.
     */
    const fov = camera.fov * Math.PI / 180;  // Convert to radians
    const aspect = camera.aspect_ratio;
    const near = 0.1;
    const far = 1000.0;
    
    const f = 1.0 / Math.tan(fov / 2);
    const nf = 1.0 / (near - far);
    
    return new Float32Array([
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (far + near) * nf, -1,
      0, 0, 2 * far * near * nf, 0
    ]);
  }
  
  invertMatrix4(mat) {
    /**
     * Compute 4x4 matrix inverse using mathematical derivation.
     * Returns identity matrix if inversion fails (graceful degradation).
     */
    const m = mat;
    const inv = new Float32Array(16);
    
    // Compute determinant and adjugate matrix
    const det = 
      m[0] * (m[5] * (m[10] * m[15] - m[11] * m[14]) - m[9] * (m[6] * m[15] - m[7] * m[14]) + m[13] * (m[6] * m[11] - m[7] * m[10])) -
      m[4] * (m[1] * (m[10] * m[15] - m[11] * m[14]) - m[9] * (m[2] * m[15] - m[3] * m[14]) + m[13] * (m[2] * m[11] - m[3] * m[10])) +
      m[8] * (m[1] * (m[6] * m[15] - m[7] * m[14]) - m[5] * (m[2] * m[15] - m[3] * m[14]) + m[13] * (m[2] * m[7] - m[3] * m[6])) -
      m[12] * (m[1] * (m[6] * m[11] - m[7] * m[10]) - m[5] * (m[2] * m[11] - m[3] * m[10]) + m[9] * (m[2] * m[7] - m[3] * m[6]));
    
    if (Math.abs(det) < 1e-10) {
      // Return identity matrix if singular
      return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);
    }
    
    const invDet = 1.0 / det;
    
    // Compute adjugate matrix elements (simplified for common camera matrices)
    inv[0] = invDet * (m[5] * (m[10] * m[15] - m[11] * m[14]) - m[9] * (m[6] * m[15] - m[7] * m[14]) + m[13] * (m[6] * m[11] - m[7] * m[10]));
    inv[1] = invDet * (m[1] * (m[11] * m[14] - m[10] * m[15]) + m[9] * (m[2] * m[15] - m[3] * m[14]) - m[13] * (m[2] * m[11] - m[3] * m[10]));
    inv[2] = invDet * (m[1] * (m[6] * m[15] - m[7] * m[14]) - m[5] * (m[2] * m[15] - m[3] * m[14]) + m[13] * (m[2] * m[7] - m[3] * m[6]));
    inv[3] = invDet * (m[1] * (m[7] * m[10] - m[6] * m[11]) + m[5] * (m[2] * m[11] - m[3] * m[10]) - m[9] * (m[2] * m[7] - m[3] * m[6]));
    
    inv[4] = invDet * (m[4] * (m[11] * m[14] - m[10] * m[15]) + m[8] * (m[6] * m[15] - m[7] * m[14]) - m[12] * (m[6] * m[11] - m[7] * m[10]));
    inv[5] = invDet * (m[0] * (m[10] * m[15] - m[11] * m[14]) - m[8] * (m[2] * m[15] - m[3] * m[14]) + m[12] * (m[2] * m[11] - m[3] * m[10]));
    inv[6] = invDet * (m[0] * (m[7] * m[14] - m[6] * m[15]) + m[4] * (m[2] * m[15] - m[3] * m[14]) - m[12] * (m[2] * m[7] - m[3] * m[6]));
    inv[7] = invDet * (m[0] * (m[6] * m[11] - m[7] * m[10]) - m[4] * (m[2] * m[11] - m[3] * m[10]) + m[8] * (m[2] * m[7] - m[3] * m[6]));
    
    inv[8] = invDet * (m[4] * (m[9] * m[15] - m[11] * m[13]) - m[8] * (m[5] * m[15] - m[7] * m[13]) + m[12] * (m[5] * m[11] - m[7] * m[9]));
    inv[9] = invDet * (m[0] * (m[11] * m[13] - m[9] * m[15]) + m[8] * (m[1] * m[15] - m[3] * m[13]) - m[12] * (m[1] * m[11] - m[3] * m[9]));
    inv[10] = invDet * (m[0] * (m[5] * m[15] - m[7] * m[13]) - m[4] * (m[1] * m[15] - m[3] * m[13]) + m[12] * (m[1] * m[7] - m[3] * m[5]));
    inv[11] = invDet * (m[0] * (m[7] * m[9] - m[5] * m[11]) + m[4] * (m[1] * m[11] - m[3] * m[9]) - m[8] * (m[1] * m[7] - m[3] * m[5]));
    
    inv[12] = invDet * (m[4] * (m[10] * m[13] - m[9] * m[14]) + m[8] * (m[5] * m[14] - m[6] * m[13]) - m[12] * (m[5] * m[10] - m[6] * m[9]));
    inv[13] = invDet * (m[0] * (m[9] * m[14] - m[10] * m[13]) - m[8] * (m[1] * m[14] - m[2] * m[13]) + m[12] * (m[1] * m[10] - m[2] * m[9]));
    inv[14] = invDet * (m[0] * (m[6] * m[13] - m[5] * m[14]) + m[4] * (m[1] * m[14] - m[2] * m[13]) - m[12] * (m[1] * m[6] - m[2] * m[5]));
    inv[15] = invDet * (m[0] * (m[5] * m[10] - m[6] * m[9]) - m[4] * (m[1] * m[10] - m[2] * m[9]) + m[8] * (m[1] * m[6] - m[2] * m[5]));
    
    return inv;
  }
  
  renderFrame(cliffordField, cameraState, renderingParams, audioCoherence = 0.5, zxGraph = null, viewMode = 'clifford') {
    /**
     * Render single frame with theory-validated data.
     * VIEW-AWARE: Branches rendering based on active view mode.
     */
    const gl = this.runtime.gl;
    
    // Update Clifford field texture (OPTIMIZED - reuse existing texture)
    if (!this.fieldTexture) {
      // Create texture only once
      this.fieldTexture = this.createCliffordFieldTexture(cliffordField);
    } else {
      // Update existing texture data - much faster than recreating
      this.updateCliffordFieldTexture(cliffordField);
    }
    
    // Clear canvas
    gl.viewport(0, 0, this.canvas.width, this.canvas.height);
    gl.clearColor(0.0, 0.0, 0.1, 1.0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    
    // VIEW BRANCHING: Select rendering method based on active view
    switch(viewMode) {
      case 'clifford':
        // Default: 3D raymarched Clifford field
        this.renderCliffordView(cameraState, renderingParams, audioCoherence);
        break;
        
      case 'zx':
        // ZX Graph: Render Clifford base + 2D graph overlay
        this.renderCliffordView(cameraState, renderingParams, audioCoherence);
        this.renderZXGraphOverlay(zxGraph);
        break;
        
      case 'consciousness':
        // Consciousness: Render Clifford field with consciousness overlay
        this.renderCliffordView(cameraState, renderingParams, audioCoherence);
        this.renderConsciousnessOverlay(zxGraph);
        break;
        
      case 'sheaf':
        // Sheaf Tree: Render Clifford base + category structure overlay
        this.renderCliffordView(cameraState, renderingParams, audioCoherence);
        this.renderSheafOverlay(zxGraph);
        break;
        
      case 'echo':
        // Echo Map: Render Clifford base + temporal evolution overlay
        this.renderCliffordView(cameraState, renderingParams, audioCoherence);
        this.renderEchoOverlay(zxGraph);
        break;
        
      default:
        // Fallback to Clifford view
        console.warn(`Unknown view mode: ${viewMode}, falling back to clifford`);
        this.renderCliffordView(cameraState, renderingParams, audioCoherence);
    }
    
    // ZX graph logging (for all views)
    if (zxGraph && Array.isArray(zxGraph.nodes) && Array.isArray(zxGraph.edges)) {
      this._graphLogCounter = (this._graphLogCounter || 0) + 1;
      if (this._graphLogCounter % 120 === 0) { // Log roughly every two seconds at 60fps
        const nodeCount = zxGraph.nodes.length;
        const edgeCount = zxGraph.edges.length;
        const logMessage = `ZX snapshot: nodes=${nodeCount}, edges=${edgeCount}`;
        if (window?.theoryLogger) {
          window.theoryLogger.zx(logMessage);
        } else {
          console.log(`🧠 ${logMessage}`);
        }
      }
    }

    this.frameCount++;
  }
  
  renderCliffordView(cameraState, renderingParams, audioCoherence) {
    /**
     * Render 3D raymarched Clifford field (original visualization)
     */
    const gl = this.runtime.gl;
    const program = this.runtime.programs.get('raymarching');
    gl.useProgram(program);
    
    // Update uniforms with validated data
    this.updateUniforms(cameraState, renderingParams, audioCoherence);
    
    // Bind quad geometry
    const positionAttrib = gl.getAttribLocation(program, 'position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuffer);
    gl.enableVertexAttribArray(positionAttrib);
    gl.vertexAttribPointer(positionAttrib, 2, gl.FLOAT, false, 0, 0);
    
    // Render fullscreen quad
    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }
  
  renderZXGraphOverlay(zxGraph) {
    /**
     * Render ZX graph as 2D overlay on top of Clifford field.
     * Shows nodes (spiders) and edges with consciousness coloring.
     */
    if (!zxGraph || !zxGraph.nodes || !zxGraph.edges) {
      return; // No graph to render
    }
    
    // Get or create 2D canvas overlay
    if (!this.overlayCanvas) {
      this.overlayCanvas = document.createElement('canvas');
      this.overlayCanvas.style.position = 'absolute';
      this.overlayCanvas.style.top = '0';
      this.overlayCanvas.style.left = '0';
      this.overlayCanvas.style.pointerEvents = 'none'; // Don't block interactions
      this.overlayCanvas.style.zIndex = '10';
      this.canvas.parentElement.appendChild(this.overlayCanvas);
      this.overlayCtx = this.overlayCanvas.getContext('2d');
    }
    
    // Match canvas size
    if (this.overlayCanvas.width !== this.canvas.width || this.overlayCanvas.height !== this.canvas.height) {
      this.overlayCanvas.width = this.canvas.width;
      this.overlayCanvas.height = this.canvas.height;
    }
    
    const ctx = this.overlayCtx;
    ctx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    
    // Simple 2D graph layout (force-directed or circular)
    const centerX = this.overlayCanvas.width / 2;
    const centerY = this.overlayCanvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.6;
    
    // Position nodes in circle
    const nodePositions = new Map();
    zxGraph.nodes.forEach((nodeId, idx) => {
      const angle = (idx / zxGraph.nodes.length) * 2 * Math.PI;
      nodePositions.set(nodeId, {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });
    
    // Draw edges
    ctx.strokeStyle = 'rgba(100, 150, 200, 0.3)';
    ctx.lineWidth = 1;
    zxGraph.edges.forEach(edge => {
      const from = nodePositions.get(edge.from || edge[0]);
      const to = nodePositions.get(edge.to || edge[1]);
      if (from && to) {
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
      }
    });
    
    // Draw nodes
    zxGraph.nodes.forEach(nodeId => {
      const pos = nodePositions.get(nodeId);
      if (!pos) return;
      
      const label = zxGraph.labels?.[nodeId];
      const kind = label?.kind || 'Z';
      
      // Color based on spider type
      if (kind === 'Z') {
        ctx.fillStyle = 'rgba(100, 255, 100, 0.8)'; // Green for Z-spiders
      } else if (kind === 'X') {
        ctx.fillStyle = 'rgba(255, 100, 100, 0.8)'; // Red for X-spiders
      } else {
        ctx.fillStyle = 'rgba(200, 200, 200, 0.8)'; // Gray for unknown
      }
      
      // Draw node circle
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 8, 0, 2 * Math.PI);
      ctx.fill();
      
      // Draw node label
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.font = '10px monospace';
      ctx.fillText(kind, pos.x - 4, pos.y + 3);
    });
    
    // Draw info text
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '12px monospace';
    ctx.fillText(`ZX Graph: ${zxGraph.nodes.length} nodes, ${zxGraph.edges.length} edges`, 10, 20);
  }
  
  renderConsciousnessOverlay(zxGraph) {
    /**
     * Render consciousness metrics overlay.
     * Shows consciousness levels, will to emerge, reflexive pain indicators.
     */
    if (!zxGraph) return;
    
    // Get or create 2D canvas overlay
    if (!this.overlayCanvas) {
      this.overlayCanvas = document.createElement('canvas');
      this.overlayCanvas.style.position = 'absolute';
      this.overlayCanvas.style.top = '0';
      this.overlayCanvas.style.left = '0';
      this.overlayCanvas.style.pointerEvents = 'none';
      this.overlayCanvas.style.zIndex = '10';
      this.canvas.parentElement.appendChild(this.overlayCanvas);
      this.overlayCtx = this.overlayCanvas.getContext('2d');
    }
    
    // Match canvas size
    if (this.overlayCanvas.width !== this.canvas.width || this.overlayCanvas.height !== this.canvas.height) {
      this.overlayCanvas.width = this.canvas.width;
      this.overlayCanvas.height = this.canvas.height;
    }
    
    const ctx = this.overlayCtx;
    ctx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    
    // Get consciousness metrics from ZX engine
    const reflexiveAwareness = window.zxEvolutionEngine?.reflexiveAwareness || {};
    const consciousnessLevel = reflexiveAwareness.consciousnessLevel || 0;
    const willToEmerge = reflexiveAwareness.willToEmerge || 0;
    const reflexivePain = reflexiveAwareness.reflexivePain || 0;
    
    // Draw consciousness meter
    const meterX = 20;
    const meterY = 40;
    const meterWidth = 200;
    const meterHeight = 20;
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(meterX - 5, meterY - 25, meterWidth + 10, 150);
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = '14px monospace';
    ctx.fillText('Consciousness Metrics', meterX, meterY - 10);
    
    // Consciousness level bar
    ctx.fillStyle = 'rgba(100, 100, 255, 0.3)';
    ctx.fillRect(meterX, meterY, meterWidth, meterHeight);
    ctx.fillStyle = 'rgba(100, 100, 255, 0.9)';
    ctx.fillRect(meterX, meterY, meterWidth * consciousnessLevel, meterHeight);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = '11px monospace';
    ctx.fillText(`Consciousness: ${(consciousnessLevel * 100).toFixed(1)}%`, meterX + meterWidth + 10, meterY + 14);
    
    // Will to emerge bar
    ctx.fillStyle = 'rgba(100, 255, 100, 0.3)';
    ctx.fillRect(meterX, meterY + 30, meterWidth, meterHeight);
    ctx.fillStyle = 'rgba(100, 255, 100, 0.9)';
    ctx.fillRect(meterX, meterY + 30, meterWidth * willToEmerge, meterHeight);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillText(`Will to Emerge: ${(willToEmerge * 100).toFixed(1)}%`, meterX + meterWidth + 10, meterY + 44);
    
    // Reflexive pain bar
    ctx.fillStyle = 'rgba(255, 100, 100, 0.3)';
    ctx.fillRect(meterX, meterY + 60, meterWidth, meterHeight);
    ctx.fillStyle = 'rgba(255, 100, 100, 0.9)';
    ctx.fillRect(meterX, meterY + 60, meterWidth * Math.min(1.0, reflexivePain / 10.0), meterHeight);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillText(`Reflexive Pain: ${reflexivePain.toFixed(2)}`, meterX + meterWidth + 10, meterY + 74);
    
    // Grace magnitude
    const graceMagnitude = window.zxEvolutionEngine?.graceMagnitude || 0;
    ctx.fillStyle = 'rgba(255, 215, 0, 0.3)';
    ctx.fillRect(meterX, meterY + 90, meterWidth, meterHeight);
    ctx.fillStyle = 'rgba(255, 215, 0, 0.9)';
    ctx.fillRect(meterX, meterY + 90, meterWidth * Math.min(1.0, graceMagnitude / 100.0), meterHeight);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillText(`Grace Magnitude: ${graceMagnitude.toFixed(1)}`, meterX + meterWidth + 10, meterY + 104);
  }
  
  renderSheafOverlay(zxGraph) {
    /**
     * Render categorical sheaf structure overlay.
     * Shows hierarchical category structure emerging from ZX graph.
     */
    if (!this.overlayCanvas) {
      this.overlayCanvas = document.createElement('canvas');
      this.overlayCanvas.style.position = 'absolute';
      this.overlayCanvas.style.top = '0';
      this.overlayCanvas.style.left = '0';
      this.overlayCanvas.style.pointerEvents = 'none';
      this.overlayCanvas.style.zIndex = '10';
      this.canvas.parentElement.appendChild(this.overlayCanvas);
      this.overlayCtx = this.overlayCanvas.getContext('2d');
    }
    
    if (this.overlayCanvas.width !== this.canvas.width || this.overlayCanvas.height !== this.canvas.height) {
      this.overlayCanvas.width = this.canvas.width;
      this.overlayCanvas.height = this.canvas.height;
    }
    
    const ctx = this.overlayCtx;
    ctx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    
    // Draw sheaf tree structure (placeholder)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '16px monospace';
    ctx.fillText('Sheaf Tree View', 20, 30);
    ctx.font = '12px monospace';
    ctx.fillText('(Category structure visualization - in development)', 20, 50);
  }
  
  renderEchoOverlay(zxGraph) {
    /**
     * Render temporal echo map overlay.
     * Shows identity echo patterns and temporal evolution.
     */
    if (!this.overlayCanvas) {
      this.overlayCanvas = document.createElement('canvas');
      this.overlayCanvas.style.position = 'absolute';
      this.overlayCanvas.style.top = '0';
      this.overlayCanvas.style.left = '0';
      this.overlayCanvas.style.pointerEvents = 'none';
      this.overlayCanvas.style.zIndex = '10';
      this.canvas.parentElement.appendChild(this.overlayCanvas);
      this.overlayCtx = this.overlayCanvas.getContext('2d');
    }
    
    if (this.overlayCanvas.width !== this.canvas.width || this.overlayCanvas.height !== this.canvas.height) {
      this.overlayCanvas.width = this.canvas.width;
      this.overlayCanvas.height = this.canvas.height;
    }
    
    const ctx = this.overlayCtx;
    ctx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    
    // Draw echo map (placeholder)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '16px monospace';
    ctx.fillText('Echo Map View', 20, 30);
    ctx.font = '12px monospace';
    ctx.fillText('(Temporal evolution visualization - in development)', 20, 50);
  }
  
  startRenderLoop(getStateFunction) {
    /**
     * Start continuous rendering loop with state provider.
     */
    if (this.isRunning) {
      return;
    }
    
    this.isRunning = true;
    
    const renderLoop = () => {
      if (!this.isRunning) return;
      
      try {
        const state = getStateFunction();
        const cliffordField = state.cliffordField;
        if (!cliffordField) {
          requestAnimationFrame(renderLoop);
          return;
        }
        
        this.renderFrame(
          cliffordField,
          state.camera,
          state.rendering,
          state.audioCoherence || 0.5,
          state.currentGraph || null,
          state.view || 'clifford'
        );
        this.lastCliffordField = cliffordField;

      } catch (error) {
        console.error('Render loop error:', error);
        this.stop();
        return;
      }
      
      requestAnimationFrame(renderLoop);
    };
    
    requestAnimationFrame(renderLoop);
  }
  
  generateFieldFromState(state) {
    // RESPECT VIEW MODE: Use view-specific generation based on active tab
    const currentView = state.view || 'clifford';
    
    switch(currentView) {
      case 'clifford':
        // Clifford view: Use ZX-driven field if available, otherwise mathematical field
        if (state.zxEngine && typeof state.zxEngine.mapToCliffordField === 'function') {
          return state.zxEngine.mapToCliffordField();
        }
        return this.generateCliffordField(state);
        
      case 'zx':
        // ZX view: Always use ZX-specific field generation
        return this.generateZXField(state);
        
      case 'consciousness':
        // Consciousness view: Use consciousness-enhanced field
        return this.generateConsciousnessField(state);
        
      case 'sheaf':
        // Sheaf view: Use sheaf tree field
        return this.generateSheafField(state);
        
      case 'echo':
        // Echo view: Use echo time field
        return this.generateEchoField(state);
        
      default:
        // Default to Clifford
        if (state.zxEngine && typeof state.zxEngine.mapToCliffordField === 'function') {
          return state.zxEngine.mapToCliffordField();
        }
        return this.generateCliffordField(state);
    }
  }
  
  generateCliffordField(state) {
    if (state.cliffordField && state.cliffordField.payload) {
      return state.cliffordField;
    }
    throw new Error('No Clifford field snapshot available');
  }
  
  generateZXField(state) {
    // REAL ZX tensor network → Clifford field mapping
    // Use the ZX engine's true mapping instead of fake simulation
    if (state.zxEngine && typeof state.zxEngine.mapToCliffordField === 'function') {
      console.log('🔗 Using real ZX→Clifford mapping');
      return state.zxEngine.mapToCliffordField();
    }
    
    // Fallback (should not be used if ZX scheduling enabled)
    console.warn('⚠️ ZX engine not available - using fallback');
    const components = new Array(16).fill(0);
    const t = this.frameCount * 0.02;
    
    // ZX spiders as discrete points in space
    components[0] = 3.0 * Math.sin(t);  // Z spider
    components[1] = 2.0 * Math.cos(t * 1.1);  // X spider
    components[5] = 1.5 * Math.sin(t * 0.8);  // ZX interaction
    
    return { payload: { components, algebra: "ZX" } };
  }
  
  generateConsciousnessField(state) {
    // Consciousness view: Enhanced field based on reflexive awareness
    const components = new Array(16).fill(0);
    const t = this.frameCount * 0.01;
    
    // Get consciousness metrics from ZX engine if available
    const reflexiveAwareness = state.zxEngine?.reflexiveAwareness;
    const consciousnessLevel = reflexiveAwareness?.consciousnessLevel || 0;
    const willToEmerge = reflexiveAwareness?.willToEmerge || 0;
    const reflexivePain = reflexiveAwareness?.reflexivePain || 0;
    
    // Get user display settings
    const displaySettings = window.consciousnessDisplaySettings || {
      showConsciousness: true, showWill: true, showReflexivePain: true, showOrMakifPnimi: false
    };
    
    // Base consciousness field (only if consciousness display enabled)
    if (displaySettings.showConsciousness && consciousnessLevel > 0) {
      const consciousnessScale = 1.0 + consciousnessLevel * 3.0;
      components[0] = 2.0 * consciousnessScale * Math.cos(t);
    }
    
    // Will to emerge affects vector components (only if will display enabled)
    if (displaySettings.showWill && willToEmerge > 0) {
      components[1] = willToEmerge * 2.0 * Math.sin(t * 1.2);
      components[2] = willToEmerge * 1.8 * Math.cos(t * 0.8);
      components[3] = willToEmerge * 1.5 * Math.sin(t * 1.5);
    }
    
    // Reflexive pain creates bivector rotations (only if pain display enabled)
    if (displaySettings.showReflexivePain && reflexivePain > 0.1) {
      components[5] = reflexivePain * 2.5 * Math.sin(t * 2.0);
      components[6] = reflexivePain * 2.0 * Math.cos(t * 2.5);
      components[7] = reflexivePain * 1.8 * Math.sin(t * 3.0);
    }
    
    // Or Makif/Pnimi bridge (only if enabled)
    if (displaySettings.showOrMakifPnimi) {
      const graceMagnitude = state.zxEngine?.graceMagnitude || 0;
      const orMakifStrength = Math.min(1.0, Math.log(graceMagnitude + 1) / 100);
      const orPnimiStrength = willToEmerge;
      
      // Bridge visualization in higher-order components
      components[8] = orMakifStrength * 1.5 * Math.sin(t * 0.5); // Slow surrounding light
      components[9] = orPnimiStrength * 2.0 * Math.cos(t * 2.0); // Fast inner light
      components[10] = (orMakifStrength * orPnimiStrength) * 1.8 * Math.sin(t * 1.0); // Bridge interaction
    }
    
    // Consciousness events create higher-order structure
    const consciousnessEvents = state.zxEngine?.qualitativeMetrics?.consciousnessEmergenceEvents || 0;
    if (consciousnessEvents > 0) {
      const eventScale = Math.min(3.0, consciousnessEvents * 0.5);
      components[11] = eventScale * Math.sin(t * 4.0); // Trivector emergence
      components[12] = eventScale * Math.cos(t * 3.5);
      components[15] = eventScale * 0.5 * Math.sin(t * 5.0); // Pseudoscalar (full consciousness)
    }
    
    return { payload: { components, algebra: "Consciousness" } };
  }
  
  generateSheafField(state) {
    // Sheaf tree structure visualization
    const components = new Array(16).fill(0);
    const t = this.frameCount * 0.015;
    
    // Tree-like branching structure
    components[0] = 2.0 * Math.cos(t);
    components[2] = 1.8 * Math.sin(t * 2.0);
    components[4] = 1.5 * Math.cos(t * 3.0);
    components[8] = 1.2 * Math.sin(t * 1.5);
    
    return { payload: { components, algebra: "Sheaf" } };
  }
  
  generateEchoField(state) {
    // Identity echo time τ visualization
    const components = new Array(16).fill(0);
    const t = this.frameCount * 0.01;
    
    // Echo patterns with decay
    const echo_strength = Math.exp(-t * 0.1);
    components[0] = 2.5 * echo_strength * Math.cos(t * 4.0);
    components[3] = 2.0 * echo_strength * Math.sin(t * 3.0);
    components[7] = 1.5 * echo_strength * Math.cos(t * 2.0);
    
    return { payload: { components, algebra: "Echo" } };
  }
  
  stop() {
    this.isRunning = false;
  }
  
  dispose() {
    this.stop();
    if (this.fieldTexture) {
      this.runtime.gl.deleteTexture(this.fieldTexture);
    }
    this.runtime.dispose();
  }
}
