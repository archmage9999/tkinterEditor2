from tkinter import Frame
from functools import partial


class TabControlBase(Frame):

    def __init__(self, master=None, cnf={}, **kw):
        Frame.__init__(self, master, cnf, **kw)
        self.col_distance = 1                                               # 列间距
        self.btn_frame_distance = 0                                         # btn与frame间距
        self.tab_index = 0                                                  # tab索引
        self.cur_tab = None                                                 # 当前选中的tab
        self.tabs = {}                                                      # 所有tab
        self.event_add("<<on_add_tab>>", 'VirtualEvent')
        self.event_add("<<on_select_tab>>", 'VirtualEvent')
        self.event_add("<<on_tab_cancel_selected>>", 'VirtualEvent')
        self.event_add("<<on_del_tab>>", 'VirtualEvent')

    def place_configure(self, cnf={}, **kw):
        Frame.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def get_tab_index(self):
        return self.tab_index

    def set_tab_index(self, tab_index):
        if self.tab_index == tab_index:
            return
        self.tab_index = tab_index

    def add_tab_index(self, add_num=1):
        self.tab_index += add_num

    def get_cur_tab(self):
        return self.cur_tab

    def set_cur_tab(self, cur_tab):
        if self.cur_tab == cur_tab:
            return
        self.cur_tab = cur_tab

    def get_data(self, tab_index=None):
        if tab_index is None:
            tab_index = self.get_cur_tab()
        if tab_index not in self.tabs:
            return None
        return self.tabs[tab_index]["data"]

    def get_tab_frame(self, tab_index=None):
        if tab_index is None:
            tab_index = self.get_cur_tab()
        if tab_index not in self.tabs:
            return None
        return self.tabs[tab_index]["frame"]

    def get_tab_button(self, tab_index=None):
        if tab_index is None:
            tab_index = self.get_cur_tab()
        if tab_index not in self.tabs:
            return None
        return self.tabs[tab_index]["btn"]

    def get_tab_frame_and_data(self, tab_index=None):
        if tab_index is None:
            tab_index = self.get_cur_tab()
        if tab_index not in self.tabs:
            return None, None
        return self.tabs[tab_index]["frame"], self.tabs[tab_index]["data"]

    def bind(self, sequence=None, func=None, add=None):
        if sequence in ("<<on_add_tab>>", "<<on_select_tab>>", "<<on_tab_cancel_selected>>", "<<on_del_tab>>"):
            Frame.bind(self, sequence, partial(self.on_virtual_event, func), add)
            return
        Frame.bind(self, sequence, func, add)

    def on_virtual_event(self, func, event):
        if event.x not in self.tabs:
            return None
        func(self.tabs[event.x]["btn"], self.tabs[event.x]["frame"], self.tabs[event.x]["data"], event)

    def add_tab_base(self, tab_button, tab_frame, data=None, is_select_tab=True):
        """
        添加一个新tab
        :param tab_button: tab_button
        :param tab_frame: tab_frame
        :param data: 存储的额外数据
        :param is_select_tab: 增加tab后是否选中这个tab
        :return: None
        """
        tab_index = self.get_tab_index()
        tab_button.bind("<Button-1>", lambda event: self.tab_select(tab_index))
        self.tabs[tab_index] = {"btn": tab_button, "frame": tab_frame, "data": data}
        self.add_tab_index()
        tab_button.bind_close(lambda event: self.del_tab(tab_index))
        self.event_generate("<<on_add_tab>>", x=tab_index)
        self.do_layout()

        if is_select_tab:
            self.tab_select(tab_index)

    def tab_select(self, tab_index, force_select=False):
        """
        切换tab
        :param tab_index: 要切换到的tab
        :param force_select: 强制选中
        :return: None
        """
        cur_tab = self.get_cur_tab()
        if cur_tab == tab_index and not force_select:
            return

        new_tab_frame = self.get_tab_frame(tab_index)
        if not new_tab_frame:
            return

        new_tab_button = self.get_tab_button(tab_index)
        if not new_tab_button:
            return

        if cur_tab is not None:
            cur_tab_button = self.get_tab_button(cur_tab)
            cur_tab_button.on_tab_cancel_selected()
            self.event_generate("<<on_tab_cancel_selected>>", x=cur_tab)

        # 显示新Frame
        pos_y = new_tab_button.winfo_height() + self.btn_frame_distance
        new_tab_frame.place_configure({"x": 0, "y": pos_y, "width": self.winfo_width(), "height": self.winfo_height() - pos_y})
        new_tab_frame.tkraise()
        self.set_cur_tab(tab_index)
        new_tab_button.on_tab_selected()
        self.event_generate("<<on_select_tab>>", x=tab_index)

    def select_tab_by_data(self, data):
        for index, tab_info in self.tabs.items():
            if tab_info["data"] == data:
                self.tab_select(index)
                return True
        return False

    def del_tab(self, tab_index):
        """
        删除一个tab
        :param tab_index:要删除的tab
        :return:None
        """
        if tab_index not in self.tabs:
            return

        tab_frame = self.get_tab_frame(tab_index)
        tab_button = self.get_tab_button(tab_index)

        # 删除控件回调
        self.on_del_tab(tab_index, tab_button, tab_frame)

        if tab_frame:
            tab_frame.destroy()

        if tab_button:
            tab_button.destroy()

        del self.tabs[tab_index]

        # 重新布局界面
        self.do_layout()

        # 如果删除的是当前选中的则选中第一个
        if self.get_cur_tab() == tab_index:
            self.set_cur_tab(None)
            self.select_first()

    def del_all_tab(self):
        """
        删除所有tab
        :return: None
        """
        keys = []
        for tab_index in self.tabs.keys():
            keys.append(tab_index)

        for tab_index in keys:
            self.del_tab(tab_index)

    def on_del_tab(self, tab_index, tab_button, tab_frame):
        self.event_generate("<<on_del_tab>>", x=tab_index)

    def select_first(self):
        """
        todo:选中第一个tab,以后考虑改成选中上次选中的
        :return:None
        """
        if len(self.tabs) == 0:
            self.set_cur_tab(None)
            return

        first_tab = sorted(self.tabs.keys())[0]
        self.tab_select(first_tab)

    def do_layout(self):
        """
        重新布局界面
        :return:None
        """
        tab_infos = [self.tabs[k] for k in sorted(self.tabs.keys())]
        pos_x = 0
        for tab_info in tab_infos:
            tab_info["btn"].place_configure({"x": pos_x, "y": 0})
            pos_x += tab_info["btn"].winfo_width() + self.col_distance

