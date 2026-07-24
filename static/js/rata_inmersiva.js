document.addEventListener("DOMContentLoaded", function () {
    const layers = document.querySelectorAll(".ri-layer");
    const form = document.getElementById("ri-form");
    const btnCalcular = document.getElementById("ri-btn-calcular");
    const trackLine = document.getElementById("ri-track-line");
    const trackFill = document.getElementById("ri-track-fill");
    const trackPercent = document.getElementById("ri-track-percent");
    const checkpointsWrap = document.getElementById("ri-checkpoints");
    const sprite = document.getElementById("ri-sprite");
    const resultado = document.getElementById("ri-resultado");
    const rataTitulo = document.getElementById("ri-rata-titulo");
    const rataDescripcion = document.getElementById("ri-rata-descripcion");

    const campoIds = [
        "id_patrimonio_neto",
        "id_ingreso_mensual",
        "id_gasto_mensual",
        "id_fuentes_ingreso",
        "id_horas_trabajadas",
    ];
    const campos = campoIds.map(function (id) { return document.getElementById(id); });

    // Misma tabla de categorías que la versión clásica (static/js/rata.js),
    // duplicada a propósito para no arriesgar romper esa versión.
    const categoriasRata = [
        { rango: [0, 10], nombre: "Rata Obrera", desc: "Vivís para trabajar, pero tu esfuerzo no se traduce en avance financiero. Tu día a día está marcado por la urgencia y el cansancio. Aún no comenzaste a construir libertad, pero estás a tiempo si cambiás el rumbo." },
        { rango: [11, 20], nombre: "Rata Desorientada", desc: "Tenés voluntad de progresar, pero no un plan claro. Probás cosas sueltas, sin una estrategia que te sostenga. Tu energía es valiosa, pero necesita dirección para convertirse en libertad real." },
        { rango: [21, 30], nombre: "Rata Optimista", desc: "Estás dando pasos hacia la salida del laberinto. Quizás ya te hiciste preguntas importantes o empezaste a ahorrar. Tus decisiones aún son limitadas, pero tu mentalidad va en ascenso." },
        { rango: [31, 40], nombre: "Rata Planificadora", desc: "Ya trazaste un camino: presupuestos, organización, metas. Aunque aún dependés del trabajo diario, tu estructura te permite resistir imprevistos y pensar en mediano plazo. Vas bien, seguí así." },
        { rango: [41, 50], nombre: "Rata Emprendedora", desc: "Estás construyendo algo propio. Tal vez no sea estable aún, pero ya no dependés 100% del sistema tradicional. Tu enfoque está en crecer, innovar y expandirte, aunque el riesgo todavía es parte del juego." },
        { rango: [51, 60], nombre: "Rata Estratégica", desc: "No trabajás más: decidís. Elegís qué hacer con tu tiempo y tu dinero. Conocés tus números, diversificás ingresos y sabés cuándo actuar. Tu mentalidad es de constructor de futuro, no de superviviente." },
        { rango: [61, 70], nombre: "Rata Inversionista", desc: "Tu dinero ya empezó a generar más dinero. Usás el interés compuesto, la diversificación y el análisis para consolidar tu libertad. Cada decisión financiera tuya tiene un objetivo claro detrás." },
        { rango: [71, 80], nombre: "Rata Autónoma", desc: "Podés dejar de trabajar hoy mismo si quisieras, aunque todavía elegís no hacerlo. Tu ingreso pasivo supera tus gastos, y vivís con orden, estrategia y visión a largo plazo. Tu libertad es real, pero aún vulnerable." },
        { rango: [81, 90], nombre: "Rata Libre", desc: "Tu situación financiera ya no depende de tu trabajo. Ingresos pasivos, baja carga laboral, control emocional sobre tus decisiones. Vivís desde la abundancia, pero con humildad y visión." },
        { rango: [91, 100], nombre: "Rata Iluminada", desc: "Lograste la libertad financiera plena. Vivís sin presiones económicas y dedicás tu energía a compartir, enseñar o expandir un propósito. Sos un referente: otros pueden aprender de vos." },
    ];

    categoriasRata.forEach(function (cat) {
        const dot = document.createElement("div");
        dot.className = "ri-checkpoint";
        dot.style.left = cat.rango[0] + "%";
        dot.title = cat.nombre;
        dot.dataset.umbral = cat.rango[0];
        checkpointsWrap.appendChild(dot);
    });
    const checkpointEls = checkpointsWrap.querySelectorAll(".ri-checkpoint");

    // Misma fórmula ponderada que static/js/rata.js, para que ambas versiones
    // den siempre el mismo resultado con los mismos datos.
    function calcularLibertad(patrimonio, ingreso, gasto, fuentes, horas) {
        const MRF = gasto > 0 ? Math.min((patrimonio / gasto) / 60 * 100, 100) : 0;
        const TA_bruta = ingreso > 0 ? (ingreso - gasto) / ingreso : 0;
        const TA = TA_bruta <= 0 ? 0 : Math.min(TA_bruta, 0.8) / 0.8 * 100;
        const DI = fuentes === 1 ? 0 : fuentes === 2 ? 50 : 100;
        const CH = Math.max(0, Math.min(100, (12 - horas) / 9 * 100));
        return Math.round((MRF * 0.35) + (TA * 0.35) + (DI * 0.15) + (CH * 0.15));
    }

    function leerValores() {
        return {
            patrimonio: parseFloat(campos[0].value) || 0,
            ingreso: parseFloat(campos[1].value) || 0,
            gasto: parseFloat(campos[2].value) || 0,
            fuentes: parseInt(campos[3].value, 10) || 0,
            horas: parseInt(campos[4].value, 10) || 0,
        };
    }

    function posicionarSprite(pct) {
        const clamped = Math.max(0, Math.min(100, pct));
        sprite.style.left = clamped + "%";
        trackFill.style.width = clamped + "%";
        trackPercent.textContent = clamped + "%";
        checkpointEls.forEach(function (dot) {
            const umbral = parseFloat(dot.dataset.umbral);
            dot.classList.toggle("passed", clamped >= umbral);
        });
    }

    function actualizarVivo() {
        const v = leerValores();
        sprite.classList.remove("ri-sprite-final");
        posicionarSprite(calcularLibertad(v.patrimonio, v.ingreso, v.gasto, v.fuentes, v.horas));
    }

    campos.forEach(function (campo) {
        campo.addEventListener("input", actualizarVivo);
    });

    function spawnParticles(xPercent) {
        for (let i = 0; i < 8; i++) {
            const p = document.createElement("div");
            p.className = "ri-particle";
            p.style.left = xPercent + "%";
            const angle = Math.random() * Math.PI * 2;
            const distancia = 20 + Math.random() * 30;
            p.style.setProperty("--dx", Math.cos(angle) * distancia + "px");
            p.style.setProperty("--dy", Math.sin(angle) * distancia + "px");
            trackLine.appendChild(p);
            p.addEventListener("animationend", function () { p.remove(); });
        }
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const valoresCrudos = campos.map(function (c) { return c.value; });
        if (valoresCrudos.some(function (val) { return val === "" || isNaN(parseFloat(val)); })) {
            alert("Por favor, completá todos los campos correctamente.");
            return;
        }

        const v = leerValores();
        const libertad = calcularLibertad(v.patrimonio, v.ingreso, v.gasto, v.fuentes, v.horas);

        btnCalcular.disabled = true;
        btnCalcular.textContent = "Corriendo...";

        sprite.classList.add("ri-sprite-final");
        posicionarSprite(libertad);

        const particulasInterval = setInterval(function () {
            spawnParticles(libertad);
        }, 150);

        sprite.addEventListener("transitionend", function handler() {
            sprite.removeEventListener("transitionend", handler);
            clearInterval(particulasInterval);
            spawnParticles(libertad);

            const categoria = categoriasRata.find(function (cat) {
                return libertad >= cat.rango[0] && libertad <= cat.rango[1];
            });
            if (categoria) {
                rataTitulo.textContent = categoria.nombre;
                rataDescripcion.textContent = categoria.desc;
            }

            resultado.classList.add("visible");
            resultado.scrollIntoView({ behavior: "smooth", block: "center" });

            btnCalcular.disabled = false;
            btnCalcular.textContent = "🏁 Correr de nuevo";
        }, { once: true });
    });

    // ===== Parallax: scroll (capas a distinta velocidad) + tilt de mouse =====
    let mouseX = 0, mouseY = 0, mouseXActual = 0, mouseYActual = 0;
    let scrollActual = window.scrollY;

    window.addEventListener("mousemove", function (e) {
        mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    window.addEventListener("scroll", function () {
        scrollActual = window.scrollY;
    }, { passive: true });

    function animarParallax() {
        mouseXActual += (mouseX - mouseXActual) * 0.06;
        mouseYActual += (mouseY - mouseYActual) * 0.06;

        layers.forEach(function (layer) {
            const depth = parseFloat(layer.dataset.depth) || 0;
            const tiltX = mouseXActual * depth * 25;
            const tiltY = mouseYActual * depth * 15;
            const scrollOffset = scrollActual * depth * -0.3;
            layer.style.transform = "translate3d(" + tiltX + "px," + (tiltY + scrollOffset) + "px,0)";
        });

        requestAnimationFrame(animarParallax);
    }
    requestAnimationFrame(animarParallax);

    // ===== Reveal on scroll =====
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    }, { threshold: 0.2 });

    document.querySelectorAll(".reveal").forEach(function (el) { observer.observe(el); });

    posicionarSprite(0);
});
