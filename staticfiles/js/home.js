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


$(document).ready(function() {
    let container, carousel, items, radius, itemLength, rotationY, autoRotate;
    let mouseX = 0;
    let mouseY = 0;
    let rotationAngle = 0;
  
    container = $('#contentContainer');
    carousel = $('#carouselContainer');
    items = $('.carouselItem');
    itemLength = items.length;
    rotationY = 360 / itemLength;
    radius = Math.round(500 / Math.tan(Math.PI / itemLength));
  
    // Configura perspectiva y posición de inicio
    gsap.set(container, { perspective: 1000 });
    gsap.set(carousel, { z: -radius });
  
    // Posiciona elementos en el círculo
    items.each(function(i, el) {
      gsap.set(el, { rotationY: rotationY * i, z: radius, transformOrigin: "50% 50% -" + radius + "px" });
      gsap.to(el, 1, { autoAlpha: 1, delay: i * 0.1 });
    });
  
    // Animación de rotación continua
    function rotateCarousel() {
      rotationAngle += 0.2;
      gsap.to(carousel, { rotationY: rotationAngle, duration: 1, ease: "power2.out" });
      requestAnimationFrame(rotateCarousel);
    }
    rotateCarousel();
  
    // Interacción de rotación con el mouse
    window.addEventListener("mousemove", function(event) {
      mouseX = (event.clientX - window.innerWidth / 2) / window.innerWidth;
      mouseY = (event.clientY - window.innerHeight / 2) / window.innerHeight;
      rotationAngle += mouseX * 5;
    });
});


// Función para abrir la ventana modal
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.add("show");
}

// Función para cerrar la ventana modal
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.remove("show");
}

// Cerrar el modal cuando el usuario hace clic fuera del contenido del modal
window.onclick = function(event) {
  const modals = document.getElementsByClassName('modal');
  for (let i = 0; i < modals.length; i++) {
      if (event.target === modals[i]) {
          modals[i].classList.remove("show");
      }
  }
}

// Cerrar el modal cuando el usuario hace clic en la "X"
document.addEventListener("DOMContentLoaded", function() {
  const closeButtons = document.getElementsByClassName("close");
  for (let i = 0; i < closeButtons.length; i++) {
      closeButtons[i].onclick = function() {
          const modal = closeButtons[i].closest('.modal');
          modal.classList.remove("show");
      };
  }
});


