/**
 * dynamic_evolution.js
 *
 * JavaScript implementation of dynamic phase evolution for Soul Garbage Collection.
 *
 * Implements the theoretical equation:
 * dΦ_i/dt = -α_i ∇_Φ D_i + β_i Transmute(D_i) + γ_i Grace(Φ_i)
 *
 * This bridges the gap between static analysis and dynamic evolution in the 𝒮-GC system.
 */

// Import existing DSL modules
import { ObjectG } from './core.js';
import { computeResonanceAlignment, deriveOmegaSignature } from './resonance.js';
import { compute_coherence } from './coherence.js';
import { FieldRegime } from './soul_garbage_collection.js';

// Evolution states enum
export const EvolutionState = {
    STABLE: 'stable',
    EVOLVING: 'evolving',
    CONVERGING: 'converging',
    DIVERGING: 'diverging',
    OSCILLATING: 'oscillating'
};

// Evolution metrics class
export class EvolutionMetrics {
    constructor() {
        this.coherence_history = [];
        this.resonance_history = [];
        this.phase_history = [];
        this.evolution_rate = 0.0;
        this.convergence_rate = 0.0;
        this.oscillation_amplitude = 0.0;
        this.state = EvolutionState.STABLE;
    }
}

// Dynamic phase evolution class
export class DynamicPhaseEvolution {
    constructor(alpha_i = 0.5, beta_i = 0.3, gamma_i = 0.4, dt = 0.01) {
        this.alpha_i = alpha_i;  // Resonance gradient coefficient
        this.beta_i = beta_i;    // Transmutation coefficient
        this.gamma_i = gamma_i;  // Grace field coefficient
        this.dt = dt;            // Time step for evolution
        this.max_iterations = 1000;
        this.convergence_threshold = 1e-6;
        this.oscillation_threshold = 0.1;

        // Validate coefficients
        if (![this.alpha_i, this.beta_i, this.gamma_i].every(c => c >= 0)) {
            throw new Error("All evolution coefficients must be non-negative");
        }
    }

    computeDissonanceGradient(phi_i, omega, structure) {
        // Get current structure resonance (which measures dissonance)
        const currentResonance = computeResonanceAlignment(structure, omega);
        const dissonance = 1.0 - currentResonance;

        // Estimate gradient by perturbing phase slightly
        const epsilon = 1e-6;
        const perturbedStructure = this._perturbPhase(structure, epsilon);
        const perturbedResonance = computeResonanceAlignment(perturbedStructure, omega);
        const perturbedDissonance = 1.0 - perturbedResonance;

        const gradient = (perturbedDissonance - dissonance) / epsilon;
        return gradient;
    }

    computeTransmutation(phi_i, omega, structure) {
        // Simplified transmutation based on structure connectivity and phase diversity
        const coherence = compute_coherence(structure);

        // Transmutation factor based on phase diversity within structure
        const phaseDiversity = this._computePhaseDiversity(structure);

        // Transmutation promotes structures with balanced phase diversity
        // Optimal diversity around 0.5-0.7 for good mediation
        const optimalDiversity = 0.6;
        const transmutationFactor = 1.0 - Math.abs(phaseDiversity - optimalDiversity);

        return coherence * transmutationFactor;
    }

    computeGraceField(phi_i, fieldRegime) {
        // Grace field strength varies by regime
        const regimeMultipliers = {
            [FieldRegime.NON_BEING]: 0.1,
            [FieldRegime.VACUUM]: 0.3,
            [FieldRegime.DARK_SECTOR]: 0.6,
            [FieldRegime.MATTER]: 0.8,
            [FieldRegime.OMEGA]: 1.0
        };

        const baseGrace = regimeMultipliers[fieldRegime] || 0.5;

        // Grace field also depends on current phase coherence
        // More coherent phases receive stronger grace field guidance
        // Canonical baseline: φ⁻¹ ≈ 0.618 represents natural vacuum potential
        const PHI_INVERSE = 1 / 1.618033988749;  // ≈ 0.618
        const phaseCoherenceFactor = Math.min(1.0, phi_i / PHI_INVERSE);

        return baseGrace * phaseCoherenceFactor;
    }

