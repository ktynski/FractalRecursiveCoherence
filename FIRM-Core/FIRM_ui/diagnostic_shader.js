/**
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
