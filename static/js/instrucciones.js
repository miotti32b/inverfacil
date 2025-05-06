let intervaloEscritura;  // Guardamos la referencia global


document.addEventListener("DOMContentLoaded", function () {
    const sliders = document.querySelectorAll(".slider");
    const explicacion = document.getElementById("explicacion");
    const empezarBtn = document.getElementById("empezar-btn");
    const avatarElemento = document.getElementById("avatar"); // 👈 Esta es la línea que falta


    const textos = [
        "CAPACITACION: (CURSOS, CARRERAS, MAESTRIAS, ETC) invertir en aprender nuevas habilidades. La educacion es muy importante pero a veces tiene un costo de oportunidad mucho mayor a sus beneficios.",
        "NEGOCIO: (TU PROPIO NEGOCIO)destinar dinero a tu emprendimiento. Un emprendimiento te abre las puertas del mundo, pero enfocarse en exceso puede arruinarte.",
        "INVERSION: (ACTIVOS FINANCIEROS Y RELACIONADSO) invertir para el futuro. Invertir te da prevision y seguridad, pero arriesgar demasiado puede llevarte a la quiebra.",
        "VEHICULO: (PLAN DE AHORRO, AUTO, MOTO, ETC) comprar o mantener un auto. Un vehiculo casi siempre es un pasivo que genera perdida, pero en ocaciones puede ser beneficioso tenerlo.",
        "VIVIENDA: (PLAN DE AHORRO, COMPRA DEPTO O CASA, ETC) gastos relacionados a tu casa. Una vivienda casi siempre es un pasivo que genera perdida, pero en ocaciones otorga beneficios.",
        "OCIO: (VIAJES, COMIDAS, SALIDAS SOCIALES) disfrutar del presente. El sacrificio y el esfuerzo son determinantes en tu vida, pero sin un poco de ocio nada tendria sentido."
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
    avatarElemento.addEventListener("click", function () {
        // 🧹 Reinicia todos los sliders visualmente
        sliders.forEach(slider => {
            slider.classList.remove("slider-activo");
            slider.value = 0;
        });
    
        // 🎬 Oculta el botón de empezar si ya se había mostrado
        empezarBtn.style.display = "none";
    
        // 🧙‍♂️ Muestra nuevamente la intro y comienza la animación
        escribirTexto("Hola! Soy el Conde, Para ganar debes pasar 5 escenarios en los cuales deberas repartir el dinero disponible segun la situacion.", () => {
            setTimeout(() => {
                i = 0; // Reinicia el índice de animación
                animarSlider();
            }, 2000);
        });
    });
    
       

    sliders.forEach(slider => slider.value = 0);

    let i = 0;

    function animarSlider() {
        if (i >= sliders.length) {
            escribirTexto("Empezamos?");
            sliders.forEach(slider => slider.classList.remove("slider-activo"));
    
            // ✅ Aseguramos que no haya interferencias con timeouts anteriores
            clearInterval(intervaloEscritura);
    
            // ✅ Mostramos el botón sí o sí, sin depender del setTimeout
            empezarBtn.style.display = "block";
    
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
    escribirTexto("Hola! Soy el Conde, Para ganar debes pasar 5 escenarios en los cuales deberas repartir el dinero disponible segun la situacion.", () => {
        setTimeout(() => {
            animarSlider();
        }, 3500);
    });
});