    evolveStructure(structure, omega, fieldRegime, maxSteps = null) {
        // Create a copy of the structure for evolution
        let currentStructure = new ObjectG({
            nodes: [...structure.nodes],
            edges: [...structure.edges],
            labels: {...structure.labels}
        });

        const metrics = new EvolutionMetrics();
        const maxIterations = maxSteps || this.max_iterations;

        for (let step = 0; step < maxIterations; step++) {
            // Compute current state
            const currentCoherence = compute_coherence(currentStructure);
            const currentResonance = computeResonanceAlignment(currentStructure, omega);

            // Extract representative phase for evolution (simplified)
            const phi_i = this._extractRepresentativePhase(currentStructure);

            // Compute evolution terms
            const dissonanceGradient = this.computeDissonanceGradient(phi_i, omega, currentStructure);
            const transmutationTerm = this.computeTransmutation(phi_i, omega, currentStructure);
            const graceTerm = this.computeGraceField(phi_i, fieldRegime);

            // Apply evolution equation: dΦ_i/dt = -α ∇_Φ D_i + β Transmute + γ Grace
            const phaseDerivative = (
                -this.alpha_i * dissonanceGradient +
                this.beta_i * transmutationTerm +
                this.gamma_i * graceTerm
            );

            // Update phase
            const newPhi_i = phi_i + phaseDerivative * this.dt;

            // Apply phase update to structure
            const evolvedStructure = this._applyPhaseEvolution(currentStructure, phi_i, newPhi_i, omega);

            // Update metrics
            const evolvedCoherence = compute_coherence(evolvedStructure);
            const evolvedResonance = computeResonanceAlignment(evolvedStructure, omega);

            metrics.coherence_history.push(evolvedCoherence);
            metrics.resonance_history.push(evolvedResonance);
            metrics.phase_history.push({ step, phase: newPhi_i });

            // Check convergence
            if (this._checkConvergence(metrics, step)) {
                metrics.state = EvolutionState.CONVERGING;
                break;
            }

            // Check oscillation
            if (this._checkOscillation(metrics, step)) {
                metrics.state = EvolutionState.OSCILLATING;
                break;
            }

            currentStructure = evolvedStructure;

            // Safety check for divergence
            if (this._checkDivergence(metrics, step)) {
                metrics.state = EvolutionState.DIVERGING;
                break;
            }
        }

        // Final metrics computation
        this._computeFinalMetrics(metrics);

        return { evolvedStructure: currentStructure, metrics };
    }

    _perturbPhase(structure, epsilon) {
        // Create a perturbed version of the structure for gradient computation
        const perturbedStructure = new ObjectG({
            nodes: [...structure.nodes],
            edges: [...structure.edges],
            labels: {...structure.labels}
        });

        // Perturb a representative node's phase
        if (perturbedStructure.labels && Object.keys(perturbedStructure.labels).length > 0) {
            const firstNodeId = Object.keys(perturbedStructure.labels)[0];
            const originalLabel = perturbedStructure.labels[firstNodeId];

            // Add small phase perturbation
            const newNumer = originalLabel.phase_numer + epsilon;
            const newDenom = originalLabel.phase_denom;

            perturbedStructure.labels[firstNodeId] = {
                kind: originalLabel.kind,
                phase_numer: Math.round(newNumer),
                phase_denom: newDenom,
                monadic_id: originalLabel.monadic_id
            };
        }

        return perturbedStructure;
    }

    _computePhaseDiversity(structure) {
        if (!structure.labels || Object.keys(structure.labels).length === 0) {
            return 0.0;
        }

        const phases = [];
        for (const label of Object.values(structure.labels)) {
            const phaseAngle = 2 * Math.PI * label.phase_numer / label.phase_denom;
            phases.push(phaseAngle);
        }

        if (phases.length <= 1) {
            return 0.0;
        }

        // Compute standard deviation of phases normalized to [0,1]
        const meanPhase = phases.reduce((sum, p) => sum + p, 0) / phases.length;
        const variance = phases.reduce((sum, p) => sum + Math.pow(p - meanPhase, 2), 0) / phases.length;
        const stdDev = Math.sqrt(variance);

        // Normalize to [0,1] range (max possible std dev is π)
        return Math.min(1.0, stdDev / Math.PI);
    }

    _extractRepresentativePhase(structure) {
        if (!structure.labels || Object.keys(structure.labels).length === 0) {
            return 0.0;
        }

        // Use average phase as representative
        let totalPhase = 0.0;
        let count = 0;

        for (const label of Object.values(structure.labels)) {
            const phaseAngle = 2 * Math.PI * label.phase_numer / label.phase_denom;
            totalPhase += phaseAngle;
            count++;
        }

        return count > 0 ? totalPhase / count : 0.0;
    }

    _applyPhaseEvolution(structure, oldPhi, newPhi, omega) {
        const evolvedStructure = new ObjectG({
            nodes: [...structure.nodes],
            edges: [...structure.edges],
            labels: {...structure.labels}
        });

        // Apply phase evolution to all nodes (simplified approach)
        const phaseShift = newPhi - oldPhi;

        for (const [nodeId, label] of Object.entries(evolvedStructure.labels)) {
            // Convert phase shift back to rational representation
            const oldPhaseAngle = 2 * Math.PI * label.phase_numer / label.phase_denom;
            const newPhaseAngle = oldPhaseAngle + phaseShift;

            // Convert back to rational (simplified)
            const newNumer = Math.round(newPhaseAngle * label.phase_denom / (2 * Math.PI));
            const clampedNumer = newNumer % (2 * label.phase_denom);

            evolvedStructure.labels[nodeId] = {
                kind: label.kind,
                phase_numer: clampedNumer,
                phase_denom: label.phase_denom,
                monadic_id: label.monadic_id
            };
        }

        return evolvedStructure;
    }

