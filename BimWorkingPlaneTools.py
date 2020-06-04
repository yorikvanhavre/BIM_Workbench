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

"""This module contains FreeCAD commands for the BIM workbench"""

import os
import FreeCAD
from BimTranslateUtils import *


class BIM_SetWPTop:


    def GetResources(self):

        return {'Pixmap'  : "view-top.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_SetWPTop", "Working Plane Top"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_SetWPTop", "Set the working plane to Top"),
                'Accel': 'Ctrl+Shift+2'}

    def Activated(self):

        import FreeCADGui
        FreeCADGui.doCommandGui("FreeCAD.DraftWorkingPlane.setTop()")


class BIM_SetWPFront:


    def GetResources(self):

        return {'Pixmap'  : "view-front.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_SetWPFront", "Working Plane Front"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_SetWPFront", "Set the working plane to Front"),
                'Accel': 'Ctrl+Shift+1'}

    def Activated(self):

        import FreeCADGui
        FreeCADGui.doCommandGui("FreeCAD.DraftWorkingPlane.setFront()")


class BIM_SetWPSide:


    def GetResources(self):

        return {'Pixmap'  : "view-right.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_SetWPSide", "Working Plane Side"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_SetWPSide", "Set the working plane to Side"),
                'Accel': 'Ctrl+Shift+3'}

    def Activated(self):

        import FreeCADGui
        FreeCADGui.doCommandGui("FreeCAD.DraftWorkingPlane.setSide()")
