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
      esperaLobby: document.getElementById("pdp-espera-lobby"),
      esperaRonda: document.getElementById("pdp-espera-ronda"),
      rondaActiva: document.getElementById("pdp-ronda-activa"),
      rondaRevelada: document.getElementById("pdp-ronda-revelada"),
      final: document.getElementById("pdp-final"),
      miParticipante: document.getElementById("pdp-mi-participante"),
      capital: document.getElementById("pdp-capital"),
      deuda: document.getElementById("pdp-deuda"),
      habilidad: document.getElementById("pdp-mi-habilidad"),
      rondaTitulo: document.getElementById("pdp-jr-titulo"),
      rondaDescripcion: document.getElementById("pdp-jr-descripcion"),
      opciones: document.getElementById("pdp-jr-opciones"),
      resultadoTexto: document.getElementById("pdp-resultado-texto"),
      podio: document.getElementById("pdp-podio"),
      miPosicion: document.getElementById("pdp-mi-posicion"),
    };

    function ocultarTodo() {
      [els.esperaLobby, els.esperaRonda, els.rondaActiva, els.rondaRevelada, els.final].forEach(
        (e) => e && (e.hidden = true)
      );
    }

    function pintarCapital(participante) {
      if (!els.capital || !participante) return;
      els.capital.textContent = money(participante.capital_actual);
      if (els.deuda) {
        els.deuda.textContent =
          Number(participante.deuda) > 0 ? "Deuda pendiente: " + money(participante.deuda) : "";
      }
    }

    async function votar(opcion, boton) {
      document.querySelectorAll(".pdp-boton--opcion").forEach((b) => (b.disabled = true));
      const res = await postForm(urls.votar, { opcion });
      if (res.success) {
        boton.classList.add("pdp-seleccionada");
      }
      document.querySelectorAll(".pdp-boton--opcion").forEach((b) => (b.disabled = false));
      refrescar();
    }

    function renderOpciones(opciones, miVoto) {
      els.opciones.innerHTML = "";
      opciones.forEach((op) => {
        const btn = document.createElement("button");
        btn.className = "pdp-boton pdp-boton--opcion";
        btn.textContent = op.label + (op.disponible ? "" : " (no disponible todavía)");
        btn.disabled = !op.disponible;
        if (op.id === miVoto) btn.classList.add("pdp-seleccionada");
        btn.addEventListener("click", () => votar(op.id, btn));
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

      if (data.mi_habilidad && els.habilidad) {
        els.habilidad.textContent = "Tu habilidad: " + data.mi_habilidad;
        els.habilidad.hidden = false;
      }

      if (data.estado_partida === "lobby") {
        els.esperaLobby.hidden = false;
        if (els.miParticipante && data.participante) {
          els.miParticipante.innerHTML =
            data.participante.tipo === "equipo"
              ? `Código de tu equipo: <strong>${data.participante.codigo_equipo}</strong> (${data.participante.miembros} integrante(s))`
              : "";
        }
        return;
      }

      if (data.estado_partida === "finalizada") {
        els.final.hidden = false;
        const podio = data.podio || [];
        els.podio.innerHTML = podio
          .map(
            (p, i) => `<li class="pdp-fila-lb"><span class="pdp-fila-lb__pos">${i + 1}</span><span class="pdp-fila-lb__nombre">${escapeHtml(p.nombre)}</span><span class="pdp-fila-lb__capital">${money(p.capital_actual)}</span></li>`
          )
          .join("");
        const miIndice = podio.findIndex((p) => p.nombre === data.mi_participante.nombre);
        if (miIndice >= 0) els.miPosicion.textContent = `Terminaste en el puesto #${miIndice + 1}`;
        pintarCapital(data.mi_participante);
        return;
      }

      pintarCapital(data.mi_participante);

      if (data.ronda_estado === "activa") {
        els.rondaActiva.hidden = false;
        els.rondaTitulo.textContent = data.titulo_ronda;
        els.rondaDescripcion.textContent = data.descripcion_ronda;
        if (data.opciones && data.opciones.length) {
          renderOpciones(data.opciones, data.mi_voto);
        } else {
          els.opciones.innerHTML = '<p class="pdp-esperando">Esta ronda es automática, esperá al profe.</p>';
        }
      } else if (data.ronda_estado === "revelada") {
        els.rondaRevelada.hidden = false;
        if (data.resultado_ultima_ronda) {
          els.resultadoTexto.textContent =
            "Capital tras esta ronda: " + money(data.resultado_ultima_ronda.capital);
        }
      } else {
        els.esperaRonda.hidden = false;
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

  window.pdpInitJugador = initJugador;
})();
