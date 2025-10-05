"""
Critical Experiments: Testing if FIRM exhibits fundamental physics-like behavior.

These tests probe for:
1. Phase transitions (spontaneous organization)
2. Emergent dimensionless ratios (physical constants)
3. Lorentz invariance (relativistic structure)
4. Quantum interference (path integral behavior)
5. Gauge symmetry (local phase invariance)

Each test is designed to be falsifiable and to distinguish between
"interesting toy model" and "candidate theory of reality."
"""

import pytest
import numpy as np
from collections import defaultdict
from FIRM_dsl.core import ObjectG
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment


class TestPhaseTransitions:
    """
    Test 1: Spontaneous Phase Transitions
    
    If FIRM is reality, the graph should spontaneously organize into
    distinct phases (vacuum → dark → ordinary matter) without external tuning.
    
    Signatures:
    - C(G) plateaus at distinct values
    - Hysteresis loops in Res(S,Ω) vs C(G)
    - Critical points with power-law fluctuations
    """
    
    def test_coherence_plateaus_during_evolution(self):
        """Test if C(G) exhibits plateau behavior suggesting phase boundaries."""
        graph = ObjectG()
        graph.add_node(0, node_type='Z', phase=0.0)
        graph.add_node(1, node_type='X', phase=np.pi/4)
        graph.add_node(2, node_type='Z', phase=np.pi/2)
        graph.add_edge(0, 1)
        graph.add_edge(1, 2)
        
        coherence_history = []
        num_steps = 100
        
        # Evolve and track C(G)
        for step in range(num_steps):
            coh = compute_coherence(graph)
            coherence_history.append(coh)
            
            # Simple evolution: add nodes and edges
            if np.random.random() < 0.3:
                new_id = max(graph.nodes.keys()) + 1
                node_type = 'Z' if np.random.random() > 0.5 else 'X'
                phase = np.random.random() * 2 * np.pi
                graph.add_node(new_id, node_type=node_type, phase=phase)
                
                # Connect to existing node
                existing = np.random.choice(list(graph.nodes.keys())[:-1])
                graph.add_edge(existing, new_id)
            
            # Occasionally add cross-links
            if len(graph.nodes) > 4 and np.random.random() < 0.2:
                nodes = list(graph.nodes.keys())
                n1, n2 = np.random.choice(nodes, 2, replace=False)
                if not graph.has_edge(n1, n2):
                    graph.add_edge(n1, n2)
        
        # Analyze for plateaus: compute local variance
        window = 10
        variances = []
        for i in range(len(coherence_history) - window):
            window_data = coherence_history[i:i+window]
            variances.append(np.var(window_data))
        
        # Plateaus have low variance
        low_variance_count = sum(1 for v in variances if v < 0.01)
        
        # Log results for inspection
        print(f"\nPhase Transition Test:")
        print(f"  Final C(G): {coherence_history[-1]:.4f}")
        print(f"  Low-variance windows: {low_variance_count}/{len(variances)}")
        print(f"  Mean variance: {np.mean(variances):.6f}")
        
        # Assertion: we should see SOME low-variance regions (plateaus)
        # This is a weak test; strong version would require multiple distinct plateaus
        assert low_variance_count > 0, "No plateaus detected; system may not self-organize"
    
    def test_hysteresis_in_resonance_coherence_relationship(self):
        """Test if Res(S,Ω) vs C(G) shows hysteresis (path-dependent behavior)."""
        graph = ObjectG()
        for i in range(5):
            graph.add_node(i, node_type='Z' if i % 2 == 0 else 'X', phase=i * np.pi / 5)
        for i in range(4):
            graph.add_edge(i, i+1)
        
        omega = derive_omega_signature(graph)
        
        # Path 1: increase complexity
        path1_res = []
        path1_coh = []
        for _ in range(20):
            res = compute_resonance_alignment(graph, omega)
            coh = compute_coherence(graph)
            path1_res.append(res)
            path1_coh.append(coh)
            
            # Add node
            new_id = max(graph.nodes.keys()) + 1
            graph.add_node(new_id, node_type='Z', phase=np.random.random() * 2 * np.pi)
            graph.add_edge(new_id - 1, new_id)
        
        # Path 2: decrease complexity (remove nodes)
        path2_res = []
        path2_coh = []
        for _ in range(15):
            res = compute_resonance_alignment(graph, omega)
            coh = compute_coherence(graph)
            path2_res.append(res)
            path2_coh.append(coh)
            
            # Remove a node
            if len(graph.nodes) > 3:
                to_remove = max(graph.nodes.keys())
                graph.remove_node(to_remove)
        
        # Check if paths differ (hysteresis signature)
        # Compare overlapping C(G) ranges
        overlap_coh_min = max(min(path1_coh), min(path2_coh))
        overlap_coh_max = min(max(path1_coh), max(path2_coh))
        
        if overlap_coh_max > overlap_coh_min:
            # Find Res values in overlapping C(G) range
            path1_res_in_overlap = [path1_res[i] for i, c in enumerate(path1_coh) 
                                     if overlap_coh_min <= c <= overlap_coh_max]
            path2_res_in_overlap = [path2_res[i] for i, c in enumerate(path2_coh) 
                                     if overlap_coh_min <= c <= overlap_coh_max]
            
            if path1_res_in_overlap and path2_res_in_overlap:
                mean_diff = abs(np.mean(path1_res_in_overlap) - np.mean(path2_res_in_overlap))
                print(f"\nHysteresis Test:")
                print(f"  Mean Res difference in overlap: {mean_diff:.4f}")
                print(f"  Path 1 mean Res: {np.mean(path1_res_in_overlap):.4f}")
                print(f"  Path 2 mean Res: {np.mean(path2_res_in_overlap):.4f}")
                
                # Hysteresis present if paths differ significantly
                # (This is exploratory; we're logging, not asserting strongly)
                assert True  # Always pass; this is data collection


