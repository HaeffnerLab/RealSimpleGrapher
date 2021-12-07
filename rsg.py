"""
### BEGIN NODE INFO
[info]
name =  Real Simple Grapher
version = 1.0
description =
instancename = Real Simple Grapher
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

#import GUI elements
from Dataset import Dataset
from GraphWindow import GraphWindow
from PyQt5.QtWidgets import QApplication

#install qt reactor
import sys
app = QApplication(sys.argv)
import qt5reactor
qt5reactor.install()

#import server libraries
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from twisted.internet.defer import returnValue, Deferred, inlineCallbacks


class RealSimpleGrapher(LabradServer):
    """
    RSG Server.
    Methods for controlling graphing.
    """

    name = "Real Simple Grapher"

    # STARTUP
    @inlineCallbacks
    def initServer(self):
        self.listeners = set()
        self.gui = GraphWindow(reactor, cxn=self.client)
        self.gui.setWindowTitle('Real Simple Grapher')
        self.dv = yield self.client.data_vault
        self.pv = yield self.client.parameter_vault

    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)

    def expireContext(self, c):
        """Remove a context object."""
        self.listeners.remove(c.ID)

    def getOtherListeners(self, c):
        """Get all listeners except for the context owner."""
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified


    # PLOTTING
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

    def do_imshow(self, data, image_size, graph, name):
        self.gui.graphDict[graph].update_image(data, image_size, name)

    @setting(1, 'Plot', dataset_location=['(*s, s)', '(*s, i)'], graph='s', send_to_current='b', returns='')
    def plot(self, c, dataset_location, graph, send_to_current=True):
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

    @setting(4, 'Plot Client', client_ID='i', dataset_location=['(*s, s)', '(*s, i)'], graph='s', send_to_current='b', returns='')
    def plot_client(self, c, client_ID, dataset_location, graph, send_to_current=True):
        pass
        #self.plot_client_signal(dataset_location, graph, send_to_current, (client_ID, ***))


if __name__ == '__main__':
    from labrad import util
    util.runServer(RealSimpleGrapher())

