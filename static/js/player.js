//         //
// YOUTUBE //
//         //

//   This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

//    This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        width: '100%',
        videoId: video,
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onStateChange
        }
    });
}

// The API will call this function when the video player is ready.
function onPlayerReady(event) {
    event.target.playVideo();
    event.target.seekTo(startTime);

    var emitEstado = function () {
        estado = {
            vid: player.getVideoData().video_id,
            time: player.getCurrentTime()
        };
    
        socket.emit('playerout', estado);
    }
    window.setInterval(emitEstado, 8000);
}

function onStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {
        socket.emit('siguiente', player.getVideoData().video_id);
        console.log('pidiendo nueva cancion!');
    }
}


//        //
// SOCKET //
//        //

var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/'
}


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

        var nuevomensaje = document.createElement('tr');
        nuevomensaje.innerHTML = '<td class="msg-user">' + msg.user + ':</td><td>' 
                + msg.title + '</td> <td class="thumb"><img class="thumb" src="' 
                + msg.thumbnail + '"><td><button class="btn" id="borrar_' + msg.id
                + '" onclick=popVideo("' + msg.id + '")>Borrar</button></td></td>';
        nuevomensaje.id = 'v_' + msg.id;
        document.querySelector('table.mensajes').appendChild(nuevomensaje);
    }
})

socket.on('removedVideo', function (msg) {
    var videoRow = document.getElementById('v_' + msg);
    videoRow.parentNode.removeChild(videoRow);
})

socket.on('playVideo', function (msg) {
    if (typeof msg !== "undefined") {

        player.loadVideoById(msg)
    }
})

socket.on('info', function (msg) {
    console.log(msg)
})

function skip(){
    socket.emit('siguiente',player.getVideoData().video_id);
}

function popVideo(msg){
    if(msg==player.getVideoData().video_id){
        socket.emit('siguiente',player.getVideoData().video_id);
    }
    socket.emit('removeVideo',msg);
}
