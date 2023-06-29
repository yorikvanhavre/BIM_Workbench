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

"""This module contains BIM wrappers for commands from other workbenches"""

import os
import FreeCAD
import DraftVecUtils
from BimTranslateUtils import *
from draftguitools import gui_dimensions
from draftguitools import gui_shape2dview


class BIM_Project:
    def __init__(self):
        try:
            import ifc_tools
        except:
            self.NativeIFC = False
        else:
            self.NativeIFC = True

    def GetResources(self):
        if self.NativeIFC:
            icon = os.path.join(
                os.path.dirname(__file__), "icons", "Arch_Project_IFC.svg"
            )
            descr = QT_TRANSLATE_NOOP(
                "BIM_Project", "Create an empty NativeIFC project"
            )
        else:
            icon = os.path.join(os.path.dirname(__file__), "icons", "Arch_Project.svg")
            descr = QT_TRANSLATE_NOOP("BIM_Project", "Create an empty BIM project")
        return {
            "Pixmap": icon,
            "MenuText": QT_TRANSLATE_NOOP("BIM_Project", "Project"),
            "ToolTip": descr,
        }

    def Activated(self):
        if self.NativeIFC:
            import ifc_tools

            project = ifc_tools.create_document(FreeCAD.ActiveDocument)
            project.Modified = True
            FreeCAD.ActiveDocument.recompute()
        else:
            import FreeCADGui

            FreeCADGui.runCommand("Arch_Project")


class BIM_Builder:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Part_Shapebuilder.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("Part_Builder", "Shape builder..."),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Part_Builder", "Advanced utility to create shapes"
            ),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Builder")


class BIM_Offset2D:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Part_Offset2D.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("Part_Offset2D", "2D Offset..."),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Part_Offset2D", "Utility to offset planar shapes"
            ),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Offset2D")


class BIM_Extrude:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Part_Extrude.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("Part_Extrude", "Extrude..."),
            "ToolTip": QT_TRANSLATE_NOOP("Part_Extrude", "Extrude a selected sketch"),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Extrude")


class BIM_Cut:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "Part_Cut.svg"),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Cut", "Difference"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Cut", "Make a difference between two shapes"
            ),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Cut")


class BIM_Fuse:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "Part_Fuse.svg"),
            "MenuText": QT_TRANSLATE_NOOP("Part_Fuse", "Union"),
            "ToolTip": QT_TRANSLATE_NOOP("Part_Fuse", "Make a union of several shapes"),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Fuse")


class BIM_Common:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Part_Common.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("Part_Common", "Intersection"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Part_Common", "Make an intersection of two shapes"
            ),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Common")


class BIM_Compound:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Part_Compound.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("Part_Compound", "Make compound"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Part_Compound", "Make a compound of several shapes"
            ),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_Compound")


class BIM_SimpleCopy:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(os.path.dirname(__file__), "icons", "Tree_Part.svg"),
            "MenuText": QT_TRANSLATE_NOOP("Part_SimpleCopy", "Create simple copy"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Part_SimpleCopy", "Create a simple non-parametric copy"
            ),
        }

    def Activated(self):
        import FreeCADGui
        import PartGui

        FreeCADGui.runCommand("Part_SimpleCopy")


class BIM_TDPage:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "techdraw-PageDefault.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_TDPage", "Page"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_TDPage", "Creates a new TechDraw page from a template"
            ),
        }

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        from PySide import QtCore, QtGui
        import TechDraw

        templatedir = FreeCAD.ParamGet(
            "User parameter:BaseApp/Preferences/Mod/BIM"
        ).GetString("TDTemplateDir", "")
        if not templatedir:
            templatedir = None
        filename = QtGui.QFileDialog.getOpenFileName(
            QtGui.QApplication.activeWindow(),
            translate("BIM", "Select page template"),
            templatedir,
            "SVG file (*.svg)",
        )
        if filename:
            filename = filename[0]
            name = os.path.splitext(os.path.basename(filename))[0]
            FreeCAD.ActiveDocument.openTransaction("Create page")
            page = FreeCAD.ActiveDocument.addObject("TechDraw::DrawPage", "Page")
            page.Label = name
            template = FreeCAD.ActiveDocument.addObject(
                "TechDraw::DrawSVGTemplate", "Template"
            )
            template.Template = filename
            template.Label = translate("BIM", "Template")
            page.Template = template
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetString(
                "TDTemplateDir", filename.replace("\\", "/")
            )
            for txt in ["scale", "Scale", "SCALE", "scaling", "Scaling", "SCALING"]:
                if txt in page.Template.EditableTexts:
                    val = page.Template.EditableTexts[txt]
                    if val:
                        if ":" in val:
                            val.replace(":", "/")
                        if "/" in val:
                            try:
                                page.Scale = eval(val)
                            except:
                                pass
                            else:
                                break
                        else:
                            try:
                                page.Scale = float(val)
                            except:
                                pass
                            else:
                                break
            else:
                page.Scale = FreeCAD.ParamGet(
                    "User parameter:BaseApp/Preferences/Mod/BIM"
                ).GetFloat("DefaultPageScale", 0.01)
            FreeCAD.ActiveDocument.recompute()


