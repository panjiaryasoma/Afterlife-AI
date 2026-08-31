const form = document.querySelector("#analysis-form");
const fileInput = document.querySelector("#inventory-file");
const fileDropzone = document.querySelector("#file-dropzone");
const fileDropzoneTitle = document.querySelector("#file-dropzone-title");
const fileDropzonePrompt = document.querySelector("#file-dropzone-prompt");
const fileName = document.querySelector("#file-name");
const objectiveInput = document.querySelector("#optimization-objective");
const budgetInput = document.querySelector("#max-logistics-budget");
const rescueRatioInput = document.querySelector("#minimum-rescue-ratio");
const deadlineInput = document.querySelector("#rescue-deadline");
const button = document.querySelector("#analyze-button");
const buttonLabel = button.querySelector(".button-label");
const buttonArrow = button.querySelector(".button-arrow");
const statusMessage = document.querySelector("#status-message");
const reportAttention = document.querySelector("#report-attention");
const results = document.querySelector("#results");
const reportMeta = document.querySelector("#report-meta");
const triageMetrics = document.querySelector("#triage-metrics");
const metrics = document.querySelector("#metrics");
const solverState = document.querySelector("#solver-state");
const allocations = document.querySelector("#allocations");
const rejectedCandidates = document.querySelector("#rejected-candidates");
const reviewBanner = document.querySelector("#review-banner");
const reviews = document.querySelector("#reviews");
const provenance = document.querySelector("#provenance");
const limitations = document.querySelector("#limitations");
const scoringProvider = document.querySelector("#scoring-provider");
const downloadReport = document.querySelector("#download-report");

const NEXTSTEP_REPORT_EVENT = "afterlife:nextstep-report";
const NEXTSTEP_CLEAR_EVENT = "afterlife:nextstep-clear";

let latestReport = null;

const numberFormatter = new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
});

const currencyFormatter = new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
});

function dispatchNextStepClear() {
    window.dispatchEvent(
        new CustomEvent(NEXTSTEP_CLEAR_EVENT)
    );
}

function dispatchNextStepReport(report, sustainabilitySummary) {
    window.dispatchEvent(
        new CustomEvent(
            NEXTSTEP_REPORT_EVENT,
            {
                detail: {
                    report,
                    sustainabilitySummary,
                },
            }
        )
    );
}

