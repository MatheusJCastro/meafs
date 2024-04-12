#!/usr/bin/env python3

#####################################################
# Abundance Analysis                                #
# Matheus J. Castro                                 #
# v3.0                                              #
# Last Modification: 07/01/2022                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

# This program generates graphics to analyse the results obtained with the abundance_fit.py

# For this code work, it must be in the same folder as the abundance_fit.py file

import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd
import numpy as np
import sys
import os

# Import the main script
try:
    import abundance_fit as ab_fit
except ModuleNotFoundError:
    from . import abundance_fit as ab_fit


def erase_emission_order(abund):
    # Function to erase the emission order in the database
    new_elem = []
    for i in range(len(abund)):
        new_elem.append(abund.Element.iloc[i][:-1])

    abund.Element = new_elem

    return abund


def erase_null_abund(abund):
    # Function to erase the empty slots in the database
    abund = abund[abund["Fit Abundance"].notnull()]
    return abund


def plot_abund_hist(abund, elements, folder):
    # Plot histograms for abundance for each element
    # and trace a gaussian with the mean and standard deviation
    for i in elements:
        elem_abunds = abund["Fit Abundance"][abund.Element == i]

        plt.figure(figsize=(16, 9))

        plt.title("Found Abundances for Element {}".format(i), fontsize=24)

        plt.xlabel("Values", fontsize=20)
        plt.ylabel("Frequency", fontsize=20)

        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)

        plt.hist(elem_abunds, bins=20, density=True, label="Data", color="Blue", edgecolor="black", linewidth=1.5,
                 zorder=2)

        if len(elem_abunds) > 1 and sum(elem_abunds) != 0:
            mean, std = norm.fit(elem_abunds)

            xmin, xmax = plt.xlim()
            x = np.linspace(xmin, xmax, 100)
            y = norm.pdf(x, mean, std)

            plt.plot(x, y, color="Black", label="Gaussian Fit\nMean: {:.2f}\nStd: {:.2f}".format(mean, std), zorder=3)

        plt.grid(zorder=1)
        plt.legend(fontsize=18)

        plt.savefig(folder+"Abundance_Analysis/Abundance_Hist/hist_abundance_{}.pdf".format(i))
        plt.close()


def plot_differ_hist(abund, elements, folder):
    # Plot histograms for abundance shift for each element
    # and trace a gaussian with the mean and standard deviation
    for i in elements:
        elem_differ = abund["Differ"][abund.Element == i]

        plt.figure(figsize=(16, 9))

        plt.title("Difference of Expected and Found Abundances for Element {}".format(i), fontsize=24)

        plt.xlabel("Values", fontsize=20)
        plt.ylabel("Frequency", fontsize=20)

        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)

        plt.hist(elem_differ, bins=20, density=True, label="Data", color="Blue", edgecolor="black", linewidth=1.5,
                 zorder=2)

        if len(elem_differ) > 1 and sum(elem_differ) != 0:
            mean, std = norm.fit(elem_differ)

            xmin, xmax = plt.xlim()
            x = np.linspace(xmin, xmax, 100)
            y = norm.pdf(x, mean, std)

            plt.plot(x, y, color="Black", label="Gaussian Fit\nMean: {:.2f}\nStd: {:.2f}".format(mean, std), zorder=3)

        plt.grid(zorder=1)
        plt.legend(fontsize=18)

        plt.savefig(folder+"Abundance_Analysis/Difference_Hist/hist_differ_{}.pdf".format(i))
        plt.close()


def plot_abund_box(abund, elements, folder):
    abund_matrix = []
    for i in elements:
        abund_matrix.append(abund["Fit Abundance"][abund.Element == i])

    plt.figure(figsize=(16, 9))

    plt.title("Elements Abundances", fontsize=24)

    plt.xlabel("Element", fontsize=20)
    plt.ylabel("Abundance", fontsize=20)

    plt.xticks(fontsize=18)
    plt.yticks(np.linspace(-4, 4, 21), fontsize=18)

    bp = plt.boxplot(abund_matrix, labels=elements, showmeans=True, meanline=True,
                     flierprops={"markerfacecolor": "red"}, patch_artist=True,
                     medianprops={"linestyle": "--", "color": "black"},
                     meanprops={"linestyle": ":", "color": "black"})

    plt.legend([bp["boxes"][0], bp["caps"][0], bp["medians"][0], bp["means"][0], bp["fliers"][0]],
               ["Confidence Level", "Max and min", "Median", "Mean", "Outliers"], fontsize=18)
    plt.grid(which="both", axis="y")
    plt.tight_layout()

    plt.savefig(folder+"Abundance_Analysis/Abundance_box.pdf")
    plt.close()


