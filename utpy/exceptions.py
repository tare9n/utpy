class InvalidUrlException(Exception):
    __module__ = 'utpy'
    def __init__(self):
        message = 'Url Is Not Valid.'
        super().__init__(message)