function validateNextStepEnvelope(payload) {
    if (
        !payload
        || typeof payload !== "object"
        || !payload.rescue_decision_report
        || typeof payload.rescue_decision_report !== "object"
        || !payload.sustainability_summary
        || typeof payload.sustainability_summary !== "object"
    ) {
        throw new Error(
            "Analysis completed with an invalid NextStep response envelope."
        );
    }

    return {
        report: payload.rescue_decision_report,
        sustainabilitySummary: payload.sustainability_summary,
    };
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function humanizeEnum(value) {
    if (value === null || value === undefined || value === "") {
        return "Not provided";
    }

    return String(value)
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatNumber(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    return Number.isFinite(numeric)
        ? numberFormatter.format(numeric)
        : escapeHtml(value);
}

function formatQuantity(value) {
    return formatNumber(value);
}

function formatCurrency(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    return Number.isFinite(numeric)
        ? currencyFormatter.format(numeric)
        : escapeHtml(value);
}

function formatPercent(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    return Number.isFinite(numeric)
        ? `${numberFormatter.format(numeric * 100)}%`
        : escapeHtml(value);
}

function formatHours(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    return `${formatNumber(value)} h`;
}

function formatDistance(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    return `${formatNumber(value)} km`;
}

function formatBoolean(value, trueLabel, falseLabel) {
    if (value === null || value === undefined) {
        return "Not reported";
    }

    return value ? trueLabel : falseLabel;
}

function safeArray(value) {
    return Array.isArray(value) ? value : [];
}

async function readResponsePayload(response) {
    const contentType = (
        response.headers.get("content-type") || ""
    ).toLowerCase();

    if (contentType.includes("json")) {
        try {
            return {
                kind: "json",
                value: await response.json(),
            };
        } catch {
            return {
                kind: "invalid-json",
                value: null,
            };
        }
    }

    return {
        kind: "text",
        value: (await response.text()).trim(),
    };
}

function responseErrorMessage(response, parsed) {
    if (
        parsed.kind === "json"
        && parsed.value
        && typeof parsed.value === "object"
    ) {
        const detail = parsed.value.detail;

        if (Array.isArray(detail)) {
            return detail
                .map(
                    (item) =>
                        item?.msg || "Validation error"
                )
                .join("; ");
        }

        if (
            typeof detail === "string"
            && detail.trim() !== ""
        ) {
            return detail;
        }
    }

    if (
        parsed.kind === "text"
        && typeof parsed.value === "string"
        && parsed.value !== ""
        && response.status < 500
    ) {
        return parsed.value;
    }

    return `Inventory analysis failed (HTTP ${response.status}).`;
}

function setStatus(message, state = "neutral") {
    statusMessage.textContent = message;
    statusMessage.dataset.state = state;
}

function setAnalysisBusy(isBusy) {
    button.disabled = isBusy;

    if (isBusy) {
        button.setAttribute("aria-busy", "true");
        buttonLabel.textContent = "Analyzing Inventory";
        buttonArrow.textContent = "…";
        form.dataset.state = "loading";
        return;
    }

    button.removeAttribute("aria-busy");
    buttonLabel.textContent = "Analyze Inventory";
    buttonArrow.textContent = "→";
    form.dataset.state = "ready";
}

function badge(label, variant = "") {
    const className = variant
        ? `badge badge--${variant}`
        : "badge";

    return `<span class="${className}">${escapeHtml(label)}</span>`;
}

function metric(label, value, note = "") {
    return `
        <div class="metric">
            <span class="metric__label">${escapeHtml(label)}</span>
            <strong class="metric__value">${escapeHtml(value)}</strong>
            <span class="metric__note">${escapeHtml(note)}</span>
        </div>
    `;
}

function fact(label, value) {
    return `
        <div class="fact">
            <span class="fact__label">${escapeHtml(label)}</span>
            <span class="fact__value">${escapeHtml(value)}</span>
        </div>
    `;
}

const CODE_LABELS = Object.freeze({
    OPTIMIZER_NOT_SELECTED: "Not selected by optimizer",
    UNKNOWN_STORAGE_HISTORY: "Storage history unknown",
    VALID_PARTIAL_USER_DECLARED_SURPLUS: "Partial surplus declared by user",
    CANDIDATE_CAPACITY: "Candidate capacity limit",
    SHARED_DESTINATION_CAPACITY: "Shared destination capacity limit",
    SHARED_ACTION_CAPACITY: "Shared action capacity limit",
});

function codeLabel(code) {
    const raw = String(code ?? "").trim();

    if (!raw) {
        return "Not provided";
    }

    return CODE_LABELS[raw] || humanizeEnum(raw);
}

function codeChips(codes, emptyLabel = "No code reported") {
    const items = safeArray(codes);

    if (items.length === 0) {
        return `<span class="code-chip">${escapeHtml(emptyLabel)}</span>`;
    }

    return items
        .map(
            (code) =>
                `<span class="code-chip">${escapeHtml(codeLabel(code))}</span>`
        )
        .join("");
}

function renderReportAttention(report) {
    const batch = report.batch_metrics || {};
    const unallocated = Number(
        batch.unallocated_planning_quantity || 0
    );

    if (
        report.human_exception_review_required
        || unallocated > 0
    ) {
        const messages = [];

        if (unallocated > 0) {
            messages.push(
                `${formatQuantity(unallocated)} unallocated`
            );
        }

        if (report.human_exception_review_required) {
            messages.push("Human review required");
        }

        reportAttention.textContent = messages.join(" · ");
        reportAttention.className = "badge badge--warning";
        return;
    }

    reportAttention.textContent = "";
    reportAttention.className = "badge hidden";
}

function solverBadge(status) {
    const normalized = String(status || "").toUpperCase();

    if (normalized === "OPTIMAL" || normalized === "FEASIBLE") {
        return badge(normalized, "success");
    }

    if (normalized === "INFEASIBLE") {
        return badge(normalized, "danger");
    }

    if (normalized) {
        return badge(normalized, "warning");
    }

    return badge("NOT REPORTED");
}

function updateObjectiveControls() {
    const balanced = objectiveInput.value === "BALANCED";

    rescueRatioInput.disabled = !balanced;
    rescueRatioInput.required = balanced;

    if (!balanced) {
        rescueRatioInput.value = "";
    }
}

function renderSummary(report) {
    const batch = report.batch_metrics || {};

    triageMetrics.innerHTML = [
        metric(
            "Input lots",
            formatNumber(batch.input_lots),
            "Lots received in this analysis"
        ),
        metric(
            "Input quantity",
            formatQuantity(batch.input_quantity),
            "Total inventory quantity"
        ),
        metric(
            "Protected",
            formatQuantity(batch.protected_quantity),
            "Kept outside rescue planning"
        ),
        metric(
            "Monitor",
            formatQuantity(batch.monitor_quantity),
            "Held for inventory monitoring"
        ),
        metric(
            "Rescue planning",
            formatQuantity(batch.planning_quantity),
            "Eligible for rescue planning"
        ),
        metric(
            "Expired",
            formatQuantity(batch.expired_quantity),
            "Routed outside rescue planning"
        ),
        metric(
            "Human review",
            formatQuantity(batch.review_quantity),
            "Held for manual review"
        ),
    ].join("");

    metrics.innerHTML = [
        metric(
            "Allocated",
            formatQuantity(batch.allocated_planning_quantity),
            "Planning quantity assigned"
        ),
        metric(
            "Unallocated",
            formatQuantity(batch.unallocated_planning_quantity),
            "Planning quantity left unassigned"
        ),
        metric(
            "Expected rescue",
            formatQuantity(batch.expected_physical_rescue_quantity),
            "Model/plan estimate"
        ),
        metric(
            "Expected waste",
            formatQuantity(batch.expected_waste_quantity),
            "Model/plan estimate"
        ),
        metric(
            "Expected rescue ratio",
            formatPercent(batch.expected_rescue_ratio),
            "Estimated, not observed"
        ),
        metric(
            "Expected economic value",
            formatCurrency(batch.expected_total_economic_value),
            "Under current objective"
        ),
    ].join("");

    solverState.innerHTML = solverBadge(
        report.optimization_solver_status
    );
}

function renderAllocations(report) {
    const selected = safeArray(report.selected_allocations);

    if (selected.length === 0) {
        allocations.innerHTML = `
            <p class="empty-state">
                No rescue allocation selected.
            </p>
        `;
        return;
    }

    allocations.innerHTML = selected
        .map((item, index) => {
            const source = escapeHtml(item.source_lot_id);
            const destination = item.destination_id
                ? escapeHtml(item.destination_id)
                : "No external destination";
            const destinationType = item.destination_type
                ? ` · ${escapeHtml(humanizeEnum(item.destination_type))}`
                : "";
            const score = item.estimated_rescue_success_score === null
                || item.estimated_rescue_success_score === undefined
                ? "Not estimated"
                : `${formatPercent(item.estimated_rescue_success_score)} · synthetic-model estimate`;

            return `
                <article class="allocation-block">
                    <div class="allocation-block__header">
                        <div class="allocation-block__number">
                            ${String(index + 1).padStart(2, "0")}
                        </div>

                        <div>
                            <h3 class="allocation-block__title">
                                ${escapeHtml(humanizeEnum(item.action_type))}
                            </h3>
                            <div class="route">
                                ${source} → ${destination}${destinationType}
                            </div>
                        </div>

                        <div class="allocation-block__quantity">
                            <strong>${formatQuantity(item.allocated_quantity)}</strong>
                            <span>allocated units</span>
                        </div>
                    </div>

                    <div class="allocation-block__body">
                        <div class="allocation-detail">
                            <div class="fact-grid">
                                ${fact("Estimated rescue success", score)}
                                ${fact(
                "Completion",
                formatHours(item.estimated_completion_hours)
            )}
                                ${fact(
                "Distance",
                formatDistance(item.distance_km)
            )}
                                ${fact(
                "Value / unit",
                formatCurrency(item.expected_value_per_unit)
            )}
                                ${fact(
                "Expected rescued qty",
                formatQuantity(
                    item.expected_physical_rescue_quantity
                )
            )}
                                ${fact(
                "Expected waste qty",
                formatQuantity(item.expected_waste_quantity)
            )}
                                ${fact(
                "Selling / offer price",
                formatCurrency(
                    item.offered_or_selling_price_per_unit
                )
            )}
                                ${fact(
                "Candidate ID",
                item.candidate_id || "—"
            )}
                            </div>

                            <div class="value-breakdown">
                                <dl>
                                    <div>
                                        <dt>Cash recovery</dt>
                                        <dd>${formatCurrency(item.expected_cash_recovery)}</dd>
                                    </div>
                                    <div>
                                        <dt>Future branch recovery</dt>
                                        <dd>${formatCurrency(item.expected_future_branch_recovery)}</dd>
                                    </div>
                                    <div>
                                        <dt>Avoided purchase cost</dt>
                                        <dd>${formatCurrency(item.expected_avoided_purchase_cost)}</dd>
                                    </div>
                                    <div>
                                        <dt>Direct action cost</dt>
                                        <dd>${formatCurrency(item.direct_action_cost)}</dd>
                                    </div>
                                    <div>
                                        <dt>Logistics cost</dt>
                                        <dd>${formatCurrency(item.logistics_cost)}</dd>
                                    </div>
                                    <div>
                                        <dt>Handling cost</dt>
                                        <dd>${formatCurrency(item.handling_cost)}</dd>
                                    </div>
                                </dl>

                                <div class="net-recovery">
                                    <span>Expected net recovery</span>
                                    <strong>${formatCurrency(item.expected_net_recovery)}</strong>
                                </div>
                            </div>

                            <div
                                class="constraint-row"
                                aria-label="Binding constraints"
                            >
                                ${codeChips(
                item.binding_constraint_codes,
                "No binding constraint"
            )}
                            </div>
                        </div>
                    </div>
                </article>
            `;
        })
        .join("");
}

function renderAlternatives(report) {
    const items = safeArray(report.rejected_candidates);

    if (items.length === 0) {
        rejectedCandidates.innerHTML = `
            <p class="empty-state">
                No alternative candidate is recorded in this report.
            </p>
        `;
        return;
    }

    rejectedCandidates.innerHTML = items
        .map((item) => {
            const reasons = safeArray(item.rejection_reason_codes);
            const optimizerNotSelected = reasons.includes(
                "OPTIMIZER_NOT_SELECTED"
            );
            const stateLabel = optimizerNotSelected
                ? "FEASIBLE — NOT SELECTED"
                : "NOT CARRIED FORWARD";

            return `
                <article class="alternative-item">
                    <div>
                        <h3>${escapeHtml(humanizeEnum(item.action_type))}</h3>
                        <p>
                            ${escapeHtml(item.candidate_id)} ·
                            ${escapeHtml(item.planning_lot_id)}
                            · ${escapeHtml(stateLabel)}
                        </p>
                    </div>

                    <div class="reason-list">
                        ${codeChips(
                reasons,
                "No rejection reason reported"
            )}
                    </div>
                </article>
            `;
        })
        .join("");
}

function renderReviews(report) {
    const items = safeArray(report.review_required_lots);
    const reviewRequired = Boolean(
        report.human_exception_review_required
    );
    const approval = humanizeEnum(
        report.human_final_approval_status
    );

    if (reviewRequired || items.length > 0) {
        reviewBanner.dataset.state = "review";
        reviewBanner.innerHTML = `
            <strong>Human review required.</strong>
            <p>
                Final approval status: ${escapeHtml(approval)}.
                No physical action is executed automatically.
            </p>
        `;
    } else {
        reviewBanner.dataset.state = "clear";
        reviewBanner.innerHTML = `
            <strong>No exception review is currently required.</strong>
            <p>
                Final approval status remains ${escapeHtml(approval)}.
                The report is still advisory.
            </p>
        `;
    }

    if (items.length === 0) {
        reviews.innerHTML = `
            <p class="empty-state">
                No lot is held in the manual-review queue.
            </p>
        `;
        return;
    }

    reviews.innerHTML = items
        .map(
            (item) => `
                <article class="review-item">
                    <div>
                        <h3>${escapeHtml(item.source_lot_id)}</h3>
                        <p>
                            Review quantity:
                            ${formatQuantity(item.review_quantity)}
                        </p>
                    </div>

                    <div class="reason-list">
                        ${codeChips(
                item.reason_codes,
                "No review reason reported"
            )}
                    </div>
                </article>
            `
        )
        .join("");
}

function provenanceCard(label, title, rows, badges = []) {
    const rowMarkup = rows
        .map(
            ([key, value]) => `
                <div>
                    <dt>${escapeHtml(key)}</dt>
                    <dd>${escapeHtml(value)}</dd>
                </div>
            `
        )
        .join("");

    const badgeMarkup = badges.length
        ? `<div class="constraint-row">${badges.join("")}</div>`
        : "";

    return `
        <article class="provenance-card">
            <p class="provenance-card__label">${escapeHtml(label)}</p>
            <h3>${escapeHtml(title)}</h3>
            <dl class="provenance-list">${rowMarkup}</dl>
            ${badgeMarkup}
        </article>
    `;
}

function renderProvenance(report) {
    const score = report.score_provenance || {};
    const registrySource = report.partner_registry_source_type;
    const syntheticRegistry = registrySource === "SYNTHETIC_DEMO_FIXTURE";
    const deterministic = report.deterministic_execution;

    provenance.innerHTML = [
        provenanceCard(
            "Scoring",
            score.provider_name || "Not reported",
            [
                ["Score type", humanizeEnum(score.score_type)],
                ["Source type", humanizeEnum(score.source_type)],
                ["Fixture version", score.fixture_version || "Not applicable"],
                [
                    "Feature schema",
                    report.feature_schema_version || "Not reported",
                ],
                [
                    "Model executed",
                    formatBoolean(
                        report.model_execution_performed,
                        "Yes",
                        "No"
                    ),
                ],
            ],
            score.source_type === "EVALUATION_FIXTURE"
                ? [badge("Evaluation fixture", "synthetic")]
                : []
        ),
        provenanceCard(
            "Partner registry",
            report.partner_registry_snapshot_id || "No registry snapshot",
            [
                ["Source type", humanizeEnum(registrySource)],
                [
                    "Real-world verified",
                    formatBoolean(
                        report.partner_registry_real_world_verified,
                        "Yes",
                        "No"
                    ),
                ],
                ["Capability snapshot", report.capability_snapshot_version],
                ["Ruleset", report.ruleset_version],
            ],
            [
                syntheticRegistry
                    ? badge("Synthetic demo fixture", "synthetic")
                    : "",
                report.partner_registry_real_world_verified === false
                    ? badge("Not real-world verified", "warning")
                    : "",
            ].filter(Boolean)
        ),
        provenanceCard(
            "Optimizer",
            humanizeEnum(report.optimization_objective),
            [
                [
                    "Solver status",
                    humanizeEnum(report.optimization_solver_status),
                ],
                [
                    "Deterministic execution",
                    formatBoolean(deterministic, "Yes", "No"),
                ],
                [
                    "Random seed",
                    report.optimizer_random_seed ?? "Not reported",
                ],
                [
                    "Search workers",
                    report.optimizer_num_search_workers ?? "Not reported",
                ],
            ],
            deterministic === true
                ? [badge("Deterministic", "success")]
                : []
        ),
    ].join("");
}

function renderLimitations(report) {
    const items = safeArray(report.limitations);

    if (items.length === 0) {
        limitations.innerHTML = `
            <li>No additional limitation text was reported.</li>
        `;
        return;
    }

    limitations.innerHTML = items
        .map((item) => `<li>${escapeHtml(item)}</li>`)
        .join("");
}

function renderReport(report) {
    const timestamp = report.analysis_timestamp
        ? new Date(report.analysis_timestamp).toLocaleString()
        : "Not reported";

    reportMeta.innerHTML = `
        <span>Request · ${escapeHtml(report.request_id)}</span>
        <span>Analyzed · ${escapeHtml(timestamp)}</span>
    `;

    scoringProvider.textContent =
        report.score_provenance?.provider_name || "Score source unknown";

    renderSummary(report);
    renderReportAttention(report);
    renderAllocations(report);
    renderAlternatives(report);
    renderReviews(report);
    renderProvenance(report);
    renderLimitations(report);

    results.classList.remove("hidden");
    results.classList.add("is-visible");
}

objectiveInput.addEventListener(
    "change",
    updateObjectiveControls
);

function renderSelectedWorkbook() {
    const selectedFile = fileInput.files?.[0];

    if (!selectedFile) {
        fileDropzone.dataset.state = "empty";
        fileDropzoneTitle.textContent = "Choose workbook";
        fileDropzonePrompt.textContent = "or drag .xlsx here";
        fileName.textContent = "No workbook selected";
        return;
    }

    fileDropzone.dataset.state = "selected";
    fileDropzoneTitle.textContent = "Workbook selected";
    fileDropzonePrompt.textContent = "Click or drop another file to replace";
    fileName.textContent = selectedFile.name;
}

fileInput.addEventListener("change", renderSelectedWorkbook);

fileDropzone.addEventListener("dragenter", (event) => {
    event.preventDefault();
    fileDropzone.dataset.state = "dragover";
    fileDropzoneTitle.textContent = "Release to upload workbook";
    fileDropzonePrompt.textContent = ".xlsx inventory workbook";
});

fileDropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
});

