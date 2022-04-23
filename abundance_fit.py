#####################################################
# Abundance Fit                                     #
# Matheus J. Castro                                 #
# v2.4                                              #
# Last Modification: 03/18/2022                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

# For this code work with Turbospectrum2019, the Turbospectrum2019 folder must be in the same folder as this code

from astropy.convolution import Gaussian1DKernel, convolve
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import subprocess
import ctypes
import sys
import os


def open_files(list_name, observed_name, refer_name):
    # Function to open the needed files using PANDAS
    linelist = pd.read_csv(list_name, header=None, delimiter="\s+")
    spec_obs_1 = pd.read_csv(observed_name[0], header=None, delimiter="\s+")
    spec_obs_2 = pd.read_csv(observed_name[1], header=None, delimiter="\s+")
    refer_fl = pd.read_csv(refer_name, header=None, delimiter=",", index_col=0)

    return linelist, [spec_obs_1, spec_obs_2], refer_fl


def open_previous(linelist, fl_name="found_values.csv"):
    # Function to open the previous results and analyze it
    try:
        # Try to open
        prev = pd.read_csv(fl_name, delimiter=",")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # If file not found or empty database, create a new one and return
        return linelist, pd.DataFrame(columns=["Element", "Lambda (A)", "Lamb Shift", "Continuum", "Convolution",
                                      "Refer Abundance", "Fit Abundance", "Differ"])

    # Reads the existing data
    new_linelist = pd.DataFrame(columns=[0, 1])
    for i in range(len(linelist)):
        try:
            if linelist.iloc[i][0] == prev.iloc[i].Element and linelist.iloc[i][1] == prev.iloc[i]["Lambda (A)"]:
                if prev["Fit Abundance"].isnull().iloc[i] or prev.Differ.iloc[i] == 0:
                    new_linelist.loc[i] = linelist.iloc[i]
            else:
                new_linelist.loc[i] = linelist.iloc[i]
        except IndexError:
            new_linelist.loc[i] = linelist.iloc[i]

    return new_linelist, prev


def c_init(c_name):
    # Funtion to initialize the C shared library
    global c_lib
    c_lib = ctypes.CDLL("./{}".format(c_name))

    # Defining functions argument types
    c_lib.bisec.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_float]
    c_lib.bisec.restype = ctypes.c_int

    c_lib.chi2.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                           ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_int]
    c_lib.chi2.restype = ctypes.c_float

    return c_lib


def plot_spec(spec1, spec2, spec3, lamb, elem, show=False, save=True):
    # Plot the spectra
    plt.figure(figsize=(16, 9))

    plt.plot(spec1[0], spec1[1], label="Observed")
    plt.plot(spec2[0], spec2[1], label="Abundance Fit")
    if spec3 is not None:
        plt.plot(spec3[0], spec3[1], label="Final Fit")
    if lamb is not None:
        plt.axvline(lamb, color="red", label="Reference")

    plt.legend()

    if show:
        plt.show()
    if save:
        plt.savefig("Plots/fit_{}_{}_ang.pdf".format(elem, lamb))
    plt.close()


def check_elem_configfl(fl_name, elem):
    # Function to find the desired element in the Turbospectrum2019 configuration file
    with open(fl_name, 'r') as file:
        fl = file.read()

    elem = "foreach " + elem[:-1] + "_ab"
    pos = fl.find(elem)

    if pos == -1:
        return False
    else:
        return True


def bisec(spec, lamb):
    # Function to apply the bisection script to find a number position in an array

    # Uncomment the script bellow to use the C library (slower)
    # arr = spec[0].tolist()
    # arr_c = (ctypes.c_float * len(arr))(*arr)
    #
    # index = c_lib.bisec(arr_c, len(arr), lamb)
    #
    # return index

    # Bisection Script
    if lamb < spec.iloc[0][0]:
        return -1
    elif lamb > spec.iloc[-1][0]:
        return -1
    else:
        gap = [0, len(spec) - 1]

        while True:
            new_gap = gap[0] + (gap[1] - gap[0]) // 2

            if lamb < spec.iloc[new_gap][0]:
                gap[1] = new_gap
            else:
                gap[0] = new_gap

            if gap[0] + 1 == gap[1]:
                return gap[0]


def cut_spec(spc, lamb, cut_val=1.):
    # Function to restrict the array in the desired range
    val0 = bisec(spc, lamb - cut_val)
    val1 = bisec(spc, lamb + cut_val)

    return spc.iloc[val0:val1]


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

    elem = "foreach " + elem[:-1] + "_ab"
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


