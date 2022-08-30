from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send, join_room, leave_room

app = Flask(__name__) # create the flask app
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins='*')
ROOMS = ['main', 'help', 'fun', 'study']

@app.route('/')
def index():
    return render_template('index.html', rooms=ROOMS) # return the html page for the chatroom


@socketio.on('message') # event handler for sending a message
def message(data):
    send({'username' : data['username'], 'msg': data['msg']}, room=data['room'], broadcast=True)
    # the username and message will be broadcasted to everyone in the same room as the user

@socketio.on('newroom') # event handler for creating a new room
def newroom(data):
    ROOMS.append(data['new']) # take the name of the new room and append it to the list of rooms

@socketio.on('join') # event handler for joining a new room
def join(data):
    join_room(data['room']) # join the room
    send({'msg': data['username'] + ' has joined the ' + data['room']
    + ' room.'}, room=data['room']) # send a message to everyone in the room that the user has joined

@socketio.on('leave') # event handler for leaving a room
def leave(data):
    leave_room(data['room']) # leave the room
    send({'msg': data['username'] + ' has left the ' + data['room']
    + ' room.'}, room=data['room']) # send out a message to everyone still in the room that the user has left

if __name__ == '__main__':
    socketio.run(app, debug=True) # run the app
