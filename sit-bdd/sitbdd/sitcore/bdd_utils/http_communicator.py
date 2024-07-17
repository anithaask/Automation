__all__ = ["HTTPCommunicator"]

import time
import requests
import json
from typing import Union

from sitbdd.sitcore.bdd_utils.errors import NetworkError, ProductError
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class HTTPCommunicator:
    """
    This class is the base HTTP communication layer that is used by each communication layer.
    """

    def __init__(self, hostname: str, port: int = None, secure: bool = False):
        """
        :param hostname: Hostname without protocol
        :param port: Port number
        :param secure: Define if we want to use http or https
        """
        if hostname.lower() == "localhost":
            self.hostname = "127.0.0.1"
        else:
            self.hostname = hostname

        self.port = port
        if self.port:
            self.base_url = "http://{}:{}/".format(self.hostname, self.port)
        else:
            self.base_url = "http://{}/".format(self.hostname)

        self.secure = secure
        if self.secure:
            self.base_url = self.base_url.replace("http", "https")

    def __str__(self):
        return "{}({}, {})".format(type(self).__name__, self.hostname, self.port)

    def _get(self, resource: str, headers: dict = None,
             data: Union[dict, str] = None, verify: bool = True) -> dict:
        """Send a GET request.
        """
        return self._request(
            "GET",
            resource,
            headers=headers,
            data=data,
            verify=verify,
        )

    def _post(self, resource: str, headers: dict = None,
              data: Union[dict, str] = None, verify: bool = True) -> dict:
        """Send a POST request.
        """
        return self._request(
            "POST",
            resource,
            headers=headers,
            data=data,
            verify=verify,
        )

    def _put(self, resource: str, headers: dict = None,
             data: Union[dict, str] = None, verify: bool = True) -> dict:
        """Send a PUT request.
        """
        return self._request(
            "PUT",
            resource,
            headers=headers,
            data=data,
            verify=verify,
        )

    def _delete(self, resource: str, headers: dict = None,
                data: Union[dict, str] = None, verify: bool = True) -> dict:
        """Send a DELETE request.
        """
        return self._request(
            "DELETE",
            resource,
            headers=headers,
            data=data,
            verify=verify,
        )

    def _patch(self, resource: str, headers: dict = None,
               data: Union[dict, str] = None, verify: bool = True) -> dict:
        """Send a PATCH request.
        """
        return self._request(
            "PATCH",
            resource,
            headers=headers,
            data=data,
            verify=verify,
        )

    def _request(self, method: str, resource: str, headers: dict = None,
                 data: Union[dict, str] = None, verify: bool = True) -> dict:
        """Send an HTTP request.

        :param method: Method for the new Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.
        :param resource: URL for the new Request object
        :param headers: Dictionary of HTTP Headers to send with the Request.
        :param data: Union[Dictionary, str] to send in the body of the Request.
        :param verify: Boolean that controls whether we verify the server's TLS certificate.
        :return: Body of the response for request.
        """
        url = self._expand_url(resource)
        if isinstance(data, dict):
            data = json.dumps(data)
        logger.debug(f'_request: sending request "{url}" with data {data}')

        start = time.perf_counter()

        try:
            response = requests.request(method, url, headers=headers, data=data, verify=verify)
            duration = time.perf_counter() - start
            if duration > 0.5:
                logger.debug(f'_request: Request "{url}" took "{duration:.3f}" seconds.')
        except requests.exceptions.ConnectionError as error:
            duration = time.perf_counter() - start
            logger.error(
                f'_request: Request "{url}" failed after "{duration:.3f}" seconds with '
                f'an error: "{str(error)}"'
            )
            raise NetworkError(error, name=self)

        return self._validate_response(response)

    def _validate_response(self, response: requests.models.Response) -> dict:
        """Verify that the response indicates a successful command.

        :param response: HTTP response
        :return: Body of the response.
        """
        body = {}
        self._validate_response_code(response)
        if response.text != '':  # the response does not have body
            body = response.json()
        return body

    def _validate_response_code(self, response: requests.models.Response) -> None:
        """Validate the response's HTTP status code.

        :param response: HTTP response
        """
        # Response class has integrated handler for responses <400, 600)
        response.raise_for_status()
        if not (200 <= response.status_code < 300):
            message = 'Command failed with status {} and reason "{}".'
            message = message.format(response.status_code, response.reason)
            raise NetworkError(message, name=self)

    def _expand_url(self, suffix: str) -> str:
        """Get the full URL for a given suffix.

        :param suffix: New text to append to the base URL
        :return: Full URL
        """
        return self.base_url.strip("/") + "/" + suffix.strip("/")
