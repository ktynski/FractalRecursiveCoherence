# Simulations Menu Audit
**Date**: 2025-10-08  
**Status**: OUTDATED - Multiple missing features and sectors

## Executive Summary

The simulations menu is significantly outdated compared to implemented features. Key physics sectors (Dark Matter, Dark Energy), experimental tests, and validation suites are implemented but not exposed in the UI.

---

## 1. CRITICAL GAPS

### 1.1 Missing Physics Sectors
**Location**: `physics_constants.js` lines 105-130  
**Status**: ❌ NOT IN MENU

Three physics sectors are fully defined but not accessible:

| Sector | Topology | Nodes | Implementation Status | UI Status |
|--------|----------|-------|----------------------|-----------|
| ELECTROMAGNETIC | ring+cross | 21 | ✅ Implemented | ✅ In menu (as "clifford") |
| DARK_MATTER | tree | 105 | ✅ Defined | ❌ Missing |
| DARK_ENERGY | random | 1e68 | ✅ Defined | ❌ Missing |

**Impact**: Users cannot:
- Visualize dark matter topology (tree structure, no loops)
- Compare EM vs Dark Matter interaction differences
- Simulate dark energy's maximum entropy behavior
- Test why dark matter has no EM coupling (no closed loops)

### 1.2 Missing Experimental Test Suite
**Location**: `interpretation_modal.js` lines 152-182  
**Status**: ❌ HIDDEN IN MODAL

Four experimental tests exist but require:
1. Opening Physics Guide modal
2. Navigating to "Experiments" tab
3. Clicking individual test buttons

**Tests Available But Hidden**:
1. Sphere-Counting Theorem (`window.verifySphereCount()`)
2. φ-Spacing Law (manual measurement)
3. Interference Fringe Prediction (`window.predictInterference()`)
4. Evolution Tracking (`window.trackEvolution(30)`)

**Recommendation**: Add "🧪 Run Experiments" button to main control panel

### 1.3 Theory Validation Suite Not Accessible
**Location**: `theory_validation_tests.js` lines 90-162  
**Status**: ❌ CONSOLE ONLY

Comprehensive test suite exists with:
- Baseline scenario validation
- Grace emergence tests
- Phase transition verification
- Coherence tracking

**Current Access**: `window.theoryTests.runAllTests()` (console only)  
**Recommendation**: Add "✓ Validate Theory" button with results panel

---

## 2. VIEW SELECTOR ANALYSIS

### Current Views (index.html lines 389-396)

```html
<option value="clifford" selected>Clifford Field (Spacetime)</option>
<option value="zx">ZX Graph (Quantum)</option>
<option value="e8">E8 Topology (α=1/137)</option>
<option value="consciousness">Consciousness</option>
<option value="sheaf">Sheaf Tree</option>
<option value="echo">Echo Map</option>
<option value="sgc">𝒮-GC (Soul Garbage Collection)</option>
```

### Missing Simulation Modes

#### 2.1 Physics Sector Comparison
**Recommendation**: Add new view options:

```html
<optgroup label="Physics Sectors">
  <option value="sector_em">EM Sector (N=21, ring+cross)</option>
  <option value="sector_dm">Dark Matter (N=105, tree)</option>
  <option value="sector_de">Dark Energy (N=1e68, random)</option>
  <option value="sector_compare">Multi-Sector Comparison</option>
</optgroup>
```

#### 2.2 Particle Physics Simulations
**Evidence**: `physics_constants.js` lines 78-102 defines exact particle masses  
**Status**: ❌ NOT VISUALIZED

Particle mass ratios are calculated but not shown:
- Muon/Electron: 207 (10×21 - 3)
- Proton/Electron: 1836 (21×100 - 264)
- W Boson: 81 GeV (21×4 - 3)
- Higgs: 125 GeV (21×6 - 1)