class BIM_TDArchView:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "techdraw-ArchView.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_TDArchView", "View"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_TDArchView",
                "Creates a TechDraw view from a section plane or 2D objects",
            ),
        }

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import FreeCADGui
        import Draft

        sections = []
        page = None
        drafts = []
        for obj in FreeCADGui.Selection.getSelection():
            t = Draft.getType(obj)
            if t == "SectionPlane":
                sections.append(obj)
            elif t == "TechDraw::DrawPage":
                page = obj
            else:
                drafts.append(obj)
        if not page:
            pages = FreeCAD.ActiveDocument.findObjects(Type="TechDraw::DrawPage")
            if pages:
                page = pages[0]
        if (not page) or ((not sections) and (not drafts)):
            FreeCAD.Console.PrintError(
                translate(
                    "BIM",
                    "No section view or draft objects selected, or no page selected, or no page found in document",
                )
                + "\n"
            )
            return
        FreeCAD.ActiveDocument.openTransaction("Create view")
        for section in sections:
            view = FreeCAD.ActiveDocument.addObject(
                "TechDraw::DrawViewArch", "ArchView"
            )
            view.Label = section.Label
            view.Source = section
            page.addView(view)
            if page.Scale:
                view.Scale = page.Scale
        for draft in drafts:
            view = FreeCAD.ActiveDocument.addObject(
                "TechDraw::DrawViewDraft", "DraftView"
            )
            view.Label = draft.Label
            view.Source = draft
            page.addView(view)
            if page.Scale:
                view.Scale = page.Scale
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


class BIM_ImagePlane:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Image_CreateImagePlane.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_ImagePlane", "Image plane"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_ImagePlane", "Creates a plane from an image"
            ),
        }

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import FreeCADGui
        from PySide import QtCore, QtGui

        try:
            import DraftTrackers
        except Exception:
            import draftguitools.gui_trackers as DraftTrackers

        self.tracker = DraftTrackers.rectangleTracker()
        self.basepoint = None
        self.opposite = None
        (filename, _filter) = QtGui.QFileDialog.getOpenFileName(
            QtGui.QApplication.activeWindow(),
            translate("BIM", "Select image"),
            None,
            translate("BIM", "Image file (*.png *.jpg *.bmp)"),
        )
        if filename:
            self.filename = filename
            im = QtGui.QImage(self.filename)
            self.proportion = float(im.height()) / float(im.width())
            if hasattr(FreeCADGui, "Snapper"):
                FreeCADGui.Snapper.getPoint(
                    callback=self.PointCallback, movecallback=self.MoveCallback
                )

    def MoveCallback(self, point, snapinfo):
        if point and self.basepoint and (point != self.basepoint):
            chord = point.sub(self.basepoint)
            length = DraftVecUtils.project(chord, self.tracker.u).Length
            height = length * self.proportion
            self.opposite = (
                FreeCAD.Vector(self.tracker.u)
                .multiply(length)
                .add(FreeCAD.Vector(self.tracker.v).multiply(height))
            )
            self.opposite = self.basepoint.add(self.opposite)
            self.tracker.update(self.opposite)

    def PointCallback(self, point, snapinfo):
        import FreeCADGui
        import Image

        if not point:
            # cancelled
            self.tracker.off()
            return
        elif not self.basepoint:
            # this is our first clicked point, nothing to do just yet
            self.basepoint = point
            self.tracker.setorigin(point)
            self.tracker.on()
            FreeCADGui.Snapper.getPoint(
                last=point, callback=self.PointCallback, movecallback=self.MoveCallback
            )
        else:
            # this is our second point
            self.tracker.off()
            midpoint = self.basepoint.add(
                self.opposite.sub(self.basepoint).multiply(0.5)
            )
            rotation = FreeCAD.DraftWorkingPlane.getRotation().Rotation
            diagonal = self.opposite.sub(self.basepoint)
            length = DraftVecUtils.project(diagonal, FreeCAD.DraftWorkingPlane.u).Length
            height = DraftVecUtils.project(diagonal, FreeCAD.DraftWorkingPlane.v).Length
            FreeCAD.ActiveDocument.openTransaction("Create image plane")
            image = FreeCAD.activeDocument().addObject(
                "Image::ImagePlane", "ImagePlane"
            )
            image.Label = os.path.splitext(os.path.basename(self.filename))[0]
            image.ImageFile = self.filename
            image.Placement = FreeCAD.Placement(midpoint, rotation)
            image.XSize = length
            image.YSize = height
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()


