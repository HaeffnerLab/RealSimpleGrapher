'''
Configuration settings for Grapher gui
'''
import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'b')
class graphConfig():
    def __init__(self, name, ylim=[0,1], isScrolling=False, max_datasets = 3):
        self.name = name
        self.ylim = ylim
        self.isScrolling = isScrolling
        self.max_datasets = max_datasets
        self.graphs = 1 # just a single graph

class doubleGraphConfig():
    def __init__(self, tab, config1, config2):
        self.tab = tab
        self.config1 = config1
        self.config2 = config2
        self.graphs = 2


tabs =[
    graphConfig('current', max_datasets = 1),
    graphConfig('pmt', ylim=[0,30], isScrolling=True, max_datasets = 1),
    graphConfig('spectrum'),
    graphConfig('rabi'),
    doubleGraphConfig('carriers',
                      graphConfig('S12D52'), graphConfig('S12D12')),
    doubleGraphConfig('sidebands',
                      graphConfig('radial1'), graphConfig('radial2')),
]