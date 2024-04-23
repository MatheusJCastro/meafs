#!/usr/bin/env python3
#####################################################
# MEAFS GUI                                         #
# Matheus J. Castro                                 #
# v4.6                                              #
# Last Modification: 04/23/2024                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

from PyQt6 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
import dill
import sys
import os

version = 4.6

try:
    from gui_qt import Ui_MEAFS
except ModuleNotFoundError:
    from . import gui_qt
    Ui_MEAFS = gui_qt.Ui_MEAFS

try:
    from fitsettings_qt import Ui_fitparbox
except ModuleNotFoundError:
    from . import fitsettings_qt
    Ui_fitparbox = fitsettings_qt.Ui_fitparbox

try:
    from scripts import *
except ModuleNotFoundError:
    from .scripts import *

try:
    from desktop_entry import get_curr_dir
except ModuleNotFoundError:
    from . import desktop_entry
    get_curr_dir = desktop_entry.get_curr_dir


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys._excepthook = sys.excepthook
sys.excepthook = exception_hook


class MEAFS(QtWidgets.QMainWindow, Ui_MEAFS):
    def __init__(self, parent=None):
        # Arguments Configuration 1
        self.args = sys.argv
        self.argument_resolve(fastcheck=True)

        # Load Gui
        super(MEAFS, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(str(Path(os.path.dirname(__file__)).joinpath("images", "Meafs_Icon.ico"))))

        # Read Settings
        self.sett_path = Path(os.path.dirname(__file__)).joinpath("settings.csv")
        self.settings = pd.read_csv(self.sett_path,  delimiter=",", index_col=None)
        self.autosave.setChecked(self.settings[self.settings.variable == "auto_save"].value.iloc[0])

        # Create modules folder (not distributed in GitHub)
        if not os.path.exists(Path(os.path.dirname(__file__)).joinpath("modules")):
            os.mkdir(Path(os.path.dirname(__file__)).joinpath("modules"))

        # Linelist Configuration
        self.linelistcontent.setRowCount(5)
        self.linelistcontent.setAlternatingRowColors(True)
        self.checkLinelistElements()

        self.linelistbrowse.clicked.connect(lambda: self.browse(self.linelistname, "Select Linelist File", os.getcwd()))
        self.linelistcontent.resizeColumnsToContents()
        self.linelistload.clicked.connect(self.loadLinelist)
        self.linelistcheckbox.setDisabled(False)
        self.linelistcheckbox.clicked.connect(self.checkLinelistElements)
        self.linelistcontent.clicked.connect(self.tablecheckboxindividual)
        self.linelistaddline.clicked.connect(lambda: self.LineAddRemove(self.linelistcontent, True, islinelist=True))
        self.linelistremoveline.clicked.connect(lambda: self.LineAddRemove(self.linelistcontent, False, islinelist=True))

        # Abundance Reference Configuration
        self.refercontent.setRowCount(5)
        self.refercontent.setAlternatingRowColors(True)
        self.referbrowse.clicked.connect(lambda: self.browse(self.refername, "Select Abundance Refence File", direc=os.getcwd()))
        self.referload.clicked.connect(self.loadRefer)
        self.referaddline.clicked.connect(lambda: self.LineAddRemove(self.refercontent, True))
        self.referremoveline.clicked.connect(lambda: self.LineAddRemove(self.refercontent, False))

        # Methods General Configuration
        self.methodbox.model().item(2).setEnabled(False)
        self.methodbox.model().item(3).setEnabled(False)

        self.methodbox.setCurrentIndex(0)
        self.methodbox.currentIndexChanged.connect(self.checkmethod)

        self.checkmethod()

        # Eq. Width Configuration
        self.convinitguessvalue.setValue(0.001)
        self.deepthinitguessvalue.setValue(-1)

        # TurboSpectrum Configuration
        self.mainpath = Path(__file__).parts[:-1]
        self.pathconfig = Path(self.mainpath[0]).joinpath(*self.mainpath[1:]).joinpath("modules", "Turbospectrum2019",
                                                                                       "COM-v19.1")
        self.turbospectrumconfigname.setText(str(self.pathconfig))
        self.pathoutput = Path(self.mainpath[0]).joinpath(*self.mainpath[1:]).joinpath("modules", "Turbospectrum2019",
                                                                                       "COM-v19.1", "syntspec")
        self.turbospectrumoutputname.setText(str(self.pathoutput))

        if not os.path.exists(self.pathconfig):
            self.pathconfig = os.getcwd()
        if not os.path.exists(self.pathoutput):
            self.pathoutput = os.getcwd()

        self.turbospectrumconfigbrowse.clicked.connect(lambda: self.browse(self.turbospectrumconfigname,
                                                                           "Select TurboSpectrum Configuration File",
                                                                           direc=str(self.pathconfig)))
        self.turbospectrumoutputbrowse.clicked.connect(lambda: self.browse(self.turbospectrumoutputname,
                                                                           "Select TurboSpectrum Output File",
                                                                           direc=str(self.pathoutput)))

        # Plot Configuration
        self.fig = plt.figure(tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.figure.supxlabel("Wavelength [\u212B]")
        self.canvas.figure.supylabel("Flux")
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.grid()
        self.canvas.draw()
        self.plot.addWidget(self.canvas)
        self.plot_line_refer = pd.DataFrame(columns=["elem", "wave", "refer"])

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addWidget(NavigationToolbar2QT(self.canvas))
        self.plot.addWidget(self.toolbar)

        # Data Configuration
        self.methodsdatafittab.setCurrentIndex(0)
        self.datatableconfig()
        self.delimitertype.setCurrentIndex(0)
        self.delimitertype.model().item(0).setEnabled(False)
        self.delimitertype.setToolTip("Delimiter Type")

        self.specs_data = []
        self.loaddata.clicked.connect(self.loadData)

        # Output Configuration
        folder_name = os.getcwd()
        if folder_name[-7:] != "Results":
            folder_name = str(Path(folder_name).joinpath("Results"))
        self.outputname.setText(folder_name)
        self.outputbrowse.clicked.connect(lambda: self.browse_dir_out(self.outputname, "Select Output Folder",
                                                                      direc=os.getcwd()))

        # Run Configuration
        self.results_array = pd.DataFrame()

        self.run.clicked.connect(self.run_fit)

        # Run Manual Fit Configuration
        self.manualfitbutton.clicked.connect(self.run_fit_nopars)

        # Run Plot Current Values Configuration
        self.currentvaluesplotbutton.clicked.connect(self.run_nofit)

        # Run Save Current Abundance Configuration
        self.currentvaluessavebutton.clicked.connect(self.save_cur_abund)

        # Abundance Table Configuration
        self.abundancetable.clicked.connect(self.results_show_tab)

        # File Submenu Configuration
        self.new_2.setIcon(QtGui.QIcon.fromTheme('document-new'))
        self.open.setIcon(QtGui.QIcon.fromTheme('document-open'))
        self.openabundances.setIcon(QtGui.QIcon.fromTheme('document-open'))
        self.save.setIcon(QtGui.QIcon.fromTheme('document-save'))
        self.saveas.setIcon(QtGui.QIcon.fromTheme('document-save-as'))
        self.autosave.setIcon(QtGui.QIcon.fromTheme('chronometer'))
        self.quit.setIcon(QtGui.QIcon.fromTheme('application-exit'))

        self.filepath = None
        self.new_2.triggered.connect(self.new_session)
        # For some reason only in the line bellow the first argument after self is sent with False value,
        # direc needs to be None
        self.open.triggered.connect(lambda: self.load_session())
        self.openabundances.triggered.connect(self.open_prev_results)
        self.save.triggered.connect(self.save_session)
        self.saveas.triggered.connect(lambda: self.save_session(saveas=True))
        self.quit.triggered.connect(self.quitbtn)

        # Edit Submenu Configuration
        self.fitpar.triggered.connect(self.fitparWindow)
        self.repfit = 2
        self.cut_val = [10 / 2, 3 / 2, .4 / 2, 1 / 2]
        self.max_iter = [1000, 1000, 10]
        self.convovbound = [0, 5]
        self.wavebound = .2
        self.continuumpars = [2, 8]

        # View Submenu Configuration
        self.fullspec.triggered.connect(self.full_spec_plot_range)
        self.checkcontinuumplot.triggered.connect(self.run_check_continuum)
        self.erasecontinuumplot.triggered.connect(self.run_erase_continuum)

        # Auto Save Configuration
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.auto_save)
        self.timer.setInterval(5000)
        if self.autosave.isChecked():
            self.timer.start()

        self.autosave.triggered.connect(self.enable_auto_save)

        # Arguments Configuration 2
        self.argument_resolve()

        # TEMPORARY
        self.repfit = 1
        self.linelistname.setText("/home/castro/Desktop/MEAFS GUI/meafs_code/temp/LinesALL.csv")
        self.refername.setText("/home/castro/Desktop/MEAFS GUI/meafs_code/temp/refer_values.csv")
        self.delimitertype.setCurrentIndex(2)
        self.turbospectrumconfigname.setText("/home/castro/Desktop/MEAFS GUI/meafs_code/modules/"
                                             "Turbospectrum2019/COM-v19.1/CS31.com")
        self.turbospectrumoutputname.setText("/home/castro/Desktop/MEAFS GUI/meafs_code/modules/"
                                             "Turbospectrum2019/COM-v19.1/syntspec/CS31-HFS-Vtest.spec")
        self.dataloadtable.item(0, 1).setText("aaa")
        self.dataloadtable.item(0, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, "/home/castro/Desktop/MEAFS GUI/"
                                                                                  "meafs_code/temp/cs340n.dat")
        self.methodbox.setCurrentIndex(0)
        self.max_iter = [1000, 1000, 1]

    def keyPressEvent(self, event):
        if isinstance(event, QtGui.QKeyEvent):
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                if event.key() == QtCore.Qt.Key.Key_S:
                    self.save_session()
                if event.key() == QtCore.Qt.Key.Key_V:
                    self.full_spec_plot_range()

    def closeEvent(self, event):
        if self.show_quit():
            event.accept()
        else:
            event.ignore()

    def quitbtn(self):
        if self.show_quit():
            exit("Exit button pressed.")

    def show_quit(self):
        close_dialog = QtWidgets.QMessageBox()
        close_dialog.setWindowTitle("Quit")
        close_dialog.setText("Are you sure want to quit MEAFS?")
        close_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
        close_dialog.addButton(QtWidgets.QMessageBox.StandardButton.No)
        close_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        if close_dialog.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            if self.autosave.isChecked():
                flname = Path(os.path.dirname(__file__)).joinpath("auto_save_last.pkl")
                self.save_session(flname=flname)
            return True
        else:
            return False

    def enable_auto_save(self):
        if self.autosave.isChecked():
            self.settings.loc[self.settings.variable == "auto_save", "value"] = 1
            self.timer.start()
        else:
            self.settings.loc[self.settings.variable == "auto_save", "value"] = 0
            self.timer.stop()

        # noinspection PyTypeChecker
        self.settings.to_csv(self.sett_path, index=None)

    def auto_save(self):
        if self.filepath is None:
            flname = Path(os.path.dirname(__file__)).joinpath("auto_save.pkl")
            self.save_session(flname=flname)
        else:
            self.save_session()

    def argument_resolve(self, fastcheck=False):
        if "-h" in self.args or "--help" in self.args:
            path1 = Path(os.path.dirname(__file__)).joinpath("auto_save_last.pkl")
            path2 = Path(os.path.dirname(__file__)).joinpath("auto_save.pkl")
            help_msg = "\n\t\t\033[1;31mHelp Section\033[m\nMEAFS v{}\n" \
                       "Usage: python3 gui.py [options] argument\n\n" \
                       "Written by Matheus J. Castro <https://github.com/MatheusJCastro/meafs>\n" \
                       "Under MIT License.\n\n" \
                       "This program finds abundances of elements for a given spectrum.\n" \
                       "GUI developed using PyQt.\n\n" \
                       "Argument needs to be a Pickle File (.pkl) previously saved by MEAFS.\n" \
                       "If no argument is given, an empty session will be opened.\n\n" \
                       "Options are:\n" \
                       " -h, --help\t\t|\tShow this help;\n" \
                       " -v, --version\t\t|\tShow version number;\n" \
                       " -l, --last\t\t|\tLoad the last closed session. Default location is:\n" \
                       "\t\t\t|\t{}\n" \
                       " -s, --load-auto-save\t|\tLoad the auto saved session. Default location is:\n" \
                       "\t\t\t|\t{}\n" \
                       "\n\nExample:\n./gui.py sesssion.pkl\n".format(version, path1, path2)
            print(help_msg)
            exit()
        elif "-v" in self.args or "--version" in self.args:
            print("MEAFS v{}".format(version))
            exit()
        elif ("-l" in self.args or "--last" in self.args) and not fastcheck:
            self.filepath = Path(os.path.dirname(__file__)).joinpath("auto_save_last.pkl")
            self.load_session(loadprev=True)
        elif ("-s" in self.args or "--load-auto-save" in self.args) and not fastcheck:
            self.filepath = Path(os.path.dirname(__file__)).joinpath("auto_save.pkl")
            self.load_session(loadprev=True)
        elif len(self.args) == 2 and not fastcheck:
            if os.path.isfile(self.args[1]) and self.args[1][-4:] == ".pkl":
                self.filepath = self.args[1]
                self.load_session(loadprev=True)
            else:
                exit("File not found or type not recognized.")

    @staticmethod
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

    @staticmethod
    def browse(uiobject, caption, direc=None):
        if direc is None:
            direc = os.getcwd()

        fname = QtWidgets.QFileDialog.getOpenFileName(caption=caption,
                                                      filter="Text File (*.txt, *.csv, *)",
                                                      directory=direc)
        if fname[0] != "":
            uiobject.setText(fname[0])

    @staticmethod
    def browse_dir_out(uiobject, caption, direc=None):
        if direc is None:
            direc = os.getcwd()

        fname = QtWidgets.QFileDialog.getExistingDirectory(caption=caption,
                                                           directory=direc)
        if fname != "":
            if fname[-7:] != "Results":
                fname = str(Path(fname).joinpath("Results"))
            uiobject.setText(fname)

    def tablecheckbox(self, state):
        item = QtWidgets.QCheckBox()

        if state:
            item.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        # noinspection PyUnresolvedReferences
        item.stateChanged.connect(self.checkLineliststate)

        layout_cb = QtWidgets.QHBoxLayout()
        layout_cb.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout_cb.setContentsMargins(0, 0, 0, 0)
        layout_cb.addWidget(item)

        checkbox_widget = QtWidgets.QWidget()
        checkbox_widget.setLayout(layout_cb)

        return checkbox_widget

    def loadLinelist(self):
        fname = self.linelistname.text()
        if fname != "":
            linelist_data = fit.open_linelist_refer_fl(fname)
            if len(linelist_data) != 0:
                self.linelistcontent.setRowCount(len(linelist_data))
                self.linelistcheckbox.setDisabled(False)
                self.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Checked)

                for i in range(len(linelist_data)):
                    self.linelistcontent.setItem(i, 0, QtWidgets.QTableWidgetItem(str(linelist_data.iloc[i][0])))
                    self.linelistcontent.setItem(i, 1, QtWidgets.QTableWidgetItem(str(linelist_data.iloc[i][1])))

                    checkbox_widget = self.tablecheckbox(True)
                    self.linelistcontent.setCellWidget(i, 2, checkbox_widget)

                    self.linelistcontent.resizeColumnsToContents()
            else:
                self.show_error("Empty Linelist.")

            self.checkLineliststate()
        else:
            self.show_error("Empty Linelist location.")

    def checkLinelistElements(self):
        for i in range(self.linelistcontent.rowCount()):
            if self.linelistcheckbox.checkState() == QtCore.Qt.CheckState.Checked:
                checkbox_widget = self.tablecheckbox(True)
            else:
                checkbox_widget = self.tablecheckbox(False)

            self.linelistcontent.setCellWidget(i, 2, checkbox_widget)

        self.checkLineliststate()

    def checkLineliststate(self):
        linescurrent = self.progressvalue.text().split("/")

        checkeds = 0
        unchecked = False
        for i in range(self.linelistcontent.rowCount()):
            item = self.linelistcontent.cellWidget(i, 2).layout().itemAt(0).widget()
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                checkeds += 1
            else:
                unchecked = True

        self.progressvalue.setText("{}/{}".format(linescurrent[0], checkeds))

        if not unchecked:
            self.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def tablecheckboxindividual(self):
        row = self.linelistcontent.currentIndex().row()
        col = self.linelistcontent.currentIndex().column()
        if col == 2:
            item = self.linelistcontent.cellWidget(row, 2).layout().itemAt(0).widget()

            if item.checkState() == QtCore.Qt.CheckState.Checked:
                checkbox_widget = self.tablecheckbox(False)
            else:
                checkbox_widget = self.tablecheckbox(True)

            self.linelistcontent.setCellWidget(row, 2, checkbox_widget)
            self.checkLineliststate()

    def loadRefer(self):
        fname = self.refername.text()
        if fname != "":
            refer_data = fit.open_linelist_refer_fl(fname)
            if len(refer_data) != 0:
                self.refercontent.setRowCount(len(refer_data))

                for i in range(len(refer_data)):
                    self.refercontent.setItem(i, 0, QtWidgets.QTableWidgetItem(str(refer_data.iloc[i][0])))
                    self.refercontent.setItem(i, 1, QtWidgets.QTableWidgetItem(str(refer_data.iloc[i][1])))

            else:
                self.show_error("Empty Abundance Reference file.")
        else:
            self.show_error("Empty Abundance Reference file location.")

    def LineAddRemove(self, uiobject, add, islinelist=False):
        if add is True:
            new_row = uiobject.rowCount() + 1
            uiobject.setRowCount(new_row)
            if islinelist:
                checkbox_widget = self.tablecheckbox(False)
                self.linelistcontent.setCellWidget(new_row - 1, 2, checkbox_widget)
                self.linelistcheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            uiobject.setRowCount(uiobject.rowCount() - 1)

    def graymethods(self, metharray):
        self.eqwidthtab.setEnabled(metharray[0])
        self.turbspectrumtab.setEnabled(metharray[1])
        self.pfanttab.setEnabled(metharray[2])
        self.synthetab.setEnabled(metharray[3])

    def checkmethod(self):
        if self.methodbox.currentIndex() == 0:
            self.graymethods([True, False, False, False])
            self.methodstab.setCurrentIndex(0)
        elif self.methodbox.currentIndex() == 1:
            self.graymethods([False, True, False, False])
            self.methodstab.setCurrentIndex(1)
        elif self.methodbox.currentIndex() == 2:
            self.graymethods([False, False, True, False])
            self.methodstab.setCurrentIndex(2)
        elif self.methodbox.currentIndex() == 3:
            self.graymethods([False, False, False, True])
            self.methodstab.setCurrentIndex(3)

    def datatableconfig(self, load=False, loaddata=None):
        self.dataloadtable.setRowCount(10)
        self.dataloadtable.verticalHeader().setVisible(False)

        for i in range(self.dataloadtable.rowCount()):
            item = QtWidgets.QTableWidgetItem()
            btn = QtWidgets.QPushButton()
            # noinspection PyUnresolvedReferences
            btn.clicked.connect(self.datatableselect)
            btn.setText("X")
            btn.setFixedSize(int(1.25*self.dataloadtable.rowHeight(i)), self.dataloadtable.rowHeight(i))
            self.dataloadtable.setItem(i, 0, item)
            self.dataloadtable.setCellWidget(i, 0, btn)
            self.dataloadtable.resizeColumnToContents(0)

            if not load:
                fname = "Data {}".format(i + 1)
                showname = fname
            else:
                fname = loaddata["Data"][i]
                showname = str(Path(fname).parts[-1])

            item = QtWidgets.QTableWidgetItem()
            btn = QtWidgets.QPushButton()
            # noinspection PyUnresolvedReferences
            btn.clicked.connect(self.datatableselect)
            btn.setText(showname)
            self.dataloadtable.setItem(i, 1, item)
            self.dataloadtable.setCellWidget(i, 1, btn)

            self.dataloadtable.item(i, 1).setText(showname)
            self.dataloadtable.item(i, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, fname)

    def datatableselect(self):
        row = self.dataloadtable.currentRow()

        fname = [""]
        if self.dataloadtable.currentColumn() == 1:
            fname = QtWidgets.QFileDialog.getOpenFileName(caption="Select Spectrum Data File",
                                                          filter="Text File (*.txt, *.csv, *)",
                                                          directory=os.getcwd())

        if fname[0] != "":
            fname = fname[0]
            showname = str(Path(fname).parts[-1])
        else:
            if self.dataloadtable.currentColumn() == 0:
                fname = "Data {}".format(row + 1)
                showname = fname
            else:
                return

        item = QtWidgets.QTableWidgetItem()
        btn = QtWidgets.QPushButton()
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.datatableselect)
        btn.setText(showname)
        self.dataloadtable.setItem(row, 1, item)
        self.dataloadtable.setCellWidget(row, 1, btn)
        self.dataloadtable.item(row, 1).setText(showname)
        self.dataloadtable.item(row, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, fname)
        self.dataloadtable.resizeColumnToContents(1)

    def loadData(self):
        specs = []
        for i in range(self.dataloadtable.rowCount()):
            if self.dataloadtable.item(i, 1).text() != "Data {}".format(i + 1):
                specs.append(self.dataloadtable.item(i, 1).data(QtCore.Qt.ItemDataRole.ToolTipRole))

        if self.delimitertype.currentText() == "Comma":
            sep = ","
        elif self.delimitertype.currentText() == "Tab":
            sep = "\s+"
        else:
            self.show_error("Delimiter not selected.")
            return

        self.specs_data = []
        if len(specs) > 0:
            self.specs_data = fit.open_spec_obs(specs, delimiter=sep)

        self.plot_line_refer = fit.plot_spec_gui(self.specs_data, self.canvas, self.ax, self.plot_line_refer)

    def check_output_folder(self):
        if self.outputname.text() == "":
            self.show_error("Empty Output Location.")
            return False
        return True

    def run_fit(self):
        if self.check_output_folder():
            self.abundancetable.setRowCount(0)
            self.results_array, self.ax, self.plot_line_refer = fit.gui_call(self.specs_data,
                                                                             self,
                                                                             QtCore.Qt.CheckState.Checked,
                                                                             self.canvas,
                                                                             self.ax,
                                                                             cut_val=self.cut_val,
                                                                             plot_line_refer=self.plot_line_refer,
                                                                             repfit=self.repfit)

    def run_fit_nopars(self):
        if self.check_output_folder():
            opt_pars = [self.lambshifvalue.value(),
                        self.continuumvalue.value(),
                        self.convolutionvalue.value()]

            self.abundancetable.setRowCount(0)
            self.results_array, self.ax, self.plot_line_refer = fit.gui_call(self.specs_data,
                                                                             self,
                                                                             QtCore.Qt.CheckState.Checked,
                                                                             self.canvas,
                                                                             self.ax,
                                                                             cut_val=self.cut_val,
                                                                             plot_line_refer=self.plot_line_refer,
                                                                             opt_pars=opt_pars,
                                                                             repfit=self.repfit)

    def run_nofit(self):
        if self.check_output_folder():
            opt_pars = [self.lambshifvalue.value(),
                        self.continuumvalue.value(),
                        self.convolutionvalue.value()]
            abundplot = self.abundancevalue.value()

            self.results_array, self.ax, self.plot_line_refer = fit.gui_call(self.specs_data,
                                                                             self,
                                                                             QtCore.Qt.CheckState.Checked,
                                                                             self.canvas,
                                                                             self.ax,
                                                                             cut_val=self.cut_val,
                                                                             plot_line_refer=self.plot_line_refer,
                                                                             opt_pars=opt_pars,
                                                                             repfit=0, abundplot=abundplot,
                                                                             results_array=self.results_array)

    def run_check_continuum(self):
        folder = self.outputname.text()
        elem, order, lamb = "continuum", "", "all"

        for i, spec_obs in enumerate(self.specs_data):
            continuum, cont_err = ff.fit_continuum(spec_obs, contpars=self.continuumpars,
                                                   iterac=self.max_iter[0])

            x = np.linspace(min(spec_obs.iloc[:, 0]), max(spec_obs.iloc[:, 0]), 1000)
            y = np.zeros(1000) + continuum
            spec_plot = pd.DataFrame({0: x, 1: y})

            spec_fit_arr = [spec_plot]
            self.plot_line_refer = fit.plot_spec_ui(spec_fit_arr, folder, elem, lamb+str(i), order,
                                                    self.ax, self.canvas, self.plot_line_refer)

        self.full_spec_plot_range()

    def run_erase_continuum(self):
        ind = self.plot_line_refer[(self.plot_line_refer["elem"] == "continuum")].index
        for line in self.plot_line_refer.loc[ind, "refer"]: line.remove()
        self.plot_line_refer.drop(ind, inplace=True)
        self.plot_line_refer.reset_index(drop=True, inplace=True)

        self.canvas.draw()

    def save_cur_abund(self):
        currow = self.abundancetable.currentRow()
        currow = self.abundancetable.rowCount() - 1 if currow == -1 else currow
        elem = self.abundancetable.item(currow, 0).text()
        lamb = self.abundancetable.item(currow, 1).text()
        abund = self.abundancevalue.value()

        ind = self.results_array[(self.results_array["Element"] == elem) & (self.results_array["Lambda (A)"] == float(lamb))].index
        for i in ind:
            self.results_array.loc[i, "Fit Abundance"] = abund
            self.results_array.loc[i, "Differ"] = np.abs(abund-self.results_array.loc[i, "Refer Abundance"])
            self.results_array.loc[i, "Lamb Shift"] = self.lambshifvalue.value()
            self.results_array.loc[i, "Continuum"] = self.continuumvalue.value()
            self.results_array.loc[i, "Convolution"] = self.convolutionvalue.value()

        folder = self.outputname.text()

        # Create necessary folders
        if not os.path.exists(folder):
            os.mkdir(folder)
        if not os.path.exists(Path(folder).joinpath("On_time_Plots")):
            os.mkdir(Path(folder).joinpath("On_time_Plots"))

        save_name = "found_values.csv"
        # Write the line result to the csv file
        self.results_array.to_csv(Path(folder).joinpath(save_name), index=False, float_format="%.4f")

    def open_prev_results(self):
        init_path = self.outputname.text()
        fname = QtWidgets.QFileDialog.getOpenFileName(caption="Select Previous Results File",
                                                      filter="Text File (*.txt, *.csv, *)",
                                                      directory=init_path)[0]
        line, self.results_array = fit.open_previous([], [], fl_name=fname)

        self.abundancetable.setRowCount(len(self.results_array))
        for i in range(len(self.results_array)):
            elem = self.results_array.iloc[i, 0]
            lamb = self.results_array.iloc[i, 1]

            self.abundancetable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(elem)))
            self.abundancetable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(lamb)))

            path = Path(os.path.dirname(fname)).joinpath("On_time_Plots")
            count = 0
            while True:
                file = path.joinpath("fit_{}_{}_ang_{}.csv".format(elem, lamb, count + 1))

                if os.path.isfile(file):
                    data = pd.read_csv(file)
                    count += 1
                    lineplot = self.ax.plot(data.iloc[:, 0], data.iloc[:, 1], "--", linewidth=1.5)
                    axvlineplot = self.ax.axvline(lamb, ls="-.", c="red", linewidth=.5)
                    self.plot_line_refer.loc[len(self.plot_line_refer)] = {"elem": elem, "wave": lamb, "refer": lineplot[0]}
                    self.plot_line_refer.loc[len(self.plot_line_refer)] = {"elem": elem, "wave": lamb, "refer": axvlineplot}
                else:
                    break
            self.canvas.draw()

    def results_show_tab(self):
        currow = self.abundancetable.currentRow()

        self.lambshifvalue.setValue(self.results_array.iloc[currow, 2])
        self.continuumvalue.setValue(self.results_array.iloc[currow, 3])
        self.convolutionvalue.setValue(self.results_array.iloc[currow, 4])
        self.abundancevalue.setValue(self.results_array.iloc[currow, 6])

        self.ax.set_xlim(self.results_array.iloc[currow, 1] - self.cut_val[3],
                         self.results_array.iloc[currow, 1] + self.cut_val[3])
        self.canvas.draw()

    def full_spec_plot_range(self):
        if self.specs_data != []:
            xmin_all_old = min(self.specs_data[0].iloc[:, 0])
            xmax_all_old = max(self.specs_data[0].iloc[:, 0])
            ymin_all_old = min(self.specs_data[0].iloc[:, 1])
            ymax_all_old = max(self.specs_data[0].iloc[:, 1])
        else:
            xmin_all_old = 0
            xmax_all_old = 1
            ymin_all_old = 0
            ymax_all_old = 1

        for spec in self.specs_data:
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

        self.ax.set_xlim(xmin_all_old, xmax_all_old)
        self.ax.set_ylim(ymin_all_old, ymax_all_old*1.05)
        self.canvas.draw()

    def fitparWindow(self):
        def accept():
            self.repfit = uifitset.repfitvalue.value()
            self.cut_val = [uifitset.wavecutvalue.value()/2,
                            uifitset.convovcutvalue.value()/2,
                            uifitset.abundcutvalue.value()/2,
                            uifitset.plotcutvalue.value()/2]
            self.max_iter = [uifitset.contitervalue.value(),
                             uifitset.waveconvitervalue.value(),
                             uifitset.abunditervalue.value()]
            self.convovbound = [uifitset.convboundminvalue.value(),
                                uifitset.convboundmaxvalue.value()]
            self.continuumpars = [uifitset.contfitparalphavalue.value(),
                                  uifitset.contfitparepsvalue.value()]
            self.wavebound = uifitset.waveboundmaxshiftvalue.value()

        def check_convov():
            if uifitset.convovcutvalue.value() > uifitset.wavecutvalue.value():
                uifitset.convovcutvalue.setValue(uifitset.wavecutvalue.value())
                self.show_error("Convolution Fit Range can not be higher than Continuum/Wave. Shit range.")

        def check_contwave():
            if uifitset.convovcutvalue.value() > uifitset.wavecutvalue.value():
                uifitset.convovcutvalue.setValue(uifitset.wavecutvalue.value())

        fitparbox = QtWidgets.QDialog()
        uifitset = Ui_fitparbox()
        uifitset.setupUi(fitparbox)

        uifitset.repfitvalue.setValue(self.repfit)
        uifitset.wavecutvalue.setValue(self.cut_val[0]*2)
        uifitset.convovcutvalue.setValue(self.cut_val[1]*2)
        uifitset.abundcutvalue.setValue(self.cut_val[2]*2)
        uifitset.plotcutvalue.setValue(self.cut_val[3]*2)
        uifitset.contitervalue.setValue(self.max_iter[0])
        uifitset.waveconvitervalue.setValue(self.max_iter[1])
        uifitset.abunditervalue.setValue(self.max_iter[2])
        uifitset.convboundminvalue.setValue(self.convovbound[0])
        uifitset.convboundmaxvalue.setValue(self.convovbound[1])
        uifitset.contfitparalphavalue.setValue(self.continuumpars[0])
        uifitset.contfitparepsvalue.setValue(self.continuumpars[1])
        uifitset.waveboundmaxshiftvalue.setValue(self.wavebound)
        uifitset.okcancelbutton.accepted.connect(accept)

        uifitset.wavecutvalue.valueChanged.connect(check_contwave)
        uifitset.convovcutvalue.valueChanged.connect(check_convov)

        fitparbox.exec()

    @staticmethod
    def qtable_to_dict(qtable, checkboxes=None, tooltip=False):
        rows = qtable.rowCount()
        columns = qtable.columnCount()
        dict_table = {}
        for i in range(columns):
            current_col = []
            for j in range(rows):
                item = qtable.item(j, i)
                if item is not None:
                    if not tooltip:
                        current_col.append(item.text())
                    else:
                        current_col.append(item.data(QtCore.Qt.ItemDataRole.ToolTipRole))
                else:
                    if checkboxes is not None and i in checkboxes:
                        state = qtable.cellWidget(j, i).layout().itemAt(0).widget().checkState()
                        if state == QtCore.Qt.CheckState.Checked:
                            current_col.append(True)
                        else:
                            current_col.append(False)
                    else:
                        current_col.append(None)

            dict_table[qtable.horizontalHeaderItem(i).text()] = current_col

        return dict_table

    def dict_to_qtable(self, qtable, dict_table, checkboxes=None, tooltip=False):
        qtable.setColumnCount(len(dict_table))
        qtable.setRowCount(len(dict_table[list(dict_table.keys())[0]]))
        for i, value in enumerate(dict_table):
            qtable.horizontalHeaderItem(i).setText(value)
            for j in range(len(dict_table[value])):
                item = dict_table[value][j]
                if item is not None:
                    if checkboxes is None or i not in checkboxes:
                        if not tooltip:
                            qtable.setItem(j, i, QtWidgets.QTableWidgetItem(str(item)))
                        else:
                            self.datatableconfig(load=tooltip, loaddata=dict_table)
                    else:
                        checkbox_widget = self.tablecheckbox(item)
                        qtable.setCellWidget(j, i, checkbox_widget)

    def save_session(self, saveas=False, direc=None, flname=None, getdill=False):
        if direc is None:
            direc = os.getcwd()

        direc = str(Path(direc).joinpath("session.pkl"))

        if (self.filepath is None or saveas) and not getdill and flname is None:
            self.filepath = QtWidgets.QFileDialog.getSaveFileName(caption="File Name to save current session.",
                                                                  filter="Pickle File (*.pkl)",
                                                                  directory=direc)
            self.filepath = self.filepath[0]

            if os.path.isdir(self.filepath):
                self.filepath = "session"
            if self.filepath != "" and self.filepath[-4:] != ".pkl":
                self.filepath += ".pkl"

        list_save = [self.filepath,
                     self.linelistname.text(),
                     self.linelistcheckbox.checkState(),
                     self.restart.checkState(),
                     self.qtable_to_dict(self.linelistcontent, checkboxes=[2]),
                     self.refername.text(),
                     self.qtable_to_dict(self.refercontent),
                     self.qtable_to_dict(self.dataloadtable, tooltip=True),
                     self.specs_data,
                     self.fig,
                     self.plot_line_refer,
                     self.results_array,
                     self.outputname.text(),
                     self.progressvalue.text(),
                     self.qtable_to_dict(self.abundancetable),
                     self.methodbox.currentIndex(),
                     self.turbospectrumconfigname.text(),
                     self.turbospectrumoutputname.text(),
                     self.repfit,
                     self.cut_val,
                     self.max_iter,
                     self.convovbound,
                     self.wavebound,
                     self.continuumpars]

        if self.filepath != "" and not getdill:
            if flname is None:
                pathfinal = self.filepath
            else:
                pathfinal = flname

            with open(pathfinal, "wb") as file:
                dill.dump(list_save, file)
        elif getdill:
            return list_save
        else:
            self.filepath = None

    def load_session(self, direc=None, list_save=None, loadprev=False):
        if direc is None:
            direc = os.getcwd()

        if list_save is None and not loadprev:
            self.filepath = QtWidgets.QFileDialog.getOpenFileName(caption="File to load a session.",
                                                                  filter="Pickle File (*.pkl)",
                                                                  directory=direc)
            self.filepath = self.filepath[0]

        if self.filepath is not None and not os.path.isfile(self.filepath):
            self.filepath = None

        if self.filepath != "" and self.filepath is not None:
            if list_save is None:
                with open(self.filepath, "rb") as file:
                    list_save = dill.load(file)

            self.filepath = list_save[0]
            self.linelistname.setText(list_save[1])
            self.linelistcheckbox.setCheckState(list_save[2])
            self.restart.setCheckState(list_save[3])
            self.dict_to_qtable(self.linelistcontent, list_save[4], checkboxes=[2])
            self.refername.setText(list_save[5])
            self.dict_to_qtable(self.refercontent, list_save[6])
            self.dict_to_qtable(self.dataloadtable, list_save[7], tooltip=True)
            self.specs_data = list_save[8]
            self.fig = list_save[9]
            self.plot_line_refer = list_save[10]
            self.results_array = list_save[11]
            self.outputname.setText(list_save[12])
            self.progressvalue.setText(list_save[13])
            self.dict_to_qtable(self.abundancetable, list_save[14])
            self.methodbox.setCurrentIndex(list_save[15])
            self.turbospectrumconfigname.setText(list_save[16])
            self.turbospectrumoutputname.setText(list_save[17])
            self.repfit = list_save[18]
            self.cut_val = list_save[19]
            self.max_iter = list_save[20]
            self.convovbound = list_save[21]
            self.wavebound = list_save[22]
            self.continuumpars = list_save[23]

            self.canvas = FigureCanvasQTAgg(self.fig)
            self.ax = self.fig.axes[0]
            plot_widget = self.plot.itemAt(0).widget()
            plot_widget.deleteLater()
            self.plot.replaceWidget(plot_widget, self.canvas)

            toolbar_widget = self.plot.itemAt(1).widget()
            toolbar_widget.deleteLater()
            self.toolbar = QtWidgets.QToolBar()
            self.toolbar.addWidget(NavigationToolbar2QT(self.canvas))
            self.plot.replaceWidget(toolbar_widget, self.toolbar)

            self.checkmethod()

    def new_session(self):
        close_dialog = QtWidgets.QMessageBox()
        close_dialog.setWindowTitle("New Session")
        close_dialog.setText("Are you sure want to open a new session? All changes not saved will be lost.")
        close_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
        close_dialog.addButton(QtWidgets.QMessageBox.StandardButton.No)
        close_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        if close_dialog.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            list_save = [None,
                         "",
                         QtCore.Qt.CheckState.Unchecked,
                         QtCore.Qt.CheckState.Unchecked,
                         {"Element": ["", "", "", "", ""],
                          "Wavelength": ["", "", "", "", ""],
                          "Analyze": [False, False, False, False, False]},
                         "",
                         {"Element": ["", "", "", "", ""],
                          "Abundance": ["", "", "", "", ""]},
                         {"": [None, None, None, None, None, None, None, None, None, None],
                          "Data": ["Data 1", "Data 2", "Data 3", "Data 4", "Data 5",
                                   "Data 6", "Data 7", "Data 8", "Data 9", "Data 10"]},
                         [],
                         self.fig,
                         pd.DataFrame(columns=["elem", "wave", "refer"]),
                         pd.DataFrame(),
                         "",
                         "0/0",
                         {"Element": [],
                          "Wavelength": []},
                         1,
                         "",
                         "",
                         2,
                         [10 / 2, 3 / 2, .4 / 2, 1 / 2],
                         [1000, 1000, 10],
                         [0, 5],
                         .2,
                         [2, 8]]

            self.canvas.figure.delaxes(self.ax)
            self.ax = self.canvas.figure.add_subplot(111)
            self.ax.grid()

            self.lambshifvalue.setValue(0.0000)
            self.continuumvalue.setValue(0.0000)
            self.convolutionvalue.setValue(0.0000)
            self.abundancevalue.setValue(0.0000)

            self.methodsdatafittab.setCurrentIndex(0)

            self.load_session(list_save=list_save)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MEAFS()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
