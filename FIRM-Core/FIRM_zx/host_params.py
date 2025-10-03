"""host_params.py

Host-side mirror of WGSL `Params` uniform struct:

  struct Params {
    max_spiders: u32,
    bins_qpi: u32,
    reserved0: u32,
    reserved1: u32,
  };

Validation functions enforce symbolic constraints (e.g., bins_qpi multiple of
2*LCM of denominators). No numeric guessing is performed here.
"""
from __future__ import annotations
from dataclasses import dataclass
import struct


_PARAMS_FMT = "<IIII"
_PARAMS_SIZE = struct.calcsize(_PARAMS_FMT)


@dataclass(frozen=True)
class Params:
    max_spiders: int
    bins_qpi: int
    reserved0: int = 0
    reserved1: int = 0


def validate_params(p: Params) -> Params:
    if p.max_spiders <= 0:
        raise ValueError("max_spiders must be positive")
    if p.bins_qpi <= 0:
        raise ValueError("bins_qpi must be positive and Qπ-consistent")
    return p


def pack_params(p: Params) -> bytes:
    validate_params(p)
    return struct.pack(_PARAMS_FMT, p.max_spiders, p.bins_qpi, p.reserved0, p.reserved1)


def params_record_size_bytes() -> int:
    return _PARAMS_SIZE


