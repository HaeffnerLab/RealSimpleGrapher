'''
Configuration settings for the RSG.
'''

import pyqtgraph as pg
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'y')

class traceListConfig():
    """
    Config for the traceList widget. Mostly concerns its color.
    """
    def __init__(self, background_color='black', use_trace_color=False):
        self.background_color = background_color
        self.use_trace_color = use_trace_color

class graphConfig():
    """
    Config for an individual graph within a GridGraphWindow.
    Sets graphing-related settings such as axes limits and horizontal/vertical lines.
    """
    def __init__(self, name, ylim=[0,1], isScrolling=False, max_datasets=20,
                 show_points=True, grid_on=False, scatter_plot='all', isImages=False,
                 isHist=False, line_param=None, vline=None, vline_param=None, hline=None, hline_param=None):
        self.name = name
        self.ylim = ylim
        self.isScrolling = isScrolling
        self.max_datasets = max_datasets
        self.graphs = 1
        self.show_points = show_points
        self.grid_on = grid_on
        self.scatter_plot = scatter_plot
        self.isImages = isImages
        self.isHist = isHist
        self.line_param = line_param
        self.vline = vline
        self.vline_param = vline_param
        self.hline = hline
        self.hline_param = hline_param

class gridGraphConfig():
    """
    Config for a GridGraphWindow (i.e. a tab).
    Sets the layout of the graphs on the tab.
    """
    def __init__(self, tab, config_list):
        self.tab = tab
        self.config_list = config_list[0::3]
        self.row_list = config_list[1::3]
        self.column_list = config_list[2::3]
        self.graphs = len(self.config_list)


"""
The actual config of the RSG is set here.
"""
tabs = [
    gridGraphConfig('Temperature', [graphConfig('Lakeshore 336 Temperature', max_datasets=1), 0, 0]),
    gridGraphConfig('Pressure', [graphConfig('Twistorr 74 Pressure', max_datasets=1), 0, 0]),
    gridGraphConfig('SLS', [graphConfig('SLS Locking Output', max_datasets=3), 0, 0]),
    gridGraphConfig('RGA', [graphConfig('RGA Sweeps', max_datasets=3), 0, 0]),
    gridGraphConfig('PMT', [graphConfig('pmt', ylim=[0, 30], isScrolling=True, max_datasets=1, show_points=False), 0, 0]),
    gridGraphConfig('local_stark', [
                      graphConfig('ms_local_stark'), 0, 0,
                      graphConfig('ms_local_stark_detuning'), 1, 0,
                      graphConfig('vaet_local_stark'), 0, 1,
                      graphConfig('vaet_local_stark_detuning'), 1, 1])
]
