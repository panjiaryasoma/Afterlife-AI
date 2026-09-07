# Extreme UI/UX Resource Convergence

Branch: `extreme/uiux`

This branch is a deliberately aggressive design laboratory. Product semantics, backend APIs, deterministic gates, model behavior, optimizer behavior, and report meaning remain out of scope. The experiment may radically change hierarchy, presentation, interaction, navigation, density, and motion.

## Resource Map

### BagUI templates
Source: https://bagui.vercel.app/templates

Applied as a composition reference, not as a framework migration. BagUI targets React + shadcn/ui + Tailwind, while Afterlife AI production is FastAPI + Jinja2 + vanilla CSS/JS. The branch therefore adapts the reusable-block philosophy instead of installing an incompatible frontend stack.

Concrete application:
- reusable operational signal strip
- high-contrast section composition
- clear hero / summary / action blocks
- component-like styling boundaries without introducing React

### Playwright
Source: https://playwright.dev/docs/intro

Applied through an isolated browser test harness under `ui-tests/`.

Coverage includes:
- desktop and mobile Chromium
- core landmark smoke test
- Design Lab keyboard reachability
- URL-synced variant state
- focus visibility
- horizontal overflow detection
- automated axe scan for serious / critical accessibility violations

The root Python runtime remains untouched by Node dependencies.

### Emil Kowalski skills
Source: https://github.com/emilkowalski/skills

Applied:
- purposeful motion only
- transform/opacity-first interaction feedback
- coarse-pointer-aware behavior inherited from the previous Emil pass
- reduced-motion handling
- strong press feedback
- explicit animation review boundaries
- prototype-style direction comparison through the Design Lab

### UI UX Pro Max
Source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

Applied:
- explicit design-system reasoning
- anti-pattern rejection
- responsive checks at desktop/tablet/mobile widths
- focus and contrast requirements
- tabular numerals for comparison-heavy data
- design direction chosen by product category rather than generic AI dashboard aesthetics
- formalized token snapshot in `design-system/extreme.tokens.json`

### Taste Skill
Source: https://github.com/Leonxlnx/taste-skill

Applied directly through branch-level design controls:
- Design Variance dial
- Motion Intensity dial
- Visual Density dial
- anti-slop preference for asymmetric composition, editorial hierarchy, and non-generic component rhythm
- three live directions: Control, Editorial, Evidence

The dials persist locally and in the URL so experiments are reproducible.

### Huashu Design
Source: https://github.com/alchaincyf/huashu-design

Applied:
- three real visual directions instead of text-only style selection
- live tweak panel
- persistent variant state
- HTML-native implementation
- branch intended for 5-dimension review: philosophy consistency, hierarchy, detail execution, functionality, innovation
- early visual comparison instead of committing immediately to one direction

### Impeccable
Source: https://github.com/pbakaus/impeccable

Applied across its strongest relevant command ideas:
- `bolder`: stronger hierarchy and composition
- `layout`: asymmetric operational layout
- `typeset`: display/technical type separation
- `animate`: purposeful state motion
- `harden`: overflow, focus, responsive, and reduced-motion handling
- `adapt`: mobile-specific behavior
- `distill`: no card-within-card explosion
- `overdrive`: branch-only Design Lab and control-room presentation

Anti-patterns explicitly avoided:
- generic purple/blue AI gradients
- rounded-square icon tiles everywhere
- nested card soup
- gratuitous bounce / elastic motion
- pure black/gray-only palette without warm tinting

### Vercel Web Interface Guidelines
Source: https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md

Applied:
- semantic controls and native anchors
- visible `:focus-visible` states
- `aria-live` status behavior retained
- reduced-motion support
- no `transition: all`
- explicit touch behavior
- safe-area-aware fixed lab controls
- `scroll-margin-top` for anchored sections
- balanced headings and pretty body wrapping
- tabular numerals
- URL state for Design Lab variants
- theme-color injection for the dark branch surface
- autocomplete disabled on non-auth decision controls

### Awesome DESIGN.md
Source: https://github.com/voltagent/awesome-design-md

Applied as documentation discipline:
- branch design language is written down instead of living only in CSS
- token roles, typography, component rules, layout principles, motion, responsive behavior, and anti-patterns are made explicit
- the design can be reviewed independently from code

### Hyperbrowser examples / skills
Source: https://github.com/hyperbrowserai/examples/tree/main/skills

Applied methodology:
- design system facts are separated from guesses
- current stack and runtime conventions are treated as evidence
- browser verification is a first-class completion gate
- generated guidance must trace to observed code or named external guidelines

No Hyperbrowser branding extraction was run in this branch because no external site was selected as an authoritative design source.

### shadcn/improve
Source: https://github.com/shadcn/improve

Applied workflow discipline:
- branch-scoped audit rather than repo-wide feature churn
- implementation boundaries recorded explicitly
- verification commands are separated from implementation claims
- browser test harness exists independently of the design implementation
- branch is expected to be reviewed against `main` before any merge decision

### extract-design-system
Source: https://github.com/arvindrk/extract-design-system

Applied by formalizing the branch design primitives into:
- `design-system/extreme.tokens.json`
- CSS custom-property driven branch styling

This is a project-derived token snapshot, not a claim that tokens were extracted from an external website.

### Superpowers
Source: https://github.com/obra/superpowers

Applied:
- isolated branch experimentation
- explicit design direction before merge
- test harness added before declaring the branch complete
- verification-before-completion rule
- evidence over claims
- main branch remains the authority boundary for release

## Current Extreme Direction

The default mode is `Control`:
- dark warm-neutral control-room canvas
- brass signal accent
- narrow persistent operations rail
- oversized editorial hierarchy
- dense but flat evidence presentation
- operational status language
- aggressive asymmetry without decorative chaos

Two alternate modes can be previewed from Design Lab:

### Editorial
More display typography, larger outcome emphasis, looser composition, lower visual resemblance to a conventional dashboard.

### Evidence
Tighter hierarchy, stronger rule system, smaller hero, provenance-first reading order, more technical labeling.

## Design Lab State

State is synchronized into URL parameters:
- `view=control|editorial|evidence`
- `variance=1..10`
- `motion=0..10`
- `density=1..10`

State also persists through `localStorage` for repeated local evaluation.

Keyboard shortcut:
- `Shift + L` toggles Design Lab
- `Escape` closes it

## Verification

Python application verification remains the repo's existing workflow.

Extreme browser verification:

```bash
cd ui-tests
npm install
npx playwright install chromium
npm test
```

The Playwright config starts the existing FastAPI app with:

```bash
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Do not claim browser verification passed until these commands have actually been run against the current branch commit.

## Merge Boundary

Nothing in this document authorizes merging `extreme/uiux` into `main`.

The branch exists to answer a narrower question first: which parts of the extreme design materially improve operator comprehension, confidence, and interaction without weakening the product's evidence boundaries?
