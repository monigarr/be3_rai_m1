"""
Render Boeing E-3 camouflage variants in Blender.

This script is designed to be run *inside Blender* (i.e. with access to `bpy`).
It loads camouflage textures from `CamoMats/`, applies them to the aircraft's
`body` and `wings` materials, and writes still renders to disk.

## CLI usage (recommended)

From the repository root (same folder as `Boeing_E3.blend`):

    blender "Boeing_E3.blend" --background --python "render_boeing_camos.py" -- \\
      --mats-dir "CamoMats" \\
      --output-dir "CamoMats/Rendered" \\
      --limit 10

Notes:
- Arguments after `--` are passed to this script (Blender consumes earlier args).
- Output images are written as `.jpg` files.

## Public API

- `main(argv: list[str] | None = None) -> int`
- `render_camo_variants(...) -> list[str]`
- `setup_scene_camera_sun(...) -> None`
- `ensure_camo_material_nodes(...) -> None`

See `docs/API.md` for detailed API documentation and examples.
"""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

import bpy

#-------------------------------------------------------------------------------------------
#
#   Interview Test for Technical Artist
#
#   MoniGarr,  monigarr@MoniGarr.com,  MoniGarr.com
#
#
#   (i) Use “blender Boeing_E3.blend --background --python scriptname.py” from the command line to call the script.
#
#   (ii) The script will open the Blender file provided and make modifications to the aircraft.
#
#   (ii) Modify the node-based Shader Editor via script to change the paint job of the body of the aircraft to give 
#           the plane a camouflage. Only modify the body and wing materials, 
#           do not modify the dome or other aircraft materials.
#
#   (iii) Create a camera and a sun object in the script and apply the appropriate settings.
#
#   (iv) Generate 10 renders of the aircraft, each with a new color and pattern of camouflage. 
#
#
#	PC WorkStation:
#		Omniverse Launcher
#		Blender 3.4.0-usd.101.0
#		msi gtx 1660, windows 10
#		Disco Diffusion
#
#-------------------------------------------------------------------------------------------
#	Camo Mats generated with Disco Diffusion:
#	https://colab.research.google.com/drive/14gt9Z1wqQRS8jVfzJA1K9_PAYlXUAFrR?usp=sharing
#
#	Disco Diffusion Prompts:
#	  seed = 48
#	  prompt = "High resolution photograph of red camouflage fabric"
# 	 strength = 0.50
#	  red / white / black / green / tan / blue/ ice / water / snow / mountain / forest / city 
#	  sandy beach / rocky beach / blue sky / cloudy sky / ...
#
#	References: docs that helped me figure this out.
#		https://blenderartists.org/t/save-render-result-as-a-specific-path-name/650566
#		https://blender.stackexchange.com/questions/245973/is-it-possible-to-get-the-current-time-in-blender
#		https://stackoverflow.com/questions/69514207/how-to-set-a-shader-node-property-for-blender-material-via-python-script
#		https://stackoverflow.com/questions/13955176/file-paths-in-python-in-the-form-of-string-throw-errors
#		https://behreajj.medium.com/coding-blender-materials-with-nodes-python-66d950c0bc02
#		https://docs.blender.org/manual/en/latest/addons/import_export/node_shaders_info.html
#		https://blender.stackexchange.com/questions/240278/how-to-access-shader-node-via-python-script
#		https://tabreturn.github.io/code/blender/python/2020/06/06/a_quick_intro_to_blender_creative_coding-part_1_of_3.html
#
#
#--------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class RenderConfig:
    """Configuration for rendering camouflage variants."""

    mats_dir: str
    output_dir: str
    limit: Optional[int] = 10
    sleep_seconds: float = 1.0

    # Scene/model identifiers (must match the provided .blend).
    aircraft_object_name: str = "Boeing_E3"
    scene_name: str = "Scene"
    camera_name: str = "Camera"

    # Materials to modify (only these are modified).
    body_material_name: str = "body"
    wings_material_name: str = "wings"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _iter_png_files(directory: str) -> Iterable[str]:
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith(".png"):
            yield os.path.join(directory, filename)


