from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.request
import secrets
import json




### APP ###

app = Flask(__name__)
app.config['CONFIG_KEY'] = secrets.appKey
youtubeKey = secrets.youtubeKey
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(),'radio.db')
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
    activo = db.Column(db.Boolean, nullable=False)
    videos = db.relationship('Player', backref='video', lazy=True)

    def __repr__(self):
        return '<Video %r>' % self.videoid

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video_time = db.Column(db.Integer)

     def __repr__(self):
        return '<Player %r %r>' % self.video_id, self.video_time

db.create_all()

### DATOS INICIALES ###

if Video.query.first() is None:
    crab_rave = Video(videoid='iM_s0yoMepw'
    )

if Player.query.first() is None:
    player = Player(video_id)

# crea user autoplay si no existe
if User.query.filter_by(username='autoplay').first() is None:
    user_autoplay = User(username='autoplay')
    db.session.add(user_autoplay)
    db.session.commit()



### FUNCIONES ###

def playlist():
    return Video.query.filter_by(activo=True)

def historial():
    return Video.query.filter_by(activo=False)

def nextVideo():
    actual = playlist().first()
    actual.activo=False
    db.session.commit()
    return playlist.first()

def detalle(vidID):
    dataUrl = 'https://www.googleapis.com/youtube/v3/videos?id={}&key={}&fields=items(id,snippet(channelTitle,title,thumbnails))&part=snippet'.format(vidID,youtubeKey)
    vidInfo = urllib.request.urlopen(dataUrl) #.decode('utf-8')
    det = json.load(vidInfo)
    return det['items'][0]


# Agrega un video a la base de datos (tabla video)
def agregarVideo(user,videoID):
    #print('agregarVideo('+user+','+videoID+')')

    det = detalle(videoID)
    titulo = det['snippet']['title']
    miniatura = det['snippet']['thumbnails']['high']['url']

    user_actual = User.query.filter_by(username=user).first()

    if user_actual is None:
        user_actual = User(username=user)

    nuevoVideo= Video(videoid=videoID, title=titulo, thumbnail=miniatura, user=user_actual, activo=True)
    db.session.add(nuevoVideo)
    db.session.commit()
    return nuevoVideo


# Obtiene el objeto User desde la base de datos (si usuario no existe, lo agrega)
def signin(nombre):
    user_actual = User.query.filter_by(username=nombre).first()
    
    if user_actual is None:
        user_actual = User(username=nombre)
        db.session.add(user_actual)
        db.session.commit()
        print('    {} se registro'.format(user_actual.username))
    
    return user_actual


# Retorna un array con Video IDs relacionados (la API key afecta el resultado)
def videoRelated(videoID):
    dataUrl = 'https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId={}&type=video&key={}'.format(videoID,secrets.youtubeKey)
    vidInfo = urllib.request.urlopen(dataUrl)
    det = json.load(vidInfo)
    vids = []
    for item in det['items']:
        vids.append(item['id']['videoId'])
    return vids





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
    playlist = Video.query.filter_by(activo=True)
    return render_template('index.html',videos=playlist)

@app.route('/player')
def player():
    vid_actual = Video.query.filter_by(activo=True).first()
    if vid_actual is None:
        return render_template('player.html',videoinicial='iM_s0yoMepw')
    return render_template('player.html',videoinicial=vid_actual.videoid)






### EVENTOS ###

@socketio.on('mensaje')
def messageRecieved(data, methods=['GET','POST']):
    newVid = agregarVideo(data['username'], data['videoid'])
    respuesta = dict(id=newVid.id, user=newVid.user.username, videoid=newVid.videoid, title=newVid.title, thumbnail=newVid.thumbnail)
    socketio.emit('addedVideo',respuesta)
    print('    {} agrego video {}'.format(newVid.user.username,newVid.videoid))

@socketio.on('siguiente')
def siguiente(videoIdActual):
    print('siguiente('+videoIdActual+')')
    
    vid_actual = Video.query.filter_by(videoid=videoIdActual,activo=True).first()
    newVid = None

    if(vid_actual is not None):
        vid_actual.activo = False
        db.session.commit()
        socketio.emit('removedVideo',vid_actual.id)
        newVid = Video.query.filter_by(activo=True).first()

    if(newVid is None):
        newVid = agregarVideo('autoplay',videoRelated(videoIdActual)[3]) # elije el 3, mejor que sea random
        socketio.emit('addedVideo',dict(id=newVid.id, user=newVid.user.username, videoid=newVid.videoid, title=newVid.title, thumbnail=newVid.thumbnail))
    
    respuesta = newVid.videoid
    socketio.emit('playVideo',respuesta)

@socketio.on('playerout')
def playerDisconnect(info):
    playerstate = Player.query.first()
    playerstate

if __name__ == '__main__':
    socketio.run(app, debug=True)
    