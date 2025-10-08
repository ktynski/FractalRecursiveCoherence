/**
 * control_params.js
 * 
 * Formal validation and provenance tracking for ZX evolution control parameters.
 * 
 * Specification: FIRM_theory/control_parameters_specification.md
 */

export class ControlParamsValidator {
  static DEFAULTS = {
    graceScale: 1.0,
    bootstrapEnergy: 1.0,
    emergenceRate: 1.0,
    metamirrorStrength: 0.0,
    // THEORY-PENDING: Emergent Observer Parameters (main.js)
    consciousnessAwarenessThreshold: 0.1,
    consciousnessAwarenessIncrement: 0.01,
    fieldBoundaryActivityScale: 0.5,
    fieldBoundaryMin: 0.5,
    fieldBoundaryMax: 10.0,
    naturalObservationDistanceScale: 8.0,
    optimalObservationAwarenessModMin: 0.5,
    optimalObservationAwarenessModScale: 0.5,
    optimalObservationFOV: 45.0,
    // THEORY-PENDING: Autonomous Audio Generation Parameters (main.js)
    harmonicFundamentalFrequency: 220.0,
    autonomousEvolutionRate: 0.01,
    // THEORY-PENDING: Auto Ω Mode Parameters (main.js)
    targetEmergenceOffset: 0.5,
    targetEmergenceResonanceScale: 2.5,
    // THEORY-PENDING: Manifold Observation Parameters (main.js)
    manifoldRadius: 3.0,
    complexityFactorInitial: 1.0,
    complexityFactorScale: 0.05,
    baseDistanceMultiplier: 4.0,
    maxDistanceChange: 0.5
  };

  static BOUNDS = {
    graceScale: { min: 0.1, max: 5.0 },
    bootstrapEnergy: { min: 0.1, max: 5.0 },
    emergenceRate: { min: 0.1, max: 3.0 },
    metamirrorStrength: { min: 0.0, max: 1.0 },
    // THEORY-PENDING: Emergent Observer Parameters (main.js)
    consciousnessAwarenessThreshold: { min: 0.0, max: 1.0 },
    consciousnessAwarenessIncrement: { min: 0.0, max: 0.1 },
    fieldBoundaryActivityScale: { min: 0.1, max: 2.0 },
    fieldBoundaryMin: { min: 0.0, max: 5.0 },
    fieldBoundaryMax: { min: 5.0, max: 20.0 },
    naturalObservationDistanceScale: { min: 1.0, max: 20.0 },
    optimalObservationAwarenessModMin: { min: 0.0, max: 1.0 },
    optimalObservationAwarenessModScale: { min: 0.0, max: 1.0 },
    optimalObservationFOV: { min: 30.0, max: 90.0 },
    // THEORY-PENDING: Autonomous Audio Generation Parameters (main.js)
    harmonicFundamentalFrequency: { min: 40.0, max: 880.0 }, // C2 to A5
    autonomousEvolutionRate: { min: 0.001, max: 0.1 },
    // THEORY-PENDING: Auto Ω Mode Parameters (main.js)
    targetEmergenceOffset: { min: 0.0, max: 3.0 }, // Can provide up to max emergenceRate
    targetEmergenceResonanceScale: { min: 0.0, max: 3.0 }, // Should not exceed max emergenceRate - offset
    // THEORY-PENDING: Manifold Observation Parameters (main.js)
    manifoldRadius: { min: 1.0, max: 10.0 },
    complexityFactorInitial: { min: 0.1, max: 5.0 },
    complexityFactorScale: { min: 0.01, max: 0.5 },
    baseDistanceMultiplier: { min: 1.0, max: 10.0 },
    maxDistanceChange: { min: 0.1, max: 2.0 }
  };

