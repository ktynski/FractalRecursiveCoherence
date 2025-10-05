#!/usr/bin/env python3
"""
Fix Critical WebGL Rendering Issues
Addresses module loading and integration problems
"""

import os
import re

def fix_module_exports():
    """Convert ES6 exports to window objects for non-module scripts"""
    
    files_to_fix = [
        ('FIRM_ui/mass_spectrum_display.js', 'MassSpectrumDisplay'),
        ('FIRM_ui/e8_webgl_integration.js', ['E8WebGLRenderer', 'MultiSectorController'])
    ]
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    fixed_count = 0
    
    for file_path, exports in files_to_fix:
        full_path = os.path.join(base_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"❌ {file_path} not found")
            continue
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Handle single or multiple exports
        if isinstance(exports, str):
            exports = [exports]
        
        for export_name in exports:
            # Replace export class/function with window assignment
            old_pattern = f'export class {export_name}'
            new_pattern = f'window.{export_name} = class'
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                fixed_count += 1
            
            # Also handle export { Name }
            old_export_pattern = f'export {{ {export_name}'
            if old_export_pattern in content:
                content = content.replace(old_export_pattern, f'// Exported via window.{export_name}\n// {old_export_pattern}')
                fixed_count += 1
        
        # Remove standalone export statements at the end
        content = re.sub(r'\nexport\s*{\s*[^}]+\s*};\s*$', '', content)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed exports in {file_path}")
    
    return fixed_count > 0

def add_e8_renderer_case():
    """Add E8 case to renderer.js"""
    
    renderer_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'renderer.js')
    
    if not os.path.exists(renderer_path):
        print(f"❌ renderer.js not found")
        return False
    
    with open(renderer_path, 'r') as f:
        content = f.read()
    
    # Check if e8 case already exists
    if "case 'e8':" in content:
        print("⚠️ E8 case already exists in renderer.js")
        return False
    
    # Find the switch statement for view modes
    switch_pattern = r"(switch\s*\([^)]*viewMode[^)]*\)\s*{)"
    match = re.search(switch_pattern, content)
    
    if not match:
        # Try alternative pattern
        switch_pattern = r"(switch\s*\(mode\)\s*{)"
        match = re.search(switch_pattern, content)
    
    if match:
        # Find the end of the first case to insert our new case
        switch_start = match.end()
        
        # Find a good insertion point (after the first case)
        first_break = content.find('break;', switch_start)
        if first_break > 0:
            insertion_point = first_break + 6  # After 'break;'
            
            e8_case = """
      case 'e8':
        // E8 Topology visualization
        console.log('E8 view mode selected');
        // For now, use clifford mode with E8 overlay
        // TODO: Implement full E8 renderer
        this.currentViewMode = 'clifford';  // Fallback for now
        if (typeof window.E8WebGLRenderer !== 'undefined') {
          if (!this.e8Renderer) {
            this.e8Renderer = new window.E8WebGLRenderer(this.gl, this.shaderProgram);
          }
          this.e8Renderer.updateUniforms(true, 0);
        }
        break;
"""
            
            content = content[:insertion_point] + e8_case + content[insertion_point:]
            
            with open(renderer_path, 'w') as f:
                f.write(content)
            
            print("✅ Added E8 case to renderer.js")
            return True
    
    print("❌ Could not find switch statement in renderer.js")
    return False

def fix_physics_constants_scope():
    """Ensure PHYSICS constants are globally accessible"""
    
    constants_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'physics_constants.js')
    
    if not os.path.exists(constants_path):
        print(f"❌ physics_constants.js not found")
        return False
    
    with open(constants_path, 'r') as f:
        content = f.read()
    
    # Check if already exposed to window
    if 'window.PHYSICS' in content:
        print("⚠️ PHYSICS already exposed to window")
        return False
    
    # Add window exposure before the export
    if 'const PHYSICS = {' in content:
        # Add window assignment after the PHYSICS definition
        insertion_point = content.find('};', content.find('const PHYSICS = {'))
        if insertion_point > 0:
            insertion_point += 2  # After '};'
            window_assignment = '\n\n// Make globally accessible\nwindow.PHYSICS = PHYSICS;\n'
            content = content[:insertion_point] + window_assignment + content[insertion_point:]
            
            with open(constants_path, 'w') as f:
                f.write(content)
            
            print("✅ Exposed PHYSICS to global scope")
            return True
    
    print("❌ Could not expose PHYSICS to window")
    return False

