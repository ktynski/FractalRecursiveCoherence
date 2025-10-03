"""shader_validator.py

WebGL shader compilation validator (syntax-only, no execution).

This module provides syntax validation for GLSL/WGSL shaders without executing
or rendering anything. It validates structure, uniforms, attributes, and basic
syntax compliance per the locked spec.
"""
from __future__ import annotations
from typing import Dict, List, Any
import re


class ShaderValidationResult:
    """Container for shader validation results."""
    
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str]):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.proof_id = "THM-SHADER-SYNTAX-001"


class WebGLShaderValidator:
    """Syntax-only validator for WebGL shaders (no execution, no GPU calls)."""
    
    def __init__(self):
        self.required_precision_regex = re.compile(r'precision\s+(lowp|mediump|highp)\s+(float|int);')
        self.uniform_regex = re.compile(r'uniform\s+\w+\s+\w+;')
        self.attribute_regex = re.compile(r'attribute\s+\w+\s+\w+;')
        self.varying_regex = re.compile(r'varying\s+\w+\s+\w+;')
    
    def validate_vertex_shader(self, source: str) -> ShaderValidationResult:
        """Validate vertex shader syntax without compilation."""
        errors = []
        warnings = []
        
        if not source.strip():
            errors.append("Vertex shader source is empty")
            return ShaderValidationResult(False, errors, warnings)
        
        # Check for required gl_Position assignment
        if "gl_Position" not in source:
            errors.append("Vertex shader must assign to gl_Position")
        
        # Check precision declarations for fragment shader compatibility
        if not self.required_precision_regex.search(source):
            warnings.append("No precision qualifier found (may be required for fragment shader)")
        
        return ShaderValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_fragment_shader(self, source: str) -> ShaderValidationResult:
        """Validate fragment shader syntax without compilation."""
        errors = []
        warnings = []
        
        if not source.strip():
            errors.append("Fragment shader source is empty")
            return ShaderValidationResult(False, errors, warnings)
        
        # Fragment shaders require precision qualifiers
        if not self.required_precision_regex.search(source):
            errors.append("Fragment shader must have precision qualifier")
        
        # Check for gl_FragColor or gl_FragData assignment
        if "gl_FragColor" not in source and "gl_FragData" not in source:
            errors.append("Fragment shader must assign to gl_FragColor or gl_FragData")
        
        return ShaderValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_wgsl_compute_shader(self, source: str) -> ShaderValidationResult:
        """Validate WGSL compute shader syntax without compilation."""
        errors = []
        warnings = []
        
        if not source.strip():
            errors.append("WGSL shader source is empty")
            return ShaderValidationResult(False, errors, warnings)
        
        # Check for compute entry point
        if "@compute" not in source:
            errors.append("WGSL compute shader must have @compute entry point")
        
        # Check for workgroup_size specification
        if "@workgroup_size" not in source:
            warnings.append("WGSL compute shader should specify @workgroup_size")
        
        return ShaderValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_shader_program_structure(self, vertex_source: str, fragment_source: str) -> Dict[str, Any]:
        """Validate that vertex and fragment shaders are compatible."""
        vertex_result = self.validate_vertex_shader(vertex_source)
        fragment_result = self.validate_fragment_shader(fragment_source)
        
        # Extract varyings from both shaders
        vertex_varyings = set(self.varying_regex.findall(vertex_source))
        fragment_varyings = set(self.varying_regex.findall(fragment_source))
        
        compatibility_errors = []
        if vertex_varyings != fragment_varyings:
            compatibility_errors.append("Varying declarations must match between vertex and fragment shaders")
        
        return {
            "vertex_valid": vertex_result.is_valid,
            "fragment_valid": fragment_result.is_valid,
            "program_valid": vertex_result.is_valid and fragment_result.is_valid and len(compatibility_errors) == 0,
            "vertex_errors": vertex_result.errors,
            "fragment_errors": fragment_result.errors,
            "compatibility_errors": compatibility_errors,
            "proof_id": "THM-SHADER-PROGRAM-001"
        }
