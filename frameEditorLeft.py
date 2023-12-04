import os
from scrollTreeview import ScrollTreeView
from dataMgr import DataMgr
from project import File


class FrameEditorLeft(ScrollTreeView):

    def __init__(self, master=None, cnf={}, **kw):
        ScrollTreeView.__init__(self, master, cnf, **kw)

    def on_init(self):
        self.bind('<Double-1>', self.handle_double_1)

    @staticmethod
    def handle_double_1(event):
        """
        双击事件
        :param event: event
        :return: None
        """
        index = event.widget.focus()
        file = event.widget.get_data_by_index(index)
        if not file or file.is_dir:
            return
        DataMgr().get_editor().show_file(file)

    def refresh_tree(self, project_path, show_file_name=""):
        """
        刷新tree
        :param project_path: 项目路径
        :param show_file_name: 要显示的文件
        :return: None
        """
        self.delete_node(project_path)
        project_name = os.path.basename(project_path)
        self.add_root_node(project_path, project_name, File(project_path, project_path, project_name))

        custom_frame_list = DataMgr().get_custom_frame_list()
        for root, dirs, files in os.walk(project_path, topdown=True, followlinks=True):
            for folder in [folder for folder in dirs if folder.startswith((".", "__"))]:
                dirs.remove(folder)

            for folder in dirs:
                dir_path = os.path.join(root, folder)
                self.add_node(root, 'end', dir_path, folder, File(project_path, dir_path, folder))

            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.add_node(root, 'end', file_path, file_name, File(project_path, file_path, file_name))
                if not file_name.startswith("form") and file_name not in custom_frame_list:
                    continue
                gui_name = f'{file_name}.gui'
                gui_path = file_path + '.gui'
                file = File(project_path, gui_path, gui_name)
                self.add_node(root, 'end', gui_path, gui_name, file)
                if show_file_name == "" or show_file_name == file_name:
                    self.selection_set(gui_path)
                    DataMgr().get_editor().show_file(file)

        self.open_all_node(project_path)

