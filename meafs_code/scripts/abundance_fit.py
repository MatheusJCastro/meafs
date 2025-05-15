#!/usr/bin/env python3
"""
| MEAFS Abundance Fit
| Matheus J. Castro

| Main fit code to do all the operations with the spectrum, call the modules to generate
  the synthetic spectrum, plot the curves and more.
"""

from specutils.analysis import equivalent_width
from PyQt6 import QtWidgets, QtCore
from specutils import Spectrum1D, SpectralRegion
import matplotlib.pyplot as plt
import astropy.units as u
from pathlib import Path
import pandas as pd
import numpy as np
import time
import sys
import os

from . import fit_functions as ff
from . import voigt_functions as vf
from . import turbospec_functions as tf
from . import abundance_plot as ap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# noinspection PyUnresolvedReferences
from meafs_code import __version__


def open_linelist_refer_fl(list_name):
    """
    Open the Linelist using PANDAS.

    :param list_name: file name of the linelist.
    :return: the pandas dataframe with the linelist.
    """

    return pd.read_csv(list_name, header=None, comment="#")


def open_spec_obs(observed_name, delimiter=None, increment=1):
    """
    Open the observed spectrum file using PANDAS.

    :param observed_name: file name with the spectrum.
    :param delimiter: delimiter type of the file.
    :param increment: increment to get the delimiter automatically
                      (previously necessary in the older no-gui version).
    :return: the pandas dataframe with the spectrum.
    """

    spec_obs = []

    for i in range(0, len(observed_name), increment):
        if increment == 2:
            delimiter = observed_name[i + 1]
        spec_obs.append(pd.read_csv(observed_name[i], header=None, delimiter=delimiter, comment="#"))
    return spec_obs


def open_previous(linelist, columns_names, fl_name=Path("found_values.csv")):
    """
    Open the previous results and analyse it.

    :param linelist: linelist object.
    :param columns_names: names of the columns in the file.
    :param fl_name: file name.
    :return: the new linelist and the pandas dataframe with the previous results.
    """

    try:
        # Try to open
        prev = pd.read_csv(fl_name, delimiter=",", dtype=str)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # If file not found or empty database, create a new one and return
        return linelist, pd.DataFrame(columns=columns_names)

    for i in prev.columns:
        if i != "Element" and i != "Chi" and i != "Equiv Width Obs (A)" and i != "Equiv Width Fit (A)":
            prev[i] = prev[i].astype(float)

    # Reads the existing data
    new_linelist = pd.DataFrame(columns=[0, 1])
    for i in range(len(linelist)):
        elem = linelist.iloc[i][0]
        lamb = linelist.iloc[i][1]
        ind = prev[(prev["Element"] == elem) & (prev["Lambda (A)"] == float(lamb))].index
        if ind.tolist() == []:
            new_linelist.loc[i] = linelist.iloc[i]

    return new_linelist, prev


def plot_spec_gui(specs, canvas, ax, plot_line_refer):
    """
    Plot the spectrum in the GUI.

    :param specs: spectrum data to be plotted.
    :param canvas: canvas to plot.
    :param ax: ax to plot.
    :param plot_line_refer: array to save the reference label of the plots.
    :return: the actualized ``plot_line_refer`` array.
    """

    if specs != []:
        min_all_old = min(specs[0].iloc[:, 0])
        max_all_old = max(specs[0].iloc[:, 0])
    else:
        min_all_old = 0
        max_all_old = 1

    same_line_plots = plot_line_refer[plot_line_refer["elem"] == "spec"]
    for line in range(len(same_line_plots)):
        same_line_plots.iloc[line]["refer"].remove()
        ind = plot_line_refer[plot_line_refer["refer"] == same_line_plots.iloc[line]["refer"]].index
        plot_line_refer = plot_line_refer.drop(ind)
    plot_line_refer.reset_index(drop=True, inplace=True)

    for spec in specs:
        lineplot = ax.plot(spec.iloc[:, 0], spec.iloc[:, 1])
        min_all = min(spec.iloc[:, 0])
        max_all = max(spec.iloc[:, 0])
        if min_all < min_all_old:
            min_all_old = min_all
        if max_all > max_all_old:
            max_all_old = max_all

        plot_line_refer.loc[len(plot_line_refer)] = {"elem": "spec", "wave": "all", "refer": lineplot[0]}

    ax.set_xlim(min_all_old, max_all_old)
    canvas.draw()

    return plot_line_refer


def plot_spec(spec1, spec2, spec3, lamb, elem, folder, show=False, save=True):
    """
    Plot the spectra (previously necessary in the older no-gui version).

    :param spec1: first spectrum data.
    :param spec2: second spectrum data.
    :param spec3: third spectrum data.
    :param lamb: current wavelength.
    :param elem: current element.
    :param folder: directory to save the plot.
    :param show: true to show with the ``matplotlib.pyplot.show()``.
    :param save: true to save the spectrum.
    """


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
        plt.savefig(Path(folder).joinpath("On_time_Plots", "fit_{}_{}_ang.pdf".format(elem, lamb)))
    plt.close()


