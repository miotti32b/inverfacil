(function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  async function post(url) {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    });
    return resp.json();
  }

  async function get(url) {
    const resp = await fetch(url, { cache: "no-store" });
    return resp.json();
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
  }

  function renderLeaderboard(el, filas) {
    if (!filas || !filas.length) {
      el.innerHTML = '<p class="tf-esperando">Todavía no hay puntajes.</p>';
      return;
    }

    // técnica FLIP: guardamos la posición anterior de cada fila (por nombre)
    // para animar el deslizamiento cuando cambia el orden del ranking.
    let ul = el.querySelector(".tf-leaderboard");
    const posicionesPrevias = new Map();
    if (ul) {
      ul.querySelectorAll("li[data-key]").forEach((li) => {
        posicionesPrevias.set(li.dataset.key, li.getBoundingClientRect().top);
      });
    } else {
      ul = document.createElement("ul");
      ul.className = "tf-leaderboard";
      el.innerHTML = "";
      el.appendChild(ul);
    }

    ul.innerHTML = filas
      .map(
        (f, i) => `
        <li class="tf-fila-lb" data-key="${encodeURIComponent(f.nombre)}">
          <span class="tf-fila-lb__pos">${i + 1}</span>
          <span class="tf-badge tf-badge--${f.tipo || "individual"}">${f.tipo === "equipo" ? "Equipo" : "Individual"}</span>
          <span class="tf-fila-lb__nombre">${escapeHtml(f.nombre)}</span>
          <span class="tf-fila-lb__puntaje">${f.puntaje_total} pts</span>
        </li>`
      )
      .join("");

    ul.querySelectorAll("li[data-key]").forEach((li) => {
      const antes = posicionesPrevias.get(li.dataset.key);
      if (antes === undefined) return; // fila nueva, sin animación de movimiento
      const delta = antes - li.getBoundingClientRect().top;
      if (Math.abs(delta) < 1) return;
      li.style.transition = "none";
      li.style.transform = `translateY(${delta}px)`;
      li.classList.add(delta > 0 ? "tf-fila-subio" : "tf-fila-bajo");
      requestAnimationFrame(() => {
        li.style.transition = "transform 0.5s ease";
        li.style.transform = "";
      });
      setTimeout(() => li.classList.remove("tf-fila-subio", "tf-fila-bajo"), 900);
    });
  }

  function initHostLobby(root) {
    const urls = JSON.parse(root.dataset.urls);
    const els = {
      lobbyBox: document.getElementById("tf-lobby-box"),
      lobbyLista: document.getElementById("tf-lobby-lista"),
      btnIniciarPartida: document.getElementById("tf-btn-iniciar-partida"),
      preguntaBox: document.getElementById("tf-pregunta-box"),
      preguntaNumero: document.getElementById("tf-pregunta-numero"),
      preguntaTitulo: document.getElementById("tf-pregunta-titulo"),
      timerWrap: document.getElementById("tf-timer-wrap"),
      timerNumero: document.getElementById("tf-timer-numero"),
      timerRelleno: document.getElementById("tf-timer-relleno"),
      votos: document.getElementById("tf-votos"),
      explicacion: document.getElementById("tf-explicacion"),
      btnIniciarPregunta: document.getElementById("tf-btn-iniciar-pregunta"),
      btnRevelar: document.getElementById("tf-btn-revelar"),
      btnSiguiente: document.getElementById("tf-btn-siguiente"),
      leaderboard: document.getElementById("tf-leaderboard"),
      finalLink: document.getElementById("tf-final-link"),
    };

    let procesando = false;
    let timerHandle = null;

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
      let autoRevelando = false;
      function tick() {
        const restanteMs = Math.max(0, duracionMs - (Date.now() - iniciadaEnMs));
        els.timerNumero.textContent = Math.ceil(restanteMs / 1000);
        els.timerRelleno.style.width = (100 * restanteMs / duracionMs) + "%";
        els.timerRelleno.classList.toggle("tf-timer-urgente", restanteMs <= 5000);
        if (restanteMs <= 0) {
          detenerTimer();
          // se agotó el tiempo: revelamos solo, sin esperar a que el host toque el botón
          if (!autoRevelando) {
            autoRevelando = true;
            accion(els.btnRevelar, urls.revelar);
          }
        }
      }
      tick();
      timerHandle = setInterval(tick, 100);
    }

    async function refrescar() {
      const data = await get(urls.estado);
      if (!data.success) return;

      els.lobbyBox.hidden = data.estado_partida !== "lobby";
      els.preguntaBox.hidden = data.estado_partida === "lobby";

      if (data.estado_partida === "lobby") {
        detenerTimer();
        els.lobbyLista.innerHTML = (data.lobby_jugadores || [])
          .map(
            (j) =>
              `<li class="tf-fila-lb"><span class="tf-badge tf-badge--${j.tipo}">${j.tipo === "equipo" ? "Equipo" : "Individual"}</span><span class="tf-fila-lb__nombre">${escapeHtml(j.nombre)}</span><span class="tf-tenue">${j.tipo === "equipo" ? j.miembros + " integrante(s)" : ""}</span></li>`
          )
          .join("");
        els.btnIniciarPartida.disabled = data.total_jugadores < 1;
        return;
      }

      if (data.estado_partida === "finalizada") {
        detenerTimer();
        els.finalLink.hidden = false;
        els.preguntaTitulo.textContent = "¡Partida terminada!";
        els.timerWrap.hidden = true;
        els.votos.textContent = "";
        els.explicacion.textContent = "";
        els.btnIniciarPregunta.hidden = true;
        els.btnRevelar.hidden = true;
        els.btnSiguiente.hidden = true;
        renderLeaderboard(els.leaderboard, data.podio);
        return;
      }

      els.preguntaNumero.textContent = `Pregunta ${data.pregunta_actual_index + 1} de ${data.total_preguntas}`;

      if (data.pregunta_estado === "inactiva") {
        detenerTimer();
        els.preguntaTitulo.textContent = "Listos para la próxima pregunta";
        els.timerWrap.hidden = true;
        els.votos.textContent = "";
        els.explicacion.textContent = "";
        els.btnIniciarPregunta.hidden = false;
        els.btnRevelar.hidden = true;
        els.btnSiguiente.hidden = true;
      } else if (data.pregunta_estado === "activa") {
        els.preguntaTitulo.textContent = data.pregunta_texto;
        els.timerWrap.hidden = false;
        if (data.pregunta_iniciada_en) iniciarTimer(data.pregunta_iniciada_en, data.duracion_seg);
        els.votos.textContent = `${data.votos_recibidos} / ${data.votos_totales_esperados} ya decidieron`;
        els.explicacion.textContent = "";
        els.btnIniciarPregunta.hidden = true;
        els.btnRevelar.hidden = false;
        els.btnSiguiente.hidden = true;
      } else if (data.pregunta_estado === "revelada") {
        detenerTimer();
        els.preguntaTitulo.textContent = data.pregunta_texto;
        els.timerWrap.hidden = true;
        els.votos.textContent = "";
        const correcta = data.opciones ? data.opciones[data.respuesta_correcta] : "";
        els.explicacion.textContent = `Correcta: ${correcta}. ${data.explicacion || ""}`;
        els.btnIniciarPregunta.hidden = true;
        els.btnRevelar.hidden = true;
        els.btnSiguiente.hidden = false;
      }

      renderLeaderboard(els.leaderboard, data.leaderboard);
    }

    async function accion(boton, url) {
      if (procesando) return;
      procesando = true;
      boton.disabled = true;
      try {
        await post(url);
        await refrescar();
      } finally {
        boton.disabled = false;
        procesando = false;
      }
    }

    els.btnIniciarPartida.addEventListener("click", () => accion(els.btnIniciarPartida, urls.iniciarPartida));
    els.btnIniciarPregunta.addEventListener("click", () => accion(els.btnIniciarPregunta, urls.iniciarPregunta));
    els.btnRevelar.addEventListener("click", () => accion(els.btnRevelar, urls.revelar));
    els.btnSiguiente.addEventListener("click", () => accion(els.btnSiguiente, urls.siguiente));

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

  window.tfInitHostLobby = initHostLobby;
})();
