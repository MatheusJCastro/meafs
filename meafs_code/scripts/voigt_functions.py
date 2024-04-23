#####################################################
# MEAFS Voigt Functions                             #
# Matheus J. Castro                                 #
# v1.6                                              #
# Last Modification: 04/23/2024                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

from scipy.optimize import minimize
import pandas as pd
import numpy as np

from . import fit_functions as ff


def gaussian(x, b, c, a=1, d=0):
    return a * np.exp(-(x - b)**2 / (c * np.sqrt(2 * np.pi))) + d


def lorentzian(x, b, c, a=1, d=0):
    return a * c / (np.pi * ((x - b)**2 + c**2)) + d


def voigt(x, b, c, a, d):
    return a * gaussian(x, b, c) * lorentzian(x, b, c) + d


def find_func(type_func):
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
