import os
from typing import Any
from typing import Callable
from unittest import mock

import pytest
from behave.model import Table
from cfrpos.core.bdd_utils.errors import ProductError as POSProductError
from cfrpos.core.pos.user_interface import MenuFrame
from cfrpos.core.pos.user_interface import UiButton
from cfrpos.core.pos.user_interface import UiFrame

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils import utility

os.environ["TEMP"] = os.getcwd()  # Workaround for environment error with cfrfuelbdd

MENU_FRAME_NAME_MODULE = "cfrpos.core.pos.user_interface.MenuFrame.name"


@pytest.fixture
def poll():
    return mock.Mock()


@pytest.fixture
def sentinel():
    return mock.Mock()


@pytest.fixture
def context():
    Context = mock.Mock()
    Context.pump_number.return_value = 1
    context.sit_product.pos = mock.Mock()
    context.sit_product.fuel = mock.Mock()
    context.sit_product.simpumps = mock.Mock()
    context.sit_product.pos.control = mock.Mock()
    return Context


@pytest.fixture
def menu_frame():
    button = UiButton()
    button._name = "foo"
    child = UiFrame()
    child._buttons = [button]

    parent = MenuFrame()
    parent._instance_id = 1
    parent.has_done = mock.Mock()
    parent._frames = [child]

    return parent


