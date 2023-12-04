from tkinter import Frame, Scrollbar, Text
from idlelib.colorizer import color_config, ColorDelegator
from idlelib.percolator import Percolator


class ScrollText(Frame):

    def __init__(self, master=None, cnf={}, **kw):
        Frame.__init__(self, master, cnf, **kw)
        self.is_high_light = True
        self.scroll_text = Text(self, name="scroll_text")
        self.scroll_bar_x = Scrollbar(self, name="scroll_bar_x")
        self.scroll_bar_y = Scrollbar(self, name="scroll_bar_y")
        self.init_component()

    def init_component(self):
        """
        初始化控件
        :return: None
        """
        self.scroll_bar_x.configure(orient='horizontal')
        self.scroll_bar_x.configure(command=self.scroll_text.xview)
        self.scroll_bar_x.place_configure({'x': 0, 'y': 0})

        self.scroll_bar_y.configure(command=self.scroll_text.yview)
        self.scroll_bar_y.place_configure({'x': 0, 'y': 0})

        self.scroll_text.configure(wrap='none')
        self.scroll_text.configure(xscrollcommand=self.scroll_bar_x.set)
        self.scroll_text.configure(yscrollcommand=self.scroll_bar_y.set)

        if self.is_high_light:
            color_config(self.scroll_text)
            p = Percolator(self.scroll_text)
            d = ColorDelegator()
            p.insertfilter(d)

    def place_configure(self, cnf={}, **kw):
        Frame.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def do_layout(self):
        """
        重新布局界面
        :return: None
        """
        self.scroll_text.place_configure({
            "x": 0, "y": 0, "width": self.winfo_width() - self.scroll_bar_y.winfo_width(),
            "height": self.winfo_height() - self.scroll_bar_x.winfo_height(),
        })
        self.scroll_bar_x.place_configure({
            "x": 1, "y": self.winfo_height() - self.scroll_bar_x.winfo_height(),
            "width": self.winfo_width() - (self.scroll_bar_y.winfo_width() + 1),
        })
        self.scroll_bar_y.place_configure({
            "x": self.winfo_width() - self.scroll_bar_y.winfo_width(), "y": 1,
            "height": self.winfo_height() - 1,
        })

    def get_text_str(self):
        return self.scroll_text.get("1.0", 'end')

    def insert(self, index, chars, *args):
        self.scroll_text.insert(index, chars, *args)

    def delete(self, index1, index2=None):
        self.scroll_text.delete(index1, index2)

    def index(self, index):
        return self.scroll_text.index(index)

    def get(self, index1, index2=None):
        return self.scroll_text.get(index1, index2)


if __name__ == '__main__':
    from tkinter import Tk, Button, Frame


    class TestScrollText:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 500, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            text = ScrollText(self.master, name="test", background="white")
            text.place_configure({"x": 0, "y": 0, "width": width, "height": height})
            with open("scrollText.py", "r", encoding="utf-8") as f:
                text.scroll_text.insert('end', f.read())


    root = Tk()
    TestScrollText(root)
    root.mainloop()
