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



class BIM_Levels:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Levels.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Levels", "Manage levels..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Levels", "Set/modify the different levels of your BIM project")}

    def Activated(self):
        FreeCADGui.Control.showDialog(BIM_Levels_TaskPanel())



class BIM_Levels_TaskPanel:


    def __init__(self):

        from PySide import QtCore,QtGui
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogLevels.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Levels.svg")))
        QtCore.QObject.connect(self.form.levels, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *, int)"), self.editLevel)
        QtCore.QObject.connect(self.form.levels, QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"), self.showLevel)
        QtCore.QObject.connect(self.form.buttonStore, QtCore.SIGNAL("clicked()"), self.storeView)
        QtCore.QObject.connect(self.form.buttonAdd, QtCore.SIGNAL("clicked()"), self.addLevel)
        QtCore.QObject.connect(self.form.levelName, QtCore.SIGNAL("returnPressed()"), self.updateLevels)
        QtCore.QObject.connect(self.form.levelCoord, QtCore.SIGNAL("returnPressed()"), self.updateLevels)
        QtCore.QObject.connect(self.form.levelHeight, QtCore.SIGNAL("returnPressed()"), self.updateLevels)
        QtCore.QObject.connect(self.form.restoreView, QtCore.SIGNAL("stateChanged(int)"), self.updateLevels)
        QtCore.QObject.connect(self.form.restoreState, QtCore.SIGNAL("stateChanged(int)"), self.updateLevels)
        QtCore.QObject.connect(self.form.buttonDelete, QtCore.SIGNAL("clicked()"), self.deleteLevels)
        self.form.levels.header().setResizeMode(0,QtGui.QHeaderView.Stretch)
        self.update()

    def getStandardButtons(self):

        from PySide import QtGui
        return int(QtGui.QDialogButtonBox.Close)

    def reject(self):

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()

    def update(self,keepSelection=False):

        sel = [it.toolTip(0) for it in self.form.levels.selectedItems()]
        import Draft,Arch_rc
        from PySide import QtGui
        self.form.levels.clear()
        levels = [o for o in FreeCAD.ActiveDocument.Objects if (Draft.getType(o) == "Floor")]
        for level in levels:
            s1 = level.Label
            s2 = FreeCAD.Units.Quantity(level.Placement.Base.z,FreeCAD.Units.Length).UserString
            it = QtGui.QTreeWidgetItem([s1,s2])
            it.setIcon(0,QtGui.QIcon(":/icons/Arch_Floor_Tree.svg"))
            it.setToolTip(0,level.Name)
            self.form.levels.addTopLevelItem(it)
        if keepSelection and sel:
            for i in range(self.form.levels.topLevelItemCount()):
                it = self.form.levels.topLevelItem(i)
                if it.toolTip(0) in sel:
                    self.form.levels.setCurrentItem(it)

    def showLevel(self,item,column):

        level = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
        if level:
            if hasattr(level.Proxy,"show"):
                level.Proxy.show()

    def editLevel(self,item,column):

        if len(self.form.levels.selectedItems()) == 1:
            # dont change the contents if we have more than one floor selected
            level = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
            if level:
                self.form.levelName.setText(level.Label)
                self.form.levelCoord.setText(FreeCAD.Units.Quantity(level.Placement.Base.z,FreeCAD.Units.Length).UserString)
                if hasattr(level,"Height"):
                    self.form.levelHeight.setText(FreeCAD.Units.Quantity(level.Height,FreeCAD.Units.Length).UserString)
                if hasattr(level,"RestoreView"):
                    self.form.restoreView.setChecked(level.RestoreView)
                if hasattr(level,"RestoreState"):
                    self.form.restoreState.setChecked(level.RestoreState)

    def storeView(self):

        for it in self.form.levels.selectedItems():
            level = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if level:
                if hasattr(level.Proxy,"writeCamera"):
                    level.Proxy.writeCamera()

    def addLevel(self):
        
        import Arch
        level = Arch.makeFloor()
        self.setLevel(level)
        self.update()
        
    def setLevel(self,level):

        if self.form.levelName.text():
            level.Label = self.form.levelName.text()
        if self.form.levelCoord.text():
            p = FreeCAD.Placement()
            p.Base = FreeCAD.Vector(0,0,FreeCAD.Units.Quantity(self.form.levelCoord.text()).Value)
            level.Placement = p
        if self.form.levelHeight.text():
            level.Height = FreeCAD.Units.Quantity(self.form.levelHeight.text()).Value
        if hasattr(level,"RestoreView"):
            level.RestoreView = self.form.restoreView.isChecked()
        if hasattr(level,"RestoreState"):
            level.RestoreState = self.form.restoreState.isChecked()

    def updateLevels(self,arg=None):
        
        for it in self.form.levels.selectedItems():
            level = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if level:
                self.setLevel(level)
        self.update(keepSelection=True)

    def deleteLevels(self):

        dels = []
        for it in self.form.levels.selectedItems():
            level = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if level:
                dels.append(level.Name)
        for d in dels:
            FreeCAD.ActiveDocument.removeObject(d)
        self.update()



FreeCADGui.addCommand('BIM_Levels',BIM_Levels())

