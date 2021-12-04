import socket
from PyQt5 import QtWidgets
from twisted.internet.defer import inlineCallbacks


class DataVaultList(QtWidgets.QWidget):
    """
    Data vault pop-up window used to select datasets for plotting.
    Creates a client connection to LabRAD to access the datavault and grapher servers.
    """

    def __init__(self, tracename, cxn=None, parent=None, root=None):
        super(DataVaultList, self).__init__()
        self.tracename = tracename
        self.root = root
        self.connect()

    @inlineCallbacks
    def connect(self):
        if not self.cxn:
            from labrad.wrappers import connectAsync
            self.cxn = yield connectAsync(name=socket.gethostname() + ' Data Vault Client')
            self.grapher = yield self.cxn.real_simple_grapher2
            self.dv = yield self.cxn.data_vault
            self.initializeGUI()

    def initializeGUI(self):
        mainLayout = QtWidgets.QVBoxLayout()
        self.dataListWidget = QtWidgets.QListWidget()
        self.dataListWidget.doubleClicked.connect(self.onDoubleclick)
        mainLayout.addWidget(self.dataListWidget)
        self.setWindowTitle('Data Vault')
        self.setLayout(mainLayout)
        self.populate()
        self.show()

    @inlineCallbacks
    def populate(self):
        self.dataListWidget.clear()
        ls = yield self.dv.dir()
        self.dataListWidget.addItem('...')
        self.dataListWidget.addItems(sorted(ls[0]))
        if ls[1] is not None:
            self.dataListWidget.addItems(sorted(ls[1]))

    @inlineCallbacks
    def onDoubleclick(self, item):
        item = self.dataListWidget.currentItem().text()
        if item == '...':
            yield self.dv.cd(1)
            self.populate()
        else:
            try:
                yield self.dv.cd(str(item))
                self.populate()
            except:
                path = yield self.dv.cd()
                yield self.grapher.plot((path, str(item)), self.tracename, False)

    def closeEvent(self, event):
        self.cxn.disconnect()
