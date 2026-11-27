# Penang War Museum (Muzium Perang, Batu Maung): Site Survey for Blender Modelling

Survey of every building and structure visible in Google Street View, user Photo Spheres and satellite imagery of the
Penang War Museum. The museum is a 1930s British coastal fort on Bukit Maung, Batu Maung, Penang, Malaysia.

This file is written to be used directly by Claude (or a person) to build Blender models. Every entry gives:
**ID, GPS, local coordinates, description, estimated dimensions, materials and colours, modelling notes, and the reference screenshots** in `screenshots/`.

> **Accuracy:** positions come from Street View/Photo Sphere GPS (±2–5 m) and satellite pixel measurements
> (±2–4 m). Dimensions are **visual estimates** scaled from known objects: doors ≈ 2.0 m, people ≈ 1.65 m, cars ≈ 4.7 m.
> Expect ±15–25 %. No published measured drawings were found.

---

## 1. Coordinate system (use this in Blender)

| Item | Value |
|---|---|
| **Survey origin O** | `5.281400 N, 100.288800 E` (front centre of the main gate on Jalan Muzium Perang) |
| ENU metres | `E = (lon − 100.2888) × 110 847`, `N = (lat − 5.2814) × 110 574` |
| **Model frame (same as the existing entrance models)** | `x = −E` (+x = west), `y = −N` (+y = south, into the grounds), `z = up`; gate front faces −y (north, toward the road) |
| Existing models in this frame | `site_structures/penang_war_museum_B01_B02_entrance_gate.blend` (gate, origin = O), `site_structures/penang_war_museum_B03_B04_B06_entrance_plaza.blend` (inner plaza) |

The site runs **north to south-east, downhill and along the ridge**. From the gate the visitor route goes south about 40 m through the
entrance plaza, then about 140 m south-east along a covered walkway to a courtyard. A side branch runs south-west to a blue
barrack building and a jungle trail. The coastal gun battery is about 110 m south-south-east of the gate.

![coverage](screenshots/SAT06_coverage_148m_center_5.2809481_100.288984.jpg)

**Satellite and coverage maps:**
- `SAT01_site_overview_228m.jpg`: whole hill
- `SAT02_site_166m_center_5.2809371_100.2892343.jpg`: best roof detail, about 0.27 m/px, centre pixel (400,300)
- `SAT03_streetview_coverage_166m.jpg`, `SAT04_coverage_with_photospheres_215m.jpg`, `SAT05_coverage_228m_center_5.28075_100.28905.jpg`, `SAT06_coverage_148m_center_5.2809481_100.288984.jpg`: blue lines are Street View, blue dots are Photo Spheres

---

## 2. Master table of buildings and structures

