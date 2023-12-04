import re
from tkinter import Button, Frame, Label, Entry, Canvas, Checkbutton, Listbox, Text, Radiobutton, Scale, Scrollbar, Spinbox, LabelFrame
from tkinter import N, S, W, E, NW, SW, NE, SE, NS, EW, NSEW, CENTER
from tkinter import LEFT, RIGHT, TOP, BOTTOM, NONE
from tkinter import RAISED, SUNKEN, FLAT, RIDGE, GROOVE, SOLID
from tkinter import NORMAL, DISABLED, ACTIVE
from tkinter import SINGLE, BROWSE, MULTIPLE, EXTENDED
from tkinter.ttk import Combobox, Treeview, Progressbar, Separator
from tkinter import font as tk_font
from enum import IntEnum


tk_init_str = """
    def __init__(self, screen_name=None, base_name=None, class_name='Tk', use_tk=True, sync=False, use=None):
        Tk.__init__(self, screen_name, base_name, class_name, use_tk, sync, use)"""


top_level_init_str = """
    def __init__(self, master=None, cnf={}, **kw):
        Toplevel.__init__(self, master, cnf, **kw)"""


new_form_str = """# import start
from tkinter import {0}
# import end


# class start from tkinter import {0}
class {1}({0}):
{2}
        # create component start
        # create component end
        self.init_component()

    # init_component start
    def init_component(self):
        \"\"\"
        初始化控件
        :return: None
        \"\"\"
        # {3} start
        self.geometry('571x192+582+493')
        # {3} end
    # init_component end    

# class end
"""


new_project_str = """{0}

if __name__ == '__main__':
    try:
        Form1().mainloop()
    except Exception as e:
        print(e)
"""


class EditorThemeType(IntEnum):
    THEME_DEFAULT = 1
    THEME_BLACK = 2
    THEME_WHITE = 3


EDITOR_THEME = {
    EditorThemeType.THEME_DEFAULT: "#252b39",
    EditorThemeType.THEME_BLACK: "black",
    EditorThemeType.THEME_WHITE: "white",
}


def get_color_by_theme(theme):
    return EDITOR_THEME.get(theme, "black")


def single_instance(cls, *args, **kwargs):
    instances = {}

    def get_instance(*args1, **kwargs1):
        if cls not in instances:
            instances[cls] = cls(*args1, **kwargs1)
        return instances[cls]
    return get_instance


def try_pass(func):
    def try_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(e)
        return
    return try_func


def is_ttk(name):
    return name in ("Combobox", "Treeview", "Progressbar", "Separator")


class_pattern = re.compile(r"# class start (from (.*) import (.*))\nclass (\w*)\((\w*)\):.*(?=# class end)", re.M | re.S)
create_component_pattern = re.compile(r"(?<=# create component start\n).*(?=\s{8}# create component end)", re.M | re.S)
init_component_pattern = re.compile(r"(?<=# init_component start\n).*(?=\s{4}# init_component end)", re.M | re.S)
import_pattern = re.compile(r"(?<=# import start\n).*(?=# import end)", re.M | re.S)

toolbox_public_list = [
    Label, Button, Entry, Frame, Canvas, Checkbutton, Listbox, Text, Radiobutton, Scale, Scrollbar, Spinbox, LabelFrame,
    Combobox, Treeview, Progressbar, Separator
]
all_tool_dict = {}
all_tool_module_dict = {}
for tool in toolbox_public_list:
    all_tool_dict[tool.__name__] = tool
    module_name = "tkinter.ttk" if is_ttk(tool.__name__) else "tkinter"
    all_tool_module_dict[tool.__name__] = module_name


def get_all_prop_name():
    """
    获取所有属性名字
    :return: []
    """
    return [
        "x", "y", "width", "height", "component_name", "text", "background", "repeatdelay", "title", "orient",
        "activebackground", "activeforeground", "anchor", "bitmap", "borderwidth", "cursor", "disabledforeground", "font",
        "foreground", "highlightbackground", "highlightcolor", "highlightthickness", "justify", "padx", "pady", "relief",
        "takefocus", "repeatinterval", "underline", "wraplength", "overrelief", "compound", "state", "insertbackground",
        "insertborderwidth", "insertontime", "insertofftime", "insertwidth", "selectbackground", "selectborderwidth",
        "selectforeground", "show", "closeenough", "xscrollincrement", "yscrollincrement", "selectcolor", "offvalue",
        "onvalue", "selectmode", "setgrid", "exportselection", "listbox_values", "value", "bigincrement", "digits",
        "from", "to", "label", "length", "resolution", "showvalue", "sliderlength", "sliderrelief", "tickinterval",
        "troughcolor", "activerelief", "elementborderwidth", "jump", "buttonbackground", "buttoncursor",
        "buttondownrelief", "buttonuprelief", "disabledbackground", "increment", "readonlybackground", "wrap", "format",
        "validate", "labelanchor", "combobox_values", "phase"
    ]


