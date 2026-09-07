(() => {
    const body = document.body;

    if (!body.classList.contains("extreme-ui")) {
        return;
    }

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

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

    function markRevealTargets(root = document) {
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

        root.querySelectorAll(selectors.join(",")).forEach((element) => {
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
            const target = document.querySelector(link.getAttribute("href"));

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
