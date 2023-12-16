import logging
from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
)
from urllib.parse import urlencode

from requests import Request, Response, Session
from requests.adapters import HTTPAdapter

_logger = logging.getLogger('semaphore.http_client')


class HttpResponse(object):
    """
    HttpResponse mocker class for tests
    """
    def __init__(
        self,
        status_code: int,
        content: object,
        headers: Optional[Any] = None,
    ):
        self.content = content
        self.headers = headers
        self.status_code = status_code
        self.ok = self.status_code < 400

    @property
    def text(self) -> str:
        return str(self.content)

    def json(self) -> dict:
        return self.content

    def __repr__(self) -> str:
        return 'HTTP {} {}'.format(self.status_code, self.content)


class HttpClient:
    """
    General purpose HTTP Client for interacting with the Semaphore SMS Gateway API
    """

    def __init__(
        self,
        timeout: Optional[float] = None,
        logger: logging.Logger = _logger,
        max_retries: Optional[int] = None,
    ):
        """
        Constructor for the HttpClient

        :param timeout: Timeout for the requests.
                        Timeout should never be zero (0) or less.
        :param logger
        :param max_retries: Maximum number of retries each request should attempt
        """
        self.logger = logger
        if timeout is not None and timeout <= 0:
            raise ValueError(timeout)
        self.timeout = timeout

        self.session = Session()
        if self.session and max_retries is not None:
            self.session.mount('https://', HTTPAdapter(max_retries=max_retries))

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, object]] = None,
        data: Optional[Dict[str, object]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        timeout: Optional[float] = None,
        allow_redirects: bool = False,
    ) -> Response:
        """
        Make an HTTP Request with parameters provided.

        :param method: The HTTP method to use
        :param url: The URL to request
        :param params: Query parameters to append to the URL
        :param data: Parameters to go in the body of the HTTP request
        :param headers: HTTP Headers to send with the request
        :param auth: Basic Auth arguments
        :param timeout: Socket/Read timeout for the request
        :param allow_redirects: Whether or not to allow redirects
        See the requests documentation for explanation of all these parameters

        :return: An http response
        """
        if timeout is None:
            timeout = self.timeout
        elif timeout <= 0:
            raise ValueError(timeout)

        kwargs = {
            'method': method.upper(),
            'url': url,
            'params': params,
            'data': data,
            'headers': headers,
            'auth': auth,
        }

        self.log_request(kwargs)

        session = self.session or Session()
        request = Request(**kwargs)

        prepped_request = session.prepare_request(request)

        settings = session.merge_environment_settings(
            prepped_request.url, None, None, None, None
        )

        response = session.send(
            prepped_request,
            allow_redirects=allow_redirects,
            timeout=timeout,
            **settings
        )

        self.log_response(response.status_code, response)

        return response

    def log_request(self, kwargs: Dict[str, Any]) -> None:
        """
        Logs the HTTP request
        """
        self.logger.info('Sending request to Semaphore SMS Gateway API...')

        if kwargs['params']:
            self.logger.info(
                '{} Request: {}?{}'.format(
                    kwargs['method'], kwargs['url'], urlencode(kwargs['params'])
                )
            )
            self.logger.info('Query Params: {}'.format(kwargs['params']))
        else:
            self.logger.info('{} Request: {}'.format(kwargs['method'], kwargs['url']))

        if kwargs['headers']:
            self.logger.info('Headers:')
            for key, value in kwargs['headers'].items():
                # Do not log authorization headers
                if 'authorization' not in key.lower():
                    self.logger.info('{} : {}'.format(key, value))

    def log_response(self, status_code: int, response: Response) -> None:
        self.logger.info('Response status code: {}'.format(status_code))
        self.logger.info('Response headers: {}'.format(response.headers))
