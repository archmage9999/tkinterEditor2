import copy
from scrollRows import ScrollRows
from scrollCols import ScrollCols
from dataMgr import DataMgr
from tkinter import colorchooser, END
from tkinter.filedialog import askopenfilename
from componentOperate import *
from functools import partial


class EditPropType(IntEnum):

    TYPE_ENTRY = 1
    TYPE_COMBO_BOX = 2
    TYPE_COLOR = 3
    TYPE_SELECT = 4
    TYPE_VALUES = 5


class EntryBtnFunctionID(IntEnum):

    FUNCTION_COLOR = 1
    FUNCTION_SELECT = 2
    FUNCTION_COLLECT_VALUES = 3


def get_prop_type_by_name(name):
    """
    根据属性名字获取编辑框类型
    :param name: 属性名字
    :return: 编辑框类型
    """
    match name:
        case "anchor" | "bitmap" | "cursor" | "font" | "justify" | "relief" | "overrelief" | "compound" | "state" \
             | "selectmode" | "setgrid" | "exportselection" | "showvalue" | "sliderrelief" | "orient" \
             | "activerelief" | "buttoncursor" | "buttondownrelief" | "buttonuprelief" | "labelanchor":
            return EditPropType.TYPE_COMBO_BOX
        case "combobox_values" | "listbox_values":
            return EditPropType.TYPE_VALUES
        case "background" | "activeforeground" | "activebackground" | "disabledforeground" | "foreground" | "highlightbackground" \
             | "highlightcolor" | "insertbackground" | "selectbackground" | "selectforeground" | "selectcolor" \
             | "troughcolor" | "buttonbackground" | "disabledbackground" | "readonlybackground":
            return EditPropType.TYPE_COLOR
    return EditPropType.TYPE_ENTRY


class EntryWithBtn(Entry):

    def __init__(self, master=None, cnf={}, **kw):
        self.function_id = EntryBtnFunctionID.FUNCTION_COLOR
        if "function_id" in cnf:
            self.function_id = cnf["function_id"]
            del cnf["function_id"]

        self.callback = None
        if "callback" in cnf:
            self.callback = cnf["callback"]
            del cnf["callback"]

        self.function_dict = {
            EntryBtnFunctionID.FUNCTION_COLOR: self.btn_color_click,
            EntryBtnFunctionID.FUNCTION_SELECT: self.btn_select_click,
            EntryBtnFunctionID.FUNCTION_COLLECT_VALUES: self.btn_collect_click,
        }

        Entry.__init__(self, master, cnf, **kw)
        self.button = self.create_btn()

    def set_function_id(self, function_id):
        if self.function_id == function_id:
            return
        self.function_id = function_id

    def get_function_id(self):
        return self.function_id

    def create_btn(self):
        button_prop = {"text": "...", "background": "grey"}
        button = Button(self, button_prop, name="button")
        button.bind("<Button-1>", self.handle_button_button_1)
        return button

    def do_layout(self):
        width = self.place_info().get("width")
        self.button.place_configure({"x": int(width) - 26, "y": 0, "width": 20, "height": 22})

    def handle_button_button_1(self, event):
        function = self.function_dict[self.get_function_id()]
        function()

    def btn_color_click(self):
        color = colorchooser.askcolor()
        if color[0] is None:
            return
        self.delete(0, END)
        self.insert(0, color[1])
        if self.callback is not None:
            self.callback()

    def btn_select_click(self):
        file_path = askopenfilename(title=u"选择文件", filetypes=[("all files", "*")])
        if not file_path:
            return
        self.delete(0, END)
        self.insert(0, file_path)
        if self.callback is not None:
            self.callback()

    def btn_collect_click(self):
        DataMgr().get_editor().open_values_collect(self.callback)


