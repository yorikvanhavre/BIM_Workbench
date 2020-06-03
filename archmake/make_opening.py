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
"""Provide the object code for Arch make_opening function."""
## @package make_opening
# \ingroup ARCH
# \brief Provide the object code for Arch make_opening function.

import FreeCAD as App

from archobjects.opening import Opening 

if App.GuiUp:
    import FreeCADGui as Gui
    from archviewproviders.view_opening import ViewProviderOpening


def make_opening(width=1000, height=2000, host_thickness=500, z_offset=0):
    obj = App.ActiveDocument.addObject('Part::FeaturePython', 'Opening', Opening(), ViewProviderOpening(), True)
    obj.OpeningHeight = height
    obj.OpeningWidth = width
    obj.HostThickness = host_thickness
    obj.Placement.Base.z = z_offset
    return obj


def make_opening_window(width=900, height=1400, host_thickness=500, z_offset=1000):
    opening = make_opening(width, height, host_thickness, z_offset)
    opening.Label = "Window"
    opening.Filling = "Default Window"
    return opening


def make_opening_door(width=1000, height=2000, host_thickness=500, z_offset=0):
    opening = make_opening(width, height, host_thickness, z_offset)
    opening.Label = "Door"
    opening.Filling = "Default Door"
    return opening
