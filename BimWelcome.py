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

from PySide import QtCore,QtGui

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Welcome:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Welcome.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Welcome", "BIM Welcome screen"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Welcome", "Show the BIM workbench welcome screen")}

    def Activated(self):

        # load dialog
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogWelcome.ui"))

        # set the title image
        self.form.image.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"icons","banner.png")))

        # handle the tutorial link
        QtCore.QObject.connect(self.form.label_4, QtCore.SIGNAL("linkActivated(QString)"), self.launchTutorial)

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        # show dialog and run setup dialog afterwards if OK was pressed
        result = self.form.exec_()
        if result:
            FreeCADGui.runCommand("BIM_Setup")
            
        # remove first time flag
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetBool("FirstTime",False)

    def launchTutorial(self,link):
        
        if hasattr(self,"form"):
            self.form.hide()
            FreeCADGui.runCommand("BIM_Tutorial")
