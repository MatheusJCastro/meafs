#!/usr/bin/env python3
#####################################################
# MEAFS GUI                                         #
# Matheus J. Castro                                 #
# v4.0                                              #
# Last Modification: 04/12/2024                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

from PyQt6 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
import sys
import os


try:
    from gui_qt import Ui_MEAFS
    from fitsettings_qt import Ui_fitparbox
except ModuleNotFoundError:
    from . import gui_qt
    from . import fitsettings_qt
    Ui_MEAFS = gui_qt.Ui_MEAFS
    Ui_fitparbox = fitsettings_qt.Ui_fitparbox

try:
    from scripts import *
except ModuleNotFoundError:
    from .scripts import *


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys._excepthook = sys.excepthook
sys.excepthook = exception_hook


def handle_interface(ui):
    def show_error(msg):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setWindowTitle("Error")
        error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        error_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
        error_dialog.setText(msg)

        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)
        error_dialog.setFont(font)

        error_dialog.exec()

    def browse(uiobject, caption, direc=None):
        if direc is None:
            direc = os.getcwd()

        fname = QtWidgets.QFileDialog.getOpenFileName(caption=caption,
                                                      filter="Text File (*.txt, *.csv, *)",
                                                      directory=direc)
        if fname[0] != "":
            uiobject.setText(fname[0])

    def browse_dir_out(uiobject, caption, direc=None):
        if direc is None:
            direc = os.getcwd()

        fname = QtWidgets.QFileDialog.getExistingDirectory(caption=caption,
                                                           directory=direc)
        if fname != "":
            if fname[-7:] != "Results":
                fname = str(Path(fname).joinpath("Results"))
            uiobject.setText(fname)

    def tablecheckbox(state):
        item = QtWidgets.QCheckBox()

        if state:
            item.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        item.stateChanged.connect(checkLineliststate)

        layout_cb = QtWidgets.QHBoxLayout()
        layout_cb.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout_cb.setContentsMargins(0, 0, 0, 0)
        layout_cb.addWidget(item)

        checkbox_widget = QtWidgets.QWidget()
        checkbox_widget.setLayout(layout_cb)

        return checkbox_widget

    def loadLinelist():
        fname = ui.linelistname.text()
        if fname != "":
            linelist_data = fit.open_linelist_refer_fl(fname)
            if len(linelist_data) != 0:
                ui.linelistcontent.setRowCount(len(linelist_data))
                ui.linelistcheckbox.setDisabled(False)
                ui.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Checked)

                for i in range(len(linelist_data)):
                    ui.linelistcontent.setItem(i, 0, QtWidgets.QTableWidgetItem(str(linelist_data.iloc[i][0])))
                    ui.linelistcontent.setItem(i, 1, QtWidgets.QTableWidgetItem(str(linelist_data.iloc[i][1])))

                    checkbox_widget = tablecheckbox(True)
                    ui.linelistcontent.setCellWidget(i, 2, checkbox_widget)

                    ui.linelistcontent.resizeColumnsToContents()
            else:
                show_error("Empty Linelist.")

            checkLineliststate()
        else:
            show_error("Empty Linelist location.")

    def checkLinelistElements():
        for i in range(ui.linelistcontent.rowCount()):
            if ui.linelistcheckbox.checkState() == QtCore.Qt.CheckState.Checked:
                checkbox_widget = tablecheckbox(True)
            else:
                checkbox_widget = tablecheckbox(False)

            ui.linelistcontent.setCellWidget(i, 2, checkbox_widget)

        checkLineliststate()

    def checkLineliststate():
        linescurrent = ui.progressvalue.text().split("/")

        checkeds = 0
        unchecked = False
        for i in range(ui.linelistcontent.rowCount()):
            item = ui.linelistcontent.cellWidget(i, 2).layout().itemAt(0).widget()
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                checkeds += 1
            else:
                unchecked = True

        ui.progressvalue.setText("{}/{}".format(linescurrent[0], checkeds))

        if not unchecked:
            ui.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            ui.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def tablecheckboxindividual():
        row = ui.linelistcontent.currentIndex().row()
        col = ui.linelistcontent.currentIndex().column()
        if col == 2:
            item = ui.linelistcontent.cellWidget(row, 2).layout().itemAt(0).widget()

            if item.checkState() == QtCore.Qt.CheckState.Checked:
                checkbox_widget = tablecheckbox(False)
            else:
                checkbox_widget = tablecheckbox(True)

            ui.linelistcontent.setCellWidget(row, 2, checkbox_widget)
            checkLineliststate()

    def loadRefer():
        fname = ui.refername.text()
        if fname != "":
            refer_data = fit.open_linelist_refer_fl(fname)
            if len(refer_data) != 0:
                ui.refercontent.setRowCount(len(refer_data))

                for i in range(len(refer_data)):
                    ui.refercontent.setItem(i, 0, QtWidgets.QTableWidgetItem(str(refer_data.iloc[i][0])))
                    ui.refercontent.setItem(i, 1, QtWidgets.QTableWidgetItem(str(refer_data.iloc[i][1])))

            else:
                show_error("Empty Abundance Reference file.")
        else:
            show_error("Empty Abundance Reference file location.")

    def LineAddRemove(uiobject, add, islinelist=False):
        if add is True:
            new_row = uiobject.rowCount() + 1
            uiobject.setRowCount(new_row)
            if islinelist:
                checkbox_widget = tablecheckbox(False)
                ui.linelistcontent.setCellWidget(new_row - 1, 2, checkbox_widget)
                ui.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            uiobject.setRowCount(uiobject.rowCount() - 1)

    def graymethods(metharray):
        ui.eqwidthtab.setEnabled(metharray[0])
        ui.turbspectrumtab.setEnabled(metharray[1])
        ui.pfanttab.setEnabled(metharray[2])
        ui.synthetab.setEnabled(metharray[3])

    def checkmethod():
        if ui.methodbox.currentIndex() == 0:
            graymethods([True, False, False, False])
            ui.methodstab.setCurrentIndex(0)
        elif ui.methodbox.currentIndex() == 1:
            graymethods([False, True, False, False])
            ui.methodstab.setCurrentIndex(1)
        elif ui.methodbox.currentIndex() == 2:
            graymethods([False, False, True, False])
            ui.methodstab.setCurrentIndex(2)
        elif ui.methodbox.currentIndex() == 3:
            graymethods([False, False, False, True])
            ui.methodstab.setCurrentIndex(3)

    def datatableconfig():
        ui.dataloadtable.setRowCount(10)
        ui.dataloadtable.verticalHeader().setVisible(False)

        for i in range(ui.dataloadtable.rowCount()):
            item = QtWidgets.QTableWidgetItem()
            btn = QtWidgets.QPushButton()
            btn.clicked.connect(datatableselect)
            btn.setText("X")
            btn.setFixedSize(int(1.25*ui.dataloadtable.rowHeight(i)), ui.dataloadtable.rowHeight(i))
            ui.dataloadtable.setItem(i, 0, item)
            ui.dataloadtable.setCellWidget(i, 0, btn)
            ui.dataloadtable.resizeColumnToContents(0)

            item = QtWidgets.QTableWidgetItem()
            btn = QtWidgets.QPushButton()
            btn.clicked.connect(datatableselect)
            btn.setText("Data {}".format(i + 1))
            ui.dataloadtable.setItem(i, 1, item)
            ui.dataloadtable.setCellWidget(i, 1, btn)

            fname = "Data {}".format(i + 1)
            ui.dataloadtable.item(i, 1).setText(fname)
            ui.dataloadtable.item(i, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, fname)

    def datatableselect():
        row = ui.dataloadtable.currentRow()

        item = QtWidgets.QTableWidgetItem()
        btn = QtWidgets.QPushButton()
        btn.clicked.connect(datatableselect)

        fname = [""]
        if ui.dataloadtable.currentColumn() == 1:
            fname = QtWidgets.QFileDialog.getOpenFileName(caption="Select Spectrum Data File",
                                                          filter="Text File (*.txt, *.csv, *)",
                                                          directory=os.getcwd())

        if fname[0] != "":
            fname = fname[0]
            showname = str(Path(fname).parts[-1])
        else:
            if ui.dataloadtable.currentColumn() == 0:
                fname = "Data {}".format(row + 1)
                showname = fname
            else:
                return

        btn.setText(showname)
        ui.dataloadtable.setItem(row, 1, item)
        ui.dataloadtable.setCellWidget(row, 1, btn)
        ui.dataloadtable.item(row, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, fname)
        ui.dataloadtable.resizeColumnToContents(1)

    def loadData():
        nonlocal ax, specs_data

        specs = []
        for i in range(ui.dataloadtable.rowCount()):
            if ui.dataloadtable.item(i, 1).text() != "Data {}".format(i + 1):
                specs.append(ui.dataloadtable.item(i, 1).data(QtCore.Qt.ItemDataRole.ToolTipRole))

        if ui.delimitertype.currentText() == "Comma":
            sep = ","
        elif ui.delimitertype.currentText() == "Tab":
            sep = "\s+"
        else:
            show_error("Delimiter not selected.")
            return

        specs_data = []
        if len(specs) > 0:
            specs_data = fit.open_spec_obs(specs, delimiter=sep)

        ax = fit.plot_spec_gui(specs_data, canvas, ax)

    def run_fit():
        nonlocal results_array, ax, plot_line_refer

        ui.abundancetable.setRowCount(0)
        results_array, ax, plot_line_refer = fit.gui_call(specs_data,
                                                          ui,
                                                          QtCore.Qt.CheckState.Checked,
                                                          canvas,
                                                          ax,
                                                          cut_val=cut_val,
                                                          plot_line_refer=plot_line_refer,
                                                          repfit=repfit)

    def run_fit_nopars():
        nonlocal results_array, ax, plot_line_refer

        opt_pars = [ui.lambshifvalue.value(),
                    ui.continuumvalue.value(),
                    ui.convolutionvalue.value()]

        ui.abundancetable.setRowCount(0)
        results_array, ax, plot_line_refer = fit.gui_call(specs_data,
                                                          ui,
                                                          QtCore.Qt.CheckState.Checked,
                                                          canvas,
                                                          ax,
                                                          cut_val=cut_val,
                                                          plot_line_refer=plot_line_refer,
                                                          opt_pars=opt_pars,
                                                          repfit=repfit)

    def run_nofit():
        nonlocal results_array, ax, plot_line_refer
        print(plot_line_refer)

        opt_pars = [ui.lambshifvalue.value(),
                    ui.continuumvalue.value(),
                    ui.convolutionvalue.value()]
        abundplot = ui.abundancevalue.value()

        results_array, ax, plot_line_refer = fit.gui_call(specs_data,
                                                          ui,
                                                          QtCore.Qt.CheckState.Checked,
                                                          canvas,
                                                          ax,
                                                          cut_val=cut_val,
                                                          plot_line_refer=plot_line_refer,
                                                          opt_pars=opt_pars,
                                                          repfit=0, abundplot=abundplot,
                                                          results_array=results_array)

    def save_cur_abund():
        nonlocal results_array

        currow = ui.abundancetable.currentRow()
        currow = ui.abundancetable.rowCount() - 1 if currow == -1 else currow
        elem = ui.abundancetable.item(currow, 0).text()
        lamb = ui.abundancetable.item(currow, 1).text()
        abund = ui.abundancevalue.value()

        ind = results_array[(results_array["Element"] == elem) & (results_array["Lambda (A)"] == float(lamb))].index
        for i in ind:
            results_array.loc[i, "Fit Abundance"] = abund
            results_array.loc[i, "Differ"] = np.abs(abund-results_array.loc[i, "Refer Abundance"])

        folder = ui.outputname.text()
        save_name = "found_values.csv"
        # Write the line result to the csv file
        results_array.to_csv(Path(folder).joinpath(save_name), index=False, float_format="%.4f")

    def open_prev_results():
        nonlocal results_array, ax

        init_path = ui.outputname.text()
        fname = QtWidgets.QFileDialog.getOpenFileName(caption="Select Previous Results File",
                                                      filter="Text File (*.txt, *.csv, *)",
                                                      directory=init_path)[0]
        line, results_array = fit.open_previous([], [], fl_name=fname)

        ui.abundancetable.setRowCount(len(results_array))
        for i in range(len(results_array)):
            elem = results_array.iloc[i, 0]
            lamb = results_array.iloc[i, 1]

            ui.abundancetable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(elem)))
            ui.abundancetable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(lamb)))

            path = Path(os.path.dirname(fname)).joinpath("On_time_Plots")
            count = 0
            while True:
                file = path.joinpath("fit_{}_{}_ang_{}.csv".format(elem, lamb, count + 1))

                if os.path.isfile(file):
                    data = pd.read_csv(file)
                    count += 1
                    ax.plot(data.iloc[:, 0], data.iloc[:, 1], "--", linewidth=1.5)
                    ax.axvline(lamb, ls="-.", c="red", linewidth=.5)
                else:
                    break
            canvas.draw()

    def results_show_tab():
        nonlocal results_array, ax

        currow = ui.abundancetable.currentRow()

        ui.lambshifvalue.setValue(results_array.iloc[currow, 2])
        ui.continuumvalue.setValue(results_array.iloc[currow, 3])
        ui.convolutionvalue.setValue(results_array.iloc[currow, 4])
        ui.abundancevalue.setValue(results_array.iloc[currow, 6])

        ax.set_xlim(results_array.iloc[currow, 1] - cut_val[3],
                    results_array.iloc[currow, 1] + cut_val[3])
        canvas.draw()

    def full_spec_plot_range():
        nonlocal ax

        if specs_data != []:
            xmin_all_old = min(specs_data[0].iloc[:, 0])
            xmax_all_old = max(specs_data[0].iloc[:, 0])
            ymin_all_old = min(specs_data[0].iloc[:, 1])
            ymax_all_old = max(specs_data[0].iloc[:, 1])
        else:
            xmin_all_old = 0
            xmax_all_old = 1
            ymin_all_old = 0
            ymax_all_old = 1

        for spec in specs_data:
            xmin_all = min(spec.iloc[:, 0])
            xmax_all = max(spec.iloc[:, 0])
            if xmin_all < xmin_all_old:
                xmin_all_old = xmin_all
            if xmax_all > xmax_all_old:
                xmax_all_old = xmax_all

            ymin_all = min(spec.iloc[:, 1])
            ymax_all = max(spec.iloc[:, 1])
            if ymin_all < ymin_all_old:
                ymin_all_old = ymin_all
            if ymax_all > ymax_all_old:
                ymax_all_old = ymax_all

        ax.set_xlim(xmin_all_old, xmax_all_old)
        ax.set_ylim(ymin_all_old, ymax_all_old*1.05)
        canvas.draw()

    def fitparWindow():
        nonlocal repfit, cut_val

        def accept():
            nonlocal repfit, cut_val
            repfit = uifitset.repfitvalue.value()
            cut_val = [uifitset.contwavecutvalue.value()/2,
                       uifitset.convovcutvalue.value()/2,
                       uifitset.abundcutvalue.value()/2,
                       uifitset.plotcutvalue.value()/2]

        def check_convov():
            if uifitset.convovcutvalue.value() > uifitset.contwavecutvalue.value():
                uifitset.convovcutvalue.setValue(uifitset.contwavecutvalue.value())
                show_error("Convolution Fit Range can not be higher than Continuum/Wave. Shit range.")

        def check_contwave():
            if uifitset.convovcutvalue.value() > uifitset.contwavecutvalue.value():
                uifitset.convovcutvalue.setValue(uifitset.contwavecutvalue.value())

        fitparbox = QtWidgets.QDialog()
        uifitset = Ui_fitparbox()
        uifitset.setupUi(fitparbox)

        uifitset.repfitvalue.setValue(repfit)
        uifitset.contwavecutvalue.setValue(cut_val[0]*2)
        uifitset.convovcutvalue.setValue(cut_val[1]*2)
        uifitset.abundcutvalue.setValue(cut_val[2]*2)
        uifitset.plotcutvalue.setValue(cut_val[3]*2)
        uifitset.okcancelbutton.accepted.connect(accept)

        uifitset.contwavecutvalue.valueChanged.connect(check_contwave)
        uifitset.convovcutvalue.valueChanged.connect(check_convov)

        fitparbox.exec()

    # Linelist Configuration
    ui.linelistcontent.setRowCount(5)
    ui.linelistcontent.setAlternatingRowColors(True)
    checkLinelistElements()

    ui.linelistbrowse.clicked.connect(lambda: browse(ui.linelistname, "Select Linelist File", os.getcwd()))
    ui.linelistcontent.resizeColumnsToContents()
    ui.linelistload.clicked.connect(loadLinelist)
    ui.linelistcheckbox.setDisabled(False)
    ui.linelistcheckbox.clicked.connect(checkLinelistElements)
    ui.linelistcontent.clicked.connect(tablecheckboxindividual)
    ui.linelistaddline.clicked.connect(lambda: LineAddRemove(ui.linelistcontent, True, islinelist=True))
    ui.linelistremoveline.clicked.connect(lambda: LineAddRemove(ui.linelistcontent, False, islinelist=True))

    # Abundance Reference Configuration
    ui.refercontent.setRowCount(5)
    ui.refercontent.setAlternatingRowColors(True)
    ui.referbrowse.clicked.connect(lambda: browse(ui.refername, "Select Abundance Refence File", direc=os.getcwd()))
    ui.referload.clicked.connect(loadRefer)
    ui.referaddline.clicked.connect(lambda: LineAddRemove(ui.refercontent, True))
    ui.referremoveline.clicked.connect(lambda: LineAddRemove(ui.refercontent, False))

    # Methods General Configuration
    ui.methodbox.model().item(2).setEnabled(False)
    ui.methodbox.model().item(3).setEnabled(False)

    ui.methodbox.setCurrentIndex(1)
    ui.methodbox.currentIndexChanged.connect(checkmethod)

    checkmethod()

    # TurboSpectrum Configuration
    mainpath = Path(__file__).parts[:-1]
    pathconfig = Path(mainpath[0]).joinpath(*mainpath[1:]).joinpath("modules", "Turbospectrum2019",
                                                                    "COM-v19.1")
    ui.turbospectrumconfigname.setText(str(pathconfig))
    pathoutput = Path(mainpath[0]).joinpath(*mainpath[1:]).joinpath("modules", "Turbospectrum2019",
                                                                    "COM-v19.1", "syntspec")
    ui.turbospectrumoutputname.setText(str(pathoutput))

    if not os.path.exists(pathconfig):
        pathconfig = os.getcwd()
    if not os.path.exists(pathoutput):
        pathoutput = os.getcwd()

    ui.turbospectrumconfigbrowse.clicked.connect(lambda: browse(ui.turbospectrumconfigname,
                                                                "Select TurboSpectrum Configuration File",
                                                                direc=str(pathconfig)))
    ui.turbospectrumoutputbrowse.clicked.connect(lambda: browse(ui.turbospectrumoutputname,
                                                                "Select TurboSpectrum Output File",
                                                                direc=str(pathoutput)))

    # Plot Configuration
    fig = plt.figure(tight_layout=True)
    canvas = FigureCanvasQTAgg(fig)
    canvas.figure.supxlabel("Wavelength [\u212B]")
    canvas.figure.supylabel("Flux")
    ax = canvas.figure.add_subplot(111)
    ax.grid()
    canvas.draw()
    ui.plot.addWidget(canvas)
    plot_line_refer = pd.DataFrame(columns=["elem", "wave", "refer"])

    toolbar = QtWidgets.QToolBar()
    toolbar.addWidget(NavigationToolbar2QT(canvas))
    ui.plot.addWidget(toolbar)

    # Data Configuration
    ui.methodsdatafittab.setCurrentIndex(0)
    datatableconfig()
    ui.delimitertype.setCurrentIndex(0)
    ui.delimitertype.model().item(0).setEnabled(False)
    ui.delimitertype.setToolTip("Delimiter Type")

    specs_data = []
    ui.loaddata.clicked.connect(loadData)

    # Output Configuration
    folder_name = os.getcwd()
    if folder_name[-7:] != "Results":
        folder_name = str(Path(folder_name).joinpath("Results"))
    ui.outputname.setText(folder_name)
    ui.outputbrowse.clicked.connect(lambda: browse_dir_out(ui.outputname, "Select Output Folder",
                                                           direc=os.getcwd()))

    # Run Configuration
    results_array = pd.DataFrame()

    ui.run.clicked.connect(run_fit)

    # Run Manual Fit Configuration
    ui.manualfitbutton.clicked.connect(run_fit_nopars)

    # Run Plot Current Values Configuration
    ui.currentvaluesplotbutton.clicked.connect(run_nofit)

    # Run Save Current Abundance Configuration
    ui.currentvaluessavebutton.clicked.connect(save_cur_abund)

    # Abundance Table Configuration
    ui.abundancetable.clicked.connect(results_show_tab)

    # File Submenu Configuration
    ui.openabundances.triggered.connect(open_prev_results)
    ui.quit.triggered.connect(lambda: exit("Exit button pressed."))

    ui.new_2.setIcon(QtGui.QIcon.fromTheme('document-new'))
    ui.open.setIcon(QtGui.QIcon.fromTheme('document-open'))
    ui.openabundances.setIcon(QtGui.QIcon.fromTheme('document-open'))
    ui.save.setIcon(QtGui.QIcon.fromTheme('document-save'))
    ui.saveas.setIcon(QtGui.QIcon.fromTheme('document-save-as'))
    ui.quit.setIcon(QtGui.QIcon.fromTheme('application-exit'))

    # Edit Submenu Configuration
    ui.fitpar.triggered.connect(fitparWindow)
    repfit = 2
    cut_val = [10/2, 3/2, .4/2, 1/2]

    # View Submenu Configuration
    ui.fullspec.triggered.connect(full_spec_plot_range)

    # TEMPORARY
    repfit = 1
    ui.linelistname.setText("/home/castro/Desktop/Sync/MEAFS GUI/meafs_code/temp/LinesALL.csv")
    ui.refername.setText("/home/castro/Desktop/Sync/MEAFS GUI/meafs_code/temp/refer_values.csv")
    ui.delimitertype.setCurrentIndex(2)
    ui.turbospectrumconfigname.setText("/home/castro/Desktop/Sync/MEAFS GUI/meafs_code/modules/"
                                       "Turbospectrum2019/COM-v19.1/CS31.com")
    ui.turbospectrumoutputname.setText("/home/castro/Desktop/Sync/MEAFS GUI/meafs_code/modules/"
                                       "Turbospectrum2019/COM-v19.1/syntspec/CS31-HFS-Vtest.spec")
    ui.dataloadtable.item(0, 1).setText("aaa")
    ui.dataloadtable.item(0, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, "/home/castro/Desktop/Sync/MEAFS GUI/"
                                                                            "meafs_code/temp/cs340n.dat")


def main():
    app = QtWidgets.QApplication(sys.argv)
    MEAFS = QtWidgets.QMainWindow()
    ui = Ui_MEAFS()
    ui.setupUi(MEAFS)

    handle_interface(ui)

    MEAFS.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
