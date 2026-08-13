# Afterlife AI — Brand Guidelines

**Version:** 1.0.1  
**Status:** Production UI Source of Truth  
**Project:** Afterlife AI  
**Product Type:** Operational decision-support system for surplus inventory rescue planning  
**Frontend:** FastAPI + Jinja2 + semantic HTML + vanilla CSS + vanilla JavaScript

---

## 1. Brand Core

### 1.1 Purpose

Afterlife AI helps transform surplus inventory into a traceable, constrained, human-reviewed rescue plan.

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
- scores feasible rescue actions;
- optimizes allocation under shared constraints;
- surfaces selected and rejected alternatives;
- produces an advisory Rescue Decision Report;
- keeps human approval as the final authority.

It does **not**:

- execute physical rescue actions automatically;
- negotiate or transact autonomously;
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

Avoid:

- “AI-powered magic”
- “Smart rescue”
- “Autonomous optimization”
- “Guaranteed success”
- “Approved” when human review is still pending
- “Real-world probability” for synthetic-model outputs
- “Best action” when the system only selected an action under current constraints
- “Optimizer outperforms greedy” without benchmark evidence

### 2.2 Claim Discipline

Every user-facing claim must respect three boundaries:

1. **Semantic truth**  
   The wording must match what the system actually computes.
2. **Evidence truth**  
   Synthetic, static, inferred, or model-derived information must be labeled as such.
3. **Execution truth**  
   The interface must never imply an action has been physically executed unless external execution evidence exists.

### 2.3 Preferred Labels

Use:

- `Selected Rescue Plan`
- `Alternatives Not Selected`
- `Human Review`
- `Evidence & Provenance`
- `Limitations`
- `Optimization Objective`
- `Expected Rescue`
- `Expected Waste`
- `Expected Rescue Ratio`
- `Expected Net Recovery`
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

### 3.3 Reference Hierarchy

Use references in this order:

1. **Afterlife AI product contracts and Issue 7 requirements** — functional truth.
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
- major editorial statement.

Do not use for dense data or control labels.

**Interface Sans**

Use for:

- forms;
- metrics;
- allocation details;
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
- solver metadata.

---

## 6. Layout Philosophy

### 6.1 Page Model

The product is a **single linear decision workspace**, not a multi-page admin dashboard.

The canonical sequence is:

1. Hero / product identity
2. Decision Context
3. Rescue Summary
4. Selected Rescue Plan
5. Alternatives Not Selected
6. Human Review
7. Evidence & Provenance
8. Limitations + Export

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

Use consistent editorial numbering:

- `01 / DECISION CONTEXT`
- `02 / RESCUE SUMMARY`
- `03 / SELECTED RESCUE PLAN`
- `04 / ALTERNATIVES`
- `05 / HUMAN REVIEW`
- `06 / EVIDENCE`
- `07 / LIMITATIONS`

Numbers are navigational rhythm, not decorative gimmicks.

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

Secondary:

`Download JSON Report`

### 7.3 Inputs

Every input must have:

- persistent visible label;
- appropriate `type`;
- helper text when domain semantics are non-obvious;
- error feedback near the field;
- visible keyboard focus.

### 7.4 Statuses

Statuses must combine text + color.

Examples:

- `OPTIMAL`
- `PENDING HUMAN APPROVAL`
- `REVIEW REQUIRED`
- `SYNTHETIC DEMO FIXTURE`
- `NOT REAL-WORLD VERIFIED`
- `FEASIBLE — NOT SELECTED`

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

---

## 8. Motion Identity

Motion exists to explain state changes.

Approved motion patterns:

- subtle reveal for newly available result sections;
- staggered reveal for allocation items;
- smooth disclosure expand/collapse;
- loading state transition;
- subtle numeric transition when values update.

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
- capacity utilization or shared-resource pressure.

A chart is not required merely because the product contains data.

### 9.3 Chart Rules

- No decorative charts.
- No chart if plain numbers communicate the decision faster.
- Never encode critical meaning by color alone.
- Labels, legends, and units must be explicit.
- Use the same semantic color tokens as the rest of the product.
- Avoid 3D charts, ornamental gradients, and excessive animation.
- Preserve exact values in the JSON report even if visible labels are abbreviated.
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
- secondary provenance may collapse;
- no horizontal table dependency.

**Tablet**
- two-column form groups where appropriate;
- metrics may use 2 columns.

**Desktop**
- editorial wide layout;
- summary may use 3–4 columns;
- allocation detail can use split columns.

---

## 12. Imagery & Iconography

### 12.1 Imagery

The core application does not require decorative imagery.

If imagery is introduced:

- it must support the surplus/resource-rescue story;
- use restrained documentary/material imagery;
- avoid stock “AI brain”, robot, glowing network, or futuristic city imagery.

### 12.2 Icons

Use one consistent SVG icon family if icons become necessary.

Preferred qualities:

- outline or sharp;
- simple geometry;
- consistent stroke weight.

Do not use emojis as interface icons.

---

## 13. Do / Don't

### Do

- use whitespace as primary hierarchy;
- use section numbering consistently;
- use tabular numerals for data;
- show provenance near model-derived outputs;
- state synthetic status explicitly;
- preserve human-review boundaries;
- surface rejected alternatives;
- expose constraint reasons in plain language;
- keep the happy path short;
- keep the interface useful without animation.

### Don't

- use “AI-powered” as filler;
- add decorative charts;
- hide limitations in a modal;
- imply automatic execution;
- imply synthetic estimates are observed outcomes;
- add a chatbot just to make the product look more “AI”;
- add a sidebar without a real navigation need;
- add a framework dependency only for aesthetics;
- use gradients as the primary visual identity;
- make every section a rounded card;
- copy external components without adapting them to the current stack.

---

## 14. Brand Review Checklist

Before accepting a UI change:

- [ ] Does the screen still feel like an operational decision workspace?
- [ ] Are human-review boundaries explicit?
- [ ] Are synthetic/model-derived values labeled accurately?
- [ ] Is there only one dominant primary action?
- [ ] Is hierarchy created by type/space/layout rather than card spam?
- [ ] Does the palette remain warm, restrained, and non-neon?
- [ ] Are data values easy to scan?
- [ ] Are warnings readable without relying on color alone?
- [ ] Does the page work without animation?
- [ ] Does the page remain understandable at mobile width?
- [ ] Are external inspirations adapted rather than copied?
- [ ] Are all user-facing claims supported by actual system behavior?

---

## 15. External References

These references inform the design process but do not override this document:

- Dali AI Agency / Agent Studio template: https://21st.dev/@lyanchouss/templates/dali-ai-agency-agent-studio-site
- UI UX Pro Max: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Watermelon UI: https://ui.watermelon.sh/home
- Bklit: https://bklit.com/
- Motion Primitives: https://motion-primitives.com/
