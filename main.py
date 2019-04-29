from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['CONFIG_KEY'] = 'vnkdjnfjknfl1232'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('session.html')

def messageRecieved(methods=['GET','POST']):
    print('message was recieved!!')

@socketio.on('my event')
def handle_my_event(json, methods=['GET','POST']):
    print('Recieved (My event): '+str(json))
    socketio.emit('my response', json, callback=messageRecieved)

@app.route('/player')
def player():
    return render_template('player.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
    