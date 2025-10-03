import { validate_object_g } from '../FIRM_dsl/core.js';

export class MultivectorField {
  constructor(payload) {
    this.payload = payload;
    Object.freeze(this.payload);
    Object.freeze(this);
  }
}

export function phi_zx_to_clifford(graph) {
  validate_object_g(graph);
  const components = new Array(16).fill(0);

  for (const [nodeId, label] of Object.entries(graph.labels)) {
    const phaseRad = Math.PI * label.phase_numer / label.phase_denom;
    const degree = graph.edges.reduce((deg, [u, v]) => deg + (u === Number(nodeId) || v === Number(nodeId) ? 1 : 0), 0);
    const weight = Math.sqrt(1 + degree);

    if (label.kind === 'Z') {
      const scalarPart = weight * Math.cos(phaseRad / 2);
      const bivectorPart = weight * Math.sin(phaseRad / 2);
      components[0] += scalarPart;
      components[5] += bivectorPart;
    } else if (label.kind === 'X') {
      const biv12 = weight * Math.cos(phaseRad);
      const biv13 = weight * Math.sin(phaseRad);
      components[6] += biv12;
      components[7] += biv13;
    }
  }

  const magnitudeSq = components.reduce((acc, c) => acc + c * c, 0);
  if (magnitudeSq > 0) {
    const norm = Math.sqrt(magnitudeSq);
    for (let i = 0; i < components.length; i += 1) {
      components[i] /= norm;
    }
  }

  return new MultivectorField({ components, algebra: 'Cl(1,3)' });
}
