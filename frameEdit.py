import os
import importlib
from tkinter import Frame
from scrollCanvas import ScrollCanvas
from componentOperate import *
from dataMgr import DataMgr
from functools import partial


class FrameEdit(ScrollCanvas):

    def __init__(self, master=None, cnf={}, **kw):
        ScrollCanvas.__init__(self, master, cnf, **kw)
        self.is_sizing = False
        self.is_dragging = False
        self.start_x = 0
        self.start_y = 0
        self.start_width = 0
        self.start_height = 0
        self.start_event_x = 0
        self.start_event_y = 0
        self.changed = False
        self.select_frame_map = {}
        self.create_select_frame()

    def tkraise(self, *args):
        self.tk.call('raise', self._w, None)

    @staticmethod
    def get_class_module(name_module, class_name):
        if name_module.find('tkinter') != -1:
            module = importlib.import_module(name_module)
        else:
            project_name = os.path.basename(DataMgr().get_project_path())
            module = importlib.import_module(f'.{name_module}', project_name)
        return getattr(module, class_name, None)

    def refresh_gui(self, file):
        """
        刷新gui
        :param file: 文件
        :return: None
        """
        gui = DataMgr().get_gui(file.file_path)
        if gui is None:
            return

        main_form_mgr = gui.operate_mgr.get_main_form_mgr()
        if main_form_mgr is None:
            return

        main_form = self.create_component(gui, "tkinter", "Frame", self, main_form_mgr.component_id)
        if main_form is None:
            return

        for operate in main_form_mgr.operate_list:
            self.on_component_operate_added(main_form, operate)

        gui.set_main_form(main_form)
        for component_id, mgr in sorted(gui.operate_mgr.component_operate_mgr_map.items(), key=lambda mgr_info: mgr_info[1].create_time):
            if gui.operate_mgr.is_main_form(component_id):
                continue
            component = self.create_component(gui, mgr.component_module, mgr.component_class, main_form, mgr.component_id)
            if component is None:
                return
            gui.calc_component_name(mgr.component_class, mgr.component_name)
            for operate in mgr.operate_list:
                self.on_component_operate_added(component, operate)

    def create_component(self, gui, from_module, class_name, master, component_id):
        """
        创建控件
        :param gui: GUI
        :param from_module:
        :param class_name:
        :param master: master
        :param component_id: 控件名字
        :return: 控件
        """
        class_module = self.get_class_module(from_module, class_name)
        if class_module is None:
            print(f"{from_module}.{class_name} is None")
            return None

        if master.__class__.__name__ == "FrameEdit":
            component = master.create_child(class_module, name=component_id)
        else:
            component = class_module(master, name=component_id)

        gui.add_component(component_id, component)

        component.bind("<Button-1>", partial(self.handle_component_button_1, component_id, gui))
        component.bind("<B1-Motion>", partial(self.handle_component_button_motion_1, component_id))
        component.bind("<ButtonRelease-1>", partial(self.handle_component_button_release_1, component_id))

        return component

    @try_pass
    def on_component_operate_added(self, component, component_operate):
        """
        控件操作被添加时
        :param component: 控件
        :param component_operate: 操作
        :return: None
        """
        match component_operate.get_operate_type():
            case ComponentOperateType.Configure:
                cnf = component_operate.get_cnf_dict()
                component.configure(cnf)
            case ComponentOperateType.PlaceConfigure:
                cnf = component_operate.get_cnf_dict()
                component.place_configure(cnf)
                component.update()
                self.update_scroll()
            case ComponentOperateType.ListBoxInsert:
                cnf = component_operate.get_cnf_dict()
                component.delete(0, 'end')
                for item in cnf:
                    component.insert('end', item)
            case ComponentOperateType.ComboboxValues:
                cnf = component_operate.get_cnf_dict()
                component.configure(values=cnf)

    def handle_component_button_1(self, component_id, gui, event):
        """
        mouse button_1 event
        :param component_id: 控件id
        :param event: event
        :param gui: GUI
        :return: None
        """
        self.changed = False
        self.start_x, self.start_y = self.calc_pos(event.widget)
        self.start_width = event.widget.winfo_width()
        self.start_height = event.widget.winfo_height()
        self.start_event_x = event.x_root
        self.start_event_y = event.y_root
        self.is_dragging = True
        DataMgr().select_component(event.widget, gui, False)

    def handle_component_button_motion_1(self, component_id, event):
        """
        mouse motion event
        :param component_id: 控件id
        :param event:事件
        :return:None
        """
        if not self.is_dragging:
            return

        cur_selected = DataMgr().get_cur_selected()
        if not cur_selected.is_selected(event.widget):
            return

        self.changed = True
        width = self.start_width
        height = self.start_height

        x = self.start_x - (self.start_event_x - event.x_root)
        y = self.start_y - (self.start_event_y - event.y_root)

        self.place_configure_select_frame(x, y, width, height)

    def handle_component_button_release_1(self, component_id, event):
        """
        mouse button_1_release event
        :param component_id: 控件id
        :param event:事件
        :return:None
        """
        if not self.is_dragging:
            return

        cur_selected = DataMgr().get_cur_selected()
        if not cur_selected.is_selected(event.widget):
            return

        self.is_dragging = False
        self.refresh_component_place_info()

    def on_component_selected(self):
        """
        控件被选中
        :return: None
        """
        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None:
            return
        self.show_select_frame(cur_selected.component)

    def create_select_frame(self):
        """
        创建选中框
        :return: None
        """
        for name in ('left', 'right', 'up', 'down'):
            self.select_frame_map[name] = Frame(self, name=name, bg="red")

        for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se'):
            self.select_frame_map[name] = frame = Frame(self, name=name, bg="red")
            frame.bind('<Enter>', partial(self.handle_select_frame_enter, name))
            frame.bind('<Leave>', partial(self.handle_select_frame_leave, name))
            frame.bind('<Button-1>', partial(self.handle_select_frame_button_1, name))
            frame.bind('<B1-Motion>', partial(self.handle_select_frame_button_motion_1, name))
            frame.bind('<ButtonRelease-1>', partial(self.handle_select_frame_button_release_1, name))

    def calc_pos(self, component):
        pos_x = component.winfo_x()
        pos_y = component.winfo_y()
        master = component.master
        while master is not self:
            pos_x += master.winfo_x()
            pos_y += master.winfo_y()
            master = master.master
        return pos_x, pos_y

    def show_select_frame(self, component):
        """
        显示
        :param component: 选中的控件
        :return: None
        """
        width = component.winfo_width()
        height = component.winfo_height()
        x, y = self.calc_pos(component)
        if width == 0 or height == 0:
            return
        self.place_configure_select_frame(x, y, width, height)

    def place_configure_select_frame(self, x, y, width, height):
        self.select_frame_map["left"].place_configure({"x": x - 5, "y": y - 5, "width": 2, "height": height + 8})
        self.select_frame_map["right"].place_configure({"x": x + width + 4, "y": y - 5, "width": 2, "height": height + 8})
        self.select_frame_map["up"].place_configure({"x": x - 1, "y": y - 5, "width": width + 8, "height": 2})
        self.select_frame_map["down"].place_configure({"x": x - 1, "y": y + height + 4, "width": width + 8, "height": 2})
        self.select_frame_map["nw"].place_configure({"x": x - 8, "y": y - 8, "width": 7, "height": 7})
        self.select_frame_map["sw"].place_configure({"x": x - 8, "y": y + height + 1, "width": 7, "height": 7})
        self.select_frame_map["ne"].place_configure({"x": x + width + 1, "y": y - 8, "width": 7, "height": 7})
        self.select_frame_map["se"].place_configure({"x": x + width + 1, "y": y + height + 1, "width": 7, "height": 7})
        self.select_frame_map["n"].place_configure({"x": x + (width - 7) / 2, "y": y - 8, "width": 7, "height": 7})
        self.select_frame_map["s"].place_configure({"x": x + (width - 7) / 2, "y": y + height + 1, "width": 7, "height": 7})
        self.select_frame_map["w"].place_configure({"x": x - 8, "y": y + (height - 7) / 2, "width": 7, "height": 7})
        self.select_frame_map["e"].place_configure({"x": x + width + 1, "y": y + (height - 7) / 2, "width": 7, "height": 7})

    def hide_select_frame(self):
        """
        隐藏
        :return: None
        """
        for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se', 'left', 'right', 'up', 'down'):
            self.select_frame_map[name].place_forget()

    def handle_select_frame_enter(self, frame_name, event):
        """
        鼠标进入select_frame事件
        :param frame_name: frame名字
        :param event: event
        :return: None
        """
        match frame_name:
            case "nw" | "sw" | "ne" | "se":
                self["cursor"] = "sizing"
            case "w" | "e":
                self["cursor"] = "sb_h_double_arrow"
            case _:
                self["cursor"] = "sb_v_double_arrow"

    def handle_select_frame_leave(self, frame_name, event):
        """
        鼠标离开select_frame事件
        :param frame_name: frame名字
        :param event: event
        :return: None
        """
        if self.is_sizing:
            return
        self["cursor"] = "arrow"

    def handle_select_frame_button_1(self, frame_name, event):
        """
        鼠标点击select_frame事件
        :param frame_name: frame名字
        :param event: event
        :return: None
        """
        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None:
            return

        self.changed = False
        self.is_sizing = True
        self.start_x, self.start_y = self.calc_pos(cur_selected.component)
        self.start_width = cur_selected.component.winfo_width()
        self.start_height = cur_selected.component.winfo_height()
        self.start_event_x = event.x_root
        self.start_event_y = event.y_root

    def handle_select_frame_button_motion_1(self, frame_name, event):
        """
        鼠标移动select_frame事件
        :param frame_name: frame名字
        :param event: event
        :return: None
        """
        if not self.is_sizing:
            return

        self.changed = True
        x = self.start_x
        y = self.start_y
        width = self.start_width
        height = self.start_height

        if 'e' in frame_name:
            width = event.x_root - self.start_event_x + self.start_width
            width = max(20, width)

        if 'w' in frame_name:
            x = self.start_x - (self.start_event_x - event.x_root)
            width = self.start_event_x - event.x_root + self.start_width
            width = max(20, width)

        if 's' in frame_name:
            height = event.y_root - self.start_event_y + self.start_height
            height = max(20, height)

        if 'n' in frame_name:
            y = self.start_y - (self.start_event_y - event.y_root)
            height = self.start_event_y - event.y_root + self.start_height
            height = max(20, height)

        self.place_configure_select_frame(x, y, width, height)

    def handle_select_frame_button_release_1(self, frame_name, event):
        """
        鼠标松开事件
        :param frame_name: frame名字
        :param event: event
        :return: None
        """
        self.is_sizing = False
        self["cursor"] = "arrow"
        self.refresh_component_place_info()

    def refresh_component_place_info(self):
        if not self.changed:
            return

        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None:
            return

        self.changed = False
        width = self.select_frame_map['right'].winfo_x() - self.select_frame_map['left'].winfo_x() - 9
        height = self.select_frame_map['down'].winfo_y() - self.select_frame_map['up'].winfo_y() - 9
        add_pos_width = self.select_frame_map['up'].winfo_x() - (self.start_x - 1)
        add_pos_height = self.select_frame_map['up'].winfo_y() - (self.start_y - 5)
        old_operate = ComponentOperatePlaceConfigure(cur_selected.component.winfo_x(), cur_selected.component.winfo_y(), cur_selected.component.winfo_width(), cur_selected.component.winfo_height(), False)
        component_operate = ComponentOperatePlaceConfigure(cur_selected.component.winfo_x() + add_pos_width, cur_selected.component.winfo_y() + add_pos_height, width, height, False)
        DataMgr().add_place_configure_operate(cur_selected, old_operate, component_operate)