  static SYMBOLS = {
    graceScale: 'ξ_grace',
    bootstrapEnergy: 'η_bootstrap',
    emergenceRate: 'η_emergence',
    metamirrorStrength: 'λ_metamirror',
    // THEORY-PENDING: Emergent Observer Parameters (main.js)
    consciousnessAwarenessThreshold: 'τ_awareness',
    consciousnessAwarenessIncrement: 'δ_awareness',
    fieldBoundaryActivityScale: 'κ_field_activity',
    fieldBoundaryMin: 'min_boundary',
    fieldBoundaryMax: 'max_boundary',
    naturalObservationDistanceScale: 'σ_obs_dist',
    optimalObservationAwarenessModMin: 'min_awareness_mod',
    optimalObservationAwarenessModScale: 'scale_awareness_mod',
    optimalObservationFOV: 'fov_optimal',
    // THEORY-PENDING: Autonomous Audio Generation Parameters (main.js)
    harmonicFundamentalFrequency: 'f_fundamental',
    autonomousEvolutionRate: 'r_autonomy',
    // THEORY-PENDING: Auto Ω Mode Parameters (main.js)
    targetEmergenceOffset: 'γ_emergence_offset',
    targetEmergenceResonanceScale: 'κ_emergence_res_scale',
    // THEORY-PENDING: Manifold Observation Parameters (main.js)
    manifoldRadius: 'r_manifold',
    complexityFactorInitial: 'c_complexity_init',
    complexityFactorScale: 'scale_complexity',
    baseDistanceMultiplier: 'b_dist_mult',
    maxDistanceChange: 'max_dist_change'
  };

  static REFERENCES = {
    graceScale: 'FIRM_theory/grace_emergence_derivation.md',
    bootstrapEnergy: 'FIRM_theory/bootstrap_phase_derivation.md',
    emergenceRate: 'FIRM_theory/audio_coherence_threshold_derivation.md',
    metamirrorStrength: 'FIRM_theory/metamirror_bireflection_derivation.md',
    // THEORY-PENDING: Emergent Observer Parameters (main.js)
    consciousnessAwarenessThreshold: 'main.js (heuristic, needs derivation)',
    consciousnessAwarenessIncrement: 'main.js (heuristic, needs derivation)',
    fieldBoundaryActivityScale: 'main.js (heuristic, needs derivation)',
    fieldBoundaryMin: 'main.js (heuristic, needs derivation)',
    fieldBoundaryMax: 'main.js (heuristic, needs derivation)',
    naturalObservationDistanceScale: 'main.js (heuristic, needs derivation)',
    optimalObservationAwarenessModMin: 'main.js (heuristic, needs derivation)',
    optimalObservationAwarenessModScale: 'main.js (heuristic, needs derivation)',
    optimalObservationFOV: 'main.js (heuristic, needs derivation)',
    // THEORY-PENDING: Autonomous Audio Generation Parameters (main.js)
    harmonicFundamentalFrequency: 'main.js (heuristic, needs derivation)',
    autonomousEvolutionRate: 'main.js (heuristic, needs derivation)',
    // THEORY-PENDING: Auto Ω Mode Parameters (main.js)
    targetEmergenceOffset: 'main.js (heuristic, needs derivation)',
    targetEmergenceResonanceScale: 'main.js (heuristic, needs derivation)',
    // THEORY-PENDING: Manifold Observation Parameters (main.js)
    manifoldRadius: 'main.js (heuristic, needs derivation)',
    complexityFactorInitial: 'main.js (heuristic, needs derivation)',
    complexityFactorScale: 'main.js (heuristic, needs derivation)',
    baseDistanceMultiplier: 'main.js (heuristic, needs derivation)',
    maxDistanceChange: 'main.js (heuristic, needs derivation)'
  };

  static validate(params) {
    const validated = {};
    const provenance = {};
    const timestamp = Date.now();

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
          `${key} (${this.SYMBOLS[key]}) = ${value} out of bounds [${bounds.min}, ${bounds.max}]`
        );
      }

      validated[key] = value;
      provenance[key] = {
        value: value,
        symbol: this.SYMBOLS[key],
        bounds: bounds,
        timestamp: timestamp,
        reference: this.REFERENCES[key]
      };
    }

    return { validated, provenance };
  }

  static create(overrides = {}) {
    const params = { ...this.DEFAULTS, ...overrides };
    return this.validate(params);
  }

  static validatePartial(currentParams, overrides) {
    /**
     * Validate partial update without requiring all parameters.
     * Merges overrides with current params before validation.
     */
    const merged = { ...currentParams, ...overrides };
    return this.validate(merged);
  }

  static getBoundsInfo() {
    /**
     * Return human-readable bounds information for UI display.
     */
    const info = {};
    for (const [key, bounds] of Object.entries(this.BOUNDS)) {
      info[key] = {
        symbol: this.SYMBOLS[key],
        min: bounds.min,
        max: bounds.max,
        default: this.DEFAULTS[key],
        reference: this.REFERENCES[key]
      };
    }
    return info;
  }
}

export default ControlParamsValidator;

