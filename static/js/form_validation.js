function checkFields(formId = "base-signup-form") {
    const form = document.getElementById(formId);
    const fields = form.querySelectorAll("input, textarea");
    const submitButton = form.querySelector("input[type='submit']");

    let allFilled = true;
    fields.forEach(field => {
        if (!field.value.trim()) {
            allFilled = false;
            return;
        }
    });

    if (allFilled) {
        submitButton.classList.remove("disabled");
    } else {
        submitButton.classList.add("disabled");
    }
}

// Ensure it works for all forms, even future ones
document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("input", () => checkFields(form.id)); // Check whenever any field changes
        checkFields(form.id); // Initial check
    });
});