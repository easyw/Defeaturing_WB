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

import dft_locator, os
DefeaturingWBpath = os.path.dirname(dft_locator.__file__)
DefeaturingWB_icons_path =  os.path.join( DefeaturingWBpath, 'Resources', 'icons')
global defeat_icon, use_cm
defeat_icon=os.path.join(DefeaturingWB_icons_path,'DefeaturingParametric.svg')
use_cm = True

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

    def getIcon(self):
        #import osc_locator, os
        global defeat_icon
        if isinstance(self.Object.Proxy,DefeatShape):
            #print (defeat_icon)
            # try: 
            #     if self.upd: return (defeat_icon)
            # except: pass
            return(defeat_icon)

    def updateData(self, fp, prop):
        #print (fp.Label)
        #if fp.Label.find('_ERR') != -1:
        #    fp.touch()
        #    #import FreeCAD
        #    #doc = FreeCAD.ActiveDocument
        #    #doc.getObject(fp.Name).touch()
        #    print('touched')
        #self.getIcon()
        #try: self.upd
        #except: self.upd=True
        #self.upd=not self.upd
        #print('update')
        return

    def getDisplayModes(self,obj):
        modes=[]
        return modes

    def setDisplayMode(self,mode):
        return mode

    def onChanged(self, vp, prop):
        #self.getIcon()
        #print (prop)
        #self.getIcon()
        #print('change')
        return

    def __getstate__(self):
#        return {'ObjectName' : self.Object.Name}
        return None

    def __setstate__(self,state):
        if state is not None:
            import FreeCAD
            doc = FreeCAD.ActiveDocument #crap
            self.Object = doc.getObject(state['ObjectName'])

    # dumps and loads replace __getstate__ and __setstate__ post v. 0.21.2
    def dumps(self):
        return None

    def loads(self, state):
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
   

