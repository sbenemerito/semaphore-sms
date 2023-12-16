# semaphore-sms

[![PyPI](https://img.shields.io/pypi/v/semaphore-sms.svg)](https://pypi.python.org/pypi/semaphore-sms)
[![PyPI](https://img.shields.io/pypi/pyversions/semaphore-sms.svg)](https://pypi.python.org/pypi/semaphore-sms)

API wrapper for [Semaphore SMS Gateway](https://semaphore.co/). The documentation for their API can be found [here](https://semaphore.co/docs).

## Installation

This library should be able to support Python versions >= 3.7.

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
    sender_name'sender_name',
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

## Tests

Clone the repo and run

```shell
PYTHONPATH=src python -m unittest
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/sbenemerito/semaphore-sms/

## License

The library is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
