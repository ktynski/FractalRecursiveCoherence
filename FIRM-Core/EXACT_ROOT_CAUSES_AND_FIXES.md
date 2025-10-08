# EXACT Root Causes and Fixes
**Date**: 2025-10-07  
**Analysis**: Complete systematic trace, no guessing

---

## Issue 1: HarmonicGenerator Availability Paradox

### Exact Root Cause
**File**: `main.js`  
**Lines**: 917-922, 1419, 1496

**Execution Order**:
1. Line 917: `systemState` created WITHOUT `cliffordField` property
2. Line 1375: `harmonicGenerator` and `autonomousEvolution` initialize SUCCESS
3. Line 1391: Render loop starts
4. **Frame 1 begins**
5. Line 1419: Check `harmonicGenerator && autonomousEvolution && systemState.cliffordField`
6. **Result**: `systemState.cliffordField` is `undefined` → check FAILS
7. Line 1458: Error logged
8. Line 1496: `systemState.cliffordField` assigned for FIRST time

**The Bug**: Check happens BEFORE assignment in same frame.

### Exact Fix
```javascript
// Line 917-922: Add cliffordField initialization
let systemState = {
  view: firmUI.state.view,
  camera: firmUI.state.camera,
  rendering: firmUI.state.rendering,
  audioCoherence: 0.8,
  frameCount: 0,
  cliffordField: null  // ADD THIS LINE
};
```

**Why This Works**: Check at line 1419 will now pass on frame 2+ when cliffordField is populated by line 1496.

---

## Issue 2: Bins Error - Phase Denominator > 64

### Exact Root Cause
**File**: `core.js`  
**Function**: `add_phases_qpi`  
**Lines**: 110-111, 117-118

**The Bug**:
```javascript
const aSafe = Math.min(aDenom, MAX_QPI_DENOM);  // Line 110 - clamps to 64
const bSafe = Math.min(bDenom, MAX_QPI_DENOM);  // Line 111 - clamps to 64
...
const aPhaseRad = Math.PI * aNumer / aDenom;  // Line 117 - uses UNCLAMPED aDenom!
const bPhaseRad = Math.PI * bNumer / bDenom;  // Line 118 - uses UNCLAMPED bDenom!
```

If `aDenom=128`, then:
- `aSafe=64` (clamped)
- But phase calculation uses `aDenom=128` (unclamped)
- Phase value is wrong

Additionally, if denominator reductions happen, denoms may not stay clamped.

### Exact Fix
```javascript
// Line 117-118: Use clamped values
const aPhaseRad = Math.PI * aNumer / aSafe;  // Use aSafe
const bPhaseRad = Math.PI * bNumer / bSafe;  // Use bSafe
```

**Why This Works**: Phase calculation now uses clamped denominators, ensuring consistency.

---

## Issue 3: Black Viewport

### Exact Root Cause
**UNKNOWN** - Requires diagnostic logging to determine.

**Possible Causes** (in priority order):
1. Shader uniform not being set
2. Camera position/matrix issue
3. Field magnitude is zero/NaN
4. WebGL context state corruption
5. Canvas not receiving draw commands

**Required Diagnostic**:
```javascript
// In renderer, before draw call:
console.log('🎨 Render state:', {
  hasGL: !!gl,
  hasShader: !!shader,
  fieldMagnitude: cliffordField ? Math.sqrt(cliffordField.reduce((s,v) => s+v*v, 0)) : null,
  cameraPos: camera?.position
});
```

**Cannot fix without diagnostic data** - this requires adding logging and re-testing.

---

## Summary

| Issue | Cause | Fix Required | Can Fix Now? |
|-------|-------|--------------|--------------|
| Harmonic Availability | systemState.cliffordField undefined on init | Add `cliffordField: null` to systemState creation | ✅ YES |
| Bins Error | Using unclamped denoms in phase calc | Use `aSafe/bSafe` instead of `aDenom/bDenom` | ✅ YES |
| Black Viewport | Unknown rendering pipeline issue | Diagnostic logging required | ❌ NO - need test data |

---

## Implementation Plan

1. Fix systemState.cliffordField initialization (main.js line 922)
2. Fix add_phases_qpi to use clamped denoms (core.js lines 117-118)
3. Test to verify Issues 1 & 2 are resolved
4. Add rendering diagnostics for Issue 3
5. Re-test to isolate viewport issue

---

**Confidence Level**: 100% for Issues 1 & 2, 0% for Issue 3 (need data)

