(() => {
    const budgetInput = document.querySelector("#max-logistics-budget");

    if (!budgetInput) {
        return;
    }

    const field = budgetInput.closest(".field");
    const help = field?.querySelector(".field-help");

    budgetInput.disabled = false;
    budgetInput.removeAttribute("aria-disabled");
    budgetInput.placeholder = "Optional";
    budgetInput.removeAttribute("title");

    if (help) {
        help.textContent = "Optional request-level budget cap.";
    }
})();
