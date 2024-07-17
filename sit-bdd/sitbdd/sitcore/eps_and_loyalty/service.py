import time
import bs4
from typing import Union, List

from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.bdd_utils.registry_handler import RegistryHandler
from sitbdd.sitcore.bdd_utils.radviewer import RadViewerScript
from sitbdd.sitcore.eps_and_loyalty.pmi_communicator import PMICommunicator

logger = get_sit_logger()

@wrap_all_methods_with_log_trace
class Service:

    HOST_SIM_REGISTRY_PATH = "Software\\RadiantSystems\\HostSimulator\\"
    HOST_SIM_SERVICE_NAME = "RSHostSimulator"

    def __init__(
        self,
        pmi_hostname: str,
        pmi_port: int,
        name: str,
        registry_path: str,
        service_name: str,
        networks: List[str],
    ):

        self.name = name
        self.registry_path = registry_path
        self.service_name = service_name
        self.networks = networks
        self.selected_network = networks[0]

        # TODO: uncomment once PMI has been reintroduced - RPOS-60082
        # self._pmi = PMICommunicator(pmi_hostname, pmi_port, self.name)
        self.pmi_hostname = pmi_hostname

        self.registry_handler = RegistryHandler()
        self.registry_handler_host_sim = RegistryHandler()

    def get_nvps(
        self,
        transaction_number: int,
        nvp_list: List[str],
        global_nvp_list: List[str] = None,
        remove_special_characters: bool = False,
    ) -> Union[dict, None]:
        """
        Attempt to retrieve the NVPs in nvp_list from
        desired transaction or global NVPs in global_nvp_list from the service.
        :param int transaction_number: Transaction number to
            retrieve NVPs from, None if retrieving global NVPs
        :param list[str] nvp_list: NVPs to retrieve
        :param list[str] global_nvp_list: Global NVPs to retrieve
        :param bool remove_special_characters: If True, removes file,
            group, record, and unit separators from the response prior to parsing.
        :return: List of NVPs and their values from the service or None
        :rtype: dict or None
        """
        requested_operation = "Get"
        
        message_soup = bs4.BeautifulSoup(
            self._pmi.build_pmi_request_message_header(operation=requested_operation),
            "xml",
        )

        for nvp in nvp_list:
            nvp_tag = message_soup.new_tag("NVP", Name=nvp)
            message_soup.Message.append(nvp_tag)

        if global_nvp_list is not None:
            for nvp in global_nvp_list:
                nvp_tag = message_soup.new_tag("NVP", Name=nvp, IsGlobal="YES")
                message_soup.Message.append(nvp_tag)

        if transaction_number is not None:
            message_soup.Message[
                self._pmi.MESSAGE_ATT_TRANSACTION_NUMBER
            ] = transaction_number

        result = self._pmi._communicate(str(message_soup.Message))
        parsed_response = self._pmi.parse_response(
            result, requested_operation, remove_special_characters
        )

        if parsed_response is not None:
            result_soup = bs4.BeautifulSoup(parsed_response, "xml")
            nvp_list_result = result_soup.Message.find_all("NVP")
            data = {}
            for nvp in nvp_list_result:
                data[nvp["Name"]] = nvp["Value"]
            return data
        else:
            return None

    def get_global_nvps(self, global_nvp_list: List[str]) -> Union[dict, None]:
        """
        Attempt to retrieve the global NVPs in global_nvp_list from the service
        :param list[str] global_nvp_list: Global NVPs to retrieve
        :return: List of NVPs and their values from the service or None
        :rtype: dict or None
        """
        return self.get_nvps(None, [], global_nvp_list)

    def get_registry_value(self, sub_path: str, name: str) -> Union[str, None]:
        """
        Attempt to find specified key under the service's registry path
        :param str sub_path: Subpath to the desired key within the service's registry path
            Can be an empty string to look under the network, also known as global registry values
        :param str name: Name of the desired key
        :return: String of the registry value. Will raise WindowsError
            if something goes wrong
        :rtype: str, None
        """
        value = self.registry_handler.get_registry_value(
            self.registry_path + sub_path,
            name,
        )

        return value

    def set_registry_value(
        self,
        sub_path: str,
        name: str,
        value: Union[str,int],
        reg_type: Union[int,None] = None
    ) -> None:
        """
        Sets the desired registry key under the service's registry path to the given value.
        :param str sub_path: Subpath to the desired key within the service's registry path
        :param str name: Name of the desired key
        :param str/int value: Desired value to set the key to
        :param int reg_type: Integer value representing the type of registry value it is
            or None for the value representing REG_SZ by default
        :return: None, will raise WindowsError if something goes wrong
        """
        self.registry_handler.set_registry_value(
            self.registry_path + sub_path,
            name,
            value,
            reg_type=reg_type,
        )

    def create_registry_key(self, path: str, key: str) -> None:
        """
        Attempt to create the desired registry key of the service
        :param str sub_path: Subpath to the desired key within the service's registry path
        :param str name: Name of the desired key
        :return: None
        """
        self.registry_handler.create_registry_key(self.registry_path + path, key)

    def delete_registry_value(self, sub_path: str, name: str) -> None:
        """
        Attempt to delete the desired registry value of the service
        :param str sub_path: Subpath to the desired key within the service's registry path
        :param str name: Name of the desired value
        :return: None
        """
        self.registry_handler.delete_registry_value(
            self.registry_path + sub_path,
            name,
        )

    def get_registry_value_host_simulator(self, sub_path: str, name: str) -> str:
        """
        Gets the desired registry key for a host simulator.
        :param str sub_path: Subpath to the desired key within the host simulator's registry path
        :param str name: Name of the desired key
        :return: str, will raise FileNotFoundError if something goes wrong
        """
        value = self.registry_handler_host_sim.get_registry_value(
            self.HOST_SIM_REGISTRY_PATH + self.selected_network + "\\" + sub_path,
            name,
        )
        return value

    def create_registry_key_host_simulator(self, path: str, key: str) -> None:
        """
        Attempt to create the desired registry key for a host simulator.
        :param str sub_path: Subpath to the desired key within the service's registry path
        :param str name: Name of the desired key
        :return: None
        """
        self.registry_handler.create_registry_key(self.HOST_SIM_REGISTRY_PATH + self.selected_network + "\\" +  path, key)

    def set_registry_value_host_simulator(self,
        sub_path: str,
        name: str,
        value: Union[str,int],
        reg_type: Union[int,None] = None,
    ) -> None:
        """
        Sets the desired registry key for a host simulator to the given value.
        :param str sub_path: Subpath to the desired key within the host simulator's registry path
        :param str name: Name of the desired key
        :param str value: Desired value to set the key to
        :param int reg_type: Integer value representing the type of registry value it is
            or None for the value representing REG_SZ by default
        :return: None, will raise WindowsError if something goes wrong
        """
        self.registry_handler_host_sim.set_registry_value(
            self.HOST_SIM_REGISTRY_PATH + self.selected_network + "\\" + sub_path,
            name,
            value,
            reg_type=reg_type,
        )

    def delete_registry_value_host_simulator(self, sub_path: str, name: str) -> None:
        """
        Deletes the desired registry value for a host simulator
        :param str sub_path: Subpath to the desired key within the host simulator's registry path
        :param str name: Name of the desired value
        :return: None, will raise WindowsError if something goes wrong
        """
        self.registry_handler_host_sim.delete_registry_value(
            self.HOST_SIM_REGISTRY_PATH + self.selected_network + "\\" + sub_path,
            name,
        )

    def delete_all_registry_values_host_simulator(self, sub_path: str) -> None:
        """
        Deletes all registry values in a given key under host simulator registries
        :param str sub_path: Subpath to the desired key within the host simulator's registry path
        :return: None, will raise WindowsError if something goes wrong
        """
        self.registry_handler.delete_all_registry_values(
            self.HOST_SIM_REGISTRY_PATH + self.selected_network + "\\" + sub_path)

    def delete_registry_key_host_simulator(self, parent: str, key_name: str) -> None:
        """
        Delete the desired registry key under host simulator and including all its children.

        Note that deletion of the entire key is not remembered by the framework 
        and deleted keys are not restored at the end of test run as are individual
        registry values.

        :param str parent: Path to the parent key containing the key to be deleted
        :param str sub_key_name: Name of the key that is to be deleted from parent
        :return: None
        """
        self.registry_handler.delete_registry_key(
            self.HOST_SIM_REGISTRY_PATH + self.selected_network + "\\" + parent,
            key_name,
        )

    def start(self) -> None:
        """
        Attempt to start the service
        :return: None, will raise RuntimeError if something goes wrong
        """
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        RadViewerScript().start_service(self.service_name).result(self.pmi_hostname)

    def stop(self) -> None:
        """
        Attempt to stop the service.
        :return: None, will raise RuntimeError if something goes wrong
        """
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        RadViewerScript().stop_service(self.service_name).result(self.pmi_hostname)


    def restart(self, timeout: int = 120, extra_wait: int = 5, attempts: int = 30, polling_sleep: float = 0.5) -> None:
        """
        Attempt to restart the service. Starts the service if it's already stopped.
        :param int timeout: Timeout (in seconds) for polling the service after
            attempting to start it
        :param int extra_wait: Adds and extra wait at the end of the function
            to account for any additional time the service might need to come back up
        :param int attemps: Number of attempts to try function.
        :param float polling_sleep: Amount of time to wait between polling checks
        :return: None, will raise RuntimeError if something goes wrong
        """
        # .stop_service() already has logic to skip if service is already stopped
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        RadViewerScript().stop_service(self.service_name).start_service(self.service_name).result(self.pmi_hostname)

        result, success = utility.wait_until(
            self.is_online,
            lambda x: x,
            attempts,
            polling_sleep,
            timeout=timeout
        )

        if not success:
            raise RuntimeError(f"Service manager - Timed out waiting for {self.name} to come online")

        time.sleep(
            extra_wait
        )  # wait a bit longer in case Sigma is still starting stuff

    def is_online(self) -> bool:
        """
        Checks if the service is available or not
        :return: True if the service is available
        :rtype: bool
        """
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        result = (
            RadViewerScript()
            .get_service_info(self.service_name)
            .result(self.pmi_hostname)
        )
        return "SERVICE_RUNNING" in result.log

    def start_host(self) -> None:
        """
        Attempt to start the HostSimulator service
        :return: None, will raise RuntimeError if something goes wrong
        """
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        RadViewerScript().start_service(self.HOST_SIM_SERVICE_NAME).result(
            self.pmi_hostname
        )

    def stop_host(self) -> None:
        """
        Attempt to stop the HostSimulator service.
        :return: None, will raise RuntimeError if something goes wrong
        """
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        RadViewerScript().stop_service(self.HOST_SIM_SERVICE_NAME).result(
            self.pmi_hostname
        )

    def is_host_online(self) -> bool:
        """
        Checks if the selected host sim service is available or not
        :return: True if the selected host sim service is available
        :rtype: bool
        """
        # TODO: use self._pmi.hostname once PMI has been reintroduced - RPOS-60082
        result = (
            RadViewerScript()
            .get_service_info(self.HOST_SIM_SERVICE_NAME)
            .result(self.pmi_hostname)
        )
        return "SERVICE_RUNNING" in result.log
