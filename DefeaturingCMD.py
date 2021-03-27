# -*- coding: utf-8 -*-
#****************************************************************************
#*                                                                          *
#*  Kicad STEPUP (TM) (3D kicad board and models to STEP) for FreeCAD       *
#*  3D exporter for FreeCAD                                                 *
#*  Kicad STEPUP TOOLS (TM) (3D kicad board and models to STEP) for FreeCAD *
#*  Copyright (c) 2015                                                      *
#*  Maurice easyw@katamail.com                                              *
#*                                                                          *
#*  Kicad STEPUP (TM) is a TradeMark and cannot be freely usable            *
#*                                                                          *

import FreeCAD, FreeCADGui, Part, os
import imp, os, sys, tempfile
import FreeCAD, FreeCADGui
from PySide import QtGui, QtCore
import dft_locator


try:
    from PathScripts.PathUtils import horizontalEdgeLoop
    from PathScripts.PathUtils import horizontalFaceLoop
    from PathScripts.PathUtils import loopdetect
except:
    FreeCAD.Console.PrintError('Path WB not found\n')

reload_Gui=False#True

def reload_lib(lib):
    if (sys.version_info > (3, 0)):
        import importlib
        importlib.reload(lib)
    else:
        reload (lib)

DefeaturingWBpath = os.path.dirname(dft_locator.__file__)
DefeaturingWB_icons_path =  os.path.join( DefeaturingWBpath, 'Resources', 'icons')

class DefeatShapeFeature:
    def IsActive(self):
        #print ('isactive')
        if hasattr(Part, "OCC_VERSION"):
            OCCMV = Part.OCC_VERSION.split('.')[0]
            OCCmV = Part.OCC_VERSION.split('.')[1]
            if (int(OCCMV)>= 7) and (int(OCCmV)>= 3):
                sel = FreeCADGui.Selection.getSelectionEx()
                for sub in sel:
                    if 'Face' in str(sub.SubElementNames):
                        return True
        else:
            return False

    def Activated(self):
    #def execute():
        import Part, DefeaturingFeature
        #print ('activated')
        selection=FreeCADGui.Selection.getSelectionEx()
        rh_faces = [];rh_faces_names=[]
        selEx=FreeCADGui.Selection.getSelectionEx()
        if len (selEx) > 0:
            for selFace in selEx:
                for i,f in enumerate(selFace.SubObjects):
                    if 'Face' in selFace.SubElementNames[i]:
                        rh_faces.append(f)
                        rh_faces_names.append(selFace.ObjectName+'.'+selFace.SubElementNames[i])
                        print(selFace.ObjectName+'.'+selFace.SubElementNames[i])
            #print (len(rh_faces))
            for selobj in selection:
                newobj=selobj.Document.addObject("Part::FeaturePython",'defeat')
                DefeaturingFeature.DefeatShape(rh_faces_names,newobj,selobj.Object)
                DefeaturingFeature.ViewProviderTree(newobj.ViewObject)
                newobj.Label='defeat_%s' % selobj.Object.Label
                selobj.Object.ViewObject.hide()
            FreeCAD.ActiveDocument.recompute()
    def GetResources(self):
        return {'Pixmap'  : os.path.join(DefeaturingWB_icons_path,'DefeaturingParametric.svg'), 'MenuText': \
                QtCore.QT_TRANSLATE_NOOP('DefeatShapeFeature',\
                'Defeat Shape Feature'), 'ToolTip': \
                QtCore.QT_TRANSLATE_NOOP('DefeatShapeFeature',\
                'Create Defeat Shape Parametric Feature')}
