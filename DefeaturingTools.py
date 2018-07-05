#!/usr/bin/python
# -*- coding: utf-8 -*-
#****************************************************************************
#*                                                                          *
#*  Copyright (c) 2017                                                      *
#*  Maurice easyw@katamail.com                                              *
#*                                                                          *
#                                                                           *
#   Repair Defeaturing Macro                                 *
#                                                                           *
#  (C) Maurice easyw-fc 2018                                               *
#    This program is free software; you can redistribute it and/or modify   *
#    it under the terms of the GNU Library General Public License (LGPL)    *
#    as published by the Free Software Foundation; either version 2 of      *
#    the License, or (at your option) any later version.                    *
#    for detail see the LICENCE text file.                                  *
#****************************************************************************


import FreeCAD, FreeCADGui, Draft, Part
import re, os, sys
import OpenSCADCommands, OpenSCAD2Dgeom, OpenSCADFeatures
from PySide import QtCore, QtGui
import tempfile

#int(re.search(r'\d+', string1).group())

global rh_edges, rh_faces, rh_obj
global rh_edges_names, rh_faces_names, rh_obj_name
global created_faces, rh_faces_indexes, rh_edges_to_connect
global force_recompute, invert

__version__ = "v1.1.5"

invert = True
rh_edges = []
rh_edges_names = []
rh_edges_to_connect = []
rh_faces = []
rh_faces_names = []
rh_faces_indexes = []
created_faces = []
rh_obj = []
rh_obj_name = []
force_recompute = False #True

def mk_str(input):
    if (sys.version_info > (3, 0)):  #py3
        if isinstance(input, str):
            return input
        else:
            input =  input.encode('utf-8')
            return input
    else:  #py2
        if type(input) == unicode:
            input =  input.encode('utf-8')
            return input
        else:
            return input
##
def i_say(msg):
    FreeCAD.Console.PrintMessage(msg)
    FreeCAD.Console.PrintMessage('\n')

def i_sayw(msg):
    FreeCAD.Console.PrintWarning(msg)
    FreeCAD.Console.PrintWarning('\n')
    
def i_sayerr(msg):
    FreeCAD.Console.PrintError(msg)
    FreeCAD.Console.PrintWarning('\n')
##
        
def check_TypeId_RH():
    if FreeCADGui.Selection.getSelection():
        sel=FreeCADGui.Selection.getSelection()

        if len(sel)<1:
                msg="Select one or more object(s) to be checked!\n"
                reply = QtGui.QMessageBox.information(None,"Warning", msg)
                FreeCAD.Console.PrintWarning(msg)             
        else:
            non_solids=''
            solids=''
            for o in sel:
                if hasattr(o,"Shape"):
                    if '.[compsolid]' in o.Label or '.[solid]' in o.Label or '.[shell]' in o.Label\
                            or '.[compound]' in o.Label or '.[face]' in o.Label or '.[edge]' in o.Label:
                        o.Label=mk_str(o.Label).replace('.[solid]','').replace('.[shell]','').replace('.[compsolid]','').replace('.[compound]','')\
                                               .replace('.[face]','').replace('.[edge]','')
                    else:
                        if len(o.Shape.Solids)>0:
                            i_say(mk_str(o.Label)+' Solid object(s) NBR : '+str(len(o.Shape.Solids)))
                            solids+=mk_str(o.Label)+'<br>'
                            if '.[solid]' not in o.Label:
                                o.Label=mk_str(o.Label)+'.[solid]'
                        else:
                            i_sayerr(mk_str(o.Label)+' object is a NON Solid')
                            non_solids+=mk_str(o.Label)+'<br>'
                        if len(o.Shape.Shells)>0:
                            i_say(mk_str(o.Label)+' Shell object(s) NBR : '+str(len(o.Shape.Shells)))
                            if '.[shell]' not in o.Label and '.[solid]' not in o.Label:
                                o.Label=mk_str(o.Label)+'.[shell]'
                        if len(o.Shape.Compounds)>0:
                            i_say(mk_str(o.Label)+' Compound object(s) NBR : '+str(len(o.Shape.Compounds)))
                            if '.[compound]' not in o.Label and '.[solid]' not in o.Label and '.[shell]' not in o.Label:
                                o.Label=mk_str(o.Label)+'.[compound]'
                        if len(o.Shape.CompSolids)>0:
                            i_say(mk_str(o.Label)+' CompSolids object(s) NBR : '+str(len(o.Shape.CompSolids)))
                            if '.[compsolid]' not in o.Label and '.[solid]' not in o.Label and '.[shell]' not in o.Label\
                                and '.[compound]' not in o.Label and '.[face]' not in o.Label and '.[edge]' not in o.Label:
                                o.Label=mk_str(o.Label)+'.[compsolid]'
                        if len(o.Shape.Faces)>0:
                            i_say(mk_str(o.Label)+' Face object(s) NBR : '+str(len(o.Shape.Faces)))
                            if '.[compsolid]' not in o.Label and '.[solid]' not in o.Label and '.[shell]' not in o.Label\
                                and '.[compound]' not in o.Label and '.[face]' not in o.Label and '.[edge]' not in o.Label:
                                o.Label=mk_str(o.Label)+'.[face]'
                        if len(o.Shape.Edges)>0:
                            i_say(mk_str(o.Label)+' Edge object(s) NBR : '+str(len(o.Shape.Edges)))
                            if '.[compsolid]' not in o.Label and '.[solid]' not in o.Label and '.[shell]' not in o.Label\
                                and '.[compound]' not in o.Label and '.[face]' not in o.Label and '.[edge]' not in o.Label:
                                o.Label=mk_str(o.Label)+'.[edge]'
                        
                else:
                    FreeCAD.Console.PrintWarning("Select object with a \"Shape\" to be checked!\n")
            # if len (non_solids)>0:
            #     reply = QtGui.QMessageBox.information(None,"Warning", 'List of <b>NON Solid</b> object(s):<br>'+non_solids)
            # if len (solids)>0:
            #     reply = QtGui.QMessageBox.information(None,"Info", 'List of <b>Solid</b> object(s):<br>'+solids)
    else:
        #FreeCAD.Console.PrintError("Select elements from dxf imported file\n")
        reply = QtGui.QMessageBox.information(None,"Warning", "Select one or more object(s) to be checked!")
        FreeCAD.Console.PrintWarning("Select one or more object(s) to be checked!\n")             

def clear_all_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect

    rh_edges = []
    rh_edges_names = []
    rh_edges_to_connect = []
    created_faces = []
    RHDockWidget.ui.TE_Edges.setPlainText("")
    rh_faces = []
    rh_faces_names = []
    rh_faces_indexes = []
    created_faces = []
    RHDockWidget.ui.TE_Faces.setPlainText("")
    rh_obj = []
    rh_obj_name = []    
    RHDockWidget.ui.Edge_Nbr.setText("0")
    RHDockWidget.ui.Face_Nbr.setText("0")
    RHDockWidget.ui.Obj_Nbr.setText("0")
    RHDockWidget.ui.Obj_Nbr_2.setText("0")   
##
def refine_parametric_RH():
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
                #docG.getObject(newobj.Name).ShapeColor=docG.getObject(selobj.Object.Name).ShapeColor
                #docG.getObject(newobj.Name).LineColor=docG.getObject(selobj.Object.Name).LineColor
                #docG.getObject(newobj.Name).PointColor=docG.getObject(selobj.Object.Name).PointColor
                #newobj.Label='r_%s' % selobj.Object.Label
                newobj.Label=selobj.Object.Label
                selobj.Object.ViewObject.hide()
        doc.recompute()
##
def refine_RH():
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    sel=FreeCADGui.Selection.getSelection()
    if len (sel):
        for o in sel:
            if hasattr(o,"Shape"):
                doc.addObject('Part::Feature','refined').Shape=o.Shape.removeSplitter()
                doc.ActiveObject.Label=o.Label
                docG.getObject(o.Name).hide()                
                docG.ActiveObject.ShapeColor=docG.getObject(o.Name).ShapeColor
                docG.ActiveObject.LineColor=docG.getObject(o.Name).LineColor
                docG.ActiveObject.PointColor=docG.getObject(o.Name).PointColor
                doc.recompute()
##
def edges_clear_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect

    rh_edges = []
    rh_edges_names = []
    rh_edges_to_connect = []
    created_faces = []
    RHDockWidget.ui.TE_Edges.setPlainText("")
    rh_faces = []
    rh_faces_names = []
    rh_faces_indexes = []
    created_faces = []
    RHDockWidget.ui.TE_Faces.setPlainText("")
    rh_obj = []
    rh_obj_name = []    
    RHDockWidget.ui.Edge_Nbr.setText("0")
    RHDockWidget.ui.Face_Nbr.setText("0")
##

def faces_clear_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect

    rh_faces = []
    rh_faces_names = []
    rh_faces_indexes = []
    created_faces = []
    RHDockWidget.ui.TE_Faces.setPlainText("")
    rh_edges = []
    rh_edges_names = []
    rh_edges_to_connect = []
    created_faces = []
    rh_obj = []
    rh_obj_name = []
    RHDockWidget.ui.TE_Edges.setPlainText("")
    RHDockWidget.ui.Edge_Nbr.setText("0")
    RHDockWidget.ui.Face_Nbr.setText("0")
##

def close_RH():
    """closing dialog"""
    RHDockWidget.deleteLater()

def merge_selected_faces_RH():
    """merging Faces of selected shapes""" 
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    
    #af_faces = []
    af_faces = rh_faces
    #print rh_faces
    #faces = []
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    #rh_edges = []; rh_edges_names = []; created_faces = []
    #rh_edges_to_connect = []
    # af_faces = [];af_faces_names = []
    # selEx=FreeCADGui.Selection.getSelectionEx()
    # if len (selEx):
    #     for selFace in selEx:
    #         for i,f in enumerate(selFace.SubObjects):
    #         #for e in selEdge.SubObjects
    #             if 'Face' in selFace.SubElementNames[i]:
    #                 af_faces.append(f)
    #                 af_faces_names.append(selFace.SubElementNames[i])
    #                 print(selFace.SubElementNames[i])
    if len(af_faces) > 0:
        #print af_faces
        try:
            _ = Part.Shell(af_faces)
            if _.isNull():
            #raise RuntimeError('Failed to create shell')
                FreeCAD.Console.PrintWarning('Failed to create shell\n')
        except:
            FreeCAD.Console.PrintWarning('Failed to create shell\n')
            for f in af_faces:
                Part.show(f)
                doc.ActiveObject.Label="face"
            stop
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            try:
                _.removeSplitter()
            except:
                print ('not refined')
        if _.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
        _=Part.Solid(_)
        if _.isNull(): raise RuntimeError('Failed to create solid')
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            try:
                _.removeSplitter()
            except:
                print ('not refined')
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            doc.addObject('Part::Feature','SolidRefined').Shape=_.removeSplitter()
        else:
            doc.addObject('Part::Feature','Solid').Shape=_
        #App.ActiveDocument.ActiveObject.Label=App.ActiveDocument.mysolid.Label
        mysolidr = doc.ActiveObject
        #original_label = rh_obj.Label
        #if RHDockWidget.ui.checkBox_keep_original.isChecked():
        #    docG.getObject(rh_obj.Name).Visibility=False
        #else:
        #    doc.removeObject(rh_obj.Name)
        #if RHDockWidget.ui.checkBox_Refine.isChecked():
        #    mysolidr.Label = original_label + "_refined"
