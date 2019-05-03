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
        videoId: 'LDU_Txk06tM',
        autoplay: 0,
        events: {
            'onReady': onPlayerReady,
            'onStateChange' : onStateChange
        }
    });
}

// The API will call this function when the video player is ready.
function onPlayerReady(event) {
    event.target.stopVideo();
}

function onStateChange(event) {
    switch(event.data){
        case YT.PlayerState.ENDED:
            socket.emit('siguiente');
            console.log('siguiente!!');
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
socket.on('nuevoVideo', function (msg) {
    console.log(msg)
    if (typeof msg.videoid !== "undefined") {
        if(player.getPlayerState() == 2 || player.getPlayerState() == -1){
            socket.emit('siguiente');
        }
        // AUN NO HAY TAblA
        //var nuevomensaje = document.createElement('tr')
        // Agrega a tabla playlist
        //nuevomensaje.innerHTML = '<td class="msg-user">' + msg.user + ':</td><td>' + msg.title + '</td> <td><img class="thumb" src="' + msg.thumbnail + '"></td>'
        //document.querySelector('table.mensajes').appendChild(nuevomensaje)
    }    
})

socket.on('playVideo', function (msg) {
    console.log('musica tito: '+msg)
    if (typeof msg !== "undefined") {

        player.loadVideoById(msg)
    }    
})


socket.on('signin', function (msg){
    console.log("se registro"+msg);
})

socket.on('info', function (msg) {
    console.log(msg)
})