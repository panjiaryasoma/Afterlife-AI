# Afterlife AI — Brand Guidelines

**Version:** 1.1.0  
**Status:** Production UI Source of Truth  
**Project:** Afterlife AI  
**Product Type:** Operational decision-support system for surplus inventory rescue planning, sustainability reporting, and outcome reconciliation  
**Frontend:** FastAPI + Jinja2 + semantic HTML + vanilla CSS + vanilla JavaScript

---

## 1. Brand Core

### 1.1 Purpose

Afterlife AI helps transform surplus inventory into a traceable, constrained, human-reviewed rescue plan, then separates expected sustainability impact from outcomes that an operator has actually confirmed.

The product should feel like an operational decision workspace, not an autonomous AI assistant, chatbot, marketplace, or speculative “future of AI” showcase.

### 1.2 Product Promise

> Give surplus inventory another useful life.

Supporting line:

> Decision support for constrained surplus rescue.

### 1.3 Brand Character

Afterlife AI should feel:

- precise;
- calm;
- operational;
- traceable;
- resource-conscious;
- evidence-aware;
- restrained;
- technically credible;
- human-supervised.

It should not feel:

- magical;
- autonomous;
- playful;
- neon-futuristic;
- crypto-like;
- chatbot-first;
- marketing-heavy;
- overly optimistic about model certainty.

### 1.4 Brand Positioning

Afterlife AI is a **decision-support tool**.

It:

- validates and triages surplus inventory;
- applies deterministic safety and feasibility gates;
- scores only gate-eligible rescue actions;
- calculates expected economic and rescue/waste outcomes;
- optimizes allocation under shared constraints;
- surfaces selected and non-selected alternatives;
- produces an advisory Rescue Decision Report;
- produces a typed Sustainability Summary from the same planned rescue scope;
- reports mass-evidence coverage as `COMPLETE`, `PARTIAL`, or `NONE`;
- exposes full-batch rescue/waste mass only when package-weight evidence is complete;
- reconciles operator-confirmed rescued and waste quantities without mutating the original rescue plan;
- shows confirmed coverage, unresolved quantity, realized diversion ratio, and expected-vs-confirmed deltas;
- exports a human-readable Markdown report;
- keeps typed JSON available through the application APIs;
- keeps human approval as the final authority.

It does **not**:

- execute physical rescue actions automatically;
- negotiate or transact autonomously;
- infer an actual outcome that an operator has not confirmed;
- silently classify unresolved quantity as rescued or waste;
- impute missing package weights to claim complete batch mass;
- invent carbon, CO2, emissions, meals, trees, or other impact proxies the runtime does not calculate;
- persist outcome observations in the current demo;
- present synthetic estimates as real-world truth;
- claim real-world rescue probability accuracy;
- claim global optimization is superior to greedy allocation unless the registered benchmark gate is actually passed.

---

## 2. Messaging Principles

### 2.1 Voice

Use language that is:

- direct;
- concise;
- factual;
- operational;
- calm under uncertainty;
- explicit about limitations.

Prefer:

- “Estimated rescue success”
- “Human approval: Pending”
- “Synthetic-model estimate”
- “Feasible, not selected”
- “Review required”
- “Advisory report”
- “Static partner registry snapshot”
- “Sustainability Summary”
- “Expected rescue”
- “Expected waste”
- “Mass evidence: COMPLETE”
- “Mass evidence: PARTIAL”
- “Mass evidence: NONE”
- “Operator-confirmed outcome”
- “Outcome Reconciliation”
- “Unresolved quantity”
- “Realized diversion ratio”
- “Download Markdown Report”

Avoid:

- “AI-powered magic”
- “Smart rescue”
- “Autonomous optimization”
- “Guaranteed success”
- “Approved” when human review is still pending
- “Real-world probability” for synthetic-model outputs
- “Best action” when the system only selected an action under current constraints
- “Optimizer outperforms greedy” without benchmark evidence
- “Actual impact” before an operator-confirmed observation exists
- “Waste diverted” as a realized outcome when only an expected value exists
- “Carbon avoided”, “CO2 avoided”, or similar environmental claims when the runtime does not compute them.

### 2.2 Claim Discipline

Every user-facing claim must respect four boundaries:

1. **Semantic truth**  
   The wording must match what the system actually computes.
