from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os


### APP ###ph

app = Flask(__name__)
app.config['CONFIG_KEY'] = 'vnkdjnfjknfl1232'
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.getcwd() + '\\radio.db'
db = SQLAlchemy(app)


### MODELO ###

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    online = db.Column(db.Boolean,nullable=False)
    videos = db.relationship('Video', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    videoid = db.Column(db.String(16))
    name = db.Column(db.String(100))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Video %r>' % self.videoid

db.create_all()


def datosTest():    
    # DATOS PRUEBAS
    db.session.add(Video(videoid='LDU_Txk06tM', name='crab rave', user=User(username='seba', online=True), activo=True))
    db.session.commit()


### RUTAS ###

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        socketio.emit('login',)
        return redirect(url_for('sessions'))
    else:
        return redirect(url_for('index'))

@app.route('/session')
def sessions():
    playlist = Video.query.all()
    return render_template('session.html',videos=playlist)

@app.route('/player')
def player():
    return render_template('player.html')



### EVENTOS ###

@socketio.on('mensaje')
def messageRecieved(json, methods=['GET','POST']):
    #print('message was recieved!! '+str(json))
    socketio.emit('info','info:'+str(json))
    socketio.emit('mensaje',json)
    
    db.session.add(Video(videoid=json['message'], name='crab rave', user=User(username=json['username'], online=True), activo=True))
    db.session.commit()



if __name__ == '__main__':
    socketio.run(app, debug=True)
    