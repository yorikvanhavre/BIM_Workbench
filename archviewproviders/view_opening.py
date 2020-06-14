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
"""Provide the object code for Arch Opening viewprovider."""
## @package view_opening
# \ingroup ARCH
# \brief Provide the viewprovider code for Arch Opening.

import os
from archviewproviders.view_base import ViewProviderShapeGroup


class ViewProviderOpening(ViewProviderShapeGroup):
    
    def __init__(self, vobj=None):
        super(ViewProviderOpening, self).__init__(vobj)

    def getIcon(self):
        """Return the path to the appropriate icon.

        Return the Arch wall icon.

        Returns
        -------
        str
            Path to the appropriate icon .svg file.
        """ 
        return os.path.join(os.path.dirname(__file__),"..","icons","Arch_Opening_Experimental.svg")

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def onChanged(self, vobj, prop):
        super(ViewProviderOpening, self).onChanged(vobj, prop)

    # Drag handling

    def canDropObject(self, incoming_object):
        """Return True if the dropped object is accepted.
        """
        return hasattr(incoming_object, 'Shape')
        
    def dropObject(self, vobj, incoming_object):
        """Called when an object is dropped over the Opening ViewProvider in the tree.
        TODO: Setup the Type or add the object.
        """
        print(incoming_object.Name)
        vobj.Object.addObject(incoming_object)