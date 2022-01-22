from ..exception import AnyUtilsError


class DatabaseError(AnyUtilsError):
    """"""


class DuplicateEngineError(DatabaseError):
    """
    重复引擎尝试添加时抛出
    """


class NotSupportedDatabaseError(DatabaseError):
    """
    引擎不支持时抛出
    """


class NotFoundEngineError(DatabaseError):
    """
    未根据标识找到引擎时抛出
    """


class ModelError(Exception):
    """"""


class PrimaryKeyNotEqualError(Exception):
    """
    Model 与 sqlaOrm 定义的 PK 不相等时抛出
    """
