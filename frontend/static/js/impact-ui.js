const resultsRoot = document.querySelector("#results");
const reportMetaRoot = document.querySelector("#report-meta");
const triageMetricsRoot = document.querySelector("#triage-metrics");
const rescueMetricsRoot = document.querySelector("#metrics");
const allocationsRoot = document.querySelector("#allocations");

const IMPACT_SECTION_ID = "impact-reconciliation-section";

function impactEscapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function parseRenderedNumber(value) {
    const normalized = String(value ?? "")
        .trim()
        .replaceAll(",", "");

    if (!normalized || normalized === "—") {
        return null;
    }

    const numeric = Number(normalized.replace(/[^0-9.+-]/g, ""));
    return Number.isFinite(numeric) ? numeric : null;
}

function metricValueByLabel(container, expectedLabel) {
    const cards = container?.querySelectorAll(".metric") || [];

    for (const card of cards) {
        const label = card.querySelector(".metric__label")?.textContent?.trim();

        if (label === expectedLabel) {
            return card.querySelector(".metric__value")?.textContent?.trim() || null;
        }
    }

    return null;
}

function currentRequestId() {
    const firstMeta = reportMetaRoot?.querySelector("span")?.textContent || "";
    const separator = "·";

    if (!firstMeta.includes(separator)) {
        return null;
    }

    return firstMeta.split(separator).slice(1).join(separator).trim() || null;
}

function impactMetric(label, value, note = "") {
    return `
        <div class="metric">
            <span class="metric__label">${impactEscapeHtml(label)}</span>
            <strong class="metric__value">${impactEscapeHtml(value)}</strong>
            <span class="metric__note">${impactEscapeHtml(note)}</span>
        </div>
    `;
}

function formatImpactNumber(value) {
    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return "—";
    }

    return new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 2,
    }).format(numeric);
}

function formatImpactPercent(value) {
    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return "—";
    }

    return `${formatImpactNumber(numeric * 100)}%`;
}

function readImpactContext() {
    const requestId = currentRequestId();
    const reconciledQuantity = parseRenderedNumber(
        metricValueByLabel(triageMetricsRoot, "Rescue planning")
    );
    const expectedRescueQuantity = parseRenderedNumber(
        metricValueByLabel(rescueMetricsRoot, "Expected rescue")
    );
    const expectedWasteQuantity = parseRenderedNumber(
        metricValueByLabel(rescueMetricsRoot, "Expected waste")
    );
    const expectedRescueRatio = metricValueByLabel(
        rescueMetricsRoot,
        "Expected rescue ratio"
    );

    if (
        !requestId
        || reconciledQuantity === null
        || expectedRescueQuantity === null
        || expectedWasteQuantity === null
    ) {
        return null;
    }

    return {
        requestId,
        reconciledQuantity,
        expectedRescueQuantity,
        expectedWasteQuantity,
        expectedRescueRatio: expectedRescueRatio || "—",
    };
}

function impactErrorMessage(payload, status) {
    const detail = payload?.detail;

    if (Array.isArray(detail)) {
        return detail
            .map((item) => item?.msg || "Validation error")
            .join("; ");
    }

    if (typeof detail === "string" && detail.trim()) {
        return detail;
    }

    return `Outcome reconciliation failed (HTTP ${status}).`;
}

function renderReconciliationResult(container, reconciliation) {
    container.innerHTML = `
        <div class="summary-group">
            <p class="section-index">REALIZED OUTCOME</p>
            <div class="metric-grid">
                ${impactMetric(
                    "Actual rescued",
                    formatImpactNumber(reconciliation.actual_rescued_quantity),
                    "Operator-confirmed quantity"
                )}
                ${impactMetric(
                    "Actual waste",
                    formatImpactNumber(reconciliation.actual_waste_quantity),
                    "Operator-confirmed quantity"
                )}
                ${impactMetric(
                    "Unresolved",
                    formatImpactNumber(reconciliation.unresolved_quantity),
                    "Outcome not yet confirmed"
                )}
                ${impactMetric(
                    "Realized diversion ratio",
                    formatImpactPercent(reconciliation.realized_diversion_ratio),
                    "Confirmed outcomes only"
                )}
                ${impactMetric(
                    "Rescue delta",
                    formatImpactNumber(reconciliation.rescue_quantity_delta),
                    "Realized minus expected"
                )}
                ${impactMetric(
                    "Waste delta",
                    formatImpactNumber(reconciliation.waste_quantity_delta),
                    "Realized minus expected"
                )}
            </div>
        </div>
    `;
}

