__all__ = ["TankSimCommunicator"]

from sitbdd.sitcore.bdd_utils.http_communicator import HTTPCommunicator


class TankSimCommunicator(HTTPCommunicator):
    """This class is the communication layer between sitbdd and the tank simulator."""

    def __init__(self, hostname: str, port: int = None):
        """
        :param hostname: Hostname without protocol
        :param port: Port number
        """
        super().__init__(hostname, port)

    def get_tank_status(self, tank_num: int) -> bool:
        """Get tank online status.

        :param tank_num: Fuel tank to get status of.
        :return: True or False whether the given tank is online or not.
        """
        response = self._get(f"tank/{tank_num}/online")
        return response.get("online", None)

    def set_tank_online(self, tank_num: int):
        """Sets a specified fuel tank to online.

        :param tank_num: Fuel tank to set to online.
        """
        self._put(f"tank/{tank_num}/online", data="true")

    def set_tank_offline(self, tank_num: int) -> int:
        """Sets a specified fuel tank to offline.

        :param tank_num: Fuel tank to set to offline.
        :return: response status for given request.
        """
        self._put(f"tank/{tank_num}/online", data="false")
