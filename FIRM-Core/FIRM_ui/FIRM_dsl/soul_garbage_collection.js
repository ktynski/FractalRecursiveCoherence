/**
 * Soul Garbage Collection (𝒮-GC) JavaScript implementation for FIRM UI
 *
 * JavaScript version of the Python SGC module for browser-based operation.
 * Implements the recursive coherence-sieve rule for morphic pruning:
 * 𝒮GC(μ) = ∅ if resonance(μ) < ε and grace(μ) = true, else μ ← { 𝒮GC(ν) | ν ∈ children(μ) }
 */

// Import existing DSL modules
import { ObjectG } from './core.js';
import { computeResonanceAlignment, deriveOmegaSignature } from './resonance.js';

// SGC Parameters class (JavaScript version)
export class SGCGCParams {
    constructor(epsilon = 0.3, grace_readiness_threshold = 0.5, max_recursion_depth = 10, observer_feedback_weight = 0.2) {
        this.epsilon = epsilon;
        this.grace_readiness_threshold = grace_readiness_threshold;
        this.max_recursion_depth = max_recursion_depth;
        this.observer_feedback_weight = observer_feedback_weight;
    }
}

// Field regimes enum (JavaScript version)
export const FieldRegime = {
    NON_BEING: 'non_being',
    VACUUM: 'vacuum',
    DARK_SECTOR: 'dark_sector',
    MATTER: 'matter',
    OMEGA: 'omega'
};

// Morphic structure class (JavaScript version)
export class MorphicStructure {
    constructor(graph, parent = null) {
        // Ensure graph is an ObjectG instance
        if (graph && typeof graph === 'object' && !graph.nodes) {
            this.graph = new ObjectG(graph);
        } else {
            this.graph = graph;
        }
        this.parent = parent;
        this.children = [];
        this.coherence_cache = null;
        this.grace_cache = null;
        this.resonance_cache = null;

        // Build children from graph structure
        this._build_children();
    }

    _build_children() {
        // CORRECTED: For sovereign triads, children represent internal structure
        // Each triad node becomes a child structure for more granular SGC
        if (this.graph && this.graph.labels && Object.keys(this.graph.labels).length === 3) {
            // For triads, create child structures for each node (sovereign architecture)
            const nodeIds = Object.keys(this.graph.labels);

            this.children = nodeIds.map(nodeId => {
                const nodeGraph = this._create_node_subgraph(nodeId);
                return nodeGraph ? new MorphicStructure(nodeGraph, this) : null;
            }).filter(child => child !== null);
        } else if (this.graph && this.graph.labels && Object.keys(this.graph.labels).length > 3) {
            // For larger structures, use intelligent partitioning based on connectivity
            const nodeIds = Object.keys(this.graph.labels);
            const connectedComponents = this._find_connected_components();

            this.children = connectedComponents.map(component => {
                const componentGraph = this._create_subgraph(component);
                return componentGraph ? new MorphicStructure(componentGraph, this) : null;
            }).filter(child => child !== null);
        }
    }

    _find_connected_components() {
        // Find connected components for intelligent partitioning
        const visited = new Set();
        const components = [];

        for (const nodeId of Object.keys(this.graph.labels)) {
            if (!visited.has(nodeId)) {
                const component = this._dfs_component(nodeId, visited);
                if (component.length > 0) {
                    components.push(component);
                }
            }
        }

        return components;
    }

    _dfs_component(startNode, visited) {
        const component = [];
        const stack = [startNode];

        while (stack.length > 0) {
            const node = stack.pop();
            if (!visited.has(node)) {
                visited.add(node);
                component.push(node);

                // Add connected nodes to stack
                if (this.graph.edges) {
                    for (const [u, v] of this.graph.edges) {
                        if (u === node && !visited.has(v)) {
                            stack.push(v);
                        } else if (v === node && !visited.has(u)) {
                            stack.push(u);
                        }
                    }
                }
            }
        }

        return component;
    }

    _create_subgraph(nodeIds) {
        if (!nodeIds || nodeIds.length === 0) return null;

        const subgraphLabels = {};
        const subgraphEdges = [];

        // Safely extract relevant labels
        if (this.graph && this.graph.labels) {
            for (const nodeId of nodeIds) {
                if (this.graph.labels[nodeId]) {
                    subgraphLabels[nodeId] = this.graph.labels[nodeId];
                }
            }
        }

        // Extract relevant edges
        if (this.graph && this.graph.edges) {
            for (const [u, v] of this.graph.edges) {
                if (nodeIds.includes(u) && nodeIds.includes(v)) {
                    subgraphEdges.push([u, v]);
                }
            }
        }

        if (Object.keys(subgraphLabels).length === 0) return null;

        return new ObjectG({
            nodes: nodeIds,
            edges: subgraphEdges,
            labels: subgraphLabels
        });
    }

    _create_node_subgraph(nodeId) {
        // Create a subgraph containing just one node (for triad internal structure)
        if (!this.graph || !this.graph.labels || !this.graph.labels[nodeId]) {
            return null;
        }

        return new ObjectG({
            nodes: [nodeId],
            edges: [], // Single node has no internal edges
            labels: { [nodeId]: this.graph.labels[nodeId] }
        });
    }