def plot_spec_ui(spec_fit_arr, folder, elem, lamb, order, ax, canvas, plot_line_refer, vline=True):
    """
    Plot the current line results in the GUI.

    :param spec_fit_arr: spectrum line data.
    :param folder: directory to save.
    :param elem: current element.
    :param lamb: current wavelength.
    :param order: current order of the line.
    :param ax: ax to plot.
    :param canvas: canvas to plot.
    :param plot_line_refer: array to save the reference label of the plots.
    :param vline: if it also plots a vertical line or not.
    :return: the actualized ``plot_line_refer`` array.
    """

    # noinspection PySimplifyBooleanCheck
    if spec_fit_arr != []:
        min_all_old_x = min(spec_fit_arr[0].iloc[:, 0])
        max_all_old_x = max(spec_fit_arr[0].iloc[:, 0])
        min_all_old_y = min(spec_fit_arr[0].iloc[:, 1])
        max_all_old_y = max(spec_fit_arr[0].iloc[:, 1])
    else:
        min_all_old_x = 0
        max_all_old_x = 1
        min_all_old_y = 0
        max_all_old_y = 1

    for j, sp in enumerate(spec_fit_arr):
        ind = plot_line_refer[(plot_line_refer["elem"] == elem + order) &
                              (plot_line_refer["wave"] == lamb)].index
        for line in plot_line_refer.loc[ind, "refer"]: line.remove()
        plot_line_refer.drop(ind, inplace=True)
        plot_line_refer.reset_index(drop=True, inplace=True)

        lineplot = ax.plot(sp.iloc[:, 0], sp.iloc[:, 1], "--", linewidth=1.5)

        min_all_x = min(sp.iloc[:, 0])
        max_all_x = max(sp.iloc[:, 0])
        if min_all_x < min_all_old_x:
            min_all_old_x = min_all_x
        if max_all_x > max_all_old_x:
            max_all_old_x = max_all_x

        min_all_y = min(sp.iloc[:, 1])
        max_all_y = max(sp.iloc[:, 1])
        if min_all_y < min_all_old_y:
            min_all_old_y = min_all_y
        if max_all_y > max_all_old_y:
            max_all_old_y = max_all_y

        plot_line_refer.loc[len(plot_line_refer)] = {"elem": elem+order, "wave": lamb, "refer": lineplot[0]}

        if vline:
            axvlineplot = ax.axvline(lamb, ls="-.", c="red", linewidth=.5)
            plot_line_refer.loc[len(plot_line_refer)] = {"elem": elem+order, "wave": lamb, "refer": axvlineplot}

        sp.to_csv(Path(folder).joinpath("On_time_Plots",
                                        "fit_{}_{}_ang_{}.csv".format(elem + order, lamb, j + 1)),
                  index=False,
                  float_format="%.4f",
                  header=None)

    min_all_old_y = 0.9*min_all_old_y if min_all_old_y > 0 else 1.1*min_all_old_y
    max_all_old_y = 1.1*max_all_old_y if max_all_old_y > 0 else 0.9*max_all_old_y

    ax.set_xlim(min_all_old_x, max_all_old_x)
    ax.set_ylim(min_all_old_y, max_all_old_y)
    canvas.draw()

    return plot_line_refer


def check_order(elem):
    """
    | Check if the current element has any type of order written in the end of the string.
    | Supported types are: roman numbers *(I, II, III...)* and western digits *(1, 2, 3...)*.

    :param elem:
    :return: the element without the order and the order itself.
    """

    if len(elem) == 1:
        return elem, ""

    if elem[1].isdigit() or elem[1] == "I" or elem[1] == "V" or elem[1] == "X" or elem[1] == " ":
        if elem[1] == " ":
            order = elem[2:]
        else:
            order = elem[1:]
        elem = elem[0]
    else:
        if len(elem) == 2:
            return elem, ""
        if elem[2] == " ":
            order = elem[3:]
        else:
            order = elem[2:]
        elem = elem[0:2]

    return elem, order


