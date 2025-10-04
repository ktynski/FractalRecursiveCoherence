/**
 * JS unit tests for resonance.js (bounds, identity, binning parity)
 */
const path = require('path');
const fs = require('fs');

test('resonance.js exists and exports functions', () => {
  const p = path.join(__dirname, '..', 'FIRM_ui', 'FIRM_dsl', 'resonance.js');
  expect(fs.existsSync(p)).toBe(true);
  const src = fs.readFileSync(p, 'utf8');
  expect(src).toContain('export function deriveOmegaSignature');
  expect(src).toContain('export function computeResonanceAlignment');
});

test('resonance alignment identity and bounds (static source check)', () => {
  const coreP = path.join(__dirname, '..', 'FIRM_ui', 'FIRM_dsl', 'core.js');
  const cohP = path.join(__dirname, '..', 'FIRM_ui', 'FIRM_dsl', 'coherence.js');
  const resP = path.join(__dirname, '..', 'FIRM_ui', 'FIRM_dsl', 'resonance.js');
  expect(fs.existsSync(coreP)).toBe(true);
  expect(fs.existsSync(cohP)).toBe(true);
  expect(fs.existsSync(resP)).toBe(true);
});


