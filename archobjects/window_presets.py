"""
 FreeCAD script - macro
 to be used with the OnePartLib part library

 copyright 2019 Carlo Dormeletti (onekk)
 carlo.dormeletti@yahoo.com

 Version:   

"""

import sys
import datetime
import time

import FreeCAD
import FreeCADGui
from FreeCAD import Rotation, Vector
import Part
App = FreeCAD

# BEGIN DOC Settings
DEBUG = True
DBG_LOAD = False
DOC_NAME = "finestra"
# END DOC settings


#from math import pi cos, sin, pi, sqrt
import numpy as np


def activate_doc():
    """activate document"""
    FreeCAD.setActiveDocument(DOC_NAME)
    FreeCAD.ActiveDocument = FreeCAD.getDocument(DOC_NAME)
    FreeCADGui.ActiveDocument = FreeCADGui.getDocument(DOC_NAME)
    if DBG_LOAD is True:    
        print("{0} activated".format(DOC_NAME))


def setview():
    """Rearrange View"""
    DOC.recompute()
    VIEW.viewAxometric()
    VIEW.setAxisCross(True)
    VIEW.fitAll()


def clear_doc():
    """Clear the active document deleting all the objects"""
    for obj in DOC.Objects:
        DOC.removeObject(obj.Name)

# =========================

# the code below creates a document on every BIM workbench load
# so turning it off for now - Yorik

# if FreeCAD.ActiveDocument is None:
#    FreeCAD.newDocument(DOC_NAME)
#    if DBG_LOAD is True:    
#        print("Document: {0} Created".format(DOC_NAME))

# test if there is an active document with a "proper" name
#if FreeCAD.ActiveDocument.Name == DOC_NAME:
#    if DBG_LOAD is True:    
#        print("DOC_NAME exist")
#else:
#    if DBG_LOAD is True:    
#        print("DOC_NAME is not active")
#    # test if there is a document with a "proper" name
#    try:
#        FreeCAD.getDocument(DOC_NAME)
#    except NameError:
#        if DBG_LOAD is True:    
#            print("No Document: {0}".format(DOC_NAME))
#        FreeCAD.newDocument(DOC_NAME)
#        if DBG_LOAD is True:    
#            print("Document {0} Created".format(DOC_NAME))

#DOC = FreeCAD.getDocument(DOC_NAME)
#GUI = FreeCADGui.getDocument(DOC_NAME)
#VIEW = GUI.ActiveView    
#if DBG_LOAD is True:    
#    print("DOC : {0} GUI : {1}".format(DOC, GUI))

# activate_doc()

# if DBG_LOAD is True:    
#    print(FreeCAD.ActiveDocument.Name)

# clear_doc()

# =================================

EPS = 0.002

VZOR = App.Vector(0, 0, 0)
ROT0 = App.Rotation(0, 0, 0)
ROTX90 = App.Rotation(0, 0, 90)
ROTXN90 = App.Rotation(0, 0, -90)
ROTY90 = App.Rotation(0, 90, 0)
ROTZ180 = App.Rotation(180, 0, 0)
#Used to shorten most Placements
PL0 = App.Placement(VZOR, ROT0)

# DOCUMENT START HERE