def plot_abund_nofit(elem, lamb, abundplot, refer_fl, folder, type_synth,
                     cut_val=None, canvas=None, ax=None, plot_line_refer=None,
                     opt_pars=None):
    """
    Plot in the GUI the specified parameters.

    :param elem: current element.
    :param lamb: current wavelength.
    :param abundplot: abundance to be plotted.
    :param refer_fl: reference abundance dataframe.
    :param folder: directory to save.
    :param type_synth: type of the current synthetics spectrum generator.
    :param cut_val: range to plot.
    :param canvas: canvas to plot.
    :param ax: ax to plot.
    :param plot_line_refer: array to save the reference label of the plots.
    :param opt_pars: parameters for the convolution, wavelength shift and continuum.
    :return: the actualized ``plot_line_refer`` array.
    """

    if type_synth[0] == "TurboSpectrum":
        conv_name = type_synth[1]
        config_fl = type_synth[2]
    else:
        conv_name = None
        config_fl = None

    lamb = float(lamb)

    elem, order = check_order(elem)

    # Try to find element abundance reference. If not found, 0 is used.
    try:
        abund_val_refer = float(refer_fl.loc[elem, "value"]) if not refer_fl.loc[elem].isnull().item() else 0
    except KeyError:
        abund_val_refer = 0

    if type_synth[0] == "Equivalent Width":
        func = vf.find_func(type_synth[1])
        x = np.linspace(lamb-cut_val[3], lamb+cut_val[3], 1000)
        spec_fit = pd.DataFrame({0: x, 1: func(x, opt_pars[0] + lamb, opt_pars[2], abundplot, opt_pars[1])})
    elif type_synth[0] == "TurboSpectrum":
        tf.change_abund_configfl(config_fl, elem, find=False, abund=abundplot)
        tf.change_spec_range_configfl(config_fl, lamb, cut_val[3])
        tf.run_configfl(config_fl)
        # Return the Turbospectrum2019 configuration file to original abundance value
        tf.change_abund_configfl(config_fl, elem, find=False, abund=abund_val_refer)

        spec_conv = pd.read_csv(conv_name, header=None, delimiter=r"\s+")

        # noinspection PyTypeChecker
        spec_fit = ff.spec_operations(spec_conv.copy(), lamb_desloc=opt_pars[0], continuum=opt_pars[1],
                                      convol=opt_pars[2])
    else:
        return plot_line_refer

    spec_fit_arr = [spec_fit]
    plot_line_refer = plot_spec_ui(spec_fit_arr, folder, elem, lamb, order, ax, canvas, plot_line_refer)

    return plot_line_refer


