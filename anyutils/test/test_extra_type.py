import pytest
from anyutils import extra_type as ts
from hypothesis import given, assume
from hypothesis.strategies import integers, text


class TestPropDict:
    @pytest.mark.skip
    @given(a=integers(), b=text())
    def test_as_normal_dict(self, a: int, b: str):
        assume(b)
        dic: dict[str, int] = dict()
        dic_ = ts.PropDict[int]()
        dic[b] = a
        dic_[b] = a
        print(dic_[b], dic[b])
        assert dic_[b] == dic[b]
        assert dic_.get(b) == dic.get(b)
        assert dic_ != dic
