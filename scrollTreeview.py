# import start
from tkinter import Frame
from tkinter import Scrollbar
from tkinter.ttk import Treeview
# import end

from functools import partial


# class start from tkinter import Frame
class ScrollTreeView(Frame):

    def __init__(self, master=None, cnf={}, **kw):
        Frame.__init__(self, master, cnf, **kw)
        # create component start
        self.scroll_bar_x = Scrollbar(self, name='scroll_bar_x')  # from tkinter import Scrollbar
        self.scroll_bar_y = Scrollbar(self, name='scroll_bar_y')  # from tkinter import Scrollbar
        self.tree_view = Treeview(self, name='tree_view')  # from tkinter.ttk import Treeview
        # create component end
        self.data = {}
        self.init_component()

    # init_component start
    def init_component(self):
        """
        初始化控件
        :return: None
        """
        # scrollTreeView start
        self.place_configure({'x': 287, 'y': 117, 'width': 330, 'height': 1000})
        # scrollTreeView end
        # scroll_bar_x start
        self.scroll_bar_x.place_configure({'x': 5, 'y': 974, 'width': 317, 'height': 20})
        self.scroll_bar_x.configure(orient='horizontal')
        self.scroll_bar_x.configure(command=self.tree_view.xview)
        # scroll_bar_x end
        # scroll_bar_y start
        self.scroll_bar_y.place_configure({'x': 306, 'y': 7, 'width': 17, 'height': 957})
        self.scroll_bar_y.configure(command=self.tree_view.yview)
        # scroll_bar_y end
        # tree_view start
        self.tree_view.place_configure({'x': 7, 'y': 9, 'width': 295, 'height': 957})
        self.tree_view.configure(xscrollcommand=self.scroll_bar_x.set)
        self.tree_view.configure(yscrollcommand=self.scroll_bar_y.set)
        # tree_view end
    # init_component end

    def get_data_by_index(self, index):
        return self.data.get(index, None)

    def place_configure(self, cnf={}, **kw):
        Frame.place_configure(self, cnf, **kw)
        self.update()
        if "width" in cnf or "height" in cnf:
            self.do_layout()

    def configure_tree_view(self, cnf=None, **kw):
        self.tree_view.configure(cnf, **kw)

    def do_layout(self):
        """
        重新布局界面
        :return: None
        """
        self.scroll_bar_x.place_configure({
            "x": 1,
            "y": self.winfo_height() - self.scroll_bar_x.winfo_height(),
            "width": self.winfo_width() - self.scroll_bar_y.winfo_width() - 1,
        })
        self.scroll_bar_y.place_configure({
            "x": self.winfo_width() - self.scroll_bar_y.winfo_width(),
            "y": 1,
            "height": self.winfo_height() - 1,
        })
        self.tree_view.place_configure({
            "x": 1, "y": 1,
            "width": self.winfo_width() - self.scroll_bar_y.winfo_width() - 1,
            "height": self.winfo_height() - self.scroll_bar_x.winfo_height() - 1,
        })

    def add_root_node(self, root_name, text, values=()):
        """
        增加跟节点
        :param root_name: 根节点名字
        :param text: 根节点标题
        :param values: 节点存的数据
        :return: 节点索引
        """
        return self.add_node("", "end", root_name, text, values)

    def add_node(self, parent_index, add_index, index_name, text, values=()):
        """
        增加节点
        :param parent_index: 父节点索引
        :param add_index: 添加的节点索引
        :param index_name: 节点名字
        :param text: 节点标题
        :param values: 节点存的数据
        :return: 节点索引
        """
        index = self.tree_view.insert(parent_index, add_index, index_name, text=text)
        self.data[index] = values
        return index

    def open_all_node(self, item):
        """
        打开某节点的所有子节点
        :param item: 父节点
        :return: None
        """
        self.tree_view.item(item, open=True)

        def open_child(parent):
            for child in self.tree_view.get_children(parent):
                self.tree_view.item(child, open=True)
                open_child(child)

        open_child(item)

    def delete_node(self, node):
        """
        删除节点
        :param node: 节点
        :return: None
        """
        if not self.tree_view.exists(node):
            return

        for item in self.tree_view.get_children(node):
            if item in self.data:
                del self.data[item]

        if node in self.data:
            self.tree_view.delete(node)
            del self.data[node]

    def clear_all_node(self):
        """
        清除所有节点
        :return: None
        """
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        self.data.clear()

    def column(self, column, option=None, **kw):
        return self.tree_view.column(column, option, **kw)

    def heading(self, column, option=None, **kw):
        return self.tree_view.heading(column, option, **kw)

    def bind(self, sequence=None, func=None, add=None):
        Frame.bind(self, sequence, func, add)
        self.tree_view.bind(sequence, partial(self.on_tree_view_event, func), add)

    def on_tree_view_event(self, func, event):
        event.widget = self
        func(event)

    def selection_set(self, *items):
        self.tree_view.selection_set(*items)

    def focus(self, item=None):
        return self.tree_view.focus(item)

# class end


if __name__ == '__main__':
    from tkinter import Tk

    class TestScrollTreeview:

        def __init__(self, master):
            self.master = master
            width, height, pos_x, pos_y = 500, 500, 0, 0
            self.master.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            tree_view = ScrollTreeView(self.master, name="test")
            tree_view.configure_tree_view(selectmode="browse")
            tree_view.configure_tree_view(columns=("test", ))
            tree_view.place_configure({"x": 0, "y": 0, "width": width, "height": height})
            tree_view.column("#0", width=width - 20, stretch=False)
            tree_view.column("test", width=200, minwidth=20, stretch=False)
            tree_view.heading("#0", text="root", anchor="w")
            tree_view.heading("test", text="test", anchor="w")
            index = tree_view.add_root_node("root", "root_node111111111111111111111111111111112222222222222222222222222222222211111111111111111111111111111111", "root")
            for i in range(35):
                tree_view.add_node(index, "end", f"node_{i}", f"node_{i}", f"node_{i}")
            tree_view.open_all_node("root")
            tree_view.add_root_node("root2", "root_node_2", "root2")
            tree_view.after(6000, lambda: tree_view.delete_node("root"))

    root = Tk()
    TestScrollTreeview(root)
    root.mainloop()
