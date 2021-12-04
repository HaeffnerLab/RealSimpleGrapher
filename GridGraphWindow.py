'''
Window containing a grid of graphs
'''

import sys
import GUIConfig
from PyQt5.QtWidgets import QWidget

from GraphWidgetPyQtGraph import Graph_PyQtGraph as Graph
from ScrollingGraphWidgetPyQtGraph import ScrollingGraph_PyQtGraph as ScrollingGraph


class GridGraphWindow(QWidget):
    def __init__(self, g_list, row_list, column_list, reactor, parent=None):
        super(GridGraphWindow, self).__init__(parent)
        self.reactor = reactor        
        self.initUI(g_list, row_list, column_list)
        self.show()

    def initUI(self, g_list, row_list, column_list):
        reactor = self.reactor
        layout = QtWidgets.QGridLayout()
        for k in range(len(g_list)):
            layout.addWidget(g_list[k], row_list[k], column_list[k])
        self.setLayout(layout)

