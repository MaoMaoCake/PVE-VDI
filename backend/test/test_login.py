import unittest

from ..auth.utils import authenticate_user
from ..auth.models import User

class TestLoginCase(unittest.TestCase):
    def test_valid_login(self):
        """
        This function will return The user class if login is success
        :return:
        """
        valid = User(user_id=1, username='admin', role='Admin')
        tester = authenticate_user(username='admin',password='password')
        self.assertEqual(valid, tester)

    def test_invalid_login(self):
        """
        If login fails the reply will be none
        :return:
        """
        tester = authenticate_user(username='admin',password='wrongpassword')
        self.assertEqual(None, tester)

# class TestTokenEndpointCase(unittest.TestCase):
#     def test_valid_token(self):
#         import requests

if __name__ == '__main__':
    unittest.main()
