#***************************************************************************
#*   Copyright (c) 2020 Carlo Pavan                                        *
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
"""Provide the object code for Arch Opening object."""
## @package opening
# \ingroup ARCH
# \brief Provide the object code for Arch Opening object.

import FreeCAD as App

import DraftVecUtils

# from archutils import IFCutils


class Opening(object):
    def __init__(self, obj=None):
        self.Object = obj
        if obj:
            self.attach(obj)

    def __getstate__(self):
        return

    def __setstate__(self,_state):
        return
    
    def execute(self, obj):
        a_shape = self.get_addition_shape(obj)
        f_shape = self.get_filling_shape(obj)
        v_shape = self.get_void_shape(obj)
       
        obj.Shape = f_shape


    def attach(self,obj):
        obj.addExtension('App::GeoFeatureGroupExtensionPython', None)
        self.set_properties(obj)

    def set_properties(self, obj):
        # obj.addProperty('App::PropertyPlacement', 'GlobalPlacement', 
        #                'Base', 
        #                'Object global Placement', 1)

        # Ifc Properties ----------------------------------------------------
        # IFCutils.set_ifc_properties(obj, "IfcProduct")
        obj.addProperty('App::PropertyString', 'IfcType', 'Ifc')
        obj.IfcType = "Opening Element"
        # IFCutils.setup_ifc_attributes(obj)
        # obj.PredefinedType = "OPENING"

        # COMPONENTS - ADDITIONS (not implemented yet) ----------------------------
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyEnumeration', 'Addition', 
                        'Component - Additions', _tip).Addition = ["Default Sill", "Custom"]

        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyLinkListGlobal', 'AdditionElements', 
                        'Component - Additions', _tip)
        obj.setPropertyStatus("AdditionElements", 2)

        # COMPONENTS - FILLING Properties (Windows, doors) ----------------------------
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyEnumeration', 'Filling', 
                        'Component - Filling', _tip).Filling = ["None", "Default Door", "Default Window", "By Sketch", "Custom"]

        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyEnumeration', 'FillingAlignment', 
                        'Component - Filling', _tip).FillingAlignment = ["Left", "Center", "Right", "Offset"]
        
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyDistance', 'FillingDisplacement', 
                        'Component - Filling', _tip).FillingDisplacement = 0.0

        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyLinkGlobal', 'FillingElement', 
                        'Component - Filling', _tip)

        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyEnumeration', 'FillingMode', 
                        'Component - Filling', _tip).FillingMode = ["Embed Shape", "Display Child"]

        # COMPONENTS Properties (not implemented yet) ----------------------------
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyEnumeration', 'Void', 
                        'Component - Void', _tip).Void = ["Rectangular", "Arc", "Custom"]

        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyLinkGlobal', 'VoidElement', 
                        'Component - Void', _tip)

        # Geometry Properties (not implemented yet) ----------------------------
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyLength', 'OpeningWidth', 
                        'Geometry', _tip).OpeningWidth = 800
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyLength', 'OpeningHeight', 
                        'Geometry', _tip).OpeningHeight = 1500
        _tip = 'Link the door or the window that you want to insert into the opening'
        obj.addProperty('App::PropertyLength', 'HostThickness', 
                        'Geometry', _tip).HostThickness = 500

    # ADDITIONS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def get_addition_shape(self, obj):
        pass

    # FILLING ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def get_filling_shape(self, obj):
        import Part

        f = None
        if 'Filling' in obj.PropertiesList and obj.Filling == "None":
            # return an empty shape
            f = Part.Shape()
        elif 'Filling' in obj.PropertiesList and obj.Filling == "Default Door":
            f = self.get_default_door_shape(obj)
        elif 'Filling' in obj.PropertiesList and obj.Filling == "Default Window":
            f = self.get_default_window_shape(obj)
        elif 'Filling' in obj.PropertiesList and obj.Filling == "By Sketch":
            f = self.get_filling_by_sketch(obj)
        elif 'Filling' in obj.PropertiesList and obj.Filling == "Custom":
            if 'FillingElement' in obj.PropertiesList and obj.FillingElement:
                # TODO: Inherit custom window shape
                f = obj.FillingElement.Shape
        if f: return f

    def get_default_door_shape(self, obj):
        import Part

        if (not 'OpeningWidth' in obj.PropertiesList or
            not 'OpeningHeight' in obj.PropertiesList):
            return None
        f = Part.makeBox(obj.OpeningWidth,60,obj.OpeningHeight)
        m = App.Matrix()
        m.move(-obj.OpeningWidth/2, 0, 0)
        f = f.transformGeometry(m)
        return f

    def get_default_window_shape(self, obj):
        import Part

        if (not 'OpeningWidth' in obj.PropertiesList or
            not 'OpeningHeight' in obj.PropertiesList):
            return None
        f = Part.makeBox(obj.OpeningWidth,60,obj.OpeningHeight)
        m = App.Matrix()
        m.move(-obj.OpeningWidth/2, 0, 0)
        f = f.transformGeometry(m)
        return f

    def get_filling_by_sketch(self, obj):
        #TODO: To be implemented
        pass

    # VOID ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def get_void_shape(self, obj):
        import Part

        void = None
        if obj.Void == "Rectangular":
            void = Part.makeBox(obj.OpeningWidth.Value, obj.HostThickness.Value + 50, obj.OpeningHeight.Value)
            void.Placement = obj.Placement
            void.Placement.Base.x -= obj.OpeningWidth.Value/2
            void.Placement.Base.y -= obj.HostThickness.Value/2
        return void



    def onChanged(self, obj, prop):
        if 'Addition' in obj.PropertiesList and prop == 'Addition':
            if obj.Addition != "Custom" and 'AdditionElements' in obj.PropertiesList:
                obj.setPropertyStatus("AdditionElements", 2)
            elif 'AdditionElements' in obj.PropertiesList:
                obj.setPropertyStatus("AdditionElements", -2)

        if 'AdditionElements' in obj.PropertiesList and prop == 'AdditionElements':
            pass

        if 'Filling' in obj.PropertiesList and prop == 'Filling':
            pass

        if 'FillingElement' in obj.PropertiesList and prop == 'FillingElement':
            pass

        if 'Void' in obj.PropertiesList and prop == 'Void':
            pass

        if 'VoidElement' in obj.PropertiesList and prop == 'VoidElement':
            pass


    def onDocumentRestored(self, obj):
        self.Object = obj