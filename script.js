const socket = io();
const editor = document.getElementById('editor');

editor.addEventListener('input', () => {
  socket.emit('text-change', editor.value);
});

socket.on('text-update', (data) => {
  editor.value = data;
});
