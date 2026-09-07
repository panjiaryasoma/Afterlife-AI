# Emil Kowalski Skills Pass

Status: experimental branch review record  
Branch: `polish/emil-skills-pass`  
Reference: `https://github.com/emilkowalski/skills`

This pass applies the repository's web-relevant design-engineering guidance without changing Afterlife AI's Operational Editorial identity, product semantics, or production stack.

## Applied skills

### `emil-design-eng`

Applied:

- immediate press feedback for primary and secondary buttons;
- pointer-aware hover behavior so touch/coarse pointers do not inherit desktop hover motion;
- existing 150 ms / 220 ms product motion tokens remain authoritative;
- stable tabular numerals for sustainability and reconciliation values;
- explicit busy feedback on the reconciliation action;
- restrained motion that supports state understanding instead of decoration.

### `animate`

Implementation choices:

- plain CSS remains the cheapest sufficient tool;
- no motion library was added;
- interaction motion stays on `transform` / `opacity` where positional motion is used;
- reconciliation result reveal uses the existing `--duration-normal` and `--ease-out` tokens;
- reduced-motion behavior removes positional motion while retaining short state feedback.

### `review-animations`

The pass specifically removes or avoids the common blockers relevant to this codebase:

- no `transition: all`;
- no `scale(0)` entrances;
- no `ease-in` UI entrance;
- no layout-property animation;
- no hover-only motion left unguarded on coarse/touch pointers;
- `prefers-reduced-motion` remains supported;
- button feedback stays below the 300 ms UI budget.

### `improve-animations`

Repo-level audit findings addressed in this branch:

1. pressable controls lacked tactile visual feedback;
2. desktop hover rules also applied to coarse/touch pointers;
3. the existing reduced-motion rule removed every transition, including useful non-positional state feedback;
4. the operator-confirmed reconciliation result appeared with no visual bridge;
5. impact values did not consistently opt into tabular numerals.

### `find-animation-opportunities`

One additive motion opportunity survived the restraint gate:

- **Outcome Reconciliation result reveal**: occasional, operator-triggered, and useful as state indication.

Candidates intentionally rejected:

- allocation-list stagger: decision data should settle immediately for reading;
- animated metric counters: decorative movement would compete with evidence scanning;
- hero entrance animation: no functional benefit in the operator workspace;
- continuous or ambient motion: inconsistent with the product's operational character;
- large file-dropzone press scaling: too much movement for a functional input surface.

### `apple-design`

Applied selectively where it agrees with Afterlife AI's product language:

- immediate response on deliberate actions;
- stable, predictable interaction states;
- touch targets already remain at or above the existing 44 px design requirement;
- size-specific typography and tabular numeric presentation remain intact;
- reduced motion keeps comprehension while removing positional movement.

Not adopted:

- glass/translucent material styling;
- gesture-heavy interaction models;
- decorative depth or spring behavior.

Those conflict with the existing flat, evidence-first Operational Editorial system.

### `animation-vocabulary`

Used as terminology/reference only. The implemented motion is described as press feedback, state indication, reveal, hover feedback, and reduced motion rather than inventing new effect names.

## Explicitly not invoked

These are on-demand or stack-specific and were intentionally left out of this pass:

- `prototype`
- `pick-ui-library`
- `ask-sonner`
- `animate-expo`
- `write-swift`

No new frontend dependency was introduced.

## Files changed

- `frontend/static/css/emil-polish.css`
- `frontend/static/js/impact-ui.js`
- `frontend/templates/index.html`
- `docs/design/EMIL_SKILLS_PASS.md`

## Merge boundary

This branch is a polish experiment. Merge only after syntax checks, regression tests, and a visual smoke test confirm that the added feedback improves the interface without changing decision semantics or creating presentation regressions.
