
#import GUI elements
from Dataset import Dataset
from GraphWindow import GraphWindow

#import server libraries
from twisted.internet.threads import deferToThread
from twisted.internet.defer import returnValue, Deferred, inlineCallbacks


class RSG_client(object):
    """
    RSG Client
    """
    name = "Real Simple Grapher2"

    def __init__(self, reactor, cxn=None, parent=None):
        super().__init__()
        self.cxn = cxn
        self.gui = self
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
            self.pv = self.parameter_vault
            self.dv = self.cxn.data_vault
            self.rsg = self.cxn.real_simple_grapher
        except Exception as e:
            print(e)
            raise

        # connect to signals
            #device parameters
        yield self.tt.signal__pressure_update(self.PRESSUREID)
        yield self.tt.addListener(listener=self.updatePressure, source=None, ID=self.PRESSUREID)
        yield self.tt.signal__power_update(self.POWERID)
        yield self.tt.addListener(listener=self.updatePower, source=None, ID=self.POWERID)
            #server connections
        yield self.cxn.manager.subscribe_to_named_message('Server Connect', 9898989, True)
        yield self.cxn.manager.addListener(listener=self.on_connect, source=None, ID=9898989)
        yield self.cxn.manager.subscribe_to_named_message('Server Disconnect', 9898989 + 1, True)
        yield self.cxn.manager.addListener(listener=self.on_disconnect, source=None, ID=9898989 + 1)

        return self.cxn

    @inlineCallbacks
    def initServer(self):
        self.listeners = set()
        self.gui = GraphWindow(reactor, cxn=self.client)
        self.gui.setWindowTitle('Real Simple Grapher2')
        self.dv = yield self.client.data_vault
        self.pv = yield self.client.parameter_vault

    def make_dataset(self, dataset_location):
        cxt = self.client.context()
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
        print(self.gui.graphDict[graph])

    def do_imshow(self, data, image_size, graph, name):
        self.gui.graphDict[graph].update_image(data, image_size, name)

    @setting(1, 'Plot', dataset_location=['(*s, s)', '(*s, i)'], graph='s', send_to_current='b', returns='')
    def plot(self, c,  dataset_location, graph, send_to_current=True):
        self.do_plot(dataset_location, graph, send_to_current)

    @setting(2, 'Plot with axis', dataset_location=['(*s, s)', '(*s, i)'], graph='s', axis='*v', send_to_current='b', returns='')
    def plot_with_axis(self, c, dataset_location, graph, axis, send_to_current=True):
        minim = min(axis)
        maxim = max(axis)
        if (graph != 'current') and send_to_current:
            self.gui.graphDict['current'].set_xlimits([minim[minim.units], maxim[maxim.units]])
        self.gui.graphDict[graph].set_xlimits([minim[minim.units], maxim[maxim.units]])
        self.do_plot(dataset_location, graph, send_to_current)

    @setting(3, 'Plot image', image='*i', image_size='*i', graph='s', name='s', returns='')
    def plot_image(self, c, image, image_size, graph, name=''):
        self.do_imshow(image, image_size, graph, name)


if __name__ == '__main__':
    from labrad import util
    util.runServer(RealSimpleGrapher2())