class FrameProperty(ScrollCols):

    TYPE_TO_CLASS = {
        EditPropType.TYPE_ENTRY: Entry,
        EditPropType.TYPE_COMBO_BOX: Combobox,
        EditPropType.TYPE_VALUES: EntryWithBtn,
        EditPropType.TYPE_COLOR: EntryWithBtn,
        EditPropType.TYPE_SELECT: EntryWithBtn,
    }

    def __init__(self, master=None, cnf={}, **kw):
        self.edit_prop_type = EditPropType.TYPE_ENTRY
        if "edit_prop_type" in cnf:
            self.edit_prop_type = cnf["edit_prop_type"]
            del cnf["edit_prop_type"]

        self.prop_name = "None"
        if "prop_name" in cnf:
            self.prop_name = cnf["prop_name"]
            del cnf["prop_name"]

        ScrollCols.__init__(self, master, cnf, **kw)
        self.label = self.create_label()
        self.edit = self.create_edit()

    def create_label(self):
        """
        创建属性名字标签
        :return: None
        """
        label_prop = {"text": self.prop_name, "highlightthickness": 1, "relief": "sunken", "borderwidth": 2}
        label = self.add_col_base(Label, 150, None, False, label_prop)
        return label

    def create_edit(self):
        """
        创建属性编辑框
        :return: None
        """
        edit_class = self.TYPE_TO_CLASS[self.edit_prop_type]
        edit_prop = {
            "borderwidth": 2
        }

        match self.edit_prop_type:
            case EditPropType.TYPE_COMBO_BOX:
                pass
            case EditPropType.TYPE_VALUES:
                edit_prop.update({"function_id": EntryBtnFunctionID.FUNCTION_COLLECT_VALUES, "callback": partial(self.handle_edit_focus_out, None)})
            case EditPropType.TYPE_COLOR:
                edit_prop.update({"function_id": EntryBtnFunctionID.FUNCTION_COLOR, "callback": partial(self.handle_edit_focus_out, None)})
            case EditPropType.TYPE_SELECT:
                edit_prop.update({"function_id": EntryBtnFunctionID.FUNCTION_SELECT, "callback": partial(self.handle_edit_focus_out, None)})

        edit = self.add_col_base(edit_class, 165, None, False, edit_prop)
        match self.edit_prop_type:
            case EditPropType.TYPE_COMBO_BOX:
                values = get_prop_default_values(self.prop_name)
                edit.configure(values=values)
                edit.bind("<<ComboboxSelected>>", self.handle_edit_focus_out)
            case EditPropType.TYPE_VALUES:
                edit.do_layout()
            case EditPropType.TYPE_COLOR:
                edit.do_layout()

        edit.bind("<Key>", self.handle_edit_key)
        edit.bind("<FocusOut>", self.handle_edit_focus_out)

        return edit

    def handle_edit_key(self, event):
        """
        edit键盘事件
        :param event: event
        :return: None
        """
        if event.keysym in ("Return", "Escape"):
            self.master.focus_set()

    def handle_edit_focus_out(self, event):
        """
        edit焦点失去事件
        :param event: event
        :return: None
        """
        value = self.edit.get()
        if not value:
            return

        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None:
            return

        if self.prop_name in ("x", "y", "width", "height"):
            x, y = cur_selected.component.winfo_x(), cur_selected.component.winfo_y()
            width, height = cur_selected.component.winfo_width(), cur_selected.component.winfo_height()
            old_operate = ComponentOperatePlaceConfigure(x, y, width, height, False)
            match self.prop_name:
                case "x":
                    x = int(value)
                case "y":
                    y = int(value)
                case "width":
                    width = int(value)
                case "height":
                    height = int(value)
            component_operate = ComponentOperatePlaceConfigure(x, y, width, height, False)
            DataMgr().add_place_configure_operate(cur_selected, old_operate, component_operate)
        elif self.prop_name == "component_name":
            DataMgr().add_rename_operate(cur_selected, value)
        elif self.prop_name == "listbox_values":
            values = DataMgr().get_editor().form_values_collect.get_values()
            old_items = cur_selected.gui.operate_mgr.get_operate_values(cur_selected.component_id)
            old_operate = ComponentOperateListboxInsert(copy.deepcopy(old_items))
            component_operate = ComponentOperateListboxInsert(copy.deepcopy(values))
            DataMgr().add_listbox_insert_operate(cur_selected, old_operate, component_operate)
        elif self.prop_name == "combobox_values":
            values = DataMgr().get_editor().form_values_collect.get_values()
            old_items = cur_selected.gui.operate_mgr.get_operate_values(cur_selected.component_id)
            old_operate = ComponentOperateComboboxValues(copy.deepcopy(old_items))
            component_operate = ComponentOperateComboboxValues(copy.deepcopy(values))
            DataMgr().add_combobox_values_operate(cur_selected, old_operate, component_operate)
        elif self.prop_name in cur_selected.component.configure():
            old_operate = ComponentOperateConfigure(self.prop_name, cur_selected.component.configure(self.prop_name)[4])
            if self.prop_name in get_change_to_str_list():
                value = change_prop_to_str(value)
                old_operate.prop_value = change_prop_to_str(old_operate.prop_value)
            component_operate = ComponentOperateConfigure(self.prop_name, value)
            DataMgr().add_configure_operate(cur_selected, old_operate, component_operate)
        elif self.prop_name == "title":
            old_title = cur_selected.gui.operate_mgr.get_operate_title(cur_selected.component_id)
            old_operate = ComponentOperateTitle(change_prop_to_str(old_title))
            component_operate = ComponentOperateTitle(change_prop_to_str(value))
            DataMgr().add_title_operate(cur_selected, old_operate, component_operate)

    def do_layout(self):
        """
        重新布局界面
        :return: None
        """
        ScrollCols.do_layout(self)
        pos_x = self.pos_x_default
        for col_info in self.get_sorted_cols():
            col_info["col"].place_configure({"x": pos_x, "y": 1, "width": col_info["width"], "height": self.winfo_height()-3})
            pos_x += col_info["width"] + self.col_distance


