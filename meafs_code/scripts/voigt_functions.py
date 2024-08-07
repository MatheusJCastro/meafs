"""
| MEAFS Voigt Functions
| Matheus J. Castro

| Voigt, Gaussian, Lorentzian module functions.
"""

from scipy.optimize import minimize
import pandas as pd
import numpy as np

from . import fit_functions as ff


def gaussian(x, b, c, a=1, d=0):
    """
    Gaussian function.

    .. math:: f(x) = a \\cdot \\exp\\left[\\frac{-(x - b)^2}{c \\cdot \\sqrt{2 \\cdot \\pi}}\\right] + d
        :label: gauss


    :param x: can be a list or a number.
    :param b: a single number.
    :param c: a single number.
    :param a: a single number.
    :param d: a single number.
    :return: :math:`f(x)` as a number or a list.
    """

    return a * np.exp(-(x - b)**2 / (c * np.sqrt(2 * np.pi))) + d


def lorentzian(x, b, c, a=1, d=0):
    """
    Lorentzian function.

    .. math:: g(x) = a \\cdot \\exp\\left[\\frac{c}{\\pi \\cdot ((x - b)^2 + c^2)}\\right] + d
        :label: loren

    :param x: can be a list or a number.
    :param b: a single number.
    :param c: a single number.
    :param a: a single number.
    :param d: a single number.
    :return: :math:`g(x)` as a number or a list.
    """

    return a * c / (np.pi * ((x - b)**2 + c**2)) + d


def voigt(x, b, c, a, d):
    """
    Voigt function.

    .. math::
        h(x) = a \\cdot f(x) \\cdot g(x) + d

    With :math:`f(x)` being the :eq:`gauss` and :math:`g(x)` being the :eq:`loren`.

    :param x: can be a list or a number.
    :param b: a single number.
    :param c: a single number.
    :param a: a single number.
    :param d: a single number.
    :return: :math:`h(x)` as a number or a list.
    """

    return a * gaussian(x, b, c) * lorentzian(x, b, c) + d


def find_func(type_func):
    """
    Determines the function to be called: Gaussian, Lorentzian or Voigt.

    :param type_func: string with the name of the function.
    :return: the function itself.
    """

    if type_func == "Gaussian":
        func = gaussian
    elif type_func == "Lorentzian":
        func = lorentzian
    elif type_func == "Voigt":
        func = voigt
    else:
        print("Function not recognized.")
        func = None
    return func


def optimize_spec(spec_obs_cut, type_synth, lamb, continuum, convovbound=None,
                  wavebound=None, iterac=100):
    """
    Fit of the Convolution and the Wavelength Shift using the minimization of the :math:`\\chi^2`
    with the Nelder-Mead method.

    :param spec_obs_cut: spectrum data.
    :param type_synth: type of the function to apply.
    :param lamb: current wavelength.
    :param continuum: continuum value.
    :param convovbound: range to fit the convolution.
    :param wavebound: range to fit the wavelength shift.
    :param iterac: maximum allowed iterations of the Nelder-Mead method.
    :return: the optimized parameters, the value of the minimum :math:`\\chi^2` and the spectrum
             generated with the best parameters.
    """

    if convovbound is None:
        convovbound = [0, 1]
    if wavebound is None:
        wavebound = [lamb-1, lamb+1]
    else:
        wavebound = [lamb-wavebound, lamb+wavebound]

    func = find_func(type_synth[1])

    x = np.linspace(min(spec_obs_cut.iloc[:, 0]), max(spec_obs_cut.iloc[:, 0]), 1000)

    a = -(continuum - spec_obs_cut.iloc[ff.bisec(spec_obs_cut, lamb), 1])
    b = lamb
    c = type_synth[2]
    d = continuum

    def fit(guess):
        bfit = guess[0]
        cfit = guess[1]
        sp_fit = [x, func(x, bfit, cfit, a, d)]
        return ff.chi2(spec_obs_cut, sp_fit)

    b, c = minimize(fit, np.array([b, c]), method='Nelder-Mead', bounds=[wavebound, convovbound],
                    options={"maxiter": iterac}).x

    # opt_pars = [lamb_desloc, continuum, convol]
    opt_pars = [b - lamb, d, c]
    spec_fit = pd.DataFrame({0: x, 1: func(x, b, c, a, d)})
    chi = ff.chi2(spec_obs_cut, spec_fit)

    return opt_pars, chi, spec_fit


def optimize_abund(spec_obs_cut, type_synth, lamb, opt_pars, iterac=100):
    """
    Fit of the Abundance using the minimization of the :math:`\\chi^2`
    with the Nelder-Mead method.

    :param spec_obs_cut: spectrum data.
    :param type_synth: type of the function to apply.
    :param lamb: current wavelength.
    :param opt_pars: the Continuum, Convolution and Wavelength Shift parameters.
    :param iterac: maximum allowed iterations of the Nelder-Mead method.
    :return: the abundance, the value of the minimum :math:`\\chi^2` and the spectrum
             generated with the best parameters.
    """

    func = find_func(type_synth[1])

    x = np.linspace(min(spec_obs_cut.iloc[:, 0]), max(spec_obs_cut.iloc[:, 0]), 1000)

    a = - (opt_pars[1] - spec_obs_cut.iloc[ff.bisec(spec_obs_cut, lamb), 1])
    b = lamb
    c = opt_pars[2]
    d = opt_pars[1]

    def fit(guess):
        afit = guess[0]
        sp_fit = [x, func(x, b, c, afit, d)]
        return ff.chi2(spec_obs_cut, sp_fit)

    a = minimize(fit, np.array([a]), method='Nelder-Mead',
                 options={"maxiter": iterac}).x

    par = a
    spec_fit = pd.DataFrame({0: x, 1: func(x, b, c, a, d)})
    chi = ff.chi2(spec_obs_cut, spec_fit)

    return par, chi, spec_fit
