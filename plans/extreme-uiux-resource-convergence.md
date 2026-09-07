# Plan: Extreme UI/UX Resource Convergence

Written against branch: `extreme/uiux`

## Goal

Push the Afterlife AI interface much further than the production Operational Editorial surface while preserving all decision semantics and evidence boundaries.

## In Scope

- layout
- typography
- hierarchy
- motion
- navigation
- responsive behavior
- accessibility hardening
- browser verification
- branch-specific design documentation
- live design-direction comparison

## Out of Scope

- backend behavior
- API schemas
- triage rules
- candidate generation
- hard gates
- HGB-E scoring semantics
- expected-value math
- CP-SAT constraints/objective
- sustainability math
- outcome-reconciliation semantics
- persistence
- production deployment decisions

## Implementation Steps

### 1. Keep the branch isolated

Expected base: current `main` plus branch-only UI commits.

Verification:

```bash
git diff --name-only main...extreme/uiux
```

Expected: frontend presentation, branch design docs, design-system artifacts, and isolated UI-test files only.

### 2. Add an extreme visual system

Files:
- `frontend/static/css/extreme-ui.css`
- `frontend/static/css/extreme-convergence.css`

Done criteria:
- no product semantics encoded in CSS
- no `transition: all`
- reduced-motion path exists
- responsive path exists
- focus-visible states remain visible

### 3. Add live branch-only design comparison

File:
- `frontend/static/js/extreme-ui.js`

Done criteria:
- Control / Editorial / Evidence directions work without reload
- Variance / Motion / Density controls work
- state is represented in URL parameters
- state persists locally
- Escape closes Design Lab
- Shift+L toggles Design Lab outside editable controls
- semantic buttons and labeled range inputs only

### 4. Formalize branch design primitives

Files:
- `design-system/extreme.tokens.json`
- `docs/design/EXTREME_UIUX_RESOURCE_CONVERGENCE.md`

Done criteria:
- no claim that external tokens were extracted when they were not
- token values match branch CSS intent
- sources and adaptations are explicit

### 5. Browser verification

Files:
- `ui-tests/package.json`
- `ui-tests/playwright.config.js`
- `ui-tests/extreme-ui.spec.js`

Commands:

```bash
cd ui-tests
npm install
npx playwright install chromium
npm test
```

Expected:
- desktop Chromium pass
- mobile Chromium pass
- no serious/critical axe violations
- no horizontal page overflow
- design lab URL state pass
- visible focus test pass

STOP if Playwright discovers a serious/critical accessibility violation. Fix the UI before treating the branch as review-ready.

### 6. Existing repo verification

From repository root:

```bash
uv run python -m pytest -q
uv run ruff check .
node --check frontend/static/js/app.js
node --check frontend/static/js/impact-ui.js
node --check frontend/static/js/report-markdown.js
node --check frontend/static/js/extreme-ui.js
```

Do not report these as passing until run against the current branch commit.

## Review Gates

1. Product semantics unchanged.
2. Extreme UI is materially distinguishable from `main`.
3. UI remains keyboard navigable.
4. Mobile does not degrade into horizontal overflow.
5. Reduced motion preserves information and operation.
6. Dynamic data remains readable under long strings and high density.
7. Human authority / expected-vs-realized boundaries remain visible.
8. Browser tests actually pass before any merge discussion.

## Merge Rule

Completion of this plan does not authorize merge. Merge remains a separate user decision after visual review and verification.
