from enum import IntEnum
from componentOperate import ComponentOperateType


class OperateType(IntEnum):
    Create = 1
    Configure = 2
    PlaceConfigure = 3
    Delete = 4
    Rename = 5
    Title = 6
    ListboxInsert = 7
    ComboboxValues = 8


class OperateBase:

    def __init__(self, operate_type, component, component_operate_list=[]):
        self.operate_type = operate_type
        self.component = component
        self.component_operate_list = component_operate_list

    @property
    def component_id(self):
        return self.component.winfo_name()

    def get_component_operate_list(self):
        return self.component_operate_list

    def get_first_operate(self):
        if len(self.component_operate_list) == 0:
            return None
        return self.component_operate_list[0]

    def get_operate_type(self):
        return self.operate_type

    def get_place_operate(self):
        for operate in self.component_operate_list:
            if operate.get_operate_type() != ComponentOperateType.PlaceConfigure:
                continue
            return operate
        return None


class OperateCreate(OperateBase):

    def __init__(self, component, operate_mgr, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.Create, component, component_operate_list)
        self.operate_mgr = operate_mgr


class OperateConfigure(OperateBase):

    def __init__(self, component, old_operate, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.Configure, component, component_operate_list)
        self.old_operate = old_operate


class OperatePlaceConfigure(OperateBase):

    def __init__(self, component, old_operate, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.PlaceConfigure, component, component_operate_list)
        self.old_operate = old_operate


class OperateDelete(OperateBase):

    def __init__(self, component, old_place_operate, operate_mgr, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.Delete, component, component_operate_list)
        self.old_place_operate = old_place_operate
        self.operate_mgr = operate_mgr


class OperateRename(OperateBase):

    def __init__(self, component, old_name, new_name, operate_mgr, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.Rename, component, component_operate_list)
        self.old_name = old_name
        self.new_name = new_name
        self.operate_mgr = operate_mgr


class OperateTitle(OperateBase):

    def __init__(self, component, old_operate, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.Title, component, component_operate_list)
        self.old_operate = old_operate


class ListboxInsert(OperateBase):

    def __init__(self, component, old_operate, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.ListboxInsert, component, component_operate_list)
        self.old_operate = old_operate


class ComboboxValues(OperateBase):

    def __init__(self, component, old_operate, component_operate_list=[]):
        OperateBase.__init__(self, OperateType.ComboboxValues, component, component_operate_list)
        self.old_operate = old_operate


class OperateStack:

    def __init__(self):
        self.undo_list = []
        self.redo_list = []

    def append(self, operate):
        self.redo_list.clear()
        self.undo_list.append(operate)

    def undo(self):
        if len(self.undo_list) == 0:
            return None
        operate = self.undo_list.pop()
        self.redo_list.append(operate)
        return operate

    def redo(self):
        if len(self.redo_list) == 0:
            return None
        operate = self.redo_list.pop()
        self.undo_list.append(operate)
        return operate