##
    
    
def merge_faces_from_selected_objects_RH():
    """merging Faces of selected shapes""" 
    
    faces = []
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    
    sel=FreeCADGui.Selection.getSelection()
    if len (sel):
        for o in sel:
            for f in o.Shape.Faces:
                faces.append(f) 
        #print faces
        try:
            _ = Part.Shell(faces)
            if _.isNull():
            #raise RuntimeError('Failed to create shell')
                FreeCAD.Console.PrintWarning('Failed to create shell\n')
        except:
            FreeCAD.Console.PrintWarning('Failed to create shell\n')
            for f in faces:
                Part.show(f)
                doc.ActiveObject.Label="face"
            stop
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            try:
                _.removeSplitter()
            except:
                print ('not refined')
        if _.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
        _=Part.Solid(_)
        if _.isNull(): raise RuntimeError('Failed to create solid')
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            try:
                _.removeSplitter()
            except:
                print ('not refined')
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            doc.addObject('Part::Feature','SolidRefined').Shape=_.removeSplitter()
        else:
            doc.addObject('Part::Feature','Solid').Shape=_
        #App.ActiveDocument.ActiveObject.Label=App.ActiveDocument.mysolid.Label
        mysolidr = doc.ActiveObject
        #original_label = rh_obj.Label
        if RHDockWidget.ui.checkBox_keep_original.isChecked():
            for o in sel:
                docG.getObject(o.Name).Visibility=False
        else:
            for o in sel:
                doc.removeObject(o.Name)
        #if RHDockWidget.ui.checkBox_Refine.isChecked():
        #    mysolidr.Label = original_label + "_refined"
##

def edges_confirmed_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    
    #close_RH()
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    #rh_edges = []; rh_edges_names = []; created_faces = []
    #rh_edges_to_connect = []
    en = None
    selEx=FreeCADGui.Selection.getSelectionEx()
    if len (selEx):
        for selEdge in selEx:
            for i,e in enumerate(selEdge.SubObjects):
            #for e in selEdge.SubObjects
                if 'Edge' in selEdge.SubElementNames[i]:
                    edge_in_list = False
                    for en in rh_edges_names:
                        if en == selEdge.ObjectName+'.'+selEdge.SubElementNames[i]:
                            edge_in_list =True
                    if not edge_in_list:
                        rh_edges.append(e)
                        rh_edges_names.append(selEdge.ObjectName+'.'+selEdge.SubElementNames[i])
                        rh_obj.append(selEdge.Object)
                        rh_obj_name.append(selEdge.ObjectName)
                        if (e.isClosed()):
                            cf=(Part.Face(Part.Wire(e)))
                            created_faces.append(cf)
                            i_say('face created from closed edge')
                            if RHDockWidget.ui.checkBox_keep_faces.isChecked():
                                # _ = Part.Solid(Part.Shell([cf]))
                                # doc.addObject('Part::Feature','Face_Solid').Shape = _
                                # doc.ActiveObject.Label = 'Face_Solid'
                                Part.show(cf)
                                doc.ActiveObject.Label = 'Face'
                                docG.ActiveObject.Visibility=False
                        else:
                            #cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges))
                            #if _.isNull(): raise RuntimeError('Failed to create face')
                            #    App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
                            #del _
                            #w1 = Part.Wire(e)
                            #try:
                            #cf=(Part.Face(w1))
                            #created_faces.append(cf)
                            #if RHDockWidget.ui.checkBox_keep_faces.isChecked():
                            #    Part.show(cf)
                            #    docG.ActiveObject.Visibility=False
                            #except:
                            rh_edges_to_connect.append(e)
                #i_say(re.search(r'\d+', selEdge.SubElementNames[i]).group())
        i_say(selEdge.ObjectName)
        if len (rh_edges_to_connect) >0:
            try:
                #cf=Part.makeFilledFace(Part.Wire(Part.__sortEdges__(rh_edges_to_connect)))
                cf=Part.Face(Part.Wire(Part.__sortEdges__(rh_edges_to_connect)))
                created_faces.append(cf)
                i_say('face created from open edges')
                if RHDockWidget.ui.checkBox_keep_faces.isChecked():
                    Part.show(cf)
                    doc.ActiveObject.Label = 'Face'
                    docG.ActiveObject.Visibility=False
                rh_edges_to_connect = []
            except:
                i_sayerr("make Face failed")
        #rh_obj_name.append(selx.ObjectName)
        #rh_obj.append(selx.Object)
        #for e in rh_edges: # selx.SubObjects:
        #    if (e.isClosed()):
        #        cf=(Part.Face(Part.Wire(e)))
        #        created_faces.append(cf)
        #    else:
        #        rh_edges_to_connect.append(e)
        #eh_edges_grouped = []
        #for e in rh_edges_to_connect:
        #nw_edges=sum((e for e in rh_edges_to_connect),[])
        #print rh_edges_to_connect
        #if len(rh_edges_to_connect) > 0:
        #    f = OpenSCAD2Dgeom.edgestofaces(rh_edges_to_connect)
        #    created_faces.append(f)
        #Part.show(f)
        #sn = doc.ActiveObject
        #fn = sn.Shape.Faces[0]
        #created_faces.append(fn)
        #doc.removeObject(sn.Name)
        if 0:
            try:
                cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges_to_connect))
            #if _.isNull(): raise RuntimeError('Failed to create face')
            #    App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
            #del _
            #w1 = Part.Wire(e)
            #try:
            #cf=(Part.Face(w1))
                created_faces.append(cf)
                if RHDockWidget.ui.checkBox_keep_faces.isChecked():
                    Part.show(Part.makeSolid(Part.makeShell(cf)))
                    docG.ActiveObject.Visibility=False
                rh_edges_to_connect = []
            except:
                print('edge outline not closed')
        print ('To Do: collect connected edges to create a Wire')
        e_list=""
        for e in rh_edges_names:
            e_list=e_list+str(e)+'\n'
        RHDockWidget.ui.TE_Edges.setPlainText(e_list)
        RHDockWidget.ui.Edge_Nbr.setText(str(len(rh_edges)))
        unique_obj = set(rh_obj)
        unique_obj_count = len(unique_obj)
        RHDockWidget.ui.Obj_Nbr.setText(str(unique_obj_count))
        for ob in FreeCAD.ActiveDocument.Objects:
            FreeCADGui.Selection.removeSelection(ob)
##
def faces_confirmed_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    
    doc=FreeCAD.ActiveDocument
    #rh_faces = []; rh_faces_names = []
    selEx=FreeCADGui.Selection.getSelectionEx()
    selEx=FreeCADGui.Selection.getSelectionEx()
    #fn = None
    if len (selEx):
        for selFace in selEx:
            for i,f in enumerate(selFace.SubObjects):
            #for e in selEdge.SubObjects
                if 'Face' in selFace.SubElementNames[i]:
                    face_in_list = False
                    for fn in rh_faces_names:
                        if fn == selFace.ObjectName+'.'+selFace.SubElementNames[i]:
                            face_in_list =True
                    #if len (rh_faces_names) == 0:
                    #    fn = selFace.ObjectName+'.'+selFace.SubElementNames[i]
                    if not face_in_list:
                        rh_faces.append(f)
                        rh_faces_indexes.append (re.search(r'\d+',selFace.SubElementNames[i]).group())
                        rh_faces_names.append(selFace.ObjectName+'.'+selFace.SubElementNames[i])
                        rh_obj.append(selFace.Object)
                        rh_obj_name.append(selFace.ObjectName)
                    #af_faces.append(f)
                    #af_faces_names.append(selFace.Object+'.'+selFace.SubElementNames[i])
                    print(selFace.ObjectName+'.'+selFace.SubElementNames[i])
        f_list=""
        for f in rh_faces_names:
            f_list=f_list+str(f)+'\n'
        RHDockWidget.ui.TE_Faces.setPlainText(f_list)
        #print(selx.ObjectName)
        #if selx.ObjectName != rh_obj_name:
        #    #raise RuntimeError('ERROR object changed. Please repeat process from the start')
        #    FreeCAD.Console.PrintWarning('object changed\n')
        #    rh_obj = selx.Object
        RHDockWidget.ui.Face_Nbr.setText(str(len(rh_faces)))
        unique_obj = set(rh_obj)
        unique_obj_count = len(unique_obj)
        RHDockWidget.ui.Obj_Nbr_2.setText(str(unique_obj_count))
        for ob in FreeCAD.ActiveDocument.Objects:
            FreeCADGui.Selection.removeSelection(ob)
        
##
def removeHoles_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute, invert
    
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    print('Removing Holes')
    #print rh_edges; print rh_faces; print (rh_obj)
    unique_obj = set(rh_obj)
    unique_obj_count = len(unique_obj)
    if unique_obj_count == 1:
        RHDockWidget.ui.TE_Edges.setPlainText("")
        RHDockWidget.ui.TE_Faces.setPlainText("")
        myshape = rh_obj[0]
        i = 0
        faces = []
        for f in myshape.Shape.Faces:
            i+=1
            idx_found = False
            for j in rh_faces_indexes:
                if int(j) == i:
                    idx_found = True
                    print('index found '+str(j))
            if not idx_found:
                faces.append(f)
        if len(rh_edges_to_connect) > 0:
            if not invert:
                try:
                    print("try to create a Face w/ OpenSCAD2Dgeom")
                    cf = OpenSCAD2Dgeom.edgestofaces(Part.__sortEdges__(rh_edges_to_connect))
                except:
                    print("OpenSCAD2Dgeom failed\ntry to makeFilledFace")
                    cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges_to_connect))
            else:
                try:
                    print("try to makeFilledFace")
                    cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges_to_connect))
                except:
                    print("makeFilledFace failed\ntry to create a Face w/ OpenSCAD2Dgeom")
                    cf = OpenSCAD2Dgeom.edgestofaces(Part.__sortEdges__(rh_edges_to_connect))
            created_faces.append(cf)
            if RHDockWidget.ui.checkBox_keep_faces.isChecked():
                #_ = Part.Solid(Part.Shell([cf]))
                #doc.addObject('Part::Feature','Face_Solid').Shape = _
                #doc.ActiveObject.Label = 'Face_Solid'
                Part.show(cf)
                doc.ActiveObject.Label = 'Face'
                docG.ActiveObject.Visibility=False
            rh_edges_to_connect = []
        if 0:
            for f in created_faces:
                faces.append(f)
            res_faces = []
            _ = Part.Shell(faces)
            if _.isNull(): raise RuntimeError('Failed to create shell')
        _ = Part.Shell(faces)
        if _.isNull(): raise RuntimeError('Failed to create shell')
        _=Part.Solid(_)
        if _.isNull(): raise RuntimeError('Failed to create solid')
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            try:
                _.removeSplitter()
            except:
                print ('not refined')    
        for f in created_faces:
            new_faces = []
            for nf in _.Faces:
                new_faces.append(nf)
            new_faces.append(f)
            del _
            _ = Part.Shell(new_faces)
            i_sayw('added 1 face')
            if _.isNull(): raise RuntimeError('Failed to create shell')
            if RHDockWidget.ui.checkBox_Refine.isChecked():
                try:
                    _.removeSplitter()
                except:
                    print ('not refined')
            if _.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
            _=Part.Solid(_)
            if _.isNull(): raise RuntimeError('Failed to create solid')
            if RHDockWidget.ui.checkBox_Refine.isChecked():
                try:
                    _.removeSplitter()
                except:
                    print ('not refined')
            #doc.recompute()
        #for f in created_faces:
        #    new_faces.append(f)
        #del _
        #_ = Part.Shell(new_faces)
        #if _.isNull(): raise RuntimeError('Failed to create shell')
        
        #App.ActiveDocument.addObject('Part::Feature','Shell').Shape=_
        #if RHDockWidget.ui.checkBox_Refine.isChecked():
        #    try:
        #        _.removeSplitter()
        #    except:
        #        print ('not refined')
        #myshell = doc.ActiveObject
        #del _
            
        #if myshell.Shape.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
        # if _.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
        # _=Part.Solid(_)
        # if _.isNull(): raise RuntimeError('Failed to create solid')
        # if RHDockWidget.ui.checkBox_Refine.isChecked():
        #     try:
        #         _.removeSplitter()
        #     except:
        #         print ('not refined')
        #App.ActiveDocument.addObject('Part::Feature','Solid').Shape=_
        #mysolid = doc.ActiveObject
        #del _
        #doc.removeObject(myshell.Name)
        
        #docG.mysolid.Visibility=True
        #doc.addObject('Part::Feature','SolidRefined').Shape=mysolid.Shape.removeSplitter()
        #doc.removeObject(mysolid.Name)
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            doc.addObject('Part::Feature','SolidRefined').Shape=_.removeSplitter()
        else:
            doc.addObject('Part::Feature','Solid').Shape=_
        #    doc.addObject('Part::Feature','Solid').Shape=_
        #App.ActiveDocument.ActiveObject.Label=App.ActiveDocument.mysolid.Label
        mysolidr = doc.ActiveObject
        original_label = myshape.Label
        if RHDockWidget.ui.checkBox_keep_original.isChecked():
            docG.getObject(myshape.Name).Visibility=False
        else:
            doc.removeObject(myshape.Name)
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            mysolidr.Label = original_label # + "_refined"
        #mysolidr.hide()
        clear_all_RH()
        if force_recompute:
            for obj in FreeCAD.ActiveDocument.Objects:
                obj.touch()
        doc.recompute() 
        print('ToDo Apply colors to corresponding faces') 
    else:
        i_sayerr('select only one object')
