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

import os,FreeCAD,FreeCADGui,Draft,DraftTools,ArchStructure,ArchWindow

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator
import DraftTools
from DraftTools import translate


class BIM_Copy(DraftTools.Move):


    def __init__(self):
        DraftTools.Move.__init__(self)
        self.copymode = True

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Copy.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Copy", "Copy"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Copy", "Copies selected objects to another location"),
                'Accel': 'C,P'}


class BIM_Clone(DraftTools.Draft_Clone):


    def __init__(self):
        DraftTools.Draft_Clone.__init__(self)
        self.moveAfterCloning = True


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Clone.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Clone", "Clone"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Clone", "Clones selected objects to another location"),
                'Accel': 'C,L'}


class BIM_ResetCloneColors:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_ResetCloneColors.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_ResetCloneColors", "Reset colors"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_ResetCloneColors", "Resets the colors of this object from its cloned original"),
                'Accel': 'D,O'}

    def Activated(self):

        for obj in FreeCADGui.Selection.getSelection():
            if hasattr(obj,"CloneOf") and obj.CloneOf:
                obj.ViewObject.DiffuseColor = obj.CloneOf.ViewObject.DiffuseColor

