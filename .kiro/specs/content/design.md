# Design: MVP Content (Muzium Perang Penang)

## Overview
All content lives in `app/seed_data.py` as Python dictionaries plus asset files under `static/`. The seed code in the db spec inserts it. Text content must be fact-checked before the demo; the draft below is a structure and tone guide.

## Destination record
```
name:        "Muzium Perang Penang"
location:    "Batu Maung, Penang, Malaysia"
category:    "Museum / Historical Landmark"
thumbnail:   "images/muzium_perang_thumb.jpg"
hero_image:  "images/muzium_perang_hero.jpg"
model_path:  "models/muzium_perang.glb"
description: 3 short paragraphs: the fort's origin as a British coastal
             defence, its WWII role and the Japanese occupation, and its
             present use as a museum.
```

## Hotspots
| # | Title | Theme | Position (x, y, z) in glTF metres | Location confidence |
|---|---|---|---|---|
| 1 | Main Entrance | Arrival, site overview | (0.0, -4.81, -0.0) | from the museum map |
| 2 | Japanese Tunnel | Tunnel network | (81.8, 3.68, 86.4) | provisional |
| 3 | Command Centre | Military operations | (-84.8, -14.39, 46.4) | from the museum map |
| 4 | Observation Tower | Surveillance | (-39.2, 1.86, 104.8) | from the museum map |
| 5 | Prison Area | Wartime detention | (-101.8, -15.23, 58.6) | from the museum map |
| 6 | Underground Bunker | Shelter and storage | (-50.2, -8.45, 45.9) | provisional |
| 7 | Memorial Zone | Remembrance | (10.0, -0.39, 75.0) | provisional |
| 8 | Weapons Display | Artillery and arms | (14.9, 2.28, 95.3) | from the museum map |
| 9 | Lookout Point | Coastal views | (77.2, 3.54, 95.9) | provisional |
| 10 | Escape Route | Passages out of the fort | (44.86, 0.3, 88.85) | provisional |

Coordinates come from `blender/out/hotspots.json`, produced by `blender/scripts/build_muzium.py` (glTF axes: x east, y up, z south). Provisional means the location is a guess: the memorial and escape route are unconfirmed, the lookout, Japanese tunnel and underground bunker have no exact match on the museum map. Regenerate the seed from this file whenever the model changes.

## Hotspot content shape
```
{
  "title": ..., 
  "description": "<2-3 sentence history>\n\nFacts:\n- ...\n- ...\n- ...",
  "x_position": ..., "y_position": ..., "z_position": ...,
  "image_path": "images/hotspots/<slug>.jpg",
  "audio_path": "audio/<slug>.mp3"
}
```
`<slug>` is the lowercase hyphenated title (for example `japanese-tunnel`).

## Assets
- `static/images/muzium_perang_{thumb,hero}.jpg`, `static/images/hotspots/<slug>.jpg`: generated or licensed placeholders (1600x900 hero, 600x400 thumbnail, 800x600 hotspot).
- `static/audio/<slug>.mp3`: sample narration generated from scripts in `content/narration/<slug>.txt` (offline TTS or recorded), mono 64 kbps.
- `static/images/CREDITS.md` lists sources and licenses.

## Content rules
- Neutral, factual tone; no unverified claims; the site's folklore is labeled as such.
- Sensitive topics (prison, war) are described respectfully.
- Missing images/audio never break the page (the viewer omits them).

## Testing
Check that the seed produces 10 hotspots with titles matching the required list, that every referenced asset file exists, and that audio plays in the viewer panel.