##

##
def removeFaces_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute

    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    print('Removing Holes')
    #print rh_edges; print rh_faces; print (rh_obj)
    #ui.TE_Edges.setPlainText("")
    #ui.TE_Faces.setPlainText("")
    
    unique_obj = set(rh_obj)
    unique_obj_count = len(unique_obj)
    if unique_obj_count == 1: #ToDo manage multi objs faces selection
    #for myshape in unique_obj:
        myshape = rh_obj[0]
        i = 0
        faces = []
        for f in myshape.Shape.Faces:
            i+=1
            idx_found = False
            for j in rh_faces_indexes:
                if int(j) == i:
                    idx_found = True
                    print('index found '+str(j))
            if not idx_found:
                faces.append(f)
        if 1:
            try:
                _ = Part.Shell(faces)
                if _.isNull():
                #raise RuntimeError('Failed to create shell')
                    FreeCAD.Console.PrintWarning('Failed to create shell\n')
            except:
                FreeCAD.Console.PrintWarning('Failed to create shell\n')
                if RHDockWidget.ui.checkBox_keep_faces.isChecked():
                    for f in faces:
                        Part.show(f)
                        doc.ActiveObject.Label="face"
                stop
            #App.ActiveDocument.addObject('Part::Feature','Shell').Shape=_
            if RHDockWidget.ui.checkBox_Refine.isChecked():
                try:
                    _.removeSplitter()
                except:
                    print ('not refined')
        #myshell = doc.ActiveObject
        #del _
            
        #if myshell.Shape.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
            if _.ShapeType != 'Shell': raise RuntimeError('Part object is not a shell')
            _=Part.Solid(_)
            if _.isNull(): raise RuntimeError('Failed to create solid')
            if RHDockWidget.ui.checkBox_Refine.isChecked():
                try:
                    _.removeSplitter()
                except:
                    print ('not refined')
            #App.ActiveDocument.addObject('Part::Feature','Solid').Shape=_
            #mysolid = doc.ActiveObject
            #del _
            #doc.removeObject(myshell.Name)
            
            #docG.mysolid.Visibility=True
            #doc.addObject('Part::Feature','SolidRefined').Shape=mysolid.Shape.removeSplitter()
            #doc.removeObject(mysolid.Name)
            if RHDockWidget.ui.checkBox_Refine.isChecked():
                doc.addObject('Part::Feature','SolidRefined').Shape=_.removeSplitter()
            else:
                doc.addObject('Part::Feature','Solid').Shape=_
            #App.ActiveDocument.ActiveObject.Label=App.ActiveDocument.mysolid.Label
        mysolidr = doc.ActiveObject
        original_label = myshape.Label
        if RHDockWidget.ui.checkBox_keep_original.isChecked():
            docG.getObject(myshape.Name).Visibility=False
        else:
            doc.removeObject(myshape.Name)
        if RHDockWidget.ui.checkBox_Refine.isChecked():
            mysolidr.Label = original_label # + "_refined"
        #mysolidr.hide()
        #docG.getObject(mysolidr.Name).Visibility=False
        #rh_edges = []; rh_edges_names = []; created_faces = []
        #rh_edges_to_connect = []
        #rh_faces = []; rh_faces_names = []
        #rh_faces_indexes = []
        #ui.Edge_Nbr.setText("0")
        #ui.Face_Nbr.setText("0")
        #ui.TE_Edges.setPlainText("")
        #ui.TE_Faces.setPlainText("")
        clear_all_RH()
        if force_recompute:
            for obj in FreeCAD.ActiveDocument.Objects:
                obj.touch()
        doc.recompute() 
    print('ToDo Apply colors to corresponding faces') 

##
def addFaces_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute, invert
    
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    if len(rh_edges) > 0:
        #try:
        #    print("try to makeFilledFace")
        #    cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges))
        #except:
        #    print("makeFilledFace failed\ntry to create a Face w/ OpenSCAD2Dgeom")
        #    cf = OpenSCAD2Dgeom.edgestofaces(rh_edges)
        if not invert:
            try:
                print("try to create a Face w/ OpenSCAD2Dgeom")
                cf = OpenSCAD2Dgeom.edgestofaces(rh_edges)
            except:
                print("OpenSCAD2Dgeom failed\ntry to makeFilledFace")
                cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges))
        else:
            try:
                print("try to makeFilledFace")
                cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges))
            except:
                print("makeFilledFace failed\ntry to create a Face w/ OpenSCAD2Dgeom")
                cf = OpenSCAD2Dgeom.edgestofaces(rh_edges)
        #created_faces.append(cf)
        Part.show(cf)
        doc.ActiveObject.Label = "Face"
    #if len(rh_edges_to_connect) > 0:
    #    try:
    #        print("try to makeFilledFace")
    #        cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges_to_connect))
    #    except:
    #        print("makeFilledFace failed\ntry to create a Face w/ OpenSCAD2Dgeom")
    #        cf = OpenSCAD2Dgeom.edgestofaces(rh_edges_to_connect)
    #    #created_faces.append(cf)
    #    Part.show(cf)
    #    doc.ActiveObject.Label = "Face"
    if len(rh_edges) > 0 or len(rh_edges_to_connect) > 0:
        clear_all_RH()
##
def offsetFaces_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute, invert
    
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    if len(rh_faces) > 0:
        for f in rh_faces:
            Part.show(f)
            fname = doc.ActiveObject.Name
            s=doc.ActiveObject.Shape.copy()
            offset_dir = RHDockWidget.ui.offset_input.text().split(':')
            if len(offset_dir)>1:
                offset = float(offset_dir[0])
                if 'x' in offset_dir[1]:
                    norm=FreeCAD.Vector(1,0,0)
                elif 'y'in offset_dir[1]:
                    norm=FreeCAD.Vector(0,1,0)
                elif 'z' in offset_dir[1]:
                    norm=FreeCAD.Vector(0,0,1)
                elif 'n' in offset_dir[1]:
                    norm=f.normalAt(0,0)
                else:
                    i_sayerr('direction not inserted, using norm to face')
                    norm=f.normalAt(0,0)
                    RHDockWidget.ui.offset_input.setText(str(offset)+':n')
            else:
                offset = float(RHDockWidget.ui.offset_input.text())
                i_sayerr('direction not inserted, using norm to face')
                norm=f.normalAt(0,0)
                RHDockWidget.ui.offset_input.setText(str(offset)+':n')
            s.translate(norm*offset)
            doc.removeObject(fname)
            Part.show(s)
            doc.ActiveObject.Label = "Face"
##
def offsetEdges_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute, invert
    
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    if len(rh_edges) > 0:
        for e in rh_edges:
            Part.show(e)
            #norm=doc.ActiveObject.Shape.Faces[0].normalAt(0,0)
            offset_dir = RHDockWidget.ui.offset_input.text().split(':')
            if len(offset_dir)>1:
                offset = float(offset_dir[0])
                if 'x' in offset_dir[1]:
                    norm=FreeCAD.Vector(1,0,0)
                elif 'y'in offset_dir[1]:
                    norm=FreeCAD.Vector(0,1,0)
                elif 'z' in offset_dir[1]:
                    norm=FreeCAD.Vector(0,0,1)
                else:
                    i_sayerr('direction not inserted, using z axis')
                    norm=FreeCAD.Vector(0,0,1)
            else:
                offset = float(RHDockWidget.ui.offset_input.text())
                i_sayerr('direction not inserted, using z axis')
                norm = FreeCAD.Vector(0,0,1)
                RHDockWidget.ui.offset_input.setText(str(offset)+':x')
            fname = doc.ActiveObject.Name
            s=doc.ActiveObject.Shape.copy()
            s.translate(norm*offset)
            doc.removeObject(fname)
            Part.show(s)
            doc.ActiveObject.Label = "Edge"

def copyFaces_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute, invert
    
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    if len(rh_faces) > 0:
        for f in rh_faces:
            Part.show(f)
            doc.ActiveObject.Label = "Face"
    #if len(rh_edges_to_connect) > 0:
    #    try:
    #        print("try to makeFilledFace")
    #        cf=Part.makeFilledFace(Part.__sortEdges__(rh_edges_to_connect))
    #    except:
    #        print("makeFilledFace failed\ntry to create a Face w/ OpenSCAD2Dgeom")
    #        cf = OpenSCAD2Dgeom.edgestofaces(rh_edges_to_connect)
    #    #created_faces.append(cf)
    #    Part.show(cf)
    #    doc.ActiveObject.Label = "Face"
    if len(rh_faces) > 0:
        clear_all_RH()
##

def makeEdge_RH():
    global force_recompute
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    verts = []; verts_names = []
    selEx=FreeCADGui.Selection.getSelectionEx()
    verts = []
    if len (selEx):
        for selV in selEx:
            for i,v in enumerate(selV.SubObjects):
            #for e in selEdge.SubObjects
                if 'Vertex' in selV.SubElementNames[i]:
                    verts.append(v)
                    verts_names.append(selV.SubElementNames[i])
                    print(selV.SubElementNames[i])
    if len(verts) == 2:
        try:
            i_say("try to create an Edge w/ makeLine")
            ce = Part.makeLine(verts[0].Point, verts[1].Point)
            Part.show(ce)
            del ce
            doc.ActiveObject.Label = "Edge"
        except:
            i_sayerr("failed to create a Line")
    else:
        i_sayerr("select only 2 Vertexes")
    for ob in FreeCAD.ActiveDocument.Objects:
        FreeCADGui.Selection.removeSelection(ob)
