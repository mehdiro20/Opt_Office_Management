(function () {
  "use strict";

  // -----------------------------
  // 1️⃣ Define all checkbox → target field pairs
  // target can be a string or an array of strings
  // -----------------------------
  const FIELD_PAIRS = [
    { checkbox: "tintable", target: ["tintcolors"] },
    { checkbox: "antireflex", target: ["antireflexcolor","antireflexfeature"] },
    { checkbox: "hydrophobe", target: ["hydrophobe_features"] },

    { checkbox: "blue_light_filter", target: ["bluecontrol","bluecut","coating_features"] },
    { checkbox: "uv_protection", target: ["uvblocking_features","uv400"] },
    { checkbox: "photochromic", target: ["rayblock_precentage", "transition","photochromic_features"] }, // multiple targets
    { checkbox: "occupational_lens", target: ["protections_features","best_occupational_use"] }
  ];

  // -----------------------------
  // 2️⃣ Helper: enable/disable element
  // -----------------------------
  function setDisabled(el, disabled) {
    if (!el) return;
    if (disabled) {
      el.setAttribute("disabled", "disabled");
      el.classList.add("disabled-by-toggle");
    } else {
      el.removeAttribute("disabled");
      el.classList.remove("disabled-by-toggle");
    }
  }

  // -----------------------------
  // 3️⃣ Find checkbox + target elements in a context
  // -----------------------------
  function findControls(context = document) {
    const controls = [];

    FIELD_PAIRS.forEach(pair => {
      const targets = Array.isArray(pair.target) ? pair.target : [pair.target];

      // By ID for main form
      const checkboxById = context.getElementById("id_" + pair.checkbox);
      const targetsById = targets.map(t => context.getElementById("id_" + t));

      // By Name (inlines)
      const checkboxByName = Array.from(context.querySelectorAll(`[name$="${pair.checkbox}"]`));
      const targetsByName = targets.map(t =>
        Array.from(context.querySelectorAll(`[name$="${t}"], textarea[name$="${t}"], select[name$="${t}"]`))
      );

      // Determine max number of instances
      const maxInstances = Math.max(
        checkboxByName.length || (checkboxById ? 1 : 0),
        ...targetsByName.map(arr => arr.length || (targetsById ? 1 : 0))
      );

      for (let i = 0; i < maxInstances; i++) {
        controls.push({
          checkbox: checkboxByName[i] || checkboxById || null,
          targets: targetsByName.map((arr, idx) => arr[i] || targetsById[idx] || null)
        });
      }

      // Fallback regex search
      if (!controls.length) {
        const checkboxGuess = Array.from(context.querySelectorAll('input, select, textarea'))
          .find(i => new RegExp(pair.checkbox, "i").test(i.id || i.name || ""));
        const targetsGuess = targets.map(t =>
          Array.from(context.querySelectorAll('input, select, textarea'))
            .find(i => new RegExp(t, "i").test(i.id || i.name || ""))
        );
        if (checkboxGuess || targetsGuess.length) {
          controls.push({ checkbox: checkboxGuess || null, targets: targetsGuess });
        }
      }
    });

    return controls;
  }

  // -----------------------------
  // 4️⃣ Apply toggle to each checkbox + targets
  // -----------------------------
  function applyToggle(pair) {
    if (!pair || !pair.checkbox || !pair.targets) return;
    const enabled = pair.checkbox.checked;

    pair.targets.forEach(targetEl => {
      setDisabled(targetEl, !enabled);
    });
  }

  function wireUp(context = document) {
    const controls = findControls(context);
    controls.forEach(pair => {
      applyToggle(pair);
      if (pair.checkbox && !pair.checkbox._toggleAttached) {
        pair.checkbox.addEventListener("change", () => applyToggle(pair));
        pair.checkbox._toggleAttached = true;
      }
    });
  }

  // -----------------------------
  // 5️⃣ Init + observe dynamically added inline rows
  // -----------------------------
  document.addEventListener("DOMContentLoaded", function () {
    wireUp(document);

    if ("MutationObserver" in window) {
      const observer = new MutationObserver(mutations => {
        mutations.forEach(m => {
          m.addedNodes.forEach(node => {
            if (node instanceof HTMLElement) {
              wireUp(node);
            }
          });
        });
      });

      observer.observe(document.body, { childList: true, subtree: true });
    }

    // Fallback for Django admin "Add another"
    document.body.addEventListener("click", e => {
      const btn = e.target.closest(".add-row, .addlink");
      if (btn) {
        setTimeout(() => wireUp(document), 200);
      }
    }, true);
  });

})();

document.addEventListener("DOMContentLoaded", function() {
  function formatNumberInput(input) {
    let value = input.value.replace(/\D/g, '');
    if (value === '') return input.value = '';
    input.value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  const priceInputs = document.querySelectorAll('input[name*="base_price"]');
  priceInputs.forEach(input => {
    input.addEventListener('input', () => formatNumberInput(input));
    input.addEventListener('blur', () => formatNumberInput(input));
  });
});

document.addEventListener("DOMContentLoaded", function() {
  function formatNumberInput(input) {
    let value = input.value.replace(/\D/g, '');
    if (value === '') return input.value = '';
    input.value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  const priceInputs = document.querySelectorAll('input[name*="price"]');
  priceInputs.forEach(input => {
    input.addEventListener('input', () => formatNumberInput(input));
    input.addEventListener('blur', () => formatNumberInput(input));
  });
});
