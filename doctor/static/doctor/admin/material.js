

(function() {
    const select = document.getElementById("id_material");
    const otherField = document.getElementById("id_other_material").closest('.form-row');

    function toggle() {
        if (select.value === "other") {
            otherField.style.display = "block";
        } else {
            otherField.style.display = "none";
        }
    }

    toggle();
    select.addEventListener("change", toggle);
})();