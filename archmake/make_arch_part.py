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
"""Provide the object code for Arch make_part function."""
## @package make_opening
# \ingroup ARCH
# \brief Provide the object code for Arch make_opening function.

import FreeCAD as App

from archobjects.opening import Opening

if App.GuiUp:
    import FreeCADGui as Gui
    from archviewproviders.view_opening import ViewProviderOpening


def makeArchPart(name="Ground Floor", over_level=None, height=3000):
    obj = App.ActiveDocument.addObject("App::Part", "BuildingPart")

    obj.Label = name

    _tip = "Describe."
    obj.addProperty("App::PropertyLinkGlobal", "OverLevel", "Level properties", _tip)
    obj.OverLevel = over_level

    _tip = "Describe."
    obj.addProperty("App::PropertyLength", "OverLevelOffset", "Level properties", _tip)

    _tip = "Describe."
    obj.addProperty("App::PropertyLength", "LevelHeight", "Level properties", _tip)
    obj.LevelHeight = height

    if obj.OverLevel:
        obj.Placement.Base.z = (
            obj.OverLevel.Placement.Base.z + obj.OverLevel.LevelHeight
        )

    return obj
