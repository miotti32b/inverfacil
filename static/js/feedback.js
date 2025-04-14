// feedback.js – Sistema de Perfiles Creativos (36 combinaciones divertidas)

// 🎯 Generador de Perfil Financiero Basado en Decisiones del Jugador

window.addEventListener("load", () => {
    const perfilElement = document.getElementById("perfil-usuario");
    if (perfilElement) {
        perfilElement.textContent = generarPerfil();
    }
});

function generarPerfil() {
    let resultados = JSON.parse(sessionStorage.getItem("player_results"));
    if (!resultados || resultados.length === 0) return "No hay suficientes datos para generar un perfil.";

    const promedios = resultados.reduce((acc, r) => {
        acc.vehicle += r.vehicle;
        acc.property += r.property;
        acc.education += r.education;
        acc.investment += r.investment;
        acc.leisure += r.leisure;
        acc.business += r.business;
        return acc;
    }, { vehicle: 0, property: 0, education: 0, investment: 0, leisure: 0, business: 0 });

    let cantidad = resultados.length;
    for (let key in promedios) {
        promedios[key] = Math.round(promedios[key] / cantidad);
    }

    function nivel(valor) {
        if (valor >= 60) return 2;
        if (valor >= 30) return 1;
        return 0;
    }

    const claves = {
        education: nivel(promedios.education),
        investment: nivel(promedios.investment),
        business: nivel(promedios.business),
        leisure: nivel(promedios.leisure),
        property: nivel(promedios.property),
        vehicle: nivel(promedios.vehicle)
    };

    const claveFinal = `${claves.education}${claves.investment}${claves.business}${claves.leisure}${claves.property}${claves.vehicle}`;

    const perfiles = {
        "222222": { nombre: "Maestro del Dinero", descripcion: "Dominás todos los aspectos del juego financiero. ¡Impresionante!" },
        "000000": { nombre: "Nómada Despreocupado", descripcion: "Vivís sin ataduras ni planes. Tal vez deberías empezar a mirar tu cuenta bancaria." },
        "111111": { nombre: "El Equilibrado Legendario", descripcion: "Tu sentido del balance es envidiable. No te sobra nada, no te falta nada. Un verdadero Jedi de las finanzas." },
        "222000": { nombre: "El Cerebro del Capital", descripcion: "Un genio de las finanzas con alma de CEO. Tus decisiones muestran visión, cálculo y estrategia." },
        "000222": { nombre: "El Placerista Espontáneo", descripcion: "Si algo te gusta, lo hacés. El futuro... bueno, ese se verá después." },
        "202120": { nombre: "El Cazador de Oportunidades", descripcion: "Saltás de inversión en inversión. A veces ganás, a veces aprendés." },
        "021120": { nombre: "El Visionario Creativo", descripcion: "Invertís con coraje y aprendés del camino. Un soñador con pies en la tierra." },
        "110012": { nombre: "El Buen Vecino", descripcion: "No arriesgás mucho, pero cuidás lo tuyo. Tu casa, tu auto y tu paz mental." },
        "100122": { nombre: "El Hedonista Estratega", descripcion: "Disfrutás del ahora, pero con mirada astuta hacia el futuro." },
        "200201": { nombre: "El Tacaño Inversionista", descripcion: "Sacrificaste todo por tu billetera. ¿Y el disfrute? Está en los intereses compuestos." },
        "011211": { nombre: "El Estudiante Emprendedor", descripcion: "Capacitación e inversión son tus pilares. Lo vas a lograr (¡y lo sabés!)." },
        "120102": { nombre: "El Experto Minimalista", descripcion: "Elegís poco, pero elegís bien. Tu enfoque selectivo tiene impacto." },
        "212012": { nombre: "El Jugador Pro", descripcion: "Arriesgás con sentido, y sabés cuándo bajar la palanca. Crack total." },
        "002222": { nombre: "El Epicúreo Rodante", descripcion: "Vivís la vida a todo motor y sin mirar atrás. Para vos, la experiencia presente lo es todo." },
        "101101": { nombre: "El Arquitecto del Equilibrio", descripcion: "Tu planificación está presente, pero dejás espacio para la aventura." },
        "121112": { nombre: "El Capitán de su Destino", descripcion: "Llevás el timón con seguridad. Tomás riesgos calculados y no le temés al cambio." },
        "010000": { nombre: "El Hijo del Azar", descripcion: "Tus decisiones parecen aleatorias... ¿o sabés algo que el resto no?" },
        "111000": { nombre: "El Conservador Tranquilo", descripcion: "Nada de locuras. Tu enfoque sobrio y predecible te mantiene a salvo... por ahora." },
        "002000": { nombre: "El Fiestero Místico", descripcion: "Vivís entre humo y música. A veces te acordás que existían los ahorros." },
        "222111": { nombre: "El Emperador Moderno", descripcion: "Tenés visión, tenés control, tenés estilo. Un perfil para dominar el mundo (financiero)." },
        "011011": { nombre: "El Clásico Sensato", descripcion: "Tus decisiones reflejan prudencia y sentido común. Como tu abuela te enseñó." },
        "221002": { nombre: "El Ejecutivo Relajado", descripcion: "Cuidás tu negocio pero no descuidás el disfrute. Buen balance para un alma intensa." },
        "122001": { nombre: "El Constructor de Sueños", descripcion: "Tus ideas se transforman en ladrillos. Literalmente: ¡invertís y construís!" },
        "102220": { nombre: "El Aprendiz Glorioso", descripcion: "Invertiste en capacitarte, en vivir y en crecer. No parás de evolucionar." },
        "220220": { nombre: "El Intocable", descripcion: "Todo lo hacés bien, incluso cuando fallás. Tenés ángel financiero." },
        "000111": { nombre: "El Vacacionista Empedernido", descripcion: "Te tomaste en serio eso de vivir la vida. Pero ojo con el colchón de ahorros." },
        "210012": { nombre: "El Disciplinado Rebelde", descripcion: "Respetás las reglas, pero también sabés cuándo romperlas. Todo con estilo." },
        "120222": { nombre: "El Glotón de Oportunidades", descripcion: "Donde hay chance, ahí estás. Sos ambicioso y entusiasta. ¡Canalizalo!" },
        "101100": { nombre: "El Moderado Precavido", descripcion: "No te volás la cabeza, pero tampoco dormís. Equilibrio con freno de mano." },
        "100100": { nombre: "El Zen Financiero", descripcion: "Todo con calma. Tu mantra: gastar poco, pensar mucho, vivir bien." },
        "222221": { nombre: "El Titán", descripcion: "Te jugás con todo y sabés que vas a ganar. Nada te detiene." },
        "121000": { nombre: "El Metódico Silencioso", descripcion: "Pocos lo notan, pero vas avanzando firme. Tu plan es secreto... y funciona." },
        "210210": { nombre: "El Inversor de Batalla", descripcion: "Pasaste por todo y seguís en pie. Sos resiliente y tenés calle financiera." },
        "011222": { nombre: "El Disfrutador Sagaz", descripcion: "Sabés cuándo parar y cuándo gozar. ¡Maestro del momento justo!" },
        "221221": { nombre: "El Máster de Portafolios", descripcion: "Tu cabeza es una hoja de Excel. Sabés diversificar como un profesional." },
        "112211": { nombre: "El Semilla de Éxito", descripcion: "No llegaste aún, pero vas en camino. Seguís creciendo. Vas bien." },
        "000000": { nombre: "El Espíritu Libre", descripcion: "Hacés lo que querés, sin pensar en consecuencias. A veces, eso también es vivir." }
    };

    return `${perfiles[claveFinal]?.nombre || "Jugador Inusual"}: ${perfiles[claveFinal]?.descripcion || "Decisiones únicas. ¡Sos un misterio financiero!"}`;
}

// Manejo del pago simulado y visualización del perfil
document.getElementById("feedback-btn").addEventListener("click", () => {
    if (confirm("¿Deseas pagar $100 para conocer tu perfil personalizado?")) {
        const perfilElement = document.getElementById("perfil-usuario");
        perfilElement.classList.remove("oculto");
        perfilElement.textContent = generarPerfil();
    }
});