class BIM_DimensionAligned(gui_dimensions.Dimension):
    def __init__(self):
        super(BIM_DimensionAligned, self).__init__()

    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_DimensionAligned.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_DimensionAligned", "Aligned dimension"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_DimensionAligned", "Create an aligned dimension"
            ),
            "Accel": "D, I",
        }


class BIM_DimensionHorizontal(gui_dimensions.Dimension):
    def __init__(self):
        super(BIM_DimensionHorizontal, self).__init__()

    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_DimensionHorizontal.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "BIM_DimensionHorizontal", "Horizontal dimension"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_DimensionHorizontal", "Create an horizontal dimension"
            ),
            "Accel": "D, H",
        }

    def Activated(self):
        self.dir = FreeCAD.DraftWorkingPlane.u
        super(BIM_DimensionHorizontal, self).Activated()


class BIM_DimensionVertical(gui_dimensions.Dimension):
    def __init__(self):
        super(BIM_DimensionVertical, self).__init__()

    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_DimensionVertical.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "BIM_DimensionVertical", "Vertical dimension"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_DimensionVertical", "Create a vertical dimension"
            ),
            "Accel": "D, V",
        }

    def Activated(self):
        self.dir = FreeCAD.DraftWorkingPlane.v
        super(BIM_DimensionVertical, self).Activated()


class BIM_Text:
    def GetResources(self):
        import Draft_rc

        return {
            "Pixmap": "Draft_Text",
            "MenuText": QT_TRANSLATE_NOOP("BIM_Text", "Text"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Text", "Create a text in the current 3D view or TechDraw page"
            ),
            "Accel": "T, E",
        }

    def Activated(self):
        import FreeCADGui
        import draftutils.utils as utils

        self.view = FreeCADGui.ActiveDocument.ActiveView
        if hasattr(self.view, "getPage") and self.view.getPage():
            self.text = ""
            FreeCADGui.draftToolBar.sourceCmd = self
            FreeCADGui.draftToolBar.taskUi()
            FreeCADGui.draftToolBar.textUi()
        else:
            FreeCADGui.runCommand("Draft_Text")

    def createObject(self):
        import TechDraw

        if self.text:
            page = self.view.getPage()
            pagescale = page.Scale
            if not pagescale:
                pagescale = 1
            anno = FreeCAD.ActiveDocument.addObject(
                "TechDraw::DrawViewAnnotation", "Annotation"
            )
            anno.Text = self.text
            page.addView(anno)
            param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
            anno.TextSize = param.GetFloat("textheight", 10) * pagescale
            anno.Font = param.GetString("textfont", "Sans")
            c = param.GetUnsigned("DefaultTextColor", 255)
            r = ((c >> 24) & 0xFF) / 255.0
            g = ((c >> 16) & 0xFF) / 255.0
            b = ((c >> 8) & 0xFF) / 255.0
            anno.TextColor = (r, g, b)
            self.finish()

    def finish(self, arg=False):
        import FreeCADGui

        FreeCADGui.draftToolBar.sourceCmd = None
        FreeCADGui.draftToolBar.offUi()


class BIM_Shape2DView(gui_shape2dview.Shape2DView):
    def GetResources(self):
        d = super(BIM_Shape2DView, self).GetResources()
        d["Pixmap"] = "Arch_BuildingPart_Tree"
        d["MenuText"] = QT_TRANSLATE_NOOP("BIM_Shape2DView", "Shape-based view")
        return d