##
def addEdges_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    #rh_edges = []; rh_edges_names = []; created_faces = []
    #rh_edges_to_connect = []
    ae_edges = rh_edges;ae_edges_names = rh_edges_names
    selEx=FreeCADGui.Selection.getSelectionEx()
    if len (selEx):
        for selEdge in selEx:
            for i,e in enumerate(selEdge.SubObjects):
            #for e in selEdge.SubObjects
                if 'Edge' in selEdge.SubElementNames[i]:
                    ae_edges.append(e)
                    ae_edges_names.append(selEdge.SubElementNames[i])
                    print(selEdge.SubElementNames[i])
    if len(ae_edges) > 0:
        #try:
        #    print("try to makeWire")
        #    ce=Part.Wire(Part.__sortEdges__(ae_edges))
        #except:
        #    print("makeWire failed\ntry to create an Edge w/ OpenSCAD2Dgeom")
        #    ce = Part.Wire(OpenSCAD2Dgeom.edgestowires(ae_edges))
        if not invert:
            try:
                print("try to create an Edge w/ OpenSCAD2Dgeom")
                ce = Part.Wire(OpenSCAD2Dgeom.edgestowires(ae_edges))
                #OpenSCAD2Dgeom.edgestofaces(ae_edges)
            except:
                print("OpenSCAD2Dgeom failed\ntry to makeWire")
                ce=Part.Wire(Part.__sortEdges__(ae_edges))
                #Part.makeFilledFace(Part.__sortEdges__(ae_edges))
        else:
            try:
                print("try to makeWire")
                ce=Part.Wire(Part.__sortEdges__(ae_edges))
            except:
                print("makeWire failed\ntry to create an Edge w/ OpenSCAD2Dgeom")
                ce = OpenSCAD2Dgeom.edgestofaces(ae_edges)
        #created_faces.append(cf)
        Part.show(ce)
        doc.ActiveObject.Label = "Edge"
        if len(rh_edges) > 0:
            clear_all_RH()
##
def showEdges_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument

    for en in rh_edges_names:
        FreeCADGui.Selection.addSelection(doc.getObject(en.split('.')[0]),en.split('.')[1])
        #print (rh_obj[0],' ', en.split('.')[1])
        #FreeCADGui.Selection.addSelection(FreeCAD.ActiveDocument.Box,'Face2',21.0,8.604081153869629,8.553047180175781)

##
def showFaces_RH():
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument

    for fn in rh_faces_names:
        FreeCADGui.Selection.addSelection(doc.getObject(fn.split('.')[0]),fn.split('.')[1])
        #print (rh_obj[0],' ', en.split('.')[1])
        #FreeCADGui.Selection.addSelection(FreeCAD.ActiveDocument.Box,'Face2',21.0,8.604081153869629,8.553047180175781)

##

def PartDefeaturing_RH():
    #pass
    global rh_edges, rh_faces, rh_obj
    global rh_edges_names, rh_faces_names, rh_obj_name
    global created_faces, rh_faces_indexes, rh_edges_to_connect
    global force_recompute
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    
    unique_obj = set(rh_obj)
    unique_obj_count = len(unique_obj)
    if unique_obj_count == 1 and len(rh_faces) >0: #ToDo manage multi objs faces selection
        sh = rh_obj[0].Shape
        #nsh = sh.defeaturing([sh.Face5,])
        i_say(rh_faces)
        nsh = sh.defeaturing(rh_faces)
        if not sh.isPartner(nsh):
                defeat = doc.addObject('Part::Feature','Defeatured').Shape = nsh
                docG.getObject(rh_obj[0].Name).hide()
        else:
                FreeCAD.Console.PrintError('Defeaturing failed\n')
        doc.recompute()
##

def makeSolidExpSTEP_RH():
    
    doc=FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    if doc is not None:
        fname = doc.FileName
        if len(fname) == 0:
            fname='untitled'
        tempdir = tempfile.gettempdir() # get the current temporary directory
        tempfilepath = os.path.join(tempdir,fname + u'.stp')
        sel=FreeCADGui.Selection.getSelection()
        if len (sel) == 1:
            __objs__=[]
            __objs__.append(sel[0])
            import ImportGui
            ImportGui.export(__objs__,tempfilepath)
            del __objs__
            docG.getObject(sel[0].Name).Visibility = False
            ImportGui.insert(tempfilepath,doc.Name)
            FreeCADGui.SendMsgToActiveView("ViewFit")
        else:
            i_sayerr('select only one object')
    else:
        i_sayerr('select only one object')
##    