class FramePropertyList(ScrollRows):

    def __init__(self, master=None, cnf={}, **kw):
        ScrollRows.__init__(self, master, cnf, **kw)
        self.all_rows = []  # 存储所有的行
        self.show_rows = []  # 存储显示的行
        self.edit_gui = None
        self.edit_component = None

    def tkraise(self, *args):
        self.tk.call('raise', self._w, None)

    def add_prop_rows(self):
        """
        创建所有属性的row,如果每次重新创建所有的row会卡,所以在初始化后直接创建
        :return: None
        """
        all_name = sorted(get_all_prop_name())
        for prop_name in all_name:
            edit_type = get_prop_type_by_name(prop_name)
            edit_prop = {
                "prop_name": prop_name, "edit_prop_type": edit_type,
            }
            row = self.add_row_base(FrameProperty, 30, None, False, edit_prop)
            row.set_prop("is_show_scroll_y", False)
            row.set_prop("is_show_scroll_x", False)
            self.all_rows.append(prop_name)
        self.hide_rows()

    def hide_rows(self):
        """
        隐藏所有row
        :return: None
        """
        del self.show_rows[:]
        for row_name in self.all_rows:
            row_info = self.get_row_info_by_name(row_name)
            if row_info is None:
                print("hide_rows error row:" + row_name)
                continue
            row_info["row"].place_forget()

    def get_row_info_by_name(self, name):
        """
        根据名字获取row
        :param name: 名字
        :return: row
        """
        for row_info in self.rows.values():
            if row_info["row"].prop_name == name:
                return row_info
        return None

    def get_sorted_rows(self):
        sorted_rows = []
        show_rows_sort = sorted(self.show_rows)
        for row_name in show_rows_sort:
            row_info = self.get_row_info_by_name(row_name)
            if row_info is None:
                continue
            sorted_rows.append(row_info)
        return sorted_rows

    def do_layout(self):
        ScrollRows.do_layout(self)
        for row_info in self.rows.values():
            row_info["row"].do_layout()
        ScrollRows.do_layout(self)

    def update_props(self):
        """
        刷新所有属性
        :return: None
        """
        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is None:
            self.hide_rows()
            return

        self.hide_rows()
        self.show_rows.extend(get_show_prop_name(cur_selected.component.__class__.__name__, cur_selected.is_main_form()))
        self.do_layout()
        for prop_name in self.show_rows:
            self.update_prop(cur_selected, prop_name)

    def update_prop(self, selected_component, prop_name):
        row_info = self.get_row_info_by_name(prop_name)
        if row_info is None:
            return

        prop_value = ""
        if prop_name in ["x", "y", "width", "height"]:
            prop_value = selected_component.component.place_info().get(prop_name, "")
        elif prop_name in selected_component.component.configure():
            prop_value = selected_component.component.configure(prop_name)[4]
        elif prop_name == "component_name":
            prop_value = selected_component.component_name
        elif prop_name == "title":
            prop_value = selected_component.gui.operate_mgr.get_operate_title(selected_component.component_id)
        elif prop_name in ("listbox_values", "combobox_values"):
            prop_value = "items"

        row_info["row"].edit.delete(0, "end")
        row_info["row"].edit.insert(0, prop_value)

