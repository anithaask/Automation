import pytest

from sitbdd.sitcore.bdd_utils.foreign import f64_to_i64
from sitbdd.sitcore.bdd_utils.foreign import i64_to_f64


@pytest.mark.parametrize(
    ("start_value", "end_value"), [(0, 0), (3.45845952618e-313, 70000000107)]
)
def test__f64_to_i64(start_value, end_value):
    assert end_value == f64_to_i64(start_value)


@pytest.mark.parametrize(
    ("start_value", "end_value"), [(0, 0), (70000000107, 3.45845952618e-313)]
)
def test__i64_to_f64(start_value, end_value):
    assert end_value == i64_to_f64(start_value)
