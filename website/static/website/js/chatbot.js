const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatBox = document.getElementById('chatBox');
const suggestions = document.querySelectorAll('.suggestion');

function addMessage(text, type) {
  const div = document.createElement('div');
  div.className = type === 'user' ? 'user-message' : 'bot-message';
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(message) {
  addMessage(message, 'user');
  chatInput.value = '';
  try {
    const response = await fetch('/api/chatbot/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await response.json();
    addMessage(data.reply || 'Sorry, I could not process that question.', 'bot');
  } catch (error) {
    addMessage('The assistant is currently unavailable. Please try again later.', 'bot');
  }
}

if (chatForm) {
  chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (message) sendMessage(message);
  });
}

suggestions.forEach((button) => {
  button.addEventListener('click', () => sendMessage(button.dataset.question));
});
