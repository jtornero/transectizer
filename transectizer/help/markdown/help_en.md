Transectizer
============

Transectizer is a QGIS plugin which provides an easy way to **design linear transects** with sampling stations distributed at a given distance along the transect.

Transectizer makes possible to **automatically generate each individual station details** (transect name, station name, station number) or have control over all the attributes of each station.

**You can store your transects** in a new layer or provide an existing layer for it. In that case, Transectizer will make the appropiate changes to your layer to make it compatible with Transectizer.

Copyright/License
=================

Transectizer has been developed by Jorge Tornero.

(C) 2013, 2014 Jorge Tornero, http://imasdemase.com

Transectizer is released under the terms of the

**GNU GENERAL PUBLIC LICENSE**

Version 3, 29 June 2007


This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see:

**http://www.gnu.org/licenses**

Donations/Fees
==============

Of course, no donations or fees are required for Transectizer to work... but if you feel that Transectizer has improved you life in any way, you can make a small donation to a NGO/Charity of your choice. Donate to QGIS project is a nice idea, too, providing that nothing of this is possible without QGIS.

Additionally, if you really feel in the mood of rewarding me, just send me a postcard from where you live. I'll be proud of showing it to my kid. Feel free of contact me through jtorlistas//at//gmail.com

Things to be aware of
=====================

Transectizer positions the stations using <a href="http://en.wikipedia.org/wiki/Vincenty's_formulae" target="_blank">Vincenty's direct formula</a>, using the WGS84 ellipsoid to perform the calculations. They are made feeding Vincenty's formula with the same inital point but different destination distances. These distances are the *n-multiples* of the the distance between stations, being *n* the number of the station to be deployed. But another approach could be to fix the distance but move the point for calculation: First point should be the start point, second point is calculated from first, third from the second, and so on. Providing that these two approaches render different results, if you feel that either the calculation proceeding I've chosen is wrong or you think that the two methods should be available for the user to choose, please contact me. I'll be glad to modify Transectizer in the best possible way.

The reference for T. Vincenty's work is:

    Vincenty, T., (1975) Direct and inverse solutions on the ellipsoid
    with application of nested equations, Survey Review, Vol. 23, No. 176, pp. 88-93.

Usage
=====

The basic operation of Transectizer is pretty simple: You choose a point layer to operate, define your transect line, set the distance between the stations to be deployed and the number of them and that's all... Transectizer will add each station as a new feature into your layer.

Transectizer dialog is organized into three separate tabs: One for choosing the layer where Transectizer will do its work, another for the definition of the transenct and a last one for providing station details.

Choosing the layer
------------------

![Alt text](./choosing_layer.png "Choosing layer in Transectizer")

This part of Transectizer's main dialog if self-explicative, but there are some caveats to be aware of:

1) When choosing a existing layer, Transectizer will check if the chosen layer has the attributes that Transectizer needs to work:

- A *survey* string field with length 20.
- A *station* string field with length 20.
- A *stnnum* integer field.
- A *stnlat* double field.
- A *stnlon* double field.If 
- A *stnobs* string field with length 254.

If your chosen layer doesn't have those attributes, you will be
asked for creating them inside your layer or cancel the operation.

2) **When creating a new layer, it will be created as a memory layer**, so it is mandatory to save to a file if you want to keep your information.

Defining the transect
---------------------

![Alt text](./transect_definition.png "Defining the transect in Transectizer")

This tab of the dialog makes possible to define the line along which the stations are going to be deployed (Yessss, that's the transect!!!)

You will define your transect providing an initial point for it, a bearing for the line and a distance between the stations, plus a distance unit. For this to be accomplished, Transectizer provides two modes of operation:

**1) Automatic transect definition:** You must check the Automatic definition checkbox to enter this mode. Click the canvas to set the initial point of yor transect and drag the mouse. Pay attention to the mouse pointer, which provides the current bearing of your transect line. Release the mouse button when appropiate and the start point and bearing of the transect will be defined.

In any moment of the automatic transect definition, pay attention to QGIS status bar on top of the canvas, which will give you hints about the proccess.

The automatic transect definition tools are only available when the transect definition tab is active.

**2) Manual transect definition (default):** Type/check in the X/Lon Y/Lat spinboxes the coordinates of your initial point. **You must provide the coordinates in the same CRS than your project.** Set/type the bearing of the transect in the bearing spinbox and you are done.

If you have a GPS connection available, you can set your current coordinates as initial point for your transect, just pressing the button 'Get from GPS'.

After defining the transect line, you have to provide the distance between stations, choose its units in the units combobox and the number of stations to be deployed. Available units so far are, for convenience, meters, kilometers, feet, yards, miles and nautical miles. If you want to use another multiple/submultiple, set the appropiate value in the distance betweeb stations spinbox. For instance, if you want to deploy stations/sampling points every centimeter, you can just type/set 0.01 and choose meters.

Station details
---------------
![Alt text](./station_details.png "Providing stations details in Transectizer")

Each of the stations deployed may have some information associated. A transectizer enabled layer has as least several attributes, as depicted in *Choosing the layer* section above. Transectizer has two operation modes that give the user some control and customization over the information stored with the stations. You can choose the operation mode by checking/unchecking the checkbox *Automatic details* in the Station details & go!!! tab in Transectizer dialog.

**1) Automatic details (default):** With this operation mode, you will be able provide a fixed survey/station name, an station prefix and an initial station number **for all the stations**. No observations/remarks are allowed in this case, and the station number will be increased sequentially. However, you can choose where to begin the sequence by setting its initial value in the *initial station number* spinbox.

**2) Manual details:** When creating the transect, you will be offered with a dialog like this: 

![Alt text](./manual_naming.png "Manual stations details in Transectizer")

Here, you gain total control over station attributes. You can provide a custom transect/survey name, station prefix, station number and observation for each of the deployed stations. You can fix those variables as you wish and even make the station number sequential. For instance, if you want to keep the same transect/survey name for all the deployed stations but change every station prefix, you can check the Fix checkbox besides the Transect name line edit and it will be kept for the subsequent stations. This can be useful, i.e. if you want to deploy a single transect but you want to do different things in odd stations and even stations.

With manual details, also, **you can provide observations/remarks for each station** if you want to.

**Please bear in mind that this dialog will pop-up for all and every of the stations that you deploy, so if you design a transect with relatively high number of stations, it can be very tedious!!!**

Creating the transect
---------------------
After all steps above are done, you must press over *Create new transect* button to create a new transect into the layer that you have selected before. You can create as many transects as you wish in the same layer.