    _checkConvergence(metrics, step) {
        if (metrics.coherence_history.length < 10) {
            return false;
        }

        const recentCoherence = metrics.coherence_history.slice(-10);
        const coherenceRange = Math.max(...recentCoherence) - Math.min(...recentCoherence);

        return coherenceRange < this.convergence_threshold;
    }

    _checkOscillation(metrics, step) {
        if (metrics.coherence_history.length < 20) {
            return false;
        }

        const recentCoherence = metrics.coherence_history.slice(-20);
        let oscillations = 0;

        for (let i = 1; i < recentCoherence.length - 1; i++) {
            if ((recentCoherence[i] - recentCoherence[i-1]) * (recentCoherence[i+1] - recentCoherence[i]) < 0) {
                oscillations++;
            }
        }

        const oscillationRatio = oscillations / (recentCoherence.length - 2);
        return oscillationRatio > 0.3; // More than 30% of steps are oscillation points
    }

    _checkDivergence(metrics, step) {
        if (metrics.coherence_history.length < 5) {
            return false;
        }

        // Check if coherence is consistently decreasing or becoming erratic
        const recentCoherence = metrics.coherence_history.slice(-5);
        if (recentCoherence.every(c => c < 0.1)) {
            return true;
        }

        // Check for rapid degradation
        const coherenceTrend = recentCoherence[recentCoherence.length - 1] - recentCoherence[0];
        return coherenceTrend < -0.5; // Rapid coherence loss
    }

    _computeFinalMetrics(metrics) {
        if (metrics.coherence_history.length < 2) {
            return;
        }

        // Evolution rate (change per step)
        const coherenceChanges = [];
        for (let i = 0; i < metrics.coherence_history.length - 1; i++) {
            coherenceChanges.push(metrics.coherence_history[i+1] - metrics.coherence_history[i]);
        }
        metrics.evolution_rate = coherenceChanges.reduce((sum, change) => sum + change, 0) / coherenceChanges.length;

        // Convergence rate (how quickly approaching final state)
        if (metrics.coherence_history.length >= 10) {
            const finalCoherence = metrics.coherence_history[metrics.coherence_history.length - 1];
            const initialCoherence = metrics.coherence_history[0];

            if (Math.abs(finalCoherence - initialCoherence) > 1e-6) {
                const totalChange = finalCoherence - initialCoherence;
                const stepsNeeded = metrics.coherence_history.length;
                metrics.convergence_rate = totalChange / stepsNeeded;
            }
        }

        // Oscillation amplitude
        if (metrics.coherence_history.length >= 20) {
            const recentCoherence = metrics.coherence_history.slice(-20);
            metrics.oscillation_amplitude = Math.max(...recentCoherence) - Math.min(...recentCoherence);
        }
    }
}

// Mode coefficients management
export class ModeCoefficients {
    constructor() {
        this.coefficient_sets = {
            [FieldRegime.NON_BEING]: [0.1, 0.1, 0.1],
            [FieldRegime.VACUUM]: [0.3, 0.2, 0.4],
            [FieldRegime.DARK_SECTOR]: [0.5, 0.4, 0.6],
            [FieldRegime.MATTER]: [0.7, 0.6, 0.8],
            [FieldRegime.OMEGA]: [1.0, 1.0, 1.0]
        };
    }

    getCoefficients(fieldRegime) {
        return this.coefficient_sets[fieldRegime] || [0.5, 0.5, 0.5];
    }

    adaptCoefficients(fieldRegime, evolutionMetrics) {
        const baseCoeffs = this.getCoefficients(fieldRegime);

        // Adjust based on evolution state
        if (evolutionMetrics.state === EvolutionState.DIVERGING) {
            // Reduce coefficients to slow down evolution
            const adaptationFactor = 0.7;
            return baseCoeffs.map(c => c * adaptationFactor);
        } else if (evolutionMetrics.state === EvolutionState.OSCILLATING) {
            // Reduce alpha (resonance gradient) to dampen oscillations
            const alphaFactor = 0.6;
            return [baseCoeffs[0] * alphaFactor, baseCoeffs[1], baseCoeffs[2]];
        } else if (evolutionMetrics.state === EvolutionState.CONVERGING) {
            // Slightly increase coefficients for faster convergence
            const adaptationFactor = 1.2;
            return baseCoeffs.map(c => c * adaptationFactor);
        } else {
            return baseCoeffs;
        }
    }
}

// Factory functions
export function createDynamicEvolution(alpha = 0.5, beta = 0.3, gamma = 0.4, dt = 0.01) {
    return new DynamicPhaseEvolution(alpha, beta, gamma, dt);
}

export function createModeCoefficients() {
    return new ModeCoefficients();
}
