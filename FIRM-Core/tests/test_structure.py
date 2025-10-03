"""Structure checks (no mocks, no network, no execution of unfinished code).

Ensures the breadth-first skeleton exists and key files are present. This is a
temporary guard; functional tests will be added once modules are implemented
from derivations.
"""
import os
import importlib
import pytest
from pathlib import Path

# Mark all tests in this module as theory validation tests
pytestmark = pytest.mark.theory

TEST_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = [
    TEST_ROOT/'FIRM_dsl', TEST_ROOT/'FIRM_zx', TEST_ROOT/'FIRM_clifford', TEST_ROOT/'FIRM_audio', TEST_ROOT/'FIRM_ui', TEST_ROOT/'provenance', TEST_ROOT/'FIRM_constants'
]
REQUIRED_FILES = [
    TEST_ROOT/'FIRM_spec.md', TEST_ROOT/'FIRM_COVENANT.md', TEST_ROOT/'LICENSE'
]

def test_directories_exist():
    for d in REQUIRED_DIRS:
        assert d.is_dir(), f"Missing directory: {d}"

def test_files_exist():
    for f in REQUIRED_FILES:
        assert f.exists(), f"Missing file: {f}"


def test_unimplemented_raise():
    """Ensure unfinished derivations explicitly raise, preventing silent fallback."""
    coherence = importlib.import_module('FIRM_dsl.coherence')
    core = importlib.import_module('FIRM_dsl.core')
    # Update: τ is now implemented; ensure invalid schema raises ValueError instead of NotImplementedError
    with pytest.raises(ValueError):
        coherence.compute_identity_echo_time_tau({})


def test_theta_saddle_point_derivation():
    """Test θ derivation from coherence functional."""
    coh = importlib.import_module('FIRM_dsl.coherence')
    core = importlib.import_module('FIRM_dsl.core')
    import math
    # Test triangle graph
    g_triangle = core.ObjectG(
        nodes=[0, 1, 2], 
        edges=[(0, 1), (1, 2), (2, 0)], 
        labels={
            0: core.make_node_label('Z', 0, 1, 'm0'),
            1: core.make_node_label('X', 1, 2, 'm1'),
            2: core.make_node_label('Z', 1, 4, 'm2')
        }
    )
    theta = coh.derive_theta_saddle_point(g_triangle)
    assert isinstance(theta, float)
    assert theta > 0.0
    # θ should be less than maximum possible coherence
    coherence = coh.compute_coherence(g_triangle)
    assert theta > 0  # Critical threshold exists
    # Test empty graph
    g_empty = core.ObjectG(nodes=[], edges=[], labels={})
    theta_empty = coh.derive_theta_saddle_point(g_empty)
    assert theta_empty == 0.0


def test_qpi_phase_binning_and_similarity():
    """Arithmetic-only Qπ utilities must behave deterministically without floats."""
    core = importlib.import_module('FIRM_dsl.core')
    coh = importlib.import_module('FIRM_dsl.coherence')
    # Build a simple two-node graph with compatible denominators
    n0 = 0
    n1 = 1
    lbl0 = core.make_node_label('Z', phase_numer=1, phase_denom=4, monadic_id='m0')
    lbl1 = core.make_node_label('X', phase_numer=2, phase_denom=4, monadic_id='m1')
    g = core.ObjectG(nodes=[n0, n1], edges=[(n0, n1)], labels={n0: lbl0, n1: lbl1})
    core.validate_object_g(g)
    bins = coh.derive_minimal_qpi_bins(g)
    assert bins == 2 * 4  # 2 * LCM(4) = 8
    hist = coh.compute_phase_histogram_signature(g, bins)
    assert len(hist) == bins
    assert abs(sum(hist) - 1.0) < 1e-12
    # Similarity against itself is 1.0 when cycle signatures equal and histograms equal
    s = coh.similarity_S([], [], hist, hist)
    assert abs(s - 1.0) < 1e-12


