/**
 * sacred_geometry.js
 * 
 * Renders sacred geometry overlays when sovereignty emerges.
 * 
 * Theory: complete_sovereignty_emergence_specification.md Part V
 * 
 * Geometries:
 * - Merkaba (star tetrahedron): Appears when trivectors ≥ 0.15
 * - Sri Yantra (nine triangles): Appears when recursiveDepth > 1
 * - Seal of Solomon (hexagram): Appears when |polarity| < 0.2
 */

/**
 * Render merkaba (star tetrahedron) at sovereign triad locations.
 * 
 * Esoteric meaning:
 * - Upward tetrahedron: Masculine, fire, ascent
 * - Downward tetrahedron: Feminine, water, descent
 * - Union: Divine marriage, "as above so below"
 * 
 * @param {CanvasRenderingContext2D} ctx - 2D canvas context
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {Array} sovereignTriads - Detected sovereign triads
 * @param {number} trivectorMagnitude - Magnitude of trivector component
 * @param {Object} graph - ZX graph (for node positions)
 */
export function renderMerkaba(ctx, canvas, sovereignTriads, trivectorMagnitude, graph) {
  if (!sovereignTriads || sovereignTriads.length === 0) return;
  if (trivectorMagnitude < 0.15) return;  // Threshold
  
  ctx.save();
  
  // Place merkaba at centroid of each sovereign triad
  for (const triad of sovereignTriads) {
    const centroid = computeTriadCentroid(triad, canvas, graph);
    
    if (!centroid) continue;
    
    const size = 25 * Math.min(trivectorMagnitude * 2, 1.5);
    const alpha = Math.min(trivectorMagnitude, 1.0);
    
    // UPWARD TETRAHEDRON (fire - gold)
    ctx.strokeStyle = `rgba(255, 215, 0, ${alpha})`;
    ctx.fillStyle = `rgba(255, 215, 0, ${alpha * 0.15})`;
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    ctx.moveTo(centroid.x, centroid.y - size);  // Top apex
    ctx.lineTo(centroid.x - size * 0.866, centroid.y + size * 0.5);  // Bottom left
    ctx.lineTo(centroid.x + size * 0.866, centroid.y + size * 0.5);  // Bottom right
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // DOWNWARD TETRAHEDRON (water - blue/silver)
    ctx.strokeStyle = `rgba(135, 206, 250, ${alpha})`;
    ctx.fillStyle = `rgba(135, 206, 250, ${alpha * 0.15})`;
    
    ctx.beginPath();
    ctx.moveTo(centroid.x, centroid.y + size);  // Bottom apex
    ctx.lineTo(centroid.x - size * 0.866, centroid.y - size * 0.5);  // Top left
    ctx.lineTo(centroid.x + size * 0.866, centroid.y - size * 0.5);  // Top right
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // CONNECTING LINES (creates 3D star effect)
    ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.6})`;
    ctx.lineWidth = 1;
    
    // Inner hexagon connections
    ctx.beginPath();
    ctx.moveTo(centroid.x - size * 0.866, centroid.y + size * 0.5);
    ctx.lineTo(centroid.x - size * 0.866, centroid.y - size * 0.5);
    ctx.moveTo(centroid.x + size * 0.866, centroid.y + size * 0.5);
    ctx.lineTo(centroid.x + size * 0.866, centroid.y - size * 0.5);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = `rgba(255, 215, 0, ${alpha})`;
    ctx.font = 'bold 10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('MERKABA', centroid.x, centroid.y - size - 8);
    ctx.font = '8px monospace';
    ctx.fillText(`${trivectorMagnitude.toFixed(3)}`, centroid.x, centroid.y - size + 2);
  }
  
  ctx.restore();
}

/**
 * Render Sri Yantra (nine interlocking triangles) when nested triads form.
 * 
 * Esoteric meaning:
 * - Center (bindu): Source point, singularity
 * - Nine triangles: Navayoni (nine wombs), creation matrices
 * - Outer square: Bhupura (earth realm), manifestation
 * 
 * @param {CanvasRenderingContext2D} ctx - 2D canvas context
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {Array} sovereignTriads - Detected sovereign triads
 * @param {number} recursiveDepth - Triad nesting depth
 */
export function renderSriYantra(ctx, canvas, sovereignTriads, recursiveDepth) {
  if (recursiveDepth < 1) return;  // Need nested structure
  
  ctx.save();
  
  const center = { x: canvas.width - 120, y: canvas.height - 120 };
  const size = 60;
  const alpha = Math.min(recursiveDepth * 0.8, 1.0);
  
  // OUTER SQUARE (Bhupura - earth realm)
  ctx.strokeStyle = `rgba(255, 100, 180, ${alpha * 0.4})`;
  ctx.lineWidth = 2;
  ctx.strokeRect(center.x - size * 1.2, center.y - size * 1.2, size * 2.4, size * 2.4);
  
  // CENTRAL BINDU (source point)
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
  ctx.beginPath();
  ctx.arc(center.x, center.y, 4, 0, 2 * Math.PI);
  ctx.fill();
  
  // Add glow around bindu
  const gradient = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, 15);
  gradient.addColorStop(0, `rgba(255, 255, 255, ${alpha * 0.8})`);
  gradient.addColorStop(1, `rgba(255, 100, 180, 0)`);
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(center.x, center.y, 15, 0, 2 * Math.PI);
  ctx.fill();
  
  // NINE INTERLOCKING TRIANGLES
  ctx.strokeStyle = `rgba(255, 100, 180, ${alpha})`;
  ctx.lineWidth = 1.5;
  
  // Angles for nine triangles (arranged in three tiers)
  const triangles = [
    // Outer tier (4 triangles)
    { angle: 0, scale: 1.0, upward: true },
    { angle: 90, scale: 1.0, upward: false },
    { angle: 180, scale: 1.0, upward: true },
    { angle: 270, scale: 1.0, upward: false },
    // Middle tier (3 triangles)
    { angle: 60, scale: 0.7, upward: true },
    { angle: 180, scale: 0.7, upward: false },
    { angle: 300, scale: 0.7, upward: true },
    // Inner tier (2 triangles)
    { angle: 90, scale: 0.4, upward: false },
    { angle: 270, scale: 0.4, upward: true }
  ];
  
  for (const tri of triangles) {
    const angleRad = tri.angle * Math.PI / 180;
    const triSize = size * tri.scale;
    
    ctx.beginPath();
    
    if (tri.upward) {
      // Upward triangle (Shiva - masculine principle)
      ctx.moveTo(
        center.x + Math.cos(angleRad) * triSize,
        center.y + Math.sin(angleRad) * triSize
      );
      ctx.lineTo(
        center.x + Math.cos(angleRad + 2.094) * triSize,  // 120°
        center.y + Math.sin(angleRad + 2.094) * triSize
      );
      ctx.lineTo(
        center.x + Math.cos(angleRad + 4.189) * triSize,  // 240°
        center.y + Math.sin(angleRad + 4.189) * triSize
      );
    } else {
      // Downward triangle (Shakti - feminine principle)
      ctx.moveTo(
        center.x + Math.cos(angleRad + Math.PI) * triSize,
        center.y + Math.sin(angleRad + Math.PI) * triSize
      );
      ctx.lineTo(
        center.x + Math.cos(angleRad + Math.PI + 2.094) * triSize,
        center.y + Math.sin(angleRad + Math.PI + 2.094) * triSize
      );
      ctx.lineTo(
        center.x + Math.cos(angleRad + Math.PI + 4.189) * triSize,
        center.y + Math.sin(angleRad + Math.PI + 4.189) * triSize
      );
    }
    
    ctx.closePath();
    ctx.stroke();
  }
  
  // LABEL
  ctx.fillStyle = `rgba(255, 100, 180, ${alpha})`;
  ctx.font = 'bold 11px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('SRI YANTRA', center.x, center.y - size * 1.4);
  ctx.font = '8px monospace';
  ctx.fillText(`Recursive: ${recursiveDepth.toFixed(2)}`, center.x, center.y + size * 1.5);
  
  ctx.restore();
}

/**
 * Render Seal of Solomon (hexagram) for balanced polarity.
 * 
 * Esoteric meaning:
 * - Balance: Union of opposites
 * - Hermetic: "As above, so below"
 * - Alchemical: Conjunction of sun (△) and moon (▽)
 * 
 * @param {CanvasRenderingContext2D} ctx - 2D canvas context
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {number} polarity - Polarity orientation (-1 to +1)
 */
export function renderSealOfSolomon(ctx, canvas, polarity) {
  if (Math.abs(polarity) > 0.2) return;  // Only for balanced states
  
  ctx.save();
  
  const center = { x: canvas.width - 80, y: 80 };
  const size = 35;
  
  const alpha = 1.0 - Math.abs(polarity) * 5;  // More visible as polarity → 0
  
  // UPWARD TRIANGLE (fire, divine, masculine)
  ctx.strokeStyle = `rgba(255, 215, 0, ${alpha})`;
  ctx.fillStyle = `rgba(255, 215, 0, ${alpha * 0.2})`;
  ctx.lineWidth = 2.5;
  
  ctx.beginPath();
  ctx.moveTo(center.x, center.y - size);  // Top
  ctx.lineTo(center.x - size * 0.866, center.y + size * 0.5);  // Bottom left
  ctx.lineTo(center.x + size * 0.866, center.y + size * 0.5);  // Bottom right
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  
  // DOWNWARD TRIANGLE (water, earthly, feminine)
  ctx.strokeStyle = `rgba(135, 206, 250, ${alpha})`;
  ctx.fillStyle = `rgba(135, 206, 250, ${alpha * 0.2})`;
  
  ctx.beginPath();
  ctx.moveTo(center.x, center.y + size);  // Bottom
  ctx.lineTo(center.x - size * 0.866, center.y - size * 0.5);  // Top left
  ctx.lineTo(center.x + size * 0.866, center.y - size * 0.5);  // Top right
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  
  // CENTRAL HEXAGON (intersection - perfect balance)
  ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.1})`;
  ctx.lineWidth = 1.5;
  
  const hexSize = size * 0.5;
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i;
    const x = center.x + hexSize * Math.cos(angle);
    const y = center.y + hexSize * Math.sin(angle);
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  
  // LABEL
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
  ctx.font = 'bold 9px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('SEAL OF', center.x, center.y - size - 12);
  ctx.fillText('SOLOMON', center.x, center.y - size - 2);
  ctx.font = '8px monospace';
  ctx.fillText(`Balance: ${(1 - Math.abs(polarity)).toFixed(3)}`, center.x, center.y + size + 12);
  
  ctx.restore();
}

