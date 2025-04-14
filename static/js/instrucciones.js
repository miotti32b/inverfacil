let intervaloEscritura;  // Guardamos la referencia global


document.addEventListener("DOMContentLoaded", function () {
    const sliders = document.querySelectorAll(".slider");
    const explicacion = document.getElementById("explicacion");
    const empezarBtn = document.getElementById("empezar-btn");

    const textos = [
        "Capacitación: invertir en aprender nuevas habilidades. La educacion es muy importante pero a veces tiene un costo de oportunidad mucho mayor a sus beneficios.",
        "Negocio: destinar dinero a tu emprendimiento. Un emprendimiento te abre las puertas del mundo, pero enfocarse en exceso puede arruinarte.",
        "Inversión: invertir para el futuro. Invertir te da prevision y seguridad, pero arriesgar demasiado puede llevarte a la quiebra.",
        "Vehículo: comprar o mantener un auto. Un vehiculo casi siempre es un pasivo que genera perdida, pero en ocaciones puede ser beneficioso tenerlo.",
        "Vivienda: gastos relacionados a tu casa. Una vivienda casi siempre es un pasivo que genera perdida, pero en ocaciones otorga beneficios.",
        "Ocio: disfrutar del presente. El sacrificio y el esfuerzo son determinantes en tu vida, pero sin un poco de ocio nada tendria sentido."
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
            escribirTexto(textos[index], null, true); // 👈 Mostrar texto al instante
            resaltarSlider(index);
        });
    });
    // Evento cuando hace CLICK en el avatar (efecto máquina de escribir otra vez)
    const avatarElemento = document.getElementById("avatar"); // Asegurate de tener este ID en el HTML

    avatarElemento.addEventListener("click", function () {
        // Detectamos qué slider está activo
        let sliderActivo = Array.from(sliders).findIndex(s => s.classList.contains("slider-activo"));

        if (sliderActivo >= 0) {
            escribirTexto(textos[sliderActivo]); // Con efecto de máquina de escribir
        }
    });    

    sliders.forEach(slider => slider.value = 0);

    let i = 0;

    function animarSlider() {
        if (i >= sliders.length) {
            escribirTexto("Empezamos?");
            sliders.forEach(slider => slider.classList.remove("slider-activo"));
            setTimeout(() => {
                empezarBtn.style.display = "block";
            }, 1500);
            return;
        }

        escribirTexto(textos[i]);
        resaltarSlider(i);

        let valor = 0;
        const intervalo = setInterval(() => {
            if (valor >= 100) {
                clearInterval(intervalo);
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

    // Empieza mostrando un mensaje breve y luego comienza la explicación
    escribirTexto("Para obtener un puntaje alto debes repartir bien el dinero disponible", () => {
        setTimeout(() => {
            animarSlider();
        }, 2500);
    });
});
