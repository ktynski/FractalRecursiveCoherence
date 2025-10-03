"""provenance_writer.py

Provenance bundle file writer with hash verification (no network access).

This module writes provenance bundles to the content-addressed file system
with hash verification. All operations are local and deterministic.
"""
from __future__ import annotations
from typing import Dict, Any, Callable
import os
import json
from .provenance import RunLedger, provenance_bundle_path, write_run_json, compute_content_hash


class ProvenanceBundleWriter:
    """Writer for content-addressed provenance bundles with hash verification."""
    
    def __init__(self, root_dir: str, hash_hex_fn: Callable[[bytes], str]):
        """Initialize writer with root directory and hash function.
        
        Args:
            root_dir: Root directory for provenance storage
            hash_hex_fn: Function to compute hex hash from bytes (e.g., BLAKE3)
        """
        self.root_dir = root_dir
        self.hash_hex_fn = hash_hex_fn
        if not callable(hash_hex_fn):
            raise TypeError("hash_hex_fn must be callable")
    
    def validate_bundle_structure(self, bundle_data: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that bundle contains required components.
        
        Args:
            bundle_data: Bundle data to validate
            
        Returns:
            Dict with validation results for each component
        """
        if not isinstance(bundle_data, dict):
            raise ValueError("bundle_data must be a dict")
        
        required_keys = ["run_ledger", "tau_trace", "coherence_variation"]
        optional_keys = ["echo_histogram", "audio_signature", "golden_snapshot"]
        
        validation = {}
        for key in required_keys:
            validation[f"{key}_present"] = key in bundle_data
        
        for key in optional_keys:
            validation[f"{key}_present"] = key in bundle_data
        
        validation["structure_valid"] = all(
            validation[f"{key}_present"] for key in required_keys
        )
        
        return validation
    
    def compute_bundle_hash(self, run_ledger: RunLedger) -> str:
        """Compute content hash for the run ledger.
        
        Args:
            run_ledger: The run ledger to hash
            
        Returns:
            Hex string hash of the serialized ledger
        """
        json_bytes = write_run_json("/dev/null", run_ledger)
        return compute_content_hash(json_bytes, self.hash_hex_fn)
    
    def write_bundle_to_filesystem(self, bundle_data: Dict[str, Any], run_ledger: RunLedger) -> Dict[str, Any]:
        """Write complete bundle to content-addressed filesystem.
        
        Args:
            bundle_data: Complete bundle data
            run_ledger: Run ledger for addressing
            
        Returns:
            Dict with write results and verification info
        """
        import os
        import json
        
        # Validate structure first
        validation = self.validate_bundle_structure(bundle_data)
        if not validation["structure_valid"]:
            raise ValueError("Bundle structure validation failed")
        
        # Compute content hash and path
        bundle_hash = self.compute_bundle_hash(run_ledger)
        bundle_path = provenance_bundle_path(self.root_dir, bundle_hash)
        
        # Create directory structure
        os.makedirs(bundle_path, exist_ok=True)
        
        # Write run.json
        run_json_path = os.path.join(bundle_path, "run.json")
        run_json_bytes = write_run_json("/dev/null", run_ledger)
        with open(run_json_path, "wb") as f:
            f.write(run_json_bytes)
        
        # Write other bundle files
        files_written = ["run.json"]
        
        if "tau_trace" in bundle_data:
            tau_path = os.path.join(bundle_path, "tau_trace.json")
            with open(tau_path, "w") as f:
                json.dump(bundle_data["tau_trace"], f)
            files_written.append("tau_trace.json")
        
        if "coherence_variation" in bundle_data:
            coherence_path = os.path.join(bundle_path, "C_variation.csv")
            with open(coherence_path, "w") as f:
                f.write("tick,coherence\n")
                for i, c in enumerate(bundle_data["coherence_variation"]):
                    f.write(f"{i},{c}\n")
            files_written.append("C_variation.csv")
        
        # Create manifest
        manifest = self.create_bundle_manifest(bundle_data, bundle_hash)
        manifest_path = os.path.join(bundle_path, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        files_written.append("manifest.json")
        
        return {
            "bundle_path": bundle_path,
            "bundle_hash": bundle_hash,
            "files_written": files_written,
            "write_successful": True,
            "validation": validation
        }
    
    def verify_bundle_integrity(self, bundle_path: str, expected_hash: str) -> Dict[str, Any]:
        """Verify integrity of written bundle.
        
        Args:
            bundle_path: Path to bundle directory
            expected_hash: Expected content hash
            
        Returns:
            Dict with integrity verification results
        """
        import os
        import json
        
        if not bundle_path or not expected_hash:
            raise ValueError("bundle_path and expected_hash required")
        
        if not os.path.exists(bundle_path):
            return {"integrity_valid": False, "error": "Bundle path does not exist"}
        
        # Check required files
        required_files = ["run.json", "manifest.json"]
        missing_files = []
        
        for filename in required_files:
            file_path = os.path.join(bundle_path, filename)
            if not os.path.exists(file_path):
                missing_files.append(filename)
        
        if missing_files:
            return {
                "integrity_valid": False,
                "error": f"Missing required files: {missing_files}"
            }
        
        # Verify run.json hash matches expected
        run_json_path = os.path.join(bundle_path, "run.json")
        with open(run_json_path, "rb") as f:
            run_json_bytes = f.read()
        
        computed_hash = compute_content_hash(run_json_bytes, self.hash_hex_fn)
        hash_matches = computed_hash == expected_hash
        
        # Read and validate manifest
        manifest_path = os.path.join(bundle_path, "manifest.json")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        manifest_hash_matches = manifest.get("bundle_hash") == expected_hash
        
        return {
            "integrity_valid": hash_matches and manifest_hash_matches,
            "hash_matches": hash_matches,
            "manifest_hash_matches": manifest_hash_matches,
            "computed_hash": computed_hash,
            "expected_hash": expected_hash,
            "files_verified": required_files
        }
    
    def create_bundle_manifest(self, bundle_data: Dict[str, Any], bundle_hash: str) -> Dict[str, Any]:
        """Create manifest for bundle contents.
        
        Args:
            bundle_data: Bundle data
            bundle_hash: Content hash of bundle
            
        Returns:
            Dict with manifest information
        """
        validation = self.validate_bundle_structure(bundle_data)
        
        manifest = {
            "bundle_hash": bundle_hash,
            "structure_validation": validation,
            "content_types": {},
            "file_count": 0,
            "manifest_version": "1.0"
        }
        
        # Count and categorize files
        for key, value in bundle_data.items():
            if key == "run_ledger":
                manifest["content_types"]["run_json"] = True
                manifest["file_count"] += 1
            elif key in ["tau_trace", "coherence_variation"]:
                manifest["content_types"]["json_data"] = True
                manifest["file_count"] += 1
            elif key in ["echo_histogram", "golden_snapshot"]:
                manifest["content_types"]["image_data"] = True
                manifest["file_count"] += 1
            elif key == "audio_signature":
                manifest["content_types"]["audio_data"] = True
                manifest["file_count"] += 1
        
        return manifest