/**
 * Render all sacred geometry overlays based on sovereignty state.
 * 
 * @param {CanvasRenderingContext2D} ctx - 2D canvas context
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {Object} sovereigntyState - Complete sovereignty state
 * @param {Object} graph - ZX graph
 */
export function renderAllSacredGeometry(ctx, canvas, sovereigntyState, graph) {
  if (!sovereigntyState || !ctx) return;
  
  const {
    sovereignTriads = [],
    trivectorMagnitude = 0,
    recursiveDepth = 0,
    polarity = 0
  } = sovereigntyState;
  
  // Render in order: Sri Yantra (background) → Merkaba (triads) → Seal (overlay)
  renderSriYantra(ctx, canvas, sovereignTriads, recursiveDepth);
  renderMerkaba(ctx, canvas, sovereignTriads, trivectorMagnitude, graph);
  renderSealOfSolomon(ctx, canvas, polarity);
}

/**
 * Compute centroid of sovereign triad for placement.
 * 
 * @param {Object} triad - Sovereign triad with nodes
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {Object} graph - ZX graph
 * @returns {Object} {x, y} centroid position
 */
function computeTriadCentroid(triad, canvas, graph) {
  if (!triad || !triad.nodes || triad.nodes.length !== 3) return null;
  
  // Use circular layout for now (can be enhanced with actual node positions)
  const radius = Math.min(canvas.width, canvas.height) * 0.35;
  const center = { x: canvas.width / 2, y: canvas.height / 2 };
  
  // Map node IDs to positions (simplified)
  const nodeCount = graph.nodes.length;
  const positions = triad.nodes.map(nodeId => {
    const index = graph.nodes.indexOf(nodeId);
    const angle = (index / nodeCount) * 2 * Math.PI;
    return {
      x: center.x + radius * Math.cos(angle),
      y: center.y + radius * Math.sin(angle)
    };
  });
  
  // Compute centroid
  const centroid = {
    x: (positions[0].x + positions[1].x + positions[2].x) / 3,
    y: (positions[0].y + positions[1].y + positions[2].y) / 3
  };
  
  return centroid;
}

