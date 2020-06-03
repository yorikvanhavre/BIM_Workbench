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
"""Provide the object code for Arch Opening viewprovider."""
## @package view_opening
# \ingroup ARCH
# \brief Provide the viewprovider code for Arch Opening.


class ViewProviderOpening(object):
    def __init__(self,vobj=None):
        if vobj:
            vobj.Proxy = self
            self.attach(vobj)
        else:
            self.ViewObject = None

    def attach(self,vobj):
        vobj.addExtension('Gui::ViewProviderGeoFeatureGroupExtensionPython', None)
        self.ViewObject = vobj

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def __getstate__(self):
        return None

    def __setstate__(self, _state):
        return None