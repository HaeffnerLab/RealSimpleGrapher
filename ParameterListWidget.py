import sys
from PyQt5 import QtWidgets
from twisted.internet.defer import inlineCallbacks


class ParameterList(QtWidgets.QWidget):

    def __init__(self, dataset):
        super(ParameterList, self).__init__()
        self.dataset = dataset
        mainLayout = QtWidgets.QVBoxLayout()
        self.parameterListWidget = QtWidgets.QListWidget()
        mainLayout.addWidget(self.parameterListWidget)
        self.setWindowTitle(str(dataset.dataset_name))  # + " " + str(dataset.directory))
        self.populate()
        self.setLayout(mainLayout)
        self.show()

    @inlineCallbacks
    def populate(self):
        parameters = yield self.dataset.getParameters()
        self.parameterListWidget.clear()
        self.parameterListWidget.addItems([str(x) for x in sorted(parameters)])
