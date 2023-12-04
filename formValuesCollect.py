# import start
from tkinter import Toplevel
from scrollText import ScrollText
from tkinter import Label
from tkinter import Button
# import end
from dataMgr import DataMgr


# class start from tkinter import Toplevel
class Form4(Toplevel):

    def __init__(self, master=None, cnf={}, **kw):
        Toplevel.__init__(self, master, cnf, **kw)
        # create component start
        self.text_values = ScrollText(self, name='text_values')  # from scrollText import ScrollText
        self.label1 = Label(self, name='label1')  # from tkinter import Label
        self.button_ok = Button(self, name='button_ok')  # from tkinter import Button
        self.button_cancel = Button(self, name='button_cancel')  # from tkinter import Button
        # create component end
        self.callback = None
        self.init_component()

    # init_component start
    def init_component(self):
        """
        初始化控件
        :return: None
        """
        # form4 start
        self.geometry('630x469+582+493')
        self.title('newProject')
        self.resizable(width=False, height=False)
        self.withdraw()
        # form4 end
        # text_values start
        self.text_values.place_configure({'x': 32, 'y': 43, 'width': 568, 'height': 366})
        # text_values end
        # label1 start
        self.label1.place_configure({'x': 208, 'y': 6, 'width': 200, 'height': 30})
        self.label1.configure(text='请输入要添加的字符串(每行一个)')
        # label1 end
        # button_ok start
        self.button_ok.place_configure({'x': 213, 'y': 423, 'width': 100, 'height': 30})
        self.button_ok.configure(text='确定')
        self.button_ok.bind('<Button-1>', self.handle_button_ok_button_1)
        # button_ok end
        # button_cancel start
        self.button_cancel.place_configure({'x': 338, 'y': 423, 'width': 100, 'height': 30})
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
        if self.callback is not None:
            self.callback()
        self.handle_button_cancel_button_1(None)

    def handle_button_cancel_button_1(self, event):
        """
        button_cancel button_1 事件
        :param event:
        :return: None
        """
        self.withdraw()
        DataMgr().get_editor().deiconify()

    def deiconify(self, callback):
        """
        显示
        :return: None
        """
        Toplevel.deiconify(self)
        self.callback = callback
        self.text_values.delete('1.0', "end")
        cur_selected = DataMgr().get_cur_selected()
        if cur_selected is not None:
            old_items = cur_selected.gui.operate_mgr.get_operate_values(cur_selected.component_id)
            for item in old_items:
                self.text_values.insert('end', item + '\n')

    def get_values(self):
        """
        获取所有value
        :return: []
        """
        values = []
        number_of_lines = self.text_values.index('end').split('.')[0]
        for i in range(int(number_of_lines)):
            value = self.text_values.get(f'{i}.0', f'{i}.end')
            if value == '':
                continue
            values.append(value)
        return values

    def destroy(self):
        self.handle_button_cancel_button_1(None)
        return

# class end
