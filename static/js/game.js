document.addEventListener("DOMContentLoaded", function () {
    const sliders = document.querySelectorAll(".slider");
    const percentages = document.querySelectorAll(".percentage");
    const totalPercentageIndicator = document.getElementById("total-percentage");
    const confirmButton = document.getElementById("confirm-btn");
    const avatar = document.getElementById("avatar");
    const background = document.getElementById("background");
    const eventoMensaje = document.getElementById("evento-mensaje");
    document.addEventListener("DOMContentLoaded", function () {
        const sliders = document.querySelectorAll(".slider");
    
        sliders.forEach(slider => {
            slider.value = 0; // 🔥 Establece todos los sliders en 0%
            let percentageDisplay = document.getElementById(slider.id + "-value");
            percentageDisplay.textContent = "0%"; // 🔥 También actualiza el texto de porcentaje
        });
    });
    
    let escenarios = [
        { fondo: "fondo1.png", avatar: "avatar1.png", optimo: { business: 40, investment: 30, property: 15, education: 10, vehicle: 5 } },
        { fondo: "fondo2.png", avatar: "avatar2.png", optimo: { business: 10, investment: 50, property: 20, education: 10, vehicle: 10 } },
        { fondo: "fondo3.png", avatar: "avatar3.png", optimo: { business: 25, investment: 25, property: 30, education: 10, vehicle: 10 } },
        { fondo: "fondo4.png", avatar: "avatar4.png", optimo: { business: 30, investment: 20, property: 35, education: 10, vehicle: 5 } },
        { fondo: "fondo5.png", avatar: "avatar5.png", optimo: { business: 35, investment: 30, property: 15, education: 10, vehicle: 10 } }
    ];

    let escenarioActual = 0;
    let puntajeTotal = 0;

    // 🔥 Elegimos 2 escenarios aleatorios para el evento inesperado (uno positivo y otro negativo)
    let escenariosEventos = [];
    while (escenariosEventos.length < 2) {
        let randomIndex = Math.floor(Math.random() * escenarios.length);
        if (!escenariosEventos.includes(randomIndex)) {
            escenariosEventos.push(randomIndex);
        }
    }

    let eventoPositivo = escenariosEventos[0];
    let eventoNegativo = escenariosEventos[1];

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

    confirmButton.addEventListener("click", function () {
        let puntajeEscenario = calcularPuntaje();
        puntajeTotal += puntajeEscenario;

        // 🔥 Verificar si en este escenario debe ocurrir un evento inesperado
        if (escenarioActual === eventoPositivo || escenarioActual === eventoNegativo) {
            let efecto = escenarioActual === eventoPositivo ? "positivo" : "negativo";
            let ajuste = efecto === "positivo" ? 10 : -10;
            puntajeTotal += ajuste;

            let mensajes = {
                "positivo": ["📈 ¡Tu inversión se duplicó!", "🎉 ¡El mercado creció y tu empresa se valorizó!", "💰 ¡Gran oportunidad! Tu dinero creció solo."],
                "negativo": ["📉 ¡Las acciones cayeron un 30%!", "💸 ¡Un mal negocio te hizo perder dinero!", "🚗 ¡El auto que compraste tuvo una falla y perdiste dinero!"]
            };

            let mensajeAleatorio = mensajes[efecto][Math.floor(Math.random() * mensajes[efecto].length)];

            setTimeout(() => {
                eventoMensaje.innerHTML = mensajeAleatorio;
                eventoMensaje.classList.add("fade-in");

                setTimeout(() => {
                    eventoMensaje.classList.remove("fade-in");
                    eventoMensaje.innerHTML = "";
                }, 3000);
            }, 300); // ⏳ Retraso de 1 segundo antes de mostrar el evento
        }

        if (escenarioActual < escenarios.length - 1) {
            escenarioActual++;
            background.src = `/static/img/backgrounds/${escenarios[escenarioActual].fondo}`;
            avatar.src = `/static/img/avatars/${escenarios[escenarioActual].avatar}`;
        } else {
            enviarPuntaje(puntajeTotal);
        }
    });

    function calcularPuntaje() {
        let puntaje = 100;
        let escenario = escenarios[escenarioActual];

        sliders.forEach(slider => {
            let categoria = slider.id;
            let asignado = Number(slider.value);
            let optimo = escenario.optimo[categoria];

            if (isNaN(asignado) || isNaN(optimo)) {
                return;
            }

            let diferencia = Math.abs(optimo - asignado);
            let penalizacion = diferencia * 2; // Penalización por cada punto fuera del óptimo
            puntaje -= penalizacion;
        });

        return Math.max(puntaje, 0); // Asegurar que el puntaje no sea negativo
    }

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
                "X-CSRFToken": document.cookie.split("; ")
                    .find(row => row.startsWith("csrftoken="))
                    ?.split("=")[1]
            },
            body: JSON.stringify({
                player_id: playerId,
                score: puntaje
            })
        }).then(response => response.json())
          .then(data => {
              if (data.success) {
                  window.location.href = "/juego/ranking/";
              } else {
                  alert("Error al guardar puntaje.");
              }
          });
    }
});

