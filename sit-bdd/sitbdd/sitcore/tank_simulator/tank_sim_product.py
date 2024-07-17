__all__ = ["TankSimCommunicator"]

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.tank_simulator.tank_sim_communicator import TankSimCommunicator

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class TankSimProduct:
    """This class is the communication layer between sitbdd and the tank simulator."""

    def __init__(self, hostname: str, port: int = None):
        """
        :param hostname: Hostname without protocol
        :param port: Port number
        """

        self._comm = TankSimCommunicator(hostname, port)

    def get_tank_status(self, tank_num: int) -> bool:
        """Get tank online status.

        :param tank_num: Fuel tank to get status of.
        :return: Response to this request.
        """
        response = self._comm.get_tank_status(tank_num)
        if response is None:
            raise ProductError("Tank simulator did not have requested field 'online' in its body.")
        return response

    def set_tank_online(self, tank_num: int) -> None:
        """Sets a specified fuel tank to online.

        :param tank_num: Fuel tank to set to online.
        """
        self._comm.set_tank_online(tank_num)

    def set_tank_offline(self, tank_num: int) -> None:
        """Sets a specified fuel tank to offline.

        :param tank_num: Fuel tank to set to offline.
        """
        self._comm.set_tank_offline(tank_num)
