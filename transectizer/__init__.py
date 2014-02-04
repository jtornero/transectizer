# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Transectizer
                                 A QGIS plugin
 Transectizer plugin
                             -------------------
        begin                : 2013-11-21
        copyright            : (C) 2013 by jorge
        email                : jorge.tornero@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load transectizer class from file transectizer
    from transectizer import transectizer
    return transectizer(iface)
