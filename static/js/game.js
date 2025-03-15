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
    const textBoxContainer = document.getElementById("text-box-container");

    const mensajesEscenarios = [
        "¡Hola, soy Lucas! Tengo 20 años y estudio Psicología. Trabajo como Rappi y gano 1M al mes. ¿Cómo diversifico mis ahorros de 1000 USD?",
        "Hola, me llamo Sofía, tengo 32 años, soy abogada y quiero comprar mi primera vivienda. ¿Qué debería priorizar?",
        "Soy Tomás, tengo 40 años, trabajo en tecnología y quiero invertir en la bolsa. ¿Cómo empiezo?",
        "Soy Carolina, 25 años, freelancer y quiero hacer crecer mi fondo de emergencia. ¿Cómo administro mejor mi dinero?",
        "Soy Javier, empresario de 50 años. Estoy pensando en jubilarme. ¿Cómo administro mi patrimonio?"
    ];

    let typingTimeout;
    
    function typeText(message) {
        clearTimeout(typingTimeout);
        textBox.innerHTML = "";
        let i = 0;
        function escribir() {
            if (i < message.length) {
                textBox.innerHTML = message.substring(0, i + 1);
                i++;
                typingTimeout = setTimeout(escribir, 50);
            }
        }
        escribir();
    }

    function mostrarTextoEscenario() {
        let sceneContainer = document.querySelector(".scene-container");
        let avatar = document.querySelector(".avatar img");
        let textBox = document.getElementById("text-box");
    
        if (sceneContainer) {
            sceneContainer.style.visibility = "visible"; // Lo hacemos visible de nuevo
            sceneContainer.style.opacity = "1";
        }
    
        if (avatar) {
            avatar.style.display = "block"; // Asegura que el avatar se muestre
        }
    
        if (textBox) {
            typeText(mensajesEscenarios[escenarioActual]); // Muestra el nuevo texto
        }
    }
    

    function ocultarElementos() {
        let boxContainer = document.getElementById("text-box-container");
        let sceneContainer = document.querySelector(".scene-container");
    
        if (boxContainer) {
            boxContainer.style.display = "none";
            boxContainer.style.visibility = "hidden";
            boxContainer.style.opacity = "0";
            boxContainer.style.position = "absolute";
            boxContainer.style.top = "-9999px";
            boxContainer.style.width = "0";
            boxContainer.style.height = "0";
        }
    
        if (sceneContainer) {
            sceneContainer.style.visibility = "hidden"; // En vez de display: none
            sceneContainer.style.opacity = "0"; 
            sceneContainer.style.transition = "opacity 0.5s ease-in-out"; 
        }
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

// 🎲 Definimos los eventos positivo y negativo
const eventos = [
    {
        tipo: "positivo",
        descripcion: {
            vehicle: "🚗 ¡El auto que compraste se revalorizó! Ganancia extra.",
            property: "🏠 ¡Boom inmobiliario! Tu propiedad subió de valor.",
            education: "📚 ¡Beca sorpresa! Gastaste menos en educación.",
            investment: "📈 ¡Suba inesperada en la bolsa! Rendimiento increíble.",
            leisure: "🎉 ¡Te volviste influencer! Ganas dinero con ocio.",
            business: "💼 ¡Tu negocio explotó en ventas! Beneficio extra."
        },
        efecto: (valor) => valor * (Math.floor(Math.random() * 9) + 2) // Multiplica entre x2 y x10
    },
    {
        tipo: "negativo",
        descripcion: {
            vehicle: "⛽ ¡Suba del combustible! Gastos inesperados.",
            property: "🏚️ ¡Crisis inmobiliaria! Tu propiedad bajó de valor.",
            education: "📉 ¡Crisis en la universidad! Subieron las cuotas.",
            investment: "📉 ¡Colapso del mercado! Pérdidas importantes.",
            leisure: "💸 ¡Fiesta costosa! Gastaste más de lo planeado.",
            business: "📉 ¡Competencia feroz! Tu negocio sufrió pérdidas."
        },
        efecto: (valor) => valor * (Math.random() * -0.5 - 0.5) // Reduce entre -50% y -100%
    }
];

// 📌 Elegimos dos escenarios distintos para cada evento
let escenariosConEventos = new Set();
while (escenariosConEventos.size < 2) {
    let escenarioAleatorio = Math.floor(Math.random() * mensajesEscenarios.length);
    escenariosConEventos.add(escenarioAleatorio);
}
let [escenarioEventoPositivo, escenarioEventoNegativo] = [...escenariosConEventos]; // Asignamos eventos a escenarios

// 📌 Para saber qué evento se aplicó en qué escenario
let eventoAplicado = {}; 

// 📌 Función para calcular el puntaje aplicando los eventos aleatorios correctamente
function calcularPuntaje() {
    let puntaje = 100;
    let bonus = 0;
    let mensajeBonus = "";

    sliders.forEach(slider => {
        let asignado = Number(slider.value);
        let optimo = 50;
        let diferencia = Math.abs(optimo - asignado);
        let puntajeSlider = Math.max(100 - diferencia * 2, 0); // Cálculo base

        // 📌 Si este escenario tiene un evento, aplicarlo a un solo slider
        if ((escenarioActual === escenarioEventoPositivo || escenarioActual === escenarioEventoNegativo) 
            && !eventoAplicado[escenarioActual]) {

            let evento = escenarioActual === escenarioEventoPositivo ? eventos[0] : eventos[1]; // Asigna positivo o negativo
            let sliderAfectado = sliders[Math.floor(Math.random() * sliders.length)]; // Seleccionamos un slider al azar

            if (slider.id === sliderAfectado.id) {
                let puntajeModificado = evento.efecto(puntajeSlider); // Aplicamos el efecto
                let diferenciaPuntaje = puntajeModificado - puntajeSlider;

                // Guardamos el mensaje del evento
                mensajeBonus = `${evento.descripcion[slider.id]} (${evento.tipo === "positivo" ? "+" : ""}${Math.round(diferenciaPuntaje)} pts)`;
                bonus += Math.round(diferenciaPuntaje); // Sumamos o restamos al puntaje total
                eventoAplicado[escenarioActual] = true; // Marcamos este evento como usado
            }
        }

        puntaje += puntajeSlider;
    });

    return { puntaje: Math.max(puntaje + bonus, 0), mensajeBonus };
}

// 🔎 Detectamos si el usuario está en un móvil
let esMovil = /Android|iPhone|iPad/i.test(navigator.userAgent);

// 📌 Función para activar sonido o vibración según el dispositivo
function activarEfectoSonidoOSensacion(idSonido, duracionVibracion) {
    if (esMovil && navigator.vibrate) {
        navigator.vibrate(duracionVibracion); // Vibra en móviles
    } else {
        let sonido = document.getElementById(idSonido);
        if (sonido) {
            sonido.play().catch(error => console.log("🔇 Audio bloqueado en móvil:", error));
        }
    }
}

// 🎯 Evento al confirmar el escenario (mostramos puntaje con efecto)
confirmButton.addEventListener("click", function () {
    ocultarElementos();
    
    let { puntaje, mensajeBonus } = calcularPuntaje();
    puntajeTotal += puntaje;

    let eventoMensaje = document.getElementById("evento-mensaje");
    let mensajeFinal = `<p class="puntaje-total">🎯 Puntaje en este escenario: <strong id="puntaje-animado">0</strong> pts</p>`;

    if (mensajeBonus) {
        let claseBonus = mensajeBonus.includes("+") ? "bonus" : "penalizacion";
        let duracionVibracion = mensajeBonus.includes("+") ? 300 : 600; // 🎶 Bonus vibra menos, penalización más
        let sonidoEvento = mensajeBonus.includes("+") ? "sonido-bonus" : "sonido-penalizacion";
        
        mensajeFinal += `<p class="${claseBonus}">💰 ${mensajeBonus}</p>`;

        // 🔊 Reproduce sonido o vibración según el dispositivo
        activarEfectoSonidoOSensacion(sonidoEvento, duracionVibracion);
    }

    mensajeFinal += `<button id="avanzar-btn" class="avanzar-btn">Avanzar</button>`;
    eventoMensaje.innerHTML = mensajeFinal;
    eventoMensaje.style.display = "block";
    
    // 🎵 Activamos efecto al mostrar la tabla de puntaje
    activarEfectoSonidoOSensacion("sonido-entrada", 200);

    // 📊 Animación de aparición de la tabla
    setTimeout(() => {
        eventoMensaje.classList.add("mostrar");
    }, 50);

    // 🔢 Animación del conteo del puntaje
    let puntajeElement = document.getElementById("puntaje-animado");
    let tiempoConteo = 3000; // 3 segundos
    let incremento = puntaje / (tiempoConteo / 50);
    let contador = 0;
    
    let intervalo = setInterval(() => {
        contador += incremento;
        if (contador >= puntaje) {
            contador = puntaje;
            clearInterval(intervalo);
        }
        puntajeElement.innerText = Math.floor(contador);
    }, 50);

    // 🎵 Sonido o vibración mientras sube el puntaje
    activarEfectoSonidoOSensacion("sonido-contador", 100);

    // 🎮 Evento para avanzar al siguiente escenario
    document.getElementById("avanzar-btn").addEventListener("click", function () {
        eventoMensaje.classList.remove("mostrar");
        setTimeout(() => {
            eventoMensaje.style.display = "none";
        }, 500);

        if (escenarioActual < mensajesEscenarios.length - 1) {
            escenarioActual++;
            if (background && avatar) {
                background.src = `/static/img/backgrounds/fondo${escenarioActual + 1}.png`;
                avatar.src = `/static/img/avatars/avatar${escenarioActual + 1}.png`;
            }
            setTimeout(mostrarTextoEscenario, 500);
        } else {
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

    setTimeout(mostrarTextoEscenario, 500);
});





