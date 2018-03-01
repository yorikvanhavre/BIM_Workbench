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

def QT_TRANSLATE_NOOP(ctx,txt): return txt



class BIM_Setup:


    def GetResources(self):

        return {'Pixmap'  : ":icons/preferences-system.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Setup", "Setup"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Setup", "Set some common preferences form BIM workflow")}

    def Activated(self):

        # load dialog
        from PySide import QtGui
        form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogSetup.ui"))

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        form.move(mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center())

        # show/hide first time text
        firsttime = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetBool("FirstTime",True)
        if not firsttime:
            form.welcometext.hide()

        # fill values from current settings
        unit = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("UserSchema",0)
        unit = [0,2,3,3,1,4,0][unit] # less choices in our simplified dialog
        form.settingUnits.setCurrentIndex(unit)
        decimals = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("Decimals",2)
        form.settingDecimals.setValue(decimals)
        grid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("gridSpacing",10)
        grid = FreeCAD.Units.Quantity(grid,FreeCAD.Units.Length).UserString
        form.settingGrid.setText(grid)
        wp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("defaultWP",0)
        form.settingWP.setCurrentIndex(wp)
        tsize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("textheight",10)
        tsize = FreeCAD.Units.Quantity(tsize,FreeCAD.Units.Length).UserString
        form.settingText.setText(tsize)
        font = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetString("textfont","Sans")
        form.settingFont.setCurrentFont(QtGui.QFont(font))
        linewidth = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetInt("DefautShapeLineWidth",2)
        form.settingLinewidth.setValue(linewidth)
        dimstyle = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("dimsymbol",0)
        dimstyle = [0,0,1,2][dimstyle] # less choices in our simplified dialog
        form.settingDimstyle.setCurrentIndex(dimstyle)
        asize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("arrowsize",5)
        asize = FreeCAD.Units.Quantity(asize,FreeCAD.Units.Length).UserString
        form.settingArrowsize.setText(asize)
        author = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetString("prefAuthor","")
        form.settingAuthor.setText(author)
        lic = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetInt("prefLicenseType",0)
        lic = [0,1,2,1,3,4,1,0,0,0][lic] # less choices in our simplified dialog
        form.settingLicense.setCurrentIndex(lic)
        bimdefault = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").GetString("AutoloadModule","")
        form.settingWorkbench.setChecked(bimdefault == "BIMWorkbench")
        newdoc = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetBool("CreateNewDoc",False)
        form.settingNewdocument.setChecked(newdoc)
        bkp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetInt("CountBackupFiles",2)
        form.settingBackupfiles.setValue(bkp)

        # show dialog and exit if cancelled
        result = form.exec_()
        if not result:
            return

        # set preference values
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetBool("FirstTime",False)
        unit = form.settingUnits.currentIndex()
        unit = [0,4,1,3,5][unit] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema",unit)
        decimals = form.settingDecimals.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("Decimals",decimals)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetBool("UseGlobalDecimals",True)
        grid = form.settingGrid.text()
        grid = FreeCAD.Units.Quantity(grid).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("gridSpacing",grid)
        wp = form.settingWP.currentIndex()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("defaultWP",wp)
        tsize = form.settingText.text()
        tsize = FreeCAD.Units.Quantity(tsize).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("textheight",tsize)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetFloat("FontSize",tsize) # TODO - check if this needs a mult factor?
        font = form.settingFont.currentFont().family()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetString("textfont",font)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Labels").SetString("LabelFont",font)
        linewidth = form.settingLinewidth.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetInt("DefautShapeLineWidth",linewidth)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("linewidth",linewidth)
        # TODO - TechDraw default line styles
        dimstyle = form.settingDimstyle.currentIndex()
        ddimstyle = [0,2,3][dimstyle] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("dimsymbol",ddimstyle)
        tdimstyle = [3,0,2][dimstyle] # TechDraw has different order than Draft
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetInt("dimsymbol",tdimstyle)
        asize = form.settingArrowsize.text()
        asize = FreeCAD.Units.Quantity(asize).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("arrowsize",asize)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetFloat("ArrowSize",asize)
        author = form.settingAuthor.text()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetString("prefAuthor",author)
        lic = form.settingLicense.currentIndex()
        lic = [0,1,2,4,5][lic] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetInt("prefLicenseType",lic)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetString("prefLicenseUrl","") # TODO - set correct license URL
        bimdefault = form.settingWorkbench.isChecked()
        if bimdefault:
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").SetString("AutoloadModule","BIMWorkbench")
        newdoc = form.settingNewdocument.isChecked()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetBool("CreateNewDoc",newdoc)
        bkp = form.settingBackupfiles.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetInt("CountBackupFiles",bkp)

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


class BIM_TogglePanels:


    def GetResources(self):

        return {'Pixmap'  : ":icons/preferences-display.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle panels"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle report panels on/off")}

    def Activated(self):

        from  PySide import QtGui
        mw = FreeCADGui.getMainWindow()
        windows = [mw.findChild(QtGui.QWidget,"Python console"),mw.findChild(QtGui.QWidget,"Selection view"),mw.findChild(QtGui.QWidget,"Report view")]
        if windows[0].isVisible():
            for w in windows:
                w.hide()
        else:
            for w in windows:
                w.show()

FreeCADGui.addCommand('BIM_Setup',BIM_Setup())
FreeCADGui.addCommand('BIM_TogglePanels',BIM_TogglePanels())
