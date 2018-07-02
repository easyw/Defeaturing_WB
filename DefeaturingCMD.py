# -*- coding: utf-8 -*-
#****************************************************************************
#*                                                                          *
#*  Kicad STEPUP (TM) (3D kicad board and models to STEP) for FreeCAD       *
#*  3D exporter for FreeCAD                                                 *
#*  Kicad STEPUP TOOLS (TM) (3D kicad board and models to STEP) for FreeCAD *
#*  Copyright (c) 2015                                                      *
#*  Maurice easyw@katamail.com                                              *
#*                                                                          *
#*  Kicad STEPUP (TM) is a TradeMark and cannot be freely useable           *
#*                                                                          *

import FreeCAD,FreeCADGui
import FreeCAD, FreeCADGui, Part, os
import imp, os, sys, tempfile
import FreeCAD, FreeCADGui
from PySide import QtGui
import dft_locator

reload_Gui=False#True

def reload_lib(lib):
    if (sys.version_info > (3, 0)):
        import importlib
        importlib.reload(lib)
    else:
        reload (lib)

DefeaturingWBpath = os.path.dirname(dft_locator.__file__)
DefeaturingWB_icons_path =  os.path.join( DefeaturingWBpath, 'Resources', 'icons')



class DefeaturingTools:
    "defeaturing tools object"
 
    def GetResources(self):
        return {'Pixmap'  : os.path.join( DefeaturingWB_icons_path , 'defeaturingTools.svg') , # the name of a svg file available in the resources
                     'MenuText': "Defeaturing Tools" ,
                     'ToolTip' : "Defeaturing workbench"}
 
    def IsActive(self):
        import os, sys
        return True
 
    def Activated(self):
        # do something here...
        import DefeaturingTools
        reload_lib(DefeaturingTools)
        FreeCAD.Console.PrintWarning( 'Defeaturing Tools active :)\n' )
        #import kicadStepUptools
 
FreeCADGui.addCommand('DefeaturingTools',DefeaturingTools())
##