############################################################################################
# embedded button images
import base64
# "b64_data" is a variable containing your base64 encoded jpeg
closeW_b64=\
"""
PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIKICAgeG1sbnM6c29kaXBvZGk9Imh0dHA6Ly9zb2RpcG9kaS5zb3VyY2Vmb3JnZS5uZXQvRFREL3NvZGlwb2RpLTAuZHRkIgogICB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIKICAgd2lkdGg9IjY0IgogICBoZWlnaHQ9IjY0IgogICBpZD0ic3ZnMiIKICAgdmVyc2lvbj0iMS4xIgogICBpbmtzY2FwZTp2ZXJzaW9uPSIwLjQ4LjUgcjEwMDQwIgogICBzb2RpcG9kaTpkb2NuYW1lPSJlZGl0X0NhbmNlbC5zdmciCiAgIHZpZXdCb3g9IjAgMCA2NCA2NCI+CiAgPGRlZnMKICAgICBpZD0iZGVmczQiPgogICAgPGxpbmVhckdyYWRpZW50CiAgICAgICBpZD0ibGluZWFyR3JhZGllbnQzODc5IgogICAgICAgaW5rc2NhcGU6Y29sbGVjdD0iYWx3YXlzIj4KICAgICAgPHN0b3AKICAgICAgICAgaWQ9InN0b3AzODgxIgogICAgICAgICBvZmZzZXQ9IjAiCiAgICAgICAgIHN0eWxlPSJzdG9wLWNvbG9yOiNhNDAwMDA7c3RvcC1vcGFjaXR5OjEiIC8+CiAgICAgIDxzdG9wCiAgICAgICAgIGlkPSJzdG9wMzg4MyIKICAgICAgICAgb2Zmc2V0PSIxIgogICAgICAgICBzdHlsZT0ic3RvcC1jb2xvcjojZWYyOTI5O3N0b3Atb3BhY2l0eToxIiAvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudAogICAgICAgaW5rc2NhcGU6Y29sbGVjdD0iYWx3YXlzIgogICAgICAgaWQ9ImxpbmVhckdyYWRpZW50Mzg2OSI+CiAgICAgIDxzdG9wCiAgICAgICAgIHN0eWxlPSJzdG9wLWNvbG9yOiNhNDAwMDA7c3RvcC1vcGFjaXR5OjEiCiAgICAgICAgIG9mZnNldD0iMCIKICAgICAgICAgaWQ9InN0b3AzODcxIiAvPgogICAgICA8c3RvcAogICAgICAgICBzdHlsZT0ic3RvcC1jb2xvcjojZWYyOTI5O3N0b3Atb3BhY2l0eToxIgogICAgICAgICBvZmZzZXQ9IjEiCiAgICAgICAgIGlkPSJzdG9wMzg3MyIgLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQKICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgIHhsaW5rOmhyZWY9IiNsaW5lYXJHcmFkaWVudDM4NjkiCiAgICAgICBpZD0ibGluZWFyR3JhZGllbnQzODc1IgogICAgICAgeDE9Ii00NSIKICAgICAgIHkxPSIxMDQ0LjM2MjIiCiAgICAgICB4Mj0iLTU1IgogICAgICAgeTI9Ijk5NC4zNjIxOCIKICAgICAgIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIgogICAgICAgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwLjg2NjQ3NzI3LDAsMCwwLjg2NjQ3NzM5LDczLjY1MzQwOSwxMzYuMzAzOTEpIiAvPgogICAgPGxpbmVhckdyYWRpZW50CiAgICAgICBpbmtzY2FwZTpjb2xsZWN0PSJhbHdheXMiCiAgICAgICB4bGluazpocmVmPSIjbGluZWFyR3JhZGllbnQzODc5IgogICAgICAgaWQ9ImxpbmVhckdyYWRpZW50Mzg3NyIKICAgICAgIHgxPSItNDUiCiAgICAgICB5MT0iMTA0NC4zNjIyIgogICAgICAgeDI9Ii01NSIKICAgICAgIHkyPSI5OTQuMzYyMTgiCiAgICAgICBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIKICAgICAgIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMC44NjY0NzcyNywwLDAsMC44NjY0NzczOSw3My42NTM0MDksMTM2LjMwMzkxKSIgLz4KICA8L2RlZnM+CiAgPHNvZGlwb2RpOm5hbWVkdmlldwogICAgIGlkPSJiYXNlIgogICAgIHBhZ2Vjb2xvcj0iI2ZmZmZmZiIKICAgICBib3JkZXJjb2xvcj0iIzY2NjY2NiIKICAgICBib3JkZXJvcGFjaXR5PSIxLjAiCiAgICAgaW5rc2NhcGU6cGFnZW9wYWNpdHk9IjAuMCIKICAgICBpbmtzY2FwZTpwYWdlc2hhZG93PSIyIgogICAgIGlua3NjYXBlOnpvb209IjYuNTU3NzM4IgogICAgIGlua3NjYXBlOmN4PSI1MC4yNzE5NTgiCiAgICAgaW5rc2NhcGU6Y3k9IjMyLjkwMDkyNCIKICAgICBpbmtzY2FwZTpkb2N1bWVudC11bml0cz0icHgiCiAgICAgaW5rc2NhcGU6Y3VycmVudC1sYXllcj0ibGF5ZXIxIgogICAgIHNob3dncmlkPSJ0cnVlIgogICAgIGlua3NjYXBlOndpbmRvdy13aWR0aD0iMTU5OCIKICAgICBpbmtzY2FwZTp3aW5kb3ctaGVpZ2h0PSI4MzYiCiAgICAgaW5rc2NhcGU6d2luZG93LXg9IjAiCiAgICAgaW5rc2NhcGU6d2luZG93LXk9IjI3IgogICAgIGlua3NjYXBlOndpbmRvdy1tYXhpbWl6ZWQ9IjAiCiAgICAgaW5rc2NhcGU6c25hcC1nbG9iYWw9InRydWUiCiAgICAgaW5rc2NhcGU6c25hcC1iYm94PSJ0cnVlIgogICAgIGlua3NjYXBlOnNuYXAtbm9kZXM9InRydWUiPgogICAgPGlua3NjYXBlOmdyaWQKICAgICAgIHR5cGU9Inh5Z3JpZCIKICAgICAgIGlkPSJncmlkMTE1MjEiCiAgICAgICBlbXBzcGFjaW5nPSIyIgogICAgICAgZG90dGVkPSJmYWxzZSIKICAgICAgIHZpc2libGU9InRydWUiCiAgICAgICBlbmFibGVkPSJ0cnVlIgogICAgICAgc25hcHZpc2libGVncmlkbGluZXNvbmx5PSJ0cnVlIiAvPgogIDwvc29kaXBvZGk6bmFtZWR2aWV3PgogIDxtZXRhZGF0YQogICAgIGlkPSJtZXRhZGF0YTciPgogICAgPHJkZjpSREY+CiAgICAgIDxjYzpXb3JrCiAgICAgICAgIHJkZjphYm91dD0iIj4KICAgICAgICA8ZGM6Zm9ybWF0PmltYWdlL3N2Zyt4bWw8L2RjOmZvcm1hdD4KICAgICAgICA8ZGM6dHlwZQogICAgICAgICAgIHJkZjpyZXNvdXJjZT0iaHR0cDovL3B1cmwub3JnL2RjL2RjbWl0eXBlL1N0aWxsSW1hZ2UiIC8+CiAgICAgICAgPGRjOnRpdGxlPjwvZGM6dGl0bGU+CiAgICAgIDwvY2M6V29yaz4KICAgIDwvcmRmOlJERj4KICA8L21ldGFkYXRhPgogIDxnCiAgICAgaW5rc2NhcGU6bGFiZWw9IkxheWVyIDEiCiAgICAgaW5rc2NhcGU6Z3JvdXBtb2RlPSJsYXllciIKICAgICBpZD0ibGF5ZXIxIgogICAgIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAsLTk4OC4zNjIxOCkiPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMyODAwMDA7c3Ryb2tlLXdpZHRoOjE2O3N0cm9rZS1saW5lY2FwOnNxdWFyZTtzdHJva2UtbGluZWpvaW46bWl0ZXI7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgIGQ9Im0gMTMsMTAwMS4zNjIyIDM4LjEyNSwzOC4xMjUiCiAgICAgICBpZD0icGF0aDMwMDIiCiAgICAgICBpbmtzY2FwZTpjb25uZWN0b3ItY3VydmF0dXJlPSIwIgogICAgICAgc29kaXBvZGk6bm9kZXR5cGVzPSJjYyIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMjgwMDAwO3N0cm9rZS13aWR0aDoxNjtzdHJva2UtbGluZWNhcDpzcXVhcmU7c3Ryb2tlLWxpbmVqb2luOm1pdGVyO3N0cm9rZS1vcGFjaXR5OjEiCiAgICAgICBkPSJNIDUxLjEyNSwxMDAxLjM2MjIgMTMsMTAzOS40ODcyIgogICAgICAgaWQ9InBhdGgzMDAyLTYiCiAgICAgICBpbmtzY2FwZTpjb25uZWN0b3ItY3VydmF0dXJlPSIwIgogICAgICAgc29kaXBvZGk6bm9kZXR5cGVzPSJjYyIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojZWYyOTI5O3N0cm9rZS13aWR0aDoxMjtzdHJva2UtbGluZWNhcDpzcXVhcmU7c3Ryb2tlLWxpbmVqb2luOm1pdGVyO3N0cm9rZS1taXRlcmxpbWl0OjQ7c3Ryb2tlLW9wYWNpdHk6MTtzdHJva2UtZGFzaGFycmF5Om5vbmUiCiAgICAgICBkPSJtIDEzLDEwMDEuMzYyMiAzOC4xMjUsMzguMTI1IgogICAgICAgaWQ9InBhdGgzMDAyLTciCiAgICAgICBpbmtzY2FwZTpjb25uZWN0b3ItY3VydmF0dXJlPSIwIgogICAgICAgc29kaXBvZGk6bm9kZXR5cGVzPSJjYyIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojZWYyOTI5O3N0cm9rZS13aWR0aDoxMjtzdHJva2UtbGluZWNhcDpzcXVhcmU7c3Ryb2tlLWxpbmVqb2luOm1pdGVyO3N0cm9rZS1taXRlcmxpbWl0OjQ7c3Ryb2tlLW9wYWNpdHk6MTtzdHJva2UtZGFzaGFycmF5Om5vbmUiCiAgICAgICBkPSJNIDUxLjEyNSwxMDAxLjM2MjIgMTMsMTAzOS40ODcyIgogICAgICAgaWQ9InBhdGgzMDAyLTYtNSIKICAgICAgIGlua3NjYXBlOmNvbm5lY3Rvci1jdXJ2YXR1cmU9IjAiCiAgICAgICBzb2RpcG9kaTpub2RldHlwZXM9ImNjIiAvPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOnVybCgjbGluZWFyR3JhZGllbnQzODc3KTtzdHJva2Utd2lkdGg6ODtzdHJva2UtbGluZWNhcDpzcXVhcmU7c3Ryb2tlLWxpbmVqb2luOm1pdGVyO3N0cm9rZS1taXRlcmxpbWl0OjQ7c3Ryb2tlLW9wYWNpdHk6MTtzdHJva2UtZGFzaGFycmF5Om5vbmUiCiAgICAgICBkPSJtIDEzLDEwMDEuMzYyMiAzOC4xMjUsMzguMTI1IgogICAgICAgaWQ9InBhdGgzMDAyLTctNiIKICAgICAgIGlua3NjYXBlOmNvbm5lY3Rvci1jdXJ2YXR1cmU9IjAiCiAgICAgICBzb2RpcG9kaTpub2RldHlwZXM9ImNjIiAvPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOnVybCgjbGluZWFyR3JhZGllbnQzODc1KTtzdHJva2Utd2lkdGg6ODtzdHJva2UtbGluZWNhcDpzcXVhcmU7c3Ryb2tlLWxpbmVqb2luOm1pdGVyO3N0cm9rZS1taXRlcmxpbWl0OjQ7c3Ryb2tlLW9wYWNpdHk6MTtzdHJva2UtZGFzaGFycmF5Om5vbmUiCiAgICAgICBkPSJNIDUxLjEyNSwxMDAxLjM2MjIgMTMsMTAzOS40ODcyIgogICAgICAgaWQ9InBhdGgzMDAyLTYtNS0yIgogICAgICAgaW5rc2NhcGU6Y29ubmVjdG9yLWN1cnZhdHVyZT0iMCIKICAgICAgIHNvZGlwb2RpOm5vZGV0eXBlcz0iY2MiIC8+CiAgPC9nPgo8L3N2Zz4K
"""
dock_right_b64=\
"""
PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpzb2RpcG9kaT0iaHR0cDovL3NvZGlwb2RpLnNvdXJjZWZvcmdlLm5ldC9EVEQvc29kaXBvZGktMC5kdGQiCiAgIHhtbG5zOmlua3NjYXBlPSJodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy9uYW1lc3BhY2VzL2lua3NjYXBlIgogICB3aWR0aD0iNjRweCIKICAgaGVpZ2h0PSI2NHB4IgogICBpZD0ic3ZnMjk4NSIKICAgdmVyc2lvbj0iMS4xIgogICBpbmtzY2FwZTp2ZXJzaW9uPSIwLjQ4LjQgcjk5MzkiCiAgIHNvZGlwb2RpOmRvY25hbWU9ImRvY2stbGVmdC5zdmciPgogIDxkZWZzCiAgICAgaWQ9ImRlZnMyOTg3IiAvPgogIDxzb2RpcG9kaTpuYW1lZHZpZXcKICAgICBpZD0iYmFzZSIKICAgICBwYWdlY29sb3I9IiNmZmZmZmYiCiAgICAgYm9yZGVyY29sb3I9IiM2NjY2NjYiCiAgICAgYm9yZGVyb3BhY2l0eT0iMS4wIgogICAgIGlua3NjYXBlOnBhZ2VvcGFjaXR5PSIwLjAiCiAgICAgaW5rc2NhcGU6cGFnZXNoYWRvdz0iMiIKICAgICBpbmtzY2FwZTp6b29tPSI1LjA5NjgzMTIiCiAgICAgaW5rc2NhcGU6Y3g9Ii01OS45NzI4ODUiCiAgICAgaW5rc2NhcGU6Y3k9IjE2LjE5MzQxMyIKICAgICBpbmtzY2FwZTpjdXJyZW50LWxheWVyPSJsYXllcjEiCiAgICAgc2hvd2dyaWQ9InRydWUiCiAgICAgaW5rc2NhcGU6ZG9jdW1lbnQtdW5pdHM9InB4IgogICAgIGlua3NjYXBlOmdyaWQtYmJveD0idHJ1ZSIKICAgICBpbmtzY2FwZTp3aW5kb3ctd2lkdGg9IjI1NjAiCiAgICAgaW5rc2NhcGU6d2luZG93LWhlaWdodD0iMTM2MSIKICAgICBpbmtzY2FwZTp3aW5kb3cteD0iLTkiCiAgICAgaW5rc2NhcGU6d2luZG93LXk9Ii05IgogICAgIGlua3NjYXBlOndpbmRvdy1tYXhpbWl6ZWQ9IjEiCiAgICAgaW5rc2NhcGU6c25hcC1iYm94PSJ0cnVlIgogICAgIGlua3NjYXBlOnNuYXAtbm9kZXM9ImZhbHNlIj4KICAgIDxpbmtzY2FwZTpncmlkCiAgICAgICB0eXBlPSJ4eWdyaWQiCiAgICAgICBpZD0iZ3JpZDI5ODciCiAgICAgICBlbXBzcGFjaW5nPSIyIgogICAgICAgdmlzaWJsZT0idHJ1ZSIKICAgICAgIGVuYWJsZWQ9InRydWUiCiAgICAgICBzbmFwdmlzaWJsZWdyaWRsaW5lc29ubHk9InRydWUiIC8+CiAgPC9zb2RpcG9kaTpuYW1lZHZpZXc+CiAgPG1ldGFkYXRhCiAgICAgaWQ9Im1ldGFkYXRhMjk5MCI+CiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsKICAgICAgICAgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ+aW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlCiAgICAgICAgICAgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIgLz4KICAgICAgICA8ZGM6dGl0bGU+PC9kYzp0aXRsZT4KICAgICAgICA8ZGM6Y3JlYXRvcj4KICAgICAgICAgIDxjYzpBZ2VudD4KICAgICAgICAgICAgPGRjOnRpdGxlPlt5b3Jpa3ZhbmhhdnJlXTwvZGM6dGl0bGU+CiAgICAgICAgICA8L2NjOkFnZW50PgogICAgICAgIDwvZGM6Y3JlYXRvcj4KICAgICAgICA8ZGM6dGl0bGU+QXJjaF9TZWN0aW9uUGxhbmVfVHJlZTwvZGM6dGl0bGU+CiAgICAgICAgPGRjOmRhdGU+MjAxMS0xMi0wNjwvZGM6ZGF0ZT4KICAgICAgICA8ZGM6cmVsYXRpb24+aHR0cDovL3d3dy5mcmVlY2Fkd2ViLm9yZy93aWtpL2luZGV4LnBocD90aXRsZT1BcnR3b3JrPC9kYzpyZWxhdGlvbj4KICAgICAgICA8ZGM6cHVibGlzaGVyPgogICAgICAgICAgPGNjOkFnZW50PgogICAgICAgICAgICA8ZGM6dGl0bGU+RnJlZUNBRDwvZGM6dGl0bGU+CiAgICAgICAgICA8L2NjOkFnZW50PgogICAgICAgIDwvZGM6cHVibGlzaGVyPgogICAgICAgIDxkYzppZGVudGlmaWVyPkZyZWVDQUQvc3JjL01vZC9BcmNoL1Jlc291cmNlcy9pY29ucy9BcmNoX1NlY3Rpb25QbGFuZV9UcmVlLnN2ZzwvZGM6aWRlbnRpZmllcj4KICAgICAgICA8ZGM6cmlnaHRzPgogICAgICAgICAgPGNjOkFnZW50PgogICAgICAgICAgICA8ZGM6dGl0bGU+RnJlZUNBRCBMR1BMMis8L2RjOnRpdGxlPgogICAgICAgICAgPC9jYzpBZ2VudD4KICAgICAgICA8L2RjOnJpZ2h0cz4KICAgICAgICA8Y2M6bGljZW5zZT5odHRwczovL3d3dy5nbnUub3JnL2NvcHlsZWZ0L2xlc3Nlci5odG1sPC9jYzpsaWNlbnNlPgogICAgICAgIDxkYzpjb250cmlidXRvcj4KICAgICAgICAgIDxjYzpBZ2VudD4KICAgICAgICAgICAgPGRjOnRpdGxlPlthZ3J5c29uXSBBbGV4YW5kZXIgR3J5c29uPC9kYzp0aXRsZT4KICAgICAgICAgIDwvY2M6QWdlbnQ+CiAgICAgICAgPC9kYzpjb250cmlidXRvcj4KICAgICAgPC9jYzpXb3JrPgogICAgPC9yZGY6UkRGPgogIDwvbWV0YWRhdGE+CiAgPGcKICAgICBpZD0ibGF5ZXIxIgogICAgIGlua3NjYXBlOmxhYmVsPSJMYXllciAxIgogICAgIGlua3NjYXBlOmdyb3VwbW9kZT0ibGF5ZXIiPgogICAgPHBhdGgKICAgICAgIHNvZGlwb2RpOnR5cGU9InN0YXIiCiAgICAgICBzdHlsZT0iY29sb3I6IzAwMDAwMDtmaWxsOiM4MDgwODA7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOiM0ZDRkNGQ7c3Ryb2tlLXdpZHRoOjEuNTc0ODgyMjc7c3Ryb2tlLWxpbmVjYXA6YnV0dDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6NDtzdHJva2Utb3BhY2l0eToxO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2UtZGFzaG9mZnNldDowO21hcmtlcjpub25lO3Zpc2liaWxpdHk6dmlzaWJsZTtkaXNwbGF5OmlubGluZTtvdmVyZmxvdzp2aXNpYmxlO2VuYWJsZS1iYWNrZ3JvdW5kOmFjY3VtdWxhdGUiCiAgICAgICBpZD0icGF0aDI5OTciCiAgICAgICBzb2RpcG9kaTpzaWRlcz0iMyIKICAgICAgIHNvZGlwb2RpOmN4PSIyMiIKICAgICAgIHNvZGlwb2RpOmN5PSIxNy4wOTA5MDgiCiAgICAgICBzb2RpcG9kaTpyMT0iMjAuNDMyNTEyIgogICAgICAgc29kaXBvZGk6cjI9IjEwLjIxNjI1NyIKICAgICAgIHNvZGlwb2RpOmFyZzE9IjIuMDk0Mzk1MSIKICAgICAgIHNvZGlwb2RpOmFyZzI9IjMuMTQxNTkyNyIKICAgICAgIGlua3NjYXBlOmZsYXRzaWRlZD0idHJ1ZSIKICAgICAgIGlua3NjYXBlOnJvdW5kZWQ9IjAiCiAgICAgICBpbmtzY2FwZTpyYW5kb21pemVkPSIwIgogICAgICAgZD0ibSAxMS43ODM3NDQsMzQuNzg1OTgzIDAsLTM1LjM5MDE0OTYzIDMwLjY0ODc2OCwxNy42OTUwNzQ2MyB6IgogICAgICAgaW5rc2NhcGU6dHJhbnNmb3JtLWNlbnRlci14PSItNi42Njg0MTU5IgogICAgICAgdHJhbnNmb3JtPSJtYXRyaXgoMS4zMDU0NTI5LDAsMCwxLjEzMDA0NzYsLTMuMjAyMzc3OCwxMi42ODY0NTkpIiAvPgogIDwvZz4KPC9zdmc+Cg==
"""
dock_left_b64=\
"""
PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpzb2RpcG9kaT0iaHR0cDovL3NvZGlwb2RpLnNvdXJjZWZvcmdlLm5ldC9EVEQvc29kaXBvZGktMC5kdGQiCiAgIHhtbG5zOmlua3NjYXBlPSJodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy9uYW1lc3BhY2VzL2lua3NjYXBlIgogICB3aWR0aD0iNjRweCIKICAgaGVpZ2h0PSI2NHB4IgogICBpZD0ic3ZnMjk4NSIKICAgdmVyc2lvbj0iMS4xIgogICBpbmtzY2FwZTp2ZXJzaW9uPSIwLjQ4LjQgcjk5MzkiCiAgIHNvZGlwb2RpOmRvY25hbWU9ImRvY2stbGVmdC5zdmciPgogIDxkZWZzCiAgICAgaWQ9ImRlZnMyOTg3IiAvPgogIDxzb2RpcG9kaTpuYW1lZHZpZXcKICAgICBpZD0iYmFzZSIKICAgICBwYWdlY29sb3I9IiNmZmZmZmYiCiAgICAgYm9yZGVyY29sb3I9IiM2NjY2NjYiCiAgICAgYm9yZGVyb3BhY2l0eT0iMS4wIgogICAgIGlua3NjYXBlOnBhZ2VvcGFjaXR5PSIwLjAiCiAgICAgaW5rc2NhcGU6cGFnZXNoYWRvdz0iMiIKICAgICBpbmtzY2FwZTp6b29tPSI1LjA5NjgzMTIiCiAgICAgaW5rc2NhcGU6Y3g9Ii01OS45NzI4ODUiCiAgICAgaW5rc2NhcGU6Y3k9IjE2LjE5MzQxMyIKICAgICBpbmtzY2FwZTpjdXJyZW50LWxheWVyPSJsYXllcjEiCiAgICAgc2hvd2dyaWQ9InRydWUiCiAgICAgaW5rc2NhcGU6ZG9jdW1lbnQtdW5pdHM9InB4IgogICAgIGlua3NjYXBlOmdyaWQtYmJveD0idHJ1ZSIKICAgICBpbmtzY2FwZTp3aW5kb3ctd2lkdGg9IjI1NjAiCiAgICAgaW5rc2NhcGU6d2luZG93LWhlaWdodD0iMTM2MSIKICAgICBpbmtzY2FwZTp3aW5kb3cteD0iLTkiCiAgICAgaW5rc2NhcGU6d2luZG93LXk9Ii05IgogICAgIGlua3NjYXBlOndpbmRvdy1tYXhpbWl6ZWQ9IjEiCiAgICAgaW5rc2NhcGU6c25hcC1iYm94PSJ0cnVlIgogICAgIGlua3NjYXBlOnNuYXAtbm9kZXM9ImZhbHNlIj4KICAgIDxpbmtzY2FwZTpncmlkCiAgICAgICB0eXBlPSJ4eWdyaWQiCiAgICAgICBpZD0iZ3JpZDI5ODciCiAgICAgICBlbXBzcGFjaW5nPSIyIgogICAgICAgdmlzaWJsZT0idHJ1ZSIKICAgICAgIGVuYWJsZWQ9InRydWUiCiAgICAgICBzbmFwdmlzaWJsZWdyaWRsaW5lc29ubHk9InRydWUiIC8+CiAgPC9zb2RpcG9kaTpuYW1lZHZpZXc+CiAgPG1ldGFkYXRhCiAgICAgaWQ9Im1ldGFkYXRhMjk5MCI+CiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsKICAgICAgICAgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ+aW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlCiAgICAgICAgICAgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIgLz4KICAgICAgICA8ZGM6dGl0bGUgLz4KICAgICAgICA8ZGM6Y3JlYXRvcj4KICAgICAgICAgIDxjYzpBZ2VudD4KICAgICAgICAgICAgPGRjOnRpdGxlPlt5b3Jpa3ZhbmhhdnJlXTwvZGM6dGl0bGU+CiAgICAgICAgICA8L2NjOkFnZW50PgogICAgICAgIDwvZGM6Y3JlYXRvcj4KICAgICAgICA8ZGM6dGl0bGU+QXJjaF9TZWN0aW9uUGxhbmVfVHJlZTwvZGM6dGl0bGU+CiAgICAgICAgPGRjOmRhdGU+MjAxMS0xMi0wNjwvZGM6ZGF0ZT4KICAgICAgICA8ZGM6cmVsYXRpb24+aHR0cDovL3d3dy5mcmVlY2Fkd2ViLm9yZy93aWtpL2luZGV4LnBocD90aXRsZT1BcnR3b3JrPC9kYzpyZWxhdGlvbj4KICAgICAgICA8ZGM6cHVibGlzaGVyPgogICAgICAgICAgPGNjOkFnZW50PgogICAgICAgICAgICA8ZGM6dGl0bGU+RnJlZUNBRDwvZGM6dGl0bGU+CiAgICAgICAgICA8L2NjOkFnZW50PgogICAgICAgIDwvZGM6cHVibGlzaGVyPgogICAgICAgIDxkYzppZGVudGlmaWVyPkZyZWVDQUQvc3JjL01vZC9BcmNoL1Jlc291cmNlcy9pY29ucy9BcmNoX1NlY3Rpb25QbGFuZV9UcmVlLnN2ZzwvZGM6aWRlbnRpZmllcj4KICAgICAgICA8ZGM6cmlnaHRzPgogICAgICAgICAgPGNjOkFnZW50PgogICAgICAgICAgICA8ZGM6dGl0bGU+RnJlZUNBRCBMR1BMMis8L2RjOnRpdGxlPgogICAgICAgICAgPC9jYzpBZ2VudD4KICAgICAgICA8L2RjOnJpZ2h0cz4KICAgICAgICA8Y2M6bGljZW5zZT5odHRwczovL3d3dy5nbnUub3JnL2NvcHlsZWZ0L2xlc3Nlci5odG1sPC9jYzpsaWNlbnNlPgogICAgICAgIDxkYzpjb250cmlidXRvcj4KICAgICAgICAgIDxjYzpBZ2VudD4KICAgICAgICAgICAgPGRjOnRpdGxlPlthZ3J5c29uXSBBbGV4YW5kZXIgR3J5c29uPC9kYzp0aXRsZT4KICAgICAgICAgIDwvY2M6QWdlbnQ+CiAgICAgICAgPC9kYzpjb250cmlidXRvcj4KICAgICAgPC9jYzpXb3JrPgogICAgPC9yZGY6UkRGPgogIDwvbWV0YWRhdGE+CiAgPGcKICAgICBpZD0ibGF5ZXIxIgogICAgIGlua3NjYXBlOmxhYmVsPSJMYXllciAxIgogICAgIGlua3NjYXBlOmdyb3VwbW9kZT0ibGF5ZXIiPgogICAgPHBhdGgKICAgICAgIHNvZGlwb2RpOnR5cGU9InN0YXIiCiAgICAgICBzdHlsZT0iY29sb3I6IzAwMDAwMDtmaWxsOiM4MDgwODA7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOiM0ZDRkNGQ7c3Ryb2tlLXdpZHRoOjEuNTc0ODgyMjcwMDAwMDAwMDA7c3Ryb2tlLWxpbmVjYXA6YnV0dDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6NDtzdHJva2Utb3BhY2l0eToxO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2UtZGFzaG9mZnNldDowO21hcmtlcjpub25lO3Zpc2liaWxpdHk6dmlzaWJsZTtkaXNwbGF5OmlubGluZTtvdmVyZmxvdzp2aXNpYmxlO2VuYWJsZS1iYWNrZ3JvdW5kOmFjY3VtdWxhdGUiCiAgICAgICBpZD0icGF0aDI5OTciCiAgICAgICBzb2RpcG9kaTpzaWRlcz0iMyIKICAgICAgIHNvZGlwb2RpOmN4PSIyMiIKICAgICAgIHNvZGlwb2RpOmN5PSIxNy4wOTA5MDgiCiAgICAgICBzb2RpcG9kaTpyMT0iMjAuNDMyNTEyIgogICAgICAgc29kaXBvZGk6cjI9IjEwLjIxNjI1NyIKICAgICAgIHNvZGlwb2RpOmFyZzE9IjIuMDk0Mzk1MSIKICAgICAgIHNvZGlwb2RpOmFyZzI9IjMuMTQxNTkyNyIKICAgICAgIGlua3NjYXBlOmZsYXRzaWRlZD0idHJ1ZSIKICAgICAgIGlua3NjYXBlOnJvdW5kZWQ9IjAiCiAgICAgICBpbmtzY2FwZTpyYW5kb21pemVkPSIwIgogICAgICAgZD0ibSAxMS43ODM3NDQsMzQuNzg1OTgzIDAsLTM1LjM5MDE0OTYzIDMwLjY0ODc2OCwxNy42OTUwNzQ2MyB6IgogICAgICAgaW5rc2NhcGU6dHJhbnNmb3JtLWNlbnRlci14PSI2LjY2ODQxNTkiCiAgICAgICB0cmFuc2Zvcm09Im1hdHJpeCgtMS4zMDU0NTI5LDAsMCwxLjEzMDA0NzYsNjcuNTc0MzkxLDEyLjY4NjQ1OSkiIC8+CiAgPC9nPgo8L3N2Zz4K
"""