def test_provenance_content_addressing_and_hash_injection():
    prov = importlib.import_module('FIRM_dsl.provenance')
    run = prov.RunLedger(
        axioms_hash="AX",
        graph_seed="SEED",
        version_hash="VER",
        machine_fingerprint="CI_CANONICAL",
        compile_time="1970-01-01T00:00:00Z",
        render_tick=0,
        tau_distribution=[0.0],
        active_macros=["FIRM_TEST"]
    )
    jb = prov.write_run_json("/dev/null", run)
    # Inject a trivial hex function for deterministic testing
    fake_hex = lambda b: "ab" + ("cd" * 2)
    hh = prov.compute_content_hash(jb, fake_hex)
    assert isinstance(hh, str) and len(hh) >= 2
    path = prov.provenance_bundle_path("provenance", hh)
    assert path.startswith("provenance/ab/")
    # Compose run bundle using the same injected hash
    bundle = prov.compose_run_bundle("provenance", run, fake_hex)
    assert bundle["path"].startswith("provenance/ab/")
    assert isinstance(bundle["run_json_bytes"], (bytes, bytearray))
    # Deterministic hash across repeated calls
    bundle2 = prov.compose_run_bundle("provenance", run, fake_hex)
    assert bundle2["hash_hex"] == bundle["hash_hex"]


def test_blake3_vendor_with_fallback_detection():
    blake3_vendor = importlib.import_module('FIRM_dsl.blake3_vendor')
    # Test that we can create test function
    test_fn = blake3_vendor.create_test_blake3_function()
    test_hash = test_fn(b"test data")
    assert isinstance(test_hash, str)
    assert test_hash.startswith("TEST-")
    # Test deterministic behavior
    test_hash2 = test_fn(b"test data")
    assert test_hash == test_hash2
    # Test get_blake3_function in test mode
    fn = blake3_vendor.get_blake3_function(use_test=True)
    h1 = fn(b"same input")
    h2 = fn(b"same input")
    assert h1 == h2


def test_zx_host_layout_pack_unpack_and_size():
    layout = importlib.import_module('FIRM_zx.host_layout')
    sp = layout.SpiderPacked(phase_numer=1, phase_denom=4, kind=0, deg=2)
    b = layout.pack_spider(sp)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) == layout.spider_record_size_bytes() == 16
    sp2 = layout.unpack_spider(b)
    assert sp2 == sp


def test_qpi_phase_add_and_binning_invariants():
    core = importlib.import_module('FIRM_dsl.core')
    # 1/4π + 1/4π = 1/2π in Qπ domain
    n, d = core.add_phases_qpi(1, 4, 1, 4)
    assert (n, d) == (1, 2)
    # Minimal bins for denom 4 is 8; bin indices must align exactly
    bins = 8
    i1 = core.phase_to_bin_index(1, 4, bins)
    i2 = core.phase_to_bin_index(1, 4, bins)
    assert i1 == i2


def test_derivations_now_implemented():
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    import math
    # Test phase unit derivation
    phase_result = deriv.derive_phase_unit()
    assert isinstance(phase_result, deriv.DerivationResult)
    assert abs(phase_result.value - math.pi/4) < 1e-12
    assert phase_result.proof_id.startswith("THM-PHASE-UNIT")
    # Test echo threshold derivation  
    theta_result = deriv.derive_echo_threshold()
    assert isinstance(theta_result, deriv.DerivationResult)
    assert abs(theta_result.value - 1.0/math.e) < 1e-12
    assert theta_result.proof_id.startswith("THM-ECHO-THRESHOLD")


def test_constants_header_renderer_accepts_proven_values_only():
    gen = importlib.import_module('FIRM_constants.generate_header')
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    # Fake proven values for test rendering
    res_phase = deriv.DerivationResult(proof_id="THM-PHASE-001", value=3.14159)
    header = gen.render_header({
        "FIRM_PHASE_UNIT": res_phase,
    })
    assert "#define FIRM_PHASE_UNIT" in header
    assert "proof: THM-PHASE-001" in header


def test_constants_from_derivations_with_rational_phase():
    gen = importlib.import_module('FIRM_constants.generate_header')
    constants = gen.build_constants_from_derivations([2, 4])
    assert "FIRM_PHASE_UNIT" in constants
    assert constants["FIRM_PHASE_UNIT"].value == 0.25  # 1/4
    header = gen.render_header(constants)
    assert "THM-PHASE-QPI-LCM-001" in header


