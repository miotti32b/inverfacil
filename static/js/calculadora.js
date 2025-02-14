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
    // Formatear el número con separadores de miles
        const montoFormateado = parseFloat(monto).toLocaleString('es-ES', { minimumFractionDigits: 0 });
        resultadoTexto.innerHTML = `El monto final sería: $${montoFormateado}`;
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
  
  // Asegúrate de redondear el valor a un entero
    

  // Si existe un resultado, mostrarlo en el modal
  if (montoCalculado) {
      mostrarResultado(montoCalculado);
  }
});





// Configuración de Three.js
const canvas = document.getElementById('grafico-3d');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(canvas.clientWidth, 400);
renderer.shadowMap.enabled = true; // Activar sombras

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff); // Fondo blanco

const camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / 400, 0.1, 1000);
camera.position.set(0, 50, 150);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Luz ambiental
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// Luz direccional con sombras
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(50, 50, 50);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Plano receptor de sombras
const planeGeometry = new THREE.PlaneGeometry(500, 500);
const planeMaterial = new THREE.ShadowMaterial({ opacity: 0.2 });
const plane = new THREE.Mesh(planeGeometry, planeMaterial);
plane.rotation.x = -Math.PI / 2; // Horizontal
plane.position.y = 0; // Nivel del suelo
plane.receiveShadow = true;
scene.add(plane);

// Conversión de tasas y períodos
function convertirPeriodo(periodo) {
    switch (periodo) {
        case 'daily':
            return 1;
        case 'weekly':
            return 7;
        case 'monthly':
            return 30;
        case 'yearly':
            return 365;
        default:
            return 1;
    }
}

// Función para proyectar etiquetas al espacio 2D
function agregarEtiqueta(x, y, z, texto) {
    const div = document.createElement('div');
    div.className = 'etiqueta';
    div.textContent = texto;
    div.style.position = 'absolute';
    div.style.color = '#000';
    div.style.backgroundColor = '#fff';
    div.style.padding = '5px';
    div.style.borderRadius = '4px';
    div.style.fontSize = '12px';
    div.style.transform = 'translate(-50%, -50%)';
    document.body.appendChild(div);

    const vector = new THREE.Vector3(x, y, z);
    vector.project(camera);

    const halfWidth = window.innerWidth / 2;
    const halfHeight = window.innerHeight / 2;

    div.style.left = `${halfWidth + vector.x * halfWidth}px`;
    div.style.top = `${halfHeight - vector.y * halfHeight}px`;

    return div;
}

// Función para generar el gráfico
function generarGrafico(principal, additionalInvestment, investmentPeriod, time, timePeriod, rate, ratePeriod) {
    // Limpia la escena (excepto luz, cámara y plano)
    while (scene.children.length > 2) {
        scene.remove(scene.children[2]);
    }

    // Elimina etiquetas existentes
    document.querySelectorAll('.etiqueta').forEach((el) => el.remove());

    const timeUnit = convertirPeriodo(timePeriod);
    const investmentDays = convertirPeriodo(investmentPeriod);
    const rateDays = convertirPeriodo(ratePeriod);

    const dailyRate = rate / 100 / rateDays;
    const totalUnits = time;

    let totalCapital = principal;
    let totalContributions = principal;

    const data = [];

    for (let unit = 1; unit <= totalUnits; unit++) {
        if (unit % (investmentDays / timeUnit) === 0) {
            totalCapital += additionalInvestment;
            totalContributions += additionalInvestment;
        }

        for (let day = 0; day < timeUnit; day++) {
            totalCapital *= (1 + dailyRate);
        }

        data.push({
            totalCapital,
            totalContributions,
            interest: totalCapital - totalContributions,
        });
    }

    // Encontrar la barra más alta para escalar el gráfico
    const maxHeight = Math.max(...data.map((item) => item.totalCapital));
    const maxGraphHeight = 50; // Altura máxima del gráfico en unidades

    // Crear las barras
    data.forEach((item, index) => {
        const totalHeight = (item.totalCapital / maxHeight) * maxGraphHeight;
        const contributionHeight = (item.totalContributions / maxHeight) * maxGraphHeight;
        const interestHeight = totalHeight - contributionHeight;

        const xPosition = index * 10 - (data.length * 5);

        // Barra de aportes
        const contributionGeometry = new THREE.BoxGeometry(5, contributionHeight, 5);
        const contributionMaterial = new THREE.MeshStandardMaterial({ color: 0x44aa88 });
        const contributionBar = new THREE.Mesh(contributionGeometry, contributionMaterial);
        contributionBar.position.set(xPosition, contributionHeight / 2 + 1, 0); // Desde la base
        contributionBar.castShadow = true;
        scene.add(contributionBar);

        // Barra de intereses
        const interestGeometry = new THREE.BoxGeometry(5, interestHeight, 5);
        const interestMaterial = new THREE.MeshStandardMaterial({ color: 0xff69b4 });
        const interestBar = new THREE.Mesh(interestGeometry, interestMaterial);
        interestBar.position.set(
            xPosition,
            contributionHeight + interestHeight / 2 + 1,
            0
        );
        interestBar.castShadow = true;
        scene.add(interestBar);

        // Agregar etiqueta al total
        agregarEtiqueta(
            xPosition,
            contributionHeight + interestHeight + 2,
            0,
            `$${item.totalCapital.toFixed(2)}`
        );
    });
}

// Leer valores del formulario y actualizar el gráfico
document.querySelector('form').addEventListener('submit', (event) => {
    event.preventDefault();

    const principal = parseFloat(document.getElementById('principal').value) || 0;
    const additionalInvestment = parseFloat(document.getElementById('additional_investment').value) || 0;
    const investmentPeriod = document.getElementById('investment_period').value;
    const time = parseFloat(document.getElementById('time').value) || 0;
    const timePeriod = document.getElementById('time_period').value;
    const rate = parseFloat(document.getElementById('rate').value) || 0;
    const ratePeriod = document.getElementById('rate_period').value;

    generarGrafico(principal, additionalInvestment, investmentPeriod, time, timePeriod, rate, ratePeriod);
});

// Animación
function animate() {
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}
animate();
