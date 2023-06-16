import json
import re
from typing import Any, Optional, Union

import requests

from dsp_tools.models.exceptions import BaseError


def check_for_api_error(response: requests.Response) -> None:
    """
    Check the response of an API request if it contains an error raised by DSP-API.

    Args:
        res: The requests.Response object that is returned by the API request

    Raises:
        BaseError: If the status code of the response is not 200
    """
    if response.status_code != 200:
        raise BaseError(
            message="KNORA-ERROR: status code=" + str(response.status_code) + "\nMessage:" + response.text,
            status_code=response.status_code,
            json_content_of_api_response=response.text,
            reason_from_api=response.reason,
            api_route=response.url,
        )


class Connection:
    """
    An Connection instance represents a connection to a DSP server.

    Attributes
    ----------

    none (internal use attributes should not be modified/set directly)
    """

    _server: str
    _prefixes: Union[dict[str, str], None]
    _token: Union[str, None]
    _log: bool

    def __init__(self, server: str, prefixes: dict[str, str] = None):
        """
        Constructor requiring the server address, the user and password of DSP
        :param server: Address of the server, e.g https://api.dasch.swiss
        :param prefixes: Ontology prefixes used
        """

        self._server = re.sub(r"\/$", "", server)
        self._prefixes = prefixes
        self._token = None
        self._log = False

    def login(self, email: str, password: str) -> None:
        """
        Method to login into DSP which creates a session token.
        :param email: Email of user, e.g., root@example.com
        :param password: Password of the user, e.g. test
        """

        credentials = {"email": email, "password": password}
        jsondata = json.dumps(credentials)

        response = requests.post(
            self._server + "/v2/authentication",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            data=jsondata,
            timeout=5,
        )
        check_for_api_error(response)
        result = response.json()
        self._token = result["token"]

    def get_token(self) -> str:
        """
        Returns the token
        :return: token string
        """

        return self._token

    @property
    def token(self) -> str:
        return self._token

    def start_logging(self) -> None:
        self._log = True

    def stop_logging(self):
        self._log = False

    def logout(self) -> None:
        """
        Performs a logout
        :return: None
        """

        if self._token is not None:
            response = requests.delete(
                self._server + "/v2/authentication",
                headers={"Authorization": "Bearer " + self._token},
                timeout=5,
            )
            check_for_api_error(response)
            self._token = None

    def __del__(self):
        pass
        # self.logout()

    def post(self, path: str, jsondata: Optional[str] = None):
        """
        Post Json data to a given server using a HTTP POST request
        :param path: Path of RESTful route
        :param jsondata: Valid JSON as string
        :return: Response from server
        """

        if path[0] != "/":
            path = "/" + path
        headers = None
        if jsondata is None:
            if self._token is not None:
                headers = {"Authorization": "Bearer " + self._token}
                response = requests.post(
                    self._server + path,
                    headers=headers,
                    timeout=5,
                )
            else:
                response = requests.post(self._server + path, timeout=5)
        else:
            if self._token is not None:
                headers = {"Content-Type": "application/json; charset=UTF-8", "Authorization": "Bearer " + self._token}
                response = requests.post(
                    self._server + path,
                    headers=headers,
                    data=jsondata,
                    timeout=5,
                )
            else:
                headers = {"Content-Type": "application/json; charset=UTF-8"}
                response = requests.post(
                    self._server + path,
                    headers=headers,
                    data=jsondata,
                    timeout=5,
                )
        if self._log:
            if jsondata:
                jsonobj = json.loads(jsondata)
            else:
                jsonobj = None
            logobj = {
                "method": "POST",
                "headers": headers,
                "route": path,
                "body": jsonobj,
                "return-headers": dict(response.headers),
                "return": response.json()
                if response.status_code == 200
                else {"status": str(response.status_code), "message": response.text},
            }
            tmp = path.split("/")
            filename = "POST" + "_".join(tmp) + ".json"
            with open(filename, "w", encoding="utf8") as f:
                json.dump(logobj, f, indent=4)
        check_for_api_error(response)
        result = response.json()
        return result

    def get(self, path: str, headers: Optional[dict[str, str]] = None) -> dict[str, Any]:
        """
        Get data from a server using a HTTP GET request
        :param path: Path of RESTful route
        :param headers: ...
        :return: Response from server
        """

        if path[0] != "/":
            path = "/" + path
        if not self._token:
            if not headers:
                response = requests.get(self._server + path, timeout=5)
            else:
                response = requests.get(self._server + path, headers, timeout=5)
        else:
            if not headers:
                response = requests.get(
                    self._server + path,
                    headers={"Authorization": "Bearer " + self._token},
                    timeout=5,
                )
            else:
                headers["Authorization"] = "Bearer " + self._token
                response = requests.get(self._server + path, headers, timeout=5)

        check_for_api_error(response)
        json_response = response.json()
        return json_response

    def put(self, path: str, jsondata: Optional[str] = None, content_type: str = "application/json"):
        """
        Send data to a RESTful server using a HTTP PUT request
        :param path: Path of RESTful route
        :param jsondata: Valid JSON as string
        :param content_type: HTTP Content-Type [default: 'application/json']
        :return:
        """

        if path[0] != "/":
            path = "/" + path
        if jsondata is None:
            response = requests.put(
                self._server + path,
                headers={"Authorization": "Bearer " + self._token},
                timeout=5,
            )
        else:
            response = requests.put(
                self._server + path,
                headers={"Content-Type": content_type + "; charset=UTF-8", "Authorization": "Bearer " + self._token},
                data=jsondata,
                timeout=5,
            )
        check_for_api_error(response)
        result = response.json()
        return result

    def delete(self, path: str, params: Optional[any] = None):
        """
        Send a delete request using the HTTP DELETE request
        :param path: Path of RESTful route
        :return: Response from server
        """

        if path[0] != "/":
            path = "/" + path
        if params is not None:
            response = requests.delete(
                self._server + path,
                headers={"Authorization": "Bearer " + self._token},
                params=params,
                timeout=5,
            )

        else:
            response = requests.delete(
                self._server + path,
                headers={"Authorization": "Bearer " + self._token},
                timeout=5,
            )
        check_for_api_error(response)
        result = response.json()
        return result
