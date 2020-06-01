from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLabel, QLineEdit, QStyleFactory, QWidget,QVBoxLayout,QStackedWidget
from PyQt5 import QtGui
from PyQt5 import QtCore
import asyncio
import json
import time
import statistics
import math
#server client
IPADDR = '127.0.0.1'
PORT = 8888


#settings
title = 'CDT'
posx = 800
posy = 100
width, height = 800, 800
focus = None
msg = None
app = QApplication([])
mwidget = QWidget()
stack = QStackedWidget()
win = QMainWindow()
win.setWindowTitle('CDT')
win.setGeometry(posx,posy,width,height)
win.setCentralWidget(stack)
stack.addWidget(mwidget)

async def request(message_out):
    #Requesting information from the server
    global msg
    reader, writer = await asyncio.open_connection(
        IPADDR, PORT)

    data_out = json.dumps(message_out).encode()
    
    writer.write(data_out)
    writer.write_eof()
    await writer.drain()

    data = await reader.read()

    message_out = json.loads(data.decode())
    msg = message_out

    writer.close()
    await writer.wait_closed()
    

#Functions
def switch(stack,index,t):
    #switch windows
    global focus
    stack.setCurrentIndex(index)
    focus = t

def changeTooltip(text,tt):
    #change safety level
    tt.setToolTip(text)

def send(text,location):
    global msg
    #different request packets
    packet = {
        'mode': 'record',
        'payload': {
            'fname': location,
            'number': int(text)
        },
        'auth': {
            'username': 'superadmin',
            'token': 'password'
        }
    }
    table_1 = {
        'mode': 'fetchall',
        'auth': {
            'username': 'superadmin',
            'token': 'password'
        },
        'payload': 3
    }
    table_2 = {
        'mode': 'fetchall',
        'auth': {
            'username': 'superadmin',
            'token': 'password'
        },
        'payload': 0
    }
    asyncio.run(request(packet))
    asyncio.run(request(table_1))
    # decode msg
    values = list()
    for x in msg:
        if x['locid'] == location:
            values.append(x['pollres'])
    asyncio.run(request(table_2))
    for x in msg:
        if x['name'] == location:
            area = x['area']
    if len(values) > 1:
        ans = math.ceil(statistics.mean(values))
    elif len(values) == 1:
        ans = values[0]
    else:
        ans = None
    if ans != None:
        if area // ans <= 5:
            changeTooltip('Safe',buttons[location])
        else:
            changeTooltip('Risky',buttons[location])


#map layout
mapL = QGridLayout()
pts = [
    'Washroom', ' ', 'Gym', ' ',
    ' ', "Store", ' ', ' ',
    ' ', ' ', 'Park', 'Restaurant'
]
buttons = dict()
r, c = len(pts)//4, 4
pos = list()
for i in range(r):
    for v in range(c):
        pos.append((i,v))

for i,x in enumerate(pts):
    if x != ' ':
        b = QPushButton(x)
        buttons[x] = b
        b.setIcon(QtGui.QIcon("icon.png"))
        mapL.addWidget(b,pos[i][0],pos[i][1])
        b.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips)
        b.setToolTip('No Entries')
        
#infowindow
infoL = QVBoxLayout()
back = QPushButton("Back")

question = QLabel("Give your best estimate to how many people are at your current location?")
question.setFont(QtGui.QFont("Arial",15))
lbl = QLabel()
text = QLineEdit()
text.setSizePolicy(200,20)
text.setFont(QtGui.QFont("Arial",41))
submit = QPushButton('Submit')
submit.setFixedSize(490,30)
infoL.addWidget(back, alignment=QtCore.Qt.AlignTop)
infoL.addWidget(question)
infoL.addWidget(text, alignment=QtCore.Qt.AlignCenter)
infoL.addWidget(submit, alignment=QtCore.Qt.AlignCenter)

infoL.setAlignment(QtCore.Qt.AlignCenter)
infoL.setSpacing(30)
infow = QWidget()
infow.setLayout(infoL)
stack.addWidget(infow)

#clicked events
back.clicked.connect(lambda: switch(stack,0,None))
submit.clicked.connect(lambda: send(text.text(),focus))
buttons['Washroom'].clicked.connect(lambda: switch(stack,1,'Washroom'))
buttons['Gym'].clicked.connect(lambda: switch(stack,1,'Gym'))
buttons['Store'].clicked.connect(lambda: switch(stack,1,'Store'))
buttons['Park'].clicked.connect(lambda: switch(stack,1,'Park'))
buttons['Restaurant'].clicked.connect(lambda: switch(stack,1,'Restaurant'))

mapL.setSpacing(100)
mwidget.setLayout(mapL)
mwidget.setStyleSheet("background-image: url(map.jpg);")

win.show()
app.exec_()
