// Detecta cuando el usuario hace scroll en dispositivos móviles
window.addEventListener('scroll', function() {
  if (window.innerWidth <= 768) {
      document.body.classList.add('scrolled');
  }
});

document.addEventListener('mousemove', function(e) {
  const focusCircle = document.getElementById('focus-circle');
  focusCircle.style.left = `${e.pageX - 100}px`; // Centra el círculo horizontalmente
  focusCircle.style.top = `${e.pageY - 100}px`; // Centra el círculo verticalmente
});


