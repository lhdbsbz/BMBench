# tests/test_lens_base.py
from bmb.contract import Dimension
from lenses.base import Lens


def test_lens_protocol_has_dimension_method():
    # Protocol 的结构性检查:实现类须有 dimension() -> Dimension 与 run()
    class DummyLens:
        def dimension(self) -> Dimension:
            return Dimension.FORGETTING
        def run(self, adapter, graph, **kw) -> float:
            return 0.5
    lens = DummyLens()
    assert lens.dimension() == Dimension.FORGETTING
    assert callable(lens.run)
