import uuid
from define import *

create_no = 0


class ComponentOperateType(IntEnum):
    Unknown = 0
    Configure = 1
    PlaceConfigure = 2
    Title = 3
    Resizable = 4
    ListBoxInsert = 5
    ComboboxValues = 6


class ComponentOperateBase:

    def __init__(self, operate_type):
        self.operate_type = operate_type

    def is_same_operate(self, component_operate):
        return self.operate_type == component_operate.operate_type

    def modify_operate(self, component_operate):
        pass

    def generate_operate_str(self, component_define):
        return ""

    def get_operate_type(self):
        return self.operate_type

    def get_cnf_dict(self):
        return {}

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        return None


class ComponentOperateUnknown(ComponentOperateBase):

    def __init__(self, value):
        ComponentOperateBase.__init__(self, ComponentOperateType.Unknown)
        self.value = value

    def is_same_operate(self, component_operate):
        return False

    def generate_operate_str(self, component_define):
        return f"{self.value}".lstrip(" ")

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        return ComponentOperateUnknown(code_str)


class ComponentOperateConfigure(ComponentOperateBase):

    def __init__(self, prop_name, prop_value):
        ComponentOperateBase.__init__(self, ComponentOperateType.Configure)
        self.prop_name = prop_name
        self.prop_value = prop_value

    def is_same_operate(self, component_operate):
        if not ComponentOperateBase.is_same_operate(self, component_operate):
            return False
        return self.prop_name == component_operate.prop_name

    def modify_operate(self, component_operate):
        self.prop_value = component_operate.prop_value

    def generate_operate_str(self, component_define):
        return f"{component_define}.configure({self.prop_name}={self.prop_value})"

    def get_cnf_dict(self):
        if self.prop_value.startswith("["):
            prop_value = []
            for value in self.prop_value[1:-1].split(','):
                prop_value.append(value.lstrip(' ')[1:-1])
            return {self.prop_name: prop_value}
        elif self.prop_value.startswith("'"):
            return {self.prop_name: self.prop_value[1:-1]}
        elif self.prop_value == "True":
            return {self.prop_name: True}
        elif self.prop_value == "False":
            return {self.prop_name: False}
        return {self.prop_name: self.prop_value}

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        matched_operate = re.search(fr"self\.({component_name}\.)?configure\((.*)=(.*)\)", code_str)
        if not matched_operate:
            return None

        prop_value = matched_operate.group(3)
        if matched_operate.group(2) == "values":
            return None
        if matched_operate.group(2) in ("command", "xscrollcommand", "yscrollcommand"):
            return ComponentOperateUnknown(code_str)

        return ComponentOperateConfigure(matched_operate.group(2), prop_value)


class ComponentOperatePlaceConfigure(ComponentOperateBase):

    def __init__(self, x, y, width, height, is_geometry):
        ComponentOperateBase.__init__(self, ComponentOperateType.PlaceConfigure)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_geometry = is_geometry

    def modify_operate(self, component_operate):
        if component_operate.x is not None:
            self.x = component_operate.x

        if component_operate.y is not None:
            self.y = component_operate.y

        if component_operate.width is not None:
            self.width = component_operate.width

        if component_operate.height is not None:
            self.height = component_operate.height

    def generate_operate_str(self, component_define):
        if self.is_geometry:
            return f"{component_define}.geometry('{self.width}x{self.height}+{self.x}+{self.y}')"
        return f"{component_define}.place_configure({{'x': {self.x}, 'y': {self.y}, 'width': {self.width}, 'height': {self.height}}})"

    def get_cnf_dict(self):
        cnf = {}
        if self.x is not None:
            cnf['x'] = self.x

        if self.y is not None:
            cnf['y'] = self.y

        if self.width is not None:
            cnf['width'] = self.width

        if self.height is not None:
            cnf['height'] = self.height

        return cnf

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        matched_operate = re.search(fr"self\.({component_name}\.)?place_configure\({{'x': (.*), 'y': (.*), 'width': (.*), 'height': (.*)}}\)", code_str)
        if not matched_operate:
            matched_operate = re.search(fr"self\.geometry\('(\d*)x(\d*)\+(\d*)\+(\d*)'\)", code_str)
            if not matched_operate:
                return None
            return ComponentOperatePlaceConfigure(matched_operate.group(3), matched_operate.group(4), matched_operate.group(1), matched_operate.group(2), True)
        return ComponentOperatePlaceConfigure(matched_operate.group(2), matched_operate.group(3), matched_operate.group(4), matched_operate.group(5), False)