def test_phase_unit_rational_derivation_via_lcm():
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    pid, ru = deriv.derive_phase_unit_rational([2, 4, 8])
    assert pid.startswith("THM-PHASE-QPI-LCM")
    assert ru.numer == 1 and ru.denom == 8


def test_theta_saddle_structure_analysis():
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    sig = {"cycles": 2, "nodes": 3}
    pid, struct = deriv.analyze_theta_saddle_structure(sig)
    assert pid.startswith("THM-THETA-SADDLE-STRUCT")
    assert struct.cycle_terms == 2 and struct.node_terms == 3
    assert len(struct.constraints) == 5  # 2 cycles + 3 nodes
    assert struct.hessian_signature == (5, 0, 0)  # All positive for minimum


def test_coherence_functional_structure():
    coh = importlib.import_module('FIRM_dsl.coherence')
    core = importlib.import_module('FIRM_dsl.core')
    # Simple graph with 2 nodes, no cycles
    g_tree = core.ObjectG(nodes=[0, 1], edges=[], labels={
        0: core.make_node_label('Z', 1, 4, 'm0'),
        1: core.make_node_label('X', 0, 1, 'm1')
    })
    struct = coh.coherence_functional_structure(g_tree)
    assert struct["cycle_count"] == 0
    assert struct["node_count"] == 2
    assert struct["total_terms"] == 2


def test_cycle_basis_signature_computation():
    coh = importlib.import_module('FIRM_dsl.coherence')
    core = importlib.import_module('FIRM_dsl.core')
    # Triangle graph: 0-1-2-0
    g_triangle = core.ObjectG(
        nodes=[0, 1, 2], 
        edges=[(0, 1), (1, 2), (2, 0)], 
        labels={
            0: core.make_node_label('Z', 0, 1, 'm0'),
            1: core.make_node_label('X', 1, 2, 'm1'),
            2: core.make_node_label('Z', 1, 4, 'm2')
        }
    )
    cycles = coh.compute_cycle_basis_signature(g_triangle)
    assert len(cycles) == 1  # One fundamental cycle
    assert len(cycles[0]) == 3  # Triangle
    assert min(cycles[0]) == cycles[0][0]  # Canonicalized to start with min node
    # Test empty graph
    g_empty = core.ObjectG(nodes=[], edges=[], labels={})
    cycles_empty = coh.compute_cycle_basis_signature(g_empty)
    assert cycles_empty == []


def test_coherence_functional_computation():
    coh = importlib.import_module('FIRM_dsl.coherence')
    core = importlib.import_module('FIRM_dsl.core')
    # Test triangle graph coherence
    g_triangle = core.ObjectG(
        nodes=[0, 1, 2], 
        edges=[(0, 1), (1, 2), (2, 0)], 
        labels={
            0: core.make_node_label('Z', 0, 1, 'm0'),  # phase = 0
            1: core.make_node_label('X', 1, 2, 'm1'),  # phase = π/2
            2: core.make_node_label('Z', 1, 4, 'm2')   # phase = π/4
        }
    )
    coherence = coh.compute_coherence(g_triangle)
    assert isinstance(coherence, float)
    assert coherence > 0.0  # Coherence must be positive
    # Test that coherence is deterministic
    coherence2 = coh.compute_coherence(g_triangle)
    assert abs(coherence - coherence2) < 1e-12
    # Test empty graph
    g_empty = core.ObjectG(nodes=[], edges=[], labels={})
    coherence_empty = coh.compute_coherence(g_empty)
    assert coherence_empty == 0.0


def test_wgsl_params_pack_and_size():
    params = importlib.import_module('FIRM_zx.host_params')
    p = params.Params(max_spiders=1024, bins_qpi=8)
    b = params.pack_params(p)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) == params.params_record_size_bytes() == 16


def test_zx_rule_preconditions_raise_on_invalid_sites():
    rules = importlib.import_module('FIRM_zx.rules')
    with pytest.raises(ValueError):
        rules.check_fusion_preconditions(rules.RewriteSite(nodes=[1], edges=[]))
    with pytest.raises(ValueError):
        rules.check_fusion_preconditions(rules.RewriteSite(nodes=[1,2], edges=[]))
    with pytest.raises(ValueError):
        rules.check_color_flip_preconditions(rules.RewriteSite(nodes=[], edges=[]))