def _require_object(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required object not found: {name!r}")
    return obj


def _require_scene(name: str) -> bpy.types.Scene:
    scene = bpy.data.scenes.get(name)
    if scene is None:
        raise RuntimeError(f"Required scene not found: {name!r}")
    return scene


def setup_scene_camera_sun(
    *,
    aircraft_object_name: str = "Boeing_E3",
    scene_name: str = "Scene",
    camera_name: str = "Camera",
) -> None:
    """
    Ensure a camera and sun exist and frame the aircraft.

    This mirrors the original assessment script behavior:
    - selects the aircraft
    - adds a SUN light
    - adds a camera and sets it as the active scene camera
    - frames the camera to the selected aircraft
    """
    aircraft = _require_object(aircraft_object_name)
    scene = _require_scene(scene_name)

    # Select aircraft for framing.
    aircraft.select_set(True)

    bpy.ops.object.light_add(type="SUN")
    bpy.ops.object.camera_add()

    cam = bpy.data.objects.get(camera_name)
    if cam is None:
        raise RuntimeError(
            f"Camera object {camera_name!r} not found after creation."
        )
    scene.camera = cam

    # Frame camera to aircraft (requires a 3D view context; works in many headless runs,
    # but may fail depending on Blender context).
    try:
        bpy.ops.view3d.camera_to_view_selected()
    except Exception:
        # If context isn't available, we keep the created camera and proceed.
        pass


def _find_principled_node(nodes: bpy.types.Nodes, preferred_name: str | None = None):
    if preferred_name and preferred_name in nodes:
        return nodes[preferred_name]
    for node in nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    return None


def ensure_camo_material_nodes(
    *,
    body_material_name: str = "body",
    wings_material_name: str = "wings",
    wings_principled_node_name: str = "Principled BSDF.001",
    body_principled_node_name: str = "Principled BSDF",
) -> None:
    """
    Ensure `body` and `wings` materials are set up to accept an image texture.

    The graph created/ensured is:
        Image Texture (Color) -> Bright/Contrast (Color) -> Principled BSDF (Base Color)

    Only the `body` and `wings` materials are modified. Materials that do not
    exist in the loaded `.blend` are skipped with a notice (some Boeing E-3
    `.blend` files share a single `wings` material for both the fuselage body
    and the wings, and therefore have no separate `body` material). A
    `RuntimeError` is raised only if none of the requested materials exist.
    """
    processed = 0
    for mat_name, principled_name in [
        (wings_material_name, wings_principled_node_name),
        (body_material_name, body_principled_node_name),
    ]:
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            print(f"[render_boeing_camos] Skipping missing material: {mat_name!r}")
            continue
        processed += 1
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        tex = nodes.get("Image Texture")
        if tex is None:
            tex = nodes.new(type="ShaderNodeTexImage")
            tex.name = "Image Texture"
            tex.label = "Image Texture"

        bc = nodes.get("Bright/Contrast")
        if bc is None:
            bc = nodes.new(type="ShaderNodeBrightContrast")
            bc.name = "Bright/Contrast"
            bc.label = "Bright/Contrast"

        principled = _find_principled_node(nodes, preferred_name=principled_name)
        if principled is None:
            raise RuntimeError(
                f"Could not find a Principled BSDF node in material {mat_name!r}."
            )

        # Link (idempotent-ish): make sure the expected links exist.
        def _link(out_socket, in_socket):
            for l in links:
                if l.from_socket == out_socket and l.to_socket == in_socket:
                    return
            links.new(out_socket, in_socket)

        _link(tex.outputs[0], bc.inputs[0])
        _link(bc.outputs[0], principled.inputs[0])

    if processed == 0:
        raise RuntimeError(
            "None of the configured camo materials were found: "
            f"{body_material_name!r}, {wings_material_name!r}."
        )


def render_camo_variants(
    *,
    mats_dir: str,
    output_dir: str,
    limit: Optional[int] = 10,
    sleep_seconds: float = 1.0,
    aircraft_object_name: str = "Boeing_E3",
    body_material_name: str = "body",
    wings_material_name: str = "wings",
) -> list[str]:
    """
    Render camouflage variants from `.png` textures in `mats_dir`.

    Parameters:
    - `mats_dir`: Directory containing `.png` camouflage textures.
    - `output_dir`: Output directory for rendered `.jpg` stills.
    - `limit`: Maximum number of renders. Use `None` to render all textures.
    - `sleep_seconds`: Optional delay between renders (useful for debugging/IO pacing).

    Returns:
    - A list of written image file paths.
    """
    mats_dir = os.path.abspath(mats_dir)
    output_dir = os.path.abspath(output_dir)
    _ensure_dir(output_dir)

    _require_object(aircraft_object_name).select_set(True)

    # Some Boeing E-3 .blend files share a single `wings` material for both the
    # fuselage body and the wings (no separate `body` material). Only assign the
    # texture to the configured materials that actually exist.
    target_materials: list[bpy.types.Material] = []
    for name in (body_material_name, wings_material_name):
        mat = bpy.data.materials.get(name)
        if mat is None:
            print(f"[render_boeing_camos] Skipping missing material: {name!r}")
            continue
        target_materials.append(mat)
    if not target_materials:
        raise RuntimeError(
            "None of the configured camo materials were found: "
            f"{body_material_name!r}, {wings_material_name!r}."
        )

    written: list[str] = []
    rendered = 0

    for image_filepath in _iter_png_files(mats_dir):
        if limit is not None and rendered >= limit:
            break

        # Load texture image and assign to each existing target material.
        img = bpy.data.images.load(image_filepath, check_existing=True)
        for mat in target_materials:
            mat.node_tree.nodes["Image Texture"].image = img

        base_name = os.path.splitext(os.path.basename(image_filepath))[0]
        out_path = os.path.join(output_dir, f"{base_name}_render.jpg")
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)

        written.append(out_path)
        rendered += 1

        if sleep_seconds:
            time.sleep(sleep_seconds)

    return written


