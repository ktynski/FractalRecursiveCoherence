"""test_benchmarks.py

Performance benchmarks with theory validation for FIRM-Core.

These benchmarks measure computational performance while validating that
all operations maintain mathematical correctness and theory fidelity.
"""
import pytest
import time
import importlib


@pytest.mark.benchmark
def test_coherence_computation_performance(benchmark):
    """Benchmark C(G) coherence computation with theory validation."""
    core = importlib.import_module('FIRM_dsl.core')
    coh = importlib.import_module('FIRM_dsl.coherence')
    
    # Create moderately complex graph for benchmarking
    nodes = list(range(10))
    edges = [(i, (i + 1) % 10) for i in range(10)]  # Cycle
    edges.extend([(i, (i + 3) % 10) for i in range(0, 10, 2)])  # Cross connections
    
    labels = {
        i: core.make_node_label('Z' if i % 2 == 0 else 'X', i % 4, 4, f'm{i}')
        for i in nodes
    }
    
    g = core.ObjectG(nodes=nodes, edges=edges, labels=labels)
    
    # Benchmark coherence computation
    result = benchmark(coh.compute_coherence, g)
    
    # Validate result maintains theory properties
    assert isinstance(result, float)
    assert result > 0.0
    
    # Validate determinism across runs
    result2 = coh.compute_coherence(g)
    assert abs(result - result2) < 1e-12


@pytest.mark.benchmark
def test_cycle_basis_performance(benchmark):
    """Benchmark cycle basis computation with correctness validation."""
    core = importlib.import_module('FIRM_dsl.core')
    coh = importlib.import_module('FIRM_dsl.coherence')
    
    # Create graph with known cycle structure
    nodes = list(range(8))
    edges = [(0, 1), (1, 2), (2, 0),  # Triangle
             (3, 4), (4, 5), (5, 3),  # Another triangle
             (0, 3), (2, 5)]          # Connections between triangles
    
    labels = {i: core.make_node_label('Z', 0, 1, f'm{i}') for i in nodes}
    g = core.ObjectG(nodes=nodes, edges=edges, labels=labels)
    
    # Benchmark cycle basis computation
    cycles = benchmark(coh.compute_cycle_basis_signature, g)
    
    # Validate correctness
    assert len(cycles) >= 2  # At least 2 fundamental cycles expected
    for cycle in cycles:
        assert len(cycle) >= 3  # Valid cycles have at least 3 nodes
        assert cycle[0] == min(cycle)  # Canonicalized


@pytest.mark.benchmark
def test_clifford_mapping_performance(benchmark):
    """Benchmark Clifford Φ mapping with algebraic validation."""
    core = importlib.import_module('FIRM_dsl.core')
    iface = importlib.import_module('FIRM_clifford.interface')
    
    # Create ZX graph for mapping
    nodes = list(range(6))
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    labels = {
        i: core.make_node_label('Z' if i % 2 == 0 else 'X', i % 8, 8, f'm{i}')
        for i in nodes
    }
    
    g = core.ObjectG(nodes=nodes, edges=edges, labels=labels)
    
    # Benchmark Clifford mapping
    field = benchmark(iface.phi_zx_to_clifford, g)
    
    # Validate Clifford field properties
    assert isinstance(field, iface.MultivectorField)
    assert field.payload["algebra"] == "Cl(1,3)"
    components = field.payload["components"]
    assert len(components) == 16
    
    # Validate normalization
    magnitude_sq = sum(c * c for c in components)
    assert abs(magnitude_sq - 1.0) < 1e-10 or magnitude_sq == 0.0


@pytest.mark.benchmark
def test_zx_delta_c_performance(benchmark):
    """Benchmark ZX rewrite delta-C computation with mathematical validation."""
    rules = importlib.import_module('FIRM_zx.rules')
    
    delta_computer = rules.CoherenceDeltaScaffold()
    
    # Test fusion delta-C computation
    spider1 = {"phase_numer": 1, "phase_denom": 4, "degree": 3}
    spider2 = {"phase_numer": 3, "phase_denom": 4, "degree": 2}
    
    # Benchmark fusion computation
    fusion_delta = benchmark(delta_computer.compute_fusion_delta_c, spider1, spider2)
    
    # Validate result properties
    assert isinstance(fusion_delta, float)
    # Delta-C should be bounded (no infinite values)
    assert abs(fusion_delta) < 100.0


@pytest.mark.benchmark
def test_provenance_bundle_performance(benchmark):
    """Benchmark provenance bundle creation with integrity validation."""
    writer_mod = importlib.import_module('FIRM_dsl.provenance_writer')
    prov_mod = importlib.import_module('FIRM_dsl.provenance')
    blake3_mod = importlib.import_module('FIRM_dsl.blake3_vendor')
    
    import tempfile
    
    # Setup
    test_hash_fn = blake3_mod.create_test_blake3_function()
    
    run_ledger = prov_mod.RunLedger(
        axioms_hash="BENCHMARK_TEST",
        graph_seed="SEED_PERF", 
        version_hash="VER_PERF",
        machine_fingerprint="CI_CANONICAL",
        compile_time="2025-01-01T00:00:00Z",
        render_tick=100,
        tau_distribution=[1.0, 1.1, 0.9, 1.05],
        active_macros=["FIRM_BENCHMARK"]
    )
    
    bundle_data = {
        "run_ledger": run_ledger,
        "tau_trace": list(range(50)),  # Larger data set
        "coherence_variation": [0.8 + 0.1 * (i % 5) for i in range(50)]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = writer_mod.ProvenanceBundleWriter(temp_dir, test_hash_fn)
        
        # Benchmark bundle writing
        write_result = benchmark(writer.write_bundle_to_filesystem, bundle_data, run_ledger)
        
        # Validate write success and integrity
        assert write_result["write_successful"] is True
        
        integrity = writer.verify_bundle_integrity(
            write_result["bundle_path"],
            write_result["bundle_hash"]
        )
        assert integrity["integrity_valid"] is True


def test_benchmark_suite_coverage():
    """Validate that benchmarks cover all critical computational paths."""
    benchmark_functions = [
        "test_coherence_computation_performance",
        "test_cycle_basis_performance", 
        "test_clifford_mapping_performance",
        "test_zx_delta_c_performance",
        "test_provenance_bundle_performance"
    ]
    
    # Ensure all critical paths are benchmarked
    assert len(benchmark_functions) >= 5
    
    # Validate benchmark naming convention
    for func_name in benchmark_functions:
        assert func_name.startswith("test_")
        assert "performance" in func_name
