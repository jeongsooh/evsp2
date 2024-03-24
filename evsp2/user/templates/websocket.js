const socket = new WebSocket(
    'ws://127.0.0.1:8000/ws/ocpp/'
);

socket.addEventListener('open', function(event) {
    console.log('Connected to the WebSocket.');
    socket.send('Hello Server!');
});

socket.addEventListener('message', function(event) {
    console.log('Message received: ', event.data);
});

socket.addEventListener('close', function(event) {
    console.log('WebSocket connection closed: ', event.code, event.reason);
});

socket.addEventListener('error', function(event) {
    console.log('WebSocket error: ', event);
});