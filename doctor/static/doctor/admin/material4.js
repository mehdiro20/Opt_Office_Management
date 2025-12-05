document.addEventListener('DOMContentLoaded', function () {
    var select = document.getElementById("id_material");
    var otherInput = document.getElementById("id_other_material");

    if (!select || !otherInput) {
        // Elements not present on this page (maybe using a different form)
        return;
    }

    // Try to find the row container (Django admin structure varies by version)
    function findRow(elem) {
        // admin 2.x/3.x: .form-row
        var row = elem.closest('.form-row');
        if (row) return row;
        // fallback to field-box wrapper
        return elem.closest('.field-box') || elem.parentElement;
    }

    var otherRow = findRow(otherInput);

    function toggleOther() {
        if (select.value === "other") {
            if (otherRow) otherRow.style.display = '';
            otherInput.required = true;
        } else {
            if (otherRow) otherRow.style.display = 'none';
            otherInput.required = false;
            otherInput.value = '';  // optional: clear
        }
    }

    // initial state
    toggleOther();

    // watch changes
    select.addEventListener('change', toggleOther);
});
