document.addEventListener('DOMContentLoaded', function() {
    // Animación básica en elementos de fondo
    anime({
        targets: '.line, .bar, .coin',
        translateY: function() {
            return anime.random(-200, 200);
        },
        translateX: function() {
            return anime.random(-200, 200);
        },
        scale: function() {
            return anime.random(0.5, 1.5);
        },
        easing: 'easeInOutQuad',
        duration: 2000,
        direction: 'alternate',
        loop: true
    });

    // Interacción con el fondo
    document.addEventListener('mousemove', function(e) {
        const x = e.clientX / window.innerWidth - 0.5;
        const y = e.clientY / window.innerHeight - 0.5;

        anime({
            targets: '.background',
            translateX: x * 50,
            translateY: y * 50,
            easing: 'easeOutQuad',
            duration: 300
        });
    });
});
