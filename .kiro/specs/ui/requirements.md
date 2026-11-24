# Requirements: UI Design System

## Introduction
The interface is modern, premium and tourism-focused, inspired by Apple Vision Pro, in dark mode, built with TailwindCSS and responsive on mobile.

## Requirements

### Requirement 1: Visual identity
#### Acceptance Criteria
1. The UI SHALL use Deep Blue `#0A192F` as the base background, Cyan `#00D4FF` as the accent and White `#FFFFFF` for primary text.
2. The UI SHALL be dark mode only.
3. Text contrast SHALL meet WCAG AA against its background.

### Requirement 2: Components
#### Acceptance Criteria
1. Cards, panels, nav and modals SHALL use a glassmorphism style (translucent background, backdrop blur, thin light border, rounded corners).
2. The UI SHALL provide consistent primary (cyan), secondary (glass) buttons and form inputs.
3. Navigation SHALL include logo, Explore, and Login or avatar menu (Profile, Admin when authorized, Logout).

### Requirement 3: Motion
#### Acceptance Criteria
1. Page elements SHALL use smooth transitions (hover, fade-in, slide-up) of about 150 to 400 ms.
2. WHEN the user prefers reduced motion THEN the system SHALL disable non-essential animation.

### Requirement 4: Responsiveness
#### Acceptance Criteria
1. All pages SHALL work from 360 px wide phones to desktop, with the navigation collapsing into a menu on small screens.
2. Touch targets SHALL be at least 44 px.
3. The viewer UI (hotspot panel, joystick, VR button) SHALL not obstruct the view on small screens and SHALL work in landscape.

### Requirement 5: Viewer overlay
#### Acceptance Criteria
1. The viewer SHALL show a loading screen with progress, a minimal HUD (back button, VR button, controls hint) and a slide-in glass hotspot panel.

### Requirement 6: Performance and accessibility
#### Acceptance Criteria
1. Pages SHALL load quickly: images lazy-loaded, no large UI libraries beyond Tailwind.
2. Interactive elements SHALL be keyboard accessible with visible focus, and images SHALL have alt text.

## Additional requirements (added during the build)
- The visual direction SHALL be "Ghost Hill after dark": navy and cyan, glass panels, drifting fog, wisps, a flickering headline, vignette and film grain, all disabled under `prefers-reduced-motion`.
- The viewer HUD SHALL stay usable on a 360 px tall landscape phone (scrollable help dialog, 44 px targets, hidden in Cardboard mode except Exit VR).
