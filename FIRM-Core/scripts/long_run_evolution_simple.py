"""
Long-Run Evolution (Simplified): Extended simulation to detect emergent phenomena.

This simplified version works with the actual FIRM DSL structure.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import time
import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment
from FIRM_dsl.emergence_detection import run_emergence_battery


def initialize_graph(num_nodes=10):
    """Create initial graph with ring + cross-links."""
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]  # Ring
    
    # Add cross-links for richer structure
    for i in range(0, num_nodes, 3):
        target = (i + num_nodes // 2) % num_nodes
        if [i, target] not in edges and [target, i] not in edges:
            edges.append([i, target])
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        phase_denom = 100
        labels[i] = make_node_label(kind, phase_numer, phase_denom, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def evolve_step(graph, omega, grace_probability=0.1):
    """
    Perform one evolution step.
    
    Returns:
        event_size: Number of nodes affected
    """
    event_size = 0
    
    # Compute resonance for steering
    res = compute_resonance_alignment(graph, omega)
    
    # Grace emergence (probabilistic, resonance-modulated)
    if np.random.random() < grace_probability * res:
        new_id = len(graph.nodes)
        phi = (1 + np.sqrt(5)) / 2
        
        kind = 'Z' if np.random.random() > 0.5 else 'X'
        phase_numer = int((new_id * 100 / phi)) % 100
        phase_denom = 100
        
        new_label = make_node_label(kind, phase_numer, phase_denom, f'n{new_id}')
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        
        # Connect to existing node (prefer high-degree)
        degrees = {}
        for node in graph.nodes[:-1]:
            degree = sum(1 for u, v in graph.edges if u == node or v == node)
            degrees[node] = degree
        
        if degrees:
            total_degree = sum(degrees.values())
            if total_degree > 0:
                probs = [degrees[n] / total_degree for n in graph.nodes[:-1]]
                target = np.random.choice(graph.nodes[:-1], p=probs)
            else:
                target = np.random.choice(graph.nodes[:-1])
            
            graph.edges.append([new_id, target])
            event_size += 1
    
    # Add cross-links occasionally
    if len(graph.nodes) > 5 and np.random.random() < 0.2 * res:
        n1, n2 = np.random.choice(graph.nodes, 2, replace=False)
        if [n1, n2] not in graph.edges and [n2, n1] not in graph.edges:
            graph.edges.append([n1, n2])
            event_size += 1
    
    # Validate
    graph = validate_object_g(graph)
    
    return event_size, graph


def test_lorentz_invariance(graph, gamma=1.5):
    """
    Test if C(G) is invariant under Lorentz boost (phase rescaling).
    
    Returns:
        Dict with coherence before/after and relative change
    """
    coh_before = compute_coherence(graph)
    
    # Apply boost: rescale all phases by γ
    boosted_labels = {}
    for node_id, label in graph.labels.items():
        # Boost: multiply phase by γ
        new_numer = int((label.phase_numer * gamma)) % (2 * label.phase_denom)
        boosted_labels[node_id] = make_node_label(
            label.kind, new_numer, label.phase_denom, label.monadic_id
        )
    
    boosted_graph = ObjectG(
        nodes=graph.nodes.copy(),
        edges=graph.edges.copy(),
        labels=boosted_labels
    )
    boosted_graph = validate_object_g(boosted_graph)
    
    coh_after = compute_coherence(boosted_graph)
    relative_change = abs(coh_after - coh_before) / (coh_before + 1e-10)
    
    return {
        "coherence_before": coh_before,
        "coherence_after": coh_after,
        "relative_change": relative_change,
        "gamma": gamma,
        "is_lorentz_invariant": relative_change < 0.10  # 10% tolerance
    }


def run_long_evolution(num_steps=1000, checkpoint_interval=100, output_file="evolution_data.json"):
    """Run extended evolution and test for profound phenomena."""
    print(f"="*70)
    print(f"LONG-RUN EVOLUTION: {num_steps} steps")
    print(f"="*70)
    print(f"Checkpoint interval: {checkpoint_interval}")
    print(f"Output file: {output_file}\n")
    
    # Initialize
    graph = initialize_graph(num_nodes=10)
    omega = derive_omega_signature(graph)
    
    # Measure vacuum baseline
    vacuum_coherence = compute_coherence(graph)
    print(f"Vacuum coherence (baseline): {vacuum_coherence:.4f}\n")
    
    # Data collection
    data = {
        "vacuum_coherence": vacuum_coherence,
        "coherence_history": [],
        "resonance_history": [],
        "node_count_history": [],
        "edge_count_history": [],
        "event_sizes": [],
        "checkpoints": []
    }
    
    start_time = time.time()
    
    # Evolution loop
    for step in range(num_steps):
        # Evolve
        event_size, graph = evolve_step(graph, omega, grace_probability=0.1)
        
        # Measure
        coh = compute_coherence(graph)
        res = compute_resonance_alignment(graph, omega)
        
        # Log
        data["coherence_history"].append(coh)
        data["resonance_history"].append(res)
        data["node_count_history"].append(len(graph.nodes))
        data["edge_count_history"].append(len(graph.edges))
        data["event_sizes"].append(event_size)
        
        # Checkpoint
        if step % checkpoint_interval == 0 and step > 0:
            elapsed = time.time() - start_time
            steps_per_sec = step / elapsed if elapsed > 0 else 0
            
            print(f"\nStep {step}/{num_steps} ({steps_per_sec:.1f} steps/sec)")
            print(f"  Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
            print(f"  C(G): {coh:.4f}, Res(S,Ω): {res:.4f}")
            
            # Test Lorentz invariance at checkpoints
            if step % (checkpoint_interval * 2) == 0:
                lorentz_result = test_lorentz_invariance(graph, gamma=1.5)
                print(f"  Lorentz test: {lorentz_result['relative_change']*100:.2f}% violation")
                if lorentz_result['is_lorentz_invariant']:
                    print(f"    ✓ Lorentz invariant")
                else:
                    print(f"    ✗ Not Lorentz invariant")
            
            # Run emergence detection
            emergence_results = run_emergence_battery(
                graph,
                data["coherence_history"],
                data["event_sizes"]
            )
            
            print(f"  Emergence: {emergence_results['summary']['assessment']}")
            print(f"  Profound phenomena: {emergence_results['summary']['profound_phenomena_detected']}/4")
            
            # Save checkpoint
            checkpoint = {
                "step": step,
                "coherence": coh,
                "resonance": res,
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "emergence": emergence_results
            }
            data["checkpoints"].append(checkpoint)
    
    # Final measurements
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    final_coh = data["coherence_history"][-1]
    final_res = data["resonance_history"][-1]
    
    print(f"\nFinal state:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"  C(G): {final_coh:.4f} (Δ from vacuum: {final_coh - vacuum_coherence:.4f})")
    print(f"  Res(S,Ω): {final_res:.4f}")
    
    # Final Lorentz test
    print(f"\n" + "-"*70)
    print("LORENTZ INVARIANCE TEST (Final)")
    print("-"*70)
    
    lorentz_final = test_lorentz_invariance(graph, gamma=1.5)
    print(f"  C(G) before boost: {lorentz_final['coherence_before']:.4f}")
    print(f"  C(G) after boost (γ={lorentz_final['gamma']}): {lorentz_final['coherence_after']:.4f}")
    print(f"  Relative change: {lorentz_final['relative_change']*100:.2f}%")
    
    if lorentz_final['is_lorentz_invariant']:
        print(f"  ✓ LORENTZ INVARIANCE DETECTED")
        lorentz_status = "PASSED"
    else:
        print(f"  ✗ NO LORENTZ INVARIANCE")
        lorentz_status = "FAILED"
    
    data["lorentz_test"] = lorentz_final
    data["lorentz_status"] = lorentz_status
    
    # Run final emergence battery
    print(f"\n" + "-"*70)
    print("EMERGENCE DETECTION (Final)")
    print("-"*70)
    
    final_emergence = run_emergence_battery(
        graph,
        data["coherence_history"],
        data["event_sizes"]
    )
    
    data["final_emergence"] = final_emergence
    
    print(f"\nEmergence Assessment: {final_emergence['summary']['assessment']}")
    print(f"Profound phenomena detected: {final_emergence['summary']['profound_phenomena_detected']}/4")
    
    if final_emergence['criticality'].get('is_critical'):
        alpha = final_emergence['criticality']['power_law_exponent']
        r2 = final_emergence['criticality']['r_squared']
        print(f"  ✓ Self-organized criticality (α={alpha:.2f}, R²={r2:.2f})")
    
    if final_emergence['holography'].get('is_holographic'):
        print(f"  ✓ Holographic behavior")
    
    if final_emergence['arrow_of_time'].get('has_arrow'):
        frac = final_emergence['arrow_of_time']['monotonic_fraction']
        print(f"  ✓ Thermodynamic arrow of time ({frac*100:.1f}% monotonic)")
    
    if final_emergence['locality'].get('has_locality'):
        ratio = final_emergence['locality']['locality_ratio']
        print(f"  ✓ Emergent locality (ratio={ratio:.2f})")
    
    # Dimensionless ratios (comprehensive measurement)
    print(f"\n" + "-"*70)
    print("DIMENSIONLESS RATIOS (Comprehensive)")
    print("-"*70)
    
    # Import ratio measurement
    sys.path.insert(0, os.path.dirname(__file__))
    from measure_dimensionless_ratios import measure_all_ratios, find_alpha_candidates, print_ratio_report
    
    # Count grace events (estimate from event sizes)
    grace_events_estimate = sum(1 for e in data["event_sizes"] if e > 0)
    total_rewrites_estimate = len(data["event_sizes"])
    
    ratios_data = measure_all_ratios(graph, grace_events_estimate, total_rewrites_estimate)
    print_ratio_report(ratios_data)
    
    data["dimensionless_ratios"] = ratios_data
    
    # Check for α
    alpha_candidates = find_alpha_candidates(ratios_data, threshold=0.01)
    ratio_status = "MATCHES_ALPHA" if alpha_candidates else "NO_ALPHA_MATCH"
    
    # Overall assessment
    print(f"\n" + "="*70)
    print("OVERALL ASSESSMENT")
    print("="*70)
    
    phenomena_count = final_emergence['summary']['profound_phenomena_detected']
    
    # Add Lorentz invariance to count
    if lorentz_status == "PASSED":
        phenomena_count += 1
        print(f"  ✓ Lorentz invariance")
    
    # Add dimensionless ratios if matched
    if ratio_status == "MATCHES_ALPHA":
        phenomena_count += 1
        print(f"  ✓ Dimensionless ratios (α found!)")
    elif alpha_candidates:
        phenomena_count += 1
        print(f"  ✓ Dimensionless ratios (α candidates: {len(alpha_candidates)})")
    
    print(f"\nTotal profound phenomena: {phenomena_count}/6")
    
    if phenomena_count >= 5:
        assessment = "REVOLUTIONARY"
    elif phenomena_count >= 4:
        assessment = "HIGHLY INTERESTING (approaching revolutionary)"
    elif phenomena_count >= 3:
        assessment = "HIGHLY INTERESTING"
    elif phenomena_count >= 2:
        assessment = "PROMISING"
    else:
        assessment = "TOY MODEL"
    
    print(f"FINAL ASSESSMENT: {assessment}")
    
    data["final_assessment"] = {
        "phenomena_count": phenomena_count,
        "total_possible": 6,
        "assessment": assessment
    }
    
    # Save data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\nData saved to: {output_file}")
    print(f"Total time: {time.time() - start_time:.1f} seconds")
    print("="*70)
    
    return data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run long FIRM evolution")
    parser.add_argument("--steps", type=int, default=1000, help="Number of steps")
    parser.add_argument("--checkpoint", type=int, default=100, help="Checkpoint interval")
    parser.add_argument("--output", type=str, default="evolution_data.json", help="Output file")
    
    args = parser.parse_args()
    
    run_long_evolution(
        num_steps=args.steps,
        checkpoint_interval=args.checkpoint,
        output_file=args.output
    )
