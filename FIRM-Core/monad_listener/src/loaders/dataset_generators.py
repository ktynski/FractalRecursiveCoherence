"""
Dataset Generators for Monad Listener Validation

Generates reproducible datasets for 5 domains with rich symmetries:
1. Quantum circuits (Clifford+T)
2. Cellular automata (Rule 30/54/110, 2D Life)
3. PDE fields (wave, Burgers, reaction-diffusion)
4. Spin lattices (Ising/XY models)
5. Graph dynamics (Boolean networks)
"""

import numpy as np
import torch
from typing import Dict, List, Tuple, Any
import random

class DatasetGenerator:
    """Base class for all dataset generators"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

    def generate_dataset(self, n_samples: int, split_ratios: Tuple[float, float, float] = (0.7, 0.15, 0.15)) -> Dict[str, List]:
        """Generate train/val/test splits"""
        train_size = int(n_samples * split_ratios[0])
        val_size = int(n_samples * split_ratios[1])
        test_size = n_samples - train_size - val_size

        data = self._generate_samples(n_samples)

        return {
            'train': data[:train_size],
            'val': data[train_size:train_size + val_size],
            'test': data[train_size + val_size:]
        }

    def _generate_samples(self, n_samples: int) -> List[Dict]:
        """Generate n_samples of data"""
        raise NotImplementedError

class QuantumCircuitGenerator(DatasetGenerator):
    """Generate random Clifford+T quantum circuits"""

    def __init__(self, n_qubits: int = 4, max_gates: int = 20, **kwargs):
        super().__init__(**kwargs)
        self.n_qubits = n_qubits
        self.max_gates = max_gates

    def _generate_samples(self, n_samples: int) -> List[Dict]:
        samples = []

        for _ in range(n_samples):
            # Generate random Clifford+T circuit
            circuit = self._generate_circuit()

            # Convert to statevector/density matrix
            statevector = self._circuit_to_statevector(circuit)

            # Generate ZX normal form
            zx_form = self._circuit_to_zx(circuit)

            samples.append({
                'type': 'quantum',
                'circuit': circuit,
                'statevector': statevector,
                'zx_form': zx_form,
                'symmetries': ['global_phase', 'clifford_conjugation']
            })

        return samples

    def _generate_circuit(self) -> List[str]:
        """Generate random Clifford+T circuit"""
        clifford_gates = ['H', 'S', 'X', 'Y', 'Z', 'CNOT']
        circuit = []

        for _ in range(np.random.randint(5, self.max_gates)):
            if np.random.random() < 0.3:  # 30% chance of T gate
                gate = 'T'
            else:
                gate = np.random.choice(clifford_gates)

            if gate == 'CNOT':
                control = np.random.randint(0, self.n_qubits)
                target = (control + np.random.randint(1, self.n_qubits)) % self.n_qubits
                circuit.append(f'CNOT({control},{target})')
            else:
                qubit = np.random.randint(0, self.n_qubits)
                circuit.append(f'{gate}({qubit})')

        return circuit

    def _circuit_to_statevector(self, circuit: List[str]) -> np.ndarray:
        """Convert circuit to statevector (simplified)"""
        # This would use actual quantum simulation
        # For now, return random but realistic statevector
        dim = 2 ** self.n_qubits
        real_part = np.random.normal(0, 1/np.sqrt(dim), dim)
        imag_part = np.random.normal(0, 1/np.sqrt(dim), dim)
        statevector = real_part + 1j * imag_part
        statevector /= np.linalg.norm(statevector)
        return statevector

    def _circuit_to_zx(self, circuit: List[str]) -> Dict:
        """Convert circuit to ZX normal form (simplified)"""
        # This would use actual ZX calculus
        # For now, return simplified representation
        return {
            'spiders': np.random.randint(1, 10),
            'phases': np.random.uniform(0, 2*np.pi, np.random.randint(1, 5)),
            'connections': np.random.randint(0, 5, (np.random.randint(1, 10), 2))
        }

class CellularAutomataGenerator(DatasetGenerator):
    """Generate cellular automata traces"""

    def __init__(self, rule: int = 30, size: int = 100, steps: int = 200, **kwargs):
        super().__init__(**kwargs)
        self.rule = rule
        self.size = size
        self.steps = steps

    def _generate_samples(self, n_samples: int) -> List[Dict]:
        samples = []

        for _ in range(n_samples):
            # Generate random initial condition
            initial = np.random.randint(0, 2, self.size)

            # Evolve CA
            trace = self._evolve_ca(initial)

            samples.append({
                'type': 'ca',
                'rule': self.rule,
                'initial': initial,
                'trace': trace,
                'symmetries': ['lattice_translations', 'reflections']
            })

        return samples

    def _evolve_ca(self, initial: np.ndarray) -> np.ndarray:
        """Evolve cellular automaton"""
        trace = [initial.copy()]

        for step in range(self.steps):
            current = trace[-1]
            next_state = np.zeros_like(current)

            for i in range(self.size):
                # Get neighborhood
                left = current[(i-1) % self.size]
                center = current[i]
                right = current[(i+1) % self.size]

                # Apply rule
                neighborhood = (left << 2) | (center << 1) | right
                next_state[i] = (self.rule >> neighborhood) & 1

            trace.append(next_state.copy())

        return np.array(trace)

class PDEFieldGenerator(DatasetGenerator):
    """Generate PDE field solutions"""

    def __init__(self, equation: str = "wave", grid_size: int = 64, time_steps: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.equation = equation
        self.grid_size = grid_size
        self.time_steps = time_steps

    def _generate_samples(self, n_samples: int) -> List[Dict]:
        samples = []

        for _ in range(n_samples):
            if self.equation == "wave":
                field = self._generate_wave_field()
            elif self.equation == "burgers":
                field = self._generate_burgers_field()
            else:
                field = self._generate_gray_scott_field()

            samples.append({
                'type': 'pde',
                'equation': self.equation,
                'field': field,
                'symmetries': ['se2', 'mobius_complex']
            })

        return samples

    def _generate_wave_field(self) -> np.ndarray:
        """Generate 2D wave equation solution"""
        x = np.linspace(-1, 1, self.grid_size)
        y = np.linspace(-1, 1, self.grid_size)
        X, Y = np.meshgrid(x, y)

        # Initial condition: Gaussian pulse
        field = np.exp(-((X-0.2)**2 + (Y-0.2)**2) / 0.1)

        # Time evolution (simplified)
        for t in range(1, self.time_steps):
            # Simple wave propagation
            field = np.roll(field, 1, axis=0) * 0.99 + np.roll(field, -1, axis=0) * 0.99
            field = np.roll(field, 1, axis=1) * 0.99 + np.roll(field, -1, axis=1) * 0.99

        return field

    def _generate_burgers_field(self) -> np.ndarray:
        """Generate Burgers equation solution"""
        # Simplified Burgers equation solution
        x = np.linspace(-2, 2, self.grid_size)
        y = np.linspace(-2, 2, self.grid_size)
        X, Y = np.meshgrid(x, y)

        # Initial condition
        field = np.exp(-X**2 - Y**2)

        # Simplified evolution
        for t in range(self.time_steps):
            field = field - 0.1 * field * (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0))

        return field

    def _generate_gray_scott_field(self) -> np.ndarray:
        """Generate Gray-Scott reaction-diffusion"""
        # Simplified Gray-Scott
        field = np.random.uniform(0.4, 0.6, (self.grid_size, self.grid_size))

        for t in range(self.time_steps):
            laplacian = (np.roll(field, 1, axis=0) + np.roll(field, -1, axis=0) +
                        np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1) - 4*field)

            reaction = field * (1 - field) * (field - 0.3)

            field += 0.01 * (0.1 * laplacian - reaction)

            field = np.clip(field, 0, 1)

        return field

class SpinLatticeGenerator(DatasetGenerator):
    """Generate spin lattice trajectories"""

    def __init__(self, model: str = "ising_2d", lattice_size: int = 32, steps: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.lattice_size = lattice_size
        self.steps = steps

    def _generate_samples(self, n_samples: int) -> List[Dict]:
        samples = []

        for _ in range(n_samples):
            # Initialize random spin configuration
            if self.model.startswith("ising"):
                spins = np.random.choice([-1, 1], size=(self.lattice_size, self.lattice_size))
            else:  # XY model
                spins = np.random.uniform(0, 2*np.pi, size=(self.lattice_size, self.lattice_size))

            # Evolve spins
            trajectory = self._evolve_spins(spins)

            samples.append({
                'type': 'spin',
                'model': self.model,
                'initial_spins': spins,
                'trajectory': trajectory,
                'symmetries': ['spin_flip', 'lattice_permutations']
            })

        return samples

    def _evolve_spins(self, initial_spins: np.ndarray) -> np.ndarray:
        """Evolve spin system"""
        trajectory = [initial_spins.copy()]

        for step in range(self.steps):
            current = trajectory[-1]

            if self.model == "ising_2d":
                # Metropolis-Hastings for Ising model
                for _ in range(self.lattice_size * self.lattice_size):
                    i, j = np.random.randint(0, self.lattice_size, 2)

                    # Calculate energy change
                    neighbors = [
                        current[(i-1)%self.lattice_size, j],
                        current[(i+1)%self.lattice_size, j],
                        current[i, (j-1)%self.lattice_size],
                        current[i, (j+1)%self.lattice_size]
                    ]

                    delta_E = 2 * current[i,j] * sum(neighbors)

                    # Accept/reject
                    if delta_E <= 0 or np.random.random() < np.exp(-delta_E):
                        current[i,j] *= -1

            trajectory.append(current.copy())

        return np.array(trajectory)

class GraphDynamicsGenerator(DatasetGenerator):
    """Generate graph dynamics (Boolean networks)"""

    def __init__(self, n_nodes: int = 20, connectivity: float = 0.3, steps: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.n_nodes = n_nodes
        self.connectivity = connectivity
        self.steps = steps

    def _generate_samples(self, n_samples: int) -> List[Dict]:
        samples = []

        for _ in range(n_samples):
            # Generate random graph
            graph = self._generate_graph()

            # Generate random Boolean functions
            functions = self._generate_functions()

            # Evolve dynamics
            trajectory = self._evolve_graph(graph, functions)

            samples.append({
                'type': 'graph',
                'graph': graph,
                'functions': functions,
                'trajectory': trajectory,
                'symmetries': ['node_relabeling']
            })

        return samples

    def _generate_graph(self) -> Dict:
        """Generate random graph"""
        nodes = list(range(self.n_nodes))

        # Generate edges
        edges = []
        for i in range(self.n_nodes):
            for j in range(i+1, self.n_nodes):
                if np.random.random() < self.connectivity:
                    edges.append([i, j])

        return {
            'nodes': nodes,
            'edges': edges
        }

    def _generate_functions(self) -> Dict:
        """Generate random Boolean functions for each node"""
        functions = {}

        for node in range(self.n_nodes):
            # Random Boolean function (simplified)
            func_type = np.random.choice(['and', 'or', 'xor', 'majority'])

            # Select 1-3 inputs
            n_inputs = min(3, len([e for e in self.graph['edges'] if e[0] == node or e[1] == node]))
            inputs = np.random.choice(self.n_nodes, n_inputs, replace=False)

            functions[node] = {
                'type': func_type,
                'inputs': inputs.tolist()
            }

        return functions

    def _evolve_graph(self, graph: Dict, functions: Dict) -> np.ndarray:
        """Evolve Boolean network"""
        n_nodes = len(graph['nodes'])
        trajectory = []

        # Initial state
        state = np.random.randint(0, 2, n_nodes)
        trajectory.append(state.copy())

        for step in range(self.steps):
            new_state = np.zeros(n_nodes)

            for node in range(n_nodes):
                func = functions[node]

                if func['type'] == 'and':
                    new_state[node] = np.all(state[func['inputs']])
                elif func['type'] == 'or':
                    new_state[node] = np.any(state[func['inputs']])
                elif func['type'] == 'xor':
                    new_state[node] = np.sum(state[func['inputs']]) % 2
                else:  # majority
                    new_state[node] = np.sum(state[func['inputs']]) > len(func['inputs']) / 2

            trajectory.append(new_state.copy())
            state = new_state

        return np.array(trajectory)

class DomainLoader:
    """Unified interface for loading datasets"""

    def __init__(self):
        self.generators = {
            'quantum': QuantumCircuitGenerator,
            'ca': CellularAutomataGenerator,
            'pde': PDEFieldGenerator,
            'spin': SpinLatticeGenerator,
            'graphs': GraphDynamicsGenerator
        }

    def load_dataset(self, domain: str, n_samples: int, **kwargs) -> Dict[str, List]:
        """Load dataset for specified domain"""

        if domain not in self.generators:
            raise ValueError(f"Unknown domain: {domain}")

        generator_class = self.generators[domain]
        generator = generator_class(**kwargs)

        return generator.generate_dataset(n_samples)

    def load_all_datasets(self, n_samples_per_domain: int = 1000) -> Dict[str, Dict[str, List]]:
        """Load all 5 datasets"""
        datasets = {}

        for domain in ['quantum', 'ca', 'pde', 'spin', 'graphs']:
            print(f"Generating {domain} dataset...")
            datasets[domain] = self.load_dataset(domain, n_samples_per_domain)

        return datasets
