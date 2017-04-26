import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from TraceListWidget import TraceList
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import itertools
import Queue


class imageWidget(QtGui.QWidget):

    def __init__(self, config, reactor, parent=None):
        super(imageWidget, self).__init__(parent)

        self.reactor = reactor
        self.artists = {}
        self.should_stop = False
        self.name = config.name
        self.image_list = []
        self.image_index = -1

        self.initUI()

    def initUI(self):
        self.imv = pg.ImageView()
        self.title = QtGui.QLabel(self.name)
        self.next_button = QtGui.QPushButton('>')
        self.prev_button = QtGui.QPushButton('<')
        self.next_button.clicked.connect(self.on_next)
        self.prev_button.clicked.connect(self.on_prev)
        layout = QtGui.QGridLayout()
        layout.addWidget(self.title, 0,0)
        layout.addWidget(self.prev_button, 1,0)
        layout.addWidget(self.next_button, 1,1)
        layout.addWidget(self.imv, 2,0, 20,2)
        self.setLayout(layout)

    def update_image(self, data, image_size, name):
        image = data.reshape(image_size[0], image_size[1])
        self.imv.setImage(image)
        self.image_list.append([image, self.name + ' ' + name])
        self.image_index += 1
        if len(self.image_list) > 100:
            del self.image_list[0]
        self.title.setText(self.name + ' ' + name)

    def on_next(self):
        try:
            self.imv.setImage(self.image_list[self.image_index + 1][0])
            self.title.setText(self.image_list[self.image_index + 1][1])
            self.image_index += 1

        except:
            print 'Could not access index: ' + str(self.image_index + 1)

    def on_prev(self):
        try:
            self.imv.setImage(self.image_list[self.image_index - 1][0])
            self.title.setText(self.image_list[self.image_index - 1][1])
            self.image_index -= 1
        except:
            print 'Could not access index: ' + str(self.image_index - 1)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    main = imageWidget('example', reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()