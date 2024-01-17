# ***************************************************************************
# *   Copyright (c) 2020 Carlo Pavan                                        *
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
"""Provide the object code for Arch View.
This object is a spaghetti Frankenstein of various code written by Yorik.
"""
## @package archview
# \ingroup ARCH
# \brief Provide the object code for Arch View.

from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCAD as App


class ArchView(object):
    """
    A prototype for a new wall object for the Arch Workbench
    """

    def __init__(self, obj=None):
        # print("running wall object init method\n")
        if obj:
            # print("running obj init method")

            obj.Proxy = self
            self.Object = obj
            self.attach(obj)
            self.execute(obj)

        self.Type = "Arch_View"

    def set_properties(self, obj):
        pl = obj.PropertiesList
        if not "Placement" in pl:
            _tip = "The placement of this object"
            obj.addProperty(
                "App::PropertyPlacement",
                "Placement",
                "Base",
                QT_TRANSLATE_NOOP("App::Property", _tip),
            )

        if not "Shape" in pl:
            obj.addProperty(
                "Part::PropertyPartShape",
                "Shape",
                "Base",
                QT_TRANSLATE_NOOP("App::Property", "The shape of this object"),
            )

        if not "Objects" in pl:
            obj.addProperty(
                "App::PropertyLinkListGlobal",
                "Objects",  # changed to global
                "Section Plane",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The objects that must be considered by this section plane. Empty means the whole document.",
                ),
            )

        if not "OnlySolids" in pl:
            obj.addProperty(
                "App::PropertyBool",
                "OnlySolids",
                "Section Plane",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "If false, non-solids will be cut too, with possible wrong results.",
                ),
            )
            obj.OnlySolids = True

        if not "Clip" in pl:
            obj.addProperty(
                "App::PropertyBool",
                "Clip",
                "Section Plane",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "If True, resulting views will be clipped to the section plane area.",
                ),
            )

        if not "UseMaterialColorForFill" in pl:
            obj.addProperty(
                "App::PropertyBool",
                "UseMaterialColorForFill",
                "Section Plane",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "If true, the color of the objects material will be used to fill cut areas.",
                ),
            )
            obj.UseMaterialColorForFill = False

        if not "GenerateSectionGeometry" in pl:
            obj.addProperty(
                "App::PropertyBool",
                "GenerateSectionGeometry",
                "Geometry",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "If true, a new object is generated to display the section cut shape.",
                ),
            )
            obj.GenerateSectionGeometry = False

        if not "SectionGeometry" in pl:
            obj.addProperty(
                "App::PropertyLinkChild",
                "SectionGeometry",
                "Geometry",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "If true, a new object is generated to display the section cut shape.",
                ),
            )

        self.Type = "SectionPlane"

    def attach(self, obj):
        # print("running" + obj.Name + "attach() method\n")
        obj.addExtension("App::GeoFeatureGroupExtensionPython")
        self.set_properties(obj)

    def execute(self, obj):
        """Compute the wall shape as boolean operations among the children objects"""
        # print("running " + obj.Name + " execute() method\n")
        # get wall base shape from BaseGeometry object
        import Part

        l = 1
        h = 1
        if obj.ViewObject:
            if hasattr(obj.ViewObject, "DisplayLength"):
                l = obj.ViewObject.DisplayLength.Value
                h = obj.ViewObject.DisplayHeight.Value
            elif hasattr(obj.ViewObject, "DisplaySize"):
                # old objects
                l = obj.ViewObject.DisplaySize.Value
                h = obj.ViewObject.DisplaySize.Value
        p = Part.makePlane(l, h, App.Vector(l / 2, -h / 2, 0), App.Vector(0, 0, -1))
        # make sure the normal direction is pointing outwards, you never know what OCC will decide...
        if (
            p.normalAt(0, 0).getAngle(
                obj.Placement.Rotation.multVec(App.Vector(0, 0, 1))
            )
            > 1
        ):
            p.reverse()
        p.Placement = obj.Placement
        obj.Shape = p

    def onBeforeChange(self, obj, prop):
        """this method is activated before a property changes"""
        return

    def onChanged(self, obj, prop):
        """this method is activated when a property changes"""
        if prop in [
            "Placement",
            "Objects",
            "OnlySolids",
            "UseMaterialColorForFill",
            "Clip",
        ]:
            self.svgcache = None
            self.shapecache = None

        if (
            prop in ("GenerateSectionGeometry", "SectionGeometry")
            and "GenerateSectionGeometry" in obj.PropertiesList
            and "SectionGeometry" in obj.PropertiesList
        ):
            self.setSectionGeometry(obj)

        if prop == "Objects" and hasattr(obj, "Objects"):
            if hasattr(obj, "GenerateSectionGeometry") and obj.GenerateSectionGeometry:
                self.recomputeSectionGeometry(obj)

    def getNormal(self, obj):
        return obj.Shape.Faces[0].normalAt(0, 0)

    # Create section cut ++++++++++++++++++++++++++++++++++++++++++++++++++++

    def setSectionGeometry(self, obj):
        if obj.GenerateSectionGeometry:
            if obj.SectionGeometry:
                self.recomputeSectionGeometry(obj)
            else:
                return self.createCutObject(obj)
        else:
            if obj.SectionGeometry:
                App.ActiveDocument.removeObject(obj.SectionGeometry.Name)

    def createCutObject(self, obj):
        cut_object = App.ActiveDocument.addObject("Part::Feature", "SectionCut")
        obj.addObject(cut_object)
        obj.SectionGeometry = cut_object
        if App.GuiUp:
            cut_object.ViewObject.Selectable = False

    def recomputeSectionGeometry(self, obj):
        if obj.Objects is None or len(obj.Objects) == 0:
            return
        if obj.Visibility == False:
            return
        if App.GuiUp and obj.ViewObject.DisplayMode != "Group":
            return

        import Part
        import Drawing

        section_plane = Part.makePlane(10000000.0, 10000000.0)
        section_plane.Placement.Base.x = -5000000.0
        section_plane.Placement.Base.y = -5000000.0
        npl = section_plane.Placement.multiply(obj.getGlobalPlacement())
        section_plane.Placement = npl

        # shapes = Drawing.projectEx(obj.Objects[0].Shape, self.getNormal(obj))
        shapes = []
        for o in obj.Objects:
            s = o.Shape.copy()
            # s.Placement.multiply(o.getGlobalPlacement())
            shapes.append(s)
        shapes = Part.makeCompound(shapes)

        shape = shapes.section(section_plane)

        shape.Placement.multiply(obj.getGlobalPlacement().inverse())

        obj.SectionGeometry.Shape = shape

    # Other methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def onDocumentRestored(self, obj):
        self.Object = obj
        # obj.Proxy.Type needs to be re-setted every time the document is opened.
        obj.Proxy.Type = "Arch_View"

    def __getstate__(self):
        return

    def __setstate__(self, _state):
        return

    def dumps(self):
        return

    def loads(self, _state):
        return
