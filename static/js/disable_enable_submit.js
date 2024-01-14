/** @format */

function checkFields(formId) {
    const form = document.getElementById(formId);
    if (!form) {
        return;
    }

    const fields = form.querySelectorAll("input, textarea"); // Get all fields initially
    const inputSubmitButtons = form.querySelectorAll("input[type='submit']");
    const buttonSubmitButtons = form.querySelectorAll("button");

    console.log("input buttons =", inputSubmitButtons);
    console.log("button buttons =", buttonSubmitButtons);

    // Check for empty fields (only for input buttons)
    if (inputSubmitButtons.length > 0) {
        let hasEmptyFields = false;
        fields.forEach((field) => {
            if (!field.value.trim()) {
                hasEmptyFields = true;
                return; // Stop iterating when empty field is found
            }
        });

        inputSubmitButtons.forEach((button) => {
            // Allow input buttons with 'bypass-disable' class to not be disabled
            if (button.classList.contains("bypass-disable") || !hasEmptyFields) {
                button.classList.remove("disabled");
            } else {
                button.classList.add("disabled");
            }
        });
    }

    // Check for changed fields (only for button elements)
    if (buttonSubmitButtons.length > 0) {
        let hasChanges = false;
        const changedFields = form.querySelectorAll("input[type='text'], textarea"); // Focus on text fields for changes
        changedFields.forEach((field, index) => {
            const originalValue = field.dataset.originalValue;

            // Sets empty string as value instead of undefined
            if (field.value.length == 0) {
                field.value = "";
            }
            if (field.value.trim() !== originalValue && field.value != "") {
                hasChanges = true;
                return; // Stop iterating once a change is detected
            }
        });

        buttonSubmitButtons.forEach((button) => {
            // Allow buttons with 'bypass-disable' class to not be disabled
            if (button.classList.contains("bypass-disable") || hasChanges) {
                button.classList.remove("disabled");
            } else {
                button.classList.add("disabled");
            }
        });
    }
}

// Ensure it works for all forms, even future ones
document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll("form");
    forms.forEach((form) => {
        form.addEventListener("input", () => checkFields(form.id)); // Check whenever any field changes
        checkFields(form.id); // Initial check
    });
});
