/**
 * e8_visualizer.js
 * 
 * E8 Lie Group Visualization and Physics Integration
 * ===================================================
 * 
 * Visualizes how N=21 Ring+Cross topology encodes E8's 248 dimensions.
 * Shows mass generation, alpha derivation, and multi-sector universe.
 */

class E8Visualizer {
  constructor(canvas, context = '2d') {
    this.canvas = canvas;
    this.ctx = context === '2d' ? canvas.getContext('2d') : null;
    this.gl = context === 'webgl' ? canvas.getContext('webgl2') : null;
    
    // E8 structure from physics_constants.js
    this.N = PHYSICS.N;
    this.dimension = PHYSICS.E8.DIMENSION;
    this.roots = PHYSICS.E8.ROOT_VECTORS;
    
    // Visual parameters
    this.time = 0;
    this.rotation = { x: 0, y: 0, z: 0 };
    this.zoom = 1.0;
    
    // Topology
    this.topology = createRingCross(this.N);
    this.particles = this.initializeParticles();
    
    // Animation state
    this.animating = false;
    this.showE8Projection = true;
    this.showMassGeneration = true;
    this.showAlphaFlow = true;
  }
  
  initializeParticles() {
    // Create particle representations at specific topology locations
    return {
      electron: {
        position: this.topology.nodes[0],
        mass: PHYSICS.MASSES.ELECTRON,
        color: [255, 255, 0],
        radius: 5
      },
      muon: {
        position: this.topology.nodes[5],
        mass: PHYSICS.MASSES.MUON,
        color: [255, 150, 0],
        radius: 8
      },
      proton: {
        position: this.topology.nodes[10],
        mass: PHYSICS.MASSES.PROTON_ELECTRON,
        color: [255, 0, 0],
        radius: 12
      },
      W: {
        position: this.topology.nodes[20], // Center
        mass: PHYSICS.MASSES.W_BOSON,
        color: [0, 200, 255],
        radius: 10
      },
      Z: {
        position: this.topology.nodes[20], // Center
        mass: PHYSICS.MASSES.Z_BOSON,
        color: [0, 100, 255],
        radius: 11
      },
      Higgs: {
        position: this.topology.nodes[20], // Center
        mass: PHYSICS.MASSES.HIGGS,
        color: [255, 255, 255],
        radius: 15
      }
    };
  }
  
  /**
   * Project E8 from 248D to 3D for visualization
   * Uses Coxeter projection for optimal symmetry display
   */
  projectE8To3D() {
    // E8 root system has 240 roots in 8D
    // We project to 3D using principal components
    
    const points = [];
    const goldenRatio = GOLDEN;
    
    // Generate E8 root positions (simplified)
    // In reality, these come from E8's root lattice
    for (let i = 0; i < this.roots; i++) {
      const theta = (i * 2 * PI) / this.roots;
      const phi = Math.asin(2 * i / this.roots - 1);
      
      // Coxeter-style projection
      const r = Math.sqrt(i / this.roots) * 100;
      
      points.push({
        x: r * Math.cos(theta) * Math.cos(phi),
        y: r * Math.sin(theta) * Math.cos(phi),
        z: r * Math.sin(phi),
        connection: i % this.N  // Which node it connects to
      });
    }
    
    return points;
  }
  
  /**
   * Visualize alpha emerging from topology
   */
  drawAlphaEmergence() {
    if (!this.ctx) return;
    
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Draw the formula
    ctx.save();
    ctx.font = '20px monospace';
    ctx.fillStyle = 'rgba(255, 215, 0, 0.9)';
    ctx.textAlign = 'center';
    
    if (this.N === 21) {
      ctx.fillText('α = 19g/(80π³k)', centerX, 30);
    } else {
      ctx.fillText('α = 3g/(4π⁴k)', centerX, 30);
    }
    
    // Show current calculated value
    const g = PHYSICS.ALPHA.COUPLING_G;
    const k = PHYSICS.ALPHA.KINETIC_K;
    const alpha = PHYSICS.ALPHA.calculate(g, k, this.N);
    
    ctx.font = '16px monospace';
    ctx.fillText(`= 1/${(1/alpha).toFixed(1)}`, centerX, 55);
    
    // Show error
    const error = Math.abs(alpha - PHYSICS.ALPHA.VALUE) / PHYSICS.ALPHA.VALUE * 100;
    ctx.fillStyle = error < 1 ? 'rgba(0, 255, 0, 0.8)' : 'rgba(255, 255, 0, 0.8)';
    ctx.fillText(`Error: ${error.toFixed(3)}%`, centerX, 80);
    
    ctx.restore();
  }
  
