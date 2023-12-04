from scrollCanvas import ScrollCanvas


class ScrollCols(ScrollCanvas):

    def __init__(self, master=None, cnf={}, **kw):
        ScrollCanvas.__init__(self, master, cnf, **kw)
        self.col_distance = 1                                       # 列间距
        self.pos_x_default = 1                                      # 列初始位置x
        self.created_col_num = 0                                    # 已创建的列数
        self.cols = {}                                              # 存储所有的列

    def place_configure(self, cnf={}, **kw):
        ScrollCanvas.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def get_created_col_num(self):
        return self.created_col_num

    def set_created_col_num(self, created_col_num):
        if self.created_col_num == created_col_num:
            return
        self.created_col_num = created_col_num

    def get_col_by_index(self, index):
        col_dict = self.cols.get(index, None)
        if col_dict is None:
            return None
        return col_dict["col"]

    def get_col_data_by_index(self, index):
        col_dict = self.cols.get(index, None)
        if col_dict is None:
            return None
        return col_dict["data"]

    def clear_cols(self):
        """
        清空所有列
        :return: None
        """
        for k, v in self.cols.items():
            v["col"].destroy()
        self.set_created_col_num(0)
        self.cols.clear()

    def add_col_base(self, col_class, width, col_data, is_do_layout, cnf={}, **kw):
        """
        增加一列
        :param col_class: 列控件类
        :param width: 列控件宽
        :param col_data: 列控件存储的额外数据
        :param is_do_layout: 是否重新布局
        :param cnf:
        :param kw:
        :return: col
        """
        created_num = self.get_created_col_num()

        col = self.create_child(col_class, cnf, name=f"col_{created_num}", **kw)
        col.place_configure({"x":0, "y": 0, "width": width})
        self.cols[created_num] = {"col": col, "data": col_data, "width": width}
        self.set_created_col_num(created_num + 1)

        if is_do_layout:
            self.do_layout()

        return col

    def get_sorted_cols(self):
        return [self.cols[key] for key in sorted(self.cols.keys())]

    def do_layout(self):
        """
        重新布局界面
        :return: None
        """
        ScrollCanvas.do_layout(self)
        pos_x = self.pos_x_default
        for col_info in self.get_sorted_cols():
            col_info["col"].place_configure({"x": pos_x, "y": 1, "width": col_info["width"], "height": self.winfo_height()-self.scroll_bar_x.winfo_height()-3})
            pos_x += col_info["width"] + self.col_distance


if __name__ == '__main__':
    from tkinter import Tk, Button

    class TestScrollCols:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 50, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            cols = ScrollCols(self.master)
            cols.place_configure({"x": 0, "y": 0, "width": 500, "height": height-3})
            cols.set_prop("is_show_scroll_y", False)
            for i in range(5):
                cols.add_col_base(Button, 120, None, False, text=f"button{i}")
            cols.do_layout()


    root = Tk()
    TestScrollCols(root)
    root.mainloop()

