from tkinter import Canvas, Frame, Scrollbar
from functools import partial
from define import is_ttk


class ScrollCanvas(Canvas):

    def __init__(self, master=None, cnf={}, **kw):
        Canvas.__init__(self, master, cnf, **kw)
        self.is_show_scroll_x = True
        self.is_show_scroll_y = True
        self.slide_window = Frame(self, name='slide_window')
        self.scroll_bar_x = Scrollbar(self, name='scroll_bar_x')
        self.scroll_bar_y = Scrollbar(self, name='scroll_bar_y')
        self.init_component()

    def init_component(self):
        """
        初始化控件
        :return: None
        """
        self.slide_window.configure(bg=self['bg'])
        self.slide_window.bind("<MouseWheel>", self.scroll_slide_window_y)
        self.slide_window.bind("<Control-MouseWheel>", self.scroll_slide_window_x)
        self.slide_window.bind_all("<Configure>", self.on_child_configure)
        self.create_window((0, 0), window=self.slide_window, anchor="nw")

        self.scroll_bar_x.place_configure({'x': 0, 'y': 0})
        self.scroll_bar_x.configure(orient='horizontal')
        self.scroll_bar_x.configure(command=self.xview)

        self.scroll_bar_y.place_configure({'x': 0, 'y': 0})
        self.scroll_bar_y.configure(command=self.yview)

        self.configure(xscrollcommand=self.scroll_bar_x.set)
        self.configure(yscrollcommand=self.scroll_bar_y.set)

    def place_configure(self, cnf={}, **kw):
        Canvas.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def set_prop(self, prop_name, prop_value):
        """
        设置属性
        :param prop_name: 属性名字
        :param prop_value: 属性值
        :return: None
        """
        setattr(self, prop_name, prop_value)
        self.do_layout()

    def on_child_configure(self, event):
        """
        当子控件位置与大小发生变化时触发
        :param event: 事件
        :return: None
        """
        if not event.widget or not hasattr(event.widget, "master"):
            return

        if event.widget.master is not self.slide_window:
            return

        self.update_scroll()

    def create_child(self, child_class, cnf={}, **kw):
        if is_ttk(child_class.__name__):
            return child_class(self.slide_window, **kw)
        return child_class(self.slide_window, cnf, **kw)

    def do_layout(self):
        """
        重新布局界面
        :return:None
        """
        if self.is_show_scroll_x:
            scroll_bar_y_width = 0 if not self.is_show_scroll_y else self.scroll_bar_y.winfo_width()
            self.scroll_bar_x.place_configure({"x": 1, "y": self.winfo_height() - self.scroll_bar_x.winfo_height(), "width": self.winfo_width() - scroll_bar_y_width - 1})
        else:
            self.scroll_bar_x.place_forget()

        if self.is_show_scroll_y:
            self.scroll_bar_y.place_configure({"x": self.winfo_width() - self.scroll_bar_y.winfo_width(), "y": 1, "height": self.winfo_height() - 1})
        else:
            self.scroll_bar_y.place_forget()

        self.slide_window.configure(width=self.winfo_width())
        self.slide_window.configure(height=self.winfo_height())
        self.update_scroll()

    def update_scroll(self):
        """
        更新滑动条
        :return:None
        """
        self.update_scroll_vertical()
        self.update_scroll_horizontal()
        self.configure(scrollregion=self.bbox("all"))

    def update_scroll_vertical(self):
        """
        更新垂直滑动条
        :return:None
        """
        height = self.winfo_height()
        if (pos_y := self.calc_slide_window_height()) > self.winfo_height():
            scroll_bar_x_height = 0 if not self.is_show_scroll_x else self.scroll_bar_x.winfo_height()
            height = pos_y + scroll_bar_x_height + 1
        self.slide_window.configure(height=height)

    def calc_slide_window_height(self):
        """
        计算滑动窗口的高度
        :return: int
        """
        slaves = self.slide_window.place_slaves()
        if not slaves:
            return 0

        pos_y = 0
        for child in slaves:
            if not child.place_info():
                continue
            if child.winfo_y() + child.winfo_height() > pos_y:
                pos_y = child.winfo_y() + child.winfo_height()

        return pos_y

    def update_scroll_horizontal(self):
        """
        更新水平滑动条
        :return:None
        """
        width = self.winfo_width()
        if (pos_x := self.calc_slide_window_width()) > self.winfo_width():
            scroll_bar_y_width = 0 if not self.is_show_scroll_y else self.scroll_bar_y.winfo_width()
            width = pos_x + scroll_bar_y_width + 1
        self.slide_window.configure(width=width)

    def calc_slide_window_width(self):
        """
        计算滑动窗口的宽度
        :return: int
        """
        slaves = self.slide_window.place_slaves()
        if not slaves:
            return 0

        pos_x = 0
        for child in slaves:
            if not child.place_info():
                continue
            if child.winfo_x() + child.winfo_width() > pos_x:
                pos_x = child.winfo_x() + child.winfo_width()

        return pos_x

    def scroll_slide_window_y(self, event):
        """
        垂直滚动页面
        :param event:
        :return:None
        """
        if self.slide_window["height"] <= self.winfo_height():
            return
        units = -5 if event.delta > 0 else 5
        self.yview_scroll(units, "units")

    def scroll_slide_window_x(self, event):
        """
        水平滚动页面
        :param event:
        :return:None
        """
        if self.slide_window["width"] <= self.winfo_width():
            return
        units = -5 if event.delta > 0 else 5
        self.xview_scroll(units, "units")

    def bind(self, sequence=None, func=None, add=None):
        Frame.bind(self, sequence, func, add)
        self.slide_window.bind(sequence, partial(self.on_frame_event, func), add)

    def on_frame_event(self, func, event):
        event.widget = self
        func(event)


if __name__ == '__main__':
    from tkinter import Tk, Button, Entry

    class TestScrollCanvas:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 500, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            canvas = ScrollCanvas(self.master, name="test", background="white")
            canvas.place_configure({"x": 0, "y": 0, "width": width, "height": height})
            button = canvas.create_child(Button, name="button", text="button")
            button.place(x=600, y=100, anchor="nw")
            entry = canvas.create_child(Entry, name="entry", background="red")
            entry.place_configure(x=10, y=600, width=149, height=21)
            canvas.after(6000, lambda: button.place(x=100, y=100, anchor="nw"))

    root = Tk()
    TestScrollCanvas(root)
    root.mainloop()
