// feedback.js – Generador de Cartas de Perfil Financiero (versión retro con carta épica)


function generarPerfil() {
    
    let puntajeFinal = sessionStorage.getItem("puntaje_final") || 0;



    let resultados = JSON.parse(sessionStorage.getItem("player_results"));
    if (!resultados || resultados.length === 0) return {
        nombre: "Sin Datos",
        descripcion: "No hay suficientes datos para generar un perfil.",
        activo: "N/A",
        imagen: "/static/img/perfiles/default.png",
        rareza: "DESCONOCIDA"
    };

    const totales = resultados.reduce((acc, r) => {
        acc.vehicle += r.vehicle;
        acc.property += r.property;
        acc.education += r.education;
        acc.investment += r.investment;
        acc.leisure += r.leisure;
        acc.business += r.business;
        return acc;
    }, { vehicle: 0, property: 0, education: 0, investment: 0, leisure: 0, business: 0 });
    console.log("Totales calculados:", totales);

    let perfil;
const total = parseInt(puntajeFinal); // Puntaje promedio entre 0 y 100

if (total >= 95) {
    perfil = {
        nombre: "10ini",
        descripcion: "Eres el dios de las finanzas, sabes en donde apostar y donde no. Tus jugadas maestras te llevaran muy lejos.",
        activo: "Reputación & Rendimiento",
        imagen: "/static/img/perfiles/messi.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 90) {
    perfil = {
        nombre: "Marquini",
        descripcion: "Tenés visión emprendedora y mentalidad de crecimiento. Sos un constructor digital.",
        activo: "Startups",
        imagen: "/static/img/perfiles/galperin.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 85) {
    perfil = {
        nombre: "Mirthini",
        descripcion: "Creés en la educación, la elegancia y la constancia. Siempre presente, siempre aprendiendo.",
        activo: "Fondos Educativos",
        imagen: "/static/img/perfiles/mirtha.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 80) {
    perfil = {
        nombre: "Ricardini",
        descripcion: "Tu aptitud financiera es buena, balanceas entre buenas desiciones y vivir la vida, te esfuerzas para luego disfrutar al maximo.",
        activo: "Acciones de empresas de consumo masivo.",
        imagen: "/static/img/perfiles/fort.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 75) {
    perfil = {
        nombre: "Charlyni",
        descripcion: "Aprendiste a tu manera. Invertís en lo que amás, aunque a veces no te entiendan.",
        activo: "Arte Financiero",
        imagen: "/static/img/perfiles/charly.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 70) {
    perfil = {
        nombre: "REAL-STATINI",
        descripcion: "Te gustan las propiedades y el espectáculo. Tu habilidad es socializar y desarrollar.",
        activo: "Real Estate",
        imagen: "/static/img/perfiles/susana.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 65) {
    perfil = {
        nombre: "Wandini",
        descripcion: "Disfrutás del presente, las redes y los contratos. Sos estratega del social.",
        activo: "Influencers & Publicidad",
        imagen: "/static/img/perfiles/wanda.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 60) {
    perfil = {
        nombre: "F1 Franquini",
        descripcion: "Vas rápido, con precisión. Apostás al movimiento y sabés cómo llegar a la meta.",
        activo: "Velocidad & Patrocinios",
        imagen: "/static/img/perfiles/colapinto.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 55) {
    perfil = {
        nombre: "Carlos",
        descripcion: "Sabés moverte entre el poder y los negocios. Tu estilo es polémico pero efectivo.",
        activo: "Privatizaciones",
        imagen: "/static/img/perfiles/menem.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 50) {
    perfil = {
        nombre: "Albertini Sami",
        descripcion: "Sos terrenal, directo y tenés alma de comerciante. Las finanzas no te estresan.",
        activo: "Mercado Local",
        imagen: "/static/img/perfiles/samid.png",
        nivelFinanciero: `${total}/100`
    };
} else if (total >= 40) {
    perfil = {
        nombre: "L-Gantini",
        descripcion: "No tuviste recursos, pero hiciste negocios desde cero. Sos voz del pueblo con visión.",
        activo: "Movimiento Popular",
        imagen: "/static/img/perfiles/lgante.png",
        nivelFinanciero: `${total}/100`
    };
} else {
    perfil = {
        nombre: "Jugador Inusual",
        descripcion: "No puedes guardar un dolar que ya sabes donde es el peor lugar para gastarlo",
        activo: "Cartera Diversificada",
        imagen: "/static/img/perfiles/default.png",
        nivelFinanciero: `${total}/100`
    };
}

    fetch("/juego/guardar_perfil/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            resultados: totales,
            perfil_generado: perfil.nombre,
            player_id: sessionStorage.getItem("player_id")  // 👈 AGREGAR ESTO
        })
    });
    

    return perfil;
}

// El resto de las funciones se mantienen igual (mostrarPerfil, cerrarFeedback, etc.)


// El resto de las funciones se mantienen igual (mostrarPerfil, cerrarFeedback, etc.)


function mostrarPerfil() {
    const perfil = generarPerfil();

    // Determinar clase de nivel
    let nivelClass = "nivel-medio";
    const nivel = parseInt(perfil.nivelFinanciero) || 50;


    if (nivel < 35) nivelClass = "nivel-bajo";
    else if (nivel > 70) nivelClass = "nivel-alto";

    const cartaHTML = `
        <div class="carta-wrapper levitando">
            <div class="carta-financiera animacion-epica" onclick="compartirEnInstagram()">
                <h3 class="titulo-carta">${perfil.nombre}</h3>
                <img src="${perfil.imagen}" alt="${perfil.nombre}">
                <p class="frase-carta">“${perfil.descripcion}”</p>
                <div class="descripcion-extra">
                    <div class="texto">Activo representativo: ${perfil.activo}</div>
                    <div class="nivel-financiero ${nivelClass}">Nivel Financiero: ${nivel}%</div>
                </div>
            </div>
        </div>
    `;

    const perfilUsuario = document.getElementById("perfil-usuario");
    perfilUsuario.innerHTML = cartaHTML;
    perfilUsuario.style.display = "block";

    const overlay = document.getElementById("overlay-feedback");
    overlay.style.display = "block";
    requestAnimationFrame(() => overlay.classList.add("visible"));

    document.getElementById("cartel-contenido").style.display = "none";

    if (!document.getElementById("boton-cerrar-carta")) {
        const botonCerrar = document.createElement("button");
        botonCerrar.innerText = "✖";
        botonCerrar.className = "cerrar-carta";
        botonCerrar.id = "boton-cerrar-carta";
        botonCerrar.onclick = cerrarFeedback;
        document.body.appendChild(botonCerrar);
    }
}


function cerrarFeedback() {
    const overlay = document.getElementById("overlay-feedback");
    const carta = document.getElementById("perfil-usuario");

    overlay.classList.remove("visible");
    carta.style.opacity = "0";

    setTimeout(() => {
        overlay.style.display = "none";
        carta.style.display = "none";
        document.getElementById("boton-cerrar-carta")?.remove();
        document.getElementById("overlay-borroso")?.classList.remove("visible");
    }, 1000);
}

function cerrarCartelInicial() {
    document.getElementById("overlay-borroso")?.classList.remove("visible");
    document.getElementById("cartel-contenido").style.display = "none";
}

function reiniciarJuego() {
    sessionStorage.removeItem("player_results");
    window.location.href = "/juego/game/";
}

function compartirEnInstagram() {
    alert("📸 Hacé una captura de pantalla de tu carta y etiquetanos en Instagram para compartir tu perfil financiero.");
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function mostrarCartelCompra() {
    const overlay = document.getElementById("overlay-borroso");
    const cartel = document.getElementById("cartel-contenido");

    if (overlay && cartel) {
        overlay.classList.add("visible");
        cartel.style.display = "block";
    }
}
