var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/login'
}

popPreview();

function matchYoutubeUrl(url){

    var d = /^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$/;

    url = (decodeURIComponent(url));
    return (url.match(d)) ? RegExp.$5 : false ;
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

function popPreview(){
    let prevista = document.querySelector('table.prevista');
    while(prevista.firstChild){
        prevista.removeChild(prevista.firstChild);
    }
    document.querySelector('form').reset();
}

function cargarPreview(obj){
    //limpia lo que hay
    let prevista = document.querySelector('table.prevista');
    while(prevista.firstChild){
        prevista.removeChild(prevista.firstChild);
    }

    let previewRow = document.createElement('tr');
    previewRow.innerHTML = '<td>' + obj.titulo + '</td> <td><img class="thumb" src="' + obj.miniatura + '"></td>';
    document.querySelector('table.prevista').appendChild(previewRow);
}

// Connect
socket.on('connect', function () {
    // Notificar online

    document.querySelector('input.message').addEventListener('input', (e) => {
        let user_input = e.target.value;
        let videoIdMatch = matchYoutubeUrl(user_input)
        if(videoIdMatch){
            getDetails(videoIdMatch);
            document.querySelector('input.btnEnviar').removeAttribute('disabled');
        }
        else {
            document.querySelector('input.btnEnviar').setAttribute('disabled',true);
        }
    })
    
    document.addEventListener('submit', function (e) {
        e.preventDefault()
        let user_input = document.querySelector('input.message').value;

        socket.emit('mensaje', {
            username: user_name,
            videoid: matchYoutubeUrl(user_input)
        });

        console.log('enviado'+user_input);
        popPreview();
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
    console.log('Removed '+msg);
    popVideo(msg);
})

socket.on('signin', function (msg){
    console.log(msg);
})

socket.on('info', function (msg) {
    console.log(msg)
})

function popVideo(msg){
    var videoRow = document.getElementById('v_'+msg);
    videoRow.parentNode.removeChild(videoRow);
}