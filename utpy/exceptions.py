class InvalidUrlException(Exception):
    __module__ = 'utpy'
    def __init__(self):
        message = 'Url Is Not Valid.'
        super().__init__(message)

class FailedToGetContent(Exception):
    __module__ = 'utpy'
    def __init__(self):
        message = 'Content Not found. Check url and internet connection and try again'
        super().__init__(message)