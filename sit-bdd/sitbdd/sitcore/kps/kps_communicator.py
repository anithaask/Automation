__all__ = ["KPSCommunicator"]
# Only the most simple functions have been implemented use the following
# to explore the rest of the functionality: 
# https://github.com/ncr-swt-cfr/rpos/blob/7d3a3686df9392a19e50c9a9a635edf16281d62c/6.1/Interfaces/KPS/KpsMqttApi.yaml

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.bdd_utils.errors import ProductError
from cfrsc.core.sc.mqtt_client_manager import MqttClient
from cfrsc.core.sc.mqtt_client_manager import MqttClientManager

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class KPSCommunicator():
    """
    This class is the communication layer between SITCore and the KPS MQTT Broker.
    """

    def __init__(self, hostname: str):
        """
        :param hostname: Hostname without protocol.
        """
        self.mqtt_client_manager = MqttClientManager()

        # Setting up the subscriber allows us to receive messages from the MQTT Broker
        self.subscriber = self.mqtt_client_manager.get_client("Subscriber")
        self.subscriber.connect(hostname)
        self.subscriber.loop_start()
        self.subscriber.wait_until_connected()

        # Setting up the publisher allows us to send messages to the MQTT Broker
        self.publisher = self.mqtt_client_manager.get_client("Publisher")
        self.publisher.connect(hostname)
        self.publisher.loop_start()
        self.publisher.wait_until_connected()


    def get_kps_status(self) -> bool:
        """
        Returns the current status of the KPS.
        
        :return: True if KPS is online, False otherwise.
        """
        self.subscriber.subscribe("rpos/kps/200/system/heartbeat")
        self.subscriber.wait_until_subscribed()

        msg_received: bool = self.subscriber.wait_until_message(1)

        if not msg_received or not self.subscriber.received_messages:
            raise ProductError("Failed to receive status for KPS.")

        message: MQTTMessage = self.subscriber.received_messages[0]

        if "STARTED" in str(message.payload):
            return True
        else:
            return False


    def bump_transaction(self, transaction_number: int) -> None:
        """
        Bumps a transaction on the KPS given the transaction number.
        
        :param int transaction_number: Transaction number for transaction that will be bumped on KPS.
        """
        self.publisher.publish(f"rpos/kps/200/view/1/transaction/{transaction_number}/bump", "CommonIncomingMessage")
        self.publisher.wait_until_published()
    

    def get_bump_status(self, transaction_number: int) -> bool:
        """
        This method waits for KPS to send message that a transaction has been bumped.
        
        :param int transaction_number: Transaction number for transaction that will be bumped on KPS.
        """
        self.subscriber.subscribe(f"rpos/kps/200/view/1/transaction/{transaction_number}/bumped")
        self.subscriber.wait_until_subscribed()

        msg_received: bool = self.subscriber.wait_until_message(30)

        if not msg_received:
            logger.error("Failed to receive message from KPS.")
            return False

        return True
