/**
 * Textual export checks for FIRM_audio/index.js without executing in Node.
 */
const fs = require('fs');
const path = require('path');

test('FIRM_audio/index.js defines expected exports', () => {
  const p = path.join(__dirname, '..', 'FIRM_audio', 'index.js');
  expect(fs.existsSync(p)).toBe(true);
  const src = fs.readFileSync(p, 'utf8');
  expect(src).toContain('export function createOscillatorBank');
  expect(src).toContain('export function setupAnalyser');
  expect(src).toContain('export function computeParsevalEnergy');
  expect(src).toContain('export function createCoherentFeedbackLoop');
});