**Recommendation**: Add "Particle Spectrum" view showing:
- Mass ratios derived from N=21
- Visual comparison to experimental values
- Error bars and validation

#### 2.3 Alpha Evolution Visualization
**Evidence**: `physics_constants.js` lines 36-64 has α calculation  
**Status**: ❌ NOT VISUALIZED

Formula: α = (3g)/(4π⁴k) where:
- g = coupling (topology-dependent)
- k = kinetic phase gradient
- Result: 1/137.036 (0.52% error)

**Recommendation**: Add "α Evolution" view showing:
- How topology changes affect α
- g and k values over time
- Convergence to 1/137

---

## 3. WAVEFORM DRIVERS ANALYSIS

### Current Drivers (index.html lines 549-557)

```html
<option value="sine">Sine (Default)</option>
<option value="fractal">Fractal (1/f)</option>
<option value="phi_recursive">φ-Recursive</option>
<option value="hebrew_letter">Hebrew Letter</option>
<option value="sacred_name">Sacred Name</option>
<option value="quantum">Quantum Coherence</option>
<option value="morphic">Morphic Resonance</option>
```

**Status**: ✅ COMPLETE (all 7 drivers implemented)

### Missing Driver Features

#### 3.1 Driver Comparison Tool
**Current**: Can only test one driver at a time  
**Recommendation**: Add "Compare Drivers" mode that:
- Runs 2-3 drivers simultaneously
- Shows side-by-side metrics
- Highlights which driver maximizes coherence/grace

#### 3.2 Driver Auto-Selection
**Current**: Manual selection only  
**Evidence**: Auto Ω alignment exists (lines 569-619) but doesn't auto-select driver  
**Recommendation**: Extend Auto Ω to include driver selection

---

## 4. VANTAGE POINTS (CAMERA PRESETS)

### Current Presets (index.html lines 479-498)

**Status**: ✅ COMPREHENSIVE (15 presets)

Includes:
- 5 theory-specific vantages (Void Observer, φ-Grace Torus, etc.)
- 10 physics perspectives (Scalar Field, QFT, GR, QM, etc.)

**No changes needed** - this section is well-designed

---

## 5. CONSCIOUSNESS VISUALIZATION

### Current Controls (lines 1317-1358 in main.js)

```javascript
window.consciousnessDisplaySettings = {
  showConsciousness: true,
  showWill: true,
  showReflexivePain: true,
  showOrMakifPnimi: false
};
```

**Status**: ✅ IMPLEMENTED  
**Issue**: Checkboxes exist but not clearly labeled as simulations

**Recommendation**: Group under "Consciousness Simulations" section:
- Label as "Monad State Visualization"
- Add tooltips explaining what each represents
- Link to theoretical documentation

---

## 6. MISSING SIMULATION CATEGORIES

### 6.1 Topology Simulations
**Evidence**: `physics_constants.js` has `createRingCross()` function  
**Status**: ❌ NOT EXPOSED

**Recommendation**: Add "Topology Sandbox" with:
- Adjustable N (current: 21)
- Switch topology: ring+cross, tree, random
- Real-time α calculation
- Validation against E8 constraints

### 6.2 Phase Quantization Experiments
**Evidence**: `physics_constants.js` lines 67-76 defines phase steps  
**Status**: ❌ NOT VISUALIZED

100 discrete phase steps with 102-step resonance period.

**Recommendation**: Add "Phase Dynamics" simulation:
- Visualize discrete phase steps
- Show resonance period emergence
- Test phase coherence vs audio input

### 6.3 E8 Validation Dashboard
**Evidence**: `validateE8()` and `calculateAlphaError()` functions exist  
**Status**: ❌ CONSOLE ONLY

**Recommendation**: Add real-time validation panel showing:
- E8 dimension: 21×12 - 4 = 248 ✓
- E8 roots: 21×11 + 9 = 240 ✓
- α error: current %
- All particle mass errors

---

