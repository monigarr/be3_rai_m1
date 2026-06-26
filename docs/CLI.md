# Command-line usage

This project is intended to be run via **Blender in background mode** with `--python`.

## Requirements

- **Blender**: a version that ships with Python 3.10+ (Blender 3.4+ is fine).
- **Repository assets present**:
  - `Boeing_E3.blend` (scene file)
  - `CamoMats/` (directory of `.png` camouflage textures)

## Quickstart

Run from the repo root (recommended so relative paths resolve):

```bash
blender "Boeing_E3.blend" --background --python "render_boeing_camos.py" -- \
  --mats-dir "CamoMats" \
  --limit 10
```

By default, renders are written to a timestamped folder inside `CamoMats/`, e.g. `CamoMats/Rendered_1530/`.

## Syntax

Blender consumes its own arguments first. **Everything after `--` is passed to the script**:

```bash
blender <scene.blend> [blender-args...] --python render_boeing_camos.py -- [script-args...]
```

## Options

- `--mats-dir <path>`
  - Directory containing input `.png` camouflage textures.
  - Default: `CamoMats`
- `--output-dir <path>`
  - Directory to write output `.jpg` renders.
  - Default: `CamoMats/Rendered_<HHMM>/` (under `--mats-dir`)
- `--limit <int>`
  - Maximum number of renders to produce.
  - Default: `10`
  - Use `0` to render **all** `.png` files found in `--mats-dir`.
- `--sleep-seconds <float>`
  - Optional delay between renders.
  - Default: `1.0`

## Examples

Render all textures into a stable output folder:

```bash
blender "Boeing_E3.blend" --background --python "render_boeing_camos.py" -- \
  --mats-dir "CamoMats" \
  --output-dir "BoeingRenders" \
  --limit 0 \
  --sleep-seconds 0
```

Render just 3 variants for a quick smoke test:

```bash
blender "Boeing_E3.blend" --background --python "render_boeing_camos.py" -- \
  --limit 3
```

## Output

- Output format: `.jpg`
- Output naming: `<texture_basename>_render.jpg`
  - Example: `CamoMats/red_camo.png` → `CamoMats/Rendered_1530/red_camo_render.jpg`

## Exit codes

- `0`: success
- non-zero: an error occurred (e.g. missing objects/materials in the `.blend`, invalid paths)

## Troubleshooting

### “Required object not found”

The script expects the aircraft object `Boeing_E3` (and `Scene`) to exist in the loaded
`.blend`. If your `.blend` uses different names, call the Python API with custom names
(see `docs/API.md`).

### Materials (`body` / `wings`)

The script applies the camouflage to the `body` and `wings` materials. Any of these material
names that are **not present** in the loaded `.blend` are skipped with a notice such as:

```
[render_boeing_camos] Skipping missing material: 'body'
```

The bundled `Boeing_E3.blend` shares a **single `wings` material for the fuselage body and the
wings** (it has no separate `body` material), so a normal run prints the notice above and applies
the camo via `wings` only. A `RuntimeError` is raised only if **none** of the configured camo
materials exist.

> Note: if you run the copy of this script that is saved *inside* `Boeing_E3.blend`
> (Blender's Text Editor), use the on-disk `render_boeing_camos.py` instead — the embedded
> copy is older and assumes a separate `body` material exists, so it fails with
> `KeyError: ... key "body" not found`.

### Camera framing doesn’t work in headless mode

`bpy.ops.view3d.camera_to_view_selected()` can fail depending on Blender context. The script tolerates this and will still render, but the framing may not match expectations. If you need deterministic framing, set camera transforms explicitly in a custom script that calls the API.

