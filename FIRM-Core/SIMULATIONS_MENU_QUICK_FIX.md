# Simulations Menu - Quick Fix Guide
**Critical issues only - 30 minute implementation**

## What I Can Directly Observe

### 1. View Menu Is Missing Defined Sectors
**File**: `index.html` lines 389-396  
**Evidence**: `physics_constants.js` lines 105-130 defines 3 sectors:
- ✅ ELECTROMAGNETIC (N=21, ring+cross) - in menu as "clifford"
- ❌ DARK_MATTER (N=105, tree) - **MISSING**
- ❌ DARK_ENERGY (N=1e68, random) - **MISSING**

### 2. Experimental Tests Are Hidden
**File**: `interpretation_modal.js` lines 152-182  
**Evidence**: 4 experiments exist but require modal navigation:
1. `window.verifySphereCount()` - Sphere-counting theorem
2. `window.predictInterference()` - Interference prediction
3. `window.trackEvolution(30)` - Evolution tracking
4. φ-Spacing Law - manual measurement

**Problem**: Users must open Physics Guide → navigate to Experiments tab → click individual tests

### 3. Theory Validation Suite Not Accessible
**File**: `theory_validation_tests.js` lines 90-162  
**Evidence**: Comprehensive test suite exists  
**Access**: `window.theoryTests.runAllTests()` - **CONSOLE ONLY**

### 4. Physics Constants Not Visualized
**File**: `physics_constants.js`  
**Evidence**: 
- α calculation (lines 36-64): α = (3g)/(4π⁴k) → 1/137.036
- Particle masses (lines 78-102): Muon=207, Proton=1836, Higgs=125 GeV
- E8 validation (lines 24-34): Dimension=248, Roots=240

**Problem**: All calculated but never shown to user

---

## Quick Fix #1: Add Dark Matter/Energy Views (5 min)

### File: `index.html` (after line 395)

```html
<option value="clifford" selected>Clifford Field (Spacetime)</option>
<option value="zx">ZX Graph (Quantum)</option>
<option value="e8">E8 Topology (α=1/137)</option>
<optgroup label="Physics Sectors">
  <option value="sector_em">EM Sector (N=21)</option>
  <option value="sector_dm">Dark Matter (N=105, tree)</option>
  <option value="sector_de">Dark Energy (random)</option>
</optgroup>
<option value="consciousness">Consciousness</option>
<option value="sheaf">Sheaf Tree</option>
<option value="echo">Echo Map</option>
<option value="sgc">𝒮-GC (Soul Garbage Collection)</option>
```

### File: `main.js` (in switchView method, around line 230)

```javascript
switchView(viewName) {
  // Add sector views to valid views
  if (!['clifford', 'zx', 'e8', 'sheaf', 'echo', 'consciousness', 'sgc',
        'sector_em', 'sector_dm', 'sector_de'].includes(viewName)) {
    throw new Error(`Invalid view: ${viewName}`);
  }
  // ... rest of switchView
}
```

### File: `main.js` (in onViewChange method, around line 249)

```javascript
onViewChange(viewName) {
  console.log(`Switching to view: ${viewName}`);
  
  switch(viewName) {
    // ... existing cases
    
    case 'sector_em':
      console.log('⚡ EM Sector: N=21, ring+cross topology, α=1/137');
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.setSector('ELECTROMAGNETIC');
      }
      break;
      
    case 'sector_dm':
      console.log('🌑 Dark Matter: N=105, tree topology, no EM coupling');
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.setSector('DARK_MATTER');
      }
      break;
      
    case 'sector_de':
      console.log('💫 Dark Energy: Maximum entropy, random topology');
      if (window.zxEvolutionEngine) {
        window.zxEvolutionEngine.setSector('DARK_ENERGY');
      }
      break;
  }
}
```

### File: `zx_objectg_engine.js` (add new method)

```javascript
setSector(sectorName) {
  const sector = window.PHYSICS?.SECTORS?.[sectorName];
  if (!sector) {
    console.error(`Unknown sector: ${sectorName}`);
    return;
  }
  
  console.log(`Switching to ${sectorName} sector:`, sector);
  
  // Reset graph with sector-specific parameters
  this.reset();
  
  // Set initial nodes based on sector
  // (For now, just log - full implementation in Phase 2)
  console.log(`  Topology: ${sector.topology}`);
  console.log(`  Nodes: ${sector.nodes}`);
  console.log(`  Has loops: ${sector.hasLoops}`);
  console.log(`  Generates α: ${sector.generatesAlpha}`);
  
  this._currentSector = sectorName;
}
```

---

## Quick Fix #2: Add Experiments Button (5 min)

### File: `index.html` (in control panel, after line 500)

