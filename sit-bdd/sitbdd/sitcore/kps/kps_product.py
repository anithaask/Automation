__all__ = ["KPSProduct"]

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.kps.kps_communicator import KPSCommunicator

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class KPSProduct:
    """
    This class is the highest level abstraction of the KPS product and
    should be used in test step implementations.
    """

    def __init__(self, hostname: str):
        """
        :param hostname: Hostname of the KPS
        """
        self._comm = KPSCommunicator(hostname)

    def get_kps_status(self) -> bool:
        """
        Returns the current status of the KPS.
        
        :return: True if KPS is online, False otherwise.
        """
        return self._comm.get_kps_status()
    
    def bump_transaction(self, transaction_number: int) -> None:
        """
        Bumps a transaction on the KPS given the transaction number.
        
        :param int transaction_number: Transaction number for transaction that will be bumped on KPS.
        """
        self._comm.bump_transaction(transaction_number)
    

    def get_bump_status(self, transaction_number: int) -> bool:
        """
        This method waits for KPS to send message that a transaction has been bumped.
        
        :param int transaction_number: Transaction number for transaction that will be bumped on KPS.
        """
        self._comm.get_bump_status(transaction_number)
