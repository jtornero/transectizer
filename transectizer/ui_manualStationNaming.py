# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_manualStationNaming.ui'
#
# Created by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_manualNamesDialog(object):
    def setupUi(self, manualNamesDialog):
        manualNamesDialog.setObjectName(_fromUtf8("manualNamesDialog"))
        manualNamesDialog.setWindowModality(QtCore.Qt.WindowModal)
        manualNamesDialog.resize(280, 146)
        manualNamesDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(manualNamesDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.transectLabel = QtGui.QLabel(manualNamesDialog)
        self.transectLabel.setObjectName(_fromUtf8("transectLabel"))
        self.mainLayout.addWidget(self.transectLabel, 0, 0, 1, 1)
        self.transectText = QtGui.QLineEdit(manualNamesDialog)
        self.transectText.setMaxLength(20)
        self.transectText.setObjectName(_fromUtf8("transectText"))
        self.mainLayout.addWidget(self.transectText, 0, 1, 1, 1)
        self.fixTransectCheck = QtGui.QCheckBox(manualNamesDialog)
        self.fixTransectCheck.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fixTransectCheck.setObjectName(_fromUtf8("fixTransectCheck"))
        self.mainLayout.addWidget(self.fixTransectCheck, 0, 2, 1, 1)
        self.stationLabel = QtGui.QLabel(manualNamesDialog)
        self.stationLabel.setObjectName(_fromUtf8("stationLabel"))
        self.mainLayout.addWidget(self.stationLabel, 1, 0, 1, 1)
        self.stationText = QtGui.QLineEdit(manualNamesDialog)
        self.stationText.setMaxLength(10)
        self.stationText.setObjectName(_fromUtf8("stationText"))
        self.mainLayout.addWidget(self.stationText, 1, 1, 1, 1)
        self.fixStationCheck = QtGui.QCheckBox(manualNamesDialog)
        self.fixStationCheck.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fixStationCheck.setObjectName(_fromUtf8("fixStationCheck"))
        self.mainLayout.addWidget(self.fixStationCheck, 1, 2, 1, 1)
        self.stnNumberLabel = QtGui.QLabel(manualNamesDialog)
        self.stnNumberLabel.setObjectName(_fromUtf8("stnNumberLabel"))
        self.mainLayout.addWidget(self.stnNumberLabel, 2, 0, 1, 1)
        self.observationsLabel = QtGui.QLabel(manualNamesDialog)
        self.observationsLabel.setObjectName(_fromUtf8("observationsLabel"))
        self.mainLayout.addWidget(self.observationsLabel, 3, 0, 1, 1)
        self.observationsText = QtGui.QLineEdit(manualNamesDialog)
        self.observationsText.setText(_fromUtf8(""))
        self.observationsText.setMaxLength(254)
        self.observationsText.setObjectName(_fromUtf8("observationsText"))
        self.mainLayout.addWidget(self.observationsText, 3, 1, 1, 1)
        self.fixObservationCheck = QtGui.QCheckBox(manualNamesDialog)
        self.fixObservationCheck.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fixObservationCheck.setObjectName(_fromUtf8("fixObservationCheck"))
        self.mainLayout.addWidget(self.fixObservationCheck, 3, 2, 1, 1)
        self.stnNumberText = QtGui.QSpinBox(manualNamesDialog)
        self.stnNumberText.setMinimum(1)
        self.stnNumberText.setMaximum(999)
        self.stnNumberText.setProperty("value", 1)
        self.stnNumberText.setObjectName(_fromUtf8("stnNumberText"))
        self.mainLayout.addWidget(self.stnNumberText, 2, 1, 1, 1)
        self.autoNumberCheck = QtGui.QCheckBox(manualNamesDialog)
        self.autoNumberCheck.setFocusPolicy(QtCore.Qt.NoFocus)
        self.autoNumberCheck.setObjectName(_fromUtf8("autoNumberCheck"))
        self.mainLayout.addWidget(self.autoNumberCheck, 2, 2, 1, 1)
        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(manualNamesDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(manualNamesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), manualNamesDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(manualNamesDialog)
        manualNamesDialog.setTabOrder(self.transectText, self.stationText)
        manualNamesDialog.setTabOrder(self.stationText, self.observationsText)

    def retranslateUi(self, manualNamesDialog):
        manualNamesDialog.setWindowTitle(_translate("manualNamesDialog", "Manual Station naming", None))
        self.transectLabel.setText(_translate("manualNamesDialog", "Transect Name", None))
        self.fixTransectCheck.setText(_translate("manualNamesDialog", "Fix", None))
        self.stationLabel.setText(_translate("manualNamesDialog", "Station prefix", None))
        self.fixStationCheck.setText(_translate("manualNamesDialog", "Fix", None))
        self.stnNumberLabel.setText(_translate("manualNamesDialog", "Station Number", None))
        self.observationsLabel.setText(_translate("manualNamesDialog", "Observations", None))
        self.fixObservationCheck.setText(_translate("manualNamesDialog", "Fix", None))
        self.autoNumberCheck.setText(_translate("manualNamesDialog", "Auto", None))

