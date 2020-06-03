#***************************************************************************
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
"""Provide the object code for Arch make_opening_template function.

The opening template is an App::Part object containing the definition of the
opening filling, being it a door, a window, a skylight or whatever else.
This object can be used to create many opening types, that will be linked
inside the Opening objects.
"""
## @package make_opening_template
# \ingroup ARCH
# \brief Provide the object code for Arch make_opening_template function.

import FreeCAD as App

# from archutils import IFCutils


def make_template_opening(ifc_type="Window"):
    """
    make_template_opening(name)
    
    Create an App::Part object to serve as Window or Door object definition and
    customize it adding the necessary properties and base geometries.

    This object is meant to be istantiated by custom windows and doors types.

    The user may want to add more properties to the object, according to 
    specific needs.
    
    Parameters
    ----------
    ifc_type: string
        The IfcType of object, being "Window", "Door" or "Void".
    """

    if not App.ActiveDocument:
        App.Console.PrintError("No active document. Aborting\n")
        return

    template = App.ActiveDocument.addObject('App::Part', "Template" + ifc_type)

    # Geometry properties setup
    template.addProperty("App::PropertyLength", "OpeningHeight",
                       "Geometry", "Height of the opening")
    template.addProperty("App::PropertyLength", "OpeningWidth",
                       "Geometry", "Width of the opening")

    return template


def make_template_window():
    template = make_template_opening("Window")

    # properties setting
    template.Height = 1500
    template.Width = 800
    template.Type = "Arch_Opening"

    return template


def make_template_door():
    template = make_template_opening("Door")

    # properties setting
    template.Height = 1500
    template.Width = 800
    template.Type = "Arch_Opening"

    return template
