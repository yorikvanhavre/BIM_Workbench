import FreeCAD, FreeCADGui
from pivy import coin

class CyclicSelectionObserver:
    def __init__(self, preselectedObject):
        self.preselectedObject = preselectedObject

    def addSelection(self, document, object, element, position):
        if not hasattr(FreeCAD, "CyclicSelectionObserver"):
            return

        FreeCADGui.Selection.removeSelection(FreeCAD.ActiveDocument.getObject(object))
        FreeCADGui.Selection.removeObserver(FreeCAD.CyclicSelectionObserver)
        del FreeCAD.CyclicSelectionObserver
        FreeCADGui.Selection.addSelection(FreeCAD.ActiveDocument.getObject(self.preselectedObject))

class CyclicObjectSelector():
    def __init__(self):
        self.selectableObjects = []
        self.objectIndex = 0

    def selectObject(self, event_callback):
        event = event_callback.getEvent()

        if event.getState() != coin.SoMouseButtonEvent.DOWN or not self.selectableObjects:
            return

        pos = event.getPosition().getValue()
        element_list = FreeCADGui.ActiveDocument.ActiveView.getObjectsInfo((int(pos[0]), int(pos[1])))

        if not element_list:
            self.selectableObjects = []
            return

        FreeCAD.CyclicSelectionObserver = CyclicSelectionObserver(self.selectableObjects[self.objectIndex])
        FreeCADGui.Selection.addObserver(FreeCAD.CyclicSelectionObserver)
        view = FreeCADGui.ActiveDocument.ActiveView.getViewer()
        root = view.getSceneGraph()
        hm = root.highlightMode.getValue() # store the original highlightMode
        root.highlightMode.setValue(1) # switch highlightMode off
        self.root = root
        self.hm = hm

    def cycleSelectableObjects(self, event_callback):
        event = event_callback.getEvent()

        if not event.isKeyPressEvent(event, event.TAB):
            return

        pos = event.getPosition().getValue()
        element_list = FreeCADGui.ActiveDocument.ActiveView.getObjectsInfo((int(pos[0]), int(pos[1])))

        if not element_list:
            return

        selectableObjects = []
        for element in element_list:
            selectableObjects.append(element["Object"])
        selectableObjects = list(set(selectableObjects))

        if self.selectableObjects != selectableObjects:
            self.selectableObjects = selectableObjects
            self.objectIndex = 0
        elif self.objectIndex < len(self.selectableObjects) - 1:
            self.objectIndex += 1
        else:
            self.objectIndex = 0
        FreeCADGui.getMainWindow().showMessage('Cycle preselected (TAB): {}'.format(self.selectableObjects[self.objectIndex]), 5000)

class Setup():
    def slotActivateDocument(self, doc):
        print('add callback')
        cos = CyclicObjectSelector()
        self.callback = doc.ActiveView.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), cos.selectObject)
        self.callback = doc.ActiveView.addEventCallbackPivy(coin.SoKeyboardEvent.getClassTypeId(), cos.cycleSelectableObjects)
