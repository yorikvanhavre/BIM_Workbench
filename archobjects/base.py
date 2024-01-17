# ***************************************************************************
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
"""Provide the object code for Arch objects.
This module was added during 0.19 dev cycle to offer some base classes
to the new arch objects.
Old objects were derived from ArchComponent, and strictly related to IFC
implementation, new objects are more lightweight related to IFC.
"""
## @package base
# \ingroup ARCH
# \brief Provide the object code for Arch base objects.


class ShapeGroup(object):
    """
    The ShapeGroup object is the base object for Arch Walls.
    It provides the possibility to display the object own shape and also
    the grouped objects shape at the same time.
    The object was designed by realthunder.

    ref: Python object with OriginGroupExtension
         https://forum.freecadweb.org/viewtopic.php?f=22&t=44701
         https://gist.github.com/realthunder/40cd71a3085be666c3e2d718171de133
    """

    def __init__(self, obj=None):
        self.Object = obj
        if obj:
            self.attach(obj)

    def __getstate__(self):
        return

    def __setstate__(self, _state):
        return

    def dumps(self):
        return

    def loads(self, _state):
        return
    
    def attach(self, obj):
        obj.addExtension("App::GeoFeatureGroupExtensionPython")

    def onDocumentRestored(self, obj):
        self.Object = obj
