// var socket = io('http://localhost');
var socket = io();
socket.on('commands', function (data) {
    var dict = JSON.parse(data['data']);
    var command = data['data'];
    console.log(data['data']);
    emitCommand(dict['val'], dict['dir'], dict['threshold']);
});