####################################
class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(367, 483)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons-new/Center-Align.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DockWidget.setWindowIcon(icon)
        DockWidget.setToolTip("Defeaturing tools")
        DockWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        DockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        DockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        DockWidget.setWindowTitle("Defeaturing Tools")
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.PB_RHoles = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_RHoles.setGeometry(QtCore.QRect(12, 288, 81, 28))
        self.PB_RHoles.setToolTip("remove Hole from Face")
        self.PB_RHoles.setText("del Hole")
        self.PB_RHoles.setObjectName("PB_RHoles")
        self.PB_Edges = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_Edges.setGeometry(QtCore.QRect(288, 36, 69, 28))
        self.PB_Edges.setToolTip("add selected Edges to List")
        self.PB_Edges.setText("Confirm")
        self.PB_Edges.setObjectName("PB_Edges")
        self.TE_Faces = QtGui.QPlainTextEdit(self.dockWidgetContents)
        self.TE_Faces.setGeometry(QtCore.QRect(41, 164, 237, 71))
        self.TE_Faces.setToolTip("List of Face(s)")
        self.TE_Faces.setObjectName("TE_Faces")
        self.checkBox_keep_original = QtGui.QCheckBox(self.dockWidgetContents)
        self.checkBox_keep_original.setGeometry(QtCore.QRect(248, 252, 110, 33))
        self.checkBox_keep_original.setToolTip("keep the original object")
        self.checkBox_keep_original.setText("keep Object")
        self.checkBox_keep_original.setChecked(True)
        self.checkBox_keep_original.setObjectName("checkBox_keep_original")
        self.InfoLabel = QtGui.QLabel(self.dockWidgetContents)
        self.InfoLabel.setGeometry(QtCore.QRect(43, 0, 196, 36))
        self.InfoLabel.setText("Select Edge(s)\n"
"Ctrl+Click")
        self.InfoLabel.setObjectName("InfoLabel")
        self.TE_Edges = QtGui.QPlainTextEdit(self.dockWidgetContents)
        self.TE_Edges.setEnabled(True)
        self.TE_Edges.setGeometry(QtCore.QRect(41, 36, 237, 66))
        self.TE_Edges.setToolTip("List of Edge(s)")
        self.TE_Edges.setPlainText("")
        self.TE_Edges.setObjectName("TE_Edges")
        self.PB_Faces = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_Faces.setGeometry(QtCore.QRect(288, 164, 69, 28))
        self.PB_Faces.setToolTip("add selected Faces to List")
        self.PB_Faces.setText("Confirm")
        self.PB_Faces.setObjectName("PB_Faces")
        self.PB_Edges_Clear = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_Edges_Clear.setGeometry(QtCore.QRect(288, 71, 69, 28))
        self.PB_Edges_Clear.setText("Clear List")
        self.PB_Edges_Clear.setObjectName("PB_Edges_Clear")
        self.PB_Faces_Clear = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_Faces_Clear.setGeometry(QtCore.QRect(288, 200, 69, 28))
        self.PB_Faces_Clear.setText("Clear List")
        self.PB_Faces_Clear.setObjectName("PB_Faces_Clear")
        self.Edge_Nbr = QtGui.QLabel(self.dockWidgetContents)
        self.Edge_Nbr.setGeometry(QtCore.QRect(59, 104, 53, 16))
        self.Edge_Nbr.setText("0")
        self.Edge_Nbr.setObjectName("Edge_Nbr")
        self.Face_Nbr = QtGui.QLabel(self.dockWidgetContents)
        self.Face_Nbr.setGeometry(QtCore.QRect(59, 236, 53, 16))
        self.Face_Nbr.setText("0")
        self.Face_Nbr.setObjectName("Face_Nbr")
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setGeometry(QtCore.QRect(43, 124, 177, 45))
        self.label.setText("Select Face(s)\n"
"Ctrl+Click")
        self.label.setObjectName("label")
        self.checkBox_Refine = QtGui.QCheckBox(self.dockWidgetContents)
        self.checkBox_Refine.setGeometry(QtCore.QRect(20, 260, 100, 20))
        self.checkBox_Refine.setToolTip("refine the resulting solid\n"
"after the operation ")
        self.checkBox_Refine.setText("refine")
        self.checkBox_Refine.setChecked(False)
        self.checkBox_Refine.setObjectName("checkBox_Refine")
        self.checkBox_keep_faces = QtGui.QCheckBox(self.dockWidgetContents)
        self.checkBox_keep_faces.setGeometry(QtCore.QRect(116, 260, 100, 20))
        self.checkBox_keep_faces.setToolTip("keep construcion faces")
        self.checkBox_keep_faces.setText("keep faces")
        self.checkBox_keep_faces.setObjectName("checkBox_keep_faces")
        self.PB_RFaces = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_RFaces.setGeometry(QtCore.QRect(100, 288, 81, 28))
        self.PB_RFaces.setToolTip("remove \'in List\' Faces")
        self.PB_RFaces.setText("del Faces")
        self.PB_RFaces.setObjectName("PB_RFaces")
        self.PB_AFaces = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_AFaces.setGeometry(QtCore.QRect(188, 288, 81, 28))
        self.PB_AFaces.setToolTip("add Faces from \'in List\' Edges")
        self.PB_AFaces.setText("add Faces")
        self.PB_AFaces.setObjectName("PB_AFaces")
        self.PB_makeShell = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_makeShell.setGeometry(QtCore.QRect(12, 360, 81, 28))
        self.PB_makeShell.setToolTip("make Solid from in list Faces")
        self.PB_makeShell.setText("mk Solid")
        self.PB_makeShell.setObjectName("PB_makeShell")
        self.PB_makeShell_2 = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_makeShell_2.setGeometry(QtCore.QRect(100, 360, 81, 28))
        self.PB_makeShell_2.setToolTip("make Solid from the Faces\n"
"of the selected Objects")
        self.PB_makeShell_2.setText("mk Solid 2")
        self.PB_makeShell_2.setObjectName("PB_makeShell_2")
        self.PB_check_TypeId = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_check_TypeId.setGeometry(QtCore.QRect(188, 432, 81, 28))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setBold(False)
        self.PB_check_TypeId.setFont(font)
        self.PB_check_TypeId.setToolTip("show/hide TypeId of the Shape")
        self.PB_check_TypeId.setText("? TypeId")
        self.PB_check_TypeId.setObjectName("PB_check_TypeId")
        self.Obj_Nbr = QtGui.QLabel(self.dockWidgetContents)
        self.Obj_Nbr.setGeometry(QtCore.QRect(223, 104, 53, 16))
        self.Obj_Nbr.setText("0")
        self.Obj_Nbr.setObjectName("Obj_Nbr")
        self.Obj_Nbr_2 = QtGui.QLabel(self.dockWidgetContents)
        self.Obj_Nbr_2.setGeometry(QtCore.QRect(223, 236, 53, 16))
        self.Obj_Nbr_2.setText("0")
        self.Obj_Nbr_2.setObjectName("Obj_Nbr_2")
        self.PB_AEdges = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_AEdges.setGeometry(QtCore.QRect(276, 288, 81, 28))
        self.PB_AEdges.setToolTip("create a copy of the \'in List\' Edges")
        self.PB_AEdges.setText("add Edges")
        self.PB_AEdges.setObjectName("PB_AEdges")
        self.PB_showEdgeList = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_showEdgeList.setGeometry(QtCore.QRect(12, 396, 81, 28))
        self.PB_showEdgeList.setToolTip("show \'in List\' Edge(s)")
        self.PB_showEdgeList.setText("show Edges")
        self.PB_showEdgeList.setObjectName("PB_showEdgeList")
        self.PB_showFaceList = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_showFaceList.setGeometry(QtCore.QRect(100, 396, 81, 28))
        self.PB_showFaceList.setToolTip("show \'in List\' Face(s)")
        self.PB_showFaceList.setText("show Faces")
        self.PB_showFaceList.setObjectName("PB_showFaceList")
        self.PB_Refine = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_Refine.setGeometry(QtCore.QRect(188, 396, 81, 28))
        self.PB_Refine.setToolTip("refine")
        self.PB_Refine.setText("Refine")
        self.PB_Refine.setObjectName("PB_Refine")
        self.PB_RefineParametric = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_RefineParametric.setGeometry(QtCore.QRect(276, 396, 81, 28))
        self.PB_RefineParametric.setToolTip("parametric Refine")
        self.PB_RefineParametric.setText("prm Refine")
        self.PB_RefineParametric.setObjectName("PB_RefineParametric")
        self.PB_CFaces = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_CFaces.setGeometry(QtCore.QRect(12, 324, 81, 28))
        self.PB_CFaces.setToolTip("copy Faces from \'in List\' Edges")
        self.PB_CFaces.setText("cpy Faces")
        self.PB_CFaces.setObjectName("PB_CFaces")
        self.PB_TFace = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_TFace.setGeometry(QtCore.QRect(100, 324, 81, 28))
        self.PB_TFace.setToolTip("copy Faces from \'in List\' Edges")
        self.PB_TFace.setText("offset Face")
        self.PB_TFace.setObjectName("PB_TFace")
        self.offset_input = QtGui.QLineEdit(self.dockWidgetContents)
        self.offset_input.setGeometry(QtCore.QRect(192, 328, 73, 22))
        self.offset_input.setToolTip("Face offset to apply")
        self.offset_input.setText("0.0")
        self.offset_input.setObjectName("offset_input")
        self.PB_TEdge = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_TEdge.setGeometry(QtCore.QRect(276, 324, 81, 28))
        self.PB_TEdge.setToolTip("copy Faces from \'in List\' Edges")
        self.PB_TEdge.setText("offset Edge")
        self.PB_TEdge.setObjectName("PB_TEdge")
        self.PB_close = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_close.setGeometry(QtCore.QRect(-1, -1, 20, 20))
        self.PB_close.setToolTip("add selected Edges to List")
        self.PB_close.setText("")
        self.PB_close.setObjectName("PB_close")
        self.Version = QtGui.QLabel(self.dockWidgetContents)
        self.Version.setGeometry(QtCore.QRect(300, 0, 53, 16))
        self.Version.setText("0")
        self.Version.setObjectName("Version")
        self.PB_left = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_left.setGeometry(QtCore.QRect(-1, 17, 20, 20))
        self.PB_left.setToolTip("dock left")
        self.PB_left.setText("")
        self.PB_left.setObjectName("PB_left")
        self.PB_right = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_right.setGeometry(QtCore.QRect(-1, 34, 20, 20))
        self.PB_right.setToolTip("dock right")
        self.PB_right.setText("")
        self.PB_right.setObjectName("PB_right")
        self.PB_makeEdge = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_makeEdge.setGeometry(QtCore.QRect(276, 360, 81, 28))
        self.PB_makeEdge.setToolTip("make Edge from selected Vertexes")
        self.PB_makeEdge.setText("mk Edge")
        self.PB_makeEdge.setObjectName("PB_makeEdge")
        self.PB_expSTEP = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_expSTEP.setGeometry(QtCore.QRect(188, 360, 81, 28))
        self.PB_expSTEP.setToolTip("make Solid from the Faces\n"
"of the selected Objects")
        self.PB_expSTEP.setText("mk Solid 3")
        self.PB_expSTEP.setObjectName("PB_expSTEP")
        self.PB_PartDefeaturing = QtGui.QPushButton(self.dockWidgetContents)
        self.PB_PartDefeaturing.setEnabled(False)
        self.PB_PartDefeaturing.setGeometry(QtCore.QRect(12, 432, 81, 28))
        self.PB_PartDefeaturing.setToolTip("show \'in List\' Edge(s)")
        self.PB_PartDefeaturing.setText("Defeat")
        self.PB_PartDefeaturing.setObjectName("PB_PartDefeaturing")
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

