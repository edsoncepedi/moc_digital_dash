const notificationsDiv = document.getElementById('notifications');
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function (event) {
    console.log("Mensagem recebida:", event.data);
    const notification = document.createElement('div');
    notification.classList.add('notification');

    const message = document.createElement('p');
    message.textContent = `🔔 ${event.data}`;

    const closeButton = document.createElement('button');
    closeButton.classList.add('close-btn');
    closeButton.innerHTML = '&times;';
    
    // Fechar notificação ao clicar no botão
    closeButton.onclick = () => {
        notification.style.animation = 'fadeOut 0.5s ease-in-out';
        setTimeout(() => notification.remove(), 500);
    };

    notification.appendChild(message);
    notification.appendChild(closeButton);
    notificationsDiv.appendChild(notification);

    // Rolar automaticamente para a última notificação
    notificationsDiv.scrollTop = notificationsDiv.scrollHeight;
};

ws.onopen = function () {
    console.log("Conectado ao WebSocket");
};

ws.onclose = function () {
    console.log("Desconectado do WebSocket");
};