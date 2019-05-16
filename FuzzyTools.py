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
from PySide import QtCore, QtGui

__version__ = "v1.0.2"

def f_say(msg):
    FreeCAD.Console.PrintMessage(msg)
    FreeCAD.Console.PrintMessage('\n')

def f_sayw(msg):
    FreeCAD.Console.PrintWarning(msg)
    FreeCAD.Console.PrintWarning('\n')
    
def f_sayerr(msg):
    FreeCAD.Console.PrintError(msg)
    FreeCAD.Console.PrintWarning('\n')

##
def fuzzyCut():
    import Part
    global fuzzyTolerance
    from PySide import QtCore, QtGui
    
    fuzzyTolerance = 0.01
    reply = QtGui.QInputDialog.getText(None, "Tolerance","Fuzzy Tolerance",QtGui.QLineEdit.Normal,str(fuzzyTolerance))
    if reply[1]:
            # user clicked OK
            replyText = reply[0]
            fuzzyTolerance = float (replyText)
    else:
        # user clicked Cancel
        replyText = reply[0] # which will be "" if they clicked Cancel
    doc = FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    sel = FreeCADGui.Selection.getSelection()
    if len(sel)==2:
        if 0:
            doc.addObject("Part::Cut","Cut")
            added = doc.ActiveObject
            added.Base = sel[0]
            added.Tool = sel[1]
        else:
            shapeBase = sel[0].Shape
            shapeTool = sel[1].Shape      
            result_shape = shapeBase.cut(shapeTool, fuzzyTolerance)
            Part.show(result_shape)
            added = doc.ActiveObject
        docG.getObject(sel[0].Name).Visibility=False
        docG.getObject(sel[1].Name).Visibility=False
        docG.getObject(added.Name).ShapeColor=docG.getObject(sel[0].Name).ShapeColor
        docG.getObject(added.Name).Transparency=docG.getObject(sel[0].Name).Transparency
        docG.getObject(added.Name).DisplayMode=docG.getObject(sel[0].Name).DisplayMode
        added.Label = 'CutFuzzy'
        doc.recompute()
##
def fuzzyUnion():
    import Part
    global fuzzyTolerance
    
    fuzzyTolerance = 0.01
    reply = QtGui.QInputDialog.getText(None, "Tolerance","Fuzzy Tolerance",QtGui.QLineEdit.Normal,str(fuzzyTolerance))
    if reply[1]:
            # user clicked OK
            replyText = reply[0]
            fuzzyTolerance = float (replyText)
    else:
        # user clicked Cancel
        replyText = reply[0] # which will be "" if they clicked Cancel
    doc = FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    sel = FreeCADGui.Selection.getSelection()
    shapes = []
    for s in sel[1:]:
        shapes.append(s.Shape)
    c = sel[0].Shape.multiFuse(shapes, fuzzyTolerance)
    Part.show(c)
    added = doc.ActiveObject
    for s in sel:
        docG.getObject(s.Name).Visibility=False
    docG.getObject(added.Name).ShapeColor=docG.getObject(sel[0].Name).ShapeColor
    docG.getObject(added.Name).Transparency=docG.getObject(sel[0].Name).Transparency
    docG.getObject(added.Name).DisplayMode=docG.getObject(sel[0].Name).DisplayMode
    added.Label = 'UnionFuzzy'
    doc.recompute()
##
def fuzzyCommon():
    import Part
    global fuzzyTolerance
    
    fuzzyTolerance = 0.01
    reply = QtGui.QInputDialog.getText(None, "Tolerance","Fuzzy Tolerance",QtGui.QLineEdit.Normal,str(fuzzyTolerance))
    if reply[1]:
            # user clicked OK
            replyText = reply[0]
            fuzzyTolerance = float (replyText)
    else:
        # user clicked Cancel
        replyText = reply[0] # which will be "" if they clicked Cancel
    doc = FreeCAD.ActiveDocument
    docG = FreeCADGui.ActiveDocument
    sel = FreeCADGui.Selection.getSelection()
    shapes = []
    for s in sel[1:]:
        shapes.append(s.Shape)
    c = sel[0].Shape.common(shapes, fuzzyTolerance)
    Part.show(c)
    added = doc.ActiveObject
    for s in sel:
        docG.getObject(s.Name).Visibility=False
    docG.getObject(added.Name).ShapeColor=docG.getObject(sel[0].Name).ShapeColor
    docG.getObject(added.Name).Transparency=docG.getObject(sel[0].Name).Transparency
    docG.getObject(added.Name).DisplayMode=docG.getObject(sel[0].Name).DisplayMode
    added.Label = 'CommonFuzzy'
    doc.recompute()
##