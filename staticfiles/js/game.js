document.addEventListener("DOMContentLoaded", function () {
    // Elementos del DOM
    const sliders = document.querySelectorAll(".slider");
    const percentages = document.querySelectorAll(".percentage");
    const totalPercentageIndicator = document.getElementById("total-percentage");
    const confirmButton = document.getElementById("confirm-btn");
    const avatar = document.getElementById("avatar");
    const background = document.getElementById("background");

    // Definición de escenarios con configuraciones óptimas
    let escenarios = [
        { fondo: "fondo1.png", avatar: "avatar1.png", optimo: { business: 40, investment: 30, property: 15, education: 10, vehicle: 5 } },
        { fondo: "fondo2.png", avatar: "avatar2.png", optimo: { business: 10, investment: 50, property: 20, education: 10, vehicle: 10 } },
        { fondo: "fondo3.png", avatar: "avatar3.png", optimo: { business: 25, investment: 25, property: 30, education: 10, vehicle: 10 } },
        { fondo: "fondo4.png", avatar: "avatar4.png", optimo: { business: 30, investment: 20, property: 35, education: 10, vehicle: 5 } },
        { fondo: "fondo5.png", avatar: "avatar5.png", optimo: { business: 35, investment: 30, property: 15, education: 10, vehicle: 10 } }
    ];
    
    

    let escenarioActual = 0;
    let puntajeTotal = 0;
    let tiempoRestante = 50; // 50 segundos por escenario

    // ⏳ Actualizar los sliders para no sobrepasar el 100%
    function updateSliders(changedSlider) {
        let total = Array.from(sliders).reduce((sum, s) => sum + Number(s.value), 0);

        if (total > 100) {
            let excess = total - 100;
            let adjustableSliders = Array.from(sliders).filter(s => s !== changedSlider && s.value > 0);

            if (adjustableSliders.length > 0) {
                let reductionPerSlider = excess / adjustableSliders.length;
                adjustableSliders.forEach(s => {
                    s.value = Math.max(0, s.value - reductionPerSlider);
                });
            }
        }

        sliders.forEach(slider => {
            let percentageDisplay = document.getElementById(slider.id + "-value");
            percentageDisplay.textContent = slider.value + "%";
        });

        let updatedTotal = Array.from(sliders).reduce((sum, s) => sum + Number(s.value), 0);
        totalPercentageIndicator.textContent = `Total: ${updatedTotal}%`;
    }

    sliders.forEach(slider => {
        slider.addEventListener("input", function () {
            updateSliders(this);
        });
    });

    // 🕒 Configurar la barra de tiempo
    function iniciarTemporizador() {
        let intervalo = setInterval(() => {
            tiempoRestante--;
            document.getElementById("timer-bar").style.width = (tiempoRestante / 50) * 100 + "%";

            if (tiempoRestante <= 10) {
                document.getElementById("timer-bar").style.backgroundColor = "red";
            } else if (tiempoRestante <= 30) {
                document.getElementById("timer-bar").style.backgroundColor = "yellow";
            }

            if (tiempoRestante <= 0) {
                clearInterval(intervalo);
                confirmarEscenario(); // Si se acaba el tiempo, confirma la elección actual
            }
        }, 1000);
    }

    iniciarTemporizador();

    // ✅ Confirmar la elección y cambiar de escenario
    confirmButton.addEventListener("click", function () {
        confirmarEscenario();
    });

    function confirmarEscenario() {
        let puntajeEscenario = calcularPuntaje();
        puntajeTotal += puntajeEscenario;

        if (escenarioActual < escenarios.length - 1) {
            escenarioActual++;
            background.src = `/static/img/backgrounds/${escenarios[escenarioActual].fondo}`;
            avatar.src = `/static/img/avatars/${escenarios[escenarioActual].avatar}`;
            tiempoRestante = 50; // Reiniciar tiempo para el nuevo escenario
        } else {
            enviarPuntaje(puntajeTotal);
        }
    }

    function calcularPuntaje() {
        let puntaje = 100;
        let escenario = escenarios[escenarioActual];
        console.log("📌 Revisando escenario actual:", escenario);
    
        sliders.forEach(slider => {
            let categoria = slider.id;
            let asignado = Number(slider.value);
            let optimo = escenario.optimo[categoria];
    
            if (isNaN(asignado) || isNaN(optimo)) {
                console.error(`🚨 Error en categoría "${categoria}": asignado=${asignado}, optimo=${optimo}`);
                return;
            }
    
            // 📌 Nueva lógica: si la diferencia es pequeña, la penalización también lo es.
            let diferencia = Math.abs(optimo - asignado);
            let penalizacion = 0;
    
            if (diferencia <= 5) {  // ⚖️ Si la diferencia es mínima, casi no hay penalización
                penalizacion = diferencia * 0.5;
            } else if (diferencia <= 15) {  // ⚠️ Si la diferencia es moderada, penalización media
                penalizacion = diferencia * 1;
            } else {  // ❌ Si la diferencia es alta, penalización más fuerte
                penalizacion = diferencia * 1.5;
            }
    
            puntaje -= penalizacion;
        });
    
        // 🟢 **Evento aleatorio** (ajustado para no ser tan injusto)
        if (Math.random() < 0.2) {  // 20% de probabilidad de evento
            let categorias = Object.keys(escenario.optimo);
            let categoriaAfectada = categorias[Math.floor(Math.random() * categorias.length)];
            let efecto = Math.random() < 0.5 ? "positivo" : "negativo";
            let ajuste = efecto === "positivo" ? 5 : -5;  // 🔥 Ajuste menor (+5 o -5)
    
            puntaje = Math.max(0, puntaje + ajuste);  // Evita que sea negativo
    
            alert(`¡Evento inesperado! Tu ${categoriaAfectada} tuvo un efecto ${efecto} en tus finanzas.`);
        }
    
        console.log("📌 Puntaje calculado (después de ajustes):", puntaje);
    
        return Math.max(puntaje, 0); // 🔥 Se asegura que no sea negativo
    }
    
    
    
    // 📩 Enviar el puntaje final al servidor
    function enviarPuntaje(puntaje) {
        const playerId = sessionStorage.getItem("player_id");  // Recuperamos el ID guardado
    
        if (!playerId) {
            alert("Error: No se encontró el ID del jugador.");
            console.error("📌 ERROR: player_id es NULL o no existe en sessionStorage.");
            return;
        }
    
        if (isNaN(puntaje) || puntaje === null) {
            alert("Error: Puntaje inválido.");
            console.error("📌 ERROR: El puntaje calculado es NaN o null.");
            return;
        }
    
        console.log("📌 Enviando puntaje con:", { player_id: playerId, score: puntaje });
    
        fetch("/juego/guardar_puntaje/", {  
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.cookie.split("; ")
                    .find(row => row.startsWith("csrftoken="))
                    ?.split("=")[1]
            },
            body: JSON.stringify({ 
                player_id: playerId, 
                score: puntaje 
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("📌 Respuesta del servidor:", data); // 🟢 Ver qué responde el servidor
            if (data.success) {
                window.location.href = "/juego/ranking/"; // ✅ Redirección correcta

            } else {
                alert("Error al guardar puntaje: " + data.error);
            }
        })
        .catch(error => console.error("Error al enviar puntaje:", error));
    }
    
    // 🔐 Obtener token CSRF para enviar datos a Django
    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }

    // 🏆 Obtener ID del jugador al iniciar
    let playerId = sessionStorage.getItem("player_id");

    if (!playerId) {
        fetch("/obtener_id_jugador/")
            .then(response => response.json())
            .then(data => {
                if (data.player_id) {
                    sessionStorage.setItem("player_id", data.player_id);
                    console.log("ID del jugador guardado:", data.player_id);
                } else {
                    console.error("Error: No se recibió un ID de jugador.");
                }
            })
            .catch(error => console.error("Error al obtener el ID del jugador:", error));
    } else {
        console.log("El jugador ya tiene ID:", playerId);
    }
});


function activarEventoInesperado() {
    console.log("🚀 Se activó un evento inesperado");  // 🔴 Verifica si esta línea aparece en la consola

    let categorias = Object.keys(escenarios[escenarioActual].optimo);
    let categoriaAfectada = categorias[Math.floor(Math.random() * categorias.length)];
    let efecto = Math.random() < 0.5 ? "positivo" : "negativo";
    let ajuste = efecto === "positivo" ? 10 : -10;

    puntajeTotal += ajuste;

    let eventoMensaje = document.getElementById("evento-mensaje");
    eventoMensaje.innerHTML = `¡Tu ${categoriaAfectada} tuvo un efecto ${efecto} en tus finanzas!`;
    eventoMensaje.classList.add("fade-in");

    setTimeout(() => {
        eventoMensaje.classList.remove("fade-in");
        eventoMensaje.innerHTML = "";
    }, 3000);
}