| ID | Name | Lat | Lon | E (m) | N (m) | model x | model y | Footprint (est.) | Source |
|---|---|---|---|---|---|---|---|---|---|
| B01 | Main entrance gate (log-letter "WAR MUSEUM") | 5.281400 | 100.288800 | 0 | 0 | 0 | 0 | 23 × 3 m frontage, 9.5 m deep passage | SV 2013 + 2024 |
| B02 | Gate passage (lattice-truss roof) | 5.281356 | 100.288809 | 1.0 | −4.9 | −1.0 | 4.9 | 4.6 × 9.5 m | SV 2013 |
| B03 | Ticket counter / office building (counter on the west side of the drive) | 5.281237 | 100.288764 | −4.0 | −18.0 | 4.0 | 18.0 | ≈ 5 × 17 m | SV 2013 (counter pano at E 2.8, N −17.4) |
| B04 | Camouflage kiosk ("WAR MUSEUM" plaque) | ≈5.281228 | ≈100.288908 | ≈ 12 | ≈ −19 | ≈ −12 | ≈ 19 | 5.4 × 3.6 m, rotated ≈ 40° | SV 2013, PS 2016 |
| B05 | Timber watchtower | ≈5.281287 | ≈100.288935 | ≈ 15 | ≈ −12.5 | ≈ −15 | ≈ 12.5 | ≈ 3 × 3 m, ≈ 8–9 m tall | PS 2016 |
| B06 | Big "WAR MUSEUM" signboard + soldier statue + "MALAYA Border Check Point" sign | ≈5.281201 | ≈100.288926 | ≈ 14 | ≈ −22 | ≈ −14 | ≈ 22 | — | SV 2013, PS 2016 |
| B07 | Rest area + souvenir/café building (teal wall, "TIPPNA") | 5.281180 | 100.288841 | 4.6 | −24.3 | −4.6 | 24.3 | ≈ 10 × 5 m | SV 2013 |
| B08 | Toilet block (blue-grey, camouflage doors) | 5.281138 | 100.288876 | 8.4 | −29.0 | −8.4 | 29.0 | ≈ 8 × 4 m | SV 2013 |
| B09 | Covered walkway (timber gable roof) | 5.281058 → 5.280653 | 100.288962 → 100.289582 | 18 → 87 | −38 → −83 | — | — | ≈ 3.2 m wide × ≈ 140 m long, polyline | SV 2013 |
| B10 | Site-map board on walkway | 5.280915 | 100.289113 | 34.7 | −53.6 | −34.7 | 53.6 | 2.5 × 1.8 m board | SV 2013 |
| B11 | Rubble-stone retaining wall + steps up the hill | 5.280734 | 100.289438 | 70.7 | −73.6 | −70.7 | 73.6 | wall ≈ 60 m long, 1.5–2.5 m high | SV 2013 |
| B12 | Vaulted concrete bunker (ammunition store) | 5.280781 | 100.289335 | 59.3 | −68.5 | −59.3 | 68.5 | ≈ 5 × 6 m, ≈ 3 m high | SV 2013 |
| B13 | Garden display huts / miniature models | 5.28085 | 100.28915 | ≈ 40 | ≈ −61 | ≈ −40 | ≈ 61 | small, < 2 m | SV 2013 |
| B14 | South-east courtyard (vine pergola, wooden fort model, fenced exhibits) | 5.280613 | 100.289623 | 91.2 | −87.1 | −91.2 | 87.1 | ≈ 20 × 15 m open area | SV 2013 |
| B15 | Blue barrack building (south-west branch, end of path) | ≈5.280731 | ≈100.288818 | ≈ 2 | ≈ −74 | ≈ −2 | ≈ 74 | ≈ 12 × 7 m | SV 2013 |
| B16 | Jungle trail + execution/noose display + info post | 5.280724 | 100.288738 | −6.9 | −74.7 | 6.9 | 74.7 | trail | SV 2013 |
| B17 | **Coastal gun emplacement** (circular gun pit + magazines) | 5.280445 | 100.289401 | 66.6 | −105.6 | −66.6 | 105.6 | pit ≈ 9 m dia., complex ≈ 20 × 15 m | PS 2017 |
| S1 | Open clearing / lawn (helipad-like) | 5.280889 | 100.289369 | 63.1 | −56.5 | −63.1 | 56.5 | ≈ 25 × 25 m | SAT |
| S2 | Small roofed building (south of walkway) | 5.280558 | 100.289318 | 57.4 | −93.1 | −57.4 | 93.1 | ≈ 8 × 10 m | SAT |
| S3 | Small white hut (south-east edge) | 5.280425 | 100.289640 | 93.1 | −107.8 | −93.1 | 107.8 | ≈ 3 × 3 m | SAT |
| S4 | Small hut (far south-west) | 5.280385 | 100.288922 | 13.5 | −112.2 | −13.5 | 112.2 | ≈ 4 × 4 m | SAT |
| S5 | Dark-roof building east of plaza (likely exhibition hall; sketch map puts the **cafeteria** here) | 5.281287 | 100.289030 | 25.5 | −12.5 | −25.5 | 12.5 | ≈ 12 × 13 m + 12 × 11 m annex | SAT |
| S6 | Brown-roof building beside the SW branch path (sketch #3 / #4 area) | 5.280901 | 100.288922 | 13.5 | −55.2 | −13.5 | 55.2 | ≈ 15 × 9 m | SAT |

`≈` means the position was triangulated from a view direction, not stood on.

---

## 3. Detailed descriptions

### B01 Main entrance gate
**Screenshots:**
- `P01_gate_h174.jpg`: 2013, close
- `P02_gate_2024_5.2814433_100.2887926_h190.jpg`: 2024
- `P02b_gate_2024_left_paintball_5.2814433_100.2887926_h146.jpg`: 2024, left side
- `REF01_war_museum_relics_sitemap_board_2024.jpg`: 2024 map board

**2013 version:** this is already modelled in `site_structures/penang_war_museum_B01_B02_entrance_gate.blend`.
- **Brick piers:** two deep brick piers, about 2.6 m deep, flank a 4 m opening.
- **Posts:** green-painted square timber posts sit at the pier corners.
- **Pergola deck:** a flat timber pergola deck at about 3.1–3.4 m high.
- **Letters:** about 13.6 m of rustic "WAR MUSEUM" letters made from tree branches, standing on a log rail, with a row of small triangular pennants on sticks behind them.
- **Left pier:** a white anchor, a driftwood root sculpture and three green artillery shells.
- **Right pier:** a black "Night Tour" poster and a carved "WAR MUSEUM BATU MAUNG PENANG MALAYSIA" plank on a driftwood log.
- **Right wall:** a set-back brick wall with a site map, then a low boundary wall with a blue banner.

**2024 changes, for a "current" version of the gate:**
- **Letters:** the log letters are replaced by **large cream/white block letters "WAR MUSEUM"**, about 1.4 m tall, sans-serif and 3D, on the same deck. A row of national flags on tall poles stands behind the letters.
- **Flags:** a line of national flags hangs across the left half of the opening (Japan, Thailand, Australia, UK, and others).
- **Map board:** the right brick wall now carries the **"WAR MUSEUM RELICS"** illustrated site-map board, about 3.4 × 2.2 m in a white frame.
- **Poster:** a yellow poster board, about 1.5 × 2.2 m, reads "BEAR HISTORY IN MIND / CHERISH PEACE / COMMEMORATE MARTYRS / BUILD A BETTER FUTURE" with Chinese text.
- **Signs and road:** a black "100 FEET UNDERGROUND" paintball advert, a timber "WAR MUSEUM PAINTBALL PARK" sign with a soldier silhouette, an "AWAS" (danger) sign, white "DROP ZONE" lettering and arrows on the asphalt, and a rubble-stone kerb.
- **Left side:** a timber picket fence and a hut roof.

**Materials:** red-brown face brick, sage-green timber posts, dark stained timber, cream block letters, asphalt.

### B02 Gate passage
**Screenshots:** `P03_gate_passage_5.281356_100.288809_h190.jpg`, `P18_ps2016_gate_rear_watchtower_5.2812304_100.2889023_h2.jpg`

- **Roof:** a low pitched passage roof whose underside is a lattice of timber trusses (king post plus diagonals) and rafters. Eaves are about 2.55 m and the ridge about 3.35 m, running about 9 m south. It is already modelled in entrance1.
- **Pier walls:** the inner pier walls are face brick with deep-set windows behind dark timber frames, plus a **vertical timber louvre screen** of slats about 0.6 m wide beside the window.
- **Kerbs:** red-painted kerbs, with a grey concrete drive and a red path.
- **From the plaza, looking back (2016):** the pier backs show an **orange canvas awning** over the opening, the brick office facade with a window and door, and green and grey wheelie bins.

### B03 Ticket counter / museum office
**Screenshots:** `P04_ticket_counter_5.2812423_100.2888256_h190.jpg`, `P05_rest_area_souvenir_5.28118_100.2888414_h175.jpg`

- **Counter:** a long **dark-stained timber counter**, about 6 m long and 1.1 m high, with a top shelf of brochures. It stands under a **translucent corrugated pergola roof**, about 2.6–3.0 m high on timber rafters and posts.
- **Wall:** the back wall is a dark brick/timber facade with an arched door and notice boards, with a "WELCOME WAR MUSEUM BATU MAUNG" green panel on the right.
- **Decorations:** Malaysian and US flags hang on poles under the eaves, with a wall-mounted air-conditioning unit, potted plants and a "COUNTER" sign.
- **Mannequins:** a soldier mannequin in jungle uniform stands on the left beside the **"MALAYA Border Check Point"** Union-Jack sign.
- In `site_structures/penang_war_museum_B03_B04_B06_entrance_plaza.blend` this is the "ticket building and booth".

### B04 Camouflage kiosk
**Screenshots:**
- `P04b_kiosk_signboard_5.2812423_100.2888256_h110.jpg`
- `P18b_ps2016_watchtower_kiosk_h60.jpg`
- `P18c_ps2016_signboard_statue_counter_h130.jpg`

- **Shape:** an open-fronted timber pavilion about 5.4 × 3.6 m on a white tiled platform.
- **Roof:** a lower hip roof skirt painted in **jungle camouflage** (green, yellow and brown blotches), with a **steep pyramidal/gable timber shingle roof** above it.
- **Back wall:** dark green, with a carved "WARMUSEUM" plank.
- **Furniture:** log-stump stools, timber benches and a display mortar. In 2016 it was used as a seating and rest area.
- It is already modelled in entrance2. Note: the 2016 photo shows the **upper roof is dark timber shingle, not red tile**.

### B05 Timber watchtower (modelled: `site_structures/penang_war_museum_B05_watchtower.blend`)
**Screenshots:** `P18_ps2016_gate_rear_watchtower_5.2812304_100.2889023_h2.jpg`, `P18b_ps2016_watchtower_kiosk_h60.jpg`

- **Position:** a 3-level open **timber lookout tower** beside and north-east of the kiosk, behind the right gate pier.
- **Structure:** four heavy timber corner posts, about 0.25 m square, with horizontal rails at each level, and a **steel-framed open staircase** zig-zagging up the inside.
- **Top deck:** at about 6 m, with a **small gabled timber roof** whose ridge is about 8–9 m high and runs east to west.
- **Base:** a concrete pad with a low brick and stone plinth, and green mesh fencing next to it.
- **Model notes:** plan about 3 × 3 m; post height 6 m; roof 3.4 × 3.4 m at a 45° pitch; three landings at 2, 4 and 6 m.

### B06 Signboard, statue and checkpoint sign
**Screenshots:** `P04b_…`, `P18c_ps2016_signboard_statue_counter_h130.jpg`

- **Signboard:** green-framed "WAR MUSEUM" board, about 2.0 × 1.3 m, on two timber posts with its top at about 3.4 m. It shows red stencil text and a photo strip, and hangs below the big tree canopy.
- **Statue:** a soldier statue (stormtrooper-like white armour helmet) on a black plinth, about 1.8 m.
- **Checkpoint sign:** "MALAYA Border Check Point" board, about 1.1 × 0.7 m, red and blue with a Union Jack, on black steel posts.
- **Planting:** tropical potted plants (bird's-nest fern, cordyline) and a raised planter bed.

### B07 Rest area and souvenir/café building
**Screenshot:** `P05_rest_area_souvenir_5.28118_100.2888414_h175.jpg`

- **Building:** single storey with walls painted **teal/blue-grey**, about 2.7 m high.
- **Roof:** a translucent corrugated pergola over the front.
- **Signs and stock:** a red "TIPPNA" banner, a book and postcard rack, and military unit pennants hanging along the eave.
- **Seating:** outdoor rustic **timber picnic tables with log benches** on concrete paving.
- **Banners:** a large photo banner of WWII soldiers on a steel frame above the roof line, about 6 × 2 m.

### B08 Toilet block
**Screenshot:** `P06_toilet_block_covered_walkway_5.2811381_100.2888759_h175.jpg`

- **Building:** a low **blue-grey rendered block**, about 8 × 4 m and 2.6 m high, with a flat roof.
- **Doors:** two **camouflage-painted doors** marked with gender signs and no-entry discs, with small timber-louvred windows.
- **Banner:** a large black-and-white **photo banner of POWs/soldiers**, about 8 × 2.5 m, on a steel frame above.
- **Planting:** potted plants line the base.

### B09 Covered walkway (main visitor route)
**Screenshots:**
- `P06_…`, `P07_covered_walkway_notices_…`, `P07b_covered_walkway_long_…`
- `P08_walkway_lanterns_garden_…`, `P10_…`, `P11_…`, `P12_…`, `P13_walkway_end_open_road_…`

- **Route:** from (E 18, N −38) to (E 87, N −83), heading south-east (bearing about 125°).
- **Cross-section:** about 3.2 m wide with a concrete deck painted with red arrow markings.
- **Posts:** timber posts about 0.2 m square at about 2.4 m spacing, on **squat rendered concrete pillars** about 1.0 m high and 0.45 m square, painted green-grey.
- **Roof:** a **timber gable roof** at about a 30° pitch, with eaves at about 2.4 m and the ridge at about 3.4 m. It is open to the underside: rafters, purlins and collar ties are visible, with dark corrugated sheet on top.
- **Lighting:** **brass/copper hanging hurricane-style lanterns** every 3–4 posts along the ridge.
- **Edges:**
  - East/garden side: low parapet walls about 0.6 m high, and timber bench seats in places.
  - West/hill side: a rubble-stone retaining wall (see B11).
- **Bend:** the walkway bends at about E 40, N −60 and again near the end.

**Model notes:** this is a sweep along a polyline. Use one bay module, 2.4 m long, and repeat it with an array along a curve.

### B10 Site-map board
**Screenshot:** `P09_walkway_sitemap_board_5.2809152_100.2891132_h120.jpg`

A large painted **illustrated site map** ("WAR MUSEUM"), about 2.5 × 1.8 m, in a timber frame on the west side of the walkway. It has a blue sea background with the fort buildings drawn on the hill. The text is not legible at Street View resolution. The same map design appears on the 2024 gate (`REF01_…`).

### B11 Rubble-stone retaining wall and hill steps
**Screenshots:** `P10_walkway_stone_retaining_wall_…`, `P12_walkway_stairs_up_hillside_…`

- **Wall:** a dry-laid / mortared **grey granite rubble** retaining wall, 1.5–2.5 m high, along the hill (south-west) side of the walkway for about 60 m.
- **Steps:** a **concrete stair, about 1.2 m wide**, climbs through the wall at about E 70, N −74 to the upper level, which holds the forest and higher batteries.
- **Furniture:** timber bench seats sit against the wall.

### B12 Entrance to the ammunition storage tunnel (sketch **#29 Tunnel**); vaulted concrete portal
**Screenshots:** `P11_walkway_bunker_5.2807809_100.2893346_h125.jpg`, `P11b_vaulted_bunker_side_5.2807809_100.2893346_h195.jpg`

- **Shape:** a **reinforced-concrete bunker with a segmental (barrel-vault) roof**, half dug into the hillside, about 5 m wide, 6 m deep and 3 m high at the crown.
- **Front:** a flat rendered facade with a **camouflage-painted steel door**, about 1.0 × 2.0 m, and a yellow interpretation sign, about 0.8 × 0.6 m, probably "AMMUNITION STORAGE".
- **Surface:** the concrete is weathered grey with moss. An information board stands in front of it in a timber frame.
- Sources describe the main ammunition store as "**9 m underground** with thick stone walls". This may be one of the entrances.

### B13 Garden display huts and models
**Screenshots:** `P08_…`, `P10_…`, `P13_…`, `P14_…`

- **Huts:** small thatched/attap-roof huts, about 2 × 1.5 m, in the garden on the east side of the walkway, probably dioramas of a jungle camp.
- **Wooden model:** a dark timber model, about 1.5 × 1 × 2.5 m, at the walkway end. It is the **"Replica of abandoned Senior British Army Residence"**: a 3-storey colonial building with a central tower and a flag, inside a chain-and-post fence with a blue name sign (Penang Travel Tips, 2013).
- **Rope fence:** log bollards with rope fencing.

### B14 South-east courtyard
**Screenshot:** `P14_courtyard_wooden_model_pergola_5.2806125_100.2896227_h125.jpg`

- **Ground:** open asphalt/concrete with arrow markings.
- **Canopy:** a **large vine-covered steel pergola canopy**, about 15 m wide, overhead.
- **Edges:** a rubble-stone wall on the south side, small yellow interpretation signs, a fenced exhibit with a radiation-style yellow sign, and planting beds with red cordyline.
- This is the end of the 2013 Street View path. Exhibits continue beyond it but weren't captured.

### B15 Blue barrack building (south-west branch)
**Screenshot:** `P15_SWbranch_blue_building_5.2807604_100.2887897_h225.jpg`

- **Shape:** a single-storey **masonry barrack** about 15 × 9 m, rendered and painted **mid-blue/teal**.
- **Roof:** a **flat or low concrete roof with a deep overhanging eave/fascia**, about 0.6 m. From the satellite view it is a brown corrugated sheet.
- **Openings:** window openings about 1.0 × 1.0 m with **white frames, filled with vertical bamboo screens**, and a timber door.
- **Surroundings:** a narrow concrete/timber walkway with a black handrail runs along the front, under tall forest trees.

### B16 Jungle trail and display
**Screenshot:** `P16_SW_jungle_trail_5.2807244_100.2887379_h225.jpg`

- **Trail:** an earth trail with **log steps and rope-and-post fencing**, rising south-west into the forest.
- **Displays:** a **hanging noose** on a tree branch (execution display), a small timber stool, a concrete pillar holding an interpretation board with a yellow sign, and a large boulder.

### B17 Coastal gun emplacement (gun battery)
**Screenshots:**
- `P17_gun_emplacement_pit_2017_5.2804449_100.2894012_h350.jpg`: pit, looking north
- `P17b_gun_emplacement_parapet_east_h98.jpg`
- `P17c_gun_emplacement_ready_room_trench_h194.jpg`
- `P17d_gun_emplacement_magazine_steps_h291.jpg`

The **original 1930s British fort structure**, in reinforced concrete.

- **Gun pit:** circular, about **8–9 m internal diameter** and sunk about 1.0–1.2 m.
- **Parapet:** a curved concrete parapet, about 1.0 m high and 0.6 m thick, with a rounded top, enclosing about 270°.
- **Pivot and holdfast:** a raised central concrete **pivot plinth**, about 2.4 m in diameter, with a **ring of holdfast bolts and a steel racer ring**, and a capped central pivot (red-brown).
- **Ammunition recesses:** recessed cartridge and shell lockers in the parapet wall, with **steel grille doors and decorative steel grilles**.
- **Rear (south) side:** a **sunken concrete trench and passage**, about 1.5 m wide, leads to **ready-use magazines / shelters** with steel-grilled openings. Concrete steps lead up to a higher terrace.
- **Above it, to the north:** a **timber lookout hut with a gabled roof** on the higher terrace (B05-style), and concrete retaining walls showing large cracks.
- **Displays:** an inert artillery shell (black body, red nose) stands at the parapet.
- **Surface:** weathered grey concrete with moss and black staining, surrounded by forest.

**Model notes:** this is the most historically important structure. Build a lathe-style circular pit (a cylinder with a boolean cut), a parapet as a partial torus or extruded curve, a pivot plinth with an array of bolts, and rectangular magazine cut-outs with a grille texture.

### S1–S6 Satellite-only structures
These were seen only on satellite (`SAT02_…`) and are not covered by Street View. Treat them as placeholders until better photos exist.

| ID | What it is | Detail |
|---|---|---|
| S1 | Open clearing | Grass and earth, about 25 × 25 m, possibly a former parade ground |
| S2 | Building with a brown corrugated roof | About 8 × 10 m, likely a barrack or exhibition room |
| S3 | Small white-roofed hut | About 3 × 3 m |
| S4 | Small hut in the forest | Unknown use |
| S5 | Dark brown roof plus a grey metal annex east of the entrance plaza | About 12 × 13 m plus 12 × 11 m, likely the main exhibition hall / office behind the kiosk and watchtower |

---

## 4. Known structures *not* captured (need on-site photos)

Published sources mention all of these, but no Street View or Photo Sphere covers them:
- **underground tunnels** and the main **ammunition storeroom, about 9 m underground**;
- **lockups / torture chambers** (Japanese occupation period);
- **observation towers** other than B05;
- **machine-gun emplacements and sniper posts**;
- the **cannon sites** other than B17;
- a **concrete military guard post**.

The fort covers about 20 acres. The surveyed area is about 130 × 120 m, roughly a fifth of the site. The 2024 "WAR MUSEUM RELICS"
board (`REF01_…`) shows the full layout, and a high-resolution photo of it taken on site would complete this survey.

---

## 5. Material and colour palette (sRGB approximate)

| Material | Colour | Used on |
|---|---|---|
| Face brick | `#7A3B22` to `#5C2C1A`, grey mortar | Gate piers and walls |
| Sage-green paint (timber posts) | `#4E6B55` | Gate and pergola posts |
| Dark stained timber | `#3A2616` | Counter, walkway frame, kiosk |
| Teal/blue-grey render | `#3F6F78` / `#5A7C86` | Café, toilets, barrack (B07, B08, B15) |
| Camouflage | `#4F6B2A`, `#C9A93A`, `#7A4A1E`, `#1E1E14` | Kiosk skirt, toilet doors, bunker door |
| Weathered concrete | `#8E8C84` with moss `#4C5A32` | Bunker, gun emplacement, pillars |
| Granite rubble | `#7D7A72` | Retaining walls |
| Red-painted concrete | `#8E2F22` | Path edges and kerbs |
| Grey concrete drive | `#9A9891` | Paths |

Poly Haven textures that match (already used in entrance2):
- `red_brick_pavers`, `concrete_pavement`, `concrete_floor_worn_001`
- `weathered_brown_planks`, `corrugated_iron_02`, `distressed_painted_planks`

Suggested for new structures:
- `castle_brick_02_red`
- `rustic_stone_wall`, for the retaining walls
- `concrete_moss` / `worn_mossy_plasterwall`, for the bunker and gun pit
- `rusty_metal_grid`, for the grilles

---

## 6. Suggested modelling order and file names

| File | Contents |
|---|---|
| `site_structures/penang_war_museum_B01_B02_entrance_gate.blend` | B01–B02 (2013 look), **done** |
| `penang_war_museum_entrance1_2024.blend` | B01 with the 2024 block letters, flags and posters (optional) |
| `site_structures/penang_war_museum_B03_B04_B06_entrance_plaza.blend` | B03, B04, B06 plus plaza, **done**. B05 watchtower is a separate file (done). Open: kiosk upper roof should be dark timber shingle |
| `penang_war_museum_amenities.blend` | B07 café / rest area, B08 toilets |
| `penang_war_museum_walkway.blend` | B09 walkway, B10 board, B11 walls and steps, B13 garden huts |
| `penang_war_museum_bunker1.blend` | B12 vaulted ammunition bunker |
| `penang_war_museum_courtyard.blend` | B14 |
| `penang_war_museum_barrack_blue.blend` | B15 + B16 trail |
| `penang_war_museum_gun_emplacement.blend` | **B17**: highest priority |
| `penang_war_museum_sitemap.blend` | Terrain plus all of the above, linked at their model x/y |

Use the **model x/y** column for each building's root empty. All files share origin O, so linking them into the site map places them correctly
without manual alignment. Site elevation drops about 10–15 m from the gate (about 70 m above sea level per Street View altitude)
to the gun battery (about 65 m). Use z offsets if you build terrain.

---

## 7. Screenshot index

| File | Location (lat, lon) | Heading | Date | Shows |
|---|---|---|---|---|
| P01_gate_h174.jpg | 5.2814104, 100.2888007 | 174° | 2013 | Gate, close |
| P02_gate_2024_… | 5.2814433, 100.2887926 | 190° | 2024 | Gate, current version |
| P02b_gate_2024_left_paintball_… | 5.2814433, 100.2887926 | 146° | 2024 | Gate left, paintball sign, block letters |
| P03_gate_passage_… | 5.281356, 100.288809 | 190° | 2013 | Passage, pier windows, louvres |
| P04_ticket_counter_… | 5.2812423, 100.2888256 | 190° | 2013 | Counter, pergola, checkpoint sign |
| P04b_kiosk_signboard_… | 5.2812423, 100.2888256 | 110° | 2013 | Kiosk, signboard, statue |
| P05_rest_area_souvenir_… | 5.28118, 100.2888414 | 175° | 2013 | Café, picnic tables, walkway start |
| P06_toilet_block_covered_walkway_… | 5.2811381, 100.2888759 | 175° | 2013 | Toilets, photo banner |
| P07_covered_walkway_notices_… | 5.2810579, 100.2889617 | 175° | 2013 | Walkway, notice boards |
| P07b_covered_walkway_long_… | 5.2810579, 100.2889617 | 120° | 2013 | Walkway perspective |
| P08_walkway_lanterns_garden_… | 5.2809899, 100.2890402 | 120° | 2013 | Lanterns, garden |
| P09_walkway_sitemap_board_… | 5.2809152, 100.2891132 | 120° | 2013 | Site-map board |
| P10_walkway_stone_retaining_wall_… | 5.2808523, 100.2891885 | 125° | 2013 | Stone wall, garden hut |
| P11_walkway_bunker_… | 5.2807809, 100.2893346 | 125° | 2013 | Bunker beside walkway |
| P11b_vaulted_bunker_side_… | 5.2807809, 100.2893346 | 195° | 2013 | Vaulted bunker facade |
| P12_walkway_stairs_up_hillside_… | 5.2807341, 100.2894376 | 125° | 2013 | Steps up through the wall |
| P13_walkway_end_open_road_… | 5.2806531, 100.2895817 | 125° | 2013 | Walkway end |
| P14_courtyard_wooden_model_pergola_… | 5.2806125, 100.2896227 | 125° | 2013 | Courtyard, vine pergola, wooden model |
| P15_SWbranch_blue_building_… | 5.2807604, 100.2887897 | 225° | 2013 | Blue barrack |
| P16_SW_jungle_trail_… | 5.2807244, 100.2887379 | 225° | 2013 | Trail, noose display |
| P17_gun_emplacement_pit_2017_… | 5.2804449, 100.2894012 | 350° | 2017 PS | Gun pit, pivot, magazines |
| P17b_gun_emplacement_parapet_east_h98 | same | 98° | 2017 PS | Parapet, interpretation plate |
| P17c_gun_emplacement_ready_room_trench_h194 | same | 194° | 2017 PS | Trench, grilled shelters |
| P17d_gun_emplacement_magazine_steps_h291 | same | 291° | 2017 PS | Magazine block, steps, lookout hut |
| P18_ps2016_gate_rear_watchtower_… | 5.2812304, 100.2889023 | 2° | 2016 PS | Gate rear, awning, watchtower |
| P18b_ps2016_watchtower_kiosk_h60 | same | 60° | 2016 PS | Watchtower and kiosk |
| P18c_ps2016_signboard_statue_counter_h130 | same | 130° | 2016 PS | Signboard, statue, counter |
| REF01_war_museum_relics_sitemap_board_2024 | 5.2814433, 100.2887926 | 203° | 2024 | Official illustrated site map |
| SAT01–SAT06 | see filenames | — | Airbus/Maxar | Satellite views and coverage lines |

Photo Sphere credits: P17 by Google Maps contributor "Zooxter" (Dec 2017); P18 by "Jung Yi Hung" (Feb 2016).
Street View imagery © Google (Jan 2013, Sep 2024). These screenshots are for internal modelling reference only.

## 8. Top-view site map and sketch-map comparison

![site map](penang_war_museum_sitemap_topview.png)

| File | What it is |
|---|---|
| `penang_war_museum_sitemap_topview.png` / `.svg` | **North-up, georeferenced top view** (2400 px, 4.3 px/m in the SVG, 20 m grid labelled in E/N metres from origin O). Layers: satellite (Google 228 m detail inset over a 912 m context view); surveyed structures B01–B17; satellite-only S1–S6; Street View path; user Photo Spheres; covered walkway; retaining wall; the 37 numbered relics and named features from the museum's own sketch map, fitted onto real coordinates; dashed match lines. |
| `penang_war_museum_sitemap_sketch_overlay.png` / `.svg` | The same map with the **"WAR MUSEUM RELICS" sketch map warped onto it at 55 % opacity**, so you can compare it directly. |
| `penang_war_museum_sitemap_points.csv` | Every point (B, S, R01–R37 relics, F named features, B09 walkway vertices) with lat/lon, E/N, **model_x/model_y**, footprint size, rotation, source, accuracy and sketch match. **Import this into Blender** (snippet below). |
| `tools/fit.py`, `tools/make_sitemap.py`, `tools/transform.json` | Rebuild scripts. Edit coordinates there and re-run `python3 tools/make_sitemap.py` (needs `sketch.jpg` and the screenshots). |
| `screenshots/REF02_…scan.webp`, `REF03_…board_photo.webp`, `REF04_terrain_model_display_case.webp` | Your references: the sketch-map scan, a photo of the sketch-map board, and the museum's terrain model. |

### How the sketch map was placed
The sketch map is a **perspective illustration, rotated about 180° from north-up**. On the sketch the sea is on the left and the road enters bottom-right. In reality the sea is **east/south-east** (Batu Maung bay with fish farms, see `SAT07`) and Jalan Muzium Perang climbs in from the **north-west**.

A 2-D similarity transform was fitted using five control points:

| Sketch feature | Matched to |
|---|---|
| Information & ticketing | B03 |
| Souvenir | B07 |
| Cafeteria | S5 |
| Path below ticketing | Gate O |
| #25 Canon firing bay | B17 gun pit |

| Result | Value |
|---|---|
| Rotation | −154° (the sketch is drawn looking roughly north, so south is at the top) |
| Scale | 0.39 m per sketch pixel, which puts the whole hill at about 350 m across, consistent with the stated ~20 acres |
| Residuals | 6–30 m. The sketch enlarges the plaza and compresses the outskirts. |

**Independent checks:**
- After the transform, the sketch's "TO WAR MUSEUM" access road falls on the real winding Jalan Muzium Perang (west).
- Its car parks fall on the real road loops (north-west).
- Its coast, jetty and pill boxes fall toward the real shoreline (east).
- The terrain model (`REF04`) also shows the building cluster on the hill-top ridge with the sea to one side.

### What the comparison tells you
**Sketch matches the survey:**

| Sketch item | Survey match |
|---|---|
| Information & ticketing, Office & R&D (#3), Souvenir | B03 / B07 at the plaza |
| Cafeteria | S5, the dark-roof building east of the plaza |
| Toilets | B08 |
| #25 Canon firing bay | **B17 gun emplacement**, the only relic confirmed by Photo Sphere |
| #29 Tunnel, #34 Guillotine, #4 Mortuary | Along and just south of the covered walkway (B09–B12) |
| #7 British other ranks 1 | The SW branch / **B15 blue barrack** |

**Not covered by Street View (sketch positions only, ±30 m):**
- **Barracks quarter:** British, Indian and Malay "other ranks" barracks #6, #7, #13–#22, cook houses #12 and #17, lock-up #19, intelligence room #11, infirmary #9 and officers' mess #10. On the real ground these fall **south-west of the plaza, beyond the blue barrack**, in the forest at about E −90…+20, N −60…−150.
- **Hill-top military core:** underground communication centre #8, underground water tank #23, observation post #24, anti-aircraft pit #30, armoury #35, General Yamashita gallow #32 and trench route #33. These fall **south of the plaza** at about E −20…+40, N −80…−140.
- **Seaward defences:** canon firing bay #27, canon #36, tunnels #26 and #29, pill box #37, well #28 and booby-trap zone #31. These fall **east, toward the sea**.
- **Shore features:** the coastal pill boxes, jetty / maritime museum and submarine landing bay are well **outside** the surveyed area, on the east/north-east shore.

For Blender, use the **B/S rows** as reliable placements. Use the **R/F rows** only as layout guides until on-site photos confirm them.

### Blender: import the CSV as empties
```python
import bpy, csv
path = "/Users/izardy/Desktop/blender/museum_survey/penang_war_museum_sitemap_points.csv"
col = bpy.data.collections.get("SitePoints") or bpy.data.collections.new("SitePoints")
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for r in csv.DictReader(open(path)):
    e = bpy.data.objects.new(f'{r["id"]}_{r["name"][:30]}', None)
    e.location = (float(r["model_x"]), float(r["model_y"]), 0.0)
    e.empty_display_type = 'CUBE' if r["type"] in ("surveyed", "satellite") else 'SPHERE'
    e.empty_display_size = 1.0 if r["type"] != "path" else 0.4
    if r["size_E_m"]:   # show footprint (note: model x = -E, model y = -N)
        e.scale = (float(r["size_E_m"]) / 2, float(r["size_N_m"]) / 2, 1)
        e.rotation_euler[2] = __import__("math").radians(float(r["rot_deg_ccw"] or 0))
    col.objects.link(e)
```
*(In the model frame both axes are flipped, so a rotation CCW in ENU stays CCW. The footprint boxes are approximate.)*

## 9. Built Blender models (Nov 2026)

Every structure in this survey now has a model. Each file holds **one top collection, marked as an asset**, with **root empties named
by survey ID**, placed at the surveyed model x/y. All files share origin O, so linking them needs no alignment.

| File (`~/Desktop/blender/`) | Contains | Basis |
|---|---|---|
| `site_structures/penang_war_museum_B01_B02_entrance_gate.blend` | B01–B02 gate (2013) | Street View, earlier work |
| `site_structures/penang_war_museum_B03_B04_B06_entrance_plaza.blend` | B03, B04, B06 plaza + Poly Haven vegetation and props | Street View, earlier work |
| `site_structures/penang_war_museum_B05_watchtower.blend` | B05 timber watchtower: 3 levels, steel stairs, gable roof | Photo Sphere 2016 |
| `site_structures/penang_war_museum_B07_B08_amenities.blend` | B07 café/souvenir (teal, translucent pergola, picnic tables, photo banner); B08 toilets (camouflage doors, banner) | Street View |
| `site_structures/penang_war_museum_B09_walkway.blend` | B09 covered walkway along the surveyed polyline (bays every 2.4 m, lanterns); B10 site-map board; B11 rubble wall and steps; B13 attap huts | Street View |
| `site_structures/penang_war_museum_R29_tunnel_entrance.blend` | **#29 entrance to the ammunition storage tunnel** (survey B12): barrel-vault portal, camouflage door, "29" plate, 2002 dedication plaque, dark corridor, interpretation board | Street View + Tye 2013 |
| `site_structures/penang_war_museum_B14_courtyard.blend` | B14 steel pergola with vine canopy, wooden fort model, fenced exhibit, stone wall | Street View |
| `site_structures/penang_war_museum_B15_B16_barrack_trail.blend` | B15 blue barrack (bamboo-screened windows, handrail walkway); B16 jungle trail, noose display, info pillar | Street View |
| `site_structures/penang_war_museum_B17_gun_emplacement.blend` | **B17 gun pit** (r 4.25 m, −1.1 m) with parapet, pivot, racer ring, 24 holdfast bolts, ammunition recesses with grilles, rear trench, ready magazine, terrace, steps, lookout hut, display shell | Photo Sphere 2017 |
| `site_structures/penang_war_museum_V_vegetation.blend` | **Poly Haven vegetation across the whole site (CC0):** 404 Island Tree 02 instances (~41 full-detail near visitor areas, ~363 far LOD that keeps ~30 % of leaf cards scaled ×1.45 with decimated wood), plus ~150 understory plants near the paths (Pachira, Shrub 04, Fern 02, Calathea, Anthurium). All seated on the terrain; they avoid every structure footprint, the walkway corridor, the gate/plaza and the approach road. Rebuild with `tools/build_vegetation.py`. | Poly Haven + survey CSV |
| `site_structures/penang_war_museum_S_satellite_placeholders.blend` | S1–S6 massing placeholders | Satellite only |
| `site_structures/penang_war_museum_R_sketch_relics.blend` | R01–R37 and named sketch features as **approximate massing**: barracks, cook houses, pill boxes, tunnel portals, observation post, AA pit, gun bays, gallow, guillotine, trench, booby-trap stakes, well, water tanks, jetty, slipway, car parks. R36 Canon uses the Poly Haven `cannon_01`; R35 Armoury uses Poly Haven crates and ammo boxes. | Sketch map (±30 m) |
| `site_structures/penang_war_museum_PB1_pillbox_loaf_cupola.blend` | Rectangular "loaf" pillbox with round cupola, furnished interior. Candidate model for sketch-map pill boxes R01, R02, R37 and the coastal pill boxes. **Not placed on the site map; generic type.** | Penang sample photos |
| `site_structures/penang_war_museum_PB2_pillbox_octagonal_halfburied.blend` | Octagonal half-buried watch-post pillbox (Bumbong Lima type), furnished interior. **Not placed on the site map; generic type.** | Bumbong Lima type |
| **`penang_war_museum_sitemap.blend`** | **Links all of the above** as collection instances, over georeferenced satellite ground. Includes `Cam_TopDown_NorthUp` (ortho) and `Cam_Oblique_FromNorthEast`. | — |

Renders: `sitemap3d_oblique.png`, `sitemap3d_topdown.png`.

**Rebuilding:** run `blender -b --factory-startup --python tools/build_structures.py -- <target>` with one of these targets:
`gun_emplacement | watchtower | bunker | amenities | walkway | courtyard | barrack_blue | satellite | sketch_relics`.
For `sketch_relics`, add the output folder and the baked Poly Haven folder as further arguments.
Then run `tools/assemble_sitemap.py -- <out.blend>`. The scripts refuse to overwrite existing files.

### Terrain elevation (added)
- **Data:** SRTM 30 m, from OpenTopoData with bilinear interpolation, on a 25 m grid covering about 800 × 580 m (`tools/terrain_srtm.json`).
- **Calibration:** SRTM is a surface model and reads the forest canopy, not the ground. I corrected it with **20 Street View camera altitudes**, the URL `NNa` value minus 2 m camera height. Residuals are spread by inverse-distance weighting over 60 m and fade to a −10 m canopy correction elsewhere. Near the coast the correction fades out so the shore stays at sea level. All 20 checkpoints now agree to within 0.8 m (`tools/terrain.py`).
- **Reference height:** z = 0 is the ground at the gate front, about **68.6 m ASL**. The sea lies at z ≈ −68.6.

| Location | Ground (m ASL) | z in model |
|---|---|---|
| Gate O | 68.6 | 0 |
| Entrance plaza | ≈ 70 | ≈ +1.3 |
| Walkway, highest point near B07/B08 | 71 | +2.4 |
| Walkway end / courtyard B14 | 63 | −6 |
| Blue barrack B15 | 74–75 | +6 |
| Gun emplacement B17 | ≈ 70 | ≈ +1.7 |
| Barracks quarter (sketch) | ≈ 73 | ≈ +4…+5 |

How the structures sit on the terrain:
- Every structure root now sits on the terrain, because `pwm_lib.root()` sets z from `terrain.z_model`.
- The walkway is draped vertex-by-vertex, so it slopes down its route.
- The site-map terrain (`PWM_Terrain_SRTM_SVcalibrated`, a 4 m grid) is flattened into pads under each footprint and along the walkway corridor.
- It is textured with both satellite views: the high-resolution view inside its coverage, the context view outside.
- `WarMuseumEntrance2` is lifted to the plaza height.
- Renders: `sitemap3d_terrain_oblique_NE.png`, `sitemap3d_terrain_from_sea_SE.png`, `sitemap3d_terrain_topdown.png`.

**Limitations:**
- Terrain accuracy is about ±1 m along the Street View paths and about ±3–6 m elsewhere (SRTM resolution plus canopy uncertainty). The real hill likely has steeper local banks than a 30 m model shows.
- Materials are procedural, so no textures are needed. Entrance 2 uses packed Poly Haven textures.
- R and F models are placeholders until the site is photographed.

## 10. Relic catalogue: photo-confirmed details (added during the audit)

### Sources for this section
- **[Penang Travel Tips: Penang War Museum](https://www.penang-traveltips.com/penang-war-museum.htm)**, Timothy Tye. It has about 25 captioned photos of every relic from his visit on 26 Oct 2013. The photos are marked "please get my permission before using", so **they are not copied here**. Open the page for the images; the details below are what they show. The museum's own numbering of each relic was unchanged from 2002 to 2013 and matches the sketch map.
- **Google Maps visitor photos** (2019–2026), saved as low-resolution screen captures in `screenshots/gallery/` for **internal modelling reference only**. Credits are in the gallery index below.

### Corrections to earlier assumptions
| Earlier label | Corrected |
|---|---|
| B12 "vaulted bunker / ammunition store" | **#29 Tunnel, the entrance to the ammunition storage tunnel**, at the sharp bend of the covered walkway. In 2002 its portal was painted **terracotta red** with a **green steel door**, a "29" number plate and a dedication plaque (opened 14 Oct 2002). By 2013 it was grey concrete with a camouflage door. |
| B14 "wooden fort model" | **Replica of the abandoned Senior British Army Residence**, a 3-storey miniature |
| R05 Open-air theatre modelled as stepped seating (**fixed**) | It is a **teal-painted open shed with a gable roof** and a vintage motorcycle mounted on the gable wall. Inside are displays: large earthen jars, a wooden bed, and a "A LIFE FOR EVERY SLEEPER" board. **Rebuilt as a shed.** |
| B17 "gun emplacement" | The museum calls it **"The Penang Battery"**. The 2026 photo (G001) shows a **steel ring railing around the pivot**, **blue gas cylinders and display props** on the parapet, and a **lean-to roofed shed** on the terrace. |

### Newly confirmed relics (from the photos; positions still from the sketch map)
| Sketch # | Relic | What the photos show (modelling detail) |
|---|---|---|
| 36 (plaza) | **6-inch BL gun replica** ("Canon") | Long black barrel, about 7 m, on a box pedestal stencilled "AMMUNITION", on a circular concrete pad. It sits under **camouflage netting with leaf-shaped scrim** strung between trees. Red **clay-tile-roofed buildings** stand behind it. Sources call it "the 6-inch breech-loading gun originally installed in that spot in 1941". |
| 29 (interior) | **Ammunition storage chamber, now an interpretation gallery** | A straight concrete **tunnel about 1.2 m wide and 2.2 m high**, lit by bulbs, leads from the walkway bend. The chamber has cream-painted walls, a dark timber-beamed ceiling, framed pictures, log-stump stools and timber benches. |
| 29 → stairs | **Escape route to the top** | A square opening in the chamber wall leads to a steep steel/timber ladder-stair in a narrow shaft, with a red sign: "ESCAPE ROUTE TO TOP". |
| 29 | **Ammunition hoist** | An inclined chute/shaft with timber guide rails rising to daylight, and an "AMMUNITION HOIST" sign. |
| — | **Steep steps going up** | A narrow concrete stair, about 1 m wide, cut through a **moss-covered rock cutting**, with **chequer-plate treads**, a black steel handrail and an inscription carved in the rock face. This is the escape route's surface exit. |
| 37 / 1 / 2 | **Remains of a pill box** | A ruined base beside a **rubble-stone wall** and path. Next to it is a **brick pedestal holding a yellow interpretation board** (the standard museum sign type), and a small steel lattice mast. |
| — | **Shaft going down to the ammunition chamber** (end of the old hill road) | A square vertical concrete shaft inside a **steel mesh-panel enclosure**, with a **winch drum and arched steel frame** at the top. |
| 25 / 27 | **Gun firing bay** | A raised circular gun pit with a parapet. In front is a lower apron with **recessed shell lockers** (dark openings), concrete steps, and a yellow board on the side wall. |
| — | **Ammunition shaft entrance** | A concrete portal with a **white steel lattice grille gate** marked **"MERBAHAYA"** (danger). Beside it is a recess labelled "AMMUNITION LOCKER" and a steel stair handrail. |
| 31 | **Booby trap zone** | A **tripod of poles with a hanging can/bell alarm**, a black hose line on the ground, and a brick-pedestal yellow board "No. 31 BOOBY TRAP ZONE". |
| 30 | **Anti-aircraft pit** | A **stepped circular pit**: three or four concentric concrete rings sunk about 1.5 m into the earth. A **twin-barrel AA gun replica** is mounted on a post (G005, 2024; Tye 2013). There's a timber frame overhead with an "ANTI AIRCRAFT" sign. |
| — | **Tapioca garden** | A planted plot with a blue "TAPIOCA GARDEN" sign and a laminated info sheet on stakes. |
| — | **Quarters for officers on duty** | A **low flat-roofed concrete block**, half sunk into the hill, with a row of window openings and deep reveals. A **sunken concrete-walled trench path** runs alongside it, with earth and plants on the roof. |
| 12 / 17 | **Cook house** | A **colonnaded concrete building**: square columns with **flared capitals and brackets**, a flat roof slab and a dark interior. G008 (2021) shows the same type, with a net-curtained doorway and logs. |
| 13–16 | **Staircase down to the Indian Army quarters** | A **two-storey concrete barrack with a deep columned verandah**, flared column heads and a long concrete stair with a black handrail descending beside it. |
| 11 | **Intelligence Officer's quarters** | A concrete building with a columned front, a blue door, a yellow board and graffiti on the walls. |
| 8 | **Doorway to the British Army underground command centre** | A concrete portal set into the hillside, with a **dark doorway**, a **steel-barred transom grille**, two small plaques, a yellow board and a blue sign. Bamboo grows around it. |
| — | **Exit** | A tall timber post-and-beam gateway with an "EXIT" lintel. Beside it are painted skeleton murals on a black board and a green steel handrail on steps. |
| — | **Banyan-root hut** (G004, 2024) | A timber hut **completely wrapped by banyan roots**, with a black "Welcome WAR MUSEUM" post sign on a concrete plinth. |
| — | **Ghost-banner courtyard** (G007, 2023) | A **brick-paved open courtyard** under large trees, with a painted "ghost" banner on a red frame, huts and a booth. |
| — | **Checkpoint gate** (G003, 2025) | Timber slat gate posts painted **red with "CHECK POINT"**, a Japanese-soldier statue on rocks, the "MALAYA Border Check Point" board and a "BACK TO MALAYA" sign. This updates B06. |
| — | **View east** | From the grounds you look across the bay with fish farms to the **Second Penang Bridge**. Include it as the backdrop or HDRI for the digital twin. |


### Model fixes applied (Nov 2026)
All ten fixes from the gap checklist are built. Renders are in `renders/`.

| # | Fix | File |
|---|---|---|
| 1 | B12 rebuilt as **#29 tunnel entrance** ("29" plate, 2002 dedication plaque, dark corridor). The old B12 file is replaced. | `site_structures/penang_war_museum_R29_tunnel_entrance.blend` |
| 2 | R05 open theatre is now a teal gable shed with a motorcycle on the gable, earthen jars and a display bed | `R_sketch_relics` |
| 3 | R30 AA pit: stepped concentric rings sunk about 1.5 m, twin AA gun on a post, timber frame, "ANTI AIRCRAFT" sign | `R_sketch_relics` |
| 4 | R36 is now a **6-inch BL gun replica** (7 m barrel, AMMUNITION pedestal) under sagging camouflage netting. It moved to **east of the plaza** (model −32, 24, ±15 m), following Tye's 2013 photo order. | `R_sketch_relics` |
| 5 | Barracks, cook houses, office, infirmary, mess and intelligence quarters are now **flat-roofed concrete colonnade buildings** with flared capitals. The Indian Army quarters (#13–16) are 2 storeys with an external stair; the cook houses have chimneys. | `R_sketch_relics` |
| 6 | Museum-standard **brick-pedestal yellow interpretation boards** ("No. NN") at every sketch relic, plus B17, #29 and B14 | several |
| 7 | B17 Penang Battery in its 2026 state: ring railing round the pivot, blue gas cylinders on display, terrace lean-to shed | `B17_gun_emplacement` |
| 8 | Kiosk upper roof darkened to timber shingle (plaza file backed up first) | `B03_B04_B06_entrance_plaza` |
| 9 | Walkway exhibits: hanging flags, uniform mannequins, notice boards; bamboo clumps and a gravel bed round the attap huts | `B09_walkway` |
| 10 | B14 **Senior British Army Residence replica**: 3 storeys, central tower, windows, flag, chain fence, blue name sign | `B14_courtyard` |

Sketch relics #7, #25 and #29 are no longer duplicated: they are the surveyed B15, B17 and B12/R29. The CSV `sketch_match` column records this.

### Gallery index (`screenshots/gallery/`, internal reference only)
| File | Shows | Photo |
|---|---|---|
| G001_B17_gun_pit_2026-06_railing_display | Penang Battery (B17), current state | Google Maps, Fadhil Hashim, Jun 2026 |
| G002_video_still_2022_doorway_net_curtain_concrete_building | Colonnaded concrete building, net-curtain doorway | Google Maps video, mura 1967, May 2022 |
| G003_B06_checkpoint_gate_statue_2025-04 | Checkpoint gate and statue | Google Maps, Chan Yut Seng, Apr 2025 |
| G004_banyan_tree_hut_welcome_sign_2024-07 | Banyan-root hut | Google Maps, M.Hafies Abdullah, Jul 2024 |
| G005_stepped_circular_pit_AA_gun_2024-10 | #30 AA pit with gun | Google Maps, Edwan Nur Ikraam Idris, Oct 2024 |
| G006_B01_gate_2025-03_block_letters | Gate, 2025 | Google Maps, Dan Manners, Mar 2025 |
| G007_ghost_banner_courtyard_brick_paving_huts_2023-08 | Ghost-banner courtyard | Google Maps, Wang Miss, Aug 2023 |
| G008_barrack_colonnade_verandah_concrete_original_2021-11 | Original colonnaded barrack / cook house | Google Maps, Ibrahim Isa, Nov 2021 |
| G009_B09_walkway_interior_flags_uniform_displays_2019 | Walkway exhibits: flags and uniforms | Google Maps, Aug 2019 |

See **`penang_war_museum_digital_twin_gaps.md`** for the full checklist of what is still missing.

## 11. Sources
- Google Maps Street View and Photo Spheres, Penang War Museum (accessed Nov 2026)
- [Bernama: Penang War Museum structures](https://www.bernama.com/en/region/news.php?id=2599074)
- [The Star: War museum that honours sacrifices](https://www.thestar.com.my/metro/metro-news/2026/09/12/war-museum-that-honours-sacrifices)
- [Time Out: Penang War Museum and WWII Relics](https://www.timeout.com/penang/museums/penang-war-museum-and-world-war-ii-relics)
- [TracesOfWar: Batu Maung Fort War Museum](https://www.tracesofwar.com/sights/8827/Batu-Maung-Fort-War-Museum-Batu-Maung.htm)
- [Lonely Planet: Penang War Museum](https://www.lonelyplanet.com/points-of-interest/penang-war-museum/1218798)
- [Penang Travel Tips: Penang War Museum (Timothy Tye, 2002/2013 photos)](https://www.penang-traveltips.com/penang-war-museum.htm)
- Google Maps place photos, Penang War Museum (contributors credited in the section 10 gallery index)
