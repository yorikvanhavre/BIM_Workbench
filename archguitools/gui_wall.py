# ***************************************************************************
# *   Copyright (c) 2011 Yorik van Havre <yorik@uncreated.net>              *
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

"""Provide the Arch_Wall command."""

## @package gui_wall
# \ingroup ARCH
# \brief Provide the Arch_Wall command used in Arch to create an Arch Wall.

import os

import FreeCAD as App
import FreeCADGui as Gui

import Draft
import DraftVecUtils

import archmake.make_wall as make_wall
from PySide import QtCore, QtGui

import draftguitools.gui_trackers as DraftTrackers


class Arch_Wall:
    """Arch_Wall command definition.

    This is just a very rough implementation to test the objects.
    """

    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "..", "icons", "Arch_Wall_Experimental.svg"
            ),
            "MenuText": "Wall_EXPERIMENTAL",
            "Accel": "W, A",
            "ToolTip": "EXPERIMENTAL\nCreate a wall object from scratch.",
        }

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        self.points = []
        self.join_first = None
        self.join_last = None
        self.set_default_parameters()
        self.tracker = DraftTrackers.boxTracker()
        self.setup_snapper_callback()

    def set_default_parameters(self):
        p = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
        self.Align = ["Center", "Left", "Right"][p.GetInt("WallAlignment", 0)]
        self.MultiMat = None
        self.Length = None
        self.lengthValue = 0
        self.continueCmd = False
        self.Width = p.GetFloat("WallWidth", 200)
        self.Height = p.GetFloat("WallHeight", 3000)

    def setup_snapper_callback(self):
        Gui.Snapper.getPoint(
            last=self.points[0] if len(self.points) == 1 else None,
            callback=self.getPoint,
            movecallback=self.on_moved,
            extradlg=self.taskbox(),
            title="Pick point:",
            mode="line",
        )

    def getPoint(self, point=None, obj=None):
        """This function is called by the snapper when it has a 3D point."""
        if len(self.points) == 0:
            self.on_picked_first_point(point, obj)
            self.setup_snapper_callback()
        elif len(self.points) == 1:
            # picked last point
            self.on_picked_last_point(point, obj)

    def on_picked_first_point(self, point=None, obj=None):
        """This function is called when user input first point."""
        self.points.append(point)
        # set tracker
        self.tracker.width(self.Width)
        self.tracker.height(self.Height)
        self.tracker.on()
        # search for a clicked wall
        self.join_first = self.get_picked_wall()

    def on_moved(self, point, info):
        """This function is called when user move the mouse after first input."""
        if len(self.points) != 1:
            return
        b = self.points[0]
        n = App.DraftWorkingPlane.axis
        bv = point.sub(b)
        dv = bv.cross(n)
        dv = DraftVecUtils.scaleTo(dv, self.Width / 2)
        if self.Align == "Center":
            self.tracker.update([b, point])
        elif self.Align == "Left":
            self.tracker.update([b.add(dv), point.add(dv)])
        else:
            dv = dv.negative()
            self.tracker.update([b.add(dv), point.add(dv)])

    def on_picked_last_point(self, point=None, obj=None):
        """This function is called when user input last point."""
        self.points.append(point)
        self.tracker.finalize()
        # search for a clicked wall
        self.join_last = self.get_picked_wall()
        # create the wall
        self.commit()

    def get_picked_wall(self):
        v = Gui.activeDocument().activeView()
        pos = v.getCursorPos()
        info = v.getObjectInfo(pos)
        if info:
            return info["Object"]
        else:
            return None

    def commit(self):
        """Create the wall."""
        import Draft

        App.ActiveDocument.openTransaction("Create Wall")
        wall = make_wall.makeWallFromPoints(
            p1=self.points[0],
            p2=self.points[1],
            width=self.Width,
            height=self.Height,
            align="Center",
            name="Wall",
        )
        # Apply end joining if present
        if self.join_first != self.join_last:
            if self.join_first:
                wall.JoinFirstEndTo = self.join_first
                """target = App.ActiveDocument.getObject(self.join_first) # TODO: Fix this
                if target:
                    point_on_target_axis = target.Proxy.get_point_on_axis(target, self.points[0])
                    if point_on_target_axis.sub(target.Proxy.get_first_point(target)).Length < target.Width/2:
                        target.JoinFirstEndTo = wall.Name
                    elif point_on_target_axis.sub(target.Proxy.get_last_point(target)).Length < target.Width/2:
                        target.JoinLastEndTo = wall.Name"""
            if self.join_last:
                wall.JoinLastEndTo = self.join_last
        Draft.autogroup(wall)
        App.ActiveDocument.commitTransaction()
        App.ActiveDocument.recompute()

    def taskbox(self):
        "sets up a taskbox widget"

        w = QtGui.QWidget()
        ui = Gui.UiLoader()
        w.setWindowTitle("Wall options")
        grid = QtGui.QGridLayout(w)

        matCombo = QtGui.QComboBox()
        matCombo.addItem("Wall Presets...")
        matCombo.setToolTip(
            "This list shows all the MultiMaterials objects of this document. Create some to define wall types."
        )
        self.multimats = []
        self.MultiMat = None
        for o in App.ActiveDocument.Objects:
            if Draft.getType(o) == "MultiMaterial":
                self.multimats.append(o)
                matCombo.addItem(o.Label)
        if hasattr(App, "LastArchMultiMaterial"):
            for i, o in enumerate(self.multimats):
                if o.Name == App.LastArchMultiMaterial:
                    matCombo.setCurrentIndex(i + 1)
                    self.MultiMat = o
        grid.addWidget(matCombo, 0, 0, 1, 2)

        label5 = QtGui.QLabel("Length")
        self.Length = ui.createWidget("Gui::InputField")
        self.Length.setText("0.00 mm")
        grid.addWidget(label5, 1, 0, 1, 1)
        grid.addWidget(self.Length, 1, 1, 1, 1)
        return w


Gui.addCommand("Arch_Wall2", Arch_Wall())