def frame_rectangular(tel_name, tel_w, tel_h , tel_ww, tel_wh, tel_th, et=0):
    i_tel_w = tel_w - tel_ww * 2
    i_tel_h = tel_h - tel_wh * 2

    if et == 0:
        ofz = 0
    else:
        ofz = tel_wh

    ep0 = (tel_w * -0.5, 0, ofz)
    ep1 = (tel_w * 0.5, 0, ofz)
    ep2 = (tel_w * 0.5, 0, tel_h + ofz)
    ep3 = (tel_w * -0.5, 0, tel_h + ofz)

    ip0 = (i_tel_w * -0.5, 0, tel_ww + ofz)
    ip1 = (i_tel_w * 0.5, 0, tel_ww + ofz)
    ip2 = (i_tel_w * 0.5, 0, tel_ww + i_tel_h + ofz)
    ip3 = (i_tel_w * -0.5, 0, tel_ww + i_tel_h + ofz)
  
    tel_b = (ep0, ep1, ip1, ip0, ep0)
    tel_bp = Part.makePolygon([Vector(*vtx) for vtx in tel_b])

    tel_r = (ep1, ep2, ip2, ip1, ep1)
    tel_rp = Part.makePolygon([Vector(*vtx) for vtx in tel_r])

    tel_t = (ep2, ep3, ip3, ip2, ep2)
    tel_tp = Part.makePolygon([Vector(*vtx) for vtx in tel_t])

    tel_l = (ep3, ep0, ip0, ip3, ep3)
    tel_lp = Part.makePolygon([Vector(*vtx) for vtx in tel_l])

    tel_fb = Part.makeFilledFace(tel_bp.Edges) 
    tel_fbs = tel_fb.extrude(Vector(0, tel_th, 0))

    tel_fr = Part.makeFilledFace(tel_rp.Edges) 
    tel_frs = tel_fr.extrude(Vector(0, tel_th, 0))
    
    tel_ft = Part.makeFilledFace(tel_tp.Edges) 
    tel_fts = tel_ft.extrude(Vector(0, tel_th, 0))

    tel_fl = Part.makeFilledFace(tel_lp.Edges) 
    tel_fls = tel_fl.extrude(Vector(0, tel_th, 0))    

    #obj0 = DOC.addObject("Part::Feature", tel_name)
    return Part.makeCompound((tel_fbs, tel_frs, tel_fts, tel_fls))
    #obj0.ViewObject.ShapeColor = (0.54, 0.27, 0.07) # rgb(139, 69, 19)

    #return obj0


def window_single_pane(opening_th=300, opening_height=1400, opening_width=1200,
             frame_width=50, frame_th=50, glass_th=21):
    vetro_add = 5
    # permit to differentiate from the top-bottom 
    # and left right    
    frame_height = frame_width 
    cont_w = frame_width * 2
    cont_h = frame_height * 2

    ea_w = opening_width - cont_w
    ea_h = opening_height - cont_h

    v_w = ea_w - cont_w + vetro_add * 2
    v_h = ea_h - cont_h + vetro_add * 2
 
    vp0 = (v_w * -0.5, 0, cont_w - vetro_add)
    vp1 = (v_w * 0.5, 0, cont_w  - vetro_add)
    vp2 = (v_w * 0.5, 0, cont_h - vetro_add + v_h)
    vp3 = (v_w * -0.5, 0, cont_h - vetro_add + v_h)

    vetro_pt = (vp0, vp1, vp2, vp3, vp0)    
    vetro_p = Part.makePolygon([Vector(*vtx) for vtx in vetro_pt])

    vetro_f = Part.makeFilledFace(vetro_p.Edges) 
    vetro_s = vetro_f.extrude(Vector(0, glass_th, 0))
    vetro_s.Placement = FreeCAD.Placement(Vector(0, (frame_th - glass_th) * 0.5, 0), ROT0)

    obj_t = frame_rectangular("telaio", opening_width, opening_height, frame_width, 
                   frame_height, frame_th, 0)
   
    obj_ea = frame_rectangular("elemento apribile", ea_w, ea_h, frame_width, 
                   frame_height, frame_th, 1)

    compound = Part.makeCompound([obj_t, obj_ea, vetro_s])
    return compound
    obj1 = DOC.addObject("Part::Feature", "vetro")
    obj1.Shape = vetro_s
    obj1.ViewObject.ShapeColor = (0.33, 0.67, 1.00)
    obj1.ViewObject.Transparency = 50

    obj_f = DOC.addObject("Part::Compound", "finestra")
    obj_f.Links = [obj_t, obj_ea, obj1]  
 
    return obj_f

