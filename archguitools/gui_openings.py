#***************************************************************************
#*   Copyright (c) 2011 Yorik van Havre <yorik@uncreated.net>              *
#*   Copyright (c) 2020 Carlo Pavan                                        *
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
"""Provide the Arch_Opening, Arch_Door, Arch_Window commands.
"""
## @package gui_openings
# \ingroup ARCH
# \brief Provide the Arch_Opening, Arch_Door, Arch_Window commands commands.

from PySide import QtGui

import FreeCAD as App
import FreeCADGui as Gui

import Draft
import archmake.make_opening as make_opening

import archmake.make_opening_template as make_opening_template

import archmake.make_opening_type as make_opening_type

from draftutils.translate import translate

from draftguitools.gui_base import GuiCommandBase
import draftguitools.gui_trackers as trackers


# ---------------------------------------------------------------------------
# Arch Opening, Window, Door commands
# ---------------------------------------------------------------------------

class Arch_Openings(GuiCommandBase):
    """The Arch Openings command definition.
    This class is inherited and used by the Arch_Opening, Arch_Window, Arch_Door commands.
    """

    def GetResources(self):
        """To be override by derived commands."""
        pass

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        self.host = None

        sel = Gui.Selection.getSelection()
        if len(sel) == 1:
            self.host = sel[0]
            # TODO: Check if host is a correct object
        elif len(sel) > 1:
            print("select only one host object")
            self.finish()

        self.tracker = trackers.boxTracker()
        self.tracker.length(self.opening_width)
        self.tracker.width(self.host_thickness)
        self.tracker.height(self.opening_height)
        self.tracker.on()

        Gui.Snapper.getPoint(callback=self.getPoint, movecallback=self.update, extradlg=self.taskbox())

    def getPoint(self, point=None, host=None):
        """This function is called by the snapper when the user clicks a 3d point.
        """
        self.tracker.finalize()

        if point is None:
            return

        if self.host is not None:
            # if something was selected, override callback host
            host = self.host
        elif self.host is None:
            self.host = host

        point = point.add(App.Vector(0, 0, self.sill_height))

        if host:
            self.pl.Base = host.getGlobalPlacement().inverse().multVec(point)
            self.pl.Base.y = 0.0
            self.pl.Base.z = self.sill_height
            if hasattr(host, "Width"):
                self.host_thickness = host.Width
        else:
            self.pl.Base = point

        self.finish()


    def update(self, point, info):
        """This function is called by the Snapper when the mouse is moved.
        """

        delta = App.Vector(0, 0, self.opening_height/2 + self.sill_height)
        rot = App.Rotation()
        if info:
            o = App.ActiveDocument.getObject(info['Object'])
            if o and hasattr(o, "getGlobalPlacement"):
                rot = o.getGlobalPlacement().Rotation
                #if hasattr(o, "Proxy") and hasattr(o.Proxy, "get_core_axis"):
                #    point.projectToLine(o.getGlobalPlacement().multVec(o.Proxy.get_first_point(o)), 
                #                        o.getGlobalPlacement().multVec(o.Proxy.get_last_point(o)))
        self.tracker.setRotation(rot)
        self.tracker.pos(point.add(delta))


    def taskbox(self):
        """Returns the opening taskbox widget. 
        Used by the snapper to append the widget to the task panel. 
        """

        w = QtGui.QWidget()
        ui = Gui.UiLoader()
        w.setWindowTitle(translate("Arch","Opening options"))
        grid = QtGui.QGridLayout(w)
        return w

    def finish(self):
        pass


class Arch_Opening(Arch_Openings):
    """The Arch Opening command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Arch_Window',
                'MenuText': "Opening_EXPERIMENTAL",
                'Accel': "W, A",
                'ToolTip': "EXPERIMENTAL\nCreates an Opening object"}

    def Activated(self):
        self.insert_point = App.Vector(0,0,0)
    
        self.pl = App.Placement()
        self.host = None

        self.opening_width = 1000.0
        self.opening_height = 1400.0
        self.sill_height = 0.0
        self.host_thickness = 500.0

        super(Arch_Opening, self).Activated()

    def finish(self):
        super(Arch_Opening, self).finish()
        App.ActiveDocument.openTransaction("Create Window")

        opening = make_opening.make_opening(self.opening_width,
                                            self.opening_height,
                                            self.host_thickness,
                                            self.sill_height
                                            )
        opening.Placement = self.pl
        if self.host:
            self.host.addObject(opening)
            
        App.ActiveDocument.commitTransaction()
        App.ActiveDocument.recompute()


class Arch_Window(Arch_Openings):
    """The Arch Window command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Arch_Window',
                'MenuText': "Window_EXPERIMENTAL",
                'Accel': "W, A",
                'ToolTip': "EXPERIMENTAL\nCreates an Opening object filled with a Window"}

    def Activated(self):
        self.insert_point = App.Vector(0,0,0)
    
        self.pl = App.Placement()
        self.host = None

        self.opening_width = 1000.0
        self.opening_height = 1400.0
        self.host_thickness = 500.0
        self.sill_height = 1000.0

        super(Arch_Window, self).Activated()

    def finish(self):
        super(Arch_Window, self).finish()
        App.ActiveDocument.openTransaction("Create Window")

        opening = make_opening.make_opening_window(self.opening_width,
                                                   self.opening_height,
                                                   self.host_thickness,
                                                   self.sill_height
                                                   )
        opening.Placement = self.pl
        if self.host:
            self.host.addObject(opening)
            
        App.ActiveDocument.commitTransaction()
        App.ActiveDocument.recompute()


