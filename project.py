import os
import re


class Gui:

    def __init__(self, gui_path, operate_mgr, ori_code):
        self.gui_path = gui_path
        self.operate_mgr = operate_mgr
        self.ori_code = ori_code
        self.main_form = None
        self.component_dict = {}
        self.component_name_dict = {}

    @property
    def gui_name(self):
        return os.path.basename(self.gui_path)

    def set_main_form(self, main_form):
        self.main_form = main_form

    def is_main_form(self, component):
        return self.main_form is component

    def add_component(self, component_id, component):
        self.component_dict[component_id] = component

    def get_component(self, component_id):
        return self.component_dict.get(component_id, None)

    @staticmethod
    def get_lower_component_class(component_class: str):
        return component_class[0].lower() + component_class[1:]

    def generate_component_name(self, component_class):
        """
        生成控件名字
        :param component_class: 控件类名
        :return: int
        """
        lower_component_class = self.get_lower_component_class(component_class)
        self.component_name_dict.setdefault(lower_component_class, 0)
        self.component_name_dict[lower_component_class] += 1
        return f"{lower_component_class}{self.component_name_dict[lower_component_class]}"

    def calc_component_name(self, component_class_name, component_name):
        """
        计算控件名字
        :param component_class_name: 控件类名
        :param component_name: 控件名字
        :return: None
        """
        lower_component_class = self.get_lower_component_class(component_class_name)
        now_num = self.component_name_dict.setdefault(lower_component_class, 0)
        matched = re.search(rf"{lower_component_class}(\d+)", component_name)
        if not matched:
            return

        if (num := int(matched.group(1))) and num <= now_num:
            return

        self.component_name_dict[lower_component_class] = num


class File:

    def __init__(self, project_path, file_path, file_name):
        self.project_path = project_path
        self.file_path = file_path
        self.file_name = file_name

    @property
    def is_gui(self):
        return self.file_name.endswith(".gui")

    @property
    def is_dir(self):
        return os.path.isdir(self.file_path)

    @property
    def gui_py_path(self):
        return self.file_path[:-4]

    @property
    def gui_py_name(self):
        return self.file_name[:-4]
