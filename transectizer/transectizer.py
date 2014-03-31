# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Transectizer
                                 A QGIS plugin for easy design of linear 
                                 transects with sampling stations distributed
                                 along the transect at a given distance
 Transectizer plugin
                              -------------------
        begin                : 2013-11-21
        copyright            : (C) 2013,2014 by Jorge Tornero
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

# Import the PyQt and QGIS libraries
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4 import uic

# Initialize Qt resources from file resources.py
# Resources file includes the html and image for
# the plugin help to work
import resources_rc

# Import the code for the dialog
from transectizerdialog import transectizerDialog
from manualStationNaming import manualNamesDialog
from aboutdialog import aboutDialog

# import other modules
import math
import os.path
import imp

class transectizer(QObject):

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        QDockWidget.__init__(self, self.iface.mainWindow())
        self.canvas = self.iface.mapCanvas()
        self.clickTool = clickTool(self.canvas,self.iface)
        self.clickTool.deactivate()
        
        # LOCALIZATION
        
        locale = QSettings().value("locale/userLocale")[0:2]
        
        mainTranslatorPath = os.path.join(\
            self.plugin_dir, 'i18n', 'ui_transectizer_{0}.qm'.format(locale))
        codeTranslatorPath = os.path.join(\
            self.plugin_dir, 'i18n', 'transectizer_{0}.qm'.format(locale))
        manualStationInfoTranslatorPath = os.path.join(\
            self.plugin_dir, 'i18n', 'ui_manualStationNaming_{0}.qm'.format(locale))
        aboutTranslatorPath = os.path.join(\
            self.plugin_dir, 'i18n', 'ui_about_{0}.qm'.format(locale))
        helpTranslatorPath = os.path.join(\
            self.plugin_dir, 'i18n', 'about_dialog_{0}.qm'.format(locale))
       
        # Localization
        self.mainTranslator = QTranslator()
        self.codeTranslator = QTranslator()
        self.manualStationInfoTranslator = QTranslator()
        self.aboutTranslator = QTranslator()
        self.helpTranslator = QTranslator()
        
        self.mainTranslator.load(mainTranslatorPath)
        self.codeTranslator.load(codeTranslatorPath)
        self.manualStationInfoTranslator.load(manualStationInfoTranslatorPath)
        self.aboutTranslator.load(aboutTranslatorPath)
        self.helpTranslator.load(helpTranslatorPath)
      
        
        QCoreApplication.installTranslator(self.mainTranslator)
        QCoreApplication.installTranslator(self.codeTranslator)
        QCoreApplication.installTranslator(self.manualStationInfoTranslator)
        QCoreApplication.installTranslator(self.aboutTranslator)
        QCoreApplication.installTranslator(self.helpTranslator)
                                    
        # Create the dialog (after translation) and keep reference
        self.dlg = transectizerDialog()
        
        # Signals and slot connections
        
        self.closeButton = self.dlg.ui.buttonBox.button(QDialogButtonBox.Close)
        self.closeButton.pressed.connect(self.dlg.close)
        
        self.dlg.ui.layersCombo.activated.connect(self.checkForTransectizerLayer)
        self.dlg.ui.newTransectButton.clicked.connect(self.newTransect)
        self.dlg.ui.outputToExisting.toggled.connect(self.populateLayersCombo)
        self.dlg.ui.autoNameCheck.toggled.connect(self.autoNamingToggled)
        
        self.dlg.ui.autoTransectCheck.toggled.connect(self.autoTransectToggled)
        self.dlg.ui.GPSButton.clicked.connect(self.getCoordsFromGPS)
        
        self.dlg.ui.buttonBox.helpRequested.connect(self.about)
       
        
        self.dlg.ui.toolBox.currentChanged.connect(self.activateClickTool)
        self.dlg.visibilityChanged.connect(self.dockClosed)
        
        # Initial variables and states which must be set
        self.finalLat = 0
        self.finalLon = 0
        
        self.firstSelectedPoint = False
        self.secondSelectedPoint = False

        self.autoTransect = False
        self.autoNaming = True
        self.existMarkers = False
        
    def dockClosed(self, visible):
        """
        Unsets Transectizer's maptool and clean the screen 
        from markers
        Parameteres:
            visible: Boolean which states if Transectizer widget
                     is visible, or not.
        """
        if not visible:

            self.canvas.unsetMapTool(self.clickTool)
            self.destroyMarkers()
    
    def autoDefineTransect(self, startPoint, endPoint, bearing):
        """
        In the case of Automatic Transect Definition, this functions
        gets the coordinates and bearing that the clicktool emitted,
        draws the markers and the rubberdband and sets the inital 
        point coordinates in the gui for further processing.
        
        """
        # First we set the bearing
        self.dlg.ui.bearing.setValue(bearing)
        
        # Now we set the coordinates in the lineedits, draw
        # the rubberband and set the positions of the markers.
        # Coordinatesar properly transformed to project CRS
        
        projectSrsEntry = QgsProject.instance().readEntry("SpatialRefSys", "/ProjectCRSProj4String")
        projectSrs = QgsCoordinateReferenceSystem()
        projectSrs.createFromProj4(projectSrsEntry[0])
        wgs84 = QgsCoordinateReferenceSystem(4326)
        transfromFromWgs84 = QgsCoordinateTransform(wgs84, projectSrs)
        start = transfromFromWgs84.transform(startPoint)
        end = transfromFromWgs84.transform(endPoint)
        
        self.dlg.ui.startLat.setValue(start.y())
        self.dlg.ui.startLon.setValue(start.x())
        
        self.rubberBand.reset()
        self.rubberBand.addPoint(start)
        self.rubberBand.addPoint(end)
        
        self.initialPoint.setCenter(start)
        self.initialPoint.show()
        
        self.finalPoint.setCenter(end)
        self.finalPoint.show()
        
        
    def activateClickTool(self, index):
        """
        Enables the point selection tool only if the second tab
        (transect definition) is active. In all other cases, it 
        is disabled so no accidental chages are made and the
        mouse cursor is the standard.
        Parameters:
            index: Tab of the QToolBox currently active
        """
        if (index == 1) and (self.autoTransect):
            self.autoTransectToggled(True)
        else:
            self.clickTool.tabChange=True
            self.canvas.unsetMapTool(self.clickTool)
        self.clickTool.alreadyStarted = False
        self.firstSelectedPoint = False
        
        
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
            self.finalLat = point.y()
            self.finalLon = point.x()
            self.secondSelectedPoint = True
                
        # Updates and draws the position of the initial point.
        if not self.firstSelectedPoint:
           
            self.destroyMarkers()
            self.createMarkers()
            self.initialPoint.setCenter(point)
            self.initialPoint.show()
            self.firstSelectedPoint = True
            
    def createMarkers(self):
        """
        Creates the markers objects for initial and final point
        of the transect as well as the rubberband which shows
        the transect being designed when automatic transect
        definition is enabled
        """
        self.existMarkers = True
        self.initialPoint = QgsVertexMarker(self.canvas)
        self.initialPoint.hide()
        
        self.finalPoint = QgsVertexMarker(self.canvas)
        self.finalPoint.setIconType(QgsVertexMarker.ICON_BOX)
        self.finalPoint.hide()
        
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Line)
        self.rubberBand.setColor(Qt.green)
        self.rubberBand.setWidth(2)
        
    def destroyMarkers(self):
        """
        Destroys the markers and rubberband
        """
        if self.existMarkers:
            self.canvas.scene().removeItem(self.finalPoint)
            self.canvas.scene().removeItem(self.initialPoint)
            self.canvas.scene().removeItem(self.rubberBand)
    
    def resetFirstPoint(self):
        """
        Resets the lineEdit widgets for the initial point, as
        well as the calculated bearing
        """
        self.dlg.ui.startLat.setValue(0)
        self.dlg.ui.startLon.setValue(0)
        self.dlg.ui.bearing.clear()
        self.firstSelectedPoint = False
    
    def resetSecondPoint(self):
        """
        Resets the variables for the coordinates of 
        the final point, as well as the calculated bearing
        """
        self.finalLat = 0
        self.finalLon = 0
        self.dlg.ui.bearing.clear()
        self.secondSelectedPoint = False
    
    
    def getCoordsFromGPS(self):
        """This function grabs coordinates for the initial point
        of the transect if there is one available GPS connection
        """

        # First we get the connectionRegistry
        connectionRegistry = QgsGPSConnectionRegistry().instance()

        # Now the connections list from that registry instance
        connectionList = connectionRegistry.connectionList()
              
        if connectionList:
            
            # Time for getting, extracting and transforming the GPS
            # data and pass it to the clicktool to fake first click
            # and continue with the transect definition
            
            GPSInfo = connectionList[0].currentGPSInformation()
            
            projectSrsEntry = QgsProject.instance()\
                .readEntry("SpatialRefSys", "/ProjectCRSProj4String")
            projectSrs = QgsCoordinateReferenceSystem()
            projectSrs.createFromProj4(projectSrsEntry[0])
            wgs84 = QgsCoordinateReferenceSystem(4326)
            transfromFromWgs84 = QgsCoordinateTransform(self.wgs84, projectSrs)
    
            lon = GPSInfo.longitude
            lat = GPSInfo.latitude
            mapPoint = QgsPoint(lon, lat)
            
            self.firstSelectedPoint = True
            
            # We need to transform the point received from
            # the GPS to canvas coordinates to pass it to the 
            # clickTool. If we have automatic definition, the click
            # tool will take care of them. If not, we just need to set
            # the coordinates in the gui but in SRS coordinates, so
            # we need to transform them
            
            if self.autoTransect:
                
                mapUnitsPerPixel = self.canvas.mapUnitsPerPixel()
                transformer = QgsMapToPixel(mapUnitsPerPixel)
                canvasPoint = transformer.transform(lon, lat) 
                # Finally we call the appropiate method of clickTool to
                # set the initial point of the transect
                self.clickTool.setFirstPoint(mapPoint, canvasPoint)
                            
            else:
                
                mapCoordinates = transfromFromWgs84.transform(mapPoint)
                self.dlg.ui.startLat.setValue(mapCoordinates.y())
                self.dlg.ui.startLon.setValue(mapCoordinates.x())
            
        else:
            msg = QMessageBox()
            msg.setText(self.tr("<center>Sorry, no GPS connection available</center>"))
            msg.exec_()
        
    def initGui(self):
        
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/icon.png"), u"Transectizer", self.iface.mainWindow())
        # Connect the action to the run method
        self.action.triggered.connect(self.run)
    
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu(u"&Transectizer", self.action)
        self.iface.digitizeToolBar().addAction(self.action)
        
        #Populate existing layers combobox iwth layer list
        self.populateLayersCombo()
        
        # Creation of coordinate transform object from project SRS to WGS84
        projectSrsEntry = QgsProject.instance().readEntry("SpatialRefSys",\
            "/ProjectCRSProj4String")
        projectSrs = QgsCoordinateReferenceSystem()
        projectSrs.createFromProj4(projectSrsEntry[0])
        self.wgs84 = QgsCoordinateReferenceSystem(4326)
        self.transformToWgs84 = QgsCoordinateTransform(projectSrs, self.wgs84)
        self.transfromFromWgs84 = QgsCoordinateTransform(self.wgs84, projectSrs)
        
        #Add dlg to dock area
        self.iface.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self.dlg)
        

    def unload(self):
        
        # Remove the plugin menu item and icon
        self.dlg.close()
        self.iface.mainWindow().removeDockWidget(self.dlg)
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
        Parameters:
            isAutoNamingChecked: Boolean which states if Automatic
            station info checkbox is checked or not
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
        Parameters:
            isAutoTransectChecked: Boolean which states if Automatic
            transect design checkbox is checked or not
        """
        # Manual transect creation
        if not isAutoTransectChecked:
            
            self.dlg.ui.startLat.setEnabled(True)
            self.dlg.ui.startLon.setEnabled(True)
            self.clickTool.iniPointSelected.disconnect(self.resetFirstPoint)
            self.clickTool.iniPointSelected.disconnect(self.resetSecondPoint)
            self.clickTool.endPointSelected.disconnect(self.resetSecondPoint)
            self.clickTool.iniPointSelected.disconnect(self.autoDefineTransect)
            self.clickTool.endPointSelected.disconnect(self.autoDefineTransect)
            self.clickTool.movingCanvas.disconnect(self.autoDefineTransect)
            self.destroyMarkers()
            self.firstSelectedPoint = True
            self.secondSelectedPoint = True
            self.canvas.unsetMapTool(self.clickTool)
            self.autoTransect = False
            return
        # Automatic transect creation: 
        else:
            
            self.dlg.ui.startLat.setEnabled(False)
            self.dlg.ui.startLon.setEnabled(False)
            self.clickTool.iniPointSelected.connect(self.resetFirstPoint)
            self.clickTool.iniPointSelected.connect(self.resetSecondPoint)
            self.clickTool.endPointSelected.connect(self.resetSecondPoint)
            self.createMarkers()
            self.clickTool.iniPointSelected.connect(self.autoDefineTransect)
            self.clickTool.endPointSelected.connect(self.autoDefineTransect)
            self.clickTool.movingCanvas.connect(self.autoDefineTransect)
            self.canvas.setMapTool(self.clickTool)
            self.autoTransect = True
            return           
    
    def newTransect(self):
        """
        Draws and stores the points for the transect, making the
        appropiate checks for all to work properly.
        """
        
        # Transformation between project SRS and WGS84
        projectSrsEntry = QgsProject.instance().readEntry("SpatialRefSys",\
            "/ProjectCRSProj4String")
        projectSrs = QgsCoordinateReferenceSystem()
        projectSrs.createFromProj4(projectSrsEntry[0])
        wgs84 = QgsCoordinateReferenceSystem(4326)
        transformToWgs84 = QgsCoordinateTransform(projectSrs, self.wgs84)
        transfromFromWgs84 = QgsCoordinateTransform(self.wgs84, projectSrs)
             
        # Gets the values for the main calculations:
        # Bearing, initial latitude, initial longitude
        # and creates a QgsPoint with them
        brg = self.dlg.ui.bearing.value()
        lat = self.dlg.ui.startLat.value()
        lon = self.dlg.ui.startLon.value()
        startPoint = QgsPoint(lon, lat)
        
        # Gets the transect definition parameters
        # and transforms the distance between stations
        # to meters to perform calculations properly
        unit = self.dlg.ui.unitsCombo.currentIndex()
        dst =  self.dlg.ui.dstBtwnStations.value()
        numberOfStations = self.dlg.ui.numberOfStations.value()
        
        if unit == 0:
            dst = dst  #Meters, no conversion at all
        elif unit == 1:
            dst = dst * 1000.0 #Kilometers    
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
            layerName = self.dlg.ui.newLayerName.text()
            if len(layerName.strip(' ')) > 0:
                layer = self.createTransectizerLayer(layerName)
            else:
                msg = QMessageBox()
                msg.setText(self.tr("""<center>New layer name is
                    empty.<br>Please provide one for the layer to be created</center>"""))
                msg.exec_()
                return
                
        else:
            # Otherwise, we must check if the selected layer
            # is appropiate for working with Transectizer.
            # If not, the called function will offer the user
            # the possibility to enable the selected layer for
            # working with Transectizer creating the needed attributes.
            layer = self.checkForTransectizerLayer(selectedByCombo = False)
        
        # If after all we have a working layer, we start the station deployment
        if layer:
            
            startPoint = transformToWgs84.transform(startPoint)
            lat = startPoint.y()
            lon = startPoint.x()
            stations = []
            nlat = lat
            nlon = lon        
            layer.startEditing()
            featureCount = int(layer.featureCount()) 
            layerFields = layer.dataProvider().fields()
            
            # Here themanual naming dialog is instantiated even if
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
                    # (***) Maybe this is the place to create the
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
                point = QgsPoint(nlon, nlat)
                
                # Adding the new feature to the layer
                feature = QgsFeature(layerFields)
                feature.setGeometry(QgsGeometry.fromPoint(point))
                
                feature.setAttribute(layer.fieldNameIndex('id'),\
                    station + featureCount)
                feature.setAttribute(layer.fieldNameIndex('survey'),\
                    transectSurvey)
                feature.setAttribute(layer.fieldNameIndex('station'),\
                    stationName)
                feature.setAttribute(layer.fieldNameIndex('stnnum'),\
                    stationNumber)
                feature.setAttribute(layer.fieldNameIndex('stnlat'),\
                    point.y())
                feature.setAttribute(layer.fieldNameIndex('stnlon'),\
                    point.x())
                feature.setAttribute(layer.fieldNameIndex('stnobs'),\
                    stationObs)

                layer.addFeature(feature, True)
                # Now the departure point for the next iteration is calculated
                nlat, nlon, nbrg = self.vinc_pt(1/298.257223563, 6378137.0,\
                    lat, lon,brg,dst * (station + 1))
            
            # When all stations are deployed, changes ar commited
            # and canvas refresed
            layer.commitChanges()
            layer.triggerRepaint()
            
            # We clean the canvas from markers and transect linededit
            self.destroyMarkers()
            
            
    def run(self):
        
        self.dlg.show()
 
    
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
              "Point?crs=epsg:4326&field=id:integer&field=survey:string(20)&field=station:string(10)&field=stnnum:integer&field=stnlat:double&field=stnlon:double&field=stnobs:string(254)&index=yes",
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
        station:(string, 10): A short descriptive prefix/name for the stations.
        stnnum(int): Sequential/arbitrary number for the station.
        stnlat(double): Latitude, , in decimal degrees, for the station.
        stnlon(double): Longitude, in decimal degrees, for the station.
        stnobs(string, 254): Observations/remarks for the station.
        
        Checking a layer is done field by field, against a field list
        """
        
        # Creating the list of fields to be compared
        surveyField = QgsField(name = 'survey', type = 10,\
            typeName = 'string', len = 20)
        stationField = QgsField(name = 'station', type = 10,\
            typeName = 'string', len = 10)
        stnnumField = QgsField(name = 'stnnum', type =2,\
            typeName = 'integer', len = 10, prec = 0)
        stnlatField = QgsField(name = 'stnlat', type = 6,\
            typeName = 'double', len = 20, prec = 5)
        stnlonField = QgsField(name = 'stnlon', type = 6,\
            typeName = 'double', len = 20, prec = 5)
        stnobsField = QgsField(name = 'stnobs', type = 10,\
            typeName = 'string', len = 254)
        
        fieldList = (surveyField, stationField, stnnumField,\
            stnlatField, stnlonField, stnobsField)
        
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
                msg.setText(self.tr("<center>%s is a valid layer<br>for Transectizer to work<center>" %layerName))
                msg.exec_()
            return layer
        # If not, we offer the user the chance
        # of creating them in the chosen layer
        else:
            msg.setText(self.tr("""<center>It looks like the selected layer<br>
                has not the fields required for Transectizer to work.<br>
                Do you want them to be added to your layer?<center>"""))
            btn1 = msg.addButton(self.tr("Add and continue"), QMessageBox.YesRole)
            btn2 = msg.addButton(self.tr("Cancel"), QMessageBox.NoRole)
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
        Parameters:
        ===========
            f: flattening of the ellipsoid
            a: radius of the ellipsoid, meteres
            phil: latitude of the start point, decimal degrees
            lembda1: longitude of the start point, decimal degrees
            alpha12: bearing, decimal degrees
            s: Distance to endpoint, meters
        NOTE: This code could have some license issues. It has been obtained 
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
            
        phi2 = math.atan2 ( (math.sin(U1) * math.cos(sigma) +\
            math.cos(U1) * math.sin(sigma) * math.cos(alpha12) ), \
            ((1-f) * math.sqrt( math.pow(Sinalpha, 2) +  \
            pow(math.sin(U1) * math.sin(sigma) - math.cos(U1) * \
            math.cos(sigma) * math.cos(alpha12), 2)))) 
            
        lembda = math.atan2( (math.sin(sigma) * math.sin(alpha12 )),\
            (math.cos(U1) * math.cos(sigma) -  \
            math.sin(U1) *  math.sin(sigma) * math.cos(alpha12))) 
            
        C = (f/16) * cosalpha_sq * (4 + f * (4 - 3 * cosalpha_sq )) 
        omega = lembda - (1-C) * f * Sinalpha *  \
            (sigma + C * math.sin(sigma) * (math.cos(two_sigma_m) + \
            C * math.cos(sigma) * (-1 + 2 *\
            math.pow(math.cos(two_sigma_m), 2) ))) 

        lembda2 = lembda1 + omega 
        alpha21 = math.atan2 ( Sinalpha, (-math.sin(U1) * \
            math.sin(sigma) +
            math.cos(U1) * math.cos(sigma) * math.cos(alpha12))) 

        alpha21 = alpha21 + two_pi / 2.0 
        if ( alpha21 < 0.0 ) : 
            alpha21 = alpha21 + two_pi 
        if ( alpha21 > two_pi ) : 
            alpha21 = alpha21 - two_pi 

        phi2 = phi2 * 45.0 / piD4 
        lembda2 = lembda2 * 45.0 / piD4 
        alpha21 = alpha21 * 45.0 / piD4 
        
        return phi2, lembda2, alpha21 

    def about(self):
        """
        This function just shows the About/help dialog
        """
        aboutDialog().exec_()
        

