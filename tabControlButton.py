from tabControlBase import TabControlBase
from tkinter import Button, Frame


class ButtonTabBtn(Button):

    def __init__(self, master=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)

    def place_configure(self, cnf={}, **kw):
        Frame.place_configure(self, cnf, **kw)
        self.update()

    def get_width(self):
        return self.winfo_reqwidth() + 30

    def bind_close(self, func):
        pass

    def on_tab_selected(self):
        pass

    def on_tab_cancel_selected(self):
        pass


class TabControlButton(TabControlBase):

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
        tab_button = ButtonTabBtn(self, text=text)
        tab_button.place_configure({'width': tab_button.get_width(), 'height': 26})
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
            if tab_info["btn"]['text'] == name:
                return tab_info["frame"], tab_info["data"]
        return None, None


if __name__ == '__main__':
    from tkinter import Tk, Frame


    class TestTabControl:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 500, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            tab_control = TabControlButton(self.master, name="test", bg="black")
            tab_control.place_configure({"x": 0, "y": 0, "width": width, "height": height})

            def on_add_tab(tab_btn, tab_frame, tab_data, event):
                btn = Button(tab_frame, text=tab_data)
                btn.place(x=0, y=0)

            tab_control.bind("<<on_add_tab>>", on_add_tab)
            tab_control.add_tab("test1", "111", Frame)
            tab_control.add_tab("test2", "222", Frame, bg='red')

            tab, frame = tab_control.get_tab_by_name("test1")
            print(tab, frame)


    root = Tk()
    TestTabControl(root)
    root.mainloop()