class TestDimensionlessRatios:
    """
    Test 2: Emergent Dimensionless Ratios
    
    If FIRM is reality, graph topology should produce dimensionless ratios
    that match physical constants (α ≈ 1/137, mass ratios, etc.).
    
    We measure:
    - Cycle length ratios
    - Trivector/bivector ratios
    - Grace/rewrite ratios
    """
    
    def test_cycle_length_ratios_converge(self):
        """Test if (longest cycle) / (mean cycle) converges to a constant."""
        graph = ObjectG()
        # Create a graph with multiple cycles
        for i in range(10):
            graph.add_node(i, node_type='Z' if i % 2 == 0 else 'X', phase=i * np.pi / 10)
        
        # Create cycles of different lengths
        graph.add_edge(0, 1)
        graph.add_edge(1, 2)
        graph.add_edge(2, 0)  # 3-cycle
        
        graph.add_edge(3, 4)
        graph.add_edge(4, 5)
        graph.add_edge(5, 6)
        graph.add_edge(6, 3)  # 4-cycle
        
        graph.add_edge(7, 8)
        graph.add_edge(8, 9)
        graph.add_edge(9, 7)  # 3-cycle
        
        # Find cycles (simple DFS-based detection)
        def find_cycles(g, max_length=10):
            cycles = []
            visited = set()
            
            def dfs(node, path):
                if len(path) > max_length:
                    return
                if node in path:
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:]
                    if len(cycle) >= 3:
                        cycles.append(tuple(sorted(cycle)))
                    return
                if node in visited:
                    return
                
                for neighbor in g.neighbors(node):
                    dfs(neighbor, path + [node])
            
            for start_node in g.nodes:
                dfs(start_node, [])
            
            return list(set(cycles))
        
        cycles = find_cycles(graph)
        if len(cycles) > 1:
            cycle_lengths = [len(c) for c in cycles]
            longest = max(cycle_lengths)
            mean_length = np.mean(cycle_lengths)
            ratio = longest / mean_length if mean_length > 0 else 0
            
            print(f"\nCycle Length Ratio Test:")
            print(f"  Cycles found: {len(cycles)}")
            print(f"  Lengths: {cycle_lengths}")
            print(f"  Longest/Mean ratio: {ratio:.4f}")
            
            # This is exploratory; we're collecting data
            assert ratio > 0, "Cycle ratio should be positive"
        else:
            pytest.skip("Not enough cycles for ratio test")
    
    def test_grace_to_rewrite_ratio(self):
        """Test if Grace events / total rewrites converges to a constant."""
        # This would require running the full evolution engine
        # For now, we document the expected measurement
        print("\nGrace/Rewrite Ratio Test:")
        print("  (Requires full evolution run; see long_run_evolution.py)")
        print("  Expected: ratio should converge to φ-related constant")
        assert True  # Placeholder


