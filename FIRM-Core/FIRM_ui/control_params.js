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
    metamirrorStrength: 0.0
  };

  static BOUNDS = {
    graceScale: { min: 0.1, max: 5.0 },
    bootstrapEnergy: { min: 0.1, max: 5.0 },
    emergenceRate: { min: 0.1, max: 3.0 },
    metamirrorStrength: { min: 0.0, max: 1.0 }
  };

  static SYMBOLS = {
    graceScale: 'ξ_grace',
    bootstrapEnergy: 'η_bootstrap',
    emergenceRate: 'η_emergence',
    metamirrorStrength: 'λ_metamirror'
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

