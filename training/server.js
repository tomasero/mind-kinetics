//python to node

var PORT = 33333;
var HOST = '127.0.0.1';
var dgram = require('dgram');

var PYTHON_PORT = 10000;

// receiving messages from python
var server = dgram.createSocket('udp4');
var socket = null;

server.on('listening', function () {
    var address = server.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

server.on('message', function (message, remote) {
    console.log(remote.address + ':' + remote.port +' - ' + message);
    socket.emit('commands', { data: message.toString('utf-8') });
});

server.bind(PORT, HOST);


// sending messages to python
var client = dgram.createSocket("udp4");

function send_python_data(data) {
    var message = new Buffer(data);
    client.send(message, 0, message.length, PYTHON_PORT, HOST);
}

// serving files
var express = require('express');
var app = express();
var server = require('http').Server(app);
var io = require('socket.io')(server);

server.listen(3000);

app.use(express.static(__dirname + '/assets'));

app.get('/', function (req, res) {
    res.sendFile(__dirname + '/index.html');
});

// sending/receiving messages to/from web app
io.on('connection', function (soc) {
    console.log('connected');
    socket = soc;
    socket.on('backend', function(data) {
        send_python_data(JSON.stringify(data));
    });
});
