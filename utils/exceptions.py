class AppBaseException(RuntimeError):
    def __init__(self, args):
        self.args = args

class AppServiceException(AppBaseException):
    def __init__(self, args):
        self.args = args

class AppViewException(AppBaseException):
    def __init__(self, args):
        self.args = args

