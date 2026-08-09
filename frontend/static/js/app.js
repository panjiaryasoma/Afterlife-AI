const form = document.querySelector("#analysis-form");
const fileInput = document.querySelector("#inventory-file");
const button = document.querySelector("#analyze-button");
const statusMessage = document.querySelector("#status-message");
const results = document.querySelector("#results");
const metrics = document.querySelector("#metrics");
const allocations = document.querySelector("#allocations");
const reviews = document.querySelector("#reviews");
const limitations = document.querySelector("#limitations");
const scoringProvider = document.querySelector("#scoring-provider");
const downloadReport = document.querySelector("#download-report");

let latestReport = null;

function metric(label, value) {
    return `
        <div class="metric">
            <span class="muted">${label}</span>
            <strong>${value}</strong>
        </div>
    `;
}

function renderReport(report) {
    const batch = report.batch_metrics;

    metrics.innerHTML = [
        metric("Input lots", batch.input_lots),
        metric("Input quantity", batch.input_quantity),
        metric("Protected", batch.protected_quantity),
        metric("Monitor", batch.monitor_quantity),
        metric("Planning", batch.planning_quantity),
        metric("Allocated", batch.allocated_planning_quantity),
        metric("Unallocated", batch.unallocated_planning_quantity),
        metric("Expected value", batch.expected_total_economic_value),
    ].join("");

    scoringProvider.textContent =
        report.score_provenance.provider_name;

    if (report.selected_allocations.length === 0) {
        allocations.innerHTML =
            '<p class="muted">No rescue allocation selected.</p>';
    } else {
        allocations.innerHTML = report.selected_allocations
            .map(
                (item) => `
                    <div class="allocation">
                        <strong>${item.action_type}</strong><br>
                        Lot: ${item.source_lot_id}<br>
                        Quantity: ${item.allocated_quantity}<br>
                        Expected recovery: ${item.expected_net_recovery}
                    </div>
                `
            )
            .join("");
    }

    if (report.review_required_lots.length === 0) {
        reviews.innerHTML =
            '<p class="muted">No lot requires manual review.</p>';
    } else {
        reviews.innerHTML = report.review_required_lots
            .map(
                (item) => `
                    <div class="allocation">
                        <strong>${item.source_lot_id}</strong><br>
                        Review quantity: ${item.review_quantity}<br>
                        ${item.reason_codes.join(", ")}
                    </div>
                `
            )
            .join("");
    }

    limitations.innerHTML = report.limitations
        .map((item) => `<li>${item}</li>`)
        .join("");

    results.classList.remove("hidden");
}

function downloadLatestReport() {
    if (!latestReport) {
        return;
    }

    const json = JSON.stringify(
        latestReport,
        null,
        2
    );

    const blob = new Blob(
        [json],
        {
            type: "application/json",
        }
    );

    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    const requestId =
        latestReport.request_id || "unknown";

    link.href = objectUrl;
    link.download =
        `rescue-decision-report-${requestId}.json`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(objectUrl);
}

downloadReport.addEventListener(
    "click",
    downloadLatestReport
);

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        statusMessage.textContent = "Select an XLSX file first.";
        statusMessage.classList.add("error");
        return;
    }

    const data = new FormData();
    data.append("inventory_file", file);

    latestReport = null;

    button.disabled = true;
    downloadReport.classList.add("hidden");
    results.classList.add("hidden");

    statusMessage.classList.remove("error");
    statusMessage.textContent = "Analyzing inventory...";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            body: data,
        });

        const payload = await response.json();

        if (!response.ok) {
            throw new Error(
                payload.detail || "Inventory analysis failed."
            );
        }

        latestReport = payload;

        renderReport(payload);

        downloadReport.classList.remove("hidden");
        statusMessage.textContent = "Analysis completed.";
    } catch (error) {
        latestReport = null;
        downloadReport.classList.add("hidden");

        statusMessage.textContent = error.message;
        statusMessage.classList.add("error");
    } finally {
        button.disabled = false;
    }
});