var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/'
}

var tempResults = new Array();

function generarTr(v_id, srcThumb, title, autor) {
    let newTr = document.createElement('tr');
    newTr.id = v_id;

    let thumbTd = document.createElement('td');
    thumbTd.className = 'thumb';
    let thumbImg = document.createElement('img')
    thumbImg.className = 'thumb';
    thumbImg.src = srcThumb;

    let infoTd = document.createElement('td');
    let tituloVid = document.createElement('p');
    tituloVid.className = 'tituloVid';
    tituloVid.textContent = htmlDecode(title);
    let autorVid = document.createElement('p');
    autorVid.className = 'autorVid';
    autorVid.textContent = autor;

    let addTd = document.createElement('td');
    let addBtn = document.createElement('button');
    addBtn.className='btn';
    addBtn.textContent = 'Agregar Video';
    addBtn.onclick = agregarVideo;

    thumbTd.appendChild(thumbImg);
    newTr.appendChild(thumbTd);

    infoTd.appendChild(tituloVid);
    infoTd.appendChild(autorVid);
    newTr.appendChild(infoTd);

    addTd.appendChild(addBtn);
    newTr.appendChild(addTd);

    return newTr;
}

function htmlDecode(input)
{
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}

function agregarVideo(e){
    var idObtenido = e.target.parentNode.parentNode.id;
    e.target.style.backgroudColor='#dd715f';
    socket.emit('mensaje', {
        username: user_name,
        videoid: idObtenido
    });
    console.log(idObtenido);
}

function mostrarResultados(res) {
    let tablaDestino = document.querySelector('table.resultados');
    //limpia tabla
    while (tablaDestino.firstChild) {
        tablaDestino.removeChild(tablaDestino.firstChild);
    }
    tempResults.length = 0;

    res.items.forEach(item => {
        tempResults.push(item);
        console.log(item);
        if (item.id.kind == 'youtube#video') {
            let nuevaFila = generarTr(item.id.videoId, item.snippet.thumbnails.default.url, item.snippet.title, item.snippet.channelTitle);
            tablaDestino.appendChild(nuevaFila);
        }
    });
}

document.addEventListener('submit', function (e) {
    e.preventDefault();
    let user_input = document.querySelector('input.message');

    fetch('http://' + document.domain + ':' + location.port + '/buscar?q=' + user_input.value)
        .then(res => res.json())
        .then(obj => {
            //console.log(obj);
            mostrarResultados(obj)
        })
        .catch(console.log);

});

document.querySelector('input.message').addEventListener('input', (e) => {
    let user_input = e.target.value;
    if (user_input) {
        document.querySelector('input.btnBuscar').removeAttribute('disabled');
    } else {
        document.querySelector('input.btnBuscar').setAttribute('disabled', true);
    }
});
