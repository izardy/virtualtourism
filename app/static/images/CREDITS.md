# Image credits

All photographs below come from Wikimedia Commons and were resized and recompressed for the web (no other changes).
Creative Commons licences: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/ and CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/ .
Credit line: "<author>, <licence>, via Wikimedia Commons". File page: https://commons.wikimedia.org/wiki/File:<Commons file name>

| Local file | Commons file name | Author | Licence |
|---|---|---|---|
| muzium_perang_hero.jpg, muzium_perang_thumb.jpg | Penang War Museum 001.jpg | LEE 003 | CC BY 4.0 |
| hotspots/main-entrance.jpg | Penang War Museum.jpg | angys | CC BY-SA 4.0 |
| hotspots/japanese-tunnel.jpg | Penang War Museum 008.jpg | LEE 003 | CC BY 4.0 |
| hotspots/prison-area.jpg | Penang War Museum 016.jpg | LEE 003 | CC BY 4.0 |
| hotspots/underground-bunker.jpg | Penang War Museum 005.jpg | LEE 003 | CC BY 4.0 |
| hotspots/memorial-zone.jpg | Penang War Museum 012.jpg | LEE 003 | CC BY 4.0 |
| hotspots/weapons-display.jpg | Penang War Museum 002.jpg | LEE 003 | CC BY 4.0 |
| hotspots/lookout-point.jpg | Penang War Museum 004.jpg | LEE 003 | CC BY 4.0 |
| hotspots/escape-route.jpg | Penang War Museum 022.jpg | LEE 003 | CC BY 4.0 |
| gallery/muzium_perang_penang/banyan-roots.jpg | Penang War Museum 011.jpg | LEE 003 | CC BY 4.0 |
| gallery/muzium_perang_penang/gun-emplacement.jpg | Penang War Museum 003.jpg | LEE 003 | CC BY 4.0 |
| gallery/muzium_perang_penang/tunnel-dark.jpg | Penang War Museum 020.jpg | LEE 003 | CC BY 4.0 |
| gallery/muzium_perang_penang/cell-cage.jpg | Penang War Museum 014.jpg | LEE 003 | CC BY 4.0 |
| gallery/muzium_perang_penang/hatch.jpg | Penang War Museum 009.jpg | LEE 003 | CC BY 4.0 |
| gallery/muzium_perang_penang/site-model.jpg | Penang War Museum 019.jpg | LEE 003 | CC BY 4.0 |

Note: hotspots/main-entrance.jpg is CC BY-SA, so the share-alike condition applies to that image and any derivative of it.

# 3D assets
- Site layout, terrain and structures (since 2026-11-27): the project's Penang War Museum digital twin (`blender/penang_war_museum`), built from public Street View observation, the museum's sketch map and SRTM 30 m elevation (NASA, public domain, via OpenTopoData). The Google satellite imagery used inside the twin is not shipped in the app.
- Pill boxes (type 1 and type 2) and the WAR MUSEUM entrance: modelled in Blender by the project author (`blender/user_models/`).
- Red brick on the entrance: Poly Haven `brick_4`, CC0.
- Props, textures and the sky map in the 3D model come from Poly Haven (https://polyhaven.com), CC0.
- Terrain shape and site layout follow the reeaki.com photo of the museum's "Fort Relics" visitor map (heights derived from the drawn hill and bay). Older builds used Open-Meteo elevation data (Copernicus DEM) and OpenStreetMap data, (c) OpenStreetMap contributors, ODbL.
- Site layout is based on the museum's public visitor map; the model is an unofficial, provisional reconstruction.

# Audio
Hotspot narration is synthetic speech generated offline with Kokoro-82M (Apache-2.0, https://huggingface.co/hexgrad/Kokoro-82M), voice `bf_emma` (British English), from the scripts in `content/narration/` using `content/make_narration.py`. Rerun that script to change the voice.

## Materials and sky
- PBR materials for buildings and ground (2k in the desktop model, 1k in the phone model): [Poly Haven](https://polyhaven.com), CC0. `forest_leaves_02`, `concrete_layers_02`, `concrete_floor_02`, `mossy_rock`, `asphalt_02`, `rusty_metal_02` (Rob Tuytel); `red_laterite_soil_stones`, `worn_mossy_plasterwall`, `mossy_stone_wall`, `rusty_metal_03` (Amal Kumar); `concrete_wall_006`, `weathered_planks` (Dario Barresi, Dimitrios Savva); `corrugated_iron` (Jenelle van Heerden, Dimitrios Savva); `worn_plaster_wall` (Dimitrios Savva). These replaced the earlier ambientCG (CC0) materials.
- Trees `island_tree_01`, `island_tree_02` (thinned) and the `industrial_wall_lamp` door lamps: [Poly Haven](https://polyhaven.com), CC0.
- Room fit-out, clutter, plants and rocks (decimated, textures 512 px): [Poly Haven](https://polyhaven.com), CC0. `WoodenTable_01`, `wooden_table_02`, `metal_office_desk`, `folding_wooden_stool`, `worn_metal_rack`, `wooden_bookshelf_worn`, `standing_chalkboard_01`, `wooden_crate_01`, `wooden_crate_02`, `old_military_crate`, `oil_tin`, `can_rusted`, `rusted_spade_01`, `picke_dirty_01`, `wooden_bucket_01`, `metal_toolbox`, `wooden_ladder_02`, `hanging_industrial_lamp`, `wooden_picnic_table`, `metal_trash_can`, `lifebuoy`, `ocean_buoy`, `anthurium_botany_01`, `calathea_orbifolia_01`, `shrub_03`, `shrub_04`, `pachira_aquatica_01`, `rock_07`, `rock_face_01`, `rock_face_02`, `rock_moss_set_02`, `tree_stump_02`, `dead_tree_trunk`, `dry_branches_medium_01`.
- Sky HDRIs `qwantani_night_puresky` (night), `kloofendal_48d_partly_cloudy_puresky` (day; replaced `fish_hoek_beach`, whose photo showed beach huts and a person): [Poly Haven](https://polyhaven.com), CC0.
- Nature ambience (crickets, waves, wind, bird calls, gecko, owl): synthesised in this repo by `content/make_ambience.sh`.
