# Penang War Museum: Digital Twin Audit and Gap Checklist

Audit of `museum_survey/` and the Blender models in `~/Desktop/blender`, Nov 2026.
The goal is a digital twin as close as possible to the real site. Legend: ✅ have · ⚠️ partial or approximate · ❌ missing.

## 1. Folder audit result
| Check | Result |
|---|---|
| Files referenced by `penang_war_museum_survey.md` | ✅ All present: 34 survey screenshots, 9 gallery captures, site maps (PNG and SVG), CSV, renders, tools |
| Out-of-date sections | ✅ Fixed: B05 was marked "not yet modelled"; B12 mislabelled (now #29 tunnel entrance); B14 model identified; S1–S5 heading now S1–S6; entrance-plaza "next steps" |
| Site map links after the 12:40 move/rename | ✅ All 11 linked models resolve. The scheduled run moved the files but didn't relink, so this was fixed by hand and the site map backed up first. |
| Model ↔ survey consistency | ⚠️ See section 3. Several models predate the new relic photos. |
| Plaza screenshots used for entrance 2 (Street View at 5.2812959, 100.2888158) | ❌ Not saved in the folder (captured before the survey existed). Re-capture if needed. |

## 2. Coverage by area
| Area / structure | Position | Exterior detail | Interior | Signage text | Status |
|---|---|---|---|---|---|
| Approach road, car parks, paintball zone | ⚠️ satellite | ⚠️ 2024 SV at gate only | — | ⚠️ | Road up the hill, VIP car park and paintball park not modelled |
| B01–B02 gate | ✅ ±3 m | ✅ 2013 + 2024/25 photos | ✅ passage | ⚠️ | **Model shows the 2013 look.** The current gate (2024/25) has block letters, flags and posters. Decide which era to model. |
| B03–B08 plaza, kiosk, watchtower, café, toilets | ✅ ±4–5 m | ✅ | ❌ shop/office interiors | ⚠️ posters are stand-ins | Kiosk roof colour wrong; checkpoint gate (G003) not modelled |
| B09 walkway (≈140 m) | ✅ ±3 m | ✅ | n/a | ⚠️ | **Exhibits along it (flags, uniform mannequins, notice boards, G009) not modelled** |
| #29 tunnel entrance (was "B12") | ✅ | ✅ | ⚠️ described (chamber, hoist, escape stair), **no dimensions** | ⚠️ | Interior tunnel/chamber not modelled |
| B13 garden huts, bamboo | ⚠️ | ✅ (Tye 2013) | — | — | Bamboo clumps and gravel beds missing |
| B14 courtyard + Senior British Army Residence replica | ✅ | ✅ | — | ⚠️ | ✅ 3-storey replica modelled |
| B15 blue barrack, B16 trail | ✅ | ✅ | ❌ | ⚠️ | — |
| B17 Penang Battery | ✅ ±3 m | ✅ 2017 + 2026 | n/a | ⚠️ | ✅ 2026 state modelled |
| #36 6-inch BL gun replica + camouflage netting | ⚠️ ±15 m (east of plaza) | ✅ (Tye) | — | — | ✅ Modelled |
| #30 AA pit (stepped rings + twin AA gun) | ⚠️ sketch | ✅ (G005, Tye) | — | ✅ | ✅ Rebuilt as a stepped pit with twin gun |
| #25/#27 gun firing bay with shell lockers | ⚠️ sketch | ✅ (Tye) | — | — | Placeholder only |
| Ammunition shaft + winch, MERBAHAYA grille portal | ❌ position unknown | ✅ (Tye) | ❌ | ✅ | Not modelled |
| #8 underground command-centre doorway | ⚠️ sketch | ✅ | ❌ tunnel unknown | ⚠️ | Placeholder portal |
| #11 Intelligence Officer's quarters, officers-on-duty quarters | ⚠️ sketch | ✅ | ❌ | ⚠️ | Placeholder blocks |
| #12/#17 cook houses, #13–#16 Indian quarters, #18–#22 barracks | ⚠️ sketch | ⚠️ type only (colonnade, flared capitals, 2-storey) | ❌ | ❌ | ✅ Restyled as colonnade buildings (layout and dimensions still approximate) |
| #5 open theatre (actually a teal shed) | ⚠️ sketch | ✅ | ⚠️ displays | ⚠️ | ✅ Rebuilt as a teal shed |
| #31 booby-trap zone, tapioca garden, exit gate | ⚠️ sketch | ✅ | — | ✅ | Booby trap placeholder only; tapioca garden and exit missing |
| #32 Yamashita gallows, #34 guillotine, #4 mortuary | ⚠️ sketch | ❌ no photos | ❌ | ❌ | Generic placeholders |
| #23 water tank, #24 observation post, #33 trench, #35 armoury, #26 tunnel, #28 well, #37 pill box | ⚠️ sketch | ❌ (pill box ✅ ruin) | ❌ | ❌ | Generic placeholders |
| Coastal features (jetty, submarine landing bay, coastal pill boxes, maritime museum, generator room) | ⚠️ sketch ±30 m+ | ❌ | ❌ | ❌ | Outside the surveyed area; may be outside museum grounds today |
| Banyan-root hut, ghost-banner courtyard | ❌ position unknown | ✅ (G004, G007) | — | ⚠️ | Not modelled |

## 3. Model fixes already identified: ✅ ALL APPLIED Nov 2026 (see survey section 10, "Model fixes applied")
1. Rename B12 to **#29 Tunnel entrance**. Add the terracotta 2002 variant or the grey 2013+ variant, a "29" plate and a dedication plaque.
2. Rebuild **R05 open theatre** as a teal gable shed with a motorcycle and displays.
3. Rebuild **R30 AA pit** as a stepped circular pit with a twin AA gun on a post and a timber frame with sign.
4. Replace the **R36 Canon** placeholder with a **6-inch BL gun replica** (about 7 m barrel, AMMUNITION box pedestal) under camouflage netting. It probably stands near the plaza, so its position needs checking.
5. Restyle **barracks, cook houses and quarters** as **flat-roofed concrete with square columns, flared capitals and deep verandahs**. Make the Indian quarters two storeys with an external stair.
6. Add museum-standard **brick-pedestal yellow interpretation boards** at every relic.
7. Update **B17** to the 2026 state: ring railing, display props, terrace lean-to.
8. Kiosk upper roof: dark timber shingle.
9. Add walkway exhibits (flags, mannequins, boards), bamboo clumps and gravel beds.
10. Add the **Senior British Army Residence** replica façade (3 storeys, central tower).

## 4. What only an on-site visit can provide (biggest remaining gaps)
| Need | Why | How (suggested) |
|---|---|---|
| **GPS point at every numbered relic (1–37)** | Sketch-map positions are only ±30 m | Phone GPS or RTK at each yellow board. Photograph the board (it shows the number). |
| **Measured dimensions** of the key structures | Current sizes are visual estimates ±15–25 % | Laser distance meter: widths, heights, wall thickness, door sizes |
| **Drone photogrammetry / LiDAR scan** of the grounds | True terrain (SRTM is ±3–6 m, misses banks and cuttings), exact footprints, roof shapes | A drone flight (needs museum permission) processed into a mesh and orthophoto. iPhone LiDAR for the tunnels. |
| **Tunnel and chamber interiors** (#29, #8 command centre, ammunition shaft) | No dimensions or layout | Walk with a 360 camera; tape-measure the cross-sections; sketch the plan |
| **Photos of unphotographed relics** (#4 mortuary, #6–#7, #9–#10, #18–#24, #26, #28, #32–#35, coastal features) | No visual reference at all | 4 sides + details + signage at each |
| **Texture photos** (concrete, brick, timber, camo paint, rubble walls, signage) | Procedural materials are approximations | Straight-on, evenly lit, with a colour chart |
| **Vegetation map** (big trees, banyans, bamboo, palms) | Trees define the look. ⚠️ The whole site now has Poly Haven trees (`V_vegetation.blend`), but they're placed procedurally and are all one species (Island Tree 02), so real positions and species are still unknown | Mark the large trees on the site map; photograph species |
| **Signage text** (yellow boards, posters, notices) | Readable signs add realism | Photograph every board |
| **Night-tour lighting** (museum open 7–11 pm) | If the twin should support night visits | Night photos of the lighting positions |
| **Ambient audio** | For an immersive experience | Field recording: jungle, birds, sea |
| **Current state** | Most coverage is 2013–2019; the 2024–26 photos show changes (gate, B17) | Fresh photos of everything |

## 5. Decisions needed from you
- **Era:** model the site as in **2013** (most of the Street View coverage), as **today (2024–26)**, or both as switchable variants?
- **Extent:** museum grounds only, or include the approach road, paintball zone and coastal relics?
- **Interior depth:** model the tunnels and chamber interiors without measurements (approximate), or wait for a site visit?
