# -*- coding: utf8 -*-

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""This module contains FreeCAD commands for the BIM workbench"""

import os
import FreeCAD
from BimTranslateUtils import *
import ArchWindow
import DraftVecUtils
from draftguitools import gui_lines  # Line tool from Draft


class BIM_Help:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "BIM_Help.svg"),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Help", "BIM Help"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Help",
                "Opens the BIM help page on the FreeCAD documentation website",
            ),
        }

    def Activated(self):
        from PySide import QtCore, QtGui

        QtGui.QDesktopServices.openUrl("https://www.freecadweb.org/wiki/BIM_Workbench")


class BIM_Glue:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "BIM_Glue.svg"),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Glue", "Glue"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Glue", "Joins selected shapes into one non-parametric shape"
            ),
        }

    def IsActive(self):
        import FreeCADGui

        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False

    def Activated(self):
        import FreeCADGui

        sel = FreeCADGui.Selection.getSelection()
        if sel:
            rem = []
            shapes = []
            for obj in sel:
                if obj.isDerivedFrom("Part::Feature"):
                    if obj.Shape:
                        shapes.append(obj.Shape)
                        rem.append(obj.Name)
            import Part

            if shapes:
                comp = Part.makeCompound(shapes)
                FreeCAD.ActiveDocument.openTransaction("Glue")
                Part.show(comp)
                for name in rem:
                    FreeCAD.ActiveDocument.removeObject(name)
                FreeCAD.ActiveDocument.commitTransaction()


class BIM_Sketch:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "Sketch.svg"),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Sketch", "Sketch"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Sketch", "Creates a new sketch in the current working plane"
            ),
            "Accel": "S,K",
        }

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import FreeCADGui

        issnap = False
        if hasattr(FreeCAD, "DraftWorkingPlane"):
            FreeCAD.DraftWorkingPlane.setup()
        if hasattr(FreeCADGui, "Snapper"):
            FreeCADGui.Snapper.setGrid()
            issnap = FreeCADGui.Snapper.isEnabled("Grid")
        sk = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObject", "Sketch")
        if issnap and hasattr(sk.ViewObject, "GridSnap"):
            s = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt(
                "gridSize", 100
            )
            sk.ViewObject.GridSize = s
            sk.ViewObject.GridSnap = True
        sk.MapMode = "Deactivated"
        p = FreeCAD.DraftWorkingPlane.getPlacement()
        p.Base = FreeCAD.DraftWorkingPlane.position
        sk.Placement = p
        FreeCADGui.ActiveDocument.setEdit(sk.Name)
        FreeCADGui.activateWorkbench("SketcherWorkbench")


class BIM_WPView:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_WPView.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_WPView", "Working Plane View"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_WPView",
                "Aligns the view on the current item in BIM Views window or on the current working plane",
            ),
            "Accel": "9",
        }

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import FreeCADGui

        done = False
        try:
            import BimViews
        except ImportError:
            pass
        else:
            v = BimViews.findWidget()
            if v:
                i = v.tree.currentItem()
                if i:
                    # Aligning on current widget item
                    BimViews.show(i)
                    done = True
                elif hasattr(v, "lastSelected"):
                    BimViews.show(v.lastSelected)
                    # Aligning on stored widget item
                    done = True
            elif hasattr(FreeCAD, "DraftWorkingPlane"):
                if hasattr(FreeCAD.DraftWorkingPlane, "lastBuildingPart"):
                    BimViews.show(FreeCAD.DraftWorkingPlane.lastBuildingPart)
                    done = True
        if not done:
            # Aligning on current working plane
            c = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
            r = FreeCAD.DraftWorkingPlane.getRotation().Rotation.Q
            c.orientation.setValue(r)


class BIM_Convert:
    def GetResources(self):
        import Arch_rc

        return {
            "Pixmap": ":/icons/Arch_Component.svg",
            "MenuText": QT_TRANSLATE_NOOP("BIM_Convert", "Convert to BIM"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Convert", "Converts any object to a BIM component"
            ),
        }

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import FreeCADGui

        sel = FreeCADGui.Selection.getSelection()
        if sel:
            FreeCADGui.Control.showDialog(BIM_Convert_TaskPanel(sel))


class BIM_Convert_TaskPanel:
    def __init__(self, objs):
        from PySide import QtGui

        self.types = [
            "Wall",
            "Structure",
            "Rebar",
            "Window",
            "Stairs",
            "Roof",
            "Panel",
            "Frame",
            "Space",
            "Equipment",
            "Component",
        ]
        self.objs = objs
        self.form = QtGui.QListWidget()
        import Arch_rc

        for t in self.types:
            ti = t + "_Tree"
            tx = t
            if t == "Component":
                ti = t
                tx = "Generic component"
            i = QtGui.QListWidgetItem(QtGui.QIcon(":/icons/Arch_" + ti + ".svg"), tx)
            i.setToolTip(t)
            self.form.addItem(i)
        self.form.itemDoubleClicked.connect(self.accept)

    def accept(self, idx=None):
        i = self.form.currentItem()
        if i:
            import Arch

            FreeCAD.ActiveDocument.openTransaction("Convert to BIM")
            for o in self.objs:
                getattr(Arch, "make" + i.toolTip())(o)
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()
        if idx:
            from DraftGui import todo

            todo.delay(FreeCADGui.Control.closeDialog, None)
        return True


class BIM_Ungroup:
    def GetResources(self):
        import Draft_rc

        return {
            "Pixmap": ":/icons/Draft_AddToGroup.svg",
            "MenuText": QT_TRANSLATE_NOOP("BIM_Convert", "Remove from group"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Convert", "Removes this object from its parent group"
            ),
        }

    def Activated(self):
        import FreeCADGui

        sel = FreeCADGui.Selection.getSelection()
        first = True
        if sel:
            for obj in sel:
                for parent in obj.InList:
                    if parent.isDerivedFrom(
                        "App::DocumentObjectGroup"
                    ) or parent.hasExtension("App::GroupExtension"):
                        if obj in parent.Group:
                            if first:
                                FreeCAD.ActiveDocument.openTransaction("Ungroup")
                                first = False
                            if hasattr(parent, "removeObject"):
                                parent.removeObject(obj)
                            else:
                                g = parent.Group
                                g.remove(obj)
                                parent.Group = g
        if not first:
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()


class BIM_Door(ArchWindow._CommandWindow):
    def __init__(self):
        if hasattr(ArchWindow._CommandWindow, "__init__"):
            ArchWindow._CommandWindow.__init__(self)
        self.doormode = True

    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "BIM_Door.svg"),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Door", "Door"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Door", "Places a door at a given location"
            ),
            "Accel": "D,O",
        }


class BIM_Rewire:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_Rewire.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Rewire", "Rewire"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Rewire", "Recreates wires from selected objects"
            ),
            "Accel": "R,W",
        }

    def Activated(self):
        import FreeCADGui
        import Part
        import Draft
        import DraftGeomUtils

        objs = FreeCADGui.Selection.getSelection()
        names = []
        edges = []
        for obj in objs:
            if (
                hasattr(obj, "Shape")
                and hasattr(obj.Shape, "Edges")
                and obj.Shape.Edges
            ):
                edges.extend(obj.Shape.Edges)
                names.append(obj.Name)
        wires = DraftGeomUtils.findWires(edges)
        FreeCAD.ActiveDocument.openTransaction("Rewire")
        selectlist = []
        for wire in wires:
            if DraftGeomUtils.hasCurves(wire):
                nobj = FreeCAD.ActiveDocument.addObject("Part::Feature", "Wire")
                nobj.shape = wire
                selectlist.append(nobj)
            else:
                selectlist.append(
                    Draft.makeWire([v.Point for v in wire.OrderedVertexes])
                )
        for name in names:
            FreeCAD.ActiveDocument.removeObject(name)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCADGui.Selection.clearSelection()
        for obj in selectlist:
            FreeCADGui.Selection.addSelection(obj)
        FreeCAD.ActiveDocument.recompute()


class BIM_Leader(gui_lines.Line):
    def __init__(self):
        super(BIM_Leader, self).__init__(wiremode=True)

    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_Leader.svg"
            ),
            "Accel": "L, E",
            "MenuText": QT_TRANSLATE_NOOP("BIM_Leader", "Leader"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Leader", "Creates a polyline with an arrow at its endpoint"
            ),
        }

    def Activated(self):
        super(BIM_Leader, self).Activated(name="Leader", icon="Draft_Wire")

    def finish(self, closed=False, cont=False):
        import FreeCADGui

        self.removeTemporaryObject()
        if self.oldWP:
            FreeCAD.DraftWorkingPlane = self.oldWP
            if hasattr(Gui, "Snapper"):
                FreeCADGui.Snapper.setGrid()
                FreeCADGui.Snapper.restack()
            self.oldWP = None
        rot, sup, pts, fil = self.getStrings()
        if self.node:
            base = DraftVecUtils.toString(self.node[0])
        else:
            base = DraftVecUtils.toString(FreeCAD.Vector())
        color = FreeCAD.ParamGet(
            "User parameter:BaseApp/Preferences/Mod/Draft"
        ).GetUnsigned("DefaultTextColor", 255)
        r = ((color >> 24) & 0xFF) / 255.0
        g = ((color >> 16) & 0xFF) / 255.0
        b = ((color >> 8) & 0xFF) / 255.0
        cmd_list = [
            "pl = FreeCAD.Placement()",
            "pl.Rotation.Q = " + rot,
            "pl.Base = " + base,
            "points = " + pts,
            "leader = Draft.makeWire(points,placement=pl)",
            "leader.ViewObject.LineColor = "
            + str(
                (
                    r,
                    g,
                    b,
                )
            ),
            "leader.ViewObject.EndArrow = True",
            "Draft.autogroup(leader)",
            "FreeCAD.ActiveDocument.recompute()",
        ]
        FreeCADGui.addModule("Draft")
        self.commit(translate("BIM", "Create Leader"), cmd_list)
        super(gui_lines.Line, self).finish()
        if self.ui and self.ui.continueMode:
            self.Activated()


class BIM_Background:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_Background.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Background", "Toggle background"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Background",
                "Toggles the background of the 3D view between simple and gradient",
            ),
        }

    def Activated(self):
        import FreeCADGui

        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
        if param.GetBool("Simple", True):
            param.SetBool("Simple", False)
            param.SetBool("Gradient", True)
        else:
            param.SetBool("Simple", True)
            param.SetBool("Gradient", False)
        FreeCADGui.updateGui()


class BIM_MoveView:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_MoveView.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_MoveView", "Move view..."),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_MoveView", "Moves this view to an existing page"
            ),
        }

    def Activated(self):
        import FreeCADGui

        self.selection = FreeCADGui.Selection.getSelection()
        self.pages = FreeCAD.ActiveDocument.findObjects(Type="TechDraw::DrawPage")
        self.labels = [obj.Label for obj in self.pages]
        FreeCADGui.draftToolBar.sourceCmd = self
        FreeCADGui.draftToolBar.popupMenu(self.labels)

    def proceed(self, labelname):
        import FreeCADGui

        FreeCADGui.draftToolBar.sourceCmd = None
        if labelname in self.labels:
            page = self.pages[self.labels.index(labelname)]
            for view in self.selection:
                for p in view.InList:
                    if hasattr(p, "Views") and view in p.Views:
                        p.removeView(view)
                x = view.X
                y = view.Y
                page.addView(view)
                FreeCAD.ActiveDocument.recompute()
                view.X = x
                view.Y = y
