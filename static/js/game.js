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
            nombre: "Maximo",
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
            ingresos: "$2.500 USD / MES",
            patrimonio: "$15.000",
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
            ingresos: "6.000 USD / MES",
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
            ingresos: "$500 USD / MES",
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
            ingresos: "$100 USD / MES",
            patrimonio: "$50,000",
            tiempo_libre: "Mucho",
            descripcion: "Me regalaron 5.000 por mi cumpleaños y actualmente cree un negocio digital que me da dinero, me quiero comprar un auto y quiero ser millonario ¿Cómo lo logrías?",
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
                0: "🚗 ¡Tu auto te ayudo para realizar un negocio!",
                1: "🏠 ¡Se revalorizo tu propiedad!",
                2: "📚 Contactos universitarios te ayudaron a formar una sociedad.",
                3: "📈 ¡Gran suba en tus activos financieros!",
                4: "🎉 ¡Gracias a tu pasatiempo te volviste influencer!",
                5: "💼 ¡Tu negocio explotó en ventas!"
            },
            efecto: (valor) => Math.min(valor + valor * (Math.random() * 0.5 + 0.1), 100)
        },
        {
            tipo: "negativo",
            descripcion: {
                0: "⛽ Falla mecánica deja a tu vehiculo al 30% de su valor.",
                1: "🏚️ Estafa inmobiliaria.",
                2: "📉 El costo de oportunidad de estudiar fue muy alto.",
                3: "📉 ¡Colapso del mercado!",
                4: "💸 Despilfarraste plata por un bloqueo emocional.",
                5: "📉 El negocio en el que invertiste no resulto como esperabas."
            },
            efecto: (valor) => Math.max(valor - valor * (Math.random() * 0.5 + 0.1), 0)
        }
    ];
    
    let eventoAplicado = {};
    
// game.js Lógica Reformulada Definitiva - Versión Rigurosa
// game.js Lógica Reformulada Definitiva - Limpia y Óptima

// Inicialización del array de puntajes al cargar el juego
if (!sessionStorage.getItem("puntajes_escenarios")) {
    sessionStorage.setItem("puntajes_escenarios", JSON.stringify([]));
}

// Selección del Slider con Mayor Valor Asignado por el Jugador
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
    let puntajeTotal = 0;
    let distribucionOptima = escenarios[escenarioActual].distribucionOptima;
    let mensajeBonus = "";

    let sliderAfectado = seleccionarSliderAfectado();

    sliders.forEach((slider, index) => {
        let asignado = Number(slider.value);
        let optimo = distribucionOptima[index];
        let diferencia = Math.abs(optimo - asignado);

        let penalizacion = diferencia * 7; // Más riguroso
        let puntajeSlider = Math.max(100 - penalizacion, 0);

        puntajeTotal += puntajeSlider;
    });

    if (!eventoAplicado[escenarioActual] && sliderAfectado) {
        let indexAfectado = Array.from(sliders).indexOf(sliderAfectado);
        let asignadoAfectado = Number(sliderAfectado.value);
        let optimoAfectado = distribucionOptima[indexAfectado];
        let diferenciaAfectado = Math.abs(optimoAfectado - asignadoAfectado);

        let probPositivo = diferenciaAfectado <= 5 ? 0.9 : diferenciaAfectado >= 20 ? 0.1 : 0.5;

        let evento = Math.random() < probPositivo ? eventos[0] : eventos[1];
        let puntajeOriginal = Math.max(100 - (diferenciaAfectado * 7), 0);
        let puntajeModificado = evento.efecto(puntajeOriginal);
        let diferenciaEvento = Math.round(puntajeModificado - puntajeOriginal);

        mensajeBonus = `${evento.descripcion[indexAfectado]} (${evento.tipo === "positivo" ? "+" : ""}${diferenciaEvento} pts)`;

        puntajeTotal += (puntajeModificado - puntajeOriginal);
        eventoAplicado[escenarioActual] = true;
    }

    let slidersUsados = Array.from(sliders).filter(s => Number(s.value) > 0);
    if (slidersUsados.length === 1) {
        puntajeTotal *= 0.3; // Penalización más dura
    }

    let puntajeEscenario = Math.min(puntajeTotal, 200);

    let puntajesAnteriores = JSON.parse(sessionStorage.getItem("puntajes_escenarios"));
    puntajesAnteriores.push(puntajeEscenario);
    sessionStorage.setItem("puntajes_escenarios", JSON.stringify(puntajesAnteriores));

    return { puntaje: Math.round(puntajeEscenario), mensajeBonus };
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



function enviarPuntaje() {
    const playerId = sessionStorage.getItem("player_id");
    if (!playerId) {
        alert("Error: No se encontró el ID del jugador.");
        return;
    }

    // Sumamos los puntajes guardados de los 5 escenarios
    let puntajesAnteriores = JSON.parse(sessionStorage.getItem("puntajes_escenarios")) || [];
    let puntajeFinal = puntajesAnteriores.reduce((acc, val) => acc + val, 0);

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
