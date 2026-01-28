"""
Semaphore SMS API Exception Classes.

This module defines a comprehensive exception hierarchy for handling
errors that may occur when interacting with the Semaphore SMS API.

Exception Hierarchy:
    SemaphoreException (base)
    ├── AuthenticationError - Missing or invalid API credentials
    ├── ValidationError - Client-side validation failures
    │   ├── InvalidPhoneNumberError - Invalid Philippine phone format
    │   └── EmptyMessageError - Blank message content
    └── APIError - Server returned an error response
        ├── AuthorizationError - 401/403 responses
        ├── RateLimitError - 429 responses
        ├── ServerError - 5xx responses
        └── NetworkError - Connection/timeout failures

Example:
    >>> from semaphore_sms import SemaphoreClient
    >>> from semaphore_sms.exceptions import (
    ...     AuthenticationError,
    ...     InvalidPhoneNumberError,
    ...     RateLimitError,
    ... )
    >>>
    >>> try:
    ...     client = SemaphoreClient(api_key='invalid_key')
    ...     client.send(message='Hello', recipients=['09991234567'])
    ... except AuthenticationError as e:
    ...     print(f"Auth failed: {e}")
    ... except InvalidPhoneNumberError as e:
    ...     print(f"Invalid phone: {e.recipients}")
    ... except RateLimitError as e:
    ...     print(f"Rate limited. Retry after: {e.retry_after}")
"""

from typing import List, Optional, Union


__all__ = [
    "SemaphoreException",
    "AuthenticationError",
    "ValidationError",
    "InvalidPhoneNumberError",
    "EmptyMessageError",
    "APIError",
    "AuthorizationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]


class SemaphoreException(Exception):
    """
    Base exception for all Semaphore SMS API errors.

    All exceptions raised by this library inherit from SemaphoreException,
    allowing you to catch all Semaphore-related errors with a single except block.

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['09991234567'])
        ... except SemaphoreException as e:
        ...     print(f"Semaphore error: {e}")
    """

    def __init__(self, message: str = "An error occurred with the Semaphore API"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class AuthenticationError(SemaphoreException):
    """
    Raised when API credentials are missing or invalid.

    This error occurs when:
    - No API key is provided and none is found in environment variables
    - The API key format is invalid

    Example:
        >>> try:
        ...     client = SemaphoreClient()  # No api_key, not in env
        ... except AuthenticationError as e:
        ...     print(f"Please set SEMAPHORE_SMS_APIKEY: {e}")
    """

    def __init__(self, message: str = "Credentials are required to create a SemaphoreClient"):
        super().__init__(message)


class ValidationError(SemaphoreException):
    """
    Base class for client-side validation errors.

    This is raised when input data fails validation before being sent to the API.
    Specific validation errors (InvalidPhoneNumberError, EmptyMessageError) inherit
    from this class.

    Example:
        >>> try:
        ...     client.send(message='', recipients=['invalid'])
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e}")
    """

    def __init__(self, message: str = "Validation error"):
        super().__init__(message)


class InvalidPhoneNumberError(ValidationError):
    """
    Raised when one or more phone numbers fail Philippine format validation.

    Valid formats:
    - 09XXXXXXXXX (11 digits starting with 09)
    - +639XXXXXXXXX (12 digits starting with +639)
    - 639XXXXXXXXX (12 digits starting with 639)

    Attributes:
        recipients: The list of phone numbers that were being validated.

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['123', '09991234567'])
        ... except InvalidPhoneNumberError as e:
        ...     print(f"Invalid numbers in: {e.recipients}")
    """

    def __init__(
        self,
        recipients: Optional[List[str]] = None,
        message: str = "You supplied an invalid Philippine phone number in `recipients`",
    ):
        self.recipients = recipients or []
        super().__init__(message)

    def __str__(self) -> str:
        if self.recipients:
            return f"{self.message}: {self.recipients}"
        return self.message


class EmptyMessageError(ValidationError):
    """
    Raised when attempting to send a blank or whitespace-only message.

    Example:
        >>> try:
        ...     client.send(message='   ', recipients=['09991234567'])
        ... except EmptyMessageError as e:
        ...     print("Message cannot be empty")
    """

    def __init__(self, message: str = "Cannot send a blank message"):
        super().__init__(message)


class APIError(SemaphoreException):
    """
    Base class for errors returned by the Semaphore API.

    This is raised when the API returns an error response (HTTP 4xx or 5xx).
    Specific API errors (AuthorizationError, RateLimitError, ServerError)
    inherit from this class.

    Attributes:
        status_code: The HTTP status code returned by the API.
        response_text: The response body text from the API.

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['09991234567'])
        ... except APIError as e:
        ...     print(f"API error {e.status_code}: {e.response_text}")
    """

    def __init__(
        self,
        status_code: int,
        response_text: str = "",
        message: Optional[str] = None,
    ):
        self.status_code = status_code
        self.response_text = response_text
        if message is None:
            message = f"Request failed: HTTP {status_code} {response_text}"
        super().__init__(message)

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.response_text}" if self.response_text else f"HTTP {self.status_code}"


class AuthorizationError(APIError):
    """
    Raised when the API returns 401 (Unauthorized) or 403 (Forbidden).

    This typically indicates:
    - Invalid API key
    - API key lacks permission for the requested operation
    - Account is suspended or disabled

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['09991234567'])
        ... except AuthorizationError as e:
        ...     print(f"Authorization failed ({e.status_code}): Check your API key")
    """

    def __init__(
        self,
        status_code: int,
        response_text: str = "",
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Authorization failed: HTTP {status_code}"
        super().__init__(status_code, response_text, message)


class RateLimitError(APIError):
    """
    Raised when the API returns 429 (Too Many Requests).

    This indicates you've exceeded the API rate limit. Check the retry_after
    attribute for when you can retry the request.

    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API).

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['09991234567'])
        ... except RateLimitError as e:
        ...     if e.retry_after:
        ...         time.sleep(e.retry_after)
        ...     else:
        ...         time.sleep(60)  # Default backoff
    """

    def __init__(
        self,
        status_code: int = 429,
        response_text: str = "",
        retry_after: Optional[Union[int, str]] = None,
        message: Optional[str] = None,
    ):
        self.retry_after = int(retry_after) if retry_after else None
        if message is None:
            if self.retry_after:
                message = f"Rate limit exceeded. Retry after {self.retry_after} seconds"
            else:
                message = "Rate limit exceeded"
        super().__init__(status_code, response_text, message)


class ServerError(APIError):
    """
    Raised when the API returns a 5xx server error.

    This indicates a problem on the Semaphore server side. These errors
    are typically transient and may succeed if retried.

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['09991234567'])
        ... except ServerError as e:
        ...     print(f"Server error ({e.status_code}). Try again later.")
    """

    def __init__(
        self,
        status_code: int,
        response_text: str = "",
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Server error: HTTP {status_code}"
        super().__init__(status_code, response_text, message)


class NetworkError(APIError):
    """
    Raised when a network-level error occurs (connection, timeout, etc.).

    This wraps underlying network exceptions from the requests library.

    Attributes:
        original_exception: The original exception that caused this error.

    Example:
        >>> try:
        ...     client.send(message='Hello', recipients=['09991234567'])
        ... except NetworkError as e:
        ...     print(f"Network error: {e.original_exception}")
    """

    def __init__(
        self,
        message: str = "Network error occurred",
        original_exception: Optional[Exception] = None,
    ):
        self.original_exception = original_exception
        # Use 0 as status_code for network errors (no HTTP response received)
        super().__init__(status_code=0, response_text="", message=message)

    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.message}: {self.original_exception}"
        return self.message