2. **Evidence truth**  
   Synthetic, static, inferred, model-derived, or incomplete-weight information must be labeled as such.
3. **Execution truth**  
   The interface must never imply an action has been physically executed unless external/operator confirmation exists.
4. **Outcome truth**  
   Expected/model-derived impact must remain separate from operator-confirmed realized impact. Unresolved quantity remains unresolved.

Additional rules:

- `Expected rescue` and `Expected waste` are planning outputs, not observed outcomes.
- `Realized diversion ratio` is calculated from confirmed outcomes only.
- Unresolved quantity is excluded from the realized diversion ratio.
- Full-batch mass is withheld when mass evidence is `PARTIAL` or `NONE`.
- Missing package weight is never silently imputed.
- Outcome reconciliation does not rewrite the original plan.

### 2.3 Preferred Labels

Use:

- `Selected Rescue Plan`
- `Alternatives Not Selected`
- `Sustainability Summary`
- `Outcome Reconciliation`
- `Human Review`
- `Evidence & Provenance`
- `Limitations`
- `Optimization Objective`
- `Expected Rescue`
- `Expected Waste`
- `Expected Rescue Ratio`
- `Expected Net Recovery`
- `Mass Evidence`
- `Expected Rescue Mass`
- `Expected Waste Mass`
- `Operator-Confirmed Outcome`
- `Confirmed Quantity`
- `Unresolved Quantity`
- `Realized Diversion Ratio`
- `Rescue Delta`
- `Waste Delta`
- `Binding Constraints`
- `Partner Registry`
- `Deterministic Execution`

Avoid vague labels such as:

- `Insights`
- `Magic`
- `AI Result`
- `Smart Recommendation`
- `Opportunity Score`
- `Optimization Power`

---

## 3. Visual Direction

### 3.1 Design Name

**Operational Editorial**

### 3.2 Visual DNA

The interface combines:

- Swiss-style discipline for structure and hierarchy;
- editorial layout for section rhythm and storytelling;
- industrial operations UI for credibility and density;
- restrained sustainability cues for material/resource context;
- minimal computational character for AI provenance.

Expected impact and confirmed outcomes should feel related but not interchangeable. Typography, labels, scope notes, and explicit evidence states should do more work than decoration.

### 3.3 Reference Hierarchy

Use references in this order:

1. **Afterlife AI product contracts and current production behavior** — functional truth.
2. **Dali AI Agency / Agent Studio** — visual mood, editorial rhythm, typography hierarchy.
3. **UI UX Pro Max** — UX, accessibility, responsive, token, and design-system reasoning.
4. **Watermelon UI** — general component anatomy and interaction references.
5. **Bklit** — data-visualization anatomy and chart interaction references.
6. **Motion Primitives** — motion references only.
7. **This file + `DESIGN.md`** — local source of truth.

External references must never override Afterlife AI semantics or introduce a framework dependency by themselves.

---

## 4. Color Identity

### 4.1 Palette Direction

The palette is a warm dark-neutral system.

It should feel closer to charcoal, paper, metal, olive, and brass than to neon software gradients.

### 4.2 Core Palette

| Role | Token | Value | Usage |
|---|---|---:|---|
| Canvas | `canvas` | `#10110E` | Main page background |
| Surface | `surface` | `#171813` | Primary content surface |
| Raised Surface | `surface-raised` | `#1E2019` | Elevated content blocks |
| Border | `border` | `#35372D` | Dividers, input outlines |
| Border Strong | `border-strong` | `#4A4B3D` | Active or emphasized boundaries |
| Text Primary | `text-primary` | `#EEECE4` | Main content |
| Text Secondary | `text-secondary` | `#B1AEA4` | Supporting copy |
| Text Tertiary | `text-tertiary` | `#7F7D74` | Metadata |
| Accent | `accent` | `#B8A767` | Primary action, focus accents |
| Accent Strong | `accent-strong` | `#D0BC78` | Hover/important accent |
| Success | `success` | `#819A79` | Positive state |
| Warning | `warning` | `#C29A62` | Review / caution |
| Danger | `danger` | `#B8756D` | Errors / blocked state |
| Synthetic | `synthetic` | `#968BAA` | Synthetic/provenance badge |

### 4.3 Color Rules

