from tabControlNormal import TabControlNormal
from scrollText import ScrollText
from frameEdit import FrameEdit
from dataMgr import DataMgr
from define import *


class FrameEditorMiddle(TabControlNormal):

    def __init__(self, master=None, cnf={}, **kw):
        TabControlNormal.__init__(self, master, cnf, **kw)

    def on_init(self):
        self.configure(background=get_color_by_theme(DataMgr().get_theme()))
        self.bind('<<on_add_tab>>', self.handle_on_add_tab)
        self.bind('<<on_del_tab>>', self.handle_on_del_tab)
        self.bind('<<on_select_tab>>', self.handle_on_select_tab)

    def on_change_theme(self):
        """
        主题改变时调用
        :return: None
        """
        self.configure(background=get_color_by_theme(DataMgr().get_theme()))
        for index, tab_info in self.tabs.items():
            tab_info["frame"].slide_window.configure(bg=self['bg'])

    @staticmethod
    def handle_on_add_tab(tab_btn, tab_frame, file, event):
        """
        <<on_add_tab>> 事件
        :param tab_btn: tab_btn
        :param tab_frame: tab_frame
        :param file: tab_data
        :param event: event
        :return: None
        """
        if file.is_gui:
            tab_frame.refresh_gui(file)
            return

        with open(file.file_path, "r", encoding="utf-8") as f:
            tab_frame.insert('end', f.read())

    def handle_on_del_tab(self, tab_btn, tab_frame, file, event):
        """
        tab_control_middle <<on_del_tab>> 事件
        :param tab_btn: tab_btn
        :param tab_frame: tab_frame
        :param file: tab_data
        :param event: event
        :return: None
        """
        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is not None and cur_selected.gui.gui_path == file.file_path:
            DataMgr().cancel_selected_component()
        DataMgr().del_gui(file.file_path)

    def handle_on_select_tab(self, tab_btn, tab_frame, file, event):
        """
        tab_control_middle <<on_select_tab>> 事件
        :param tab_btn: tab_btn
        :param tab_frame: tab_frame
        :param file: tab_data
        :param event: event
        :return: None
        """
        if not file.is_gui:
            self.select_tab_by_data("工具箱")
            return

        gui = DataMgr().get_gui(file.file_path)
        if gui is None:
            return

        DataMgr().select_component(gui.main_form, gui, True)

    def show_file(self, file):
        """
        显示文件
        :param file: 文件
        :return: None
        """
        if self.select_tab_by_data(file):
            return

        if file.is_gui:
            self.add_tab(file.file_name, file, FrameEdit, bg=self['bg'])
            return

        self.add_tab(file.file_name, file, ScrollText, bg=self['bg'])

    def refresh_gui_by_name(self, file_name):
        """
        根据文件名字刷新gui(关掉gui文件再重新打开，我懒的写刷新了)
        :param file_name: 文件名字
        :return: None
        """
        index, frame, file = self.get_tab_by_name(file_name)
        if index == -1:
            return

        self.del_tab(index)
        DataMgr().get_editor().show_file(file)
