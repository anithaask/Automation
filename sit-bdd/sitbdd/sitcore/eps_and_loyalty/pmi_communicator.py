__all__ = ["PMICommunicator"]


import struct

import bs4

from sitbdd.sitcore.eps_and_loyalty.socket_communicator import SocketCommunicator
from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class PMICommunicator(SocketCommunicator):
    """
    This module handles communication to PMI to interact with Epsilon,
    Sigma, and POSCache
    """

    MESSAGE_TAG = "<Message/>"
    MESSAGE_ATT_LOCATION_ID = "LocationId"
    MESSAGE_ATT_EXTERNAL_ID = "ExternalId"
    MESSAGE_ATT_MESSAGE_TYPE = "MessageType"
    MESSAGE_ATT_OPERATION = "Operation"
    MESSAGE_ATT_ORIG_OPERATION = "OrigOperation"
    MESSAGE_ATT_REQUEST_ID = "RequestId"
    MESSAGE_ATT_VERSION = "Version"
    MESSAGE_ATT_TRANSACTION_NUMBER = "TransactionNumber"
    MESSAGE_ATT_SUBSYSTEM = "Subsystem"
    MESSAGE_ATT_RESULT = "Result"
    MESSAGE_ATT_NOTIFY_REASON = "NotifyReason"
    TRAN_STATUS_ATT_IS_APPROVED = "IsApproved"

    def __init__(self, hostname, port, subsystem):
        self.subsystem = subsystem
        self.location_id = "POS1"
        self.version = 1.1
        super().__init__(hostname, port)

    def build_pmi_request_message_header(self, operation):
        """
        Builds the header portion of a PMI request message
        and returns it as an XML string
        :param str operation: Type of operation of the request
        :return: XML string request message header
        :rtype: str
        """
        message_soup = bs4.BeautifulSoup(self.MESSAGE_TAG, "xml")
        message_soup.Message[self.MESSAGE_ATT_LOCATION_ID] = self.location_id
        message_soup.Message[self.MESSAGE_ATT_MESSAGE_TYPE] = "Request"
        message_soup.Message[self.MESSAGE_ATT_OPERATION] = operation
        message_soup.Message[self.MESSAGE_ATT_REQUEST_ID] = 0
        message_soup.Message[self.MESSAGE_ATT_VERSION] = self.version
        message_soup.Message[self.MESSAGE_ATT_SUBSYSTEM] = self.subsystem

        return str(message_soup.Message)

    def parse_response(
        self, response, requested_operation, remove_special_characters=False
    ):
        """
        Parses the response from PMI and determines if it is valid or not.
        :param str response: XML string from PMI
        :param str requested_operation: Type of operation that was originally requested
        :param bool remove_special_characters:
        If True, removes file, group, record, and unit separators from
        the response prior to parsing.
        :return: XML string if response is valid else None
        :rtype: str or None
        """
        result = None
        if response is not None:
            if remove_special_characters:
                response = response.replace("\x1c", "")  # File Separator
                response = response.replace("\x1d", "")  # Group Separator
                response = response.replace("\x1e", "")  # Record Separator
                response = response.replace("\x1f", "")  # Unit Separator
            data_soup = bs4.BeautifulSoup(response, "xml")

            """
            Can't use "self.MESSAGE_ATT_RESULT in data_soup.Message"
            since data_soup.Message isn't a normal data structure
            """
            if data_soup.Message.get(self.MESSAGE_ATT_RESULT):
                if (
                    data_soup.Message[self.MESSAGE_ATT_RESULT].lower() == "success"
                    and data_soup.Message[self.MESSAGE_ATT_MESSAGE_TYPE].lower()
                    == "response"
                    and data_soup.Message[self.MESSAGE_ATT_LOCATION_ID]
                    == self.location_id
                    and data_soup.Message[self.MESSAGE_ATT_OPERATION]
                    == requested_operation
                ):
                    result = data_soup

            if (
                not result
                and data_soup.Message.get(self.MESSAGE_ATT_OPERATION)
                and data_soup.Message.get(self.MESSAGE_ATT_NOTIFY_REASON)
            ):
                if (
                    data_soup.Message[self.MESSAGE_ATT_NOTIFY_REASON].lower()
                    == "complete"
                    or data_soup.Message[self.MESSAGE_ATT_NOTIFY_REASON].lower()
                    == "decodecomplete"
                    and (
                        data_soup.Message[self.MESSAGE_ATT_OPERATION].lower()
                        == "notify"
                        and data_soup.Message[self.MESSAGE_ATT_LOCATION_ID]
                        == self.location_id
                        and data_soup.Message[self.MESSAGE_ATT_ORIG_OPERATION]
                        == requested_operation
                    )
                ):
                    result = data_soup

        return str(result.Message) if result is not None else None

    def _communicate(self, command, buffer=4096, timeout=60, polling_sleep=0.5):
        """Sends a command to PMI
        :param str command: Command you want to send to PMI
        :param int buffer: Unused in this override
        :param float timeout: Time to continue checking for responses
        :param float polling_sleep: Time to sleep between checking for responses
        :return:
        """
        self._handle_send(command)

        result, success = utility.wait_until(
            self._handle_receive,
            self._response_in_progress,
            timeout//polling_sleep,
            polling_sleep,
            timeout=timeout
        )

        if success:
            return result
        else:
            raise RuntimeError("Timed out waiting for PMI to respond with a non-InProgress result")

    def _response_in_progress(self, response):
        """
        Checks whether the response has a result of InProgress.
        Meaning, we need to keep handling responses
        until given one that is not InProgress
        :param response:
        :return:
        """
        if response is not None:
            response = response.replace("\x1c", "")  # File Separator
            response = response.replace("\x1d", "")  # Group Separator
            response = response.replace("\x1e", "")  # Record Separator
            response = response.replace("\x1f", "")  # Unit Separator
            data_soup = bs4.BeautifulSoup(response, "xml")
            if data_soup.Message.get(self.MESSAGE_ATT_RESULT):
                if data_soup.Message[self.MESSAGE_ATT_RESULT].lower() == "inprogress":
                    return True
            else:
                return False

        return False

    def _handle_send(self, data):
        """
        Sends the given data to PMI
        :param str data: data to be sent. Should be normal (non-binary) string as
        it will be converted to binary
        :return: N/A
        """
        logger.trace("PMI >> " + data)

        data = data.encode(encoding="UTF-8")
        data_size = len(data)
        data_size_packed = struct.pack(">i", data_size)

        # Send total message size
        total_sent = 0
        while total_sent < 4:
            sent = self._conn.send(data_size_packed)
            if sent == 0:
                raise RuntimeError(
                    "socket connection broken while sending message size"
                )
            total_sent += sent

        # Send message
        total_sent = 0
        while total_sent < data_size:
            sent = self._conn.send(data[total_sent:])
            if sent == 0:
                raise RuntimeError(
                    "socket connection broken while sending message data"
                )
            total_sent += sent

    def _handle_receive(self):
        """
        Reads the PMI communication socket for a response
        :return: Response, if any, from PMI or None
        :rtype: str
        """
        data_size = self._get_incoming_message_size(self._conn)
        response = None
        if data_size is not None:
            response = self._receive_all(self._conn, data_size)
            response = response.decode(encoding="UTF-8").strip()

        logger.trace("PMI << " + response)

        return response

    def _receive_all(self, sock, n):
        """
        Receives all data from socket.
        :param sock: socket to receive from
        :param int n: size of data packet
        :return: received bytes
        """
        data = []
        bytes_rec = 0
        while bytes_rec < n:
            packet = sock.recv(n - bytes_rec)
            if packet == b"":
                return None
            data.append(packet)
            bytes_rec += len(packet)
        return b"".join(data)

    def _get_incoming_message_size(self, sock):
        """
        Determines the size of incoming data packet in bytes
        :param sock: socket to check
        :return: size of data packet
        :rtype: int
        """
        data = self._receive_all(sock, 4)
        if data:
            size = struct.unpack(
                ">i", data
            )  # Returns a tuple even if it's only one value
            return size[0]
        else:
            return None
