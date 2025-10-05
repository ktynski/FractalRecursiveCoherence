/**
 * e8_webgl_integration.js
 * 
 * WebGL shader-based E8 structure visualization
 * Integrates E8 topology directly into the raymarching pipeline
 */

window.E8WebGLRenderer = class {
  constructor(gl, shaderProgram) {
    this.gl = gl;
    this.shaderProgram = shaderProgram;
    
    // E8 parameters
    this.N = 21;
    this.dimension = 248;
    this.roots = 240;
    
    // Uniforms for E8 visualization
    this.uniforms = {
      uE8Dimension: null,
      uE8Roots: null,
      uShowE8Structure: null,
      uE8ProjectionMatrix: null,
      uSectorType: null,  // 0=EM, 1=DM, 2=DE
    };
    
    this.setupUniforms();
    this.generateE8ProjectionMatrix();
  }
  
  setupUniforms() {
    const gl = this.gl;
    const program = this.shaderProgram;
    
    // Get uniform locations
    this.uniforms.uE8Dimension = gl.getUniformLocation(program, 'uE8Dimension');
    this.uniforms.uE8Roots = gl.getUniformLocation(program, 'uE8Roots');
    this.uniforms.uShowE8Structure = gl.getUniformLocation(program, 'uShowE8Structure');
    this.uniforms.uE8ProjectionMatrix = gl.getUniformLocation(program, 'uE8ProjectionMatrix');
    this.uniforms.uSectorType = gl.getUniformLocation(program, 'uSectorType');
  }
  
  generateE8ProjectionMatrix() {
    // Create Coxeter projection matrix for E8 → 3D
    // This projects the 248D E8 structure to 3D while preserving key symmetries
    
    const matrix = new Float32Array(16);
    
    // Use golden ratio for optimal projection angles
    const phi = (1 + Math.sqrt(5)) / 2;
    const theta = Math.atan(1 / phi);
    
    // Rotation matrix for Coxeter projection
    const cos_t = Math.cos(theta);
    const sin_t = Math.sin(theta);
    
    // Build 4x4 projection matrix
    matrix[0] = cos_t;
    matrix[1] = 0;
    matrix[2] = sin_t;
    matrix[3] = 0;
    
    matrix[4] = 0;
    matrix[5] = 1;
    matrix[6] = 0;
    matrix[7] = 0;
    
    matrix[8] = -sin_t;
    matrix[9] = 0;
    matrix[10] = cos_t;
    matrix[11] = 0;
    
    matrix[12] = 0;
    matrix[13] = 0;
    matrix[14] = 0;
    matrix[15] = 1;
    
    this.projectionMatrix = matrix;
  }
  
  updateUniforms(showE8 = true, sectorType = 0) {
    const gl = this.gl;
    
    // Set E8 structure parameters
    if (this.uniforms.uE8Dimension) {
      gl.uniform1f(this.uniforms.uE8Dimension, this.dimension);
    }
    
    if (this.uniforms.uE8Roots) {
      gl.uniform1f(this.uniforms.uE8Roots, this.roots);
    }
    
    if (this.uniforms.uShowE8Structure) {
      gl.uniform1i(this.uniforms.uShowE8Structure, showE8 ? 1 : 0);
    }
    
    if (this.uniforms.uE8ProjectionMatrix) {
      gl.uniformMatrix4fv(this.uniforms.uE8ProjectionMatrix, false, this.projectionMatrix);
    }
    
    if (this.uniforms.uSectorType) {
      gl.uniform1i(this.uniforms.uSectorType, sectorType);
    }
  }
  
  getE8ShaderCode() {
    // Returns GLSL code for E8 structure in distance field
    return `
      // E8 Structure uniforms
      uniform float uE8Dimension;
      uniform float uE8Roots;
      uniform bool uShowE8Structure;
      uniform mat4 uE8ProjectionMatrix;
      uniform int uSectorType;
      
      // Project E8 lattice point to 3D
      vec3 projectE8Point(int rootIndex) {
        // Generate E8 root vector (simplified)
        float angle1 = float(rootIndex) * 2.0 * 3.14159 / uE8Roots;
        float angle2 = asin(2.0 * float(rootIndex) / uE8Roots - 1.0);
        
        // 8D coordinates (simplified representation)
        vec4 p8d_1 = vec4(
          cos(angle1) * cos(angle2),
          sin(angle1) * cos(angle2),
          sin(angle2),
          cos(angle1 + angle2)
        );
        
        vec4 p8d_2 = vec4(
          sin(angle1 + angle2),
          cos(angle2 * 2.0),
          sin(angle2 * 2.0),
          1.0
        );
        
        // Apply Coxeter projection
        vec4 proj1 = uE8ProjectionMatrix * p8d_1;
        vec3 point3d = proj1.xyz * 10.0;  // Scale for visibility
        
        return point3d;
      }
      
      // E8 lattice distance function
      float e8Distance(vec3 pos) {
        float minDist = 1000.0;
        
        // Sample key E8 lattice points
        // (In full implementation, would sample all 240 roots)
        for (int i = 0; i < 24; i++) {  // Simplified subset
          vec3 latticePoint = projectE8Point(i * 10);
          float dist = length(pos - latticePoint) - 0.5;  // Small spheres at lattice points
          minDist = min(minDist, dist);
        }
        
        // Add connections between points (E8 edges)
        for (int i = 0; i < 12; i++) {
          vec3 p1 = projectE8Point(i * 20);
          vec3 p2 = projectE8Point(i * 20 + 10);
          
          // Cylinder between points
          vec3 pa = pos - p1;
          vec3 ba = p2 - p1;
          float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
          float dist = length(pa - ba * h) - 0.1;  // Thin cylinders
          minDist = min(minDist, dist);
        }
        
        return minDist;
      }
      
      // Multi-sector universe topology
      float sectorTopology(vec3 pos, int sector) {
        if (sector == 0) {
          // Electromagnetic sector: Ring+Cross (N=21)
          float ring = length(pos.xy) - 5.0;
          float cross = min(abs(pos.x), abs(pos.y)) - 0.5;
          return min(ring, cross);
          
        } else if (sector == 1) {
          // Dark matter sector: Tree topology (N=105, no closed loops)
          float trunk = length(pos.xy) - 0.3;
          float branches = 1000.0;
          
          // Create tree branches (no loops!)
          for (int i = 0; i < 8; i++) {
            float angle = float(i) * 0.785;  // π/4 spacing
            vec3 branchDir = vec3(cos(angle), sin(angle), 0.3);
            vec3 branchStart = vec3(0.0, 0.0, float(i) * 0.5 - 2.0);
            vec3 pa = pos - branchStart;
            float t = clamp(dot(pa, branchDir), 0.0, 3.0);
            float branch = length(pa - branchDir * t) - 0.2;
            branches = min(branches, branch);
          }
          
          return min(trunk + abs(pos.z), branches);
          
        } else {
          // Dark energy sector: Random graph (maximum entropy)
          // Use noise function for chaotic structure
          float noise = sin(pos.x * 10.0) * cos(pos.y * 10.0) * sin(pos.z * 10.0);
          return length(pos) - 8.0 + noise * 2.0;
        }
      }
      
      // Integrate E8 structure into main distance field
      float addE8Structure(vec3 pos, float baseDist) {
        if (!uShowE8Structure) return baseDist;
        
        // E8 lattice structure
        float e8Dist = e8Distance(pos);
        
        // Multi-sector topology
        float sectorDist = sectorTopology(pos, uSectorType);
        
        // Combine with base distance field
        float combinedDist = min(baseDist, min(e8Dist * 0.3, sectorDist * 0.5));
        
        // Add mass generation visualization
        // Masses emerge at specific E8 symmetry breaking points
        float massField = 0.0;
        
        // Electron mass point (origin of mass scale)
        vec3 electronPoint = vec3(0.0, 0.0, 0.0);
        massField += 1.0 / (1.0 + length(pos - electronPoint));
        
        // Muon mass point (10×N - 3 = 207)
        vec3 muonPoint = projectE8Point(207);
        massField += 207.0 / (1.0 + length(pos - muonPoint));
        
        // Proton mass point (N×100 - 264 = 1836)
        vec3 protonPoint = projectE8Point(183);  // Modulo for visualization
        massField += 1836.0 / (1.0 + length(pos - protonPoint));
        
        // Modulate distance by mass field
        combinedDist -= massField * 0.001;
        
        return combinedDist;
      }
    `;
  }
  
  getE8ColoringCode() {
    // Returns GLSL code for E8-based coloring
    return `
      // E8-based coloring
      vec3 getE8Color(vec3 pos, vec3 baseColor) {
        if (!uShowE8Structure) return baseColor;
        
        vec3 color = baseColor;
        
        // Color based on proximity to E8 lattice
        float e8Dist = e8Distance(pos);
        if (e8Dist < 1.0) {
          // Near E8 lattice point - golden color
          color = mix(color, vec3(1.0, 0.843, 0.0), 1.0 - e8Dist);
        }
        
        // Color by sector
        if (uSectorType == 0) {
          // Electromagnetic - golden
          color *= vec3(1.0, 0.843, 0.0);
        } else if (uSectorType == 1) {
          // Dark matter - purple
          color *= vec3(0.541, 0.169, 0.886);
        } else {
          // Dark energy - deep blue
          color *= vec3(0.0, 0.0, 0.545);
        }
        
        // Add mass generation glow
        float massGlow = 0.0;
        
        // Check proximity to particle mass points
        vec3 electronPoint = vec3(0.0, 0.0, 0.0);
        vec3 muonPoint = projectE8Point(207);
        vec3 protonPoint = projectE8Point(183);
        
        massGlow += exp(-length(pos - electronPoint) * 0.5);
        massGlow += exp(-length(pos - muonPoint) * 0.3) * 2.0;
        massGlow += exp(-length(pos - protonPoint) * 0.2) * 3.0;
        
        // Add glow to color
        color += vec3(massGlow * 0.1, massGlow * 0.05, massGlow * 0.15);
        
        return color;
      }
    `;
  }
  
  injectE8Shaders(fragmentShaderSource) {
    // Inject E8 code into existing fragment shader
    
    // Find where to inject the E8 functions (before main())
    const mainIndex = fragmentShaderSource.indexOf('void main()');
    if (mainIndex === -1) return fragmentShaderSource;
    
    // Insert E8 shader code before main()
    const e8Code = this.getE8ShaderCode() + '\n' + this.getE8ColoringCode() + '\n';
    let modifiedShader = fragmentShaderSource.slice(0, mainIndex) + e8Code + fragmentShaderSource.slice(mainIndex);
    
    // Modify the distance sampling function to include E8
    modifiedShader = modifiedShader.replace(
      'return bireflection_distance',
      'return addE8Structure(pos, bireflection_distance)'
    );
    
    // Modify the coloring to include E8
    modifiedShader = modifiedShader.replace(
      'gl_FragColor = vec4(color, 1.0);',
      'gl_FragColor = vec4(getE8Color(rayPos, color), 1.0);'
    );
    
    return modifiedShader;
  }
}