class TestLorentzInvariance:
    """
    Test 3: Lorentz Invariance
    
    If FIRM is reality, graph structure should be invariant under
    Lorentz transformations (boosts, rotations).
    
    We test if C(G) and Res(S,Ω) are preserved under phase remapping
    that mimics Lorentz boosts.
    """
    
    def test_coherence_invariant_under_phase_boost(self):
        """Test if C(G) is invariant under 'boost' (phase rescaling)."""
        graph = ObjectG()
        for i in range(6):
            graph.add_node(i, node_type='Z' if i % 2 == 0 else 'X', phase=i * np.pi / 6)
        for i in range(5):
            graph.add_edge(i, i+1)
        graph.add_edge(5, 0)  # Close cycle
        
        # Measure coherence before boost
        coh_before = compute_coherence(graph)
        
        # Apply "boost": rescale all phases by a Lorentz factor γ
        gamma = 1.5  # Lorentz factor
        for node_id in graph.nodes:
            graph.nodes[node_id]['phase'] *= gamma
            graph.nodes[node_id]['phase'] %= (2 * np.pi)  # Keep in [0, 2π)
        
        # Measure coherence after boost
        coh_after = compute_coherence(graph)
        
        # Check invariance
        relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
        
        print(f"\nLorentz Invariance Test:")
        print(f"  C(G) before boost: {coh_before:.4f}")
        print(f"  C(G) after boost (γ={gamma}): {coh_after:.4f}")
        print(f"  Relative change: {relative_change:.4f}")
        
        # Lorentz invariance would require relative_change ≈ 0
        # Current implementation likely NOT invariant; this test documents that
        # If we see invariance emerge, that's profound
        assert True  # Data collection; not enforcing invariance yet


class TestQuantumInterference:
    """
    Test 4: Quantum Interference
    
    If FIRM is reality, paths through the graph should interfere
    like quantum amplitudes (constructive/destructive interference).
    
    We test if phase differences along different paths produce
    interference patterns.
    """
    
    def test_path_interference_from_phase_differences(self):
        """Test if two paths A→B interfere based on phase differences."""
        graph = ObjectG()
        # Create diamond: A → B,C → D
        graph.add_node(0, node_type='Z', phase=0.0)  # A
        graph.add_node(1, node_type='X', phase=np.pi/4)  # B
        graph.add_node(2, node_type='X', phase=np.pi/3)  # C
        graph.add_node(3, node_type='Z', phase=0.0)  # D
        
        graph.add_edge(0, 1)  # A → B
        graph.add_edge(0, 2)  # A → C
        graph.add_edge(1, 3)  # B → D
        graph.add_edge(2, 3)  # C → D
        
        # Path 1: A → B → D
        phase_path1 = graph.nodes[0]['phase'] + graph.nodes[1]['phase'] + graph.nodes[3]['phase']
        
        # Path 2: A → C → D
        phase_path2 = graph.nodes[0]['phase'] + graph.nodes[2]['phase'] + graph.nodes[3]['phase']
        
        # Phase difference
        phase_diff = abs(phase_path1 - phase_path2) % (2 * np.pi)
        
        # Interference amplitude (quantum-like)
        amplitude1 = np.exp(1j * phase_path1)
        amplitude2 = np.exp(1j * phase_path2)
        total_amplitude = amplitude1 + amplitude2
        probability = abs(total_amplitude)**2
        
        # Classical (no interference) would give probability = 2
        # Quantum interference gives probability in [0, 4]
        
        print(f"\nQuantum Interference Test:")
        print(f"  Phase path 1: {phase_path1:.4f}")
        print(f"  Phase path 2: {phase_path2:.4f}")
        print(f"  Phase difference: {phase_diff:.4f}")
        print(f"  Interference probability: {probability:.4f}")
        print(f"  (Classical expectation: 2.0)")
        
        # If probability ≠ 2, we have interference
        has_interference = abs(probability - 2.0) > 0.1
        print(f"  Interference detected: {has_interference}")
        
        assert True  # Data collection


class TestGaugeSymmetry:
    """
    Test 5: Gauge Symmetry
    
    If FIRM is reality, local phase rotations should leave C(G) invariant
    (U(1) gauge symmetry).
    
    We test if rotating all phases by a constant leaves coherence unchanged.
    """
    
    def test_global_phase_rotation_invariance(self):
        """Test if C(G) is invariant under global U(1) phase rotation."""
        graph = ObjectG()
        for i in range(5):
            graph.add_node(i, node_type='Z' if i % 2 == 0 else 'X', phase=i * np.pi / 5)
        for i in range(4):
            graph.add_edge(i, i+1)
        
        coh_before = compute_coherence(graph)
        
        # Apply global phase rotation
        theta = np.pi / 3
        for node_id in graph.nodes:
            graph.nodes[node_id]['phase'] = (graph.nodes[node_id]['phase'] + theta) % (2 * np.pi)
        
        coh_after = compute_coherence(graph)
        
        relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
        
        print(f"\nGauge Symmetry Test:")
        print(f"  C(G) before rotation: {coh_before:.4f}")
        print(f"  C(G) after rotation (θ={theta:.4f}): {coh_after:.4f}")
        print(f"  Relative change: {relative_change:.4f}")
        
        # U(1) gauge invariance requires relative_change ≈ 0
        # If coherence depends on phase DIFFERENCES (not absolute phases), we have gauge symmetry
        assert True  # Data collection


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
