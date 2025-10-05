#!/usr/bin/env python3
"""
Force WebGL to render something visible
Simplifies the shader to bare minimum that WILL work
"""

import os
import re

def create_minimal_working_shader():
    """Create a shader that is guaranteed to work"""
    
    shader_fix = """
// EMERGENCY FIX: Simple visible shader
const SIMPLE_VERTEX_SHADER = `
attribute vec2 position;
uniform mat4 uProjectionMatrix;
uniform mat4 uModelViewMatrix;
varying vec2 vUv;

void main() {
    vUv = position * 0.5 + 0.5;
    gl_Position = vec4(position, 0.0, 1.0);
}
`;

const SIMPLE_FRAGMENT_SHADER = `
precision mediump float;
varying vec2 vUv;
uniform float uTime;

void main() {
    // Simple animated gradient
    vec3 color = vec3(
        0.5 + 0.5 * sin(uTime + vUv.x * 3.0),
        0.5 + 0.5 * cos(uTime + vUv.y * 3.0),
        0.5 + 0.5 * sin(uTime * 0.5)
    );
    
    // Add E8 pattern
    float pattern = sin(vUv.x * 21.0) * cos(vUv.y * 21.0);
    color += vec3(0.0, pattern * 0.2, 0.0);
    
    gl_FragColor = vec4(color, 1.0);
}
`;

window.forceSimpleShader = function() {
    const canvas = document.getElementById('canvas');
    if (!canvas) {
        console.error('No canvas found');
        return false;
    }
    
    // Get or create WebGL context
    let gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) {
        console.error('No WebGL context');
        return false;
    }
    
    // Create shaders
    const vertShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertShader, SIMPLE_VERTEX_SHADER);
    gl.compileShader(vertShader);
    
    if (!gl.getShaderParameter(vertShader, gl.COMPILE_STATUS)) {
        console.error('Vertex shader error:', gl.getShaderInfoLog(vertShader));
        return false;
    }
    
    const fragShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragShader, SIMPLE_FRAGMENT_SHADER);
    gl.compileShader(fragShader);
    
    if (!gl.getShaderParameter(fragShader, gl.COMPILE_STATUS)) {
        console.error('Fragment shader error:', gl.getShaderInfoLog(fragShader));
        return false;
    }
    
    // Create program
    const program = gl.createProgram();
    gl.attachShader(program, vertShader);
    gl.attachShader(program, fragShader);
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Program link error:', gl.getProgramInfoLog(program));
        return false;
    }
    
    // Create fullscreen quad
    const vertices = new Float32Array([
        -1, -1,
         1, -1,
        -1,  1,
         1,  1
    ]);
    
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    
    // Get locations
    const positionLocation = gl.getAttribLocation(program, 'position');
    const timeLocation = gl.getUniformLocation(program, 'uTime');
    
    // Stop existing renderer
    if (window.renderer && window.renderer.stop) {
        window.renderer.stop();
        console.log('Stopped existing renderer');
    }
    
    // Start simple render loop
    let startTime = Date.now();
    function render() {
        const time = (Date.now() - startTime) * 0.001;
        
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.clearColor(0.1, 0.1, 0.2, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        gl.useProgram(program);
        
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
        
        gl.uniform1f(timeLocation, time);
        
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        
        requestAnimationFrame(render);
    }
    
    render();
    console.log('✅ Simple shader rendering started');
    return true;
};

console.log('Force simple shader loaded - run window.forceSimpleShader()');
"""
    
    # Write to force_visible.js
    force_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'force_visible.js')
    with open(force_path, 'w') as f:
        f.write(shader_fix)
    
    print(f"✅ Created force visibility shader at {force_path}")
    return force_path

def add_to_html(script_path):
    """Add the force script to index.html"""
    
    index_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'index.html')
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check if already added
    if 'force_visible.js' in content:
        print("⚠️ Force shader already in HTML")
        return False
    
    # Add before </head>
    insertion_point = content.find('</head>')
    if insertion_point > 0:
        script_tag = '    <script src="force_visible.js"></script>\n'
        content = content[:insertion_point] + script_tag + content[insertion_point:]
        
        with open(index_path, 'w') as f:
            f.write(content)
        
        print("✅ Added force shader to index.html")
        return True
    
    return False

def fix_autoOmega_errors():
    """Find and fix any remaining autoOmega errors"""
    
    # Look for the evolution chain that might still have errors
    main_path = os.path.join(os.path.dirname(__file__), '..', 'FIRM_ui', 'main.js')
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    # The error seems to come from zx_objectg_engine evolution
    # Let's wrap the evolution call properly
    fixed = False
    
    # Look for evolveFromAudioCoherence calls that might error
    pattern = r'window\.zxEvolutionEngine\?\.evolveFromAudioCoherence\?\.\((.*?)\)'
    
    def replace_evolution(match):
        nonlocal fixed
        fixed = True
        return f'(window.zxEvolutionEngine && window.zxEvolutionEngine.evolveFromAudioCoherence ? window.zxEvolutionEngine.evolveFromAudioCoherence({match.group(1)}) : null)'
    
    content = re.sub(pattern, replace_evolution, content)
    
    if fixed:
        with open(main_path, 'w') as f:
            f.write(content)
        print("✅ Fixed evolution chain calls")
    else:
        print("⚠️ No evolution chain fixes needed")
    
    return fixed

def main():
    print("🔧 Forcing WebGL Visibility...")
    print("=" * 50)
    
    # Create simple working shader
    shader_path = create_minimal_working_shader()
    
    # Add to HTML
    add_to_html(shader_path)
    
    # Fix autoOmega errors
    fix_autoOmega_errors()
    
    print("=" * 50)
    print("✅ Force visibility fix complete")
    print("\n📝 Next Steps:")
    print("1. Reload the page")
    print("2. Open console")
    print("3. Run: window.forceSimpleShader()")
    print("4. You should see an animated gradient with E8 pattern")
    print("\nThis bypasses all complex shaders and renders directly.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
