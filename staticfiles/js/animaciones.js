document.querySelector('button').addEventListener('click', function() {
  const calculadora = document.querySelector('.calculadora-container');
  calculadora.classList.add('show');
});

document.addEventListener("DOMContentLoaded", function() {
  const modal = document.getElementById("resultadoModal");
  const closeBtn = document.getElementsByClassName("close")[0];
  const resultadoTexto = document.getElementById("resultadoTexto");

  // Función para abrir el modal con el resultado
  function mostrarResultado(monto) {
      resultadoTexto.innerHTML = `El monto final seria: $${monto}`;
      modal.style.display = "block";
  }

  // Cerrar modal al hacer clic en la 'x'
  closeBtn.onclick = function() {
      modal.style.display = "none";
  }

  // Cerrar modal al hacer clic fuera del contenido
  window.onclick = function(event) {
      if (event.target === modal) {
          modal.style.display = "none";
      }
  }

  // Capturar el valor del monto calculado desde el backend
  const montoCalculado = document.getElementById("resultadoMonto").textContent;
  
  // Si existe un resultado, mostrarlo en el modal
  if (montoCalculado) {
      mostrarResultado(montoCalculado);
  }
});



