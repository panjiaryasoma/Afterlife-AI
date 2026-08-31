const markdownDownloadButton = document.querySelector("#download-report");

const markdownNumberFormatter = new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
});

const markdownCurrencyFormatter = new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
});

function markdownSafeArray(value) {
    return Array.isArray(value) ? value : [];
}

function markdownText(value, fallback = "Not reported") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }

    return String(value)
        .replaceAll("\\", "\\\\")
        .replaceAll("|", "\\|")
        .replace(/\r?\n/g, " ")
        .trim();
}

function markdownInlineCode(value) {
    const text = markdownText(value, "unknown").replaceAll("`", "'");
    return `\`${text}\``;
}

function markdownHumanize(value) {
    if (value === null || value === undefined || value === "") {
        return "Not reported";
    }

    return String(value)
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function markdownNumber(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);
    return Number.isFinite(numeric)
        ? markdownNumberFormatter.format(numeric)
        : markdownText(value);
}

function markdownSignedNumber(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return markdownText(value);
    }

    if (numeric > 0) {
        return `+${markdownNumber(numeric)}`;
    }

    return markdownNumber(numeric);
}

function markdownPercent(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);
    return Number.isFinite(numeric)
        ? `${markdownNumber(numeric * 100)}%`
        : markdownText(value);
}

function markdownCurrency(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numeric = Number(value);
    return Number.isFinite(numeric)
        ? markdownCurrencyFormatter.format(numeric)
        : markdownText(value);
}

function markdownMass(value) {
    return value === null || value === undefined || value === ""
        ? "—"
        : `${markdownNumber(value)} kg`;
}

function markdownDate(value) {
    if (!value) {
        return "Not reported";
    }

    const date = new Date(value);
    return Number.isNaN(date.getTime())
        ? markdownText(value)
        : date.toISOString();
}

function markdownBoolean(value) {
    if (value === true) {
        return "Yes";
    }

    if (value === false) {
        return "No";
    }

    return "Not reported";
}

function markdownCodes(codes) {
    const items = markdownSafeArray(codes);
    return items.length > 0
        ? items.map((code) => markdownHumanize(code)).join(", ")
        : "None reported";
}

function markdownSelectedAllocations(report) {
    const selected = markdownSafeArray(report.selected_allocations);

    if (selected.length === 0) {
        return "No rescue allocation was selected.\n";
    }

    return selected
        .map((item, index) => {
            const destination = item.destination_id || "No external destination";
            const score = item.estimated_rescue_success_score === null
                || item.estimated_rescue_success_score === undefined
                ? "Not estimated"
                : `${markdownPercent(item.estimated_rescue_success_score)} (synthetic-model estimate)`;

            return [
                `### ${String(index + 1).padStart(2, "0")}. ${markdownHumanize(item.action_type)}`,
                "",
                `- Candidate: ${markdownInlineCode(item.candidate_id || "unknown")}`,
                `- Route: ${markdownInlineCode(item.source_lot_id)} → ${markdownInlineCode(destination)}`,
                `- Destination type: ${markdownHumanize(item.destination_type)}`,
                `- Allocated quantity: **${markdownNumber(item.allocated_quantity)} units**`,
                `- Estimated rescue success: ${score}`,
                `- Expected rescued quantity: ${markdownNumber(item.expected_physical_rescue_quantity)}`,
                `- Expected waste quantity: ${markdownNumber(item.expected_waste_quantity)}`,
                `- Estimated completion: ${markdownNumber(item.estimated_completion_hours)} h`,
                `- Distance: ${item.distance_km === null || item.distance_km === undefined ? "—" : `${markdownNumber(item.distance_km)} km`}`,
                `- Selling / offer price per unit: ${markdownCurrency(item.offered_or_selling_price_per_unit)}`,
                `- Expected net recovery: **${markdownCurrency(item.expected_net_recovery)}**`,
                `- Binding constraints: ${markdownCodes(item.binding_constraint_codes)}`,
                "",
            ].join("\n");
        })
        .join("\n");
}

function markdownAlternatives(report) {
    const alternatives = markdownSafeArray(report.rejected_candidates);

    if (alternatives.length === 0) {
        return "No alternative candidate was recorded.\n";
    }

    return alternatives
        .map((item) => [
            `- **${markdownHumanize(item.action_type)}**`,
            `  - Candidate: ${markdownInlineCode(item.candidate_id || "unknown")}`,
            `  - Planning lot: ${markdownInlineCode(item.planning_lot_id || "unknown")}`,
            `  - Reason: ${markdownCodes(item.rejection_reason_codes)}`,
        ].join("\n"))
        .join("\n");
}

