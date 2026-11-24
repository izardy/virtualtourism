# Requirements: MVP Content (Muzium Perang Penang)

## Introduction
The MVP ships with one fully populated destination, Muzium Perang Penang (War Museum Penang), Malaysia, a former British coastal fortress (Batu Maung, built in the 1930s and used during World War II). Content must be factually careful and suitable for a demo.

## Requirements

### Requirement 1: Destination profile
#### Acceptance Criteria
1. The seed SHALL include name, description (historical overview), location (Batu Maung, Penang, Malaysia), category (Museum / Historical Landmark), thumbnail, hero image and model path.
2. The historical description SHALL be verified against reliable sources before release, and unverifiable claims SHALL be avoided or worded as local lore (for example the folklore around the site).

### Requirement 2: Ten hotspots
#### Acceptance Criteria
1. The seed SHALL include exactly these hotspots: Main Entrance, Japanese Tunnel, Command Centre, Observation Tower, Prison Area, Underground Bunker, Memorial Zone, Weapons Display, Lookout Point, Escape Route.
2. Each hotspot SHALL have a title, historical description, interesting facts, 3D position, image path and audio path.
3. Hotspot positions SHALL lie inside the placeholder model's bounds and be reachable by teleport.

### Requirement 3: Narration
#### Acceptance Criteria
1. Each hotspot SHALL have a short narration script (about 20 to 40 seconds) with a matching audio file.
2. WHEN real recordings are not available THEN the system SHALL use sample audio files (TTS-generated or placeholder) with the same file names.
3. The narration scripts SHALL be stored in the repo as text for later re-recording.

### Requirement 4: Images
#### Acceptance Criteria
1. The seed SHALL reference a thumbnail, hero image and one image per hotspot, all optimized (under about 300 KB each).
2. All images SHALL be either original, generated placeholders or licensed for use; sources and licenses SHALL be recorded in `static/images/CREDITS.md`.

### Requirement 5: Language
#### Acceptance Criteria
1. MVP content SHALL be in English. The structure SHALL not prevent adding Malay, Mandarin or Japanese later.
