document.addEventListener("DOMContentLoaded", () => {
  if (!window.PROYECCIONES) return;

  const ctx = document.getElementById("proyChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: [
        "Año 1","Año 2","Año 3","Año 4","Año 5",
        "Año 6","Año 7","Año 8","Año 9","Año 10"
      ],
      datasets: [
        {
          label: "Escenario positivo",
          data: window.PROYECCIONES.positiva,
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: "Escenario neutro",
          data: window.PROYECCIONES.media,
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: "Escenario negativo",
          data: window.PROYECCIONES.negativa,
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" }
      }
    }
  });
});
