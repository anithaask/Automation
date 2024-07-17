try:
    from winreg import OpenKey
    from winreg import HKEY_LOCAL_MACHINE
    from winreg import KEY_WRITE
    from winreg import DeleteValue
    from winreg import DeleteKeyEx
    from winreg import CloseKey
    from winreg import KEY_READ
    from winreg import QueryValueEx
    from winreg import EnumKey
    from winreg import EnumValue
    from winreg import CreateKey
    from winreg import SetValueEx
    from winreg import KEY_ALL_ACCESS
    from winreg import REG_SZ
    from winreg import REG_DWORD_LITTLE_ENDIAN
    from winreg import REG_DWORD_BIG_ENDIAN

    REGISTRY_SUPPORTED = True
except ImportError:
    REGISTRY_SUPPORTED = False

from typing import Union

from sitbdd.sitcore.bdd_utils.sit_logging import setup_logger, wrap_all_methods_with_log_trace

logger = setup_logger()

@wrap_all_methods_with_log_trace
class RegistryHandler:
    """
    This class contains helper functions for registry manipulation for the HostSimulator, Epsilon
    POSCache, etc.
    """

    def __init__(self):
        # Following dicts are structured as follows:
        # key: the concatenated path and name strings
        # value: (path, name, value_type_pair) tuple
        # where path and name are strings and
        # value_type_pair can be a tuple or None depending on
        # if the key is supposed to be set/created or deleted
        self.original_values = dict()
        self.current_changes = dict()
        self.previous_changes = dict()

    def _save_original_value(self, path: str, name: str) -> None:
        """
        Save the original registry setting internally
        To be run before changing a registry value
        :param str path: Path to the original key
        :param str name: Name of the original key
        :return: None
        """
        # Duplicate entry prevention (keep first)
        key = path + name
        if key in self.original_values:
            return

        # Entry addition
        value_type_pair = self.get_registry_value_type_pair(path, name)
        new_entry = (path, name, value_type_pair)
        self.original_values[key] = new_entry

    def _save_change(self, path: str, name: str) -> None:
        """
        Save the current registry setting internally
        To be run after changing a registry value
        :param str path: Path to the changed key
        :param str name: Name of the changed key
        :return: None
        """
        # Duplicate entry prevention (keep last) + entry addition
        key = path + name
        value_type_pair = self.get_registry_value_type_pair(path, name)
        new_entry = (path, name, value_type_pair)
        self.current_changes[key] = new_entry

    def is_reboot_needed(self) -> bool:
        """
        Determine whether reboot is needed based on current and previous saved changes
        To be called and acted upon under system ready to sell
        :return: True if registries have been changed since last call of
            restore_original_values(), False otherwise
        :rtype: bool
        """
        return set(self.current_changes.values()) != set(self.previous_changes.values())

    def restore_original_values(self) -> None:
        """
        Restore registry setting to its original state and shift current changes to previous
        To be run in after_scenario in environment

        Warning: This method is OBSOLETE and tests relying on it are BROKEN!

        No tests should rely on configuration being restored after previous scenarios. 
        There are number of problems this causes:
        - if scenario exits unexpectedly via exception the config isn't restored
        - if debugging stops mid scenario the config isn't restored
        - running same or similar scenarios in succession uses same config; 
          restoring old config delays the scenario both at the start and at the end
        - troubleshooting scenario is difficult of configuration of the system after
          scenario run doesn't match the configuration from its run

        :return: None
        """
        for change in self.original_values.values():
            path, name, value_type_pair = change
            if value_type_pair:
                value, reg_type = value_type_pair
                self.set_registry_value(path, name, value, reg_type=reg_type, ignore_changes=True)
            else:
                self.delete_registry_value(path, name, ignore_changes=True)

        self.previous_changes = self.current_changes
        self.current_changes = dict()

    def delete_registry_value(self, path: str, name: str, ignore_changes: bool = False) -> None:
        """
        Attempt to delete the desired registry value
        :param str path: Path to the desired key
        :param str name: Name of the desired value
        :param bool ignore_changes: Internal flag for saving changes to registry
        :return: None
        """
        # Preliminary check
        if self.get_registry_value(path, name) is None:
            return

        # Saving information
        self._save_original_value(path, name)

        # Key deletion
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        registry_key = OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_WRITE)
        DeleteValue(registry_key, name)
        logger.info(f'Deleting registry value "{name}" from path "{path}".')
        CloseKey(registry_key)

        # Saving change
        if not ignore_changes:
            self._save_change(path, name)

    def delete_registry_key(self, parent: str, sub_key_name: str) -> None:
        """
        Delete the desired registry key and including all its children.

        Note that deletion of the entire key is not remembered by the framework 
        and deleted keys are not restored at the end of test run as are individual
        registry values.

        :param str parent: Path to the parent key containing the key to be deleted
        :param str sub_key_name: Name of the key that is to be deleted from parent
        :return: None
        """
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        
        try:
            with OpenKey(HKEY_LOCAL_MACHINE, parent + sub_key_name) as sub_key:
                while True:
                    try:
                        sub_sub_key_name = EnumKey(sub_key, 0)
                        self.delete_registry_key(parent + sub_key_name + "\\", sub_sub_key_name)
                    except OSError:
                        break

            with OpenKey(HKEY_LOCAL_MACHINE, parent) as key:
                DeleteKeyEx(key, sub_key_name)
                logger.info(f'Deleting registry key "{sub_key_name}" from path "{parent}".')
        except OSError:
            #exception is thrown when attempting to delete an already deleted key
            logger.info(f'Could not delete key "{sub_key_name}" from path "{parent}"')

    def delete_all_registry_values(self, key_name: str, ignore_changes: bool = False) -> None:
        """
        Delete all values in the desired registry key
        :param str path: Path to the desired key
        :param bool ignore_changes: Internal flag for saving changes to registry
        :return: None
        """
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        
        with OpenKey(HKEY_LOCAL_MACHINE, key_name) as key:
            while True:
                try:
                    value_name = EnumValue(key, 0)[0]
                    self.delete_registry_value(key_name, value_name, ignore_changes)
                except OSError:
                    break

    def get_registry_value(self, path: str, name: str) -> Union[str, None]:
        """
        Attempt to find specified key
        :param str path: Path to the desired key
        :param str name: Name of the desired key
        :return: String of the registry value. Will raise WindowsError
            if something goes wrong
        :rtype: str, None
        """
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        registry_key = OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_READ)

        try:
            value = QueryValueEx(registry_key, name)[0]
        except FileNotFoundError:
            # Will return None if the desired key does not exist. Written this way so we can
            # use this method for verification as well. Exceptions can be thrown in the step
            # definitions themselves.
            logger.info(f"The desired key of name {name} was not found at path {path}.")
            return None

        CloseKey(registry_key)

        return str(value)

    def get_registry_value_type_pair(self, path: str, name: str) -> Union[tuple, None]:
        """
        Get the value/regtype pair of the desired key
        :param str path: Path to the desired key
        :param str name: Name of the desired key
        :return: tuple of the registry key value and regtype or
            None if key doesn't exist 
        :rtype: tuple, None
        """
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        registry_key = OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_READ)

        try:
            value_type_pair = QueryValueEx(registry_key, name)
            CloseKey(registry_key)
            return value_type_pair
        except FileNotFoundError:
            # Will return None if the desired key does not exist. Written this way so we can
            # use this method for verification as well. Exceptions can be thrown in the step
            # definitions themselves.
            logger.info(f"The desired key of name {name} was not found at path {path}.")
            CloseKey(registry_key)
            return None

    def create_registry_key(self, path: str, key: str) -> None:
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        CreateKey(HKEY_LOCAL_MACHINE, path + "\\" + key)

    def set_registry_value(
        self, path: str, name: str, value: Union[str,int],
        reg_type: Union[int,None] = None, ignore_changes: bool = False
    ) -> None:
        """
        Sets the desired registry key to the given value.
        :param str path: Path to the desired key
        :param str name: Name of the desired key
        :param str/int value: Desired value to set the key to
        :param int reg_type: Integer value representing the type of registry value it is
            or None for the value representing REG_SZ by default
        :param bool ignore_changes: Internal flag for saving changes to registry
        :return: None, will raise WindowsError if something goes wrong
        """
        
        # Preliminary check
        pair = self.get_registry_value_type_pair(path, name)
        if pair is not None:
            prev_value, prev_type = pair
            if value == prev_value and (reg_type is None or reg_type == prev_type):
                return

        # Saving original value
        self._save_original_value(path, name)

        # Setting registry value
        if reg_type is None:
            reg_type = REG_SZ
        if not REGISTRY_SUPPORTED:
            raise OSError("This system does not support the Windows registry.")
        CreateKey(HKEY_LOCAL_MACHINE, path)        

        registry_key = OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_ALL_ACCESS)        
        try:
            # Try to figure out value type of desired key and set it to correct type.
            reg_type = QueryValueEx(registry_key, name)[1]

            if reg_type in {REG_DWORD_LITTLE_ENDIAN, REG_DWORD_BIG_ENDIAN}:
                value = int(value)

            SetValueEx(registry_key, name, 0, reg_type, value)
            logger.info(f'Registry key "{name}" at path "{path}" has been successfully given a new value "{value}".')
        except FileNotFoundError:
            # Registry key does not currently exist so we assign it with provided value type; default is string.
            logger.info(f'Registry key "{name}" was not found at path "{path}" creating a new key.')
            SetValueEx(registry_key, name, 0, reg_type, value)

        CloseKey(registry_key)

        # Saving change
        if not ignore_changes:
            self._save_change(path, name)
