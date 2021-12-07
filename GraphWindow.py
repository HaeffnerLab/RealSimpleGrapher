'''
The main GUI which holds everything.
'''
import sys
import GUIConfig

from PyQt5.QtWidgets import QTabWidget, QApplication

from GridGraphWindow import GridGraphWindow
from ImageWidget import imageWidget as ImageGraph
from HistWidgetPyQtGraph import Hist_PyQtGraph as Hist
from GraphWidgetPyQtGraph import Graph_PyQtGraph as Graph
from ScrollingGraphWidgetPyQtGraph import ScrollingGraph_PyQtGraph as ScrollingGraph


class GraphWindow(QTabWidget):
    """
    The main RSG GUI which does nearly everything.
    Creates the RSG GUI from GUIConfig.py.
    Each tab is a _PyQtGraph object.
    """

    def __init__(self, reactor, cxn=None, parent=None, root=None):
        """
        Initialize self variables and setup the GUI.
        """
        # initialize the PyQt object
        super(GraphWindow, self).__init__()
        # initialize self variables
        self.cxn = cxn
        self.parent = parent
        self.reactor = reactor
        self.root = root
        # initialize the UI
        self.initUI()
        # show the UI
        self.show()
        
    def initUI(self):
        reactor = self.reactor
        # create dictionaries to hold the graphs and tabs
        self.graphDict = {}
        self.tabDict = {}

        # create the individual tabs
        for gc in GUIConfig.tabs:
            # gcli = graph config list
            gcli = gc.config_list
            gli = []
            for config in gcli:
                name = config.name
                max_ds = config.max_datasets
                if config.isScrolling:
                    graph_tmp = ScrollingGraph(config, reactor, cxn=self.cxn, root=self.root)
                elif config.isImages:
                    graph_tmp = ImageGraph(config, reactor)
                    self.graphDict[name] = graph_tmp
                    gli.append(graph_tmp)
                    continue
                elif config.isHist:
                    graph_tmp = Hist(config, reactor, cxn=self.cxn, root=self.root)
                    self.graphDict[name] = graph_tmp
                    gli.append(graph_tmp)
                    continue
                else:
                    graph_tmp = Graph(config, reactor, cxn=self.cxn, root=self.root)
                graph_tmp.set_ylimits(config.ylim)
                self.graphDict[name] = graph_tmp
                gli.append(graph_tmp)
            widget = GridGraphWindow(gli, gc.row_list, gc.column_list, reactor)
            self.tabDict[name] = widget
            self.addTab(widget, gc.tab)
            self.setMovable(True)

    def insert_tab(self, tab):
        graph_tmp = Graph(tab, reactor, cxn=self.cxn, root=self.root)
        self.graphDict[tab] = graph_tmp
        self.addTab(graph_tmp, tab)
        
    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    main = GraphWindow(reactor)
    main.show()
    #sys.exit(app.exec_())
    reactor.run()