function markdownHumanReview(report) {
    const lots = markdownSafeArray(report.review_required_lots);
    const lines = [
        `- Human exception review required: **${markdownBoolean(report.human_exception_review_required)}**`,
        `- Final approval status: **${markdownHumanize(report.human_final_approval_status)}**`,
        "- Physical execution: **Not automatic**",
        "",
    ];

    if (lots.length === 0) {
        lines.push("No lot is currently listed in the manual-review queue.");
        return lines.join("\n");
    }

    lines.push("| Lot | Review quantity | Reason |", "|---|---:|---|");

    for (const item of lots) {
        lines.push(
            `| ${markdownText(item.source_lot_id)} | ${markdownNumber(item.review_quantity)} | ${markdownCodes(item.reason_codes)} |`
        );
    }

    return lines.join("\n");
}

function markdownSustainability(summary) {
    if (!summary || typeof summary !== "object") {
        return [
            "Expected sustainability output is not available for this report.",
            "",
        ].join("\n");
    }

    const completeMass = summary.mass_evidence_coverage === "COMPLETE";

    return [
        "> Expected impact is model/plan-derived and must not be interpreted as realized impact.",
        "",
        "| Measure | Value |",
        "|---|---:|",
        `| Planning scope | ${markdownNumber(summary.reconciled_quantity)} units |`,
        `| Expected rescue | ${markdownNumber(summary.expected_rescue_quantity)} units |`,
        `| Expected waste | ${markdownNumber(summary.expected_waste_quantity)} units |`,
        `| Expected rescue ratio | ${markdownPercent(summary.expected_rescue_ratio)} |`,
        `| Mass evidence | ${markdownText(summary.mass_evidence_coverage)} |`,
        `| Expected rescue mass | ${completeMass ? markdownMass(summary.expected_rescue_mass_kg) : "Withheld"} |`,
        `| Expected waste mass | ${completeMass ? markdownMass(summary.expected_waste_mass_kg) : "Withheld"} |`,
        "",
        completeMass
            ? "Mass values use complete package-weight evidence for every relevant positive-quantity slice."
            : "Full-batch mass is withheld because package-weight evidence is incomplete.",
        "",
    ].join("\n");
}

function markdownOutcomeReconciliation(reconciliation, summary) {
    if (!reconciliation || typeof reconciliation !== "object") {
        return [
            "No operator-confirmed outcome has been reconciled for this analysis.",
            "",
            "Expected/model-derived values above are not realized outcomes.",
            "",
        ].join("\n");
    }

    const confirmedQuantity = (
        Number(reconciliation.actual_rescued_quantity || 0)
        + Number(reconciliation.actual_waste_quantity || 0)
    );
    const expectedRescue = summary?.expected_rescue_quantity;
    const expectedWaste = summary?.expected_waste_quantity;

    return [
        `**${markdownNumber(confirmedQuantity)} of ${markdownNumber(reconciliation.reconciled_quantity)} units confirmed · ${markdownNumber(reconciliation.unresolved_quantity)} unresolved**`,
        "",
        `Realized diversion ratio: **${markdownPercent(reconciliation.realized_diversion_ratio)}**`,
        "",
        "> The realized diversion ratio uses confirmed outcomes only. Unresolved quantity is excluded from the ratio.",
        "",
        "| Outcome | Expected | Confirmed | Delta |",
        "|---|---:|---:|---:|",
        `| Rescued | ${markdownNumber(expectedRescue)} | ${markdownNumber(reconciliation.actual_rescued_quantity)} | ${markdownSignedNumber(reconciliation.rescue_quantity_delta)} |`,
        `| Waste | ${markdownNumber(expectedWaste)} | ${markdownNumber(reconciliation.actual_waste_quantity)} | ${markdownSignedNumber(reconciliation.waste_quantity_delta)} |`,
        `| Unresolved | — | ${markdownNumber(reconciliation.unresolved_quantity)} | — |`,
        "",
        "Operator-confirmed outcomes are not persisted by this demo.",
        "",
    ].join("\n");
}

function markdownEvidence(report) {
    const score = report.score_provenance || {};

    return [
        "| Evidence | Value |",
        "|---|---|",
        `| Scoring provider | ${markdownText(score.provider_name)} |`,
        `| Score type | ${markdownHumanize(score.score_type)} |`,
        `| Score source | ${markdownHumanize(score.source_type)} |`,
        `| Model executed | ${markdownBoolean(report.model_execution_performed)} |`,
        `| Feature schema | ${markdownText(report.feature_schema_version)} |`,
        `| Partner registry snapshot | ${markdownText(report.partner_registry_snapshot_id)} |`,
        `| Partner registry source | ${markdownHumanize(report.partner_registry_source_type)} |`,
        `| Partner registry real-world verified | ${markdownBoolean(report.partner_registry_real_world_verified)} |`,
        `| Ruleset | ${markdownText(report.ruleset_version)} |`,
        `| Capability snapshot | ${markdownText(report.capability_snapshot_version)} |`,
        `| Deterministic execution | ${markdownBoolean(report.deterministic_execution)} |`,
        `| Optimizer random seed | ${markdownText(report.optimizer_random_seed)} |`,
        `| Optimizer search workers | ${markdownText(report.optimizer_num_search_workers)} |`,
        "",
    ].join("\n");
}

