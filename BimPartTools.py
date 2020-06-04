# -*- coding: utf8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2017 Yorik van Havre <yorik@uncreated.net>              *
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

"""This module contains BIM wrappers for Part commands"""

import os
import FreeCAD
from BimTranslateUtils import *

#Part_Builder


class BIM_Builder:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Shapebuilder.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_Builder", "Shape builder..."),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_Builder", "Advanced utility to create shapes"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Builder")



class BIM_Offset2D:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Offset2D.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_Offset2D", "2D Offset..."),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_Offset2D", "Utility to offset planar shapes"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Offset2D")


class BIM_Extrude:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Extrude.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_Extrude", "Extrude..."),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_Extrude", "Extrude a selected sketch"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Extrude")


class BIM_Cut:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Cut.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Cut", "Difference"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Cut", "Make a difference between two shapes"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Cut")


class BIM_Fuse:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Fuse.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_Fuse", "Union"),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_Fuse", "Make a union of several shapes"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Fuse")


class BIM_Common:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Common.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_Common", "Intersection"),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_Common", "Make an intersection of two shapes"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Common")


class BIM_Compound:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Part_Compound.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_Compound", "Make compound"),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_Compound", "Make a compound of several shapes"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_Compound")


class BIM_SimpleCopy:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","Tree_Part.svg"),
                'MenuText': QT_TRANSLATE_NOOP("Part_SimpleCopy", "Create simple copy"),
                'ToolTip' : QT_TRANSLATE_NOOP("Part_SimpleCopy", "Create a simple non-parametric copy"),
                }
    
    def Activated(self):
        
        import FreeCADGui
        import PartGui
        FreeCADGui.runCommand("Part_SimpleCopy")
        
