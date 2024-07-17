"""Custom exceptions for SIT framework."""


class FuelException(Exception):
    """Exception related to fuel behavior with jag-bdd framework.

    Example:
    >>>raise FuelException("Failed to set pump speed")
    """
