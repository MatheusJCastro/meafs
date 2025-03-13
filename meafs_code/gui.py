#!/usr/bin/env python3
"""
| MEAFS GUI
| Matheus J. Castro

| This is the main file. Here it is included all MEAFS features and the GUI.
"""

from PyQt6 import QtWidgets, QtGui, QtCore

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from specutils.analysis import equivalent_width
from specutils import Spectrum1D
import matplotlib.pyplot as plt
import astropy.units as u
from pathlib import Path
import pandas as pd
import numpy as np
import webbrowser
import time
import dill
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# noinspection PyUnresolvedReferences
from meafs_code import __version__

try:
    from gui_qt import Ui_MEAFS
except ModuleNotFoundError:
    from .gui_qt import Ui_MEAFS

try:
    from fitsettings_qt import Ui_fitparbox
except ModuleNotFoundError:
    from .fitsettings_qt import Ui_fitparbox

try:
    from scripts import *
except ModuleNotFoundError:
    from .scripts import *

try:
    from desktop_entry import get_curr_dir
except ModuleNotFoundError:
    from .desktop_entry import get_curr_dir


def exception_hook(exctype, value, traceback):
    """
    Function to redirect the errors of the modules to the main module, so the error can be verified.
    """

    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    # sys.exit(1)


sys._excepthook = sys.excepthook
sys.excepthook = exception_hook

# Disable Jupyter Shell warning about frozen modules.
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


class Stdredirect:
    """
    Class that redirect the stdout (outputs) and the stderr (errors) to the GUI and to the terminal, if available.
    """

    def __init__(self, edit, color=None, out=None, showtab=None):
        """
        Declare the needed variables.

        :param edit: the QT Widget that will receive the messages.
        :param color: the color of the message.
        :param out: the original stdout/stderr to redirect the messages.
        :param showtab: If the tab where the message is written should be triggered as selected or not.
        """

        self.edit = edit
        self.color = color
        self.out = out
        self.showtab = showtab

    def write(self, text):
        """
        Write function that actually writes the output in the GUI and in the terminal (if present).

        :param text: the text message to be printed.
        """

        if self.showtab:
            self.showtab.setCurrentIndex(3)

        horScrollBarcur = self.edit.horizontalScrollBar().value()
        verScrollBarcur = self.edit.verticalScrollBar().value()
        verScrollBarmax = self.edit.verticalScrollBar().maximum()

        self.edit.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        if self.color:
            # text_html = text.replace("\n", "<br>")
            # self.edit.insertHtml("<span style='white-space: pre; " \
            #                      "color: {};'>{}</span>".format(self.color, text_html))
            self.edit.setTextColor(QtGui.QColor(self.color))
            self.edit.insertPlainText(text)
        else:
            self.edit.setTextColor(QtGui.QColor(self.edit.palette().text().color()))
            self.edit.insertPlainText(text)

        if verScrollBarmax - verScrollBarcur <= 10:
            self.edit.verticalScrollBar().setValue(self.edit.verticalScrollBar().maximum())
            self.edit.horizontalScrollBar().setValue(0)
        else:
            self.edit.horizontalScrollBar().setValue(horScrollBarcur)
            self.edit.verticalScrollBar().setValue(verScrollBarcur)

        if self.out:
            self.out.write(text)

    def flush(self):
        """
        Flush function from the sys.flush()
        """

        if self.out:
            self.out.flush()


