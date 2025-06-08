document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("rata-form");
    const barraContenedor = document.getElementById("barra-libertad");
    const barraProgreso = document.getElementById("barra-progreso");
    const resultadoOverlay = document.getElementById("resultado-overlay");
    const resultadoFinal = document.getElementById("resultado-final");
    const rataImg = document.getElementById("rata-img");
    const rataTitulo = document.getElementById("rata-titulo");
    const rataDescripcion = document.getElementById("rata-descripcion");
    const botonCalcular = document.querySelector("#rata-form button[type='submit']");

    const categoriasRata = [
        { rango: [0, 10], nombre: "Rata Obrera", img: "rata1.png", desc: "Trabajás mucho y ahorrás poco. Hay margen para mejorar." },
        { rango: [11, 20], nombre: "Rata Desorientada", img: "rata2.png", desc: "Hacés esfuerzo pero sin estrategia clara." },
        { rango: [21, 30], nombre: "Rata Optimista", img: "rata3.png", desc: "Estás empezando a salir del ciclo, no pares." },
        { rango: [31, 40], nombre: "Rata Planificadora", img: "rata4.png", desc: "Ya hay organización y resultados." },
        { rango: [41, 50], nombre: "Rata Emprendedora", img: "rata5.png", desc: "Estás construyendo tu libertad." },
        { rango: [51, 60], nombre: "Rata Estratégica", img: "rata6.png", desc: "Tomás decisiones con impacto positivo." },
        { rango: [61, 70], nombre: "Rata Inversionista", img: "rata7.png", desc: "Tu dinero empieza a trabajar por vos." },
        { rango: [71, 80], nombre: "Rata Autónoma", img: "rata8.png", desc: "Podrías vivir sin trabajar si sos disciplinado." },
        { rango: [81, 90], nombre: "Rata Libre", img: "rata9.png", desc: "Casi no dependés de tu trabajo." },
        { rango: [91, 100], nombre: "Rata Iluminada", img: "rata10.png", desc: "Sos financieramente libre. Enseñale a otros." }
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
            barraProgreso.style.transition = "width 2s ease-out";
            void barraProgreso.offsetWidth; // Forzar reflow
            barraProgreso.style.width = libertad + "%";
            barraProgreso.textContent = libertad + "%";

            // Esperar fin de la transición
            barraProgreso.addEventListener("transitionend", function handler() {
                barraProgreso.removeEventListener("transitionend", handler);
                console.log("✅ Animación finalizada. Mostrando resultado.");

                const categoria = categoriasRata.find(cat => libertad >= cat.rango[0] && libertad <= cat.rango[1]);
                if (categoria) {
                    rataImg.src = `/static/img/ratas/${categoria.img}`;
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