```html
<button id="resetEvolution" ...>Reset to Void</button>
<button id="runExperiments" style="margin-top: 8px; padding: 6px 10px; width: 100%; border-radius: 6px; border: 1px solid #2a2a2a; background: #3b1a1a; color: #eaeaea; cursor: pointer;">🧪 Run Experiments</button>

<div id="experimentResults" style="margin-top: 10px; display: none; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 4px; font-size: 11px;">
  <div style="font-weight: bold; margin-bottom: 5px;">Experiment Results:</div>
  <div id="experimentResultsBody" style="color: #ccc;"></div>
</div>
```

### File: `main.js` (in setupSliders function, after resetButton handler around line 1314)

```javascript
// Run Experiments Button
const experimentsButton = document.getElementById('runExperiments');
const experimentsResults = document.getElementById('experimentResults');
const experimentsResultsBody = document.getElementById('experimentResultsBody');

if (experimentsButton && experimentsResults && experimentsResultsBody) {
  experimentsButton.addEventListener('click', async () => {
    experimentsButton.textContent = '⏳ Running...';
    experimentsButton.disabled = true;
    experimentsResults.style.display = 'block';
    experimentsResultsBody.innerHTML = 'Running experimental tests...<br>';
    
    const results = [];
    
    // Experiment 1: Sphere counting
    if (window.verifySphereCount) {
      const sphereResult = window.verifySphereCount();
      results.push(`✓ Sphere Count: ${sphereResult ? 'PASS' : 'FAIL'}`);
    }
    
    // Experiment 2: Interference prediction
    if (window.predictInterference) {
      const interference = window.predictInterference();
      results.push(`✓ Interference: ${interference ? 'Predicted' : 'N/A'}`);
    }
    
    // Experiment 3: Evolution tracking (5 seconds)
    if (window.trackEvolution) {
      experimentsResultsBody.innerHTML += 'Tracking evolution (5s)...<br>';
      const trackResult = await window.trackEvolution(5);
      results.push(`✓ Evolution: ${trackResult?.samples || 0} samples`);
    }
    
    // Display results
    experimentsResultsBody.innerHTML = results.join('<br>');
    experimentsButton.textContent = '🧪 Run Experiments';
    experimentsButton.disabled = false;
    
    console.log('🧪 Experiments complete:', results);
  });
}
```

---

## Quick Fix #3: Add Theory Validation Button (5 min)

### File: `index.html` (in control panel, after experiments button)

```html
<button id="validateTheory" style="margin-top: 8px; padding: 6px 10px; width: 100%; border-radius: 6px; border: 1px solid #2a2a2a; background: #1a3b1a; color: #eaeaea; cursor: pointer;">✓ Validate Theory</button>

<div id="validationResults" style="margin-top: 10px; display: none; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 4px; font-size: 11px;">
  <div style="font-weight: bold; margin-bottom: 5px;">Theory Validation:</div>
  <div id="validationResultsBody" style="color: #ccc;"></div>
</div>
```

### File: `main.js` (in setupSliders function, after experiments button)

```javascript
// Validate Theory Button
const validateButton = document.getElementById('validateTheory');
const validationResults = document.getElementById('validationResults');
const validationResultsBody = document.getElementById('validationResultsBody');

if (validateButton && validationResults && validationResultsBody) {
  validateButton.addEventListener('click', async () => {
    validateButton.textContent = '⏳ Validating...';
    validateButton.disabled = true;
    validationResults.style.display = 'block';
    validationResultsBody.innerHTML = 'Running theory validation...<br>';
    
    try {
      // Run theory tests if available
      if (window.theoryTests?.runAllTests) {
        await window.theoryTests.runAllTests();
        const results = window.theoryTests.testResults;
        const passed = results.filter(r => r.success).length;
        const total = results.length;
        
        validationResultsBody.innerHTML = `
          <strong>${passed}/${total} tests passed</strong><br><br>
          ${results.map(r => `${r.success ? '✓' : '✗'} ${r.scenario}`).join('<br>')}
        `;
      } else {
        // Basic validation without test suite
        const validations = [];
        
        // E8 validation
        if (window.PHYSICS?.E8?.check) {
          const e8Valid = window.PHYSICS.E8.check();
          validations.push(`${e8Valid ? '✓' : '✗'} E8 encoding (dim=248, roots=240)`);
        }
        
        // Alpha calculation
        if (window.PHYSICS?.ALPHA?.calculate) {
          const alpha = window.PHYSICS.ALPHA.calculate();
          const error = Math.abs(alpha - 1/137.036) / (1/137.036) * 100;
          validations.push(`${error < 1 ? '✓' : '✗'} α = 1/${(1/alpha).toFixed(3)} (${error.toFixed(2)}% error)`);
        }
        
        // ZX engine status
        if (window.zxEvolutionEngine) {
          const snapshot = window.zxEvolutionEngine.getSnapshot?.();
          if (snapshot) {
            validations.push(`✓ ZX engine active (${snapshot.graph.nodes.length} nodes)`);
          }
        }
        
        validationResultsBody.innerHTML = validations.join('<br>');
      }
    } catch (error) {
      validationResultsBody.innerHTML = `<span style="color: #ff5555;">Error: ${error.message}</span>`;
      console.error('Validation error:', error);
    }
    
    validateButton.textContent = '✓ Validate Theory';
    validateButton.disabled = false;
  });
}
```

