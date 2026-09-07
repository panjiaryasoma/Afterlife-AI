(() => {
    const form = document.querySelector("#analysis-form");
    const budgetInput = document.querySelector("#max-logistics-budget");
    const deadlineInput = document.querySelector("#rescue-deadline");
    const objectiveInput = document.querySelector("#optimization-objective");
    const rescueRatioInput = document.querySelector("#minimum-rescue-ratio");
    const results = document.querySelector("#results");
    const summarySection = document.querySelector(
        '[aria-labelledby="rescue-summary-title"]'
    );

    if (
        !form
        || !budgetInput
        || !deadlineInput
        || !objectiveInput
        || !rescueRatioInput
        || !results
        || !summarySection
    ) {
        return;
    }

    const SUMMARY_ID = "request-context-summary";
    let submittedContext = null;

    function finiteNumber(value) {
        if (value === null || value === undefined || value === "") {
            return null;
        }

        const numeric = Number(value);
        return Number.isFinite(numeric) ? numeric : null;
    }

    function deadlineIsoValue() {
        if (!deadlineInput.value) {
            return null;
        }

        const deadline = new Date(deadlineInput.value);

        return Number.isNaN(deadline.getTime())
            ? null
            : deadline.toISOString();
    }

    function captureSubmittedContext() {
        submittedContext = {
            optimizationObjective: objectiveInput.value,
            maxLogisticsBudget: finiteNumber(budgetInput.value),
            minimumExpectedRescueRatio: finiteNumber(
                rescueRatioInput.value
            ),
            rescueDeadlineAt: deadlineIsoValue(),
        };

        window.AfterlifeRequestContext = {
            ...submittedContext,
        };

        document.querySelector(`#${SUMMARY_ID}`)?.remove();
    }

    function selectedMaxCompletionHours(report) {
        const values = safeArray(report.selected_allocations)
            .map((item) => finiteNumber(item.estimated_completion_hours))
            .filter((value) => value !== null);

        return values.length > 0 ? Math.max(...values) : null;
    }

    function logisticsAllocationCount(report) {
        return safeArray(report.selected_allocations).filter(
            (item) => {
                const cost = finiteNumber(item.logistics_cost);
                return cost !== null && cost > 0;
            }
        ).length;
    }

    function timingRejectedCount(report) {
        return safeArray(report.rejected_candidates).filter(
            (item) => safeArray(item.rejection_reason_codes).includes(
                "TIMING_INFEASIBLE"
            )
        ).length;
    }

    function formatDeadline(value) {
        if (!value) {
            return "No deadline";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "Invalid deadline";
        }

        return date.toLocaleString(undefined, {
            dateStyle: "medium",
            timeStyle: "short",
        });
    }

    function requestWindowHours(report, deadlineValue) {
        if (!deadlineValue || !report.analysis_timestamp) {
            return null;
        }

        const deadline = new Date(deadlineValue);
        const analyzed = new Date(report.analysis_timestamp);

        if (
            Number.isNaN(deadline.getTime())
            || Number.isNaN(analyzed.getTime())
        ) {
            return null;
        }

        return (
            deadline.getTime() - analyzed.getTime()
        ) / (60 * 60 * 1000);
    }

    function budgetUsageNote(cap, used) {
        if (cap === null) {
            return "No request-level logistics cap";
        }

        if (used === null) {
            return "Optimizer usage was not reported";
        }

        if (used === 0) {
            return "No selected allocation consumed logistics budget";
        }

        if (cap === 0) {
            return "Zero-cap request";
        }

        if (used === cap) {
            return "Cap fully used";
        }

        if (used < cap) {
            return `${formatPercent(used / cap)} of cap used`;
        }

        return "Usage exceeds submitted cap";
    }

    function deadlineUsageNote(windowHours, maxCompletionHours) {
        if (windowHours === null) {
            return "No request-level completion cutoff";
        }

        if (windowHours < 0) {
            return "Submitted deadline is before the analysis timestamp";
        }

        if (maxCompletionHours === null) {
            return `${formatNumber(windowHours)} h request window`;
        }

        const headroom = windowHours - maxCompletionHours;

        if (headroom >= 0) {
            return (
                `${formatNumber(headroom)} h headroom versus the `
                + "longest selected action"
            );
        }

        return "Selected action completion exceeds the request window";
    }

    function renderRequestContextSummary() {
        if (
            !submittedContext
            || results.classList.contains("hidden")
            || typeof latestReport === "undefined"
            || !latestReport
        ) {
            return;
        }

        const report = latestReport;
        const batch = report.batch_metrics || {};
        const cap = submittedContext.maxLogisticsBudget;
        const used = finiteNumber(batch.logistics_budget_used);
        const deadlineValue = submittedContext.rescueDeadlineAt;
        const windowHours = requestWindowHours(
            report,
            deadlineValue
        );
        const maxCompletionHours = selectedMaxCompletionHours(report);
        const logisticsCount = logisticsAllocationCount(report);
        const timingRejected = timingRejectedCount(report);

        let summary = document.querySelector(`#${SUMMARY_ID}`);

        if (!summary) {
            summary = document.createElement("div");
            summary.id = SUMMARY_ID;
            summary.className = "summary-group";

            const groups = [...summarySection.children].filter(
                (element) => element.classList.contains("summary-group")
            );

            if (groups.length >= 2) {
                groups[1].before(summary);
            } else {
                summarySection.appendChild(summary);
            }
        }

        summary.innerHTML = `
            <div class="section-heading">
                <div>
                    <p class="section-index">REQUEST CONSTRAINTS</p>
                </div>
                <p class="section-note">
                    Identical plans are expected when a submitted cap or
                    deadline is not binding. This block shows the request
                    context alongside what the optimizer actually used.
                </p>
            </div>
            <div class="metric-grid">
                ${metric(
                    "Logistics cap",
                    cap === null ? "No cap" : formatCurrency(cap),
                    "Submitted request-level ceiling"
                )}
                ${metric(
                    "Logistics used",
                    used === null ? "—" : formatCurrency(used),
                    budgetUsageNote(cap, used)
                )}
                ${metric(
                    "Cost-bearing allocations",
                    formatNumber(logisticsCount),
                    "Selected allocations with logistics cost > 0"
                )}
                ${metric(
                    "Rescue deadline",
                    formatDeadline(deadlineValue),
                    deadlineUsageNote(windowHours, maxCompletionHours)
                )}
                ${metric(
                    "Longest selected action",
                    maxCompletionHours === null
                        ? "—"
                        : `${formatNumber(maxCompletionHours)} h`,
                    "Estimated completion for selected allocations"
                )}
                ${metric(
                    "Timing-rejected candidates",
                    formatNumber(timingRejected),
                    "Includes product timing windows and request deadline"
                )}
            </div>
        `;
    }

    form.addEventListener("submit", captureSubmittedContext);

    const observer = new MutationObserver(() => {
        renderRequestContextSummary();
    });

    observer.observe(results, {
        attributes: true,
        attributeFilter: ["class"],
    });
})();
