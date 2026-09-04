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

  function money(value) {
    const n = Number(value);
    const signo = n < 0 ? "-" : "";
    return signo + "$" + Math.abs(n).toLocaleString("es-AR", { maximumFractionDigits: 0 });
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

  function renderLeaderboard(el, filas) {
    if (!filas || !filas.length) {
      el.innerHTML = '<p class="pdp-esperando">Todavía no hay resultados.</p>';
      return;
    }
    el.innerHTML =
      '<ul class="pdp-leaderboard">' +
      filas
        .map(
          (f, i) => `
        <li class="pdp-fila-lb">
          <span class="pdp-fila-lb__pos">${i + 1}</span>
          <span class="pdp-badge pdp-badge--${f.tipo || "individual"}">${f.tipo === "equipo" ? "Equipo" : "Individual"}</span>
          <span class="pdp-fila-lb__nombre">${escapeHtml(f.nombre)}</span>
          <span class="pdp-fila-lb__capital">${money(f.capital_actual)}</span>
        </li>`
        )
        .join("") +
      "</ul>";
  }

  function initHostLobby(root) {
    const urls = JSON.parse(root.dataset.urls);
    const els = {
      lobbyBox: document.getElementById("pdp-lobby-box"),
      lobbyLista: document.getElementById("pdp-lobby-lista"),
      lobbyTotal: document.getElementById("pdp-lobby-total"),
      btnIniciarPartida: document.getElementById("pdp-btn-iniciar-partida"),
      rondaBox: document.getElementById("pdp-ronda-box"),
      rondaNumero: document.getElementById("pdp-ronda-numero"),
      rondaTitulo: document.getElementById("pdp-ronda-titulo"),
      rondaEstadoTxt: document.getElementById("pdp-ronda-estado-txt"),
      votos: document.getElementById("pdp-votos"),
      btnIniciarRonda: document.getElementById("pdp-btn-iniciar-ronda"),
      btnRevelar: document.getElementById("pdp-btn-revelar"),
      btnSiguiente: document.getElementById("pdp-btn-siguiente"),
      leaderboard: document.getElementById("pdp-leaderboard"),
      finalLink: document.getElementById("pdp-final-link"),
    };

    let procesando = false;

    async function refrescar() {
      const data = await get(urls.estado);
      if (!data.success) return;

      els.lobbyBox.hidden = data.estado_partida !== "lobby";
      els.rondaBox.hidden = data.estado_partida === "lobby";

      if (data.estado_partida === "lobby") {
        els.lobbyTotal.textContent = data.total_participantes;
        els.lobbyLista.innerHTML = (data.lobby_participantes || [])
          .map(
            (p) =>
              `<li class="pdp-fila-lb"><span class="pdp-badge pdp-badge--${p.tipo}">${p.tipo === "equipo" ? "Equipo" : "Individual"}</span><span class="pdp-fila-lb__nombre">${escapeHtml(p.nombre)}</span><span class="pdp-tenue">${p.tipo === "equipo" ? p.miembros + " integrante(s)" : ""}</span></li>`
          )
          .join("");
        els.btnIniciarPartida.disabled = data.total_participantes < 1;
        return;
      }

      if (data.estado_partida === "finalizada") {
        els.finalLink.hidden = false;
        els.rondaTitulo.textContent = "¡Partida terminada!";
        els.rondaEstadoTxt.textContent = "Mirá el podio final.";
        els.btnIniciarRonda.hidden = true;
        els.btnRevelar.hidden = true;
        els.btnSiguiente.hidden = true;
        renderLeaderboard(els.leaderboard, data.podio);
        return;
      }

      els.rondaNumero.textContent = `Ronda ${data.ronda_actual} de 6`;

      if (data.ronda_estado === "inactiva") {
        els.rondaTitulo.textContent = "Listos para la próxima ronda";
        els.rondaEstadoTxt.textContent = "";
        els.btnIniciarRonda.hidden = false;
        els.btnRevelar.hidden = true;
        els.btnSiguiente.hidden = true;
        els.votos.textContent = "";
      } else if (data.ronda_estado === "activa") {
        els.rondaTitulo.textContent = "Ronda en curso, están votando...";
        els.rondaEstadoTxt.textContent = "";
        els.votos.textContent = `${data.votos_recibidos} / ${data.votos_totales_esperados} ya decidieron`;
        els.btnIniciarRonda.hidden = true;
        els.btnRevelar.hidden = false;
        els.btnSiguiente.hidden = true;
      } else if (data.ronda_estado === "revelada") {
        els.rondaTitulo.textContent = "Resultados revelados";
        els.rondaEstadoTxt.textContent = "";
        els.votos.textContent = "";
        els.btnIniciarRonda.hidden = true;
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

    els.btnIniciarPartida.addEventListener("click", () =>
      accion(els.btnIniciarPartida, urls.iniciarPartida)
    );
    els.btnIniciarRonda.addEventListener("click", () =>
      accion(els.btnIniciarRonda, urls.iniciarRonda)
    );
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

  function initHostFinal(root) {
    const urls = JSON.parse(root.dataset.urls);
    const lista = document.getElementById("pdp-podio-lista");
    const canvas = document.getElementById("pdp-grafico");

    function dibujarGrafico(podio) {
      if (!canvas || !podio.length) return;
      const ctx = canvas.getContext("2d");
      const w = (canvas.width = canvas.clientWidth);
      const h = (canvas.height = 260);
      ctx.clearRect(0, 0, w, h);

      // el capital final puede terminar negativo (ronda de apalancamiento), así
      // que el gráfico necesita una línea de base en cero, no solo barras hacia arriba
      const topPad = 10;
      const bottomPad = 20; // reservado para las etiquetas de nombre
      const plotH = h - topPad - bottomPad;
      const valores = podio.map((p) => Number(p.capital_actual));
      const maxVal = Math.max(...valores, 0);
      const minVal = Math.min(...valores, 0);
      const rango = maxVal - minVal || 1;
      const baseY = topPad + (maxVal / rango) * plotH;

      ctx.strokeStyle = "#475569";
      ctx.beginPath();
      ctx.moveTo(0, baseY);
      ctx.lineTo(w, baseY);
      ctx.stroke();

      const barW = w / podio.length;
      podio.forEach((p, i) => {
        const valor = valores[i];
        const altoBarra = (Math.abs(valor) / rango) * plotH;
        const x = i * barW + barW * 0.15;
        const anchoBarra = barW * 0.7;
        const y = valor >= 0 ? baseY - altoBarra : baseY;
        ctx.fillStyle = valor < 0 ? "#f87171" : i === 0 ? "#4ade80" : "#22d3ee";
        ctx.fillRect(x, y, anchoBarra, altoBarra);
        ctx.fillStyle = "#f1f5f9";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(p.nombre.slice(0, 10), x + anchoBarra / 2, h - 6);
      });
    }

    async function cargar() {
      const data = await get(urls.estado);
      if (!data.success) return;
      const podio = data.podio || [];
      lista.innerHTML = podio
        .map(
          (p, i) => `
        <li class="pdp-fila-lb">
          <span class="pdp-fila-lb__pos">${i + 1}</span>
          <span class="pdp-fila-lb__nombre">${escapeHtml(p.nombre)}</span>
          <span class="pdp-fila-lb__capital">${money(p.capital_actual)}</span>
        </li>`
        )
        .join("");
      dibujarGrafico(podio);
    }

    cargar();
  }

  window.pdpInitHostLobby = initHostLobby;
  window.pdpInitHostFinal = initHostFinal;
})();
