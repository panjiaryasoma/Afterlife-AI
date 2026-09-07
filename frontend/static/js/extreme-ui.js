(() => {
    const body = document.body;

    if (!body.classList.contains("extreme-ui")) {
        return;
    }

    const reduceMotionQuery = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    const reduceMotion = reduceMotionQuery.matches;
    const root = document.documentElement;
    const storageKey = "afterlife-extreme-lab";

    function ensureStyle(href, marker) {
        if (document.querySelector(`link[data-${marker}="true"]`)) {
            return;
        }

        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = href;
        link.setAttribute(`data-${marker}`, "true");
        document.head.appendChild(link);
    }

    function ensureExtremeStyles() {
        ensureStyle(
            "/static/css/extreme-convergence.css",
            "extreme-convergence"
        );
        ensureStyle(
            "/static/css/extreme-compliance.css",
            "extreme-compliance"
        );
    }

    function ensureThemeColor() {
        let themeColor = document.querySelector('meta[name="theme-color"]');

        if (!themeColor) {
            themeColor = document.createElement("meta");
            themeColor.name = "theme-color";
            document.head.appendChild(themeColor);
        }

        themeColor.content = "#0a0b09";
    }

    function hardenFormDefaults() {
        document
            .querySelectorAll(
                "#analysis-form input:not([type='file']), #analysis-form select"
            )
            .forEach((control) => {
                control.setAttribute("autocomplete", "off");
            });
    }

    ensureExtremeStyles();
    ensureThemeColor();
    hardenFormDefaults();

    const railLinks = [...document.querySelectorAll(".ops-rail__link")];
    const observedTargets = new Map();

    function setActiveRailLink(id) {
        railLinks.forEach((link) => {
            const active = link.getAttribute("href") === `#${id}`;
            link.classList.toggle("is-active", active);

            if (active) {
                link.setAttribute("aria-current", "location");
            } else {
                link.removeAttribute("aria-current");
            }
        });
    }

    function registerRailTarget(link) {
        const selector = link.getAttribute("href");

        if (!selector || !selector.startsWith("#")) {
            return;
        }

        const target = document.querySelector(selector);

        if (!target || observedTargets.has(target)) {
            return;
        }

        observedTargets.set(target, selector.slice(1));
    }

    railLinks.forEach(registerRailTarget);

    const navObserver = new IntersectionObserver(
        (entries) => {
            const visible = entries
                .filter((entry) => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

            if (!visible) {
                return;
            }

            const id = observedTargets.get(visible.target);

            if (id) {
                setActiveRailLink(id);
            }
        },
        {
            rootMargin: "-18% 0px -64% 0px",
            threshold: [0.08, 0.2, 0.4],
        }
    );

    function syncNavTargets() {
        railLinks.forEach(registerRailTarget);
        observedTargets.forEach((_, target) => navObserver.observe(target));
    }

    const revealObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("is-visible");
                revealObserver.unobserve(entry.target);
            });
        },
        {
            rootMargin: "0px 0px -10% 0px",
            threshold: 0.08,
        }
    );

    function markRevealTargets(scope = document) {
        const selectors = [
            ".section-heading",
            ".summary-group",
            ".allocation-block",
            ".alternative-item",
            ".review-banner",
            ".review-item",
            ".provenance-card",
            ".advisory-note",
            ".impact-overview",
            ".impact-entry",
            ".impact-result",
        ];

        scope.querySelectorAll(selectors.join(",")).forEach((element) => {
            if (element.dataset.extremeReveal === "ready") {
                return;
            }

            element.dataset.extremeReveal = "ready";
            element.classList.add("x-reveal");

            if (reduceMotion) {
                element.classList.add("is-visible");
            } else {
                revealObserver.observe(element);
            }
        });
    }

    const dynamicObserver = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            for (const node of mutation.addedNodes) {
                if (!(node instanceof Element)) {
                    continue;
                }

                if (node.matches("#impact-reconciliation-section")) {
                    syncNavTargets();
                }

                markRevealTargets(node);
            }
        }
    });

    dynamicObserver.observe(document.body, {
        childList: true,
        subtree: true,
    });

    railLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            const selector = link.getAttribute("href");
            const target = selector ? document.querySelector(selector) : null;

            if (!target) {
                return;
            }

            event.preventDefault();
            const url = new URL(location.href);
            url.hash = selector;
            history.replaceState(null, "", url);
            target.scrollIntoView({
                behavior: reduceMotion ? "auto" : "smooth",
                block: "start",
            });
        });
    });

    function injectSignalStrip() {
        if (document.querySelector(".x-signal-strip")) {
            return;
        }

        const strip = document.createElement("aside");
        strip.className = "x-signal-strip";
        strip.setAttribute("aria-label", "Operational guardrails");
        strip.innerHTML = `
            <div class="x-signal-strip__item">
                <span class="x-signal-strip__index">01</span>
                <strong>Hard gates before scoring</strong>
            </div>
            <div class="x-signal-strip__item">
                <span class="x-signal-strip__index">02</span>
                <strong>Global allocation, not greedy ranking</strong>
            </div>
            <div class="x-signal-strip__item">
                <span class="x-signal-strip__index">03</span>
                <strong>Expected ≠ confirmed outcome</strong>
            </div>
            <div class="x-signal-strip__item">
                <span class="x-signal-strip__index">04</span>
                <strong>Human approval remains final</strong>
            </div>
        `;

        const header = document.querySelector(".site-header");
        header?.insertAdjacentElement("afterend", strip);
    }

    const defaults = Object.freeze({
        mode: "control",
        density: 5,
        motion: 5,
        variance: 5,
    });

    const modes = new Set(["control", "editorial", "evidence"]);

    function clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    function readStoredState() {
        try {
            const parsed = JSON.parse(localStorage.getItem(storageKey) || "null");
            return parsed && typeof parsed === "object" ? parsed : {};
        } catch {
            return {};
        }
    }

    function readInitialState() {
        const params = new URLSearchParams(location.search);
        const stored = readStoredState();
        const requestedMode = params.get("view") || stored.mode || defaults.mode;

        return {
            mode: modes.has(requestedMode) ? requestedMode : defaults.mode,
            density: clamp(
                Number(params.get("density") || stored.density || defaults.density),
                1,
                10
            ),
            motion: clamp(
                Number(params.get("motion") || stored.motion || defaults.motion),
                0,
                10
            ),
            variance: clamp(
                Number(params.get("variance") || stored.variance || defaults.variance),
                1,
                10
            ),
        };
    }

    let labState = readInitialState();
    let labPanel = null;
    let labToggle = null;

    function persistLabState() {
        try {
            localStorage.setItem(storageKey, JSON.stringify(labState));
        } catch {
            // Local storage is a convenience only; URL state remains authoritative.
        }
    }

    function syncLabUrl() {
        const url = new URL(location.href);
        url.searchParams.set("view", labState.mode);
        url.searchParams.set("density", String(labState.density));
        url.searchParams.set("motion", String(labState.motion));
        url.searchParams.set("variance", String(labState.variance));
        history.replaceState(null, "", url);
    }

    function syncLabControls() {
        if (!labPanel) {
            return;
        }

        labPanel.querySelectorAll("[data-lab-mode]").forEach((button) => {
            button.setAttribute(
                "aria-pressed",
                button.dataset.labMode === labState.mode ? "true" : "false"
            );
        });

        ["density", "motion", "variance"].forEach((key) => {
            const input = labPanel.querySelector(`[data-lab-range="${key}"]`);
            const value = labPanel.querySelector(`[data-lab-value="${key}"]`);

            if (input) {
                input.value = String(labState[key]);
            }

            if (value) {
                value.textContent = String(labState[key]);
            }
        });
    }

    function applyLabState({ persist = true, url = true } = {}) {
        body.dataset.labMode = labState.mode;

        const density = Number(labState.density);
        const variance = Number(labState.variance);
        const motion = reduceMotion ? 0 : Number(labState.motion);

        root.style.setProperty(
            "--lab-section-pad",
            `${clamp(122 - density * 7, 52, 115)}px`
        );
        root.style.setProperty(
            "--lab-density-gap",
            `${clamp(42 - density * 2.4, 16, 40)}px`
        );
        root.style.setProperty(
            "--lab-asymmetry",
            `${(variance - 5) * 4}px`
        );
        root.style.setProperty(
            "--lab-content-max",
            `${1240 + variance * 18}px`
        );
        root.style.setProperty(
            "--lab-motion",
            reduceMotion ? "0.01ms" : `${140 + motion * 28}ms`
        );
        root.style.setProperty(
            "--lab-motion-slow",
            reduceMotion ? "0.01ms" : `${260 + motion * 52}ms`
        );

        syncLabControls();

        if (persist) {
            persistLabState();
        }

        if (url) {
            syncLabUrl();
        }
    }

    function setLabOpen(open) {
        if (!labPanel || !labToggle) {
            return;
        }

        labPanel.hidden = !open;
        labToggle.setAttribute("aria-expanded", open ? "true" : "false");

        if (open) {
            labPanel.querySelector(".x-lab-mode")?.focus();
        }
    }

    function injectDesignLab() {
        if (document.querySelector("#extreme-design-lab")) {
            return;
        }

        labToggle = document.createElement("button");
        labToggle.type = "button";
        labToggle.className = "x-lab-toggle";
        labToggle.textContent = "Design Lab";
        labToggle.setAttribute("aria-controls", "extreme-design-lab");
        labToggle.setAttribute("aria-expanded", "false");

        labPanel = document.createElement("section");
        labPanel.id = "extreme-design-lab";
        labPanel.className = "x-lab-panel";
        labPanel.hidden = true;
        labPanel.setAttribute("aria-labelledby", "extreme-design-lab-title");
        labPanel.innerHTML = `
            <div class="x-lab-panel__head">
                <div>
                    <p class="x-lab-panel__eyebrow">Extreme / UIUX</p>
                    <h2 id="extreme-design-lab-title">Design Lab</h2>
                    <p class="x-lab-panel__hint">
                        Live branch-only tuning. State persists in the URL and locally.
                    </p>
                </div>
            </div>

            <div class="x-lab-group">
                <span class="x-lab-group__label">Design direction</span>
                <div class="x-lab-modes" role="group" aria-label="Design direction">
                    <button type="button" class="x-lab-mode" data-lab-mode="control">Control</button>
                    <button type="button" class="x-lab-mode" data-lab-mode="editorial">Editorial</button>
                    <button type="button" class="x-lab-mode" data-lab-mode="evidence">Evidence</button>
                </div>
            </div>

            <div class="x-lab-group">
                <span class="x-lab-group__label">Taste dials</span>

                <div class="x-lab-control">
                    <label for="lab-variance">Variance</label>
                    <output class="x-lab-value" data-lab-value="variance" for="lab-variance">5</output>
                    <input id="lab-variance" class="x-lab-range" data-lab-range="variance" type="range" min="1" max="10" step="1" value="5">
                </div>

                <div class="x-lab-control">
                    <label for="lab-motion">Motion</label>
                    <output class="x-lab-value" data-lab-value="motion" for="lab-motion">5</output>
                    <input id="lab-motion" class="x-lab-range" data-lab-range="motion" type="range" min="0" max="10" step="1" value="5">
                </div>

                <div class="x-lab-control">
                    <label for="lab-density">Density</label>
                    <output class="x-lab-value" data-lab-value="density" for="lab-density">5</output>
                    <input id="lab-density" class="x-lab-range" data-lab-range="density" type="range" min="1" max="10" step="1" value="5">
                </div>
            </div>

            <div class="x-lab-panel__foot">
                <button type="button" class="x-lab-reset">Reset</button>
                <span>Shift + L toggles lab</span>
            </div>
        `;

        document.body.append(labPanel, labToggle);

        labToggle.addEventListener("click", () => {
            setLabOpen(labPanel.hidden);
        });

        labPanel.querySelectorAll("[data-lab-mode]").forEach((button) => {
            button.addEventListener("click", () => {
                labState = {
                    ...labState,
                    mode: button.dataset.labMode,
                };
                applyLabState();
            });
        });

        labPanel.querySelectorAll("[data-lab-range]").forEach((input) => {
            input.addEventListener("input", () => {
                const key = input.dataset.labRange;
                labState = {
                    ...labState,
                    [key]: Number(input.value),
                };
                applyLabState();
            });
        });

        labPanel.querySelector(".x-lab-reset")?.addEventListener("click", () => {
            labState = { ...defaults };
            applyLabState();
        });

        document.addEventListener("keydown", (event) => {
            const target = event.target;
            const editing = target instanceof HTMLElement
                && (
                    /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)
                    || target.isContentEditable
                );

            if (editing) {
                return;
            }

            if (event.key === "Escape" && !labPanel.hidden) {
                setLabOpen(false);
                labToggle.focus();
                return;
            }

            if (event.shiftKey && event.key.toLowerCase() === "l") {
                event.preventDefault();
                setLabOpen(labPanel.hidden);
            }
        });

        applyLabState({ persist: false, url: false });
    }

    injectSignalStrip();
    injectDesignLab();
    markRevealTargets();
    syncNavTargets();

    requestAnimationFrame(() => {
        body.dataset.extremeReady = "true";

        requestAnimationFrame(() => {
            document
                .querySelectorAll(".x-reveal")
                .forEach((element) => {
                    const rect = element.getBoundingClientRect();

                    if (rect.top < window.innerHeight * 0.92) {
                        element.classList.add("is-visible");
                    }
                });
        });
    });
})();