def get_spectrum(fit_data, conv_name, config_fl, elem, abundance_shift=0., cut_val=1.):
    # Function to get the observed spectrum in the desired range

    # Get data from fit
    lamb = fit_data["Lambda (A)"]
    abundance = fit_data["Fit Abundance"] + abundance_shift

    # Run the model with the desired abundance
    ab_fit.change_spec_range_configfl(config_fl, lamb, cut_val)
    ab_fit.change_abund_configfl(config_fl, elem, find=False, abund=abundance)
    ab_fit.run_configfl(config_fl)

    # Read and cut the model spectrum to the desired range
    spec = pd.read_csv(conv_name, header=None, delimiter="\s+")
    # spec = ab_fit.cut_spec(spec, lamb, cut_val/2)

    # Apply the fit resolutions to the spectra
    spec = ab_fit.spec_operations(spec.copy(), lamb_desloc=fit_data["Lamb Shift"], continuum=fit_data.Continuum,
                                  convol=fit_data.Convolution)

    return spec


def get_diff(spec1, spec2):
    # Function to get the difference of observed and model spectrum
    lambs = np.array([])
    sp1_interpol = np.array([])
    sp2_interpol = np.array([])

    for i in spec2.iloc():
        pos = ab_fit.bisec(spec1, i[0])
        if pos != -1:
            x1 = spec1.iloc[pos][0]
            x2 = spec1.iloc[pos + 1][0]
            y1 = spec1.iloc[pos][1]
            y2 = spec1.iloc[pos + 1][1]
            x = i[0]
            y = y1 + (y2 - y1) / (x2 - x1) * (x - x1)

            lambs = np.append(lambs, x)
            sp1_interpol = np.append(sp1_interpol, y)
            sp2_interpol = np.append(sp2_interpol, i[1])

    if len(lambs) == 0:
        return -1
    else:
        return [lambs, sp2_interpol-sp1_interpol]


