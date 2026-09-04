(function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
  }

  async function get(url) {
    const resp = await fetch(url, { cache: "no-store" });
    return resp.json();
  }

  async function postForm(url, datos) {
    const body = new URLSearchParams(datos);
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body,
    });
    return resp.json();
  }

  function initJugador(root) {
    const urls = JSON.parse(root.dataset.urls);
    const els = {
      esperaLobby: document.getElementById("tf-espera-lobby"),
      esperaPregunta: document.getElementById("tf-espera-pregunta"),
      preguntaCard: document.getElementById("tf-pregunta-card"),
      timerWrap: document.getElementById("tf-timer-wrap"),
      resultadoWrap: document.getElementById("tf-resultado-wrap"),
      final: document.getElementById("tf-final"),
      miJugador: document.getElementById("tf-mi-jugador"),
      puntaje: document.getElementById("tf-puntaje"),
      timerNumero: document.getElementById("tf-timer-numero"),
      timerRelleno: document.getElementById("tf-timer-relleno"),
      preguntaTexto: document.getElementById("tf-pregunta-texto"),
      opciones: document.getElementById("tf-opciones"),
      resultadoTexto: document.getElementById("tf-resultado-texto"),
      explicacion: document.getElementById("tf-explicacion"),
      podio: document.getElementById("tf-podio"),
      miPosicion: document.getElementById("tf-mi-posicion"),
    };

    let timerHandle = null;
    let yaVoteEstaPregunta = false;

    function ocultarTodo() {
      [els.esperaLobby, els.esperaPregunta, els.preguntaCard, els.final].forEach(
        (e) => e && (e.hidden = true)
      );
    }

    function detenerTimer() {
      if (timerHandle) {
        clearInterval(timerHandle);
        timerHandle = null;
      }
    }

    function iniciarTimer(iniciadaEnIso, duracionSeg) {
      detenerTimer();
      const iniciadaEnMs = new Date(iniciadaEnIso).getTime();
      const duracionMs = duracionSeg * 1000;

      function tick() {
        const restanteMs = Math.max(0, duracionMs - (Date.now() - iniciadaEnMs));
        const restanteSeg = Math.ceil(restanteMs / 1000);
        if (els.timerNumero) els.timerNumero.textContent = restanteSeg;
        if (els.timerRelleno) {
          els.timerRelleno.style.width = (100 * restanteMs / duracionMs) + "%";
          els.timerRelleno.classList.toggle("tf-timer-urgente", restanteMs <= 5000);
        }
        if (restanteMs <= 0) {
          document.querySelectorAll(".tf-opcion").forEach((b) => (b.disabled = true));
          detenerTimer();
        }
      }
      tick();
      timerHandle = setInterval(tick, 100);
    }

    async function votar(indice, boton) {
      if (yaVoteEstaPregunta) return;
      yaVoteEstaPregunta = true;
      document.querySelectorAll(".tf-opcion").forEach((b) => (b.disabled = true));
      boton.classList.add("tf-seleccionada");
      await postForm(urls.votar, { opcion: indice });
    }

    function renderOpciones(opciones, miVoto) {
      els.opciones.innerHTML = "";
      yaVoteEstaPregunta = miVoto !== null && miVoto !== undefined;
      opciones.forEach((texto, i) => {
        const btn = document.createElement("button");
        btn.className = `tf-opcion tf-opcion--${i}`;
        btn.textContent = texto;
        btn.disabled = yaVoteEstaPregunta;
        if (i === miVoto) btn.classList.add("tf-seleccionada");
        btn.addEventListener("click", () => votar(i, btn));
        els.opciones.appendChild(btn);
      });
    }

    function renderOpcionesReveladas(opciones, respuestaCorrecta) {
      els.opciones.innerHTML = "";
      opciones.forEach((texto, i) => {
        const btn = document.createElement("button");
        btn.className = `tf-opcion tf-opcion--${i}`;
        btn.textContent = texto;
        btn.disabled = true;
        btn.classList.add(i === respuestaCorrecta ? "tf-correcta" : "tf-incorrecta");
        els.opciones.appendChild(btn);
      });
    }

    async function refrescar() {
      const data = await get(urls.estado);
      if (!data.success) {
        if (data.error === "no_unido") window.location.href = urls.unirse;
        return;
      }

      ocultarTodo();

      if (data.estado_partida === "lobby") {
        detenerTimer();
        els.esperaLobby.hidden = false;
        if (els.miJugador && data.jugador) {
          els.miJugador.innerHTML =
            data.jugador.tipo === "equipo"
              ? `Código de tu equipo: <strong>${data.jugador.codigo_equipo}</strong> (${data.jugador.miembros} integrante(s))`
              : "";
        }
        return;
      }

      if (els.puntaje) els.puntaje.textContent = data.mi_puntaje ?? 0;

      if (data.estado_partida === "finalizada") {
        detenerTimer();
        els.final.hidden = false;
        const podio = data.podio || [];
        els.podio.innerHTML = podio
          .map(
            (p, i) => `<li class="tf-fila-lb"><span class="tf-fila-lb__pos">${i + 1}</span><span class="tf-fila-lb__nombre">${escapeHtml(p.nombre)}</span><span class="tf-fila-lb__puntaje">${p.puntaje_total} pts</span></li>`
          )
          .join("");
        const miIndice = podio.findIndex((p) => p.nombre === data.mi_nombre || p.puntaje_total === data.mi_puntaje);
        if (miIndice >= 0) els.miPosicion.textContent = `Terminaste en el puesto #${miIndice + 1}`;
        return;
      }

      if (data.pregunta_estado === "activa" && data.pregunta_iniciada_en) {
        els.preguntaCard.hidden = false;
        els.timerWrap.hidden = false;
        els.resultadoWrap.hidden = true;
        els.preguntaTexto.textContent = data.pregunta_texto;
        renderOpciones(data.opciones, data.mi_voto);
        iniciarTimer(data.pregunta_iniciada_en, data.duracion_seg);
      } else if (data.pregunta_estado === "revelada") {
        detenerTimer();
        els.preguntaCard.hidden = false;
        els.timerWrap.hidden = true;
        els.resultadoWrap.hidden = false;
        els.preguntaTexto.textContent = data.pregunta_texto;
        renderOpcionesReveladas(data.opciones, data.respuesta_correcta);
        if (data.mi_resultado) {
          els.resultadoTexto.textContent = data.mi_resultado.es_correcta
            ? `¡Correcto! +${data.mi_resultado.puntos_obtenidos} puntos`
            : "No era esa";
          els.resultadoTexto.className = data.mi_resultado.es_correcta ? "tf-positivo" : "tf-negativo";
        } else {
          els.resultadoTexto.textContent = "No llegaste a responder";
          els.resultadoTexto.className = "tf-negativo";
        }
        els.explicacion.textContent = data.explicacion || "";
      } else {
        detenerTimer();
        els.esperaPregunta.hidden = false;
      }
    }

    refrescar();
    let intervalo = setInterval(refrescar, 2000);
    document.addEventListener("visibilitychange", () => {
      clearInterval(intervalo);
      if (!document.hidden) {
        refrescar();
        intervalo = setInterval(refrescar, 2000);
      }
    });
  }

  window.tfInitJugador = initJugador;
})();
