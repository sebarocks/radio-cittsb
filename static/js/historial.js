var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

socket.on('addedVideo', function (msg) {
    console.log(msg)
    if (typeof msg.videoid !== "undefined") {

        var nuevomensaje = document.createElement('tr');
        nuevomensaje.innerHTML = '<td class="msg-user">' + msg.user + ':</td><td>' + msg.title + '</td> <td class="thumb"><img class="thumb" src="' + msg.thumbnail + '"><td></td></td>';
        nuevomensaje.id = 'v_' + msg.id;
        document.querySelector('table.mensajes').appendChild(nuevomensaje);
    }
})

// revivir video lo popea. Estara bien asi?
socket.on('revivirVideo', function (msg) {
    var videoRow = document.getElementById('v_' + msg);
    videoRow.parentNode.removeChild(videoRow);
})

document.querySelectorAll('.revivir').forEach(b => {
    b.addEventListener('click', event => {
        var idpadre = event.target.parentNode.parentNode.id;
        console.log('idpadre: '+idpadre);
        socket.emit('revivirVideo', idpadre);
    })
});