def run_configfl():
    # Run Turbospectrum2019
    subprocess.check_output("cd Turbospectrum2019/COM-v19.1 && ./CS31.com", shell=True)


def chi2(spec1, spec2):
    # Function to find the chi square of two arrays

    # Using C library
    spec1x = spec1[0].tolist()
    spec1y = spec1[1].tolist()

    spec1x = (ctypes.c_float * len(spec1x))(*spec1x)
    spec1y = (ctypes.c_float * len(spec1y))(*spec1y)

    spec2x = spec2[0].tolist()
    spec2y = spec2[1].tolist()

    spec2x = (ctypes.c_float * len(spec2x))(*spec2x)
    spec2y = (ctypes.c_float * len(spec2y))(*spec2y)

    return c_lib.chi2(spec1x, spec1y, len(spec1x), spec2x, spec2y, len(spec2x))

    # Using Python (slower)
    # sp1_interpol = np.array([])
    # sp2_interpol = np.array([])
    #
    # for i in spec2.iloc():
    #     pos = bisec(spec1, i[0])
    #     if pos != -1:
    #         x1 = spec1.iloc[pos][0]
    #         x2 = spec1.iloc[pos + 1][0]
    #         y1 = spec1.iloc[pos][1]
    #         y2 = spec1.iloc[pos + 1][1]
    #         x = i[0]
    #         y = y1 + (y2 - y1) / (x2 - x1) * (x - x1)
    #
    #         sp1_interpol = np.append(sp1_interpol, y)
    #         sp2_interpol = np.append(sp2_interpol, i[1])
    #
    # return sum((sp1_interpol - sp2_interpol)**2 / sp2_interpol)


def spec_operations(spec, lamb_desloc=0., continuum=1., convol=0.):
    # Function to apply lambda shift, continuum fit and convolution to the spectrum
    spec[0] = spec[0] + lamb_desloc
    spec[1] = spec[1] * continuum

    if convol != 0:
        try:
            # Apply the convolution using the Gaussian1DKernel function
            g = Gaussian1DKernel(stddev=convol)
            spec[1] = convolve(spec[1], g)  # convolution between the spectrum and the function above
        except ValueError:
            pass

    return spec


def optimize_spec(spec_obs_cut, spec_conv, lamb, cut_val):
    # Function to optimize the spectrum

    # First, apply a convolution of 3.85
    sp_convoluted = spec_operations(spec_conv.copy(), convol=3.85)

    # Find the best parameters for lambda shift and continuum
    def opt_desloc_continuum(guess):
        sp_fit = spec_operations(sp_convoluted.copy(), lamb_desloc=guess[0], continuum=guess[1], convol=0)
        return chi2(spec_obs_cut, sp_fit)
    pars = minimize(opt_desloc_continuum, np.array([0, 1]), method='Nelder-Mead').x

    spec_obs_cut = cut_spec(spec_obs_cut, lamb, cut_val=cut_val[1])
    spec_conv = cut_spec(spec_conv, lamb, cut_val=cut_val[1])

    # Finally, find the best convolution
    def opt_convolution(guess):
        sp_fit = spec_operations(spec_conv.copy(), lamb_desloc=pars[0], continuum=pars[1], convol=guess[0])
        return chi2(spec_obs_cut, sp_fit)
    par = minimize(opt_convolution, np.array([3.85]), method='Nelder-Mead', bounds=[[3.5, 4.2]]).x

    pars = np.append(pars, par, axis=0)
    # pars = [0, 1, 1]

    return pars