def _parse_args(argv: list[str]) -> RenderConfig:
    """
    Parse CLI args after Blender's `--`.

    Example:
        blender file.blend --background --python render_boeing_camos.py -- --limit 10
    """
    parser = argparse.ArgumentParser(
        prog="render_boeing_camos.py",
        description="Render Boeing E-3 camouflage variants in Blender.",
    )
    parser.add_argument(
        "--mats-dir",
        default="CamoMats",
        help="Directory containing .png camouflage textures (default: CamoMats).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Directory to write rendered .jpg files (default: "
            "CamoMats/Rendered_<HHMM>/)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of renders (default: 10). Use 0 to render all.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=1.0,
        help="Delay between renders (default: 1.0).",
    )

    ns = parser.parse_args(argv)

    now = datetime.now()
    time_stamp = now.strftime("%H%M")

    mats_dir = ns.mats_dir
    output_dir = (
        ns.output_dir
        if ns.output_dir
        else os.path.join(mats_dir, f"Rendered_{time_stamp}")
    )
    limit = None if ns.limit == 0 else ns.limit

    return RenderConfig(
        mats_dir=mats_dir,
        output_dir=output_dir,
        limit=limit,
        sleep_seconds=ns.sleep_seconds,
    )


def main(argv: list[str] | None = None) -> int:
    """
    Script entrypoint for Blender `--python`.

    `argv` should contain only arguments after Blender's `--` separator.
    When run as a script, this function automatically extracts those args.
    """
    if argv is None:
        argv = []
        if "--" in os.sys.argv:
            argv = os.sys.argv[os.sys.argv.index("--") + 1 :]

    cfg = _parse_args(argv)

    # Setup scene and materials.
    setup_scene_camera_sun(
        aircraft_object_name=cfg.aircraft_object_name,
        scene_name=cfg.scene_name,
        camera_name=cfg.camera_name,
    )
    ensure_camo_material_nodes(
        body_material_name=cfg.body_material_name,
        wings_material_name=cfg.wings_material_name,
    )

    # Render.
    written = render_camo_variants(
        mats_dir=cfg.mats_dir,
        output_dir=cfg.output_dir,
        limit=cfg.limit,
        sleep_seconds=cfg.sleep_seconds,
        aircraft_object_name=cfg.aircraft_object_name,
        body_material_name=cfg.body_material_name,
        wings_material_name=cfg.wings_material_name,
    )

    print(f"Rendered {len(written)} image(s) to: {os.path.abspath(cfg.output_dir)}")
    return 0


#------------------------------------------
#
#   project setup:
#	directories, scene, camera, lights
# 
#------------------------------------------
if __name__ == "__main__":
    raise SystemExit(main())
