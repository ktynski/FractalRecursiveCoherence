"""blake3_vendor.py

Minimal BLAKE3 implementation or wrapper with dependency injection.

This module provides BLAKE3 hashing with graceful fallback detection.
No silent substitutions are performed per anti-tuning directive.
"""
from __future__ import annotations
from typing import Optional
import hashlib


def try_import_blake3() -> Optional[object]:
    """Attempt to import blake3 package, return None if unavailable."""
    try:
        import blake3
        return blake3
    except ImportError:
        return None


def blake3_hex(data: bytes) -> str:
    """Compute BLAKE3 hex digest with dependency detection.
    
    This function attempts to use the blake3 package if available.
    If not available, it raises NotImplementedError with clear guidance.
    No silent fallback to other hash functions is performed.
    """
    blake3_mod = try_import_blake3()
    if blake3_mod is None:
        raise NotImplementedError(
            "BLAKE3 not available. Install with: pip install blake3\n"
            "Or add blake3 to optional dependencies: pip install -e '.[blake3]'"
        )
    
    hasher = blake3_mod.blake3()
    hasher.update(data)
    return hasher.hexdigest()


def create_test_blake3_function() -> callable:
    """Create a deterministic test hash function for CI/testing.
    
    Returns a function that produces stable hex strings for testing
    without requiring the actual BLAKE3 implementation.
    """
    def test_hash(data: bytes) -> str:
        # Use SHA256 as a deterministic test substitute
        # Prefix with "TEST-" to make it clear this is not real BLAKE3
        sha256_hex = hashlib.sha256(data).hexdigest()
        return f"TEST-{sha256_hex[:32]}"  # Truncate to reasonable length
    
    return test_hash


def get_blake3_function(use_test: bool = False) -> callable:
    """Get BLAKE3 function with test mode option.
    
    Args:
        use_test: If True, return test function; if False, return real BLAKE3
        
    Returns:
        Callable that takes bytes and returns hex string
    """
    if use_test:
        return create_test_blake3_function()
    else:
        return blake3_hex
