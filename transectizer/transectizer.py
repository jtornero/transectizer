# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Transectizer
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

# IGUALES OK
# COMAS
# LINEBREAKS
# VINCENTY FORMULA


# Import the PyQt and QGIS libraries
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4 import uic
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from transectizerdialog import transectizerDialog
from manualStationNaming import manualNamesDialog
from aboutdialog import aboutDialog
# import other modules
import math
import os.path
import imp

class transectizer(QDialog):

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        QDialog.__init__(self, parent=None)
        self.canvas = self.iface.mapCanvas()
        self.clickTool = clickTool(self.canvas)
        
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'transectizer_{}.qm'.format(locale))
        
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = transectizerDialog()
        
        
        # Signals and slot connections
        self.dlg.ui.layersCombo.activated.connect(self.checkForTransectizerLayer)
        self.dlg.ui.newTransectButton.clicked.connect(self.newTransect)
        self.dlg.ui.outputToExisting.toggled.connect(self.populateLayersCombo)
        self.dlg.ui.autoNameCheck.toggled.connect(self.autoNamingToggled)
        self.dlg.ui.finalLon.editingFinished.connect(self.calculateBearing)
        self.dlg.ui.autoTransectCheck.toggled.connect(self.autoTransectToggled)
        self.dlg.ui.aboutButton.clicked.connect(self.about)
        self.dlg.ui.GPSButton.clicked.connect(self.getCoordsFromGPS)
        
        # Initial variables and states which must be set
        self.autoTransectToggled(True)
        self.autoNaming = True
        
        self.firstSelectedPoint = False
        self.secondSelectedPoint = False
        
        self.initialPoint = QgsVertexMarker(self.canvas)
        self.initialPoint.hide()
        self.finalPoint = QgsVertexMarker(self.canvas)
        self.finalPoint.setIconType(QgsVertexMarker.ICON_BOX)
        self.finalPoint.hide()

        
    def updatePos(self, point):
        """
        Updates and draws the marker for initial and final point 
        of the transect on the canvas
        Parameters:
            point: a QgsPoint
        """
        
        # Updates and draws the position of the final point, only if
        # the first point has been already deployed
        if not self.secondSelectedPoint and self.firstSelectedPoint:
            self.finalPoint.setCenter(point)
            self.finalPoint.show()
            self.dlg.ui.finalLat.setValue(point.y())
            self.dlg.ui.finalLon.setValue(point.x())
            self.secondSelectedPoint = True
            self.calculateBearing()
        # Updates and draws the position of the initial point.
        if not self.firstSelectedPoint:
            self.initialPoint.setCenter(point)
            self.initialPoint.show()
            self.dlg.ui.startLat.setValue(point.y())
            self.dlg.ui.startLon.setValue(point.x())
            self.firstSelectedPoint = True
            self.calculateBearing()
        
    def resetFirstPoint(self):
        """
        Resets the lineEdit widgets for the initial point, as
        well as the calculated bearing
        """
        self.dlg.ui.startLat.setValue(0)
        self.dlg.ui.startLon.setValue(0)
        self.dlg.ui.bearing.clear()
        self.initialPoint.hide()
        self.firstSelectedPoint = False
    
    def resetSecondPoint(self):
        """
        Resets the lineEdit widgets for the final point, as
        well as the calculated bearing
        """
        self.dlg.ui.finalLat.setValue(0)
        self.dlg.ui.finalLon.setValue(0)
        self.dlg.ui.bearing.clear()
        self.finalPoint.hide()
        self.secondSelectedPoint = False
    
    def calculateBearing(self):
        """
        Convenience function for bearing calculation
        taking the values from the GUI's lineEdit for
        transect line initial and final points.
        """
        
        if (not self.firstSelectedPoint) or (not self.secondSelectedPoint):
            return
        
        startLat = self.dlg.ui.startLat.value()
        startLon = self.dlg.ui.startLon.value()
        endLat = self.dlg.ui.finalLat.value()
        endLon = self.dlg.ui.finalLon.value()
        initialPoint = QgsPoint(startLon, startLat)
        endPoint = QgsPoint(endLon, endLat)
        self.calculateBearingFromPoints(initialPoint, endPoint)

    def calculateBearingFromPoints(self, initialPoint, endPoint):
        
        """
        This function calculates the bearing from an initial QGsPoint
        to a final QgsPoint. All calculations are made on the basis of
        a decimal degrees in WGS84.
        Parameters:
            initialPoint: QgsPoint
            endPoint: QgsPoint
        """
        # Transform the points provided to WGS84. The transformation
        # is made with a QgsCoordinateTransform created when the plugin
        # is loaded
        
        initialPoint = self.transform.transform(initialPoint)
        endPoint = self.transform.transform(endPoint)
        
        # First coords to radians
        startLat = math.radians(initialPoint.y())
        startLon = math.radians(initialPoint.x())
        endLat = math.radians(endPoint.y())
        endLon = math.radians(endPoint.x())
        
        # Calculation. The bearing is obtained in azimuth and radians and must be
        # transformed to degrees and bearing
        deltaLon = endLon - startLon
        y = math.sin(deltaLon) * math.cos(endLat)
        x = math.cos(startLat) * math.sin(endLat) - math.sin(startLat) *\
            math.cos(endLat) * math.cos(deltaLon)
        bearing = (5 * math.pi / 2) - math.atan2(x, y)
        bearing = round( math.degrees(bearing), 0) % 360 
        self.dlg.ui.bearing.setValue(bearing)
    
    def getCoordsFromGPS(self):
        """This function grabs coordinates for the initial point
        of the transect if there is one available GPS connection
        """
        # First we get the connectionRegistry

        connectionRegistry = QgsGPSConnectionRegistry().instance()

        # Now the connections list from that registry instance

        connectionList = connectionRegistry.connectionList()
              
        if connectionList:

            GPSInfo = connectionList[0].currentGPSInformation()

            # And now, we extract the info we want 

            lon = GPSInfo.longitude
            lat = GPSInfo.latitude
            self.dlg.ui.startLat.setValue(lat)
            self.dlg.ui.startLon.setValue(lon)
            self.firstSelectedPoint = True
            
            # We get and store the point received from GPS
            mapPoint=QgsPoint(lon, lat)
            
            # We need to transform the point received from
            #the GPS to canvas coordinates to pass it to the 
            #clickTool in canvas coordinates.
            
            mapUnitsPerPixel = self.canvas.mapUnitsPerPixel()
            transformer = QgsMapToPixel(mapUnitsPerPixel)
            canvasPoint = transformer.transform(lon,lat)            
            self.clickTool.setFirstPoint(mapPoint, canvasPoint)
        
        else:
            msg = QMessageBox()
            msg.setText("<center>Sorry, no GPS connection available</center>")
            msg.exec_()
        
    def initGui(self):
        
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/transectizer/icon.png"),
            u"transectizer", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)
    
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Transectizer", self.action)
        self.iface.digitizeToolBar().addAction(self.action)
        

    def unload(self):
        
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Transectizer", self.action)
        self.iface.removeToolBarIcon(self.action)
        
    def populateLayersCombo(self):
        """
        Populates the layer selection combo with the point layers
        loaded in the project.
        """
        
        self.dlg.ui.layersCombo.clear()
        
        # We iterate through the layers in the project
        for layer in self.iface.legendInterface().layers():
            QgsMapLayerRegistry.instance().mapLayers()
            
            # First we check if we have a vector layer
            if layer.type() == QgsMapLayer.VectorLayer:
                
                #And now if it is of the point type
                if layer.geometryType() == QGis.Point:
                    self.dlg.ui.layersCombo.addItem(layer.name())
        # If after all we don't have any appropiate layer, we
        # disable the combo and check for new layer creation
        if self.dlg.ui.layersCombo.count() == 0:
            self.dlg.ui.layersCombo.setEnabled(False)
            self.dlg.ui.outputToNew.setChecked(True)
        else:
            self.dlg.ui.layersCombo.setEnabled(True)
   
    def autoNamingToggled(self, isAutoNamingChecked):
        """
        This slot enables or disables the auto-naming of the created 
        stations depending on the state of autoNameCheck
        """
        
        if not isAutoNamingChecked:
           self.autoNaming = False
           return 
        else:
           self.autoNaming = True
           return
       
    def autoTransectToggled(self, isAutoTransectChecked):
        """
        This slot enables or disables the automatic transect creation,
        connecting or disconnecting the clickTool.
        """
        # Manual transect creation
        if not isAutoTransectChecked:
            
            self.dlg.ui.startLat.setEnabled(True)
            self.dlg.ui.startLon.setEnabled(True)
            self.dlg.ui.finalLat.setEnabled(True)
            self.dlg.ui.finalLon.setEnabled(True)
            self.clickTool.iniPointSelected.disconnect(self.resetFirstPoint)
            self.clickTool.iniPointSelected.disconnect(self.resetSecondPoint)
            self.clickTool.endPointSelected.disconnect(self.resetSecondPoint)
            self.clickTool.iniPointSelected.disconnect(self.updatePos)
            self.clickTool.endPointSelected.disconnect(self.updatePos)
            self.clickTool.movingCanvas.disconnect(self.calculateBearingFromPoints)
            self.firstSelectedPoint = True
            self.secondSelectedPoint = True
            return
        # Automatic transect creation: 
        else:
            self.dlg.ui.startLat.setEnabled(False)
            self.dlg.ui.startLon.setEnabled(False)
            self.dlg.ui.finalLat.setEnabled(False)
            self.dlg.ui.finalLon.setEnabled(False)
            self.clickTool.iniPointSelected.connect(self.resetFirstPoint)
            self.clickTool.iniPointSelected.connect(self.resetSecondPoint)
            self.clickTool.endPointSelected.connect(self.resetSecondPoint)
            self.clickTool.iniPointSelected.connect(self.updatePos)
            self.clickTool.endPointSelected.connect(self.updatePos)
            self.clickTool.movingCanvas.connect(self.calculateBearingFromPoints)
            return           
        
    def newTransect(self):
        """
        Draws and stores the points for the transect, making the
        appropiate checks for all to work properly.
        """
        
        # Gets the distance between stations and checks if it's greater
        # than zero.
        dst =  self.dlg.ui.dstBtwnStations.value()
        if dst == 0:

            msg = QMessageBox()
            msg.setText("<center>Please provide a distance between stations greater than 0 %s<center>"
                %self.dlg.ui.unitsCombo.currentText().lower())
            msg.exec_()
            return

        # Gets the number of stations to be deployed and check if it's
        # greater than zero.
        numberOfStations = self.dlg.ui.numberOfStations.value()
        if numberOfStations == 0:

            msg=QMessageBox()
            msg.setText("<center>Please provide a number of stations greater than 0<center>")
            msg.exec_()
            return
        
        # Gets the values for the main calculations:
        # Bearing, initial latitude, initial longitude
        # and creates a QgsPoint with them
        brg = self.dlg.ui.bearing.value()
        lat = self.dlg.ui.startLat.value()
        lon = self.dlg.ui.startLon.value()
        startPoint = QgsPoint(lon,lat)
        
        # Gets the chosen measurment unit for the distance
        # between stations and converts it to meters
        unit = self.dlg.ui.unitsCombo.currentIndex()
        if unit == 1:
            dst = dst * 1000.0 #Meters, no conversion at all
        elif unit == 2:
            dst = dst * 0.3048 #Feet
        elif unit == 3: 
            dst = dst * 0.9144 #Yards
        elif unit == 4:
            dst = dst * 1609.344 #Miles
        elif unit == 5:
            dst = dst * 1852.0 #Nautical Miles
        
        # Management of output layer
        if self.dlg.ui.outputToNew.isChecked():
            # If we want a new layer, let's create it with
            # the name provided in newLayerName lineEdit
            layer = self.createTransectizerLayer(self.dlg.ui.newLayerName.text())
        else:
            # Otherwise, we must check if the selected layer
            # is appropiate for working with Transectizer.
            # If not, the called function will offer the user
            # the possibility to enable the selected layer for
            # working with Transectizer creating the needed attributes.
            layer = self.checkForTransectizerLayer(selectedByCombo = False)
        
        # If after all we have a working layer, we start the station deployment
        if layer:
            
            startPoint = self.transform.transform(startPoint)
            lat = startPoint.y()
            lon = startPoint.x()
            stations = []
            nlat = lat
            nlon = lon        
            layer.startEditing()
            featureCount = int(layer.featureCount()) 
            layerFields = layer.dataProvider().fields()
            # I instntiate the manual naming dialog even if
            # it is not checked. Maybe there is a better way,
            # just checking if there is already such a dialog
            # (See (***) ahead)
             
            mnNamesDialog = manualNamesDialog()
            
            offset = 0 # Stores the offset from the initial station number
            stationNumber = 1
            
            # Deployment of stations. Because we already have a start point
            # to be deployed, we place it first and its attributes and 
            # then we calculate the new start point
            for station in range(0, numberOfStations):
               
                if self.autoNaming:
                    
                    transectSurvey = self.dlg.ui.surveyName.text()
                    stationName = self.dlg.ui.stationPrefix.text()
                    offset = self.dlg.ui.initialStationNumber.value()
                    stationNumber = station + offset
                    stationObs = ""
                else:
                    # (***) Maybe this is the place to create them
                    # manual naming dialog checking in the subsequent
                    # iterations for its existence, but don't know how
                    
                    # If any of the fix text checkboxes are toggled, it saves
                    # the text of the correspondig lineEdit for the
                    # the subsequent stations
                    if mnNamesDialog.ui.fixTransectCheck.isChecked() == True:
                        mnNamesDialog.ui.transectText.setText(transectSurvey)
                    else:
                        mnNamesDialog.ui.transectText.clear()

                    if mnNamesDialog.ui.fixStationCheck.isChecked() == True:
                        mnNamesDialog.ui.stationText.setText(stationName) 
                    else:
                        mnNamesDialog.ui.stationText.clear()
                                         
                    if mnNamesDialog.ui.fixObservationCheck.isChecked() == True:
                        mnNamesDialog.ui.observationsText.setText(stationObs)
                    else:
                        mnNamesDialog.ui.observationsText.clear()
                        
                    mnNamesDialog.exec_()
           
                    transectSurvey = mnNamesDialog.ui.transectText.text()
                    stationName = mnNamesDialog.ui.stationText.text()
                    stationNumber = mnNamesDialog.ui.stnNumberText.value()
                    stationObs = mnNamesDialog.ui.observationsText.text()
                    # Manages station number sequencing
                    if mnNamesDialog.ui.autoNumberCheck.isChecked() == True:
                        mnNamesDialog.ui.stnNumberText.setValue(stationNumber + 1)
                    else:
                        mnNamesDialog.ui.stnNumberText.setValue(stationNumber)
                        
                #Creates the point for the calculation
                point = QgsPoint(nlon,nlat)
                
                # Adding the new feature to the layer
                feature = QgsFeature(layerFields)
                feature.setGeometry(QgsGeometry.fromPoint(point))
                
                feature.setAttribute(layer.fieldNameIndex('id'), station + featureCount)
                feature.setAttribute(layer.fieldNameIndex('survey'), transectSurvey)
                feature.setAttribute(layer.fieldNameIndex('station'), stationName)
                feature.setAttribute(layer.fieldNameIndex('stnnum'), stationNumber)
                feature.setAttribute(layer.fieldNameIndex('stnlat'), point.y())
                feature.setAttribute(layer.fieldNameIndex('stnlon'), point.x())
                feature.setAttribute(layer.fieldNameIndex('stnobs'), stationObs)

                layer.addFeature(feature, True)
                # Now the departure point for the next iteration is calculated
                nlat, nlon, nbrg = self.vinc_pt(1/298.257223563, 6378137.0,
                                            lat, lon,brg,dst * (station + 1))
            # When all stations are deployed, changes ar commited
            # and canvas refresed
            layer.commitChanges()
            layer.triggerRepaint()
            
    def run(self):
        
        self.canvas.setMapTool(self.clickTool)
        
        #Populate existing layers combobox iwth layer list
        self.populateLayersCombo()
        
        
        #Show the dialog
        self.dlg.show()
        
        # Creation of coordinate transform object from project SRS to WGS84
        projectSrsEntry = QgsProject.instance().readEntry("SpatialRefSys", "/ProjectCRSProj4String")
        projectSrs = QgsCoordinateReferenceSystem()
        projectSrs.createFromProj4(projectSrsEntry[0])
        wgs84 = QgsCoordinateReferenceSystem(4326)
        self.transform = QgsCoordinateTransform(projectSrs,wgs84)
        
        # Run the dialog event loop
        self.dlg.exec_()
        #After dialog is closed
        self.canvas.unsetMapTool(self.clickTool)
    
    def createTransectizerLayer(self,newLayerName):
      """
      This function creates a new memory layer for the stations and its
      features to be stored in WGS84, adds the layer to the project
      and updates layersCombo.
      Parameters:
        newLayerName: String with the name of the new layer
      TODO: Make possible to store the layer in file/DB
      """
      
      self.transectizerLayer =  QgsVectorLayer(
              "Point?crs=epsg:4326&field=id:integer&field=survey:string(20)&field=station:string(5)&field=stnnum:integer&field=stnlat:double&field=stnlon:double&field=stnobs:string(254)&index=yes",
              newLayerName,
              "memory")
      self.provider = self.transectizerLayer.dataProvider()
      self.transectizerLayer.setDisplayField("description")
      QgsMapLayerRegistry.instance().addMapLayer(self.transectizerLayer)
      # We update the layersCombo to make the new layer available for the plugin
      self.populateLayersCombo()
      # And the function returns the new layer
      return self.transectizerLayer
    
    def checkForTransectizerLayer(self, selectedByCombo = True):
        """
        This slto checks if a layer is appropiate for woriking with
        Transectizer. A such layer should have the following
        Attributes:
        ===========
        survey(string, 20): A descripive name of survey/transect.
        station:(string, 10): A descriptive name/prefix for the stations.
        stnnum(int): Sequential/arbitrary number for the station.
        stnlat(double): Latitude, , in decimal degrees, for the station.
        stnlon(double): Longitude, in decimal degrees, for the station.
        stnobs(string, 254): Observations/remarks for the station.
        
        Checking a layer is done field by field, against a field list
        """
        
        # Creating the list of fields to be compared
        surveyField = QgsField(name = 'survey', type = 10, typeName = 'string', len = 20)
        stationField = QgsField(name = 'station', type = 10, typeName = 'string', len = 5)
        stnnumField = QgsField(name = 'stnnum', type =2 , typeName = 'integer', len = 10, prec = 0)
        stnlatField = QgsField(name = 'stnlat', type = 6, typeName = 'double', len = 20, prec = 5)
        stnlonField = QgsField(name = 'stnlon', type = 6, typeName = 'double', len = 20, prec = 5)
        stnobsField = QgsField(name = 'stnobs', type = 10, typeName = 'string', len = 254)
        
        fieldList = (surveyField, stationField, stnnumField, stnlatField, stnlonField, stnobsField)
        
        # Now we get the fields from the layer to be checked
        layerName = self.dlg.ui.layersCombo.currentText()
        layer = QgsMapLayerRegistry.instance().mapLayersByName(layerName)[0]
        provider = layer.dataProvider()
        fieldsToCheck = provider.fields()
        
        # A valid layer for the transectizer will have ALL of the defined
        # fields. Direct comparation on fields is possible.
        layerOK = all(field in fieldsToCheck for field in fieldList)
       
        
        # Time to manage the results of the field tests
        msg = QMessageBox() 
        
        # If our layer is compatible with transectizer (it has all the
        # required fields), we just return it
        if layerOK:
            if selectedByCombo:
                msg.setText("<center>%s is a valid layer<br>for Transectizer to work<center>" %layerName)
                msg.exec_()
            return layer
        # If not, we offer the user the chance
        # of creating them in the chosen layer
        else:
            msg.setText("""<center>It looks like the selected layer<br>
                has not the fields required for Transectizer to work.<br>
                Do you want them to be added to your layer?<center>""")
            btn1 = msg.addButton(u"Add and continue", QMessageBox.YesRole)
            btn2 = msg.addButton(u"Cancel", QMessageBox.NoRole)
            msg.exec_()
            # Creation of the new fields in the layer
            if msg.clickedButton() == btn1:
                layer.startEditing()
                layer.dataProvider().addAttributes(fieldList)
                layer.commitChanges()
                layer.reload()
                return layer
            else:
                return False
                
      
    
    def  vinc_pt( self ,f, a, phi1, lembda1, alpha12, s ) : 
        import math
        """ 
        Returns the lat and long of projected point and reverse azimuth 
        given a reference point and a distance and azimuth to project. 
        lats, longs and azimuths are passed in decimal degrees 
        Returns ( phi2,  lambda2,  alpha21 ) as a tuple 
        NOTE: This code has some license issues. It has been obtained 
        from a forum and its license is not clear. I'll reimplement with
        GPL3 as soon as possible.
        The code has been taken from
        https://isis.astrogeology.usgs.gov/IsisSupport/index.php?topic=408.0
        and refers to (broken link)
        http://wegener.mechanik.tu-darmstadt.de/GMT-Help/Archiv/att-8710/Geodetic_py
        """ 
        piD4 = math.atan( 1.0 ) 
        two_pi = piD4 * 8.0 
        phi1    = phi1    * piD4 / 45.0 
        lembda1 = lembda1 * piD4 / 45.0 
        alpha12 = alpha12 * piD4 / 45.0 
        if ( alpha12 < 0.0 ) : 
            alpha12 = alpha12 + two_pi 
        if ( alpha12 > two_pi ) : 
            alpha12 = alpha12 - two_pi 

        b = a * (1.0 - f) 
        TanU1 = (1-f) * math.tan(phi1) 
        U1 = math.atan( TanU1 ) 
        sigma1 = math.atan2( TanU1, math.cos(alpha12) ) 
        Sinalpha = math.cos(U1) * math.sin(alpha12) 
        cosalpha_sq = 1.0 - Sinalpha * Sinalpha 
            
        u2 = cosalpha_sq * (a * a - b * b ) / (b * b) 
        A = 1.0 + (u2 / 16384) * (4096 + u2 * (-768 + u2 * \
            (320 - 175 * u2) ) ) 
        B = (u2 / 1024) * (256 + u2 * (-128 + u2 * (74 - 47 * u2) ) ) 
            
        # Starting with the approx 
        sigma = (s / (b * A)) 
        last_sigma = 2.0 * sigma + 2.0   # something impossible 
            
        # Iterate the following 3 eqs unitl no sig change in sigma 
        # two_sigma_m , delta_sigma 
        while ( abs( (last_sigma - sigma) / sigma) > 1.0e-9 ) : 

            two_sigma_m = 2 * sigma1 + sigma 
            delta_sigma = B * math.sin(sigma) * ( math.cos(two_sigma_m) \
                    + (B/4) * (math.cos(sigma) * \
                    (-1 + 2 * math.pow( math.cos(two_sigma_m), 2 ) -  \
                    (B/6) * math.cos(two_sigma_m) * \
                    (-3 + 4 * math.pow(math.sin(sigma), 2 )) *  \
                    (-3 + 4 * math.pow( math.cos (two_sigma_m), 2 ))))) \
            
            last_sigma = sigma 
            sigma = (s / (b * A)) + delta_sigma 
            
        phi2 = math.atan2 ( (math.sin(U1) * math.cos(sigma) + math.cos(U1) * math.sin(sigma) * math.cos(alpha12) ), \
            ((1-f) * math.sqrt( math.pow(Sinalpha, 2) +  \
            pow(math.sin(U1) * math.sin(sigma) - math.cos(U1) * math.cos(sigma) * math.cos(alpha12), 2)))) 
            
        lembda = math.atan2( (math.sin(sigma) * math.sin(alpha12 )), (math.cos(U1) * math.cos(sigma) -  \
                math.sin(U1) *  math.sin(sigma) * math.cos(alpha12))) 
            
        C = (f/16) * cosalpha_sq * (4 + f * (4 - 3 * cosalpha_sq )) 
        omega = lembda - (1-C) * f * Sinalpha *  \
            (sigma + C * math.sin(sigma) * (math.cos(two_sigma_m) + \
            C * math.cos(sigma) * (-1 + 2 * math.pow(math.cos(two_sigma_m),2) ))) 

        lembda2 = lembda1 + omega 
        alpha21 = math.atan2 ( Sinalpha, (-math.sin(U1) * math.sin(sigma) +  \
            math.cos(U1) * math.cos(sigma) * math.cos(alpha12))) 

        alpha21 = alpha21 + two_pi / 2.0 
        if ( alpha21 < 0.0 ) : 
            alpha21 = alpha21 + two_pi 
        if ( alpha21 > two_pi ) : 
            alpha21 = alpha21 - two_pi 

        phi2       = phi2       * 45.0 / piD4 
        lembda2    = lembda2    * 45.0 / piD4 
        alpha21    = alpha21    * 45.0 / piD4 
        return phi2,  lembda2,  alpha21 

    def about(self):
        """
        This function just shows the About/help dialog
        """
        aboutDialog().exec_()
        

