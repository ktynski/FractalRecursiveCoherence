# FIRM_zx

GPU-first ZX tensor network engine. WGSL primary target with WebGL2 fallback.
This directory contains shader sources and (later) host bindings.

- Phases: Qπ domain (π-rational)
- Rules: canonical ZX fusion + conditional color flips
- Feedback: J multipliers derived from coherence functional curvature

## Host-side layout (mirrored in Python)

WGSL Spider struct:

```
struct Spider { phase_numer: u32, phase_denom: u32, kind: u32, deg: u32 };
```

Packing is 4×u32 = 16 bytes per spider. Host-side pack/unpack must match this
exact layout without padding differences.
