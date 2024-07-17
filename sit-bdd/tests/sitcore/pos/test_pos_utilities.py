from unittest import mock

import pytest
from cfrsmtaskman.core.bdd_utils.errors import NetworkError

from behave.runner import Context
from sitbdd.sitcore.bdd_utils import pos_utilities


def frame():
    child_frame_button = mock.Mock()
    child_frame_button.name = "child-frame-button"

    child_frame = mock.Mock()
    child_frame.buttons = [child_frame_button]

    present_button = mock.Mock()
    present_button.name = "present-button"

    menu_frame = mock.Mock()
    menu_frame.buttons = [present_button]
    menu_frame.frames = [child_frame]
    return menu_frame


@pytest.fixture
def context():
    Context = mock.Mock()
    context.sit_product.pos.control.get_menu_frame = frame
    return Context


class TestPosutilities:
    def test__set_roof_bar_frame__unknown_frame_name(self, context: Context):
        with pytest.raises(
            ValueError,
            match=r'Unknown frame name "foo"\. '
            r"Must be one of \('alerts', 'hotkeys', 'apps'\)\.",
        ):
            pos_utilities.set_roof_bar_frame(context.sit_product.smtaskman, "foo")

    def test__set_roof_bar_frame__in_frame_first_page(self, context: Context):
        context.sit_product.smtaskman.get_frame_content.side_effect = [
            {"FrameName": "alerts", "Page": {"Number": 1}}
        ]
        assert pos_utilities.set_roof_bar_frame(context.sit_product.smtaskman, "alerts") is None
        assert context.sit_product.smtaskman.get_frame_content.call_count == 1
        assert context.sit_product.smtaskman.switch_content.call_count == 0

    def test__set_roof_bar_frame__in_frame_not_first_page(self, context: Context):
        context.sit_product.smtaskman.get_frame_content.side_effect = [
            {"FrameName": "alerts", "Page": {"Number": 2}},
            {"FrameName": "hotkeys"},
            {"FrameName": "apps"},
            {"FrameName": "alerts", "Page": {"Number": 1}},
        ]
        assert pos_utilities.set_roof_bar_frame(context.sit_product.smtaskman, "alerts") is None
        assert context.sit_product.smtaskman.get_frame_content.call_count == 4
        assert context.sit_product.smtaskman.switch_content.call_count == 3

    def test__set_roof_bar_frame__not_in_frame(self, context: Context):
        context.sit_product.smtaskman.get_frame_content.side_effect = [
            {"FrameName": "hotkeys"},
            {"FrameName": "apps"},
            {"FrameName": "alerts", "Page": {"Number": 1}},
        ]
        assert pos_utilities.set_roof_bar_frame(context.sit_product.smtaskman, "alerts") is None
        assert context.sit_product.smtaskman.get_frame_content.call_count == 3
        assert context.sit_product.smtaskman.switch_content.call_count == 2

    def test__roof_bar_pages__single_page(self, context: Context):
        context.sit_product.smtaskman.get_frame_content.side_effect = [{"Page": {"Number": 1}}]
        context.sit_product.smtaskman.switch_content_page.side_effect = [NetworkError("")]
        pages = pos_utilities.roof_bar_pages(context.sit_product.smtaskman)
        assert next(pages) == {"Page": {"Number": 1}}
        with pytest.raises(StopIteration):
            next(pages)
        assert context.sit_product.smtaskman.get_frame_content.call_count == 1

    def test__roof_bar_pages__multi_page(self, context: Context):
        expected = [
            {"Page": {"Number": 1}},
            {"Page": {"Number": 2}},
            {"Page": {"Number": 1}},
        ]
        context.sit_product.smtaskman.get_frame_content.side_effect = expected
        pages = pos_utilities.roof_bar_pages(context.sit_product.smtaskman)
        assert next(pages) == expected[0]
        assert next(pages) == expected[1]
        with pytest.raises(StopIteration):
            next(pages)
        assert context.sit_product.smtaskman.get_frame_content.call_count == 3

    def test__roof_bar_pages__multi_page_last_page(self, context: Context):
        expected = [{"Page": {"Number": 2}}, {"Page": {"Number": 1}}]
        context.sit_product.smtaskman.get_frame_content.side_effect = expected
        pages = pos_utilities.roof_bar_pages(context.sit_product.smtaskman)
        assert next(pages) == expected[0]
        with pytest.raises(StopIteration):
            next(pages)
        assert context.sit_product.smtaskman.get_frame_content.call_count == 2

    def test__roof_bar_pages__multi_page_stale_page(self, context: Context):
        context.sit_product.smtaskman.get_frame_content.side_effect = [{"Page": {"Number": 2}}]
        context.sit_product.smtaskman.switch_content_page.side_effect = [NetworkError("")]
        pages = pos_utilities.roof_bar_pages(context.sit_product.smtaskman)
        assert next(pages) == {"Page": {"Number": 2}}
        with pytest.raises(StopIteration):
            next(pages)
        assert context.sit_product.smtaskman.get_frame_content.call_count == 1

    def test__wait_for_roof_bar_button_presence__single_page_present(
        self, context: Context
    ):
        expected = {"foo": "bar"}
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [{"Page": {"Number": 1}, "Buttons": [expected]}]
        )
        button = pos_utilities.wait_for_roof_bar_button_presence(
            context.sit_product.smtaskman, expected, attempts=1, delay=0
        )
        assert button == expected

    def test__wait_for_roof_bar_button_presence__multi_page_first_page_present(
        self, context: Context
    ):
        expected = {"foo": "bar"}
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [
                {"Page": {"Number": 1}, "Buttons": [expected]},
                {"Page": {"Number": 2}, "Buttons": [{"bar": "baz"}]},
            ]
        )
        button = pos_utilities.wait_for_roof_bar_button_presence(
            context.sit_product.smtaskman, expected, attempts=1, delay=0
        )
        assert button == expected

    def test__wait_for_roof_bar_button_presence__multi_page_next_page_present(
        self, context: Context
    ):
        expected = {"bar": "baz"}
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [
                {"Page": {"Number": 1}, "Buttons": [{"foo": "bar"}]},
                {"Page": {"Number": 2}, "Buttons": [expected]},
            ]
        )
        button = pos_utilities.wait_for_roof_bar_button_presence(
            context.sit_product.smtaskman, expected, attempts=1, delay=0
        )
        assert button == expected

    def test__wait_for_roof_bar_button_presence__single_page_absent(
        self, context: Context
    ):
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [{"Page": {"Number": 1}, "Buttons": [{"foo": "bar"}]}]
        )
        button = pos_utilities.wait_for_roof_bar_button_presence(
            context.sit_product.smtaskman, {"bar": "baz"}, attempts=1, delay=0
        )
        assert button is None

    def test__wait_for_roof_bar_button_presence__multi_page_absent(
        self, context: Context
    ):
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [
                {"Page": {"Number": 1}, "Buttons": [{"foo": "bar"}]},
                {"Page": {"Number": 2}, "Buttons": [{"bar": "baz"}]},
            ]
        )
        button = pos_utilities.wait_for_roof_bar_button_presence(
            context.sit_product.smtaskman, {"baz": "qux"}, attempts=1, delay=0
        )
        assert button is None

    def test__wait_for_roof_bar_button_absence__single_page_absent(
        self, context: Context
    ):
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [{"Page": {"Number": 1}, "Buttons": [{"foo": "bar"}]}]
        )
        button = pos_utilities.wait_for_roof_bar_button_absence(
            context.sit_product.smtaskman, {"bar": "baz"}, attempts=1, delay=0
        )
        assert button is None

    def test__wait_for_roof_bar_button_absence__single_page_present(
        self, context: Context
    ):
        expected = {"foo": "bar"}
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [{"Page": {"Number": 1}, "Buttons": [expected]}]
        )
        button = pos_utilities.wait_for_roof_bar_button_absence(
            context.sit_product.smtaskman, expected, attempts=1, delay=0
        )
        assert button == expected

    def test__wait_for_roof_bar_button_absence__multi_page_absent(
        self, context: Context
    ):
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [
                {"Page": {"Number": 1}, "Buttons": [{"foo": "bar"}]},
                {"Page": {"Number": 2}, "Buttons": [{"bar": "baz"}]},
            ]
        )
        button = pos_utilities.wait_for_roof_bar_button_absence(
            context.sit_product.smtaskman, {"baz": "qux"}, attempts=1, delay=0
        )
        assert button is None

    def test__wait_for_roof_bar_button_absence__multi_page_first_page_present(
        self, context: Context
    ):
        expected = {"foo": "bar"}
        pos_utilities.roof_bar_pages = mock.Mock()
        pos_utilities.roof_bar_pages.return_value = iter(
            [
                {"Page": {"Number": 1}, "Buttons": [expected]},
                {"Page": {"Number": 2}, "Buttons": [{"bar": "baz"}]},
            ]
        )
        button = pos_utilities.wait_for_roof_bar_button_absence(
            context.sit_product.smtaskman, expected, attempts=1, delay=0
        )
        assert button == expected
