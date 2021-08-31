#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2021 Yorik van Havre <yorik@uncreated.net>              *
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


class BIM_Reorder:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Reorder.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Reorder", "Reorder children"),
                 # 'Accel': "R, D",
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Reorder", "Reorder children of selected object")}

    def Activated(self):

        import FreeCADGui

        if len(FreeCADGui.Selection.getSelection()) == 1:
            obj = FreeCADGui.Selection.getSelection()[0]
            if hasattr(obj,"Group"):
                if obj.getTypeIdOfProperty("Group") == "App::PropertyLinkList":
                    FreeCADGui.Control.showDialog(BIM_Reorder_TaskPanel(obj))
                    return
        FreeCAD.Console.PrintError(translate("BIM","You must choose a group object before using this command")+"\n")


class BIM_Reorder_TaskPanel:


    def __init__(self,obj):

        import FreeCADGui
        from PySide import QtCore,QtGui

        self.obj = obj
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogReorder.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Reorder.svg")))
        self.form.pushButton.clicked.connect(self.form.listWidget.sortItems)
        for child in self.obj.Group:
            i = QtGui.QListWidgetItem(child.Label)
            i.setIcon(child.ViewObject.Icon)
            i.setToolTip(child.Name)
            self.form.listWidget.addItem(i)

    def accept(self):

        import FreeCADGui
        
        names = [self.form.listWidget.item(i).toolTip() for i in range(self.form.listWidget.count())]
        group = [FreeCAD.ActiveDocument.getObject(n) for n in names]
        FreeCAD.ActiveDocument.openTransaction("Reorder children")
        self.obj.Group = group
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        return self.reject()

    def reject(self):

        import FreeCADGui

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()
        return True
