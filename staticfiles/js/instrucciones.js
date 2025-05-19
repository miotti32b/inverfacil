let intervaloEscritura;
let intervaloAnimacionSlider;

document.addEventListener("DOMContentLoaded", function () {
    const sliders = document.querySelectorAll(".slider");
    const explicacion = document.getElementById("explicacion");
    const empezarBtn = document.getElementById("empezar-btn");
    empezarBtn.addEventListener("click", function () {
    // 🔓 Desbloquear sonidos en móviles al primer toque
    ["sonido-bonuss", "sonido-penalty", "sonido-puntaje"].forEach(id => {
        const sonido = document.getElementById(id);
        if (sonido) {
            sonido.play().then(() => {
                sonido.pause();
                sonido.currentTime = 0;
                console.log(`✅ Desbloqueado: ${id}`);
            }).catch(err => {
                console.warn(`❌ No se pudo desbloquear: ${id}`, err);
            });
        }
    });

    // 🔁 Acá iría la lógica para avanzar al juego si tenés
    // Por ejemplo: window.location.href = "/juego";
});

    const avatarElemento = document.getElementById("avatar");

    const textos = [
        "CAPACITACION: (CURSOS, CARRERAS, MAESTRIAS, ETC) invertir en aprender nuevas habilidades. La educacion es muy importante pero a veces tiene un costo de oportunidad mucho mayor a sus beneficios.",
        "NEGOCIO: (TU PROPIO NEGOCIO) destinar dinero a tu emprendimiento. Un emprendimiento te abre las puertas del mundo, pero enfocarse en exceso puede arruinarte.",
        "INVERSION: (ACTIVOS FINANCIEROS Y RELACIONADOS) invertir para el futuro. Invertir te da previsión y seguridad, pero arriesgar demasiado puede llevarte a la quiebra.",
        "VEHICULO: (PLAN DE AHORRO, AUTO, MOTO, ETC) comprar o mantener un auto. Un vehículo casi siempre es un pasivo que genera pérdida, pero en ocasiones puede ser beneficioso tenerlo.",
        "VIVIENDA: (PLAN DE AHORRO, COMPRA DEPTO O CASA, ETC) gastos relacionados a tu casa. Una vivienda casi siempre es un pasivo que genera pérdida, pero en ocasiones otorga beneficios.",
        "OCIO: (VIAJES, COMIDAS, SALIDAS SOCIALES) disfrutar del presente. El sacrificio y el esfuerzo son determinantes en tu vida, pero sin un poco de ocio nada tendría sentido."
    ];

    function escribirTexto(texto, callback, instant = false) {
        clearInterval(intervaloEscritura);
        explicacion.textContent = "";

        if (instant) {
            explicacion.textContent = texto;
            if (callback) callback();
            return;
        }

        let i = 0;
        intervaloEscritura = setInterval(() => {
            if (i < texto.length) {
                explicacion.textContent += texto.charAt(i);
                i++;
            } else {
                clearInterval(intervaloEscritura);
                if (callback) callback();
            }
        }, 50);
    }

    function resaltarSlider(index) {
        sliders.forEach(slider => slider.classList.remove("slider-activo"));
        sliders[index].classList.add("slider-activo");
    }

    sliders.forEach((slider, index) => {
        slider.addEventListener("pointerdown", function () {
            clearInterval(intervaloEscritura);
            clearInterval(intervaloAnimacionSlider);

            escribirTexto(textos[index], null, true);
            resaltarSlider(index);
        });
    });

    avatarElemento.addEventListener("click", function () {
        sliders.forEach(slider => {
            slider.classList.remove("slider-activo");
            slider.value = 0;
        });

        escribirTexto("Hola! Soy el Conde, Para ganar debes pasar 5 escenarios en los cuales deberás repartir el dinero disponible según la situación.", () => {
            setTimeout(() => {
                i = 0;
                animarSlider();
            }, 2000);
        });
    });

    sliders.forEach(slider => slider.value = 0);

    let i = 0;

    function animarSlider() {
        if (i >= sliders.length) {
            escribirTexto("¿Empezamos?");
            sliders.forEach(slider => slider.classList.remove("slider-activo"));
            clearInterval(intervaloEscritura);
            empezarBtn.style.display = "block";
            return;
        }

        escribirTexto(textos[i]);
        resaltarSlider(i);

        let valor = 0;
        intervaloAnimacionSlider = setInterval(() => {
            if (valor >= 100) {
                clearInterval(intervaloAnimacionSlider);
                setTimeout(() => {
                    sliders[i].value = 0;
                    i++;
                    animarSlider();
                }, 800);
            } else {
                valor += 1;
                sliders[i].value = valor;
            }
        }, 100);
    }

    escribirTexto("Hola! Soy el Conde, Para ganar debes pasar 5 escenarios en los cuales deberás repartir el dinero disponible según la situación.", () => {
        setTimeout(() => {
            animarSlider();
        }, 3500);
    });
});
