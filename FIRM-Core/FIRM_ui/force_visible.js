
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