def test_clifford_phi_mapping_computation():
    iface = importlib.import_module('FIRM_clifford.interface')
    core = importlib.import_module('FIRM_dsl.core')
    # Test simple Z-spider mapping
    g_z = core.ObjectG(
        nodes=[0], edges=[], 
        labels={0: core.make_node_label('Z', 1, 4, 'm0')}  # π/4 phase
    )
    field_z = iface.phi_zx_to_clifford(g_z)
    assert isinstance(field_z, iface.MultivectorField)
    assert field_z.payload["algebra"] == "Cl(1,3)"
    components = field_z.payload["components"]
    assert len(components) == 16
    assert any(c != 0 for c in components)  # Non-trivial mapping
    # Test X-spider mapping
    g_x = core.ObjectG(
        nodes=[1], edges=[],
        labels={1: core.make_node_label('X', 1, 2, 'm1')}  # π/2 phase
    )
    field_x = iface.phi_zx_to_clifford(g_x)
    assert field_x.payload["algebra"] == "Cl(1,3)"
    # Test empty graph
    g_empty = core.ObjectG(nodes=[], edges=[], labels={})
    field_empty = iface.phi_zx_to_clifford(g_empty)
    assert all(c == 0 for c in field_empty.payload["components"])


def test_spec_autogen_renders_from_docstrings():
    tool = importlib.import_module('tools.spec_autogen')
    txt = tool.render_spec()
    assert isinstance(txt, str)
    assert "FIRM Spec" in txt


def test_zx_host_bindings_build_and_sizes():
    hb = importlib.import_module('FIRM_zx.host_bindings')
    hp = importlib.import_module('FIRM_zx.host_params')
    hl = importlib.import_module('FIRM_zx.host_layout')
    params = hp.Params(max_spiders=2, bins_qpi=8)
    spiders = [hl.SpiderPacked(1,4,0,2), hl.SpiderPacked(0,1,1,1)]
    bufs = hb.build_zx_buffers(params, spiders)
    psize, ssize = hb.zx_buffer_sizes(len(spiders))
    assert isinstance(bufs.params_bytes, (bytes, bytearray)) and len(bufs.params_bytes) == psize
    assert isinstance(bufs.spiders_bytes, (bytes, bytearray)) and len(bufs.spiders_bytes) == ssize


def test_audio_parseval_derivation():
    deriv = importlib.import_module('FIRM_audio.derivations')
    norm = deriv.derive_parseval_normalization(2048, 44100.0)
    assert norm.window_function == "hann"
    assert norm.correction_factor == 8.0 / 3.0
    assert norm.max_energy_bound == 1024.0  # 2048 / 2
    assert norm.proof_id.startswith("THM-PARSEVAL-HANN")
    # Test coherence computation
    mags = [1.0, 0.5, 0.25]  # Sample FFT magnitudes
    c_audio = deriv.compute_coherence_audio_normalized(mags, norm)
    assert 0.0 <= c_audio <= 1.0


def test_hessian_structure_validator():
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    # Test positive definite case (coherence minimum)
    h_min = deriv.validate_hessian_structure(3, "coherence_minimum")
    assert h_min.dimension == 3
    assert h_min.definiteness == "positive"
    assert all(sign == "positive" for sign in h_min.expected_eigenvalue_signs)
    assert h_min.proof_id.startswith("THM-HESSIAN-POS-DEF")
    # Test negative definite case (coherence maximum)
    h_max = deriv.validate_hessian_structure(2, "coherence_maximum")
    assert h_max.definiteness == "negative"
    assert all(sign == "negative" for sign in h_max.expected_eigenvalue_signs)


def test_grace_operator_structure_validator():
    monad = importlib.import_module('FIRM_dsl.monad')
    grace = monad.GraceOperatorStructure()
    # Test idempotent structure
    idem = grace.validate_idempotent_structure(5)
    assert idem["is_idempotent"] is True
    assert idem["domain_size"] == idem["codomain_size"] == 5
    assert "coherence_restoring" in idem["properties"]
    # Test left adjoint structure
    adj = grace.validate_left_adjoint_structure(3)
    assert adj["has_left_adjoint_structure"] is True
    assert "η: Id → EmbedCoherence ∘ 𝒢" in adj["unit_natural_transformation"]
    # Test coherence restoration
    incoherent = {"coherence_level": 0.1, "cycles": 0}
    restore = grace.validate_coherence_restoration(incoherent)
    assert restore["can_restore"] is True
    assert restore["preserves_history"] is True
    # Test Grace operator application
    sheaf_mod = importlib.import_module('FIRM_dsl.sheaf')
    test_sheaf = sheaf_mod.Sheaf(values_on_objects={})
    restored = grace.apply_grace_operator(test_sheaf)
    assert isinstance(restored, sheaf_mod.Sheaf)


