# -*- coding: utf-8 -*-
#***************************************************************************
#*                                                                          *
#*  Copyright (c) 2017                                                      *
#*  Maurice easyw@katamail.com                                              *
#*                                                                          *
#                                                                           *
# Defeaturing WB                                                            *
#                                                                           *
#  (C) Maurice easyw-fc 2018                                                *
#    This program is free software; you can redistribute it and/or modify   *
#    it under the terms of the GNU Library General Public License (LGPL)    *
#    as published by the Free Software Foundation; either version 2 of      *
#    the License, or (at your option) any later version.                    *
#    for detail see the LICENCE text file.                                  *
#****************************************************************************

DWB_wb_version='v 1.1.2'
global myurlDWB
myurlDWB='https://github.com/easyw/Defeaturing_WB'
global mycommitsDWB
mycommitsDWB=34 #v 1.1.2


import FreeCAD, FreeCADGui, Part, os, sys
import re, time

if (sys.version_info > (3, 0)):  #py3
    import urllib
    from urllib import request, error #URLError, HTTPError
else:  #py2
    import urllib2
    from urllib2 import Request, urlopen, URLError, HTTPError
    
import dft_locator
from DefeaturingCMD import *

DefeaturingWBpath = os.path.dirname(dft_locator.__file__)
DefeaturingWB_icons_path =  os.path.join( DefeaturingWBpath, 'Resources', 'icons')

global main_DWB_Icon
main_DWB_Icon = os.path.join( DefeaturingWB_icons_path , 'Defeaturing-icon.svg')


#try:
#    from FreeCADGui import Workbench
#except ImportError as e:
#    FreeCAD.Console.PrintWarning("error")
    
class DefeaturingWB ( Workbench ):
    global main_DWB_Icon, DWB_wb_version
    
    "Defeaturing WB object"
    Icon = main_DWB_Icon
    #Icon = ":Resources/icons/kicad-StepUp-tools-WB.svg"
    MenuText = "Defeaturing WB"
    ToolTip = "Defeaturing workbench"
 
    def GetClassName(self):
        return "Gui::PythonWorkbench"
    
    def Initialize(self):
        
        self.appendToolbar("Defeaturing Tools", ["DefeaturingTools","DF_SelectLoop"])
        
        #self.appendMenu("ksu Tools", ["ksuTools","ksuToolsEdit"])
        self.appendMenu("Defeaturing Tools", ["DefeaturingTools","DF_SelectLoop"])
        
        Log ("Loading Defeaturing Module... done\n")
 
    def Activated(self):
                # do something here if needed...
        Msg ("Defeaturing WB Activated("+DWB_wb_version+")\n")
        from PySide import QtGui
        import time
        

    def Deactivated(self):
                # do something here if needed...
        Msg ("Defeaturing WB Deactivated()\n")
    
###

FreeCADGui.addWorkbench(DefeaturingWB)
