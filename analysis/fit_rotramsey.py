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
            'omega_rabi': ParameterInfo('f_rabi', 0, lambda x, y: 0.01, vary=True),
            'stdev_l': ParameterInfo('stdev_l', 1, lambda x, y: 50.0, vary=True),
            'sideband_order': ParameterInfo('sideband_order', 2, lambda x, y: 4, vary = False),
            'f_trap': ParameterInfo('f_trap', 3, lambda x, y: 0.845, vary=False),
            'f_rot': ParameterInfo('f_rot', 4, lambda x, y: 0.1, vary=False),
            'delta': ParameterInfo('delta', 5, lambda x, y: 0, vary=False),
            'scale': ParameterInfo('scale,', 6, lambda x, y: 1.0, vary=False)
            }

    def model(self, x, p):

        omega_rabi = p[0]
        stdev_l = p[1]
        sideband_order = p[2]
        f_trap = p[3]
        f_rot = p[4]
        delta = p[5]
        scale = p[6]

        #calculate the radius of the ion 'ring' (half the distance between the ions)        
        r = (scc.e**2/(40*scc.atomic_mass*4*math.pi**2*(f_trap**2-f_rot**2)*1e12*16*math.pi*scc.epsilon_0))**(1./3)
        self.omega_r = scc.hbar/(4*40*scc.atomic_mass*r**2)

        result = self.rot_ramsey(1e-6*x,sideband_order,stdev_l,omega_rabi,delta,scale)

        return result

    def rot_ramsey(self, times, order, sigma_l, Omega_MHz, delta_kHz=0.0, scale=1.0):
        if sigma_l > 3000:
            sigma_l = 3000.0

        # Convert to SI units
        Omega = Omega_MHz*2*np.pi*1e6
        delta = delta_kHz*2*np.pi*1e3
        
        # Get distribution of l's, their respective detunings, and calculate the excitation vs. time
        (l_vals, c_ls) = self.calc_ls_cls(sigma_l)
        delta_ls = 2*self.omega_r*order*l_vals - delta  # Array of detunings, one for each l
        Omega_gens = np.sqrt(Omega**2 + delta_ls**2) #generalized Rabi frequencies
        u1s = np.pi*Omega_gens/(4*Omega)
        u2s = 1/2.0*np.outer(delta_ls, times)
        exc = scale * np.sum(np.outer(np.abs(c_ls)**2, np.ones(len(times)))
                           *(np.outer(2*Omega/Omega_gens**2*np.sin(u1s), np.ones(len(times)))
                           *(np.outer(Omega_gens*np.cos(u1s), np.ones(len(times))) * np.cos(u2s)
                            -np.outer(delta_ls*np.sin(u1s), np.ones(len(times))) * np.sin(u2s)    ))**2, axis=0)

        return exc

    def calc_ls_cls(self, sigma_l):
        """Returns an array of l values and their amplitudes, given a standard deviation sigma_l
        The distribution is Gaussian.
        The center of the distribution is chosen to be centered at 0, which can be done without loss of generality
            (all we care about is detunings, not absolute position in frequency space)
        The l values returned are integers within 4*sigma"""
        l_max = int(4*sigma_l)
        l_vals = np.arange(-l_max, l_max+1)
        c_ls_unnorm = np.exp(-l_vals**2/(4.0*sigma_l**2))
        c_ls = c_ls_unnorm/np.linalg.norm(c_ls_unnorm)
        return (l_vals, c_ls)

    def guess_omega_rabi(self, x, y):
        '''
        Take the first time the flop goes above the average excitation of the whole scan
        to be pi/4
        '''
        
        mean = np.mean(y)
        for x0, y0 in zip(x,y):
            if y0 > mean: break
        t_2pi  = 4*x0
        return 1/(t_2pi)