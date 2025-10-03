# Provenance Store

Content-addressed run bundles live under `provenance/<2-hex>/<hash>/`.
Each bundle should at minimum include:
- `run.json` (validated by run.schema.json)
- `tau_trace.json`
- `echo_histogram.png` (optional, large)
- `C_variation.csv`
- `FIRM_audio_signature.wav` (optional, large)
- `golden_snapshot.png` (optional, large)

Large artifacts are ignored by default in .gitignore to keep the repo lean.
