from pathlib import Path
from anyutils.database import sqla
import pytest


@pytest.fixture()
def reg():
    return sqla.RegEngine()


class TestRegEngine:
    def test_add_by_link(self, tmp_path: Path, reg: sqla.RegEngine):
        reg.add("memory", "sqlite+aiosqlite:///:memory:")
        reg.add("file", f"sqlite+aiosqlite:///{tmp_path}/file.sqlite")
        with pytest.raises(sqla.DuplicateEngineError):
            reg.add("memory", "sqlite+aiosqlite:///:memory:")

    def test_add_one(self, reg: sqla.RegEngine):
        reg.add("memory", "sqlite+aiosqlite:///:memory:")
        reg.init()

        r = reg._Engine.pop("memory")
        reg.add_one("memory", r)

        with pytest.raises(sqla.DuplicateEngineError):
            reg.add_one("memory", r)

        r.dialect.name = "123"
        with pytest.raises(sqla.NotSupportedDatabaseError):
            reg.add_one("123", r)

    def test_init_engine(self, reg: sqla.RegEngine):
        reg.add("memory", "sqlite+aiosqlite:///:memory:")
        reg.init()

    def test_init_engine_raise(self, reg: sqla.RegEngine):
        reg.add("memory", "sqlite+aiosqlite:///:memory:")
        reg._Engine["memory"] = 1  # type: ignore
        with pytest.raises(sqla.DuplicateEngineError):
            reg.init()

    def test_get_engine(self, reg: sqla.RegEngine):
        reg.add("memory", "sqlite+aiosqlite:///:memory:")
        reg.get("memory")
        with pytest.raises(sqla.NotFoundEngineError):
            reg.get("12345")
        reg._Engine["123"] = 4  # type: ignore
        with pytest.raises(TypeError):
            reg.get("123")
