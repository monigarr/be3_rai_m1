# Python API documentation

`render_boeing_camos.py` can be used as:

- A **CLI script** invoked by Blender (see `docs/CLI.md`)
- A **Python module** imported and called from inside Blender’s Python runtime

Important: this code imports `bpy`, so **it must run inside Blender**.

## Public API surface

The module’s public API is:

- `RenderConfig`
- `setup_scene_camera_sun(...) -> None`
- `ensure_camo_material_nodes(...) -> None`
- `render_camo_variants(...) -> list[str]`
- `main(argv: list[str] | None = None) -> int`

Everything else should be treated as internal.

## `RenderConfig`

A small configuration container used by `main()`:

- `mats_dir: str`: where `.png` textures live
- `output_dir: str`: where rendered `.jpg` files are written
- `limit: int | None`: max renders (use `None` for no limit)
- `sleep_seconds: float`: delay between renders

Also includes scene/model naming defaults that must match the `.blend`:

- `aircraft_object_name` (default: `Boeing_E3`)
- `scene_name` (default: `Scene`)
- `camera_name` (default: `Camera`)
- `body_material_name` (default: `body`)
- `wings_material_name` (default: `wings`)

## `setup_scene_camera_sun(...)`

```python
setup_scene_camera_sun(
    *,
    aircraft_object_name: str = "Boeing_E3",
    scene_name: str = "Scene",
    camera_name: str = "Camera",
) -> None
```

Creates a SUN light and a Camera, assigns the camera to the scene, and attempts to frame the aircraft.

- **Side effects**: modifies the scene, adds objects.
- **Failure modes**: raises if required aircraft object / scene is missing.

### Example

Run in Blender’s Scripting workspace (or from another script run by Blender):

```python
import render_boeing_camos as rbc

rbc.setup_scene_camera_sun()
```

## `ensure_camo_material_nodes(...)`

```python
ensure_camo_material_nodes(
    *,
    body_material_name: str = "body",
    wings_material_name: str = "wings",
    wings_principled_node_name: str = "Principled BSDF.001",
    body_principled_node_name: str = "Principled BSDF",
) -> None
```

Ensures the `body` and `wings` materials are node-based and contain this pipeline:

`Image Texture` → `Bright/Contrast` → `Principled BSDF (Base Color)`

- **Side effects**: creates nodes/links if missing; only touches `body` and `wings`.
- **Failure modes**: raises if the materials don’t exist or no Principled BSDF node can be found.

### Example

```python
import render_boeing_camos as rbc

rbc.ensure_camo_material_nodes(body_material_name="body", wings_material_name="wings")
```

## `render_camo_variants(...)`

```python
render_camo_variants(
    *,
    mats_dir: str,
    output_dir: str,
    limit: int | None = 10,
    sleep_seconds: float = 1.0,
    aircraft_object_name: str = "Boeing_E3",
    body_material_name: str = "body",
    wings_material_name: str = "wings",
) -> list[str]
```

Renders camouflage variants by iterating `.png` files in `mats_dir` and, for each texture:

1. Loads the image into Blender (`bpy.data.images.load(..., check_existing=True)`).
2. Assigns it to the `Image Texture` node of both materials.
3. Renders a still and writes `<basename>_render.jpg` to `output_dir`.

Returns the list of written output paths.

### Minimal example

```python
import render_boeing_camos as rbc

# If you haven't already, set up materials once:
rbc.ensure_camo_material_nodes()

written = rbc.render_camo_variants(
    mats_dir="CamoMats",
    output_dir="CamoMats/Rendered",
    limit=3,
    sleep_seconds=0,
)
print(written)
```

### Example with custom names

If your `.blend` uses different object/material names:

```python
import render_boeing_camos as rbc

rbc.ensure_camo_material_nodes(
    body_material_name="FuselageMat",
    wings_material_name="WingMat",
)

rbc.render_camo_variants(
    mats_dir="/abs/path/to/textures",
    output_dir="/abs/path/to/output",
    limit=None,
    aircraft_object_name="MyPlane",
    body_material_name="FuselageMat",
    wings_material_name="WingMat",
)
```

## `main(argv=None)`

```python
main(argv: list[str] | None = None) -> int
```

Entrypoint used when you run:

```bash
blender Boeing_E3.blend --background --python render_boeing_camos.py -- <script args>
```

If `argv` is `None`, `main()` automatically reads arguments after the `--` separator in `sys.argv`.

### Example (programmatic)

```python
import render_boeing_camos as rbc

exit_code = rbc.main(["--mats-dir", "CamoMats", "--limit", "5", "--sleep-seconds", "0"])
print(exit_code)
```

## Importing inside Blender

If you run from the repo root, Blender’s current working directory is usually the repo root and importing works:

```python
import render_boeing_camos
```

If you need to import via an absolute path:

```python
import sys
sys.path.append("/abs/path/to/repo")
import render_boeing_camos
```