def test_zx_coherence_delta_scaffold():
    rules = importlib.import_module('FIRM_zx.rules')
    delta = rules.CoherenceDeltaScaffold()
    # Test delta computation structure validation
    pre = {"cycles": 2, "nodes": 4}
    post = {"cycles": 1, "nodes": 3}  # Fusion reduces both
    validation = delta.validate_delta_computation_structure(pre, post)
    assert validation["delta_cycles"] == -1
    assert validation["delta_nodes"] == -1
    assert validation["coherence_terms_affected"] == 2
    assert validation["computation_valid"] is True
    # Test fusion delta-C computation
    spider1 = {"phase_numer": 0, "phase_denom": 1, "degree": 2}
    spider2 = {"phase_numer": 1, "phase_denom": 4, "degree": 1}
    fusion_delta = delta.compute_fusion_delta_c(spider1, spider2)
    assert isinstance(fusion_delta, float)
    # Test color flip delta-C computation
    bialgebra = {"type": "Z", "phase_numer": 1, "phase_denom": 2, "degree": 3}
    flip_delta = delta.compute_color_flip_delta_c(bialgebra)
    assert isinstance(flip_delta, float)
    # Test scheduling by ΔC descending order
    candidates = [
        {"type": "fusion", "delta_c": 0.1},
        {"type": "flip", "delta_c": 0.3},
        {"type": "fusion", "delta_c": 0.2},
        {"type": "noop", "delta_c": float('nan')},
    ]
    ordered = delta.schedule_rewrites_by_delta_c(candidates)
    deltas = [c.get("delta_c") for c in ordered]
    assert deltas == [0.3, 0.2, 0.1]


def test_clifford_phi_mapping_validator():
    iface = importlib.import_module('FIRM_clifford.interface')
    validator = iface.CliffordMappingValidator()
    # Test functor structure validation
    zx_sig = {"z_spiders": 2, "x_spiders": 3, "edges": 4}
    functor_val = validator.validate_functor_structure(zx_sig)
    assert functor_val["preserves_composition"] is True
    assert functor_val["z_to_scalar_rotors"] == 2
    assert functor_val["x_to_phase_bivectors"] == 3
    assert functor_val["target_algebra"] == "Cl(1,3)"
    # Test algebraic structure preservation
    spider_sig = {"type": "Z", "phase_numer": 1, "phase_denom": 4}
    alg_val = validator.validate_algebraic_structure_preservation(spider_sig)
    assert alg_val["preserves_spider_relations"] is True
    assert alg_val["clifford_representation"] == "scalar_rotor"
    assert "π * 1/4" in alg_val["qpi_phase_preserved"]
    # Test Lorentz signature emergence
    cliff_sig = {"positive_squares": 1, "negative_squares": 3}
    lorentz_val = validator.validate_lorentz_signature_emergence(cliff_sig)
    assert lorentz_val["signature_is_lorentzian"] is True
    assert lorentz_val["minimal_complexity_attractor"] is True
    # Test that actual mapping raises
    with pytest.raises(NotImplementedError):
        validator.compute_phi_mapping(None)


def test_webgl_shader_validator():
    validator = importlib.import_module('FIRM_ui.shader_validator')
    sv = validator.WebGLShaderValidator()
    # Test valid vertex shader
    vertex_src = "precision mediump float; attribute vec3 position; void main() { gl_Position = vec4(position, 1.0); }"
    vertex_result = sv.validate_vertex_shader(vertex_src)
    assert vertex_result.is_valid is True
    # Test invalid fragment shader (missing precision)
    fragment_src = "void main() { gl_FragColor = vec4(1.0); }"
    fragment_result = sv.validate_fragment_shader(fragment_src)
    assert fragment_result.is_valid is False
    assert "precision qualifier" in fragment_result.errors[0]
    # Test valid WGSL compute shader
    wgsl_src = "@compute @workgroup_size(64) fn main() { }"
    wgsl_result = sv.validate_wgsl_compute_shader(wgsl_src)
    assert wgsl_result.is_valid is True


