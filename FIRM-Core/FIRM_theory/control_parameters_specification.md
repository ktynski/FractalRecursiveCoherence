# Control Parameters: Formal Specification

**Provenance**: Synthesized from `grace_emergence_derivation.md`, `audio_coherence_threshold_derivation.md`, `bootstrap_phase_derivation.md`, and `EsotericGuidance/Topology_and_Dynamics.md`.

**Purpose**: Formalize ad-hoc control parameters with theory-derived bounds, validation, and provenance tracking.

---

## 1. Parameter Catalog

### 1.1 Grace Scale (graceScale)

**Symbol**: ξ_grace  
**Domain**: [0.1, 5.0] ⊂ ℝ⁺  
**Default**: 1.0  
**Unit**: dimensionless (scaling factor)

**Physical Meaning**:
Modulates the strength of grace emergence relative to baseline φ-scaling.

**Theory Derivation**:
From `grace_emergence_derivation.md` Section 2.3:
```
synthesisStrength = resonance · degreeDecay · ξ_grace
```

**Bounds Justification**:
- **Lower bound (0.1)**: Prevents complete suppression of grace (acausality requires thresholdless operation)
- **Upper bound (5.0)**: Prevents runaway emergence that violates φ-scaling property
- **Default (1.0)**: Neutral scaling maintains canonical φ behavior

**Validation**:
```javascript
function validateGraceScale(value) {
  if (!Number.isFinite(value)) throw new Error('graceScale must be finite');
  if (value < 0.1 || value > 5.0) throw new Error('graceScale must be in [0.1, 5.0]');
  return value;
}
```

---

### 1.2 Bootstrap Energy (bootstrapEnergy)

**Symbol**: η_bootstrap  
**Domain**: [0.1, 5.0] ⊂ ℝ⁺  
**Default**: 1.0  
**Unit**: dimensionless (amplitude modulation)

**Physical Meaning**:
Controls initial energy available for void → form transition during bootstrap.

**Theory Derivation**:
From `bootstrap_phase_derivation.md` Section 4:
```
α_scaled = min(1, α_audio · η_bootstrap)
α_X = round(α_scaled · φ · 4) mod 16
α_Z = round(α_scaled · 2) mod 16
```

**Bounds Justification**:
- **Lower bound (0.1)**: Ensures non-zero bootstrap energy (prevents collapse to void)
- **Upper bound (5.0)**: Prevents excessive phase excursions beyond π (quantum state validity)
- **Default (1.0)**: Canonical energy matches audio coherence directly

**Validation**:
```javascript
function validateBootstrapEnergy(value) {
  if (!Number.isFinite(value)) throw new Error('bootstrapEnergy must be finite');
  if (value < 0.1 || value > 5.0) throw new Error('bootstrapEnergy must be in [0.1, 5.0]');
  return value;
}
```

---

### 1.3 Emergence Rate (emergenceRate)

**Symbol**: η_emergence  
**Domain**: [0.1, 3.0] ⊂ ℝ⁺  
**Default**: 1.0  
**Unit**: dimensionless (timescale modulation)

**Physical Meaning**:
Controls overall timescale of evolution dynamics. Higher rate → faster evolution.

**Theory Derivation**:
From `audio_coherence_threshold_derivation.md` Section 4.2:
```
ΔC_threshold(α, η) = η · 0.15 · (1 - 0.67·α)
```

**Bounds Justification**:
- **Lower bound (0.1)**: Prevents freezing of evolution dynamics
- **Upper bound (3.0)**: Prevents instability and numerical errors (CFL-like condition)
- **Default (1.0)**: Natural timescale matching frame rate (60 fps)

**Validation**:
```javascript
function validateEmergenceRate(value) {
  if (!Number.isFinite(value)) throw new Error('emergenceRate must be finite');
  if (value < 0.1 || value > 3.0) throw new Error('emergenceRate must be in [0.1, 3.0]');
  return value;
}
```

---

### 1.4 Metamirror Strength (metamirrorStrength)

**Symbol**: λ_metamirror  
**Domain**: [0.0, 1.0] ⊂ ℝ  
**Default**: 0.0 (disabled)  
**Unit**: dimensionless (blend factor)

**Physical Meaning**:
Strength of bireflection (β operator) feedback blending current graph with mirror state.

**Theory Derivation**:
From `metamirror_bireflection_derivation.md` Section 3.1:
```
G_blend = (1-λ)·G + λ·β(G)
```

**Bounds Justification**:
- **Lower bound (0.0)**: No metamirror influence (current default during development)
- **Upper bound (1.0)**: Full metamirror replacement (maximum bireflection)
- **Default (0.0)**: Disabled until metamirror attractor dynamics validated

**Validation**:
```javascript
function validateMetamirrorStrength(value) {
  if (!Number.isFinite(value)) throw new Error('metamirrorStrength must be finite');
  if (value < 0.0 || value > 1.0) throw new Error('metamirrorStrength must be in [0.0, 1.0]');
  return value;
}
```

---

## 2. Formal ControlParams Type

### 2.1 TypeScript/JavaScript Interface

```typescript
interface ControlParams {
  graceScale: number;        // ξ_grace ∈ [0.1, 5.0]
  bootstrapEnergy: number;   // η_bootstrap ∈ [0.1, 5.0]
  emergenceRate: number;     // η_emergence ∈ [0.1, 3.0]
  metamirrorStrength: number; // λ_metamirror ∈ [0.0, 1.0]
}

interface ControlParamsProvenance {
  graceScale: { value: number, timestamp: number, source: string };
  bootstrapEnergy: { value: number, timestamp: number, source: string };
  emergenceRate: { value: number, timestamp: number, source: string };
  metamirrorStrength: { value: number, timestamp: number, source: string };
}
```