class Arch_Door(Arch_Openings):
    """The Arch Door command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Arch_Window',
                'MenuText': "Door_EXPERIMENTAL",
                'Accel': "W, A",
                'ToolTip': "EXPERIMENTAL\nCreates an Opening object filled with a Door"}

    def Activated(self):
        self.insert_point = App.Vector(0,0,0)
    
        self.pl = App.Placement()
        self.host = None

        self.opening_width = 1000.0
        self.opening_height = 2000.0
        self.host_thickness = 500.0
        self.sill_height = 0.0

        super(Arch_Door, self).Activated()

    def finish(self):
        super(Arch_Door, self).finish()
        App.ActiveDocument.openTransaction("Create Window")

        opening = make_opening.make_opening_door(self.opening_width,
                                                 self.opening_height,
                                                 self.host_thickness,
                                                 self.sill_height
                                                 )
        opening.Placement = self.pl
        if self.host:
            self.host.addObject(opening)
            
        App.ActiveDocument.commitTransaction()
        App.ActiveDocument.recompute()


# ---------------------------------------------------------------------------
# Arch Door and Window Template creation commands
# ---------------------------------------------------------------------------

class Arch_Window_Template(GuiCommandBase):
    """The Arch_Window_Template command definition.
    """

    def GetResources(self):
        return {'MenuText': "Template Window (EXPERIMENTAL)",
                'ToolTip': "EXPERIMENTAL\nCreate an empty Template Window"}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        make_opening_template.make_template_window()


class Arch_Door_Template(GuiCommandBase):
    """The Arch_Door_Template command definition.
    """

    def GetResources(self):
        return {'MenuText': "Template Door (EXPERIMENTAL)",
                'ToolTip': "EXPERIMENTAL\nCreate an empty Template Window"}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        make_opening_template.make_template_door()


# ---------------------------------------------------------------------------
# Arch Door and Window Type creation commands
# ---------------------------------------------------------------------------

class Arch_Opening_Type(GuiCommandBase):
    """The Arch_Window_Type command definition.
    """

    def GetResources(self):
        return {'MenuText': "Type Window (EXPERIMENTAL)",
                'ToolTip': "EXPERIMENTAL\nCreate a Window Type from a preselected Template Window"}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        self.template = None

        sel = Gui.Selection.getSelection()
        if len(sel) == 1:
            self.template = sel[0]
            # TODO: Check if host is a correct object
        elif len(sel) > 1:
            print("select only one template object")

        self.finish()

    def finish(self):
        """To be override by Arch_Window_Type and Arch_Door_Type commands.
        """
        pass

class Arch_Window_Type(Arch_Opening_Type):
    """The Arch_Window_Type command definition.
    """

    def GetResources(self):
        return {'MenuText': "Type Window (EXPERIMENTAL)",
                'ToolTip': "EXPERIMENTAL\nCreate a Window Type from a preselected Template Window"}

    def finish(self):
        make_opening_type.make_type_window(self.template)


class Arch_Door_Type(Arch_Opening_Type):
    """The Arch_Door_Type command definition.
    """

    def GetResources(self):
        return {'MenuText': "Type Door (EXPERIMENTAL)",
                'ToolTip': "EXPERIMENTAL\nCreate a Door Type from a preselected Template Door"}

    def finish(self):
        make_opening_type.make_type_door(self.template)


Gui.addCommand('Arch_Window_Template', Arch_Window_Template())
Gui.addCommand('Arch_Door_Template', Arch_Door_Template())

Gui.addCommand('Arch_Window_Type', Arch_Window_Type())
Gui.addCommand('Arch_Door_Type', Arch_Door_Type())

Gui.addCommand('Arch_Opening', Arch_Opening())
Gui.addCommand('Arch_Door2', Arch_Door())
Gui.addCommand('Arch_Window2', Arch_Window())
