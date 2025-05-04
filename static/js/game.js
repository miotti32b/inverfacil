document.addEventListener("DOMContentLoaded", function () {
    let escenarioActual = 0;
    let puntajeTotal = 0;

    // Elegimos 3 escenarios al azar donde ocurrirá un evento inesperado
if (!sessionStorage.getItem("escenarios_evento")) {
    let indices = Array.from({ length: 5 }, (_, i) => i); // [0,1,2,3,4]
    indices.sort(() => Math.random() - 0.5); // Desordenamos
    let seleccionados = indices.slice(0, 3); // Elegimos 3
    sessionStorage.setItem("escenarios_evento", JSON.stringify(seleccionados));
}

const escenariosConEvento = JSON.parse(sessionStorage.getItem("escenarios_evento"));


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
            nombre: "Juan",
            edad: 33,
            profesion: "Empleado",
            ingresos: "U$D 900 MES",
            patrimonio: "U$D 7.000",
            
            descripcion: "Quiero lograr la libertad financiera, pero siento que gano muy poco y no voy a llegar a cumplir mis metas ¿Que deberia hacer con mis ahorros para avanzar?",
            avatarSrc: "/static/img/avatars/1.png",
            backgroundSrc: "/static/img/backgrounds/1.png",
            distribucionOptima: [0, 0, 20, 35, 10, 35]
        },
        {
            nombre: "Sofía",
            edad: 27,
            profesion: "Abogada",
            ingresos: "U$D 1200 MES",
            patrimonio: "U$D 20.000",
            
            descripcion: "Quiero tener mi casa propia, pero también me preocupa mi futuro financiero por el avance de la IA en derecho. ¿Qué debería priorizar?",
            avatarSrc: "/static/img/avatars/2.png",
            backgroundSrc: "/static/img/backgrounds/2.png",
            distribucionOptima: [0, 0, 20, 40, 15, 25]
        },
        {
            nombre: "Oracio",
            edad: 50,
            profesion: "Empresario",
            ingresos: "U$D 9.000 MES",
            patrimonio: "U$D 3.000.000",
            tiempo_libre: "Moderado",
            descripcion: "Siempre reinverti todo en mi empresa y trabaje muy duro, quiero cambiar de vida y tener un buen futuro ¿vendo acciones de mi negocio, reinvierto o me capacito y diversifico?",
            avatarSrc: "/static/img/avatars/3.png",
            backgroundSrc: "/static/img/backgrounds/3.png",
            distribucionOptima: [5, 10, 10, 30, 10, 35]
        },
        {
            nombre: "Marcela",
            edad: 69,
            profesion: "Jubilada",
            ingresos: "U$D 500  MES",
            patrimonio: "U$D 20.000",
            tiempo_libre: "Muy poco",
            descripcion: "Como jubilada sobrevivo con lo minimo, que deberia hacer para poder vivir al maximo mis ultimos 15 anios? vendo mi casa de 20.000? ",
            avatarSrc: "/static/img/avatars/4.png",
            backgroundSrc: "/static/img/backgrounds/4.png",
            distribucionOptima: [0, 0, 15, 30, 25, 30]
        },
        {
            nombre: "Julian",
            edad: 18,
            profesion: "Estudiante",
            ingresos: "U$D 100 MES",
            patrimonio: "U$D 5.000",
            tiempo_libre: "Mucho",
            descripcion: "Me regalaron 5.000 por mi cumpleaños y actualmente cree un negocio digital que me da dinero, me quiero comprar un auto y quiero ser millonario ¿Cómo lo logrías?",
            avatarSrc: "/static/img/avatars/5.png",
            backgroundSrc: "/static/img/backgrounds/5.png",
            distribucionOptima: [0, 0, 20, 35, 5, 40]
        }
    ];
    
    // Variable global
    let escribiendo = false;
    let timeoutEscribir;  // Guarda la referencia al timeout


    function typeText(message) {
        clearTimeout(timeoutEscribir); // Cancela animación anterior si existía
    
        textBox.innerHTML = "";
        escribiendo = true;
    
        let i = 0;
    
        function escribir() {
            if (i < message.length) {
                textBox.innerHTML = message.substring(0, i + 1);
                i++;
                timeoutEscribir = setTimeout(escribir, 30);
            } else {
                escribiendo = false; // Finalizó animación
            }
        }
    
        escribir();
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

    const eventos = [
        {
            tipo: "positivo",
            descripcion: {
                0: "🚗 ¡Tu auto te ayudó a cerrar un negocio!",
                1: "🏠 ¡Se revalorizó tu propiedad!",
                2: "📚 Contactos universitarios te ayudaron a formar una sociedad.",
                3: "📈 ¡Gran suba en tus activos financieros!",
                4: "🎉 ¡Gracias a tu pasatiempo te volviste influencer!",
                5: "💼 ¡Tu negocio explotó en ventas!"
            },
            efecto: (puntajeTotal) => {
                let bonus = Math.round(Math.random() * 40 + 10);
                return { nuevoPuntaje: puntajeTotal + bonus, impacto: bonus };
            }
        },
        {
            tipo: "negativo",
            descripcion: {
                0: "⛽ Falla mecánica dejó a tu vehículo muy devaluado.",
                1: "🏚️ Estafa inmobiliaria.",
                2: "📉 El costo de oportunidad de estudiar fue muy alto.",
                3: "📉 ¡Colapso del mercado!",
                4: "💸 Gastaste demasiado por un bloqueo emocional.",
                5: "📉 El negocio en el que invertiste no resultó como esperabas."
            },
            efecto: (puntajeTotal) => {
                let penalizacion = Math.round(Math.random() * 40 + 10);
                return { nuevoPuntaje: Math.max(puntajeTotal - penalizacion, 0), impacto: -penalizacion };
            }
        }
    ];
    
    let eventoAplicado = {};
    

// game.js Lógica Reformulada Definitiva - Limpia y Óptima

// Inicialización del array de puntajes al cargar el juego
if (!sessionStorage.getItem("puntajes_escenarios")) {
    sessionStorage.setItem("puntajes_escenarios", JSON.stringify([]));
}



function seleccionarSliderAfectado() {
    let slidersArray = Array.from(sliders);
    let slidersModificados = slidersArray.filter(s => Number(s.value) > 0);

    if (slidersModificados.length === 0) {
        return slidersArray[Math.floor(Math.random() * slidersArray.length)];
    }

    return slidersModificados.reduce((maxSlider, currentSlider) => {
        return Number(currentSlider.value) > Number(maxSlider.value) ? currentSlider : maxSlider;
    });
}

function calcularPuntaje() {
    let distribucionOptima = escenarios[escenarioActual].distribucionOptima;
    let mensajeBonus = "";
    let puntajeTotal = 0;

    let sliderAfectado = seleccionarSliderAfectado();

    sliders.forEach((slider, index) => {
        let asignado = Number(slider.value);
        let optimo = distribucionOptima[index];
        let diferencia = Math.abs(optimo - asignado);

        let maxPorSlider = 85 / sliders.length; // ~16.66
        let penalizacion = Math.pow(diferencia / 100, 2) * maxPorSlider * 2;

        let puntajeSlider = Math.max(maxPorSlider - penalizacion, 0);

        puntajeTotal += puntajeSlider;
    });

    // Evento inesperado
    if (!eventoAplicado[escenarioActual] && sliderAfectado && escenariosConEvento.includes(escenarioActual)) {
        let indexAfectado = Array.from(sliders).indexOf(sliderAfectado);
        let asignadoAfectado = Number(sliderAfectado.value);
        let optimoAfectado = distribucionOptima[indexAfectado];
        let diferenciaAfectado = Math.abs(optimoAfectado - asignadoAfectado);
        let probPositivo;
            if (diferenciaAfectado <= 5) {
                probPositivo = 0.95;
            } else if (diferenciaAfectado <= 15) {
                probPositivo = 0.5;
            } else {
                probPositivo = 0.05;
            }

        let evento = Math.random() < probPositivo ? eventos[0] : eventos[1];
        let resultadoEvento = evento.efecto(puntajeTotal);

        mensajeBonus = `${evento.descripcion[indexAfectado]} (${evento.tipo === "positivo" ? "+" : ""}${resultadoEvento.impacto.toFixed(1)} pts)`;
        puntajeTotal = resultadoEvento.nuevoPuntaje;
        eventoAplicado[escenarioActual] = true;
    }

    // Penalización por no diversificar
    let slidersUsados = Array.from(sliders).filter(s => Number(s.value) > 0);
    if (slidersUsados.length === 1) {
        puntajeTotal *= 0.7; // Penalización si solo usó un slider
    }

    puntajeTotal = Math.min(puntajeTotal, 100); // límite

    let puntajesAnteriores = JSON.parse(sessionStorage.getItem("puntajes_escenarios"));
    puntajesAnteriores.push(Math.round(puntajeTotal));
    sessionStorage.setItem("puntajes_escenarios", JSON.stringify(puntajesAnteriores));

    return { puntaje: Math.round(puntajeTotal), mensajeBonus };
}


// Guardar los porcentajes del escenario actual para generar el perfil
let resultado = {
    vehicle: Number(document.getElementById("vehicle").value),
    property: Number(document.getElementById("property").value),
    education: Number(document.getElementById("education").value),
    investment: Number(document.getElementById("investment").value),
    leisure: Number(document.getElementById("leisure").value),
    business: Number(document.getElementById("business").value)
};

let resultadosPrevios = JSON.parse(sessionStorage.getItem("player_results")) || [];
resultadosPrevios.push(resultado);
sessionStorage.setItem("player_results", JSON.stringify(resultadosPrevios));


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
    // 🔥 Siempre ocultar cartel de evento cuando se entra a un escenario
    eventoMensaje.style.display = "none";
    eventoMensaje.style.opacity = "0";
}

