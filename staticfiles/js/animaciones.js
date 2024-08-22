// Configuración básica para un fondo animado en Three.js
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
var renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Partículas simples
var geometry = new THREE.SphereGeometry(15, 15, 15);
var material = new THREE.MeshBasicMaterial({ color: 0xffff00 });
var particle = new THREE.Mesh(geometry, material);
scene.add(particle);

camera.position.z = 50;

var animate = function () {
    requestAnimationFrame(animate);
    particle.rotation.x += 0.01;
    particle.rotation.y += 0.01;
    renderer.render(scene, camera);
};

animate();

// interaactividad del fondo
gsap.from(".menu-link", { duration: 1, y: 100, opacity: 0, stagger: 0.3, ease: "power2.out" });

gsap.to(".menu-link", {
  scrollTrigger: {
    trigger: ".menu-link",
    start: "top 80%",
    end: "top 40%",
    scrub: true
  },
  scale: 1.05
});

//
gsap.registerPlugin(ScrollTrigger);

gsap.to(".menu-option", {
  scrollTrigger: {
    trigger: ".menu-option",
    start: "top center",
    end: "bottom center",
    scrub: true,
    markers: true,
  },
  y: 50,
  opacity: 1,
});
