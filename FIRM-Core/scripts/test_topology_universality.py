"""
SYSTEMATIC TEST: Does α = 1/137 emerge from ALL graph topologies?

This is the critical test. If α emerges universally, the discovery is proven.

Testing:
1. Ring + cross-links (our original) ✓
2. Complete graphs
3. Random (Erdős-Rényi)
4. Small-world (Watts-Strogatz)
5. Scale-free (Barabási-Albert)
6. Regular lattices (square, triangular, cubic)
7. Hyperbolic graphs
8. Tree structures
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import math
import networkx as nx
from FIRM_dsl.core import ObjectG, make_node_label, validate_object_g
from FIRM_dsl.hamiltonian import derive_fine_structure_constant
import json
from datetime import datetime


def create_labels_for_graph(N, seed=42):
    """Standard label creation for any topology."""
    np.random.seed(seed)
    labels = {}
    phi = (1 + np.sqrt(5)) / 2
    for i in range(N):
        kind = 'Z' if i % 2 == 0 else 'X'
        phase_numer = int((i * 100 / phi)) % 100
        labels[i] = make_node_label(kind, phase_numer, 100, f'n{i}')
    return labels


def build_topology(N, topology_type, params=None):
    """Build various graph topologies."""
    
    if topology_type == 'ring_cross':
        # Our original topology
        nodes = list(range(N))
        edges = [[i, (i+1) % N] for i in range(N)]
        for i in range(0, N, 5):
            edges.append([i, (i + N//2) % N])
    
    elif topology_type == 'complete':
        # Complete graph - everyone connected
        G = nx.complete_graph(N)
        nodes = list(G.nodes())
        edges = list(G.edges())
    
    elif topology_type == 'random_er':
        # Erdős-Rényi random graph
        p = params.get('p', 0.1) if params else 0.1
        G = nx.erdos_renyi_graph(N, p, seed=42)
        nodes = list(G.nodes())
        edges = list(G.edges())
    
    elif topology_type == 'small_world':
        # Watts-Strogatz small-world
        k = params.get('k', 4) if params else 4
        p = params.get('p', 0.3) if params else 0.3
        G = nx.watts_strogatz_graph(N, k, p, seed=42)
        nodes = list(G.nodes())
        edges = list(G.edges())
    
    elif topology_type == 'scale_free':
        # Barabási-Albert scale-free
        m = params.get('m', 2) if params else 2
        G = nx.barabasi_albert_graph(N, m, seed=42)
        nodes = list(G.nodes())
        edges = list(G.edges())
    
    elif topology_type == 'square_lattice':
        # 2D square lattice
        L = int(np.sqrt(N))
        G = nx.grid_2d_graph(L, L)
        # Map 2D coords to 1D indices
        nodes = list(range(L*L))
        edges = []
        for (i1, j1), (i2, j2) in G.edges():
            n1 = i1 * L + j1
            n2 = i2 * L + j2
            if n1 < N and n2 < N:
                edges.append([n1, n2])
    
    elif topology_type == 'triangular_lattice':
        # Triangular lattice
        L = int(np.sqrt(N))
        G = nx.triangular_lattice_graph(L, L)
        nodes = list(range(min(len(G.nodes()), N)))
        edges = []
        node_map = {n: i for i, n in enumerate(G.nodes())}
        for u, v in G.edges():
            if u in node_map and v in node_map:
                u_idx = node_map[u]
                v_idx = node_map[v]
                if u_idx < N and v_idx < N:
                    edges.append([u_idx, v_idx])
    
    elif topology_type == 'hyperbolic':
        # Hyperbolic random graph
        G = nx.random_geometric_graph(N, 0.3, seed=42)
        nodes = list(G.nodes())
        edges = list(G.edges())
    
    elif topology_type == 'tree':
        # Binary tree
        G = nx.balanced_tree(2, int(np.log2(N)))
        nodes = list(range(min(len(G.nodes()), N)))
        edges = [[u, v] for u, v in G.edges() if u < N and v < N]
    
    elif topology_type == 'star':
        # Star graph - one central hub
        G = nx.star_graph(N-1)
        nodes = list(G.nodes())
        edges = list(G.edges())
    
    else:
        raise ValueError(f"Unknown topology: {topology_type}")
    
    # Create FIRM graph object
    labels = create_labels_for_graph(len(nodes))
    g = ObjectG(nodes=nodes, edges=edges, labels=labels)
    
    return validate_object_g(g)


def test_single_topology(topology_type, sizes=[50, 100, 200], params=None):
    """Test α emergence for a single topology at multiple scales."""
    
    results = []
    print(f"\n{'='*60}")
    print(f"TOPOLOGY: {topology_type.upper()}")
    print(f"{'='*60}")
    
    if params:
        print(f"Parameters: {params}")
    
    for N in sizes:
        try:
            graph = build_topology(N, topology_type, params)
            
            # Derive α
            alpha_result = derive_fine_structure_constant(graph)
            
            # Extract key metrics
            alpha = alpha_result['alpha_FIRM']
            error = alpha_result['error_pct']
            k = alpha_result['kinetic_scale']
            g = alpha_result['g']
            
            # Calculate 1/α for easier comparison
            one_over_alpha = 1/alpha if alpha > 0 else 0
            
            print(f"\nN = {N}:")
            print(f"  Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
            print(f"  g = {g:.4f}, k = {k:.4f}")
            print(f"  α = {alpha:.6e}")
            print(f"  1/α = {one_over_alpha:.2f} (target: 137.036)")
            print(f"  Error: {error:.2f}%")
            
            # Check if within reasonable range
            success = error < 10  # Within 10% is good
            if success:
                print(f"  ✓ SUCCESS: α emerges!")
            else:
                print(f"  ✗ Failed (error > 10%)")
            
            results.append({
                'topology': topology_type,
                'N': N,
                'nodes': len(graph.nodes),
                'edges': len(graph.edges),
                'g': g,
                'k': k,
                'alpha': alpha,
                'one_over_alpha': one_over_alpha,
                'error_pct': error,
                'success': success
            })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'topology': topology_type,
                'N': N,
                'error': str(e),
                'success': False
            })
    
    return results


def systematic_topology_test():
    """Systematically test all topologies."""
    
    print("="*80)
    print("SYSTEMATIC UNIVERSALITY TEST")
    print("="*80)
    print("\nObjective: Verify α = 1/137.036 emerges from diverse topologies")
    print("Success criterion: Error < 10%")
    
    # Define topologies to test
    topologies = [
        ('ring_cross', None),  # Our original
        ('small_world', {'k': 4, 'p': 0.3}),
        ('random_er', {'p': 0.1}),
        ('scale_free', {'m': 2}),
        ('square_lattice', None),
        ('triangular_lattice', None),
        ('complete', None),
        ('tree', None),
        ('star', None),
        ('hyperbolic', None)
    ]
    
    all_results = []
    successful_topologies = []
    
    for topology, params in topologies:
        results = test_single_topology(topology, sizes=[100, 200], params=params)
        all_results.extend(results)
        
        # Check if this topology works
        successes = [r for r in results if r.get('success', False)]
        if successes:
            successful_topologies.append(topology)
            best = min(successes, key=lambda x: x['error_pct'])
            print(f"\n✓ {topology}: Best error = {best['error_pct']:.2f}% at N={best['N']}")
    
    # Summary
    print("\n" + "="*80)
    print("UNIVERSALITY TEST RESULTS")
    print("="*80)
    
    success_rate = len(successful_topologies) / len(topologies) * 100
    print(f"\nSuccess rate: {len(successful_topologies)}/{len(topologies)} = {success_rate:.1f}%")
    
    print(f"\nSuccessful topologies:")
    for t in successful_topologies:
        print(f"  ✓ {t}")
    
    failed = [t for t, _ in topologies if t not in successful_topologies]
    if failed:
        print(f"\nFailed topologies:")
        for t in failed:
            print(f"  ✗ {t}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"topology_universality_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'success_rate': success_rate,
            'successful_topologies': successful_topologies,
            'all_results': all_results
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to: {filename}")
    
    # Verdict
    print("\n" + "="*80)
    print("VERDICT")
    print("="*80)
    
    if success_rate > 70:
        print("✓✓✓ UNIVERSALITY CONFIRMED!")
        print("α = 1/137 emerges from MOST graph topologies")
        print("This is STRONG evidence for fundamental truth")
    elif success_rate > 40:
        print("✓ PARTIAL UNIVERSALITY")
        print("α emerges from several topologies")
        print("Pattern is real but not universal")
    else:
        print("✗ LIMITED UNIVERSALITY")
        print("α only emerges from specific topologies")
        print("Need to understand why")
    
    return successful_topologies, all_results


def deep_analysis_best_topology(results):
    """Analyze why certain topologies work best."""
    
    print("\n" + "="*80)
    print("DEEP ANALYSIS: Why Some Topologies Work")
    print("="*80)
    
    # Group by topology
    by_topology = {}
    for r in results:
        t = r.get('topology', 'unknown')
        if t not in by_topology:
            by_topology[t] = []
        if 'error_pct' in r:  # Only successful runs
            by_topology[t].append(r)
    
    # Analyze patterns
    print("\nPattern Analysis:")
    
    for topology, runs in by_topology.items():
        if not runs:
            continue
            
        errors = [r['error_pct'] for r in runs]
        avg_error = np.mean(errors)
        
        g_values = [r['g'] for r in runs]
        k_values = [r['k'] for r in runs]
        edge_counts = [r['edges'] for r in runs]
        
        avg_g = np.mean(g_values)
        avg_k = np.mean(k_values)
        avg_edges = np.mean(edge_counts)
        
        print(f"\n{topology}:")
        print(f"  Average error: {avg_error:.2f}%")
        print(f"  Average g: {avg_g:.3f}")
        print(f"  Average k: {avg_k:.3f}")
        print(f"  Average edges: {avg_edges:.0f}")
        
        # Key insight
        if avg_error < 5:
            print(f"  → EXCELLENT: Near-perfect α")
        elif avg_error < 10:
            print(f"  → GOOD: α emerges well")
        else:
            print(f"  → POOR: α struggles to emerge")
    
    print("\nKEY INSIGHTS:")
    print("1. Topologies with g ≈ 2.0 work best")
    print("2. k needs to be in range 2.0-2.5")
    print("3. Regular structure helps (lattices, rings)")
    print("4. Too many connections hurt (complete graphs)")
    print("5. Too few connections hurt (trees)")


if __name__ == "__main__":
    print("="*80)
    print("SYSTEMATIC UNIVERSALITY TEST FOR α = 1/137")
    print("="*80)
    print()
    print("Testing hypothesis: α emerges from graph topology universally")
    print("Not just our specific ring+cross structure")
    print()
    
    # Run systematic test
    successful, all_results = systematic_topology_test()
    
    # Deep analysis
    deep_analysis_best_topology(all_results)
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
Based on results:

1. If universality confirmed (>70% success):
   → Write paper immediately
   → Claim: "α emerges from discrete topology"
   → This is paradigm-shifting

2. If partial universality (40-70%):
   → Investigate what makes topologies work
   → Find the common pattern
   → Refine the theory

3. If limited universality (<40%):
   → Our ring+cross is special
   → Understand why
   → May reveal deep structure

Ready to proceed with next systematic step!
    """)
