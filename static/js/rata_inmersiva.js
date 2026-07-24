document.addEventListener("DOMContentLoaded", function () {
    const glows = document.querySelectorAll(".rw-glow");
    const dotsWrap = document.getElementById("rw-dots");
    const wheelZone = document.getElementById("rw-wheel-zone");
    const btnSaltar = document.getElementById("rw-btn-saltar");
    const rat = document.getElementById("rw-rat");
    const form = document.getElementById("rw-form");
    const campos = Array.from(document.querySelectorAll(".rw-campo"));
    const resultado = document.getElementById("rw-resultado");
    const resultadoPercent = document.getElementById("rw-resultado-percent");
    const rataTitulo = document.getElementById("rw-rata-titulo");
    const rataDescripcion = document.getElementById("rw-rata-descripcion");

    const campoIds = [
        "id_patrimonio_neto",
        "id_ingreso_mensual",
        "id_gasto_mensual",
        "id_fuentes_ingreso",
        "id_horas_trabajadas",
    ];
    const totalCampos = campoIds.length;
    let indiceActual = 0;

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
        const ids = campoIds.map(function (id) { return document.getElementById(id); });
        return {
            patrimonio: parseFloat(ids[0].value) || 0,
            ingreso: parseFloat(ids[1].value) || 0,
            gasto: parseFloat(ids[2].value) || 0,
            fuentes: parseInt(ids[3].value, 10) || 0,
            horas: parseInt(ids[4].value, 10) || 0,
        };
    }

    // ===== Puntos de progreso =====
    const dots = [];
    for (let i = 0; i < totalCampos; i++) {
        const dot = document.createElement("div");
        dot.className = "rw-dot";
        dotsWrap.appendChild(dot);
        dots.push(dot);
    }

    function actualizarDots() {
        dots.forEach(function (dot, i) {
            dot.classList.toggle("hecho", i < indiceActual);
            dot.classList.toggle("activo", i === indiceActual);
        });
    }

    // ===== Partículas =====
    function spawnParticles(origen, cantidad) {
        for (let i = 0; i < cantidad; i++) {
            const p = document.createElement("div");
            p.className = "rw-particle";
            const angle = Math.random() * Math.PI * 2;
            const distancia = 30 + Math.random() * 60;
            p.style.setProperty("--dx", Math.cos(angle) * distancia + "px");
            p.style.setProperty("--dy", Math.sin(angle) * distancia + "px");
            origen.appendChild(p);
            p.addEventListener("animationend", function () { p.remove(); });
        }
    }

    // ===== Mostrar rueda / mostrar campo =====
    function mostrarRueda() {
        form.classList.remove("rw-visible");
        wheelZone.classList.remove("rw-oculto");
        btnSaltar.disabled = false;
        btnSaltar.textContent = "🐀 ¡SALTÁ!";
    }

    function mostrarCampo(indice) {
        campos.forEach(function (campo) {
            const esActivo = parseInt(campo.dataset.index, 10) === indice;
            campo.classList.toggle("rw-activo", esActivo);
        });
        wheelZone.classList.add("rw-oculto");
        form.classList.add("rw-visible");
        actualizarDots();

        const campoActivo = campos[indice];
        const input = campoActivo.querySelector("input");
        if (input) {
            window.setTimeout(function () { input.focus(); }, 150);
        }
    }

    btnSaltar.addEventListener("click", function () {
        if (btnSaltar.disabled) return;
        btnSaltar.disabled = true;
        rat.classList.add("rw-jumping");
        spawnParticles(wheelZone, 6);

        window.setTimeout(function () {
            rat.classList.remove("rw-jumping");
            mostrarCampo(indiceActual);
        }, 600);
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const campoActivo = campos[indiceActual];
        const input = campoActivo.querySelector("input");
        const valor = input ? input.value : "";

        if (valor === "" || isNaN(parseFloat(valor))) {
            campoActivo.classList.remove("rw-shake");
            void campoActivo.offsetWidth;
            campoActivo.classList.add("rw-shake");
            input.focus();
            return;
        }
        campoActivo.classList.remove("rw-shake");

        indiceActual += 1;
        actualizarDots();

        if (indiceActual < totalCampos) {
            form.classList.remove("rw-visible");
            window.setTimeout(function () {
                mostrarRueda();
                rat.classList.add("rw-landing");
                window.setTimeout(function () { rat.classList.remove("rw-landing"); }, 500);
            }, 220);
        } else {
            form.classList.remove("rw-visible");
            const v = leerValores();
            const libertad = calcularLibertad(v.patrimonio, v.ingreso, v.gasto, v.fuentes, v.horas);
            mostrarResultado(libertad);
        }
    });

    function mostrarResultado(libertad) {
        const categoria = categoriasRata.find(function (cat) {
            return libertad >= cat.rango[0] && libertad <= cat.rango[1];
        });

        resultadoPercent.textContent = libertad + "%";
        if (categoria) {
            rataTitulo.textContent = categoria.nombre;
            rataDescripcion.textContent = categoria.desc;
        }

        resultado.classList.add("rw-visible");
        spawnParticles(resultado.querySelector(".rw-resultado-card"), 14);
        resultado.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // ===== Parallax suave del fondo con el mouse =====
    let mouseX = 0, mouseY = 0, mouseXActual = 0, mouseYActual = 0;

    window.addEventListener("mousemove", function (e) {
        mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    function animarParallax() {
        mouseXActual += (mouseX - mouseXActual) * 0.06;
        mouseYActual += (mouseY - mouseYActual) * 0.06;

        glows.forEach(function (glow, i) {
            const depth = i === 0 ? 30 : 45;
            glow.style.transform = "translate3d(" + (mouseXActual * depth) + "px," + (mouseYActual * depth) + "px,0)";
        });

        requestAnimationFrame(animarParallax);
    }
    requestAnimationFrame(animarParallax);

    actualizarDots();
});
