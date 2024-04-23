#!/usr/bin/env python3
#####################################################
# Abundance Fit                                     #
# Matheus J. Castro                                 #
# v4.6                                              #
# Last Modification: 04/23/2024                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

from specutils.analysis import equivalent_width
from PyQt6 import QtWidgets, QtCore
from specutils import Spectrum1D
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

version = 4.6


def open_linelist_refer_fl(list_name):
    # Function to open the Linelist using PANDAS
    return pd.read_csv(list_name, header=None)


def open_spec_obs(observed_name, delimiter=None, increment=1):
    # Function to open the observed spectrum file using PANDAS
    spec_obs = []

    for i in range(0, len(observed_name), increment):
        if increment == 2:
            delimiter = observed_name[i + 1]
        spec_obs.append(pd.read_csv(observed_name[i], header=None, delimiter=delimiter))
    return spec_obs


def open_previous(linelist, columns_names, fl_name=Path("found_values.csv")):
    # Function to open the previous results and analyze it
    try:
        # Try to open
        prev = pd.read_csv(fl_name, delimiter=",")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # If file not found or empty database, create a new one and return
        return linelist, pd.DataFrame(columns=columns_names)

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
        plt.savefig(Path(folder).joinpath("On_time_Plots", "fit_{}_{}_ang.pdf".format(elem, lamb)))
    plt.close()


def plot_spec_ui(spec_fit_arr, folder, elem, lamb, order, ax, canvas, plot_line_refer):
    # noinspection PySimplifyBooleanCheck
    if spec_fit_arr != []:
        min_all_old = min(spec_fit_arr[0].iloc[:, 0])
        max_all_old = max(spec_fit_arr[0].iloc[:, 0])
    else:
        min_all_old = 0
        max_all_old = 1

    for j, sp in enumerate(spec_fit_arr):
        ind = plot_line_refer[(plot_line_refer["elem"] == elem + order) &
                              (plot_line_refer["wave"] == lamb)].index
        for line in plot_line_refer.loc[ind, "refer"]: line.remove()
        plot_line_refer.drop(ind, inplace=True)
        plot_line_refer.reset_index(drop=True, inplace=True)

        lineplot = ax.plot(sp.iloc[:, 0], sp.iloc[:, 1], "--", linewidth=1.5)
        axvlineplot = ax.axvline(lamb, ls="-.", c="red", linewidth=.5)
        min_all = min(sp.iloc[:, 0])
        max_all = max(sp.iloc[:, 0])
        if min_all < min_all_old:
            min_all_old = min_all
        if max_all > max_all_old:
            max_all_old = max_all

        plot_line_refer.loc[len(plot_line_refer)] = {"elem": elem+order, "wave": lamb, "refer": lineplot[0]}
        plot_line_refer.loc[len(plot_line_refer)] = {"elem": elem+order, "wave": lamb, "refer": axvlineplot}

        sp.to_csv(Path(folder).joinpath("On_time_Plots",
                                        "fit_{}_{}_ang_{}.csv".format(elem + order, lamb, j + 1)),
                  index=False,
                  float_format="%.4f",
                  header=None)

    ax.set_xlim(min_all_old, max_all_old)
    canvas.draw()

    return plot_line_refer


def check_order(elem):
    if elem[1].isdigit() or elem[1] == "I" or elem[1] == "V" or elem[1] == "X" or elem[1] == " ":
        order = elem[1:]
        elem = elem[0]
    else:
        order = elem[2:]
        elem = elem[0:2]

    return elem, order


