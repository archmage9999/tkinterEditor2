import time
from define import *
from project import *
from operate import *
from componentOperate import *
from toolConfigParser import ToolConfigParser
from selectedComponent import SelectedComponent
from tkinter import messagebox


@single_instance
class DataMgr:

    def __init__(self):
        self.editor = None
        self.project_path = None
        self.config_parser = ToolConfigParser(file="default.ini")
        self.theme = EditorThemeType(int(self.config_parser.get("default", "theme")))
        self.gui_map = {}
        self.operate_stack_map = {}
        self.cur_selected = None
        self.old_generate_pos_time = 0
        self.old_generate_pos_x = 0
        self.old_generate_pos_y = 0

    def set_editor(self, editor):
        self.editor = editor

    def get_editor(self):
        return self.editor

    def get_theme(self):
        return self.theme

    def set_theme(self, theme):
        self.theme = EditorThemeType(theme)

    def has_project(self):
        return self.project_path is not None

    def get_project_path(self):
        return self.project_path

    def set_project_path(self, project_path):
        self.project_path = project_path

    def get_custom_frame_list(self):
        return [custom_frame for custom_frame in self.config_parser.options("custom_frame")]

    def get_gui(self, gui_path):
        return self.gui_map.get(gui_path, None)

    def add_gui(self, file):
        """
        添加gui
        :param file: File
        :return: None
        """
        if not self.has_project():
            return False

        if self.get_gui(file.file_path) is not None:
            return False

        with open(file.gui_py_path, "r", encoding="utf-8") as f:
            code_str = f.read()

        operate_mgr = GuiOperateMgr.create_mgr_by_code(code_str)
        if operate_mgr is None:
            return False

        gui = Gui(file.file_path, operate_mgr, code_str)
        self.gui_map[file.file_path] = gui

        return True

    def del_gui(self, file_path):
        gui = self.get_gui(file_path)
        if gui is None:
            return

        del self.gui_map[file_path]
        if gui.gui_path in self.operate_stack_map:
            self.operate_stack_map.pop(gui.gui_path)

    def generate_component_pos(self):
        """
        生成控件位置
        :return: int, int
        """
        now = time.time()
        if now - self.old_generate_pos_time > 2:
            self.old_generate_pos_time = now
            self.old_generate_pos_x = 0
            self.old_generate_pos_y = 0
        else:
            self.old_generate_pos_x += 6
            self.old_generate_pos_y += 6
        return self.old_generate_pos_x, self.old_generate_pos_y

    def get_cur_selected(self):
        return self.cur_selected

    def select_component(self, component, gui, force):
        """
        选中控件
        :param component: 控件
        :param gui: GUI
        :param force: 强制选中
        :return: None
        """
        if not force and self.cur_selected is not None and self.cur_selected.is_selected(component):
            return

        self.cur_selected = SelectedComponent(component, gui)
        self.editor.on_component_selected()

    def cancel_selected_component(self):
        self.cur_selected = None
        self.editor.on_cancel_component_selected()

    def add_operate(self, selected_component, operate, is_select=True):
        operate_stack = self.operate_stack_map.setdefault(selected_component.gui.gui_path, OperateStack())
        operate_stack.append(operate)

        frame = self.editor.frame_middle.get_tab_frame()
        for component_operate in operate.get_component_operate_list():
            selected_component.gui.operate_mgr.add_operate(selected_component.component_id, component_operate)
            frame.on_component_operate_added(selected_component.component, component_operate)

        if is_select:
            self.select_component(selected_component.component, selected_component.gui, True)

    def undo_operate(self, gui, frame):
        operate_stack = self.operate_stack_map.get(gui.gui_path, None)
        if operate_stack is None:
            return

        operate = operate_stack.undo()
        if operate is None:
            return

        operate_type = operate.get_operate_type()
        match operate_type:
            case OperateType.Create:
                operate.component.place_forget()
                gui.operate_mgr.del_component_operate_mgr(operate.component_id)
                self.select_component(gui.main_form, gui, True)
            case OperateType.Configure:
                gui.operate_mgr.add_operate(operate.component_id, operate.old_operate)
                frame.on_component_operate_added(operate.component, operate.old_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.PlaceConfigure:
                gui.operate_mgr.add_operate(operate.component_id, operate.old_operate)
                frame.on_component_operate_added(operate.component, operate.old_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.Delete:
                gui.operate_mgr.add_component_operate_mgr(operate.component_id, operate.operate_mgr)
                frame.on_component_operate_added(operate.component, operate.old_place_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.Rename:
                is_changed = operate.operate_mgr.change_component_name(operate.component_id, operate.old_name)
                if not is_changed:
                    messagebox.showinfo(title='提示', message='重命名失败,名字可能和其他的控件名字重复了')
                self.select_component(operate.component, gui, True)
            case OperateType.Title:
                gui.operate_mgr.add_operate(operate.component_id, operate.old_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.ListboxInsert | OperateType.ComboboxValues:
                gui.operate_mgr.add_operate(operate.component_id, operate.old_operate)
                frame.on_component_operate_added(operate.component, operate.old_operate)
                self.select_component(operate.component, gui, True)

    def redo_operate(self, gui, frame):
        operate_stack = self.operate_stack_map.get(gui.gui_path, None)
        if operate_stack is None:
            return

        operate = operate_stack.redo()
        if operate is None:
            return

        operate_type = operate.get_operate_type()
        match operate_type:
            case OperateType.Create:
                gui.operate_mgr.add_component_operate_mgr(operate.component_id, operate.operate_mgr)
                place_operate = operate.get_place_operate()
                if place_operate is None:
                    return
                frame.on_component_operate_added(operate.component, place_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.Configure:
                new_operate = operate.get_first_operate()
                gui.operate_mgr.add_operate(operate.component_id, new_operate)
                frame.on_component_operate_added(operate.component, new_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.PlaceConfigure:
                place_operate = operate.get_place_operate()
                gui.operate_mgr.add_operate(operate.component_id, place_operate)
                frame.on_component_operate_added(operate.component, place_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.Delete:
                operate.component.place_forget()
                gui.operate_mgr.del_component_operate_mgr(operate.component_id)
                self.select_component(gui.main_form, gui, True)
            case OperateType.Rename:
                is_changed = operate.operate_mgr.change_component_name(operate.component_id, operate.new_name)
                if not is_changed:
                    messagebox.showinfo(title='提示', message='重命名失败,名字可能和其他的控件名字重复了')
                self.select_component(operate.component, gui, True)
            case OperateType.Title:
                new_operate = operate.get_first_operate()
                gui.operate_mgr.add_operate(operate.component_id, new_operate)
                self.select_component(operate.component, gui, True)
            case OperateType.ListboxInsert | OperateType.ComboboxValues:
                new_operate = operate.get_first_operate()
                gui.operate_mgr.add_operate(operate.component_id, new_operate)
                frame.on_component_operate_added(operate.component, new_operate)
                self.select_component(operate.component, gui, True)

    def add_place_configure_operate(self, selected_component, old_place_operate, new_place_operate):
        operate_list = [new_place_operate]
        operate = OperatePlaceConfigure(selected_component.component, old_place_operate, operate_list)
        self.add_operate(selected_component, operate)

    def add_configure_operate(self, selected_component, old_configure_operate, new_configure_operate):
        operate_list = [new_configure_operate]
        operate = OperateConfigure(selected_component.component, old_configure_operate, operate_list)
        self.add_operate(selected_component, operate)

    def add_create_operate(self, selected_component, operate_mgr):
        operate_list = []
        x, y = self.generate_component_pos()
        match selected_component.component.__class__.__name__:
            case "Label":
                place_operate = ComponentOperatePlaceConfigure(x, y, 200, 30, False)
                set_text_operate = ComponentOperateConfigure("text", change_prop_to_str(selected_component.component_name))
                operate_list.extend([place_operate, set_text_operate])
            case "Button":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                set_text_operate = ComponentOperateConfigure("text", change_prop_to_str(selected_component.component_name))
                operate_list.extend([place_operate, set_text_operate])
            case "Entry":
                place_operate = ComponentOperatePlaceConfigure(x, y, 200, 30, False)
                operate_list.extend([place_operate, ])
            case "Frame":
                place_operate = ComponentOperatePlaceConfigure(x, y, 400, 400, False)
                operate_list.extend([place_operate, ])
            case "Canvas":
                place_operate = ComponentOperatePlaceConfigure(x, y, 300, 300, False)
                operate_list.extend([place_operate, ])
            case "Checkbutton":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                set_text_operate = ComponentOperateConfigure("text", change_prop_to_str(selected_component.component_name))
                operate_list.extend([place_operate, set_text_operate])
            case "Listbox":
                place_operate = ComponentOperatePlaceConfigure(x, y, 300, 300, False)
                operate_list.extend([place_operate, ])
            case "Text":
                place_operate = ComponentOperatePlaceConfigure(x, y, 300, 300, False)
                operate_list.extend([place_operate, ])
            case "Radiobutton":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                set_text_operate = ComponentOperateConfigure("text", change_prop_to_str(selected_component.component_name))
                operate_list.extend([place_operate, set_text_operate])
            case "Scale":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                operate_list.extend([place_operate, ])
            case "Scrollbar":
                place_operate = ComponentOperatePlaceConfigure(x, y, None, None, False)
                operate_list.extend([place_operate, ])
            case "Spinbox":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                operate_list.extend([place_operate, ])
            case "LabelFrame":
                place_operate = ComponentOperatePlaceConfigure(x, y, 400, 400, False)
                operate_list.extend([place_operate, ])
            case "Combobox":
                place_operate = ComponentOperatePlaceConfigure(x, y, 200, 30, False)
                operate_list.extend([place_operate, ])
            case "Treeview":
                place_operate = ComponentOperatePlaceConfigure(x, y, 300, 300, False)
                operate_list.extend([place_operate, ])
            case "Progressbar":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                operate_list.extend([place_operate, ])
            case "Separator":
                place_operate = ComponentOperatePlaceConfigure(x, y, 100, 30, False)
                operate_list.extend([place_operate, ])

        operate = OperateCreate(selected_component.component, operate_mgr, operate_list)
        self.add_operate(selected_component, operate, False)

    def add_delete_operate(self, selected_component):
        operate_mgr = selected_component.gui.operate_mgr.del_component_operate_mgr(selected_component.component_id)
        if operate_mgr is None:
            return

        old_operate = ComponentOperatePlaceConfigure(
            selected_component.component.winfo_x(), selected_component.component.winfo_y(),
            selected_component.component.winfo_width(), selected_component.component.winfo_height(), False
        )
        operate = OperateDelete(selected_component.component, old_operate, operate_mgr)
        self.add_operate(selected_component, operate, False)

        selected_component.component.place_forget()
        self.select_component(selected_component.gui.main_form, selected_component.gui, True)

    def add_rename_operate(self, selected_component, new_name):
        old_name = selected_component.component_name
        if old_name == new_name:
            return
        is_changed = selected_component.gui.operate_mgr.change_component_name(selected_component.component_id, new_name)
        if not is_changed:
            messagebox.showinfo(title='提示', message='重命名失败,名字可能和其他的控件名字重复了')
            self.select_component(selected_component.component, selected_component.gui, True)
            return
        operate = OperateRename(selected_component.component, old_name, new_name, selected_component.gui.operate_mgr)
        self.add_operate(selected_component, operate)

    def add_title_operate(self, selected_component, old_operate, new_operate):
        operate_list = [new_operate]
        operate = OperateTitle(selected_component.component, old_operate, operate_list)
        self.add_operate(selected_component, operate)

    def add_listbox_insert_operate(self, selected_component, old_operate, new_operate):
        operate_list = [new_operate]
        operate = ListboxInsert(selected_component.component, old_operate, operate_list)
        self.add_operate(selected_component, operate)

    def add_combobox_values_operate(self, selected_component, old_operate, new_operate):
        operate_list = [new_operate]
        operate = ComboboxValues(selected_component.component, old_operate, operate_list)
        self.add_operate(selected_component, operate)