################################################################################################
        #self.PB_Exit.clicked.connect(close_RH)
        self.PB_AEdges.clicked.connect(addEdges_RH)
        self.PB_makeShell.clicked.connect(merge_selected_faces_RH)
        self.PB_makeShell_2.clicked.connect(merge_faces_from_selected_objects_RH)
        self.PB_check_TypeId.clicked.connect(check_TypeId_RH)
        self.PB_Edges.clicked.connect(edges_confirmed_RH)
        self.PB_Edges_Clear.clicked.connect(clear_all_RH)
        self.PB_Faces.clicked.connect(faces_confirmed_RH)
        self.PB_Faces_Clear.clicked.connect(clear_all_RH)
        self.PB_RHoles.clicked.connect(removeHoles_RH)
        self.PB_RFaces.clicked.connect(removeFaces_RH)
        self.PB_AFaces.clicked.connect(addFaces_RH)
        self.PB_CFaces.clicked.connect(copyFaces_RH)
        self.checkBox_keep_original.setChecked(True)
        self.checkBox_keep_faces.setChecked(False)
        self.PB_Refine.clicked.connect(refine_RH)
        self.PB_RefineParametric.clicked.connect(refine_parametric_RH)
        self.PB_showEdgeList.clicked.connect(showEdges_RH)
        self.PB_showFaceList.clicked.connect(showFaces_RH)
        self.PB_TFace.clicked.connect(offsetFaces_RH)
        self.PB_TEdge.clicked.connect(offsetEdges_RH)
        self.offset_input.setText("1.0:n")
        self.offset_input.setToolTip("offset in mm\n separator ':'\ndirection [n=normal, x,y,z]")
        self.PB_makeEdge.clicked.connect(makeEdge_RH)
        self.PB_expSTEP.clicked.connect(makeSolidExpSTEP_RH)
        self.PB_expSTEP.setToolTip("select ONE object to try to make a Solid\nthrough STEP import/export process")
        self.TE_Edges.setReadOnly(True)
        self.TE_Faces.setReadOnly(True)
        self.PB_PartDefeaturing.clicked.connect(PartDefeaturing_RH)
        self.PB_PartDefeaturing.setVisible(False)
        
        pm = QtGui.QPixmap()
        pm.loadFromData(base64.b64decode(closeW_b64))
        self.PB_close.setGeometry(QtCore.QRect(-1, -1, 20, 20))
        self.PB_close.setToolTip("close")
        self.PB_close.setText("")
        self.PB_close.setIconSize(QtCore.QSize(16,16))
        self.PB_close.setIcon(QtGui.QIcon(pm))
        self.PB_close.clicked.connect(close_RH)
        pm = QtGui.QPixmap()
        pm.loadFromData(base64.b64decode(dock_left_b64))
        self.PB_left.setGeometry(QtCore.QRect(-1, 19, 20, 20))
        self.PB_left.setToolTip("dock left")
        self.PB_left.setText("")
        self.PB_left.setIconSize(QtCore.QSize(16,16))
        self.PB_left.setIcon(QtGui.QIcon(pm))
        self.PB_left.clicked.connect(dock_left_RH)
        pm = QtGui.QPixmap()
        pm.loadFromData(base64.b64decode(dock_right_b64))
        self.PB_right.setGeometry(QtCore.QRect(-1, 39, 20, 20))
        self.PB_right.setToolTip("dock right")
        self.PB_right.setText("")
        self.PB_right.setIconSize(QtCore.QSize(16,16))
        self.PB_right.setIcon(QtGui.QIcon(pm))
        self.PB_right.clicked.connect(dock_right_RH)
   