FreeCADGui.addCommand('DefeatShapeFeature',DefeatShapeFeature())
##

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
class DF_SelectLoop:
    "the Path command to complete loop selection definition"
    def __init__(self):
        self.obj = None
        self.sub = []
        self.active = False

    def GetResources(self):
        return {'Pixmap'  : os.path.join( DefeaturingWB_icons_path , 'Path-SelectLoop.svg') ,
                'MenuText': "Defeaturing_SelectLoop",
                'ToolTip': "Defeaturing SelectLoop"}

    def IsActive(self):
        #if bool(FreeCADGui.Selection.getSelection()) is False:
        #    return False
        if 0: #try:
            sel = FreeCADGui.Selection.getSelectionEx()[0]
            if sel.Object == self.obj and sel.SubElementNames == self.sub:
                return self.active
            self.obj = sel.Object
            self.sub = sel.SubElementNames
            if sel.SubObjects:
                self.active = self.formsPartOfALoop(sel.Object, sel.SubObjects[0], sel.SubElementNames)
            else:
                self.active = False
            return self.active
        return True
        #except Exception as exc:
        #    PathLog.error(exc)
        #    traceback.print_exc(exc)
        #    return False
        
    def Activated(self):
        sel = FreeCADGui.Selection.getSelectionEx()[0]
        obj = sel.Object
        edge1 = sel.SubObjects[0]
        if 'Face' in sel.SubElementNames[0]:
            loop = horizontalFaceLoop(sel.Object, sel.SubObjects[0], sel.SubElementNames)
            if loop:
                FreeCADGui.Selection.clearSelection()
                FreeCADGui.Selection.addSelection(sel.Object, loop)
            loopwire = []
        elif len(sel.SubObjects) == 1:
            loopwire = horizontalEdgeLoop(obj, edge1)
        else:
            edge2 = sel.SubObjects[1]
            loopwire = loopdetect(obj, edge1, edge2)

        if loopwire:
            FreeCADGui.Selection.clearSelection()
            elist = obj.Shape.Edges
            for e in elist:
                for i in loopwire.Edges:
                    if e.hashCode() == i.hashCode():
                        FreeCADGui.Selection.addSelection(obj, "Edge"+str(elist.index(e)+1))

    def formsPartOfALoop(self, obj, sub, names):
        if names[0][0:4] != 'Edge':
            if names[0][0:4] == 'Face' and horizontalFaceLoop(obj, sub, names):
                return True
            return False
        if len(names) == 1 and horizontalEdgeLoop(obj, sub):
            return True
        if len(names) == 1 or names[1][0:4] != 'Edge':
            return False
        return True

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('DF_SelectLoop', DF_SelectLoop())
##
class refineFeatureTool:
    "refine Feature Parametric"
 
    def GetResources(self):
        return {'Pixmap'  : os.path.join( DefeaturingWB_icons_path , 'RefineShapeFeature.svg') , # the name of a svg file available in the resources
                     'MenuText': "refine Feature" ,
                     'ToolTip' : "refine Feature Parametric"}
 
    def IsActive(self):
        if len(FreeCADGui.Selection.getSelection()) > 0:
            return True
 
    def Activated(self):
        import OpenSCADFeatures
        doc=FreeCAD.ActiveDocument
        docG = FreeCADGui.ActiveDocument
        sel=FreeCADGui.Selection.getSelectionEx()
        if len (sel) > 0:
            for selobj in sel:
                if hasattr(selobj.Object,"Shape"):        
                    newobj=selobj.Document.addObject("Part::FeaturePython",'refined')
                    OpenSCADFeatures.RefineShape(newobj,selobj.Object)
                    OpenSCADFeatures.ViewProviderTree(newobj.ViewObject)
                    ## to do: see if it is possible to conserve colors in refining
                    ao = FreeCAD.ActiveDocument.ActiveObject
                    docG.ActiveObject.ShapeColor=docG.getObject(selobj.Object.Name).ShapeColor
                    docG.ActiveObject.LineColor=docG.getObject(selobj.Object.Name).LineColor
                    docG.ActiveObject.PointColor=docG.getObject(selobj.Object.Name).PointColor
                    docG.ActiveObject.DiffuseColor=docG.getObject(selobj.Object.Name).DiffuseColor
                    docG.ActiveObject.Transparency=docG.getObject(selobj.Object.Name).Transparency
                    #newobj.Label='r_%s' % selobj.Object.Label
                    newobj.Label=selobj.Object.Label
                    selobj.Object.ViewObject.hide()
            doc.recompute()
