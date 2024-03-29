# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 Yorik van Havre <yorik@uncreated.net>              *
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

"""This module contains FreeCAD commands for the BIM workbench"""

import os
import FreeCAD
from BimTranslateUtils import *


class BIM_Windows:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "BIM_Windows.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP("BIM_Windows", "Manage doors and windows..."),
            "ToolTip": QT_TRANSLATE_NOOP(
                "BIM_Windows",
                "Manage the different doors and windows of your BIM project",
            ),
        }

    def Activated(self):
        import FreeCADGui

        FreeCADGui.Control.showDialog(BIM_Windows_TaskPanel())


class BIM_Windows_TaskPanel:
    def __init__(self):
        import FreeCADGui
        from PySide import QtCore, QtGui

        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.join(os.path.dirname(__file__), "dialogWindows.ui")
        )
        self.form.setWindowIcon(
            QtGui.QIcon(
                os.path.join(os.path.dirname(__file__), "icons", "BIM_Windows.svg")
            )
        )
        QtCore.QObject.connect(
            self.form.groupMode, QtCore.SIGNAL("currentIndexChanged(int)"), self.update
        )
        QtCore.QObject.connect(
            self.form.windows,
            QtCore.SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self.editWindow,
        )
        QtCore.QObject.connect(
            self.form.windows,
            QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"),
            self.showWindow,
        )
        QtCore.QObject.connect(
            self.form.windowLabel, QtCore.SIGNAL("returnPressed()"), self.setLabel
        )
        QtCore.QObject.connect(
            self.form.windowDescription,
            QtCore.SIGNAL("returnPressed()"),
            self.setDescription,
        )
        QtCore.QObject.connect(
            self.form.windowTag, QtCore.SIGNAL("returnPressed()"), self.setTag
        )
        QtCore.QObject.connect(
            self.form.windowHeight, QtCore.SIGNAL("returnPressed()"), self.setHeight
        )
        QtCore.QObject.connect(
            self.form.windowWidth, QtCore.SIGNAL("returnPressed()"), self.setWidth
        )
        QtCore.QObject.connect(
            self.form.windowMaterial, QtCore.SIGNAL("clicked()"), self.setMaterial
        )
        self.form.windows.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.update()

    def getStandardButtons(self):
        from PySide import QtGui

        return int(QtGui.QDialogButtonBox.Close)

    def reject(self):
        import FreeCADGui

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()

    def update(self, index=None):
        import Draft, Arch_rc
        from PySide import QtGui

        self.form.windows.clear()
        windows = [
            o for o in FreeCAD.ActiveDocument.Objects if Draft.getType(o) == "Window"
        ]
        if self.form.groupMode.currentIndex() == 0:
            for window in windows:
                s1 = window.Label
                s2 = window.Tag
                it = QtGui.QTreeWidgetItem([s1, s2])
                it.setIcon(0, QtGui.QIcon(":/icons/Arch_Window_Tree.svg"))
                it.setToolTip(0, window.Name)
                self.form.windows.addTopLevelItem(it)
        else:
            groups = {}
            for window in windows:
                group = None
                if self.form.groupMode.currentIndex() == 1:
                    group = window.Width.UserString + " x " + window.Height.UserString
                elif self.form.groupMode.currentIndex() == 2:
                    if window.CloneOf:
                        group = window.CloneOf.Label
                    else:
                        group = window.Name
                elif self.form.groupMode.currentIndex() == 3:
                    group = window.Tag
                else:
                    if window.Material:
                        group = window.Material.Label
                if not group:
                    group = "None"
                if group in groups:
                    groups[group].append(window)
                else:
                    groups[group] = [window]
            for group in groups.keys():
                s1 = group
                top = QtGui.QTreeWidgetItem([s1, ""])
                top.setExpanded(True)
                self.form.windows.addTopLevelItem(top)
                for window in groups[group]:
                    s1 = window.Label
                    s2 = window.Tag
                    it = QtGui.QTreeWidgetItem([s1, s2])
                    it.setIcon(0, QtGui.QIcon(":/icons/Arch_Window_Tree.svg"))
                    it.setToolTip(0, window.Name)
                    top.addChild(it)
            self.form.windows.expandAll()
        wc = 0
        dc = 0
        for w in windows:
            if hasattr(w, "IfcType"):
                r = w.IfcType
            elif hasattr(w, "IfcRole"):
                r = w.IfcRole
            else:
                r = w.Role
            if "Window" in r:
                wc += 1
            elif "Door" in r:
                dc += 1
        self.form.windowsCount.setText(str(wc))
        self.form.doorsCount.setText(str(dc))

    def editWindow(self, item, column):
        import FreeCADGui

        if len(self.form.windows.selectedItems()) == 1:
            # don't change the contents if we have more than one floor selected
            window = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
            if window:
                self.form.windowLabel.setText(window.Label)
                self.form.windowDescription.setText(window.Description)
                self.form.windowTag.setText(window.Tag)
                self.form.windowWidth.setText(window.Width.UserString)
                self.form.windowHeight.setText(window.Height.UserString)
                if window.Material:
                    self.form.windowMaterial.setText(window.Material.Label)
        # select objects
        FreeCADGui.Selection.clearSelection()
        for item in self.form.windows.selectedItems():
            o = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
            if o:
                FreeCADGui.Selection.addSelection(o)

    def showWindow(self, item, column):
        import FreeCADGui

        window = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
        if window:
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(window)
            FreeCADGui.SendMsgToActiveView("ViewSelection")

    def setWidth(self):
        val = FreeCAD.Units.Quantity(self.form.windowWidth.text()).Value
        if val:
            for it in self.form.windows.selectedItems():
                window = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
                if window:
                    window.Width = val
            self.update()

    def setHeight(self):
        val = FreeCAD.Units.Quantity(self.form.windowHeight.text()).Value
        if val:
            for it in self.form.windows.selectedItems():
                window = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
                if window:
                    window.Height = val
            self.update()

    def setLabel(self):
        val = self.form.windowLabel.text()
        if val:
            for it in self.form.windows.selectedItems():
                window = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
                if window:
                    window.Label = val
            self.update()

    def setTag(self):
        for it in self.form.windows.selectedItems():
            window = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if window:
                window.Tag = self.form.windowTag.text()
        self.update()

    def setDescription(self):
        for it in self.form.windows.selectedItems():
            window = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if window:
                window.Description = self.form.windowDescription.text()
        self.update()

    def setMaterial(self):
        import FreeCADGui
        import Draft, Arch_rc
        from PySide import QtGui

        form = FreeCADGui.PySideUic.loadUi(
            os.path.join(os.path.dirname(__file__), "dialogMaterialChooser.ui")
        )
        mw = FreeCADGui.getMainWindow()
        form.move(
            mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center()
        )
        materials = [
            o for o in FreeCAD.ActiveDocument.Objects if Draft.getType(o) == "Material"
        ]
        it = QtGui.QListWidgetItem(translate("BIM", "None"))
        it.setIcon(QtGui.QIcon(":/icons/button_invalid.svg"))
        it.setToolTip("__None__")
        form.list.addItem(it)
        for mat in materials:
            it = QtGui.QListWidgetItem(mat.Label)
            it.setIcon(QtGui.QIcon(":/icons/Arch_Material.svg"))
            it.setToolTip(mat.Name)
            form.list.addItem(it)
        result = form.exec_()
        if result:
            mat = None
            sel = form.list.selectedItems()
            if sel:
                sel = sel[0]
                if sel.toolTip() != "__None__":
                    mat = FreeCAD.ActiveDocument.getObject(str(sel.toolTip()))
                for it in self.form.windows.selectedItems():
                    window = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
                    if window:
                        if mat:
                            window.Material = mat
                        else:
                            window.Material = None
                if mat:
                    self.form.windowMaterial.setText(mat.Label)
                self.update()
