class InvalidUrlException(Exception):
    __module__ = 'utpy'
    def __init__(self):
        message = 'Url Is Not Valid.'
        super().__init__(message)


class SignatureCipher(Exception):
    __module__ = 'utpy'
    def __init__(self):
        message = 'This video has signatureCipher. We are working on it.'
        super().__init__(message)