- Never use color alone to communicate status.
- All functional colors require supporting text or icons.
- Purple may only appear as a muted provenance/synthetic marker.
- No purple/pink AI gradients.
- No glowing borders.
- No decorative rainbow gradients.
- Avoid pure black and pure white as dominant surfaces.
- Test foreground/background pairs for WCAG AA contrast.
- Expected vs confirmed outcomes must not rely on color alone for distinction.

---

## 5. Typography Identity

### 5.1 Typeface Strategy

Use a maximum of two font families:

- **Editorial display family:** serif.
- **Interface/data family:** neutral sans-serif.

Typography should carry most of the visual identity. Decorative effects should not.

### 5.2 Roles

**Display Serif**

Use for:

- `Afterlife AI`
- major page title;
- major editorial statement;
- a single dominant expected or realized measure when appropriate.

Do not use for dense data or control labels.

**Interface Sans**

Use for:

- forms;
- metrics;
- allocation details;
- sustainability metadata;
- reconciliation values;
- labels;
- provenance;
- warnings;
- buttons;
- helper text;
- system metadata.

### 5.3 Numeric Treatment

Use tabular numerals for:

- quantities;
- currency;
- percentages;
- distances;
- durations;
- timestamps;
- solver metadata;
- expected-vs-confirmed comparisons.

---

## 6. Layout Philosophy

### 6.1 Page Model

The product is a **single linear decision workspace**, not a multi-page admin dashboard.

The current production sequence is:

1. Hero / product identity
2. Decision Context
3. Rescue Summary
4. Sustainability Summary + optional Outcome Reconciliation
5. Selected Rescue Plan
6. Alternatives Not Selected
7. Human Review
8. Evidence & Provenance
9. Limitations + Export

### 6.2 Hierarchy

Prefer hierarchy through:

- spacing;
- typography;
- alignment;
- section numbering;
- dividers;
- restrained contrast.

Do not solve hierarchy by placing every block inside a rounded card.

### 6.3 Section Numbering

Use the current editorial numbering:

- `01 / DECISION CONTEXT`
- `02 / RESCUE SUMMARY`
- `03 / OUTCOME RECONCILIATION`
- `04 / SELECTED RESCUE PLAN`
- `05 / ALTERNATIVES`
- `06 / HUMAN REVIEW`
- `07 / EVIDENCE`
- `08 / LIMITATIONS`

The `03 / OUTCOME RECONCILIATION` section includes expected Sustainability Summary content before the operator-confirmed reconciliation controls. Numbers are navigational rhythm, not decorative gimmicks.

---

## 7. Component Identity

### 7.1 General Rule

Components should feel like tools, not toys.

Prefer:

- clear boundaries;
- low-radius surfaces;
- precise spacing;
- text-forward hierarchy;
- minimal shadow.

Avoid:

- card-inside-card nesting;
- pill-shaped everything;
- floating glass panels;
- oversized icons;
- “dashboard tile” spam.

### 7.2 Buttons

Primary CTA:

- one primary action per main state;
- high contrast;
- clear label;
- no icon required unless it improves meaning.

Preferred primary label:

`Analyze Inventory`

Primary human-facing export label:

`Download Markdown Report`

Reconciliation action:

`Reconcile outcome`

Typed JSON remains available through APIs and should not be presented as the primary browser export.

### 7.3 Inputs

Every input must have:

- persistent visible label;
- appropriate `type`;
- helper text when domain semantics are non-obvious;
- error feedback near the field;
- visible keyboard focus.

Outcome inputs must explicitly represent operator-confirmed actual rescued and actual waste quantities.

### 7.4 Statuses

Statuses must combine text + color.

Examples:

- `OPTIMAL`
- `PENDING HUMAN APPROVAL`
- `REVIEW REQUIRED`
- `SYNTHETIC DEMO FIXTURE`
- `NOT REAL-WORLD VERIFIED`
- `FEASIBLE — NOT SELECTED`
- `MASS EVIDENCE — COMPLETE`
- `MASS EVIDENCE — PARTIAL`
- `MASS EVIDENCE — NONE`
- `OUTCOME NOT RECONCILED`
- `UNRESOLVED QUANTITY`

### 7.5 Allocation Blocks

Selected allocations should be presented as structured decision blocks, not generic cards.

Priority order:

1. action type;
2. source lot → destination;
3. quantity;
4. rescue estimate;
5. time/distance;
6. value/cost breakdown;
7. expected net recovery;
8. binding constraints.

### 7.6 Sustainability & Reconciliation Blocks

Sustainability and outcome components should read like an evidence ledger, not a celebratory “impact dashboard.”

Prioritize:

1. expected rescue scope;
2. expected rescue/waste quantities and ratio;
3. mass-evidence status;
4. mass values only when evidence is complete;
5. operator-confirmed actuals;
6. confirmed vs unresolved coverage;
7. realized diversion ratio;
8. expected-vs-confirmed deltas;
9. explicit note that actual observations are not persisted in the current demo.

Do not decorate expected impact in a way that implies it has already happened.

---

## 8. Motion Identity

Motion exists to explain state changes.

Approved motion patterns:

- subtle reveal for newly available result sections;
- staggered reveal for allocation items;
- smooth disclosure expand/collapse;
- loading state transition;
- subtle numeric transition when values update;
- restrained reveal of reconciliation results after a confirmed submission.

Avoid:

- text scramble;
- magnetic cursor;
- glowing spotlight;
- tilt;
- infinite marquee;
- parallax for decoration;
- spinning text;
- attention-seeking motion.

Default timing:

- micro-interaction: 150–200 ms;
- section state change: 200–300 ms;
- exit should be faster than enter.

Only animate `transform` and `opacity` where possible.

Always respect `prefers-reduced-motion`.

---

## 9. Data Visualization

### 9.1 Reference Source

Use **Bklit** as the primary external reference for chart and data-visualization composition.

Use it for:

- chart anatomy;
- axis and legend treatment;
- tooltip behavior;
- reference lines / thresholds;
- density and spacing;
- accessible visual hierarchy.

Do not introduce Bklit, React, shadcn, or another UI framework as a production dependency solely to reuse a chart.

### 9.2 Chart Admission Rule

A chart may be added only when it answers a decision question more clearly than direct numbers or structured text.

Potential valid uses:

- rescue vs waste composition;
- allocation by rescue action;
- value-component breakdown;
- capacity utilization or shared-resource pressure;
- expected vs confirmed outcomes when a chart becomes clearer than the comparison table.

A chart is not required merely because the product contains data.

### 9.3 Chart Rules

- No decorative charts.
- No chart if plain numbers communicate the decision faster.
- Never encode critical meaning by color alone.
- Labels, legends, and units must be explicit.
- Use the same semantic color tokens as the rest of the product.
- Avoid 3D charts, ornamental gradients, and excessive animation.
- Preserve the semantics and exact structured values available from typed API/JSON contracts.
- The human-facing Markdown report may format values for readability but must not alter their meaning.
- Motion must remain secondary to interpretation.

---

## 10. Accessibility

Minimum requirements:

- WCAG AA contrast for normal text;
- visible keyboard focus;
- semantic heading order;
- visible form labels;
- keyboard-operable actions;
- no hover-only information;
- `aria-live` for async status/error output;
- 44px minimum interactive target height where practical;
- no horizontal page scroll on mobile;
- no color-only semantics;
- zoom must remain enabled;
- reduced-motion support.

Expected, confirmed, unresolved, and evidence-coverage states must remain understandable without color.

Accessibility is a release gate, not a polish task.

---

## 11. Responsive Identity

Breakpoints:

- ~375px: compact mobile
- ~768px: tablet / narrow laptop
- ~1024px: desktop
- ~1440px: wide desktop

Behavior:

**Mobile**
- one column;
- core decision information first;
- stack impact and reconciliation fields;
- secondary provenance may collapse;
- no horizontal body-scroll dependency.

**Tablet**
- two-column form groups where appropriate;
- metrics may use 2 columns;
- reconciliation details may stack where needed.

**Desktop**
- editorial wide layout;
- summary may use 3–4 columns;
- allocation detail can use split columns;
- impact ledger and expected-vs-confirmed comparison may use wider layouts where readable.

---

## 12. Imagery, Iconography & Brand Assets

### 12.1 Imagery

The core application does not require decorative imagery.

If imagery is introduced:

- it must support the surplus/resource-rescue story;
- use restrained documentary/material or operational-artifact imagery;
- avoid stock “AI brain”, robot, glowing network, or futuristic city imagery;
- avoid invented environmental impact symbols that imply unsupported claims.

