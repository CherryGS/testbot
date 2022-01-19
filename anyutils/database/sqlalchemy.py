from typing import Any, List, Tuple, Any
from functools import lru_cache


@lru_cache(maxsize=None)
async def anywhere(stmt, data: Tuple[Tuple[Any, Any], ...]):
    for i in data:
        if i[1] is not None:
            stmt = stmt.where(i[0] == i[1])
    return stmt