def plot_abund_nofit(elem, lamb, abundplot, refer_fl, folder, type_synth,
                     cut_val=None, canvas=None, ax=None, plot_line_refer=None,
                     opt_pars=None):

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

        spec_conv = pd.read_csv(conv_name, header=None, delimiter="\s+")

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
                  contpars=None, wavebound=None):
    # Function to analyse the spectrum and find the fit values for it

    stop = False

    def stop_state():
        nonlocal stop
        stop = True

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

        if ui is not None:
            rowpos = ui.abundancetable.rowCount()
            for i in range(len(found_val)):
                elem = found_val.iloc[i, 0]
                lamb = float(found_val.iloc[i, 1])

                elem, order = check_order(elem)

                ui.abundancetable.insertRow(rowpos+i)
                ui.abundancetable.setItem(rowpos+i, 0, QtWidgets.QTableWidgetItem(str(elem)+str(order)))
                ui.abundancetable.setItem(rowpos+i, 1, QtWidgets.QTableWidgetItem(str(lamb)))
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

    # For each line in the linelist file
    for i in range(len(linelist)):
        elem = linelist.iloc[i][0]
        lamb = float(linelist.iloc[i][1])

        if ui is not None:
            ui.linedefvalue.setText("Element {}, line {}".format(elem, lamb))
            ui.stop.clicked.connect(stop_state)
            # Allow QT to actualize the UI while in the loop
            QtCore.QCoreApplication.processEvents()
            if stop:
                return found_val, ax, plot_line_refer

        print("Analysing the element {} for lambda {}. Line {} of {}.".format(elem, lamb, i+1, len(linelist)))

        elem, order = check_order(elem)

        # Try to find element abundance reference. If not found, 0 is used.
        try:
            abund_val_refer = float(refer_fl.loc[elem, "value"]) if not refer_fl.loc[elem].isnull().item() else 0
        except KeyError:
            abund_val_refer = 0

        abund_lim = abund_lim_df if abund_val_refer != 0 else 3
        index_append = len(found_val)  # linelist.index.tolist()[i]

        # Check whether the element exists in turbospectrum config file
        if type_synth[0] == "TurboSpectrum" and not tf.check_elem_configfl(config_fl, elem):
            print("Element not in TurboSpectrum Configuration file")
            continue
        # If the lamb is not between the range of the spec, skip the iteration
        if not spec_obs.iloc[0][0] <= lamb <= spec_obs.iloc[-1][0]:
            print("Wavelength not in the range of the spectrum.")
            continue
        # If continuum, conv, abund or plot range to fit is smaller than 0, stop fitting
        if len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[0])) <= 1:
            print("Continuum range smaller than 0.")
            break
        elif len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[1])) <= 1:
            print("Convolution range smaller than 0.")
            break
        elif len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[2])) <= 1:
            print("Abundance range smaller than 0.")
            break
        elif len(ff.cut_spec(spec_obs, lamb, cut_val=cut_val[3])) <= 1:
            print("Plot range smaller than 0.")
            break

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
                    opt_pars, chi, spec_fit = vf.optimize_spec(spec_obs_cut, type_synth, lamb, continuum,
                                                               iterac=max_iter[1], convovbound=convovbound,
                                                               wavebound=wavebound)
                ui.abundancelabel.setText("Deepth")
            elif type_synth[0] == "TurboSpectrum":
                tf.change_spec_range_configfl(config_fl, lamb, cut_val[0])
                tf.run_configfl(config_fl)
                spec_conv = pd.read_csv(conv_name, header=None, delimiter="\s+")
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
                if stop:
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
                if stop:
                    return found_val, ax, plot_line_refer

            # Fit of Equivalent Width Observed Spectrum
            # noinspection PyUnresolvedReferences
            spec1d = Spectrum1D(spectral_axis=np.asarray(spec_obs_cut[0]) * u.AA,
                                flux=np.asarray(spec_obs_cut[1]) * u.Jy)
            equiv_width_obs = equivalent_width(spec1d)
            # noinspection PyUnresolvedReferences
            equiv_width_obs = np.float128(equiv_width_obs / u.AA)

            # Fit of Equivalent Width Fitted Spectrum
            # noinspection PyUnresolvedReferences
            spec1d = Spectrum1D(spectral_axis=np.asarray(spec_fit[0]) * u.AA,
                                flux=np.asarray(spec_fit[1]) * u.Jy)
            equiv_width_fit = equivalent_width(spec1d)
            # noinspection PyUnresolvedReferences
            equiv_width_fit = np.float128(equiv_width_fit / u.AA)

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

            spec_conv = pd.read_csv(conv_name, header=None, delimiter="\s+")

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
            rowpos = ui.abundancetable.rowCount()
            ui.abundancetable.insertRow(rowpos)
            ui.abundancetable.setItem(rowpos, 0, QtWidgets.QTableWidgetItem(str(elem)+str(order)))
            ui.abundancetable.setItem(rowpos, 1, QtWidgets.QTableWidgetItem(str(lamb)))

            # linescurrent = ui.progressvalue.text().split("/")
            ui.progressvalue.setText("{}/{}".format(i+1, len(linelist)))

    return found_val, ax, plot_line_refer


