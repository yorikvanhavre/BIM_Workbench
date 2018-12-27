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

import os,FreeCAD,FreeCADGui,sys

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

UPDATEINTERVAL = 2000 # number of milliseconds between BIM Views window update

class BIM_Views:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Views.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Views", "Views manager"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Views", "Shows or hides the views manager"),
                'Accel': 'Ctrl+9'}

    def Activated(self):
        from PySide import QtCore,QtGui
        vm = findWidget()
        bimviewsbutton = None
        mw = FreeCADGui.getMainWindow()
        st = mw.statusBar()
        statuswidget = st.findChild(QtGui.QToolBar,"BIMStatusWidget")
        if statuswidget:
            if hasattr(statuswidget,"bimviewsbutton"):
                bimviewsbutton = statuswidget.bimviewsbutton
        if vm:
            if vm.isVisible():
                vm.hide()
                if bimviewsbutton:
                    bimviewsbutton.setChecked(False)
            else:
                vm.show()
                if bimviewsbutton:
                    bimviewsbutton.setChecked(True)
                update()
        else:
            vm = QtGui.QListWidget()
            vm.setObjectName("Views Manager")
            vm.setSortingEnabled(True)
            vm.setIconSize(QtCore.QSize(16,16))
            QtCore.QObject.connect(vm, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),show)
            mw = FreeCADGui.getMainWindow()
            combo = mw.findChild(QtGui.QDockWidget,"Combo View")
            if combo:
                s = combo.findChild(QtGui.QSplitter)
                if s:
                    # discount the widget size from the first one
                    h = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetInt("BimViewsSize",100)
                    sizes = s.sizes()
                    sizes[0] = sizes[0]-h
                    s.addWidget(vm)
                    s.setSizes(sizes+[h])
            update()
            from DraftGui import todo


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
            from PySide import QtCore,QtGui
            for obj in FreeCAD.ActiveDocument.Objects:
                if obj and (Draft.getType(obj) in ["Building","BuildingPart","WorkingPlaneProxy"]):
                    it = QtGui.QListWidgetItem(vm)
                    it.setText(obj.Label)
                    it.setToolTip(obj.Name)
                    if obj.ViewObject:
                        it.setIcon(QtGui.QIcon(obj.ViewObject.Proxy.getIcon()))
            QtCore.QTimer.singleShot(UPDATEINTERVAL, update)

def show(item):
    
    "item has been double-clicked"
    
    if isinstance(item,str) or ((sys.version_info.major < 3) and isinstance(item,unicode)):
        obj = FreeCAD.ActiveDocument.getObject(item)
    else:
        obj = FreeCAD.ActiveDocument.getObject(item.toolTip())
    if obj:
        sel = FreeCADGui.Selection.getSelection()
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(obj)
        FreeCADGui.runCommand("Draft_SelectPlane")
        FreeCADGui.Selection.clearSelection()
        for s in sel:
            FreeCADGui.Selection.addSelection(s)
    vm = findWidget()
    if vm:
        if isinstance(item,str) or ((sys.version_info.major < 3) and isinstance(item,unicode)):
            vm.lastSelected = item
        else:
            vm.lastSelected = item.toolTip()
