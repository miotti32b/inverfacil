document.addEventListener("DOMContentLoaded", function () {
    let escenarioActual = 0;
    let puntajeTotal = 0;

    const sliders = document.querySelectorAll(".slider");
    const totalPercentageIndicator = document.getElementById("total-percentage");
    const confirmButton = document.getElementById("confirm-btn");
    const avatar = document.querySelector(".avatar img");
    const background = document.getElementById("background");
    const eventoMensaje = document.getElementById("evento-mensaje");
    const textBox = document.getElementById("text-box");

    // 📌 Escenarios con sus respectivos avatares y fondos
    const escenarios = [
        {
            nombre: "Edmundo",
            edad: 33,
            profesion: "MILLONARIO",
            ingresos: "$0 USD / MES",
            patrimonio: "$2.000.000",
            
            descripcion: "Recibi una herencia muy grande, pero no tengo ingresos mensuales, nunca trabaje ni estudie ¿Cómo distribuirías mi dinero?",
            avatarSrc: "/static/img/avatars/1.png",
            backgroundSrc: "/static/img/backgrounds/1.png",
            distribucionOptima: [4, 26, 7, 29, 4, 29]
        },
        {
            nombre: "Sofía",
            edad: 27,
            profesion: "Abogada",
            ingresos: "$2,500/mes",
            patrimonio: "$15,000",
            tiempo_libre: "Normal",
            descripcion: "Quiero comprar mi primera vivienda, pero también me preocupa mi futuro financiero ¿Qué debería priorizar?",
            avatarSrc: "/static/img/avatars/2.png",
            backgroundSrc: "/static/img/backgrounds/2.png",
            distribucionOptima: [0, 0, 20, 50, 10, 20]
        },
        {
            nombre: "Elon",
            edad: 50,
            profesion: "Empresario",
            ingresos: "6.000/mes",
            patrimonio: "$250.000",
            tiempo_libre: "Moderado",
            descripcion: "Siempre reinverti todo en mi empresa y trabaje muy duro, quiero cambiar de vida y tener un buen futuro, reinvierto en mi negocio o me capacito y diversifico?",
            avatarSrc: "/static/img/avatars/3.png",
            backgroundSrc: "/static/img/backgrounds/3.png",
            distribucionOptima: [5, 10, 10, 20, 5, 50]
        },
        {
            nombre: "Marcela",
            edad: 69,
            profesion: "Jubilada",
            ingresos: "$500/mes",
            patrimonio: "$20,000",
            tiempo_libre: "Muy poco",
            descripcion: "Como jubilada sobrevivo con lo minimo, que deberia hacer para poder mejorar mi futuro? vendo mi casa de 20.000? ",
            avatarSrc: "/static/img/avatars/4.png",
            backgroundSrc: "/static/img/backgrounds/4.png",
            distribucionOptima: [0, 0, 15, 30, 25, 30]
        },
        {
            nombre: "Julian",
            edad: 18,
            profesion: "Estudiante",
            ingresos: "$100/mes",
            patrimonio: "$10,000",
            tiempo_libre: "Mucho",
            descripcion: "Me regalaron 10.000 por mi cumpleaños y actualmente cree un negocio digital que me da dinero, me quiero comprar un auto y quiero ser millonario ¿Cómo lo logrías?",
            avatarSrc: "/static/img/avatars/5.png",
            backgroundSrc: "/static/img/backgrounds/5.png",
            distribucionOptima: [0, 0, 20, 35, 5, 40]
        }
    ];
    
    

    function typeText(message) {
        textBox.innerHTML = "";
        let i = 0;
        function escribir() {
            if (i < message.length) {
                textBox.innerHTML = message.substring(0, i + 1);
                i++;
                setTimeout(escribir, 30);
            }
        }
        escribir();
    }

    function mostrarTextoEscenario() {
        let esc = escenarios[escenarioActual];

        let mensaje = `
             Soy ${esc.nombre} tengo ${esc.edad} años. <br>Soy ${esc.profesion}.
             <br>            
                <span class="ingresos">Ingresos: ${esc.ingresos}</span><br>
                <span class="patrimonio">Patrimonio: ${esc.patrimonio}</span><br>            
             
            <br><strong>${esc.descripcion}</strong>
        `;

        textBox.style.display = "block";
        textBox.style.opacity = "1";
        typeText(mensaje);

        // 📌 🔥 Asegurar que el avatar y el fondo cambien correctamente
        if (avatar && esc.avatarSrc) {
            avatar.src = esc.avatarSrc;
            avatar.style.display = "block";
            avatar.style.opacity = "1";
        }

        if (background && esc.backgroundSrc) {
            background.src = esc.backgroundSrc;
            background.style.display = "block";
            background.style.opacity = "1";
        }
    }

    function ocultarElementos() {
        textBox.style.opacity = "0";
        avatar.style.opacity = "0"; // ✅ Ocultamos solo el avatar
        setTimeout(() => {
            textBox.style.display = "none";
            avatar.style.display = "none"; // ✅ Mantiene el fondo visible
        }, 300);
    }

    function updateSliders(changedSlider) {
        let total = Array.from(sliders).reduce((sum, s) => sum + Number(s.value), 0);
        if (total > 100) {
            let excess = total - 100;
            changedSlider.value -= excess;
            total = 100; 
        }
        sliders.forEach(slider => {
            let percentageDisplay = document.getElementById(slider.id + "-value");
            percentageDisplay.textContent = slider.value + "%";
        });
        totalPercentageIndicator.textContent = `Total: ${total}%`;
    }

    sliders.forEach(slider => {
        slider.addEventListener("input", function () {
            updateSliders(this);
        });
    });

    // 🎲 Definimos los eventos inesperados
const eventos = [
    {
        tipo: "positivo",
        descripcion: {
            0: "📚 ¡Beca sorpresa! Gastaste menos en educación.",
            1: "💼 ¡Tu negocio explotó en ventas! Beneficio extra.",
            2: "📈 ¡Suba inesperada en la bolsa! Rendimiento increíble.",
            3: "🚗 ¡Tu auto aumentó de valor inesperadamente!",
            4: "🏠 ¡Boom inmobiliario! Tu casa subió de precio.",
            5: "🎉 ¡Te volviste influencer! Ganas dinero con ocio."
        },
        efecto: (valor) => Math.min(valor + valor * (Math.random() * 0.5 + 0.1), 100) // Suma entre 10% y 50%
    },
    {
        tipo: "negativo",
        descripcion: {
            0: "📉 ¡Crisis en la universidad! Subieron las cuotas.",
            1: "📉 ¡Competencia feroz! Tu negocio sufrió pérdidas.",
            2: "📉 ¡Colapso del mercado! Pérdidas importantes.",
            3: "⛽ ¡Suba del combustible! Gastos inesperados.",
            4: "🏚️ ¡Crisis inmobiliaria! Tu propiedad bajó de valor.",
            5: "💸 ¡Fiesta costosa! Gastaste más de lo planeado."
        },
        efecto: (valor) => Math.max(valor - valor * (Math.random() * 0.5 + 0.1), 0) // Resta entre 10% y 50%
    }
];

// 📌 Para saber si ya se aplicó un evento en este escenario
let eventoAplicado = {};

// 📌 Función para elegir qué slider será afectado
function seleccionarSliderAfectado() {
    let ponderaciones = escenarios[escenarioActual].distribucionOptima;
    let maxPonderacion = Math.max(...ponderaciones);
    let minPonderacion = Math.min(...ponderaciones);

    let slidersArray = Array.from(sliders); // 🔥 Convertimos sliders en un array

    let slidersMax = slidersArray.filter((_, index) => ponderaciones[index] === maxPonderacion);
    let slidersMin = slidersArray.filter((_, index) => ponderaciones[index] === minPonderacion);

    let afectado = Math.random() < 0.5 ? slidersMax : slidersMin; // 🔥 50% de afectar el mayor o menor ponderado
    return afectado[Math.floor(Math.random() * afectado.length)];
}


// 📌 Aplicar evento al puntaje
function aplicarEvento(puntaje, sliderIndex) {
    if (!eventoAplicado[escenarioActual]) {
        let evento = Math.random() < 0.5 ? eventos[0] : eventos[1]; // 🔥 50% de evento positivo o negativo
        let puntajeModificado = evento.efecto(puntaje);
        let diferencia = Math.round(puntajeModificado - puntaje);

        // 📌 Mensaje del evento
        let mensajeEvento = `${evento.descripcion[sliderIndex]} (${evento.tipo === "positivo" ? "+" : ""}${diferencia} pts)`;
        eventoAplicado[escenarioActual] = true;

        return { nuevoPuntaje: puntajeModificado, mensajeEvento };
    }
    return { nuevoPuntaje: puntaje, mensajeEvento: "" };
}


// 📌 Calcular puntaje como porcentaje por escenario y luego promediar
function calcularPuntaje() {
    let puntajeTotal = 0;
    let maxPuntajeEscenario = sliders.length * 100; // 🔥 Puntaje máximo por escenario
    let mensajeBonus = "";
    let distribucionOptima = escenarios[escenarioActual].distribucionOptima;

    let sliderAfectado = seleccionarSliderAfectado(); // 🔥 Elegimos el slider clave

    sliders.forEach((slider, index) => {
        let asignado = Number(slider.value);
        let optimo = distribucionOptima[index];

        let diferencia = Math.abs(optimo - asignado);
        let puntajeSlider = Math.max(100 - (diferencia * 3), 0);

        // 🎲 Aplicamos evento solo en el slider elegido
        if (slider.id === sliderAfectado.id) {
            let { nuevoPuntaje, mensajeEvento } = aplicarEvento(puntajeSlider, index);
            puntajeSlider = nuevoPuntaje;
            mensajeBonus = mensajeEvento;
        }

        puntajeTotal += puntajeSlider;
    });

    // 🔥 Normalización: Puntaje por escenario entre 0 y 100
    let puntajeEscenario = Math.round((puntajeTotal / maxPuntajeEscenario) * 100);
    puntajeEscenario = Math.max(0, Math.min(puntajeEscenario, 100));

    // Guardamos puntaje del escenario en una lista global para promediar al final
    if (!sessionStorage.getItem("puntajes_escenarios")) {
        sessionStorage.setItem("puntajes_escenarios", JSON.stringify([]));
    }

    let puntajesAnteriores = JSON.parse(sessionStorage.getItem("puntajes_escenarios"));
    puntajesAnteriores.push(puntajeEscenario);
    sessionStorage.setItem("puntajes_escenarios", JSON.stringify(puntajesAnteriores));

    return { puntaje: puntajeEscenario, mensajeBonus };
}



// 📌 Función para reproducir sonido si existe
function reproducirSonido(idSonido) {
    let sonido = document.getElementById(idSonido);
    if (sonido) {
        console.log("🔊 Intentando reproducir:", idSonido);
        sonido.play()
            .then(() => console.log("✅ Sonido reproducido:", idSonido))
            .catch(error => console.error("🚨 Error al reproducir sonido:", idSonido, error));
    } else {
        console.error("🚨 ERROR: No se encontró el sonido:", idSonido);
    }
}

confirmButton.addEventListener("click", function () {
    console.log("🔵 Botón de Confirmar presionado");

    ocultarElementos();

    let { puntaje, mensajeBonus } = calcularPuntaje();
    console.log("🟢 Puntaje calculado:", puntaje, "Mensaje Bonus:", mensajeBonus);

    puntajeTotal += puntaje;

    // 📌 Si hubo un evento inesperado, reproducir sonido correspondiente
    if (mensajeBonus) {
        if (mensajeBonus.includes("+")) {
            reproducirSonido("sonido-bonus"); // 🔥 Evento positivo
        } else {
            reproducirSonido("sonido-penalty"); // 🔥 Evento negativo
        }
    }

    // 📌 Mostrar el cuadro de puntajes
    eventoMensaje.style.display = "flex"; 
    eventoMensaje.style.opacity = "1";

    let mensajeFinal = `<p class="puntaje-total">🎯 Puntaje en este escenario: <strong>${puntaje}</strong> pts</p>`;
    if (mensajeBonus) {
        let claseBonus = mensajeBonus.includes("+") ? "bonus" : "penalizacion";
        mensajeFinal += `<p class="${claseBonus}">💰 ${mensajeBonus}</p>`;
    }
    mensajeFinal += `<button id="avanzar-btn" class="avanzar-btn">Avanzar</button>`;
    eventoMensaje.innerHTML = mensajeFinal;

    let avanzarBtn = document.getElementById("avanzar-btn");
    if (!avanzarBtn) {
        console.error("🚨 ERROR: No se encontró el botón 'Avanzar'");
        return;
    }

    avanzarBtn.addEventListener("click", function () {
        console.log("🟠 Botón de Avanzar presionado");

        eventoMensaje.style.opacity = "0";
        setTimeout(() => {
            eventoMensaje.style.display = "none";
        }, 500);

        if (escenarioActual < escenarios.length - 1) {
            escenarioActual++;
            console.log("✅ Avanzando al escenario:", escenarioActual);

            setTimeout(() => {
                textBox.style.display = "block"; 
                avatar.style.display = "block"; 
                background.style.display = "block";
                mostrarTextoEscenario();
            }, 600);
        } else {
            console.log("🏁 Último escenario, guardando puntaje...");
            enviarPuntaje(puntajeTotal);
        }
    }, { once: true });
});



    function enviarPuntaje(puntaje) {
        const playerId = sessionStorage.getItem("player_id");
        if (!playerId) {
            alert("Error: No se encontró el ID del jugador.");
            return;
        }

        fetch("/juego/guardar_puntaje/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1]
            },
            body: JSON.stringify({ player_id: playerId, score: puntaje })
        }).then(response => response.json())
          .then(data => data.success ? window.location.href = "/juego/ranking/" : alert("Error al guardar puntaje."));
    }

    mostrarTextoEscenario();
});
