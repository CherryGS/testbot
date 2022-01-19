from typing import Optional
from pydantic import BaseModel


class test(BaseModel):
    id: int
    text: Optional[str] = None


def r(**kw):
    print(kw)


dic = {"res": 1}

print(r(**dic, res=2))
