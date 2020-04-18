class TagNotFound(BaseException):
    def __init__(self,tag=''):
        self.tag = tag

    def __str__(self):
        return f'Tag {self.tag} not found'

