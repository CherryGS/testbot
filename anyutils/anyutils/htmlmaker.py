import copy
from typing import Any, Iterator

from attrs import define, field
from typing_extensions import Self

from .extra_type import PropDict


@define
class ElementProp:
    title: str
    content: set[str]

    def output(self):
        s = (" ".join(sorted(self.content))).strip()
        if s:
            return f"{self.title}='{s}'"
        return s

    def cp(self):
        return copy.deepcopy(self)

    def __add__(self, e: str | Self):
        r = copy.deepcopy(self)
        r.__iadd__(e)
        return r

    def __sub__(self, e: str | Self):
        r = copy.deepcopy(self)
        r.__isub__(e)
        return r

    def __iadd__(self, e: str | Self):
        if isinstance(e, str):
            self.content.add(e)
        else:
            self.content |= e.content

        return self

    def __isub__(self, e: str | Self):
        if isinstance(e, str):
            self.content.remove(e)
        else:
            self.content -= e.content
        return self

    def __str__(self) -> str:
        return str(self.content)

    def __contains__(self, e: str) -> bool:
        return e in self.content

    def __iter__(self) -> Iterator:
        return iter(self.content)


@define
class DOMTree:
    """用来描述DOM树"""

    tag: str
    text: Any = field(converter=str, default="")
    c: list[Self] = field(factory=list)
    props: PropDict[ElementProp] = field(factory=lambda: PropDict[ElementProp]())
    father: Self | None = field(default=None)

    def free(self):
        """
        将该节点从其 father 上移除
        """
        if self.father is not None:
            self.father.c.remove(self)
            self.father = None
        return self

    def add(self, e: Self):
        """
        加入一个子节点 , 会将其从原先的 father 上移除
        """
        e.free()
        e.father = self
        self.c.append(e)
        return self

    def add_props(self, tag: str, e: set[str]):
        """
        添加属性的快捷方法
        """
        setattr(self.props, tag, ElementProp(tag, e))
        return self

    def cp(self):
        """深拷贝的快捷方法"""
        return copy.deepcopy(self)

    def _generate(self) -> tuple[str, str]:
        if self.tag == "br":
            return ("<br>", "")
        else:
            string = ""
            for i in self.props.items():
                if i[0] != "__orig_class__":
                    string += i[1].output() + " "
            return (
                f"<{self.tag} {string}>",
                f"</{self.tag}>",
            )

    def output(self) -> str:
        """输出当前的 DOMTree"""
        r = self._generate()
        return r[0] + "".join([i.output() for i in self.c]) + self.text + r[1]


if __name__ == "__main__":
    dt = DOMTree
    e = ElementProp

    body = dt("body")
    body.props._class = e("class", {"unit"})
    # for i in body.props.items():
    #     print(i)
    # print(body.props.values())
    print(body.output())
