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


# import commands that are defined in their separate files

import BimWelcome,BimSetup,BimProject,BimLevels,BimWindows,BimIfcElements,BimViews,BimClassification



class BIM_TogglePanels:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_TogglePanels.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle panels"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle report panels on/off"),
                'Accel': 'Ctrl+0'}

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



class BIM_Trash:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Trash.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Move to Trash"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Moves the selected objects to the Trash folder"),
                'Accel': 'Shift+Del'}

    def Activated(self):

        if FreeCADGui.Selection.getSelection():
            trash = FreeCAD.ActiveDocument.getObject("Trash")
            if trash:
                if not trash.isDerivedFrom("App::DocumentObjectGroup"):
                    trash = None
            if not trash:
                trash = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Trash")
            for obj in FreeCADGui.Selection.getSelection():
                trash.addObject(obj)
                obj.ViewObject.hide()

    def IsActive(self):

        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False



class BIM_Copy(DraftTools.Move):


    def __init__(self):
        DraftTools.Move.__init__(self)
        self.copymode = True

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Copy.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Copy", "Copy"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Copies selected objects to another location"),
                'Accel': 'C,P'}



class BIM_Clone(DraftTools.Draft_Clone):


    def __init__(self):
        DraftTools.Draft_Clone.__init__(self)
        self.moveAfterCloning = True


FreeCADGui.addCommand('BIM_TogglePanels',BIM_TogglePanels())
FreeCADGui.addCommand('BIM_Trash',BIM_Trash())
FreeCADGui.addCommand('BIM_Copy',BIM_Copy())
FreeCADGui.addCommand('BIM_Clone',BIM_Clone())


class BimSelectionObserver:
    
    "a multipurpose selection observer that stays active while in BIM workbench"

    def addSelection(self,document, object, element, position):

        BimViews.update()

    def clearSelection(self,document):
        
        BimViews.update()



def setStatusIcons(show=True):

    "shows or hides the BIM icons in the status bar"

    def toggle(): FreeCADGui.runCommand("BIM_TogglePanels")

    mw = FreeCADGui.getMainWindow()
    if mw:
        st = mw.statusBar()
        from PySide import QtCore,QtGui
        statuswidget = st.findChild(QtGui.QPushButton,"BIMStatusWidget")
        if show:
            if statuswidget:
                statuswidget.show()
            else:
                statuswidget = QtGui.QPushButton()
                statuswidget.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_TogglePanels.svg")))
                statuswidget.setText("")
                statuswidget.setToolTip("Toggle report panels on/off")
                statuswidget.setObjectName("BIMStatusWidget")
                QtCore.QObject.connect(statuswidget,QtCore.SIGNAL("pressed()"),toggle)
                st.addPermanentWidget(statuswidget)
        else:
            if statuswidget:
                statuswidget.hide()
