import configparser


# 默认的configParser会强制转换大写为小写
class ToolConfigParser(configparser.ConfigParser):

    def __init__(self, defaults=None, file=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
        if file is not None:
            self.read(file, encoding="utf-8-sig")

    def optionxform(self, option_str):
        return option_str


