# Form implementation generated from reading ui file 'meafs.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MEAFS(object):
    def setupUi(self, MEAFS):
        MEAFS.setObjectName("MEAFS")
        MEAFS.resize(1203, 781)
        self.centralwidget = QtWidgets.QWidget(parent=MEAFS)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.linelist = QtWidgets.QGridLayout()
        self.linelist.setObjectName("linelist")
        self.linelistlabel = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.linelistlabel.setFont(font)
        self.linelistlabel.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.linelistlabel.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.linelistlabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.linelistlabel.setScaledContents(False)
        self.linelistlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.linelistlabel.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.NoTextInteraction)
        self.linelistlabel.setObjectName("linelistlabel")
        self.linelist.addWidget(self.linelistlabel, 0, 0, 1, 5)
        self.linelistload = QtWidgets.QPushButton(parent=self.centralwidget)
        self.linelistload.setObjectName("linelistload")
        self.linelist.addWidget(self.linelistload, 1, 4, 1, 1)
        self.linelistname = QtWidgets.QLineEdit(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.linelistname.sizePolicy().hasHeightForWidth())
        self.linelistname.setSizePolicy(sizePolicy)
        self.linelistname.setObjectName("linelistname")
        self.linelist.addWidget(self.linelistname, 1, 1, 1, 1)
        self.linelistcontent = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.linelistcontent.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.linelistcontent.setObjectName("linelistcontent")
        self.linelistcontent.setColumnCount(3)
        self.linelistcontent.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.linelistcontent.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.linelistcontent.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.linelistcontent.setHorizontalHeaderItem(2, item)
        self.linelistcontent.horizontalHeader().setStretchLastSection(True)
        self.linelist.addWidget(self.linelistcontent, 3, 0, 1, 4)
        self.linelistbrowse = QtWidgets.QPushButton(parent=self.centralwidget)
        self.linelistbrowse.setObjectName("linelistbrowse")
        self.linelist.addWidget(self.linelistbrowse, 1, 2, 1, 1)
        self.linelistlabel2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.linelistlabel2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.linelistlabel2.sizePolicy().hasHeightForWidth())
        self.linelistlabel2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.linelistlabel2.setFont(font)
        self.linelistlabel2.setObjectName("linelistlabel2")
        self.linelist.addWidget(self.linelistlabel2, 1, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.linelistcheckbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.linelistcheckbox.setEnabled(False)
        self.linelistcheckbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.linelistcheckbox.setObjectName("linelistcheckbox")
        self.verticalLayout.addWidget(self.linelistcheckbox)
        self.linelistaddline = QtWidgets.QPushButton(parent=self.centralwidget)
        self.linelistaddline.setObjectName("linelistaddline")
        self.verticalLayout.addWidget(self.linelistaddline)
        self.linelistremoveline = QtWidgets.QPushButton(parent=self.centralwidget)
        self.linelistremoveline.setObjectName("linelistremoveline")
        self.verticalLayout.addWidget(self.linelistremoveline)
        self.linelist.addLayout(self.verticalLayout, 3, 4, 1, 1)
        self.gridLayout.addLayout(self.linelist, 3, 4, 1, 1)
        self.refer = QtWidgets.QGridLayout()
        self.refer.setObjectName("refer")
        self.refername = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.refername.setObjectName("refername")
        self.refer.addWidget(self.refername, 1, 1, 1, 1)
        self.referlabel = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.referlabel.setFont(font)
        self.referlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.referlabel.setObjectName("referlabel")
        self.refer.addWidget(self.referlabel, 0, 0, 1, 4)
        self.referlabel2 = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.referlabel2.setFont(font)
        self.referlabel2.setObjectName("referlabel2")
        self.refer.addWidget(self.referlabel2, 1, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.referaddline = QtWidgets.QPushButton(parent=self.centralwidget)
        self.referaddline.setObjectName("referaddline")
        self.verticalLayout_3.addWidget(self.referaddline)
        self.referremoveline = QtWidgets.QPushButton(parent=self.centralwidget)
        self.referremoveline.setObjectName("referremoveline")
        self.verticalLayout_3.addWidget(self.referremoveline)
        self.refer.addLayout(self.verticalLayout_3, 2, 3, 1, 1)
        self.referbrowse = QtWidgets.QPushButton(parent=self.centralwidget)
        self.referbrowse.setObjectName("referbrowse")
        self.refer.addWidget(self.referbrowse, 1, 2, 1, 1)
        self.referload = QtWidgets.QPushButton(parent=self.centralwidget)
        self.referload.setObjectName("referload")
        self.refer.addWidget(self.referload, 1, 3, 1, 1)
        self.refercontent = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.refercontent.setObjectName("refercontent")
        self.refercontent.setColumnCount(2)
        self.refercontent.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.refercontent.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.refercontent.setHorizontalHeaderItem(1, item)
        self.refercontent.horizontalHeader().setVisible(True)
        self.refercontent.horizontalHeader().setCascadingSectionResizes(False)
        self.refercontent.horizontalHeader().setSortIndicatorShown(False)
        self.refercontent.horizontalHeader().setStretchLastSection(True)
        self.refer.addWidget(self.refercontent, 2, 0, 1, 3)
        self.gridLayout.addLayout(self.refer, 5, 4, 1, 1)
        self.outputabundances = QtWidgets.QGridLayout()
        self.outputabundances.setObjectName("outputabundances")
        self.outputbrowse = QtWidgets.QPushButton(parent=self.centralwidget)
        self.outputbrowse.setObjectName("outputbrowse")
        self.outputabundances.addWidget(self.outputbrowse, 3, 4, 1, 1)
        self.outputname = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.outputname.setObjectName("outputname")
        self.outputabundances.addWidget(self.outputname, 3, 3, 1, 1)
        self.abundanceslabel = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.abundanceslabel.setFont(font)
        self.abundanceslabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.abundanceslabel.setObjectName("abundanceslabel")
        self.outputabundances.addWidget(self.abundanceslabel, 5, 1, 1, 4)
        self.abundancetable = QtWidgets.QTableWidget(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abundancetable.sizePolicy().hasHeightForWidth())
        self.abundancetable.setSizePolicy(sizePolicy)
        self.abundancetable.setObjectName("abundancetable")
        self.abundancetable.setColumnCount(2)
        self.abundancetable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.abundancetable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.abundancetable.setHorizontalHeaderItem(1, item)
        self.abundancetable.horizontalHeader().setStretchLastSection(True)
        self.outputabundances.addWidget(self.abundancetable, 6, 0, 1, 5)
        self.stop = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.stop.setFont(font)
        self.stop.setObjectName("stop")
        self.outputabundances.addWidget(self.stop, 4, 4, 1, 1)
        self.progresslabel = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progresslabel.sizePolicy().hasHeightForWidth())
        self.progresslabel.setSizePolicy(sizePolicy)
        self.progresslabel.setObjectName("progresslabel")
        self.outputabundances.addWidget(self.progresslabel, 4, 1, 1, 1)
        self.run = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.run.setFont(font)
        self.run.setObjectName("run")
        self.outputabundances.addWidget(self.run, 4, 3, 1, 1)
        self.progressvalue = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressvalue.sizePolicy().hasHeightForWidth())
        self.progressvalue.setSizePolicy(sizePolicy)
        self.progressvalue.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.progressvalue.setObjectName("progressvalue")
        self.outputabundances.addWidget(self.progressvalue, 4, 2, 1, 1)
        self.outputlabel = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputlabel.sizePolicy().hasHeightForWidth())
        self.outputlabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.outputlabel.setFont(font)
        self.outputlabel.setObjectName("outputlabel")
        self.outputabundances.addWidget(self.outputlabel, 3, 1, 1, 2)
        self.gridLayout.addLayout(self.outputabundances, 5, 1, 1, 1)
        self.results = QtWidgets.QGridLayout()
        self.results.setObjectName("results")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.results.addWidget(self.label, 0, 0, 1, 1)
        self.plot = QtWidgets.QGridLayout()
        self.plot.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.plot.setObjectName("plot")
        self.results.addLayout(self.plot, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.results, 3, 1, 2, 3)
        self.methodsdatafittab = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.methodsdatafittab.setObjectName("methodsdatafittab")
        self.datatab = QtWidgets.QWidget()
        self.datatab.setObjectName("datatab")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.datatab)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.gridLayout_10 = QtWidgets.QGridLayout()
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.dataloadtable = QtWidgets.QTableWidget(parent=self.datatab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataloadtable.sizePolicy().hasHeightForWidth())
        self.dataloadtable.setSizePolicy(sizePolicy)
        self.dataloadtable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.dataloadtable.setObjectName("dataloadtable")
        self.dataloadtable.setColumnCount(2)
        self.dataloadtable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.dataloadtable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.dataloadtable.setHorizontalHeaderItem(1, item)
        self.dataloadtable.horizontalHeader().setStretchLastSection(True)
        self.dataloadtable.verticalHeader().setVisible(False)
        self.gridLayout_10.addWidget(self.dataloadtable, 0, 0, 1, 2)
        self.delimitertype = QtWidgets.QComboBox(parent=self.datatab)
        self.delimitertype.setObjectName("delimitertype")
        self.delimitertype.addItem("")
        self.delimitertype.addItem("")
        self.delimitertype.addItem("")
        self.gridLayout_10.addWidget(self.delimitertype, 1, 0, 1, 1)
        self.loaddata = QtWidgets.QPushButton(parent=self.datatab)
        self.loaddata.setObjectName("loaddata")
        self.gridLayout_10.addWidget(self.loaddata, 1, 1, 1, 1)
        self.gridLayout_11.addLayout(self.gridLayout_10, 0, 0, 1, 1)
        self.methodsdatafittab.addTab(self.datatab, "")
        self.majormethodstab = QtWidgets.QWidget()
        self.majormethodstab.setObjectName("majormethodstab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.majormethodstab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.methods = QtWidgets.QVBoxLayout()
        self.methods.setObjectName("methods")
        self.methodconfiglabel = QtWidgets.QLabel(parent=self.majormethodstab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.methodconfiglabel.sizePolicy().hasHeightForWidth())
        self.methodconfiglabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.methodconfiglabel.setFont(font)
        self.methodconfiglabel.setAutoFillBackground(False)
        self.methodconfiglabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.methodconfiglabel.setObjectName("methodconfiglabel")
        self.methods.addWidget(self.methodconfiglabel)
        self.methodbox = QtWidgets.QComboBox(parent=self.majormethodstab)
        self.methodbox.setObjectName("methodbox")
        self.methodbox.addItem("")
        self.methodbox.addItem("")
        self.methodbox.addItem("")
        self.methodbox.addItem("")
        self.methods.addWidget(self.methodbox)
        self.methodstab = QtWidgets.QTabWidget(parent=self.majormethodstab)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.methodstab.setFont(font)
        self.methodstab.setAccessibleName("")
        self.methodstab.setObjectName("methodstab")
        self.eqwidthtab = QtWidgets.QWidget()
        self.eqwidthtab.setObjectName("eqwidthtab")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.eqwidthtab)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_2 = QtWidgets.QLabel(parent=self.eqwidthtab)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_8.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_8, 0, 0, 1, 1)
        self.methodstab.addTab(self.eqwidthtab, "")
        self.turbspectrumtab = QtWidgets.QWidget()
        self.turbspectrumtab.setObjectName("turbspectrumtab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.turbspectrumtab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.turbospectrumconfigname = QtWidgets.QLineEdit(parent=self.turbspectrumtab)
        self.turbospectrumconfigname.setObjectName("turbospectrumconfigname")
        self.gridLayout_2.addWidget(self.turbospectrumconfigname, 1, 0, 1, 1)
        self.turbospectrumoutputname = QtWidgets.QLineEdit(parent=self.turbspectrumtab)
        self.turbospectrumoutputname.setObjectName("turbospectrumoutputname")
        self.gridLayout_2.addWidget(self.turbospectrumoutputname, 3, 0, 1, 1)
        self.turbospectrumconfigbrowse = QtWidgets.QPushButton(parent=self.turbspectrumtab)
        self.turbospectrumconfigbrowse.setObjectName("turbospectrumconfigbrowse")
        self.gridLayout_2.addWidget(self.turbospectrumconfigbrowse, 1, 1, 1, 1)
        self.turbospectrumoutputbrowse = QtWidgets.QPushButton(parent=self.turbspectrumtab)
        self.turbospectrumoutputbrowse.setObjectName("turbospectrumoutputbrowse")
        self.gridLayout_2.addWidget(self.turbospectrumoutputbrowse, 3, 1, 1, 1)
        self.turbospectrumoutputlabel = QtWidgets.QLabel(parent=self.turbspectrumtab)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.turbospectrumoutputlabel.setFont(font)
        self.turbospectrumoutputlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.turbospectrumoutputlabel.setObjectName("turbospectrumoutputlabel")
        self.gridLayout_2.addWidget(self.turbospectrumoutputlabel, 2, 0, 1, 2)
        self.turbospectrumconfiglabel = QtWidgets.QLabel(parent=self.turbspectrumtab)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.turbospectrumconfiglabel.setFont(font)
        self.turbospectrumconfiglabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.turbospectrumconfiglabel.setObjectName("turbospectrumconfiglabel")
        self.gridLayout_2.addWidget(self.turbospectrumconfiglabel, 0, 0, 1, 2)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.methodstab.addTab(self.turbspectrumtab, "")
        self.pfanttab = QtWidgets.QWidget()
        self.pfanttab.setObjectName("pfanttab")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.pfanttab)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_3 = QtWidgets.QLabel(parent=self.pfanttab)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_6.addWidget(self.label_3, 0, 0, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.methodstab.addTab(self.pfanttab, "")
        self.synthetab = QtWidgets.QWidget()
        self.synthetab.setObjectName("synthetab")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.synthetab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_4 = QtWidgets.QLabel(parent=self.synthetab)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_4, 0, 0, 1, 1)
        self.methodstab.addTab(self.synthetab, "")
        self.methods.addWidget(self.methodstab)
        self.horizontalLayout_2.addLayout(self.methods)
        self.methodsdatafittab.addTab(self.majormethodstab, "")
        self.fitparameterstab = QtWidgets.QWidget()
        self.fitparameterstab.setObjectName("fitparameterstab")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.fitparameterstab)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.fitparameters = QtWidgets.QGridLayout()
        self.fitparameters.setObjectName("fitparameters")
        self.linedeflabel = QtWidgets.QLabel(parent=self.fitparameterstab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.linedeflabel.sizePolicy().hasHeightForWidth())
        self.linedeflabel.setSizePolicy(sizePolicy)
        self.linedeflabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.linedeflabel.setObjectName("linedeflabel")
        self.fitparameters.addWidget(self.linedeflabel, 0, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(parent=self.fitparameterstab)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.fitparameters.addWidget(self.line_2, 1, 0, 1, 3)
        self.continuumlabel = QtWidgets.QLabel(parent=self.fitparameterstab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.continuumlabel.sizePolicy().hasHeightForWidth())
        self.continuumlabel.setSizePolicy(sizePolicy)
        self.continuumlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.continuumlabel.setObjectName("continuumlabel")
        self.fitparameters.addWidget(self.continuumlabel, 3, 0, 1, 1)
        self.abundancevalue = QtWidgets.QDoubleSpinBox(parent=self.fitparameterstab)
        self.abundancevalue.setDecimals(4)
        self.abundancevalue.setMinimum(-1000.0)
        self.abundancevalue.setMaximum(1000.0)
        self.abundancevalue.setSingleStep(0.01)
        self.abundancevalue.setObjectName("abundancevalue")
        self.fitparameters.addWidget(self.abundancevalue, 6, 2, 1, 1)
        self.linedefvalue = QtWidgets.QLabel(parent=self.fitparameterstab)
        self.linedefvalue.setText("")
        self.linedefvalue.setObjectName("linedefvalue")
        self.fitparameters.addWidget(self.linedefvalue, 0, 2, 1, 1)
        self.lambshifvalue = QtWidgets.QDoubleSpinBox(parent=self.fitparameterstab)
        self.lambshifvalue.setDecimals(4)
        self.lambshifvalue.setMinimum(-1000.0)
        self.lambshifvalue.setMaximum(1000.0)
        self.lambshifvalue.setSingleStep(0.001)
        self.lambshifvalue.setObjectName("lambshifvalue")
        self.fitparameters.addWidget(self.lambshifvalue, 2, 2, 1, 1)
        self.line = QtWidgets.QFrame(parent=self.fitparameterstab)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.fitparameters.addWidget(self.line, 2, 1, 3, 1)
        self.convolutionvalue = QtWidgets.QDoubleSpinBox(parent=self.fitparameterstab)
        self.convolutionvalue.setDecimals(4)
        self.convolutionvalue.setMinimum(-1000.0)
        self.convolutionvalue.setMaximum(1000.0)
        self.convolutionvalue.setSingleStep(0.001)
        self.convolutionvalue.setObjectName("convolutionvalue")
        self.fitparameters.addWidget(self.convolutionvalue, 4, 2, 1, 1)
        self.continuumvalue = QtWidgets.QDoubleSpinBox(parent=self.fitparameterstab)
        self.continuumvalue.setDecimals(4)
        self.continuumvalue.setMinimum(-1000.0)
        self.continuumvalue.setMaximum(1000.0)
        self.continuumvalue.setSingleStep(0.001)
        self.continuumvalue.setObjectName("continuumvalue")
        self.fitparameters.addWidget(self.continuumvalue, 3, 2, 1, 1)
        self.line_4 = QtWidgets.QFrame(parent=self.fitparameterstab)
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.fitparameters.addWidget(self.line_4, 0, 1, 1, 1)
        self.manualfitbutton = QtWidgets.QPushButton(parent=self.fitparameterstab)
        self.manualfitbutton.setObjectName("manualfitbutton")
        self.fitparameters.addWidget(self.manualfitbutton, 5, 0, 1, 3)
        self.lambshiflabel = QtWidgets.QLabel(parent=self.fitparameterstab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lambshiflabel.sizePolicy().hasHeightForWidth())
        self.lambshiflabel.setSizePolicy(sizePolicy)
        self.lambshiflabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lambshiflabel.setObjectName("lambshiflabel")
        self.fitparameters.addWidget(self.lambshiflabel, 2, 0, 1, 1)
        self.convolutionlabel = QtWidgets.QLabel(parent=self.fitparameterstab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.convolutionlabel.sizePolicy().hasHeightForWidth())
        self.convolutionlabel.setSizePolicy(sizePolicy)
        self.convolutionlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.convolutionlabel.setObjectName("convolutionlabel")
        self.fitparameters.addWidget(self.convolutionlabel, 4, 0, 1, 1)
        self.abundancelabel = QtWidgets.QLabel(parent=self.fitparameterstab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abundancelabel.sizePolicy().hasHeightForWidth())
        self.abundancelabel.setSizePolicy(sizePolicy)
        self.abundancelabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.abundancelabel.setObjectName("abundancelabel")
        self.fitparameters.addWidget(self.abundancelabel, 6, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(parent=self.fitparameterstab)
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.fitparameters.addWidget(self.line_3, 6, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.currentvaluesplotbutton = QtWidgets.QPushButton(parent=self.fitparameterstab)
        self.currentvaluesplotbutton.setObjectName("currentvaluesplotbutton")
        self.horizontalLayout.addWidget(self.currentvaluesplotbutton)
        self.currentvaluessavebutton = QtWidgets.QPushButton(parent=self.fitparameterstab)
        self.currentvaluessavebutton.setObjectName("currentvaluessavebutton")
        self.horizontalLayout.addWidget(self.currentvaluessavebutton)
        self.fitparameters.addLayout(self.horizontalLayout, 7, 0, 1, 3)
        self.gridLayout_13.addLayout(self.fitparameters, 0, 0, 1, 1)
        self.methodsdatafittab.addTab(self.fitparameterstab, "")
        self.gridLayout.addWidget(self.methodsdatafittab, 5, 2, 1, 1)
        MEAFS.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MEAFS)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1203, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(parent=self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuEdit = QtWidgets.QMenu(parent=self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MEAFS.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MEAFS)
        self.statusbar.setObjectName("statusbar")
        MEAFS.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(parent=MEAFS)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtGui.QAction(parent=MEAFS)
        self.actionSave.setObjectName("actionSave")
        self.open = QtGui.QAction(parent=MEAFS)
        self.open.setObjectName("open")
        self.save = QtGui.QAction(parent=MEAFS)
        self.save.setObjectName("save")
        self.openabundances = QtGui.QAction(parent=MEAFS)
        self.openabundances.setObjectName("openabundances")
        self.new_2 = QtGui.QAction(parent=MEAFS)
        self.new_2.setObjectName("new_2")
        self.saveas = QtGui.QAction(parent=MEAFS)
        self.saveas.setObjectName("saveas")
        self.quit = QtGui.QAction(parent=MEAFS)
        self.quit.setObjectName("quit")
        self.fullspec = QtGui.QAction(parent=MEAFS)
        self.fullspec.setObjectName("fullspec")
        self.fitpar = QtGui.QAction(parent=MEAFS)
        self.fitpar.setObjectName("fitpar")
        self.menuFile.addAction(self.new_2)
        self.menuFile.addAction(self.open)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.openabundances)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.save)
        self.menuFile.addAction(self.saveas)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.quit)
        self.menuView.addAction(self.fullspec)
        self.menuEdit.addAction(self.fitpar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MEAFS)
        self.methodsdatafittab.setCurrentIndex(2)
        self.methodstab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MEAFS)

    def retranslateUi(self, MEAFS):
        _translate = QtCore.QCoreApplication.translate
        MEAFS.setWindowTitle(_translate("MEAFS", "MEAFS"))
        self.linelistlabel.setText(_translate("MEAFS", "Linelist Options"))
        self.linelistload.setText(_translate("MEAFS", "Load"))
        item = self.linelistcontent.horizontalHeaderItem(0)
        item.setText(_translate("MEAFS", " Element "))
        item = self.linelistcontent.horizontalHeaderItem(1)
        item.setText(_translate("MEAFS", " Wavelength "))
        item = self.linelistcontent.horizontalHeaderItem(2)
        item.setText(_translate("MEAFS", " Analyze "))
        self.linelistbrowse.setText(_translate("MEAFS", "Browse"))
        self.linelistlabel2.setText(_translate("MEAFS", "Linelist Location:"))
        self.linelistcheckbox.setText(_translate("MEAFS", "Select All"))
        self.linelistaddline.setText(_translate("MEAFS", "Add Line"))
        self.linelistremoveline.setText(_translate("MEAFS", "Remove Line"))
        self.referlabel.setText(_translate("MEAFS", "Abundance Reference"))
        self.referlabel2.setText(_translate("MEAFS", "Abund. Ref. Location:"))
        self.referaddline.setText(_translate("MEAFS", "Add Line"))
        self.referremoveline.setText(_translate("MEAFS", "Remove Line"))
        self.referbrowse.setText(_translate("MEAFS", "Browse"))
        self.referload.setText(_translate("MEAFS", "Load"))
        item = self.refercontent.horizontalHeaderItem(0)
        item.setText(_translate("MEAFS", "Element"))
        item = self.refercontent.horizontalHeaderItem(1)
        item.setText(_translate("MEAFS", "Abundance"))
        self.outputbrowse.setText(_translate("MEAFS", "Browse"))
        self.abundanceslabel.setText(_translate("MEAFS", "Abundances"))
        item = self.abundancetable.horizontalHeaderItem(0)
        item.setText(_translate("MEAFS", "Element"))
        item = self.abundancetable.horizontalHeaderItem(1)
        item.setText(_translate("MEAFS", "Wavelength"))
        self.stop.setText(_translate("MEAFS", "Stop"))
        self.progresslabel.setText(_translate("MEAFS", "Progress:"))
        self.run.setText(_translate("MEAFS", "Run"))
        self.progressvalue.setText(_translate("MEAFS", "0/0"))
        self.outputlabel.setText(_translate("MEAFS", "Output Location:"))
        self.label.setText(_translate("MEAFS", "Spectrum Plot"))
        item = self.dataloadtable.horizontalHeaderItem(1)
        item.setText(_translate("MEAFS", "Data"))
        self.delimitertype.setItemText(0, _translate("MEAFS", "Delimiter Type"))
        self.delimitertype.setItemText(1, _translate("MEAFS", "Comma"))
        self.delimitertype.setItemText(2, _translate("MEAFS", "Tab"))
        self.loaddata.setText(_translate("MEAFS", "Load Data"))
        self.methodsdatafittab.setTabText(self.methodsdatafittab.indexOf(self.datatab), _translate("MEAFS", "Data"))
        self.methodconfiglabel.setText(_translate("MEAFS", "Method Configuration"))
        self.methodbox.setItemText(0, _translate("MEAFS", "Equivalent Width"))
        self.methodbox.setItemText(1, _translate("MEAFS", "TurboSpectrum"))
        self.methodbox.setItemText(2, _translate("MEAFS", "PFANT"))
        self.methodbox.setItemText(3, _translate("MEAFS", "Synthe"))
        self.label_2.setText(_translate("MEAFS", "Not Implemented"))
        self.methodstab.setTabText(self.methodstab.indexOf(self.eqwidthtab), _translate("MEAFS", "Eq. Width"))
        self.turbospectrumconfigbrowse.setText(_translate("MEAFS", "Browse"))
        self.turbospectrumoutputbrowse.setText(_translate("MEAFS", "Browse"))
        self.turbospectrumoutputlabel.setText(_translate("MEAFS", "TurboSpectrum Output Location"))
        self.turbospectrumconfiglabel.setText(_translate("MEAFS", "TurboSpectrum Configuration File Location"))
        self.methodstab.setTabText(self.methodstab.indexOf(self.turbspectrumtab), _translate("MEAFS", "TurboSpectrum"))
        self.label_3.setText(_translate("MEAFS", "Not Implemented"))
        self.methodstab.setTabText(self.methodstab.indexOf(self.pfanttab), _translate("MEAFS", "PFANT"))
        self.label_4.setText(_translate("MEAFS", "Not Implemented"))
        self.methodstab.setTabText(self.methodstab.indexOf(self.synthetab), _translate("MEAFS", "Synthe"))
        self.methodsdatafittab.setTabText(self.methodsdatafittab.indexOf(self.majormethodstab), _translate("MEAFS", "Method"))
        self.linedeflabel.setText(_translate("MEAFS", "Current"))
        self.continuumlabel.setText(_translate("MEAFS", "Continuum"))
        self.manualfitbutton.setText(_translate("MEAFS", "Manual Fit"))
        self.lambshiflabel.setText(_translate("MEAFS", "Lamb Shift"))
        self.convolutionlabel.setText(_translate("MEAFS", "Convolution"))
        self.abundancelabel.setText(_translate("MEAFS", "Abundance"))
        self.currentvaluesplotbutton.setText(_translate("MEAFS", "Plot Current Values"))
        self.currentvaluessavebutton.setText(_translate("MEAFS", "Save Current Values"))
        self.methodsdatafittab.setTabText(self.methodsdatafittab.indexOf(self.fitparameterstab), _translate("MEAFS", "Fit Parameters"))
        self.menuFile.setTitle(_translate("MEAFS", "File"))
        self.menuView.setTitle(_translate("MEAFS", "View"))
        self.menuEdit.setTitle(_translate("MEAFS", "Edit"))
        self.actionOpen.setText(_translate("MEAFS", "Open"))
        self.actionSave.setText(_translate("MEAFS", "Save"))
        self.open.setText(_translate("MEAFS", "Open..."))
        self.save.setText(_translate("MEAFS", "Save"))
        self.openabundances.setText(_translate("MEAFS", "Open Abundances..."))
        self.new_2.setText(_translate("MEAFS", "New..."))
        self.saveas.setText(_translate("MEAFS", "Save as..."))
        self.quit.setText(_translate("MEAFS", "Quit"))
        self.fullspec.setText(_translate("MEAFS", "Change Plot to full spectrum range"))
        self.fitpar.setText(_translate("MEAFS", "Fit Parameters"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MEAFS = QtWidgets.QMainWindow()
    ui = Ui_MEAFS()
    ui.setupUi(MEAFS)
    MEAFS.show()
    sys.exit(app.exec())
