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
