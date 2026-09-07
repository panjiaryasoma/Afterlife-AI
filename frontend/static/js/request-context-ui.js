(() => {
    const budgetInput = document.querySelector("#max-logistics-budget");

    if (!budgetInput) {
        return;
    }

    const field = budgetInput.closest(".field");
    const help = field?.querySelector(".field-help");

    budgetInput.value = "";
    budgetInput.disabled = true;
    budgetInput.placeholder = "Unavailable in current runtime";
    budgetInput.setAttribute("aria-disabled", "true");
    budgetInput.title = (
        "Current demo runtime has no non-zero logistics-cost routes, "
        + "so a logistics budget cap would have no effect."
    );

    if (help) {
        help.textContent = (
            "Unavailable in the current demo runtime because no "
            + "non-zero logistics-cost routes are configured."
        );
    }
})();