  /**
   * Draw the Ring+Cross topology with E8 structure
   */
  drawTopology() {
    if (!this.ctx) return;
    
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.3;
    
    ctx.save();
    
    // Apply rotation
    ctx.translate(centerX, centerY);
    ctx.rotate(this.rotation.y);
    ctx.scale(this.zoom, this.zoom);
    ctx.translate(-centerX, -centerY);
    
    // Draw edges
    ctx.strokeStyle = 'rgba(100, 150, 255, 0.5)';
    ctx.lineWidth = 2;
    
    for (const [i, j] of this.topology.edges) {
      const node1 = this.topology.nodes[i];
      const node2 = this.topology.nodes[j];
      
      if (!node1 || !node2) continue;
      
      let x1, y1, x2, y2;
      
      if (node1.type === 'ring') {
        const angle1 = (i * 2 * PI) / (this.N - 1);
        x1 = centerX + radius * Math.cos(angle1);
        y1 = centerY + radius * Math.sin(angle1);
      } else {
        x1 = centerX;
        y1 = centerY;
      }
      
      if (node2.type === 'ring') {
        const angle2 = (j * 2 * PI) / (this.N - 1);
        x2 = centerX + radius * Math.cos(angle2);
        y2 = centerY + radius * Math.sin(angle2);
      } else {
        x2 = centerX;
        y2 = centerY;
      }
      
      // Draw edge with phase coloring
      const phase = (node1.phase + node2.phase) / 2;
      const hue = (phase / (2 * PI)) * 360;
      ctx.strokeStyle = `hsla(${hue}, 70%, 50%, 0.6)`;
      
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }
    
    // Draw nodes
    for (let i = 0; i < this.topology.nodes.length; i++) {
      const node = this.topology.nodes[i];
      let x, y;
      
      if (node.type === 'ring') {
        const angle = (i * 2 * PI) / (this.N - 1);
        x = centerX + radius * Math.cos(angle);
        y = centerY + radius * Math.sin(angle);
      } else {
        x = centerX;
        y = centerY;
      }
      
      // Node color based on phase
      const hue = (node.phase / (2 * PI)) * 360;
      ctx.fillStyle = `hsla(${hue}, 80%, 60%, 1)`;
      
      ctx.beginPath();
      ctx.arc(x, y, node.type === 'center' ? 12 : 8, 0, 2 * PI);
      ctx.fill();
      
      // Draw node label
      ctx.fillStyle = 'white';
      ctx.font = '10px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(i.toString(), x, y);
    }
    
    ctx.restore();
  }
  
  /**
   * Show mass generation from topology
   */
  drawMassGeneration() {
    if (!this.ctx || !this.showMassGeneration) return;
    
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Draw particle masses
    ctx.save();
    ctx.font = '14px monospace';
    ctx.textAlign = 'left';
    
    let y = height - 150;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillText('Mass Generation (N=21):', 10, y);
    
    y += 20;
    for (const [name, particle] of Object.entries(this.particles)) {
      ctx.fillStyle = `rgb(${particle.color.join(',')})`;
      ctx.fillText(`${name}: ${particle.mass}`, 10, y);
      y += 18;
    }
    
    ctx.restore();
  }
  
  /**
   * Draw E8 projection overlay
   */
  drawE8Projection() {
    if (!this.ctx || !this.showE8Projection) return;
    
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Get E8 points
    const e8Points = this.projectE8To3D();
    
    ctx.save();
    ctx.globalAlpha = 0.3;
    
    // Draw E8 root connections
    ctx.strokeStyle = 'rgba(138, 43, 226, 0.2)'; // Purple for E8
    ctx.lineWidth = 0.5;
    
    for (let i = 0; i < e8Points.length; i++) {
      for (let j = i + 1; j < Math.min(i + 10, e8Points.length); j++) {
        const p1 = e8Points[i];
        const p2 = e8Points[j];
        
        // Project to 2D (simple orthographic)
        const x1 = centerX + p1.x * Math.cos(this.rotation.y) - p1.z * Math.sin(this.rotation.y);
        const y1 = centerY + p1.y;
        const x2 = centerX + p2.x * Math.cos(this.rotation.y) - p2.z * Math.sin(this.rotation.y);
        const y2 = centerY + p2.y;
        
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    }
    
    ctx.restore();
    
    // Show E8 info
    ctx.save();
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(138, 43, 226, 0.9)';
    ctx.textAlign = 'right';
    ctx.fillText(`E8: ${this.dimension}D`, width - 10, 30);
    ctx.fillText(`Roots: ${this.roots}`, width - 10, 45);
    ctx.fillText(`N×12-4 = ${this.N}×12-4 = ${this.dimension}`, width - 10, 60);
    ctx.restore();
  }
  
  /**
   * Animate the visualization
   */
  animate() {
    this.time += 0.01;
    this.rotation.y = Math.sin(this.time) * 0.5;
    this.rotation.x = Math.cos(this.time * 0.7) * 0.3;
    
    // Animate particle positions slightly
    for (const particle of Object.values(this.particles)) {
      if (particle.position.type === 'ring') {
        // Oscillate along ring
        particle.position.phase += Math.sin(this.time * 2) * 0.02;
      }
    }
    
    this.draw();
    
    if (this.animating) {
      requestAnimationFrame(() => this.animate());
    }
  }
  
  /**
   * Main draw function
   */
  draw() {
    if (!this.ctx) return;
    
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Dark background
    ctx.fillStyle = 'rgba(5, 5, 15, 1)';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Draw components
    this.drawE8Projection();
    this.drawTopology();
    this.drawAlphaEmergence();
    this.drawMassGeneration();
    
    // Draw title
    ctx.save();
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = 'rgba(255, 215, 0, 0.9)';
    ctx.textAlign = 'center';
    ctx.fillText('E8 → Ring+Cross → Reality', this.canvas.width / 2, this.canvas.height - 20);
    ctx.restore();
  }
  
  /**
   * Start animation
   */
  start() {
    this.animating = true;
    this.animate();
  }
  
  /**
   * Stop animation
   */
  stop() {
    this.animating = false;
  }
  
  /**
   * Handle mouse/touch interaction
   */
  handleInteraction(event) {
    // Implement rotation/zoom based on mouse/touch
    // This would connect to the existing UI controller
  }
}

// Export for use in main.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = E8Visualizer;
}