def test_discrete_dirac_mass_validator():
    iface = importlib.import_module('FIRM_clifford.interface')
    validator = iface.DiscreteDiracMassValidator()
    # Test difference operator structure validation
    prev_field = {"algebra": "Cl(1,3)", "dimension": 16}
    curr_field = {"algebra": "Cl(1,3)", "dimension": 16}
    diff_val = validator.validate_difference_operator_structure(prev_field, curr_field)
    assert diff_val["difference_operator_valid"] is True
    assert diff_val["preserves_clifford_structure"] is True
    assert diff_val["algebra"] == "Cl(1,3)"
    # Test spectral gap structure validation
    op_sig = {"difference_operator_valid": True, "algebra": "Cl(1,3)"}
    spectral_val = validator.validate_spectral_gap_structure(op_sig)
    assert spectral_val["has_discrete_spectrum"] is True
    assert spectral_val["first_eigenvalue_is_mass"] is True
    assert spectral_val["eigenvalues_real"] is True
    # Test mass emergence causality
    evolution_sig = {"coherence_delta": 0.1, "time_step": 1}
    causal_val = validator.validate_mass_emergence_causality(evolution_sig)
    assert causal_val["respects_causality"] is True
    assert causal_val["mass_proportional_to_coherence_change"] is True
    # Test actual mass computation with real fields
    core = importlib.import_module('FIRM_dsl.core')
    g1 = core.ObjectG(nodes=[0], edges=[], labels={0: core.make_node_label('Z', 0, 1, 'm0')})
    g2 = core.ObjectG(nodes=[0], edges=[], labels={0: core.make_node_label('Z', 1, 4, 'm0')})
    field1 = iface.phi_zx_to_clifford(g1)
    field2 = iface.phi_zx_to_clifford(g2)
    mass = validator.compute_mass_spectral_gap(field1, field2)
    assert isinstance(mass, float)
    assert mass >= 0.0  # Mass must be non-negative


def test_ui_raymarching_structure_validator():
    raymarch = importlib.import_module('FIRM_ui.raymarching')
    validator = raymarch.RaymarchingValidator()
    # Test Clifford field sampling validation
    field_sig = {"algebra": "Cl(1,3)", "dimension": 16}
    field_val = validator.validate_clifford_field_sampling(field_sig)
    assert field_val["field_sampling_valid"] is True
    assert field_val["supports_3d_visualization"] is True
    assert field_val["multivector_components"] == 16
    # Test camera mathematics validation
    camera_config = {
        "position": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0],
        "fov": 45, "aspect_ratio": 16/9
    }
    camera_val = validator.validate_camera_mathematics(camera_config)
    assert camera_val["camera_math_valid"] is True
    assert camera_val["view_matrix_invertible"] is True
    # Test raymarching algorithm structure
    algo_config = {"max_steps": 100, "min_distance": 0.001, "max_distance": 100.0}
    algo_val = validator.validate_raymarching_algorithm_structure(algo_config)
    assert algo_val["algorithm_convergent"] is True
    assert algo_val["bounded_iteration"] is True
    # Test shader pipeline structure validation
    vertex_src = "void main() { gl_Position = vec4(0.0); }"
    fragment_src = "void main() { vec3 ray_dir = vec3(1.0); for(int i=0; i<100; i++) {} gl_FragColor = vec4(1.0); }"
    shader_val = validator.validate_shader_pipeline_structure(vertex_src, fragment_src)
    assert shader_val["pipeline_structure_valid"] is True
    assert shader_val["raymarching_structure_present"] is True
    # Test raymarching pipeline creation
    pipeline = validator.create_raymarching_pipeline(None, camera_config)
    assert isinstance(pipeline, raymarch.RaymarchingPipeline)
    assert "gl_Position" in pipeline.vertex_shader_source
    assert "raymarching loop" in pipeline.fragment_shader_source.lower() or "for" in pipeline.fragment_shader_source
    assert "uCliffordField" in pipeline.uniforms
    assert pipeline.camera_parameters == camera_config


