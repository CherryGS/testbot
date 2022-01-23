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


class PrimaryKeyNotEqualError(ModelError):
    """
    Model 与 sqlaOrm 定义的 PK 不相等时抛出
    """


class ColumnNotFoundError(ModelError):
    """
    找不到应该存在的列时抛出
    """


class ChangePrimaryKeyError(ModelError):
    """
    尝试构造修改 pk 的语句时抛出
    """
