# Site map notes: Penang War Museum

Source: museum visitor map "War Museum Relics" (copy in `map-visitor-2048.jpeg`; `map-small-web.jpg` is a photo of the same map on a signboard).
The map is the museum's artwork. Use it as a private reference only. Do not copy it into `app/static/`. Credit and permission status: unknown, see NOTES.md.
Structured data (37 numbered points plus facilities): `site_layout.json` (pixel coordinates on the 2048x1489 image).

## ORIENTATION (important, corrects the summary below)
The map is NOT north-up. It is rotated about 180 degrees: image-up = south, image-left = east, image-right = west, image-down = north.
- Evidence: OpenStreetMap shows the coastline about 250-285 m EAST of the museum pin (Google Maps link: 5.28137, 100.28881) and the access road Jalan Muzium Perang on the north and west side. On the map the sea is at the left edge and the road runs along the bottom and right.
- Confidence: medium-high, +/-30 degrees. The map is schematic.
- The directions written in "Layout summary" and in the `where` fields of `site_layout.json` are IMAGE directions. For compass directions use `east_m` and `north_m` in `site_layout.json` (origin = ticketing building, X east, Y north).
- Real-world context from OSM is in `osm_context.json` (coastline, roads, nearby buildings). OSM data is (c) OpenStreetMap contributors, ODbL.
- Scale check: north-south fits about 0.25 m/px (the road is about 125 m north of the entrance). East-west is compressed on the map (coast about 260 m east of the entrance but only about 600 px away). Use 0.27 m/px for the fort core and place the real coastline from OSM.

## Facts printed on the map
- Two eras: British fort 1930-1941, Japanese 1941-1945.
- Opening hours on the map: daily 9.00am-6.00pm and 7.00pm-11.00pm (evening session; may be outdated).
- Facilities: information and ticketing, souvenir shop, cafeteria, toilets, car park, VIP car park.
- Outside the fort core: War Game Park (north-east), coastal strip on the west with barbed wire, well, 3 pill boxes, submarine landing bay, maritime museum and jetty, generator room, armoury and water tank.
- A road ("to War Museum", with a water tank beside it) winds along the south and east edge of the hill.

## Layout summary (for modelling)
- The site is a hill roughly shaped like a rounded triangle. The sea is on the west side, with a narrow coastal strip below the hill.
- Entrance and ticketing are at the south-centre. The car park is south-west, the cafeteria west of the entrance.
- A main path ("spine") runs north from the entrance past Office & R&D (3), Mortuary (4), Open Air Theatre (5), Guillotine (34) and ends at the Observation Post (24) in the north.
- West branch: tunnels (26, 29), canon firing bays (25), pill boxes (37, plus 27 unlabeled), well (28), canon (36), anti-aircraft pit (30), booby trap zone and barbed wire (31) in the far north-west, trench route (33).
- Centre: underground communication centre (8), intelligence room (11), infirmary (9), officers' dining (10), underground water tank (23), armoury (35).
- East: rows of barracks by rank: British other ranks (7, 21, 22), Indian other ranks (13-16), Malay other ranks (18), cook houses (12, 17), lock-up (20).
- North-east: generator room (British) / torture chamber (Japanese) (6), General Yamashita Gallow (32), then the War Game Park.
- Two isolated pill boxes: 1 (far east) and 2 (south, by the road).

## Provisional scale (assumption, verify on site)
Sources give about 8 ha (about 20 acres). Estimating the hill outline on the map at roughly 1.0 million square pixels gives about 0.28 m per pixel, so the fort core is about 450 m wide and 300 m deep. Use this only for a first blockout. Any measurement from the user replaces it.

## Hotspot mapping (map number to our 10 hotspots)
| Hotspot | Map items | Confidence |
|---|---|---|
| Main Entrance | Information & Ticketing, souvenir, cafeteria | high |
| Japanese Tunnel | Tunnel 26, Tunnel 29 (video shows a tunnel numbered "No. 8") | medium |
| Command Centre | 8 Underground Communication Centre, 11 Intelligence Room, 3 Office & R&D | medium |
| Observation Tower | 24 Observation Post | high |
| Prison Area | 20 Lock-up, 6 Torture Chamber (JPN), 4 Mortuary (JPN), 34 Guillotine | medium |
| Underground Bunker | 8, 23 Underground Water Tank, 35 Armoury | low-medium |
| Memorial Zone | Not on the map. Wording now confirmed from a photo. Plaque "To Our Glorious Dead" is seen in videos on the way north-west of the spine (unverified). | low |
| Weapons Display | 25 Canon Firing Bay, 36 Canon, 30 Anti-Aircraft Pit | high |
| Lookout Point | No dedicated item. Candidates: 33 Trench Route end, north-west pill boxes (37) facing the sea | low |
| Escape Route | No map item. Now confirmed as a crawl (7 m) plus ladder climb (9 m) shaft. Video shows a sign "Escape route to top" (sample3); candidates: 29 Tunnel, 33 Trench Route | low |

Suggested change to hotspot content: add map-based extras as bonus hotspots later (General Yamashita Gallow, Guillotine, Booby Trap Zone, Submarine Landing Bay).

## Decisions and open questions
1. Orientation: resolved above (south-up). A satellite screenshot of the hill would still help to confirm the outline.
2. Memorial and "Escape route" sign locations: still unknown. Google Street View could not be read (interactive app, no API access). Please send 2 or 3 Street View or phone screenshots of the memorial plaque and the escape route sign, with the nearest map number.
3. Scope: read as all 37 numbered points plus facilities. The 10 hotspots stay the interactive ones; the other points become labeled structures and props.
