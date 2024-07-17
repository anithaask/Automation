import socket

__all__ = ["SocketCommunicator"]

from sitbdd.sitcore.bdd_utils.sit_logging import log_trace


class SocketCommunicator:
    @log_trace
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._conn = None

        self._connect()

    @log_trace
    def _connect(self):
        # todo: Exception handling
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.connect((self.hostname, self.port))

    @log_trace
    def _disconnect(self):
        if self._conn:
            self._conn.close()

    @log_trace
    def _communicate(self, command, buffer=4096):
        self._conn.send(command.encode())
        response = self._conn.recv(buffer)
        response.decode("utf-8", "ignore")
        # if the response is empty, the socket needs to be reopened
        tries = 0
        while response == b"" and tries < 4:
            self._connect()
            self._conn.send(command.encode())
            response = self._conn.recv(buffer)
            response.decode("utf-8", "ignore")
            tries += 1
        return response
