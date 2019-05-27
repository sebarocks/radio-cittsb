var socket = io.connect('http://' + document.domain + ':' + location.port);

let user_name = localStorage.getItem('userRadio')

if (!user_name) {
    window.location = '/'
}

function mostrarResultados(res){
    let tablaDestino = document.querySelector('table.resultados');
    // crea un resultado
    var newTr = document.createElement('tr');        
    var thumbTd = document.createElement('td');
    thumbTd.className='thumb';
    var thumbImg = document.createElement('img')
    thumbImg.className='thumb';

    res.items.forEach(item => {
        console.log(item);


        tablaDestino.appendChild(newTr)
    });
}


document.addEventListener('submit', function (e) {
    console.log('hola :D');
    e.preventDefault();
    let user_input = document.querySelector('input.message');

    fetch('http://' + document.domain + ':' + location.port + '/buscar?q='+user_input.value)
        .then( res => res.json())
        .then( obj => {
            mostrarResultados(obj)
        })
        .catch(console.log);   

});

document.querySelector('input.message').addEventListener('input', (e) => {
    let user_input = e.target.value;
    if(user_input){
        document.querySelector('input.btnBuscar').removeAttribute('disabled');
    }
    else {
        document.querySelector('input.btnBuscar').setAttribute('disabled',true);
    }
});

