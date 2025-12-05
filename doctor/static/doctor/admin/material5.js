document.addEventListener('DOMContentLoaded', function () {
    var select = document.getElementById("id_material");
    var otherInput = document.getElementById("id_other_material");
    var otherLabel = document.querySelector("label[for='id_other_material']");

    if (!select || !otherInput) return;

    function toggleOther() {
        if (select.value === "other") {
            otherInput.style.display = '';
            if (otherLabel) otherLabel.style.display = '';
            otherInput.required = true;
        } else {
            otherInput.style.display = 'none';
            if (otherLabel) otherLabel.style.display = 'none';
            otherInput.required = false;
            otherInput.value = '';  // optional: clear value
        }
    }

    // initial state
    toggleOther();

    // watch changes
    select.addEventListener('change', toggleOther);
});
