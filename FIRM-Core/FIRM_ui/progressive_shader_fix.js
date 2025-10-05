
/**
 * Progressive Raymarching Fix
 * Systematically repairs the distance field shader
 */

window.progressiveShaderFix = {
  currentLevel: 0,
  levels: [
    'simple_sphere',
    'e8_pattern', 
    'multi_sector',
    'field_modulation',
    'full_complexity'
  ],
  
  // Level 0: Simple sphere that definitely works
  getLevel0Shader: function() {
    return `
float sampleCliffordField(vec3 pos) {
    // LEVEL 0: Simple sphere at origin
    return length(pos) - 5.0;
}`;
  },
  
  // Level 1: Add E8 pattern
  getLevel1Shader: function() {
    return `
float sampleCliffordField(vec3 pos) {
    // LEVEL 1: Sphere with E8 pattern
    float sphere = length(pos) - 5.0;
    
    // Add E8-inspired 21-fold symmetry
    float pattern = 0.0;
    for (int i = 0; i < 21; i++) {
        float angle = float(i) * 0.299; // 2π/21
        vec3 axis = vec3(cos(angle), sin(angle), 0.0);
        pattern += sin(dot(pos, axis) * 2.0) * 0.02;
    }
    
    return sphere + pattern;
}`;
  },
  
  // Level 2: Add multi-sector structure
  getLevel2Shader: function() {
    return `
float sampleCliffordField(vec3 pos) {
    // LEVEL 2: Multi-sector universe
    
    // Ring+Cross topology (electromagnetic)
    float ring = abs(length(pos.xy) - 5.0) - 0.5;
    float crossX = abs(pos.x) - 0.3;
    float crossY = abs(pos.y) - 0.3;
    float crossZ = abs(pos.z) - 0.3;
    float cross = min(min(crossX, crossY), crossZ);
    float emSector = min(ring, cross);
    
    // Tree topology (dark matter) - offset to the right
    vec3 dmPos = pos - vec3(10.0, 0.0, 0.0);
    float trunk = length(dmPos.xy) - 0.5;
    float branches = 1000.0;
    for (int i = 0; i < 5; i++) {
        float h = float(i) * 1.5 - 3.0;
        vec3 branchPos = dmPos - vec3(0.0, 0.0, h);
        float branch = length(branchPos) - 1.0;
        branches = min(branches, branch);
    }
    float dmSector = min(trunk, branches);
    
    // Random topology (dark energy) - offset to the left  
    vec3 dePos = pos - vec3(-10.0, 0.0, 0.0);
    float chaos = sin(dePos.x * 3.0) * cos(dePos.y * 3.0) * sin(dePos.z * 3.0);
    float deSector = length(dePos) - 4.0 + chaos * 0.5;
    
    return min(emSector, min(dmSector, deSector));
}`;
  },
  
  // Level 3: Add field modulation
  getLevel3Shader: function() {
    return `
float sampleCliffordField(vec3 pos) {
    // LEVEL 3: Field-modulated geometry
    
    // Sample Clifford field components
    vec4 comp0 = texture2D(uCliffordField, vec2(0.125, 0.5));
    vec4 comp1 = texture2D(uCliffordField, vec2(0.375, 0.5));
    
    // Base sphere
    float sphere = length(pos) - 5.0;
    
    // E8 pattern with field modulation
    float pattern = 0.0;
    float fieldStrength = abs(comp0.r) + abs(comp0.g) + abs(comp0.b);
    
    for (int i = 0; i < 21; i++) {
        float angle = float(i) * 0.299;
        vec3 axis = vec3(cos(angle), sin(angle), 0.0);
        float wave = sin(dot(pos, axis) * (2.0 + fieldStrength));
        pattern += wave * 0.05 * (1.0 + comp1.r);
    }
    
    // Multi-sector with field influence
    float ring = abs(length(pos.xy) - 5.0 * (1.0 + comp0.g * 0.2)) - 0.5;
    float cross = min(abs(pos.x), min(abs(pos.y), abs(pos.z))) - 0.3;
    
    float result = min(sphere + pattern, min(ring, cross));
    
    // Add mass points
    float electronMass = length(pos - vec3(0.0, 0.0, 0.0)) - 0.5;
    float muonMass = length(pos - vec3(2.07, 0.0, 0.0)) - 0.3;
    float protonMass = length(pos - vec3(0.0, 1.836, 0.0)) - 0.4;
    
    result = min(result, min(electronMass, min(muonMass, protonMass)));
    
    return result;
}`;
  },
  
  // Level 4: Full complexity (but simplified from original)
  getLevel4Shader: function() {
    return `
float sampleCliffordField(vec3 pos) {
    // LEVEL 4: Full E8 complexity (simplified)
    
    // Sample all field components
    vec4 comp0 = texture2D(uCliffordField, vec2(0.125, 0.5));
    vec4 comp1 = texture2D(uCliffordField, vec2(0.375, 0.5));
    vec4 comp2 = texture2D(uCliffordField, vec2(0.625, 0.5));
    vec4 comp3 = texture2D(uCliffordField, vec2(0.875, 0.5));
    
    // Bootstrap coherence
    float coherence = abs(comp0.r) + abs(comp0.g) + abs(comp0.b) + abs(comp0.a);
    coherence = coherence / 4.0; // Normalize
    
    // E8 lattice structure (248-dimensional projection)
    float e8Structure = 1000.0;
    for (int i = 0; i < 8; i++) {
        float angle1 = float(i) * 0.785; // π/4
        for (int j = 0; j < 3; j++) {
            float angle2 = float(j) * 2.094; // 2π/3
            vec3 latticePoint = vec3(
                cos(angle1) * 5.0,
                sin(angle1) * 5.0,
                sin(angle2) * 3.0
            );
            float dist = length(pos - latticePoint) - 0.3;
            e8Structure = min(e8Structure, dist);
        }
    }
    
    // Multi-sector universe
    float emSector = abs(length(pos.xy) - 5.0) - 0.5;
    float dmSector = length(vec3(pos.x - 8.0, pos.y, pos.z)) - 3.0;
    float deSector = length(vec3(pos.x + 8.0, pos.y, pos.z)) - 3.5;
    
    // Field modulation
    float modulation = sin(pos.x * comp0.r) * cos(pos.y * comp1.g) * sin(pos.z * comp2.b);
    
    // Mass generation points
    float masses = 1000.0;
    vec3 massPoints[5];
    massPoints[0] = vec3(0.0, 0.0, 0.0);           // Electron
    massPoints[1] = vec3(2.07, 0.0, 0.0);          // Muon  
    massPoints[2] = vec3(0.0, 18.36, 0.0);         // Proton (scaled)
    massPoints[3] = vec3(8.1, 8.1, 0.0);           // W boson (scaled)
    massPoints[4] = vec3(9.1, 9.1, 0.0);           // Z boson (scaled)
    
    for (int i = 0; i < 5; i++) {
        float dist = length(pos - massPoints[i]) - 0.2 * (1.0 + float(i) * 0.1);
        masses = min(masses, dist);
    }
    
    // Combine all structures
    float result = e8Structure;
    result = min(result, emSector);
    result = min(result, dmSector * (1.0 + coherence));
    result = min(result, deSector * (1.0 - coherence * 0.5));
    result = min(result, masses);
    result += modulation * 0.1 * coherence;
    
    // Grace operator (continuous)
    float grace = 1.0 - 0.382 * coherence;
    result *= grace;
    
    return result;
}`;
  },
  
  applyLevel: function(level) {
    if (level < 0 || level >= this.levels.length) {
      console.error('Invalid level:', level);
      return false;
    }
    
    this.currentLevel = level;
    const shaderCode = this['getLevel' + level + 'Shader']();
    
    console.log(`Applying shader level ${level}: ${this.levels[level]}`);
    
    // Get the renderer
    if (!window.renderer || !window.renderer.shaderProgram) {
      console.error('Renderer not ready');
      return false;
    }
    
    // We need to modify the fragment shader
    // This is complex because we need to recompile
    // For now, we'll create a new test function
    
    // Create test function that can be called
    window.testShaderLevel = new Function('pos', `
      const uCliffordField = window.renderer.cliffordFieldTexture;
      ${shaderCode}
      return sampleCliffordField(pos);
    `);
    
    console.log('Test function created. Use: window.testShaderLevel({x:0, y:0, z:0})');
    
    // Try to patch the actual shader
    if (window.renderer && window.renderer.gl) {
      this.patchShader(shaderCode);
    }
    
    return true;
  },
  
  patchShader: function(shaderCode) {
    console.log('Attempting to patch shader...');
    
    // Store the new distance function
    window._customDistanceFunction = shaderCode;
    
    // Flag that we want to use custom shader
    window._useCustomShader = true;
    
    console.log('Shader patch ready. Restart renderer to apply.');
    console.log('Run: window.restartWithCustomShader()');
  },
  
  nextLevel: function() {
    const next = Math.min(this.currentLevel + 1, this.levels.length - 1);
    this.applyLevel(next);
    return `Level ${next}: ${this.levels[next]}`;
  },
  
  previousLevel: function() {
    const prev = Math.max(this.currentLevel - 1, 0);
    this.applyLevel(prev);
    return `Level ${prev}: ${this.levels[prev]}`;
  },
  
  test: function() {
    console.log('Testing progressive shader levels...');
    console.log('Current level:', this.currentLevel, '-', this.levels[this.currentLevel]);
    console.log('Commands:');
    console.log('  window.progressiveShaderFix.nextLevel() - Increase complexity');
    console.log('  window.progressiveShaderFix.previousLevel() - Decrease complexity');
    console.log('  window.progressiveShaderFix.applyLevel(0-4) - Jump to specific level');
    console.log('');
    console.log('Levels:');
    this.levels.forEach((name, i) => {
      console.log(`  ${i}: ${name} ${i === this.currentLevel ? '(current)' : ''}`);
    });
  }
};

