#!/bin/sh
# Optimize the raw export for the web: dedup, GPU instancing, weld, simplify, textures capped at 1024 px as WebP, Draco geometry.
# 'flatten', 'join' and 'optimize' are NOT used: they prune empty nodes, which would delete the hotspot_*, loc_* and spawn markers.
# (Meshes are already merged per material in Blender.)
# Usage: sh blender/scripts/optimize_glb.sh   (from the repo root)
set -e
IN=blender/out/muzium_perang_raw.glb
OUT=app/static/models/muzium_perang.glb
T=blender/out/_tmp
CLI="npx --yes @gltf-transform/cli"
mkdir -p app/static/models "$T"
$CLI dedup "$IN" "$T/1.glb"
$CLI instance "$T/1.glb" "$T/2.glb"
$CLI weld "$T/2.glb" "$T/3.glb"
$CLI simplify "$T/3.glb" "$T/4.glb" --ratio 0.7 --error 0.001
$CLI resize "$T/4.glb" "$T/5.glb" --width 1024 --height 1024
$CLI webp "$T/5.glb" "$T/6.glb"
$CLI draco "$T/6.glb" "$OUT"
rm -rf "$T"
ls -la "$OUT"
