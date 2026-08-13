---
version: "1.0.1"
name: "Afterlife AI Operational Editorial"
description: "Design system for a traceable, human-reviewed surplus inventory rescue decision workspace."
status: "production-ui-source-of-truth"

colors:
  primitive:
    charcoal-950: "#10110E"
    charcoal-900: "#171813"
    charcoal-850: "#1E2019"
    charcoal-700: "#35372D"
    charcoal-600: "#4A4B3D"
    ivory-100: "#EEECE4"
    stone-300: "#B1AEA4"
    stone-500: "#7F7D74"
    brass-400: "#B8A767"
    brass-300: "#D0BC78"
    olive-400: "#819A79"
    amber-400: "#C29A62"
    clay-400: "#B8756D"
    violet-muted-400: "#968BAA"

  semantic:
    canvas: "{colors.primitive.charcoal-950}"
    surface: "{colors.primitive.charcoal-900}"
    surface-raised: "{colors.primitive.charcoal-850}"
    border: "{colors.primitive.charcoal-700}"
    border-strong: "{colors.primitive.charcoal-600}"
    text-primary: "{colors.primitive.ivory-100}"
    text-secondary: "{colors.primitive.stone-300}"
    text-tertiary: "{colors.primitive.stone-500}"
    interactive: "{colors.primitive.brass-400}"
    interactive-hover: "{colors.primitive.brass-300}"
    success: "{colors.primitive.olive-400}"
    warning: "{colors.primitive.amber-400}"
    danger: "{colors.primitive.clay-400}"
    synthetic: "{colors.primitive.violet-muted-400}"

typography:
  families:
    display: "Georgia, 'Times New Roman', serif"
    interface: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

  display:
    fontFamily: "{typography.families.display}"
    fontSize: "clamp(2.75rem, 7vw, 5.75rem)"
    fontWeight: 500
    lineHeight: 0.95
    letterSpacing: "-0.035em"

  h2:
    fontFamily: "{typography.families.interface}"
    fontSize: "clamp(1.5rem, 3vw, 2.25rem)"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.02em"

  h3:
    fontFamily: "{typography.families.interface}"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.3

  body:
    fontFamily: "{typography.families.interface}"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6

  small:
    fontFamily: "{typography.families.interface}"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5

  label:
    fontFamily: "{typography.families.interface}"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.12em"
    textTransform: "uppercase"

  data:
    fontFamily: "{typography.families.interface}"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.35
    fontVariantNumeric: "tabular-nums"

spacing:
  base: "4px"
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
  section: "96px"

rounded:
  xs: "2px"
  sm: "4px"
  md: "8px"
  lg: "12px"
  pill: "999px"

elevation:
  none: "none"
  subtle: "0 1px 0 rgba(255,255,255,0.025)"
  floating: "0 18px 40px rgba(0,0,0,0.24)"

motion:
  duration-fast: "150ms"
  duration-normal: "220ms"
  duration-slow: "300ms"
  easing-enter: "cubic-bezier(0.16, 1, 0.3, 1)"
  easing-exit: "cubic-bezier(0.7, 0, 0.84, 0)"

layout:
  maxWidth: "1180px"
  contentWidth: "760px"
  pagePaddingMobile: "20px"
  pagePaddingTablet: "32px"
  pagePaddingDesktop: "48px"
  breakpointSm: "375px"
  breakpointMd: "768px"
  breakpointLg: "1024px"
  breakpointXl: "1440px"

components:
  primary-button:
    backgroundColor: "{colors.semantic.interactive}"
    hoverBackgroundColor: "{colors.semantic.interactive-hover}"
    textColor: "{colors.primitive.charcoal-950}"
    rounded: "{rounded.sm}"
    minHeight: "44px"
    paddingInline: "20px"
    transition: "{motion.duration-fast} {motion.easing-enter}"

  secondary-button:
    backgroundColor: "transparent"
    borderColor: "{colors.semantic.border-strong}"
    textColor: "{colors.semantic.text-primary}"
    rounded: "{rounded.sm}"
    minHeight: "44px"
    paddingInline: "18px"

  input:
    backgroundColor: "{colors.semantic.surface}"
    borderColor: "{colors.semantic.border}"
    textColor: "{colors.semantic.text-primary}"
    rounded: "{rounded.sm}"
    minHeight: "46px"
    focusColor: "{colors.semantic.interactive}"

  section-rule:
    borderColor: "{colors.semantic.border}"
    thickness: "1px"

  allocation-block:
    backgroundColor: "transparent"
    borderColor: "{colors.semantic.border}"
    rounded: "{rounded.xs}"
    padding: "{spacing.lg}"

  status-badge:
    rounded: "{rounded.pill}"
    font: "{typography.label}"
    borderColor: "{colors.semantic.border-strong}"

  provenance-panel:
    backgroundColor: "{colors.semantic.surface}"
    borderColor: "{colors.semantic.border}"
    rounded: "{rounded.sm}"
    padding: "{spacing.lg}"
