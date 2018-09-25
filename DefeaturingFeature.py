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

'''
This Script includes python Features to represent Defeaturing Operations
'''
class ViewProviderTree:
    "A generic View Provider for Elements with Children"
        
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object
        
    def attach(self, obj):
        self.Object = obj.Object
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self,obj):
        modes=[]
        return modes

    def setDisplayMode(self,mode):
        return mode

    def onChanged(self, vp, prop):
        return

    def __getstate__(self):
#        return {'ObjectName' : self.Object.Name}
        return None

    def __setstate__(self,state):
        if state is not None:
            import FreeCAD
            doc = FreeCAD.ActiveDocument #crap
            self.Object = doc.getObject(state['ObjectName'])

    def claimChildren(self):
        objs = []
        if hasattr(self.Object.Proxy,"Base"):
            objs.append(self.Object.Proxy.Base)
        if hasattr(self.Object,"Base"):
            objs.append(self.Object.Base)
        if hasattr(self.Object,"Objects"):
            objs.extend(self.Object.Objects)
        if hasattr(self.Object,"Components"):
            objs.extend(self.Object.Components)
        if hasattr(self.Object,"Children"):
            objs.extend(self.Object.Children)

        return objs
   
    def getIcon(self):
        import dft_locator, os
        #import osc_locator, os
        DefeaturingWB_icons_path =  os.path.join( os.path.dirname(dft_locator.__file__), 'Resources', 'icons')
        if isinstance(self.Object.Proxy,DefeatShape):
            return(os.path.join(DefeaturingWB_icons_path,'DefeaturingParametric.svg'))
        
##
class DefeatShape:
    '''return a refined shape'''
    def __init__(self, fc, obj, child=None):
        obj.addProperty("App::PropertyLink","Base","Base",
                        "The base object that must be defeatured")
        obj.Proxy = self
        obj.Base = child
        obj.addProperty("App::PropertyStringList","Faces","dFaces",
                        "List of Faces to be defeatured")
        #print(fc)
        obj.Faces = fc

    def onChanged(self, fp, prop):
        "Do something when a property has changed"
        pass

    def execute(self, fp):
        import OpenSCADUtils, FreeCAD, FreeCADGui, Part
        doc = FreeCAD.ActiveDocument
        docG = FreeCADGui.ActiveDocument
        if fp.Base and fp.Base.Shape.isValid():
            #print (fp.Faces)
            # rh_faces_names -> (selFace.ObjectName+'.'+selFace.SubElementNames[i])
            d_faces=[]
            for fn in fp.Faces:
                oname = fn.split('.')[0]
                fnbr = int(fn.split('.')[1].strip('Face'))-1
                o = doc.getObject(oname)
                for i, f in enumerate (o.Shape.Faces):
                    if i == fnbr:
                        #print (i)
                        d_faces.append(f)
                        #print (f.hashCode())
            sh = fp.Base.Shape.defeaturing(d_faces)
            if fp.Base.Shape.isPartner(sh):
                FreeCAD.Console.PrintError('Defeaturing failed\n')
            fp.Shape=OpenSCADUtils.applyPlacement(sh)
            docG.ActiveObject.ShapeColor  =  docG.getObject(fp.Base.Name).ShapeColor
            docG.ActiveObject.LineColor   =  docG.getObject(fp.Base.Name).LineColor
            docG.ActiveObject.PointColor  =  docG.getObject(fp.Base.Name).PointColor
            docG.ActiveObject.DiffuseColor=  docG.getObject(fp.Base.Name).DiffuseColor
            docG.ActiveObject.Transparency=  docG.getObject(fp.Base.Name).Transparency
##