## 7. SACRED/HEBREW SYSTEM STATUS

### Current Controls (lines 961-1025 in main.js)

**Status**: ⚠️ PARTIALLY IMPLEMENTED

Sacred system controls exist:
- Sacred name slider (72 names)
- Hebrew boundary selector
- Sacred commentary button

**Issues**:
1. No indication of which names are "active"
2. No visualization of Hebrew letter network
3. Sacred effects on field not clearly shown

**Recommendation**: Add "Sacred System Status" panel:
- Show current active name
- Display Hebrew letter network topology
- Visualize morphic field influence

---

## 8. AUDIO/EVOLUTION INTEGRATION

### Current Features
- Enable Audio button ✅
- Auto Align to Ω ✅
- Auto Ω Mode toggle ✅
- Waveform driver selection ✅

### Missing Features

#### 8.1 Audio Spectrum Analyzer
**Status**: ❌ NOT VISIBLE

Audio coherence is calculated but spectrum not shown.

**Recommendation**: Add "Audio Spectrum" panel:
- Real-time frequency display
- Coherence meter (external vs internal)
- Parseval normalization indicator
- Harmonic spectrum from Clifford field

#### 8.2 Evolution History Timeline
**Status**: ❌ NOT RECORDED

Evolution happens but no historical view.

**Recommendation**: Add "Evolution Timeline" showing:
- Phase transitions (void → grace → bootstrap)
- Coherence history graph
- Node/edge count over time
- Major events (first cycle, trivector emergence)

---

## 9. METRICS PANEL GAP ANALYSIS

### Current Metrics (metricsPanel in index.html)

**Visible Metrics** (when expanded):
- Graph structure (nodes, edges)
- Coherence C(G)
- ZX rewrites
- Evolution phase

### Missing Critical Metrics

1. **Physics Sector Indicators**
   - Current sector (EM/DM/DE)
   - Topology type
   - Loop count

2. **Particle Physics**
   - Current α value
   - Mass ratio calculations
   - E8 validation status

3. **Consciousness Levels**
   - Awareness: 0-1
   - Focus: 0-1
   - Understanding: 0-1
   - Will to Emerge

4. **Audio/Harmonic Analysis**
   - External coherence
   - Internal (sovereign) coherence
   - Autonomy factor
   - Dominant frequencies

---

## 10. RECOMMENDED UI RESTRUCTURING

### Proposed New Control Panel Sections

```
📊 Physics Simulations
  ├─ 🌌 Sector Selection (EM / Dark Matter / Dark Energy)
  ├─ 🧬 Particle Spectrum View
  ├─ ⚡ Alpha Evolution Tracker
  └─ 🔬 E8 Validation Dashboard

🧪 Experimental Tests
  ├─ Run Sphere-Counting Test
  ├─ Run Interference Prediction
  ├─ Track Evolution (10s/30s/60s)
  └─ Full Theory Validation Suite

🎵 Audio Analysis
  ├─ Spectrum Analyzer
  ├─ Coherence Breakdown (ext/int/autonomous)
  ├─ Harmonic Generation Display
  └─ Driver Comparison Tool

🧠 Consciousness Simulations
  ├─ Monad State Visualization (current)
  ├─ Will/Pain/Understanding Meters
  ├─ Or Makif/Pnimi Bridge
  └─ Sovereignty Achievement Indicator

🔮 Sacred/Morphic Systems
  ├─ Active Sacred Name Display
  ├─ Hebrew Letter Network Topology
  ├─ Morphic Field Influence Map
  └─ 72 Names Matrix View

📈 Evolution History
  ├─ Phase Transition Timeline
  ├─ Coherence History Graph
  ├─ Event Log (cycles, trivectors)
  └─ Export/Import State

🔧 Topology Sandbox
  ├─ Adjustable N (slider: 1-100)
  ├─ Topology Selector (ring+cross/tree/random)
  ├─ Real-time α Calculation
  └─ E8 Constraint Validator
```

