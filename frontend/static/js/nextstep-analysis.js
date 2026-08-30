const NEXTSTEP_REPORT_EVENT = "afterlife:nextstep-report";
const NEXTSTEP_CLEAR_EVENT = "afterlife:nextstep-clear";

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

async function handleNextStepAnalysisSubmit(event) {
    if (event.target !== form) {
        return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();

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
        data.append(
            "minimum_expected_rescue_ratio",
            rescueRatioInput.value
        );
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
}

document.addEventListener(
    "submit",
    handleNextStepAnalysisSubmit,
    true
);
