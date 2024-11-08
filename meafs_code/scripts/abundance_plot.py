#!/usr/bin/env python3
"""
| MEAFS Abundance Analysis
| Matheus J. Castro

| This program generates graphics to analyse the results obtained with the abundance_fit.py
| For this code work, it must be in the same folder as the *abundance_fit.py* file
"""

import matplotlib.pyplot as plt
from scipy.stats import norm
from PyQt6 import QtCore, QtGui
from pathlib import Path
import pandas as pd
import numpy as np
import sys
import os

# Import the main script
try:
    import abundance_fit as ab_fit
except ModuleNotFoundError:
    from . import abundance_fit as ab_fit

try:
    import turbospec_functions as tf
except ModuleNotFoundError:
    from . import turbospec_functions as tf

try:
    import fit_functions as ff
except ModuleNotFoundError:
    from . import fit_functions as ff

try:
    import voigt_functions as vf
except ModuleNotFoundError:
    from . import voigt_functions as vf


def erase_emission_order(abund):
    """
    Erase the emission order in the database.

    :param abund: pandas element with the abundances for each line.
    :return: the abundance dataframe without the emission orders.
    """

    new_elem = []
    for i in range(len(abund)):
        new_elem.append(abund.Element.iloc[i][:-1])

    abund.Element = new_elem

    return abund


def erase_null_abund(abund):
    """
    Erase the empty slots in the database.

    :param abund: pandas element with the abundances.
    :return: the abundance dataframe without the null elements.
    """

    abund = abund[abund["Fit Abundance"].notnull()]
    return abund


def plot_abund_hist(abund, elements, folder, ui=None, bins=20):
    """
    Creeate histograms for abundance for each element
    and trace a gaussian with the mean and standard deviation.

    :param abund: pandas element with the abundances.
    :param elements: elements to create histograms.
    :param folder: directory to be saved.
    :param ui: the main ui class in the GUI.
    :param bins: define the number of bins for the histogram.
    """

    for i in elements:
        elem_abunds = abund["Fit Abundance"][abund.Element == i]

        plt.figure(figsize=(16, 9))

        plt.title("Found Abundances for Element {}".format(i), fontsize=24)

        plt.xlabel("Values", fontsize=20)
        plt.ylabel("Frequency", fontsize=20)

        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)

        plt.hist(elem_abunds, bins=bins, density=True, label="Data", color="Blue", edgecolor="black", linewidth=1.5,
                 zorder=2)

        if len(elem_abunds) > 1 and sum(elem_abunds) != 0:
            mean, std = norm.fit(elem_abunds)

            xmin, xmax = plt.xlim()
            x = np.linspace(xmin, xmax, 100)
            y = norm.pdf(x, mean, std)

            plt.plot(x, y, color="Black", label="Gaussian Fit\nMean: {:.2f}\nStd: {:.2f}".format(mean, std), zorder=3)

        plt.grid(zorder=1)
        plt.legend(fontsize=18)
        plt.tight_layout()

        main_path = Path(folder).joinpath("Abundance_Analysis", "Abundance_Hist")
        fig_path = main_path.joinpath("hist_abundance_{}.pdf".format(i))
        plt.savefig(fig_path)
        plt.close()

        if ui is not None:
            pixmap = QtGui.QPixmap(str(fig_path))
            ui.abundhistplotimage.setPixmap(pixmap.scaled(ui.scale))
            ui.abundhistplotimage.setFixedSize(ui.scale)

            QtCore.QCoreApplication.processEvents()


def plot_differ_hist(abund, elements, folder, ui=None, bins=20):
    """
    Plot histograms for abundance shift for each element
    and trace a gaussian with the mean and standard deviation

    :param abund: pandas element with the abundances.
    :param elements: elements to create histograms.
    :param folder: directory to be saved.
    :param ui: the main ui class in the GUI.
    :param bins: define the number of bins for the histogram.
    """

    for i in elements:
        elem_differ = abund["Differ"][abund.Element == i]

        plt.figure(figsize=(16, 9))

        plt.title("Difference of Expected and Found Abundances for Element {}".format(i), fontsize=24)

        plt.xlabel("Values", fontsize=20)
        plt.ylabel("Frequency", fontsize=20)

        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)

        plt.hist(elem_differ, bins=bins, density=True, label="Data", color="Blue", edgecolor="black", linewidth=1.5,
                 zorder=2)

        if len(elem_differ) > 1 and sum(elem_differ) != 0:
            mean, std = norm.fit(elem_differ)

            xmin, xmax = plt.xlim()
            x = np.linspace(xmin, xmax, 100)
            y = norm.pdf(x, mean, std)

            plt.plot(x, y, color="Black", label="Gaussian Fit\nMean: {:.2f}\nStd: {:.2f}".format(mean, std), zorder=3)

        plt.grid(zorder=1)
        plt.legend(fontsize=18)
        plt.tight_layout()

        main_path = Path(folder).joinpath("Abundance_Analysis", "Difference_Hist")
        fig_path = main_path.joinpath("hist_differ_{}.pdf".format(i))
        plt.savefig(fig_path)
        plt.close()

        if ui is not None:
            pixmap = QtGui.QPixmap(str(fig_path))
            ui.differhistplotimage.setPixmap(pixmap.scaled(ui.scale))
            ui.differhistplotimage.setFixedSize(ui.scale)

            QtCore.QCoreApplication.processEvents()


