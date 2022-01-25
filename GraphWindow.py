'''
Window for holding Graphs
'''
import sys
import GUIConfig

from PyQt5 import QtCore, QtWidgets

from GraphWidgetPyQtGraph import Graph_PyQtGraph as Graph
from HistWidgetPyQtGraph import Hist_PyQtGraph as Hist
from ScrollingGraphWidgetPyQtGraph import ScrollingGraph_PyQtGraph as ScrollingGraph
from ImageWidget import imageWidget as ImageGraph
from GridGraphWindow import GridGraphWindow

class GraphWindow(QtWidgets.QTabWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        super(GraphWindow, self).__init__(parent)
        self.cxn = cxn
        self.reactor = reactor        
        self.initUI()
        self.show()
        
    def initUI(self):
        reactor = self.reactor

        self.graphDict = {}
        self.tabDict = {}

        for gc in GUIConfig.tabs:
            gcli = gc.config_list
            gli = []
            for config in gcli:
                name = config.name
                max_ds = config.max_datasets
                if config.isScrolling:
                    g = ScrollingGraph(config, reactor, self.cxn)
                elif config.isImages:
                    g = ImageGraph(config, reactor)
                    self.graphDict[name] = g
                    gli.append(g)
                    continue
                elif config.isHist:
                    g = Hist(config, reactor, self.cxn)
                    self.graphDict[name] = g
                    gli.append(g)
                    continue
                else:
                    g = Graph(config, reactor, self.cxn)
                g.set_ylimits(config.ylim)
                self.graphDict[name] = g
                gli.append(g)
            widget = GridGraphWindow(gli, gc.row_list, gc.column_list, reactor)
            self.tabDict[name] = widget
            self.addTab(widget, gc.tab)
            self.setMovable(True)
            

    def insert_tab(self, t):
        g = Graph(t, reactor)
        self.graphDict[t] = g
        self.addTab(g, t)
        
    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()
    main = GraphWindow(reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()
