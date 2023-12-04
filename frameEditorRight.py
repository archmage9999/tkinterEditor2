from tabControlButton import TabControlButton
from frameToolbox import FrameToolbox
from framePropertyList import FramePropertyList


class FrameEditorRight(TabControlButton):

    def __init__(self, master=None, cnf={}, **kw):
        TabControlButton.__init__(self, master, cnf, **kw)

    def on_init(self):
        self.bind('<<on_add_tab>>', self.handle_on_add_tab)
        self.bind('<<on_select_tab>>', self.handle_on_select_tab)
        self.add_tab('属性', '属性', FramePropertyList, bg='white')
        self.add_tab('工具箱', '工具箱', FrameToolbox)

    @staticmethod
    def handle_on_add_tab(tab_btn, tab_frame, tab_data, event):
        """
        <<on_add_tab>> 事件
        :param tab_btn: tab_btn
        :param tab_frame: tab_frame
        :param tab_data: tab_data
        :param event: event
        :return: None
        """
        match tab_frame.__class__.__name__:
            case "FrameToolbox":
                tab_frame.on_init()
            case "FramePropertyList":
                tab_frame.set_prop("is_show_scroll_x", False)
                tab_frame.add_prop_rows()
        return

    def handle_on_select_tab(self, tab_btn, tab_frame, tab_data, event):
        """
        <<on_add_tab>> 事件
        :param tab_btn: tab_btn
        :param tab_frame: tab_frame
        :param tab_data: tab_data
        :param event: event
        :return: None
        """
        match tab_frame.__class__.__name__:
            case "FramePropertyList":
                tab_frame.update_props()

    def on_component_selected(self):
        """
        控件被选中
        :return: None
        """
        frame = self.get_tab_frame()
        if frame is None:
            return

        if frame.__class__.__name__ != "FramePropertyList":
            self.select_tab_by_data("属性")
            return

        frame.update_props()

    def on_cancel_component_selected(self):
        """
        取消选中
        :return: None
        """
        frame = self.get_tab_frame()
        if frame is None:
            return

        if frame.__class__.__name__ != "FramePropertyList":
            self.select_tab_by_data("属性")
            return

        frame.update_props()

