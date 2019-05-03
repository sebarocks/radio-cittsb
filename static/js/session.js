var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/'
}

// Connect
socket.on('connect', function () {

    // OBTENER LISTA DE VIDEOS

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
socket.on('nuevoVideo', function (msg) {
    if (typeof msg.videoid !== "undefined") {

        var nuevomensaje = document.createElement('tr')
        nuevomensaje.innerHTML = '<td class="msg-user">' + msg.title + ':</td> <td>' + msg.videoid + '</td> <td>' + msg.thumbnail + '</td>'
        document.querySelector('table.mensajes').appendChild(nuevomensaje)
    }
})

socket.on('info', function (msg) {
    console.log(msg)
})