class ComponentOperateTitle(ComponentOperateBase):

    def __init__(self, title):
        ComponentOperateBase.__init__(self, ComponentOperateType.Title)
        self.title = title

    def get_title(self):
        return self.title[1:-1]

    def modify_operate(self, component_operate):
        self.title = component_operate.title

    def generate_operate_str(self, component_define):
        return f"{component_define}.title({self.title})"

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        matched_operate = re.search(fr"self\.({component_name}\.)?title\((.*)\)", code_str)
        if not matched_operate:
            return None
        return ComponentOperateTitle(matched_operate.group(2))


class ComponentOperateListboxInsert(ComponentOperateBase):

    def __init__(self, items: []):
        ComponentOperateBase.__init__(self, ComponentOperateType.ListBoxInsert)
        self.items = items

    def modify_operate(self, component_operate):
        self.items = component_operate.items

    def generate_operate_str(self, component_define):
        if len(self.items) == 0:
            return ""

        items_str = ""
        for index, item in enumerate(self.items):
            str_tab = ""
            if index != 0:
                str_tab += "        "
            items_str += f"{str_tab}{component_define}.insert('end', '{item}')\n"

        return items_str.rstrip("\n")

    def get_cnf_dict(self):
        return self.items

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        if component_class != "Listbox":
            return None
        matched_operate = re.search(fr"self\.{component_name}\.insert\('end', '(.*)'\)", code_str)
        if not matched_operate:
            return None
        return ComponentOperateListboxInsert([matched_operate.group(1)])


class ComponentOperateComboboxValues(ComponentOperateBase):

    def __init__(self, items: []):
        ComponentOperateBase.__init__(self, ComponentOperateType.ComboboxValues)
        self.items = items

    def modify_operate(self, component_operate):
        self.items = component_operate.items

    def generate_operate_str(self, component_define):
        if len(self.items) == 0:
            return ""

        values_str = ""
        for item in self.items:
            values_str += f"'{item}', "

        return f"{component_define}.configure(values=[{values_str}])"

    def get_cnf_dict(self):
        return self.items

    @classmethod
    def create_by_code(cls, component_class, component_name, code_str):
        if component_class != "Combobox":
            return None

        matched_operate = re.search(fr"self\.({component_name}\.)?configure\((.*)=(.*)\)", code_str)
        if not matched_operate:
            return None

        prop_value = matched_operate.group(3)
        if matched_operate.group(2) != "values":
            return None

        if not prop_value.startswith("["):
            return None

        items = []
        for value in prop_value[1:-1].split(','):
            value_str = value.lstrip(' ')[1:-1]
            if value_str == "":
                continue
            items.append(value_str)

        return ComponentOperateComboboxValues(items)


def get_some_component_operate_class():
    return [
        ComponentOperateConfigure, ComponentOperatePlaceConfigure, ComponentOperateTitle,
        ComponentOperateListboxInsert, ComponentOperateComboboxValues, ComponentOperateUnknown,
    ]


class ComponentOperateMgr:

    def __init__(self, component_id, component_name, component_define, component_class, component_module):
        self.component_id = component_id
        self.component_name = component_name
        self.component_define = component_define
        self.component_class = component_class
        self.component_module = component_module
        global create_no
        self.create_time = create_no
        create_no += 1
        self.operate_list = []

    @property
    def import_str(self):
        return f"from {self.component_module} import {self.component_class}"

    def add_operate(self, component_operate):
        """
        添加操作
        :param component_operate: ComponentOperateBase
        :return: None
        """
        for operate in self.operate_list:
            if not operate.is_same_operate(component_operate):
                continue
            operate.modify_operate(component_operate)
            return
        self.operate_list.append(component_operate)

    def get_init_component_str(self):
        if len(self.operate_list) == 0:
            return ""
        init_component_str = f"        # {self.component_name} start\n"
        for operate in self.operate_list:
            operate_str = operate.generate_operate_str(self.component_define)
            if operate_str == "":
                continue
            init_component_str += f"        {operate_str}\n"
        init_component_str += f"        # {self.component_name} end\n"
        return init_component_str

    def change_component_name(self, new_component_name):
        self.component_name = new_component_name
        if self.component_define != "self":
            self.component_define = f"self.{self.component_name}"
        return True


