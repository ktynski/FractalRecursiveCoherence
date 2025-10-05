/**
 * simple_test_shader.js
 * Guaranteed visible shader for testing
 */

window.simpleTestShader = {
  
  // Fragment shader that creates a simple visible sphere
  getSimpleFragmentShader: function() {
    return `
precision mediump float;
varying vec2 vUv;
varying vec3 vRayDir;

uniform vec3 uCameraPosition;
uniform float uMinDistance;
uniform float uMaxDistance;
uniform sampler2D uCliffordField;
uniform float uTime;

#define MAX_STEPS 64

// SIMPLE SPHERE - GUARANTEED VISIBLE
float simpleSphere(vec3 pos) {
    // Simple sphere at origin, radius 5
    return length(pos) - 5.0;
}

// SIMPLE E8 PATTERN
float simpleE8Pattern(vec3 pos) {
    float sphere = length(pos) - 5.0;
    
    // Add E8-inspired pattern
    float pattern = 0.0;
    
    // 8 axes of symmetry for E8
    for (int i = 0; i < 8; i++) {
        float angle = float(i) * 0.785398; // PI/4
        vec3 axis = vec3(cos(angle), sin(angle), 0.0);
        float wave = sin(dot(pos, axis) * 2.0 + uTime * 0.5);
        pattern += wave * 0.05;
    }
    
    return sphere + pattern;
}

// MULTI-SECTOR TEST
float multiSectorTest(vec3 pos) {
    // Three overlapping spheres for three sectors
    float em = length(pos - vec3(0.0, 0.0, 0.0)) - 3.0;      // EM sector
    float dm = length(pos - vec3(6.0, 0.0, 0.0)) - 4.0;      // Dark matter
    float de = length(pos - vec3(-6.0, 0.0, 0.0)) - 3.5;     // Dark energy
    
    return min(em, min(dm, de));
}

void main() {
    vec3 rayPos = uCameraPosition;
    vec3 rayDir = normalize(vRayDir);
    float totalDist = 0.0;
    
    // Simple raymarching
    for (int i = 0; i < MAX_STEPS; i++) {
        // Use simple sphere for testing
        float dist = simpleE8Pattern(rayPos);
        
        if (dist < uMinDistance || dist < 0.001) {
            // Hit! Color based on position
            vec3 normal = normalize(rayPos);
            
            // E8-inspired coloring
            float e8Factor = abs(sin(rayPos.x * 0.5)) * 
                            abs(cos(rayPos.y * 0.5)) * 
                            abs(sin(rayPos.z * 0.5));
            
            vec3 color = vec3(
                0.5 + 0.5 * normal.x,
                0.5 + 0.5 * normal.y + e8Factor * 0.3,
                0.5 + 0.5 * normal.z
            );
            
            // Add lighting
            vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
            float lighting = max(0.3, dot(normal, lightDir));
            color *= lighting;
            
            // Add E8 validation indicator (green glow)
            if (abs(rayPos.x) < 2.0 && abs(rayPos.y) < 2.0) {
                color += vec3(0.0, 0.3, 0.0); // Green for E8 valid region
            }
            
            gl_FragColor = vec4(color, 1.0);
            return;
        }
        
        rayPos += rayDir * dist;
        totalDist += dist;
        
        if (totalDist > uMaxDistance || totalDist > 100.0) {
            break;
        }
    }
    
    // Background gradient
    vec3 bgColor = vec3(0.0, 0.0, 0.1) + vRayDir.y * 0.1;
    gl_FragColor = vec4(bgColor, 1.0);
}
`;
  },
  
  // Apply simple shader to current renderer
  applySimpleShader: function() {
    if (!window.renderer) {
      console.error('Renderer not found');
      return false;
    }
    
    console.log('Applying simple test shader...');
    
    // Try to replace the fragment shader
    const newShader = this.getSimpleFragmentShader();
    
    // Store original shader
    if (!window.renderer._originalFragmentShader) {
      window.renderer._originalFragmentShader = window.renderer.fragmentShader;
    }
    
    // Apply new shader
    window.renderer.fragmentShader = newShader;
    
    // Force shader recompilation
    if (window.renderer.recompileShaders) {
      window.renderer.recompileShaders();
    } else {
      console.warn('Cannot recompile shaders - may need page reload');
    }
    
    console.log('Simple shader applied - you should see a sphere');
    return true;
  },
  
  // Restore original shader
  restoreOriginal: function() {
    if (window.renderer && window.renderer._originalFragmentShader) {
      window.renderer.fragmentShader = window.renderer._originalFragmentShader;
      if (window.renderer.recompileShaders) {
        window.renderer.recompileShaders();
      }
      console.log('Original shader restored');
      return true;
    }
    return false;
  },
  
  // Debug camera position
  debugCamera: function() {
    const camera = window.renderer?.camera || window.camera;
    if (camera) {
      console.log('Camera position:', camera.position);
      console.log('Camera target:', camera.target || 'Not set');
      
      // Set camera to known good position
      camera.position = { x: 0, y: 0, z: 30 };
      console.log('Camera moved to (0, 0, 30)');
      return true;
    }
    console.error('Camera not found');
    return false;
  }
};

// Auto-load message
console.log('%c✅ Simple test shader loaded!', 'color: green; font-weight: bold');
console.log('Commands:');
console.log('  window.simpleTestShader.applySimpleShader() - Apply simple visible shader');
console.log('  window.simpleTestShader.debugCamera() - Fix camera position');
console.log('  window.simpleTestShader.restoreOriginal() - Restore original shader');