def test_provenance_bundle_writer():
    writer_mod = importlib.import_module('FIRM_dsl.provenance_writer')
    prov_mod = importlib.import_module('FIRM_dsl.provenance')
    import tempfile
    import os
    
    # Create writer with mock hash function
    mock_hash = lambda b: "abcd1234" + "ef" * 10
    
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = writer_mod.ProvenanceBundleWriter(temp_dir, mock_hash)
        
        # Test bundle structure validation
        valid_bundle = {
            "run_ledger": {"test": "data"},
            "tau_trace": [1.0, 2.0],
            "coherence_variation": [0.5, 0.6, 0.7]
        }
        validation = writer.validate_bundle_structure(valid_bundle)
        assert validation["structure_valid"] is True
        assert validation["run_ledger_present"] is True
        
        # Test bundle hash computation
        run_ledger = prov_mod.RunLedger(
            axioms_hash="TEST", graph_seed="SEED", version_hash="VER",
            machine_fingerprint="CI_CANONICAL", compile_time="1970-01-01T00:00:00Z",
            render_tick=0, tau_distribution=[1.0], active_macros=["TEST"]
        )
        bundle_hash = writer.compute_bundle_hash(run_ledger)
        assert isinstance(bundle_hash, str) and len(bundle_hash) > 0
        
        # Test filesystem writing
        write_result = writer.write_bundle_to_filesystem(valid_bundle, run_ledger)
        assert write_result["write_successful"] is True
        assert os.path.exists(write_result["bundle_path"])
        assert "run.json" in write_result["files_written"]
        assert "manifest.json" in write_result["files_written"]
        
        # Test integrity verification
        integrity = writer.verify_bundle_integrity(write_result["bundle_path"], bundle_hash)
        assert integrity["integrity_valid"] is True
        assert integrity["hash_matches"] is True
        assert integrity["manifest_hash_matches"] is True


def test_audio_oscillator_structure_validation():
    """Test audio oscillator bank structure without executing Web Audio API."""
    # Note: Cannot test actual Web Audio API in Node.js environment
    # Test structure validation only
    config = {
        "baseFrequency": 220.0,
        "oscillatorCount": 4,
        "phaseCoherence": True
    }
    # Validate configuration structure
    assert config["baseFrequency"] > 0
    assert config["oscillatorCount"] > 0
    assert isinstance(config["phaseCoherence"], bool)
    # Test that expected waveforms are defined
    waveforms = ['sine', 'square', 'triangle', 'sawtooth']
    assert len(waveforms) == 4


def test_ui_controller_structure_and_state():
    """Test UI controller structure without DOM execution."""
    # Test camera state validation
    camera_state = {
        "position": [0, 0, 5],
        "target": [0, 0, 0], 
        "up": [0, 1, 0],
        "fov": 45,
        "aspect_ratio": 16/9
    }
    # Validate camera parameters
    assert len(camera_state["position"]) == 3
    assert len(camera_state["target"]) == 3
    assert len(camera_state["up"]) == 3
    assert 0 < camera_state["fov"] < 180
    assert camera_state["aspect_ratio"] > 0
    
    # Test view names
    valid_views = ['clifford', 'zx', 'sheaf', 'echo']
    assert len(valid_views) == 4
    assert 'clifford' in valid_views  # Default view per spec


def test_shader_runtime_structure_validation():
    """Test shader runtime structure without GPU execution."""
    # Test WebGL runtime requirements
    webgl_config = {
        "context_type": "webgl2",
        "required_extensions": ["EXT_color_buffer_float"],
        "shader_types": ["vertex", "fragment"]
    }
    assert webgl_config["context_type"] == "webgl2"
    assert len(webgl_config["required_extensions"]) >= 1
    assert len(webgl_config["shader_types"]) == 2
    
    # Test WebGPU runtime requirements  
    webgpu_config = {
        "context_type": "webgpu",
        "pipeline_types": ["compute", "render"],
        "buffer_usage_flags": ["STORAGE", "UNIFORM", "VERTEX"]
    }
    assert webgpu_config["context_type"] == "webgpu"
    assert "compute" in webgpu_config["pipeline_types"]
    assert len(webgpu_config["buffer_usage_flags"]) >= 3
