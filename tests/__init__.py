import os

from flask_pymongo import MongoClient
from eve.tests import TestMinimal
from run import create_app

SETTINGS_PATH = os.path.join(os.path.dirname('..'), 'db', 'test.py')

class MaterialsTestBase(TestMinimal):

  def setUp(self, settings_file=None, url_converters=None):

    self.this_directory = os.path.dirname(os.path.realpath(__file__))

    if settings_file is None:
      settings_file = SETTINGS_PATH

    self.connection = None
    self.setupDB()

    self.settings_file = settings_file
    self.app = create_app(SETTINGS_PATH)
    self.app.testing = True

    self.test_client = self.app.test_client()

    self.domain = self.app.config['DOMAIN']

  def setupDB(self):
    self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
    self.connection.drop_database(MONGO_DBNAME)

  def dropDB(self):
    self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
    self.connection.drop_database(MONGO_DBNAME)