def plot_lines(obs_specs, abund, refer_fl, conv_name, config_fl, folder, order_sep, cut_val=.5, abundance_shift=.1,
               drop=0):
    # Plot the spectrum fit and the observed one
    abund.drop(range(drop), inplace=True)

    for i in range(len(abund)):
        elem = abund.Element.iloc[i]
        lamb = abund["Lambda (A)"].iloc[i]
        abundance = abund["Fit Abundance"].iloc[i]

        order = ""
        if order_sep == "1":
            order = elem[-1]
            elem = elem[:-1]

        spec_obs = obs_specs[0]
        if lamb > spec_obs[0].iloc[-1]:
            spec_obs = obs_specs[1]

        spec_obs = ab_fit.cut_spec(spec_obs, lamb, cut_val)

        spec_fit = get_spectrum(abund.iloc[i], conv_name, config_fl, elem)
        spec_fit_under = get_spectrum(abund.iloc[i], conv_name, config_fl, elem, abundance_shift=+abundance_shift)
        spec_fit_above = get_spectrum(abund.iloc[i], conv_name, config_fl, elem, abundance_shift=-abundance_shift)
        spec_no = get_spectrum(abund.iloc[i], conv_name, config_fl, elem, abundance_shift=-99999)

        # Write the refer value back
        abund_val_refer = float(refer_fl.loc[elem]) if not refer_fl.loc[elem].isnull().item() else 0
        ab_fit.change_abund_configfl(config_fl, elem, find=False, abund=abund_val_refer)

        res_fit = get_diff(spec_obs, spec_fit)
        res_fit_under = get_diff(spec_obs, spec_fit_under)
        res_fit_above = get_diff(spec_obs, spec_fit_above)
        res_no = get_diff(spec_obs, spec_no)

        if res_fit == -1 or res_fit_under == -1 or res_fit_above == -1 or res_no == -1:
            continue

        max_lim = 1.05 * abs(max([max(res_fit[1], key=abs), max(res_fit_above[1], key=abs),
                                  max(res_fit_under[1], key=abs), max(res_no[1], key=abs)], key=abs))

        plt.figure(figsize=(16, 9))
        if order == "2":
            plt.suptitle("{} II at {:.2f} \u212b".format(elem, lamb), fontsize=24)
        elif order == "1":
            plt.suptitle("{} I at {:.2f} \u212b".format(elem, lamb), fontsize=24)
        else:
            plt.suptitle("{} at {:.2f} \u212b".format(elem, lamb), fontsize=24)

        # noinspection PyTypeChecker
        plt.subplot(3, 1, (1, 2))

        plt.ylabel("Normalized Flux", fontsize=20)

        plt.xlim(min(spec_obs[0]), max(spec_obs[0]))

        plt.xticks(fontsize=0)
        plt.yticks(fontsize=18)

        plt.plot(spec_obs[0], spec_obs[1], "+", label="Data Point", markersize=10, color="black")
        plt.axvline(x=lamb, color="red", linestyle=":", zorder=0, linewidth=1.8)

        plt.plot(spec_fit[0], spec_fit[1], "-", label="A({}) {:.2f}".format(elem, abundance), linewidth=1.8,
                 color="blue")
        plt.fill_between(spec_fit[0], spec_fit_above[1], spec_fit_under[1], alpha=0.8, color="lightblue",
                         label="A({}) {:.2f} \u00b1 {:.1f}".format(elem, abundance, abundance_shift))
        plt.plot(spec_no[0], spec_no[1], "--", label="No {}".format(elem), linewidth=1.5, color="gray")

        plt.grid(zorder=1)
        plt.legend(fontsize=18)

        plt.subplot(313)

        plt.xlabel("Wavelength (\u212b)", fontsize=20)
        plt.ylabel("Residuals", fontsize=20)

        plt.xlim(min(spec_obs[0]), max(spec_obs[0]))
        plt.ylim(-max_lim, max_lim)

        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)

        plt.axhline(y=0, color="black")
        plt.axvline(x=lamb, color="red", linestyle=":", zorder=0, linewidth=1.8)

        plt.plot(res_fit[0], res_fit[1], "-", linewidth=1.8, color="blue")
        plt.fill_between(res_fit_above[0], res_fit_above[1], res_fit_under[1], alpha=0.8, color="lightblue")
        plt.plot(res_no[0], res_no[1], "--", linewidth=1.5, color="gray")

        plt.grid(zorder=1)

        plt.tight_layout()
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.savefig(folder+"Abundance_Analysis/Lines_Plot/fit_{}_{}_ang.pdf".format(elem+order, lamb))
        plt.close()

        print("{} of {} finished.".format(i+1, len(abund)))


def folders_creation(folder):
    # Subroutine to create necessary folders
    if not os.path.exists(folder+"Abundance_Analysis"):
        os.mkdir(folder+"Abundance_Analysis")
    if not os.path.exists(folder+"Abundance_Analysis/Abundance_Hist"):
        os.mkdir(folder+"Abundance_Analysis/Abundance_Hist")
    if not os.path.exists(folder+"Abundance_Analysis/Difference_Hist"):
        os.mkdir(folder+"Abundance_Analysis/Difference_Hist")
    if not os.path.exists(folder+"Abundance_Analysis/Lines_Plot"):
        os.mkdir(folder+"Abundance_Analysis/Lines_Plot")


def main(args):
    # Main Routine

    # Arguments Menu Call
    config_name = ab_fit.args_menu(args)

    # Read Configuration File
    list_name, refer_name, type_synth, config_fl, conv_name, folder, observed_name = ab_fit.read_config(config_name)
    order_sep = list_name[2]

    fl_name = folder+"found_values.csv"  # result file

    linelist, refer_fl, spec_obs = ab_fit.open_files(list_name, observed_name, refer_name)

    # Create necessary folders
    folders_creation(folder)

    # Read results and erase empty ones
    abund = pd.read_csv(fl_name)
    abund = erase_null_abund(abund)

    # Plot spectra graphics
    plot_lines(spec_obs, abund, refer_fl, conv_name, config_fl, folder, order_sep)

    # Erase emission order and create an array with elements
    if order_sep == "1":
        abund = erase_emission_order(abund)
    elements = abund.Element.unique()

    # Plot boxplot
    plot_abund_box(abund, elements, folder)

    # Plot histograms
    plot_abund_hist(abund, elements, folder)
    plot_differ_hist(abund, elements, folder)


if __name__ == '__main__':
    arg = sys.argv[1:]
    main(arg)
