"""Constants header rendering: ordering and provenance enforcement.
"""
import importlib


def test_header_orders_keys_and_includes_provenance_comments():
    gen = importlib.import_module('FIRM_constants.generate_header')
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')

    r1 = deriv.DerivationResult(proof_id='THM-ECHO-THRESHOLD-CRITICAL-001', value=0.3678794412)
    r2 = deriv.DerivationResult(proof_id='THM-PHASE-UNIT-ZX-BIALGEBRA-001', value=0.7853981634)

    # Intentionally unsorted insertion order
    header = gen.render_header({
        'FIRM_ECHO_THRESHOLD': r1,
        'FIRM_PHASE_UNIT': r2,
    })

    # Ensure #define lines exist with proof comments
    assert '#define FIRM_ECHO_THRESHOLD' in header
    assert 'proof: THM-ECHO-THRESHOLD-CRITICAL-001' in header
    assert '#define FIRM_PHASE_UNIT' in header
    assert 'proof: THM-PHASE-UNIT-ZX-BIALGEBRA-001' in header

    # Ensure sorted order by name (ECHO before PHASE)
    echo_idx = header.index('FIRM_ECHO_THRESHOLD')
    phase_idx = header.index('FIRM_PHASE_UNIT')
    assert echo_idx < phase_idx


def test_render_define_requires_firm_prefix():
    gen = importlib.import_module('FIRM_constants.generate_header')
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    res = deriv.DerivationResult(proof_id='THM-X', value=1.23)
    try:
        gen.render_define('NOT_FIRM_NAME', res)
        raised = False
    except ValueError:
        raised = True
    assert raised is True