function markdownLimitations(report) {
    const items = markdownSafeArray(report.limitations);

    if (items.length === 0) {
        return "- No additional limitation text was reported.\n";
    }

    return `${items.map((item) => `- ${markdownText(item)}`).join("\n")}\n`;
}

function buildAfterlifeMarkdownReport(report, exportState = {}) {
    const batch = report.batch_metrics || {};
    const summary = exportState.sustainabilitySummary || null;
    const reconciliation = exportState.reconciliation || null;

    return [
        "# Afterlife AI — Rescue Decision Report",
        "",
        "> Traceable surplus rescue decision support. This report is advisory only; no physical action is executed automatically.",
        "",
        `- Request: ${markdownInlineCode(report.request_id || "unknown")}`,
        `- Analyzed: ${markdownDate(report.analysis_timestamp)}`,
        `- Optimization objective: ${markdownHumanize(report.optimization_objective)}`,
        `- Solver status: ${markdownHumanize(report.optimization_solver_status)}`,
        `- Final approval: ${markdownHumanize(report.human_final_approval_status)}`,
        "",
        "## Decision Summary",
        "",
        "| Measure | Value |",
        "|---|---:|",
        `| Input lots | ${markdownNumber(batch.input_lots)} |`,
        `| Input quantity | ${markdownNumber(batch.input_quantity)} |`,
        `| Protected | ${markdownNumber(batch.protected_quantity)} |`,
        `| Monitor | ${markdownNumber(batch.monitor_quantity)} |`,
        `| Rescue planning scope | ${markdownNumber(batch.planning_quantity)} |`,
        `| Expired | ${markdownNumber(batch.expired_quantity)} |`,
        `| Human review | ${markdownNumber(batch.review_quantity)} |`,
        `| Allocated | ${markdownNumber(batch.allocated_planning_quantity)} |`,
        `| Unallocated | ${markdownNumber(batch.unallocated_planning_quantity)} |`,
        `| Expected rescue | ${markdownNumber(batch.expected_physical_rescue_quantity)} |`,
        `| Expected waste | ${markdownNumber(batch.expected_waste_quantity)} |`,
        `| Expected rescue ratio | ${markdownPercent(batch.expected_rescue_ratio)} |`,
        `| Expected economic value | ${markdownCurrency(batch.expected_total_economic_value)} |`,
        "",
        "## Sustainability Impact",
        "",
        markdownSustainability(summary),
        "## Selected Rescue Plan",
        "",
        markdownSelectedAllocations(report),
        "## Alternatives",
        "",
        markdownAlternatives(report),
        "",
        "## Outcome Reconciliation",
        "",
        markdownOutcomeReconciliation(reconciliation, summary),
        "## Human Review",
        "",
        markdownHumanReview(report),
        "",
        "## Evidence & Provenance",
        "",
        markdownEvidence(report),
        "## Limitations",
        "",
        markdownLimitations(report),
        "",
        "---",
        "",
        "Generated by Afterlife AI. Expected/model-derived values and operator-confirmed realized outcomes are labeled separately.",
        "",
    ].join("\n");
}

function markdownFilename(requestId) {
    const safeRequestId = String(requestId || "unknown")
        .replace(/[^a-zA-Z0-9._-]+/g, "-")
        .replace(/^-+|-+$/g, "")
        || "unknown";

    return `afterlife-ai-rescue-report-${safeRequestId}.md`;
}

function downloadAfterlifeMarkdownReport(event) {
    if (!latestReport) {
        return;
    }

    event.preventDefault();

    const exportState = window.AfterlifeReportExportState || {};
    const markdown = buildAfterlifeMarkdownReport(latestReport, exportState);
    const blob = new Blob([markdown], {
        type: "text/markdown;charset=utf-8",
    });
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = markdownFilename(latestReport.request_id);

    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(objectUrl);
}

if (markdownDownloadButton) {
    markdownDownloadButton.textContent = "Download Markdown Report";
    markdownDownloadButton.addEventListener(
        "click",
        downloadAfterlifeMarkdownReport
    );
}
