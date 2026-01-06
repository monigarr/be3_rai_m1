# Project components

This repo is best understood as a small pipeline with a few concrete “components”:

## Scene component: `Boeing_E3.blend`

- **Role**: the Blender scene containing the aircraft model, materials, and render settings.
- **Required names (defaults)**:
  - **Object**: `Boeing_E3`
  - **Scene**: `Scene`
  - **Materials to modify**: `body`, `wings`
- **Not modified**: the script only touches the `body` and `wings` materials by design (e.g., it will not change the dome).

If you rename these in Blender, you must call the Python API with matching names (see `docs/API.md`).

## Other `.blend` files

- `eczemaDemo1.blend` / `eczemaDemo1.blend1` appear to be unrelated working files/backups and are not used by the camouflage rendering workflow.

## Texture dataset component: `CamoMats/`

- **Role**: input camouflage textures.
- **Format**: `.png`
- **Selection**: all `.png` files in the directory (sorted by filename), optionally limited by `--limit`.

## Script component: `render_boeing_camos.py`

- **Role**: automation that:
  - ensures the `body` and `wings` materials are node-based and accept an image texture
  - creates a camera and a sun light
  - iterates textures and renders stills to disk
- **Interfaces**:
  - CLI invocation from Blender (see `docs/CLI.md`)
  - Python API for custom pipelines (see `docs/API.md`)

## Output component: rendered `.jpg` stills

- **Default output location**: `CamoMats/Rendered_<HHMM>/`
- **File naming**: `<texture_basename>_render.jpg`

You can override output with `--output-dir`.

