# import start
from tkinter import Tk
from frameEditorLeft import FrameEditorLeft
from frameEditorMiddle import FrameEditorMiddle
from frameEditorRight import FrameEditorRight
# import end

import os
import sys
from functools import partial
from tkinter import Menu, messagebox
from tkinter.filedialog import askdirectory
from dataMgr import DataMgr
from selectedComponent import SelectedComponent
from formNewProject import Form2
from formNewForm import Form3
from formValuesCollect import Form4
from componentOperate import *


# class start from tkinter import Tk
class Form1(Tk):

    def __init__(self, screen_name=None, base_name=None, class_name='Tk', use_tk=True, sync=False, use=None):
        Tk.__init__(self, screen_name, base_name, class_name, use_tk, sync, use)
        # create component start
        self.frame_left = FrameEditorLeft(self, name='frame_left')  # from frameEditorLeft import FrameEditorLeft
        self.frame_middle = FrameEditorMiddle(self, name='frame_middle')  # from frameEditorMiddle import FrameEditorMiddle
        self.frame_right = FrameEditorRight(self, name='frame_right')  # from frameEditorRight import FrameEditorRight
        # create component end
        self.form_new_project = Form2(self, name='form_new_project')
        self.form_new_form = Form3(self, name='form_new_form')
        self.form_values_collect = Form4(self, name='form_values_collect')
        DataMgr().set_editor(self)
        self.init_menu()
        self.init_component()
        self.init_component_2()
        self.init_hot_key()

    # init_component start
    def init_component(self):
        """
        初始化控件
        :return: None
        """
        # form1 start
        self.title('tkinterEditor')
        self.geometry('1920x1000+94+125')
        # form1 end
        # frame_left start
        self.frame_left.configure_tree_view(selectmode='browse')
        self.frame_left.configure_tree_view(columns='extra')
        self.frame_left.place_configure({'x': 0, 'y': 0, 'width': 330, 'height': 1000})
        self.frame_left.column('#0', width=310, stretch=False, minwidth=100)
        self.frame_left.column('extra', width=200, minwidth=20, stretch=False)
        self.frame_left.heading('#0', text='Project', anchor='w')
        self.frame_left.on_init()
        # frame_left end
        # frame_middle start
        self.frame_middle.place_configure({'x': 331, 'y': 0, 'width': 1249, 'height': 1000})
        self.frame_middle.configure(background='#1b2529')
        self.frame_middle.on_init()
        # frame_middle end
        # frame_right start
        self.frame_right.place_configure({'x': 1581, 'y': 0, 'width': 339, 'height': 1000})
        self.frame_right.configure(background='white')
        self.frame_right.on_init()
        # frame_right end
    # init_component end

    # init_menu start
    def init_menu(self):
        """
        初始化菜单
        :return: None
        """
        menu_main = Menu(self, name='menu')
        menu_file = Menu(menu_main, name='file', tearoff=0)
        menu_file.add_command(label='new_project', accelerator='ctrl+n', command=self.new_project)
        menu_file.add_command(label='open_project', accelerator='ctrl+o', command=self.open_project)
        menu_file.add_command(label='new_form', accelerator='none', command=self.new_form)
        menu_file.add_command(label='save_file', accelerator='ctrl+s', command=self.save_file)
        menu_main.add_cascade(label='file', menu=menu_file)

        menu_edit = Menu(menu_main, name='edit', tearoff=0)
        menu_edit.add_command(label='undo', accelerator='ctrl+z', command=self.undo_operate)
        menu_edit.add_command(label='redo', accelerator='ctrl+y', command=self.redo_operate)
        menu_edit.add_command(label='delete', accelerator='delete', command=self.delete_component)
        menu_edit.add_command(label='move_up', accelerator='ctrl+up', command=partial(self.move_control, "Up", None))
        menu_edit.add_command(label='move_down', accelerator='ctrl+down', command=partial(self.move_control, "Down", None))
        menu_edit.add_command(label='move_left', accelerator='ctrl+left', command=partial(self.move_control, "Left", None))
        menu_edit.add_command(label='move_right', accelerator='ctrl+right', command=partial(self.move_control, "Right", None))
        menu_edit.add_command(label='size_up', accelerator='shift+up', command=partial(self.move_control, "North", None))
        menu_edit.add_command(label='size_down', accelerator='shift+down', command=partial(self.move_control, "South", None))
        menu_edit.add_command(label='size_left', accelerator='shift+left', command=partial(self.move_control, "West", None))
        menu_edit.add_command(label='size_right', accelerator='shift+right', command=partial(self.move_control, "East", None))
        menu_main.add_cascade(label='edit', menu=menu_edit)

        menu_window = Menu(menu_main, name='window', tearoff=0)
        menu_window.add_command(label='refresh_main_ui', accelerator='None', command=self.refresh_main_ui)
        menu_window.add_command(label='change_theme', accelerator='None')
        menu_theme = Menu(menu_window, name="theme", tearoff=0)
        menu_theme.add_radiobutton(label="default", value=1, command=partial(self.change_theme, 1))
        menu_theme.add_radiobutton(label="black", value=3, command=partial(self.change_theme, 2))
        menu_theme.add_radiobutton(label="white", value=2, command=partial(self.change_theme, 3))
        menu_window.add_cascade(label='theme', menu=menu_theme)

        menu_main.add_cascade(label='window', menu=menu_window)
        self.config(menu=menu_main)
    # init_menu end

    def init_hot_key(self):
        """
        初始化快捷键
        :return: None
        """
        self.bind("<Control-o>", lambda event: self.open_project())
        self.bind("<Control-n>", lambda event: self.new_project())
        self.bind("<Control-s>", lambda event: self.save_file())
        self.bind("<Control-z>", lambda event: self.undo_operate())
        self.bind("<Control-y>", lambda event: self.redo_operate())
        self.bind("<Key-Delete>", lambda event: self.delete_component())

        size_map = {
            "Up": "North",
            "Down": "South",
            "Left": "West",
            "Right": "East",
        }
        for k in ("Up", "Down", "Left", "Right"):
            self.bind(f"<Control-{k}>", partial(self.move_control, k))
            self.bind(f"<Shift-{k}>", partial(self.move_control, size_map[k]))

    def init_component_2(self):
        """
        初始化窗口2
        :return: None
        """
        self.state('zoomed')
        self.on_configure(None)

    def on_configure(self, event):
        """
        窗口size改变事件 todo:这个事件有问题,如果监测的话会循环调用
        :param event: event
        :return: None
        """
        width = self.winfo_width()
        height = self.winfo_height()

        self.frame_left.place_configure({'x': 0, 'y': 0, 'width': 330, 'height': height})
        self.frame_middle.place_configure({'x': 331, 'y': 0, 'width': width - 669, 'height': height})
        self.frame_right.place_configure({'x': width - 339, 'y': 0, 'width': 339, 'height': height})

        cur_tab = self.frame_middle.get_cur_tab()
        if cur_tab is not None:
            self.frame_middle.tab_select(cur_tab, True)

        cur_tab = self.frame_right.get_cur_tab()
        if cur_tab is not None:
            self.frame_right.tab_select(cur_tab, True)

    def new_project(self):
        """
        创建新项目
        :return: None
        """
        project_path = DataMgr().get_project_path()
        if project_path is not None:
            result = messagebox.askquestion(title='提示', message='创建新项目时会关闭当前项目')
            if result == "no":
                return

        self.close_project()
        self.form_new_project.deiconify()

    def close_project(self):
        """
        关闭当前项目
        :return: None
        """
        project_path = DataMgr().get_project_path()
        if project_path is None:
            return

        DataMgr().set_project_path(None)
        self.frame_left.delete_node(project_path)
        self.frame_middle.del_all_tab()

    def open_project(self):
        """
        打开项目
        :return: None
        """
        project_path = DataMgr().get_project_path()
        if project_path is not None:
            result = messagebox.askquestion(title='提示', message='打开新项目时会关闭当前项目')
            if result == "no":
                return

        self.close_project()
        project_path = askdirectory()
        if not project_path:
            return

        self.on_open_project(project_path)

    def on_open_project(self, project_path):
        """
        打开项目成功
        :param project_path: 项目路径
        :return: None
        """
        main_py_path = os.path.join(project_path, "formMain.py")
        if not os.path.exists(main_py_path):
            return

        if DataMgr().has_project():
            messagebox.showinfo(title='提示', message='暂时不支持打开多个项目')
            return

        sys.path.append(os.path.dirname(project_path))
        DataMgr().set_project_path(project_path)
        self.frame_left.refresh_tree(project_path)

    def new_form(self):
        """
        创建新窗口
        :return: None
        """
        project_path = DataMgr().get_project_path()
        if project_path is None:
            messagebox.showinfo(title='提示', message='请先打开项目')
            return

        self.form_new_form.deiconify()

    def save_file(self):
        """
        保存文件
        :return: None
        """
        frame, file = self.frame_middle.get_tab_frame_and_data()
        if frame is None or file is None:
            return

        if file.is_gui:
            gui = DataMgr().get_gui(file.file_path)
            if gui is None:
                return
            replace_str = gui.operate_mgr.replace_form_str(gui.ori_code)
            with open(file.gui_py_path, "w", encoding="utf-8") as f:
                f.write(replace_str)
            index, gui_py_frame, gui_py_file = self.frame_middle.get_tab_by_name(file.gui_py_name)
            if gui_py_frame is not None:
                gui_py_frame.delete('1.0', 'end')
                gui_py_frame.insert('end', replace_str)
            messagebox.showinfo(title='提示', message='保存成功')
            return

        # 如果想保存其他文件就把这里的注释打开
        # with open(file.file_path, "w", encoding="utf-8") as f:
        #     text_str = frame.get_text_str()
        #     # 这里取出来的字符串会多一个字符
        #     f.write(text_str[:-1])
        #
        # self.frame_middle.refresh_gui_by_name(file.file_name + ".gui")
        # self.frame_middle.select_tab_by_data(file)
        #
        # messagebox.showinfo(title='提示', message='保存成功')

        messagebox.showinfo(title='提示', message='此文件不支持保存')

    def show_file(self, file):
        """
        显示文件
        :param file: 文件
        :return: None
        """
        if self.frame_middle.select_tab_by_data(file):
            return

        if file.is_gui and not DataMgr().add_gui(file):
            return

        self.frame_middle.show_file(file)

    def on_component_selected(self):
        """
        控件被选中
        :return: None
        """
        frame_middle = self.frame_middle.get_tab_frame()
        if frame_middle is not None:
            frame_middle.on_component_selected()
        self.frame_right.on_component_selected()

    def on_cancel_component_selected(self):
        """
        取消选中控件
        :return: None
        """
        self.frame_right.on_cancel_component_selected()

    def create_component(self, class_name, from_module):
        """
        创建控件
        :param class_name: 控件类名
        :param from_module: 控件模块名
        :return: None
        """
        frame, file = self.frame_middle.get_tab_frame_and_data()
        if frame is None or file is None or not file.is_gui:
            return

        gui = DataMgr().get_gui(file.file_path)
        if gui is None:
            return

        component_name = gui.generate_component_name(class_name)
        operate_mgr = gui.operate_mgr.create_component_operate_mgr(component_name, class_name, from_module)
        if operate_mgr is None:
            return

        component = frame.create_component(gui, from_module, class_name, gui.main_form, operate_mgr.component_id)
        if component is None:
            return

        s = SelectedComponent(component, gui)
        DataMgr().add_create_operate(s, operate_mgr)

    def undo_operate(self):
        """
        取消操作
        :return: None
        """
        frame, file = self.frame_middle.get_tab_frame_and_data()
        if frame is None or file is None or not file.is_gui:
            return

        gui = DataMgr().get_gui(file.file_path)
        if gui is None:
            return

        DataMgr().undo_operate(gui, frame)

    def redo_operate(self):
        """
        重新执行操作
        :return: None
        """
        frame, file = self.frame_middle.get_tab_frame_and_data()
        if frame is None or file is None or not file.is_gui:
            return

        gui = DataMgr().get_gui(file.file_path)
        if gui is None:
            return

        DataMgr().redo_operate(gui, frame)

    def delete_component(self):
        """
        删除控件
        :return: None
        """
        frame, file = self.frame_middle.get_tab_frame_and_data()
        if frame is None or file is None or not file.is_gui:
            return

        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None or cur_selected.is_main_form():
            return

        DataMgr().add_delete_operate(cur_selected)

    def move_control(self, keysym, event):
        """
        移动控件
        :param keysym: Up,Down,Left,Right
        :param event:
        :return: None
        """
        frame, file = self.frame_middle.get_tab_frame_and_data()
        if frame is None or file is None or not file.is_gui:
            return

        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None:
            return

        x, y = cur_selected.component.winfo_x(), cur_selected.component.winfo_y()
        width, height = cur_selected.component.winfo_width(), cur_selected.component.winfo_height()
        old_operate = ComponentOperatePlaceConfigure(x, y, width, height, False)

        match keysym:
            case "Up":
                y -= 1
            case "Down":
                y += 1
            case "Left":
                x -= 1
            case "Right":
                x += 1
            case "North":
                height -= 1
            case "South":
                height += 1
            case "West":
                width -= 1
            case "East":
                width += 1

        component_operate = ComponentOperatePlaceConfigure(x, y, width, height, False)
        DataMgr().add_place_configure_operate(cur_selected, old_operate, component_operate)

    def change_theme(self, theme):
        """
        改变主题
        :return: None
        """
        DataMgr().set_theme(theme)
        self.frame_middle.on_change_theme()

    def refresh_main_ui(self):
        """
        刷新主界面
        :return: None
        """
        self.on_configure(None)

    def open_values_collect(self, callback):
        """
        打开form_values_collect
        :param callback: 回调函数
        :return: None
        """
        project_path = DataMgr().get_project_path()
        if project_path is None:
            return
        self.form_values_collect.deiconify(callback)

# class end


if __name__ == '__main__':
    try:
        Form1().mainloop()
    except Exception as e:
        print(e)