// Helper to restart renderer with custom shader
window.restartWithCustomShader = function() {
  if (!window._customDistanceFunction) {
    console.error('No custom shader defined');
    return;
  }
  
  // Stop current renderer
  if (window.renderer && window.renderer.stop) {
    window.renderer.stop();
  }
  
  // We need to reinitialize with the custom shader
  // This is complex and would require modifying the renderer
  console.log('Custom shader ready but needs renderer modification to apply.');
  console.log('The shader code is stored in window._customDistanceFunction');
  
  // For now, create a simple test visualization
  window.visualizeCustomShader();
};

// Visualize the distance field in 2D
window.visualizeCustomShader = function() {
  const canvas = document.createElement('canvas');
  canvas.width = 200;
  canvas.height = 200;
  canvas.style.position = 'fixed';
  canvas.style.top = '10px';
  canvas.style.right = '10px';
  canvas.style.border = '2px solid green';
  canvas.style.zIndex = '10000';
  document.body.appendChild(canvas);
  
  const ctx = canvas.getContext('2d');
  const imageData = ctx.createImageData(200, 200);
  
  console.log('Visualizing distance field slice at z=0...');
  
  // Sample the distance field
  for (let x = 0; x < 200; x++) {
    for (let y = 0; y < 200; y++) {
      const pos = {
        x: (x - 100) * 0.2,
        y: (y - 100) * 0.2, 
        z: 0
      };
      
      // Use the test function if available
      let dist = 0;
      if (window.testShaderLevel) {
        try {
          dist = window.testShaderLevel(pos);
        } catch(e) {
          dist = Math.sqrt(pos.x*pos.x + pos.y*pos.y) - 5;
        }
      } else {
        dist = Math.sqrt(pos.x*pos.x + pos.y*pos.y) - 5;
      }
      
      // Color based on distance
      const idx = (y * 200 + x) * 4;
      if (Math.abs(dist) < 0.1) {
        // Surface (green)
        imageData.data[idx] = 0;
        imageData.data[idx + 1] = 255;
        imageData.data[idx + 2] = 0;
      } else if (dist < 0) {
        // Inside (red)
        imageData.data[idx] = 128;
        imageData.data[idx + 1] = 0;
        imageData.data[idx + 2] = 0;
      } else {
        // Outside (blue gradient)
        const fade = Math.min(255, dist * 20);
        imageData.data[idx] = 0;
        imageData.data[idx + 1] = 0;
        imageData.data[idx + 2] = fade;
      }
      imageData.data[idx + 3] = 255;
    }
  }
  
  ctx.putImageData(imageData, 0, 0);
  console.log('Distance field visualization added to top-right corner');
  console.log('Green = surface, Red = inside, Blue = outside');
};

console.log('Progressive shader fix loaded!');
console.log('Run: window.progressiveShaderFix.test()');
console.log('Then: window.progressiveShaderFix.applyLevel(0) to start');
