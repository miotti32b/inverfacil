document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formulario-financiero");
  const blocks = Array.from(document.querySelectorAll(".question-block"));

  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  const submitBtn = document.getElementById("submitBtn");

  const progressLabel = document.getElementById("progressLabel");
  const progressBar = document.getElementById("progressBar");

  const estadoInput = document.getElementById("estado_financiero");

  let currentIndex = 0;

  /* =========================
     Helpers error
  ========================= */
  function showError(block, msg) {
    const box = block.querySelector(".form-error");
    if (!box) return;
    box.textContent = msg;
    box.classList.remove("hidden");
  }

  function clearError(block) {
    const box = block.querySelector(".form-error");
    if (!box) return;
    box.textContent = "";
    box.classList.add("hidden");
  }

  /* =========================
     Progress
  ========================= */
  function updateProgress() {
    const step = currentIndex + 1;
    const total = blocks.length;
    if (progressLabel) progressLabel.textContent = `Paso ${step} de ${total}`;
    if (progressBar) {
      progressBar.style.width = `${Math.round((step / total) * 100)}%`;
    }
  }

  /* =========================
     Mostrar bloque + slide
  ========================= */
  function showBlock(index, direction = "right") {
    blocks.forEach((b, i) => {
      b.classList.remove("active", "slide-in-right", "slide-in-left");
      b.style.display = "none";

      if (i === index) {
        b.style.display = "block";
        b.classList.add("active");
        b.classList.add(
          direction === "right" ? "slide-in-right" : "slide-in-left"
        );
      }
    });

    updateNavButtons();
    updateProgress();

    const active = blocks[currentIndex];
    if (active && active.dataset.block === "diagnostico") {
      calcularEstadoFinanciero();
    }
  }

  /* =========================
     Nav buttons
  ========================= */
  function updateNavButtons() {
    const last = currentIndex === blocks.length - 1;

    prevBtn.style.display = currentIndex === 0 ? "none" : "inline-flex";
    nextBtn.style.display = last ? "none" : "inline-flex";
    submitBtn.classList.toggle("hidden", !last);
  }

  /* =========================
     Utils numéricos
  ========================= */
  function getNumber(name) {
    const v = form[name]?.value;
    const n = parseFloat(v || 0);
    return Number.isFinite(n) ? n : 0;
  }

  /* =========================
     Diagnóstico silencioso
  ========================= */
  function calcularEstadoFinanciero() {
    const ingresos = [
      "ingreso_trabajo",
      "ingreso_negocio",
      "ingreso_emprendimiento",
      "ingreso_rentas",
      "ingreso_inversiones",
      "ingreso_otros"
    ].reduce((s, k) => s + getNumber(k), 0);

    const gastos = [
      "gasto_necesarios",
      "gasto_innecesarios",
      "gasto_financieros",
      "gasto_inversiones"
    ].reduce((s, k) => s + getNumber(k), 0);

    let estado = "estancado";
    if (ingresos > gastos * 1.15) estado = "capacidad_construccion";
    if (ingresos <= gastos) estado = "riesgo_estructural";

    if (estadoInput) estadoInput.value = estado;

    const dynamicBlocks = form.querySelectorAll(".dynamic-block");
    dynamicBlocks.forEach(b => b.classList.add("hidden"));

    const toShow = form.querySelector(
      `.dynamic-block[data-show-if="${estado}"]`
    );
    if (toShow) toShow.classList.remove("hidden");
  }

  /* =========================
     Max selections por grupo
  ========================= */
  function enforceMax(group) {
    const max = parseInt(group.dataset.max || "99", 10);
    const checks = Array.from(group.querySelectorAll('input[type="checkbox"]'));
    const checked = checks.filter(c => c.checked);

    if (checked.length > max) {
      checked[checked.length - 1].checked = false;
    }
  }

  document.querySelectorAll(".options").forEach(group => {
    group.addEventListener("change", e => {
      if (e.target?.type === "checkbox") {
        enforceMax(group);
      }
    });
  });

  /* =========================
     Cards ordenadas (genérico)
  ========================= */
  function setupOrderedCards(containerId, prefix) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const max = parseInt(container.dataset.max || "99", 10);
    let order = [];

    container.addEventListener("change", e => {
      const input = e.target;
      if (!input || input.type !== "checkbox") return;

      if (input.checked) {
        if (order.length >= max) {
          input.checked = false;
          return;
        }
        order.push(input.value);
      } else {
        order = order.filter(v => v !== input.value);
      }

      // badges
      container.querySelectorAll(".opt-card").forEach(card => {
        const i = card.querySelector("input");
        const badge = card.querySelector(".badge");
        if (!i || !badge) return;

        const idx = order.indexOf(i.value);
        if (idx === -1) {
          badge.classList.add("hidden");
          badge.textContent = "";
        } else {
          badge.classList.remove("hidden");
          badge.textContent = idx + 1;
        }
      });

      // limpiar hidden previos
      form
        .querySelectorAll(`input[name^="${prefix}_"]`)
        .forEach(i => i.remove());

      // crear hidden ordenados
      order.forEach((val, i) => {
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = `${prefix}_${i + 1}`;
        hidden.value = val;
        form.appendChild(hidden);
      });
    });
  }

  /* =========================
     Inicialización dinámicas
  ========================= */
  setupOrderedCards("objetivosCards", "objetivo");
  setupOrderedCards("valoresCards", "valor");
  setupOrderedCards("conocimientoCards", "conocimiento"); // 🧠 NUEVO

  /* =========================
     Validación por bloque
  ========================= */
  function validateCurrentBlock() {
    const block = blocks[currentIndex];
    clearError(block);

    const name = block.dataset.block;

    if (name === "contexto") {
      if (!form.edad?.value) {
        showError(block, "Necesito tu edad para contextualizar el diagnóstico.");
        return false;
      }
      return true;
    }

    if (name === "ingresos") {
      const total = [
        "ingreso_trabajo",
        "ingreso_negocio",
        "ingreso_emprendimiento",
        "ingreso_rentas",
        "ingreso_inversiones",
        "ingreso_otros"
      ].reduce((s, k) => s + getNumber(k), 0);

      if (total <= 0) {
        showError(block, "Cargá al menos un ingreso.");
        return false;
      }
      return true;
    }

    if (name === "gastos") {
      const total = [
        "gasto_necesarios",
        "gasto_innecesarios",
        "gasto_financieros",
        "gasto_inversiones"
      ].reduce((s, k) => s + getNumber(k), 0);

      if (total <= 0) {
        showError(block, "Cargá al menos un gasto.");
        return false;
      }
      return true;
    }

    if (name === "objetivos") {
      if (block.querySelectorAll('input[type="checkbox"]:checked').length < 1) {
        showError(block, "Elegí al menos una prioridad.");
        return false;
      }
      return true;
    }

    if (name === "riesgo") {
      if (!form.querySelector('input[name="reaccion_perdida"]:checked')) {
        showError(block, "Elegí una reacción.");
        return false;
      }
      return true;
    }

    if (name === "valores") {
      if (
        block.querySelectorAll('input[type="checkbox"]:checked').length < 1
      ) {
        showError(block, "Elegí al menos un valor.");
        return false;
      }
      return true;
    }

    if (name === "conocimiento") {
      if (
        block.querySelectorAll('input[type="checkbox"]:checked').length < 1
      ) {
        showError(
          block,
          "Ordená al menos una opción según tu criterio."
        );
        return false;
      }
      return true;
    }

    return true;
  }

  /* =========================
     Navegación
  ========================= */
  nextBtn.addEventListener("click", () => {
    if (!validateCurrentBlock()) return;
    if (currentIndex < blocks.length - 1) {
      currentIndex++;
      showBlock(currentIndex, "right");
    }
  });

  prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
      currentIndex--;
      showBlock(currentIndex, "left");
    }
  });

  form.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      const tag = (e.target?.tagName || "").toLowerCase();
      if (tag === "textarea") return;
      e.preventDefault();
      nextBtn.click();
    }
  });

  /* =========================
     Init
  ========================= */
  showBlock(currentIndex);
});
