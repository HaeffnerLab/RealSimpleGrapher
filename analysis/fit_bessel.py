# Fitter class for Lorentzians

from model import Model, ParameterInfo
import numpy as np
import scipy.special as sp

class Bessel(Model):

    def __init__(self):
        self.parameters = {
            'center': ParameterInfo('center', 0, self.guess_center),
            'scale': ParameterInfo('scale', 1, self.guess_scale),
            'fwhm': ParameterInfo('fwhm', 2, self.guess_fwhm),
            'offset': ParameterInfo('offset', 3, self.guess_offset),
            'modDepth': ParameterInfo('modDepth', 4, self.guess_modDepth),
            'driveRF': ParameterInfo('driveRF', 5, self.guess_driveRF)
            }

    def model(self, x, p):
        '''
        Base Bessel function modulated spectrum model for micromotion.
        Using definition from Pruttivarasin thesis. 
        p = [center, scale, gamma, offset, modulation depth]
        '''
        p[2] = abs(p[2]) # fwhm is positive
        return p[3] +  p[1]*p[2]*0.5*((sp.jv(-6,p[4])**2/((x - p[0] - 6*p[5])**2 + (0.5*p[2])**2)) + 
               (sp.jv(-5,p[4])**2/((x - p[0] - 5*p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(-4,p[4])**2/((x - p[0] - 4*p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(-3,p[4])**2/((x - p[0] -3*p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(-2,p[4])**2/((x - p[0] -2*p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(-1,p[4])**2/((x - p[0] - p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(0,p[4])**2/((x - p[0])**2 + (0.5*p[2])**2)) +
               (sp.jv(1,p[4])**2/((x - p[0] + p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(2,p[4])**2/((x - p[0] + 2*p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(3,p[4])**2/((x - p[0] + 3*p[5])**2 + (0.5*p[2])**2)) +
               (sp.jv(4,p[4])**2/((x - p[0] + 4*p[5])**2 + (0.5*p[2])**2)) + 
               (sp.jv(5,p[4])**2/((x - p[0] + 5*p[5])**2 + (0.5*p[2])**2)) + 
               (sp.jv(6,p[4])**2/((x - p[0] + 6*p[5])**2 + (0.5*p[2])**2)))

    def guess_center(self, x, y):
        max_index = np.argmax(y)
        return x[max_index]

    def guess_scale(self, x, y):
        return 1500.0
    
    def guess_fwhm(self, x, y):
        return (max(x) - min(x))/6.0
    
    def guess_offset(self, x, y):
        return np.min(y)

    def guess_modDepth(self, x, y):
        return 0.2

    def guess_driveRF(self, x ,y):
        return 48.537