def plot_abund_box(abund, elements, folder, ui=None):
    """
    Create the abundance box plot.

    :param abund: pandas element with the abundances.
    :param elements: elements to create histograms.
    :param folder: directory to be saved.
    :param ui: the main ui class in the GUI.
    """

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

    main_path = Path(folder).joinpath("Abundance_Analysis")
    fig_path = main_path.joinpath("Abundance_box.pdf")
    plt.savefig(fig_path)
    plt.close()

    if ui is not None:
        pixmap = QtGui.QPixmap(str(fig_path))
        ui.boxplotimage.setPixmap(pixmap.scaled(ui.scale))
        ui.boxplotimage.setFixedSize(ui.scale)


def get_spectrum(fit_data, conv_name, config_fl, elem, abundance_shift=0., cut_val=1.):
    """
    Function to get the synthetic spectrum in the desired range.

    :param fit_data: pandas dataframe with the results.
    :param conv_name: file name of the TurboSpectrum output file.
    :param config_fl: file name of the TurboSpectrum configuration file.
    :param elem: element to be plotted.
    :param abundance_shift: overall shift in abundance, if needed.
    :param cut_val: range to plot.
    :return: the final spectrum.
    """

    # Get data from fit
    lamb = fit_data["Lambda (A)"]
    abundance = fit_data["Fit Abundance"] + abundance_shift

    # Run the model with the desired abundance
    tf.change_spec_range_configfl(config_fl, lamb, cut_val)
    tf.change_abund_configfl(config_fl, elem, find=False, abund=abundance)
    tf.run_configfl(config_fl)

    # Read and cut the model spectrum to the desired range
    spec = pd.read_csv(conv_name, header=None, delimiter=r"\s+")
    # spec = ab_fit.cut_spec(spec, lamb, cut_val/2)

    # Apply the fit resolutions to the spectra
    spec = ff.spec_operations(spec.copy(), lamb_desloc=fit_data["Lamb Shift"], continuum=fit_data.Continuum,
                              convol=fit_data.Convolution)

    return spec


def get_diff(spec1, spec2):
    """
    Get the difference of observed and synthetic spectrum.

    :param spec1: first spectrum.
    :param spec2: second spectrum.
    :return: -1 if it finds nothing; otherwise the difference.
    """

    lambs = np.array([])
    sp1_interpol = np.array([])
    sp2_interpol = np.array([])

    for i in spec2.iloc():
        pos = ff.bisec(spec1, i[0])
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


