# Fitter class for Rabi flops

from .model import Model, ParameterInfo
from .rabi.motional_distribution import motional_distribution as md
from .rabi.rabi_coupling import rabi_coupling as rc
import scipy.constants as scc

import math
import numpy as np

class RotRamsey(Model):

    def __init__(self):
        self.parameters = {
            'stdev_l': ParameterInfo('stdev_l', 0, lambda x, y: 50.0, vary=True),
            'sideband_order': ParameterInfo('sideband_order', 1, lambda x, y: 1, vary = False),
            'f_trap': ParameterInfo('f_trap', 2, lambda x, y: 1.5, vary=False),
            'f_rot': ParameterInfo('f_rot', 3, lambda x, y: 0.1, vary=False),
            'delta': ParameterInfo('delta', 4, lambda x, y: 5, vary=True),
            'scale': ParameterInfo('scale,', 5, lambda x, y: 1.0, vary=True),
            'contrast': ParameterInfo('contrast,', 6, lambda x, y: 1.0, vary=True),
            'phase': ParameterInfo('phase,', 7, lambda x, y: 0.0, vary=True),
            }

    def model(self, x, p):

        stdev_l = p[0]
        sideband_order = p[1]
        f_trap = p[2]
        f_rot = p[3]
        delta = p[4]
        scale = p[5]
        contrast =  p[6]
        phase = p[7]

        #calculate the radius of the ion 'ring' (half the distance between the ions)        
        r = (scc.e**2/(40*scc.atomic_mass*4*math.pi**2*(f_trap**2-f_rot**2)*1e12*16*math.pi*scc.epsilon_0))**(1./3)
        self.omega_r = scc.hbar/(4*40*scc.atomic_mass*r**2)

        result = self.rot_ramsey(1e-6*x, sideband_order, stdev_l, delta, scale, contrast, phase)

        return result

    def rot_ramsey(self, times, order, sigma_l, delta_kHz=0.0, scale=1.0, contrast=1.0, phase_deg=0.0):
        if sigma_l > 3000:
            sigma_l = 3000.0

        # Convert to SI units
        delta = delta_kHz*2*np.pi*1e3
        
        sigma_f = 2*self.omega_r*order*sigma_l               # Frequency-space standard deviation of the line
        Ct = contrast*np.exp(-(sigma_f*times)**2/2.0)        # Inverse Fourier transform of Gaussian lineshape from frequency domain to time domain
        exc =  scale * (Ct*np.cos(delta*times-phase_deg*np.pi/180) + 1.0)/2.0

        return exc