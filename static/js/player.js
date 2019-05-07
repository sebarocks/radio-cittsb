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
        height: '360',
        width: '640',
        videoId: video,
        events: {
            'onReady': onPlayerReady,
            'onStateChange' : onStateChange
        }
    });
}

// The API will call this function when the video player is ready.
function onPlayerReady(event) {    
    event.target.playVideo();
    event.target.seekTo(startTime); 
       
}

function onStateChange(event) {
    if(event.data == YT.PlayerState.ENDED){
        socket.emit('siguiente',player.getVideoData().video_id);
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

        if(player.getPlayerState() == 5){
            console.log('addedvideo-state5');
            player.loadVideoById(msg.videoid);
            player.playVideo();
        } 

        // AUN NO HAY TAblA
        //var nuevomensaje = document.createElement('tr')
        // Agrega a tabla playlist
        //nuevomensaje.innerHTML = '<td class="msg-user">' + msg.user + ':</td><td>' + msg.title + '</td> <td><img class="thumb" src="' + msg.thumbnail + '"></td>'
        //document.querySelector('table.mensajes').appendChild(nuevomensaje)
    }    
})

socket.on('playVideo', function (msg) {
    console.log('musica tito! '+msg)
    if (typeof msg !== "undefined") {

        player.loadVideoById(msg)
    }    
})

socket.on('info', function (msg) {
    console.log(msg)
})

window.onbeforeunload = function(){
    estado = {vid:player.getVideoData().video_id, time:player.getCurrentTime()};
    socket.emit('playerout',estado);
}