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


# import commands that are defined in their separate files

import BimWelcome,BimSetup,BimProject,BimLevels,BimWindows

# some useful closed 2D shapes
symbolShapes = { 
"Man Vertical":[(-236.868, 481.548),(-222.936, 441.41999999999996),(-204.36, 409.308),(-181.14, 385.23600000000005),(-162.564, 353.136),(-92.892, 152.484),(-74.31599999999999, 120.384),(-41.796, 112.356),(-65.028, 88.284),(-150.324, 67.224),(-152.64, 53.928),(-139.33200000000002, 40.128),(-83.46000000000001, 26.34),(-74.31599999999999),(0.0),(32.508, 8.028),(78.96000000000001, 56.184),(143.976, 72.228),(167.208, 96.312),(153.264, 136.44),(134.688, 176.568),(125.4, 224.72400000000002),(120.756, 280.89599999999996),(120.756, 409.308),(125.4, 465.492),(153.264, 609.9599999999999),(157.908, 666.132),(167.208, 779.6039999999999),(199.716, 787.632),(274.032, 787.632),(292.608, 819.732),(301.896, 867.888),(292.608, 980.244),(274.032, 1012.356),(297.252, 1036.4279999999999),(315.828, 1068.528),(329.76, 1108.6560000000002),(334.404, 1164.8400000000001),(325.11600000000004, 1212.9959999999999),(325.11600000000004, 1277.196),(315.828, 1325.352),(315.828, 1389.564),(301.896, 1429.692),(274.032, 1445.748),(250.8, 1469.82),(195.072, 1517.9759999999999),(167.208, 1534.02),(157.908, 1582.176),(171.852, 1622.3039999999999),(181.14, 1670.46),(176.49599999999998, 1726.644),(148.62, 1742.6999999999998),(116.11200000000001, 1750.716),(88.24799999999999, 1766.772),(51.083999999999996, 1766.772),(-13.931999999999999, 1750.716),(-41.796, 1734.672),(-65.028, 1710.588),(-60.384, 1654.4160000000002),(-65.028, 1598.2320000000002),(-41.796, 1574.16),(-27.863999999999997, 1534.02),(4.644000000000001, 1526.004),(0.0, 1469.82),(-23.220000000000002, 1445.748),(-41.796, 1413.636),(-65.028, 1389.564),(-83.604, 1357.464),(-111.468, 1277.196),(-116.11200000000001, 1221.0240000000001),(-171.852, 1060.512),(-190.428, 964.1999999999999),(-204.36, 924.072),(-185.784, 827.7600000000001),(-213.648, 682.188),(-241.512, 537.72)],
"Woman Vertical":[(-370.512, 762.5748),(-354.576, 793.7028),(-350.59200000000004, 848.1708),(-342.62399999999997, 894.8628),(-342.62399999999997, 957.1068),(-334.656, 1066.0548000000001),(-322.704, 1112.7348),(-306.768, 1206.1188),(-302.784, 1260.5868),(-290.832, 1299.4908),(-274.89599999999996, 1330.6188000000002),(-227.08800000000002, 1377.3108),(-199.2, 1385.0868),(-175.29600000000002, 1400.6508),(-187.248, 1439.5548000000001),(-247.008, 1509.5867999999998),(-239.04, 1556.2788),(-215.136, 1579.6188),(-175.29600000000002, 1626.3108),(-127.48799999999999, 1657.4388),(-99.6, 1665.2148),(-67.728, 1665.2148),(-43.824000000000005, 1649.6508000000001),(-23.904, 1626.3108),(-7.968, 1595.1827999999998),(-4.440892098500626e-16, 1548.5028),(11.952, 1509.5867999999998),(3.984, 1462.9068),(-11.952000000000002, 1431.7788),(7.967999999999998, 1408.4388000000001),(55.775999999999996, 1377.3108),(83.664, 1369.5228),(103.58399999999999, 1346.1828),(127.5, 1330.6188000000002),(139.452, 1291.7148),(147.42, 1245.0228000000002),(151.40400000000002, 1190.5548),(183.27599999999998, 1128.2988),(207.18, 1050.4908),(207.18, 925.9908),(211.164, 871.5228000000001),(211.164, 809.2668),(219.132, 762.5748),(215.148, 700.3308000000001),(187.26000000000002, 692.5428),(163.356, 708.1068),(143.436, 739.2348),(139.452, 684.7668),(147.42, 575.8235999999999),(155.388, 529.1352),(159.372, 474.666),(147.42, 435.7584),(91.632, 420.1956),(67.728, 404.63280000000003),(59.76, 357.9444),(47.808, 311.256),(31.871999999999996, 280.1304),(-7.968, 233.442),(-11.952, 178.97279999999998),(-7.967999999999999, 124.5024),(0.0, 77.814),(11.952, 38.9076),(0.0),(-27.887999999999998, -7.7808),(-55.775999999999996),(-79.68, 15.5628),(-107.568, 23.3448),(-127.48799999999999, 46.6884),(-119.52, 93.3768),(-71.712, 186.7536),(-79.68, 233.442),(-103.58399999999999, 311.256),(-111.55199999999999, 357.9444),(-116.56800000000001, 426.5772),(-167.328, 412.4148),(-191.232, 396.852),(-207.16799999999998, 427.9776),(-211.15200000000002, 482.4468),(-203.184, 529.1352),(-199.2, 583.6056),(-191.232, 630.294),(-187.248, 684.7668),(-191.232, 739.2348),(-203.184, 778.1388000000001),(-211.15200000000002, 824.8308),(-211.15200000000002, 887.0748000000001),(-187.248, 964.8948),(-171.31199999999998, 1058.2667999999999),(-187.248, 1089.3948),(-199.2, 1128.2988),(-215.136, 1097.1827999999998),(-223.10399999999998, 1050.4908),(-247.008, 972.6708),(-262.944, 941.5548),(-274.89599999999996, 902.6388),(-290.832, 871.5228000000001),(-282.86400000000003, 762.5748),(-290.832, 715.8948),(-330.672, 669.2028),(-358.56, 676.9788),(-374.496, 708.1068)],
"Person Top":[(-178.33231999999998, -80.27287),(-81.78978000000001, -196.21025),(-4.555729999999999, -279.02265),(188.52935000000002, -314.90802),(191.28772999999998, -287.3039),(235.42145, -281.78308000000004),(246.45487999999997, -267.98100000000005),(326.44728, -265.2206),(373.33938, -187.929),(365.0643, -176.88735),(315.41384999999997, -174.12695),(362.30593, -154.80405),(348.51415000000003, -143.7624),(276.79683, -171.36652999999998),(238.1798, -210.01232),(196.80442000000002, -210.01232),(116.81202, -174.12695),(125.0871, 35.664500000000004),(69.91995, 173.68517),(169.22085, 135.03937),(196.80442000000002, 63.26863),(227.14638000000002, 43.945730000000005),(232.66310000000001, 49.46655),(202.32115000000002, 96.39359999999999),(235.42145, 88.11235),(251.97160000000002, 54.9874),(257.48832, 123.99773000000002),(221.62965, 154.36227),(191.28772999999998, 176.4456),(177.49592, 204.04971999999998),(177.49592, 223.37261999999998),(86.47009999999999, 284.10173),(9.236050000000002, 308.94545),(-43.17275, 303.42462),(-109.37334999999999, 242.69552),(-156.26545, 132.27897),(-192.1241, -8.502119999999994)],
}

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


