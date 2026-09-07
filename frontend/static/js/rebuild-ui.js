(() => {
    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    const navLinks = [...document.querySelectorAll(".phase-nav__link")];
    const systemState = document.querySelector(".system-state");
    const systemStateLabel = document.querySelector("#system-state-label");
    const analysisForm = document.querySelector("#analysis-form");
    const statusMessage = document.querySelector("#status-message");
    const results = document.querySelector("#results");

    function normalizeLoadingStatus(element) {
        if (
            !(element instanceof HTMLElement)
            || !element.classList.contains("status-message")
            || element.dataset.state !== "loading"
        ) {
            return;
        }

        const normalized = element.textContent.replace(/(?:\.{3}|…)\s*$/, "");

        if (normalized !== element.textContent) {
            element.textContent = normalized;
        }
    }

    function normalizeAllLoadingStatuses(root = document) {
        if (root instanceof HTMLElement && root.classList.contains("status-message")) {
            normalizeLoadingStatus(root);
        }

        root.querySelectorAll?.(".status-message[data-state='loading']")
            .forEach(normalizeLoadingStatus);
    }

    function setSystemState(state, label) {
        if (!systemState || !systemStateLabel) {
            return;
        }

        systemState.dataset.state = state;
        systemStateLabel.textContent = label;
    }

    function syncSystemState() {
        const status = statusMessage?.dataset.state;

        if (analysisForm?.dataset.state === "loading" || status === "loading") {
            setSystemState("working", "Analyzing");
            return;
        }

        if (status === "error") {
            setSystemState("error", "Needs attention");
            return;
        }

        if (status === "success" && results && !results.classList.contains("hidden")) {
            setSystemState("complete", "Plan ready");
            return;
        }

        setSystemState("ready", "System ready");
    }

    if (analysisForm) {
        analysisForm.addEventListener(
            "submit",
            (event) => {
                if (analysisForm.checkValidity()) {
                    return;
                }

                event.preventDefault();
                event.stopImmediatePropagation();
                analysisForm.reportValidity();
            },
            true
        );
    }

    function resolveNavTarget(link) {
        const selector = link.getAttribute("href");

        if (!selector?.startsWith("#")) {
            return null;
        }

        return document.querySelector(selector);
    }

    function setActiveLink(id) {
        navLinks.forEach((link) => {
            const active = link.getAttribute("href") === `#${id}`;
            link.classList.toggle("is-active", active);

            if (active) {
                link.setAttribute("aria-current", "location");
            } else {
                link.removeAttribute("aria-current");
            }
        });
    }

    const sectionObserver = new IntersectionObserver(
        (entries) => {
            const visible = entries
                .filter((entry) => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

            if (visible?.target?.id) {
                setActiveLink(visible.target.id);
            }
        },
        {
            rootMargin: "-24% 0px -62% 0px",
            threshold: [0.05, 0.18, 0.35],
        }
    );

    const observedSections = new WeakSet();

    function registerSections() {
        navLinks.forEach((link) => {
            const target = resolveNavTarget(link);

            if (!target || observedSections.has(target)) {
                return;
            }

            observedSections.add(target);
            sectionObserver.observe(target);
        });
    }

    navLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            const target = resolveNavTarget(link);

            if (!target) {
                return;
            }

            event.preventDefault();
            target.scrollIntoView({
                behavior: reduceMotion ? "auto" : "smooth",
                block: "start",
            });
        });
    });

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
            rootMargin: "0px 0px -8% 0px",
            threshold: 0.08,
        }
    );

    const revealSelectors = [
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

    function registerRevealTargets(root = document) {
        root.querySelectorAll(revealSelectors.join(",")).forEach((element) => {
            if (element.dataset.reveal === "ready") {
                return;
            }

            element.dataset.reveal = "ready";

            if (reduceMotion) {
                element.classList.add("is-visible");
                return;
            }

            revealObserver.observe(element);
        });
    }

    const mutationObserver = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (
                mutation.type === "attributes"
                && mutation.target instanceof HTMLElement
                && mutation.target.classList.contains("status-message")
            ) {
                normalizeLoadingStatus(mutation.target);
            }

            if (
                mutation.type === "attributes"
                && (
                    mutation.target === analysisForm
                    || mutation.target === statusMessage
                    || mutation.target === results
                )
            ) {
                syncSystemState();
            }

            if (
                mutation.type === "childList"
                && mutation.target instanceof HTMLElement
                && mutation.target.classList.contains("status-message")
            ) {
                normalizeLoadingStatus(mutation.target);
                syncSystemState();
            }

            for (const node of mutation.addedNodes) {
                if (!(node instanceof Element)) {
                    continue;
                }

                normalizeAllLoadingStatuses(node);
                registerRevealTargets(node);

                if (
                    node.id === "impact-reconciliation-section"
                    || node.querySelector?.("#impact-reconciliation-section")
                ) {
                    registerSections();
                }
            }
        }
    });

    mutationObserver.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["data-state", "class"],
    });

    registerSections();
    registerRevealTargets();
    normalizeAllLoadingStatuses();
    syncSystemState();
})();
