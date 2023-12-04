from define import *
from scrollTreeview import ScrollTreeView
from dataMgr import DataMgr


class FrameToolbox(ScrollTreeView):

    def __init__(self, master, cnf={}, **kw):
        ScrollTreeView.__init__(self, master, cnf, **kw)

    def init_component(self):
        ScrollTreeView.init_component(self)
        self.configure_tree_view(selectmode="browse")
        self.configure_tree_view(columns="extra")
        self.place_configure({'x': 0, 'y': 0, 'width': 330, 'height': 1000})
        self.heading("#0", text="Toolbox", anchor="w")
        self.column("#0", width=self.winfo_width() - 20, stretch=False, minwidth=100)
        self.column("extra", width=200, minwidth=20, stretch=False)

    def on_init(self):
        self.bind('<Double-1>', self.handle_double_1)
        public_root_index = self.add_root_node("public", "公共控件")
        for tool_public in toolbox_public_list:
            tool_name = tool_public.__name__
            self.add_node(public_root_index, 'end', tool_name, tool_name, tool_public)
        self.open_all_node("public")

    def handle_double_1(self, event):
        """
        双击事件
        :param event: event
        :return: None
        """
        index = event.widget.focus()
        class_module = all_tool_dict.get(index, None)
        if class_module is None:
            return

        from_module = all_tool_module_dict.get(index, None)
        if from_module is None:
            return

        DataMgr().get_editor().create_component(class_module.__name__, from_module)
