"""host_bindings.py

Pure host-side utilities to assemble ZX buffers:
 - Validate and pack Params and Spider arrays into contiguous byte buffers
 - Compute total buffer sizes and offsets

No GPU calls or execution are performed here.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from .host_layout import SpiderPacked, pack_spider, spider_record_size_bytes
from .host_params import Params, pack_params, params_record_size_bytes


@dataclass(frozen=True)
class ZXBuffers:
    params_bytes: bytes
    spiders_bytes: bytes


def build_zx_buffers(params: Params, spiders: List[SpiderPacked]) -> ZXBuffers:
    pb = pack_params(params)
    sb = b"".join(pack_spider(s) for s in spiders)
    return ZXBuffers(params_bytes=pb, spiders_bytes=sb)


def zx_buffer_sizes(num_spiders: int) -> Tuple[int, int]:
    return params_record_size_bytes(), num_spiders * spider_record_size_bytes()