def fit_abundance(linelist, spec_obs, refer_fl, folder, type_synth, cut_val=None,
                  abund_lim_df=1., restart=False, save_name="found_values.csv",
                  ui=None, canvas=None, ax=None, plot_line_refer=None,
                  opt_pars=None, repfit=2, max_iter=None, convovbound=None,
                  contpars=None, wavebound=None, only_abund_ind=None,
                  spec_count=None, spec_iter=None):
    """
    Main function to analyse the spectrum and find the fit values for it

    :param linelist: linelist dataframe.
    :param spec_obs: spectrum data.
    :param refer_fl: reference abundace dataframe.
    :param folder: directory to save.
    :param type_synth: type of the current synthetics spectrum generator.
    :param cut_val: ranges to cut the spectrum.
    :param abund_lim_df: default value of the range of the allowed abundance.
    :param restart: if it should ignore past results in the database.
    :param save_name: file name of the previous results.
    :param ui: main GUI QT object.
    :param canvas: canvas to plot.
    :param ax: ax to plot.
    :param plot_line_refer: array to save the reference label of the plots.
    :param opt_pars: convolution, wavelength shift and continuum initial guess.
    :param repfit: number of iterations of the main fit function.
    :param max_iter: maximum allowed iterations of the Nelder-Mead method.
    :param convovbound: range to fit the convolution.
    :param contpars: the calibration values of the overall continuum fit method.
    :param wavebound: range to fit the wavelength shift.
    :param only_abund_ind: change only abundance without fitting other parameters at this index.
    :param spec_count: defines the total number of spectra to be analysed.
    :param spec_iter: defines the current spectrum index.
    :return: dataframe with the results of the fit, the actualized
             ``ax`` array and the actualized ``plot_line_refer`` array.
    """

    if type_synth[0] == "TurboSpectrum":
        conv_name = type_synth[1]
        config_fl = type_synth[2]
    else:
        conv_name = None
        config_fl = None

    # For each fit parameter, a spectrum range can be selected
    # a value of 5, will select a total of 10 Angstroms with the element line wavelength in the middle
    if cut_val is None:
        # spec range vals for [continuum, convolution, abundance, plot]
        cut_val = [10/2, 3/2, .4/2, 1/2]

    columns_names = ["Element", "Lambda (A)", "Lamb Shift", "Continuum", "Convolution",
                     "Refer Abundance", "Fit Abundance", "Differ", "Chi", "Equiv Width Obs (A)",
                     "Equiv Width Fit (A)"]

    if restart:
        found_val = pd.DataFrame(columns=columns_names)
    else:
        linelist, found_val = open_previous(linelist, columns_names, fl_name=Path(folder).joinpath(save_name))

        if only_abund_ind is not None:
            linelist = pd.DataFrame(columns=[0, 1])
            linelist.loc[0] = [found_val.loc[only_abund_ind, "Element"],
                               found_val.loc[only_abund_ind, "Lambda (A)"]]

        if ui is not None:
            ui.abundancetable.setRowCount(0)
            for i in range(len(found_val)):
                elem = found_val.iloc[i, 0]
                lamb = float(found_val.iloc[i, 1])

                elem, order = check_order(elem)

                ui.abundancetable.insertRow(i)
                ui.abundancetable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(elem)+str(order)))
                ui.abundancetable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(lamb)))
                path = Path(folder).joinpath("On_time_Plots")
                count = 0
                while True:
                    file = path.joinpath("fit_{}_{}_ang_{}.csv".format(elem+order, lamb, count + 1))

                    if os.path.isfile(file):
                        data = pd.read_csv(file)
                        count += 1

                        ind = plot_line_refer[(plot_line_refer["elem"] == elem + order) &
                                              (plot_line_refer["wave"] == lamb)].index
                        for line in plot_line_refer.loc[ind, "refer"]: line.remove()
                        plot_line_refer.drop(ind, inplace=True)
                        plot_line_refer.reset_index(drop=True, inplace=True)

                        lineplot = ax.plot(data.iloc[:, 0], data.iloc[:, 1], "--", linewidth=1.5)
                        axvlineplot = ax.axvline(lamb, ls="-.", c="red", linewidth=.5)
                        plot_line_refer.loc[len(plot_line_refer)] = {"elem": elem+order, "wave": lamb,
                                                                     "refer": lineplot[0]}
                        plot_line_refer.loc[len(plot_line_refer)] = {"elem": elem+order, "wave": lamb,
                                                                     "refer": axvlineplot}
                    else:
                        break
                canvas.draw()

    if opt_pars is None:
        continuum, cont_err = ff.fit_continuum(spec_obs, contpars=contpars, iterac=max_iter[0])
    else:
        continuum = None

    input_opt_pars = opt_pars

    # For each line in the linelist file
    for i in range(len(linelist)):
        elem = linelist.iloc[i][0]
        lamb = float(linelist.iloc[i][1])

        opt_pars = input_opt_pars

        if ui is not None:
            ui.linedefvalue.setText("Element {}, line {}".format(elem, lamb))
            # Allow QT to actualize the UI while in the loop
            QtCore.QCoreApplication.processEvents()
            if ui.stop_state:
                ui.stop_state = False
                return found_val, ax, plot_line_refer

        print("Analysing the element {} for lambda {}. Line {} out of {}"
              " for spectrum {} out of {}.".format(elem, lamb, i+1, len(linelist),
                                                   spec_iter+1, spec_count))

        elem, order = check_order(elem)

        # Try to find element abundance reference. If not found, 0 is used.
        try:
            abund_val_refer = float(refer_fl.loc[elem, "value"]) if not refer_fl.loc[elem].isnull().item() else 0
        except KeyError:
            abund_val_refer = 0

        abund_lim = abund_lim_df if abund_val_refer != 0 else 3

        # Check whether the element exists in turbospectrum config file
        if type_synth[0] == "TurboSpectrum" and not tf.check_elem_configfl(config_fl, elem):
            print("Element not in TurboSpectrum Configuration file")
            continue
        # If the lamb is not between the range of the spec, skip the iteration
        if not spec_obs.iloc[0][0] <= lamb <= spec_obs.iloc[-1][0]:
            print("Wavelength not in the range of the spectrum.")
            continue
        # If continuum, conv, abund or plot range to fit is smaller than 0, skip the iteration
        if len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[0])) <= 1:
            print("Continuum range smaller than 0.")
            continue
        elif len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[1])) <= 1:
            print("Convolution range smaller than 0.")
            continue
        elif len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[2])) <= 1:
            print("Abundance range smaller than 0.")
            continue
        elif len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[3])) <= 1:
            print("Plot range smaller than 0.")
            continue

        if max_iter is None:
            max_iter = [100, 10]

        # arrumar segundo espectro overwriting os valores bons do primeiro
        chi, equiv_width_obs, equiv_width_fit = 0, 0, 0
        par = [abund_val_refer]
        spec_fit = [[], []]
        for repeat in range(repfit):
            # Fit of lambda shift, continuum and convolution
            spec_obs_cut = ff.cut_spec(spec_obs, lamb, cut_val=cut_val[0])

            if type_synth[0] == "Equivalent Width":
                if opt_pars is None:
                    continuum_local, cont_err_local = ff.fit_continuum(spec_obs_cut, contpars=contpars,
                                                                       iterac=max_iter[0])
                    opt_pars, chi, spec_fit = vf.optimize_spec(spec_obs_cut, type_synth, lamb, continuum_local,
                                                               iterac=max_iter[1], convovbound=convovbound,
                                                               wavebound=wavebound)
                if ui is not None:
                    ui.abundancelabel.setText("Depth")
            elif type_synth[0] == "TurboSpectrum":
                tf.change_spec_range_configfl(config_fl, lamb, cut_val[0])
                tf.run_configfl(config_fl)
                spec_conv = pd.read_csv(conv_name, header=None, delimiter=r"\s+")
                if ui is not None:
                    ui.abundancelabel.setText("Abundance")

                if opt_pars is None:
                    opt_pars = tf.optimize_spec(spec_obs_cut, spec_conv, lamb, cut_val, continuum,
                                                init=opt_pars, iterac=max_iter[1], convovbound=convovbound,
                                                wavebound=wavebound)
            # opt_pars = [0,0,0]

            print("\tLamb Shift:\t\t{:.4f}\n"
                  "\tContinuum:\t\t{:.4f}\n"
                  "\tConvolution:\t\t{:.4f}".format(opt_pars[0], opt_pars[1], opt_pars[2]))
            if ui is not None:
                ui.lambshifvalue.setValue(opt_pars[0])
                ui.continuumvalue.setValue(opt_pars[1])
                ui.convolutionvalue.setValue(opt_pars[2])
                # Allow QT to actualize the UI while in the loop
                QtCore.QCoreApplication.processEvents()
                if ui.stop_state:
                    ui.stop_state = False
                    return found_val, ax, plot_line_refer

            # Fit of abundance
            spec_obs_cut = ff.cut_spec(spec_obs, lamb, cut_val=cut_val[3])
            if type_synth[0] == "Equivalent Width":
                par, chi, spec_fit = vf.optimize_abund(spec_obs_cut, type_synth, lamb, opt_pars, iterac=max_iter[2])
            elif type_synth[0] == "TurboSpectrum":
                tf.change_spec_range_configfl(config_fl, lamb, cut_val[3])

                par, chi, spec_fit = tf.optimize_abund(spec_obs_cut, config_fl, conv_name, elem, opt_pars, par,
                                                       abund_lim, iterac=max_iter[2])

            print("\tAbundance:\t\t{:.4f}".format(par[0]))

            if ui is not None:
                ui.abundancevalue.setValue(par[0])
                # Allow QT to actualize the UI while in the loop
                QtCore.QCoreApplication.processEvents()
                if ui.stop_state:
                    ui.stop_state = False
                    return found_val, ax, plot_line_refer

            # Fit of Equivalent Width Observed Spectrum
            # noinspection PyUnresolvedReferences
            cont_level = ff.fit_continuum(spec_obs_cut, contpars=contpars, iterac=max_iter[0])[0]
            spec_obs_cut_norm = spec_obs_cut[1] / cont_level
            spec1d = Spectrum1D(spectral_axis=np.asarray(spec_obs_cut[0]) * u.AA,
                                flux=np.asarray(spec_obs_cut_norm) * u.Jy)

            # Get the minimum and maximum range of the line to apply the equivalent width function
            min_line, max_line = ff.line_boundaries(spec_obs_cut, lamb, threshold=0.98, contpars=contpars,
                                                    iterac=max_iter[0])

            if max_line < len(spec_obs_cut)-10:
                max_line += 10
            else:
                max_line = len(spec_obs_cut) - 1

            if min_line > 10:
                min_line -= 10
            else:
                min_line = 0

            region = SpectralRegion(spec_obs_cut.iloc[min_line][0] * u.AA,
                                    spec_obs_cut.iloc[max_line][0] * u.AA)

            equiv_width_obs = equivalent_width(spec1d, regions=region)
            # noinspection PyUnresolvedReferences
            equiv_width_obs = np.float16(equiv_width_obs / u.AA)

            # Fit of Equivalent Width Fitted Spectrum
            # noinspection PyUnresolvedReferences
            cont_level = ff.fit_continuum(spec_fit, contpars=contpars, iterac=max_iter[0])[0]
            spec_fit_norm = spec_fit[1] / cont_level
            spec1d = Spectrum1D(spectral_axis=np.asarray(spec_fit[0]) * u.AA,
                                flux=np.asarray(spec_fit_norm) * u.Jy)

            # Get the minimum and maximum range of the line to apply the equivalent width function
            min_line, max_line = ff.line_boundaries(spec_fit, lamb, threshold=0.98, contpars=contpars,
                                                    iterac=max_iter[0])

            if max_line < len(spec_obs_cut)-10:
                max_line += 10
            else:
                max_line = len(spec_obs_cut) - 1

            if min_line > 10:
                min_line -= 10
            else:
                min_line = 0

            region = SpectralRegion(spec_fit.iloc[min_line][0] * u.AA,
                                    spec_fit.iloc[max_line][0] * u.AA)

            equiv_width_fit = equivalent_width(spec1d, regions=region)
            # noinspection PyUnresolvedReferences
            equiv_width_fit = np.float16(equiv_width_fit / u.AA)

        index_append = len(found_val) if only_abund_ind is None else only_abund_ind
        found_val.loc[index_append] = [elem+order, lamb, opt_pars[0], opt_pars[1], opt_pars[2], abund_val_refer,
                                       par[0], np.abs(par[0]-abund_val_refer), "{:.4e}".format(chi),
                                       "{:.4e}".format(equiv_width_obs), "{:.4e}".format(equiv_width_fit)]

        # Plot of data
        spec_obs_cut = ff.cut_spec(spec_obs, lamb, cut_val=cut_val[3])
        if type_synth[0] == "Equivalent Width":
            func = vf.find_func(type_synth[1])
            x = np.linspace(min(spec_obs_cut.iloc[:, 0]), max(spec_obs_cut.iloc[:, 0]), 1000)
            spec_fit = pd.DataFrame({0: x, 1: func(x, b=opt_pars[0]+lamb, c=opt_pars[2], a=par[0], d=opt_pars[1])})
        elif type_synth[0] == "TurboSpectrum":
            tf.change_abund_configfl(config_fl, elem, find=False, abund=par[0])
            tf.change_spec_range_configfl(config_fl, lamb, cut_val[3])
            tf.run_configfl(config_fl)
            # Return the Turbospectrum2019 configuration file to original abundance value
            tf.change_abund_configfl(config_fl, elem, find=False, abund=abund_val_refer)

            spec_conv = pd.read_csv(conv_name, header=None, delimiter=r"\s+")

            # noinspection PyTypeChecker
            spec_fit = ff.spec_operations(spec_conv.copy(), lamb_desloc=opt_pars[0], continuum=opt_pars[1],
                                          convol=opt_pars[2])

        if ui is None:
            plot_spec(spec_obs_cut, spec_conv, spec_fit, lamb, elem+order, folder)
        else:
            spec_fit_arr = [spec_fit]
            plot_line_refer = plot_spec_ui(spec_fit_arr, folder, elem, lamb, order, ax, canvas, plot_line_refer)

        # Write the line result to the csv file
        found_val.to_csv(Path(folder).joinpath(save_name), index=False, float_format="%.4f")

        if ui is not None:
            if only_abund_ind is None:
                rowpos = ui.abundancetable.rowCount()
                ui.abundancetable.insertRow(rowpos)
                ui.abundancetable.setItem(rowpos, 0, QtWidgets.QTableWidgetItem(str(elem)+str(order)))
                ui.abundancetable.setItem(rowpos, 1, QtWidgets.QTableWidgetItem(str(lamb)))

            # linescurrent = ui.progressvalue.text().split("/")
            ui.progressvalue.setText("{}/{}".format(i+1, len(linelist)))

    return found_val, ax, plot_line_refer