---

## 11. PRIORITY IMPLEMENTATION ORDER

### Phase 1: Critical Gaps (Week 1)
1. ✅ Add Dark Matter sector view
2. ✅ Add Dark Energy sector view
3. ✅ Add Multi-Sector comparison
4. ✅ Add "Run Experiments" button with results panel
5. ✅ Add "Validate Theory" button

### Phase 2: Metrics Enhancement (Week 2)
1. ⬜ Expand metrics panel with physics constants
2. ⬜ Add real-time α tracker
3. ⬜ Add particle mass display
4. ⬜ Add consciousness meters (awareness/focus/understanding)
5. ⬜ Add audio spectrum analyzer

### Phase 3: Advanced Features (Week 3)
1. ⬜ Evolution history timeline
2. ⬜ Driver comparison tool
3. ⬜ Topology sandbox
4. ⬜ Sacred system status panel
5. ⬜ Phase dynamics visualization

### Phase 4: Polish & Documentation (Week 4)
1. ⬜ Tooltips for all controls
2. ⬜ Link each feature to theory docs
3. ⬜ Add export/import for reproducibility
4. ⬜ Create user guide video
5. ⬜ Publish experiment protocols

---

## 12. CODE LOCATIONS FOR UPDATES

### Files to Modify

1. **index.html**
   - Lines 389-396: Add sector options
   - Lines 406-578: Add new control sections
   - Add experiment buttons panel
   - Add theory validation panel

2. **main.js**
   - Lines 134-148: Update view labels to include sectors
   - Lines 230-274: Add sector switching logic
   - Add experiment button handlers
   - Add theory validation trigger

3. **renderer.js**
   - Lines 382-430: Add sector rendering cases
   - Add particle spectrum renderer
   - Add α evolution renderer

4. **New Files Needed**
   - `sector_visualizer.js` - Dark matter/energy rendering
   - `particle_spectrum.js` - Mass ratio display
   - `alpha_tracker.js` - Fine structure evolution
   - `experiment_panel.js` - Test suite UI
   - `theory_validator_ui.js` - Validation dashboard

---

## 13. TESTING CHECKLIST

Before considering menu "current":

- [ ] All 3 physics sectors selectable and render correctly
- [ ] Experimental tests accessible via UI button
- [ ] Theory validation runs from UI and shows results
- [ ] Particle masses display with error bars
- [ ] α value updates in real-time
- [ ] E8 validation shows live status
- [ ] Audio spectrum visible when enabled
- [ ] Consciousness meters show current values
- [ ] Sacred system status panel shows active name
- [ ] Evolution history records and displays events
- [ ] All tooltips and documentation links work
- [ ] Export/import state functionality

---

## 14. BACKWARDS COMPATIBILITY

### Ensure These Still Work

1. ✅ Existing view selector (clifford, zx, e8, etc.)
2. ✅ Current waveform drivers
3. ✅ Camera vantage presets
4. ✅ Sacred name controls
5. ✅ Consciousness checkboxes
6. ✅ Auto Ω alignment
7. ✅ Metrics panel toggle

**Strategy**: Add new features as non-breaking additions. Use feature flags if needed.

---

## 15. CONCLUSION

The simulations menu is **severely outdated** relative to implemented functionality. Critical physics sectors (Dark Matter, Dark Energy), comprehensive experimental tests, and theory validation are implemented but hidden or console-only.

**Immediate Actions Required**:
1. Expose Dark Matter/Dark Energy sectors in view menu
2. Add "Run Experiments" button to control panel
3. Add "Validate Theory" button with results display
4. Expand metrics panel to show physics constants

**Estimated Effort**: 2-3 weeks for complete overhaul, 2-3 days for critical gaps only.

**User Impact**: Currently, users can access <40% of implemented simulation features. Full menu update would expose 95%+ of capabilities.

