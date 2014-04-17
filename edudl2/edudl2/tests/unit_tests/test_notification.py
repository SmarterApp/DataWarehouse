__author__ = 'tshewchuk'

"""
Unit tests for notification module.
"""

import unittest
import httpretty
from unittest.mock import patch

from edudl2.udl2 import message_keys as mk
from edudl2.notification.notification import post_notification, create_notification_body


class TestNotification(unittest.TestCase):

    def setUp(self):
        self.udl2_conf = {'sr_notification_retries': 5, 'sr_notification_timeout': 1}

    @httpretty.activate
    def test_post_notification_success_no_retries(self):
        # Create the notification request body.
        notification_body = {'status': mk.SUCCESS, 'id': 'aaa-bbb-ccc', 'testRegistrationId': '111-222-333', 'message': ''}

        # Send the status.
        callback_url = self.register_url([201])
        notification_status, notification_error = post_notification(callback_url, 1, notification_body)

        # Verify results.
        self.assertEquals(mk.SUCCESS, notification_status)
        self.assertEquals(None, notification_error)

    @httpretty.activate
    def test_post_notification_pending(self):
        # Create the notification request body.
        notification_body = {'status': mk.SUCCESS, 'id': 'aaa-bbb-ccc', 'testRegistrationId': '111-222-333', 'message': ''}

        # Send the status.
        callback_url = self.register_url([408])
        notification_status, notification_error = post_notification(callback_url, 1, notification_body)

        # Verify results.
        self.assertEquals(mk.PENDING, notification_status)
        self.assertEquals('408 Client Error: Request a Timeout', notification_error)

    @httpretty.activate
    def test_post_notification_failure(self):
        # Create the notification request body.
        notification_body = {'status': mk.SUCCESS, 'id': 'aaa-bbb-ccc', 'testRegistrationId': '111-222-333', 'message': ''}

        # Send the status.
        callback_url = self.register_url([401])
        notification_status, notification_error = post_notification(callback_url, 1, notification_body)

        # Verify results.
        self.assertEquals('401 Client Error: Unauthorized', notification_error)
        self.assertEquals(mk.FAILURE, notification_status)

    @httpretty.activate
    def test_post_notification_pending_connection_error(self):
        # Create the notification request body.
        notification_body = {'status': mk.SUCCESS, 'id': 'aaa-bbb-ccc', 'testRegistrationId': '111-222-333', 'message': ''}

        # Send the status.
        callback_url = 'http://SomeBogusurl/SomeBogusEndpoint'
        notification_status, notification_error = post_notification(callback_url, 1, notification_body)

        # Verify results.
        self.assertEquals(mk.PENDING, notification_status)
        self.assertRegex(notification_error, "Max retries exceeded with url")

    @patch('edudl2.notification.notification.get_notification_message')
    @patch('edudl2.notification.notification._retrieve_status')
    def test_create_notification_body_success(self, mock__retrieve_status, mock_get_notification_message):
        mock__retrieve_status.return_value = mk.SUCCESS
        mock_get_notification_message.return_value = ['Completed Successfully']

        body = create_notification_body("guid_batch", "batch_table", "id", "test_reg_id", 100)

        self.assertEquals(body['rowCount'], 100)
        self.assertEquals(body['id'], 'id')
        self.assertEquals(body['testRegistrationId'], 'test_reg_id')
        self.assertEquals(body['status'], 'Success')
        self.assertEquals(body['message'], ['Completed Successfully'])

    @patch('edudl2.notification.notification.get_notification_message')
    @patch('edudl2.notification.notification._retrieve_status')
    def test_create_notification_body_failure(self, mock__retrieve_status, mock_get_notification_message):
        mock__retrieve_status.return_value = mk.FAILURE
        mock_get_notification_message.return_value = ['ERROR 3000']

        body = create_notification_body("guid_batch", "batch_table", "id", "test_reg_id", 100)

        self.assertTrue('rowCount' not in body)
        self.assertEquals(body['id'], 'id')
        self.assertEquals(body['testRegistrationId'], 'test_reg_id')
        self.assertEquals(body['status'], 'Failed')
        self.assertEquals(body['message'], ['ERROR 3000'])

    def register_url(self, return_statuses):
        url = "http://MyTestUri/MyEndpoint"
        responses = [httpretty.Response(body={}, status=return_status) for return_status in return_statuses]
        httpretty.register_uri(httpretty.POST, url, responses=responses)
        return url


if __name__ == '__main__':
    unittest.main()
