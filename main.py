from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os, random, json, urllib.request, secret


### APP ###

app = Flask(__name__)
app.config['CONFIG_KEY'] = secret.appKey
youtubeKey = secret.youtubeKey
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(),'radio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)








### MODELO ###

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    #online = db.Column(db.Boolean,nullable=False)
    videos = db.relationship('Video', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    videoid = db.Column(db.String(16))
    title = db.Column(db.String(80))
    thumbnail = db.Column(db.String(60))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False) # en cola
    videos = db.relationship('Player', backref='video', lazy=True)

    def __repr__(self):
        return '<Video %r>' % self.videoid

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video_time = db.Column(db.Integer)

    def __repr__(self):
        return '<Player %r %r>' % (self.video_id, self.video_time)

with app.app_context():
    db.create_all()











### FUNCIONES ###


def getAutoplayUser():
    autoplay = User.query.filter_by(username='autoplay').first()
    if autoplay is None:
        autoplay = User(username='autoplay')
        db.session.add(autoplay)
        db.session.commit()
    return autoplay


def playlist():
    return Video.query.filter_by(activo=True)


def getHistorial():
    return Video.query.filter_by(activo=False)

def currentVideo():
    return playlist().first()

def currentState():
    return Player.query.first()

def savePlayer(vid):
    player_now = currentState()
    player_now.video_id= Video.query.filter_by(videoid=vid).first().videoid
    player_now.video_time = 0
    db.session.commit()

def detalle(vidID): #que pasa si es 404?
    dataUrl = 'https://www.googleapis.com/youtube/v3/videos?id={}&key={}&fields=items(id,snippet(channelTitle,title,thumbnails(default)))&part=snippet'.format(vidID,youtubeKey)
    print('REQUEST > '+dataUrl)
    vidInfo = urllib.request.urlopen(dataUrl) #.decode('utf-8')
    det = json.load(vidInfo)
    return det['items'][0]


# Agrega un video a la base de datos (tabla video)
def agregarVideo(user,videoID):

    det = detalle(videoID)
    titulo = det['snippet']['title']
    miniatura = det['snippet']['thumbnails']['default']['url']

    user_actual = User.query.filter_by(username=user).first()

    if user_actual is None:
        user_actual = User(username=user)

    nuevoVideo= Video(videoid=videoID, title=titulo, thumbnail=miniatura, user=user_actual, activo=True)
    db.session.add(nuevoVideo)
    db.session.commit()
    return nuevoVideo

def revivir(user, vIdDb):
    muerto = Video.query.filter_by(id=vIdDb).first()
    det = detalle(muerto.videoid)
    r_titulo = det['snippet']['title']
    r_thumb = det['snippet']['thumbnails']['default']['url']
    renacido = Video(videoid=muerto.videoid, title=r_titulo, thumbnail=r_thumb,activo=True)
    db.session.add(renacido)
    db.session.commit()
    socketio.emit('addedvideo',renacido.__dict__)

# Obtiene el objeto User desde la base de datos (si usuario no existe, lo agrega)
def signin(nombre):
    user_actual = User.query.filter_by(username=nombre).first()
    
    if user_actual is None:
        user_actual = User(username=nombre)
        db.session.add(user_actual)
        db.session.commit()
    
    return user_actual


# Retorna un array con Video IDs relacionados (la API key afecta el resultado)
def videosRelated(videoID):
    dataUrl = 'https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId={}&type=video&key={}&fields=items(id)'.format(videoID,secret.youtubeKey)
    print('REQUEST > '+dataUrl)
    vidInfo = urllib.request.urlopen(dataUrl)
    det = json.load(vidInfo)
    vids = []
    for item in det['items']:
        vids.append(item['id']['videoId'])
    return vids







### DATOS INICIALES ###

with app.app_context():
    user_autoplay = getAutoplayUser()
    if Player.query.first() is None:
        id_inicial ='-oCPAO3bp4Q'
        det = detalle(id_inicial)
        vid_inicial = Video(videoid=id_inicial,title=det['snippet']['title'], thumbnail = det['snippet']['thumbnails']['default']['url'], user=user_autoplay, activo=True)
        playerState = Player(video=vid_inicial, video_time='0')
        
        db.session.add(vid_inicial)
        db.session.add(playerState)
        db.session.commit()








### RUTAS ###


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        user = signin(nombre)
        socketio.emit('signin',dict(id=user.id, name=user.username))
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html',videos=playlist())

@app.route('/player')
def player():
    playernow=currentState()
    return render_template('player.html',vid_actual=playernow.video.videoid, time_actual=playernow.video_time, videos=playlist())

@app.route('/historial')
def historial():
    return render_template('historial.html', videos=getHistorial()) 

@app.route('/detalle')
def details():
    iddetalle=request.args['vid']
    det = detalle(iddetalle)
    r_titulo = det['snippet']['title']
    r_thumb = det['snippet']['thumbnails']['default']['url']
    return jsonify(dict(titulo=r_titulo,miniatura=r_thumb))

@app.route('/search')
def buscador():
    return render_template('buscador.html')

@app.route('/buscar')
def buscar():
    
    termino = request.args.get('q')
    termino = urllib.parse.quote_plus(termino)
    dataUrl = 'https://www.googleapis.com/youtube/v3/search?part=snippet&kind=video&maxResults=10&q={}&key={}&fields=items(id,snippet(channelTitle,title,thumbnails(default)))'.format(termino,secret.youtubeKey)
    vidInfo = urllib.request.urlopen(dataUrl)
    datos = json.load(vidInfo)
    print('REQUEST > '+dataUrl)    
    return jsonify(datos)



### EVENTOS ###

@socketio.on('mensaje')
def messageRecieved(data, methods=['GET','POST']):
    newVid = agregarVideo(data['username'], data['videoid'])
    respuesta = dict(id=newVid.id, user=newVid.user.username, videoid=newVid.videoid, title=newVid.title, thumbnail=newVid.thumbnail)
    socketio.emit('addedVideo',respuesta)

@socketio.on('siguiente')
def siguiente(videoIdActual):
    
    vid_actual = Video.query.filter_by(videoid=videoIdActual,activo=True).first()
    newVid = None

    if(vid_actual is not None):
        vid_actual.activo = False
        db.session.commit()
        socketio.emit('removedVideo',vid_actual.id)
        newVid = Video.query.filter_by(activo=True).first()

    if(newVid is None):
        choice = random.choice(videosRelated(videoIdActual))
        newVid = agregarVideo('autoplay',choice)
        socketio.emit('addedVideo',dict(id=newVid.id, user=newVid.user.username, videoid=newVid.videoid, title=newVid.title, thumbnail=newVid.thumbnail))
    
    respuesta = newVid.videoid
    socketio.emit('playVideo',respuesta)
    savePlayer(newVid.videoid)

@socketio.on('playerout')
def playerDisconnect(info):
    playerstate = currentState()
    playerstate.video = currentVideo()
    playerstate.video_time = int(info['time'])
    db.session.commit()

@socketio.on('removeVideo')
def removeVideo(info):
    vid_to_remove = Video.query.filter_by(videoid=info).first()
    if(vid_to_remove is not None):
        vid_to_remove.activo = False
        db.session.commit()
        socketio.emit('removedVideo',info)



if __name__ == '__main__':
    socketio.run(app)
    
