import os
import re
from typing import Dict, List, MutableMapping, Optional, Union

from semaphore_sms.exceptions import SemaphoreException
from semaphore_sms.http import HttpClient

BASE_URI = 'http://api.semaphore.co/api/v4/'


class SemaphoreClient(object):
    """A client for accessing the Semaphore API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        sender_name: Optional[str] = None,
        environment: Optional[MutableMapping[str, str]] = None,
    ):
        """
        Initializes the Semapore SMS Client

        :param api_key: Semaphore API key to authenticate with
        :param sender_name: SMS sender name to use when sending messages (defaults to 'SEMAPHORE')
        :param environment: Environment to look for auth details, defaults to os.environ
        """
        environment = environment or os.environ
        self.api_key = api_key or environment.get('SEMAPHORE_SMS_APIKEY')
        self.sender_name = sender_name or environment.get('SEMAPHORE_SMS_SENDERNAME')

        if not self.api_key:
            raise SemaphoreException('Credentials are required to create a SemaphoreClient')

        self.http_client = HttpClient()
        self._account = None

    def request(
        self,
        method: str,
        uri: str,
        params: Optional[Dict[str, object]] = None,
        data: Optional[Dict[str, object]] = None,
        timeout: float = 10,
        allow_redirects: bool = False,
    ) -> dict:
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
        response = self.http_client.request(
            method,
            uri,
            params=params,
            data=data,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

        if response.ok:
            # We assume that Semaphore API always returns JSON,
            # and won't handle probable case of not receiving JSON type (YAGNI)
            return response.json()

        raise SemaphoreException(f'Request failed: HTTP {response.status_code} {response.text}')

    def get(self, uri: str, params: Dict[str, object] = dict()) -> dict:
        params = {
            **params,
            'apikey': self.api_key  # automatically add apikey as query param
        }
        params = {k: v for k, v in params.items() if v is not None}

        return self.request('get', uri, params, None)

    def post(self, uri: str, data: Dict[str, object] = dict()) -> dict:
        data = {
            **data,
            'apikey': self.api_key,  # automatically add apikey in request data
            'sendername': self.sender_name,  # automatically add sender_name in request data
        }
        data = {k: v for k, v in data.items() if v is not None}

        # make sure we re-fetch `account` next time it's called because a transaction has been triggered
        self._account = None

        return self.request('post', uri, None, data)

    def validate_phone_format(self, number: Union[str, List[str]]):
        """
        Philippine phone number validation, solely based on prefix and length
        """
        clean_number = ''.join(number.split('-')).strip()
        return re.match(r'^(\+?639|09)\d{9}$', clean_number)

    def send(self, message: str, recipients: List[str], sender_name: Optional[str] = None):
        """
        Used for hitting the send message endpoints (single and bulk).
        https://semaphore.co/docs#sending_messages
        https://semaphore.co/docs#bulk_messages

        :param message: SMS body
        :param recipients: Recipient PH phone number(s)
        :param sender_name: SMS sender name (defaults to 'SEMAPHORE' if None)

        :returns: Response from the Semaphore API
        """
        sender_name = sender_name or self.sender_name

        if not message.strip():
            raise SemaphoreException('Cannot send a blank message')

        if not all([self.validate_phone_format(recipient) for recipient in recipients]):
            raise SemaphoreException('You supplied an invalid Philippine phone number in `recipients`')

        return self.post(
            'messages',
            {
                'message': message,
                'sendername': sender_name,
                'number': ','.join(recipients)  # recipients are to be sent as a comma-separated string
            }
        )

    def priority(self, message: str, recipients: List[str], sender_name: Optional[str] = None):
        """
        Used for hitting the PRIORITY send message endpoint.
        Similar to the normal send message endpoint, except that this takes more credits,
        and will use the priority queue which bypasses the default message queue and
        sends the message immediately.
        https://semaphore.co/docs#priority_messages

        :param message: SMS body
        :param recipients: Recipient PH phone number(s)
        :param sender_name: SMS sender name (defaults to 'SEMAPHORE' if None)

        :returns: Response from the Semaphore API
        """
        sender_name = sender_name or self.sender_name

        if not message.strip():
            raise SemaphoreException('Cannot send a blank message')

        if not all([self.validate_phone_format(recipient) for recipient in recipients]):
            raise SemaphoreException('You supplied an invalid Philippine phone number in `recipients`')

        return self.post(
            'priority',
            {
                'message': message,
                'sendername': sender_name,
                'number': ','.join(recipients)  # recipients are to be sent as a comma-separated string
            }
        )

    def otp(self, recipients: List[str], message: Optional[str] = None,
            sender_name: Optional[str] = None, code: Optional[Union[int, str]] = None):
        """
        Used for hitting the OTP message endpoint.
        Similar to priority messaging, except this is dedicated for one-time password messages,
        and uses a route dedicated to OTP traffic.
        Please do not use this route to send regular messages.
        https://semaphore.co/docs#otp_messages

        :param message: Custom SMS body (please see docs for this)
        :param recipients: Recipient PH phone number(s)
        :param sender_name: SMS sender name (defaults to 'SEMAPHORE' if None)
        :param code: Custom OTP code if you want to skip the auto-generated one

        :returns: Response from the Semaphore API
        """
        sender_name = sender_name or self.sender_name

        if not all([self.validate_phone_format(recipient) for recipient in recipients]):
            raise SemaphoreException('You supplied an invalid Philippine phone number in `recipients`')

        return self.post(
            'otp',
            {
                'message': message,
                'sendername': sender_name,
                'number': ','.join(recipients),  # recipients are to be sent as a comma-separated string
                'code': code,
            }
        )

    def messages(self, id: Optional[Union[int, str]] = None, page: Optional[Union[int, str]] = None,
                 limit: Optional[Union[int, str]] = None, network: Optional[str] = None,
                 status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Used for hitting the retrieve message(s) endpoint.
        Providing `id` shall hit the /messages/<id>/ endpoint.
        https://semaphore.co/docs#retrieving_messages

        :param id: Specific message ID
        :param page: Page of results to return. 
        :param limit: Only take top <limit> results. Default is 100, max is 1000.
        :param network: which network the message was sent to
        :param status: delivery status
        :param start_date: YYYY-MM-DD
        :param end_date: YYYY-MM-DD

        :returns: Response from the Semaphore API
        """
        uri = f'messages/{id}' if id else 'messages'
        params = {
          'page': page,
          'limit': limit,
          'startDate': start_date,
          'endDate': end_date,
          'network': network.lower() if network else None,
          'status': status.lower() if status else None
        }

        return self.get(uri, params)

    def transactions(self, page: Optional[Union[int, str]] = None, limit: Optional[Union[int, str]] = None):
        """
        Retrieving transaction information under https://semaphore.co/docs#retrieving_account

        :param page: Page of results to return.
        :param limit: Only take top <limit> results. Default is 100, max is 1000.

        :returns: Response from the Semaphore API
        """
        params = {
          'page': page,
          'limit': limit
        }

        return self.get('account/transactions', params)

    def sender_names(self, page: Optional[Union[int, str]] = None, limit: Optional[Union[int, str]] = None):
        """
        Retrieving sender names under https://semaphore.co/docs#retrieving_account

        :param page: Page of results to return.
        :param limit: Only take top <limit> results. Default is 100, max is 1000.

        :returns: Response from the Semaphore API
        """
        params = {
          'page': page,
          'limit': limit
        }

        return self.get('account/sendernames', params)

    def users(self, page: Optional[Union[int, str]] = None, limit: Optional[Union[int, str]] = None):
        """
        Retrieving users under https://semaphore.co/docs#retrieving_account

        :param page: Page of results to return.
        :param limit: Only take top <limit> results. Default is 100, max is 1000.

        :returns: Response from the Semaphore API
        """
        params = {
          'page': page,
          'limit': limit
        }

        return self.get('account/users', params)

    @property
    def account(self):
        """
        Used for retrieving basic information about your account
        https://semaphore.co/docs#retrieving_account
        """
        if not self._account:
            self._account = self.get('account')

        return self._account
