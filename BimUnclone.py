# -*- coding: utf8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2017 Yorik van Havre <yorik@uncreated.net>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

"""This module contains FreeCAD commands for the BIM workbench"""

import FreeCAD,FreeCADGui,Arch,Draft,Part,os

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Unclone:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Unclone.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Unclone", "Unclone"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Unclone", "Reconnewobjs an independent extrusion from a selected face"),
               }

    def IsActive(self):

        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False

    def Activated(self):

        # get selected object and face
        sel = FreeCADGui.Selection.getSelectionEx()

        if (len(sel) == 1) and (len(sel[0].SubObjects) == 1) and ("Face" in sel[0].SubElementNames[0]):

            sel = sel[0]
            obj = sel.Object
            name = obj.Name
            label = obj.Label

            fac = sel.SubObjects[0]

            # make this undoable
            FreeCAD.ActiveDocument.openTransaction("Unclone")

            # check if the face has holes or any of the edges is not a line
            wirable = True
            if len(fac.Wires) > 1:
                wirable = False
            else:
                for edge in fac.Edges:
                    if not isinstance(edge,(Part.Line,Part.LineSegment)):
                        # edge can be a spline, but even so be straight. Simple check if tangents are identical at first and last verts...
                        if edge.tangentAt(edge.FirstParameter).getAngle(edge.tangentAt(edge.LastParameter)) > 0.0001:
                            wirable = False
                            break
            if wirable:
                # recompose the base wire
                verts = [v.Point for v in fac.Wires[0].OrderedVertexes]
                wir = Draft.makeWire(verts,closed=True)
            else:
                # there are curves. Unable to make a wire. We just use the base face
                wir = FreeCAD.ActiveDocument.addObject("Part::Feature","Face")
                wir.Shape = fac

            # make the new object
            if Draft.getType(obj) == "Wall":
                newobj = Arch.makeWall(wir)
            elif Draft.getType(obj) == "Panel":
                newobj = Arch.makePanel(wir)
            else:
                newobj = Arch.makeStructure(wir)

            # deduce the normal and extrusion size
            norm = fac.normalAt(0,0).negative()
            newobj.Normal = norm
            for e in obj.Shape.Edges:
                if abs(e.tangentAt(0).getAngle(norm)) < 0.0001:
                    if hasattr(newobj,"Thickness"):
                        newobj.Thickness = e.Length
                    else:
                        newobj.Height = e.Length

            # set material
            if hasattr(obj,"Material") and obj.Material:
                newobj.Material = obj.Material
                
            # set role and class
            if hasattr(obj,"IfcRole"):
                newobj.IfcRole = obj.IfcRole
            if hasattr(obj,"StandardCode"):
                newobj.StandardCode = obj.StandardCode

            # find objects cloning or owning this one
            for parent in obj.InList:
                if hasattr(parent,"CloneOf") and (parent.CloneOf == obj):
                    parent.CloneOf = newobj
                    FreeCAD.Console.PrintMessage("Object "+parent.Label+" was a clone of this object and has been updated to the new object\n")
                if hasattr(parent,"Group") and (obj in parent.Group):
                    if hasattr(parent,"addObject"):
                        parent.addObject(newobj)
                    else:
                        g = parent.Group
                        g.append(newobj)
                        parent.Group = g

            # delete original object
            FreeCAD.ActiveDocument.removeObject(name)
            newobj.Label = label

            # commit changes
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()

        else:
            FreeCAD.Console.PrintError("Error: Please select exactly one base face\n")


FreeCADGui.addCommand('BIM_Unclone',BIM_Unclone())