class VerticalNavigationToolbar2QT(NavigationToolbar2QT):
    """
    Class to create a vertical toolbar for the plot in the matplotlib package.
    """

    # Add only intended buttons
    toolitems = [('Home', 'Reset original view', 'home', 'home'),
                 ('Back', 'Back to previous view', 'back', 'back'),
                 ('Forward', 'Forward to next view', 'forward', 'forward'),
                 (None, None, None, None),
                 ('Pan', 'Left button pans, Right button zooms\nx/y fixes axis, CTRL fixes aspect', 'move', 'pan'),
                 ('Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),
                 # ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
                 (None, None, None, None),
                 ('Save', 'Save the figure', 'filesave', 'save_figure')
                 ]

    def __init__(self, canvas, parent=None, coordinates=True):
        """
        Define the vertical property of the toolbar and calls the original toolbar from matplotlib.

        :param canvas: the canvas where the toolbar should be effective.
        :param parent: parent widget.
        :param coordinates: coordinates of the mouse pointer.
        """

        # Calls the original routine
        super().__init__(canvas, parent, coordinates)

        self.setOrientation(QtCore.Qt.Orientation.Vertical)

        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(QtCore.Qt.AlignmentFlag(
                QtCore.Qt.AlignmentFlag.AlignCenter |
                QtCore.Qt.AlignmentFlag.AlignBottom))

            self.locLabel.setSizePolicy(QtWidgets.QSizePolicy(
                # QtWidgets.QSizePolicy.Policy.Ignored,  # using Fixed instead
                QtWidgets.QSizePolicy.Policy.Fixed,
                QtWidgets.QSizePolicy.Policy.Expanding,
            ))
            self.locLabel.setFixedWidth(50)  # default: 30
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

    # config showing mouse position in toolbar
    def set_message(self, s):
        """
        Write the mouse pointer coordinates in the toolbar.

        :param s: the message to write (coordinates)
        """

        # self.message.emit(s)  # deprecated in matplotlib>=3.8
        if self.coordinates:
            if "(x, y)" in s:
                s = s.split(" = ")
                s = s[-1]
                s = s[1:-1]
                s = s.split(", ")

                # Check if the value is negative, the negative sign string used by the toolbar
                # is not recognized in the function float()
                if ord(s[0][0]) == 8722:
                    s = ["-"+s[0][1:], s[1]]
                if ord(s[1][0]) == 8722:
                    s = [s[0], "-"+s[1][1:]]

                s = "Wave\n{:.0f}\nFlux\n{:.2f}".format(float(s[0]),
                                                        float(s[1]))
            self.locLabel.setText(s)


class MEAFS(QtWidgets.QMainWindow, Ui_MEAFS):
    """
    Main class that define the properties of the GUI.
    """

    def __init__(self, parent=None):
        """
        Defines and create all variables used by the program.

        :param parent: the parent class (in this case the GUI created using the Qt Designer).
        """

        # Arguments Configuration 1
        self.args = sys.argv
        self.argument_resolve(fastcheck=True)

        # Load Gui
        super(MEAFS, self).__init__(parent)
        self.setupUi(self)
        ico_path = None
        if "linux" in sys.platform:
            ico_path = str(Path(os.path.dirname(__file__)).joinpath("images", "Meafs_Icon.png"))
        elif "win" in sys.platform and "darwin" not in sys.platform:
            ico_path = str(Path(os.path.dirname(__file__)).joinpath("images", "Meafs_Icon.ico"))
        self.setWindowIcon(QtGui.QIcon(ico_path))

        self.run.setStyleSheet("QWidget { font-weight: 750 }")
        self.stop.setStyleSheet("font-weight: 750")
        self.setStyleSheet("QLabel { font-weight: 750 }")

        # Jupyter Qt Console Configuration
        self.ipython_widget = self.make_jupyter_widget_with_kernel()
        self.layoutjupyshell.addWidget(self.ipython_widget)
        self.ipython_widget.kernel_manager.kernel.shell.push(locals())

        # Stdout and Stderr configuration
        self.stdtext.setReadOnly(True)
        self.stdtext.insertPlainText("This is MEAFS v{}.\n".format(__version__) +
                                     "Messages and errors will appear here.\n\n")
        sys.stdout = Stdredirect(self.stdtext, out=sys.stdout)
        sys.stderr = Stdredirect(self.stdtext, out=sys.stderr, color="lightcoral", showtab=self.tabplotshels)
        self.clearstdbutton.clicked.connect(self.clearstd)

        # Read Settings
        self.sett_path = Path(os.path.dirname(__file__)).joinpath("settings.csv")
        self.settings = pd.read_csv(self.sett_path,  delimiter=",", index_col=None, dtype=str)
        self.autosave.setChecked(int(self.settings[self.settings.variable == "auto_save"].value.iloc[0]))

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
        self.depthinitguessvalue.setValue(-1)

        # TurboSpectrum Configuration
        self.pathconfig = self.settings[self.settings.variable == "turbospectrum_config"].value.iloc[0]
        self.pathoutput = self.settings[self.settings.variable == "turbospectrum_output"].value.iloc[0]
        self.turbospec_config_path()

        self.turbospectrumconfigbrowse.clicked.connect(lambda: self.turbospec_config_path(init=False, tp="config"))
        self.turbospectrumoutputbrowse.clicked.connect(lambda: self.turbospec_config_path(init=False, tp="output"))

        self.turbospectrumconfigname.textChanged.connect(lambda: self.turbospec_config_path(init=False,
                                                                                            tp="config",
                                                                                            onlytext=True))
        self.turbospectrumoutputname.textChanged.connect(lambda: self.turbospec_config_path(init=False,
                                                                                            tp="output",
                                                                                            onlytext=True))

        # Plot Configuration
        self.tabplotshels.setCurrentIndex(0)
        self.tabplotshels.currentChanged.connect(self.checktabshels)

        self.fig = plt.figure(tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.figure.supxlabel("Wavelength [\u212B]")
        self.canvas.figure.supylabel("Flux")
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.grid()
        self.canvas.draw()

        # First add ToolBar
        # self.toolbar = QtWidgets.QToolBar()
        # self.toolbar.addWidget(VerticalNavigationToolbar2QT(self.canvas))
        # self.plot.addWidget(self.toolbar)
        self.plot.addWidget(VerticalNavigationToolbar2QT(self.canvas))

        # Second add the plot
        self.plot.addWidget(self.canvas)

        self.plot_line_refer = pd.DataFrame(columns=["elem", "wave", "refer"])

        # Lines Final Plot Configuration
        self.plotstab.setCurrentIndex(0)
        self.histplottab.setCurrentIndex(0)
        self.scale = None

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
        self.stop_state = False
        self.stop.clicked.connect(self.stop_func)

        # Run Manual Fit Configuration
        self.manualfitbutton.clicked.connect(self.run_fit_nopars)

        # Run Plot Current Values Configuration
        self.currentvaluesplotbutton.clicked.connect(self.run_nofit)

        # Run Save Current Abundance Configuration
        self.currentvaluessavebutton.clicked.connect(self.save_cur_abund)

        # Run Final Plots Tab Configuration
        self.linesplotsingle.clicked.connect(lambda: self.run_final_plots("lines", single=True))
        self.linesplotall.clicked.connect(lambda: self.run_final_plots("lines", single=False))
        self.boxplotcreate.clicked.connect(lambda: self.run_final_plots("box", single=False))
        self.histplotsingle.clicked.connect(lambda: self.run_final_plots("hist", single=True))
        self.hitsplotall.clicked.connect(lambda: self.run_final_plots("hist", single=False))

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

        self.new_2.setShortcut(QtGui.QKeySequence("Ctrl+N"))
        self.new_2.setShortcutVisibleInContextMenu(True)
        self.open.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        self.open.setShortcutVisibleInContextMenu(True)
        self.openabundances.setShortcut(QtGui.QKeySequence("Ctrl+Shift+O"))
        self.openabundances.setShortcutVisibleInContextMenu(True)
        self.save.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        self.save.setShortcutVisibleInContextMenu(True)
        self.saveas.setShortcut(QtGui.QKeySequence("Ctrl+Shift+S"))
        self.saveas.setShortcutVisibleInContextMenu(True)
        self.quit.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        self.quit.setShortcutVisibleInContextMenu(True)

        # Edit Submenu Configuration
        self.fitpar.triggered.connect(self.fitparWindow)
        self.repfit = 2
        self.cut_val = [10 / 2, 3 / 2, .4 / 2, 1 / 2]
        self.max_iter = [1000, 1000, 10]
        self.convovbound = [0, 5]
        self.wavebound = .2
        self.continuumpars = [2, 8]

        self.errorguireset.triggered.connect(lambda: self.gui_hold(False))

        # View Submenu Configuration
        self.fullspec.triggered.connect(self.full_spec_plot_range)
        self.checkcontinuumplot.triggered.connect(self.run_check_continuum)
        self.erasecontinuumplot.triggered.connect(self.run_erase_continuum)
        self.clearspectrumplot.triggered.connect(self.clear_spectrum_plot)
        self.clearfinalplotsscale.triggered.connect(self.clear_scale)

        self.fullspec.setShortcut(QtGui.QKeySequence("Ctrl+Shift+V"))
        self.fullspec.setShortcutVisibleInContextMenu(True)
        self.clearfinalplotsscale.setShortcut(QtGui.QKeySequence("Ctrl+C"))
        self.clearfinalplotsscale.setShortcutVisibleInContextMenu(True)

        # Help Submenu Configuration
        # noinspection PyUnresolvedReferences
        palette = QtWidgets.QApplication.instance().palette()
        curr_color = palette.color(palette.ColorRole.Window).lightness()

        rtd_icon = git_icon = Path(os.path.dirname(__file__)).joinpath("images")
        if curr_color > 128:
            rtd_icon = rtd_icon.joinpath("logo-dark-rtd.svg")
            git_icon = git_icon.joinpath("github-mark.svg")
        else:
            rtd_icon = rtd_icon.joinpath("logo-light-rtd.svg")
            git_icon = git_icon.joinpath("github-mark-white.svg")
        rtd_icon = QtGui.QIcon(str(rtd_icon))
        git_icon = QtGui.QIcon(str(git_icon))

        self.readthedocsopen.setIcon(rtd_icon)
        self.guthubopen.setIcon(git_icon)
        self.aboutopen.setIcon(QtGui.QIcon.fromTheme('help-about'))

        self.readthedocsopen.triggered.connect(lambda: webbrowser.open("https://meafs.readthedocs.io/"))
        self.guthubopen.triggered.connect(lambda: webbrowser.open("https://github.com/MatheusJCastro/meafs"))
        self.aboutopen.triggered.connect(self.show_about)

        # Auto Save Configuration
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.auto_save)
        self.timer.setInterval(5000)
        if self.autosave.isChecked():
            self.timer.start()

        self.autosave.triggered.connect(self.enable_auto_save)

        # Arguments Configuration 2
        self.argument_resolve()

    # def keyPressEvent(self, event):
    #     """
    #     Catches keyboard events to create shortcuts used.
    #
    #     Available shortcuts are:
    #         | Ctrl+S: Save the session;
    #         | Ctrl+Shift+V: Show the entire spectrum.
    #
    #     :param event: the event itself.
    #     """
    #
    #     if isinstance(event, QtGui.QKeyEvent):
    #         if event.modifiers() == (QtCore.Qt.KeyboardModifier.ControlModifier |
    #                                  QtCore.Qt.KeyboardModifier.ShiftModifier):
    #             if event.key() == QtCore.Qt.Key.Key_V:
    #                 self.full_spec_plot_range()
    #         elif event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
    #             if event.key() == QtCore.Qt.Key.Key_S:
    #                 self.save_session()

    def closeEvent(self, event):
        """
        Handles the close button event and trigger an "are you sure?" message.

        :param event: the event itself.
        """

        if self.show_quit():
            self.ipython_widget.kernel_client.stop_channels()
            self.ipython_widget.kernel_manager.shutdown_kernel()
            event.accept()
        else:
            event.ignore()

    def quitbtn(self):
        """
        Create an alias to the close button event.
        """

        if self.show_quit():
            exit("Exit button pressed.")

    def show_quit(self):
        """
        Shows the quit message "are you sure?"

        :return: true or false, depending on the clicked button.
        """

        textclose = "Are you sure want to quit MEAFS?\n"
        if self.autosave.isChecked():
            textclose += "Auto Save is ON."
        else:
            textclose += "Auto Save is OFF."

        close_dialog = QtWidgets.QMessageBox()
        close_dialog.setWindowTitle("Quit")
        close_dialog.setText(textclose)

        close_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
        close_dialog.addButton(QtWidgets.QMessageBox.StandardButton.No)
        close_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)

        if not self.autosave.isChecked():
            close_dialog.addButton(QtWidgets.QMessageBox.StandardButton.Save)
            close_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Save)

        action_close = close_dialog.exec()

        if action_close == QtWidgets.QMessageBox.StandardButton.Yes:
            if self.autosave.isChecked():
                flname = Path(os.path.dirname(__file__)).joinpath("auto_save_last.pkl")
                self.save_session(flname=flname)
            return True
        elif action_close == QtWidgets.QMessageBox.StandardButton.Save:
            return self.save_session()
        else:
            return False

    def enable_auto_save(self):
        """
        Enable or disable the timed auto-save and the close auto-save capability and write
        this setting in to the settings file.
        """

        if self.autosave.isChecked():
            self.settings.loc[self.settings.variable == "auto_save", "value"] = "1"
            self.timer.start()
        else:
            self.settings.loc[self.settings.variable == "auto_save", "value"] = "0"
            self.timer.stop()

        # noinspection PyTypeChecker
        self.settings.to_csv(self.sett_path, index=None)

    def auto_save(self):
        """
        Save the session by the *auto_save.plk* file name or the name previously chosen by the user.
        """

        if self.filepath is None:
            flname = Path(os.path.dirname(__file__)).joinpath("auto_save.pkl")
            self.save_session(flname=flname)
        else:
            self.save_session()

    def argument_resolve(self, fastcheck=False):
        """
        Resolve the arguments passed in the commandline.

        :param fastcheck: if true, only check for the help and version arguments.
        """

        if "-h" in self.args or "--help" in self.args:
            root_path = Path(os.path.dirname(__file__))
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
                       "The root folder of this MEAFS installation is: {}\n\n" \
                       "Options are:\n" \
                       " -h, --help\t\t|\tShow this help;\n" \
                       " -v, --version\t\t|\tShow version number;\n" \
                       " -l, --last\t\t|\tLoad the last closed session. Default location is:\n" \
                       "\t\t\t|\t{}\n" \
                       " -s, --load-auto-save\t|\tLoad the auto saved session. Default location is:\n" \
                       "\t\t\t|\t{}\n" \
                       "\n\nExample:\n./gui.py sesssion.pkl\n\n" \
                       "For more information go to <https://meafs.readthedocs.io/>\n".format(__version__, root_path,
                                                                                           path1, path2)
            print(help_msg)
            exit()
        elif "-v" in self.args or "--version" in self.args:
            print("MEAFS v{}".format(__version__))
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

    def clearstd(self):
        """
        Clear the QT Widget that receive the stdout and stderr messages.
        """

        self.stdtext.clear()

    @staticmethod
    def show_about():
        """
        Create a new window to show info about MEAFS.
        """

        about_dialog = QtWidgets.QDialog()
        about_dialog.setWindowTitle("About MEAFS v{}".format(__version__))

        about_widget = QtWidgets.QVBoxLayout()

        image_widget = QtWidgets.QLabel()
        text_widget = QtWidgets.QLabel()
        btt_widget = QtWidgets.QDialogButtonBox()

        img_resize = 2.5
        scale = QtCore.QSize(int(1000 / img_resize), int(325 / img_resize))
        pixmap = QtGui.QPixmap(str(Path(os.path.dirname(__file__)).joinpath("images",
                                                                            "Meafs_Logo.png"))).scaled(scale)

        about_msg = "This is MEAFS, Multiple Element Abundance Fitting Software<br>" \
                    "<br>" \
                    "<i>Version {}<br><br>".format(__version__) + \
                    "Written by: Matheus J. Castro<br>" \
                    "Under MIT License</i><br>" \
                    "<br>" \
                    "The MEAFS is a fitting tool software for spectra abundance analysis.<br>" \
                    "The aim is to provide a medium to high quality analysis for each individual " \
                    "absorption line in a given spectrum.<br>" \
                    "The software also fits the wavelength shift, continuum and convolution " \
                    "of the spectrum.<br>" \
                    "<br>" \
                    "Find more at:<br>" \
                    "<a href='https://meafs.readthedocs.io/'>Read the Docs</a><br>" \
                    "<a href='https://github.com/MatheusJCastro/meafs'>GitHub</a>"

        image_widget.setPixmap(pixmap)

        text_widget.setText(about_msg)
        text_widget.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        text_widget.setOpenExternalLinks(True)

        btt_widget.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        # noinspection PyUnresolvedReferences
        btt_widget.accepted.connect(about_dialog.accept)

        about_widget.addWidget(image_widget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        about_widget.addWidget(text_widget)
        about_widget.addWidget(btt_widget)

        about_dialog.setLayout(about_widget)
        about_dialog.exec()

    @staticmethod
    def make_jupyter_widget_with_kernel():
        """
        Create and configure the Jupyter QT Widget.

        :return: the widget itself.
        """

        # Create an in-process kernel
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel(show_banner=False)
        kernel = kernel_manager.kernel
        kernel.gui = 'qt'

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        ipython_widget = RichJupyterWidget()
        ipython_widget.kernel_manager = kernel_manager
        ipython_widget.kernel_client = kernel_client
        return ipython_widget

    @staticmethod
    def show_error(msg):
        """
        Show a QT window for some user-input-error message.

        :param msg: the message to be showed.
        """

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
        """
        Show a File Dialog to select some file.

        :param uiobject: the QT widget that shows the file path.
        :param caption: the caption in File Dialog.
        :param direc: the first directory that File Dialog should show.
        """

        if direc is None:
            direc = os.getcwd()

        fname = QtWidgets.QFileDialog.getOpenFileName(caption=caption,
                                                      filter="Text File (*.txt, *.csv, *)",
                                                      directory=direc)
        if fname[0] != "":
            uiobject.setText(fname[0])

    @staticmethod
    def browse_dir_out(uiobject, caption, direc=None):
        """
        Show a File Dialog to select some directory.

        :param uiobject: the QT widget that shows the file path.
        :param caption: the caption in File Dialog.
        :param direc: the first directory that File Dialog should show.
        """

        if direc is None:
            direc = os.getcwd()

        fname = QtWidgets.QFileDialog.getExistingDirectory(caption=caption,
                                                           directory=direc)
        if fname != "":
            if fname[-7:] != "Results":
                fname = str(Path(fname).joinpath("Results"))
            uiobject.setText(fname)

    def gui_hold(self, value):
        """
        Froozen some widgets in the GUI so they can not be modified while running the fit.

        :param value: if it is to hold or not the GUI
        """

        self.run.setDisabled(value)
        self.manualfitbutton.setDisabled(value)
        self.currentvaluesplotbutton.setDisabled(value)
        self.currentvaluessavebutton.setDisabled(value)
        self.abundancetable.setDisabled(value)

        if value:
            btt_text = "Running"
            back_col = "red"
        else:
            btt_text = "Run"
            back_col = "none"

        self.run.setText(btt_text)
        self.run.setStyleSheet("background-color: {}; font-weight: 750".format(back_col))

    def checktabshels(self):
        """
        Modify the behaviour of some UI elements to guide the user through the creation of the final plots for the
        abundances.
        """

        if self.tabplotshels.currentIndex() == 1:
            self.linelist.setEnabled(False)
            self.refer.setEnabled(False)
            self.run.setEnabled(False)
            self.methodsdatafittab.setCurrentIndex(3)
            self.methodsdatafittab.setTabEnabled(3, True)
            self.manualfitbutton.setEnabled(False)
            self.currentvaluesplotbutton.setEnabled(False)
            self.currentvaluessavebutton.setEnabled(False)
        else:
            self.linelist.setEnabled(True)
            self.refer.setEnabled(True)
            self.run.setEnabled(True)
            self.methodsdatafittab.setTabEnabled(3, False)
            self.manualfitbutton.setEnabled(True)
            self.currentvaluesplotbutton.setEnabled(True)
            self.currentvaluessavebutton.setEnabled(True)

    def tablecheckbox(self, state):
        """
        Create a QT Widget with a CheckBox inside to use it in QT tables.

        :param state: if it should be checked or not.
        :return: the QT widget containing the checkbox.
        """

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
        """
        Load a line-list file with element and wavelength in the proper QT table.
        """

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
        """
        Check or uncheck all checkboxes in the line-list table.
        """

        for i in range(self.linelistcontent.rowCount()):
            if self.linelistcheckbox.checkState() == QtCore.Qt.CheckState.Checked:
                checkbox_widget = self.tablecheckbox(True)
            else:
                checkbox_widget = self.tablecheckbox(False)

            self.linelistcontent.setCellWidget(i, 2, checkbox_widget)

        self.checkLineliststate()

    def checkLineliststate(self):
        """
        Count the number of checked checkboxes in the line-list table,
        update the progress total value accordingly and also check or
        uncheck the "Select All" element.
        """

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
        """
        Check or uncheck a unique checkbox in the line-list table.
        """

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
        """
        Load the abundance reference file containing the elements and their abundances in the QT table.
        """

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
        """
        Add new or removes lines from a QT table.

        :param uiobject: the QT table widget to change.
        :param add: true: add a line; false: remove a line.
        :param islinelist: if it is a line-list table, also calls the function to generate the checkboxes.
        """
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
        """
        Gray the tabs of the methods that are not selected.

        :param metharray: the pattern that should be grayed.
        """

        self.eqwidthtab.setEnabled(metharray[0])
        self.turbspectrumtab.setEnabled(metharray[1])
        self.pfanttab.setEnabled(metharray[2])
        self.synthetab.setEnabled(metharray[3])

        for i,j in enumerate(metharray):
            self.methodstab.setTabEnabled(i, j)

    def checkmethod(self):
        """
        Check which methods tab is selected and disable the other ones.
        """

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

    def turbospec_config_path(self, init=True, tp=None, onlytext=False):
        """
        Check, select and write into the settings the path to the configuration and output files
        of TurboSpectrum

        :param init: if it is only to look if the path in the database exists
        :param tp: type of file being called
        """

        if init:
            mainpath = Path(__file__).parts[:-1]

            if self.pathconfig is np.nan:
                self.pathconfig = Path(mainpath[0]).joinpath(*mainpath[1:]).joinpath("modules",
                                                                                     "Turbospectrum2019",
                                                                                     "COM-v19.1")
            if self.pathoutput is np.nan:
                self.pathoutput = Path(mainpath[0]).joinpath(*mainpath[1:]).joinpath("modules",
                                                                                     "Turbospectrum2019",
                                                                                     "COM-v19.1", "syntspec")
            self.turbospectrumconfigname.setText(str(self.pathconfig))
            self.turbospectrumoutputname.setText(str(self.pathoutput))

            if not os.path.exists(self.pathconfig):
                self.pathconfig = Path(mainpath[0]).joinpath(*mainpath[1:])
            if not os.path.exists(self.pathoutput):
                self.pathoutput = Path(mainpath[0]).joinpath(*mainpath[1:])

        else:
            if tp == "config":
                if not onlytext:
                    self.browse(self.turbospectrumconfigname,
                                "Select TurboSpectrum Configuration File",
                                direc=str(self.pathconfig))
                if os.path.isfile(self.turbospectrumconfigname.text()):
                    self.settings.loc[
                        self.settings.variable == "turbospectrum_config", "value"] = self.turbospectrumconfigname.text()
                try:
                    mainpath = Path(self.turbospectrumconfigname.text()).parts[:-1]
                    self.pathconfig = Path(mainpath[0]).joinpath(*mainpath[1:])
                except IndexError:
                    pass
                self.auto_set_output()
            elif tp == "output":
                if not onlytext:
                    self.browse(self.turbospectrumoutputname,
                                "Select TurboSpectrum Output File",
                                direc=str(self.pathoutput))
                if os.path.isfile(self.turbospectrumoutputname.text()):
                    self.settings.loc[
                        self.settings.variable == "turbospectrum_output", "value"] = self.turbospectrumoutputname.text()
                try:
                    mainpath = Path(self.turbospectrumoutputname.text()).parts[:-1]
                    self.pathoutput = Path(mainpath[0]).joinpath(*mainpath[1:])
                except IndexError:
                    pass

            # noinspection PyTypeChecker
            self.settings.to_csv(self.sett_path, index=None)

    def auto_set_output(self):
        """
        Try to find the synthetic spectrum output file name automatic by looking
        in the configuration file
        """
        pathfile = self.turbospectrumconfigname.text()
        if os.path.isfile(pathfile):
            with open(pathfile, 'r') as file:
                fl = file.read()
        else:
            return

        pos = fl.find("RESULTFILE")
        pos_end = pos + fl[pos:].find("\n")
        var_ini = fl[pos:pos_end]
        var_ini = var_ini.split("\'")[-2]

        while var_ini.count("$") != 0:
            pos = var_ini.find("$")
            if var_ini[pos+1] == "{":
                pos_end = pos + var_ini[pos:].find("}")
                var = var_ini[pos+2:pos_end]
            else:
                pos_end_t1 = var_ini[pos:].find("/")
                pos_end_t2 = var_ini[pos+1:].find("$")
                if pos_end_t1 <= pos_end_t2 and pos_end_t1 != -1:
                    pos_end = pos_end_t1
                elif pos_end_t2 != -1:
                    pos_end = pos_end_t2 + 1
                else:
                    pos_end = len(var_ini[pos:])
                pos_end += pos
                var = var_ini[pos+1:pos_end]

            if pos == pos_end or var == "" or var == " ":
                print("Turbospectrum config file name variable not found.")
                return

            pos_global = fl.find("set {} ".format(var))
            if pos_global == -1:
                pos_global = fl.find("set {}=".format(var))
            if pos_global == -1:
                pos_global = fl.find("foreach {} ".format(var))

                if pos_global == -1:
                    print("Turbospectrum config file name variable not found.")
                    return

                pos_end_global = pos_global + fl[pos_global:].find(")")
                var_value = fl[pos_global:pos_end_global].split(" (")[1]
                var_value = var_value.replace("\n", "").replace("\\", "")
            else:
                pos_end_global = pos_global + fl[pos_global:].find("\n")
                var_value = fl[pos_global:pos_end_global].split("=")[1]
                var_value = var_value.replace(" ", "").replace("\'", "")

            if var_ini[pos+1] == "{":
                pos_end += 1
            var_ini = var_ini.replace(var_ini[pos:pos_end], var_value, 1)

        pathfinal = self.pathconfig.joinpath(var_ini)
        self.turbospectrumoutputname.setText(str(pathfinal))
        mainpath = Path(pathfinal).parts[:-1]
        self.pathoutput = Path(mainpath[0]).joinpath(*mainpath[1:])


    def datatableconfig(self, load=False, loaddata=None):
        """
        Configure the button to show the spectrum file name and the tooltip
        to show the full path in the data QT table.

        :param load: if it is to load or to clear the spectrum data.
        :param loaddata: the data containing the file names.
        """

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

            # self.dataloadtable.item(i, 1).setText(showname)
            self.dataloadtable.item(i, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, fname)

    def datatableselect(self):
        """
        Configure the data QT table with the buttons to select spectra or clear them.
        """

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
        # self.dataloadtable.item(row, 1).setText(showname)
        self.dataloadtable.item(row, 1).setData(QtCore.Qt.ItemDataRole.ToolTipRole, fname)
        self.dataloadtable.resizeColumnToContents(1)

    def loadData(self):
        """
        Load the data present in the QT table and call the function to plot the spectra in the GUI.
        """

        specs = []
        for i in range(self.dataloadtable.rowCount()):
            data_dir = self.dataloadtable.item(i, 1).data(QtCore.Qt.ItemDataRole.ToolTipRole)
            if data_dir != "Data {}".format(i + 1):
                specs.append(data_dir)

        if self.delimitertype.currentText() == "Comma":
            sep = ","
        elif self.delimitertype.currentText() == "Tab":
            sep = r"\s+"
        else:
            self.show_error("Delimiter not selected.")
            return

        self.specs_data = []
        if len(specs) > 0:
            self.specs_data = fit.open_spec_obs(specs, delimiter=sep)

        if len(self.specs_data[0].columns) == 1:
            self.show_error("MEAFS failed to load the data. Maybe wrong separator?")
            self.specs_data = []

        if self.specs_data:  # check if the list is not empty
            self.plot_line_refer = fit.plot_spec_gui(self.specs_data, self.canvas, self.ax, self.plot_line_refer)

    def check_output_folder(self):
        """
        Check if the output folder location is written.

        :return: true if it is present, otherwise false.
        """

        if self.outputname.text() == "":
            self.show_error("Empty Output Location.")
            return False
        return True

    def run_fit(self):
        """
        Call the fit algorithm.
        """

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
        """
        Call the fit algorithm only for the abundance, without fitting the
        Wavelength Shift, Continuum and Convolution.
        """

        if self.check_output_folder():
            ind = self.abundancetable.currentRow()
            ind_col = self.abundancetable.currentColumn()

            if ind == -1:
                self.show_error("No table row selected.")
                return

            self.restart.setCheckState(QtCore.Qt.CheckState.Unchecked)

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
                                                                             repfit=self.repfit,
                                                                             only_abund_ind=ind)

            self.abundancetable.setCurrentCell(ind, ind_col)

    def run_nofit(self):
        """
        Call the fit algorithm without any fit at all, only to generate the plots
        with the selected values.
        """

        if self.check_output_folder():
            ind = self.abundancetable.currentRow()
            if ind == -1:
                self.show_error("No table row selected.")
                return

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

    def run_final_plots(self, plot_type, single=False):
        """
        Run the subroutines to create the final plots.

        :param plot_type: type of the final plot to create.
        :param single: create a final plot to a single line or for all of them.
        """

        if self.abundancetable.rowCount() == 0:
            self.show_error("Abundance Table is empty!")
            return

        ind = self.abundancetable.currentRow()
        if ind == -1 and single:
            self.show_error("No table row selected.")
            return

        if self.scale is None:
            ind = self.plotstab.currentIndex()
            if ind == 0:
                getsizefrom = self.linesplotimage
            elif ind == 1:
                getsizefrom = self.boxplotimage
            else:
                if self.histplottab.currentIndex() == 0:
                    getsizefrom = self.abundhistplotimage
                else:
                    getsizefrom = self.differhistplotimage
            self.scale = QtCore.QSize(getsizefrom.width(), getsizefrom.height())

        self.results_array, self.ax, self.plot_line_refer = fit.gui_call(self.specs_data,
                                                                         self,
                                                                         QtCore.Qt.CheckState.Checked,
                                                                         self.canvas,
                                                                         self.ax,
                                                                         cut_val=self.cut_val,
                                                                         plot_line_refer=self.plot_line_refer,
                                                                         results_array=self.results_array,
                                                                         final_plot=True,
                                                                         plot_type=plot_type,
                                                                         single=single)

    def run_check_continuum(self):
        """
        Call the Continuum algorithm and draw in the plot the results.
        """

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
                                                    self.ax, self.canvas, self.plot_line_refer,
                                                    vline=False)

        self.full_spec_plot_range()

    def run_erase_continuum(self):
        """
        Erase from the plot the continuum fit line.
        """

        ind = self.plot_line_refer[(self.plot_line_refer["elem"] == "continuum")].index
        for line in self.plot_line_refer.loc[ind, "refer"]: line.remove()
        self.plot_line_refer.drop(ind, inplace=True)
        self.plot_line_refer.reset_index(drop=True, inplace=True)

        self.canvas.draw()

    def clear_spectrum_plot(self):
        """
        Clear all plots in the Spectrum Plot tab, except the spectra themselves.
        """

        self.fig = plt.figure(tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.figure.supxlabel("Wavelength [\u212B]")
        self.canvas.figure.supylabel("Flux")
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.grid()

        plot_widget = self.plot.itemAt(1).widget()
        plot_widget.deleteLater()
        self.plot.replaceWidget(plot_widget, self.canvas)

        toolbar_widget = self.plot.itemAt(0).widget()
        toolbar_widget.deleteLater()
        self.plot.replaceWidget(toolbar_widget, VerticalNavigationToolbar2QT(self.canvas))

        self.loadData()



    def clear_scale(self, show_msg=True):
        """
        Resets the fixed scale to show images in the final plots area, allowing resizing the GUI
        into smaller sizes.

        :param show_msg: Option to pop up a message saying that the scale was cleared.
        """

        def reset_image(widget):
            sizepolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                                               QtWidgets.QSizePolicy.Policy.Preferred)

            widget.clear()
            widget.setText("No data.")
            widget.setSizePolicy(sizepolicy)
            widget.setMinimumSize(0, 0)
            widget.setMaximumSize(16777215, 16777215)

        self.scale = None

        reset_image(self.linesplotimage)
        reset_image(self.boxplotimage)
        reset_image(self.abundhistplotimage)
        reset_image(self.differhistplotimage)

        ind = self.plotstab.currentIndex()
        for i in range(3):
            self.plotstab.setCurrentIndex(i)
        self.plotstab.setCurrentIndex(ind)

        if show_msg:
            self.show_error("Scale cleared.")

    def stop_func(self):
        """
        Define if the stop button was precessed during a run.
        """

        self.stop_state = True

    def save_cur_abund(self):
        """
        Save the results of the fit in a CSV file.
        """

        self.setWindowTitle("MEAFS - Saving")

        currow = self.abundancetable.currentRow()
        currow = self.abundancetable.rowCount() - 1 if currow == -1 else currow
        elem = self.abundancetable.item(currow, 0).text()
        lamb = self.abundancetable.item(currow, 1).text()
        abund = self.abundancevalue.value()

        ind = self.results_array[(self.results_array["Element"] == elem) &
                                 (self.results_array["Lambda (A)"] == float(lamb))].index
        for i in ind:
            file = Path(self.outputname.text()).joinpath("On_time_Plots",
                                                  "fit_{}_{}_ang_{}.csv".format(elem, lamb, 1))

            if os.path.isfile(file):
                spec_fit = pd.read_csv(file)
                # Fit of Equivalent Width Fitted Spectrum
                # noinspection PyUnresolvedReferences
                spec1d = Spectrum1D(spectral_axis=np.asarray(spec_fit.iloc[:, 0]) * u.AA,
                                    flux=np.asarray(spec_fit.iloc[:, 1]) * u.Jy)
                equiv_width_fit = equivalent_width(spec1d)
                # noinspection PyUnresolvedReferences
                equiv_width_fit = np.float16(equiv_width_fit / u.AA)

                self.results_array.loc[i, "Equiv Width Fit (A)"] = equiv_width_fit

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

        time.sleep(0.2)
        self.setWindowTitle("MEAFS")

    def open_prev_results(self):
        """
        Open CSV files with previous runs and load the results, including
        the available plots (if any).
        """

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
        """
        Show the results of the selected line in the results table in the results
        tab and focus the plot in the current line.
        """

        currow = self.abundancetable.currentRow()

        elem = self.abundancetable.item(currow, 0).text()
        lamb = self.abundancetable.item(currow, 1).text()
        self.linedefvalue.setText("Element {}, line {}".format(elem, lamb))

        self.lambshifvalue.setValue(self.results_array.iloc[currow, 2])
        self.continuumvalue.setValue(self.results_array.iloc[currow, 3])
        self.convolutionvalue.setValue(self.results_array.iloc[currow, 4])
        self.abundancevalue.setValue(self.results_array.iloc[currow, 6])

        if self.tabplotshels.currentIndex() == 0:
            self.ax.set_xlim(self.results_array.iloc[currow, 1] - self.cut_val[3],
                             self.results_array.iloc[currow, 1] + self.cut_val[3])
            self.canvas.draw()
        elif self.tabplotshels.currentIndex() == 1:
            folder = self.outputname.text()

            if self.plotstab.currentIndex() == 0:
                main_path = Path(folder).joinpath("Abundance_Analysis", "Lines_Plot")
                fig_path = main_path.joinpath("fit_{}_{}_ang.pdf".format(elem, lamb))

                if fig_path.is_file():
                    if self.scale is None:
                        self.scale = QtCore.QSize(self.linesplotimage.width(),
                                                  self.linesplotimage.height())

                    pixmap = QtGui.QPixmap(str(fig_path))
                    self.linesplotimage.setPixmap(pixmap.scaled(self.scale))
                    self.linesplotimage.setFixedSize(self.scale)
                else:
                    self.clear_scale(show_msg=False)
            elif self.plotstab.currentIndex() == 2:
                if self.histplottab.currentIndex() == 0:
                    main_path = Path(folder).joinpath("Abundance_Analysis", "Abundance_Hist")
                    elem, order = fit.check_order(elem)
                    fig_path = main_path.joinpath("hist_abundance_{}.pdf".format(elem))

                    if fig_path.is_file():
                        if self.scale is None:
                            self.scale = QtCore.QSize(self.abundhistplotimage.width(),
                                                      self.abundhistplotimage.height())

                        pixmap = QtGui.QPixmap(str(fig_path))
                        self.abundhistplotimage.setPixmap(pixmap.scaled(self.scale))
                        self.abundhistplotimage.setFixedSize(self.scale)
                    else:
                        self.clear_scale(show_msg=False)
                elif self.histplottab.currentIndex() == 1:
                    main_path = Path(folder).joinpath("Abundance_Analysis", "Difference_Hist")
                    elem, order = fit.check_order(elem)
                    fig_path = main_path.joinpath("hist_differ_{}.pdf".format(elem))

                    if fig_path.is_file():
                        if self.scale is None:
                            self.scale = QtCore.QSize(self.differhistplotimage.width(),
                                                      self.differhistplotimage.height())

                        pixmap = QtGui.QPixmap(str(fig_path))
                        self.differhistplotimage.setPixmap(pixmap.scaled(self.scale))
                        self.differhistplotimage.setFixedSize(self.scale)
                    else:
                        self.clear_scale(show_msg=False)

    def full_spec_plot_range(self):
        """
        Find the total maximum and minimum values of the current plot and
        change the range to it.
        """

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
        """
        Call and get the values of the *Fit Parameters* window.
        """

        def accept():
            """Write the values from the window in the main variables"""

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

        def check_convov(showerror=False):
            """Check if the convolution respect the limits"""
            if uifitset.convovcutvalue.value() > uifitset.wavecutvalue.value():
                uifitset.convovcutvalue.setValue(uifitset.wavecutvalue.value())
                if showerror:
                    self.show_error("Convolution Fit Range can not be higher than Continuum/Wave. Shit range.")

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

        uifitset.wavecutvalue.valueChanged.connect(lambda: check_convov(showerror=False))
        uifitset.convovcutvalue.valueChanged.connect(lambda: check_convov(showerror=True))

        fitparbox.exec()

    @staticmethod
    def qtable_to_dict(qtable, checkboxes=None, tooltip=False):
        """
        Transform a QT Table in a dictionary.

        :param qtable: the QT Table to be read.
        :param checkboxes: the index of checkboxes, if exists.
        :param tooltip: get the item or the tooltip (for spectrum data table)
        :return: the dictionary
        """

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
        """
        Transform a QT Table in a dictionary.

        :param qtable: the QT Table to be written.
        :param dict_table: the dictionary to read the data.
        :param checkboxes: the index of checkboxes, if exists.
        :param tooltip: write the item or the tooltip (for spectrum data table)
        """

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
        """
        Save a session using dill.

        :param saveas: if true, ignore the `self.filepath` variable.
        :param direc: the directory where the File Dialog should first open.
        :param flname: file name to save the session. If present, the File Dialog will not be shown.
        :param getdill: if true, does not save the session and
                        return the list to be saved.
        :return: the list to be saved (if ``getdill`` is true), true if the session is saved or
                 false if the `self.filepath` was not properly filled.
        """

        if (self.filepath is None or saveas) and not getdill and flname is None:
            if direc is None:
                direc = os.getcwd()

            direc = str(Path(direc).joinpath("session.pkl"))

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
                     self.delimitertype.currentIndex(),
                     self.specs_data,
                     self.fig,
                     self.plot_line_refer,
                     self.results_array,
                     self.outputname.text(),
                     self.progressvalue.text(),
                     self.qtable_to_dict(self.abundancetable),
                     self.methodbox.currentIndex(),
                     self.ewfuncbox.currentIndex(),
                     self.convinitguessvalue.value(),
                     self.depthinitguessvalue.value(),
                     self.turbospectrumconfigname.text(),
                     self.turbospectrumoutputname.text(),
                     self.repfit,
                     self.cut_val,
                     self.max_iter,
                     self.convovbound,
                     self.wavebound,
                     self.continuumpars,
                     self.tabplotshels.currentIndex(),
                     self.stdtext.toHtml(),
                     self.plotstab.currentIndex(),
                     self.abundshift.value(),
                     self.histbinsvalue.value()]

        if getdill:
            return list_save
        elif self.filepath != "":
            if flname is None:
                pathfinal = self.filepath
            else:
                pathfinal = flname

            with open(pathfinal, "wb") as file:
                self.setWindowTitle("MEAFS - Saving")
                dill.dump(list_save, file)
                time.sleep(0.2)
                self.setWindowTitle("MEAFS")
            return True
        else:
            self.filepath = None
            return False

    def load_session(self, direc=None, list_save=None, loadprev=False):
        """
        Load a previously saved session, or a list with all session-variables.

        :param direc: the directory where the File Dialog should first open.
        :param list_save: a list with all session-variable. If it is different from None,
                          the prompt to choose a file will not be shown.
        :param loadprev: if true, the path of the file needs to be written in the
                         ``self.filepath`` variable.
        """

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
            self.delimitertype.setCurrentIndex(list_save[8])
            self.specs_data = list_save[9]
            self.fig = list_save[10]
            self.plot_line_refer = list_save[11]
            self.results_array = list_save[12]
            self.outputname.setText(list_save[13])
            self.progressvalue.setText(list_save[14])
            self.dict_to_qtable(self.abundancetable, list_save[15])
            self.methodbox.setCurrentIndex(list_save[16])
            self.ewfuncbox.setCurrentIndex(list_save[17]),
            self.convinitguessvalue.setValue(list_save[18]),
            self.depthinitguessvalue.setValue(list_save[19]),
            self.turbospectrumconfigname.setText(list_save[20])
            self.turbospectrumoutputname.setText(list_save[21])
            self.repfit = list_save[22]
            self.cut_val = list_save[23]
            self.max_iter = list_save[24]
            self.convovbound = list_save[25]
            self.wavebound = list_save[26]
            self.continuumpars = list_save[27]
            self.tabplotshels.setCurrentIndex(list_save[28])
            self.stdtext.clear()
            self.stdtext.insertHtml(list_save[29])
            self.plotstab.setCurrentIndex(list_save[30])
            self.abundshift.setValue(list_save[31])
            self.histbinsvalue.setValue(list_save[32])

            self.canvas = FigureCanvasQTAgg(self.fig)
            self.ax = self.fig.axes[0]
            plot_widget = self.plot.itemAt(1).widget()
            plot_widget.deleteLater()
            self.plot.replaceWidget(plot_widget, self.canvas)

            toolbar_widget = self.plot.itemAt(0).widget()
            toolbar_widget.deleteLater()
            # self.toolbar = QtWidgets.QToolBar()
            # self.toolbar.addWidget(NavigationToolbar2QT(self.canvas))
            # self.plot.replaceWidget(toolbar_widget, self.toolbar)
            self.plot.replaceWidget(toolbar_widget, VerticalNavigationToolbar2QT(self.canvas))

            self.checkmethod()
            self.checktabshels()

    def new_session(self):
        """
        Load a new empty session by overriding all variable to the default values.
        """

        close_dialog = QtWidgets.QMessageBox()
        close_dialog.setWindowTitle("New Session")
        close_dialog.setText("Are you sure want to open a new session? All changes not saved will be lost.")
        close_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
        close_dialog.addButton(QtWidgets.QMessageBox.StandardButton.No)
        close_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)

        if close_dialog.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            self.fig = plt.figure(tight_layout=True)
            self.canvas = FigureCanvasQTAgg(self.fig)
            self.canvas.figure.supxlabel("Wavelength [\u212B]")
            self.canvas.figure.supylabel("Flux")
            self.ax = self.canvas.figure.add_subplot(111)
            self.ax.grid()
            self.canvas.draw()

            list_save = [
                         # filepath
                         None,
                         # linelistname
                         "",
                         # linelistcheckbox
                         QtCore.Qt.CheckState.Unchecked,
                         # restart
                         QtCore.Qt.CheckState.Unchecked,
                         # linelistcontent
                         {"Element": ["", "", "", "", ""],
                          "Wavelength": ["", "", "", "", ""],
                          "Analyze": [False, False, False, False, False]},
                         # refername
                         "",
                         # refercontent
                         {"Element": ["", "", "", "", ""],
                          "Abundance": ["", "", "", "", ""]},
                         # dataloadtable
                         {"": [None, None, None, None, None, None, None, None, None, None],
                          "Data": ["Data 1", "Data 2", "Data 3", "Data 4", "Data 5",
                                   "Data 6", "Data 7", "Data 8", "Data 9", "Data 10"]},
                         # delimitertype
                         0,
                         # specs_data
                         [],
                         # fig
                         self.fig,
                         # plot_line_refer
                         pd.DataFrame(columns=["elem", "wave", "refer"]),
                         # results_array
                         pd.DataFrame(),
                         # outputname
                         "",
                         # progressvalue
                         "0/0",
                         # abundancetable
                         {"Element": [],
                          "Wavelength": []},
                         # methodbox
                         1,
                         # ewfuncbox
                         0,
                         # convinitguessvalue
                         0.001,
                         # depthinitguessvalue
                         -1,
                         # turbospectrumconfigname
                         "",
                         # turbospectrumoutputname
                         "",
                         # repfit
                         2,
                         # cut_val
                         [10 / 2, 3 / 2, .4 / 2, 1 / 2],
                         # max_iter
                         [1000, 1000, 10],
                         # convovbound
                         [0, 5],
                         # wavebound
                         .2,
                         # continuumpars
                         [2, 8],
                         # tabplotshels
                         0,
                         # stdtext
                         "",
                         # plotstab
                         0,
                         # abundshift
                         0.1,
                         # histbinsvalue
                         20
                         ]

            self.lambshifvalue.setValue(0.0000)
            self.continuumvalue.setValue(0.0000)
            self.convolutionvalue.setValue(0.0000)
            self.abundancevalue.setValue(0.0000)

            self.methodsdatafittab.setCurrentIndex(0)
            self.tabplotshels.setCurrentIndex(0)
            self.plotstab.setCurrentIndex(0)

            self.load_session(list_save=list_save)


def main():
    """
    Main function to run the GUI.
    """

    app = QtWidgets.QApplication(sys.argv)
    win = MEAFS()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
