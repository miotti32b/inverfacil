document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formulario-financiero");
  const blocks = Array.from(document.querySelectorAll(".question-block"));
  let currentIndex = 0;

  // ===============================
  // Mostrar bloque con slide lateral
  // ===============================
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
  }

  showBlock(currentIndex);

  // ===============================
  // Navegación automática (Enter)
  // ===============================
  form.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      nextBlock();
    }
  });

  function nextBlock() {
    if (currentIndex < blocks.length - 1) {
      currentIndex++;
      showBlock(currentIndex, "right");
    }
  }

  // ===============================
  // Calcular estado financiero
  // ===============================
  function calcularEstadoFinanciero() {
    const ingresos = [
      "ingreso_trabajo",
      "ingreso_negocio",
      "ingreso_rentas",
      "ingreso_inversiones",
      "ingreso_otros"
    ].reduce((sum, name) => {
      const val = parseFloat(form[name]?.value || 0);
      return sum + val;
    }, 0);

    const gastos = [
      "gasto_necesarios",
      "gasto_innecesarios",
      "gasto_financieros",
      "gasto_inversiones"
    ].reduce((sum, name) => {
      const val = parseFloat(form[name]?.value || 0);
      return sum + val;
    }, 0);

    let estado = "estancado";

    if (ingresos > gastos * 1.15) estado = "capacidad_construccion";
    if (ingresos <= gastos) estado = "riesgo_estructural";

    document.getElementById("estado_financiero").value = estado;

    document.querySelectorAll(".question-block.dynamic").forEach(block => {
      block.classList.add("hidden");
      if (block.dataset.showIf === estado) {
        block.classList.remove("hidden");
      }
    });
  }

  // Ejecutar cálculo cuando termina gastos
  const gastosBlock = document.querySelector('[data-block="gastos"]');
  gastosBlock.addEventListener("focusout", calcularEstadoFinanciero);

  // ===============================
  // Limitar checkboxes (máx N)
  // ===============================
  document.querySelectorAll(".options").forEach(group => {
    const max = parseInt(group.dataset.max || "99");

    group.addEventListener("change", () => {
      const checked = group.querySelectorAll("input[type=checkbox]:checked");
      if (checked.length > max) {
        checked[checked.length - 1].checked = false;
      }
    });
  });

  // ===============================
  // Objetivos con orden de selección
  // ===============================
  const objetivosGroup = document.querySelector(".options.ordered");
  if (objetivosGroup) {
    let orden = [];

    objetivosGroup.addEventListener("change", e => {
      const input = e.target;
      if (!input.checked) {
        orden = orden.filter(v => v !== input.value);
      } else {
        if (orden.length < 3) {
          orden.push(input.value);
        } else {
          input.checked = false;
        }
      }

      // limpiar previos
      form.querySelectorAll("input[name^='objetivo_']").forEach(i => i.remove());

      // crear hidden inputs
      orden.forEach((val, i) => {
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = `objetivo_${i + 1}`;
        hidden.value = val;
        form.appendChild(hidden);
      });
    });
  }
});
