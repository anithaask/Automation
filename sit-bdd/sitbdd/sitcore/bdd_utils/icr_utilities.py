"""Utility functions for ICR communication in jag-bdd"""
from typing import Optional

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.exceptions import FuelException

from cfrfuelbdd.simpump_proxy import CSimPumpsProxy


def set_paper_low(simpumps: CSimPumpsProxy, pump_number: int):
    """Sets the 'receipt paper low' flag in the given ICR.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump number where receipt paper will be set to low.
    :raises FuelException: If 'receipt paper low' flag cannot be set
    """
    if not simpumps.set_printer_paper_low(pump_number, 1):
        raise FuelException(
            f"Failed to set receipt paper low on ICR {pump_number}: "
            f"{simpumps.Message}"
        )


def set_paper_out(simpumps: CSimPumpsProxy, pump_number: int):
    """Sets the 'receipt paper out' flag in the given ICR.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump number where receipt paper will be set to out.
    :raises FuelException: If 'receipt paper out' flag cannot be set
    """
    if not simpumps.set_printer_paper_out(pump_number, 1):
        raise FuelException(
            f"Failed to set receipt paper out on ICR {pump_number}: "
            f"{simpumps.Message}"
        )


def reset_paper(simpumps: CSimPumpsProxy, pump_number: int):
    """Resets the receipt paper flags (paper out and paper low) in the ICR.

    Resetting those flags is essentially "refilling" the receipt paper.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump number where receipt paper will be reset.
    :raises FuelException: If receipt paper flags cannot be reset"""
    if not simpumps.set_printer_paper_out(pump_number, 0):
        raise FuelException(
            f"Failed to reset receipt paper on ICR {pump_number}: "
            f"{simpumps.Message}"
        )

    if not simpumps.set_printer_paper_low(pump_number, 0):
        raise FuelException(
            f"Failed to reset receipt paper on ICR {pump_number}: "
            f"{simpumps.Message}"
        )