CURSOR_LIST = [
    'arrow', 'based_arrow_down', 'based_arrow_up', 'boat', 'bogosity', 'bottom_left_corner', 'bottom_right_corner',
    'bottom_side', 'bottom_tee', 'box_spiral', 'center_ptr', 'circle', 'clock', 'coffee_mug', 'cross', 'cross_reverse', 'crosshair',
    'diamond_cross', 'dot', 'dotbox', 'double_arrow', 'draft_large', 'draft_small', 'draped_box', 'exchange', 'fleur', 'gobbler', 'gumby',
    'hand1', 'hand2', 'heart', 'icon', 'iron_cross', 'left_ptr', 'left_side', 'left_tee', 'leftbutton', 'll_angle', 'lr_angle', 'man',
    'middlebutton', 'mouse', 'none', 'pencil', 'pirate', 'plus', 'question_arrow', 'right_ptr', 'right_side', 'right_tee', 'rightbutton',
    'rtl_logo', 'sailboat', 'sb_down_arrow', 'sb_h_double_arrow', 'sb_left_arrow', 'sb_right_arrow', 'sb_up_arrow',
    'sb_v_double_arrow', 'shuttle', 'sizing', 'spider', 'spraycan', 'star', 'target', 'tcross', 'top_left_arrow', 'top_left_corner',
    'top_right_corner', 'top_side', 'top_tee', 'trek', 'ul_angle', 'umbrella', 'ur_angle', 'watch', 'xterm', 'X_cursor'
]


def get_prop_default_values(prop_name):
    """
    获取属性可以设置的内容列表
    :param prop_name: 属性名
    :return: []
    """
    match prop_name:
        case "anchor":
            return [N, S, W, E, NW, SW, NE, SE, CENTER]
        case "labelanchor":
            return [N, S, W, E, NW, SW, NE, SE]
        case "bitmap":
            return ['error', 'gray75', 'gray50', 'gray25', 'gray12', 'hourglass', 'info', 'questhead', 'question', 'warning']
        case "cursor" | "buttoncursor":
            return CURSOR_LIST
        case "font":
            return tk_font.families()
        case "justify":
            return [LEFT, RIGHT, CENTER]
        case "relief" | "overrelief" | "sliderrelief" | "activerelief" | "buttondownrelief" | "buttonuprelief":
            return [RAISED, SUNKEN, FLAT, RIDGE, GROOVE, SOLID]
        case "compound":
            return [NONE, LEFT, RIGHT, TOP, BOTTOM, CENTER]
        case "state":
            return [NORMAL, DISABLED, ACTIVE, "readonly"]
        case "selectmode":
            return [NONE, SINGLE, BROWSE, MULTIPLE, EXTENDED]
        case "setgrid" | "exportselection" | "showvalue" | "jump" | "wrap":
            return ["True", "False"]
        case "orient":
            return ["horizontal", "vertical"]
    return []


def get_change_to_str_list():
    """
    获取需要转换字符串的属性列表
    :return: []
    """
    return [
        "text", "orient", "background", "bitmap", "activebackground", "activeforeground", "anchor", "cursor", "disabledforeground",
        "font", "foreground", "highlightbackground", "highlightcolor", "justify", "relief", "overrelief", "compound", "state",
        "insertbackground", "selectbackground", "selectforeground", "show", "selectcolor", "selectmode", "label", "orient",
        "sliderrelief", "activerelief", "buttonbackground", "buttoncursor", "disabledbackground", "readonlybackground", "wrap",
        "format", "validate", "labelanchor"
    ]


def get_common_prop_name_list():
    """
    获取所有通用属性名字
    :return: []
    """
    return ["x", "y", "width", "height", "component_name"]


label_attr_list = (
    "activebackground", "activeforeground", "anchor", "background", "bitmap", "borderwidth", "cursor",
    "disabledforeground", "font", "foreground", "highlightbackground", "highlightcolor", "highlightthickness",
    "justify", "padx", "pady", "relief", "takefocus", "text", "underline", "wraplength", "state"
)

button_attr_list = (
    "text", "repeatdelay", "activebackground", "activeforeground", "anchor", "bitmap", "borderwidth",
    "cursor", "disabledforeground", "font", "background", "foreground", "highlightbackground", "highlightcolor",
    "highlightthickness", "justify", "padx", "pady", "relief", "takefocus", "repeatinterval", "underline", "wraplength",
    "overrelief", "compound", "state"
)

frame_attr_list = (
    "background", "borderwidth", "cursor", "highlightbackground",
    "highlightcolor", "highlightthickness", "relief", "takefocus",
)

entry_attr_list = (
    "background", "borderwidth", "cursor", "font", "foreground", "highlightbackground",
    "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth", "insertofftime",
    "insertontime", "insertwidth", "justify", "relief", "selectbackground", "selectborderwidth",
    "selectforeground", "show", "state", "takefocus"
)

canvas_attr_list = (
    "background", "borderwidth", "closeenough", "cursor", "highlightbackground", "highlightcolor",
    "highlightthickness", "insertbackground", "insertborderwidth", "insertofftime", "insertontime",
    "insertwidth", "relief", "selectbackground", "selectborderwidth", "selectforeground", "state",
    "takefocus", "xscrollincrement", "yscrollincrement"
)