def adjust_abundance(linelist, spec_obs, conv_name, config_fl, refer_fl, cut_val=None, abund_lim_df=1., restart=False,
                     save_name="found_values.csv"):
    # Function to analyse the spectrum and find the fit values for it

    # For each fit parameter, a spectrum range can be selected
    # a value of 5, will select a total of 10 Angstroms with the element line wavelength in the middle
    if cut_val is None:
        cut_val = [10/2, 3/2, .2/2, 1/2]
        # spec range vals for [continuum, convolution, abundance, plot]

    if not restart:
        linelist, found_val = open_previous(linelist, fl_name=save_name)
    else:
        found_val = pd.DataFrame(columns=["Element", "Lambda (A)", "Lamb Shift", "Continuum", "Convolution",
                                          "Refer Abundance", "Fit Abundance", "Differ"])

    # For each line in the linelist file
    for i in range(len(linelist)):
        elem = linelist.iloc[i][0]
        lamb = linelist.iloc[i][1]

        print("Analysing the element {} for lambda {}. Line {} of {}.".format(elem, lamb, i+1, len(linelist)))

        abund_val_refer = float(refer_fl.loc[elem]) if not refer_fl.loc[elem].isnull().item() else 0
        abund_lim = abund_lim_df if abund_val_refer != 0 else 3
        index_append = linelist.index.tolist()[i]

        if check_elem_configfl(config_fl, elem) and spec_obs.iloc[0][0] <= lamb <= spec_obs.iloc[-1][0]:
            # Fit of lambda shift, continuum and convolution
            spec_obs_cut = cut_spec(spec_obs, lamb, cut_val=cut_val[0])
            change_spec_range_configfl(config_fl, lamb, cut_val[0])

            run_configfl()
            spec_conv = pd.read_csv(conv_name, header=None, delimiter="\s+")

            opt_pars = optimize_spec(spec_obs_cut, spec_conv, lamb, cut_val)
            # opt_pars = [0,0,0]

            print("\tLamb Shift:\t\t{:.4f}\n\tContinuum:\t\t{:.4f}\n\tConvolution:\t{:.4f}".format(opt_pars[0],
                                                                                                   opt_pars[1],
                                                                                                   opt_pars[2]))

            # Fit of abundance
            change_spec_range_configfl(config_fl, lamb, cut_val[3])
            spec_obs_cut = cut_spec(spec_obs, lamb, cut_val=cut_val[2])

            def mini_func(abund):
                change_abund_configfl(config_fl, elem, find=False, abund=abund[0])
                run_configfl()
                spec = pd.read_csv(conv_name, header=None, delimiter="\s+")
                spec = spec_operations(spec.copy(), lamb_desloc=opt_pars[0], continuum=opt_pars[1],
                                       convol=opt_pars[2])

                return chi2(spec_obs_cut, spec)

            par = minimize(mini_func, np.array([abund_val_refer]), method='Nelder-Mead', options={"maxiter": 10},
                           bounds=[[abund_val_refer-abund_lim, abund_val_refer+abund_lim]]).x

            print("\tAbundance:\t\t{:.4f}".format(par[0]))
            found_val.loc[index_append] = [elem, lamb, opt_pars[0], opt_pars[1], opt_pars[2], abund_val_refer, par[0],
                                           np.abs(par[0]-abund_val_refer)]

            # Plot of data
            spec_obs_cut = cut_spec(spec_obs, lamb, cut_val=cut_val[3])

            change_spec_range_configfl(config_fl, lamb, cut_val[3])
            run_configfl()

            spec_conv = pd.read_csv(conv_name, header=None, delimiter="\s+")
            spec_fit = spec_operations(spec_conv.copy(), lamb_desloc=opt_pars[0], continuum=opt_pars[1],
                                       convol=opt_pars[2])

            plot_spec(spec_obs_cut, spec_conv, spec_fit, lamb, elem)

            # Return the Turbospectrum2019 configuration file to original abundance value
            change_abund_configfl(config_fl, elem, find=False, abund=abund_val_refer)
        else:
            found_val.loc[index_append] = [elem, lamb, np.nan, np.nan, np.nan, abund_val_refer, np.nan, np.nan]
            print("\tValue not found.")

        # Write the line result to the csv file
        found_val.to_csv(save_name, index=False, float_format="%.4f")


def main():
    # Main subroutine to call the functions
    if not os.path.exists("Plots"):
        os.mkdir("Plots")

    # Required path files for the script work
    list_name = "Heavylist.txt"  # File with the lines to analyze
    observed_name = ["cs340n.dat", "cs437n.dat"]  # observed spectra
    conv_name = "Turbospectrum2019/COM-v19.1/syntspec/CS31-HFS-Vtest.spec"  # simulated spectrum
    config_fl = "Turbospectrum2019/COM-v19.1/CS31.com"  # Turbospectrum2019 configuration file
    refer_name = "refer_values.csv"  # values of reference for each element (0 for no reference)

    # Open some files
    linelist, spec_obs, refer_fl = open_files(list_name, observed_name, refer_name)

    # Adjust parameters for each spectra declared
    # Caution: be aware of data overlay on the final csv file
    for spec in spec_obs:
        adjust_abundance(linelist, spec, conv_name, config_fl, refer_fl, restart=False)


if __name__ == '__main__':
    c_lib = c_init("bisec_interpol.so")  # initialize the C library
    main()  # call main subroutine