    get_resonance(omega, params) {
        if (this.resonance_cache === null) {
            try {
                // Simple fallback - use coherence as resonance measure
                // The actual resonance calculation requires proper Qπ setup
                this.resonance_cache = this.get_coherence();
            } catch (error) {
                console.warn('Failed to compute resonance:', error.message);
                // Canonical baseline: φ⁻¹ ≈ 0.618 represents natural vacuum potential
                this.resonance_cache = 1 / 1.618033988749; // Golden ratio inverse
            }
        }
        return this.resonance_cache;
    }

    get_grace_state(params) {
        if (this.grace_cache === null) {
            const coherence = this.get_coherence();
            const fieldRegime = this.get_field_regime();

            // Grace readiness based on field regime and coherence stability
            const regime_grace_factor = {
                [FieldRegime.NON_BEING]: 0.0,
                [FieldRegime.VACUUM]: 0.1,
                [FieldRegime.DARK_SECTOR]: 0.3,
                [FieldRegime.MATTER]: 0.7,
                [FieldRegime.OMEGA]: 1.0
            }[fieldRegime] || 0.0;

            const grace_threshold = params.grace_readiness_threshold * regime_grace_factor;
            const stability_factor = 1.0 - Math.abs(coherence - 0.5) * 0.5;

            this.grace_cache = (coherence < grace_threshold) && (stability_factor > 0.3);
        }
        return this.grace_cache;
    }

    get_coherence() {
        if (this.coherence_cache === null) {
            // Simplified coherence calculation for JavaScript
            // In a full implementation, this would use the coherence.js module
            if (this.graph && this.graph.labels) {
                const nodeCount = Object.keys(this.graph.labels).length;
                const edgeCount = this.graph.edges ? this.graph.edges.length : 0;
                this.coherence_cache = Math.min(1.0, (nodeCount + edgeCount) / 20.0);
            } else {
                this.coherence_cache = 0.0;
            }
        }
        return this.coherence_cache;
    }

    get_field_regime() {
        const numNodes = this.graph && this.graph.labels ? Object.keys(this.graph.labels).length : 0;

        if (numNodes <= 1) {
            return FieldRegime.NON_BEING;
        } else if (numNodes <= 5) {
            return FieldRegime.VACUUM;
        } else if (numNodes <= 12) {
            return FieldRegime.DARK_SECTOR;
        } else {
            return FieldRegime.MATTER;
        }
    }
}

// Soul Garbage Collector class (JavaScript version)
export class SoulGarbageCollector {
    constructor(omega, params) {
        this.omega = omega;
        this.params = params;
        this.pruned_nodes = [];
        this.recursion_depth = 0;
    }

    sgc_rule(morphic_structure) {
        this.recursion_depth++;

        try {
            // Safety check for max recursion depth
            if (this.recursion_depth > this.params.max_recursion_depth) {
                return morphic_structure;
            }

            // Compute resonance and grace state
            const resonance = morphic_structure.get_resonance(this.omega, this.params);
            const grace_ready = morphic_structure.get_grace_state(this.params);

            // 𝒮-GC Decision Logic
            if (resonance < this.params.epsilon && grace_ready) {
                // Prune this morphic structure
                this._record_pruned_nodes(morphic_structure);
                return null; // Return ∅ (deletion)
            }

            // Otherwise, recursively apply to children
            const surviving_children = [];
            for (const child of morphic_structure.children) {
                const surviving_child = this.sgc_rule(child);
                if (surviving_child !== null) {
                    surviving_children.push(surviving_child);
                }
            }

            // Update children if any were pruned
            if (surviving_children.length !== morphic_structure.children.length) {
                // Create new structure with surviving children
                const new_structure = new MorphicStructure(morphic_structure.graph, morphic_structure.parent);
                new_structure.children = surviving_children;
                return new_structure;
            }

            return morphic_structure;

        } finally {
            this.recursion_depth--;
        }
    }

    _record_pruned_nodes(structure) {
        if (structure.graph && structure.graph.labels) {
            this.pruned_nodes.push(...Object.keys(structure.graph.labels));
        }
    }

    compute_entropy_reduction(original_structure, pruned_structure) {
        if (!pruned_structure) {
            // Complete pruning
            return 1.0;
        }

        const original_coherence = original_structure.get_coherence();
        const pruned_coherence = pruned_structure.get_coherence();

        const coherence_improvement = Math.max(0, pruned_coherence - original_coherence);

        const original_nodes = original_structure.graph && original_structure.graph.labels ? Object.keys(original_structure.graph.labels).length : 0;
        const pruned_nodes = pruned_structure && pruned_structure.graph && pruned_structure.graph.labels ? Object.keys(pruned_structure.graph.labels).length : 0;
        const node_reduction = original_nodes > 0 ? Math.max(0, original_nodes - pruned_nodes) / original_nodes : 0;

        // Weighted combination
        return 0.6 * coherence_improvement + 0.4 * node_reduction;
    }
}

// Factory function for SGC parameters (JavaScript version)
export function create_sgc_params(epsilon = 0.3, grace_threshold = 0.5, max_recursion_depth = 10, feedback_weight = 0.2) {
    return new SGCGCParams(epsilon, grace_threshold, max_recursion_depth, feedback_weight);
}
