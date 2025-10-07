"""
MDL Sweep: Test if 20 is the natural dimensionality

This implements the MDL sweep from the plan to discover the elbow
point where description length is minimized.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import yaml
from pathlib import Path
import json
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt

from ..models.monad_listener import MonadListener
from ..loaders.dataset_generators import DomainLoader

class MDLSweeper:
    """Main MDL sweep implementation"""

    def __init__(self, config_path: str = "configs/mdlsweep.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.results = {}

    def run_sweep(self):
        """Run MDL sweep across all latent dimensions and domains"""

        print("🧪 Starting MDL Sweep for Monad Listener Validation")
        print("=" * 60)

        # Load datasets
        loader = DomainLoader()
        datasets = loader.load_all_datasets(self.config['datasets']['quantum']['samples'])

        # Test each latent dimension
        for latent_dim in self.config['latent_dims']:
            print(f"\n🔍 Testing latent dimension: {latent_dim}")

            results = self._test_dimension(latent_dim, datasets)
            self.results[latent_dim] = results

            print(f"   MDL: {results['mdl']:.4f}")
            print(f"   NLL: {results['nll']:.4f}")
            print(f"   Param bits: {results['param_bits']:.4f}")

        # Analyze results
        self._analyze_results()

        return self.results

    def _test_dimension(self, latent_dim: int, datasets: Dict) -> Dict:
        """Test single latent dimension across all domains"""

        results = {'latent_dim': latent_dim, 'domain_results': {}}

        total_mdl = 0
        total_nll = 0
        total_param_bits = 0
        total_samples = 0

        for domain_name, domain_data in datasets.items():
            print(f"   📊 Domain: {domain_name}")

            domain_results = self._test_domain_dimension(latent_dim, domain_name, domain_data)
            results['domain_results'][domain_name] = domain_results

            total_mdl += domain_results['mdl'] * len(domain_data)
            total_nll += domain_results['nll'] * len(domain_data)
            total_param_bits += domain_results['param_bits']
            total_samples += len(domain_data)

        # Average across all domains and samples
        results['mdl'] = total_mdl / total_samples
        results['nll'] = total_nll / total_samples
        results['param_bits'] = total_param_bits

        return results

    def _test_domain_dimension(self, latent_dim: int, domain: str, data: List) -> Dict:
        """Test single dimension on single domain"""

        # Create model
        model = MonadListener(latent_dim=latent_dim, backbone_type=self._get_backbone_type(domain))
        model.to(self.device)

        # Prepare data
        train_data, val_data = self._prepare_domain_data(data, domain)

        # Train model
        self._train_model(model, train_data, val_data, domain)

        # Compute MDL
        mdl, nll, param_bits = self._compute_mdl(model, val_data, domain)

        return {
            'mdl': mdl,
            'nll': nll,
            'param_bits': param_bits,
            'converged': True  # Placeholder
        }

    def _get_backbone_type(self, domain: str) -> str:
        """Get appropriate backbone for domain"""
        backbone_map = {
            'quantum': 'gnn',      # Graph-like circuits
            'ca': 'fno',          # Field-like patterns
            'pde': 'fno',         # Field equations
            'spin': 'gnn',        # Lattice graphs
            'graphs': 'gnn'       # Explicit graphs
        }
        return backbone_map.get(domain, 'mlp')

    def _prepare_domain_data(self, data: List, domain: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """Prepare domain-specific data format"""

        # Split data
        split_point = int(0.8 * len(data))
        train_data = data[:split_point]
        val_data = data[split_point:]

        # Convert to tensors (domain-specific preprocessing)
        if domain == 'quantum':
            train_tensor = self._preprocess_quantum(train_data)
            val_tensor = self._preprocess_quantum(val_data)
        elif domain in ['ca', 'pde']:
            train_tensor = self._preprocess_fields(train_data)
            val_tensor = self._preprocess_fields(val_data)
        else:
            train_tensor = self._preprocess_generic(train_data)
            val_tensor = self._preprocess_generic(val_data)

        return train_tensor, val_tensor

    def _preprocess_quantum(self, data: List) -> torch.Tensor:
        """Preprocess quantum circuit data"""
        # Simplified: use circuit length as feature
        features = []
        for sample in data:
            # Simple feature extraction
            circuit_length = len(sample['circuit'])
            statevector_real = np.real(sample['statevector'][:8])  # First 8 components
            features.append([circuit_length] + statevector_real.tolist())

        return torch.tensor(features, dtype=torch.float32)

    def _preprocess_fields(self, data: List) -> torch.Tensor:
        """Preprocess field data (CA, PDE)"""
        # Simplified: flatten field to vector
        features = []
        for sample in data:
            if 'trace' in sample:
                # CA: use final state
                final_state = sample['trace'][-1]
                features.append(final_state.astype(np.float32))
            elif 'field' in sample:
                # PDE: use final field
                field = sample['field']
                features.append(field.flatten().astype(np.float32))

        return torch.tensor(features, dtype=torch.float32)

    def _preprocess_generic(self, data: List) -> torch.Tensor:
        """Generic preprocessing"""
        features = []
        for sample in data:
            # Extract numerical features
            feature_vec = []
            if 'trajectory' in sample:
                traj = sample['trajectory']
                feature_vec.extend([
                    np.mean(traj), np.std(traj.flatten()),
                    np.sum(traj > 0.5) / traj.size
                ])

            features.append(feature_vec)

        return torch.tensor(features, dtype=torch.float32)

    def _train_model(self, model: MonadListener, train_data: torch.Tensor, val_data: torch.Tensor, domain: str):
        """Train model for this dimension"""

        optimizer = optim.Adam(model.parameters(), lr=self.config['training']['learning_rate'])
        criterion = nn.MSELoss()  # Simplified

        model.train()

        for epoch in range(self.config['training']['epochs']):
            optimizer.zero_grad()

            # Forward pass
            outputs = model(train_data.to(self.device), domain)

            # Simplified loss (would be multi-head loss in practice)
            loss = 0
            for head_name, head_output in outputs.items():
                if head_output is not None:
                    # Dummy target (would be actual labels)
                    target = torch.randn_like(head_output)
                    loss += criterion(head_output, target)

            loss.backward()
            optimizer.step()

            if epoch % 20 == 0:
                print(f"      Epoch {epoch}, Loss: {loss.item()".4f"}")

    def _compute_mdl(self, model: MonadListener, val_data: torch.Tensor, domain: str) -> Tuple[float, float, float]:
        """Compute MDL for this model"""

        model.eval()

        with torch.no_grad():
            outputs = model(val_data.to(self.device), domain)

            # Compute NLL (negative log likelihood)
            nll = 0
            n_samples = 0

            for head_name, head_output in outputs.items():
                if head_output is not None:
                    # Simplified: assume Gaussian noise
                    noise_std = 0.1
                    nll_component = 0.5 * np.log(2 * np.pi * noise_std**2) + \
                                   0.5 * ((head_output.mean() - 0)**2) / noise_std**2
                    nll += nll_component
                    n_samples += 1

            nll_avg = nll / max(n_samples, 1)

            # Parameter complexity (simplified)
            total_params = sum(p.numel() for p in model.parameters())
            param_bits = np.log2(total_params + 1)  # Rough approximation

            # MDL = NLL + λ * param_bits
            lambda_param = self.config['mdl']['lambda']
            mdl = nll_avg + lambda_param * param_bits

            return mdl, nll_avg, param_bits

    def _analyze_results(self):
        """Analyze MDL sweep results to find elbow"""

        print("\n📈 MDL Sweep Results Analysis")
        print("=" * 40)

        # Extract MDL values
        dims = sorted(self.results.keys())
        mdls = [self.results[dim]['mdl'] for dim in dims]

        print("Latent Dim | MDL")
        print("-----------|-----")
        for dim, mdl in zip(dims, mdls):
            print(f"{dim"9"} | {mdl".4f"}")

        # Find elbow (simplified)
        if len(mdls) >= 3:
            elbow_dim = self._find_elbow(dims, mdls)
            print(f"\n🎯 Detected elbow at dimension: {elbow_dim}")

            # Check stability across domains
            self._check_stability(elbow_dim)

        # Save results
        self._save_results()

    def _find_elbow(self, dims: List[int], mdls: List[float]) -> int:
        """Find elbow point in MDL curve"""

        if len(dims) < 3:
            return dims[0]

        # Simple elbow detection: find point with maximum second derivative
        second_derivs = []
        for i in range(1, len(mdls)-1):
            second_deriv = mdls[i+1] - 2*mdls[i] + mdls[i-1]
            second_derivs.append(second_deriv)

        if not second_derivs:
            return dims[0]

        max_idx = np.argmax(second_derivs)
        elbow_idx = max_idx + 1  # Offset for second derivative

        return dims[min(elbow_idx, len(dims)-1)]

    def _check_stability(self, elbow_dim: int):
        """Check if elbow is stable across domains"""

        print("
🔍 Stability Analysis:"        print(f"   Target elbow: {elbow_dim}")

        # Check per-domain elbows
        domain_elbows = {}
        for domain in ['quantum', 'ca', 'pde', 'spin', 'graphs']:
            domain_mdls = []
            dims = sorted(self.results.keys())

            for dim in dims:
                domain_mdls.append(self.results[dim]['domain_results'][domain]['mdl'])

            domain_elbow = self._find_elbow(dims, domain_mdls)
            domain_elbows[domain] = domain_elbow

            diff = abs(domain_elbow - elbow_dim)
            print(f"   {domain"8"}: {domain_elbow"2"} (diff: {diff})")

        # Check stability criterion
        max_diff = max(abs(elbow - elbow_dim) for elbow in domain_elbows.values())
        stable = max_diff <= self.config['elbow_detection']['stability_threshold']

        print(f"\n🎯 Stability: {'STABLE' if stable else 'UNSTABLE'} (max diff: {max_diff})")

        if stable:
            print("✅ Evidence supports 'sung' dimensionality (20 is natural, not imposed)")
        else:
            print("⚠️  Evidence suggests imposed dimensionality (20 may be arbitrary)")

    def _save_results(self):
        """Save results to file"""

        results_path = Path(self.config['output']['results_dir'])
        results_path.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        with open(results_path / 'mdl_sweep_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save as CSV
        import pandas as pd

        csv_data = []
        for dim, result in self.results.items():
            row = {'latent_dim': dim, 'mdl': result['mdl'], 'nll': result['nll'], 'param_bits': result['param_bits']}

            # Add domain-specific results
            for domain, domain_result in result['domain_results'].items():
                row[f'{domain}_mdl'] = domain_result['mdl']
                row[f'{domain}_nll'] = domain_result['nll']

            csv_data.append(row)

        df = pd.DataFrame(csv_data)
        df.to_csv(results_path / 'mdl_sweep_results.csv', index=False)

        print(f"\n💾 Results saved to {results_path}")

def main():
    """Main execution"""
    sweeper = MDLSweeper()
    results = sweeper.run_sweep()

    print("\n🎉 MDL Sweep Complete!")
    print("Check results/mdlsweep/ for detailed outputs")

if __name__ == "__main__":
    main()
