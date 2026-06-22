function appendMessage(type, html) {
    const box = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = type === 'user' ? 'user-message' : 'bot-message';
    div.innerHTML = html;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function sendChatMessage(message) {
    appendMessage('user', `<strong>You:</strong> ${message}`);
    const formData = new FormData();
    formData.append('message', message);
    fetch('/api/chatbot/', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            appendMessage('bot', `<strong>Assistant:</strong> ${data.reply}<br><small><strong>Suggested category:</strong> ${data.category}<br>${data.next_step}</small>`);
        })
        .catch(() => appendMessage('bot', '<strong>Assistant:</strong> Sorry, I could not process that request right now.'));
}

function quickAsk(message) {
    document.getElementById('chatInput').value = message;
    sendChatMessage(message);
    document.getElementById('chatInput').value = '';
}

const chatForm = document.getElementById('chatForm');
if (chatForm) {
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (message) {
            sendChatMessage(message);
            input.value = '';
        }
    });
}