function ocultarElementos() {
    textBox.style.opacity = "0";
    avatar.style.opacity = "0"; // ✅ Ocultamos solo el avatar
    setTimeout(() => {
        textBox.style.display = "none";
        avatar.style.display = "none"; // ✅ Mantiene el fondo visible
    }, 300);
}


confirmButton.addEventListener("click", function () {
    console.log("🔵 Botón de Confirmar presionado");

    ocultarElementos();

    let { puntaje, mensajeBonus } = calcularPuntaje();

    let resultado = {
        vehicle: Number(document.getElementById("vehicle").value),
        property: Number(document.getElementById("property").value),
        education: Number(document.getElementById("education").value),
        investment: Number(document.getElementById("investment").value),
        leisure: Number(document.getElementById("leisure").value),
        business: Number(document.getElementById("business").value)
    };
    console.log("🎛️ Sliders actuales:", resultado);
    let resultadosPrevios = JSON.parse(sessionStorage.getItem("player_results")) || [];
    resultadosPrevios.push(resultado);
    sessionStorage.setItem("player_results", JSON.stringify(resultadosPrevios));
    
    console.log("🟢 Puntaje calculado:", puntaje, "Mensaje Bonus:", mensajeBonus);

    puntajeTotal += puntaje;

    // 📌 Si hubo un evento inesperado, reproducir sonido correspondiente
    if (mensajeBonus) {
        if (mensajeBonus.includes("+")) {
            reproducirSonido("sonido-bonuss"); // 🔥 Evento positivo
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
        eventoAplicado = {};  // Reseteamos solo al pasar de escenario
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


function enviarPuntaje() {
    const playerId = sessionStorage.getItem("player_id");
    if (!playerId) {
        alert("Error: No se encontró el ID del jugador.");
        return;
    }

    let puntajesAnteriores = JSON.parse(sessionStorage.getItem("puntajes_escenarios")) || [];
    let puntajeFinal = Math.round(
        puntajesAnteriores.reduce((acc, val) => acc + val, 0) / puntajesAnteriores.length
    );

    // 🔥 Acá guardás el puntaje final para que luego se use en la carta
    sessionStorage.setItem("puntaje_final", puntajeFinal);

    fetch("/juego/guardar_puntaje/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1]
        },
        body: JSON.stringify({ player_id: playerId, score: puntajeFinal })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = "/juego/ranking/";
        } else {
            alert("Error al guardar puntaje.");
        }
    });
}





    mostrarTextoEscenario();
});
