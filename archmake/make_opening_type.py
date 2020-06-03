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
"""Provide the object code for Arch make_opening_type function."""
## @package make_opening_type
# \ingroup ARCH
# \brief Provide the object code for Arch make_opening_type function.

import FreeCAD as App

# from archutils import IFCutils TODO: understand how to apply IFC Properties to C++ objects


def make_type_opening(ifc_type):
    """
    make_type_opening(template)
    
    Create an App::Part object to serve as Window or Door object definition and
    customize it adding the necessary properties and base geometries.

    This object is meant to be istantiated by custom windows and doors types.

    The user may want to add more properties to the object, according to 
    specific needs.
    
    Parameters
    ----------
    type: string
        The IfcType of object, being "Window", "Door" or "Void".
    """

    if not App.ActiveDocument:
        App.Console.PrintError("No active document. Aborting\n")
        return

    opening_type = App.ActiveDocument.addObject('PartDesign::SubShapeBinder', 'Type'+ifc_type)

    # SubShapeBinder properties setup
    if hasattr(opening_type, "BindCopyOnChange"):
        opening_type.BindCopyOnChange = "Mutated"
    if hasattr(opening_type, "Relative"):
        opening_type.Relative = False
    if hasattr(opening_type, "PartialLoad"):
        opening_type.PartialLoad = True

    if App.GuiUp:
        opening_type.ViewObject.UseBinderStyle = False

    return opening_type


def make_type_window(window_template=None, height=1350, width=800):
    """make_window_type

    Make a window_type object. Consider a window every opening in an Arch object
    that is filled by a fixed or openable frame, that is not usually meant for a person
    to pass through.
    """

    window_type = make_type_opening("Window")

    # properties setting
    if hasattr(window_type, "Support"):
        window_type.Support = window_template
    if hasattr(window_type, "OpeningHeight"):
        window_type.Height = height
    if hasattr(window_type, "OpeningWidth"):
       window_type.Width = width

    # Ifc properties setup
    #IFCutils.set_ifc_properties(window_type, "IfcType") # IfcType not supported yet, treated as a IfcProduct
    #window_type.IfcType = "Window"
    #IFCutils.setup_ifc_attributes(window_type)


def make_type_door(door_template=None, height=2100, width=800):
    """make_window_type

    Make a window_type object. Consider a door every opening in an Arch object
    that is filled by an openable frame and is meant for a person
    to pass through.
    """
    door_type = make_type_opening("Door")

    # properties setting
    if hasattr(door_type, "Support"):
        door_type.Support = door_template
    if hasattr(door_type, "OpeningHeight"):
        door_type.Height = height
    if hasattr(door_type, "OpeningWidth"):
       door_type.Width = width

    # Ifc properties setup
    #IFCutils.set_ifc_properties(door_type, "IfcType") # IfcType not supported yet, treated as a IfcProduct
    #door_type.IfcType = "Window"
    #IFCutils.setup_ifc_attributes(door_type)
