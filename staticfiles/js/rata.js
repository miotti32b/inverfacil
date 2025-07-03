document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("rata-form");
    const barraContenedor = document.getElementById("barra-libertad");
    const barraProgreso = document.getElementById("barra-progreso");
    const resultadoOverlay = document.getElementById("resultado-overlay");
    const resultadoFinal = document.getElementById("resultado-final");
    
    const rataTitulo = document.getElementById("rata-titulo");
    const rataDescripcion = document.getElementById("rata-descripcion");
    const botonCalcular = document.querySelector("#rata-form button[type='submit']");

   const categoriasRata = [
    {
        rango: [0, 10],
        nombre: "Rata Obrera",
        desc: "Vivís para trabajar, pero tu esfuerzo no se traduce en avance financiero. Tu día a día está marcado por la urgencia y el cansancio. Aún no comenzaste a construir libertad, pero estás a tiempo si cambiás el rumbo."
    },
    {
        rango: [11, 20],
        nombre: "Rata Desorientada",
        desc: "Tenés voluntad de progresar, pero no un plan claro. Probás cosas sueltas, sin una estrategia que te sostenga. Tu energía es valiosa, pero necesita dirección para convertirse en libertad real."
    },
    {
        rango: [21, 30],
        nombre: "Rata Optimista",
        desc: "Estás dando pasos hacia la salida del laberinto. Quizás ya te hiciste preguntas importantes o empezaste a ahorrar. Tus decisiones aún son limitadas, pero tu mentalidad va en ascenso."
    },
    {
        rango: [31, 40],
        nombre: "Rata Planificadora",
        desc: "Ya trazaste un camino: presupuestos, organización, metas. Aunque aún dependés del trabajo diario, tu estructura te permite resistir imprevistos y pensar en mediano plazo. Vas bien, seguí así."
    },
    {
        rango: [41, 50],
        nombre: "Rata Emprendedora",
        desc: "Estás construyendo algo propio. Tal vez no sea estable aún, pero ya no dependés 100% del sistema tradicional. Tu enfoque está en crecer, innovar y expandirte, aunque el riesgo todavía es parte del juego."
    },
    {
        rango: [51, 60],
        nombre: "Rata Estratégica",
        desc: "No trabajás más: decidís. Elegís qué hacer con tu tiempo y tu dinero. Conocés tus números, diversificás ingresos y sabés cuándo actuar. Tu mentalidad es de constructor de futuro, no de superviviente."
    },
    {
        rango: [61, 70],
        nombre: "Rata Inversionista",
        desc: "Tu dinero ya empezó a generar más dinero. Usás el interés compuesto, la diversificación y el análisis para consolidar tu libertad. Cada decisión financiera tuya tiene un objetivo claro detrás."
    },
    {
        rango: [71, 80],
        nombre: "Rata Autónoma",
        desc: "Podés dejar de trabajar hoy mismo si quisieras, aunque todavía elegís no hacerlo. Tu ingreso pasivo supera tus gastos, y vivís con orden, estrategia y visión a largo plazo. Tu libertad es real, pero aún vulnerable."
    },
    {
        rango: [81, 90],
        nombre: "Rata Libre",
        desc: "Tu situación financiera ya no depende de tu trabajo. Ingresos pasivos, baja carga laboral, control emocional sobre tus decisiones. Vivís desde la abundancia, pero con humildad y visión."
    },
    {
        rango: [91, 100],
        nombre: "Rata Iluminada",
        desc: "Lograste la libertad financiera plena. Vivís sin presiones económicas y dedicás tu energía a compartir, enseñar o expandir un propósito. Sos un referente: otros pueden aprender de vos."
    }
];


    resultadoOverlay.addEventListener("click", function (e) {
        if (e.target === resultadoOverlay) {
            resultadoOverlay.classList.remove("visible");
            form.classList.remove("blur");
        }
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const patrimonio = parseFloat(document.getElementById("id_patrimonio_neto").value);
        const ingreso = parseFloat(document.getElementById("id_ingreso_mensual").value);
        const gasto = parseFloat(document.getElementById("id_gasto_mensual").value);
        const fuentes = parseInt(document.getElementById("id_fuentes_ingreso").value);
        const horas = parseInt(document.getElementById("id_horas_trabajadas").value);

        if ([patrimonio, ingreso, gasto, fuentes, horas].some(val => isNaN(val))) {
            alert("Por favor, completá todos los campos correctamente.");
            return;
        }

        // Subcálculos normalizados
        const MRF = Math.min((patrimonio / gasto) / 60 * 100, 100);
        const TA_bruta = (ingreso - gasto) / ingreso;
        const TA = TA_bruta <= 0 ? 0 : Math.min(TA_bruta, 0.8) / 0.8 * 100;
        const DI = fuentes === 1 ? 0 : fuentes === 2 ? 50 : 100;
        const CH = Math.max(0, Math.min(100, (12 - horas) / 9 * 100));
        const libertad = Math.round((MRF * 0.35) + (TA * 0.35) + (DI * 0.15) + (CH * 0.15));

        console.log("🧠 Puntaje libertad financiera:", libertad);

        // Preparación visual
        botonCalcular.disabled = true;
        botonCalcular.textContent = "Calculando...";
        form.classList.add("blur");
        resultadoFinal.style.display = "none";
        barraContenedor.style.display = "none";
        barraProgreso.style.width = "0%";
        barraProgreso.textContent = "0%";
        resultadoOverlay.classList.add("visible");

        // Iniciar animación tras leve retardo
        setTimeout(() => {
            console.log("🚀 Iniciando animación de barra");
            barraContenedor.style.display = "block";
            document.getElementById("titulo-libertad").style.display = "block";

            barraProgreso.style.transition = "width 2s ease-out";
            void barraProgreso.offsetWidth; // Forzar reflow
            let porcentajeActual = 0;

            const velocidad = 20; // milisegundos entre cada incremento
            const incremento = Math.ceil(libertad / (2000 / velocidad)); // proporcional a la animación de 2s

barraProgreso.style.width = libertad + "%";

// animar número
const animarPorcentaje = setInterval(() => {
    porcentajeActual += incremento;
    if (porcentajeActual >= libertad) {
        porcentajeActual = libertad;
        clearInterval(animarPorcentaje);
    }
    barraProgreso.textContent = porcentajeActual + "%";
}, velocidad);

            // Esperar fin de la transición
            barraProgreso.addEventListener("transitionend", function handler() {
                barraProgreso.removeEventListener("transitionend", handler);
                console.log("✅ Animación finalizada. Mostrando resultado.");

                const categoria = categoriasRata.find(cat => libertad >= cat.rango[0] && libertad <= cat.rango[1]);
                if (categoria) {
                    
                    rataTitulo.textContent = categoria.nombre;
                    rataDescripcion.textContent = categoria.desc;
                    resultadoFinal.style.display = "flex";
                } else {
                    console.warn("❌ No se encontró categoría para el puntaje:", libertad);
                }

                botonCalcular.disabled = false;
                botonCalcular.textContent = "Calcular";
            });

        }, 400); // pequeña pausa para suavidad
    });
});
