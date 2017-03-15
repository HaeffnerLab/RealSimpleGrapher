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

        self.initUI()

    def initUI(self):
        self.imv = pg.ImageView()
        self.title = QtGui.QLabel(self.name)
        self.next_button = QtGui.QPushButton('>')
        self.prev_button = QtGui.QPushButton('<')
        layout = QtGui.QGridLayout()
        layout.addWidget(self.title, 0,0)
        layout.addWidget(self.prev_button, 1,0)
        layout.addWidget(self.next_button, 1,1)
        layout.addWidget(self.imv, 2,0, 20,2)
        self.setLayout(layout)

    def update_image(self, data, image_size, name):
        self.imv.setImage(data.reshape(image_size[0], image_size[1]))
        self.title.setText(self.name + ' ' + name)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    main = imageWidget('example', reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()