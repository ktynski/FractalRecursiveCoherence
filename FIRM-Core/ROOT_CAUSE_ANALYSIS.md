# Root Cause Analysis - Black Viewport Issue
**Date**: 2025-10-07  
**Status**: 🔍 SYSTEMATIC ANALYSIS (NO GUESSING)

---

## Observable Facts

### From Console Logs:
1. ✅ `Sovereign audio system initialized` (line 1375)
2. ❌ `Sovereign audio system not available` (line 1458, frame 1)
3. ❌ `bins must be a multiple of 2*max(phase_denoms)` (STILL HAPPENING)
4. ✅ Evolution working: Hebrew letters emerging, triads detected, phase transitions
5. ❌ Viewport: COMPLETELY BLACK

### From Code (main.js lines 1365-1462):
```javascript
// Line 1365-1378: Variables declared, async import attempted
let harmonicGenerator = null;
let autonomousEvolution = null;
try {
  const { HarmonicGenerator, AutonomousEvolution } = await import('./harmonic_generator.js');
  harmonicGenerator = new HarmonicGenerator(...);
  autonomousEvolution = new AutonomousEvolution(...);
  console.log('✅ Sovereign audio system initialized');  // THIS LOGS
} catch (error) {
  console.error('❌ CRITICAL: Failed to load...', error.message);
}

// Line 1391: Render loop starts
renderer.startRenderLoop(async () => {
  // Line 1419: Check fails
  if (harmonicGenerator && autonomousEvolution && systemState.cliffordField) {
    // SUCCESS PATH - doesn't execute
  } else {
    // Line 1457-1458: ERROR PATH - does execute
    if (systemState.frameCount === 1) {
      console.error('❌ CRITICAL: Sovereign audio system not available');  // THIS LOGS
    }
  }
});
```

---

## Contradiction Analysis

**Both messages log**, meaning:
- Import SUCCESS (line 1375)
- Runtime check FAILS (line 1419)

**Possible causes** (in order of likelihood):

### 1. `systemState.cliffordField` is null
- Variables `harmonicGenerator` and `autonomousEvolution` exist
- But `systemState.cliffordField` doesn't exist yet on frame 1
- Entire check fails, goes to else block

**Test**: Add separate logging to determine which variable is null.

### 2. Scope issue (UNLIKELY given console evidence)
- Variables are in parent scope of render loop
- Should be accessible via closure
- But console shows they DO exist (import logged success)

### 3. Timing issue (UNLIKELY)
- Async import might not complete before render loop starts
- But `await` should prevent this
- And error only logs once (frame 1), suggesting they DO exist later

---

## The Bins Error (SEPARATE ISSUE)

**Error**: `bins must be a multiple of 2*max(phase_denoms)`

**My fix applied**:
```javascript
const aSafe = Math.min(aDenom, MAX_QPI_DENOM);  // Cap at 64
const bSafe = Math.min(bDenom, MAX_QPI_DENOM);  // Cap at 64
```

**Why it's still failing**:
1. Graph ALREADY has denoms > 64 from PREVIOUS runs (persisted state?)
2. OR seed graph creates denoms > 64
3. OR some OTHER code path creates them (not add_phases_qpi)

**Need to check**:
- createSeedGraph() - what denoms does it create?
- Is there browser localStorage persisting bad graph state?
- Are there other functions that set phase_denom directly?

---

## The Black Viewport (THIRD SEPARATE ISSUE)

**Console shows**: Evolution IS happening (letters, triads)  
**Viewport shows**: Nothing (black)

**This means**: Rendering pipeline is broken, NOT evolution.

**Possible causes**:
1. **Shader compilation failure** (silent)
2. **Camera position** (outside field / at singularity)
3. **Field magnitude** (all zeros / NaN)
4. **WebGL state corruption**
5. **Canvas not receiving updates**

**Not tested yet**:
- Check WebGL context state
- Check shader uniform values
- Check camera position/matrices
- Check if raymarching is even executing

---

## Required Actions (NO GUESSING)

### Issue 1: HarmonicGenerator Availability
```javascript
// Add diagnostic logging to determine WHICH variable is null:
console.log('🔍 Frame 1 diagnostic:', {
  hasGenerator: !!harmonicGenerator,
  hasEvolution: !!autonomousEvolution,
  hasClifford: !!systemState.cliffordField
});
```

### Issue 2: Bins Error
```javascript
// Log graph state at error:
// In coherence.js line 153, ADD:
console.error('❌ Bins error diagnostic:', {
  bins: bins,
  maxDenom: maxDenom,
  required: 2 * maxDenom,
  allDenoms: Object.values(graph.labels).map(l => l.phase_denom)
});
```

### Issue 3: Black Viewport
```javascript
// Check rendering pipeline:
// In renderer or shader, ADD:
console.log('🎨 Render diagnostic:', {
  hasCanvas: !!canvas,
  hasGL: !!gl,
  fieldMagnitude: systemState.cliffordField ? 
    Math.sqrt(systemState.cliffordField.reduce((s,v) => s + v*v, 0)) : null,
  cameraPos: camera?.position
});
```

---

## Theory vs Implementation

**This is NOT a theory error.**

Theory says:
- Phase denoms ≤ 64 ✓ (correct)
- Omega bins = 128 ✓ (correct)
- Autonomous audio ✓ (correct)

Implementation has:
- Scoping/timing bugs (harmonicGenerator availability)
- State persistence bugs (denoms > 64 persisting)
- Rendering bugs (black viewport, separate issue)

**These are implementation bugs, not theory violations.**

---

**Next Step**: Add diagnostic logging to isolate exact failure point for each issue.

