# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about.ui'
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

class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        aboutDialog.setObjectName(_fromUtf8("aboutDialog"))
        aboutDialog.setWindowModality(QtCore.Qt.WindowModal)
        aboutDialog.resize(400, 613)
        self.tabWidget = QtGui.QTabWidget(aboutDialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 381, 561))
        self.tabWidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.aboutTab = QtGui.QWidget()
        self.aboutTab.setObjectName(_fromUtf8("aboutTab"))
        self.licenseText = QtGui.QTextBrowser(self.aboutTab)
        self.licenseText.setGeometry(QtCore.QRect(5, 180, 361, 341))
        self.licenseText.setObjectName(_fromUtf8("licenseText"))
        self.abotLabel = QtGui.QLabel(self.aboutTab)
        self.abotLabel.setGeometry(QtCore.QRect(10, 10, 350, 160))
        self.abotLabel.setObjectName(_fromUtf8("abotLabel"))
        self.tabWidget.addTab(self.aboutTab, _fromUtf8(""))
        self.helpTab = QtGui.QWidget()
        self.helpTab.setObjectName(_fromUtf8("helpTab"))
        self.webView = QtWebKit.QWebView(self.helpTab)
        self.webView.setGeometry(QtCore.QRect(10, 10, 351, 511))
        self.webView.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("qrc:/plugins/transectizer/help/html/help/html/help_en.html")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.tabWidget.addTab(self.helpTab, _fromUtf8(""))
        self.closeButton = QtGui.QPushButton(aboutDialog)
        self.closeButton.setGeometry(QtCore.QRect(140, 580, 99, 23))
        self.closeButton.setDefault(True)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))

        self.retranslateUi(aboutDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), aboutDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(aboutDialog)

    def retranslateUi(self, aboutDialog):
        aboutDialog.setWindowTitle(_translate("aboutDialog", "About Transectizer", None))
        self.licenseText.setDocumentTitle(_translate("aboutDialog", "License", None))
        self.licenseText.setHtml(_translate("aboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><title>License</title><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">GNU GENERAL PUBLIC LICENSE</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:4px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:small; font-weight:600;\">Version 3, 29 June 2007</span> </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.<br /><br />This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.<br /><br />You should have received a copy of the GNU General Public License along with this program. If not, see:<br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.gnu.org/licenses\"><span style=\" text-decoration: underline; color:#006e28;\">http://www.gnu.org/licenses</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.abotLabel.setText(_translate("aboutDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:xx-large; font-weight:600;\">Transectizer</span></p><p align=\"center\"><span style=\" font-size:14pt;\">A plugin for transect design in QGIS</span></p><p align=\"center\"><span style=\" font-size:medium; font-weight:600;\">Version 1.0</span></p><p align=\"center\">© 2013, 2014 Jorge Tornero<br/><a href=\"http://imasdemase.com\"><span style=\" text-decoration: underline; color:#006e28;\">http://imasdemase.com</span></a><br/></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.aboutTab), _translate("aboutDialog", "About", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.helpTab), _translate("aboutDialog", "Help", None))
        self.closeButton.setText(_translate("aboutDialog", "Close", None))

from PyQt4 import QtWebKit
import resources_rc