check_button_attr_list = (
    "activebackground", "activeforeground", "anchor", "background", "bitmap", "borderwidth", "cursor",
    "disabledforeground", "font", "foreground", "highlightbackground", "highlightcolor", "highlightthickness",
    "justify", "offvalue", "onvalue", "padx", "pady", "relief", "selectcolor", "state",
    "takefocus", "text", "underline", "wraplength"
)

list_box_attr_list = (
    "background", "borderwidth", "cursor", "font", "foreground", "highlightbackground",
    "highlightcolor", "highlightthickness", "relief", "selectbackground", "listbox_values",
    "selectborderwidth", "selectforeground", "selectmode", "setgrid", "takefocus", "exportselection"
)

text_attr_list = (
    "background", "borderwidth", "cursor", "exportselection", "font", "foreground", "highlightbackground",
    "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth", "insertofftime",
    "insertontime", "insertwidth", "padx", "pady", "relief", "selectbackground", "selectborderwidth",
    "selectforeground", "setgrid", "takefocus"
)

radio_button_attr_list = (
    "activebackground", "activeforeground", "anchor", "background", "bitmap", "borderwidth", "cursor",
    "disabledforeground", "font", "foreground", "highlightbackground", "highlightcolor", "highlightthickness",
    "justify", "padx", "pady", "relief", "selectcolor", "state", "takefocus", "text", "underline", "value",
    "wraplength"
)

scale_attr_list = (
    "activebackground", "background", "bigincrement", "borderwidth", "cursor", "digits", "font", "foreground",
    "from", "highlightbackground", "highlightcolor", "highlightthickness", "label", "length", "orient",
    "relief", "repeatdelay", "repeatinterval", "resolution", "showvalue", "sliderlength", "sliderrelief",
    "state", "takefocus", "tickinterval", "to", "troughcolor"
)

scroll_bar_attr_list = (
    "activebackground", "activerelief", "background", "borderwidth", "cursor", "elementborderwidth",
    "highlightbackground", "highlightcolor", "highlightthickness", "jump", "orient",
    "relief", "repeatdelay", "repeatinterval", "takefocus", "troughcolor"
)

spinbox_attr_list = (
    "activebackground", "background", "borderwidth", "cursor", "exportselection", "font", "foreground",
    "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth",
    "insertofftime", "insertontime", "insertwidth", "justify", "relief", "repeatdelay", "repeatinterval",
    "selectbackground", "selectborderwidth", "selectforeground", "takefocus",
    "buttonbackground", "buttoncursor", "buttondownrelief", "buttonuprelief",
    "disabledbackground", "disabledforeground", "format", "from", "increment",
    "readonlybackground", "state", "to", "validate", "wrap"
)

label_frame_attr_list = (
    "borderwidth", "cursor", "font", "foreground", "highlightbackground", "highlightcolor",
    "highlightthickness", "padx", "pady", "relief", "takefocus", "text", "background",
    "labelanchor"
)

combobox_attr_list = (
    "cursor", "exportselection", "justify", "state", "combobox_values"
)

treeview_attr_list = (
    "cursor",
)

progressbar_attr_list = (
    "cursor", "orient", "length", "maximum", "value", "phase"
)

separator_attr_list = (
    "cursor", "orient"
)


def get_show_prop_name(module_class, is_main_form):
    """
    获取要显示的属性名字
    :param module_class:
    :param is_main_form:
    :return: []
    """
    show_name_list = []
    show_name_list.extend(get_common_prop_name_list())

    match module_class:
        case "Label":
            show_name_list.extend(label_attr_list)
        case "Button":
            show_name_list.extend(button_attr_list)
        case "Frame":
            show_name_list.extend(frame_attr_list)
        case "Entry":
            show_name_list.extend(entry_attr_list)
        case "Canvas":
            show_name_list.extend(canvas_attr_list)
        case "Checkbutton":
            show_name_list.extend(check_button_attr_list)
        case "Listbox":
            show_name_list.extend(list_box_attr_list)
        case "Text":
            show_name_list.extend(text_attr_list)
        case "Radiobutton":
            show_name_list.extend(radio_button_attr_list)
        case "Scale":
            show_name_list.extend(scale_attr_list)
        case "Scrollbar":
            show_name_list.extend(scroll_bar_attr_list)
        case "Spinbox":
            show_name_list.extend(spinbox_attr_list)
        case "LabelFrame":
            show_name_list.extend(label_frame_attr_list)
        case "Combobox":
            show_name_list.extend(combobox_attr_list)
        case "Treeview":
            show_name_list.extend(treeview_attr_list)
        case "Progressbar":
            show_name_list.extend(progressbar_attr_list)
        case "Separator":
            show_name_list.extend(separator_attr_list)

    if is_main_form:
        show_name_list.extend(("title", ))

    return show_name_list


def change_prop_to_str(prop_value):
    return f"'{prop_value}'"