### 2.2 Validation Class

```javascript
class ControlParamsValidator {
  static DEFAULTS = {
    graceScale: 1.0,
    bootstrapEnergy: 1.0,
    emergenceRate: 1.0,
    metamirrorStrength: 0.0
  };

  static BOUNDS = {
    graceScale: { min: 0.1, max: 5.0 },
    bootstrapEnergy: { min: 0.1, max: 5.0 },
    emergenceRate: { min: 0.1, max: 3.0 },
    metamirrorStrength: { min: 0.0, max: 1.0 }
  };

  static REFERENCES = {
    graceScale: 'FIRM_theory/grace_emergence_derivation.md',
    bootstrapEnergy: 'FIRM_theory/bootstrap_phase_derivation.md',
    emergenceRate: 'FIRM_theory/audio_coherence_threshold_derivation.md',
    metamirrorStrength: 'FIRM_theory/metamirror_bireflection_derivation.md'
  };

  static validate(params) {
    const validated = {};
    const provenance = {};

    for (const [key, value] of Object.entries(params)) {
      if (!(key in this.BOUNDS)) {
        throw new Error(`Unknown control parameter: ${key}`);
      }

      if (!Number.isFinite(value)) {
        throw new Error(`${key} must be finite, got ${value}`);
      }

      const bounds = this.BOUNDS[key];
      if (value < bounds.min || value > bounds.max) {
        throw new Error(
          `${key} = ${value} out of bounds [${bounds.min}, ${bounds.max}]`
        );
      }

      validated[key] = value;
      provenance[key] = {
        value: value,
        timestamp: Date.now(),
        source: this.REFERENCES[key]
      };
    }

    return { validated, provenance };
  }

  static create(overrides = {}) {
    const params = { ...this.DEFAULTS, ...overrides };
    return this.validate(params);
  }
}
```

---

## 3. Implementation in ZXObjectGraphEngine

### 3.1 Current Implementation (Ad-Hoc)

```javascript
this._controlParams = {
  graceScale: 1.0,
  bootstrapEnergy: 1.0,
  emergenceRate: 1.0,
  metamirrorStrength: 0.0
};
```

**Issues**:
1. No validation
2. No bounds checking
3. No provenance tracking
4. No documentation of allowed values

### 3.2 Theory-Compliant Implementation

```javascript
import { ControlParamsValidator } from './control_params.js';

constructor() {
  // Initialize with validated defaults
  const { validated, provenance } = ControlParamsValidator.create();
  this._controlParams = validated;
  this._controlParamsProvenance = provenance;
}

updateControlParams(overrides) {
  const { validated, provenance } = ControlParamsValidator.validate({
    ...this._controlParams,
    ...overrides
  });
  
  this._controlParams = validated;
  
  // Merge provenance (track only changed params)
  for (const key of Object.keys(overrides)) {
    this._controlParamsProvenance[key] = provenance[key];
  }
  
  return this._controlParams;
}

getControlParamsProvenance() {
  return { ...this._controlParamsProvenance };
}
```

---

## 4. UI Integration

### 4.1 Slider Bounds

Update `index.html` sliders to match theory bounds:

```html
<!-- Grace Coherence: ξ_grace ∈ [0.1, 5.0] -->
<input type="range" id="graceSlider" 
  min="0.1" max="5.0" step="0.01" value="1.0">

<!-- Bootstrap Energy: η_bootstrap ∈ [0.1, 5.0] -->
<input type="range" id="bootstrapSlider" 
  min="0.1" max="5.0" step="0.01" value="1.0">

<!-- Emergence Rate: η_emergence ∈ [0.1, 3.0] -->
<input type="range" id="emergenceSlider" 
  min="0.1" max="3.0" step="0.01" value="1.0">
```

### 4.2 Validation on Change

```javascript
graceSlider.addEventListener('input', (e) => {
  try {
    const newParams = window.zxEvolutionEngine.updateControlParams({
      graceScale: parseFloat(e.target.value)
    });
    graceValue.textContent = newParams.graceScale.toFixed(3);
  } catch (error) {
    console.error('Invalid grace scale:', error.message);
    e.target.value = window.zxEvolutionEngine._controlParams.graceScale;
  }
});
```

---

## 5. Validation Tests

### 5.1 Bounds Checking Tests
1. **Reject out-of-bounds**: Attempting to set params outside bounds throws error
2. **Accept valid values**: All values within bounds accepted
3. **Default initialization**: Defaults match specified values

### 5.2 Provenance Tests
1. **Timestamp tracking**: Each update records timestamp
2. **Source reference**: Each param links to derivation document
3. **History preservation**: Can retrieve full param change history

---

## 6. Cross-References

- **Grace Emergence**: `FIRM_theory/grace_emergence_derivation.md`
- **Bootstrap Phases**: `FIRM_theory/bootstrap_phase_derivation.md`
- **Audio Threshold**: `FIRM_theory/audio_coherence_threshold_derivation.md`
- **Metamirror**: `FIRM_theory/metamirror_bireflection_derivation.md`
- **Implementation**: `FIRM-Core/FIRM_ui/zx_objectg_engine.js` lines 54-59, 84-91

---

## 7. Future Extensions

1. **Adaptive parameters**: Auto-tune based on coherence history
2. **Parameter presets**: Named configurations for specific emergence patterns
3. **Parameter coupling**: Constraints between related parameters
4. **Sensitivity analysis**: Track parameter influence on evolution metrics

---

**Document Status**: COMPLETE - Ready for implementation
**Last Updated**: 2025-01-03
**Next Steps**: Create ControlParamsValidator class and integrate with ZXObjectGraphEngine