---

# 1. Overview

Afterlife AI uses an **Operational Editorial** design language.

The interface should look like a serious decision workspace used to inspect constraints, compare alternatives, and review evidence. It should not look like a generic AI dashboard, a chatbot, or a marketing landing page.

Primary visual characteristics:

- dark warm-neutral canvas;
- editorial section rhythm;
- strong typography;
- medium-high information density;
- low decorative complexity;
- precise dividers;
- restrained use of cards;
- explicit status semantics;
- minimal purposeful motion.

The visual hierarchy is created mainly through typography, spacing, alignment, section numbers, and rules.

---

# 2. Colors

## 2.1 Palette Intent

The palette represents:

- charcoal / operational surfaces;
- paper / readable foreground;
- brass / decision and action;
- olive / successful rescue state;
- amber / review and caution;
- clay / failure or blocking;
- muted violet / synthetic provenance only.

## 2.2 Functional Rules

- Never use raw colors in components when a semantic token exists.
- Never use status color without a textual label.
- `synthetic` must only mark synthetic/provenance semantics.
- Do not use purple/pink gradients.
- Do not add additional accent colors casually.
- Add new palette entries here before using them in code.

---

# 3. Typography

## 3.1 Display

Use the display serif only for strong editorial moments:

- product name;
- page headline;
- short statement.

Do not use serif for dense metrics or input labels.

## 3.2 Interface

Use the interface sans for all operational content.

## 3.3 Data

Use tabular numerals for:

- quantities;
- percentages;
- prices;
- distances;
- durations;
- timestamps;
- optimizer metadata.

## 3.4 Section Labels

Section labels use uppercase sans-serif with tracking:

`01 / DECISION CONTEXT`

Keep them small and quiet. Their purpose is orientation.

---

# 4. Layout

## 4.1 Canonical Page Structure

The final page follows one vertical workflow:

1. product identity;
2. decision context;
3. rescue summary;
4. selected rescue plan;
5. alternatives;
6. human review;
7. evidence & provenance;
8. limitations + export.

Do not introduce a sidebar unless the application gains real multi-view navigation.

## 4.2 Desktop

On desktop:

- maintain a centered max-width container;
- use large section spacing;
- allow decision controls to form two columns;
- use summary metrics in 3–4 columns;
- use split alignment inside allocation blocks;
- keep explanatory prose within a readable measure.

## 4.3 Mobile

On mobile:

- one column;
- no horizontal table dependency;
- keep the primary CTA full-width where useful;
- place core decision information before secondary evidence;
- allow provenance detail to collapse;
- retain limitations as visible content.

## 4.4 Grid

Use grid only when the content actually benefits from alignment.

Do not turn every section into a bento grid.

---

# 5. Elevation & Depth

Use mostly flat surfaces.

Approved depth hierarchy:

1. Canvas
2. Surface
3. Raised surface
4. Floating only for temporary overlays if added later

Allocation blocks should normally use borders and spacing, not large shadows.

Avoid:

- glassmorphism;
- glow;
- stacked floating cards;
- random shadow values.

---

# 6. Shapes

Preferred radii are restrained:

- 2–4px for structural blocks;
- 4–8px for inputs/buttons;
- 999px only for compact badges.

Avoid large 16–32px “soft SaaS” radii.

Use sharp geometry when it improves the operational/editorial character.

---

# 7. Components

## 7.1 Hero

The hero is brief.

Target height: approximately 20–30vh, not a full-screen marketing hero.

Content:

- `Afterlife AI`
- concise product statement
- optional system status

No decorative 3D or WebGL requirement.

## 7.2 Decision Context Form

Required controls:

- inventory XLSX;
- optimization objective;
- max logistics budget;
- minimum expected rescue ratio;
- rescue deadline.

Every field requires:

- visible label;
- helper text where semantics are not obvious;
- visible error state;
- keyboard focus.

The form has one dominant CTA:

`Analyze Inventory`

## 7.3 Rescue Summary

Required summary values:

- planning quantity;
- allocated quantity;
- unallocated quantity;
- expected physical rescue quantity;
- expected waste quantity;
- expected rescue ratio;
- expected economic value;
- optimization solver status.

The summary is data-first.

Do not use charts unless a chart answers a decision question better than numbers.

## 7.4 Selected Allocation

Each selected allocation must show, where available:

- action type;
- source lot;
- destination identifier/type;
- allocated quantity;
- estimated rescue success score;
- completion time;
- distance;
- direct cost;
- logistics cost;
- handling cost;
- expected cash recovery;
- expected future branch recovery;
- expected avoided purchase cost;
- expected physical rescue quantity;
- expected waste quantity;
- expected net recovery;
- binding constraint codes.