##
class DefeatShape:
    '''return a refined shape'''
    def __init__(self, fc, obj, child=None):
        
        global use_cm
        import FreeCAD
        doc = FreeCAD.ActiveDocument
        obj.addProperty("App::PropertyLink","Base","Base",
                        "The base object that must be defeatured")
        obj.Proxy = self
        obj.Base = child
        obj.addProperty("App::PropertyStringList","Faces","dFaces",
                        "List of Faces to be defeatured")
        obj.Faces = fc
        if use_cm:
            obj.addProperty("App::PropertyStringList","CM","dFaces",
                            "Center of Mass")
            #print(fc)
            cm = []
            for f in fc:    
                oname = obj.Base.Name #f.split('.')[0]
                o = doc.getObject(oname)
                fnbr = int(f.split('.')[1].strip('Face'))-1
                mf = o.Shape.Faces[fnbr]
                cm.append('x='+"{0:.3f}".format(mf.CenterOfMass.x)+' y='+"{0:.3f}".format(mf.CenterOfMass.y)+' z='+"{0:.3f}".format(mf.CenterOfMass.z))
            obj.CM = cm
            obj.addProperty("App::PropertyBool","useFaceNbr","dFaces",
                            "use Face Number")
        
    def onChanged(self, fp, prop):
        "Do something when a property has changed"
        import FreeCAD
        doc = FreeCAD.ActiveDocument
        d_faces=[]
        #print (prop,' changed')
        if (prop == 'useFaceNbr' or prop == 'Shape') and len (fp.Base.Shape.Faces) > 0:
            #print (fp.useFaceNbr)
            if fp.useFaceNbr: #not use_cm:
                cm_list=[]
                for fn in fp.Faces:
                    oname = fp.Base.Name #fp.Faces[0].split('.')[0]
                    fnbr = int(fn.split('.')[1].strip('Face'))-1
                    o = doc.getObject(oname)
                    for i, f in enumerate (o.Shape.Faces):
                        if i == fnbr:
                            #print (i)
                            d_faces.append(f)
                            c='x='+"{0:.3f}".format(f.CenterOfMass.x)+' y='+"{0:.3f}".format(f.CenterOfMass.y)+' z='+"{0:.3f}".format(f.CenterOfMass.z)
                            cm_list.append(c)
                            #print (c)
                            #print(fp.CM)
                            #print (f.CenterOfMass)
                            #print (f.hashCode())
                    fp.CM = cm_list        
            else:
                #print(fp.Base.Shape.Faces)
                if len (fp.Base.Shape.Faces) > 0:
                #if fp.Base.Shape.isValid():
                    fc = []
                    #fc.append(fp.Faces[0])
                    for i, c in enumerate(fp.CM):
                        for j, f in enumerate (fp.Base.Shape.Faces):
                                if c ==('x='+"{0:.3f}".format(f.CenterOfMass.x)+' y='+"{0:.3f}".format(f.CenterOfMass.y)+' z='+"{0:.3f}".format(f.CenterOfMass.z)):
                                    d_faces.append(f)
                                    #print (f.CenterOfMass)
                                    fc.append(str(fp.Base.Name)+'.'+'Face'+str(j+1))
                    fp.Faces = fc
                else:
                    print('loading first time')
            #doc.recompute()
        pass

    def execute(self, fp):
        global defeat_icon, use_cm
        import OpenSCADUtils, FreeCAD, FreeCADGui, Part, os
        doc = FreeCAD.ActiveDocument
        docG = FreeCADGui.ActiveDocument
        #print(fp.Base.Shape.Faces)
        #if 0: #
        if len (fp.Faces) > 0:
            if fp.Base and fp.Base.Shape.isValid():
                #print (fp.Faces)
                # rh_faces_names -> (selFace.ObjectName+'.'+selFace.SubElementNames[i])
                d_faces=[]
                if fp.useFaceNbr: #not use_cm:
                    cm_list=[]
                    for fn in fp.Faces:
                        oname = fp.Base.Name #fp.Faces[0].split('.')[0]
                        fnbr = int(fn.split('.')[1].strip('Face'))-1
                        o = doc.getObject(oname)
                        for i, f in enumerate (o.Shape.Faces):
                            if i == fnbr:
                                #print (i)
                                d_faces.append(f)
                                c='x='+"{0:.3f}".format(f.CenterOfMass.x)+' y='+"{0:.3f}".format(f.CenterOfMass.y)+' z='+"{0:.3f}".format(f.CenterOfMass.z)
                                cm_list.append(c)
                                #print (c)
                                #print(fp.CM)
                                #print (f.CenterOfMass)
                                #print (f.hashCode())
                        fp.CM = cm_list
                else:
                    oname = fp.Base.Name #fp.Faces[0].split('.')[0]
                    o = doc.getObject(oname)
                    fc = []
                    #fc.append(fp.Faces[0])
                    for i, c in enumerate(fp.CM):
                        for j, f in enumerate (fp.Base.Shape.Faces):
                                if c ==('x='+"{0:.3f}".format(f.CenterOfMass.x)+' y='+"{0:.3f}".format(f.CenterOfMass.y)+' z='+"{0:.3f}".format(f.CenterOfMass.z)):
                                    d_faces.append(f)
                                    #print (f.CenterOfMass)
                                    fc.append(str(o.Name)+'.'+'Face'+str(j+1))
                #fp.Faces = fc
                check_faces = True
                if not fp.useFaceNbr: #use_cm:
                    if len (d_faces) != len (fp.CM):
                        check_faces = False
                elif len (d_faces) == 0:
                    check_faces = False
                if check_faces:
                    sh = fp.Base.Shape.defeaturing(d_faces)
                    if fp.Base.Shape.isPartner(sh):
                        #fp.touch()
                        FreeCAD.Console.PrintError('Defeaturing failed 1\n')
                        #defeat_icon=os.path.join(DefeaturingWB_icons_path,'error.svg')
                        defeat_icon=os.path.join(DefeaturingWB_icons_path,'DefeaturingParametric.svg')
                        docG.getObject(fp.Name).ShapeColor  =  (1.00,0.00,0.00)
                        raise NameError('Defeaturing FAILED!')
                        #try:
                        #    raise NameError('Defeaturing FAILED!')
                        #except NameError:
                        #    print ('Defeaturing FAILED!')
                        #    raise
                        #raise Exception('Defeaturing FAILED!')
                    else:
                        fp.Shape=OpenSCADUtils.applyPlacement(sh)
                        if fp.Label.find('_ERR') != -1:
                            fp.Label=fp.Label[:fp.Label.rfind('_ERR')]
                        defeat_icon=os.path.join(DefeaturingWB_icons_path,'DefeaturingParametric.svg')
                        docG.getObject(fp.Name).ShapeColor  =  docG.getObject(fp.Base.Name).ShapeColor
                        docG.getObject(fp.Name).LineColor   =  docG.getObject(fp.Base.Name).LineColor
                        docG.getObject(fp.Name).PointColor  =  docG.getObject(fp.Base.Name).PointColor
                        docG.getObject(fp.Name).DiffuseColor=  docG.getObject(fp.Base.Name).DiffuseColor
                        docG.getObject(fp.Name).Transparency=  docG.getObject(fp.Base.Name).Transparency
                else:
                    #defeat_icon=os.path.join(DefeaturingWB_icons_path,'error.svg')
                    defeat_icon=os.path.join(DefeaturingWB_icons_path,'DefeaturingParametric.svg')
                    #fp.touch()
                    FreeCAD.Console.PrintError('Defeaturing failed 2\n')
                    sh = fp.Base.Shape
                    fp.Shape=OpenSCADUtils.applyPlacement(sh)
                    if fp.Label.find('_ERR') == -1:
                        fp.Label='%s_ERR' % fp.Label
                    docG.getObject(fp.Name).ShapeColor  =  (1.00,0.00,0.00)
                    raise Exception('Defeaturing FAILED!')
                #doc.recompute()
        else:
            print('first executing')
##

## class UnionFuzzyShape:
##     '''return a fuzzy unioned shape'''
##     def __init__(self, compNames, obj, child=None):
##         #obj.addProperty("App::PropertyLink","Base","Base",
##         #                "The base object that must be fuzzy unioned")
##         obj.addProperty("App::PropertyStringList","Components","Components",
##                         "List of Objects to be fuzzy unioned")
##         obj.Proxy = self
##         obj.Base = child
##         obj.Components = compNames
## 
##     def onChanged(self, fp, prop):
##         "Do something when a property has changed"
##         pass
## 
##     def execute(self, fp):
##         if len (fp.Components) > 1:
##             makeOp=True
##             for name in fp.Components:
##                 if not doc.getObject(name).Shape.isValid():
##                     makeOp=False
##             if makeOp:
##                 import OpenSCADUtils, FuzzyTools
##                 #sh=fp.Base.Shape.removeSplitter()
##                 ### do my ops
##                 result_shape = FuzzyTools.fuzzyUnion()
##                 fp.Shape=OpenSCADUtils.applyPlacement(result_shape)
## 
