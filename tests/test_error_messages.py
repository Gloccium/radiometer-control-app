import unittest
from app.utils import error_messages


class TestErrorMessages(unittest.TestCase):
    def test_already_exists(self):
        network_status = 400
        self.assertTrue(error_messages.is_network_error(network_status))

    def test_authorization_error(self):
        network_status = 401
        self.assertTrue(error_messages.is_network_error(network_status))

    def test_network_error(self):
        network_status = 201
        self.assertTrue(error_messages.is_network_error(network_status))