################################################################################################
    def retranslateUi(self, DockWidget):
        pass

    
##############################################################
global instance_nbr
instance_nbr=0

def RH_singleInstance():
    
    app = QtGui.QApplication #QtGui.qApp
    for i in app.topLevelWidgets():
        #i_say (str(i.objectName()))
        if i.objectName() == "DefeaturingTools":
            #i_say (str(i.objectName()))
            #i.close()
            #i.deleteLater()
            #i_say ('closed')
            return False
    t=FreeCADGui.getMainWindow()
    dw=t.findChildren(QtGui.QDockWidget)
    #say( str(dw) )
    for i in dw:
        #i_say (str(i.objectName()))
        if str(i.objectName()) == "DefeaturingTools": #"kicad StepUp 3D tools":
            #i_say (str(i.objectName())+' docked')
            #i.deleteLater()
            return False
    return True
##

def dock_right_RH():
    RHmw = FreeCADGui.getMainWindow()
    RHmw.addDockWidget(QtCore.Qt.RightDockWidgetArea,RHDockWidget)
    RHDockWidget.setFloating(False)  #dock
    #RHDockWidget.resize(sizeXright,sizeYright)
    RHDockWidget.activateWindow()
    RHDockWidget.raise_()
def dock_left_RH():
    RHmw = FreeCADGui.getMainWindow()
    RHmw.addDockWidget(QtCore.Qt.LeftDockWidgetArea,RHDockWidget)
    RHDockWidget.setFloating(False)  #dock
    #RHDockWidget.resize(sizeXright,sizeYright)
    RHDockWidget.activateWindow()
    RHDockWidget.raise_()
#def tabify():

    RHDockWidget.setFloating(False)  #dock
    #RHDockWidget.resize(sizeX,sizeY)
    RHDockWidget.activateWindow()
    RHDockWidget.raise_()
    t=FreeCADGui.getMainWindow()
    cv = t.findChild(QtGui.QDockWidget, "Combo View")
    if RHDockWidget and cv:
        dw=t.findChildren(QtGui.QDockWidget)
        try:
            t.tabifyDockWidget(cv,RHDockWidget)                
        except:
            pass
        d_tab = t.findChild(QtGui.QDockWidget, "DefeaturingTools") #"kicad StepUp 3D tools")
        d_tab.activateWindow()
        d_tab.raise_()
        RHDockWidget.showMaximized()
        RHDockWidget.activateWindow()
        RHDockWidget.raise_()
        i_say( "Tabified done !")               
        d_tab = t.findChild(QtGui.QDockWidget, "DefeaturingTools") #"kicad StepUp 3D tools")
        if d_tab:
            #KSUWidget.resize(sizeX,sizeY)
            d_tab.activateWindow()
            d_tab.raise_()
        #say ("focus on me!")
##

doc=FreeCAD.ActiveDocument
if RH_singleInstance():
    RHDockWidget = QtGui.QDockWidget()
    RHDockWidget.ui = Ui_DockWidget()   
    RHDockWidget.ui.setupUi(RHDockWidget) # setup the ui
    RHDockWidget.setObjectName("DefeaturingTools")
    RHDockWidget.raise_()
    #RHDockWidget.ui.closeEvent.connect(showFaces_RH())
    #RHDockWidget.setFeatures( QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetClosable )
    RHDockWidget.setFeatures( QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable) #|QtGui.QDockWidget.DockWidgetClosable )
    
    def onClickClose():
        #print("Changed visibility")
        RH_visible = RHDockWidget.isVisible()
        #print (RH_visible)
        #if not RH_visible:
        #    RHDockWidget.deleteLater()
    
    #RHDockWidget.destroyed.connect(onDestroy)
    RHDockWidget.visibilityChanged.connect(onClickClose)
    #RHDockWidget.closed.connect(onDestroy)
    #ui = Ui_DockWidget()
    #ui.setupUi(RHDockWidget)
    #RHDockWidget.show()
    #RHDockWidget.setFeatures( QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable) #|QtGui.QDockWidget.DockWidgetClosable )
        
    RHmw = FreeCADGui.getMainWindow()                 # PySide # the active qt window, = the freecad window since we are inside it
    RHmw.addDockWidget(QtCore.Qt.RightDockWidgetArea,RHDockWidget)
    RHDockWidget.setFloating(True)  #undock
    RHDockWidget.ui.Version.setText(__version__)
    
    if hasattr(Part, "OCC_VERSION"):
        OCCMV = Part.OCC_VERSION.split('.')[0]
        OCCmV = Part.OCC_VERSION.split('.')[1]
        if (int(OCCMV)>= 7) and (int(OCCmV)>= 3):
            RHDockWidget.ui.PB_PartDefeaturing.setVisible(True)
            RHDockWidget.ui.PB_PartDefeaturing.setEnabled(True)
    
    # print (instance_nbr)
    # if instance_nbr >1:
    #     RH_killInstance()
        
    #RHDockWidget.resize(sizeX,sizeY)
    
#    dw = ui.QDockWidget("Test",mw)
#    dw.setWidget(ui.QLabel("Content"))

#    mw.addDockWidget(core.Qt.RightDockWidgetArea, dw)


