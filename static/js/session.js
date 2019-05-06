var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/login'
}

// Connect
socket.on('connect', function () {
    // Notificar online

    // ENVIAR URL
    document.addEventListener('submit', function (e) {
        e.preventDefault()
        let user_input = document.querySelector('input.message').value;

        socket.emit('mensaje', {
            username: user_name,
            videoid: user_input
        })

        user_input.value = '';
    })
})

// my response
socket.on('addedVideo', function (msg) {
    console.log(msg)
    if (typeof msg.videoid !== "undefined") {

        var nuevomensaje = document.createElement('tr')
        nuevomensaje.id = msg.id
        // MENSAJE
        nuevomensaje.innerHTML = '<td class="msg-user">' + msg.user + ':</td><td>' + msg.title + '</td> <td><img class="thumb" src="' + msg.thumbnail + '"></td>'
        document.querySelector('table.mensajes').appendChild(nuevomensaje)
    }
})

socket.on('removedVideo', function (msg) {
    var videoRow = document.getElementById(msg);
    videoRow.parentNode.removeChild(videoRow);
})

socket.on('signin', function (msg){
    console.log(msg);
})

socket.on('info', function (msg) {
    console.log(msg)
})