def read_config(config_name):
    """
    Function to read the configuration file (previously necessary in
    the older no-gui version).

    :param config_name: configuration file name.
    :return: linelist file name, reference abundance file name, type of the
             synthetics spectrum to use, TurboSpectrum configuration file name,
             TurboSpectrum results file name, directory to save the results,
             spectrum file name.
    """

    def separator(sep):
        # Define the type of separator
        if sep == "comma":
            return ","
        elif sep == "tab":
            return r"\s+"
        else:
            return ","

    # Read file
    config_data = pd.read_csv(config_name, comment="#", header=None)

    # Enable long strings
    pd.options.display.max_colwidth = 150

    # Attribution of the variables
    list_name = [config_data.loc[0].to_string(index=False),
                 config_data.loc[1].to_string(index=False),
                 config_data.loc[2].to_string(index=False)]
    refer_name = [config_data.loc[3].to_string(index=False),
                  config_data.loc[4].to_string(index=False)]
    type_synth = config_data.loc[5].to_string(index=False)
    config_fl = config_data.loc[6].to_string(index=False)
    conv_name = config_data.loc[7].to_string(index=False)
    folder = config_data.loc[8].to_string(index=False) + "/"

    # Attribution of the spectra names
    observed_name = []
    for i in range(9, len(config_data)):
        observed_name.append(config_data.iloc[i].to_string(index=False))

    # Define the separator type in the file
    list_name[1] = separator(list_name[1])
    refer_name[1] = separator(refer_name[1])
    for i in range(1, len(observed_name), 2):
        observed_name[i] = separator(observed_name[i])

    return list_name, refer_name, type_synth, config_fl, conv_name, folder, observed_name


