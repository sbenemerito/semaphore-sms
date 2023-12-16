import os
import unittest
from unittest.mock import patch

from semaphore_sms import SemaphoreClient
from semaphore_sms.exceptions import SemaphoreException
from semaphore_sms.http import HttpResponse


class SemaphoreClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = SemaphoreClient(api_key='randomkey', sender_name='HELLO')

    # CLIENT INIT TESTS

    def test_missing_credentials_raises_exception(self):
        with self.assertRaises(
            SemaphoreException,
            msg='Credentials are required to create a SemaphoreClient'
        ):
            SemaphoreClient()

    def test_client_takes_creds_from_os_environ_if_unset(self):
        os.environ['SEMAPHORE_SMS_APIKEY'] = 'testkey'
        os.environ['SEMAPHORE_SMS_SENDERNAME'] = 'testsendername'

        client = SemaphoreClient()
        self.assertEqual(client.api_key, 'testkey')
        self.assertEqual(client.sender_name, 'testsendername')

        # clean up
        os.environ.pop('SEMAPHORE_SMS_APIKEY')
        os.environ.pop('SEMAPHORE_SMS_SENDERNAME')

    # SEND SMS TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_send_single_sms_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Single',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                }
            ]
        )

        message = self.client.send(
            message='Hello world, this is a test message',
            recipients=['639980101010', ],
            sender_name='HELLO'
        )[0]
        self.assertEqual(message.get('message_id'), 200112345)
        self.assertEqual(message.get('recipient'), '639980101010')
        self.assertEqual(message.get('message'), 'Hello world, this is a test message')
        self.assertEqual(message.get('sender_name'), 'HELLO')
        self.assertEqual(message.get('type'), 'Single')
        self.assertEqual(message.get('source'), 'Api')

    @patch('semaphore_sms.http.Session.send')
    def test_send_multiple_sms_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                },
                {
                    'message_id': 200112346,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980202020',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                }
            ]
        )

        messages = self.client.send(
            message='Hello world, this is a test message',
            recipients=['639980101010', '639980202020'],
            sender_name='HELLO'
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[1].get('message_id'), 200112346)
        self.assertEqual(messages[1].get('recipient'), '639980202020')
        self.assertEqual(messages[1].get('message'), 'Hello world, this is a test message')
        self.assertEqual(messages[1].get('sender_name'), 'HELLO')
        self.assertEqual(messages[1].get('type'), 'Bulk')
        self.assertEqual(messages[1].get('source'), 'Api')

    def test_send_sms_invalid_phone_fails(self):
        with self.assertRaises(
            SemaphoreException,
            msg='You supplied an invalid Philippine phone number in `recipients`'
        ):
            self.client.send(
                message='Validation failure - will not get sent to Semaphore API',
                recipients=['123', '639980202020'],
                sender_name='HELLO'
            )

    # PRIORITY SMS TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_priority_single_sms_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Single',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                }
            ]
        )

        message = self.client.priority(
            message='Hello world, this is a test message',
            recipients=['639980101010', ],
            sender_name='HELLO'
        )[0]
        self.assertEqual(message.get('message_id'), 200112345)
        self.assertEqual(message.get('recipient'), '639980101010')
        self.assertEqual(message.get('message'), 'Hello world, this is a test message')
        self.assertEqual(message.get('sender_name'), 'HELLO')
        self.assertEqual(message.get('type'), 'Single')
        self.assertEqual(message.get('source'), 'Api')

    @patch('semaphore_sms.http.Session.send')
    def test_priority_multiple_sms_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                },
                {
                    'message_id': 200112346,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980202020',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                }
            ]
        )

        messages = self.client.priority(
            message='Hello world, this is a test message',
            recipients=['639980101010', '639980202020'],
            sender_name='HELLO'
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[1].get('message_id'), 200112346)
        self.assertEqual(messages[1].get('recipient'), '639980202020')
        self.assertEqual(messages[1].get('message'), 'Hello world, this is a test message')
        self.assertEqual(messages[1].get('sender_name'), 'HELLO')
        self.assertEqual(messages[1].get('type'), 'Bulk')
        self.assertEqual(messages[1].get('source'), 'Api')

    def test_priority_sms_invalid_phone_fails(self):
        with self.assertRaises(
            SemaphoreException,
            msg='You supplied an invalid Philippine phone number in `recipients`'
        ):
            self.client.priority(
                message='Validation failure - will not get sent to Semaphore API',
                recipients=['123', '639980202020'],
                sender_name='HELLO'
            )

    # OTP SMS TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_otp_single_sms_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Your OTP is: 123456',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Single',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03',
                    'code': 123456
                }
            ]
        )

        message = self.client.otp(
            message='Hello world, this is a test message',
            recipients=['639980101010', ],
            sender_name='HELLO'
        )[0]
        self.assertEqual(message.get('message_id'), 200112345)
        self.assertEqual(message.get('recipient'), '639980101010')
        self.assertEqual(message.get('message'), 'Your OTP is: 123456')
        self.assertEqual(message.get('sender_name'), 'HELLO')
        self.assertEqual(message.get('type'), 'Single')
        self.assertEqual(message.get('source'), 'Api')
        self.assertEqual(message.get('code'), 123456)

    @patch('semaphore_sms.http.Session.send')
    def test_otp_multiple_sms_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Your OTP is: 123456',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03',
                    'code': 123456
                },
                {
                    'message_id': 200112346,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980202020',
                    'message': 'Your OTP is: 789101',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03',
                    'code': 789101
                }
            ]
        )

        messages = self.client.otp(
            message='Hello world, this is a test message',
            recipients=['639980101010', '639980202020'],
            sender_name='HELLO'
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[1].get('message_id'), 200112346)
        self.assertEqual(messages[1].get('recipient'), '639980202020')
        self.assertEqual(messages[1].get('message'), 'Your OTP is: 789101')
        self.assertEqual(messages[1].get('sender_name'), 'HELLO')
        self.assertEqual(messages[1].get('type'), 'Bulk')
        self.assertEqual(messages[1].get('source'), 'Api')
        self.assertEqual(messages[1].get('code'), 789101)

    def test_otp_sms_invalid_phone_fails(self):
        with self.assertRaises(
            SemaphoreException,
            msg='You supplied an invalid Philippine phone number in `recipients`'
        ):
            self.client.otp(
                message='Validation failure - will not get sent to Semaphore API',
                recipients=['123', '639980202020'],
                sender_name='HELLO'
            )

    # ACCOUNT TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_accounts_success_and_persists(self, mock_http_request):
        """
        We test the way `client.account` works in that:
        1. The first time it's called, it will retrieve account information from Semaphore API
        2. Once retrieved, it will save the result in memory (`self._account`)
        3. The succeeding calls to `client.account` will simply return data from memory
          except when `client` does POST requests (like `send`, `otp`, etc), in which case
          the client then returns to point #1 (to update things like account credit balance)
        """
        mock_http_request.return_value = HttpResponse(
            200,
            {
                'account_id': 12312,
                'account_name': 'Meraki',
                'status': 'Active',
                'credit_balance': 999
            }
        )

        account_data = self.client.account
        self.assertEqual(account_data.get('account_id'), 12312)
        self.assertEqual(account_data.get('credit_balance'), 999)
        self.assertEqual(mock_http_request.call_count, 1)

        # try to call `client.account` again, verify that no extra API calls were executed
        account_data = self.client.account
        self.assertEqual(mock_http_request.call_count, 1)

        # send a basic SMS
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'hello this is a test',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Single',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03',
                    'code': 123456
                }
            ]
        )
        self.client.send(message='hello this is a test', recipients=['09980101010', ])
        self.assertEqual(mock_http_request.call_count, 2)  # there are now 2 API calls in total
        mock_http_request.return_value = HttpResponse(
            200,
            {
                'account_id': 12312,
                'account_name': 'Meraki',
                'status': 'Active',
                'credit_balance': 998
            }
        )

        # try calling `client.account` again. another API call should have been made, updating data
        account_data = self.client.account
        self.assertEqual(account_data.get('account_id'), 12312)
        self.assertEqual(account_data.get('credit_balance'), 998)
        self.assertEqual(mock_http_request.call_count, 3)

    # MESSAGES TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_messages_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'message_id': 200112345,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980101010',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                },
                {
                    'message_id': 200112346,
                    'user_id': 33333,
                    'user': 'sam@mail.com',
                    'account_id': 11111,
                    'account': 'Meraki',
                    'recipient': '639980202020',
                    'message': 'Hello world, this is a test message',
                    'sender_name': 'HELLO',
                    'network': 'Smart',
                    'status': 'Pending',
                    'type': 'Bulk',
                    'source': 'Api',
                    'created_at': '2023-12-07 15:20:03',
                    'updated_at': '2023-12-07 15:20:03'
                }
            ]
        )

        messages = self.client.messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].get('message_id'), 200112345)
        self.assertEqual(messages[1].get('message_id'), 200112346)

    # TRANSACTIONS TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_transactions_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'id': 123123123,
                    'user_id': 12345,
                    'user': 'sam@mail.com',
                    'status': 'Approved',
                    'transaction_method': 'Dragonpay',
                    'external_transaction_id': '[000] ECPY Payment Auto Validated at Branch XXXXX with ref YYYY #AAA',
                    'amount': '500.00',
                    'credit_value': '1000',
                    'created_at': '2023-12-02 12:55 pm',
                    'updated_at': '2023-12-02 1:00 pm'
                }
            ]
        )

        transactions = self.client.transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].get('id'), 123123123)

    # SENDER NAMES TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_sender_names_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'name': 'MERAKI',
                    'status': 'Active',
                    'created': '2023-12-02 1:21 pm'
                }
            ]
        )

        sender_names = self.client.sender_names()
        self.assertEqual(len(sender_names), 1)
        self.assertEqual(sender_names[0].get('name'), 'MERAKI')

    # USERS TESTS

    @patch('semaphore_sms.http.Session.send')
    def test_users_success(self, mock_http_request):
        mock_http_request.return_value = HttpResponse(
            200,
            [
                {
                    'user_id': 12312,
                    'email': 'sam@mail.com',
                    'role': 'Owner'
                }
            ]
        )

        users = self.client.users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].get('user_id'), 12312)
