# Boeing E-3 camouflage renderer (Blender)

This repository contains a Blender automation script that applies camouflage textures to the **aircraft body and wings only**, then renders still images for each texture variant.

## What you get

- **CLI**: run Blender in background mode to generate renders
- **Python API**: call functions from inside Blender for custom pipelines
- **Assets**:
  - `Boeing_E3.blend` (scene)
  - `CamoMats/` (input camouflage textures)

## Quickstart (CLI)

From the repo root:

```bash
blender "Boeing_E3.blend" --background --python "render_boeing_camos.py" -- \
  --mats-dir "CamoMats" \
  --limit 10
```

Outputs are written to a timestamped folder such as `CamoMats/Rendered_1530/`.

## Documentation

- **CLI usage**: `docs/CLI.md`
- **Python API**: `docs/API.md`
- **Project components (assets + naming assumptions)**: `docs/Components.md`

## Repository layout

- `render_boeing_camos.py`: Blender automation script (CLI + API)
- `Boeing_E3.blend`: provided scene/model
- `CamoMats/`: camouflage textures (`.png`)
- `docs/`: usage and API documentation

## Contact

MoniGarr - [@monigarr](https://twitter.com/monigarr) - monigarr@monigarr.com

Project Link: `https://github.com/monigarr/be3_rai_m1`
