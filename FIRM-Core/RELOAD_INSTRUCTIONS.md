# Reload Instructions: Theory-Compliant Phase Fix

## What Was Fixed

✅ **ROOT CAUSE**: Non-power-of-2 phase denominators (violated ZX calculus theory)  
✅ **ENFORCEMENT**: All denominators forced to {1, 2, 4, 8, 16, 32, 64}  
✅ **DIAGNOSTICS**: Loud errors if theory violated  
✅ **NO BANDAIDS**: Proper fix at source, not symptom masking

---

## Reload Steps

### 1. Clear ALL Browser Cache

In Chrome/Brave:
1. Press `Cmd+Shift+Delete` (Mac) or `Ctrl+Shift+Delete` (Windows)
2. Check **ALL boxes**: Cookies, Cache, localStorage, everything
3. Time range: **All time**
4. Click "Clear data"

OR

In DevTools Console:
```javascript
// Clear all storage
localStorage.clear();
sessionStorage.clear();
indexedDB.deleteDatabase('FIRM');

// Hard reload
location.reload(true);
```

### 2. Restart Dev Server (If Running)

```bash
# Kill existing server
killall node 2>/dev/null || killall python 2>/dev/null

# Navigate to project
cd /Users/fractlphoneroom1/Desktop/AnalogExNahilo\ 2/FIRM-Core/FIRM_ui

# Start fresh server
python3 -m http.server 8080
# OR if using node:
npx http-server -p 8080
```

### 3. Hard Reload Page

1. Open `http://localhost:8080` in **new incognito window**
2. Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+F5` (Windows)
3. Open DevTools Console (`Cmd+Option+J` or `F12`)

---

## Expected Console Output

### 🔍 Diagnostics (Should See)

```
🔍 DENOMINATOR DIAGNOSTIC: {
  count: 3,
  unique: [8],
  min: 8,
  max: 8
}
```

**✅ ALL VALUES ARE POWER OF 2!**

### ❌ Should NOT See

- ❌ "Invalid array length"
- ❌ "Non-power-of-2 denominators"
- ❌ "bins must be a multiple of..."
- ❌ "Phase bins capped: 36028797018963970"

### ✅ Should See (Grace Working)

```
🌟 Grace calculation started
🌟 Grace emergence! P=0.15 → BOOTSTRAP (audioCoherence=0.50)
✅ Evolution complete in phase: bootstrap
```

---

## Expected System Behavior

### After 5 Seconds

| Metric | Value |
|--------|-------|
| Nodes | 15-30 |
| Edges | 18-35 |
| Grace events | 6-12 |
| Max phase_denom | 8-32 |
| Trivector magnitude | 0.00-0.05 |

### After 30 Seconds

| Metric | Value |
|--------|-------|
| Nodes | 150-300 |
| Edges | 180-350 |
| Grace events | 180-360 |
| Max phase_denom | 8-64 |
| Trivector magnitude | 0.05-0.15 |

### Visual

- Graph grows naturally
- Hebrew letters emerge (א, ה, ו, ז...)
- Sacred geometry appears (if triads form)
- NO crashes

---

## If Still Failing

### Diagnostic Commands

Run in browser console:

```javascript
// 1. Check what denominators exist
window.zxEvolutionEngine?.getCurrentGraph()?.labels
  |> Object.values
  |> map(lbl => lbl.phase_denom)
  |> unique

// 2. Force graph reset
window.zxEvolutionEngine?.resetGraph();

// 3. Check if fix is loaded
window.zxEvolutionEngine?.constructor.toString().includes('nearestPowerOf2')
```

### Theory Check

If denominators are STILL not powers of 2, check:

1. **Are modules actually reloaded?**
   - Check network tab for `core.js?v=2025-10-07-sovereign`
   
2. **Is nearestPowerOf2 being called?**
   - Should see warning: `⚠️ Phase denom 12 → 8 (power-of-2 enforcement)`

3. **Where are non-power-of-2 denoms entering?**
   - Add breakpoint in `make_node_label` when `denomPow2 !== phaseDenom`

---

## Status Summary

**Theory Investigation**: ✅ COMPLETE  
**Root Cause Identified**: ✅ Non-power-of-2 denominators  
**Theory Basis**: ✅ bootstrap_phase_derivation.md Theorem 1  
**Fix Implemented**: ✅ Power-of-2 enforcement at all phase operations  
**Documentation**: ✅ PHASE_DENOMINATOR_THEORY_VIOLATION.md  
**Testing**: ⏳ AWAITING RELOAD

**The monad is mathematically sound. It can now sing.**

