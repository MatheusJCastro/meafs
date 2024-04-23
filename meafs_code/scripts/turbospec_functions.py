#####################################################
# MEAFS TurboEspectrum Functions                    #
# Matheus J. Castro                                 #
# v1.2                                              #
# Last Modification: 04/23/2024                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

from scipy.optimize import minimize
import pandas as pd
import numpy as np
import subprocess

from . import fit_functions as ff


def check_elem_configfl(fl_name, elem):
    # Function to find the desired element in the Turbospectrum2019 configuration file
    with open(fl_name, 'r') as file:
        fl = file.read()

    elem = "foreach " + elem + "_ab"
    pos = fl.find(elem)

    if pos == -1:
        return False
    else:
        return True


def change_spec_range_configfl(fl_name, lamb, cut_val):
    # Function to change the spectrum range in Turbospectrum2019 configuration file
    spec_range = [lamb - cut_val, lamb + cut_val]

    with open(fl_name, 'r') as file:
        fl = file.read()

    for i, str_i in enumerate(["set lam_min    = ", "set lam_max    = "]):
        pos = fl.find(str_i)
        # noinspection PyListCreation
        pos = [pos + fl[pos:].find("'") + 1]
        # noinspection
        pos.append(pos[0] + fl[pos[0]:].find("'"))
        fl = fl[:pos[0]] + str(spec_range[i]) + fl[pos[1]:]

    with open(fl_name, "w") as file:
        file.write(fl)


def change_abund_configfl(fl_name, elem, abund=None, find=True):
    # Function to change the element abundance in Turbospectrum2019 configuration file
    # or to find the actual value
    with open(fl_name, 'r') as file:
        fl = file.read()

    elem = "foreach " + elem + "_ab"
    pos = fl.find(elem)
    pos += fl[pos:].find("(") + 1
    pos_end = pos + fl[pos:].find(")")

    if find:
        abund = float(fl[pos:pos_end])
    else:
        fl = fl[:pos] + str(abund) + fl[pos_end:]

        with open(fl_name, "w") as file:
            file.write(fl)

    return abund


def run_configfl(config_fl):
    # Run Turbospectrum2019
    run = config_fl.split("/")[-1]
    config_fodler = config_fl.removesuffix(run)

    subprocess.check_output("cd \"{}\" && ./{}".format(config_fodler, run), shell=True)


def optimize_spec(spec_obs_cut, spec_conv, lamb, cut_val, continuum, init=None, iterac=100, convovbound=None,
                  wavebound=None):
    # Function to optimize the spectrum

    # Define initial values if not given
    if init is None:
        init = [0, 1, 3.85]
    if convovbound is None:
        convovbound = [3.5, 4.2]
    if wavebound is None:
        wavebound = [lamb-1, lamb+1]
    else:
        wavebound = [-wavebound, +wavebound]

    # First, apply a convolution of 3.85
    sp_convoluted = ff.spec_operations(spec_conv.copy(), convol=init[2])

    # Find the best parameters for lambda shift
    def opt_desloc_continuum(guess):
        sp_fit = ff.spec_operations(sp_convoluted.copy(), lamb_desloc=guess[0], continuum=guess[1], convol=0)
        return ff.chi2(spec_obs_cut, sp_fit)
    pars = minimize(opt_desloc_continuum, np.array([init[0], continuum]), method='Nelder-Mead',
                    options={"maxiter": iterac}, bounds=[wavebound, [continuum*0.9, continuum*1.1]]).x

    # pars = [pars[0], continuum]

    spec_obs_cut = ff.cut_spec(spec_obs_cut, lamb, cut_val=cut_val[1])
    spec_conv = ff.cut_spec(spec_conv, lamb, cut_val=cut_val[1])

    # Finally, find the best convolution
    def opt_convolution(guess):
        # noinspection PyTypeChecker
        sp_fit = ff.spec_operations(spec_conv.copy(), lamb_desloc=pars[0], continuum=pars[1], convol=guess[0])
        return ff.chi2(spec_obs_cut, sp_fit)
    par = minimize(opt_convolution, np.array([init[2]]), method='Nelder-Mead', options={"maxiter": iterac},
                   bounds=[convovbound]).x

    pars = np.append(pars, par, axis=0)
    # pars = [0, 1, 1]

    return pars


def optimize_abund(spec_obs_cut, config_fl, conv_name, elem, opt_pars, par, abund_lim, iterac=10):
    def opt_abund(abund):
        change_abund_configfl(config_fl, elem, find=False, abund=abund[0])
        run_configfl(config_fl)
        spec = pd.read_csv(conv_name, header=None, delimiter="\s+")
        # noinspection PyTypeChecker
        spec = ff.spec_operations(spec.copy(), lamb_desloc=opt_pars[0], continuum=opt_pars[1],
                                  convol=opt_pars[2])

        chi = ff.chi2(spec_obs_cut, spec)
        return chi

    par = minimize(opt_abund, np.array(par), method='Nelder-Mead', options={"maxiter": iterac},
                   bounds=[[par[0] - abund_lim, par[0] + abund_lim]]).x

    spec_conv = pd.read_csv(conv_name, header=None, delimiter="\s+")
    spec_fit = ff.spec_operations(spec_conv, lamb_desloc=opt_pars[0], continuum=opt_pars[1],
                                  convol=opt_pars[2])
    chi = ff.chi2(spec_obs_cut, spec_fit)

    return par, chi, spec_fit