function buildImpactSection(context) {
    const section = document.createElement("section");
    section.id = IMPACT_SECTION_ID;
    section.className = "workspace-section result-section";
    section.setAttribute("aria-labelledby", "impact-reconciliation-title");

    section.innerHTML = `
        <div class="section-heading">
            <div>
                <p class="section-index">03 / OUTCOME RECONCILIATION</p>
                <h2 id="impact-reconciliation-title">
                    Compare the plan with what actually happened.
                </h2>
            </div>

            <p class="section-note">
                Actual outcomes are operator-confirmed and are not persisted by this demo.
            </p>
        </div>

        <div class="summary-group">
            <p class="section-index">EXPECTED IMPACT</p>
            <div class="metric-grid">
                ${impactMetric(
                    "Reconciled scope",
                    formatImpactNumber(context.reconciledQuantity),
                    "Planning quantity"
                )}
                ${impactMetric(
                    "Expected rescue",
                    formatImpactNumber(context.expectedRescueQuantity),
                    "Model/plan estimate"
                )}
                ${impactMetric(
                    "Expected waste",
                    formatImpactNumber(context.expectedWasteQuantity),
                    "Model/plan estimate"
                )}
                ${impactMetric(
                    "Expected rescue ratio",
                    context.expectedRescueRatio,
                    "Estimated, not observed"
                )}
            </div>
        </div>

        <form id="outcome-reconciliation-form" class="analysis-form">
            <div class="field">
                <label for="actual-rescued-quantity">Actual rescued quantity</label>
                <input
                    id="actual-rescued-quantity"
                    name="actual_rescued_quantity"
                    type="number"
                    min="0"
                    step="0.01"
                    inputmode="decimal"
                    placeholder="Operator-confirmed"
                    required
                >
                <p class="field-help">Confirmed rescued quantity within this planning scope.</p>
            </div>

            <div class="field">
                <label for="actual-waste-quantity">Actual waste quantity</label>
                <input
                    id="actual-waste-quantity"
                    name="actual_waste_quantity"
                    type="number"
                    min="0"
                    step="0.01"
                    inputmode="decimal"
                    placeholder="Operator-confirmed"
                    required
                >
                <p class="field-help">Confirmed waste quantity. Any remainder stays unresolved.</p>
            </div>

            <div class="form-actions field--wide">
                <p class="form-assurance">
                    Confirmed rescued + waste cannot exceed ${impactEscapeHtml(
                        formatImpactNumber(context.reconciledQuantity)
                    )} units.
                </p>
                <button class="secondary-button" type="submit">
                    Reconcile Actual Outcome
                </button>
            </div>
        </form>

        <div
            id="outcome-reconciliation-status"
            class="status-message"
            role="status"
            aria-live="polite"
        ></div>

        <div id="realized-impact"></div>
    `;

    const form = section.querySelector("#outcome-reconciliation-form");
    const status = section.querySelector("#outcome-reconciliation-status");
    const realized = section.querySelector("#realized-impact");
    const submitButton = form.querySelector("button[type='submit']");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const rescuedInput = form.querySelector("#actual-rescued-quantity");
        const wasteInput = form.querySelector("#actual-waste-quantity");
        const actualRescued = Number(rescuedInput.value);
        const actualWaste = Number(wasteInput.value);

        if (
            !Number.isFinite(actualRescued)
            || !Number.isFinite(actualWaste)
            || actualRescued < 0
            || actualWaste < 0
        ) {
            status.textContent = "Enter valid non-negative actual quantities.";
            status.dataset.state = "error";
            return;
        }

        submitButton.disabled = true;
        status.textContent = "Reconciling operator-confirmed outcome...";
        status.dataset.state = "loading";
        realized.innerHTML = "";

        try {
            const response = await fetch("/api/outcomes/reconcile", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    request_id: context.requestId,
                    observation: {
                        reconciled_quantity: context.reconciledQuantity,
                        actual_rescued_quantity: actualRescued,
                        actual_waste_quantity: actualWaste,
                    },
                    expected_rescue_quantity: context.expectedRescueQuantity,
                    expected_waste_quantity: context.expectedWasteQuantity,
                }),
            });

            const payload = await response.json();

            if (!response.ok) {
                throw new Error(impactErrorMessage(payload, response.status));
            }

            renderReconciliationResult(realized, payload.reconciliation);
            status.textContent = "Outcome reconciled · realized impact shown below.";
            status.dataset.state = "success";
        } catch (error) {
            status.textContent = error instanceof Error
                ? error.message
                : "Outcome reconciliation failed.";
            status.dataset.state = "error";
        } finally {
            submitButton.disabled = false;
        }
    });

    return section;
}

function syncImpactUi() {
    if (!resultsRoot || resultsRoot.classList.contains("hidden")) {
        document.querySelector(`#${IMPACT_SECTION_ID}`)?.remove();
        return;
    }

    const context = readImpactContext();

    if (!context) {
        return;
    }

    document.querySelector(`#${IMPACT_SECTION_ID}`)?.remove();

    const section = buildImpactSection(context);
    const selectedPlanSection = allocationsRoot?.closest("section");

    if (selectedPlanSection) {
        selectedPlanSection.before(section);
    } else {
        resultsRoot.appendChild(section);
    }
}

if (resultsRoot) {
    const observer = new MutationObserver(syncImpactUi);

    observer.observe(resultsRoot, {
        attributes: true,
        attributeFilter: ["class"],
    });

    if (reportMetaRoot) {
        observer.observe(reportMetaRoot, {
            childList: true,
            subtree: true,
        });
    }

    syncImpactUi();
}
