# -*- coding: utf8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2019 Yorik van Havre <yorik@uncreated.net>              *
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

import os,FreeCAD,FreeCADGui,DraftTools,DraftVecUtils
from  PySide import QtCore,QtGui

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator


class BIM_TogglePanels:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_CurtainWall.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Curtain wall"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Builds a curtain wall from a selected face"),
                'Accel': 'C,W'}

    def Activated(self):

        import Part
        edges = []
        for sel in FreeCADGui.Selection.getSelectionEx():
            for sub in sel.SubObjects:
                if insinstance(sub,Part.Edge):
                    edges.append(sub)
        if edges:
            makeCurtainWall(edges)


def sortedge(edge):

    vdir = FreeCAD.Vector(1,0,0)
    proj = DraftVecUtils.project(edge.CenterOfMass,vdir)
    if proj.getAngle(vdir) < 1:
        return proj.Length
    else:
        return -proj.Length

def makeFlatFace(mobile=[],fixed=[],vert=False):
    
    import Part,DraftGeomUtils
    if not fixed:
        pol = Part.makePolygon(mobile+[mobile[0]])
        pol = DraftGeomUtils.flattenWire(pol)
        return Part.Face(pol)
    elif len(fixed) == 3:
        tempf = Part.Face(Part.makePolygon(fixed+[fixed[0]]))
        v4 = mobile[0].add(DraftVecUtils.project(tempf.CenterOfMass.sub(mobile[0]),tempf.normalAt(0,0)))
        pol = Part.makePolygon([fixed[0],fixed[1],v4,fixed[2],fixed[0]])
        pol = DraftGeomUtils.flattenWire(pol)
        return Part.Face(pol)
    elif len(fixed) == 2:
        tp = DraftGeomUtils.findMidpoint(Part.LineSegment(mobile[0],mobile[1]).toShape())
        tempf = Part.Face(Part.makePolygon(fixed+[tp,fixed[0]]))
        v4 = mobile[0].add(DraftVecUtils.project(tempf.CenterOfMass.sub(mobile[0]),tempf.normalAt(0,0)))
        v5 = mobile[1].add(DraftVecUtils.project(tempf.CenterOfMass.sub(mobile[1]),tempf.normalAt(0,0)))
        if vert:
            pol = Part.makePolygon([fixed[0],v4,v5,fixed[1],fixed[0]])
        else:
            pol = Part.makePolygon(fixed+[v4,v5,fixed[0]])
        pol = DraftGeomUtils.flattenWire(pol)
        return Part.Face(pol)
        

def makeCurtainWall(edges,subdiv=5,detach=False):
    
    import Part
    
    edges = sorted(edges,key=sortedge)
    faces = []
    p0 = edges[0].Vertexes[0].Point
    
    for i in range(len(edges)-1):
        e1 = edges[i]
        e2 = edges[i+1]
        pts1 = e1.discretize(Number=subdiv)
        if pts1[0].sub(p0).Length > pts1[-1].sub(p0).Length:
            pts1.reverse()
        pts2 = e2.discretize(Number=subdiv)
        if pts2[0].sub(p0).Length > pts2[-1].sub(p0).Length:
            pts2.reverse()
        for j in range(subdiv-1):
            p1 = pts1[j]
            p2 = pts2[j]
            p3 = pts2[j+1]
            p4 = pts1[j+1]
            if detach:
                fac = makeFlatFace(mobile=[p1,p2,p3,p4])
            elif (i == 0) and (j == 0):
                fac = makeFlatFace(mobile=[p1,p2,p3,p4])
            elif i == 0:
                p5 = faces[-1].Vertexes[3].Point
                p6 = faces[-1].Vertexes[2].Point
                fac = makeFlatFace(fixed=[p5,p6],mobile=[p3,p4])
            elif j == 0:
                p5 = faces[-(subdiv-1)].Vertexes[1].Point
                p6 = faces[-(subdiv-1)].Vertexes[2].Point
                fac = makeFlatFace(fixed=[p5,p6],mobile=[p2,p3],vert=True)
            else:
                p5 = faces[-1].Vertexes[3].Point
                p6 = faces[-1].Vertexes[2].Point
                p7 = faces[-(subdiv-1)].Vertexes[2].Point
                fac = makeFlatFace(fixed=[p5,p6,p7],mobile=[p3])
            faces.append(fac)
    if faces:
        if detach:
            shell = Part.makeCompound(faces)
        else:
            shell = Part.makeShell(faces)
        Part.show(shell)

