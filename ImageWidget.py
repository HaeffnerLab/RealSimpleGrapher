import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from TraceListWidget import TraceList
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import itertools
import Queue

class artistParameters():
    def __init__(self, artist, dataset, index, shown):
        self.artist = artist
        self.dataset = dataset
        self.index = index
        self.shown = shown
        self.last_update = 0 # update counter in the Dataset object
                             # only redraw if the dataset has a higher
                             # update count

class imageWidget(QtGui.QWidget):

    def __init__(self, config, reactor, parent=None):
        super(imageWidget, self).__init__(parent)

        self.reactor = reactor
        self.artists = {}
        self.should_stop = False
        self.name = config.name

        self.dataset_queue = Queue.Queue(config.max_datasets)

        self.live_update_loop = LoopingCall(self.update_figure)
        self.live_update_loop.start(0)

        self.initUI()

    def initUI(self):
        self.tracelist = TraceList(self)
        self.imv = pg.ImageView()
        self.coords = QtGui.QLabel('')
        self.title = QtGui.QLabel(self.name)
        frame = QtGui.QFrame()
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.tracelist)
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.title)
        vbox.addWidget(self.imv)
        vbox.addWidget(self.coords)
        frame.setLayout(vbox)
        splitter.addWidget(frame)
        hbox.addWidget(splitter)
        self.setLayout(hbox)
        self.tracelist.itemChanged.connect(self.checkboxChanged)

    def update_figure(self):
        pass

    def add_artist(self, ident, dataset, index):
        '''
        no_points is an override parameter to the global show_points setting.
        It is to allow data fits to be plotted without points
        '''
        image = self.imv.setImage(dataset)
        self.artists[ident] = artistParameters(image, dataset, index, True)
        self.tracelist.addTrace(ident)

    def remove_artist(self, ident):
        pass

    def checkboxChanged(self):
        pass

    @inlineCallbacks
    def add_dataset(self, dataset):
        pass

    @inlineCallbacks
    def remove_dataset(self, dataset):
        pass

    def set_xlimits(self, limits):
        pass

    def set_ylimits(self, limits):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    main = imageWidget('example', reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()