from scrollCanvas import ScrollCanvas


class ScrollRows(ScrollCanvas):

    def __init__(self, master=None, cnf={}, **kw):
        ScrollCanvas.__init__(self, master, cnf, **kw)
        self.row_distance = 1                                           # 行间距
        self.pos_y_default = 1                                          # 列初始位置y
        self.created_row_num = 0                                        # 已创建的行数
        self.rows = {}                                                  # 存储所有的行

    def place_configure(self, cnf={}, **kw):
        ScrollCanvas.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def get_created_row_num(self):
        return self.created_row_num

    def set_created_row_num(self, created_row_num):
        if self.created_row_num == created_row_num:
            return
        self.created_row_num = created_row_num

    def get_row_by_index(self, index):
        row_dict = self.rows.get(index, None)
        if row_dict is None:
            return None
        return row_dict["row"]

    def get_row_data_by_index(self, index):
        row_dict = self.rows.get(index, None)
        if row_dict is None:
            return None
        return row_dict["data"]

    def clear_rows(self):
        """
        清空所有row
        :return:None
        """
        for k, v in self.rows.items():
            v["row"].destroy()
        self.set_created_row_num(0)
        self.rows.clear()

    def add_row_base(self, row_class, height, row_data, is_do_layout, cnf={}, **kw):
        """
        增加一行
        :param row_class: 行控件类
        :param height: 行控件高
        :param row_data: 行控件存储的额外数据
        :param is_do_layout:是否do_layout
        :param cnf:
        :param kw:
        :return: row
        """
        created_num = self.get_created_row_num()

        row = self.create_child(row_class, cnf, name=f"row_{created_num}", **kw)
        row.place_configure({"x": 0, "y": 0, "height": height})
        self.rows[created_num] = {"row": row, "data": row_data, "height": height}
        self.set_created_row_num(created_num + 1)

        if is_do_layout:
            self.do_layout()

        return row

    def get_sorted_rows(self):
        return [self.rows[key] for key in sorted(self.rows.keys())]

    def do_layout(self):
        """
        重新布局界面
        :return:None
        """
        ScrollCanvas.do_layout(self)
        pos_y = self.pos_y_default
        for row_info in self.get_sorted_rows():
            row_info["row"].place_configure({"x": 1, "y": pos_y, "width": self.winfo_width()-self.scroll_bar_y.winfo_width()-3, "height": row_info["height"]})
            pos_y += row_info["height"] + self.row_distance


if __name__ == '__main__':
    from tkinter import Tk, Button

    class TestScrollRows:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 500, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            rows = ScrollRows(self.master, name="test", background="white")
            rows.place_configure({"x": 0, "y": 0, "width": width, "height": height})
            rows.set_prop("is_show_scroll_x", False)
            for i in range(20):
                rows.add_row_base(Button, 30, None, False, text=f"button{i}")
            rows.do_layout()


    root = Tk()
    TestScrollRows(root)
    root.mainloop()
