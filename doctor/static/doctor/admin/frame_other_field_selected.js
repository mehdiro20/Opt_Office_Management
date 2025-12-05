document.addEventListener("DOMContentLoaded", function () {
    // Select the material dropdown
    const materialField = document.querySelector("#id_material");
    // Select the "other_material_details" input
    const otherField = document.querySelector("#id_other_material_details");

    if (!materialField || !otherField) return;

    // Get the whole form row containing the "other" field
    const otherMaterialRow = otherField.closest(".form-row");

    // Initially hide the field
    otherMaterialRow.style.display = "none";

    // Function to toggle visibility
    function toggleOtherMaterial() {
        if (materialField.value === "other") {
            otherMaterialRow.style.display = "flex"; // show
        } else {
            otherMaterialRow.style.display = "none"; // hide
        }
    }

    // Run on page load in case "other" is pre-selected
    toggleOtherMaterial();

    // Run every time the material field changes
    materialField.addEventListener("change", toggleOtherMaterial);
});