Submission-facing campaign imagery may use the **Freight Rerouting Manifest** visual metaphor when it remains clearly illustrative and does not introduce fake product metrics.

### 12.2 Icons

Use one consistent SVG icon family if interface icons become necessary.

Preferred qualities:

- outline or sharp;
- simple geometry;
- consistent stroke weight.

Do not use emojis as interface icons.

### 12.3 Brand Assets

Current repository assets:

| Asset | Path | Primary use |
|---|---|---|
| Afterlife AI icon | `frontend/static/images/afterlife-ai-icon.png` | favicon, compact mark, small identity contexts |
| Full Afterlife AI logo | `frontend/static/images/logo.png` | README, brand lockup, larger identity contexts |
| Submission thumbnail | `thumbnail.png` | Devpost/project-card and competition-facing thumbnail |

Asset rules:

- Treat the existing Afterlife AI icon as the canonical mark; do not redraw it into a different symbol casually.
- Preserve the mark's reroute-arrow idea and warm neutral/brass identity.
- Do not stretch, skew, crop through, or arbitrarily recolor the icon or full logo.
- Use the compact icon where wordmark readability would be poor.
- Use the full logo where horizontal space and hierarchy support it.
- The submission thumbnail is campaign artwork, not a substitute for the application favicon or compact product mark.
- Do not replace these assets with a generic leaf, robot, recycle symbol, brain, sparkle, or abstract AI mark.

---

## 13. Do / Don't

### Do

- use whitespace as primary hierarchy;
- use section numbering consistently;
- use tabular numerals for data;
- show provenance near model-derived outputs;
- state synthetic status explicitly;
- keep expected and realized impact separate;
- keep unresolved quantity explicit;
- expose mass-evidence coverage;
- withhold complete mass claims when evidence is incomplete;
- preserve human-review boundaries;
- surface feasible-not-selected alternatives;
- expose constraint reasons in plain language;
- use the approved brand assets consistently;
- keep the happy path short;
- keep the interface useful without animation.

### Don't

- use “AI-powered” as filler;
- add decorative charts;
- hide limitations in a modal;
- imply automatic execution;
- imply synthetic estimates are observed outcomes;
- imply expected impact is realized impact;
- infer actual outcomes;
- turn unresolved quantity into rescued/waste without confirmation;
- impute missing package weight for complete mass claims;
- invent carbon/CO2 or other unsupported environmental metrics;
- add a chatbot just to make the product look more “AI”;
- add a sidebar without a real navigation need;
- add a framework dependency only for aesthetics;
- use gradients as the primary visual identity;
- make every section a rounded card;
- redraw the canonical icon without a deliberate brand revision;
- copy external components without adapting them to the current stack.

---

## 14. Brand Review Checklist

Before accepting a UI or brand change:

- [ ] Does the screen still feel like an operational decision workspace?
- [ ] Are human-review boundaries explicit?
- [ ] Are synthetic/model-derived values labeled accurately?
- [ ] Are expected and operator-confirmed realized outcomes clearly separated?
- [ ] Does unresolved quantity remain explicit rather than guessed?
- [ ] Is mass-evidence coverage visible and truthful?
- [ ] Are complete batch-mass values withheld unless evidence is complete?
- [ ] Is there only one dominant primary action per main state?
- [ ] Is hierarchy created by type/space/layout rather than card spam?
- [ ] Does the palette remain warm, restrained, and non-neon?
- [ ] Are data values easy to scan?
- [ ] Are warnings readable without relying on color alone?
- [ ] Does the page work without animation?
- [ ] Does the page remain understandable at mobile width?
- [ ] Are the canonical icon/logo assets used consistently?
- [ ] Are external inspirations adapted rather than copied?
- [ ] Are all user-facing claims supported by actual system behavior?
- [ ] Are carbon/CO2 or other unsupported impact proxies absent?
- [ ] Does the primary browser export remain the human-readable Markdown report?

---

## 15. External References

These references inform the design process but do not override this document:

- Dali AI Agency / Agent Studio template: https://21st.dev/@lyanchouss/templates/dali-ai-agency-agent-studio-site
- UI UX Pro Max: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Watermelon UI: https://ui.watermelon.sh/home
- Bklit: https://bklit.com/
- Motion Primitives: https://motion-primitives.com/
