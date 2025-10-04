import { compute_cycle_basis_signature, compute_phase_histogram_signature, derive_minimal_qpi_bins, similarity_S } from './coherence.js';
import { validate_object_g } from './core.js';

export function deriveOmegaSignature(graph) {
  validate_object_g(graph);
  const cycles = compute_cycle_basis_signature(graph);
  const phase_bins = derive_minimal_qpi_bins(graph);
  const phase_hist = compute_phase_histogram_signature(graph, phase_bins);
  return { cycles, phase_bins, phase_hist };
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


