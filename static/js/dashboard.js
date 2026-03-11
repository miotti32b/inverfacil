document.addEventListener('DOMContentLoaded', () => {

  // --- 1. LÓGICA DE REFERIDOS ---
  const btnCopiar = document.getElementById('copiar-link-ref');
  if (btnCopiar) {
    btnCopiar.addEventListener('click', async function () {
      const input = document.getElementById('referral-hidden');
      const link = input.value;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(link);
        } else {
          input.select();
          document.execCommand('copy');
          input.blur();
        }
        btnCopiar.textContent = "¡Copiado!";
        setTimeout(() => { btnCopiar.textContent = "Copiar mi link"; }, 2000);
      } catch (e) {
        alert("No se pudo copiar automáticamente. Copiá este link:\n" + link);
      }
    });
  }

  // --- 2. LÓGICA DEL ORÁCULO (CHATBOT) ---
  const chatModal = document.getElementById('chatModal');
  const chatForm = document.getElementById('chat-form');
  const chatBox = document.getElementById('chat-box');
  const userInput = document.getElementById('user-input');
  const typing = document.getElementById('typing');

  // Función para cerrar si hacen clic afuera
  window.onclick = function(event) {
    if (event.target == chatModal) {
      cerrarChat();
    }
  }

  // Token CSRF de Django
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = userInput.value.trim();
      if (!text) return;

      // Lee la URL de Django escondida en el form
      const urlFetch = chatForm.getAttribute('data-url');
      const csrftoken = getCookie('csrftoken');

      chatBox.innerHTML += `<div class="msg user">${text}</div>`;
      userInput.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;
      typing.style.display = 'block';

      try {
        const response = await fetch(urlFetch, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify({ message: text })
        });
        
        const data = await response.json();
        
        typing.style.display = 'none';
        chatBox.innerHTML += `<div class="msg bot">${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

      } catch (error) {
        typing.style.display = 'none';
        chatBox.innerHTML += `<div class="msg bot" style="color:red;">El yate se quedó sin WiFi.</div>`;
      }
    });
  }
});

// Funciones globales para abrir y cerrar el modal desde el HTML
function abrirChat() {
  document.getElementById('chatModal').style.display = 'flex';
}
function cerrarChat() {
  document.getElementById('chatModal').style.display = 'none';
}