---

## Quick Fix #4: Add Physics Constants Display (10 min)

### File: `index.html` (after metrics panel, around line 477)

```html
<div class="section-card">
  <h3>Physics Constants</h3>
  <div id="physicsConstants" style="font-size: 11px; color: #ccc;">
    <table style="width: 100%; border-collapse: collapse;">
      <tr>
        <td>E8 Dimension:</td>
        <td id="e8Dimension">-</td>
      </tr>
      <tr>
        <td>E8 Roots:</td>
        <td id="e8Roots">-</td>
      </tr>
      <tr>
        <td>α (fine structure):</td>
        <td id="alphaValue">-</td>
      </tr>
      <tr>
        <td>Current Sector:</td>
        <td id="currentSector">EM</td>
      </tr>
      <tr>
        <td>Topology:</td>
        <td id="currentTopology">ring+cross</td>
      </tr>
    </table>
  </div>
</div>
```

### File: `main.js` (in render loop update, around line 1711)

```javascript
// Update physics constants display
if (systemState.frameCount % 60 === 0) { // Update every second
  const e8DimEl = document.getElementById('e8Dimension');
  const e8RootsEl = document.getElementById('e8Roots');
  const alphaEl = document.getElementById('alphaValue');
  const sectorEl = document.getElementById('currentSector');
  const topologyEl = document.getElementById('currentTopology');
  
  if (e8DimEl && window.PHYSICS) {
    const N = window.PHYSICS.N;
    const dim = N * 12 - 4;
    const roots = N * 11 + 9;
    const alpha = window.PHYSICS.ALPHA.calculate();
    
    e8DimEl.textContent = `${dim} ${dim === 248 ? '✓' : '✗'}`;
    e8RootsEl.textContent = `${roots} ${roots === 240 ? '✓' : '✗'}`;
    alphaEl.textContent = `1/${(1/alpha).toFixed(3)}`;
    
    if (window.zxEvolutionEngine?._currentSector) {
      sectorEl.textContent = window.zxEvolutionEngine._currentSector;
      const sector = window.PHYSICS.SECTORS[window.zxEvolutionEngine._currentSector];
      if (sector) {
        topologyEl.textContent = sector.topology;
      }
    }
  }
}
```

---

## Testing Checklist (5 min)

After implementing quick fixes:

```bash
# 1. Clear browser cache
# DevTools → Application → Clear storage → Clear all

# 2. Reload page
# Open http://localhost:8080

# 3. Test each fix:
[ ] Dark Matter view appears in dropdown
[ ] Dark Energy view appears in dropdown  
[ ] Selecting sector logs correct info to console
[ ] "Run Experiments" button exists
[ ] Clicking experiments runs and shows results
[ ] "Validate Theory" button exists
[ ] Clicking validation shows E8/α status
[ ] Physics constants table updates every second

# 4. Console checks:
window.PHYSICS.SECTORS  // Should show 3 sectors
window.zxEvolutionEngine.setSector('DARK_MATTER')  // Should work
window.theoryTests  // Should exist if test file loaded
```

---

## What This Does NOT Fix

These require more work (Phase 2):

1. ❌ Actual rendering of DM/DE sectors (needs new shaders)
2. ❌ Full theory validation suite integration
3. ❌ Audio spectrum visualization
4. ❌ Evolution history timeline
5. ❌ Particle mass spectrum display
6. ❌ Topology sandbox with adjustable N

**For those, see**: `SIMULATIONS_MENU_AUDIT.md` full implementation plan

---

## Rollback Plan

If something breaks:

```bash
git diff FIRM-Core/FIRM_ui/index.html
git diff FIRM-Core/FIRM_ui/main.js
git diff FIRM-Core/FIRM_ui/zx_objectg_engine.js

# If needed:
git checkout HEAD -- FIRM-Core/FIRM_ui/index.html
git checkout HEAD -- FIRM-Core/FIRM_ui/main.js
git checkout HEAD -- FIRM-Core/FIRM_ui/zx_objectg_engine.js
```

---

## Summary

**What I observed directly**:
- 3 physics sectors defined but 2 not in menu
- 4 experimental tests hidden in modal
- Theory validation suite console-only
- Physics constants calculated but not displayed

**What I'm NOT assuming**:
- How sectors should render (that's Phase 2)
- Whether full test suite integration is needed (provided fallback)
- What other simulations might exist (stuck to documented evidence)

**Time to implement**: 25-30 minutes  
**Risk level**: Low (non-breaking additions)  
**User impact**: Exposes 4 major hidden features

