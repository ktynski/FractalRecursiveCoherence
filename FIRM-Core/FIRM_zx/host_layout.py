"""host_layout.py

Host-side mirror of WGSL buffer layouts for ZX engine. This module defines
packing/unpacking of spiders exactly matching the WGSL struct:

  struct Spider { phase_numer: u32, phase_denom: u32, kind: u32, deg: u32 };

All packing uses little-endian 32-bit unsigned integers and returns bytes of
length 16 per spider. No floats or padding are introduced.
"""
from __future__ import annotations
from dataclasses import dataclass
import struct
from typing import List


# 4×u32 little-endian
_SPIDER_FMT = "<IIII"
_SPIDER_SIZE = struct.calcsize(_SPIDER_FMT)


@dataclass(frozen=True)
class SpiderPacked:
    phase_numer: int
    phase_denom: int
    kind: int
    deg: int


def pack_spider(sp: SpiderPacked) -> bytes:
    """Pack a Spider into 16 bytes matching WGSL layout exactly.

    All fields must be non-negative and fit into uint32. No coercion is done.
    """
    for name, v in ("phase_numer", sp.phase_numer), ("phase_denom", sp.phase_denom), ("kind", sp.kind), ("deg", sp.deg):
        if not (0 <= int(v) <= 0xFFFFFFFF):
            raise ValueError(f"{name} out of uint32 range")
    return struct.pack(_SPIDER_FMT, sp.phase_numer, sp.phase_denom, sp.kind, sp.deg)


def unpack_spider(b: bytes) -> SpiderPacked:
    """Unpack 16 bytes into a SpiderPacked."""
    if len(b) != _SPIDER_SIZE:
        raise ValueError("invalid spider byte length")
    pn, pd, k, d = struct.unpack(_SPIDER_FMT, b)
    return SpiderPacked(pn, pd, k, d)


def pack_spider_array(arr: List[SpiderPacked]) -> bytes:
    """Pack an array of spiders into a contiguous byte buffer."""
    return b"".join(pack_spider(sp) for sp in arr)


def spider_record_size_bytes() -> int:
    """Return the exact size in bytes per spider record (16)."""
    return _SPIDER_SIZE


