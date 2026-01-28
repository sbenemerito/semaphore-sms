import unittest

from semaphore_sms.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    EmptyMessageError,
    InvalidPhoneNumberError,
    NetworkError,
    RateLimitError,
    SemaphoreException,
    ServerError,
    ValidationError,
)


class TestExceptionHierarchy(unittest.TestCase):

    def test_semaphore_exception_is_base(self):
        self.assertTrue(issubclass(AuthenticationError, SemaphoreException))
        self.assertTrue(issubclass(ValidationError, SemaphoreException))
        self.assertTrue(issubclass(APIError, SemaphoreException))

    def test_validation_error_hierarchy(self):
        self.assertTrue(issubclass(InvalidPhoneNumberError, ValidationError))
        self.assertTrue(issubclass(EmptyMessageError, ValidationError))
        self.assertTrue(issubclass(InvalidPhoneNumberError, SemaphoreException))
        self.assertTrue(issubclass(EmptyMessageError, SemaphoreException))

    def test_api_error_hierarchy(self):
        self.assertTrue(issubclass(AuthorizationError, APIError))
        self.assertTrue(issubclass(RateLimitError, APIError))
        self.assertTrue(issubclass(ServerError, APIError))
        self.assertTrue(issubclass(NetworkError, APIError))
        self.assertTrue(issubclass(AuthorizationError, SemaphoreException))
        self.assertTrue(issubclass(RateLimitError, SemaphoreException))
        self.assertTrue(issubclass(ServerError, SemaphoreException))
        self.assertTrue(issubclass(NetworkError, SemaphoreException))


class TestExceptionAttributes(unittest.TestCase):

    def test_authentication_error_message(self):
        exc = AuthenticationError()
        self.assertIn('Credentials', str(exc))

    def test_authentication_error_custom_message(self):
        exc = AuthenticationError('Custom message')
        self.assertEqual(str(exc), 'Custom message')

    def test_invalid_phone_number_error_recipients(self):
        recipients = ['123', '456']
        exc = InvalidPhoneNumberError(recipients)
        self.assertEqual(exc.recipients, recipients)
        self.assertIn('123', str(exc))

    def test_empty_message_error(self):
        exc = EmptyMessageError()
        self.assertIn('blank', str(exc))

    def test_api_error_status_code(self):
        exc = APIError(400, 'Bad Request')
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.response_text, 'Bad Request')
        self.assertIn('400', str(exc))

    def test_authorization_error_status_code(self):
        exc = AuthorizationError(401, 'Unauthorized')
        self.assertEqual(exc.status_code, 401)
        self.assertTrue(isinstance(exc, APIError))

    def test_rate_limit_error_retry_after(self):
        exc = RateLimitError(429, 'Too Many Requests', retry_after=60)
        self.assertEqual(exc.status_code, 429)
        self.assertEqual(exc.retry_after, 60)
        self.assertIn('429', str(exc))

    def test_rate_limit_error_retry_after_string(self):
        exc = RateLimitError(429, 'Too Many Requests', retry_after='120')
        self.assertEqual(exc.retry_after, 120)

    def test_rate_limit_error_no_retry_after(self):
        exc = RateLimitError(429, 'Too Many Requests')
        self.assertIsNone(exc.retry_after)

    def test_server_error_status_code(self):
        exc = ServerError(500, 'Internal Server Error')
        self.assertEqual(exc.status_code, 500)
        self.assertTrue(isinstance(exc, APIError))

    def test_network_error_original_exception(self):
        original = ConnectionError('Connection refused')
        exc = NetworkError('Network failed', original_exception=original)
        self.assertEqual(exc.original_exception, original)
        self.assertIn('Network failed', str(exc))
        self.assertIn('Connection refused', str(exc))

    def test_network_error_status_code_is_zero(self):
        exc = NetworkError('Network failed')
        self.assertEqual(exc.status_code, 0)


class TestExceptionBackwardCompatibility(unittest.TestCase):

    def test_catching_specific_as_base(self):
        try:
            raise AuthenticationError('test')
        except SemaphoreException:
            pass

    def test_catching_validation_as_base(self):
        try:
            raise InvalidPhoneNumberError(['123'])
        except SemaphoreException:
            pass

    def test_catching_api_error_as_base(self):
        try:
            raise ServerError(500, 'error')
        except SemaphoreException:
            pass

    def test_catching_rate_limit_as_api_error(self):
        try:
            raise RateLimitError(429, 'error')
        except APIError:
            pass

    def test_catching_invalid_phone_as_validation_error(self):
        try:
            raise InvalidPhoneNumberError(['123'])
        except ValidationError:
            pass


if __name__ == '__main__':
    unittest.main()
