import unittest

from user import User, Guest

class TestUsers(unittest.TestCase):

	def test_email_set_on_init(self):
		user = User({"data": { "email": 'user@here.com', "groups": ['pirates'] } })
		self.assertEqual(user.get_id(), 'user@here.com')
		self.assertEqual(user.groups, ['pirates'])

	def test_guest_initial_params_set(self):
		guest = Guest()
		self.assertEqual(guest.get_id(), 'guest')
		self.assertEqual(guest.groups, ['world'])