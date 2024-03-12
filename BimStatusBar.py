# -*- coding: utf8 -*-

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


# Language path for InitGui.py


def getLanguagePath():
    return os.path.join(os.path.dirname(__file__), "translations")


# Status bar buttons


def setStatusIcons(show=True):
    "shows or hides the BIM icons in the status bar"

    import FreeCADGui
    from PySide import QtCore, QtGui

    nudgeLabelsM = [
        translate("BIM", "Custom..."),
        '1/16"',
        '1/8"',
        '1/4"',
        '1"',
        '6"',
        "1'",
        translate("BIM", "Auto"),
    ]
    nudgeLabelsI = [
        translate("BIM", "Custom..."),
        "1 mm",
        "5 mm",
        "1 cm",
        "5 cm",
        "10 cm",
        "50 cm",
        translate("BIM", "Auto"),
    ]

    def toggle(state):
        FreeCADGui.runCommand("BIM_TogglePanels")

    def toggleBimViews(state):
        FreeCADGui.runCommand("BIM_Views")

    def toggleBackground(state):
        FreeCADGui.runCommand("BIM_Background")

    def addonMgr():
        mw = FreeCADGui.getMainWindow()
        if mw:
            st = mw.statusBar()
            statuswidget = st.findChild(QtGui.QToolBar, "BIMStatusWidget")
            if statuswidget:
                updatebutton = statuswidget.findChild(QtGui.QPushButton, "UpdateButton")
                if updatebutton:
                    statuswidget.actions()[-1].setVisible(False)
        FreeCADGui.runCommand("Std_AddonMgr")

    def setNudge(action):
        utext = action.text().replace("&", "")
        if utext == nudgeLabelsM[0]:
            # load dialog
            form = FreeCADGui.PySideUic.loadUi(
                os.path.join(os.path.dirname(__file__), "dialogNudgeValue.ui")
            )
            # center the dialog over FreeCAD window
            mw = FreeCADGui.getMainWindow()
            form.move(
                mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center()
            )
            result = form.exec_()
            if not result:
                return
            utext = form.inputField.text()
        action.parent().parent().parent().setText(utext)

    class CheckWorker(QtCore.QThread):
        updateAvailable = QtCore.Signal(bool)

        def __init__(self):
            QtCore.QThread.__init__(self)

        def run(self):
            try:
                import git
            except ImportError:
                return
            FreeCAD.Console.PrintLog(
                "Checking for available updates of the BIM workbench\n"
            )
            bimdir = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "BIM")
            if os.path.exists(bimdir):
                if os.path.exists(bimdir + os.sep + ".git"):
                    gitrepo = git.Git(bimdir)
                    try:
                        gitrepo.fetch()
                        if "git pull" in gitrepo.status():
                            self.updateAvailable.emit(True)
                            return
                    except:
                        # can fail for any number of reasons, ex. not being online
                        pass
            self.updateAvailable.emit(False)

    def checkUpdates():
        FreeCAD.bim_update_checker = CheckWorker()
        FreeCAD.bim_update_checker.updateAvailable.connect(showUpdateButton)
        FreeCAD.bim_update_checker.start()

    def showUpdateButton(avail):
        if avail:
            FreeCAD.Console.PrintLog("A BIM update is available\n")
            mw = FreeCADGui.getMainWindow()
            if mw:
                st = mw.statusBar()
                statuswidget = st.findChild(QtGui.QToolBar, "BIMStatusWidget")
                if statuswidget:
                    updatebutton = statuswidget.findChild(
                        QtGui.QAction, "UpdateButton"
                    )
                    if updatebutton:
                        # updatebutton.show() # doesn't work for some reason
                        statuswidget.actions()[-1].setVisible(True)
        else:
            FreeCAD.Console.PrintLog("No BIM update available\n")
        if hasattr(FreeCAD, "bim_update_checker"):
            del FreeCAD.bim_update_checker

    def toggleContextMenu(point):
        # DISABLED - TODO need to find a way to add a context menu to a QAction...
        FreeCADGui.BimToggleMenu = QtGui.QMenu()
        for t in ["Report view", "Python console", "Selection view", "Combo View"]:
            a = QtGui.QAction(t)
            # a.setCheckable(True)
            # a.setChecked(FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetBool("toggle"+t.replace(" ",""),True))
            FreeCADGui.BimToggleMenu.addAction(a)
        pos = FreeCADGui.getMainWindow().cursor().pos()
        FreeCADGui.BimToggleMenu.triggered.connect(toggleSaveSettings)
        # QtCore.QObject.connect(FreeCADGui.BimToggleMenu,QtCore.SIGNAL("triggered(QAction *)"),toggleSaveSettings)
        FreeCADGui.BimToggleMenu.popup(pos)

    def toggleSaveSettings(action):
        t = action.text()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetBool(
            "toggle" + t.replace(" ", ""), action.isChecked()
        )
        if hasattr(FreeCADGui, "BimToggleMenu"):
            del FreeCADGui.BimToggleMenu

    # main code

    mw = FreeCADGui.getMainWindow()
    if mw:
        st = mw.statusBar()
        statuswidget = st.findChild(QtGui.QToolBar, "BIMStatusWidget")
        if show:
            if statuswidget:
                statuswidget.show()
            else:
                statuswidget = QtGui.QToolBar()
                statuswidget.setObjectName("BIMStatusWidget")
                s = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").GetInt("ToolbarIconSize", 24)
                statuswidget.setIconSize(QtCore.QSize(s,s))
                st.insertPermanentWidget(2, statuswidget)

                # report panels toggle button
                togglebutton = QtGui.QAction()
                togglemenu = QtGui.QMenu()
                for t in ["Toggle", "Report view", "Python console", "Selection view", "Combo View"]:
                    a = QtGui.QAction(t)
                    togglemenu.addAction(a)
                togglemenu.triggered.connect(toggleSaveSettings)
                togglebutton.setIcon(
                    QtGui.QIcon(
                        os.path.join(
                            os.path.dirname(__file__), "icons", "BIM_TogglePanels.svg"
                        )
                    )
                )
                togglebutton.setText("")
                togglebutton.setToolTip(
                    translate("BIM", "Toggle report panels on/off (Ctrl+0)")
                )
                togglebutton.setCheckable(True)
                rv = mw.findChild(QtGui.QWidget, "Python console")
                if rv and rv.isVisible():
                    togglebutton.setChecked(True)
                statuswidget.togglebutton = togglebutton
                #togglebutton.setMenu(togglemenu)
                togglebutton.triggered.connect(toggle)
                statuswidget.addAction(togglebutton)

                # bim views widget toggle button
                import BimViews

                bimviewsbutton = QtGui.QAction()
                bimviewsbutton.setIcon(
                    QtGui.QIcon(
                        os.path.join(
                            os.path.dirname(__file__), "icons", "BIM_Views.svg"
                        )
                    )
                )
                bimviewsbutton.setText("")
                bimviewsbutton.setToolTip(
                    translate("BIM", "Toggle BIM views panel on/off (Ctrl+9)")
                )
                bimviewsbutton.setCheckable(True)
                if BimViews.findWidget():
                    bimviewsbutton.setChecked(True)
                statuswidget.bimviewsbutton = bimviewsbutton
                bimviewsbutton.triggered.connect(toggleBimViews)
                statuswidget.addAction(bimviewsbutton)

                # background toggle button
                bgbutton = QtGui.QAction()
                #bwidth = bgbutton.fontMetrics().boundingRect("AAAA").width()
                #bgbutton.setMaximumWidth(bwidth)
                bgbutton.setIcon(
                    QtGui.QIcon(
                        os.path.join(
                            os.path.dirname(__file__), "icons", "BIM_Background.svg"
                        )
                    )
                )
                bgbutton.setText("")
                bgbutton.setToolTip(
                    translate(
                        "BIM", "Toggle 3D view background between simple and gradient"
                    )
                )
                statuswidget.bgbutton = bgbutton
                bgbutton.triggered.connect(toggleBackground)
                statuswidget.addAction(bgbutton)

                # ifc widgets
                try:
                    import ifc_status
                except:
                    pass
                else:
                    ifc_status.set_status_widget(statuswidget)

                # update notifier button (starts hidden)
                updatebutton = QtGui.QAction()
                updatebutton.setObjectName("UpdateButton")
                #updatebutton.setMaximumWidth(bwidth)
                updatebutton.setIcon(QtGui.QIcon(":/icons/view-refresh.svg"))
                updatebutton.setText("")
                updatebutton.setToolTip(
                    translate(
                        "BIM",
                        "An update to the BIM workbench is available. Click here to open the addons manager.",
                    )
                )
                updatebutton.triggered.connect(addonMgr)
                updatebutton.setVisible(False)
                statuswidget.addAction(updatebutton)
                QtCore.QTimer.singleShot(
                    2500, checkUpdates
                )  # delay a bit the check for BIM WB update...

                # nudge button
                nudge = QtGui.QPushButton(nudgeLabelsM[-1])
                nudge.setIcon(
                    QtGui.QIcon(
                        os.path.join(
                            os.path.dirname(__file__), "icons", "BIM_Nudge.svg"
                        )
                    )
                )
                nudge.setFlat(True)
                nudge.setToolTip(
                    translate(
                        "BIM",
                        "The value of the nudge movement (rotation is always 45°).\n\nCTRL+arrows to move\nCTRL+, to rotate left\nCTRL+. to rotate right\nCTRL+PgUp to extend extrusion\nCTRL+PgDown to shrink extrusion\nCTRL+/ to switch between auto and manual mode",
                    )
                )
                statuswidget.addWidget(nudge)
                statuswidget.nudge = nudge
                menu = QtGui.QMenu(nudge)
                gnudge = QtGui.QActionGroup(menu)
                for u in nudgeLabelsM:
                    a = QtGui.QAction(gnudge)
                    a.setText(u)
                    menu.addAction(a)
                nudge.setMenu(menu)
                gnudge.triggered.connect(setNudge)
                statuswidget.nudgeLabelsI = nudgeLabelsI
                statuswidget.nudgeLabelsM = nudgeLabelsM

        else:
            if statuswidget is None:
                # when switching workbenches, the toolbar sometimes "jumps"
                # out of the status bar to any other dock area...
                statuswidget = mw.findChild(QtGui.QToolBar, "BIMStatusWidget")
            if statuswidget:
                statuswidget.hide()
                statuswidget.toggleViewAction().setVisible(False)
