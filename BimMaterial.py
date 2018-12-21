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

import os,FreeCAD,FreeCADGui,DraftTools

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Material:


    def GetResources(self):

        return {'Pixmap'  : ":/icons/Arch_Material.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Material", "Material"),
                'Accel': "M, A",
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Material", "Sets or creates a material for selected objects")}

    def Activated(self):

        self.dlg = None
        from PySide import QtCore,QtGui
        objs = [obj for obj in FreeCADGui.Selection.getSelection() if hasattr(obj,"Material")]
        if objs:
            self.dlg = QtGui.QDialog()
            p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM")
            w = p.GetInt("BimMaterialDialogWidth",230)
            h = p.GetInt("BimMaterialDialogHeight",350)
            self.dlg.resize(w,h)
            self.dlg.setWindowTitle("Select material")
            self.dlg.setWindowIcon(QtGui.QIcon(":/icons/Arch_Material.svg"))
            mw = FreeCADGui.getMainWindow()
            self.dlg.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.dlg.rect().center())
            self.dlg.objects = objs
            lay = QtGui.QVBoxLayout(self.dlg)
            matList = QtGui.QListWidget(self.dlg)
            self.dlg.matList = matList
            lay.addWidget(matList)
            self.dlg.materials = []
            for o in FreeCAD.ActiveDocument.Objects:
                if o.isDerivedFrom("App::MaterialObjectPython") or ((o.TypeId == "App::FeaturePython") and hasattr(o,"Materials")):
                    self.dlg.materials.append(o)
            for o in self.dlg.materials:
                i = QtGui.QListWidgetItem(self.createIcon(o),o.Label,matList)
                i.setToolTip(o.Name)
                if len(objs) == 1:
                    if objs[0].Material == o:
                        matList.setCurrentItem(i)
            if matList.count():
                searchLayout = QtGui.QHBoxLayout()
                searchLayout.setSpacing(2)
                searchBox = QtGui.QLineEdit(self.dlg)
                searchBox.setPlaceholderText("Search...")
                searchBox.setToolTip("Searches object labels")
                self.dlg.searchBox = searchBox
                buttonClear = QtGui.QToolButton(self.dlg)
                buttonClear.setFixedSize(18, 21)
                buttonClear.setStyleSheet("QToolButton {margin-bottom:1px}")
                buttonClear.setIcon(QtGui.QIcon(":/icons/edit-cleartext.svg"))
                buttonClear.setToolTip("Clears the search field")
                buttonClear.setAutoRaise(True)
                searchLayout.addWidget(searchBox)
                searchLayout.addWidget(buttonClear)
                lay.addLayout(searchLayout)
                buttonCreate = QtGui.QPushButton("Create new material",self.dlg)
                buttonCreate.setIcon(QtGui.QIcon(":/icons/Arch_Material.svg"))
                lay.addWidget(buttonCreate)
                buttonMulti = QtGui.QPushButton("Create new multi-material",self.dlg)
                buttonMulti.setIcon(QtGui.QIcon(":/icons/Arch_Material_Multi.svg"))
                lay.addWidget(buttonMulti)
                buttonBox = QtGui.QDialogButtonBox(self.dlg)
                buttonBox.setOrientation(QtCore.Qt.Horizontal)
                buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
                lay.addWidget(buttonBox)
                buttonBox.accepted.connect(self.onAccept)
                buttonBox.rejected.connect(self.onReject)
                buttonCreate.clicked.connect(self.onCreate)
                buttonMulti.clicked.connect(self.onMulti)
                buttonClear.clicked.connect(self.onClearSearch)
                searchBox.textChanged.connect(self.onSearch)
                matList.itemDoubleClicked.connect(self.onAccept)
                self.dlg.show()
                self.dlg.searchBox.setFocus()
            else:
                self.dlg = None
                FreeCADGui.runCommand("Arch_Material")
        else:
            FreeCADGui.runCommand("Arch_Material")

    def onCreate(self):

        if self.dlg:
            self.dlg.hide()
            FreeCADGui.runCommand("Arch_Material")

    def onMulti(self):

        if self.dlg:
            self.dlg.hide()
            FreeCADGui.runCommand("Arch_MultiMaterial")

    def onAccept(self,item=None):

        if self.dlg:
            item = self.dlg.matList.currentItem()
            if item:
                mat = FreeCAD.ActiveDocument.getObject(item.toolTip())
                if mat:
                    for obj in self.dlg.objects:
                        obj.Material = mat
            p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM")
            p.SetInt("BimMaterialDialogWidth",self.dlg.width())
            p.SetInt("BimMaterialDialogHeight",self.dlg.height())
            from DraftGui import todo
            todo.delay(self.dlg.hide,None)

    def onReject(self):

        if self.dlg:
            self.dlg.hide()

    def createIcon(self,obj):

        from PySide import QtCore,QtGui
        if hasattr(obj,"Materials"):
            return QtGui.QIcon(":/icons/Arch_Material_Multi.svg")
        elif hasattr(obj,"Color"):
            c = obj.Color
            matcolor = QtGui.QColor(int(c[0]*255),int(c[1]*255),int(c[2]*255))
            darkcolor = QtGui.QColor(int(c[0]*125),int(c[1]*125),int(c[2]*125))
            im = QtGui.QImage(48,48,QtGui.QImage.Format_ARGB32)
            im.fill(QtCore.Qt.transparent)
            pt = QtGui.QPainter(im)
            pt.setPen(QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap))
            #pt.setBrush(QtGui.QBrush(matcolor, QtCore.Qt.SolidPattern))
            gradient = QtGui.QLinearGradient(0,0,48,48)
            gradient.setColorAt(0,matcolor)
            gradient.setColorAt(1,darkcolor)
            pt.setBrush(QtGui.QBrush(gradient))
            pt.drawEllipse(6,6,36,36)
            pt.setPen(QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap))
            pt.setBrush(QtGui.QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern))
            pt.drawEllipse(12,12,12,12)
            pt.end()
            px = QtGui.QPixmap.fromImage(im)
            return QtGui.QIcon(px)
        else:
            return QtGui.QIcon(":/icons/Arch_Material.svg")

    def onClearSearch(self):

        if self.dlg:
            self.dlg.searchBox.setText("")

    def onSearch(self,text):

        from PySide import QtCore,QtGui
        self.dlg.matList.clear()
        for o in self.dlg.materials:
            if text.lower() in o.Label.lower():
                i = QtGui.QListWidgetItem(self.createIcon(o),o.Label,self.dlg.matList)
                i.setToolTip(o.Name)
                self.dlg.matList.setCurrentItem(i)


FreeCADGui.addCommand('BIM_Material',BIM_Material())
