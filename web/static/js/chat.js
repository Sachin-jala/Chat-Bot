const ws = new WebSocket(`ws://${window.location.host}/ws/chat`);
const chatbox = document.getElementById('chatbox');
const input = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

ws.onopen = () => {
  ws.send(JSON.stringify({user_id: 'default', use_rag: false}));
}

ws.onmessage = (event) => {
  const obj = JSON.parse(event.data);
  if (obj.type === 'delta') {
    appendAssistantChunk(obj.chunk.choices?.[0]?.delta?.content || '');
  } else if (obj.type === 'done') {
    finalizeAssistantChunk();
  }
}

let lastAssistantEl = null;
function appendAssistantChunk(text) {
  if (!lastAssistantEl) {
    lastAssistantEl = document.createElement('div');
    lastAssistantEl.className = 'assistant msg';
    chatbox.appendChild(lastAssistantEl);
  }
  lastAssistantEl.textContent += text;
  chatbox.scrollTop = chatbox.scrollHeight;
}

function finalizeAssistantChunk() {
  lastAssistantEl = null;
}

sendBtn.onclick = () => {
  const text = input.value.trim();
  if (!text) return;
  const userEl = document.createElement('div');
  userEl.className = 'user msg';
  userEl.textContent = text;
  chatbox.appendChild(userEl);
  chatbox.scrollTop = chatbox.scrollHeight;
  ws.send(JSON.stringify({message: text}));
  input.value = '';
}

const uploadForm = document.getElementById('uploadForm');
uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = document.getElementById('fileInput').files[0];
  if (!f) return alert('Choose a file');
  const fd = new FormData();
  fd.append('file', f);
  const res = await fetch('/upload', {method: 'POST', body: fd});
  const j = await res.json();
  if (j.ok) alert('Uploaded: ' + j.filename + '. Run scripts/build_index.py to index it.');
});