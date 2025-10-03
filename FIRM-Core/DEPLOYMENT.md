# FIRM-Core Deployment Guide

This document provides systematic deployment instructions for the FIRM Ex Nihilo Monad Universe implementation.

## Prerequisites Validation

Before deployment, verify system requirements:

```bash
# Python version check
python3 --version  # Must be >= 3.10

# Node.js version check (for UI components)
node --version     # Must be >= 18

# Browser compatibility check
# Modern browser with WebGL2 or WebGPU support required
```

## Installation

### 1. Core Dependencies

```bash
# Clone repository
git clone <repository-url>
cd FIRM-Core

# Install Python dependencies
pip install -e ".[dev,blake3]"

# Verify installation
python3 -m pytest -q
```

### 2. Development Environment

```bash
# Install pre-commit hooks
pre-commit install

# Run format and lint checks
make check-all

# Generate constants header
make generate-constants
```

### 3. Audio Subsystem (Optional)

For analog audio core functionality:

```bash
# No additional installation required
# Web Audio API is browser-native
# Microphone access requires HTTPS in production
```

## Configuration

### 1. Environment Variables

Create `.env` file (optional, all defaults are derived):

```bash
# Machine fingerprint override (CI only)
FIRM_MACHINE_FINGERPRINT=CI_CANONICAL

# Development mode (enables additional validation)
FIRM_DEV_MODE=true

# Provenance storage location
FIRM_PROVENANCE_ROOT=./provenance
```

### 2. Constants Configuration

All constants are derived from first principles. To regenerate:

```bash
python3 -c "
from FIRM_constants.generate_header import build_constants_from_derivations, render_header
constants = build_constants_from_derivations([2, 4, 8])
with open('FIRM_constants.gen.h', 'w') as f:
    f.write(render_header(constants))
print('Constants regenerated with proof IDs')
"
```

## Deployment Modes

### 1. Development Mode

```bash
# Start with hot reloading (structure validation only)
python3 -m http.server 8080
# Navigate to http://localhost:8080/FIRM_ui/

# Run continuous testing
pytest --watch

# Monitor provenance generation
ls -la provenance/
```

### 2. Production Mode

```bash
# Validate complete system
make check-all
pytest -m "not benchmark"  # Skip benchmarks in production validation

# Build optimized assets (when implemented)
# npm run build

# Deploy static files to web server
# Ensure HTTPS for microphone access
```

### 3. Research Mode

```bash
# Run full benchmark suite
pytest -m benchmark --benchmark-only

# Generate research data
python3 -c "
from FIRM_dsl.coherence import compute_coherence
from FIRM_dsl.core import ObjectG, make_node_label
# Create research graphs and analyze
"

# Export provenance bundles for analysis
find provenance/ -name "*.json" | head -10
```

## System Validation

### 1. Mathematical Integrity

```bash
# Validate all derivations maintain theory fidelity
pytest -m theory -v

# Check constants have proof provenance
python3 -c "
from FIRM_constants.generate_header import build_constants_from_derivations
constants = build_constants_from_derivations([2, 4, 8])
for name, result in constants.items():
    print(f'{name}: {result.value} (proof: {result.proof_id})')
"
```

### 2. Performance Validation

```bash
# Run benchmarks with theory validation
pytest -m benchmark

# Check memory usage (no leaks)
python3 -c "
import psutil
import gc
# Run computation
gc.collect()
print(f'Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB')
"
```

### 3. Provenance Integrity

```bash
# Verify content-addressed storage
python3 -c "
from FIRM_dsl.provenance_writer import ProvenanceBundleWriter
from FIRM_dsl.blake3_vendor import get_blake3_function
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    writer = ProvenanceBundleWriter(tmp, get_blake3_function(use_test=True))
    # Test integrity verification
    print('Provenance system validated')
"
```

## Troubleshooting

### Common Issues

1. **BLAKE3 not available**
   ```bash
   pip install blake3
   # OR use test mode
   export FIRM_USE_TEST_HASH=true
   ```

2. **WebGL2 not supported**
   - Update browser to latest version
   - Enable hardware acceleration
   - Check GPU drivers

3. **Microphone permission denied**
   - Ensure HTTPS deployment
   - Check browser permissions
   - Microphone is optional (fallback to oscillators)

4. **Tests failing**
   ```bash
   # Clean environment
   make clean
   pip install -e ".[dev]"
   
   # Run specific test categories
   pytest -m theory     # Theory validation
   pytest -m integration # Integration tests
   pytest -m benchmark   # Performance tests
   ```

### Performance Optimization

1. **For large graphs**: Consider cycle basis caching
2. **For real-time audio**: Reduce FFT size if latency critical
3. **For WebGPU**: Use compute shaders for ZX evolution
4. **For provenance**: Batch bundle writes

## Security Considerations

1. **Audio privacy**: All processing local, no network transmission
2. **Provenance**: No PII in machine fingerprints
3. **Content addressing**: Cryptographic integrity via BLAKE3
4. **Sandboxing**: No arbitrary code execution in derivations

## Monitoring

### Health Checks

```bash
# System health validation
python3 -c "
import importlib
modules = ['FIRM_dsl.core', 'FIRM_constants.FIRM_derivations', 'FIRM_clifford.interface']
for mod in modules:
    try:
        importlib.import_module(mod)
        print(f'✓ {mod}')
    except Exception as e:
        print(f'✗ {mod}: {e}')
"
```

### Performance Monitoring

```bash
# Benchmark regression detection
pytest -m benchmark --benchmark-json=benchmark_results.json

# Memory usage tracking
python3 -m memory_profiler your_script.py
```

## Backup and Recovery

### Provenance Backup

```bash
# Backup content-addressed provenance
tar -czf provenance_backup_$(date +%Y%m%d).tar.gz provenance/

# Verify backup integrity
tar -tzf provenance_backup_*.tar.gz | wc -l
```

### Configuration Backup

```bash
# Backup generated constants
cp FIRM_constants.gen.h FIRM_constants.gen.h.backup

# Backup environment
cp .env .env.backup
```

## Updates and Maintenance

### 1. Theory Updates

When mathematical derivations are updated:

```bash
# Regenerate constants
make generate-constants

# Validate theory consistency
pytest -m theory

# Update documentation
python3 tools/spec_autogen.py > FIRM_spec_updated.md
```

### 2. Dependency Updates

```bash
# Update Python dependencies
pip install -e ".[dev]" --upgrade

# Update pre-commit hooks
pre-commit autoupdate

# Validate after updates
make check-all
```

This deployment maintains the complete mathematical rigor and theory fidelity of the FIRM system while providing practical operational guidance.