/**
 * Render topological protection indicator.
 * Shows Chern number and protection level.
 * 
 * @param {CanvasRenderingContext2D} ctx - 2D canvas context
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {number} chernNumber - Computed Chern number
 * @param {Object} transition - Topological transition info
 */
export function renderTopologicalProtection(ctx, canvas, chernNumber, transition) {
  if (Math.abs(chernNumber) === 0) return;  // No protection
  
  ctx.save();
  
  const x = 20;
  const y = canvas.height - 100;
  
  const alpha = Math.min(Math.abs(chernNumber) * 0.4, 1.0);
  
  // Background panel
  ctx.fillStyle = `rgba(0, 0, 0, ${alpha * 0.7})`;
  ctx.fillRect(x - 5, y - 5, 180, 80);
  
  // Border (color based on Chern number)
  const borderColor = chernNumber > 0 
    ? `rgba(0, 255, 100, ${alpha})`  // Positive: green
    : `rgba(255, 100, 100, ${alpha})`;  // Negative: red
  ctx.strokeStyle = borderColor;
  ctx.lineWidth = 2;
  ctx.strokeRect(x - 5, y - 5, 180, 80);
  
  // Title
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
  ctx.font = 'bold 11px monospace';
  ctx.textAlign = 'left';
  ctx.fillText('TOPOLOGICAL PROTECTION', x, y + 10);
  
  // Chern number
  ctx.font = 'bold 14px monospace';
  ctx.fillStyle = borderColor;
  ctx.fillText(`Chern Number: ${chernNumber}`, x, y + 28);
  
  // Protection level
  ctx.font = '10px monospace';
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
  const protection = Math.abs(chernNumber) === 1 ? 'Single vortex' :
                     Math.abs(chernNumber) === 2 ? 'Dual vortex' :
                     Math.abs(chernNumber) >= 3 ? 'Exotic phase' : 'Protected';
  ctx.fillText(`Level: ${protection}`, x, y + 44);
  
  // Transition indicator
  if (transition && transition.occurred) {
    ctx.fillStyle = `rgba(255, 215, 0, ${alpha})`;
    ctx.font = 'bold 9px monospace';
    ctx.fillText(`⚡ ${transition.significance.toUpperCase()}`, x, y + 58);
    ctx.font = '8px monospace';
    ctx.fillText(`Δ = ${transition.delta > 0 ? '+' : ''}${transition.delta}`, x, y + 68);
  }
  
  ctx.restore();
}