class GuiOperateMgr:

    def __init__(self):
        self.component_operate_mgr_map = {}

    def is_main_form(self, component_id):
        if component_id not in self.component_operate_mgr_map:
            return False
        return self.component_operate_mgr_map[component_id].component_define == "self"

    def get_main_form_mgr(self):
        for component_id, value in self.component_operate_mgr_map.items():
            if value.component_define == "self":
                return value
        return None

    def create_component_operate_mgr(self, component_name, component_class, component_module, component_define=""):
        component_id = uuid.uuid1().hex
        if component_define == "":
            component_define = f"self.{component_name}"
        return self.component_operate_mgr_map.setdefault(component_id, ComponentOperateMgr(component_id, component_name, component_define, component_class, component_module))

    def del_component_operate_mgr(self, component_id):
        if component_id not in self.component_operate_mgr_map:
            return None
        return self.component_operate_mgr_map.pop(component_id)

    def add_component_operate_mgr(self, component_id, operate_mgr):
        self.component_operate_mgr_map[component_id] = operate_mgr

    def add_operate(self, component_id, operate):
        if (mgr := self.component_operate_mgr_map.get(component_id, None)) is not None:
            mgr.add_operate(operate)

    def change_component_name(self, component_id, new_component_name):
        if self.get_component_id(new_component_name) != "":
            return False

        if (mgr := self.component_operate_mgr_map.get(component_id, None)) is not None:
            return mgr.change_component_name(new_component_name)

        return False

    def get_component_name(self, component_id):
        if (mgr := self.component_operate_mgr_map.get(component_id, None)) is not None:
            return mgr.component_name
        return ""

    def get_component_id(self, component_name):
        for component_id, value in self.component_operate_mgr_map.items():
            if value.component_name == component_name:
                return component_id
        return ""

    def get_operate_title(self, component_id):
        mgr = self.component_operate_mgr_map.get(component_id, None)
        if mgr is None:
            return ""

        for operate in mgr.operate_list:
            if operate.get_operate_type() != ComponentOperateType.Title:
                continue
            return operate.get_title()

        return ""

    def get_operate_values(self, component_id):
        mgr = self.component_operate_mgr_map.get(component_id, None)
        if mgr is None:
            return []

        for operate in mgr.operate_list:
            if operate.get_operate_type() not in (ComponentOperateType.ListBoxInsert, ComponentOperateType.ComboboxValues):
                continue
            return operate.get_cnf_dict()

        return []

    @classmethod
    def create_mgr_by_code(cls, code):
        """
        根据代码生成mgr
        :param code: 代码
        :return: GuiOperateMgr
        """
        class_matched = class_pattern.search(code)
        if not class_matched:
            return None

        init_component_matched = init_component_pattern.search(code)
        if not init_component_matched:
            return None

        create_component_matched = create_component_pattern.search(code)
        if not create_component_matched:
            return None

        form_module = class_matched.group(2)
        form_name = class_matched.group(4)
        form_name = form_name[0].lower() + form_name[1:]
        form_class_name = class_matched.group(3)

        mgr = GuiOperateMgr()
        mgr.create_component_operate_mgr(form_name, form_class_name, form_module, "self")

        for create_info_str in create_component_matched.group(0).split("\n"):
            create_matched = re.search(r"self\.(.*) = (.*)\(self, name='.*'\)\s{2}# from (.*) import \2", create_info_str)
            if create_matched is None:
                continue
            component_name = create_matched.group(1)
            class_name = create_matched.group(2)
            module = create_matched.group(3)
            mgr.create_component_operate_mgr(component_name, class_name, module)

        matched_init_list = re.finditer(r"# (.*) start(.*)# \1 end", init_component_matched.group(0), re.M | re.S)
        for matched_init in matched_init_list:
            for operate_str in matched_init.group(0).split("\n")[1:-1]:
                mgr.add_operate_by_code(matched_init.group(1), operate_str)

        return mgr

    def add_operate_by_code(self, component_name, code_str):
        for operate_class in get_some_component_operate_class():
            component_id = self.get_component_id(component_name)
            if component_id == "":
                continue
            mgr = self.component_operate_mgr_map.get(component_id, None)
            if mgr is None:
                continue
            operate = operate_class.create_by_code(mgr.component_class, component_name, code_str)
            if operate is None:
                continue
            if operate_class == ComponentOperateListboxInsert:
                old_items = self.get_operate_values(component_id)
                for item in operate.items:
                    old_items.append(item)
                operate.items = old_items
            self.add_operate(component_id, operate)
            break

    def replace_form_str(self, form_str):
        """
        替换窗口字符串
        :param form_str: 被替换的窗口字符串
        :return: 替换后的窗口字符串
        """
        import_str, create_str, init_str = "", "", ""
        init_str = """    def init_component(self):
        \"\"\"
        初始化控件
        :return: None
        \"\"\"\n"""
        for component_id, mgr in sorted(self.component_operate_mgr_map.items(), key=lambda mgr_info: mgr_info[1].create_time):
            if import_str.find(mgr.import_str) == -1:
                import_str += mgr.import_str + "\n"
            if not self.is_main_form(component_id):
                create_str += f"        {mgr.component_define} = {mgr.component_class}(self, name='{mgr.component_name}')  # {mgr.import_str}\n"
            init_str += mgr.get_init_component_str()

        sub_str = import_pattern.sub(import_str, form_str)
        sub_str = create_component_pattern.sub(create_str, sub_str)
        sub_str = init_component_pattern.sub(init_str, sub_str)

        return sub_str