fileDropzone.addEventListener("dragleave", (event) => {
    if (!fileDropzone.contains(event.relatedTarget)) {
        renderSelectedWorkbook();
    }
});

fileDropzone.addEventListener("drop", (event) => {
    event.preventDefault();

    const droppedFile = event.dataTransfer?.files?.[0];

    if (!droppedFile) {
        renderSelectedWorkbook();
        return;
    }

    const transfer = new DataTransfer();
    transfer.items.add(droppedFile);
    fileInput.files = transfer.files;

    fileInput.dispatchEvent(
        new Event("change", {
            bubbles: true,
        })
    );
});

deadlineInput.addEventListener("click", () => {
    if (typeof deadlineInput.showPicker === "function") {
        deadlineInput.showPicker();
    }
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        setStatus("Select an XLSX file first.", "error");
        fileInput.focus();
        return;
    }

    if (
        objectiveInput.value === "BALANCED"
        && rescueRatioInput.value === ""
    ) {
        setStatus(
            "Balanced objective requires a minimum expected rescue ratio.",
            "error"
        );
        rescueRatioInput.focus();
        return;
    }

    const data = new FormData();

    data.append("inventory_file", file);
    data.append("optimization_objective", objectiveInput.value);

    if (budgetInput.value !== "") {
        data.append("max_logistics_budget", budgetInput.value);
    }

    if (rescueRatioInput.value !== "") {
        data.append("minimum_expected_rescue_ratio", rescueRatioInput.value);
    }

    if (deadlineInput.value !== "") {
        const deadline = new Date(deadlineInput.value);

        if (Number.isNaN(deadline.getTime())) {
            setStatus("Enter a valid rescue deadline.", "error");
            deadlineInput.focus();
            return;
        }

        data.append("rescue_deadline_at", deadline.toISOString());
    }

    latestReport = null;
    dispatchNextStepClear();

    setAnalysisBusy(true);
    downloadReport.classList.add("hidden");
    results.classList.add("hidden");
    results.classList.remove("is-visible");

    setStatus(
        "Analyzing inventory and measuring expected rescue impact...",
        "loading"
    );

    try {
        const response = await fetch("/api/analyze-nextstep", {
            method: "POST",
            body: data,
        });

        const parsed = await readResponsePayload(response);

        if (!response.ok) {
            throw new Error(
                responseErrorMessage(response, parsed)
            );
        }

        if (
            parsed.kind !== "json"
            || !parsed.value
            || typeof parsed.value !== "object"
        ) {
            throw new Error(
                "Analysis completed with an unexpected response format."
            );
        }

        const {
            report,
            sustainabilitySummary,
        } = validateNextStepEnvelope(parsed.value);

        latestReport = report;
        renderReport(report);
        dispatchNextStepReport(
            report,
            sustainabilitySummary
        );

        downloadReport.classList.remove("hidden");
        setStatus(
            "Analysis complete · rescue and sustainability outputs generated.",
            "success"
        );

        results.scrollIntoView({
            behavior: window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches
                ? "auto"
                : "smooth",
            block: "start",
        });
    } catch (error) {
        latestReport = null;
        dispatchNextStepClear();
        downloadReport.classList.add("hidden");

        setStatus(
            error instanceof Error
                ? error.message
                : "Inventory analysis failed.",
            "error"
        );
    } finally {
        setAnalysisBusy(false);
    }
});

updateObjectiveControls();
setAnalysisBusy(false);
