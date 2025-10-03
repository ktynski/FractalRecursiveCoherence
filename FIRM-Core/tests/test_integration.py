"""test_integration.py

Comprehensive integration tests for the complete FIRM pipeline.

These tests validate end-to-end functionality from mathematical foundations
through analog audio to 3D visualization, maintaining theory fidelity.
"""
import pytest
import tempfile
import importlib


@pytest.mark.integration
def test_complete_coherence_pipeline():
    """Test complete pipeline: graph → coherence → theta → constants."""
    # Import modules
    core = importlib.import_module('FIRM_dsl.core')
    coh = importlib.import_module('FIRM_dsl.coherence')
    deriv = importlib.import_module('FIRM_constants.FIRM_derivations')
    gen = importlib.import_module('FIRM_constants.generate_header')
    
    # Create test graph
    g = core.ObjectG(
        nodes=[0, 1, 2],
        edges=[(0, 1), (1, 2), (2, 0)],
        labels={
            0: core.make_node_label('Z', 0, 1, 'm0'),
            1: core.make_node_label('X', 1, 4, 'm1'), 
            2: core.make_node_label('Z', 1, 2, 'm2')
        }
    )
    
    # Test pipeline: graph → coherence → theta
    coherence = coh.compute_coherence(g)
    assert coherence > 0.0
    
    theta = coh.derive_theta_saddle_point(g)
    assert theta > 0.0
    
    # Test constants generation
    phase_unit = deriv.derive_phase_unit()
    echo_threshold = deriv.derive_echo_threshold()
    
    constants = {
        "FIRM_PHASE_UNIT": phase_unit,
        "FIRM_ECHO_THRESHOLD": echo_threshold
    }
    
    header = gen.render_header(constants)
    assert "#define FIRM_PHASE_UNIT" in header
    assert "#define FIRM_ECHO_THRESHOLD" in header
    assert "THM-PHASE-UNIT" in header
    assert "THM-ECHO-THRESHOLD" in header


@pytest.mark.integration
def test_zx_to_clifford_pipeline():
    """Test ZX → Clifford → mass pipeline."""
    # Import modules
    core = importlib.import_module('FIRM_dsl.core')
    iface = importlib.import_module('FIRM_clifford.interface')
    
    # Create two ZX graphs for evolution
    g1 = core.ObjectG(
        nodes=[0, 1], edges=[(0, 1)],
        labels={
            0: core.make_node_label('Z', 0, 1, 'm0'),
            1: core.make_node_label('X', 1, 4, 'm1')
        }
    )
    
    g2 = core.ObjectG(
        nodes=[0, 1], edges=[(0, 1)],
        labels={
            0: core.make_node_label('Z', 1, 8, 'm0'),  # Different phase
            1: core.make_node_label('X', 1, 4, 'm1')
        }
    )
    
    # Test ZX → Clifford mapping
    field1 = iface.phi_zx_to_clifford(g1)
    field2 = iface.phi_zx_to_clifford(g2)
    
    assert field1.payload["algebra"] == "Cl(1,3)"
    assert field2.payload["algebra"] == "Cl(1,3)"
    
    # Test mass computation from field evolution
    mass_validator = iface.DiscreteDiracMassValidator()
    mass = mass_validator.compute_mass_spectral_gap(field1, field2)
    
    assert isinstance(mass, float)
    assert mass >= 0.0


@pytest.mark.integration  
def test_audio_coherence_integration():
    """Test audio → coherence feedback integration."""
    # Import modules
    audio_deriv = importlib.import_module('FIRM_audio.derivations')
    
    # Test Parseval normalization derivation
    norm = audio_deriv.derive_parseval_normalization(2048, 44100.0)
    assert norm.window_function == "hann"
    assert norm.proof_id.startswith("THM-PARSEVAL")
    
    # Test coherence computation from mock FFT data
    mock_fft_magnitudes = [1.0, 0.8, 0.6, 0.4, 0.2]  # Decreasing spectrum
    c_audio = audio_deriv.compute_coherence_audio_normalized(mock_fft_magnitudes, norm)
    
    assert 0.0 <= c_audio <= 1.0
    assert isinstance(c_audio, float)


@pytest.mark.integration
def test_complete_provenance_pipeline():
    """Test complete provenance pipeline with filesystem operations."""
    # Import modules
    prov = importlib.import_module('FIRM_dsl.provenance')
    writer_mod = importlib.import_module('FIRM_dsl.provenance_writer')
    blake3_mod = importlib.import_module('FIRM_dsl.blake3_vendor')
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test hash function
        test_hash_fn = blake3_mod.create_test_blake3_function()
        writer = writer_mod.ProvenanceBundleWriter(temp_dir, test_hash_fn)
        
        # Create run ledger
        run_ledger = prov.RunLedger(
            axioms_hash="INTEGRATION_TEST",
            graph_seed="SEED_123", 
            version_hash="VER_456",
            machine_fingerprint="CI_CANONICAL",
            compile_time="2025-01-01T00:00:00Z",
            render_tick=42,
            tau_distribution=[1.0, 2.0, 1.5],
            active_macros=["FIRM_TEST", "FIRM_INTEGRATION"]
        )
        
        # Create bundle data
        bundle_data = {
            "run_ledger": run_ledger,
            "tau_trace": [1.0, 1.2, 1.1, 0.9],
            "coherence_variation": [0.8, 0.9, 0.85, 0.92]
        }
        
        # Test complete write → verify cycle
        write_result = writer.write_bundle_to_filesystem(bundle_data, run_ledger)
        assert write_result["write_successful"] is True
        
        integrity = writer.verify_bundle_integrity(
            write_result["bundle_path"], 
            write_result["bundle_hash"]
        )
        assert integrity["integrity_valid"] is True


@pytest.mark.integration
def test_ui_shader_pipeline_integration():
    """Test UI → shader → raymarching integration."""
    # Import modules
    raymarch = importlib.import_module('FIRM_ui.raymarching')
    shader_val = importlib.import_module('FIRM_ui.shader_validator')
    
    # Create validator and camera config
    validator = raymarch.RaymarchingValidator()
    camera_config = {
        "position": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0],
        "fov": 45, "aspect_ratio": 16/9
    }
    
    # Create raymarching pipeline
    pipeline = validator.create_raymarching_pipeline(None, camera_config)
    
    # Validate generated shaders
    sv = shader_val.WebGLShaderValidator()
    vertex_result = sv.validate_vertex_shader(pipeline.vertex_shader_source)
    fragment_result = sv.validate_fragment_shader(pipeline.fragment_shader_source)
    
    assert vertex_result.is_valid is True
    assert fragment_result.is_valid is True
    
    # Test shader program compatibility
    program_validation = sv.validate_shader_program_structure(
        pipeline.vertex_shader_source,
        pipeline.fragment_shader_source
    )
    assert program_validation["program_valid"] is True
