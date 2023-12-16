import unittest
from unittest.mock import Mock, patch

from requests import Session

from semaphore_sms.http import HttpClient, HttpResponse


class TestHttpClientRequest(unittest.TestCase):
    def setUp(self):
        self.session_patcher = patch('semaphore_sms.http.Session')

        self.session_mock = Mock(wraps=Session())
        self.request_mock = Mock()

        self.session_mock.prepare_request.return_value = self.request_mock
        self.session_mock.send.return_value = HttpResponse(200, 'testing-unicode: Ω≈ç√, 💩')
        self.request_mock.headers = {}

        session_constructor_mock = self.session_patcher.start()
        session_constructor_mock.return_value = self.session_mock

        self.client = HttpClient()

    def tearDown(self):
        self.session_patcher.stop()

    def test_request_with_timeout(self):
        self.request_mock.url = 'https://api.semaphore.co/api/v4/'
        self.request_mock.headers = {'Host': 'api.semaphore.com'}

        response = self.client.request(
            'doesnt matter', 'doesnt matter', None, None, None, None, 30
        )

        self.assertEqual('api.semaphore.com', self.request_mock.headers['Host'])
        self.assertEqual(200, response.status_code)
        self.assertEqual('testing-unicode: Ω≈ç√, 💩', response.content)

    def test_request_where_method_timeout_equals_zero(self):
        self.request_mock.url = 'https://api.semaphore.co/api/v4/'
        self.request_mock.headers = {'Host': 'api.semaphore.com'}

        try:
            self.client.request(
                'doesnt matter', 'doesnt matter', None, None, None, None, 0
            )
        except Exception as e:
            self.assertEqual(ValueError, type(e))

    def test_request_where_class_timeout_manually_set(self):
        self.request_mock.url = 'https://api.semaphore.co/api/v4/'
        self.request_mock.headers = {'Host': 'api.semaphore.com'}
        self.client.timeout = 30

        response = self.client.request('doesnt matter', 'doesnt matter')
        self.assertEqual('api.semaphore.com', self.request_mock.headers['Host'])
        self.assertEqual(200, response.status_code)
        self.assertEqual('testing-unicode: Ω≈ç√, 💩', response.content)

    def test_request_where_class_timeout_equals_zero(self):
        self.request_mock.url = 'https://api.semaphore.co/api/v4/'
        self.request_mock.headers = {'Host': 'api.semaphore.com'}
        self.client.timeout = 0

        try:
            self.client.request('doesnt matter', 'doesnt matter')
        except Exception as e:
            self.assertEqual(type(e), ValueError)

    def test_request_where_class_timeout_and_method_timeout_set(self):
        self.request_mock.url = 'https://api.semaphore.co/api/v4/'
        self.request_mock.headers = {'Host': 'api.semaphore.com'}
        self.client.timeout = 30

        response = self.client.request(
            'doesnt matter', 'doesnt matter', None, None, None, None, 15
        )

        self.assertEqual('api.semaphore.com', self.request_mock.headers['Host'])
        self.assertEqual(200, response.status_code)
        self.assertEqual('testing-unicode: Ω≈ç√, 💩', response.content)

    def test_request_with_unicode_response(self):
        self.request_mock.url = 'https://api.semaphore.co/api/v4/'
        self.request_mock.headers = {'Host': 'api.semaphore.com'}

        response = self.client.request('doesnt matter', 'doesnt matter')

        self.assertEqual('api.semaphore.com', self.request_mock.headers['Host'])
        self.assertEqual(200, response.status_code)
        self.assertEqual('testing-unicode: Ω≈ç√, 💩', response.content)
