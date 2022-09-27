import socketio
import requests
import os
import random
import string

JOIN_EVERYTHING = True
SAVE_PATH = './downloads/'


# Do not change anything below this line
#
#


sio = socketio.Client()

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@sio.event
def connect():
    print('connection established')
    sio.call('get-ads')
    sio.call('create-user',get_random_string(16))
    channels = sio.call('get-channels')
    if JOIN_EVERYTHING:
        for channel in channels["channels"]:
            if channel["name"] == "FOR ADULTS":
                for room in channel["rooms"]:
                    name = room["name"]
                    sub_rooms = join_room(name)
                    join_everything(sub_rooms)
    else:
        sub_rooms = join_room("15min")
        join_everything(sub_rooms)

@sio.event
def media(data):
    if data['type'] == 'gallery':
        join_room(data['name'])
    else:
        download(data)


@sio.event
def connect_error(message):
        print('Connection was rejected due to ' + message)

@sio.event
def disconnect():
    print(f'disconnected from server: ')

def join_everything(data):
    for room in data['room']['childRooms']:
        if not room['isProtected']:
            join_room(room['name'])

def join_room(name):
    print(f'joining {name}')
    return sio.call('join',{"roomName":name,"parentRoomName":None},timeout=120)

def download(data):
    filename = data["filename"]
    print(f'downloading {data["filename"]}')
    response = requests.get(f'https://chatpic.org/media/{data["filename"]}')
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    with open(f'{SAVE_PATH}{data["filename"]}', 'wb') as f:
        f.write(response.content)

sio.connect('https://chatpic.org/socket.io/')
sio.wait()
