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

- **Repo data gotcha:** the bundled `Boeing_E3.blend` has **no `body` material** (its mesh
  uses `dome, engines, glass, landing_gear_door, landing_gears, propeller_cap, propellers,
  tires, wings`). The documented default CLI requires a `body` material and therefore fails with
  `RuntimeError: Required material not found: 'body'`. To run end-to-end against this blend, use
  the documented Python API (see `docs/API.md`) with material names that exist, e.g. `wings`
  (which has node `Principled BSDF.001`) and `engines`:

  ```python
  import render_boeing_camos as rbc
  rbc.setup_scene_camera_sun()
  rbc.ensure_camo_material_nodes(body_material_name="engines", wings_material_name="wings")
  rbc.render_camo_variants(mats_dir="CamoMats", output_dir="CamoMats/Rendered_demo",
                           limit=2, sleep_seconds=0,
                           body_material_name="engines", wings_material_name="wings")
  ```

  Run such a driver with `xvfb-run -a blender "Boeing_E3.blend" --background --python <driver>.py`.

- Renders are saved as **`.png`** (the scene's image format), even though docs/filepaths mention
  `.jpg`. Output defaults to a timestamped folder under `CamoMats/` (e.g. `CamoMats/Rendered_<HHMM>/`).
- `bpy.ops.view3d.camera_to_view_selected()` fails in headless mode (documented in `docs/CLI.md`),
  so the auto-generated camera does not tightly frame the aircraft; renders still succeed.

### Lint / test / build

- No linter, test suite, or build step is configured. For a quick syntax sanity check of the
  script use `python3 -m py_compile render_boeing_camos.py` (note: `import bpy` only resolves
  inside Blender, so the module cannot be imported by the system `python3`).
