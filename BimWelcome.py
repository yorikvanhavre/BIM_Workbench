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

import os,FreeCAD,FreeCADGui

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Welcome:


    def GetResources(self):

        return {'Pixmap'  : ":icons/preferences-system.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Welcome", "Welcome screen"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Welcome", "Show the welcome screen")}

    def Activated(self):

        # load dialog
        form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogWelcome.ui"))

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        form.move(mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center())

        # show dialog and run setup dialog afterwards if OK was pressed
        result = form.exec_()
        if result:
            FreeCADGui.runCommand("BIM_Setup")


FreeCADGui.addCommand('BIM_Welcome',BIM_Welcome())