def read_config(config_name):
    # Function to read the configuration file
    def separator(sep):
        # Define the type of separator
        if sep == "comma":
            return ","
        elif sep == "tab":
            return "\s+"
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
             repfit=2, abundplot=None, results_array=None):
    # Time Counter
    init = time.time()
    init_local = time.localtime()
    init_time = "Run started at: {} {} {}, {}:{}:{}.".format(init_local.tm_year,
                                                             init_local.tm_mon,
                                                             init_local.tm_mday,
                                                             init_local.tm_hour,
                                                             init_local.tm_min,
                                                             init_local.tm_sec)
    print(init_time)

    ui.run.setDisabled(True)
    ui.manualfitbutton.setDisabled(True)
    ui.currentvaluesplotbutton.setDisabled(True)
    ui.currentvaluessavebutton.setDisabled(True)
    ui.abundancetable.setDisabled(True)

    ui.run.setText("Running")
    ui.run.setStyleSheet("background-color: red")

    if ui.restart.checkState() == QtCore.Qt.CheckState.Checked:
        restart = True
    else:
        restart = False

    folder = ui.outputname.text()

    # Create necessary folders
    if not os.path.exists(folder):
        os.mkdir(folder)
    if not os.path.exists(Path(folder).joinpath("On_time_Plots")):
        os.mkdir(Path(folder).joinpath("On_time_Plots"))

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
                        ui.deepthinitguessvalue.value()]
    elif ui.methodbox.currentText() == "TurboSpectrum":
        methodconfig = [ui.methodbox.currentText(),
                        ui.turbospectrumoutputname.text(),
                        ui.turbospectrumconfigname.text()]

    ui.methodsdatafittab.setCurrentIndex(2)

    max_iter = ui.max_iter
    convovbound = ui.convovbound
    wavebound = ui.wavebound
    contpars = ui.continuumpars

    # Allow QT to actualize the UI while in the loop
    QtCore.QCoreApplication.processEvents()

    if abundplot is None:
        for spec in spec_obs:
            results_array, ax, plot_line_refer = fit_abundance(linelist, spec, refer_fl, folder, methodconfig,
                                                               restart=restart, ui=ui, canvas=canvas, ax=ax,
                                                               cut_val=cut_val, plot_line_refer=plot_line_refer,
                                                               opt_pars=opt_pars, repfit=repfit, max_iter=max_iter,
                                                               convovbound=convovbound, contpars=contpars,
                                                               wavebound=wavebound)
    else:
        currow = ui.abundancetable.currentRow()
        currow = ui.abundancetable.rowCount() - 1 if currow == -1 else currow
        elem = ui.abundancetable.item(currow, 0).text()
        lamb = ui.abundancetable.item(currow, 1).text()
        plot_line_refer = plot_abund_nofit(elem, lamb, abundplot, refer_fl, folder, methodconfig,
                                           cut_val=cut_val, canvas=canvas, ax=ax, plot_line_refer=plot_line_refer,
                                           opt_pars=opt_pars)

    ui.run.setDisabled(False)
    ui.manualfitbutton.setDisabled(False)
    ui.currentvaluesplotbutton.setDisabled(False)
    ui.currentvaluessavebutton.setDisabled(False)
    ui.abundancetable.setDisabled(False)

    ui.run.setText("Run")
    ui.run.setStyleSheet("background-color: none")

    # Time Counter
    end = time.time()
    dif = end - init
    time_spent = "Time spent: {:.0f} h {:.0f} m {:.0f} s ({:.0f} s).".format(dif // 3600, (dif // 60) % 60, dif % 60,
                                                                             dif)

    # noinspection PyTypeChecker
    with open(str(Path(folder).joinpath("log.txt")), "a") as f:
        f.write(init_time)
        f.write(time_spent)
        f.write("\n")
        f.close()
    print(time_spent)

    return results_array, ax, plot_line_refer


def main(args):
    # Main subroutine to call the functions

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
                   "\n\nExample:\n./abundance_fit.py meafs_config.txt\n".format(version)
        print(help_msg)


if __name__ == '__main__':
    arg = sys.argv[1:]
    main(arg)  # call main subroutine