class clickTool(QgsMapToolEmitPoint):
    """
    This class provides a clicktool which, once selected a
    start point clicking on the canvas, draws a rubberband
    showing a line until the mouse button is released.
    
    """   
    iniPointSelected = pyqtSignal(QgsPoint)
    endPointSelected = pyqtSignal(QgsPoint)
    movingCanvas = pyqtSignal(QgsPoint, QgsPoint)
    
    def __init__(self, canvas):
        
        # Initialzation of the tool
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Line)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.alreadyStarted = False
        self.reset()

    def reset(self):
        # Resets the tool
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset()
        
    def deactivate(self):
        
        self.rubberBand.reset()
    
    def setFirstPoint(self,mapPoint,canvasPoint):
    #def setFirstPoint(self,canvasPoint):
        """
        This functions makes possible to programatically pass a point as
        initial point, simulating a MouseEvent
        """
        
        self.alreadyStarted = True
        self.startPoint = mapPoint
        cvPoint = QPoint(canvasPoint.x(),canvasPoint.y())
        simuClick = QMouseEvent(QEvent.MouseButtonPress,cvPoint,
            Qt.LeftButton,Qt.LeftButton,Qt.NoModifier,)
        
        self.canvasPressEvent(simuClick)
    
    def canvasPressEvent(self, e):
        """
        Clicks on the canvas cause the tool to be reset and
        the rubberband initialized. The signal iniPointSelected
        is emitted and isEmittingPoint is set to True, so the tool
        starts to draw the rubberband. If self.alreadyStarted is set
        to True, means that the first point has been set by other means
        """
        
        #self.reset()
        if not self.alreadyStarted:
            self.reset()
            self.startPoint = self.toMapCoordinates(e.pos())
            
        else:
            self.isEmittingPoint = False
            
        self.endPoint = self.startPoint
        self.rubberBand.reset()
        self.rubberBand.addPoint(self.startPoint)
        self.rubberBand.addPoint(self.endPoint)
        self.isEmittingPoint = True
        self.iniPointSelected.emit(self.startPoint)

    def canvasReleaseEvent(self, e):
        
        """
        When the user releases the button,the signal endPointSelected
        is emitted and self.isEmittingPoint is set to True. Also, sets
        alreadyStarted to false.
        """
        self.isEmittingPoint = False
        self.alreadyStarted = False
        self.endPointSelected.emit(self.toMapCoordinates(e.pos()))
        
    def canvasMoveEvent(self, e):
        """
        When isEmittingPoint is True (set by canvasPressEvent),
        the signal movingCanvas is emitted with the initial and end
        point of the rubberband and also the rubberBand is updated.
        """
        if self.isEmittingPoint:
            self.rubberBand.movePoint(self.toMapCoordinates(e.pos()))
            self.movingCanvas.emit(self.startPoint,self.toMapCoordinates(e.pos()))