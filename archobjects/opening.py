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

from archobjects.base import ShapeGroup
from ArchIFC import IfcProduct

import archobjects.window_presets as window_presets

class Opening(ShapeGroup, IfcProduct):
    def __init__(self, obj=None):
        super(Opening, self).__init__(obj)
        self.Object = obj
        if obj:
            self.attach(obj)


    def attach(self,obj):
        ShapeGroup.attach(self, obj)
        self.set_properties(obj)
   

    def execute(self, obj):
        import Part

        shapes_collection = []

        a_shape = self.get_addition_shape(obj)
        if a_shape:
            shapes_collection.append(a_shape)

        f_shape = self.get_filling_shape(obj)
        if f_shape:
            shapes_collection.append(f_shape)

        if len(shapes_collection) > 0:
            obj.Shape = Part.makeCompound(shapes_collection)
        else:
            obj.Shape = Part.Shape()


    def set_properties(self, obj):
        """ Setup object properties.
        """
        # Ifc Properties ----------------------------------------------------
        IfcProduct.setProperties(self, obj)
        obj.IfcType = "Opening Element"

        # COMPONENTS - ADDITIONS (not implemented yet) ----------------------------
        _tip = 'List of available shapes for the opening Additions.\n'\
               'Chose Custom to use the Addition Elements objects shape.'
        obj.addProperty('App::PropertyEnumeration', 'Addition', 
                        'Component - Additions', _tip).Addition = ["Default Sill", "Custom"]

        _tip = 'List of objects to be merged into the opening shape.'
        obj.addProperty('App::PropertyLinkListChild', 'AdditionElements', 
                        'Component - Additions', _tip)
        obj.setPropertyStatus("AdditionElements", 2)

        _tip = 'Chose if the Addition Elements have to be individually displayed or\n'\
               'merged into the Opening object shape.'
        obj.addProperty('App::PropertyEnumeration', 'AdditionMode', 
                        'Component - Additions', _tip).AdditionMode = ["Embed Shape", "Display Children"]

        # COMPONENTS - FILLING Properties (Windows, doors) ----------------------------
        _tip = 'List of available shapes for the Filling element.\n'\
               'Chose Custom to use the Filling Element object shape.'
        obj.addProperty('App::PropertyEnumeration', 'Filling', 
                        'Component - Filling', _tip).Filling = ["None", "Default Door", "Default Window", "By Sketch", "Custom"]

        _tip = 'Alignment of the Filling Element according to the Host Thickness property.'
        obj.addProperty('App::PropertyEnumeration', 'FillingAlignment', 
                        'Component - Filling', _tip).FillingAlignment = ["Left", "Center", "Right", "Offset"]
        
        _tip = 'Offset of the Filling Element from the chosen Filling Alignment.'
        obj.addProperty('App::PropertyDistance', 'FillingDisplacement', 
                        'Component - Filling', _tip).FillingDisplacement = 0.0

        _tip = 'Link the door or the window that you want to insert into the opening.'
        obj.addProperty('App::PropertyLinkGlobal', 'FillingElement', 
                        'Component - Filling', _tip)

        _tip = 'Chose if the Filling Element have to be individually displayed or\n'\
               'merged into the Opening object shape.'
        obj.addProperty('App::PropertyEnumeration', 'FillingMode', 
                        'Component - Filling', _tip).FillingMode = ["Embed Shape", "Display Child"]

        # COMPONENTS Properties (not implemented yet) ----------------------------
        _tip = 'List of available shapes of the Opening void.\n'\
               'Chose Custom to use the Void Element object shape.'
        obj.addProperty('App::PropertyEnumeration', 'Void', 
                        'Component - Void', _tip).Void = ["Rectangular", "Arc", "Custom"]

        _tip = 'Ponter to the object that will be used to cut the wall.\n'\
               'To use it, set Void property to Custom'
        obj.addProperty('App::PropertyLinkGlobal', 'VoidElement', 
                        'Component - Void', _tip)

        # Geometry Properties (not implemented yet) ----------------------------
        _tip = 'Architectural Width of the opening object'
        obj.addProperty('App::PropertyLength', 'OpeningWidth', 
                        'Geometry', _tip).OpeningWidth = 800
        _tip = 'Architectural Height of the opening object'
        obj.addProperty('App::PropertyLength', 'OpeningHeight', 
                        'Geometry', _tip).OpeningHeight = 1500
        _tip = 'Thickness of the hosted object.\n'\
               'This property is set by the hosting wall on creation'
        obj.addProperty('App::PropertyLength', 'HostThickness', 
                        'Geometry', _tip).HostThickness = 500
        _tip = 'Propagate geometry properties to opening childrens'
        obj.addProperty('App::PropertyBool', 'PropagateGeometry', 
                        'Geometry', _tip).PropagateGeometry = False


    def onChanged(self, obj, prop):
        """This method is activated when a property changes.
        """
        super(Opening, self).onChanged(obj, prop)

        if 'Addition' in obj.PropertiesList and prop == 'Addition':
            if obj.Addition != "Custom" and 'AdditionElements' in obj.PropertiesList:
                obj.setPropertyStatus("AdditionElements", 2)
            elif 'AdditionElements' in obj.PropertiesList:
                obj.setPropertyStatus("AdditionElements", -2)

        if 'AdditionElements' in obj.PropertiesList and prop == 'AdditionElements':
            pass

        if 'Filling' in obj.PropertiesList and prop == 'Filling':
            pass

        if 'Void' in obj.PropertiesList and prop == 'Void':
            pass

        if 'VoidElement' in obj.PropertiesList and prop == 'VoidElement':
            pass


    def onDocumentRestored(self, obj):
        self.Object = obj


    # ADDITIONS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def get_addition_shape(self, obj):
        return None


    # FILLING ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def get_filling_shape(self, obj):
        """Return a shape representing the filling of the Opening object, 
        being it for example a window, a door, a custom filling or just None.
        """
        import Part

        if 'Filling' in obj.PropertiesList and obj.Filling == "None":
            return None

        elif 'Filling' in obj.PropertiesList and obj.Filling == "Default Door":
            return self.get_default_door_shape(obj)
        elif 'Filling' in obj.PropertiesList and obj.Filling == "Default Window":
            return self.get_default_window_shape(obj)
        elif 'Filling' in obj.PropertiesList and obj.Filling == "By Sketch":
            return self.get_filling_by_sketch(obj)
        elif 'Filling' in obj.PropertiesList and obj.Filling == "Custom":
            if 'FillingElement' in obj.PropertiesList and obj.FillingElement:
                if 'Shape' in obj.FillingElement.PropertiesList and not obj.FillingElement.Shape.isNull():
                    if 'FillingMode' in obj.PropertiesList and obj.FillingMode == "Embed Shape":
                        # if FillingMode is "Embed Shape" look for a shape to return
                        return obj.FillingElement.Shape
                    elif 'FillingMode' in obj.PropertiesList and obj.FillingMode == "Display Child":
                        # if FillingMode is "Display Child" return None cause the children will be visible by itself
                        # BUG: This option does not work so good.
                        return None
        return None


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
        return window_presets.window_single_pane(obj.HostThickness.Value,
                                                 obj.OpeningHeight.Value,
                                                 obj.OpeningWidth.Value,
                                                 frame_width=50,
                                                 frame_th=50,
                                                 glass_th=21)
        '''f = Part.makeBox(obj.OpeningWidth,60,obj.OpeningHeight)
        m = App.Matrix()
        m.move(-obj.OpeningWidth/2, 0, 0)
        f = f.transformGeometry(m)
        return f'''


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
