# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single Blender automation script (`render_boeing_camos.py`) that applies
camouflage textures to an aircraft's materials and renders stills. The "application" is
**Blender running this script in background mode** — there is no server, no test suite, no
linter config, and no Python package manifest. The only runtime dependency is Blender itself
(it bundles its own Python and `bpy`).

### Environment (already provisioned in the VM snapshot)

- **Blender 3.6.14** is installed at `/opt/blender-3.6.14-linux-x64` and symlinked to
  `/usr/local/bin/blender` (run `blender --version` to confirm).
- Headless OpenGL/EGL libs and `xvfb` are installed so EEVEE can render without a GPU/display.

### Running the renderer (non-obvious caveats)

- The scene (`Boeing_E3.blend`) uses the **EEVEE** render engine, which needs a GL context.
  In this headless VM, running Blender directly **segfaults** with
  `Couldn't open libEGL.so.1` / core dump. **Always wrap the command in `xvfb-run -a`:**

  ```bash
  xvfb-run -a blender "Boeing_E3.blend" --background --python "render_boeing_camos.py" -- --limit 2 --sleep-seconds 0
  ```

- **Repo data gotcha (`body` material):** the bundled `Boeing_E3.blend` has **no separate
  `body` material**. A material-ID render shows the `wings` material actually covers the
  **fuselage body + wings + tail**, while `engines` covers the 4 engine nacelles (its mesh
  materials are `dome, engines, glass, landing_gear_door, landing_gears, propeller_cap,
  propellers, tires, wings`). The repo test renders from 2022 imply the blend once had a
  separate `body` material that was later merged into `wings`.
  - `render_boeing_camos.py` (on disk) **tolerates this**: it skips configured camo materials
    that don't exist (printing `Skipping missing material: 'body'`) and only errors if *none*
    exist. The documented default CLI therefore works and applies the camo via `wings`.
  - There is also an **older copy of the script embedded inside `Boeing_E3.blend`** (a Blender
    Text datablock named `render_boeing_camos`). It still hard-codes `materials["body"]` and so
    fails with `KeyError: ... key "body" not found` when run from Blender's Text Editor. Prefer
    the on-disk script. The blend is saved in Blender 3.4 format (`BLENDER-v304`); re-saving it
    with the VM's Blender 3.6 would bump the format and create a large binary diff, so the
    embedded copy is intentionally left untouched.

- Renders are saved as **`.png`** (the scene's image format), even though docs/filepaths mention
  `.jpg`. Output defaults to a timestamped folder under `CamoMats/` (e.g. `CamoMats/Rendered_<HHMM>/`).
- `bpy.ops.view3d.camera_to_view_selected()` fails in headless mode (documented in `docs/CLI.md`),
  so the auto-generated camera does not tightly frame the aircraft; renders still succeed.

### Lint / test / build

- No linter, test suite, or build step is configured. For a quick syntax sanity check of the
  script use `python3 -m py_compile render_boeing_camos.py` (note: `import bpy` only resolves
  inside Blender, so the module cannot be imported by the system `python3`).
