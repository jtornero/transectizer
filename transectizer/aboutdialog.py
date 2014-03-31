# -*- coding: utf-8 -*-
"""
/***************************************************************************
TransectizerDialog
                                 A QGIS plugin
Transectizer plugin
                             -------------------
        begin                : 2013-11-21
        copyright            : (C) 2013 by Jorge Tornero
        email                : jtorlistas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_about import Ui_aboutDialog
# create the dialog for zoom to point


class aboutDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)
        
        # We have implemented the help as a QWebView, so we need
        # to translate the path for the html file of the help
        self.url = QtCore.QUrl(self.tr('qrc:/help/html/help/html/help_en.html'))
        self.ui.webView.load(self.url)
        