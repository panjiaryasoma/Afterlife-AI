---
version: "1.1.0"
name: "Afterlife AI Operational Editorial"
description: "Design system for a traceable, human-reviewed surplus inventory rescue, sustainability, and outcome-reconciliation workspace."
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

The interface should look like a serious decision workspace used to inspect constraints, compare alternatives, review expected impact, and reconcile operator-confirmed outcomes. It should not look like a generic AI dashboard, a chatbot, or a marketing landing page.

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
- short statement;
- a single dominant sustainability or realized-outcome measure when it materially aids interpretation.

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
- optimizer metadata;
- expected and confirmed outcome comparisons.

## 3.4 Section Labels

Section labels use uppercase sans-serif with tracking:

`01 / DECISION CONTEXT`

Keep them small and quiet. Their purpose is orientation.

---

# 4. Layout

## 4.1 Canonical Page Structure

The current production page follows one vertical workflow:

1. product identity;
2. decision context;
3. rescue summary;
4. sustainability impact + optional outcome reconciliation;
5. selected rescue plan;
6. alternatives;
7. human review;
8. evidence & provenance;
9. limitations + export.

The rendered section numbering intentionally maps this sequence to:

- `01 / DECISION CONTEXT`
- `02 / RESCUE SUMMARY`
- `03 / OUTCOME RECONCILIATION`
- `04 / SELECTED RESCUE PLAN`
- `05 / ALTERNATIVES`
- `06 / HUMAN REVIEW`
- `07 / EVIDENCE`
- `08 / LIMITATIONS`

`03 / OUTCOME RECONCILIATION` contains the expected Sustainability Summary first, then the optional operator-confirmed reconciliation workflow. Expected impact must be understandable before an operator supplies an actual outcome.

Do not introduce a sidebar unless the application gains real multi-view navigation.

## 4.2 Desktop

On desktop:

- maintain a centered max-width container;
- use large section spacing;
- allow decision controls to form two columns;
- use summary metrics in 3–4 columns;
- use split alignment inside allocation blocks;
- allow expected-vs-confirmed comparison tables only where they improve interpretation;
- keep explanatory prose within a readable measure.

## 4.3 Mobile

On mobile:

- one column;
- no horizontal body-scroll dependency;
- keep the primary CTA full-width where useful;
- place core decision information before secondary evidence;
- stack sustainability and reconciliation detail cleanly;
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

Allocation and impact blocks should normally use borders and spacing, not large shadows.

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

## 7.4 Sustainability Impact

The Sustainability Summary is expected, plan-derived output. It must remain visually distinct from operator-confirmed outcomes.

Show, when available:

- reconciled/planning quantity scope;
- expected rescue quantity;
- expected waste quantity;
- expected rescue ratio;
- mass evidence coverage: `COMPLETE`, `PARTIAL`, or `NONE`;
- expected rescue mass and expected waste mass only when coverage is `COMPLETE`.

Rules:

- label expected impact as model/plan-derived;
- never impute missing package weight;
- when package-weight evidence is incomplete, withhold complete full-batch mass claims;
- do not infer carbon, CO2, emissions, meals, trees, or other environmental proxies that the runtime does not compute.

## 7.5 Outcome Reconciliation

Outcome Reconciliation records what an operator has physically confirmed after the advisory plan exists.

Required semantics:

- actual rescued quantity;
- actual waste quantity;
- confirmed quantity;
- unresolved quantity;
- realized diversion ratio from confirmed outcomes only;
- expected-vs-confirmed rescue and waste values;
- rescue quantity delta;
- waste quantity delta.

Rules:

- actual rescued + actual waste cannot exceed the reconciliation scope;
- unresolved quantity remains unresolved rather than being guessed;
- unresolved quantity is excluded from the realized diversion ratio;
- reconciliation is stateless in the current demo;
- reconciliation must not mutate the original Rescue Decision Report;
- do not present a realized outcome when no operator-confirmed observation exists.

## 7.6 Selected Allocation

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

## 7.7 Alternatives

Show feasible candidates that were not selected by the optimizer.

Use explicit text such as:

`FEASIBLE — NOT SELECTED`

Do not visually style them as failures.

## 7.8 Human Review

Human review must be visually prominent when present.

Show:

- affected lot;
- review quantity;
- reason codes;
- approval state;
- exception wording when optimizer output is infeasible.

Do not use “Approved” unless actual human approval exists.

## 7.9 Evidence & Provenance

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

## 7.10 Limitations

Limitations must remain visible in the page.

Never hide them only in:

- modal;
- tooltip;
- footer link.

## 7.11 Export

Primary human-facing browser export:

`Download Markdown Report`

The Markdown report may include:

- canonical Rescue Decision Report values;
- Sustainability Summary;
- selected rescue plan;
- alternatives;
- operator-confirmed Outcome Reconciliation when supplied;
- Human Review;
- Evidence & Provenance;
- Limitations.

If no operator-confirmed outcome has been reconciled, the report must say so explicitly and must not infer an actual outcome.

Typed JSON remains available through the application APIs as the programmatic contract. The browser Markdown export does not replace or redefine API semantics.

Export remains secondary to analysis and review.

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

Outcome-reconciliation validation must explain when confirmed rescued + waste exceeds the allowed reconciliation scope.

## 8.3 Success

After successful analysis:

- show the Rescue Decision Report;
- show the expected Sustainability Summary;
- show a concise completion status;
- keep the input context visible;
- make Markdown export available;
- keep Outcome Reconciliation optional until the operator has confirmed actual quantities.

After successful reconciliation:

- show confirmed coverage;
- show unresolved quantity;
- show realized diversion ratio;
- show expected-vs-confirmed deltas;
- make the updated Markdown export include the confirmed outcome.

## 8.4 Empty States

Use plain language:

- `No rescue allocation selected.`
- `No lot requires manual review.`
- `No operator-confirmed outcome has been reconciled.`

Do not use celebratory empty-state illustrations.

---

# 9. Motion

Motion references may be adapted from Motion Primitives, but implemented in the current stack.

Approved:

- result section reveal;
- allocation-list stagger;
- disclosure expand/collapse;
- button/loading transition;
- subtle numeric update;
- reconciliation-result reveal after a confirmed submission.

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

Expected, confirmed, unresolved, warning, and evidence-coverage states must remain understandable without relying on color alone.

---

# 12. Decision Semantics

Visual design must preserve the distinction between:

- feasible vs blocked;
- selected vs feasible-not-selected;
- expected/model-derived impact vs operator-confirmed realized impact;
- confirmed quantity vs unresolved quantity;
- complete vs partial/none mass evidence;
- synthetic fixture vs real-world verified source;
- solver infeasible vs no candidate;
- system recommendation vs human approval;
- advisory output vs executed action.

Rules:

- `Expected rescue` is not `Actual rescued`.
- `Expected waste` is not `Actual waste`.
- `Realized diversion ratio` exists only from confirmed outcomes.
- Unresolved quantity must not be silently counted as rescued or waste.
- Full-batch mass must not be shown when package-weight evidence is `PARTIAL` or `NONE`.
- Physical action must not be implied from an advisory plan.

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

**Correct**

`Mass evidence — PARTIAL`  
`Full-batch mass withheld`

**Incorrect**

`Expected rescue mass — 18 kg`

when full package-weight coverage is not available.

---

# 13. Risk & Review States

Use consistent semantics.

## Success

Use for completed technical state, not implied physical execution.

Examples:

- `Analysis completed`
- `Outcome reconciled`

## Warning

Use for:

- review required;
- evidence weakness;
- incomplete mass evidence;
- unresolved outcome quantity;
- static/synthetic limitations.

## Danger

Use for:

- malformed input;
- blocked state;
- invalid reconciliation quantities;
- unrecoverable request failure.

## Neutral

Use for:

- feasible-not-selected;
- pending;
- metadata;
- outcome not yet reconciled.

---

# 14. Data Presentation

Prioritize:

1. decision;
2. consequence;
3. constraint;
4. provenance.

Avoid data dumping.

Use concise formatting for money and quantities in the visible UI. Human-facing Markdown may format values for readability, while typed API/JSON contracts remain the programmatic source for exact structured values.

Tables are optional, not default. The expected-vs-confirmed outcome table is appropriate because it directly answers a comparison question.

## 14.1 Chart Admission Rule

Use charts only when:

- the chart communicates a comparison, composition, threshold, or resource conflict the user must act on;
- plain values or structured text are insufficient;
- the visualization improves decision speed rather than merely increasing visual activity.

Potentially valid Afterlife AI visualizations:

- rescue vs waste composition;
- allocation by rescue action;
- value-component breakdown;
- capacity utilization or shared-resource pressure;
- expected vs confirmed outcomes, if a chart becomes clearer than the current comparison table.

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
- Preserve the same semantics and exact structured values exposed by typed API/JSON contracts.
- Prefer direct labels over requiring legend lookup when practical.
- Chart animation must not delay comprehension.
- All chart motion must respect `prefers-reduced-motion`.

---

# 15. AI / Model Provenance

Any model-derived result must remain distinguishable from deterministic rules and operator-confirmed outcomes.

The UI must make it possible to identify:

- which provider produced the score;
- that model outputs are estimates;
- whether the fixture/source is synthetic;
- whether external partner evidence is real-world verified;
- that deterministic hard gates cannot be bypassed by model output;
- that operator-confirmed actual quantities are not produced by the model.

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
- multi-column metrics;
- side-by-side impact ledger/comparison where it remains readable.

## 768–1023px

- compact desktop/tablet;
- 2-column metrics;
- stack detailed allocation metadata where needed;
- keep reconciliation inputs readable without horizontal overflow.

## < 768px

- one column;
- core decision first;
- full-width primary CTA;
- wrap badges;
- stack expected/confirmed comparison content when necessary;
- no horizontal body-scroll requirement.

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
- keep expected and realized impact visibly distinct;
- keep unresolved quantity explicit;
- withhold complete mass claims when evidence is incomplete;
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
- imply expected impact is realized impact;
- infer actual rescued/waste quantities;
- impute missing package weights for a complete batch-mass claim;
- invent carbon/CO2 or other unsupported impact proxies;
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

Primary UI files:

- `frontend/templates/index.html`
- `frontend/static/css/app.css`
- `frontend/static/css/impact.css`
- `frontend/static/js/app.js`
- `frontend/static/js/impact-ui.js`
- `frontend/static/js/report-markdown.js`

Primary browser analysis path:

`POST /api/analyze-nextstep`

Legacy compatibility path:

`POST /api/analyze`

Outcome reconciliation path:

`POST /api/outcomes/reconcile`

The UI must satisfy the existing production acceptance tests, including:

- production decision controls;
- explainability sections;
- decision-context request forwarding;
- rich report field rendering;
- typed Sustainability Summary consumption;
- evidence-bounded mass handling;
- operator-confirmed Outcome Reconciliation;
- expected-vs-realized semantic separation;
- Markdown report download.

Typed JSON remains available through API responses.

---

# 20. Pre-Delivery Checklist

Before the UI is accepted:

- [ ] Decision Context exposes all production request fields.
- [ ] Loading and error states are visible.
- [ ] Rescue Summary includes rescue/waste metrics.
- [ ] Sustainability Summary renders typed expected rescue, waste, and ratio metrics.
- [ ] Mass evidence clearly reports `COMPLETE`, `PARTIAL`, or `NONE`.
- [ ] Full-batch mass is withheld unless package-weight evidence is complete.
- [ ] Outcome inputs accept operator-confirmed rescued and waste quantities only.
- [ ] Confirmed and unresolved outcome quantities are visible after reconciliation.
- [ ] Realized diversion ratio uses confirmed outcomes only.
- [ ] Expected and realized values remain visually and semantically distinct.
- [ ] Selected allocations expose destination and explainability.
- [ ] Feasible-not-selected alternatives are visible.
- [ ] Human review state is explicit.
- [ ] Partner registry provenance is visible.
- [ ] Synthetic and real-world verification states are clear.
- [ ] Deterministic optimizer metadata is visible.
- [ ] Limitations are visible without a modal.
- [ ] Markdown report download works.
- [ ] An unreconciled report does not invent an operator-confirmed outcome.
- [ ] Typed API/JSON semantics remain unchanged by browser formatting.
- [ ] Keyboard navigation works.
- [ ] Focus indicators are visible.
- [ ] Mobile layout has no horizontal body scroll.
- [ ] Motion respects reduced-motion.
- [ ] No unsupported real-world or carbon/CO2 claim appears.
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