class clickTool(QgsMapToolEmitPoint):
    """
    This class provides a clicktool which, once selected a
    start point clicking on the canvas, draws a rubberband
    showing a line until the mouse button is released. It
    also is capable of showing the bearing while editing
    in QGIS mouse pointer
    """   
    iniPointSelected = pyqtSignal(QgsPoint, QgsPoint, float)
    endPointSelected = pyqtSignal(QgsPoint, QgsPoint, float)
    movingCanvas = pyqtSignal(QgsPoint, QgsPoint, float)
    
    def __init__(self, canvas,iface):
        
        # Initialzation of the tool. We need to keep some references
        # both to canvas and iface to work on cursors and statusbar
        # later on
        self.canvas = canvas
        self.iface = iface
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        
        self.startPointCursor = QCursor(QPixmap(':/cursors/startCursor.png'))
        self.endPointCursor = QCursor(QPixmap(':/cursors/dragCursor.png'))
        
        self.normalCursor = QCursor(0)
        self.prevMapTool = None
        self.alreadyStarted = False
        self.clickToFinish = False
        self.tabChange = False
        self.reset()
        self.cursor = QCursor()
        
        self.msgBar = self.iface.messageBar()
  
    
    def calculateBearing(self, startPoint, endPoint):
        """
        Calculates the bearing between two points. This calculation
        needs the points to have its coordinates in degrees
        """
        startLat = math.radians(startPoint.y())
        startLon = math.radians(startPoint.x())
        endLat = math.radians(endPoint.y())
        endLon = math.radians(endPoint.x())
            
        deltaLon = endLon - startLon
        y = math.sin(deltaLon) * math.cos(endLat)
        x = math.cos(startLat) * math.sin(endLat) - math.sin(startLat) *\
            math.cos(endLat) * math.cos(deltaLon)
        bearing = (5 * math.pi / 2) - math.atan2(x, y)
        bearing = round( math.degrees(bearing), 1) % 360
        return bearing
        
    def reset(self):
        
        # Resets the tool
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.clickToFinish = False
        self.alreadyStarted = False
        
        
    def activate(self):
        
        self.parent().setCursor(self.startPointCursor)
        msg = self.msgBar.createMessage(\
            self.tr("<b>TRANSECTIZER:</b> Click canvas to set first point, drag mouse to set bearing"))
        self.msgBar.pushWidget(msg, QgsMessageBar.INFO, 0)
              
    def deactivate(self):
        
        self.msgBar.clearWidgets()
                
    
    def setFirstPoint(self,mapPoint,canvasPoint):
        """
        This function makes possible to programatically pass a point as
        initial point, simulating a MouseEvent
        """
        
        self.reset()
        self.alreadyStarted = True
        self.passedPoint = mapPoint
        
        cvPoint = QPoint(canvasPoint.x(), canvasPoint.y())
        simuClick = QMouseEvent(QEvent.MouseButtonPress, cvPoint,\
            Qt.LeftButton, Qt.LeftButton, Qt.NoModifier,)
        self.canvasPressEvent(simuClick)
    
    def canvasPressEvent(self, e):
        """
        Clicks on the canvas cause the tool to be reset and
        the rubberband initialized. The signal iniPointSelected
        is emitted and isEmittingPoint is set to True, so the tool
        starts to draw the rubberband. If self.alreadyStarted is set
        to True, means that the first point has been set by other ,
        so the wignal will not be emmited
        """
        
        if not self.alreadyStarted: # Means that we have a true click
            
            # Reset the clickTool and set the cursor
            self.reset()
            self.parent().setCursor(self.endPointCursor)
            
            # Some messaging to guide the user
            self.msgBar.clearWidgets()
            msg = self.msgBar.createMessage(self.tr("<b>TRANSECTIZER:</b> Check bearing with cursor, release button when done"))
            self.msgBar.pushWidget(msg, QgsMessageBar.WARNING, 0)
            
            # We get the canvas position and we transform it to WGS84
            start = self.toMapCoordinates(e.pos())
            projectSrsEntry = QgsProject.instance().readEntry("SpatialRefSys", "/ProjectCRSProj4String")
            projectSrs = QgsCoordinateReferenceSystem()
            projectSrs.createFromProj4(projectSrsEntry[0])
            wgs84 = QgsCoordinateReferenceSystem(4326)
            transformToWgs84 = QgsCoordinateTransform(projectSrs,wgs84)
            self.startPoint = transformToWgs84.transform(start)
            
        else: # We've recived the position programatically
            
            # Some messaging to guide the user
            self.msgBar.clearWidgets()
            msg = self.msgBar.createMessage(\
                self.tr("<b>TRANSECTIZER:</b> Check bearing with cursor, left click when done"))
            self.msgBar.pushWidget(msg, QgsMessageBar.WARNING, 0)
            
            # Our start point is the point passed 
            # to clicktool when setFirstPoint was called
            self.startPoint = self.passedPoint
            
            # If we got the points programatically, it means that 
            # we finish the transect definition clicking on the canvas
            # rather than releasing the button, so we won't emit the
            # point in this case: time to return!!
            if self.clickToFinish:
                self.parent().setCursor(self.startPointCursor)
                self.alreadyStarted = False
                return
        
            self.clickToFinish = True
        
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.iniPointSelected.emit(self.startPoint, self.endPoint,0)
        return

    def canvasReleaseEvent(self, e):
        """
        When the user releases the button,the signal endPointSelected
        is emitted and self.isEmittingPoint is set to True. Also, sets
        alreadyStarted to false.
        """
        
        if not self.alreadyStarted:
            self.parent().setCursor(self.startPointCursor)
            self.msgBar.clearWidgets()
            msg = self.msgBar.createMessage(\
                self.tr("<b>TRANSECTIZER:</b> Click canvas to set first point, drag mouse to set bearing"))
            self.msgBar.pushWidget(msg, QgsMessageBar.INFO, 0)
            self.isEmittingPoint = False
            end = self.toMapCoordinates(e.pos())
            projectSrsEntry = QgsProject.instance()\
                .readEntry("SpatialRefSys", "/ProjectCRSProj4String")
            projectSrs = QgsCoordinateReferenceSystem()
            projectSrs.createFromProj4(projectSrsEntry[0])
        
            wgs84 = QgsCoordinateReferenceSystem(4326)
            transformToWgs84 = QgsCoordinateTransform(projectSrs, wgs84)
            endPoint = transformToWgs84.transform(end)
            bearing = self.calculateBearing(self.startPoint, endPoint)
            self.endPointSelected.emit(self.startPoint, endPoint, bearing)
            
        else:
            
            self.clickToFinish = True
            return
        
    def canvasMoveEvent(self, e):
        """
        When isEmittingPoint is True (set by canvasPressEvent),
        the signal movingCanvas is emitted with the initial and end
        point of the rubberband and also the rubberBand is updated.
        The bearing of the rubberband is calculated and shown in
        the cursor.
        """
        if self.isEmittingPoint:
                       
            # Bearing calculation: The bearing is obtained 
            # in azimuth and radians and must be
            # transformed to degrees and bearing
            # TODO: Change cursor size depending on
            # screen resolution and/or system
            
            endPoint = self.toMapCoordinates(e.pos())
            
            projectSrsEntry = QgsProject.instance().\
                readEntry("SpatialRefSys", "/ProjectCRSProj4String")
            projectSrs = QgsCoordinateReferenceSystem()
            projectSrs.createFromProj4(projectSrsEntry[0])
            wgs84 = QgsCoordinateReferenceSystem(4326)
            transformToWgs84 = QgsCoordinateTransform(projectSrs, wgs84)
            transfromFromWgs84 = QgsCoordinateTransform(wgs84, projectSrs)
            
            start = self.startPoint
            end = transformToWgs84.transform(endPoint)
            bearing = self.calculateBearing(start, end)
            
            # Fancy cursor with bearing drawn over it
            # First a simple crosshair pixmap is loaded and a 
            # QPainter object is created over it, so drawing 
            # the bearing text over the pixmap is possible
            
            # First we load the pixmap
            self.cursorPix = QPixmap(":/cursors/cursorBRG.png")
            
            #We create the painter
            cursorPainter = QPainter(self.cursorPix)
            
            #Now we draw the texts over the pixmap
            
            font = QFont()
            font.setPixelSize(8)
            cursorPainter.setFont(font)
            
            cursorPainter.drawText(0, 0, 32, 32, Qt.AlignHCenter, str('BRG'))
            font.setPixelSize(10)
            cursorPainter.setFont(font)
            cursorPainter.drawText(0, 22, 32, 32, Qt.AlignHCenter,\
                str('%.1f' %bearing))
            
            # And finally, we assign our pixmap to the tool's parent
            # (the underlying canvas) cursor
            
            self.cursor = QCursor(self.cursorPix)
            self.parent().setCursor(self.cursor)
            self.movingCanvas.emit(start, end, bearing)
            