/**
 * camera_external_fix.js
 * 
 * Emergency fix to position camera properly outside the field.
 * Run in browser console for immediate external observer positioning.
 */

window.fixCameraPosition = function() {
  console.log('🔧 Fixing camera position for external observation');
  
  // Position camera far outside the emergence region
  if (window.firmUI) {
    window.firmUI.state.camera.position = [0, 0, 50];  // Much further back
    window.firmUI.state.camera.target = [0, 0, 0];     // Looking at origin
    window.firmUI.state.camera.fov = 45;               // Standard FOV
    
    console.log('📷 Camera repositioned to external observer position [0, 0, 50]');
    console.log('🎯 Camera now observing from void, looking at emergence region');
    
    return 'Camera positioned externally';
  } else {
    console.log('✗ firmUI not accessible');
    return 'firmUI not found';
  }
};

window.testFieldScale = function() {
  console.log('🔍 Testing field scale relative to camera');
  
  // Check current camera position
  if (window.firmUI) {
    const pos = window.firmUI.state.camera.position;
    const distance = Math.sqrt(pos[0]*pos[0] + pos[1]*pos[1] + pos[2]*pos[2]);
    
    console.log(`📷 Camera distance from origin: ${distance.toFixed(1)} units`);
    console.log(`🌌 Field should be contained within radius 3-5 units`);
    console.log(`📐 Ratio: Camera distance / Field radius = ${(distance / 3).toFixed(1)}:1`);
    
    if (distance < 10) {
      console.log('⚠️  Camera too close - embedded in field');
      console.log('🔧 Recommended: Move camera to 30+ units');
    } else {
      console.log('✓ Camera properly positioned outside field');
    }
    
    return `Camera at ${distance.toFixed(1)} units`;
  }
  
  return 'Cannot access camera state';
};

window.forceExternalView = function() {
  console.log('🚨 Forcing external observer view');
  
  // Set camera very far outside
  if (window.firmUI) {
    window.firmUI.state.camera.position = [0, 0, 100];  // Very far back
    console.log('📷 Camera forced to [0, 0, 100] - definitely outside any field');
    
    // Also try to access the renderer directly
    const canvas = document.getElementById('canvas');
    if (canvas) {
      canvas.style.border = '2px solid red';  // Visual indicator
      console.log('🔴 Canvas border added - should see red border if rendering');
      
      setTimeout(() => {
        canvas.style.border = 'none';
        console.log('🔴 Canvas border removed');
      }, 3000);
    }
    
    return 'External view forced';
  }
  
  return 'Cannot force external view';
};

console.log('🔧 Camera external fix tools loaded:');
console.log('- window.fixCameraPosition() - Position camera outside field');
console.log('- window.testFieldScale() - Check camera/field scale ratio');
console.log('- window.forceExternalView() - Force very external position');
