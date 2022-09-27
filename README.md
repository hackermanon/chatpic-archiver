Chatpic Archiver
================

- [Linux Setup](#linux-setup-instructions)
- [macOS Setup](#macos-setup-instructions)
- [Windows Setup](#windows-setup-instructions)
- [The script](#the-script)

For a prettier version of these instructions, click [here](https://htmlpreview.github.io/?https://github.com/hackermanon/chatpic-archiver/blob/main/web/chatpic-archive.xyz.html)


Linux setup instructions
========================

Instructions
------------

I assume you have basic knowledge about installing software with your package manager of choice and python virtual envs

Now you need to create a new virtual env

```
python3 -m venv chatpic
source ./venv/bin/activate

```

You now can install the requirements to run the archiver

```
pip install requests python-socketio "python-socketio[client]"

```

After you installed the dependencies, you can simply start [the archiver script](#script) with

```
python3 main.py

```

macOS Setup instructions
========================

Instructions
------------

I assume you have basic knowledge about installing software with `brew` and python virtual envs

You will need python virtualenv available on your mac. This can be installed with

```
brew install pyenv pyenv-virtualenv

```

Follow this [Installation instructions](https://github.com/pyenv/pyenv-virtualenv#installing-with-homebrew-for-macos-users)

Now you need to create a new virtual env

```
pyenv virtualenv chatpic
pyenv activate chatpic

```

You now can install the requirements to run the archiver

```
pip install requests python-socketio "python-socketio[client]"

```

After you installed the dependencies, you can simply start [the archiver script](#script) with

```
python3 main.py

```

Windows setup instructions
==========================

I do not have access to windows right now. Mail me installation instructions and i will publish them here.

You may want to follow [this](https://www.liquidweb.com/kb/how-to-install-python-on-windows/) instructions and try running [the archiver script](#script) but I do not guarantee success

The script
==========

Save this script as main.py somewhere you can find it again.

To join *every* NSFW room set `JOIN_EVERYTHING` to `True`This will then join every room and all sub rooms which are not password protected and will take a long time.

Unlike the archive version, this will save every file not just pictures.

```
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

```

