"""
Long-Run Evolution: Extended simulation to detect emergent phenomena.

This script runs FIRM evolution for thousands of steps, logging:
- Coherence C(G) over time
- Resonance Res(S,Ω) over time
- Event sizes (for criticality detection)
- Dimensionless ratios (cycle lengths, Grace/rewrite ratio)
- Phase transition markers

Results are saved to JSON for analysis and visualization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import time
import numpy as np
from collections import defaultdict
from FIRM_dsl.core import ObjectG
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.resonance import derive_omega_signature, compute_resonance_alignment
from FIRM_dsl.emergence_detection import run_emergence_battery
from FIRM_zx.rules import apply_spider_fusion, apply_color_flip


def initialize_graph(num_nodes=10):
    """Create initial graph with some structure."""
    graph = ObjectG()
    phi = (1 + np.sqrt(5)) / 2  # Golden ratio
    
    for i in range(num_nodes):
        node_type = 'Z' if i % 2 == 0 else 'X'
        phase = (i * np.pi / phi) % (2 * np.pi)
        graph.add_node(i, node_type=node_type, phase=phase)
    
    # Create initial edges (ring + some cross-links)
    for i in range(num_nodes - 1):
        graph.add_edge(i, i + 1)
    graph.add_edge(num_nodes - 1, 0)  # Close ring
    
    # Add cross-links for richer structure
    for i in range(0, num_nodes, 3):
        target = (i + num_nodes // 2) % num_nodes
        if not graph.has_edge(i, target):
            graph.add_edge(i, target)
    
    return graph


def evolve_step(graph, omega, grace_probability=0.1):
    """
    Perform one evolution step with resonance-guided selection.
    
    Returns:
        event_size: Number of nodes affected by this step
    """
    event_size = 0
    
    # Compute resonance for steering
    res = compute_resonance_alignment(graph, omega)
    
    # Grace emergence (probabilistic, φ-scaled)
    if np.random.random() < grace_probability * res:
        # Add new node with φ-modulated phase
        new_id = max(graph.nodes.keys()) + 1
        phi = (1 + np.sqrt(5)) / 2
        phase = (new_id * np.pi / phi) % (2 * np.pi)
        node_type = 'Z' if np.random.random() > 0.5 else 'X'
        graph.add_node(new_id, node_type=node_type, phase=phase)
        
        # Connect to existing node (prefer high-degree nodes)
        existing_nodes = list(graph.nodes.keys())
        degrees = [len(list(graph.neighbors(n))) for n in existing_nodes]
        probs = np.array(degrees) / sum(degrees) if sum(degrees) > 0 else np.ones(len(degrees)) / len(degrees)
        target = np.random.choice(existing_nodes, p=probs)
        graph.add_edge(new_id, target)
        
        event_size += 1
    
    # Spider fusion (if eligible)
    if len(graph.nodes) > 3 and np.random.random() < 0.3 * res:
        nodes = list(graph.nodes.keys())
        for _ in range(min(5, len(nodes) // 2)):  # Try multiple fusions
            n1, n2 = np.random.choice(nodes, 2, replace=False)
            if graph.has_edge(n1, n2) and graph.nodes[n1]['node_type'] == graph.nodes[n2]['node_type']:
                try:
                    apply_spider_fusion(graph, n1, n2)
                    event_size += 1
                    break
                except:
                    pass
    
    # Color flip (if eligible)
    if np.random.random() < 0.2:
        nodes = list(graph.nodes.keys())
        if nodes:
            node_to_flip = np.random.choice(nodes)
            try:
                apply_color_flip(graph, node_to_flip)
                event_size += 1
            except:
                pass
    
    return event_size


def run_long_evolution(num_steps=5000, checkpoint_interval=100, output_file="evolution_data.json"):
    """
    Run extended evolution and log all data.
    
    Args:
        num_steps: Number of evolution steps
        checkpoint_interval: How often to log detailed data
        output_file: Where to save results
    """
    print(f"Starting long-run evolution: {num_steps} steps")
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
        "steps": [],
        "coherence_history": [],
        "resonance_history": [],
        "node_count_history": [],
        "edge_count_history": [],
        "event_sizes": [],
        "grace_events": 0,
        "fusion_events": 0,
        "colorflip_events": 0,
        "checkpoints": []
    }
    
    start_time = time.time()
    
    # Evolution loop
    for step in range(num_steps):
        # Evolve
        event_size = evolve_step(graph, omega, grace_probability=0.1)
        
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
        if step % checkpoint_interval == 0:
            elapsed = time.time() - start_time
            steps_per_sec = (step + 1) / elapsed if elapsed > 0 else 0
            
            print(f"Step {step}/{num_steps} ({steps_per_sec:.1f} steps/sec)")
            print(f"  Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
            print(f"  C(G): {coh:.4f}, Res(S,Ω): {res:.4f}")
            
            # Run emergence detection
            emergence_results = run_emergence_battery(
                graph,
                data["coherence_history"],
                data["event_sizes"]
            )
            
            print(f"  Emergence: {emergence_results['summary']['assessment']}")
            print(f"  Profound phenomena: {emergence_results['summary']['profound_phenomena_detected']}/4\n")
            
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
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    final_coh = data["coherence_history"][-1]
    final_res = data["resonance_history"][-1]
    
    print(f"\nFinal state:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"  C(G): {final_coh:.4f} (Δ from vacuum: {final_coh - vacuum_coherence:.4f})")
    print(f"  Res(S,Ω): {final_res:.4f}")
    
    # Run final emergence battery
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
        print(f"  ✓ Self-organized criticality (α={alpha:.2f})")
    
    if final_emergence['holography'].get('is_holographic'):
        print(f"  ✓ Holographic behavior")
    
    if final_emergence['arrow_of_time'].get('has_arrow'):
        frac = final_emergence['arrow_of_time']['monotonic_fraction']
        print(f"  ✓ Thermodynamic arrow of time ({frac*100:.1f}% monotonic)")
    
    if final_emergence['locality'].get('has_locality'):
        ratio = final_emergence['locality']['locality_ratio']
        print(f"  ✓ Emergent locality (ratio={ratio:.2f})")
    
    # Dimensionless ratios
    print(f"\nDimensionless Ratios:")
    if len(data["event_sizes"]) > 0:
        mean_event = np.mean(data["event_sizes"])
        max_event = max(data["event_sizes"])
        print(f"  Max event / Mean event: {max_event / mean_event if mean_event > 0 else 0:.2f}")
    
    # Save data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nData saved to: {output_file}")
    print(f"Total time: {time.time() - start_time:.1f} seconds")
    
    return data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run long FIRM evolution to detect emergence")
    parser.add_argument("--steps", type=int, default=5000, help="Number of evolution steps")
    parser.add_argument("--checkpoint", type=int, default=100, help="Checkpoint interval")
    parser.add_argument("--output", type=str, default="evolution_data.json", help="Output file")
    
    args = parser.parse_args()
    
    run_long_evolution(
        num_steps=args.steps,
        checkpoint_interval=args.checkpoint,
        output_file=args.output
    )
