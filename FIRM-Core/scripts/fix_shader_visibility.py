#!/usr/bin/env python3
"""
Systematic Shader Visibility Fix
Replaces complex raymarching with simple visible geometry
"""

import os
import re

def create_simple_shader():
    """Create a simple shader that WILL produce visible output"""
    
    simple_shader_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'simple_test_shader.js')
    
    simple_shader_code = """/**
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
"""
    
    with open(simple_shader_path, 'w') as f:
        f.write(simple_shader_code)
    
    print(f"✅ Created simple test shader at {simple_shader_path}")
    return True

def inject_shader_loader():
    """Add script tag to load simple shader"""
    
    index_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'index.html')
    
    if not os.path.exists(index_path):
        print("❌ index.html not found")
        return False
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check if already added
    if 'simple_test_shader.js' in content:
        print("⚠️ Simple shader already in index.html")
        return False
    
    # Add after diagnostic shader
    insertion_point = content.find('</head>')
    if insertion_point > 0:
        script_tag = '    <script src="simple_test_shader.js"></script>\n'
        content = content[:insertion_point] + script_tag + content[insertion_point:]
        
        with open(index_path, 'w') as f:
            f.write(content)
        
        print("✅ Added simple shader to index.html")
        return True
    
    print("❌ Could not add shader to index.html")
    return False

def create_camera_fix():
    """Create camera positioning fix"""
    
    camera_fix_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'camera_fix.js')
    
    camera_fix_code = """/**
 * camera_fix.js
 * Systematic camera positioning fix
 */

window.cameraFix = {
  positions: {
    close: { x: 0, y: 0, z: 15 },
    medium: { x: 0, y: 0, z: 30 },
    far: { x: 0, y: 0, z: 50 },
    veryFar: { x: 0, y: 0, z: 100 },
    debug: { x: 10, y: 10, z: 30 }
  },
  
  setPosition: function(distance = 'medium') {
    const pos = this.positions[distance] || this.positions.medium;
    
    // Try multiple camera references
    const camera = window.renderer?.camera || 
                  window.camera || 
                  window.firmRenderer?.camera;
    
    if (camera) {
      if (camera.position) {
        camera.position.x = pos.x;
        camera.position.y = pos.y;
        camera.position.z = pos.z;
      }
      
      // Update uniform if needed
      if (window.renderer && window.renderer.uniforms) {
        window.renderer.uniforms.uCameraPosition = [pos.x, pos.y, pos.z];
      }
      
      console.log(`Camera set to ${distance}:`, pos);
      return true;
    }
    
    console.error('Camera not found');
    return false;
  },
  
  scan: function() {
    console.log('Scanning camera positions...');
    const positions = ['close', 'medium', 'far', 'veryFar'];
    let index = 0;
    
    const interval = setInterval(() => {
      if (index >= positions.length) {
        clearInterval(interval);
        console.log('Scan complete - check which position showed geometry');
        return;
      }
      
      this.setPosition(positions[index]);
      console.log(`Testing: ${positions[index]}`);
      index++;
    }, 2000);
  }
};

console.log('%c✅ Camera fix loaded!', 'color: blue; font-weight: bold');
console.log('Commands:');
console.log('  window.cameraFix.setPosition("close"|"medium"|"far") - Set camera distance');
console.log('  window.cameraFix.scan() - Test all positions');
"""
    
    with open(camera_fix_path, 'w') as f:
        f.write(camera_fix_code)
    
    print(f"✅ Created camera fix at {camera_fix_path}")
    return True

def main():
    """Run all shader visibility fixes"""
    print("🔧 Systematic Shader Visibility Fix...")
    print("=" * 50)
    
    fixes_applied = 0
    
    # Create simple test shader
    if create_simple_shader():
        fixes_applied += 1
    
    # Add to HTML
    if inject_shader_loader():
        fixes_applied += 1
    
    # Create camera fix
    if create_camera_fix():
        fixes_applied += 1
    
    print("=" * 50)
    print(f"✅ Applied {fixes_applied} fixes")
    
    if fixes_applied > 0:
        print("\n📝 Next Steps:")
        print("1. Reload the FIRM UI page")
        print("2. Open DevTools console")
        print("3. Run: window.simpleTestShader.applySimpleShader()")
        print("4. You should see a colored sphere")
        print("5. If not, run: window.cameraFix.scan()")
        print("\nThis will systematically determine if:")
        print("- Shaders are working")
        print("- Camera position is the issue")
        print("- Distance field calculation is the problem")
    
    return fixes_applied > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
