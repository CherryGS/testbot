class DatabaseError(Exception):
    pass


class DuplicateEngineError(DatabaseError):
    """
    重复引擎尝试添加时抛出
    """
