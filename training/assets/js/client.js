// var socket = io('http://localhost');
var socket = io();
socket.on('commands', function (data) {
    var dict = JSON.parse(data['data']);
    
    var event = dict['event'],
        val = dict['val'],
        dir = dict['dir'],
        threshold = dict['threshold'],
        accuracy = dict['accuracy'];

    emitCommand(event, val, dir, threshold, accuracy);

});
