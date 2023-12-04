# import start
from tkinter import Toplevel
from tkinter import Button
from tkinter import Entry
from tkinter import Label
# import end
import os
from dataMgr import DataMgr
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from define import tk_init_str, new_form_str, new_project_str


# class start from tkinter import Toplevel
class Form2(Toplevel):

    def __init__(self, master=None, cnf={}, **kw):
        Toplevel.__init__(self, master, cnf, **kw)
        # create component start
        self.button_select = Button(self, name='button_select')  # from tkinter import Button
        self.entry_path = Entry(self, name='entry_path')  # from tkinter import Entry
        self.button_ok = Button(self, name='button_ok')  # from tkinter import Button
        self.button_cancel = Button(self, name='button_cancel')  # from tkinter import Button
        self.label_name = Label(self, name='label_name')  # from tkinter import Label
        self.entry_name = Entry(self, name='entry_name')  # from tkinter import Entry
        # create component end
        self.init_component()

    # init_component start
    def init_component(self):
        """
        初始化控件
        :return: None
        """
        # form2 start
        self.geometry('498x188+582+493')
        self.title('newProject')
        self.resizable(width=False, height=False)
        self.withdraw()
        # form2 end
        # button_select start
        self.button_select.place_configure({'x': 110, 'y': 47, 'width': 100, 'height': 30})
        self.button_select.configure(text='选择项目路径')
        self.button_select.bind('<Button-1>', self.handle_button_select_button_1)
        # button_select end
        # entry_path start
        self.entry_path.place_configure({'x': 222, 'y': 47, 'width': 200, 'height': 30})
        # entry_path end
        # button_ok start
        self.button_ok.place_configure({'x': 138, 'y': 137, 'width': 100, 'height': 30})
        self.button_ok.configure(text='确认')
        self.button_ok.bind('<Button-1>', self.handle_button_ok_button_1)
        # button_ok end
        # button_cancel start
        self.button_cancel.place_configure({'x': 269, 'y': 137, 'width': 100, 'height': 30})
        self.button_cancel.configure(text='取消')
        self.button_cancel.bind('<Button-1>', self.handle_button_cancel_button_1)
        # button_cancel end
        # label_name start
        self.label_name.place_configure({'x': 102, 'y': 89, 'width': 125, 'height': 30})
        self.label_name.configure(text='输入项目名字')
        # label_name end
        # entry_name start
        self.entry_name.place_configure({'x': 222, 'y': 88, 'width': 200, 'height': 30})
        # entry_name end
    # init_component end

    def handle_button_select_button_1(self, event):
        """
        button_select button_1 事件
        :param event:
        :return: None
        """
        project_path = askdirectory()
        self.deiconify()
        if not project_path:
            return
        self.entry_path.insert('end', project_path)

    def handle_button_ok_button_1(self, event):
        """
        button_ok button_1 事件
        :param event:
        :return: None
        """
        project_path = self.entry_path.get()
        if not project_path:
            messagebox.showinfo(title='提示', message='请选择或者输入项目路径')
            self.deiconify()
            return

        if not os.path.exists(project_path):
            messagebox.showinfo(title='提示', message='项目路径不存在')
            self.deiconify()
            return

        project_name = self.entry_name.get()
        if not project_name:
            messagebox.showinfo(title='提示', message='请输入项目名称')
            self.deiconify()
            return

        project_path = os.path.join(project_path, project_name)
        if os.path.exists(project_path):
            messagebox.showinfo(title='提示', message='此目录下已存在该项目,请重新输入项目名称')
            self.deiconify()
            return

        os.mkdir(project_path)
        init_str = tk_init_str
        code = new_form_str.format("Tk", "Form1", init_str, "form1")
        code = new_project_str.format(code)

        with open(os.path.join(project_path, "formMain.py"), "w", encoding="utf-8") as f:
            f.write(code)

        DataMgr().get_editor().on_open_project(project_path)
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
