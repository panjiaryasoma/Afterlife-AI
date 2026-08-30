const resultsRoot = document.querySelector("#results");
const allocationsRoot = document.querySelector("#allocations");

const IMPACT_SECTION_ID = "impact-reconciliation-section";
const IMPACT_NEXTSTEP_REPORT_EVENT = "afterlife:nextstep-report";
const IMPACT_NEXTSTEP_CLEAR_EVENT = "afterlife:nextstep-clear";
const IMPACT_STYLESHEET_HREF = "/static/css/impact.css";

function ensureImpactStylesheet() {
    if (document.querySelector(`link[href="${IMPACT_STYLESHEET_HREF}"]`)) {
        return;
    }

    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = IMPACT_STYLESHEET_HREF;
    document.head.appendChild(stylesheet);
}

function impactEscapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
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

function formatImpactSignedNumber(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return "—";
    }

    if (numeric > 0) {
        return `+${formatImpactNumber(numeric)}`;
    }

    return formatImpactNumber(numeric);
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

function renderReconciliationResult(container, reconciliation, context) {
    const confirmedQuantity = (
        Number(reconciliation.actual_rescued_quantity)
        + Number(reconciliation.actual_waste_quantity)
    );

    container.innerHTML = `
        <div class="impact-result">
            <div>
                <p class="impact-result__eyebrow">REALIZED OUTCOME</p>
                <p class="impact-result__ratio">
                    ${impactEscapeHtml(
                        formatImpactPercent(
                            reconciliation.realized_diversion_ratio
                        )
                    )}
                </p>
                <p class="impact-result__ratio-note">
                    <span class="impact-overview__ratio">
                        ${impactEscapeHtml(
                            formatImpactNumber(confirmedQuantity)
                        )} of ${impactEscapeHtml(
                            formatImpactNumber(
                                reconciliation.reconciled_quantity
                            )
                        )} units confirmed · ${impactEscapeHtml(
                            formatImpactNumber(
                                reconciliation.unresolved_quantity
                            )
                        )} unresolved
                    </span>
                    <br>
                    Realized diversion ratio uses confirmed outcomes only.
                </p>
            </div>

            <div>
                <table class="impact-comparison">
                    <thead>
                        <tr>
                            <th scope="col">Outcome</th>
                            <th scope="col">Expected</th>
                            <th scope="col">Confirmed</th>
                            <th scope="col">Delta</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <th scope="row">Actual rescued</th>
                            <td>${impactEscapeHtml(
                                formatImpactNumber(
                                    context.expectedRescueQuantity
                                )
                            )}</td>
                            <td>${impactEscapeHtml(
                                formatImpactNumber(
                                    reconciliation.actual_rescued_quantity
                                )
                            )}</td>
                            <td>${impactEscapeHtml(
                                formatImpactSignedNumber(
                                    reconciliation.rescue_quantity_delta
                                )
                            )}</td>
                        </tr>
                        <tr>
                            <th scope="row">Actual waste</th>
                            <td>${impactEscapeHtml(
                                formatImpactNumber(
                                    context.expectedWasteQuantity
                                )
                            )}</td>
                            <td>${impactEscapeHtml(
                                formatImpactNumber(
                                    reconciliation.actual_waste_quantity
                                )
                            )}</td>
                            <td>${impactEscapeHtml(
                                formatImpactSignedNumber(
                                    reconciliation.waste_quantity_delta
                                )
                            )}</td>
                        </tr>
                        <tr>
                            <th scope="row">Unresolved</th>
                            <td class="impact-comparison__muted">—</td>
                            <td>${impactEscapeHtml(
                                formatImpactNumber(
                                    reconciliation.unresolved_quantity
                                )
                            )}</td>
                            <td class="impact-comparison__muted">—</td>
                        </tr>
                    </tbody>
                </table>
                <p class="impact-result__ratio-note">
                    Rescue delta and Waste delta are realized minus expected.
                    Values remain operator-confirmed and are not persisted.
                </p>
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
    const massEvidenceLabel = context.massEvidenceCoverage.toLowerCase();
    const massNote = completeMassEvidence
        ? "Every relevant positive-quantity slice has package-weight evidence."
        : "Full-batch mass is withheld because package-weight evidence is incomplete.";

    section.innerHTML = `
        <div class="section-heading">
            <div>
                <p class="section-index">03 / OUTCOME RECONCILIATION</p>
                <h2 id="impact-reconciliation-title">
                    Compare the plan with what actually happened.
                </h2>
            </div>

            <p class="section-note">
                Planned impact is model-derived. Actual impact is entered by
                an operator and is not persisted by this demo.
            </p>
        </div>

        <div class="impact-overview">
            <div class="impact-overview__lead">
                <p class="impact-overview__eyebrow">EXPECTED RESCUE</p>
                <p class="impact-overview__measure">
                    <strong class="impact-overview__value">
                        ${impactEscapeHtml(
                            formatImpactNumber(context.expectedRescueQuantity)
                        )}
                    </strong>
                    <span class="impact-overview__scope">
                        of ${impactEscapeHtml(
                            formatImpactNumber(context.reconciledQuantity)
                        )} planned units
                    </span>
                </p>
                <p class="impact-overview__statement">
                    The current plan estimates an
                    <span class="impact-overview__ratio">
                        ${impactEscapeHtml(
                            formatImpactPercent(context.expectedRescueRatio)
                        )}
                    </span>
                    rescue ratio, with
                    ${impactEscapeHtml(
                        formatImpactNumber(context.expectedWasteQuantity)
                    )}
                    units expected to remain waste.
                </p>
            </div>

            <dl class="impact-ledger">
                <div class="impact-ledger__row">
                    <dt>Expected waste</dt>
                    <dd>${impactEscapeHtml(
                        formatImpactNumber(context.expectedWasteQuantity)
                    )} units</dd>
                </div>
                <div class="impact-ledger__row">
                    <dt>Mass evidence</dt>
                    <dd>
                        <span class="impact-ledger__evidence">
                            ${impactEscapeHtml(massEvidenceLabel)}
                        </span>
                    </dd>
                    <span class="impact-ledger__note">
                        ${impactEscapeHtml(massNote)}
                    </span>
                </div>
                <div class="impact-ledger__row">
                    <dt>Expected rescue mass</dt>
                    <dd>${impactEscapeHtml(
                        completeMassEvidence
                            ? formatImpactMass(context.expectedRescueMassKg)
                            : "—"
                    )}</dd>
                </div>
                <div class="impact-ledger__row">
                    <dt>Expected waste mass</dt>
                    <dd>${impactEscapeHtml(
                        completeMassEvidence
                            ? formatImpactMass(context.expectedWasteMassKg)
                            : "—"
                    )}</dd>
                </div>
            </dl>
        </div>

        <div class="impact-entry">
            <div class="impact-entry__intro">
                <p class="impact-entry__eyebrow">RECORD ACTUAL OUTCOME</p>
                <p>
                    Enter only quantities that have been physically confirmed.
                    Any remainder stays unresolved rather than being guessed.
                </p>
            </div>

            <form id="outcome-reconciliation-form" class="impact-form">
                <div class="impact-form__fields">
                    <div class="impact-field">
                        <label for="actual-rescued-quantity">
                            Actual rescued quantity
                        </label>
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
                        <p class="impact-field__help">
                            Confirmed rescued quantity within this planning scope.
                        </p>
                    </div>

                    <div class="impact-field">
                        <label for="actual-waste-quantity">
                            Actual waste quantity
                        </label>
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
                        <p class="impact-field__help">
                            Confirmed waste quantity. Unconfirmed units remain unresolved.
                        </p>
                    </div>
                </div>

                <div class="impact-form__footer">
                    <p class="impact-form__limit">
                        Confirmed rescued + waste cannot exceed
                        ${impactEscapeHtml(
                            formatImpactNumber(context.reconciledQuantity)
                        )} units.
                    </p>
                    <button class="secondary-button" type="submit">
                        Reconcile outcome
                    </button>
                </div>
            </form>
        </div>

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
                payload.reconciliation,
                context
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

ensureImpactStylesheet();

window.addEventListener(
    IMPACT_NEXTSTEP_REPORT_EVENT,
    renderNextStepImpact
);
window.addEventListener(
    IMPACT_NEXTSTEP_CLEAR_EVENT,
    clearImpactUi
);
