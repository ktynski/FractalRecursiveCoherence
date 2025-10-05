"""
Test Spontaneous Symmetry Breaking (Correct Direction)

Previous test: cold → hot (wrong direction)
This test: hot → cold (correct direction, like universe cooling)

Start: 50/50 Z/X (symmetric, high temperature)
Evolve: Reduce randomness (cool down)
Check: Does system break to 70/30 or 30/70? (asymmetric, low temperature)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.coherence_gauge_invariant import compute_coherence_gauge_invariant as compute_coherence


def initialize_symmetric_graph(num_nodes=20):
    """Initialize with 50/50 Z/X (symmetric)."""
    nodes = list(range(num_nodes))
    edges = [[i, (i+1) % num_nodes] for i in range(num_nodes)]
    
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    
    for i in range(num_nodes):
        # Exactly 50/50 Z/X
        kind = 'Z' if i < num_nodes // 2 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    return validate_object_g(g)


def evolve_at_temperature(graph, temperature, num_steps=20):
    """
    Evolve graph at given temperature.
    
    Temperature controls randomness:
    - T = 1.0: completely random (hot)
    - T = 0.0: deterministic (cold)
    
    At low T, system should "freeze" into asymmetric state.
    """
    phi = (1 + np.sqrt(5)) / 2
    
    for step in range(num_steps):
        new_id = len(graph.nodes)
        
        # Type selection depends on temperature
        if temperature > 0.5:
            # Hot: random
            kind = 'Z' if np.random.random() > 0.5 else 'X'
        else:
            # Cold: prefer majority type (symmetry breaking)
            z_count = sum(1 for nid in graph.nodes if graph.labels[nid].kind == 'Z')
            x_count = len(graph.nodes) - z_count
            
            # Bias toward majority (with some randomness from temperature)
            z_prob = (z_count / len(graph.nodes)) * (1 - temperature) + 0.5 * temperature
            kind = 'Z' if np.random.random() < z_prob else 'X'
        
        phase_numer = int((new_id * 100 / phi)) % 100
        new_label = make_node_label(kind, phase_numer, 100, f'n{new_id}')
        
        graph.nodes.append(new_id)
        graph.labels[new_id] = new_label
        
        # Connect
        if graph.nodes[:-1]:
            target = np.random.choice(graph.nodes[:-1])
            graph.edges.append([new_id, target])
        
        graph = validate_object_g(graph)
    
    return graph


def test_symmetry_breaking():
    """Test spontaneous symmetry breaking via cooling."""
    print("="*80)
    print("SPONTANEOUS SYMMETRY BREAKING TEST (Hot → Cold)")
    print("="*80)
    
    # Start symmetric (hot)
    graph = initialize_symmetric_graph(num_nodes=20)
    
    z_count_initial = sum(1 for nid in graph.nodes if graph.labels[nid].kind == 'Z')
    z_fraction_initial = z_count_initial / len(graph.nodes)
    
    print(f"\nInitial state (T = 1.0, hot):")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Z fraction: {z_fraction_initial*100:.1f}%")
    print(f"  Symmetry: {'Symmetric' if abs(z_fraction_initial - 0.5) < 0.05 else 'Asymmetric'}")
    
    # Cool down in stages
    temperatures = [1.0, 0.7, 0.4, 0.1, 0.01]
    z_fractions = [z_fraction_initial]
    
    print("\nCooling evolution:")
    print("-"*80)
    
    for T in temperatures:
        graph = evolve_at_temperature(graph, T, num_steps=20)
        
        z_count = sum(1 for nid in graph.nodes if graph.labels[nid].kind == 'Z')
        z_fraction = z_count / len(graph.nodes)
        z_fractions.append(z_fraction)
        
        deviation = abs(z_fraction - 0.5)
        
        print(f"\nT = {T:.2f}:")
        print(f"  Nodes: {len(graph.nodes)}")
        print(f"  Z fraction: {z_fraction*100:.1f}%")
        print(f"  Deviation from 50/50: {deviation*100:.1f}%")
        
        if deviation > 0.15:
            print(f"  → Symmetry BROKEN")
        else:
            print(f"  → Still symmetric")
    
    # Final assessment
    final_z_fraction = z_fractions[-1]
    final_deviation = abs(final_z_fraction - 0.5)
    
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    print(f"\nInitial Z fraction: {z_fraction_initial*100:.1f}% (symmetric)")
    print(f"Final Z fraction:   {final_z_fraction*100:.1f}%")
    print(f"Final deviation:    {final_deviation*100:.1f}%")
    
    # Check for symmetry breaking
    if final_deviation > 0.15:
        print("\n✓ SPONTANEOUS SYMMETRY BREAKING DETECTED")
        print(f"  System cooled from symmetric (50/50) to asymmetric ({final_z_fraction*100:.0f}/{(1-final_z_fraction)*100:.0f})")
        print("  This is like Higgs mechanism (electroweak symmetry breaking)")
        return True
    else:
        print("\n✗ No clear symmetry breaking")
        print("  System remained approximately symmetric")
        return False


if __name__ == "__main__":
    has_symmetry_breaking = test_symmetry_breaking()
    
    if has_symmetry_breaking:
        print("\n" + "="*80)
        print("This is phenomenon #13!")
        print("="*80)
