from tkinter import Frame, Label
from tabControlBase import TabControlBase
from functools import partial


class NormalTabBtn(Frame):

    def __init__(self, master=None, cnf={}, **kw):
        Frame.__init__(self, master, cnf, **kw)
        self.tab_label = Label(self, name='tab_label')
        self.tab_close = Label(self, name='tab_close')
        self.tab_under_line = Frame(self, name='tab_under_line')
        self.init_component()

    def place_configure(self, cnf={}, **kw):
        Frame.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def bind(self, sequence=None, func=None, add=None):
        Frame.bind(self, sequence, func, add)
        self.tab_label.bind(sequence, partial(self.on_frame_event, func), add)

    def on_frame_event(self, func, event):
        event.widget = self
        func(event)

    def init_component(self):
        """
        初始化控件
        :return: None
        """
        self.tab_label.configure(text='default')
        self.tab_label.configure(bg=self['bg'])
        self.tab_label.configure(fg='white')

        self.tab_close.configure(text='x')
        self.tab_close.configure(activebackground=self['bg'])
        self.tab_close.configure(activeforeground='red')
        self.tab_close.configure(bg=self['bg'])
        self.tab_close.configure(fg='white')
        self.tab_close.bind("<Enter>", lambda event: self.tab_close.configure(state="active"))
        self.tab_close.bind("<Leave>", lambda event: self.tab_close.configure(state="normal"))

        self.tab_under_line.configure(bg=self['bg'])

        self.configure(highlightbackground='blue')
        self.place_configure({'width': self.get_width(), 'height': 22})

    def get_width(self):
        return self.tab_label.winfo_reqwidth() + self.tab_close.winfo_reqwidth() + 12

    def do_layout(self):
        """
        重新布局界面
        :return:None
        """
        self.tab_label.place_configure({'x': 5, 'y': 0})
        self.tab_close.place_configure({'x': self.tab_label.winfo_reqwidth() + 7, 'y': 0})
        self.tab_under_line.place_configure({'x': 0, 'y': self.winfo_height() - 3, 'height': 3, 'width': self.get_width()})

    def set_label_text(self, label_text):
        self.tab_label.configure(text=label_text)
        self.place_configure({'width': self.get_width(), 'height': 26})

    def get_label_text(self):
        return self.tab_label['text']

    def bind_close(self, func):
        self.tab_close.bind("<Button-1>", func)

    def on_tab_selected(self):
        self.tab_under_line.configure(bg='red')
        self.configure(highlightthickness=1)

    def on_tab_cancel_selected(self):
        self.tab_under_line.configure(bg=self['bg'])
        self.configure(highlightthickness=0)


class TabControlNormal(TabControlBase):

    def __init__(self, master=None, cnf={}, **kw):
        TabControlBase.__init__(self, master, cnf, **kw)

    def add_tab(self, text, data, frame_class, frame_cnf={}, **frame_kwargs):
        """
        添加新tab
        :param text: tab标题
        :param data: 额外数据
        :param frame_class: frame类
        :param frame_cnf:
        :param frame_kwargs
        :return: None
        """
        tab_button = NormalTabBtn(self, bg='#252b39')
        tab_button.set_label_text(text)
        frame = frame_class(self, frame_cnf, **frame_kwargs)
        frame.place_configure({'width': self.winfo_width(), 'height': self.winfo_height() - tab_button.winfo_height()})
        self.add_tab_base(tab_button, frame, data)

    def get_tab_by_name(self, name):
        """
        根据名字获取tab
        :param name: 标签名字
        :return: tab_frame, tab_data
        """
        for index, tab_info in self.tabs.items():
            if tab_info["btn"].get_label_text() == name:
                return index, tab_info["frame"], tab_info["data"]
        return -1, None, None


if __name__ == '__main__':
    from tkinter import Tk, Frame


    class TestTabControl:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 500, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            tab_control = TabControlNormal(self.master, name="test", bg="black")
            tab_control.place_configure({"x": 0, "y": 0, "width": width, "height": height})
            tab_control.add_tab("test1", "111", Frame)
            tab_control.add_tab("test2", "222", Frame, bg='red')
            index, tab, frame = tab_control.get_tab_by_name("test1")
            print(index, tab, frame)


    root = Tk()
    TestTabControl(root)
    root.mainloop()