FreeCADGui.addCommand('refineFeatureTool',refineFeatureTool())
##

class FuzzyCut:
    "Fuzzy boolean Cut"
 
    def GetResources(self):
        return {'Pixmap'  : os.path.join( DefeaturingWB_icons_path , 'FuzzyCut.svg') , # the name of a svg file available in the resources
                     'MenuText': "Fuzzy boolean Cut" ,
                     'ToolTip' : "Fuzzy boolean Cut"}
 
    def IsActive(self):
        doc = FreeCAD.ActiveDocument
        if hasattr(Part, "OCC_VERSION"):
            OCCMV = Part.OCC_VERSION.split('.')[0]
            OCCmV = Part.OCC_VERSION.split('.')[1]
            if (int(OCCMV)>= 7) and (int(OCCmV)>= 1):
                #return True
                if len(FreeCADGui.Selection.getSelection()) == 2:
                    return True
        else:
            return False
 
    def Activated(self):
        # do something here...
        import FuzzyTools
        reload_lib(FuzzyTools)
        FuzzyTools.fuzzyCut()
        # FreeCAD.Console.PrintWarning( 'Fuzzy Boolean Tools active :)\n' )
 
FreeCADGui.addCommand('FuzzyCut',FuzzyCut())
##

class FuzzyUnion:
    "Fuzzy boolean Union"
 
    def GetResources(self):
        return {'Pixmap'  : os.path.join( DefeaturingWB_icons_path , 'FuzzyUnion.svg') , # the name of a svg file available in the resources
                     'MenuText': "Fuzzy boolean Union" ,
                     'ToolTip' : "Fuzzy boolean Union"}
 
    def IsActive(self):
        doc = FreeCAD.ActiveDocument
        if hasattr(Part, "OCC_VERSION"):
            OCCMV = Part.OCC_VERSION.split('.')[0]
            OCCmV = Part.OCC_VERSION.split('.')[1]
            if (int(OCCMV)>= 7) and (int(OCCmV)>= 1):
                #return True
                if len(FreeCADGui.Selection.getSelection()) > 1:
                    return True
        else:
            return False

    def Activated(self):
        # do something here...
        import FuzzyTools
        reload_lib(FuzzyTools)
        FuzzyTools.fuzzyUnion()
        # FreeCAD.Console.PrintWarning( 'Fuzzy Boolean Tools active :)\n' )
 
FreeCADGui.addCommand('FuzzyUnion',FuzzyUnion())
##
class FuzzyCommon:
    "Fuzzy boolean Common"
 
    def GetResources(self):
        return {'Pixmap'  : os.path.join( DefeaturingWB_icons_path , 'FuzzyCommon.svg') , # the name of a svg file available in the resources
                     'MenuText': "Fuzzy boolean Common" ,
                     'ToolTip' : "Fuzzy boolean Common"}
 
    def IsActive(self):
        doc = FreeCAD.ActiveDocument
        if hasattr(Part, "OCC_VERSION"):
            OCCMV = Part.OCC_VERSION.split('.')[0]
            OCCmV = Part.OCC_VERSION.split('.')[1]
            if (int(OCCMV)>= 7) and (int(OCCmV)>= 1):
                #return True
                if len(FreeCADGui.Selection.getSelection()) > 1:
                    return True
        else:
            return False

    def Activated(self):
        # do something here...
        import FuzzyTools
        reload_lib(FuzzyTools)
        FuzzyTools.fuzzyCommon()
        # FreeCAD.Console.PrintWarning( 'Fuzzy Boolean Tools active :)\n' )
 
FreeCADGui.addCommand('FuzzyCommon',FuzzyCommon())
##