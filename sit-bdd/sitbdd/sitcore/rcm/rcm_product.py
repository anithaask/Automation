__all__ = ["RCMProduct"]

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.rcm.rcm_communicator import RCMCommunicator

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class RCMProduct:
    """
    This class is the highest level abstraction of the RCM product and
    should be used in test step implementations.
    """

    def __init__(self, hostname: str, port: int, version: int = 1):
        """
        :param hostname: Hostname of the RCM machine
        :param port: Port for the RCM machine's Rest API
        """
        self._comm = RCMCommunicator(hostname, port)

    def update_pos_option_profile(self) -> None:
        """
        Update the POS option profile using predefined POS option values.
        """
        self._comm._update_pos_option_profile()

    def create_download(self, update_type) -> None:
        """
        Create an approved download for a site

        :param UpdateTypes update_type: One of the values in updates_types.py
        """
        self._comm.create_download(update_type)

    def wait_for_update_finish(self, update_type) -> bool:
        """
        Waits for update to be finished (download triggered from SC).

        :param UpdateTypes update_type: One of the values in updates_types.py
        :return: True if the update was successful, otherwise False.
        """
        return self._comm.wait_for_update_finish(update_type)

    def set_pos_option(self, option: str, value: str) -> None:
        """
        Set a configuration option in RCM to a specific value

        :param string option: The name of the option to set in the profile
        :param string value: The name of the value to set the option to
        """
        self._comm.set_pos_option(option, value)

    def set_icr_option(self, option: str, value: str) -> None:
        """
        Set a configuration option in RCM to a specific value

        :param string option: The name of the option to set in the profile
        :param string value: The name of the value to set the option to
        """
        self._comm.set_icr_option(option, value)

    def get_pos_option_value(self, option: str) -> str:
        """
        Gets the current value of an option

        :param option: The name of the option the value is being requested for
        :return: str Value the config option is currently set to in the RCM server
        """
        return self._comm.get_pos_option_value(option)

    def get_icr_option_value(self, code: str) -> str:
        """
        Gets the current value of an ICR option

        :param str code: The name of the ICR option the value is being requested for
        :return: str Value the config option is currently set to in the RCM server
        """
        return self._comm.get_icr_option_value(code)

    def link_RCM(self, site_number: int):
        """ Links RCM site.

        :param site_number: Number of the site written in string.
        """
        self._comm.link_RCM(site_number)

    def get_service_endpoints(self):
        """ Gets service endpoints for linking RCM site with SC.

        :return: Message URL and File URL
        """
        return self._comm.get_service_endpoints()
    
    def get_update_needed_value(self) -> bool:
        """
        Retrieve Update Needed flag for site update in RCM.
        
        :return: bool True if update is needed False otherwise.
        """
        return self._comm.get_update_needed_value()

    def get_pos_option_profiles(self) -> list:
        """
        Gets all POS option profiles.

        :return: List of profiles in form of dictionary.
        """
        return self._comm.get_pos_option_profiles()

    def create_pos_option_profile(self, profile_name: str, pos_options_list: list = None, profileId: int = 0, profile_description: str = "Default description") -> int:
        """
        Creates new POS option profile with given values.

        :param list pos_options_list: List of POS options to be set on a created profile.
        :param int profileId: Identificator of the profile to be created.
        :param str profile_name: Name of the profile to be created.
        :param str profile_description: Description of the profile to be created.
        :return: ID of the POS option profile created.
        """
        return self._comm.create_pos_option_profile(profile_name=profile_name, pos_options_list=pos_options_list, profileId=profileId, profile_description=profile_description)

    def pos_option_profile_exists(self, profile_name: str) -> bool:
        """
        Checks if profile with given name exist.
    
        :param str profile_name: Profile name to be check.
        :return: True if profile with given name exist False otherwise.
        """
        return self._comm.pos_option_profile_exists(profile_name=profile_name) 

    def get_icr_option_profiles(self) -> list:
        """
        Gets list of FuelIcrOptionProfiles.

        :return: List of profiles in form of dictionary.
        """
        return self._comm.get_icr_option_profiles()

    def create_icr_option_profile(self, profile_name: str, icr_options_list: list = None, profileId: int = 0, profile_description: str = "Default description") -> int:
        """
        Creates new ICR option profile with given values. Uses default ICR config within rcm if icr options list is not provided.

        :param list icr_options_list: List of ICR options to be set on a created profile.
        :param int profileId: Identificator of the profile to be created.
        :param str profile_name: Name of the profile to be created.
        :param str profile_description: Description of the profile to be created.
        :return: ID of the ICR option profile created.
        """
        return self._comm.create_icr_option_profile(profile_name=profile_name, icr_options_list=icr_options_list, profileId=profileId, profile_description=profile_description)

    def icr_option_profile_exists(self, profile_name: str) -> bool:
        """
        Checks if profile with given name exist.
    
        :param str profile_name: Profile name to be check.
        :return: True if profile with given name exist False otherwise.
        """ 
        return self._comm.icr_option_profile_exists(profile_name=profile_name)
    
    def set_discount(self, discount_name: str, discount_external_id: str, discount_type: str, discount_value: float) -> None:
        """
        Set a discount in RCM
        """
        self._comm.set_discount(discount_name, discount_external_id, discount_type, discount_value)

