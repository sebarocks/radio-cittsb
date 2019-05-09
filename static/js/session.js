var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/login'
}

function matchYoutubeUrl(url){
    //var p = /^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
    var d = /^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=|attribution_link\?a=.+?watch.+?v(?:%|=)))((\w|-){11})(?:\S+)?$/;

    url = (decodeURIComponent(url));
    return (url.match(d)) ? RegExp.$1 : false ;
}

function getDetails(videoID){
    fetch('http://' + document.domain + ':' + location.port + '/detalle?vid='+videoID)
        .then( res => res.json())
        .then( obj => {
            console.log(obj);
            cargarPreview(obj);
        })
        .catch(console.log);
}

function cargarPreview(obj){
    //limpia lo que hay
    let prevista = document.getElementById('preview');
    prevista.parentNode.removeChild(prevista);

    var premensaje = document.createElement('tr');
    nuevomensaje.innerHTML = '<td>' + msg.title + '</td> <td><img class="thumb" src="' + msg.thumbnail + '"></td>';
    document.querySelector('table.mensajes').appendChild(nuevomensaje);
    prevista.appendChild(premensaje);
}

// Connect
socket.on('connect', function () {
    // Notificar online

    document.querySelector('input.message').oninput((e) => {
        let user_input = e.target.value;
        let videoIdMatch = matchYoutubeUrl(user_input);
        if(videoIdMatch){
            fetch('http://' + document.domain + ':' + location.port + '/detalle'+user_input)
                .then( res => res.json())
                .then( myjson => {

                })
        }
    })
    
    document.addEventListener('submit', function (e) {
        e.preventDefault()
        let user_input = document.querySelector('input.message').value;
        let videoIdMatch = matchYoutubeUrl(user_input);

        if(!videoIdMatch){
            fetch('http://' + document.domain + ':' + location.port + '/detalle'+user_input)
        }
        socket.emit('mensaje', {
            username: user_name,
            videoid: user_input
        })

        user_input.value = '';
    })
})

// my response
socket.on('addedVideo', function (msg) {
    console.log('added:');
    console.log(msg);
    if (typeof msg.videoid !== "undefined") {

        var nuevomensaje = document.createElement('tr');
        nuevomensaje.innerHTML = '<td class="msg-user">' + msg.user + ':</td><td>' + msg.title + '</td> <td><img class="thumb" src="' + msg.thumbnail + '"></td>';
        nuevomensaje.id = 'v_'+msg.id;
        document.querySelector('table.mensajes').appendChild(nuevomensaje);
    }
})

socket.on('removedVideo', function (msg) {
    console.log('Removed');
    console.log(msg);
    var videoRow = document.getElementById('v_'+msg);
    videoRow.parentNode.removeChild(videoRow);
})

socket.on('signin', function (msg){
    console.log(msg);
})

socket.on('info', function (msg) {
    console.log(msg)
})