def gui_call(spec_obs, ui, checkstate, canvas, ax, cut_val=None, plot_line_refer=None, opt_pars=None,
             repfit=2, abundplot=None, results_array=None, only_abund_ind=None, final_plot=False,
             plot_type=None, single=None):
    """
    Main function to be called from the GUI.

    :param spec_obs: spectrum data.
    :param ui: main GUI QT object.
    :param checkstate: QT checked state for checkboxes.
    :param canvas: GUI canvas plot object.
    :param ax: GUI ax plot object.
    :param cut_val: range to cut the spectrum.
    :param plot_line_refer: array with a list of the current available plots.
    :param opt_pars: convolution, wavelength shift and continuum parameters.
    :param repfit: number of iterations of the main fit function.
    :param abundplot: overwrite the abundance fit and only plot the value
                      present in this variable.
    :param results_array: array for the results of the fit.
    :param only_abund_ind: change only abundance without fitting other parameters at this index.
    :param final_plot: if it's meant to create the final plots instead of fitting.
    :param plot_type: type of the final plot to create.
    :param single: create a final plot to a single line or for all of them.
    :return: the results of the fit, the actualized ``ax`` variable and the
             actualized ``plot_line_refer`` variable.
    """

    # Time Counter
    init = time.time()
    init_local = time.localtime()
    init_time = "Run started at: {} {} {}, {}:{}:{}. ".format(init_local.tm_year,
                                                              init_local.tm_mon,
                                                              init_local.tm_mday,
                                                              init_local.tm_hour,
                                                              init_local.tm_min,
                                                              init_local.tm_sec)
    print(init_time)

    ui.gui_hold(True)

    if ui.restart.checkState() == QtCore.Qt.CheckState.Checked:
        restart = True
    else:
        restart = False

    folder = ui.outputname.text()

    # Create necessary folders
    folder_create = Path(folder).joinpath("On_time_Plots")
    os.makedirs(folder_create, exist_ok=True)

    linelist = []
    for line in range(ui.linelistcontent.rowCount()):
        item = ui.linelistcontent.cellWidget(line, 2).layout().itemAt(0).widget()
        if item.checkState() == checkstate and \
           ui.linelistcontent.item(line, 0) is not None and \
           ui.linelistcontent.item(line, 1) is not None:
            linelist.append([ui.linelistcontent.item(line, 0).text(), ui.linelistcontent.item(line, 1).text()])
    linelist = pd.DataFrame(data=linelist)

    refer_fl = []
    inds = []
    for line in range(ui.refercontent.rowCount()):
        if ui.refercontent.item(line, 0) is not None and \
           ui.refercontent.item(line, 1) is not None:
            inds.append(ui.refercontent.item(line, 0).text())
            refer_fl.append(ui.refercontent.item(line, 1).text())
    refer_fl = pd.DataFrame(data=refer_fl, index=inds, columns=["value"])

    methodconfig = None
    if ui.methodbox.currentText() == "Equivalent Width":
        methodconfig = [ui.methodbox.currentText(),
                        ui.ewfuncbox.currentText(),
                        ui.convinitguessvalue.value(),
                        ui.depthinitguessvalue.value()]
    elif ui.methodbox.currentText() == "TurboSpectrum":
        methodconfig = [ui.methodbox.currentText(),
                        ui.turbospectrumoutputname.text(),
                        ui.turbospectrumconfigname.text()]
        if not os.path.isfile(methodconfig[1]) or not os.path.isfile(methodconfig[2]):
            ui.gui_hold(False)

            msg_err = "Error: TurboSpectrum files are not properly set. Run aborted.\n"

            # noinspection PyTypeChecker
            with open(str(Path(folder).joinpath("log.txt")), "a") as f:
                f.write(init_time)
                f.write(msg_err)
                f.write("\n")
                f.close()
            print(msg_err)

            ui.show_error("TurboSpectrum files are not properly set. Run aborted.")

            return results_array, ax, plot_line_refer

    if not final_plot:
        ui.methodsdatafittab.setCurrentIndex(2)

    max_iter = ui.max_iter
    convovbound = ui.convovbound
    wavebound = ui.wavebound
    contpars = ui.continuumpars

    # Allow QT to actualize the UI while in the loop
    QtCore.QCoreApplication.processEvents()

    if abundplot is None and not final_plot:
        spec_count = len(spec_obs)
        for spec_iter, spec in enumerate(spec_obs):
            results_array, ax, plot_line_refer = fit_abundance(linelist, spec, refer_fl, folder, methodconfig,
                                                               restart=restart, ui=ui, canvas=canvas, ax=ax,
                                                               cut_val=cut_val, plot_line_refer=plot_line_refer,
                                                               opt_pars=opt_pars, repfit=repfit, max_iter=max_iter,
                                                               convovbound=convovbound, contpars=contpars,
                                                               wavebound=wavebound, only_abund_ind=only_abund_ind,
                                                               spec_count=spec_count, spec_iter=spec_iter)
            restart = False
    elif not final_plot:
        currow = ui.abundancetable.currentRow()
        currow = ui.abundancetable.rowCount() - 1 if currow == -1 else currow
        elem = ui.abundancetable.item(currow, 0).text()
        lamb = ui.abundancetable.item(currow, 1).text()
        plot_line_refer = plot_abund_nofit(elem, lamb, abundplot, refer_fl, folder, methodconfig,
                                           cut_val=cut_val, canvas=canvas, ax=ax, plot_line_refer=plot_line_refer,
                                           opt_pars=opt_pars)
    else:
        ap.folders_creation(folder)

        res_arr_copy = results_array.copy()
        elements_full = results_array.Element
        elements = []
        for i in elements_full:
            elem, order = check_order(i)
            elements.append(elem)
        res_arr_copy.Element = elements
        elements = np.unique(elements)

        if plot_type == "lines":
            ui.plotstab.setCurrentIndex(0)

            if not single:
                res_to_send = results_array
            else:
                ind = ui.abundancetable.currentRow()
                res_to_send = results_array.iloc[[ind]]

            ap.plot_lines(spec_obs,
                          res_to_send,
                          refer_fl,
                          methodconfig,
                          folder,
                          cut_val=cut_val[3],
                          abundance_shift=ui.abundshift.value(),
                          ui=ui)
        elif plot_type == "box":
            ui.plotstab.setCurrentIndex(1)
            ap.plot_abund_box(res_arr_copy, elements, folder, ui=ui)
        elif plot_type == "hist":
            ui.plotstab.setCurrentIndex(2)
            if single:
                ind = ui.abundancetable.currentRow()
                elem = ui.results_array.Element.iloc[ind]
                elem, order = check_order(elem)
                elements = [elem]
                # res_arr_copy = ui.res_arr_copy[ui.results_array.Element.str.contains(elem)]

            bins = ui.histbinsvalue.value()
            ap.plot_abund_hist(res_arr_copy, elements, folder, ui=ui, bins=bins)
            ap.plot_differ_hist(res_arr_copy, elements, folder, ui=ui, bins=bins)

    ui.gui_hold(False)

    if final_plot:
        ui.run.setDisabled(True)

    # Time Counter
    end = time.time()
    dif = end - init
    time_spent = "Time spent: {:.0f} h {:.0f} m {:.0f} s ({:.0f} s).\n".format(dif // 3600, (dif // 60) % 60,
                                                                               dif % 60, dif)

    # noinspection PyTypeChecker
    with open(str(Path(folder).joinpath("log.txt")), "a") as f:
        f.write(init_time)
        f.write(time_spent)
        f.write("\n")
        f.close()
    print(time_spent)

    return results_array, ax, plot_line_refer


