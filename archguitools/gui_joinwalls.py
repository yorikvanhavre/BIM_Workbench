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

"""Provide the Arch_Wall command."""

## @package gui_wall
# \ingroup ARCH
# \brief Provide the Arch_Wall command used in Arch to create an Arch Wall.

import os
import FreeCAD as App
import FreeCADGui as Gui
import Draft
from archmake.joinwalls import join_walls
from PySide import QtCore,QtGui

# ---------------------------------------------------------------------------
# this is just a very rough implementation to test the objects
# ---------------------------------------------------------------------------


class Arch_JoinWalls:
    """ Arch_JoinWalls command definition.
    """

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"..","icons","Arch_Wall_Experimental.svg"),
                'MenuText': "Join_Walls_EXPERIMENTAL",
                'ToolTip': "EXPERIMENTAL\nCorner join.\nSelect 2 walls to join them."}

    def IsActive(self):

        return not App.ActiveDocument is None

    def Activated(self):
        self.walls = Gui.Selection.getSelection()
        self.continue_mode = False

        if len(self.walls) == 2:
            try:
                self.join_walls()
            except:
                self.join_by_selection()
        else:
            self.join_by_selection()
    
    def join_walls(self):
        join_walls(self.walls[0], self.walls[1], "L")
        App.ActiveDocument.recompute()

    def join_by_selection(self):
        App.Console.PrintMessage("Select the first wall"+ "\n")
        self.walls = []
        self.callback = Gui.Selection.addObserver(self)

    def addSelection(self, doc, obj, sub, pnt):
        Gui.Selection.removeObserver(self)
        if len(self.walls) == 0:
            App.Console.PrintMessage("Select the second wall"+ "\n")
            self.walls.append(App.getDocument(doc).getObject(obj))
            self.callback = Gui.Selection.addObserver(self)
        elif len(self.walls) == 1:
            self.walls.append(App.getDocument(doc).getObject(obj))
            self.join_walls()
            self.walls = []
            if self.continue_mode:
                # TODO: fix continue mode according to Draft Commands
                self.callback = Gui.Selection.addObserver(self)
            else:
                self.finish()

    def finish(self):
        if self.callback:
            Gui.Selection.removeObserver(self.callback)
            

class Arch_ExtendWall(Arch_JoinWalls):
    """ Arch_ExtendWall command definition.
    """

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"..","icons","Arch_Wall_Experimental.svg"),
                'MenuText': "Extend_Walls_EXPERIMENTAL",
                'ToolTip': "EXPERIMENTAL\nExtend one wall to another.\nSelect first the wall that you want to\nextend and then the target wall."}

    def IsActive(self):

        return not App.ActiveDocument is None

    def join_walls(self):
        join_walls(self.walls[0], self.walls[1], "T")
        App.ActiveDocument.recompute()


Gui.addCommand('Arch_JoinWalls', Arch_JoinWalls())
Gui.addCommand('Arch_ExtendWall', Arch_ExtendWall())
