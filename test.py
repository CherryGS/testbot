from typing import Optional
from pydantic import BaseModel


class test(BaseModel):
    id: int
    text: Optional[str] = None


def r(**kw):
    print(kw)


print(r(**test(id=1).dict(exclude_unset=True)))
