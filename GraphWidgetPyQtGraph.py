import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from TraceListWidget import TraceList
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
import itertools
from Dataset import Dataset
import Queue

import numpy as np
from numpy import random

class artistParameters():
    def __init__(self, artist, dataset, index, shown):
        self.artist = artist
        self.dataset = dataset
        self.index = index
        self.shown = shown
        self.last_update = 0 # update counter in the Dataset object
                             # only redraw if the dataset has a higher
                             # update count

class Graph_PyQtGraph(QtGui.QWidget):
    def __init__(self, config, reactor, cxn = None, parent=None):
        super(Graph_PyQtGraph, self).__init__(parent)
        from labrad.units import WithUnit as U
        self.U = U
        self.cxn = cxn
        self.pv = self.cxn.parametervault
        self.reactor = reactor
        self.artists = {}
        self.should_stop = False
        self.name = config.name
        self.vline_name = config.vline
        self.vline_param = config.vline_param
        self.hline_name = config.hline
        self.hline_param = config.hline_param
        self.show_points = config.show_points
        self.grid_on = config.grid_on
        self.scatter_plot = config.scatter_plot

        self.dataset_queue = Queue.Queue(config.max_datasets)

        self.live_update_loop = LoopingCall(self.update_figure)
        self.live_update_loop.start(0)

        colors = ['r', 'g', 'y', 'c', 'm', 'w']
        self.colorChooser = itertools.cycle(colors)
        self.initUI()

    @inlineCallbacks
    def initUI(self):
        self.tracelist = TraceList(self)
        self.pw = pg.PlotWidget()
        self._set_axes_font(20)
        if self.vline_name:
            self.inf = pg.InfiniteLine(movable=True, angle=90,
                                       label=self.vline_name + '{value:0.0f}',
                                       labelOpts={'position': 0.9,
                                                  'color': (200, 200, 100),
                                                  'fill': (200, 200, 200, 50),
                                                  'movable': True})
            init_value = yield self.get_init_vline()
            self.inf.setValue(init_value)
            self.inf.setPen(width=5.0)

        if self.hline_name:
            self.inf = pg.InfiniteLine(movable=True, angle=0,
                                       label=self.hline_name + '{value:0.0f}',
                                       labelOpts={'position': 0.9,
                                                  'color': (200, 200, 100),
                                                  'fill': (200, 200, 200, 50),
                                                  'movable': True})
            init_value = yield self.get_init_hline()
            self.inf.setValue(init_value)
            self.inf.setPen(width=5.0)

        self.coords = QtGui.QLabel('')
        self.title = QtGui.QLabel(self.name)
        frame = QtGui.QFrame()
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.tracelist)
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.title)
        vbox.addWidget(self.pw)
        vbox.addWidget(self.coords)
        frame.setLayout(vbox)
        splitter.addWidget(frame)
        hbox.addWidget(splitter)
        self.setLayout(hbox)
        #self.legend = self.pw.addLegend()
        self.tracelist.itemChanged.connect(self.checkboxChanged)
        self.pw.plot([],[])
        vb = self.pw.plotItem.vb
        self.img = pg.ImageItem()
        vb.addItem(self.img)

        if self.vline_name:
            vb.addItem(self.inf)
            self.inf.sigPositionChangeFinished.connect(self.vline_changed)

        if self.hline_name:
            vb.addItem(self.inf)
            self.inf.sigPositionChangeFinished.connect(self.hline_changed)

        self.pw.scene().sigMouseMoved.connect(self.mouseMoved)
        self.pw.sigRangeChanged.connect(self.rangeChanged)
        
    def _set_axes_font(self, font_size):
        font = QtGui.QFont()
        font.setPixelSize(font_size)
        left_axis = self.pw.plotItem.getAxis("left")
        left_axis.tickFont = font
        left_axis.setWidth(font_size * 7)
        left_axis.setStyle(tickTextOffset=font_size/2)
        left_axis.setStyle(textFillLimits=[(0, 0.6), (2, 0.4),
                                           (4, 0.2), (6, 0.0)])
        bottom_axis = self.pw.plotItem.getAxis("bottom")
        bottom_axis.tickFont = font
        bottom_axis.setHeight(font_size * 2)
        bottom_axis.setStyle(tickTextOffset=font_size/2)
        bottom_axis.setStyle(textFillLimits=[(0, 0.6), (2, 0.4),
                                             (4, 0.2), (6, 0.0)])

    def getItemColor(self, color):
        color_dict = {"r": QtGui.QColor(QtCore.Qt.red).lighter(130),
                      "g": QtGui.QColor(QtCore.Qt.green),
                      "y": QtGui.QColor(QtCore.Qt.yellow),
                      "c": QtGui.QColor(QtCore.Qt.cyan),
                      "m": QtGui.QColor(QtCore.Qt.magenta).lighter(120),
                      "w": QtGui.QColor(QtCore.Qt.white)}
        return color_dict[color]

    def update_figure(self):
        for ident, params in self.artists.iteritems():
            if params.shown:
                try:
                    ds = params.dataset
                    index = params.index
                    current_update = ds.updateCounter
                    if params.last_update < current_update:
                        x = ds.data[:,0]
                        y = ds.data[:,index+1]
                        params.last_update = current_update
                        params.artist.setData(x,y)
                except: pass

    def add_artist(self, ident, dataset, index, no_points = False):
        '''
        no_points is an override parameter to the global show_points setting.
        It is to allow data fits to be plotted without points
        '''
        new_color = self.colorChooser.next()
        if self.show_points and not no_points:
            line = self.pw.plot([], [], symbol='o', symbolBrush=self.getItemColor(new_color),
                                name=ident, pen = self.getItemColor(new_color), connect=self.scatter_plot)
        else:
            line = self.pw.plot([], [], pen = self.getItemColor(new_color), name = ident)
        if self.grid_on:
            self.pw.showGrid(x=True, y=True)
        self.artists[ident] = artistParameters(line, dataset, index, True)
        self.tracelist.addTrace(ident, new_color)

    def remove_artist(self, ident):
        try:
            artist = self.artists[ident].artist
            self.pw.removeItem(artist)
            #self.legend.removeItem(ident)
            self.tracelist.removeTrace(ident)
            self.artists[ident].shown = False
            try:
                del self.artists[ident]
            except KeyError:
                pass
        except:
            print "remove failed"

    def display(self, ident, shown):
        try:
            artist = self.artists[ident].artist
            if shown:
                self.pw.addItem(artist)
                self.artists[ident].shown = True
            else:
                self.pw.removeItem(artist)
                #self.legend.removeItem(ident)
                self.artists[ident].shown = False
        except KeyError:
            raise Exception('404 Artist not found')

    def checkboxChanged(self):
        for ident, item in self.tracelist.trace_dict.iteritems():
            try:
                if item.checkState() and not self.artists[ident].shown:
                    self.display(ident, True)
                if not item.checkState() and self.artists[ident].shown:
                    self.display(ident, False)
            except KeyError: # this means the artist has been deleted.
                pass

    def rangeChanged(self):

        lims = self.pw.viewRange()
        self.pointsToKeep =  lims[0][1] - lims[0][0]
        self.current_limits = [lims[0][0], lims[0][1]]

    @inlineCallbacks
    def add_dataset(self, dataset):
        try:
            self.dataset_queue.put(dataset, block=False)
        except Queue.Full:
            remove_ds = self.dataset_queue.get()
            self.remove_dataset(remove_ds)
            self.dataset_queue.put(dataset, block=False)
        labels = yield dataset.getLabels()
        for i, label in enumerate(labels):
            self.add_artist(label, dataset, i)

    @inlineCallbacks
    def remove_dataset(self, dataset):
        labels = yield dataset.getLabels()
        for label in labels:
            self.remove_artist(label)

    def set_xlimits(self, limits):
        self.pw.setXRange(limits[0], limits[1])
        self.current_limits = limits

    def set_ylimits(self, limits):
        self.pw.setYRange(limits[0],limits[1])

    def mouseMoved(self, pos):
        #print "Image position:", self.img.mapFromScene(pos)
        pnt = self.img.mapFromScene(pos)
        string = '(' + str(pnt.x()) + ' , ' + str(pnt.y()) + ')'
        self.coords.setText(string)

    @inlineCallbacks
    def get_init_vline(self):
        init_vline = yield self.pv.get_parameter(self.vline_param[0],
                                                 self.vline_param[1])
        returnValue(init_vline)

    @inlineCallbacks
    def get_init_hline(self):
        init_hline = yield self.pv.get_parameter(self.hline_param[0],
                                                 self.hline_param[1])
        returnValue(init_hline)

    @inlineCallbacks
    def vline_changed(self, sig):
        val = self.inf.value()
        param = yield self.pv.get_parameter(self.vline_param[0], self.vline_param[1])
        units = param.units
        val = self.U(val, units)
        yield self.pv.set_parameter(self.vline_param[0], self.vline_param[1], val)

    @inlineCallbacks
    def hline_changed(self, sig):
        val = self.inf.value()
        param = yield self.pv.get_parameter(self.hline_param[0], self.hline_param[1])
        units = param.units
        val = self.U(val, units)
        yield self.pv.set_parameter(self.hline_param[0], self.hline_param[1], val)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    main = Graph_PyQtGraph('example', reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()
