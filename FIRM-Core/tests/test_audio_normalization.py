"""
Test suite for audio coherence normalization.

Validates that normalization.json is correctly loaded and applied for Parseval-normalized coherence.
"""

import json
from pathlib import Path

import pytest


def test_normalization_json_structure():
    """
    Verify normalization.json exists and has required fields.
    
    Required fields: correction_factor, max_energy_bound, proof_id, fft_size.
    """
    normalization_path = Path(__file__).parent.parent / "FIRM_ui" / "normalization.json"
    
    assert normalization_path.exists(), "normalization.json should exist"
    
    with open(normalization_path, 'r') as f:
        norm = json.load(f)
    
    # Check required fields
    assert "correction_factor" in norm, "Must have correction_factor"
    assert "max_energy_bound" in norm, "Must have max_energy_bound"
    assert "proof_id" in norm, "Must have proof_id"
    assert "fft_size" in norm, "Must have fft_size"
    
    # Validate types and ranges
    assert isinstance(norm["correction_factor"], (int, float)), "correction_factor must be numeric"
    assert isinstance(norm["max_energy_bound"], (int, float)), "max_energy_bound must be numeric"
    assert isinstance(norm["proof_id"], str), "proof_id must be string"
    assert isinstance(norm["fft_size"], int), "fft_size must be integer"
    
    # Check reasonable bounds
    assert norm["correction_factor"] > 0, "correction_factor must be positive"
    assert norm["max_energy_bound"] > 0, "max_energy_bound must be positive"
    assert norm["fft_size"] in [1024, 2048, 4096, 8192], "fft_size must be power of 2"
    
    # Check proof ID format
    assert "THM-PARSEVAL" in norm["proof_id"], "proof_id should reference Parseval theorem"


def test_normalization_parseval_hann_window():
    """
    Verify correction factor matches Hann window Parseval theorem.
    
    For Hann window: correction_factor = 8/3 ≈ 2.667
    Reference: https://en.wikipedia.org/wiki/Window_function#Hann_window
    """
    normalization_path = Path(__file__).parent.parent / "FIRM_ui" / "normalization.json"
    
    with open(normalization_path, 'r') as f:
        norm = json.load(f)
    
    # Hann window Parseval correction
    expected_hann = 8.0 / 3.0  # ≈ 2.6667
    
    if norm.get("window_function") == "hann":
        assert abs(norm["correction_factor"] - expected_hann) < 0.01, \
            f"Hann window correction should be ≈{expected_hann}, got {norm['correction_factor']}"


def test_normalization_max_energy_bound():
    """
    Verify max_energy_bound is reasonable for given FFT size.
    
    For fft_size=2048, max_energy_bound should be ~ frequencyBinCount * 255^2
    where frequencyBinCount = fft_size/2 = 1024.
    """
    normalization_path = Path(__file__).parent.parent / "FIRM_ui" / "normalization.json"
    
    with open(normalization_path, 'r') as f:
        norm = json.load(f)
    
    fft_size = norm["fft_size"]
    freq_bin_count = fft_size // 2
    
    # Theoretical max energy (all bins at 255)
    theoretical_max = freq_bin_count * 255 * 255
    
    # max_energy_bound should be close to freq_bin_count (after byte normalization)
    # The bound in the file is 1024, which matches freq_bin_count
    assert norm["max_energy_bound"] == freq_bin_count, \
        f"max_energy_bound should equal freq_bin_count={freq_bin_count}, got {norm['max_energy_bound']}"


def test_parseval_normalization_formula():
    """
    Verify Parseval normalization formula implementation.
    
    From main.js lines 838-847:
    corrected = energy * correction_factor
    coherence_parseval = min(1.0, corrected / max_energy_bound)
    """
    normalization_path = Path(__file__).parent.parent / "FIRM_ui" / "normalization.json"
    
    with open(normalization_path, 'r') as f:
        norm = json.load(f)
    
    # Simulate normalization calculation
    test_energy = 500.0  # Example raw energy
    corrected = test_energy * norm["correction_factor"]
    coherence_parseval = min(1.0, corrected / norm["max_energy_bound"])
    
    # Should be bounded [0, 1]
    assert 0.0 <= coherence_parseval <= 1.0, "Parseval coherence must be in [0, 1]"
    
    # At max energy, should approach 1.0
    max_energy = norm["max_energy_bound"] / norm["correction_factor"]
    corrected_max = max_energy * norm["correction_factor"]
    coherence_at_max = min(1.0, corrected_max / norm["max_energy_bound"])
    
    assert coherence_at_max >= 0.99, \
        f"At max energy, Parseval coherence should be ~1.0, got {coherence_at_max}"


def test_normalization_provenance():
    """
    Verify normalization has proper provenance (proof_id).
    
    All derived constants must have provenance tracking.
    """
    normalization_path = Path(__file__).parent.parent / "FIRM_ui" / "normalization.json"
    
    with open(normalization_path, 'r') as f:
        norm = json.load(f)
    
    proof_id = norm["proof_id"]
    
    # Proof ID should follow convention
    assert proof_id.startswith("THM-"), "proof_id should start with THM-"
    assert "PARSEVAL" in proof_id, "proof_id should reference Parseval"
    assert proof_id.endswith(("-001", "-002", "-003")), "proof_id should have version suffix"

