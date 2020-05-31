from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLabel, QLineEdit, QStyleFactory, QWidget,QVBoxLayout
from PyQt5.QtGui import QIcon
import random

title = 'CDT'
posx = 800
posy = 100
width, height = 800, 800

app = QApplication([])
mwidget = QWidget()
win = QMainWindow()
win.setWindowTitle('CDT')
win.setGeometry(posx,posy,width,height)
win.setCentralWidget(mwidget)

#map layout
mapL = QGridLayout()
pts = [
    'Grocery store', ' ', 'Walmart', ' ',
    ' ', "Mac's", ' ', ' ',
    ' ', ' ', 'Park', 'McDonalds'
]
r, c = len(pts)//4, 4
pos = list()
for i in range(r):
    for v in range(c):
        pos.append((i,v))

for i,x in enumerate(pts):
    if x != ' ':
        b = QPushButton(x)
        b.setIcon(QIcon("icon.png"))
        mapL.addWidget(b,pos[i][0],pos[i][1])
mapL.setSpacing(100)
mwidget.setLayout(mapL)
mwidget.setStyleSheet("background-image: url(bg.jpg);")

win.show()
app.exec_()
