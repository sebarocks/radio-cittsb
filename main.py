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

    def __repr__(self):
        return '<Video %r>' % self.videoid

db.create_all()






### FUNCIONES ###

def detalle(vidID):
    dataUrl = 'https://www.googleapis.com/youtube/v3/videos?id={}&key={}&fields=items(id,snippet(channelTitle,title,thumbnails))&part=snippet'.format(vidID,youtubeKey)
    vidInfo = urllib.request.urlopen(dataUrl) #.decode('utf-8')
    det = json.load(vidInfo)
    return det['items'][0]


# Agrega un video a la base de datos (tabla video)
def agregarVideo(user,videoID):

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
    dataUrl = 'https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId=5rOiW_xY-kc&type=video&key={}'.format(secrets.youtubeKey)
    vidInfo = urllib.request.urlopen(dataUrl)
    det = json.load(vidInfo)
    vids = []
    for item in det['items']:
        vids.append(item['id']['videoId'])
    return vids





### RUTAS ###

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        user = signin(nombre)
        socketio.emit('signin',dict(id=user.id, name=user.username))
        return redirect(url_for('sessions'))
    else:
        return redirect(url_for('index'))

@app.route('/session')
def sessions():
    playlist = Video.query.filter_by(activo=True)
    return render_template('session.html',videos=playlist)

@app.route('/player')
def player():
    return render_template('player.html')






### EVENTOS ###

@socketio.on('mensaje')
def messageRecieved(data, methods=['GET','POST']):
    newVid = agregarVideo(data['username'], data['videoid'])
    respuesta = dict(user=newVid.user.username, videoid=newVid.videoid, title=newVid.title, thumbnail=newVid.thumbnail)
    socketio.emit('nuevoVideo',respuesta)
    print('    {} agrego video {}'.format(newVid.user.username,newVid.videoid))

@socketio.on('siguiente')
def siguiente():
    vid_actual = Video.query.filter_by(activo=True).first()
    if(vid_actual is not None):
        vid_actual.activo = False
        db.session.update()
        db.session.commit()
        newVid = Video.query.filter_by(activo=True).first()
    else:
        newVid = agregarVideo(videoRelated(???)) #siguiente necesita video id de actual en player
    
    respuesta = newVid.videoid
    socketio.emit('playVideo',respuesta)

if __name__ == '__main__':
    socketio.run(app, debug=True)
    