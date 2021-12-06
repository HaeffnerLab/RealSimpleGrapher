
#import GUI elements
from Dataset import Dataset
from GraphWindow import GraphWindow

#import server libraries
from twisted.internet.threads import deferToThread
from twisted.internet.defer import returnValue, Deferred, inlineCallbacks

from random import randrange


class RSG_client(object):
    """
    Client for the Real Simple Grapher.
    Doesn't require the RSG to be running at all.
    """

    name = "RSG Client"

    def __init__(self, reactor, cxn=None, parent=None):
        super().__init__()
        # create random client ID
        self.ID = randrange(3e5, 1e6)
        self.cxn = cxn
        # self.gui = GraphWindow(reactor, cxn=self.cxn, root=self)
        # self.gui.setWindowTitle('Real Simple Grapher')
        self.reactor = reactor
        self.servers = ['Real Simple Grapher', 'Data Vault', 'Parameter Vault']
        # initialization sequence
        d = self.connect()
        d.addCallback(self.initializeGUI)

    @inlineCallbacks
    def connect(self):
        """
        Creates an asynchronous connection to pump servers
        and relevant labrad servers
        """
        # create labrad connection
        if not self.cxn:
            import os
            LABRADHOST = os.environ['LABRADHOST']
            from labrad.wrappers import connectAsync
            self.cxn = yield connectAsync(LABRADHOST, name=self.name)

        # try to get servers
        try:
            self.reg = self.cxn.registry
            self.pv = self.cxn.parameter_vault
            self.dv = self.cxn.data_vault
            #self.rsg = self.cxn.real_simple_grapher
        except Exception as e:
            print(e)
            raise

        # connect to signals
            # rsg signal
        #yield self.rsg.signal__plot_update(self.ID)
        #yield self.rsg.addListener(listener=self., source=None, ID=self.ID)
            # server connections
        yield self.cxn.manager.subscribe_to_named_message('Server Connect', 9898989, True)
        yield self.cxn.manager.addListener(listener=self.on_connect, source=None, ID=9898989)
        yield self.cxn.manager.subscribe_to_named_message('Server Disconnect', 9898989 + 1, True)
        yield self.cxn.manager.addListener(listener=self.on_disconnect, source=None, ID=9898989 + 1)
        return self.cxn

    def initializeGUI(self, cxn):
        # GUI creation needs to be here since the connection needs to be established
        self.gui = GraphWindow(self.reactor, cxn=self.cxn, root=self)
        self.gui.setWindowTitle('Real Simple Grapher - Client')

    # SIGNALS
    def on_connect(self, c, message):
        server_name = message[1]
        if server_name in self.servers:
            print(server_name + ' reconnected, enabling widget.')
            self.setEnabled(True)

    def on_disconnect(self, c, message):
        server_name = message[1]
        if server_name in self.servers:
            print(server_name + ' disconnected, disabling widget.')
            self.setEnabled(False)


    # PLOTTING
    def make_dataset(self, dataset_location):
        cxt = self.cxn.context()
        ds = Dataset(self.dv, cxt, dataset_location, reactor)
        return ds

    def do_plot(self, dataset_location, graph, send_to_current):
        if (graph != 'current') and send_to_current:
            # add the plot to the Current tab as well as an additional
            # specified tab for later examination
            ds = self.make_dataset(dataset_location)
            self.gui.graphDict['current'].add_dataset(ds)
        ds = self.make_dataset(dataset_location)
        self.gui.graphDict[graph].add_dataset(ds)

    def plot_image(self, data, image_size, graph, name):
        self.gui.graphDict[graph].update_image(data, image_size, name)

    def plot_with_axis(self, c, dataset_location, graph, axis, send_to_current=True):
        minim = min(axis)
        maxim = max(axis)
        if (graph != 'current') and send_to_current:
            self.gui.graphDict['current'].set_xlimits([minim[minim.units], maxim[maxim.units]])
        self.gui.graphDict[graph].set_xlimits([minim[minim.units], maxim[maxim.units]])
        self.do_plot(dataset_location, graph, send_to_current)


if __name__ == '__main__':
    # from EGGS_labrad.lib.clients import runClient
    # runClient(RSG_client)
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    client = RSG_client(reactor)
    #sys.exit(app.exec_())
    reactor.run()

