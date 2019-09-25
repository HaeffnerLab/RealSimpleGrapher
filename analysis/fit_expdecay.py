# Fitter class for Gaussians

from model import Model, ParameterInfo
import numpy as np

class ExponentialDecay(Model):

    def __init__(self):
        self.parameters = {
            'tau':ParameterInfo('tau', 0, lambda x,y: 1000, vary=True),
            'startfrom': ParameterInfo('startfrom', 1, lambda x,y: 0, vary=True),
            'decayto': ParameterInfo('decayto', 2, lambda x,y: 0.5, vary=False),
            }

    def model(self, x, p):
        tau = p[0]
        startfrom = p[1]
        decayto = p[2]

        return startfrom + (decayto-startfrom)*(1-np.exp(-x/tau))