// Multi-sector universe controller
window.MultiSectorController = class {
  constructor(e8Renderer) {
    this.e8Renderer = e8Renderer;
    this.currentSector = 0;  // 0=EM, 1=DM, 2=DE
    this.sectorNames = ['Electromagnetic', 'Dark Matter', 'Dark Energy'];
    this.setupUI();
  }
  
  setupUI() {
    // Create sector switching UI
    const container = document.createElement('div');
    container.id = 'sector-controls';
    container.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      background: rgba(0,0,0,0.8);
      padding: 15px;
      border-radius: 8px;
      border: 2px solid #00ff00;
      color: #00ff00;
      font-family: monospace;
      z-index: 1000;
    `;
    
    container.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 10px;">Universe Sector</div>
      <button id="sector-em" class="sector-btn" style="
        background: #333;
        color: gold;
        border: 1px solid gold;
        padding: 5px 10px;
        margin: 2px;
        cursor: pointer;
        font-family: monospace;
      ">EM (Ring+Cross)</button>
      <button id="sector-dm" class="sector-btn" style="
        background: #333;
        color: #8a2be2;
        border: 1px solid #8a2be2;
        padding: 5px 10px;
        margin: 2px;
        cursor: pointer;
        font-family: monospace;
      ">Dark Matter (Tree)</button>
      <button id="sector-de" class="sector-btn" style="
        background: #333;
        color: #00008b;
        border: 1px solid #00008b;
        padding: 5px 10px;
        margin: 2px;
        cursor: pointer;
        font-family: monospace;
      ">Dark Energy (Random)</button>
      <div style="margin-top: 10px; font-size: 0.9em;">
        Current: <span id="current-sector" style="color: gold;">${this.sectorNames[0]}</span>
      </div>
      <div style="margin-top: 5px; font-size: 0.8em; opacity: 0.7;">
        N = <span id="sector-nodes">21</span> nodes
      </div>
    `;
    
    document.body.appendChild(container);
    
    // Add event listeners
    document.getElementById('sector-em').addEventListener('click', () => this.switchSector(0));
    document.getElementById('sector-dm').addEventListener('click', () => this.switchSector(1));
    document.getElementById('sector-de').addEventListener('click', () => this.switchSector(2));
  }
  
  switchSector(sector) {
    this.currentSector = sector;
    this.e8Renderer.updateUniforms(true, sector);
    
    // Update UI
    const colors = ['gold', '#8a2be2', '#00008b'];
    const nodes = [21, 105, '10⁶⁸'];
    
    document.getElementById('current-sector').textContent = this.sectorNames[sector];
    document.getElementById('current-sector').style.color = colors[sector];
    document.getElementById('sector-nodes').textContent = nodes[sector];
    
    // Highlight active button
    document.querySelectorAll('.sector-btn').forEach((btn, i) => {
      btn.style.background = i === sector ? '#555' : '#333';
      btn.style.fontWeight = i === sector ? 'bold' : 'normal';
    });
    
    console.log(`Switched to ${this.sectorNames[sector]} sector`);
  }
}

// Auto-initialize if WebGL context exists
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('canvas');
  if (canvas) {
    const gl = canvas.getContext('webgl2');
    if (gl && window.renderer && window.renderer.shaderProgram) {
      console.log('Initializing E8 WebGL integration...');
      window.e8WebGLRenderer = new E8WebGLRenderer(gl, window.renderer.shaderProgram);
      window.multiSectorController = new MultiSectorController(window.e8WebGLRenderer);
      console.log('✅ E8 WebGL integration ready');
    }
  }
});

// Exported via window.E8WebGLRenderer
// export { E8WebGLRenderer, MultiSectorController };
