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
from DraftTools import translate

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator


class BIM_Project:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Project.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Levels", "Manage project..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Levels", "Setup your BIM project")}

    def Activated(self):

        # load dialog
        from PySide import QtCore,QtGui
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogProject.ui"))

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        # set things up
        import Arch
        self.form.buildingUse.addItems(Arch.BuildingTypes)
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Project.svg")))
        QtCore.QObject.connect(self.form.buttonAdd, QtCore.SIGNAL("clicked()"), self.addGroup)
        QtCore.QObject.connect(self.form.buttonDel, QtCore.SIGNAL("clicked()"), self.delGroup)
        QtCore.QObject.connect(self.form.buttonSave,QtCore.SIGNAL("clicked()"), self.savePreset)
        QtCore.QObject.connect(self.form.presets,QtCore.SIGNAL("currentIndexChanged(QString)"), self.getPreset)
        QtCore.QObject.connect(self.form.buttonOK,QtCore.SIGNAL("clicked()"), self.accept)
        QtCore.QObject.connect(self.form.buttonCancel,QtCore.SIGNAL("clicked()"), self.reject)
        self.fillPresets()
        
        # show dialog
        self.form.show()

    def reject(self):

        self.form.hide()
        return True

    def accept(self):

        if self.form.groupNewDocument.isChecked() or (FreeCAD.ActiveDocument is None):
            doc = FreeCAD.newDocument()
            if self.form.projectName.text():
                doc.Label = self.form.projectName.text()
            FreeCAD.ActiveDocument = doc
        if not FreeCAD.ActiveDocument:
            FreeCAD.Console.PrintError(translate("BIM","No active document, aborting.")+"\n")
        import Draft,Arch,Part
        site = None
        outline = None
        if self.form.groupSite.isChecked():
            site = Arch.makeSite()
            site.Label = self.form.siteName.text()
            site.Address = self.form.siteAddress.text()
            site.Longitude = self.form.siteLongitude.value()
            site.Latitude = self.form.siteLatitude.value()
            if hasattr(site,"NorthDeviation"):
                site.NorthDeviation = self.form.siteDeviation.value()
            elif hasattr(site,"Declination"):
                site.Declination = self.form.siteDeviation.value()
            site.Elevation = FreeCAD.Units.Quantity(self.form.siteElevation.text()).Value
        human = None
        if self.form.addHumanFigure.isChecked():
            humanshape = Part.Shape()
            humanpath = os.path.join(os.path.dirname(__file__),"geometry","human figure.brep")
            humanshape.importBrep(humanpath)
            human = FreeCAD.ActiveDocument.addObject("Part::Feature","Human")
            human.Shape = humanshape
            human.Placement.move(FreeCAD.Vector(500,500,0))
        if self.form.groupBuilding.isChecked():
            building = Arch.makeBuilding()
            if site:
                site.Group = [building]
            building.Label = self.form.buildingName.text()
            building.BuildingType = self.form.buildingUse.currentText()
            buildingWidth = FreeCAD.Units.Quantity(self.form.buildingWidth.text()).Value
            buildingLength = FreeCAD.Units.Quantity(self.form.buildingLength.text()).Value
            distVAxes = FreeCAD.Units.Quantity(self.form.distVAxes.text()).Value
            distHAxes = FreeCAD.Units.Quantity(self.form.distHAxes.text()).Value
            levelHeight = FreeCAD.Units.Quantity(self.form.levelHeight.text()).Value
            color = self.form.lineColor.property("color").getRgbF()[:3]
            if buildingWidth and buildingLength:
                outline = Draft.makeRectangle(buildingLength,buildingWidth,face=False)
                outline.Label = translate("BIM","Building Outline")
                outline.ViewObject.DrawStyle = "Dashed"
                outline.ViewObject.LineColor = color
                outline.ViewObject.LineWidth = self.form.lineWidth.value()*2
                grp = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup")
                grp.Label = translate("BIM","Building Layout")
                building.addObject(grp)
                grp.addObject(outline)
                if self.form.buildingName.text():
                    outtext = Draft.makeText([self.form.buildingName.text()],point=FreeCAD.Vector(Draft.getParam("textheight",0.20)*0.3,-Draft.getParam("textheight",0.20)*1.43,0))
                    outtext.Label = translate("BIM","Building Label")
                    outtext.ViewObject.TextColor = color
                    grp.addObject(outtext)
                if human:
                    grp.addObject(human)
            axisV = None
            if self.form.countVAxes.value() and distVAxes:
                axisV = Arch.makeAxis(num = self.form.countVAxes.value(), size = distVAxes, name="vaxis")
                axisV.Label = translate("BIM","Vertical Axes")
                axisV.ViewObject.BubblePosition = "Both"
                axisV.ViewObject.LineWidth = self.form.lineWidth.value()
                axisV.ViewObject.FontSize = Draft.getParam("textheight",0.20)
                axisV.ViewObject.BubbleSize = Draft.getParam("textheight",0.20)*1.43
                axisV.ViewObject.LineColor = color
                if outline:
                    axisV.setExpression('Length', outline.Name+'.Height * 1.1')
                    axisV.setExpression('Placement.Base.y', outline.Name+'.Placement.Base.y - '+axisV.Name+'.Length * 0.05')
                    axisV.setExpression('Placement.Base.x', outline.Name+'.Placement.Base.x')
            axisH = None
            if self.form.countHAxes.value() and distHAxes:
                axisH = Arch.makeAxis(num = self.form.countHAxes.value(), size = distHAxes, name="haxis")
                axisH.Label = translate("BIM","Horizontal Axes")
                axisH.ViewObject.BubblePosition = "Both"
                axisH.ViewObject.NumberingStyle = "A,B,C"
                axisH.ViewObject.LineWidth = self.form.lineWidth.value()
                axisH.ViewObject.FontSize = Draft.getParam("textheight",0.20)
                axisH.ViewObject.BubbleSize = Draft.getParam("textheight",0.20)*1.43
                axisH.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0,0,1),90)
                axisH.ViewObject.LineColor = color
                if outline:
                    axisH.setExpression('Length', outline.Name+'.Length * 1.1')
                    axisH.setExpression('Placement.Base.x', outline.Name+'.Placement.Base.x + '+axisH.Name+'.Length * 0.945')
                    axisH.setExpression('Placement.Base.y', outline.Name+'.Placement.Base.y')
            if axisV and axisH:
                axisG = Arch.makeAxisSystem([axisH,axisV])
                axisG.Label = translate("BIM","Axes")
                grp.addObject(axisG)
            else:
                if axisV:
                    grp.addObject(axisV)
                if axisH:
                    grp.addObject(axisH)
            if self.form.countLevels.value() and levelHeight:
                h = 0
                alabels = []
                for i in range(self.form.countLevels.value()):
                    lev = Arch.makeFloor()
                    lev.Label = translate("BIM","Level")+" "+str(i)
                    alabels.append(lev.Label)
                    lev.Height = levelHeight
                    lev.Placement.move(FreeCAD.Vector(0,0,h))
                    h += levelHeight
                    building.addObject(lev)
                    if self.form.levelsWP.isChecked():
                        prx = Draft.makeWorkingPlaneProxy(FreeCAD.Placement())
                        prx.Placement.move(FreeCAD.Vector(0,0,h))
                        lev.addObject(prx)
                if self.form.levelsAxis.isChecked():
                    axisL = Arch.makeAxis(num = self.form.countLevels.value(), size = levelHeight, name="laxis")
                    axisL.Label = translate("BIM","Level Axes")
                    axisL.ViewObject.BubblePosition = "None"
                    axisL.ViewObject.LineWidth = self.form.lineWidth.value()
                    axisL.ViewObject.FontSize = Draft.getParam("textheight",0.20)
                    axisL.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector (0.577350269189626, -0.5773502691896257, 0.5773502691896257),120)
                    axisL.ViewObject.LineColor = color
                    axisL.ViewObject.LabelOffset.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90)
                    axisL.Labels = alabels
                    axisL.ViewObject.ShowLabel = True
                    if outline:
                        axisL.setExpression('Length', outline.Name+'.Length * 1.1')
                        axisL.setExpression('Placement.Base.x', outline.Name+'.Placement.Base.x + '+axisL.Name+'.Length * 0.945')
                        axisL.setExpression('Placement.Base.y', outline.Name+'.Placement.Base.y')
                        grp.addObject(axisL)
                        axisL.ViewObject.LabelOffset.Base = FreeCAD.Vector(-axisL.Length.Value + Draft.getParam("textheight",0.20)*0.43,0,Draft.getParam("textheight",0.20)*0.43)
        self.form.hide()
        FreeCAD.ActiveDocument.recompute()
        if outline:
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(outline)
            FreeCADGui.SendMsgToActiveView("ViewSelection")
            FreeCADGui.Selection.clearSelection()
        if hasattr(FreeCADGui,"Snapper"):
            FreeCADGui.Snapper.show()
        return True

    def addGroup(self):

        from PySide import QtCore,QtGui
        it = QtGui.QListWidgetItem(translate("BIM","New Group"))
        it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable)
        self.form.groupsList.addItem(it)

    def delGroup(self):

        r = self.form.groupsList.currentRow()
        if r >= 0:
            self.form.groupsList.takeItem(r)

    def savePreset(self):

        from PySide import QtCore,QtGui
        import Arch
        res = QtGui.QInputDialog.getText(None, translate("BIM","Save preset"),translate("BIM","Preset name:"), QtGui.QLineEdit.Normal,"DefaultProject")
        if res[1]:
            name = res[0]
            presetdir = os.path.join(FreeCAD.getUserAppDataDir(),"BIM")
            if not os.path.isdir(presetdir):
                os.mkdir(presetdir)

            groups = []
            for i in range(self.form.groupsList.count()):
                groups.append(self.form.groupsList.item(i).text())

            s =  "# FreeCAD BIM Project setup preset "+name+"\n"
            s += "groupNewDocument="+str(int(self.form.groupNewDocument.isChecked()))+"\n"
            s += "projectName="+self.form.projectName.text()+"\n"
            s += "groupSite="+str(int(self.form.groupSite.isChecked()))+"\n"

            s += "siteName="+self.form.siteName.text()+"\n"
            s += "siteAddress="+self.form.siteAddress.text()+"\n"
            s += "siteLongitude="+str(self.form.siteLongitude.value())+"\n"
            s += "siteLatitude="+str(self.form.siteLatitude.value())+"\n"
            s += "siteDeviation="+str(self.form.siteDeviation.value())+"\n"
            s += "siteElevation="+self.form.siteElevation.text()+"\n"

            s += "groupBuilding="+str(int(self.form.groupBuilding.isChecked()))+"\n"
            s += "buildingName="+self.form.buildingName.text()+"\n"
            s += "buildingUse="+str(self.form.buildingUse.currentIndex())+"\n"
            s += "buildingLength="+self.form.buildingLength.text()+"\n"
            s += "buildingWidth="+self.form.buildingWidth.text()+"\n"
            s += "countVAxes="+str(self.form.countVAxes.value())+"\n"
            s += "distVAxes="+self.form.distVAxes.text()+"\n"
            s += "countHAxes="+str(self.form.countHAxes.value())+"\n"
            s += "distHAxes="+self.form.distHAxes.text()+"\n"
            s += "countLevels="+str(self.form.countLevels.value())+"\n"
            s += "levelHeight="+self.form.levelHeight.text()+"\n"
            s += "lineWidth="+str(self.form.lineWidth.value())+"\n"
            s += "lineColor="+str(self.form.lineColor.property("color").getRgbF()[:3])+"\n"
            s += "groups="+";;".join(groups)+"\n"

            s += "levelsWP="+str(int(self.form.levelsWP.isChecked()))+"\n"
            s += "levelsAxis="+str(int(self.form.levelsAxis.isChecked()))+"\n"
            
            s += "addHumanFigure="+str(int(self.form.addHumanFigure.isChecked()))+"\n"

            f = open(os.path.join(presetdir,name+".txt"),"w")
            f.write(s)
            f.close()
            self.fillPresets()

    def fillPresets(self):

        self.form.presets.clear()
        self.form.presets.addItem(translate("BIM","User preset..."))
        presetdir = os.path.join(FreeCAD.getUserAppDataDir(),"BIM")
        if os.path.isdir(presetdir):
            for f in os.listdir(presetdir):
                if f.endswith(".txt"):
                    self.form.presets.addItem(os.path.splitext(f)[0])

    def getPreset(self,preset):

        import Arch
        from PySide import QtGui
        pfile = os.path.join(FreeCAD.getUserAppDataDir(),"BIM",preset+".txt")
        if os.path.exists(pfile):
            f = open(pfile,"r")
            buf = f.read()
            f.close()
            lines = buf.split("\n")
            for line in lines:
                if line:
                    if line[0] != "#":
                        s = line.split("=")
                        if s[0] ==   "groupNewDocument":
                            self.form.groupNewDocument.setChecked(bool(int(s[1])))
                        elif s[0] == "projectName":
                            self.form.projectName.setText(s[1])
                        elif s[0] == "groupSite":
                            self.form.groupSite.setChecked(bool(int(s[1])))
                        elif s[0] == "siteName":
                            self.form.siteName.setText(s[1])
                        elif s[0] == "siteAddress":
                            self.form.siteAddress.setText(s[1])
                        elif s[0] == "siteLongitude":
                            self.form.siteLongitude.setValue(float(s[1]))
                        elif s[0] == "siteLatitude":
                            self.form.siteLatitude.setValue(float(s[1]))
                        elif s[0] == "siteDeviation":
                            self.form.siteDeviation.setValue(float(s[1]))
                        elif s[0] == "siteElevation":
                            self.form.siteElevation.setText(s[1])
                        elif s[0] == "groupBuilding":
                            self.form.groupBuilding.setChecked(bool(int(s[1])))
                        elif s[0] == "buildingName":
                            self.form.buildingName.setText(s[1])
                        elif s[0] == "buildingUse":
                            self.form.buildingUse.setCurrentIndex(int(s[1]))
                        elif s[0] == "buildingLength":
                            self.form.buildingLength.setText(s[1])
                        elif s[0] == "buildingWidth":
                            self.form.buildingWidth.setText(s[1])
                        elif s[0] == "countVAxes":
                            self.form.countVAxes.setValue(int(s[1]))
                        elif s[0] == "distVAxes":
                            self.form.distVAxes.setText(s[1])
                        elif s[0] == "countHAxes":
                            self.form.countHAxes.setValue(int(s[1]))
                        elif s[0] == "distHAxes":
                            self.form.distHAxes.setText(s[1])
                        elif s[0] == "countLevels":
                            self.form.countLevels.setValue(int(s[1]))
                        elif s[0] == "levelHeight":
                            self.form.levelHeight.setText(s[1])
                        elif s[0] == "lineWidth":
                            self.form.lineWidth.setValue(int(s[1]))
                        elif s[0] == "lineColor":
                            col = tuple([float(t) for t in s[1].strip("(").strip(")").split(",")])
                            col = QtGui.QColor.fromRgbF(*col)
                            self.form.lineColor.setProperty("color",col)
                        elif s[0] == "groups":
                            groups = s[1].split(";;")
                            self.form.groupsList.clear()
                            self.form.groupsList.addItems(groups)
                        elif s[0] == "levelsWP":
                            self.form.levelsWP.setChecked(bool(int(s[1])))
                        elif s[0] == "levelsAxis":
                            self.form.levelsAxis.setChecked(bool(int(s[1])))
                        elif s[0] == "addHumanFigure":
                            self.form.addHumanFigure.setChecked(bool(int(s[1])))

