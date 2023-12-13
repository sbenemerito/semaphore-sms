import os
from typing import Dict, MutableMapping, Optional

from requests import Response

from semaphore_sms.exceptions import SemaphoreException
from semaphore_sms.http import HttpClient

BASE_URI = 'http://api.semaphore.co/api/v4/'


class SemaphoreClient(object):
    """A client for accessing the Twilio API."""

    def __init__(
        self,
        api_key: str = None,
        sender_name: str = None,
        environment: Optional[MutableMapping[str, str]] = None,
    ):
        """
        Initializes the Semapore SMS Client

        :param api_key: Semaphore API key to authenticate with
        :param sender_name: SMS sender name to use when sending messages
        :param environment: Environment to look for auth details, defaults to os.environ
        """
        environment = environment or os.environ
        self.api_key = api_key or environment.get('SEMAPHORE_SMS_APIKEY')
        self.sender_name = sender_name or environment.get('SEMAPHORE_SMS_SENDERNAME')

        if not self.api_key:
            raise SemaphoreException("Credentials are required to create a SemaphoreClient")

        self.http_client = HttpClient()

    def request(
        self,
        method: str,
        uri: str,
        params: Optional[Dict[str, object]] = None,
        data: Optional[Dict[str, object]] = None,
        timeout: Optional[float] = 10,
        allow_redirects: bool = False,
    ) -> Response:
        """
        Makes a request to the Semaphore API.

        :param method: HTTP Method
        :param uri: Fully qualified url
        :param params: Query string parameters
        :param data: POST body data
        :param timeout: Timeout in seconds, defaults to 10
        :param allow_redirects: Should the client follow redirects

        :returns: Response from the Semaphore API
        """
        uri = f'{BASE_URI}{uri}/'

        return self.http_client.request(
            method,
            uri,
            params=params,
            data=data,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    def get(self, uri: str, params: Dict[str, object] = dict()) -> Response:
        params = {
            **params,
            'apikey': self.api_key  # automatically add apikey as query param
        }

        return self.request('get', uri, params, None)

    def post(self, uri: str, data: Dict[str, object] = dict()) -> Response:
        data = {
            **data,
            'apikey': self.api_key,  # automatically add apikey in request data
            'sendername': self.sender_name,  # automatically add sender_name in request data
        }

        return self.request('post', uri, None, data)
