class AnyUtilsError(Exception):
    pass


class Cooling(AnyUtilsError):
    """
    当冷却未完成时抛出

    Args:
        `Exception` : [description]
    """


from .database.exception import *