class TestUtility:
    def test__wait_until__first_try(
        self, poll: Callable[[], Any], sentinel: Callable[[Any], Any]
    ):
        poll.return_value = "test"
        sentinel.return_value = True
        assert utility.wait_until(poll, sentinel, 2, 0.1) == ("test", True)
        sentinel.assert_called_once_with("test")

    def test__wait_until__last_try(
        self, poll: Callable[[], Any], sentinel: Callable[[Any], Any]
    ):
        poll.side_effect = ["test1", "test2", "test3"]
        sentinel.side_effect = [False, True]
        assert utility.wait_until(poll, sentinel, 2, 0.1) == ("test3", True)
        sentinel.assert_has_calls([mock.call("test2"), mock.call("test3")])
        assert poll.call_count == 3

    def test__wait_until__failure(
        self, poll: Callable[[], Any], sentinel: Callable[[Any], Any]
    ):
        poll.side_effect = ["test1", "test2", "test3"]
        sentinel.return_value = False
        assert utility.wait_until(poll, sentinel, 2, 0.1) == ("test3", False)
        sentinel.assert_has_calls([mock.call("test2"), mock.call("test3")])
        assert poll.call_count == 3

    def test__suppress_until__success(self):
        fn = mock.Mock()
        fn.return_value = None
        ret = utility.suppress_until(fn, Exception)
        fn.assert_has_calls([mock.call()])
        assert fn.call_count == 1
        assert ret is None

    def test__suppress_until__failure(self):
        fn = mock.Mock()
        fn.side_effect = Exception, Exception
        with pytest.raises(Exception):
            utility.suppress_until(fn, Exception)
        fn.assert_has_calls([mock.call()])
        assert fn.call_count == 2

    def test__wait_for_frame_name__first_try(self, context: Context):
        with mock.patch(
            MENU_FRAME_NAME_MODULE, new_callable=mock.PropertyMock
        ) as mock_frame_name:
            mock_frame_name.return_value = "test"
            context.sit_product.pos.control.get_menu_frame.return_value = MenuFrame()
            frame = utility.wait_for_frame_name(context.sit_product.pos, "test", 1)
            assert mock_frame_name.call_count == 1
            assert frame.name == "test"
            assert context.sit_product.pos.control.get_menu_frame.call_count == 2

    def test__wait_for_frame_name__last_try(self, context: Context):
        with mock.patch(
            MENU_FRAME_NAME_MODULE, new_callable=mock.PropertyMock
        ) as mock_frame_name:
            mock_frame_name.side_effect = ["fail", "pass", "done"]
            context.sit_product.pos.control.get_menu_frame.return_value = MenuFrame()
            frame = utility.wait_for_frame_name(context.sit_product.pos, "pass", 1)
            assert mock_frame_name.call_count == 2
            assert frame.name == "done"
            assert context.sit_product.pos.control.get_menu_frame.call_count == 3

    def test__wait_for_frame_name__failure(self, context: Context):
        with mock.patch(
            MENU_FRAME_NAME_MODULE, new_callable=mock.PropertyMock
        ) as mock_frame_name:
            mock_frame_name.return_value = "fail"
            context.sit_product.pos.control.get_menu_frame.return_value = MenuFrame()
            with pytest.raises(
                ProductError, match='Timed out waiting for frame "pass"'
            ):
                utility.wait_for_frame_name(context.sit_product.pos, "pass", 1)
            assert context.sit_product.pos.control.get_menu_frame.call_count == 3

    def test__get_pump_state_on_pos__success(self, context: Context):
        context.sit_product.pos._control._comm.get_frame.return_value = {
            "Frame": {"Pumps": [{"Name": "pump-1", "State": "test"}]}
        }
        pump_state = utility.get_pump_state_on_pos(context.sit_product.pos, 1)
        assert pump_state == "test"

    def test__get_pump_state_on_pos__failure(self, context: Context):
        with pytest.raises(
            ProductError, match="Pump 2 was not found within fuelpumps frame."
        ):
            context.sit_product.pos._control._comm.get_frame.return_value = {
                "Frame": {"Pumps": [{"Name": "pump-1", "State": "test"}]}
            }
            pump_state = utility.get_pump_state_on_pos(context.sit_product.pos, 2)
            assert pump_state is None

    def test__wait_for_pump_state_on_pos__first_try(self, context: Context):
        context.sit_product.pos._control._comm.get_frame.return_value = {
            "Frame": {"Pumps": [{"Name": "pump-1", "State": "test"}]}
        }
        utility.wait_for_pump_state_on_pos(context.sit_product.pos, 1, "test", 1)
        context.sit_product.pos._control._comm.get_frame.assert_has_calls(
            [mock.call("fuelpumps")] * 2
        )
        assert context.sit_product.pos._control._comm.get_frame.call_count == 2

    def test__wait_for_pump_state_on_pos__last_try(self, context: Context):
        context.sit_product.pos._control._comm.get_frame.side_effect = [
            *([{"Frame": {"Pumps": [{"Name": "pump-1", "State": "fail"}]}}] * 10),
            {"Frame": {"Pumps": [{"Name": "pump-1", "State": "pass"}]}},
        ]
        utility.wait_for_pump_state_on_pos(context.sit_product.pos, 1, "pass", 1)
        context.sit_product.pos._control._comm.get_frame.assert_has_calls(
            [mock.call("fuelpumps")] * 11
        )
        assert context.sit_product.pos._control._comm.get_frame.call_count == 11

    def test__wait_for_pump_state_on_pos__failure(self, context: Context):
        context.sit_product.pos._control._comm.get_frame.return_value = {
            "Frame": {"Pumps": [{"Name": "pump-1", "State": "fail"}]}
        }
        with pytest.raises(
            ProductError,
            match='Timed out waiting for pump state "pass". Got "fail" instead.',
        ):
            utility.wait_for_pump_state_on_pos(context.sit_product.pos, 1, "pass", timeout=1)
        context.sit_product.pos._control._comm.get_frame.assert_has_calls(
            [mock.call("fuelpumps")] * 11
        )
        assert context.sit_product.pos._control._comm.get_frame.call_count == 11

    def test__wait_for_pump_state_on_fc__first_try(self, context: Context):
        pump_number = 1
        context.sit_product.fuel.get_pump_status.return_value = "test"
        utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "test", 1)
        context.sit_product.fuel.get_pump_status.assert_has_calls(
            [mock.call(pump_number)] * 2
        )
        assert context.sit_product.fuel.get_pump_status.call_count == 2

    def test__wait_for_pump_state_on_fc__last_try(self, context: Context):
        pump_number = 1
        context.sit_product.fuel.get_pump_status.side_effect = [*(["fail"] * 10), "pass"]
        utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "pass", 1)
        context.sit_product.fuel.get_pump_status.assert_has_calls(
            [mock.call(pump_number)] * 11
        )
        assert context.sit_product.fuel.get_pump_status.call_count == 11

    def test__wait_for_pump_state_on_fc__failure(self, context: Context):
        pump_number = 1
        context.sit_product.fuel.get_pump_status.return_value = "fail"
        with pytest.raises(
            ProductError,
            match='Expected pump 1\'s state to be "pass" within 1 seconds, '
            'got "fail" instead.',
        ):
            utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "pass", 1)
        context.sit_product.fuel.get_pump_status.assert_has_calls(
            [mock.call(pump_number)] * 11
        )
        assert context.sit_product.fuel.get_pump_status.call_count == 11

    def test__wait_for_pump_dispense__success(self, context: Context):
        pump_number = 1
        context.sit_product.simpumps.get_current_money_display.side_effect = [
            "0",
            "1000",
            "2000",
        ]
        utility.wait_for_pump_dispense(context.sit_product.simpumps, pump_number, 20, 2)
        context.sit_product.simpumps.get_current_money_display.assert_has_calls(
            [mock.call(pump_number)] * 3
        )
        assert context.sit_product.simpumps.get_current_money_display.call_count == 3

    def test__wait_for_pump_dispense__failure(self, context: Context):
        pump_number = 1
        context.sit_product.simpumps.get_current_money_display.side_effect = [
            "0",
            "500",
            "1000",
        ]
        with pytest.raises(
            ProductError,
            match="Expected pump 1 to dispense \\$20 within 2 seconds, "
            "dispensed \\$10.0 instead.",
        ):
            utility.wait_for_pump_dispense(context.sit_product.simpumps, pump_number, 20, 2)
        context.sit_product.simpumps.get_current_money_display.assert_has_calls(
            [mock.call(pump_number)] * 3
        )
        assert context.sit_product.simpumps.get_current_money_display.call_count == 3

    def test__wait_until_sc_pubsub_stops_publishing__success(self, context: Context):
        context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_messages.return_value = None
        utility.wait_until_sc_pubsub_stops_publishing(
            context.sit_product.sc, "A", stop_duration=1, attempts=2
        )
        context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_messages.assert_has_calls(
            [mock.call("A", timeout=1)]
        )

    def test__wait_until_sc_pubsub_stops_publishing__timeout(self, context: Context):
        msg = dict(message=[1])
        context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_messages.return_value = msg
        with pytest.raises(ProductError):
            utility.wait_until_sc_pubsub_stops_publishing(
                context.sit_product.sc, "A", stop_duration=1, attempts=2
            )
        context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_messages.assert_has_calls(
            [mock.call("A", timeout=1)] * 2
        )

    def test__require_table_headings__success(self, context: Context):
        context.table = Table(headings=["a", "b"])
        utility.require_table_headings(context.table, "a", "b")

    def test__require_table_headings__empty(self, context: Context):
        context.table = None
        with pytest.raises(
            ValueError,
            match=r"This step requires a context table\.",
        ):
            utility.require_table_headings(context.table, "a", "b")

    def test__require_table_headings__unordered(self, context: Context):
        context.table = Table(headings=["b", "a"])
        with pytest.raises(
            ValueError,
            match="This step requires context table headings "
            r"\('a', 'b'\), got \('b', 'a'\) instead\.",
        ):
            utility.require_table_headings(context.table, "a", "b")

    def test__require_table_headings__unexpected(self, context: Context):
        context.table = Table(headings=["x", "y"])
        with pytest.raises(
            ValueError,
            match="This step requires context table headings "
            r"\('a', 'b'\), got \('x', 'y'\) instead\.",
        ):
            utility.require_table_headings(context.table, "a", "b")

    def test__require_table_headings__extras(self, context: Context):
        context.table = Table(headings=["a", "b", "x", "y"])
        with pytest.raises(
            ValueError,
            match="This step requires context table headings "
            r"\('a', 'b'\), got \('a', 'b', 'x', 'y'\) instead\.",
        ):
            utility.require_table_headings(context.table, "a", "b")

    def test__wait_until_pos_offline__online_offline(self, context: Context):
        context.sit_product.pos.control.is_active.side_effect = [True, False]
        utility.wait_until_pos_offline(context.sit_product.pos, 2, 0)
        assert context.sit_product.pos.control.is_active.call_count == 2

    def test__wait_until_pos_offline__online(self, context: Context):
        context.sit_product.pos.control.is_active.return_value = True
        with pytest.raises(
            POSProductError,
            match=r"Failed to wait for POS to go offline within 0.2 seconds\.",
        ):
            utility.wait_until_pos_offline(context.sit_product.pos, 2, 0.1)

    def test__wait_until_pos_offline__offline(self, context: Context):
        context.sit_product.pos.control.is_active.return_value = False
        utility.wait_until_pos_offline(context.sit_product.pos, 1, 0)
        assert context.sit_product.pos.control.is_active.call_count == 2

    def test__wait_for_any_pos_menu_frame__success(self, context: Context):
        context.sit_product.pos.control.get_menu_frame.return_value = MenuFrame()
        utility.wait_for_any_pos_menu_frame(context.sit_product.pos, attempts=1, delay=0)
        assert context.sit_product.pos.control.get_menu_frame.call_count == 2

    def test__wait_for_any_pos_menu_frame__failed(self, context: Context):
        context.sit_product.pos.control.get_menu_frame.return_value = None
        with pytest.raises(
            POSProductError,
            match=r"Failed to wait for POS to return a menu frame within 0 seconds\.",
        ):
            utility.wait_for_any_pos_menu_frame(context.sit_product.pos, attempts=1, delay=0)