if __name__ == "__main__":

    test_file_str = """from functools import partial

# import start
# import end


# class start from tkinter import Tk
class Form1(Tk):

    def __init__(self, screen_name=None, base_name=None, class_name='Tk', use_tk=True, sync=False, use=None):
        Tk.__init__(self, screen_name, base_name, class_name, use_tk, sync, use)
        # create component start
        # create component end

    # init_component start
    def init_component(self):
        \"\"\"
        初始化控件
        :return: None
        \"\"\"
        # init_component end    
        
# class end
"""

    gui_mgr = GuiOperateMgr()
    component_operate_mgr = gui_mgr.create_component_operate_mgr("form1", "Tk", "tkinter", "self")
    gui_mgr.add_operate(component_operate_mgr.component_id, ComponentOperatePlaceConfigure(0, 0, 600, 600, True))
    gui_mgr.add_operate(component_operate_mgr.component_id, ComponentOperateTitle("test"))
    component_operate_mgr1 = gui_mgr.create_component_operate_mgr('frame1', "Frame", "tkinter")
    gui_mgr.add_operate(component_operate_mgr1.component_id, ComponentOperatePlaceConfigure(0, 0, 500, 500, False))
    gui_mgr.add_operate(component_operate_mgr1.component_id, ComponentOperatePlaceConfigure(None, None, 450, 500, False))
    gui_mgr.add_operate(component_operate_mgr1.component_id, ComponentOperateConfigure("bg", "red"))
    component_operate_mgr2 = gui_mgr.create_component_operate_mgr('button1', "Button", "tkinter")
    gui_mgr.add_operate(component_operate_mgr2.component_id, ComponentOperatePlaceConfigure(100, 100, 100, 30, False))
    gui_mgr.add_operate(component_operate_mgr2.component_id, ComponentOperateConfigure("text", "button1"))
    gui_mgr.add_operate(component_operate_mgr2.component_id, ComponentOperateConfigure("text", "button2"))
    component_operate_mgr3 = gui_mgr.create_component_operate_mgr("form2", "Frame", "tkinter")
    gui_mgr.change_component_name(component_operate_mgr2.component_id, "button11")
    gui_mgr.change_component_name(component_operate_mgr.component_id, "form3")
    component_operate_mgr4 = gui_mgr.create_component_operate_mgr("listbox1", "Listbox", "tkinter")
    gui_mgr.add_operate(component_operate_mgr4.component_id, ComponentOperatePlaceConfigure(100, 100, 100, 30, False))
    gui_mgr.add_operate(component_operate_mgr4.component_id, ComponentOperateListboxInsert(['test1']))
    gui_mgr.add_operate(component_operate_mgr4.component_id, ComponentOperateListboxInsert(['test2']))
    gui_str = gui_mgr.replace_form_str(test_file_str)
    print(gui_str)
