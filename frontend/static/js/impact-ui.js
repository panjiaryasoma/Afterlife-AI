const resultsRoot = document.querySelector("#results");
const allocationsRoot = document.querySelector("#allocations");

const IMPACT_SECTION_ID = "impact-reconciliation-section";
const IMPACT_NEXTSTEP_REPORT_EVENT = "afterlife:nextstep-report";
const IMPACT_NEXTSTEP_CLEAR_EVENT = "afterlife:nextstep-clear";

function impactEscapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
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
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return "—";
    }

    return new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 2,
    }).format(numeric);
}

function formatImpactPercent(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return "—";
    }

    return `${formatImpactNumber(numeric * 100)}%`;
}

function formatImpactMass(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    return `${formatImpactNumber(value)} kg`;
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

function buildImpactContext(report, sustainabilitySummary) {
    if (
        !report?.request_id
        || !sustainabilitySummary
        || typeof sustainabilitySummary !== "object"
    ) {
        return null;
    }

    return {
        requestId: report.request_id,
        reconciledQuantity: sustainabilitySummary.reconciled_quantity,
        expectedRescueQuantity: (
            sustainabilitySummary.expected_rescue_quantity
        ),
        expectedWasteQuantity: (
            sustainabilitySummary.expected_waste_quantity
        ),
        expectedRescueRatio: (
            sustainabilitySummary.expected_rescue_ratio
        ),
        massEvidenceCoverage: (
            sustainabilitySummary.mass_evidence_coverage || "NONE"
        ),
        expectedRescueMassKg: (
            sustainabilitySummary.expected_rescue_mass_kg
        ),
        expectedWasteMassKg: (
            sustainabilitySummary.expected_waste_mass_kg
        ),
    };
}

function buildImpactSection(context) {
    const section = document.createElement("section");
    section.id = IMPACT_SECTION_ID;
    section.className = "workspace-section result-section";
    section.setAttribute("aria-labelledby", "impact-reconciliation-title");

    const completeMassEvidence = (
        context.massEvidenceCoverage === "COMPLETE"
    );
    const massNote = completeMassEvidence
        ? "Complete package-weight evidence"
        : "Full-batch mass withheld because weight evidence is incomplete";

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
                    formatImpactPercent(context.expectedRescueRatio),
                    "Estimated, not observed"
                )}
                ${impactMetric(
                    "Mass evidence",
                    context.massEvidenceCoverage,
                    massNote
                )}
                ${impactMetric(
                    "Expected rescue mass",
                    completeMassEvidence
                        ? formatImpactMass(context.expectedRescueMassKg)
                        : "—",
                    massNote
                )}
                ${impactMetric(
                    "Expected waste mass",
                    completeMassEvidence
                        ? formatImpactMass(context.expectedWasteMassKg)
                        : "—",
                    massNote
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

    const reconciliationForm = section.querySelector(
        "#outcome-reconciliation-form"
    );
    const status = section.querySelector(
        "#outcome-reconciliation-status"
    );
    const realized = section.querySelector("#realized-impact");
    const submitButton = reconciliationForm.querySelector(
        "button[type='submit']"
    );

    reconciliationForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const rescuedInput = reconciliationForm.querySelector(
            "#actual-rescued-quantity"
        );
        const wasteInput = reconciliationForm.querySelector(
            "#actual-waste-quantity"
        );
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
                throw new Error(
                    impactErrorMessage(payload, response.status)
                );
            }

            renderReconciliationResult(
                realized,
                payload.reconciliation
            );
            status.textContent = (
                "Outcome reconciled · realized impact shown below."
            );
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

function clearImpactUi() {
    document.querySelector(`#${IMPACT_SECTION_ID}`)?.remove();
}

function renderNextStepImpact(event) {
    clearImpactUi();

    const context = buildImpactContext(
        event.detail?.report,
        event.detail?.sustainabilitySummary
    );

    if (!context || !resultsRoot) {
        return;
    }

    const section = buildImpactSection(context);
    const selectedPlanSection = allocationsRoot?.closest("section");

    if (selectedPlanSection) {
        selectedPlanSection.before(section);
    } else {
        resultsRoot.appendChild(section);
    }
}

window.addEventListener(
    IMPACT_NEXTSTEP_REPORT_EVENT,
    renderNextStepImpact
);
window.addEventListener(
    IMPACT_NEXTSTEP_CLEAR_EVENT,
    clearImpactUi
);
