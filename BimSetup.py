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

import os,sys,FreeCAD,FreeCADGui
from FreeCAD import Vector
from DraftTools import translate

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Setup:


    def GetResources(self):

        return {'Pixmap'  : ":icons/preferences-system.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Setup", "BIM Setup..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Setup", "Set some common FreeCAD preferences for BIM workflow")}

    def Activated(self):

        TECHDRAWDIMFACTOR = 0.16 # How many times TechDraw dim arrows are smaller than Draft

        # load dialog
        from PySide import QtGui
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogSetup.ui"))

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        # connect signals / slots
        self.form.comboPresets.currentIndexChanged[int].connect(self.setPreset)

        # fill default values
        self.setPreset(None)

        # check missing addons
        self.form.labelMissingWorkbenches.hide()
        self.form.labelIfcOpenShell.hide()
        self.form.labelSnapTip.hide()
        m = []
        try:
            import RebarTools
        except:
            m.append("Reinforcement")
        try:
            import BIMServer
        except:
            m.append("WebTools")
        if sys.version_info.major < 3:
            try:
                import CommandsFrame
            except:
                m.append("Flamingo")
        else:
            try:
                import CFrame
            except:
                m.append("Dodo")
        try:
            import FastenerBase
        except:
            m.append("Fasteners")
        try:
            import report
        except:
            m.append("Reporting")
        try:
            import ifcopenshell
        except:
            ifcok = False
        else:
            ifcok = True
        libok = False
        librarypath = FreeCAD.ParamGet('User parameter:Plugins/parts_library').GetString('destination','')
        if librarypath and os.path.exists(librarypath):
            libok = True
        else:
            # check if the library is at the standard addon location
            librarypath = os.path.join(FreeCAD.getUserAppDataDir(),"Mod","parts_library")
            if os.path.exists(librarypath):
                FreeCAD.ParamGet('User parameter:Plugins/parts_library').SetString('destination',librarypath)
                libok = True
        if not libok:
            m.append("Parts Library")
        if m:
            t = translate("BIM","Some additional workbenches are not installed, that extend BIM functionality:")+" <b>"+",".join(m)+"</b>. "+translate("BIM","You can install them from menu Tools -> Addon manager.")
            self.form.labelMissingWorkbenches.setText(t)
            self.form.labelMissingWorkbenches.show()
        if not ifcok:
            self.form.labelIfcOpenShell.show()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetString("snapModes","111111111101111") == "111111111101111":
            self.form.labelSnapTip.show()

        # show dialog and exit if cancelled
        FreeCADGui.BIMSetupDialog = True # this is there to be easily detected by the BIM tutorial
        result = self.form.exec_()
        del FreeCADGui.BIMSetupDialog
        if not result:
            return

        # set preference values
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetBool("FirstTime",False)
        unit = self.form.settingUnits.currentIndex()
        unit = [0,4,1,3,7,5][unit] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema",unit)
        if hasattr(FreeCAD.Units,"setSchema"):
            FreeCAD.Units.setSchema(unit)
        decimals = self.form.settingDecimals.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("Decimals",decimals)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetBool("UseGlobalDecimals",True)
        grid = self.form.settingGrid.text()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Sketcher/General").SetString("GridSize",str(grid)) # Also set sketcher grid
        grid = FreeCAD.Units.Quantity(grid).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("gridSpacing",grid)
        squares = self.form.settingSquares.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("gridEvery",squares)
        wp = self.form.settingWP.currentIndex()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("defaultWP",wp)
        tsize = self.form.settingText.text()
        tsize = FreeCAD.Units.Quantity(tsize).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("textheight",tsize)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetFloat("FontSize",tsize) # TODO - check if this needs a mult factor?
        font = self.form.settingFont.currentFont().family()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetString("textfont",font)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Labels").SetString("LabelFont",font)
        linewidth = self.form.settingLinewidth.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetInt("DefautShapeLineWidth",linewidth)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("linewidth",linewidth)
        # TODO - TechDraw default line styles
        dimstyle = self.form.settingDimstyle.currentIndex()
        ddimstyle = [0,2,3,4][dimstyle] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("dimsymbol",ddimstyle)
        tdimstyle = [3,0,2,2][dimstyle] # TechDraw has different order than Draft
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetInt("dimsymbol",tdimstyle)
        asize = self.form.settingArrowsize.text()
        asize = FreeCAD.Units.Quantity(asize).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("arrowsize",asize)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetFloat("ArrowSize",asize*TECHDRAWDIMFACTOR)
        author = self.form.settingAuthor.text()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetString("prefAuthor",author)
        lic = self.form.settingLicense.currentIndex()
        lic = [0,1,2,4,5][lic] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetInt("prefLicenseType",lic)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetString("prefLicenseUrl","") # TODO - set correct license URL
        bimdefault = self.form.settingWorkbench.currentIndex()
        if bimdefault == 1:
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").SetString("AutoloadModule","BIMWorkbench")
        elif bimdefault == 2:
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").SetString("AutoloadModule","StartWorkbench")
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Start").SetString("AutoloadModule","BIMWorkbench")
        newdoc = self.form.settingNewdocument.isChecked()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetBool("CreateNewDoc",newdoc)
        bkp = self.form.settingBackupfiles.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetInt("CountBackupFiles",bkp)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetUnsigned("BackgroundColor2",self.form.colorButtonTop.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetUnsigned("BackgroundColor3",self.form.colorButtonBottom.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetUnsigned("DefaultShapeColor",self.form.colorButtonFaces.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetUnsigned("color",self.form.colorButtonFaces.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetUnsigned("DefaultShapeLineColor",self.form.colorButtonLines.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch").SetUnsigned("ColorHelpers",self.form.colorButtonHelpers.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetUnsigned("constructioncolor",self.form.colorButtonConstruction.property("color").rgb()<<8)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetUnsigned("ConstructionColor",self.form.colorButtonConstruction.property("color").rgb()<<8)
        height = self.form.settingCameraHeight.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("defaultCameraHeight",height)


        # set the orbit mode to turntable
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetInt("OrbitStyle",0)
        # turn thumbnails on
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetBool("SaveThumbnail",True)

        # set the working plane
        if hasattr(FreeCAD,"DraftWorkingPlane") and hasattr(FreeCADGui,"draftToolBar"):
            if wp == 1:
                FreeCAD.DraftWorkingPlane.alignToPointAndAxis(Vector(0,0,0), Vector(0,0,1), 0)
                FreeCADGui.draftToolBar.wplabel.setText("Top(XY)")
            elif wp == 2:
                FreeCAD.DraftWorkingPlane.alignToPointAndAxis(Vector(0,0,0), Vector(0,1,0), 0)
                FreeCADGui.draftToolBar.wplabel.setText("Front(XZ)")
            elif wp == 3:
                FreeCAD.DraftWorkingPlane.alignToPointAndAxis(Vector(0,0,0), Vector(1,0,0), 0)
                FreeCADGui.draftToolBar.wplabel.setText("Side(YZ)")
            else:
                FreeCADGui.draftToolBar.wplabel.setText("Auto")

        # set Draft toolbar
        if hasattr(FreeCADGui,"draftToolBar"):
            FreeCADGui.draftToolBar.widthButton.setValue(linewidth)
            FreeCADGui.draftToolBar.fontsizeButton.setValue(tsize)

        # set the grid
        if hasattr(FreeCADGui,"Snapper"):
            FreeCADGui.Snapper.setGrid()

        # set the status bar widgets
        mw = FreeCADGui.getMainWindow()
        if mw:
            st = mw.statusBar()
            statuswidget = st.findChild(QtGui.QToolBar,"BIMStatusWidget")
            if statuswidget:
                statuswidget.unitLabel.setText(statuswidget.unitsList[self.form.settingUnits.currentIndex()])
                # change the unit of the nudge button
                nudgeactions = statuswidget.nudge.menu().actions()
                if unit in [2,3,5,7]:
                    nudgelabels = statuswidget.nudgeLabelsI
                else:
                    nudgelabels = statuswidget.nudgeLabelsM
                for i in range(len(nudgelabels)):
                    nudgeactions[i].setText(nudgelabels[i])
                if not "auto" in statuswidget.nudge.text().replace("&","").lower():
                    statuswidget.nudge.setText(FreeCAD.Units.Quantity(statuswidget.nudge.text().replace("&","")).UserString)

    def setPreset(self,preset=None):

        from PySide import QtCore,QtGui

        unit = None
        decimals = None
        grid = None
        squares = None
        wp = None
        tsize = None
        font = None
        linewidth = None
        dimstyle = None
        asize = None
        author = None
        lic = None
        bimdefault = None
        newdoc = None
        bkp = None
        colTop = None
        colBottom = None
        colFace = None
        colLine = None
        colHelp = None
        colConst = None
        height = None

        if preset == 0:
            # the "Choose..." item from the presets box. Do nothing
            return

        elif preset == 1:
           # centimeters
            unit = 1
            decimals = 2
            grid = "10cm"
            squares = 10
            tsize = "20cm"
            linewidth = 1
            dimstyle = 0
            asize = "4cm"
            bkp = 2
            bimdefault = 2
            newdoc = False
            height = 4500

        elif preset == 2:
           # meters
            unit = 2
            decimals = 2
            grid = "0.1m"
            squares = 10
            tsize = "0.2m"
            linewidth = 1
            dimstyle = 0
            asize = "0.04cm"
            bkp = 2
            bimdefault = 2
            newdoc = False
            height = 4500

        elif preset == 3:
           # US
            unit = 5
            decimals = 2
            grid = "1in"
            squares = 12
            tsize = "8in"
            linewidth = 1
            dimstyle = 3
            asize = "2in"
            bkp = 2
            bimdefault = 2
            newdoc = False
            height = 4500

        elif preset == None:
            # get values from settings
            unit = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("UserSchema",0)
            unit = [0,2,3,3,1,5,0,4][unit] # less choices in our simplified dialog
            decimals = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("Decimals",2)
            grid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("gridSpacing",10)
            grid = FreeCAD.Units.Quantity(grid,FreeCAD.Units.Length).UserString
            squares = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("gridEvery",10)
            wp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("defaultWP",0)
            tsize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("textheight",10)
            tsize = FreeCAD.Units.Quantity(tsize,FreeCAD.Units.Length).UserString
            font = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetString("textfont","Sans")
            linewidth = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetInt("DefautShapeLineWidth",2)
            dimstyle = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("dimsymbol",0)
            dimstyle = [0,0,1,2,3][dimstyle] # less choices in our simplified dialog
            asize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("arrowsize",5)
            asize = FreeCAD.Units.Quantity(asize,FreeCAD.Units.Length).UserString
            author = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetString("prefAuthor","")
            lic = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetInt("prefLicenseType",0)
            lic = [0,1,2,1,3,4,1,0,0,0][lic] # less choices in our simplified dialog
            bimdefault = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").GetString("AutoloadModule","")
            if bimdefault == "BIMWorkbench":
                bimdefault = 1
            elif bimdefault == "StartWorkbench" and FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Start").GetString("AutoloadModule","") == "BIMWorkbench":
                bimdefault = 2
            else:
                bimdefault = 0
            newdoc = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetBool("CreateNewDoc",False)
            bkp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetInt("CountBackupFiles",2)
            colTop = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetUnsigned("BackgroundColor2",775244287)
            colBottom = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetUnsigned("BackgroundColor3",1905041919)
            colFace = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetUnsigned("DefaultShapeColor",4294967295)
            colLine = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetUnsigned("DefaultShapeLineColor",255)
            colHelp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch").GetUnsigned("ColorHelpers",674321151)
            colConst = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetUnsigned("constructioncolor",746455039)
            height = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("defaultCameraHeight",5)
            
        if unit != None:
            self.form.settingUnits.setCurrentIndex(unit)
        if decimals != None:
            self.form.settingDecimals.setValue(decimals)
        if grid != None:
            self.form.settingGrid.setText(grid)
        if squares != None:
            self.form.settingSquares.setValue(squares)
        if wp != None:
            self.form.settingWP.setCurrentIndex(wp)
        if tsize != None:
            self.form.settingText.setText(tsize)
        if font != None:
            self.form.settingFont.setCurrentFont(QtGui.QFont(font))
        if linewidth != None:
            self.form.settingLinewidth.setValue(linewidth)
        if dimstyle != None:
            self.form.settingDimstyle.setCurrentIndex(dimstyle)
        if asize != None:
            self.form.settingArrowsize.setText(asize)
        if author != None:
            self.form.settingAuthor.setText(author)
        if lic != None:
            self.form.settingLicense.setCurrentIndex(lic)
        if bimdefault != None:
            self.form.settingWorkbench.setCurrentIndex(bimdefault)
        if newdoc != None:
            self.form.settingNewdocument.setChecked(newdoc)
        if bkp != None:
            self.form.settingBackupfiles.setValue(bkp)
        if colTop != None:
            self.form.colorButtonTop.setProperty("color",getPrefColor(colTop))
        if colBottom != None:
            self.form.colorButtonBottom.setProperty("color",getPrefColor(colBottom))
        if colFace != None:
            self.form.colorButtonFaces.setProperty("color",getPrefColor(colFace))
        if colLine != None:
            self.form.colorButtonLines.setProperty("color",getPrefColor(colLine))
        if colHelp != None:
            self.form.colorButtonHelpers.setProperty("color",getPrefColor(colHelp))
        if colConst != None:
            self.form.colorButtonConstruction.setProperty("color",getPrefColor(colConst))
        if height:
            self.form.settingCameraHeight.setValue(height)
        # TODO - antialiasing?

def getPrefColor(color):
    r = ((color>>24)&0xFF)/255.0
    g = ((color>>16)&0xFF)/255.0
    b = ((color>>8)&0xFF)/255.0
    from PySide import QtGui
    return QtGui.QColor.fromRgbF(r,g,b)

