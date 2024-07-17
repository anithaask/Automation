import os
from unittest import mock

import pytest

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.exceptions import FuelException
from sitbdd.sitcore.bdd_utils import icr_utilities

os.environ["TEMP"] = os.getcwd()  # Workaround for environment error with cfrfuelbdd


@pytest.fixture
def context():
    Context = mock.Mock()
    Context.pump_number = 1
    context.sit_product.simpumps = mock.Mock()
    context.sit_product.simpumps.Message = "Test Message"
    return Context


class TestICRUtilities:
    def test__set_paper_low__success(self, context: Context, pump_number: int):
        context.sit_product.simpumps.set_printer_paper_low.return_value = True
        icr_utilities.set_paper_low(context.sit_product.simpumps, pump_number)
        context.sit_product.simpumps.set_printer_paper_low.assert_called_with(1, 1)

    def test__set_paper_low__success_optional(self, context: Context):
        context.sit_product.simpumps.set_printer_paper_low.return_value = True
        icr_utilities.set_paper_low(context.sit_product.simpumps, 2)
        context.sit_product.simpumps.set_printer_paper_low.assert_called_with(2, 1)

    def test__set_paper_low__exception(self, context: Context, pump_number: int):
        context.sit_product.simpumps.set_printer_paper_low.return_value = False
        message = f"Failed to set receipt paper low on ICR 1: Test Message"
        with pytest.raises(FuelException, match=message):
            icr_utilities.set_paper_low(context.sit_product.simpumps, pump_number)

    def test__set_paper_out__success(self, context: Context, pump_number: int):
        context.sit_product.simpumps.set_printer_paper_out.return_value = True
        icr_utilities.set_paper_out(context.sit_product.simpumps, pump_number)
        context.sit_product.simpumps.set_printer_paper_out.assert_called_with(1, 1)

    def test__set_paper_out__success_optional(self, context: Context, pump_number: int):
        context.sit_product.simpumps.set_printer_paper_out.return_value = True
        icr_utilities.set_paper_out(context.sit_product.simpumps, 2)
        context.sit_product.simpumps.set_printer_paper_out.assert_called_with(2, 1)

    def test__set_paper_out__exception(self, context: Context, pump_number: int):
        context.sit_product.simpumps.set_printer_paper_out.return_value = False
        message = f"Failed to set receipt paper out on ICR 1: Test Message"
        with pytest.raises(FuelException, match=message):
            icr_utilities.set_paper_out(context.sit_product.simpumps, pump_number)

    def test__reset_paper__success(self, context: Context):
        context.sit_product.simpumps.set_printer_paper_low.return_value = True
        context.sit_product.simpumps.set_printer_paper_out.return_value = True
        icr_utilities.reset_paper(context)
        context.sit_product.simpumps.set_printer_paper_out.assert_called_with(1, 0)
        context.sit_product.simpumps.set_printer_paper_low.assert_called_with(1, 0)

    def test__reset_paper__success_optional(self, context: Context):
        context.sit_product.simpumps.set_printer_paper_low.return_value = True
        context.sit_product.simpumps.set_printer_paper_out.return_value = True
        icr_utilities.reset_paper(context, 2)
        context.sit_product.simpumps.set_printer_paper_out.assert_called_with(2, 0)
        context.sit_product.simpumps.set_printer_paper_low.assert_called_with(2, 0)

    def test__reset_paper__paper_out_exception(self, context: Context):
        context.sit_product.simpumps.set_printer_paper_low.return_value = True
        context.sit_product.simpumps.set_printer_paper_out.return_value = False
        message = f"Failed to reset receipt paper on ICR 1: Test Message"
        with pytest.raises(FuelException, match=message):
            icr_utilities.reset_paper(context)

    def test__reset_paper__paper_low_exception(self, context: Context):
        context.sit_product.simpumps.set_printer_paper_low.return_value = False
        context.sit_product.simpumps.set_printer_paper_out.return_value = True
        message = f"Failed to reset receipt paper on ICR 1: Test Message"
        with pytest.raises(FuelException, match=message):
            icr_utilities.reset_paper(context)
