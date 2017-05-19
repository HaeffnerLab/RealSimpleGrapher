# test script for Lorentzian fits
from model_test import ModelTest
from fit_bessel import Bessel

test = ModelTest(Bessel, 'Bessel')
true_params = [130., 1., 5., 0.1, 1]
test.generate_data(100, 200, 200, 0.02, 0.5, true_params)
test.fit()
test.print_results()
test.plot()
