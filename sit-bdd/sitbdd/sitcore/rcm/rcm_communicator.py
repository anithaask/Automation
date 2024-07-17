__all__ = ["RCMCommunicator"]

import subprocess
import time
from typing import Union

from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils.http_communicator import HTTPCommunicator
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.rcm.pos_options import pos_options
from sitbdd.sitcore.rcm.update_types import UpdateTypes
from sitbdd.sitcore.bdd_utils.utility import wait_until

logger = get_sit_logger()

# numbers matching the hierarchies in RCM
DEFAULT_SITE_HIERARCHY_ID = "70000003"
FEATURES_SITE_HIERARCHY_ID = "70000004"


@wrap_all_methods_with_log_trace
class RCMCommunicator(HTTPCommunicator):
    """
    This class is the communication layer between SITCore and the RCM Rest API.
    """

    def __init__(self, hostname: str, port: int = None, version: int = 1):
        """
        :param hostname: Hostname without protocol.
        :param port: Port number.
        """
        super().__init__(hostname, port, secure=True)
        self._version = version
        self._prefix = f"pos/v{self._version}/"

        self._rcm_username = "admin"
        self._rcm_password = "!Rambo1@"
        self._site_hierarchy_id = DEFAULT_SITE_HIERARCHY_ID
        self._token = ""

        # Default linked site
        self._site_number = "010122"
        self._site_id = "444eb3ba-5f86-4ec8-bb89-65b776d113a0" # id taken from devops first link site
        self._pos_options_profile_id = "70000000001"
        self._pos_options_profile_name = "Default POS Options"
        self._icr_options_profile_id = 70000000003
        self._icr_options_profile_name = "Default ICR Option Profile"


    def prepare_headers_for_request(self) -> dict:
        self.refresh_token(self._rcm_username, self._rcm_password)
        headers = {
            "RCM-Site-Hierarchy-Id": self._site_hierarchy_id,
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {self._token}",
        }
        return headers


    def _update_pos_option_profile(self):
        """Update the POS option profile using predefined POS option values."""
        logger.info("Updating POS options profile with default values")
        headers = self.prepare_headers_for_request()
        pos_option_values = [
            {"posId": str(option["posId"]), "value": str(option["initialValue"])}
            for option in pos_options
        ]
        data = {
            "posOptionProfileId": self._pos_options_profile_id,
            "posOptionValues": pos_option_values,
        }
        self._put(
            f"{self._prefix}pos-option-profiles/{self._pos_options_profile_id}",
            headers=headers,
            data=data,
            verify=False,
        )
        logger.info("POS options profile was updated with default values")


    def refresh_token(self, username: str, password: str):
        """
        Requests a new authentication token from RCM's Rest API and
        updates the token for the RCM Communicator.

        :param str username: username for the RCM.
        :param str password: password for the RCM.
        :return: None
        """
        data = {
            "username": username,
            "password": password
        }
        headers = {
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._token = self._post(f"Authenticate/v{self._version}/authenticate", headers=headers, data=data, verify=False)["token"]
        logger.info("The token for RCM connection was successfully refreshed.")


    def site_update_status_to_text(self, site_update_status_code: int) -> str:
        """ Converts update status code to text for logging and debugging.

        :param site_update_status_code: Status code of the site update.
        :return: Converted status code to text
        """
        if site_update_status_code == 1:
            return "Requested"
        elif site_update_status_code == 2:
            return "Creation in progress"
        elif site_update_status_code == 3:
            return "Awaiting for site to connect"
        elif site_update_status_code == 4:
            return "Creation failed"
        elif site_update_status_code == 5:
            return "Update in progress"
        elif site_update_status_code == 6:
            return "Update successful"
        elif site_update_status_code == 7:
            return "Update failed!"
        elif site_update_status_code == 8:
            return "Obsolete data"
        elif site_update_status_code == 9:
            return "Update deferred"
        elif site_update_status_code == 10:
            return "Update stuck"
        elif site_update_status_code == 11:
            return "Reboot required"
        else:
            return "Undefined"


    def create_site(self, site_number: str, site_hierarchy_id: str = FEATURES_SITE_HIERARCHY_ID,
                    external_id: int = None, address1: str = "", address2: str = "", city: str = "",
                    postalCode: str = "", country: str = "", state: str = "", contactName: str = "",
                    phone: str = "", fax: str = "", email: str = "", inheritCity: bool = True,
                    inheritPostalCode: bool = True, inheritCountry: bool = True,
                    inheritState: bool = True, inheritReceiptHeader: bool = True, inheritReceiptFooter: bool = True,
                    inheritIcrHeader: bool = True, inheritIcrFooter: bool = True, inheritLocalePreference: bool = True):
        """ Creates site in RCM with given information.

        :param site_number: Site of the number. It will be also set as it's name.
        :param site_hierarchy_id: Id of hierarchy, where the site is created.
        :params other: Fills information about site or inherits.
        """
        headers = self.prepare_headers_for_request()
        data = {
            "parentSiteHierarchyId": site_hierarchy_id,
            "name": site_number,
            "siteNumber": site_number,
            "address1": address1,
            "address2": address2,
            "city": city if not inheritCity else "",
            "postalCode": postalCode if not inheritPostalCode else "",
            "country": country if not inheritCountry else "",
            "state": state if not inheritState else "",
            "contactName": contactName,
            "phone": phone,
            "fax": fax,
            "email": email,
            "inheritCity": inheritCity,
            "inheritPostalCode": inheritPostalCode,
            "inheritCountry": inheritCountry,
            "inheritState": inheritState,
            "inheritReceiptHeader": inheritReceiptHeader,
            "inheritReceiptFooter": inheritReceiptFooter,
            "inheritIcrHeader": inheritIcrHeader,
            "inheritIcrFooter": inheritIcrFooter,
            "inheritLocalePreference": inheritLocalePreference
        }
        if external_id:
            data['externalId'] = external_id
        self._post(f"{self._prefix}sites", headers=headers, data=data, verify=False)


    def link_RCM(self, site_number: str, site_hierarchy_id: str = FEATURES_SITE_HIERARCHY_ID):
        """ Links RCM site.

        :param site_number: Number of the site written in string.
        :param site_hierarchy_id: Hierarchy id, where the site is located.
        """
        # first we need to unlink the old site to be sure
        headers = self.prepare_headers_for_request()
        self._post(f"{self._prefix}sites/{self._site_number}/un-link", headers=headers, verify=False)
        # then we set new site number with the new hierarchy id and link a new site
        self._site_hierarchy_id = site_hierarchy_id
        self._site_number = site_number
        headers = self.prepare_headers_for_request()
        response = self._post(f"{self._prefix}sites/{site_number}/link", headers=headers, verify=False)
        self._site_id = response['siteId']


    def get_service_endpoints(self):
        """ Gets service endpoints for linking RCM site with SC.

        :return: Message URL and File URL
        """
        headers = self.prepare_headers_for_request()
        end_points = self._get(f"{self._prefix}service-end-points", headers=headers, verify=False)
        messageUrl = None
        fileUrl = None
        for end_point in end_points:
            if end_point.get('type') == 'File':
                fileUrl = end_point.get('link')
            if end_point.get('type') == 'Message':
                messageUrl = end_point.get('link')
        if not messageUrl:
            raise ProductError(f"MessageUrl was not filled from service-end-points request. The response was {end_points}")
        if not fileUrl:
            raise ProductError(f"FileUrl was not filled from service-end-points request. The response was {end_points}")
        return messageUrl, fileUrl


    def create_download(self, update_type: UpdateTypes):
        """
        Creates a site update and waits until the site update is ready for downloading.

        :param UpdateTypes update_type: An enum whose value refers to 0, 1, or 2
            for specifying the type of download.
        :return: None
        """
        headers = self.prepare_headers_for_request()
        data = {
            "statusCode": 1,
            "siteNumber": self._site_number,
            "priorityFlag": False,
            "requestTimestamp": "1965-06-24T10:39:18.221Z",
            "updateTypeCode": update_type.value,
        }
        site_update_id = self._post(f"{self._prefix}site-updates", headers=headers, data=data, verify=False)['siteUpdateId']
        self.wait_for_update_creation(site_update_id)


    def wait_for_update_creation(self, site_update_id: int) -> bool:
        """ Waits for update to be created and ready to be downloaded by SC.

        :param site_update_id: Id of the update created.
        """
        def get_update_status() -> int:
            return int(self._get(f"{self._prefix}site-updates/{site_update_id}", headers=headers, verify=False).get('statusCode'))

        def compare_update_status(status_code: int) -> bool:
            return status_code == 3

        headers = self.prepare_headers_for_request()
        status_code, done = wait_until(get_update_status, compare_update_status, attempts=60, delay=1.0)
        if not done:
            logger.error(f"The RCM update creation was not successful. Status code: {status_code}; {self.site_update_status_to_text(status_code)}")
            return False
        logger.info(f"The RCM update creation was successful. Status code: {status_code}; {self.site_update_status_to_text(status_code)}")
        return True


    def wait_for_update_finish(self, update_type: UpdateTypes) -> bool:
        """
        Executes RCM download after it was requested.

        :param UpdateTypes update_type: An enum whose value refers to 0, 1, or 2
            for specifying the type of download.
        :return: True if the update was successful, otherwise False.
        """
        def get_update_status() -> int:
            return int(self._get(f"{self._prefix}site-updates/last-site-update-status/{self._site_number}", headers=headers, verify=False).get('statusCode'))

        def compare_update_status(status_code: int) -> bool:
            return status_code == 6

        headers = self.prepare_headers_for_request()
        data = {
            "statusCode": 1,
            "siteNumber": self._site_number,
            "priorityFlag": False,
            "requestTimestamp": "1965-06-24T10:39:18.221Z",
            "updateTypeCode": update_type.value,
        }
        status_code, done = wait_until(get_update_status, compare_update_status, attempts=100, delay=2.0)
        if not done:
            logger.error(f"The RCM update was not successful. Status code: {status_code}; {self.site_update_status_to_text(status_code)}")
            return False
        logger.info(f"The RCM update was successful. Status code: {status_code}; {self.site_update_status_to_text(status_code)}")
        return True


    def set_pos_option(self, option: int, value: Union[int, float]) -> None:
        """
        Sets a config option in RCM to a value that is a valid choice for that option,
        and then checks to make sure it has been set.
        If an option is not set to "override" it will not be changeable from
        its default value, so if you attempt to set a non-overridden option to
        a value that is not its default value a ProductError will be raised.

        :param int option: POS ID of the option to set.
        :param int or double value: Numeric code of the value the option is being set to.
        :return: None
        :raises ProductError: If it was not possible to set the value of the option.
        """
        # No hierarchy should be selected for setting config options
        headers = self.prepare_headers_for_request()
        data = {
            "posOptionProfileId": self._pos_options_profile_id,
            "name": self._pos_options_profile_name,
            "posOptionValues": [
                {
                    "posOptionProfileId": self._pos_options_profile_id,
                    "posId": option,
                    "value": value,
                }
            ],
        }

        self._put(
            f"{self._prefix}pos-option-profiles/{self._pos_options_profile_id}",
            headers=headers,
            data=data,
            verify=False,
        )

        current_value = self.get_pos_option_value(option)
        if current_value != value:
            raise ProductError(
                f'After attempting to set RCM option "{option}" to "{value}", '
                f'it is instead set to "{current_value}".'
            )


    def get_pos_option_value(self, option: int) -> Union[int, float]:
        """
        Gets the current value of an option

        :param int option: The POS ID of the option the value is being requested for
        :return: int or double Value numeric code the config option is currently set to in the RCM server
        """
        headers = self.prepare_headers_for_request()
        pos_option_value = self._get(
            f"{self._prefix}pos-option-profiles/{self._pos_options_profile_id}"
            f"/pos-option-values/{option}",
            headers=headers,
            verify=False,
        )

        # the API returns a different json schema based on
        # if the option is overridden or not
        if "value" in pos_option_value:
            # this interprets the response if the option is overridden
            try:
                return int(pos_option_value["value"])
            except ValueError:
                return float(pos_option_value["value"])
        elif "defaultValue" in pos_option_value:
            # this interprets the response if the option is not overridden
            try:
                return int(pos_option_value["defaultValue"])
            except ValueError:
                return float(pos_option_value["defaultValue"])


    def set_icr_option(self, option: str, value: str) -> None:
        """
        Sets a icr config option in RCM to a value that is a valid choice for that option.

        :param str option: Id of the option to be set. It can be found with rcm client.
        :param str value: Value in the form of a string. Sometimes it is not consistent
        with the value in rcm client and has to be found in the database.
        :return: None
        """
        headers = self.prepare_headers_for_request()
        data = {
            "profileId": self._icr_options_profile_id,
            "name": self._icr_options_profile_id,
            "fuelIcrOptionValues": [
                {
                    "code": option,
                    "value": value
                }
            ],
        }

        self._put(
            f"{self._prefix}icr-option-profiles/{self._icr_options_profile_id}",
            headers=headers,
            data=data,
            verify=False,
        )

        current_value = self.get_icr_option_value(option)
        if current_value != value:
            raise ProductError(
                f'After attempting to set ICR option "{option}" to "{value}", '
                f'it is instead set to "{current_value}".'
            )


    def get_icr_option_value(self, code: str) -> str:
        """
        Gets the current value of an ICR option

        :param str code: The code of the option the value is being requested for
        :return: int Value numeric code the config option is currently set to in the RCM server
        """
        headers = self.prepare_headers_for_request()

        icr_option_value = self._get(
            f"{self._prefix}icr-option-profiles/{self._icr_options_profile_id}"
            f"/icr-option-values/{code}",
            headers=headers,
            verify=False,
        )

        # the API returns a different json schema based on
        # if the option is overridden or not
        if "value" in icr_option_value:
            # this interprets the response if the option is overridden
            return icr_option_value["value"]
        elif "defaultValue" in icr_option_value:
            # this interprets the response if the option is not overridden
            return icr_option_value["defaultValue"]


    def get_update_needed_value(self) -> bool:
            """
            Retrieve Update Needed flag for site update in RCM.
            
            :return: bool True if update is needed False otherwise.
            """
            headers = self.prepare_headers_for_request()
            response = self._get(
                f"{self._prefix}site-updates/sites/{self._site_number}",
                headers=headers,
                verify=False,
            )
            return bool(response["updateNeeded"])


    def get_pos_option_profiles(self) -> list:
        """
        Gets all POS option profiles.

        :return: List of profiles in form of dictionary.
        """
        headers = self.prepare_headers_for_request()
        pos_option_profiles = self._get(
            f"{self._prefix}pos-option-profiles",
            headers=headers,
            verify=False,
        )
        return pos_option_profiles


    def create_pos_option_profile(self, profile_name: str, pos_options_list: list = None, profileId: int = 0, profile_description: str = "Default description") -> int:
        """
        Creates new POS option profile with given values. Uses default POS config within rcm if pos options list is not provided.

        :param list pos_options_list: List of POS options to be set on a created profile.
        :param int profileId: Identificator of the profile to be created.
        :param str profile_name: Name of the profile to be created.
        :param str profile_description: Description of the profile to be created.
        :return: ID of the POS option profile created.
        """
        headers = self.prepare_headers_for_request()
        pos_option_values = [
            {"posId": str(option["posId"]), "value": str(option["value"])}
            for option in pos_options_list
        ]
        if profileId == 0:
            for profile in self.get_pos_option_profiles():
                if profile["profileId"] >= profileId:
                    profileId = profile["profileId"] + 1
        data = {
            "profileId": profileId,
            "name": profile_name,
            "description": profile_description,
                "posOptionValues": pos_option_values,
        }
        self._post(
            f"{self._prefix}pos-option-profiles",
            headers=headers,
            data=data,
            verify=False,
        )
        return profileId


    def pos_option_profile_exists(self, profile_name: str) -> bool:
        """
        Checks if profile with given name exist.
    
        :param str profile_name: Profile name to be check.
        :return: True if profile with given name exist False otherwise.
        """ 
        pos_option_profiles = self.get_pos_option_profiles()
        for profile in pos_option_profiles:
            if profile["name"] == profile_name:
                return True
        return False


    def get_icr_option_profiles(self) -> list:
        """
        Gets list of FuelIcrOptionProfiles.

        :return: List of profiles in form of dictionary.
        """
        headers = self.prepare_headers_for_request()
        icr_option_profiles = self._get(
            f"{self._prefix}icr-option-profiles",
            headers=headers,
            verify=False,
        )
        return icr_option_profiles


    def create_icr_option_profile(self, profile_name: str, icr_options_list: list = None, profileId: int = 0, profile_description: str = "Default description") -> int:
        """
        Creates new ICR option profile with given values. Uses default ICR config within rcm if icr options list is not provided.

        :param list icr_options_list: List of ICR options to be set on a created profile.
        :param int profileId: Identificator of the profile to be created.
        :param str profile_name: Name of the profile to be created.
        :param str profile_description: Description of the profile to be created.
        :return: ID of the ICR option profile created.
        """
        headers = self.prepare_headers_for_request()
        icr_option_values = [
            {"code": str(option["code"]), "value": str(option["value"])}
            for option in icr_options_list
        ]
        if profileId == 0:
            for profile in self.get_icr_option_profiles():
                if profile["profileId"] >= profileId:
                    profileId = profile["profileId"] + 1
        data = {
            "profileId": profileId,
            "name": profile_name,
            "description": profile_description,
                "fuelIcrOptionValues": icr_option_values,
        }
        self._post(
            f"{self._prefix}icr-option-profiles",
            headers=headers,
            data=data,
            verify=False,
        )
        return profileId


    def icr_option_profile_exists(self, profile_name: str) -> bool:
        """
        Checks if profile with given name exist.
    
        :param str profile_name: Profile name to be check.
        :return: True if profile with given name exist False otherwise.
        """ 
        icr_option_profiles = self.get_icr_option_profiles()
        for profile in icr_option_profiles:
            if profile["name"] == profile_name:
                return True
        return False
    
    def set_discount(self, discount_name: str, discount_external_id: str, discount_type: str, discount_value: float) -> None:
        """
        Sets the discount in RCM based on external id. Either create new discount if there is no discount with given external id or 
        update the particular discount with external id. 
        """
        headers = self.prepare_headers_for_request()
        configured_discounts = self._get(
            f"{self._prefix}Discount?externalId={discount_external_id}",
            headers=headers,
            verify=False,
        )

        data = {
            "externalId": discount_external_id,
            "type": discount_type,
            "value": discount_value,
            "isItemLevel": True,
            "securityLevel": 0,
            "reducesTaxFlag": True,
            "applyOnlyOnceFlag": False,
            "employeeDiscountFlag": False,
            "priority": 1,
            "start_date": "2023-08-31T00:00:00",
            "end_date": None,
            "stackableFlag": False,
            "maxVolume": None,
            "maxAmount": None,
            "cardDefinitionGroupId": None,
            "showInManualLookupFlag": True,
            "bestDealFlag": False,
            "reapplicableFlag": True,
            "name": discount_name            
        }

        discountId = ""
        if len(configured_discounts) > 0:
            discountId = next(iter(configured_discounts))["discountId"]

        if discountId:
            # Update discount
            self._put(
                f"{self._prefix}Discount/{discountId}",
                headers=headers,
                data=data,
                verify=False,
            )
        else:
            # Create new discount
            self._post(
                f"{self._prefix}Discount",
                headers=headers,
                data=data,
                verify=False,
            )