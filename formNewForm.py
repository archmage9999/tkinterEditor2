# import start
from tkinter import Toplevel
from tkinter.ttk import Combobox
from tkinter import Label
from tkinter import Entry
from tkinter import Button
# import end
import os
from dataMgr import DataMgr
from tkinter import messagebox
from define import *


# class start from tkinter import Toplevel
class Form3(Toplevel):

    def __init__(self, master=None, cnf={}, **kw):
        Toplevel.__init__(self, master, cnf, **kw)
        # create component start
        self.combobox_form_type = Combobox(self, name='combobox_form_type')  # from tkinter.ttk import Combobox
        self.label_form_name = Label(self, name='label_form_name')  # from tkinter import Label
        self.entry_form_name = Entry(self, name='entry_form_name')  # from tkinter import Entry
        self.label_form_type = Label(self, name='label_form_type')  # from tkinter import Label
        self.button_ok = Button(self, name='button_ok')  # from tkinter import Button
        self.button_cancel = Button(self, name='button_cancel')  # from tkinter import Button
        # create component end
        self.init_component()

    # init_component start
    def init_component(self):
        """
        初始化控件
        :return: None
        """
        # form3 start
        self.title('newForm')
        self.geometry('571x192+582+493')
        self.resizable(width=False, height=False)
        self.withdraw()
        # form3 end
        # combobox_form_type start
        self.combobox_form_type.place_configure({'x': 314, 'y': 91, 'width': 200, 'height': 30})
        self.combobox_form_type.configure(values=['Toplevel', ])
        self.combobox_form_type.current(0)
        # combobox_form_type end
        # label_form_name start
        self.label_form_name.place_configure({'x': 69, 'y': 43, 'width': 200, 'height': 30})
        self.label_form_name.configure(text='form_name')
        self.label_form_name.configure(background='white')
        # label_form_name end
        # entry_form_name start
        self.entry_form_name.place_configure({'x': 314, 'y': 43, 'width': 200, 'height': 30})
        # entry_form_name end
        # label_form_type start
        self.label_form_type.place_configure({'x': 69, 'y': 91, 'width': 200, 'height': 30})
        self.label_form_type.configure(text='form_type')
        self.label_form_type.configure(background='white')
        # label_form_type end
        # button_ok start
        self.button_ok.place_configure({'x': 170, 'y': 144, 'width': 100, 'height': 30})
        self.button_ok.configure(text='确定')
        self.button_ok.bind('<Button-1>', self.handle_button_ok_button_1)
        # button_ok end
        # button_cancel start
        self.button_cancel.place_configure({'x': 314, 'y': 144, 'width': 100, 'height': 30})
        self.button_cancel.configure(text='取消')
        self.button_cancel.bind('<Button-1>', self.handle_button_cancel_button_1)
        # button_cancel end
    # init_component end

    def handle_button_ok_button_1(self, event):
        """
        button_ok button_1 事件
        :param event:
        :return: None
        """
        form_name = self.entry_form_name.get()
        if not form_name:
            messagebox.showinfo(title='提示', message='请输入窗口名字')
            self.deiconify()
            return

        form_class = self.combobox_form_type.get()
        if not form_class:
            messagebox.showinfo(title='提示', message='请输入窗口类名')
            self.deiconify()
            return

        form_name = form_name[0].upper() + form_name[1:]
        form_py_name = f"form{form_name}.py"
        project_path = DataMgr().get_project_path()
        form_path = os.path.join(project_path, form_py_name)

        init_str = tk_init_str
        match form_class:
            case "Toplevel":
                init_str = top_level_init_str

        code = new_form_str.format(form_class, form_name, init_str, form_name[0].lower() + form_name[1:])
        with open(form_path, "w", encoding="utf-8") as f:
            f.write(code)

        DataMgr().get_editor().frame_left.refresh_tree(project_path, form_py_name)
        self.handle_button_cancel_button_1(event)

    def handle_button_cancel_button_1(self, event):
        """
        button_cancel button_1 事件
        :param event:
        :return: None
        """
        self.withdraw()
        DataMgr().get_editor().deiconify()

    def destroy(self):
        self.handle_button_cancel_button_1(None)
        return


# class end