def plot_lines(obs_specs, abund, refer_fl, type_synth, folder, cut_val=.5, abundance_shift=.1,
               drop=0, ui=None):
    """
    Plot the spectrum fit and the observed one

    :param obs_specs: spectrum data.
    :param abund: abundance pandas object.
    :param refer_fl: file name of the reference abundances file.
    :param type_synth: type of the current synthetics spectrum generator.
    :param folder: directory to save.
    :param cut_val: range to plot the lines.
    :param abundance_shift: overall abundance shift.
    :param drop: remove elements of the ``abund`` dataframe.
    :param ui: the main ui class in the GUI.
    """

    if len(abund) > 1:
        abund.drop(range(drop), inplace=True)

    if ui is not None:
        ui.progressvalue.setText("{}/{}".format(0, len(abund)))

    for i in range(len(abund)):
        if ui is not None:
            # Allow QT to actualize the UI while in the loop
            QtCore.QCoreApplication.processEvents()
            if ui.stop_state:
                ui.stop_state = False
                return

        elem = abund.Element.iloc[i]
        lamb = abund["Lambda (A)"].iloc[i]
        abundance = abund["Fit Abundance"].iloc[i]

        elem, order = ab_fit.check_order(elem)

        spec_obs = obs_specs[0]
        count = 1
        while lamb+cut_val > spec_obs[0].iloc[-1]:
            spec_obs = obs_specs[count]
            count += 1

        spec_obs = ff.cut_spec(spec_obs, lamb, cut_val)

        if type_synth[0] == "TurboSpectrum":
            spec_fit = get_spectrum(abund.iloc[i], type_synth[1], type_synth[2], elem)
            spec_fit_under = get_spectrum(abund.iloc[i], type_synth[1], type_synth[2], elem,
                                          abundance_shift=+abundance_shift)
            spec_fit_above = get_spectrum(abund.iloc[i], type_synth[1], type_synth[2], elem,
                                          abundance_shift=-abundance_shift)
            spec_no = get_spectrum(abund.iloc[i], type_synth[1], type_synth[2], elem,
                                   abundance_shift=-50)

            # Write the refer value back
            try:
                abund_val_refer = float(refer_fl.loc[elem, "value"]) if not refer_fl.loc[elem].isnull().item() else 0
            except KeyError:
                abund_val_refer = 0

            tf.change_abund_configfl(type_synth[2], elem, find=False, abund=abund_val_refer)
        elif type_synth[0] == "Equivalent Width":
            opt_pars = [abund["Lamb Shift"].iloc[i],
                        abund["Continuum"].iloc[i],
                        abund["Convolution"].iloc[i]]
            par = [abund["Fit Abundance"].iloc[i]]

            func = vf.find_func(type_synth[1])
            x = np.linspace(min(spec_obs.iloc[:, 0]), max(spec_obs.iloc[:, 0]), 1000)
            spec_fit = pd.DataFrame({0: x, 1: func(x, b=opt_pars[0] + lamb, c=opt_pars[2],
                                                   a=par[0], d=opt_pars[1])})
            spec_fit_under = pd.DataFrame({0: x, 1: func(x, b=opt_pars[0] + lamb, c=opt_pars[2],
                                                         a=par[0]+abundance_shift, d=opt_pars[1])})
            spec_fit_above = pd.DataFrame({0: x, 1: func(x, b=opt_pars[0] + lamb, c=opt_pars[2],
                                                         a=par[0]-abundance_shift, d=opt_pars[1])})
            spec_no = pd.DataFrame({0: x, 1: func(x, b=opt_pars[0] + lamb, c=opt_pars[2],
                                                  a=0, d=opt_pars[1])})
        else:
            return

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
                         label="A({}) {:.2f} \u00b1 {:.2f}".format(elem, abundance, abundance_shift))
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
        main_path = Path(folder).joinpath("Abundance_Analysis", "Lines_Plot")
        fig_path = main_path.joinpath("fit_{}_{}_ang.pdf".format(elem+order, lamb))
        plt.savefig(fig_path)
        plt.close()

        print("{} of {} finished.".format(i+1, len(abund)))

        if ui is not None:
            ui.progressvalue.setText("{}/{}".format(i + 1, len(abund)))

            pixmap = QtGui.QPixmap(str(fig_path))
            ui.linesplotimage.setPixmap(pixmap.scaled(ui.scale))
            ui.linesplotimage.setFixedSize(ui.scale)

            QtCore.QCoreApplication.processEvents()


def folders_creation(folder):
    """
    Subroutine to create necessary folders

    :param folder: root folder of the results.
    """

    main_path = Path(folder).joinpath("Abundance_Analysis")
    if not os.path.exists(main_path):
        os.mkdir(main_path)

    abhist_path = main_path.joinpath("Abundance_Hist")
    if not os.path.exists(abhist_path):
        os.mkdir(abhist_path)

    difhist_path = main_path.joinpath("Difference_Hist")
    if not os.path.exists(difhist_path):
        os.mkdir(difhist_path)

    lines_path = main_path.joinpath("Lines_Plot")
    if not os.path.exists(lines_path):
        os.mkdir(lines_path)


def main(args):
    """
    Main Routine.

    :param args: command line arguments.
    """

    # Arguments Menu Call
    config_name = ab_fit.args_menu(args)

    # Read Configuration File
    list_name, refer_name, type_synth, config_fl, conv_name, folder, observed_name = ab_fit.read_config(config_name)
    order_sep = list_name[2]

    fl_name = folder+"found_values.csv"  # result file

    refer_fl = ab_fit.open_linelist_refer_fl(refer_name)
    spec_obs = ab_fit.open_spec_obs(observed_name)

    # Create necessary folders
    folders_creation(folder)

    # Read results and erase empty ones
    abund = pd.read_csv(fl_name)
    abund = erase_null_abund(abund)

    type_synth = ["TurboSpectrum", conv_name, config_fl]

    # Plot spectra graphics
    plot_lines(spec_obs, abund, refer_fl, type_synth, folder)

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
