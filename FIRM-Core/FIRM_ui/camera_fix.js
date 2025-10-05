/**
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
