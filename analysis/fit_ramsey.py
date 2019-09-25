from model import Model, ParameterInfo
import numpy as np

class RamseyDecay(Model):

	def __init__(self):
		self.parameters = {
			'freq':ParameterInfo('freq', 0, lambda x,y: 10000, vary = True),
            'tau':ParameterInfo('tau', 1, lambda x,y: 1000, vary=True),
            'startfrom': ParameterInfo('startfrom', 2, lambda x,y: 0, vary=True),
            'decayto': ParameterInfo('decayto', 3, lambda x,y: 0.5, vary=False),
            }

	def model(self, x, p):
		t = 1e-6*x
		w = 2*np.pi*p[0]
		tau = 1e-6*p[1]
		startfrom = p[2]
		decayto = p[3]

		return (startfrom-decayto)*np.exp(-t/tau)*np.cos(w*t) + decayto