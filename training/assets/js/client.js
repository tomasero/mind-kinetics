var socket = io('http://localhost');
socket.on('commands', function (data) {
    var dict = JSON.parse(data['data']);
    var command = data['data'];
    console.log(data['data']);
    armUp(dict['dir']);
});