The reading order must prioritize the decision before the supporting detail.

## 7.5 Alternatives

Show feasible candidates that were not selected by the optimizer.

Use explicit text such as:

`FEASIBLE — NOT SELECTED`

Do not visually style them as failures.

## 7.6 Human Review

Human review must be visually prominent when present.

Show:

- affected lot;
- review quantity;
- reason codes;
- approval state;
- exception wording when optimizer output is infeasible.

Do not use “Approved” unless actual human approval exists.

## 7.7 Evidence & Provenance

Evidence is secondary but easily accessible.

Show:

- scoring provider;
- score type;
- model/provider provenance;
- partner registry snapshot ID;
- partner registry source type;
- real-world verification flag;
- deterministic execution flag;
- optimizer random seed;
- optimizer search-worker count;
- relevant ruleset/capability versions.

Use explicit labels:

- `SYNTHETIC DEMO FIXTURE`
- `NOT REAL-WORLD VERIFIED`
- `DETERMINISTIC`

## 7.8 Limitations

Limitations must remain visible in the page.

Never hide them only in:

- modal;
- tooltip;
- footer link.

## 7.9 Export

Primary export:

`Download JSON Report`

Export is secondary to analysis.

---

# 8. Interaction & Feedback

## 8.1 Submit

While analyzing:

- disable the submit button;
- show visible progress/state text;
- keep the page stable;
- do not fake progress percentages.

## 8.2 Error

Errors must state:

1. what failed;
2. what the user can do next.

Place field-specific validation near the relevant input where possible.

## 8.3 Success

After successful analysis:

- show the report;
- show a concise completion status;
- keep the input context visible;
- make JSON export available.

## 8.4 Empty States

Use plain language:

- `No rescue allocation selected.`
- `No lot requires manual review.`

Do not use celebratory empty-state illustrations.

---

# 9. Motion

Motion references may be adapted from Motion Primitives, but implemented in the current stack.

Approved:

- result section reveal;
- allocation-list stagger;
- disclosure expand/collapse;
- button/loading transition;
- subtle numeric update.

Rules:

- 150–300ms;
- `transform`/`opacity` preferred;
- no decorative infinite animation;
- animation must remain interruptible;
- interface remains usable without motion;
- respect `prefers-reduced-motion`.

Forbidden:

- magnetic cursor;
- tilt;
- spotlight glow;
- text scramble;
- marquee;
- spinning text;
- parallax decoration.

---

# 10. Component Reference Policy

Watermelon UI may be used as a component reference.

Use it for:

- component anatomy;
- spacing;
- interaction states;
- content grouping;
- visual treatment.

Do not copy framework dependencies into Afterlife AI merely to reuse a component.

Translate references to:

- semantic HTML;
- vanilla CSS;
- vanilla JS;
- existing FastAPI/Jinja2 architecture.

External component design never overrides product semantics.

---

# 11. Accessibility

Release requirements:

- normal text contrast >= 4.5:1;
- large text contrast >= 3:1;
- visible keyboard focus;
- semantic heading order;
- persistent form labels;
- no color-only state;
- keyboard-operable controls;
- `aria-live` for async status;
- no horizontal body scrolling;
- mobile body text >= 16px;
- touch targets near or above 44px;
- zoom enabled;
- `prefers-reduced-motion` respected.

---

# 12. Decision Semantics

Visual design must preserve the distinction between:

- feasible vs blocked;
- selected vs feasible-not-selected;
- rescue estimate vs observed outcome;
- synthetic fixture vs real-world verified source;
- solver infeasible vs no candidate;
- system recommendation vs human approval;
- advisory output vs executed action.

Examples:

**Correct**

`Estimated rescue success — 89%`  
`Synthetic-model estimate`

**Incorrect**

`Success probability — 89%`

**Correct**

`Human approval — PENDING`

**Incorrect**

`Approved`

**Correct**

`FEASIBLE — NOT SELECTED`

**Incorrect**

`Rejected`

when the candidate was not blocked.

---

# 13. Risk & Review States

Use consistent semantics.

## Success

Use for completed technical state, not implied physical execution.

Example:

`Analysis completed`

## Warning

Use for:

- review required;
- evidence weakness;
- static/synthetic limitations.

## Danger

Use for:

- malformed input;
- blocked state;
- unrecoverable request failure.

## Neutral

Use for:

- feasible-not-selected;
- pending;
- metadata.

---

# 14. Data Presentation

Prioritize:

1. decision;
2. consequence;
3. constraint;
4. provenance.

Avoid data dumping.

Use concise formatting for money and quantities in the visible UI while preserving exact values in downloaded JSON.

Tables are optional, not default.

## 14.1 Chart Admission Rule

Use charts only when:

- the chart communicates a comparison, composition, threshold, or resource conflict the user must act on;
- plain values or structured text are insufficient;
- the visualization improves decision speed rather than merely increasing visual activity.

Potentially valid Afterlife AI visualizations:

- rescue vs waste composition;
- allocation by rescue action;
- value-component breakdown;
- capacity utilization or shared-resource pressure.

No chart is required for the MVP by default.

## 14.2 Chart Reference

Use **Bklit** as the primary external reference for data-visualization anatomy.

Borrow only:

- chart composition;
- axis and legend treatment;
- tooltip hierarchy;
- threshold/reference-line patterns;
- information density;
- interaction and motion treatment.

Do not introduce Bklit, React, shadcn, or another framework dependency solely to reuse a chart.

## 14.3 Chart Semantics

- No decorative charts.
- No 3D charts.
- No ornamental gradients.
- Never encode critical meaning by color alone.
- Units and labels must remain explicit.
- Use existing semantic design tokens for chart colors.
- Preserve exact values in the downloadable JSON report.
- Prefer direct labels over requiring legend lookup when practical.
- Chart animation must not delay comprehension.
- All chart motion must respect `prefers-reduced-motion`.

---

# 15. AI / Model Provenance

Any model-derived result must remain distinguishable from deterministic rules.

The UI must make it possible to identify:

- which provider produced the score;
- that model outputs are estimates;
- whether the fixture/source is synthetic;
- whether external partner evidence is real-world verified;
- that deterministic hard gates cannot be bypassed by model output.

Do not personify the model.

---

# 16. Responsive Behavior

## >= 1440px

- wide editorial composition;
- no unnecessary stretching;
- keep readable text measure.

## 1024–1439px

- standard desktop;
- two-column decision context;
- multi-column metrics.

## 768–1023px

- compact desktop/tablet;
- 2-column metrics;
- stack detailed allocation metadata where needed.

## < 768px

- one column;
- core decision first;
- full-width primary CTA;
- wrap badges;
- no horizontal data table requirement.

---

# 17. Performance

The UI should remain lightweight.

Prefer:

- local CSS;
- local JavaScript;
- no runtime UI framework;
- no unnecessary animation library;
- no heavy hero media;
- no blocking font waterfall.

If external fonts are introduced later:

- use `font-display: swap` or `optional`;
- preload only critical variants;
- provide robust fallback stacks.

---

# 18. Do's and Don'ts

## Do

- use whitespace intentionally;
- use section numbering;
- use semantic HTML;
- use design tokens;
- use tabular numerals;
- keep provenance visible;
- surface alternatives and review states;
- preserve human authority;
- make the happy path obvious;
- adapt references to the current stack.

## Don't

- add React/Tailwind just for a borrowed component;
- add Streamlit as a second UI;
- use AI purple/pink gradients;
- use emojis as interface icons;
- use glassmorphism;
- use glowing borders;
- use card-inside-card nesting;
- add fake AI chat;
- add charts without a decision purpose;
- imply synthetic evidence is real-world;
- imply automatic execution;
- hide limitations;
- claim optimizer superiority without evidence.

---

# 19. Implementation Contract

Current production implementation remains:

- FastAPI;
- Jinja2;
- semantic HTML;
- vanilla CSS;
- vanilla JavaScript.

Primary files:

- `frontend/templates/index.html`
- `frontend/static/css/app.css`
- `frontend/static/js/app.js`

The UI must satisfy the existing production acceptance tests, including:

- production decision controls;
- explainability sections;
- decision-context request forwarding;
- rich report field rendering;
- JSON report download.

---

# 20. Pre-Delivery Checklist

Before the UI is accepted:

- [ ] Decision Context exposes all production request fields.
- [ ] Loading and error states are visible.
- [ ] Rescue Summary includes rescue/waste metrics.
- [ ] Selected allocations expose destination and explainability.
- [ ] Feasible-not-selected alternatives are visible.
- [ ] Human review state is explicit.
- [ ] Partner registry provenance is visible.
- [ ] Synthetic and real-world verification states are clear.
- [ ] Deterministic optimizer metadata is visible.
- [ ] Limitations are visible without a modal.
- [ ] JSON report download works.
- [ ] Keyboard navigation works.
- [ ] Focus indicators are visible.
- [ ] Mobile layout has no horizontal body scroll.
- [ ] Motion respects reduced-motion.
- [ ] No unsupported real-world claim appears.
- [ ] No dependency was added solely for aesthetics.
- [ ] Automated UI tests pass.

---

# 21. External Design References

Visual / editorial:
- https://21st.dev/@lyanchouss/templates/dali-ai-agency-agent-studio-site

Design intelligence:
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

Component references:
- https://ui.watermelon.sh/home

Data visualization references:
- https://bklit.com/

Motion references:
- https://motion-primitives.com/
