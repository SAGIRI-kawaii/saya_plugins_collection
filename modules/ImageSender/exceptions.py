class ConfigurationNotFound(Exception):
    """ 未配置config.json """
    pass


class ImagePathEmpty(Exception):
    """ 文件夹下没有图片 """
    pass