def main(args):
    """
    Main subroutine to call the functions (previously necessary in the older no-gui version).

    :param args: system command line arguments.
    """

    # Time Counter
    init = time.time()

    # Arguments Menu Call
    config_name = args_menu(args)

    # Read Configuration File
    list_name, refer_name, type_synth, config_fl, conv_name, folder, observed_name = read_config(config_name)

    # Create necessary folders
    if not os.path.exists(folder):
        os.mkdir(folder)
    if not os.path.exists(folder+"On_time_Plots"):
        os.mkdir(folder+"On_time_Plots")

    # Open some files
    linelist = open_linelist_refer_fl(list_name)
    refer_fl = open_linelist_refer_fl(refer_name)
    # Function to open the observed spectrum file using PANDAS
    spec_obs = []
    for i in range(0, len(observed_name), 2):
        delimiter = observed_name[i + 1]
        spec_obs.append(pd.read_csv(observed_name[i], header=None, delimiter=delimiter))

    type_synth = ["TurboSpectrum",
                  conv_name,
                  config_fl]

    # Adjust parameters for each spectra declared
    # Caution: be aware of data overlay on the final csv file
    for spec in spec_obs:
        fit_abundance(linelist, spec, refer_fl, folder, type_synth,
                      restart=False)

    # Time Counter
    end = time.time()
    dif = end - init
    time_spent = "Time spent: {:.0f} h {:.0f} m {:.0f} s ({:.0f} s)".format(dif // 3600, (dif // 60) % 60, dif % 60,
                                                                            dif)

    # noinspection PyTypeChecker
    np.savetxt(folder+"log.txt", [time_spent], fmt="%s")
    print(time_spent)


