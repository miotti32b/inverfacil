document.addEventListener("DOMContentLoaded", () => {

  /* === 1. Generación dinámica de opciones === */
  const grupos = {
      objetivos: [
        "🏠 Comprar vivienda propia","🚗 Adquirir vehículo","💸 Lograr independencia financiera",
        "⏳ Alcanzar jubilación anticipada","🌍 Viajar y disfrutar experiencias","🎓 Invertir en educación o formación",
        "🚀 Desarrollar o expandir mi negocio","📈 Aumentar mis ahorros e inversiones","🧘‍♂️ Mejorar mi calidad y estabilidad de vida"
      ],
      reaccion_perdida: [
        "🚨 Vendés todo para evitar más pérdidas",
        "😬 Vendés una parte por precaución",
        "😌 Mantenés la posición confiando en tu análisis",
        "🧠 Comprás más aprovechando el precio bajo",
        "🕊️ No hacés nada, esperás a que se recupere con el tiempo",
        "🧮 Analizás datos y buscás asesoramiento antes de decidir",
        "📉 Aumentás tus aportes mensuales para compensar la baja",
        "💬 Consultás con amigos o foros para ver qué hacen los demás",
        "🤷‍♂️ Ignorás el tema hasta que vuelva a subir solo"
      ],

      importancia_dinero: [
        "🛡️ Seguridad y tranquilidad","🕊️ Libertad y autonomía","🎯 Lograr metas y crecimiento personal",
        "❤️ Disfrutar la vida y experiencias","🌟 Reconocimiento o status","🤝 Ayudar a otros y generar impacto",
        "🏗️ Crear oportunidades o proyectos","📚 Aprender y superarme","⚖️ Mantener equilibrio y estabilidad"
      ],
      uso_millon: [
        "🌍 Viajar o vivir nuevas experiencias","🏦 Guardar para emergencias o estabilidad","🏢 Invertir en un negocio o inmueble",
        "📊 Diversificar en distintos activos financieros","🎓 Invertir en educación o desarrollo personal","💞 Compartir o donar parte del dinero",
        "🧱 Construir o remodelar mi vivienda","🚀 Financiar proyectos propios o familiares","📉 Cancelar todas mis deudas"
      ],
      resultados_emprendimientos: [
        "❌ No tuve experiencias aún","📚 Estoy iniciando mi primer proyecto","💸 Fracasé pero aprendí del proceso",
        "⚙️ Mantengo un negocio rentable","🚀 Logré escalar o vender mi empresa","🧭 Estoy planificando mi próximo emprendimiento",
        "🤝 Participo como socio o inversor","📊 Dirijo o gestiono varios proyectos","🏛️ Fundé una empresa consolidada"
      ],
      conocimiento_seguridad: [
        "💵 Dólares en cuenta bancaria","🇺🇸 Bonos del Tesoro de EE.UU.","🌾 Tierras o bienes raíces",
        "🏭 Negocio propio consolidado","🎓 Educación o conocimiento","🕒 Plazo fijo en dólares",
        "🏦 Fondos comunes conservadores","💎 Oro u otros metales preciosos","🪙 Criptoactivos estables (stablecoins)"
      ]
  };


  Object.entries(grupos).forEach(([id, opciones]) => {
    const container = document.getElementById(id);
    if (!container) return;
    container.classList.add("grid");
    opciones.forEach((texto, i) => {
      const input = document.createElement("input");
      input.type = "checkbox";
      input.id = `${id}_${i}`;
      input.name = id;
      input.value = texto;

      const label = document.createElement("label");
      label.htmlFor = input.id;
      label.innerText = texto;

      container.appendChild(input);
      container.appendChild(label);
    });
  });

  /* === 2. Límite de selección (máx. 3 o 1 según grupo) === */
  function limitSelection(name, max) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
    const msg = document.getElementById(`${name}-msg`);
    checkboxes.forEach(cb => {
      cb.addEventListener("change", () => {
        const checked = [...checkboxes].filter(c => c.checked);
        if (checked.length > max) {
          cb.checked = false;
          msg.textContent = `Máximo ${max} opción${max > 1 ? 'es' : ''} permitida${max > 1 ? 's' : ''}.`;
        } else {
          msg.textContent = "";
        }

        // Si el grupo solo permite 1 opción (ej: reaccion_perdida), desmarcamos las demás
        if (max === 1 && cb.checked) {
          checkboxes.forEach(c => {
            if (c !== cb) c.checked = false;
          });
        }
      });
    });
  }

  // Aplicar límites: 3 para la mayoría, 1 para reaccion_perdida
  [
    ["objetivos", 3],
    ["reaccion_perdida", 1],
    ["importancia_dinero", 3],
    ["uso_millon", 3],
    ["resultados_emprendimientos", 3],
    ["conocimiento_seguridad", 3],
  ].forEach(([g, max]) => limitSelection(g, max));


  /* === 3. Carrusel de preguntas === */
  const questions = document.querySelectorAll(".question");
  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  const submitBtn = document.querySelector(".btn");
  const progress = document.querySelector(".progress");
  const progressText = document.getElementById("progress-text");
  const formulario = document.getElementById("formulario");

  let current = 0;

  function updateProgress() {
    const percent = ((current + 1) / questions.length) * 100;
    progress.style.width = `${percent}%`;
    progressText.textContent = `Pregunta ${current + 1}/${questions.length}`;
  }

  // 🔥 Transición deslizante + ajuste dinámico de altura
  function showQuestion(index) {
    const actual = document.querySelector(".question.active");
    const siguiente = questions[index];

    if (actual) {
      actual.style.transition = "all 0.6s ease";
      actual.style.left = "-100%";
      actual.style.opacity = "0";
      actual.style.pointerEvents = "none";
      actual.classList.remove("active");
    }

    siguiente.style.transition = "none";
    siguiente.style.left = "100%";
    siguiente.style.opacity = "0";
    siguiente.style.pointerEvents = "none";
    siguiente.classList.add("active");

    setTimeout(() => {
      siguiente.style.transition = "all 0.6s ease";
      siguiente.style.left = "0";
      siguiente.style.opacity = "1";
      siguiente.style.pointerEvents = "auto";
    }, 50);

    setTimeout(() => {
      if (formulario && siguiente) {
        const nuevaAltura = siguiente.offsetHeight + 60;
        formulario.style.height = nuevaAltura + "px";
      }
    }, 150);

    updateProgress();
    prevBtn.disabled = index === 0;
    nextBtn.style.display = index === questions.length - 1 ? "none" : "inline-block";
    submitBtn.style.display = index === questions.length - 1 ? "block" : "none";
  }

  nextBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (current < questions.length - 1) current++;
    showQuestion(current);
  });

  prevBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (current > 0) current--;
    showQuestion(current);
  });

  /* === 4. Envío del formulario === */
  form = document.getElementById("formulario");
  console.log("🔍 Script cargado correctamente. Escuchando envío del formulario...");
  form.addEventListener("submit", () => console.log("✅ Formulario enviado correctamente."));

  /* === 5. Fade de entrada general === */
  const quiz = document.querySelector(".quiz-container");
  quiz.style.opacity = 0;
  setTimeout(() => {
    quiz.style.transition = "opacity .6s ease";
    quiz.style.opacity = 1;
  }, 100);

  /* === 6. Inicializar === */
  updateProgress();
  showQuestion(current);
  window.addEventListener("load", () => {
    const activa = document.querySelector(".question.active");
    if (activa && formulario) formulario.style.height = activa.offsetHeight + "px";
  });
});

/* === 7. Avanzar con ENTER en PC === */
document.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    e.preventDefault(); // evita enviar el form
    const nextBtn = document.getElementById("nextBtn");
    if (nextBtn && !nextBtn.disabled) nextBtn.click();
  }
});
