class BaseException(Exception):
    pass


class IgnoreException(BaseException):
    pass


class RaiseException(BaseException):
    pass


class UnknownError(RaiseException):
    pass


class SourceNotFoundError(IgnoreException):
    pass
