# semaphore-sms

[![CI](https://github.com/sbenemerito/semaphore-sms/actions/workflows/ci.yml/badge.svg)](https://github.com/sbenemerito/semaphore-sms/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/sbenemerito/semaphore-sms/branch/main/graph/badge.svg)](https://codecov.io/gh/sbenemerito/semaphore-sms)
[![PyPI](https://img.shields.io/pypi/v/semaphore-sms.svg)](https://pypi.python.org/pypi/semaphore-sms)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

API wrapper for [Semaphore SMS Gateway](https://semaphore.co/). The documentation for their API can be found [here](https://semaphore.co/docs).

## Installation

This library supports Python versions >= 3.7.

Install from PyPi using [pip](https://pip.pypa.io/en/latest/) via

```shell
pip install semaphore-sms
```

Don't have pip installed? Refer to [this documentation](https://pip.pypa.io/en/stable/installation/)

## Usage

‼️ For all these calls, you can see sample responses in tests/test_semaphore_client.py ‼️

### Initializing the client

```python
from semaphore_sms import SemaphoreClient

client = SemaphoreClient(
    api_key='your_api_key',
    sender_name='sender_name',
)
```

> Note: `SemaphoreClient` will try to pull `api_key` from `os.environ` if not supplied. If it still can't a value then, a `SemaphoreException` will be raised

### Sending SMS

For sending [a basic single message](https://semaphore.co/docs#sending_messages),

```python
client.send(
    message='Your text here',
    recipients=['09980101010', ]
)
```

To send one message [to several numbers in bulk](https://semaphore.co/docs#sending_messages), simply provide multiple numbers under `recipients`

```python
client.send(
    message='Your text here',
    recipients=['09980101010', '09980202020', ]
)
```

Sending out [priority messages](https://semaphore.co/docs#sending_messages) and [OTP messages](https://semaphore.co/docs#sending_messages) will look very similar

```python
client.priority(
    message='Your text here',
    recipients=['09980101010', '09980202020', ]
)

client.otp(
    message='Your OTP is: {otp}',  # refer to Semaphore's docs for details
    recipients=['09980101010', ],
    code=123456,  # refer to Semaphore's docs for details
)
```

### Fetching messages

https://semaphore.co/docs#retrieving_messages

```python
client.messages(
    limit=100,  # optional
    page=1,  # optional
    start_date='2023-11-06',  # optional
    end_date='2023-12-25',  # optional
    network='smart',  # optional
    status='succcess'  # optional
)
```

### Retrieving account information

https://semaphore.co/docs#retrieving_account

```python
account_information = client.account
transactions = client.transactions(
    limit=100,  # optional
    page=1  # optional
)
sender_names = client.sender_names(
    limit=100,  # optional
    page=1  # optional
)
users = client.users(
    limit=100,  # optional
    page=1  # optional
)
```

Again, you can see sample responses in tests/test_semaphore_client.py

## Error Handling

The library provides a comprehensive exception hierarchy for handling different error scenarios:

```
SemaphoreException (base)
├── AuthenticationError     # Missing or invalid API credentials
├── ValidationError         # Client-side validation failures
│   ├── InvalidPhoneNumberError  # Invalid Philippine phone format
│   └── EmptyMessageError        # Blank message content
└── APIError               # Server returned an error response
    ├── AuthorizationError # 401/403 responses
    ├── RateLimitError     # 429 responses (includes retry_after)
    ├── ServerError        # 5xx responses
    └── NetworkError       # Connection/timeout failures
```

### Example Usage

```python
from semaphore_sms import SemaphoreClient
from semaphore_sms.exceptions import (
    AuthenticationError,
    InvalidPhoneNumberError,
    RateLimitError,
    SemaphoreException,
)

try:
    client = SemaphoreClient(api_key='your_api_key')
    client.send(message='Hello', recipients=['09991234567'])
except AuthenticationError:
    print("Invalid API key")
except InvalidPhoneNumberError as e:
    print(f"Invalid phone numbers: {e.recipients}")
except RateLimitError as e:
    if e.retry_after:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
except SemaphoreException as e:
    print(f"Semaphore error: {e}")
```

All exceptions inherit from `SemaphoreException`, so you can catch all library errors with a single except block for backward compatibility.

## Tests

Clone the repo and run

```shell
PYTHONPATH=src python -m unittest
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/sbenemerito/semaphore-sms/

*Note: Yes, I'm currently pushing directly to main - I know, I know. When contributors come around, I'll enforce proper branch protection and PR workflows 🙇‍♂️*

## License

The library is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
