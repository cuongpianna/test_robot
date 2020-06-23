from flask import Flask, render_template, url_for, copy_current_request_context
import random
import threading
import socket
from constant import UDP_IP_STATUS, UDP_PORT_STATUS, IP_SERVER
from flask_socketio import SocketIO
from flask_socketio import emit
from threading import Thread, Event
import requests
from tcping import Ping
import time
import os

__status =-1
sock_get_status = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock_get_status.bind((UDP_IP_STATUS, UDP_PORT_STATUS))

app = Flask(__name__)

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

thread = Thread()
thread_stop_event = Event()


def check_status():
    try:
        rq = requests.get(IP_SERVER, verify=False)
        if rq.status_code == 200:
            return True
        else:
            return False
    except:
        return False


def check_status2():
    ping = Ping(IP_SERVER)
    try:
        p = ping.ping(3)
        return True
    except:
        return False


def GET_STATUS():
    while True:
        print('!!!!!!!!!!!!!!')
        msg_robot_status, addr = sock_get_status.recvfrom(20)
        print('@@@@@@@')
        if addr[0] == UDP_IP_STATUS:
            if check_status():
                status = 1
            else:
                status = 0
            socketio.emit('newUdp', {'number': int(msg_robot_status), 'status': status})


def CHECK_CONNECTION():
    status = check_status()
    number = 1 if status else 0
    socketio.emit('tt', {'connection': number, 'udp': 0}, broadcast=True)


@app.route('/')
def index():
    status = True
    if status:
        classes = 'active'
    else:
        classes = 'deactive'
    return render_template('index.html', classes = classes)


@socketio.on('connect')
def test_connect():
    global thread
    print('Client connected')

    if not thread.isAlive():
        print("Starting Thread")
    thread = socketio.start_background_task(GET_STATUS)


@socketio.on('connection2')
def check_connect():
    print('Check connection!!!!!!')
    global __status
    print(__status)
    thread = socketio.start_background_task(CHECK_CONNECTION)
@socketio.on('status')
def check_connect(sta):
    global __status
    __status =sta

@socketio.on('disconnect')
def test_check_disconnect():
    print('Client disconnected!!!!!!!')
    global __status
    __status =-1


if __name__ == '__main__':
    socketio.run(app)
