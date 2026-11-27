#!/bin/sh
# Optimize the raw export for the web: dedup, GPU instancing, weld, simplify, texture size cap, WebP, Draco geometry.
# 'flatten', 'join' and 'optimize' are NOT used: they prune empty nodes, which would delete the hotspot_*, loc_* and spawn markers.
# (Meshes are already merged per material in Blender.)
# Usage (from the repo root):
#   sh blender/scripts/optimize_glb.sh          desktop model, textures capped at 2048 px -> muzium_perang.glb
#   sh blender/scripts/optimize_glb.sh mobile   phone model (export_mobile.py), capped at 1024 px -> muzium_perang_mobile.glb
set -e
if [ "$1" = "mobile" ]; then
  IN=blender/out/muzium_perang_mobile_raw.glb; OUT=app/static/models/muzium_perang_mobile.glb; PX=1024; PROP_PX=512
else
  IN=blender/out/muzium_perang_raw.glb; OUT=app/static/models/muzium_perang.glb; PX=2048; PROP_PX=512
fi
# Small Poly Haven props (furniture, tools, clutter, ground plants, rocks): their 1k textures are capped lower
# (512 px on desktop and phone). They are seen from a metre or more and stay sharp enough; the island trees keep 1k.
PROPS="{WoodenTable_01,wooden_table_02,metal_office_desk,folding_wooden_stool,worn_metal_rack,wooden_bookshelf_worn,standing_chalkboard_01,wooden_crate_01,wooden_crate_02,old_military_crate,oil_tin,can_rusted,rusted_spade_01,picke_dirty_01,wooden_bucket_01,metal_toolbox,wooden_ladder_02,hanging_industrial_lamp,wooden_picnic_table,metal_trash_can,lifebuoy,ocean_buoy,anthurium_botany_01,calathea_orbifolia_01,shrub_03,shrub_04,pachira_aquatica_01,rock_07,rock_face_01,rock_face_02,rock_moss_set_02,tree_stump_02,dead_tree_trunk,dry_branches_medium_01,ammo_box,barrel_03,caged_hanging_light,industrial_wall_lamp,metal_jerrycan_green,old_bed_frame,old_military_compressor,vintage_radio_transceiver,wooden_barrels_01,wooden_ladder,wooden_military_crate,tree_stump_01,root_cluster_01}_*"
T=blender/out/_tmp
CLI="npx --yes @gltf-transform/cli"
mkdir -p app/static/models "$T"
$CLI dedup "$IN" "$T/1.glb"
$CLI instance "$T/1.glb" "$T/2.glb"
$CLI weld "$T/2.glb" "$T/3.glb"
$CLI simplify "$T/3.glb" "$T/4.glb" --ratio 0.7 --error 0.001
$CLI resize "$T/4.glb" "$T/4b.glb" --width $PX --height $PX
$CLI resize "$T/4b.glb" "$T/5.glb" --width $PROP_PX --height $PROP_PX --pattern "$PROPS"
$CLI webp "$T/5.glb" "$T/6.glb"
$CLI draco "$T/6.glb" "$OUT"
rm -rf "$T"
ls -la "$OUT"
