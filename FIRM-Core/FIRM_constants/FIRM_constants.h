// FIRM_constants.h
//
// Macro namespace for derived constants. No numeric literals are permitted here
// without provenance. Each macro must be populated by a generated header
// produced from FIRM_derivations.py, which cites theorem/proof ids.
//
// Example (to be generated):
// #define FIRM_PHASE_UNIT /* derived: 2π / n, proof id: THM-PHASE-001 */
// #define FIRM_ECHO_THRESHOLD /* derived: saddle point of C(G), proof id: THM-THETA-001 */
// #define FIRM_GRACE_IDEMPOTENT 1
//
// Attempting to include this header before generation should fail the build.
#ifdef FIRM_CONSTANTS_UNDERIVED
#error "FIRM constants are not yet derived. Run derivation pipeline."
#endif