def create_diagnostic_shader():
    """Create a simple diagnostic shader to verify WebGL is working"""
    
    diagnostic_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'diagnostic_shader.js')
    
    diagnostic_code = """/**
 * diagnostic_shader.js
 * Simple shader to verify WebGL rendering is working
 */

window.diagnosticShader = {
  vertex: `
    attribute vec2 position;
    void main() {
      gl_Position = vec4(position, 0.0, 1.0);
    }
  `,
  
  fragment: `
    precision mediump float;
    uniform float uTime;
    
    void main() {
      // Simple animated gradient to verify rendering
      vec2 uv = gl_FragCoord.xy / vec2(1200.0, 800.0);
      vec3 color = vec3(
        0.5 + 0.5 * sin(uTime + uv.x * 10.0),
        0.5 + 0.5 * cos(uTime + uv.y * 10.0),
        0.5 + 0.5 * sin(uTime * 0.7)
      );
      gl_FragColor = vec4(color, 1.0);
    }
  `,
  
  test: function() {
    const canvas = document.getElementById('canvas');
    if (!canvas) {
      console.error('Canvas not found');
      return;
    }
    
    const gl = canvas.getContext('webgl2');
    if (!gl) {
      console.error('WebGL2 not available');
      return;
    }
    
    console.log('Running diagnostic shader test...');
    
    // Clear to red to verify canvas is working
    gl.clearColor(1.0, 0.0, 0.0, 1.0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    
    console.log('Canvas cleared to red - if you see red, WebGL is working');
    
    // After 2 seconds, try gradient
    setTimeout(() => {
      gl.clearColor(0.0, 1.0, 0.0, 1.0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      console.log('Canvas cleared to green');
    }, 2000);
    
    // After 4 seconds, try blue
    setTimeout(() => {
      gl.clearColor(0.0, 0.0, 1.0, 1.0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      console.log('Canvas cleared to blue');
    }, 4000);
  }
};

// Auto-run diagnostic if needed
console.log('Diagnostic shader loaded. Run window.diagnosticShader.test() to test WebGL');
"""
    
    with open(diagnostic_path, 'w') as f:
        f.write(diagnostic_code)
    
    print(f"✅ Created diagnostic shader at {diagnostic_path}")
    return True

def main():
    """Run all fixes"""
    print("🔧 Fixing Critical WebGL Rendering Issues...")
    print("=" * 50)
    
    fixes_applied = 0
    
    # Fix module exports
    if fix_module_exports():
        fixes_applied += 1
    
    # Add E8 renderer case
    if add_e8_renderer_case():
        fixes_applied += 1
    
    # Fix physics constants scope
    if fix_physics_constants_scope():
        fixes_applied += 1
    
    # Create diagnostic shader
    if create_diagnostic_shader():
        fixes_applied += 1
    
    print("=" * 50)
    print(f"✅ Applied {fixes_applied} fixes")
    
    if fixes_applied > 0:
        print("\n📝 Next Steps:")
        print("1. Reload the browser page (Ctrl+Shift+R)")
        print("2. Open DevTools console")
        print("3. Run: window.diagnosticShader.test()")
        print("4. Check if canvas shows colors (red→green→blue)")
        print("5. Try E8 view mode again")
        print("\nIf canvas shows colors, WebGL is working and the issue is in the shaders.")
        print("If canvas stays black, there's a deeper WebGL context issue.")
    
    return fixes_applied > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
