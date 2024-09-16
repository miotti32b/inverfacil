function toggleMenu() {
    const menu = document.getElementById('menu-desplegable');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
  }

function formatearDolar(input) {
    let valor = input.value.replace(/[^0-9.]/g, ''); // Eliminar caracteres no numéricos
      if (valor) {
        valor = parseFloat(valor).toFixed(2); // Convertir a número con 2 decimales
        input.value = `$${valor}`;
      } else {
        input.value = ''; // Si no hay valor, dejarlo vacío
      }
  }