def args_menu(args):
    """
    Run the arguments resolve and print them if necessary (previously necessary in the older no-gui version).

    :param args: system command line arguments.
    """

    if len(args) <= 1 and not any((i == "-h" or i == "--h" or i == "-help" or i == "--help") for i in args):
        if len(args) != 0:
            config_name = args[0]
        else:
            config_name = "meafs_config.txt"

        if not os.path.exists(config_name):
            sys.exit("\033[1;31mError: file {} not found.\033[m".format(config_name))

        return config_name
    else:
        help_msg = "\n\t\t\033[1;31mHelp Section\033[m\nabundance_fit.py v{}\n" \
                   "Usage: python3 abundance_fit.py [options] argument\n\n" \
                   "Written by Matheus J. Castro <https://github.com/MatheusJCastro/meafs>\nUnder MIT License.\n\n" \
                   "This program finds abundances of elements for a given spectrum.\n\n" \
                   "Argument needs to be a \".txt\" file with the MEAFS configuration.\n" \
                   "If no argument is given, the default name is \"meafs_config.txt\".\n\n" \
                   "Options are:\n -h,  -help\t|\tShow this help;\n--h, --help\t|\tShow this help;\n" \
                   "\n\nExample:\n./abundance_fit.py meafs_config.txt\n".format(__version__)
        print(help_msg)


if __name__ == '__main__':
    arg = sys.argv[1:]
    main(arg)  # call main subroutine
