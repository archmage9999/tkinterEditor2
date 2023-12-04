class SelectedComponent:

    def __init__(self, component, gui):
        self.component = component
        self.gui = gui

    @property
    def component_id(self):
        return self.component.winfo_name()

    def is_selected(self, component):
        return self.component is component

    def is_main_form(self):
        return self.gui.is_main_form(self.component)

    @property
    def component_name(self):
        return self.gui.operate_mgr.get_component_name(self.component_id)

