# EXTREME UI/UX DESIGN.md

> Branch-scoped visual system for `extreme/uiux`. This does not replace the production `DESIGN.md` unless explicitly promoted later.

## 1. Visual Theme & Atmosphere

**Name:** Afterlife Ops / Control-Room Editorial

The interface should feel like a decision room for constrained rescue operations, not a generic AI SaaS dashboard. It combines operational density with editorial hierarchy.

Primary characteristics:
- dark warm-neutral canvas, never pure black
- brass as the single primary signal accent
- oversized display hierarchy for decision moments
- thin rules instead of stacked card containers
- evidence shown as ledgers, routes, and manifests
- deliberate asymmetry
- human authority remains visibly separate from model evidence

Avoid:
- purple/blue AI glow
- glass cards everywhere
- nested card stacks
- rounded-square icon tiles
- random gradients
- floating decorative widgets without operational purpose
- bounce/elastic easing

## 2. Color Palette & Roles

| Token | Value | Role |
|---|---|---|
| Canvas | `#0a0b09` | Primary background |
| Surface | `#11120f` | Work surfaces |
| Surface Raised | `#171914` | Controlled emphasis |
| Text | `#f1eee5` | Primary text |
| Muted | `#a8a399` | Supporting text |
| Dim | `#6e6b63` | Low-priority labels |
| Brass | `#c6b36a` | Primary interaction / signal |
| Brass Hot | `#e2ca78` | Hover / focus emphasis |
| Olive | `#8ca783` | Confirmed / success |
| Amber | `#d2a164` | Warning / caution |
| Clay | `#c1776d` | Error / blocked |

Color meaning must never be the only state carrier.

## 3. Typography Rules

### Display

Use a serif display stack only where the branch intentionally reads editorial:

```css
Georgia, "Times New Roman", serif
```

Use it for:
- hero statement
- major outcome values
- selected editorial mode emphasis

### Technical Labels

```css
ui-monospace, "SFMono-Regular", Consolas, monospace
```

Use it for:
- design-lab labels
- indices
- system identifiers
- compact technical context

### Product Body

Keep body copy readable and restrained. Do not make the entire interface monospace.

Rules:
- major headings use tight tracking and balanced wrapping
- paragraphs use pretty wrapping where supported
- numeric comparison values use tabular numerals
- technical labels are uppercase only when short
- long identifiers must wrap safely

## 4. Component Styling

### Operations Rail
- fixed left rail on desktop
- numeric section navigation
- active state uses brass rule + stronger text contrast
- semantic anchors only
- visible focus state required

### Signal Strip
- four compact operational truths
- thin dividers
- no rounded card shells
- text-first, no decorative icons

### Workbook Drop Surface
- large operational input area
- squared corners
- strong empty/selected/dragover state
- workbook filename stays readable under long values

### Decision Inputs
- worksheet-like underlined controls
- labels stay visible above fields
- no floating-label gimmicks
- disabled state remains distinct

### Primary Action
- squared command button
- brass fill / contrast
- purposeful scanning feedback during busy state
- no decorative infinite motion when idle

### Status Feedback
- loading, success, and error remain visually lightweight
- loading may animate the ellipsis and dot
- success remains static and calm
- async feedback stays in an `aria-live` region

### Result Metrics
- large values, small technical labels
- strong number alignment
- flat structure rather than card soup

### Allocation Blocks
- route-manifest language
- selected action, source, destination, quantity, evidence, and economics remain scannable
- no model score presented as field-calibrated probability

### Design Lab
- branch-only control
- three direction modes
- variance / motion / density dials
- state persists in URL + localStorage
- keyboard accessible

## 5. Layout Principles

Desktop:
- left operations rail
- shell up to ~1320px
- asymmetric hero
- major sections separated by rules
- section spacing controlled by live density token

Tablet:
- reduce rail dominance
- preserve data hierarchy before decorative asymmetry

Mobile:
- remove fixed rail from content flow if it competes with width
- single-column priority
- full-width touch targets where appropriate
- no horizontal page overflow
- fixed Design Lab respects safe-area insets

## 6. Depth & Elevation

Depth should come from:
1. surface tone differences
2. thin borders
3. controlled overlays
4. typography scale

Shadows are exceptional, not default. The Design Lab may use one stronger shadow because it is an overlaying tool surface.

Do not use:
- multiple nested shadows
- glowing borders
- neumorphism
- glass-on-glass surfaces

## 7. Motion Rules

Motion communicates state or spatial relationship.

Allowed:
- opacity reveal
- small translate reveal
- button press feedback
- active navigation feedback
- loading scan during an active request
- Design Lab open/close

Rules:
- keep interactions interruptible
- no `transition: all`
- prefer transform/opacity
- respect `prefers-reduced-motion`
- never move functional data continuously while a user is reading it
- animation intensity is branch-tunable through Design Lab

## 8. Responsive & Accessibility Behavior

Required:
- 320px minimum support
- visible `:focus-visible`
- labeled form controls
- semantic links/buttons
- skip link remains available
- anchored sections use `scroll-margin-top`
- fixed controls respect safe areas
- touch actions have deliberate feedback
- status updates remain announced politely
- text zoom must not clip critical labels
- serious/critical axe findings block review readiness

Target review widths:
- 375px
- 768px
- 1024px
- 1440px

## 9. Agent Prompt Guide

When modifying `extreme/uiux`, preserve these invariants:

- This is a rescue operations interface, not an AI landing page.
- Hard gates visually precede model evidence.
- Expected outcomes never masquerade as confirmed outcomes.
- Human approval remains an explicit authority boundary.
- Keep one brass accent; do not introduce purple/blue AI gradients.
- Prefer flat ledgers and route manifests over generic cards.
- Extreme does not mean noisy. Hierarchy should get stronger as decoration gets more selective.
- Every new animation must explain what changed or where attention should move.
- Every branch-level design experiment must remain reversible before merge.
