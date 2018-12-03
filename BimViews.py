#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2018 Yorik van Havre <yorik@uncreated.net>              *
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


class BIM_Views:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Views.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Views", "Views manager"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Views", "Shows or hides the views manager")}

    def Activated(self):
        from PySide import QtCore,QtGui
        vm = findWidget()
        if vm:
            if vm.isVisible():
                vm.hide()
            else:
                vm.show()
                update()
        else:
            vm = QtGui.QListWidget()
            vm.setObjectName("Views Manager")
            vm.setSortingEnabled(True)
            vm.setIconSize(QtCore.QSize(16,16))
            r = vm.rect()
            r.setHeight(FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetInt("BimViewsSize",160))
            vm.setGeometry(r)
            QtCore.QObject.connect(vm, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),show)
            mw = FreeCADGui.getMainWindow()
            combo = mw.findChild(QtGui.QDockWidget,"Combo View")
            if combo:
                s = combo.findChild(QtGui.QSplitter)
                if s:
                    s.addWidget(vm)
            update()


FreeCADGui.addCommand('BIM_Views',BIM_Views())


def findWidget():
    
    "finds the manager widget, if present"

    from PySide import QtGui
    mw = FreeCADGui.getMainWindow()
    combo = mw.findChild(QtGui.QDockWidget,"Combo View")
    vm = combo.findChild(QtGui.QListWidget,"Views Manager")
    if vm:
        return vm
    return None


def update():

    "updates the view manager"

    vm = findWidget()
    if vm and FreeCAD.ActiveDocument:
        if vm.isVisible():
            vm.clear()
            import Draft
            from PySide import QtGui
            for obj in FreeCAD.ActiveDocument.Objects:
                if Draft.getType(obj) in ["Building","BuildingPart","WorkingPlaneProxy"]:
                    it = QtGui.QListWidgetItem(vm)
                    it.setText(obj.Label)
                    it.setToolTip(obj.Name)
                    it.setIcon(QtGui.QIcon(obj.ViewObject.Proxy.getIcon()))

def show(item):
    
    "item has been double-clicked"
    
    obj = FreeCAD.ActiveDocument.getObject(item.toolTip())
    if obj:
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(obj)
        FreeCADGui.runCommand("Draft_SelectPlane")
