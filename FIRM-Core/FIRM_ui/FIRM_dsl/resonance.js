import { compute_cycle_basis_signature, compute_phase_histogram_signature, derive_minimal_qpi_bins, similarity_S } from './coherence.js';
import { validate_object_g } from './core.js';

export function deriveOmegaSignature(graph) {
  validate_object_g(graph);
  const cycles = compute_cycle_basis_signature(graph);
  
  // THEORY REQUIREMENT: Ω represents the omega-limit set (attractor basin) for the system
  // As the fundamental harmonic of the whole system, it must accommodate ALL possible
  // phase denominators the system can produce (up to 64, requiring bins = 2*64 = 128).
  // This is NOT derived from current graph state - it's the theoretical maximum.
  // Derivation: EsotericGuidance/Topology_and_Dynamics.md (omega-limit set definition)
  const OMEGA_MAX_BINS = 128; // 2 * 64 (max phase denominator cap)
  
  const phase_hist = compute_phase_histogram_signature(graph, OMEGA_MAX_BINS);
  return { cycles, phase_bins: OMEGA_MAX_BINS, phase_hist };
}

export function computeResonanceAlignment(graph, omega) {
  validate_object_g(graph);
  if (!omega || !Number.isInteger(omega.phase_bins) || omega.phase_bins <= 0) {
    throw new Error('Invalid omega signature');
  }
  const cycles_s = compute_cycle_basis_signature(graph);
  const hist_s = compute_phase_histogram_signature(graph, omega.phase_bins);
  return similarity_S(cycles_s, omega.cycles || [], hist_s, omega.phase_hist || new Array(omega.phase_bins).fill(0));
}


