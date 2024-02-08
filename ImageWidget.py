import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from .TraceListWidget import TraceList
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import itertools
import queue


class imageWidget(QtGui.QWidget):

    def __init__(self, config, reactor, parent=None, cxn=None):
        super(imageWidget, self).__init__(parent)

        self.reactor = reactor
        self.artists = {}
        self.should_stop = False
        self.name = config.name
        self.image_list = []
        self.image_index = 0

        self.initUI()

    def initUI(self):
        self.plt = plt = pg.PlotItem()
        self.imv = pg.ImageView(view = self.plt)
        plt.showAxis('top')
        plt.hideAxis('bottom')
        plt.setAspectLocked(True)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        plt.addItem(self.vLine, ignoreBounds=True)
        plt.addItem(self.hLine, ignoreBounds=True)
        self.plt.scene().sigMouseClicked.connect(self.mouse_clicked)
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
        if len(self.image_list) == 0:
            self.imv.setImage(image)
        else:
            self.imv.setImage(image, autoRange=False, autoLevels=False, autoHistogramRange=False)
        self.image_list.append([image, self.name + ' ' + name])
        self.image_index = len(self.image_list) - 1
        if len(self.image_list) > 100:
            del self.image_list[0]
        self.title.setText(self.name + ' ' + name)

    def on_next(self):
        try:
            if self.image_index < len(self.image_list) -1:
                self.image_index += 1
                self.imv.setImage(self.image_list[self.image_index][0], autoRange=False, autoLevels=False, autoHistogramRange=False)
                self.title.setText(self.image_list[self.image_index][1])
            else:
                pass

        except:
            print('Could not access index: ' + str(self.image_index))

    def on_prev(self):
        try:
            if self.image_index > 0:
                self.image_index -= 1
                self.imv.setImage(self.image_list[self.image_index][0], autoRange=False, autoLevels=False, autoHistogramRange=False)
                self.title.setText(self.image_list[self.image_index][1])
            else:
                pass
        except:
            print('Could not access index: ' + str(self.image_index))

    def mouse_clicked(self, event):
        '''
        draws the cross at the position of a double click
        '''
        pos = event.pos()
        if self.plt.sceneBoundingRect().contains(pos) and event.double():
            #only on double clicks within bounds
            mousePoint = self.plt.vb.mapToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    from . import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    main = imageWidget('example', reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()