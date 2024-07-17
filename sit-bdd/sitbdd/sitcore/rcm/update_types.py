__all__ = ["UpdateTypes"]

import enum

class UpdateTypes(enum.Enum):
    FULL = 0
    CONFIG = 1
    EMPLOYEE_ONLY = 2
