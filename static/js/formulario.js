document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formulario-financiero");
  const blocks = Array.from(document.querySelectorAll(".question-block"));

  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  const submitBtn = document.getElementById("submitBtn");

  const progressLabel = document.getElementById("progressLabel");
  const progressHint = document.getElementById("progressHint");
  const progressBar = document.getElementById("progressBar");

  const estadoInput = document.getElementById("estado_financiero");

  let currentIndex = 0;
  const stepHints = {
    contexto: "Datos base para calibrar estabilidad y riesgo.",
    ingresos: "Ingresos mensuales aproximados en USD.",
    gastos: "Gastos mensuales para medir margen real.",
    patrimonio_comp: "Activos actuales: liquidez, inversiones, inmuebles y negocio.",
    deuda_comp: "Deudas por tipo para detectar fragilidad.",
    diagnostico: "Lectura dinamica segun ingresos y gastos.",
    objetivos: "Prioridades ordenadas para personalizar el plan.",
    mentalidad: "Conocimiento y confianza en instrumentos financieros.",
    riesgo: "Tu reaccion ante volatilidad define la cartera sugerida.",
    experiencia: "Experiencia previa con inversiones y proyectos.",
    valores: "El tono final se ajusta a lo que el dinero representa para vos.",
  };

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

  function updateProgress() {
    const step = currentIndex + 1;
    const total = blocks.length;
    if (progressLabel) progressLabel.textContent = `Paso ${step} de ${total}`;
    if (progressHint) {
      const active = blocks[currentIndex];
      progressHint.textContent = stepHints[active?.dataset.block] || "Completa el paso para seguir";
    }
    if (progressBar) {
      progressBar.style.width = `${Math.round((step / total) * 100)}%`;
    }
  }

  function fixCopy() {
    const edad = form.querySelector('input[name="edad"]');
    if (edad) {
      edad.min = "15";
      edad.max = "115";
    }

    const laboralLabel = form.querySelector('select[name="estabilidad_laboral"]')?.closest(".field")?.querySelector("label");
    if (laboralLabel) {
      laboralLabel.innerHTML = 'Tu situacion laboral <span class="req">*</span>';
    }

    const laboralPlaceholder = form.querySelector('select[name="estabilidad_laboral"] option[value=""]');
    if (laboralPlaceholder) {
      laboralPlaceholder.textContent = "Elegi una opcion";
    }

    const estabilidadField = form.querySelector('input[name="percepcion_estabilidad"]')?.closest(".field");
    if (estabilidadField) {
      const label = estabilidadField.querySelector("label");
      const small = estabilidadField.querySelector("small");
      if (label) label.innerHTML = 'Que tan estable sentis tu ingreso principal <span class="req">*</span>';
      if (small) small.textContent = "1 = muy fragil, 5 = muy estable";
    }

    const mentalidad = form.querySelector('[data-block="mentalidad"]');
    if (mentalidad) {
      const title = mentalidad.querySelector("h3");
      const desc = mentalidad.querySelector(".desc");
      const fields = mentalidad.querySelectorAll(".field label");
      const fearBias = mentalidad.querySelector('input[value="me_paraliza_perder"]')?.closest(".opt-card")?.querySelector("span");
      if (title) title.textContent = "Relacion con el sistema financiero";
      if (desc) desc.textContent = "Quiero medir cuanto entendes el juego y cuanto ruido te mete.";
      if (fields[0]) fields[0].innerHTML = 'Cuanto entendes de finanzas e inversiones <span class="req">*</span>';
      if (fields[1]) fields[1].innerHTML = 'Cuanta confianza te da el sistema financiero <span class="req">*</span>';
      if (fearBias) fearBias.textContent = "El miedo a perder me frena aunque sepa que hacer";
    }
  }

  function updateNavButtons() {
    const last = currentIndex === blocks.length - 1;
    prevBtn.style.display = currentIndex === 0 ? "none" : "inline-flex";
    nextBtn.style.display = last ? "none" : "inline-flex";
    submitBtn.classList.toggle("hidden", !last);
  }

  function showBlock(index, direction = "right") {
    blocks.forEach((block, i) => {
      block.classList.remove("active", "slide-in-right", "slide-in-left");
      block.style.display = "none";

      if (i === index) {
        block.style.display = "block";
        block.classList.add("active");
        block.classList.add(direction === "right" ? "slide-in-right" : "slide-in-left");
      }
    });

    updateNavButtons();
    updateProgress();

    const active = blocks[currentIndex];
    if (active && active.dataset.block === "diagnostico") {
      calcularEstadoFinanciero();
    }
  }

  function getNumber(name) {
    const value = form[name]?.value;
    const parsed = parseFloat(value || 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function describeRange(input) {
    const value = Number(input.value || 0);
    if (input.name === "percepcion_estabilidad") {
      return ["muy fragil", "fragil", "intermedia", "estable", "muy estable"][value - 1] || "";
    }
    if (input.name === "conocimiento_financiero") {
      return ["muy bajo", "bajo", "intermedio", "bueno", "alto"][value - 1] || "";
    }
    if (input.name === "confianza_sistema") {
      return ["muy baja", "baja", "mixta", "buena", "alta"][value - 1] || "";
    }
    return "";
  }

  function paintRange(input) {
    const min = Number(input.min || 0);
    const max = Number(input.max || 100);
    const value = Number(input.value || min);
    const percent = max > min ? ((value - min) / (max - min)) * 100 : 0;
    const hue = 8 + (percent * 1.3);
    input.style.setProperty("--range-progress", `${percent}%`);
    input.style.setProperty("--range-color", `hsl(${hue}, 82%, 56%)`);
    input.style.setProperty("--range-color-soft", `hsla(${hue}, 82%, 56%, 0.18)`);

    const small = input.parentElement?.querySelector("small");
    const descriptor = describeRange(input);
    if (small && descriptor) {
      small.textContent = `${value}/5 | ${descriptor}`;
    }
  }

  function enhanceRanges() {
    form.querySelectorAll('input[type="range"]').forEach(input => {
      paintRange(input);
      input.addEventListener("input", () => paintRange(input));
    });
  }

  fixCopy();
  enhanceRanges();

  function calcularEstadoFinanciero() {
    const ingresos = [
      "ingreso_trabajo",
      "ingreso_negocio",
      "ingreso_emprendimiento",
      "ingreso_rentas",
      "ingreso_inversiones",
      "ingreso_otros",
    ].reduce((sum, key) => sum + getNumber(key), 0);

    const gastos = [
      "gasto_necesarios",
      "gasto_innecesarios",
      "gasto_financieros",
    ].reduce((sum, key) => sum + getNumber(key), 0);
    const inversionPct = clamp(getNumber("gasto_inversiones"), 0, 100);
    const inversionMensual = ingresos * (inversionPct / 100);
    const flujoLibre = ingresos - gastos - inversionMensual;

    let estado = "estancado";
    if (flujoLibre > ingresos * 0.15) estado = "capacidad_construccion";
    if (flujoLibre <= 0) estado = "riesgo_estructural";

    if (estadoInput) estadoInput.value = estado;

    form.querySelectorAll(".dynamic-block").forEach(block => block.classList.add("hidden"));
    const toShow = form.querySelector(`.dynamic-block[data-show-if="${estado}"]`);
    if (toShow) toShow.classList.remove("hidden");
  }

  function enforceMax(group) {
    const max = parseInt(group.dataset.max || "99", 10);
    const checks = Array.from(group.querySelectorAll('input[type="checkbox"]'));
    const checked = checks.filter(check => check.checked);

    if (checked.length > max) {
      checked[checked.length - 1].checked = false;
    }
  }

  document.querySelectorAll(".options").forEach(group => {
    group.addEventListener("change", event => {
      if (event.target?.type === "checkbox") {
        enforceMax(group);
      }
    });
  });

  function setupOrderedCards(containerId, prefix) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const max = parseInt(container.dataset.max || "99", 10);
    let order = [];

    container.addEventListener("change", event => {
      const input = event.target;
      if (!input || input.type !== "checkbox") return;

      if (input.checked) {
        if (order.length >= max) {
          input.checked = false;
          return;
        }
        order.push(input.value);
      } else {
        order = order.filter(value => value !== input.value);
      }

      container.querySelectorAll(".opt-card").forEach(card => {
        const cardInput = card.querySelector("input");
        const badge = card.querySelector(".badge");
        if (!cardInput || !badge) return;

        const idx = order.indexOf(cardInput.value);
        if (idx === -1) {
          badge.classList.add("hidden");
          badge.textContent = "";
        } else {
          badge.classList.remove("hidden");
          badge.textContent = idx + 1;
        }
      });

      form.querySelectorAll(`input[name^="${prefix}_"]`).forEach(inputEl => inputEl.remove());
      order.forEach((value, idx) => {
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = `${prefix}_${idx + 1}`;
        hidden.value = value;
        form.appendChild(hidden);
      });
    });
  }

  setupOrderedCards("objetivosCards", "objetivo");
  setupOrderedCards("valoresCards", "valor");

  function validateCurrentBlock() {
    const block = blocks[currentIndex];
    clearError(block);
    const name = block.dataset.block;

    if (name === "contexto") {
      if (!form.edad?.value) {
        showError(block, "Necesito tu edad para contextualizar el diagnostico.");
        return false;
      }
      const edad = getNumber("edad");
      if (edad < 15 || edad > 115) {
        showError(block, "La edad debe estar entre 15 y 115 anos.");
        return false;
      }
      if (!form.estabilidad_laboral?.value) {
        showError(block, "Elegi como esta hoy tu situacion laboral.");
        return false;
      }
      if (!form.querySelector('input[name="situacion_habitacional"]:checked')) {
        showError(block, "Elegi tu situacion habitacional.");
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
        "ingreso_otros",
      ].reduce((sum, key) => sum + getNumber(key), 0);

      if (total <= 0) {
        showError(block, "Carga al menos un ingreso.");
        return false;
      }
      return true;
    }

    if (name === "gastos") {
      const total = [
        "gasto_necesarios",
        "gasto_innecesarios",
        "gasto_financieros",
      ].reduce((sum, key) => sum + getNumber(key), 0);

      if (total <= 0) {
        showError(block, "Carga al menos un gasto real. El porcentaje de inversion va aparte.");
        return false;
      }
      const inversionPct = getNumber("gasto_inversiones");
      if (inversionPct < 0 || inversionPct > 100) {
        showError(block, "El porcentaje destinado a inversion debe estar entre 0 y 100.");
        return false;
      }
      return true;
    }

    if (name === "objetivos") {
      if (block.querySelectorAll('input[type="checkbox"]:checked').length < 1) {
        showError(block, "Elegi al menos una prioridad.");
        return false;
      }
      return true;
    }

    if (name === "mentalidad") {
      if (block.querySelectorAll('input[name="sesgos_sistema"]:checked').length < 1) {
        showError(block, "Marca al menos un sesgo o la opcion de que no sentis uno fuerte.");
        return false;
      }
      return true;
    }

    if (name === "riesgo") {
      if (!form.querySelector('input[name="reaccion_perdida"]:checked')) {
        showError(block, "Elegi una reaccion.");
        return false;
      }
      return true;
    }

    if (name === "valores") {
      if (block.querySelectorAll('input[type="checkbox"]:checked').length < 1) {
        showError(block, "Elegi al menos un valor.");
        return false;
      }
      return true;
    }

    return true;
  }

  nextBtn.addEventListener("click", () => {
    if (!validateCurrentBlock()) return;
    if (currentIndex < blocks.length - 1) {
      currentIndex += 1;
      showBlock(currentIndex, "right");
    }
  });

  prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
      currentIndex -= 1;
      showBlock(currentIndex, "left");
    }
  });

  form.addEventListener("keydown", event => {
    if (event.key === "Enter") {
      const tag = (event.target?.tagName || "").toLowerCase();
      if (tag === "textarea") return;
      event.preventDefault();
      nextBtn.click();
    }
  });

  showBlock(currentIndex);
});
