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
"""Provide the object code for Arch Wall viewprovider."""
## @package view_wall
# \ingroup ARCH
# \brief Provide the viewprovider code for Arch Wall.

import os
from PySide import QtCore,QtGui
from pivy import coin

import FreeCAD as App

import Part

from archviewproviders.view_base import ViewProviderShapeGroup


class ViewProviderWall(ViewProviderShapeGroup):
    
    def __init__(self, vobj=None):
        super(ViewProviderWall, self).__init__(vobj)

    def getIcon(self):
        """Return the path to the appropriate icon.

        Return the Arch wall icon.

        Returns
        -------
        str
            Path to the appropriate icon .svg file.
        """ 
        return os.path.join(os.path.dirname(__file__),"..","icons","Arch_Wall_Experimental.svg")

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def onChanged(self, vobj, prop):
        super(ViewProviderWall, self).onChanged(vobj, prop)
    
    def setupContextMenu(self, vobj, menu):
        """
        Setup context menu actions:
        - Flip wall (this is not implemented yet)
        """
        action1 = QtGui.QAction("Flip wall", menu)
        QtCore.QObject.connect(action1,QtCore.SIGNAL("triggered()"),lambda f=vobj.Object.Proxy.flip_wall, arg=vobj.Object:f(arg))
        menu.addAction(action1)

    def onDelete(self, vobj, subelements): # subelements is a tuple of strings
        delete_ok = super(ViewProviderWall, self).onDelete(vobj, subelements)

        if delete_ok:
            vobj.Object.Proxy.remove_linked_walls_references(vobj.Object)
            return True