class BIM_Symbol:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Symbol.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Symbol", "Add symbol"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Symbol", "Inserts a symbol object to the current document"),
                'Accel': 'Shift+Del'}

    def Activated(self):
        self.symbol = None
        FreeCADGui.Snapper.getPoint(callback=self.insert,extradlg=self.taskbox())

    def taskbox(self):
        from PySide import QtCore,QtGui
        w = QtGui.QWidget()
        w.setWindowTitle(translate("Arch","Symbol options", utf8_decode=True))
        lay = QtGui.QVBoxLayout(w)
        combo = QtGui.QComboBox()
        for symbol in symbolShapes.keys():
            combo.addItem(symbol)
        lay.addWidget(combo)
        QtCore.QObject.connect(combo,QtCore.SIGNAL("currentIndexChanged(int)"),self.setSymbol)
        return w

    def setSymbol(self,i):
        if i >= 0:
            self.symbol = symbolShapes[i]

    def insert(self,point=None,obj=None):
        if self.point and self.symbol:
            makeSymbol(self.symbol,self.point)

def makeSymbol(symbol,point):
    points = [FreeCAD.Vector(p[0],p[1],0) for p in symbolShapes[symbol]]
    points.append(points[0])
    import Part
    shape = Part.makePolygon(points)
    shape = Part.Face(shape)
    shape.show()



FreeCADGui.addCommand('BIM_TogglePanels',BIM_TogglePanels())
FreeCADGui.addCommand('BIM_Trash',BIM_Trash())
FreeCADGui.addCommand('BIM_Symbol',BIM_Symbol())



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



class BimSelectionObserver:


    def __init__(self):
        self.enabled = []

    def addSelection(self,doc,obj,sub,pnt):
        obj = FreeCAD.getDocument(doc).getObject(obj)
        if obj:
            if hasattr(obj,"Subtractions"):
                for sub in obj.Subtractions:
                    if not sub.ViewObject.Visibility:
                        sub.ViewObject.show()
                        if not sub in self.enabled:
                            self.enabled.append(sub)

    def clearSelection(self,doc):
        for sub in self.enabled:
            for sub in obj.Subtractions:
                sub.ViewObject.hide()
        self.enabled = []
