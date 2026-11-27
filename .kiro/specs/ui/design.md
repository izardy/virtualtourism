# Design: UI Design System

## Overview
A shared `base.html` layout with Tailwind compiled by the CLI to `static/css/app.css` (source `static/css/src.css`, config `tailwind.config.js`; no CDN) and a small `static/css/custom.css` for glass and animation utilities.

## Tokens
```js
tailwind.config = { theme: { extend: { colors: {
  navy:  { DEFAULT: '#0A192F', 800: '#0F2745', 700: '#16365C' },
  cyan:  { DEFAULT: '#00D4FF' }
}, fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] } } } }
```
- Background: `#0A192F` with radial cyan glow gradients.
- Text: white, secondary `white/70`.
- Accent: `#00D4FF` for buttons, links, focus rings and hotspot markers.

## Components (custom.css)
```css
.glass { background: rgba(255,255,255,.06); backdrop-filter: blur(16px);
         border: 1px solid rgba(255,255,255,.12); border-radius: 1.25rem; }
.btn-primary { background:#00D4FF; color:#0A192F; font-weight:600;
               border-radius:9999px; padding:.75rem 1.5rem; transition:.2s; }
.btn-primary:hover { box-shadow:0 0 24px rgba(0,212,255,.5); transform:translateY(-1px); }
.btn-glass { composes glass; border-radius:9999px; }
.fade-up { animation: fadeUp .5s ease both; }
@media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } }
```
A fallback solid translucent background is used where `backdrop-filter` is unsupported.

## Layout per page
- **Landing**: full-height hero with background image and gradient overlay, headline, CTAs, featured destination glass card, about and VR intro sections, login buttons row.
- **Explore**: sticky search bar, responsive grid (1/2/3 columns) of destination cards (image, category chip, name, location, Explore button), hover lift.
- **Destination**: hero image, glass description card, gallery grid with lightbox, hotspot chips, VR availability badge, sticky action buttons.
- **Viewer**: full-screen canvas; top-left back button; bottom-right VR button and controls hint; slide-in hotspot panel (right on desktop, bottom sheet on mobile); loading overlay with cyan progress bar.
- **Profile / Admin**: glass cards and forms, consistent inputs.

## Navigation
Top glass bar, fixed. Desktop shows links inline; mobile uses a hamburger toggling a glass dropdown. Authenticated state shows avatar with a dropdown.

## Accessibility
Focus ring `ring-2 ring-cyan`, semantic landmarks, alt text, aria-labels on icon buttons, contrast of white on navy above 12:1.

## Testing
Manual check at 360, 768 and 1280 px, landscape phone in the viewer, and with reduced motion enabled.

## As built
- Tokens in `tailwind.config.js` (navy, cyan, ghost, serif display font from system fonts, no web fonts). Components (`.glass`, `.btn-*`, `.chip`, `.input`, `.hud-btn`) live in `@layer components` so utilities such as `hidden` can override them.
- Landing and destination heroes use the licensed entrance photo under gradient, fog and vignette layers. The viewer overlays a vignette, a flash on teleport and a split caption in Cardboard mode.
- Verified in headless Edge at 1280x720, 390x780 (phone portrait) and 780x360 (phone landscape).

## As built: guided tour UI
Start screen with two glass cards (the guided card is highlighted for `?mode=guided`, with a "Best for VR" chip for `&vr=1`); a HUD button that switches modes; a bottom tour bar (Prev, Pause or Resume, Next, "Stop n of 10: title", progress bar, Free walk) hidden in Cardboard mode; a "Drag to look around" hint; an end card. HUD buttons never wrap (`whitespace-nowrap`) and the centred title only shows from 1024 px wide so the bar fits a 780x360 phone in landscape.

## As built: opening flight (2026-11-27)
Request: "when start the game it camera from top and slowly go to entrance".

- `app/static/js/IntroFlight.js` runs once the model has loaded.
  - **Path:** the camera starts 175 m above the middle of the site, which is the centre of the hotspot markers. It glides down along a cubic Bezier curve and passes under the WAR MUSEUM gate sign. It ends at the spawn point at eye height, facing the start direction.
  - **Look target:** the camera first looks at the fort, then turns toward the view ahead of the visitor.
  - **Timing:** 11 s of wall-clock time, so a slow device gets the same length rather than a slower flight.
  - **Fog and trees:** fog is thinned to 12% while high up and back to full near the ground. The viewer shows all tree chunks (650 m reach) during the flight.
  - **While it plays:** movement and look controls, fireflies and the HUD are off, and the proximity hints are paused.
- **Title card** (`#intro` in `viewer.html`): "VirtualTourism", "The Night Walk Chapter" and the destination name, with a **Skip intro** button. Any key or tap also skips.
- **After the flight:** the mode picker, or free walk, appears as before.
- **Skipped when:** `?intro=0` is set, the user prefers reduced motion, or the browser is automated (`navigator.webdriver`), so the test scripts drive the camera themselves. `?intro=1` forces it on.
- **Fix found on the way:** `MovementSystem.placeAt()` cast its ray from 60 m up with a 40 m reach. It missed the ground, so the visitor started 2 m in the air and dropped. The reach is now 140 m.
- **Checked in headless Edge:**
  - Frozen frames at 0, 30, 55, 75, 90 and 100% of the flight, at night and by day.
  - The end pose is the spawn point, the controls come back on, and the fog and fireflies are restored.
  - Skip works.
  - The float, door, chunk, tour and phone checks pass.
- **Not yet tested:** smoothness on a real phone. From the top, the phone draws the whole site for those 11 s.

## As built: platform-first landing page (2026-11-27)
Request: "considering the app landing page, it seemed like prioritize the museum perang penang… in future there will be other places to include… adjustment on the landing page so user know what this app is all about".

- **Hero:** "Walk real heritage sites, from anywhere." The text explains what VirtualTourism is (real sites rebuilt in 3D from surveys; guided tour or free walk; phone, browser, Cardboard; no install). The main button is "Choose a destination", plus a secondary "Start the Night Walk at <first destination>".
- **How it works:** three steps: pick a place, walk it your way, step inside in VR.
- **Destinations:** every destination from the database, as cards from the shared `_destination_card.html`:
  - Each card shows an "Open now in 3D" or "3D model coming soon" chip, the story count, and Explore and Guided tour buttons.
  - A dashed "Coming next" card says more places are being rebuilt and each opens as its own chapter.
  - The explore page uses the same card.
- **Chapter 1, The Night Walk:** the Muzium Perang section is presented as the current chapter, keeping the Ghost Hill theme and the folklore and respect note.
- **Wording made generic:** "Why virtual tourism?" and the site-wide meta description and footer ("not affiliated with the sites shown"; credits now list SRTM instead of OpenStreetMap).
- **Route:** `main.index` passes all destinations.
- **Checked:** headless Edge at 1280×800 and 390×844, with no console errors.
