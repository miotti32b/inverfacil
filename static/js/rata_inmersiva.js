document.addEventListener("DOMContentLoaded", function () {
    const camera = document.getElementById("pv-camera");
    const cylinder = document.getElementById("pv-cylinder");
    const reticulo = document.getElementById("pv-reticulo");
    const instrucciones = document.getElementById("pv-instrucciones");
    const dotsWrap = document.getElementById("pv-dots");
    const form = document.getElementById("pv-form");
    const campos = Array.from(document.querySelectorAll(".pv-campo"));
    const resultado = document.getElementById("pv-resultado");
    const resultadoPercent = document.getElementById("pv-resultado-percent");
    const rataTitulo = document.getElementById("pv-rata-titulo");
    const rataDescripcion = document.getElementById("pv-rata-descripcion");

    const campoIds = [
        "id_patrimonio_neto",
        "id_ingreso_mensual",
        "id_gasto_mensual",
        "id_fuentes_ingreso",
        "id_horas_trabajadas",
    ];
    const totalCampos = campoIds.length;
    let indiceActual = 0;
    let modoActual = "rueda"; // 'rueda' | 'espera' | 'input' | 'resultado'

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
        dot.className = "pv-dot";
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
            p.className = "pv-particle";
            const angle = Math.random() * Math.PI * 2;
            const distancia = 30 + Math.random() * 60;
            p.style.setProperty("--dx", Math.cos(angle) * distancia + "px");
            p.style.setProperty("--dy", Math.sin(angle) * distancia + "px");
            origen.appendChild(p);
            p.addEventListener("animationend", function () { p.remove(); });
        }
    }

    // ===== Construcción del cilindro (la rueda vista desde adentro) =====
    const N_RUNGS = 8;
    const RADIO = 220;
    const GRADOS_POR_SEGUNDO = 80; // vuelta completa ~4.5s
    const VENTANA_CAPTURA = 35; // grados de margen para "atrapar" el travesaño

    let targetRung = null;
    for (let i = 0; i < N_RUNGS; i++) {
        const rung = document.createElement("div");
        rung.className = "pv-rung";
        const baseAngle = i * (360 / N_RUNGS);
        rung.style.transform = "rotateX(" + baseAngle + "deg) translateZ(" + RADIO + "px)";
        if (i === 0) {
            rung.classList.add("pv-rung-target");
            targetRung = rung;
        }
        cylinder.appendChild(rung);
    }

    let anguloGlobal = 0;
    let capturaLista = false;

    // ===== Look-around con mouse + cercanía al retículo =====
    let mouseX = 0, mouseY = 0, mouseXActual = 0, mouseYActual = 0;
    let mouseCerca = false;
    const RADIO_RETICULO = 75;

    window.addEventListener("mousemove", function (e) {
        mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 2;

        const rect = reticulo.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dist = Math.hypot(e.clientX - cx, e.clientY - cy);
        mouseCerca = dist < RADIO_RETICULO;
        reticulo.classList.toggle("pv-cerca", mouseCerca && modoActual === "rueda");
    });

    let ultimoTimestamp = null;
    function animar(timestamp) {
        if (ultimoTimestamp === null) ultimoTimestamp = timestamp;
        const dt = (timestamp - ultimoTimestamp) / 1000;
        ultimoTimestamp = timestamp;

        anguloGlobal = (anguloGlobal + GRADOS_POR_SEGUNDO * dt) % 360;

        let efectivo = anguloGlobal % 360;
        if (efectivo > 180) efectivo -= 360;
        capturaLista = Math.abs(efectivo) < VENTANA_CAPTURA;
        targetRung.classList.toggle("pv-lista", capturaLista);

        cylinder.style.transform = "rotateX(" + anguloGlobal + "deg)";

        mouseXActual += (mouseX - mouseXActual) * 0.08;
        mouseYActual += (mouseY - mouseYActual) * 0.08;
        camera.style.transform = "rotateY(" + (mouseXActual * 10) + "deg) rotateX(" + (-mouseYActual * 8) + "deg)";

        requestAnimationFrame(animar);
    }
    requestAnimationFrame(animar);

    // ===== TAB para atrapar el travesaño =====
    window.addEventListener("keydown", function (e) {
        if (e.key !== "Tab") return;
        if (modoActual !== "rueda") return; // deja el Tab normal mientras se completa un input
        e.preventDefault();

        if (capturaLista && mouseCerca) {
            modoActual = "espera";
            spawnParticles(reticulo, 10);
            window.setTimeout(function () { mostrarCampo(indiceActual); }, 150);
        } else {
            reticulo.classList.remove("pv-fallo");
            void reticulo.offsetWidth;
            reticulo.classList.add("pv-fallo");
        }
    });

    // ===== Mostrar campo / volver a la rueda =====
    function mostrarCampo(indice) {
        campos.forEach(function (campo) {
            campo.classList.toggle("pv-activo", parseInt(campo.dataset.index, 10) === indice);
        });
        reticulo.classList.add("pv-oculto");
        instrucciones.style.opacity = "0";
        form.classList.add("pv-visible");
        modoActual = "input";
        actualizarDots();

        const input = campos[indice].querySelector("input");
        if (input) {
            window.setTimeout(function () { input.focus(); }, 150);
        }
    }

    function volverALaRueda() {
        form.classList.remove("pv-visible");
        reticulo.classList.remove("pv-oculto");
        instrucciones.style.opacity = "1";
        modoActual = "rueda";
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const campoActivo = campos[indiceActual];
        const input = campoActivo.querySelector("input");
        const valor = input ? input.value : "";

        if (valor === "" || isNaN(parseFloat(valor))) {
            campoActivo.classList.remove("pv-shake");
            void campoActivo.offsetWidth;
            campoActivo.classList.add("pv-shake");
            input.focus();
            return;
        }
        campoActivo.classList.remove("pv-shake");

        indiceActual += 1;
        actualizarDots();

        if (indiceActual < totalCampos) {
            window.setTimeout(volverALaRueda, 200);
        } else {
            form.classList.remove("pv-visible");
            reticulo.classList.add("pv-oculto");
            cylinder.classList.add("pv-escapada");
            const v = leerValores();
            const libertad = calcularLibertad(v.patrimonio, v.ingreso, v.gasto, v.fuentes, v.horas);
            mostrarResultado(libertad);
        }
    });

    function mostrarResultado(libertad) {
        modoActual = "resultado";
        const categoria = categoriasRata.find(function (cat) {
            return libertad >= cat.rango[0] && libertad <= cat.rango[1];
        });

        resultadoPercent.textContent = libertad + "%";
        if (categoria) {
            rataTitulo.textContent = categoria.nombre;
            rataDescripcion.textContent = categoria.desc;
        }

        resultado.classList.add("pv-visible");
        spawnParticles(resultado.querySelector(".pv-resultado-card"), 16);
    }

    actualizarDots();
});
