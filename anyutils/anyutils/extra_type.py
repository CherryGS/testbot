from typing import Mapping, TypeVar
from typing_extensions import Self


T = TypeVar("T")


class PropDict(Mapping[str, T]):
    """可以通过属性直接访问值的字典 , 单层"""

    __data_data__: dict[str, T]

    def get(self, key: str, default=None):
        try:
            return super().__getattribute__("__data_data__")[key]
        except:
            return default

    def __init__(self, data: dict[str, T] | None = None):
        if data is None:
            data = {}
        object.__setattr__(self, "__data_data__", data)

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except:
            raise AttributeError

    def __getattr__(self, __name):
        """
        在原始属性不存在时 , 即 `__get_attribute__` 抛出 `AttributeError` 后 , 会用这个函数尝试获取属性

        此时会去掉第一个下划线 (如果是)
        """
        __name = __name if __name[0] != "_" else __name[1:]
        try:
            return super().__getattribute__("__data_data__")[__name]
        except:
            raise AttributeError(f"{__name}")

    def __setattr__(self, __name: str, __value: T):
        super().__getattribute__("__data_data__")[__name] = __value

    def __len__(self):
        return len(super().__getattribute__("__data_data__"))

    def __getitem__(self, __k):
        return super().__getattribute__("__data_data__")[__k]

    def __setitem__(self, __value, __k):
        r = super().__getattribute__("__data_data__")
        r[__k] = __value

    def __iter__(self):
        return iter(super().__getattribute__("__data_data__"))

    def __eq__(self, __o: object):
        try:
            return super().__getattribute__("__data_data__") == __o.__getattribute__(
                "__data_data__"
            )
        except AttributeError:
            return super().__eq__(__o)

    def __ne__(self, __o: object):
        return super().__getattribute__("__eq__")(__o) ^ True


# [ ]
class PropsDict(Mapping[str, T]):
    __data_data__: dict[str, Self]
    _value_value_: T | None

    def __init__(self, data: dict[str, Self] = dict()):
        print(id(data))
        super().__setattr__("__data_data__", data)

    def __len__(self):
        return len(super().__getattribute__("__data_data__"))

    def __getitem__(self, __k: str):
        return super().__getattribute__("__data_data__")[__k]

    def __iter__(self):
        return iter(super().__getattribute__("__data_data__"))


if __name__ == "__main__":

    dic = PropDict[int]()
    dic.r = 1
    dic.a = 1
    print(dic.values())
